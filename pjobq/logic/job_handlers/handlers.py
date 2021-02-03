"""
Definitions of handlers for different job types
"""

import logging

import aiohttp

from pjobq.apptypes import HttpJob, Job
from pjobq.apphttp import AppHttp

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
