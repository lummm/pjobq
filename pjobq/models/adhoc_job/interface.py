from abc import ABC, abstractmethod
import time

from ...apptypes import AdhocJob
from ...db import DB


class AdhocJobModel(ABC):
    "interface to adhoc_jobs table"

    async def init(self, db: DB) -> None:
        self.db = db
        return

    @abstractmethod
    async def get_all_in_range(
        self,
        start_time: float,
        end_time: float,
    ) -> list[AdhocJob]:
        "Fetch all adhoc_jobs in time range.  Inclusive endpoints."
        pass

    @abstractmethod
    async def set_job_completed(
        self, job_id: str, completed_ts: float = time.time()
    ) -> None:
        "Mark a job as completed, defaults to now."
        pass

    @abstractmethod
    async def create_job(
        self, *, schedule_ts: float, job_name: str, cmd_type: str, cmd_payload: str
    ) -> None:
        "Create adhoc job."
        pass
