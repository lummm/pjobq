"""
Logic related to scheduling cron jobs.
"""

import asyncio
from datetime import datetime
import logging

import pycron  # type: ignore

from ...apptypes import JobHandler, CronJob


def run_scheduled_cron_jobs(
    *,
    dt: datetime,
    loop: asyncio.AbstractEventLoop,
    cron_jobs: list[CronJob],
    handler: JobHandler
):
    "iterate cron jobs to see if any must be run"
    for job in cron_jobs:
        if pycron.is_now(job.cron_schedule, dt):
            # it is important to create a task here and proceed to processing
            # the other jobs
            loop.create_task(handler(job))
    return
