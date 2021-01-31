from ...apptypes import AdhocJob
from .interface import AdhocJobModel
from ...db import DB
from ...db import get_data_class_convertor


adhoc_job_converter = get_data_class_convertor(AdhocJob)


class AdhocJobModelImpl(AdhocJobModel):
    "adhoc job model implementation"

    @staticmethod
    async def get_all_in_range(
        db: DB,
        start_time: float,
        end_time: float,
    ) -> list[AdhocJob]:
        sql = """
        SELECT job_id,
               job_name,
               EXTRACT(epoch FROM schedule_ts),
               cmd_type,
               cmd_payload
          FROM adhoc_job
         WHERE schedule_ts >= to_timestamp($1)
           AND schedule_ts <= to_timestamp($2)
        """
        rows = await db.fetch(sql, [start_time, end_time])
        return [adhoc_job_converter(row) for row in rows]
