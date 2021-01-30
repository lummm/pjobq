from abc import ABC, abstractmethod

from ...apptypes import CronJob
from ...db import DB


class CronJobModel(ABC):
    "interface to cron_jobs table"

    @staticmethod
    @abstractmethod
    async def get_all(db: DB) -> list[CronJob]:
        "fetch all cron_jobs"
        pass
