"""
Database (postgres) interface.
"""

import asyncio
import dataclasses
import logging
from typing import Callable, List

import asyncpg  # type: ignore

from .apptypes import CronUpdateCallback, Job, DBCon
from .env import ENV


CRON_NOTIFY_CHANNEL = "cron_job"
CRON_TABLE_UPDATE_CMD = "update"


async def connect(
    on_cron_update: CronUpdateCallback = lambda x: None,
) -> DBCon:
    con = await asyncpg.connect(
        user=ENV.PGUSER,
        password=ENV.PGPASSWORD,
        database=ENV.PGDB,
        host=ENV.PGHOST,
    )
    await con.add_listener(CRON_NOTIFY_CHANNEL, _create_update_cb(on_cron_update))
    return con


async def load_cron_jobs(con: DBCon) -> List[Job]:
    rows = await _fetch_cron_jobs(con)
    return [_raw_row_to_cron_job(row) for row in rows]


# private
def _get_data_class_convertor(clazz):
    "factory function returning map from asyncpg record to named tuple type"
    field_names = [field.name for field in dataclasses.fields(clazz)]

    def converter(record: asyncpg.Record):
        return clazz(**dict([(field, record.get(field)) for field in field_names]))

    return converter


_raw_row_to_cron_job: Callable[[asyncpg.Record], Job] = _get_data_class_convertor(Job)


async def _fetch_cron_jobs(con: DBCon) -> List[Job]:
    "returns all entries in cron_job"
    sql = """
    SELECT job_id,
           job_name,
           cron_schedule,
           cmd_type,
           cmd_payload
      FROM cron_job
    """
    async with con.transaction():
        return await con.fetch(sql)
    return


def _create_update_cb(cb: CronUpdateCallback):
    "factory function for a pg_notify listener on the asyncpg connection"

    def on_cron_job_notify(con: DBCon, _pid, channel: str, payload: str):
        logging.info("cron_job table update")

        async def load_jobs_for_cb():
            cb(await load_cron_jobs(con))

        if channel == CRON_NOTIFY_CHANNEL:
            if payload == CRON_TABLE_UPDATE_CMD:
                loop = asyncio.get_event_loop()
                loop.create_task(load_jobs_for_cb())
        return

    return on_cron_job_notify
