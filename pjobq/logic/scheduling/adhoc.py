"""
Logic related to scheduling adhoc jobs.
We mark a job as completed upon successfully performing it.
"""

import asyncio

from pjobq.apptypes import JobHandler, Job, AdhocJob
from pjobq.db import DB
from pjobq.models import AdhocJobModel
from pjobq.state import AdhocScheduler
from pjobq.util import delay_execution, create_unfailing_task


async def run_adhoc_job(
    db: DB,
    adhoc_job_model: AdhocJobModel,
    handler: JobHandler,
    job: Job,
) -> None:
    """
    Attempt to run 'handler'.
    On success, update DB record for job.
    """
    await handler(job)
    await adhoc_job_model.set_job_completed(job.job_id)
    return


def schedule_adhoc_jobs(
    scheduler: AdhocScheduler,
    loop: asyncio.AbstractEventLoop,
    jobs: list[AdhocJob],
    handler: JobHandler,
) -> None:
    "purely additive for the moment - ie. we don't 'unschedule' any jobs"
    for job in jobs:
        if job.job_id in scheduler.scheduled:
            scheduler.scheduled[job.job_id].cancel()
        job_exec_awaitable = run_adhoc_job(
            scheduler.db, scheduler.adhoc_job_model, handler, job
        )
        scheduler.scheduled[job.job_id] = create_unfailing_task(
            job.job_id, loop, delay_execution(job_exec_awaitable, job.schedule_ts)
        )
    return
