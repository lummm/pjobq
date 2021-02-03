import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable, Any, Optional

import asyncpg  # type: ignore


# ----------------------
# ----- data types -----
# ----------------------
@dataclass
class Job:
    "a generic job"
    job_id: str
    job_name: str
    cmd_type: str
    cmd_payload: str


@dataclass
class CronJob(Job):
    "job scheduled with cron syntax (ie. recurring)"
    cron_schedule: str


@dataclass
class AdhocJob(Job):
    "job scheduled with cron syntax (ie. recurring)"
    schedule_ts: float


@dataclass
class HttpJob(Job):
    "a job to be executed as an http request"
    method: str
    url: str
    body: Optional[str] = None


# ----------------------
# --- database types ---
# ----------------------
# an update callback to receive the latest cron_jobs
DBCon = asyncpg.Connection
NotifyChannel = str
NotifyPayload = str
PgNotifyListener = Callable[[NotifyPayload], Any]


# ----------------------
# ---- other types -----
# ----------------------
JobHandler = Callable[[Job], Awaitable[None]]
EventLoop = asyncio.AbstractEventLoop
