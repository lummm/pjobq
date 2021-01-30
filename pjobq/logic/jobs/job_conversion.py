"""
Functions to convert into the various kinds of jobs.
"""

import dataclasses
import json

from ...apptypes import Job, HttpJob


def as_http_job(job: Job) -> HttpJob:
    "convert a generic job into an HttpJob"
    req_args = json.loads(job.cmd_payload)
    return HttpJob(
        **base_job_dict(job),
        **{
            "method": req_args["method"],
            "url": req_args["url"],
            "body": req_args["body"],
        }
    )  # type: ignore


def base_job_dict(job: Job) -> dict:
    """
    return a job as a dict, only specifying the keys
    that exist on the Job base class
    """
    return dict(
        [(field.name, getattr(job, field.name)) for field in dataclasses.fields(Job)]
    )
