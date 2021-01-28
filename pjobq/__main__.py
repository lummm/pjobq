"""
App entrypoint
"""

import asyncio
from datetime import datetime
from typing import Any, List
from types import SimpleNamespace

import asyncpg

from . import db


class State(SimpleNamespace):
    cron_jobs: List[Any]
    db_con: asyncpg.Connection


def on_cron_update(state: State):
    def update_cron_jobs(jobs: List[Any]) -> None:
        print("updating cron jobs")
        state.cron_jobs = jobs
    return update_cron_jobs


def check_cron_jobs(cron_jobs: List[Any]):
    for job in cron_jobs:
        print("job", job)
    return


async def main():
    state = State(
        cron_jobs = [],
    )
    state.db_conn = await db.connect(
        on_cron_update=on_cron_update(state)
    )
    state.cron_jobs = await db.load_cron_jobs(state.db_conn)
    while True:
        await asyncio.sleep(1)
        if datetime.now().second == 0:
            # cron is up to minute
            check_cron_jobs(state.cron_jobs)
    return


if __name__ == '__main__':
    asyncio.run(main())
