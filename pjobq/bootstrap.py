"""
Some high-level functinos that tie together logical components into a running application.
"""

import asyncio
from datetime import datetime
import logging
import time

from .apptypes import JobHandler
from .runtime import State, default_init
from .constants import ADHOC_JOB_INTERVAL_S
from .env import ENV
from .logic.jobs import handle_job_factory, run_scheduled_cron_jobs
from .util import attempt_forever, setup_logging


async def init() -> tuple[State, JobHandler]:
    "initialize the applciation, with retry"
    state = await attempt_forever("pjobq init", default_init)
    return (state, handle_job_factory(state))


async def run_cron_job_loop(
    state: State,
    handler: JobHandler,
) -> None:
    """
    Proceeding with a very naive implementation until some performance testing is done.
    Literally sleep every second and check if we are at the top of a minute (cron is up to the minute).
    If so, we check our known list of cron_jobs to see if any must be run.
    """
    while True:
        await asyncio.sleep(1)
        if datetime.now().second == 0:
            run_scheduled_cron_jobs(
                loop=state.loop,
                cron_jobs=state.cron_scheduler.cron_jobs,
                handler=handler,
            )
    return


async def run_adhoc_job_event_loop(state: State, handler: JobHandler) -> None:
    while True:
        start_time = time.time()
        end_time = start_time + ADHOC_JOB_INTERVAL_S
        jobs = await state.adhoc_model.get_all_in_range(state.db, start_time, end_time)
        logging.debug("loaded %s new adhoc jobs", len(jobs))
        state.adhoc_scheduler.schedule_jobs(state.loop, jobs, handler)
        await asyncio.sleep(ADHOC_JOB_INTERVAL_S)
    return


async def run_application() -> None:
    """
    The highest level handler.
    Briefly: we maintain a list of known cron jobs in State.cron_jobs.
    Postgres should notify us when the state of stored cron jobs changes,
    at which point we update our list of jobs in-memory to match.
    """
    setup_logging(ENV.LOG_LEVEL)
    state, handler = await init()
    try:
        await asyncio.gather(
            *[
                run_cron_job_loop(state, handler),
                run_adhoc_job_event_loop(state, handler),
            ]
        )

    except Exception as e:
        logging.exception(e)
        state, handler = await init()
    return
