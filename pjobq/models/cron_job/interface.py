from abc import ABC, abstractmethod

from ...apptypes import CronJob
from ...db import DB


class CronJobModel(ABC):
    "interface to cron_jobs table"

    async def init(self, db: DB) -> None:
        self.db = db
        return

    @abstractmethod
    async def get_all(self) -> list[CronJob]:
        "fetch all cron_jobs"
        pass

    @abstractmethod
    async def create_job(
        self,
        *,
        cron_schedule: str,
        job_name: str,
        cmd_type: str,
        cmd_payload: str,
        enabled: bool = True
    ) -> None:
        "Create cron job."
        pass
