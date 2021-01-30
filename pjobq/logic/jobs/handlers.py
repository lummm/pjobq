"""
This package defines handlers to fire when a job needs to be run.

Job handling should always be executing in the context of an asycnio task (thus we can await as we please and not block firing off other jobs).
Job handling should ideally be pure I/O, as we are single threaded.
"""

import logging

import aiohttp

from ...apptypes import Job, HttpJob
from .job_conversion import as_http_job


async def handle_job(job: Job):
    logging.info("running job %s::%s", job.job_name, job.job_id)
    if job.cmd_type == "HTTP":
        return await handle_http(as_http_job(job))
    logging.error("no such cmd type %s", job.cmd_type)
    return


async def handle_http(job: HttpJob):
    req_args = {}
    if job.body:
        req_args["body"] = job.body
    async with aiohttp.ClientSession() as session:
        async with session.request(job.method, job.url, **req_args) as res:
            logging.debug(
                "job %s::%s http req status %s", job.job_name, job.job_id, res.status
            )
            if res.status != 200:
                logging.error(
                    "http request failed: %s, %s for job %s::%s",
                    job.method,
                    job.url,
                    job.job_name,
                    job.job_id,
                )
    return
