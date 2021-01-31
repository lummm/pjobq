"""
Logic related to scheduling adhoc jobs.
We mark a job as completed upon successfully performing it.
"""

import logging

from ...apptypes import JobHandler, Job
from ...db import DB
from ...models import AdhocJobModel


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
