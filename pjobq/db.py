import asyncio
import logging
from typing import Callable, List, Any

import asyncpg

from .env import ENV


CRON_NOTIFY_CHANNEL = "cron_job"

# an update callback receives the latest cron_jobs
CronUpdateCallback = Callable[[List[Any]], None]


def create_update_cb(cb: CronUpdateCallback):
    def on_cron_job_notify(
            con: asyncpg.Connection,
            _pid,
            channel: str,
            payload: str
    ):
        logging.info("cron_job table update")
        async def load_jobs_for_cb():
            cb(await load_cron_jobs(con))

        if channel == CRON_NOTIFY_CHANNEL:
            if payload == "update":
                loop = asyncio.get_event_loop()
                loop.create_task(load_jobs_for_cb())
        return
    return on_cron_job_notify


async def connect(
        on_cron_update: CronUpdateCallback
) -> asyncpg.Connection:
    # TODO: add retry
    con = await asyncpg.connect(
        user=ENV.PGUSER,
        password=ENV.PGPASSWORD,
        database=ENV.PGDB,
        host=ENV.PGHOST,
    )
    await con.add_listener(
        CRON_NOTIFY_CHANNEL,
        create_update_cb(on_cron_update)
    )
    return con


async def load_cron_jobs(
        con: asyncpg.Connection
) -> List[Any]:
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
