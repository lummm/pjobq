from abc import ABC, abstractmethod
import time

from ...apptypes import AdhocJob
from ...db import DB


class AdhocJobModel(ABC):
    "interface to adhoc_jobs table"

    @staticmethod
    @abstractmethod
    async def get_all_in_range(
        db: DB,
        start_time: float,
        end_time: float,
    ) -> list[AdhocJob]:
        "Fetch all adhoc_jobs in time range.  Inclusive endpoints."
        pass

    @staticmethod
    @abstractmethod
    async def set_job_completed(
        db: DB, job_id: str, completed_ts: float = time.time()
    ) -> None:
        "Mark a job as completed, defaults to now."
        pass
