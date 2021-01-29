"""
Functions in this module execute in the context of an asycnio task.
Job handling should ideally be pure I/O.
"""

import dataclasses
import json
import logging

import aiohttp

from .apptypes import Job, HttpJob


async def handle(job: Job):
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


# private
def as_http_job(job: Job) -> HttpJob:
    req_args = json.loads(job.cmd_payload)
    return HttpJob(
        **dataclasses.asdict(job),
        **{
            "method": req_args["method"],
            "url": req_args["url"],
            "body": req_args["body"],
        }
    )  # type: ignore
