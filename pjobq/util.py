"""
Misc utils
"""

import asyncio
import logging

DEFAULT_WAILT_LIMIT_S = 128  # approx 2 mins


# TODO: set type of f
async def attempt_forever(
    name: str,
    fn,
    retry_wait_limit_s: int = DEFAULT_WAILT_LIMIT_S,
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
