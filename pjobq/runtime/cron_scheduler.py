"""
Load all known cron jobs at once.
Keep track of changes to the table, and reload when necessary.
"""

import asyncio
from asyncio import Task
import logging
import time
from typing import Callable, Awaitable

from ..apptypes import JobHandler, CronJob
from ..constants import CRON_NOTIFY_CHANNEL, NOTIFY_UPDATE_CMD
from ..db import DB
from ..models import CronJobModel
from ..util import delay_execution


class CronScheduler:
    db: DB
    cron_model: type[CronJobModel]
    cron_jobs: list[CronJob]

    async def init(self, db: DB, cron_model: type[CronJobModel]):
        self.db = db
        self.cron_model = cron_model
        self.cron_jobs = []
        await self.db.add_pg_notify_listener(
            CRON_NOTIFY_CHANNEL, self.on_cron_table_notify
        )
        await self.reload_cron_jobs()
        return self

    async def reload_cron_jobs(self) -> None:
        "relaod all cron jobs"
        logging.info("reloading cron jobs")
        self.cron_jobs = await self.cron_model.get_all(self.db)
        return

    async def on_cron_table_notify(self, payload: str) -> None:
        "handler for pg_notify called for cron topic"
        if payload == NOTIFY_UPDATE_CMD:
            return await self.reload_cron_jobs()
        logging.error("unknown cron notify payload -> %s", payload)
        return
