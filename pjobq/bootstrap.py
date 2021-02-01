"""
Some high-level functinos that tie together logical components into a running application.
"""

import asyncio
from datetime import datetime
import logging
import time

from .apptypes import JobHandler, Job
from .runtime import State, default_init
from .constants import ADHOC_JOB_INTERVAL_S, ADHOC_NOTIFY_CHANNEL, NOTIFY_UPDATE_CMD
from .env import ENV
from .logic.jobs import handle_http, run_scheduled_cron_jobs, schedule_adhoc_jobs
from .util import attempt_forever, setup_logging


def handle_job_factory(state: State) -> JobHandler:
    """
    Close over state here to promote a more functional approach at
    the logic level. (ie. don't mutate the state).
    It is certainly still possible to mutate things, ex. default headers on the http session, but please avoid this.
    """

    async def handle_job(job: Job):
        """Top level handler entry."""
        logging.info("running job %s::%s", job.job_name, job.job_id)
        if job.cmd_type == "HTTP":
            return await handle_http(state.http, job)
        logging.error("no such cmd type %s", job.cmd_type)
        return

    return handle_job


async def init() -> tuple[State, JobHandler]:
    "initialize the applciation, with retry"
    loop = asyncio.get_event_loop()
    state = await attempt_forever("pjobq init", lambda: default_init(loop))
    return (state, handle_job_factory(state))


async def run_cron_job_loop(
    state: State,
    handler: JobHandler,
) -> None:
    """
    Since cron resolution is up to the minute, we poll every minute over our
    known cron schedules, adjusting the time we use to perform the cron check
    to be the top of the minute.

    Theoretically, since there is non-zero execution time outside of the
    `sleep`, we will slowly be losing time on our counter.
    TODO: implement a periodic re-sync of the clock to the top of the minute
    """
    while True:
        await asyncio.sleep(60)
        dt = datetime.now().replace(second=0, microsecond=0)
        state.loop.create_task(
            run_scheduled_cron_jobs(
                dt=dt,
                cron_jobs=state.cron_scheduler.cron_jobs,
                handler=handler,
            )
        )
    return


async def run_adhoc_job_event_loop(state: State, handler: JobHandler) -> None:
    """
    Maintain a list of jobs to be scheduled in a window of ADHOC_JOB_INTERVAL_S
    into the future.
    Also listen for updates to the adhoc_jobs table in order to reload this list.
    """
    # our window of time
    start_time = time.time()
    end_time = start_time + ADHOC_JOB_INTERVAL_S

    async def reload_window_jobs() -> None:
        """Load all jobs in the window"""
        jobs = await state.adhoc_model.get_all_in_range(state.db, start_time, end_time)
        logging.debug(
            "loaded %s adhoc jobs in window %s - %s",
            len(jobs),
            datetime.fromtimestamp(start_time).isoformat(),
            datetime.fromtimestamp(end_time).isoformat(),
        )
        schedule_adhoc_jobs(state.adhoc_scheduler, state.loop, jobs, handler)
        return

    def on_adhoc_job_table_notify(payload: str):
        """Handle updates to the adhoc_job table"""
        if payload == NOTIFY_UPDATE_CMD:
            state.loop.create_task(reload_window_jobs())
        return

    await state.db.add_pg_notify_listener(
        ADHOC_NOTIFY_CHANNEL, on_adhoc_job_table_notify
    )
    while True:
        start_time = time.time()
        end_time = start_time + ADHOC_JOB_INTERVAL_S
        await reload_window_jobs()
        await asyncio.sleep(ADHOC_JOB_INTERVAL_S)
    return


async def run_application() -> None:
    """
    The highest level function.
    Briefly: we maintain a list of known cron jobs in State.cron_jobs.
    Postgres should notify us when the state of stored cron jobs changes,
    at which point we update our list of jobs in-memory to match.
    """
    setup_logging(ENV.LOG_LEVEL)
    state, handler = await init()
    try:
        t1 = state.loop.create_task(run_cron_job_loop(state, handler))
        t2 = state.loop.create_task(run_adhoc_job_event_loop(state, handler))
        await t1
        await t2
    except Exception as e:
        logging.exception(e)
        state, handler = await init()
    return
