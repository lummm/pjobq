"""
database (postgres) implementation.
"""

import asyncio
import dataclasses
import logging
from typing import Any, Callable

import asyncpg  # type: ignore

from ..apptypes import DBCon, PgNotifyListener
from ..env import ENV
from .interface import DB
from . import sql


INIT_SQL = [
    # note all things here must be idempotent,
    # as they are run every time we init
    sql.EXTENSION_UUID,
    sql.FN_CHECK_CMD_TYPE,
    sql.TABLE_CRON_JOB,
    sql.FN_CRON_JOB_CREATE,
    sql.FN_CRON_JOB_CREATE_HTTP,
    sql.TABLE_ADHOC_JOB,
    sql.FN_ADHOC_JOB_CREATE,
    sql.FN_ADHOC_JOB_CREATE_HTTP,
    sql.FN_CRON_JOB_DELETE,
    sql.FN_ADHOC_JOB_DELETE,
]


def get_connect_args() -> dict:
    return {
        "user": ENV.PGUSER,
        "password": ENV.PGPASSWORD,
        "database": ENV.PGDB,
        "host": ENV.PGHOST,
    }


class DBImpl(DB):
    pool: asyncpg.pool.Pool
    dedicated_cons: list[DBCon]

    async def init(self):
        self.pool = await asyncpg.create_pool(
            **get_connect_args(),
            min_size=5,
            max_size=10,
        )
        for cmds in INIT_SQL:
            await self.execute(cmds)
        self.dedicated_cons = []
        return

    async def add_pg_notify_listener(
        self,
        channel: str,
        cb: PgNotifyListener,
    ):
        con = await asyncpg.connect(**get_connect_args())
        await con.add_listener(channel, _create_notify_cb(cb))
        self.dedicated_cons.append(con)
        return

    async def fetch(self, sql: str, bindargs: list[str] = []) -> list[asyncpg.Record]:
        async with self.pool.acquire() as con:
            return await con.fetch(sql, *bindargs)

    async def execute(self, sql: str, bindargs: list[Any] = []) -> None:
        async with self.pool.acquire() as con:
            return await con.execute(sql, *bindargs)


def _create_notify_cb(cb: PgNotifyListener):
    """
    Factory function for a pg_notify listener on the asyncpg connection.
    We expose a simpler cb interface.
    """

    def on_cron_job_notify(_con: DBCon, _pid: int, _channel: str, payload: str):
        cb(payload)

    return on_cron_job_notify
