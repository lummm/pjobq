from dataclasses import dataclass
from typing import Callable, List, Any

import asyncpg  # type: ignore


# an update callback to receive the latest cron_jobs
CronUpdateCallback = Callable[[List[Any]], None]

DBCon = asyncpg.Connection


@dataclass
class Job:
    "a generic job"
    job_id: str
    job_name: str
    cron_schedule: str
    cmd_type: str
    cmd_payload: str


@dataclass
class HttpJob(Job):
    "a job to be executed as an http request"
    method: str
    url: str
    body: str


@dataclass
class A:
    x: int
