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


class DBImpl(DB):
    con: DBCon

    async def init(self):
        self.con = await asyncpg.connect(
            user=ENV.PGUSER,
            password=ENV.PGPASSWORD,
            database=ENV.PGDB,
            host=ENV.PGHOST,
        )
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
