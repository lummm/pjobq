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
from types import SimpleNamespace

import pycron  # type: ignore

from .apptypes import CronJob
from .runtime import State, init as init_state
from .env import ENV
from . import job_handler
from .util import attempt_forever


def setup_logging() -> None:
    logging.basicConfig(
        level=ENV.LOG_LEVEL,
        format=f"%(asctime)s.%(msecs)03d "
        "%(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return


def check_cron_jobs(cron_jobs: list[CronJob]):
    "check all known cron jobs to see if any must be run"
    loop = asyncio.get_event_loop()
    for job in cron_jobs:
        if pycron.is_now(job.cron_schedule):
            # it is important to create a task here and proceed to processing
            # the other jobs
            loop.create_task(job_handler.handle(job))
    return


async def init() -> State:
    "init with retry"
    return await attempt_forever("pjobq init", init_state)


async def run():
    setup_logging()
    state = await init()
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
