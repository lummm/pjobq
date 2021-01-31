"""
Logic related to scheduling cron jobs.
"""

import asyncio
from datetime import datetime
import logging

import pycron  # type: ignore

from ...apptypes import JobHandler, CronJob


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
