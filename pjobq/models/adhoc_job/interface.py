from abc import ABC, abstractmethod

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
