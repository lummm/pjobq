"""
Stateful runtime logic.

Briefly, we maintain a list of known cron jobs in State.cron_jobs.
Postgres should notify us when the state of stored cron jobs changes,
at which point we update our list of jobs in-memory to match.

At every minute, we check the list of cron jobs, and execute those scheduled
to run now.
"""

import asyncio
from datetime import datetime
import logging
from typing import List
from types import SimpleNamespace

import pycron  # type: ignore

from .apptypes import Job, DBCon
from . import db
from .env import ENV
from . import job_handler


INIT_RETRY_WAIT_LIMIT_S = 120


# all application state lives here
class State(SimpleNamespace):
    cron_jobs: List[Job]
    db_con: DBCon


def on_cron_update(state: State):
    "factory function providing handler for new cron jobs"

    def update_cron_jobs(jobs: List[Job]) -> None:
        state.cron_jobs = jobs

    return update_cron_jobs


def check_cron_jobs(cron_jobs: List[Job]):
    "check all known cron jobs to see if any must be run"
    loop = asyncio.get_event_loop()
    for job in cron_jobs:
        if pycron.is_now(job.cron_schedule):
            # it is important to create a task here and proceed to processing
            # the other jobs
            loop.create_task(job_handler.handle(job))
    return


def setup_logging() -> None:
    logging.basicConfig(
        level=ENV.LOG_LEVEL,
        format=f"%(asctime)s.%(msecs)03d "
        "%(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return


async def init() -> State:
    logging.info("cron job q starting...")
    attempt = 1
    current_wait = 0
    state = State(
        cron_jobs=[],
    )
    while True:
        try:
            await asyncio.sleep(current_wait)
            state.db_conn = await db.connect(
                on_cron_update=on_cron_update(state))
            state.cron_jobs = await db.load_cron_jobs(state.db_conn)
            return state
        except Exception as e:
            logging.exception(e)
            attempt += 1
            current_wait = min([2 ** (attempt - 1), INIT_RETRY_WAIT_LIMIT_S])
            logging.info("attempt init again in %s seconds", current_wait)
    return


async def run():
    setup_logging()
    state = await init()
    logging.info("loaded %s jobs", len(state.cron_jobs))
    while True:
        try:
            await asyncio.sleep(1)
            if datetime.now().second == 0:
                # cron is up to minute
                check_cron_jobs(state.cron_jobs)
        except Exception as e:
            logging.exception(e)
            state = await init()
    return
