"""
Misc utils
"""

import asyncio
import logging
import time
from typing import Awaitable, Callable

from pjobq.apptypes import EventLoop


DEFAULT_WAIT_LIMIT_S = 128  # approx 2 mins


async def attempt_forever(
    name: str,
    fn: Callable[[], Awaitable],
    retry_wait_limit_s: int = DEFAULT_WAIT_LIMIT_S,
):
    "attempt fn forever until success, with exponential backoff"
    attempt = 1
    current_wait = 0
    while True:
        try:
            await asyncio.sleep(current_wait)
            return await fn()
        except Exception as e:
            logging.exception(e)
            attempt += 1
            current_wait = min([2 ** (attempt - 1), retry_wait_limit_s])
            logging.info("%s failure - try again in %s seconds", name, current_wait)
    return


def create_unfailing_task(name: str, loop: EventLoop, aw: Awaitable) -> asyncio.Task:
    """
    Prvents any errors in the task from bubbling up.
    We log the exception but otherwise do nothing.
    """

    async def impl():
        try:
            await aw
        except Exception as e:
            logging.error("task '%s' failed", name)
            logging.exception(e)

    return loop.create_task(impl())


def schedule_execution(
    loop: EventLoop, callback: Callable[[], None], when: float
) -> asyncio.TimerHandle:
    "execute callback at 'when'"
    return loop.call_later(when - time.time(), callback)


def setup_logging(level=logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=f"%(asctime)s.%(msecs)03d "
        "%(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return
