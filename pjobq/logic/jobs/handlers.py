"""
This package defines handlers to fire when a job needs to be run.

Job handling should always be executing in the context of an asycnio task (thus we can await as we please and not block firing off other jobs).
Job handling should ideally be pure I/O, as we are single threaded.
"""

import logging

import aiohttp

from ...apptypes import Job, HttpJob, JobHandler
from ...runtime import State
from ...apphttp import AppHttp
from .job_conversion import as_http_job


def handle_job_factory(state: State) -> JobHandler:
    """
    Close over the state here to promote a more functional approach at
    the logic level.
    """

    async def handle_job(job: Job):
        """Top level handler entry."""
        logging.info("running job %s::%s", job.job_name, job.job_id)
        if job.cmd_type == "HTTP":
            return await handle_http(state.http, as_http_job(job))
        logging.error("no such cmd type %s", job.cmd_type)
        return

    return handle_job


async def handle_http(http: AppHttp, job: HttpJob):
    "handle an http job"
    req_args = {}
    if job.body:
        req_args["body"] = job.body
    res_status = await http.req(job.method, job.url, **req_args)
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
