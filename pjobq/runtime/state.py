"""
Runtime state.
This wires together interfaces with their implementations.
Note that runtime state is mutable.
Because we are single threaded this doesn't really present an issue,
so long as we aren't careless with mutability.
"""

import asyncio
import logging

from ..apptypes import CronJob, PgNotifyListener, NotifyChannel, JobHandler, AdhocJob
from .. import constants as constants
from ..models import CronJobModelImpl, CronJobModel, AdhocJobModel, AdhocJobModelImpl
from ..db import DBImpl, DB
from ..apphttp import AppHttp, AppHttpImpl
from .job_scheduler import JobScheduler
from ..constants import ADHOC_JOB_INTERVAL_S


class State:
    """
    db: database interface
    cron_jobs: all known cron_jobs
    """

    http: AppHttp
    db: DB
    cron_model: type[CronJobModel]
    adhoc_model: type[AdhocJobModel]
    cron_jobs: list[CronJob]
    scheduler: JobScheduler
    loop: asyncio.AbstractEventLoop

    async def init(
        self,
        db: DB = DBImpl(),
        cron_model: type[CronJobModel] = CronJobModelImpl,
        adhoc_model: type[AdhocJobModel] = AdhocJobModelImpl,
        http: AppHttp = AppHttpImpl(),
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
    ) -> None:
        self.loop = loop
        await db.init()
        await http.init()
        self.http = http
        self.db = db
        self.cron_model = cron_model
        self.adhoc_model = adhoc_model
        self.cron_jobs = []
        await self.reload_cron_jobs()
        await self.register_notify_cbs(constants.CRON_NOTIFY_CHANNEL)
        self.scheduler = JobScheduler()
        return

    def schedule_adhoc_jobs(
        self,
        jobs: list[AdhocJob],
        handler: JobHandler,
    ) -> None:
        "load the next window of adhoc jobs"
        self.scheduler.schedule_jobs(self.loop, jobs, handler)
        return

    async def reload_cron_jobs(self) -> None:
        "relaod all cron jobs"
        logging.info("reloading cron jobs")
        self.cron_jobs = await self.cron_model.get_all(self.db)
        return

    async def register_notify_cbs(self, channel: NotifyChannel) -> None:
        "register all callbacks for a certain channel"
        for cb in self.get_pg_notify_listeners(channel):
            await self.db.add_pg_notify_listener(channel, cb)
        return

    def get_pg_notify_listeners(self, channel: str) -> list[PgNotifyListener]:
        "get all listeners we want to register for a given channel"
        if channel == constants.CRON_NOTIFY_CHANNEL:
            return [self.on_cron_table_notify]
        empty: list[PgNotifyListener] = []
        return empty

    async def on_cron_table_notify(self, payload: str) -> None:
        "handler for pg_notify called for cron topic"
        if payload == constants.NOTIFY_UPDATE_CMD:
            return await self.reload_cron_jobs()
        logging.error("unknown cron notify payload -> %s", payload)
        return


async def default_init() -> State:
    state = State()
    await state.init()
    return state
