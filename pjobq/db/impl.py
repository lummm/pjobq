"""
database (postgres) implementation.
"""

import asyncio
import dataclasses
import logging
from typing import Callable

import asyncpg  # type: ignore

from ..apptypes import DBCon, PgNotifyListener
from ..env import ENV
from .interface import DB
from . import sql


INIT_SQL = [
    # note all things here must be idempotent,
    # as they are run every time we init
    sql.EXTENSION_UUID,
    sql.TABLE_CRON_JOB,
    sql.FN_CRON_JOB_CREATE,
    sql.FN_CRON_JOB_CREATE_HTTP,
]


class DBImpl(DB):
    con: DBCon

    async def init(self):
        self.con = await asyncpg.connect(
            user=ENV.PGUSER,
            password=ENV.PGPASSWORD,
            database=ENV.PGDB,
            host=ENV.PGHOST,
        )
        for cmds in INIT_SQL:
            await self.con.execute(cmds)
        return

    async def add_pg_notify_listener(
        self,
        channel: str,
        cb: PgNotifyListener,
    ):
        await self.con.add_listener(channel, _create_notify_cb(cb))
        return

    async def fetch(self, sql: str, bindargs: list[str] = []) -> list[asyncpg.Record]:
        async with self.con.transaction():
            return await self.con.fetch(sql, *bindargs)


def _create_notify_cb(cb: PgNotifyListener):
    """
    Factory function for a pg_notify listener on the asyncpg connection.
    We expose a simpler cb interface.
    """

    def on_cron_job_notify(_con: DBCon, _pid: int, _channel: str, payload: str):
        cb(payload)

    return on_cron_job_notify
