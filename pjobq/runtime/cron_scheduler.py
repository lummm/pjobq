"""
Load all known cron jobs at once.
Keep track of changes to the table, and reload when necessary.
TODO: move all functions except 'init' into logic
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
    loop: asyncio.AbstractEventLoop

    async def init(
        self, db: DB, cron_model: type[CronJobModel], loop: asyncio.AbstractEventLoop
    ):
        self.db = db
        self.cron_model = cron_model
        self.cron_jobs = []
        self.loop = loop
        await self.db.add_pg_notify_listener(
            CRON_NOTIFY_CHANNEL, self.on_cron_table_notify
        )
        await self.reload_cron_jobs()
        return self

    async def reload_cron_jobs(self) -> None:
        "relaod all cron jobs"
        self.cron_jobs = await self.cron_model.get_all(self.db)
        logging.info("loaded %s cron jobs", len(self.cron_jobs))
        return

    def on_cron_table_notify(self, payload: str) -> None:
        """
        Handler for pg_notify called for cron topic.
        Because this is sync, we need to create a task
        """
        if payload == NOTIFY_UPDATE_CMD:
            self.loop.create_task(self.reload_cron_jobs())
            return
        logging.error("unknown cron notify payload -> %s", payload)
        return
