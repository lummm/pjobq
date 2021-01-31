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
from ..constants import ADHOC_JOB_INTERVAL_S
from .adhoc_scheduler import AdhocScheduler
from .cron_scheduler import CronScheduler


class State:
    """
    db: database interface
    cron_model: interface to cron_job table
    adhoc_model: interface to adhoc_job table
    cron_jobs: all known cron_jobs
    adhoc_scheduler: adhoc job scheduling service
    """

    db: DB
    cron_model: type[CronJobModel]
    adhoc_model: type[AdhocJobModel]
    http: AppHttp
    loop: asyncio.AbstractEventLoop
    adhoc_scheduler: AdhocScheduler
    cron_scheduler: CronScheduler

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
        self.db = db
        await http.init()
        self.http = http
        self.cron_model = cron_model
        self.adhoc_model = adhoc_model
        self.adhoc_scheduler = await AdhocScheduler().init()
        self.cron_scheduler = await CronScheduler().init(self.db, self.cron_model)
        return


async def default_init() -> State:
    state = State()
    await state.init()
    return state
