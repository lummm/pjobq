import time

from pjobq.apptypes import AdhocJob
from pjobq.db import get_data_class_convertor

from .interface import AdhocJobModel


adhoc_job_converter = get_data_class_convertor(AdhocJob)


class AdhocJobModelImpl(AdhocJobModel):
    "adhoc job model implementation"

    async def get_all_in_range(
        self,
        start_time: float,
        end_time: float,
    ) -> list[AdhocJob]:
        sql = """
        SELECT job_id,
               job_name,
               EXTRACT(epoch FROM schedule_ts) schedule_ts,
               cmd_type,
               cmd_payload
          FROM adhoc_job
         WHERE schedule_ts >= to_timestamp($1)
           AND schedule_ts <= to_timestamp($2)
        """
        rows = await self.db.fetch(sql, [start_time, end_time])
        return [adhoc_job_converter(row) for row in rows]

    async def set_job_completed(
        self, job_id: str, completed_ts: float = time.time()
    ) -> None:
        sql = """
        UPDATE adhoc_job
           SET completed_ts = to_timestamp($2)
         WHERE job_id = $1
        """
        await self.db.execute(sql, [job_id, completed_ts])

    async def create_job(
        self,
        *,
        schedule_ts: float,
        job_name: str,
        cmd_type: str,
        cmd_payload: str,
    ) -> None:
        sql = """
        SELECT adhoc_job_create(
                 p_schedule_ts => to_timestamp($1),
                 p_job_name => $2,
                 p_cmd_type => $3,
                 p_cmd_payload => $4
               )
        """
        await self.db.execute(sql, [schedule_ts, job_name, cmd_type, cmd_payload])
        return
