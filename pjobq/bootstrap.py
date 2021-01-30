"""
Some high-level functinos that tie together logical components into a running application.
"""

import asyncio
from datetime import datetime
import logging

from .runtime import State, default_init
from .env import ENV
from .logic.jobs import handle_job_factory, run_scheduled_cron_jobs
from .util import attempt_forever, setup_logging


async def init() -> State:
    "initialize the applciation, with retry"
    return await attempt_forever("pjobq init", default_init)


async def run_cron_job_loop(
    state: State, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
) -> None:
    """
    Proceeding with a very naive implementation until some performance testing is done.
    Literally sleep every second and check if we are at the top of a minute (cron is up to the minute).
    If so, we check our known list of cron_jobs to see if any must be run.
    """
    handler = handle_job_factory(state)
    while True:
        await asyncio.sleep(1)
        if datetime.now().second == 0:
            run_scheduled_cron_jobs(
                loop=loop,
                cron_jobs=state.cron_jobs,
                handler=handler,
            )
    return


async def run_application() -> None:
    """
    The highest level handler.
    Briefly: we maintain a list of known cron jobs in State.cron_jobs.
    Postgres should notify us when the state of stored cron jobs changes,
    at which point we update our list of jobs in-memory to match.
    """
    setup_logging(ENV.LOG_LEVEL)
    state = await init()
    loop = asyncio.get_event_loop()
    try:
        await run_cron_job_loop(state, loop)
    except Exception as e:
        logging.exception(e)
        state = await init()
    return
