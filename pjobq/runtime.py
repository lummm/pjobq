"""
Runtime state.
This wires together interfaces with their implementations.
Note that runtime state is mutable.
Because we are single threaded this doesn't really present an issue,
so long as we aren't careless with mutability.
"""

import asyncio
import logging
from types import SimpleNamespace

from .apptypes import CronJob, PgNotifyListener, NotifyChannel
from . import constants as constants
from .models import CronJobModelImpl as CronJobModel
from .db import DBImpl as DB


# public
class State(SimpleNamespace):
    """
    db: database interface
    cron_jobs: all known cron_jobs
    """

    db: DB
    cron_jobs: list[CronJob]


async def init() -> State:
    db = DB()
    await db.init()
    state = State(
        db=db,
        cron_jobs=[],
    )
    await reload_cron_jobs(state)
    await register_notify_cbs(state, constants.CRON_NOTIFY_CHANNEL)
    return state


async def reload_cron_jobs(state: State) -> None:
    "relaod all cron jobs"
    logging.info("reloading cron jobs")
    state.cron_jobs = await CronJobModel.get_all(state.db)
    return


# private
async def register_notify_cbs(state: State, channel: NotifyChannel) -> None:
    "register all callbacks for a certain channel"
    for cb in get_pg_notify_listeners(state, channel):
        await state.db.add_pg_notify_listener(channel, cb)
    return


def get_pg_notify_listeners(state: State, channel: str) -> list[PgNotifyListener]:
    "get all listeners we want to register for a given channel"
    if channel == constants.CRON_NOTIFY_CHANNEL:
        return [on_cron_table_notify_factory(state)]
    return []


def on_cron_table_notify_factory(state: State) -> PgNotifyListener:
    """ We close over the state to update it in the future. """

    def on_cron_table_notify(payload: str):
        "handler for pg_notify called for cron topic"
        if payload == constants.NOTIFY_UPDATE_CMD:
            return reload_cron_jobs(state)
        logging.error("unknown cron notify payload -> %s", payload)
        return

    return on_cron_table_notify
