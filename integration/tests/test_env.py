"""
Test state.
Since we're testing scheduling, most tests are wrapped
in a timeout somewhere, in case something is not scheduled.
"""

import asyncio


DEFAULT_REQ_TIMEOUT_S = 10


def fail():
    loop = asyncio.get_event_loop()
    loop.stop()
    raise Exception("tests failed")
    return

class TestEnv:
    def __init__(
            self,
            *,
            req_q: asyncio.Queue,
    ):
        self.req_q = req_q
        return

    async def wait_next_req(
            self,
            timeout: int = DEFAULT_REQ_TIMEOUT_S
    ) -> str:
        return await asyncio.wait_for(
            self.req_q.get(),
            timeout
        )

    def assert_eq(self, exp, act):
        if exp != act:
            print("expected: ", exp, "actual: ", act)
            fail()
        return
