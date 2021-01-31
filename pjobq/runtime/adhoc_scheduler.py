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

from ..apptypes import AdhocJob, JobHandler
from ..util import delay_execution


class AdhocScheduler:
    """
    Cache of jobs to run in the future.
    This is maintained as a dict of asyncio tasks, indexed by job id.
    When updating the job cache, if a job has been rescheduled, we cancel
    the existing task and create a new one.
    """

    scheduled: dict[str, Task]

    async def init(self):
        self.scheduled = {}
        return self

    def schedule_jobs(
        self,
        loop: asyncio.AbstractEventLoop,
        jobs: list[AdhocJob],
        handler: JobHandler,
    ) -> None:
        "purely additive for the moment"
        for job in jobs:
            if job.job_id in self.scheduled:
                self.scheduled[job.job_id].cancel()
            self.scheduled[job.job_id] = loop.create_task(
                delay_execution(handler(job), job.schedule_ts)
            )
        return
