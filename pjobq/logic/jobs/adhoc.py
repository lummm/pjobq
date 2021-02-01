"""
Logic related to scheduling adhoc jobs.
We mark a job as completed upon successfully performing it.
"""

import asyncio
import logging

from ...apptypes import JobHandler, Job, AdhocJob
from ...db import DB
from ...models import AdhocJobModel
from ...runtime import AdhocScheduler
from ...util import delay_execution


async def run_adhoc_job(
    db: DB,
    adhoc_job_model: type[AdhocJobModel],
    handler: JobHandler,
    job: Job,
) -> None:
    """
    Attempt to run 'handler'.
    On success, update DB record for job.
    """
    try:
        await handler(job)
        await adhoc_job_model.set_job_completed(db, job.job_id)
    except Exception as e:
        logging.exception(e)
    return


def schedule_adhoc_jobs(
    scheduler: AdhocScheduler,
    loop: asyncio.AbstractEventLoop,
    jobs: list[AdhocJob],
    handler: JobHandler,
) -> None:
    "purely additive for the moment"
    for job in jobs:
        if job.job_id in scheduler.scheduled:
            scheduler.scheduled[job.job_id].cancel()
        job_exec_awaitable = run_adhoc_job(
            scheduler.db, scheduler.adhoc_job_model, handler, job
        )
        scheduler.scheduled[job.job_id] = loop.create_task(
            delay_execution(job_exec_awaitable, job.schedule_ts)
        )
    return
