from ...apptypes import CronJob
from .interface import CronJobModel
from ...db import DB
from ...db import get_data_class_convertor


cron_job_converter = get_data_class_convertor(CronJob)


class CronJobModelImpl(CronJobModel):
    "cron job model implementation"

    @staticmethod
    async def get_all(db: DB) -> list[CronJob]:
        sql = """
        SELECT job_id,
               job_name,
               cron_schedule,
               cmd_type,
               cmd_payload
          FROM cron_job
        """
        rows = await db.fetch(sql)
        return [cron_job_converter(row) for row in rows]
