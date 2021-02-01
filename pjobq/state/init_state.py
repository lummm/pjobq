"""
This wires together interfaces with their implementations,
returning the state of the application.
"""

import asyncio

from ..db import DBImpl
from ..models import CronJobModelImpl, AdhocJobModelImpl
from ..apphttp import AppHttpImpl
from .adhoc_scheduler import AdhocScheduler
from .cron_scheduler import CronScheduler
from .state import State


async def init(
    loop: asyncio.AbstractEventLoop,
    db=DBImpl(),
    cron_model=CronJobModelImpl,
    adhoc_model=AdhocJobModelImpl,
    http=AppHttpImpl(),
) -> State:
    state = State(
        db=db,
        cron_model=cron_model,
        adhoc_model=adhoc_model,
        http=http,
        loop=loop,
        adhoc_scheduler=AdhocScheduler(),
        cron_scheduler=CronScheduler(),
    )
    await state.db.init()
    await state.http.init()
    await state.adhoc_scheduler.init(state.db, state.adhoc_model)
    await state.cron_scheduler.init(state.db, state.cron_model, loop)
    return state


async def default_init(loop: asyncio.AbstractEventLoop) -> State:
    return await init(loop)
