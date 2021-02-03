"""
This wires together interfaces with their implementations,
returning the state of the application.
"""

from pjobq.apptypes import EventLoop
from pjobq.db import DBImpl
from pjobq.models import CronJobModelImpl, AdhocJobModelImpl
from pjobq.apphttp import AppHttpImpl

from .adhoc_scheduler import AdhocSchedulerState
from .cron_scheduler import CronSchedulerState
from .state import State


async def init(
    loop: EventLoop,
    db=DBImpl(),
    cron_model=CronJobModelImpl(),
    adhoc_model=AdhocJobModelImpl(),
    http=AppHttpImpl(),
) -> State:
    state = State(
        db=db,
        cron_model=cron_model,
        adhoc_model=adhoc_model,
        http=http,
        loop=loop,
        adhoc_scheduler=AdhocSchedulerState(),
        cron_scheduler=CronSchedulerState(),
    )
    await state.db.init()
    await state.cron_model.init(state.db)
    await state.adhoc_model.init(state.db)
    await state.http.init()
    await state.adhoc_scheduler.init(state.adhoc_model)
    await state.cron_scheduler.init(state.cron_model)
    return state


async def default_init(loop: EventLoop) -> State:
    return await init(loop)
