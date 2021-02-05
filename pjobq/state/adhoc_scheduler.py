"""
A slice of state living on the parent State object.

Keeping a cache of adhoc-scheduled jobs.
We try to keep the cache small, because if this process were to die,
we would lose all the cached jobs.
However, we must query the adhoc_jobs table at the same interval as our cache,
so it cannot be arbitrarily small.
"""

from asyncio import TimerHandle

from pjobq.models import AdhocJobModel


class AdhocSchedulerState:
    """
    Cache of jobs to run in the future.
    This is maintained as a dict of asyncio tasks, indexed by job id.
    When updating the job cache, if a job has been rescheduled, we cancel
    the existing task and create a new one.

    We refer to the current time range as the 'window'.
    """

    sched_time: dict[str, float]
    scheduled: dict[str, TimerHandle]
    executing: dict[str, bool]
    adhoc_job_model: AdhocJobModel
    start_time: float = 0
    end_time: float = 0

    async def init(
        self,
        adhoc_job_model: AdhocJobModel,
    ):
        self.sched_time = {}
        self.scheduled = {}
        self.executing = {}
        self.adhoc_job_model = adhoc_job_model
        return self
