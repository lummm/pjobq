"""
This package defines handlers to fire when a job needs to be run.

Job handling should always be executing in the context of an asycnio task (thus we can await as we please and not block firing off other jobs).
Job handling should ideally be pure I/O, as we are single threaded.
"""

import logging

import aiohttp

from ...apptypes import HttpJob, Job
from ...apphttp import AppHttp
from .job_conversion import as_http_job


async def handle_http(http: AppHttp, generic_job: Job) -> None:
    "handle an http job"
    job: HttpJob = as_http_job(generic_job)
    res_status = await http.req(job.method, job.url, data=job.body)
    logging.debug("job %s::%s http req status %s", job.job_name, job.job_id, res_status)
    if res_status != 200:
        logging.error(
            "http request failed: %s, %s for job %s::%s",
            job.method,
            job.url,
            job.job_name,
            job.job_id,
        )
    return
