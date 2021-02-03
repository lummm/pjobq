from pjobq.apptypes import CronJob
from pjobq.db import DB, get_data_class_convertor

from .interface import CronJobModel


cron_job_converter = get_data_class_convertor(CronJob)


class CronJobModelImpl(CronJobModel):
    "cron job model implementation"

    async def get_all(self) -> list[CronJob]:
        sql = """
        SELECT job_id,
               job_name,
               cron_schedule,
               cmd_type,
               cmd_payload
          FROM cron_job
         WHERE enabled
        """
        rows = await self.db.fetch(sql)
        return [cron_job_converter(row) for row in rows]

    async def create_job(
        self,
        *,
        cron_schedule: str,
        job_name: str,
        cmd_type: str,
        cmd_payload: str,
        enabled: bool = True
    ) -> None:
        sql = """
        SELECT cron_job_create(
                 p_cron_schedule => $1,
                 p_job_name => $2,
                 p_cmd_type => $3,
                 p_cmd_payload => $4,
                 p_enabled => $5
               )
        """
        await self.db.fetch(
            sql, [cron_schedule, job_name, cmd_type, cmd_payload, enabled]
        )
        return
