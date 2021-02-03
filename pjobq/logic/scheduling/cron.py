"""
Logic related to scheduling cron jobs.
"""

import asyncio
from datetime import datetime
import logging

import pycron  # type: ignore

from pjobq.apptypes import JobHandler, CronJob, EventLoop, PgNotifyListener
from pjobq.constants import NOTIFY_UPDATE_CMD
from pjobq.state import CronSchedulerState
from pjobq.util import create_unfailing_task


async def run_scheduled_cron_jobs(
    *,
    cron_jobs: list[CronJob],
    handler: JobHandler,
    dt: datetime = None,
):
    """
    Iterate cron jobs to see if any must be run.
    This should be done in its own task.
    """
    to_run = [job for job in cron_jobs if pycron.is_now(job.cron_schedule, dt)]
    await asyncio.gather(*[handler(job) for job in to_run])
    return


async def reload_cron_jobs(cron_state: CronSchedulerState) -> None:
    "relaod all cron jobs - simply replace them"
    cron_state.cron_jobs = await cron_state.cron_model.get_all()
    logging.info("loaded %s cron jobs", len(cron_state.cron_jobs))
    return


def on_cron_table_notify_factory(
    loop: EventLoop,
    scheduler: CronSchedulerState,
) -> PgNotifyListener:
    """
    Generate a handler for pg_notify events for the cron_job table.
    Because this is sync, we need to create a task.
    Note also that we have to 'await' at some point for the task to run.
    Since we are living inside an asyncio.sleep loop, this should be fine.
    """

    def on_cron_table_notify(payload: str) -> None:
        if payload == NOTIFY_UPDATE_CMD:
            create_unfailing_task(
                "cron job table refresh",
                loop,
                reload_cron_jobs(scheduler),
            )
            return
        logging.error("unknown cron notify payload -> %s", payload)
        return

    return on_cron_table_notify
