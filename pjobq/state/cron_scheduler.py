"""
A slice of state living on the parent State object.

Load all known cron jobs at once.
Keep track of changes to the table, and reload when necessary.
TODO: move all functions except 'init' into logic
"""

from pjobq.apptypes import CronJob
from pjobq.models import CronJobModel


class CronSchedulerState:
    cron_model: CronJobModel
    cron_jobs: list[CronJob]

    async def init(self, cron_model: CronJobModel):
        self.cron_model = cron_model
        self.cron_jobs = []
        return self
