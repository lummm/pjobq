"""
Keeping a cache of adhoc-scheduled jobs.
We try to keep the cache small, because if this process were to die,
we would lose all the cached jobs.
However, we must query the adhoc_jobs table at the same interval as our cache,
so it cannot be arbitrarily small.
"""

import asyncio
from asyncio import Task
import time

from ..db import DB
from ..models import AdhocJobModel


class AdhocScheduler:
    """
    Cache of jobs to run in the future.
    This is maintained as a dict of asyncio tasks, indexed by job id.
    When updating the job cache, if a job has been rescheduled, we cancel
    the existing task and create a new one.
    """

    scheduled: dict[str, Task]
    db: DB
    adhoc_job_model: type[AdhocJobModel]

    async def init(
        self,
        db: DB,
        adhoc_job_model: type[AdhocJobModel],
    ):
        self.scheduled = {}
        self.db = db
        self.adhoc_job_model = adhoc_job_model
        return self
