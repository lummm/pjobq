import asyncio
import time
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call

import pjobq.util as util


class TestUtil(IsolatedAsyncioTestCase):

    async def test_attempt_forever(self):
        mock = MagicMock()
        attempt = 0
        trials = 2
        async def test_cb():
            nonlocal attempt
            if attempt < trials:
                mock(attempt)
                attempt += 1
                raise Exception("this is an intentional exception")
            return
        await util.attempt_forever("test attempt forever", test_cb)
        mock.assert_has_calls([call(i) for i in range(trials)])
        return

    async def test_create_unfailing_task(self):
        loop = asyncio.get_event_loop()
        async def test_fn():
            raise Exception("FAIL - but won't crash")
        await util.create_unfailing_task("test unfailing task", loop, test_fn())
        return


    async def test_delay_execution(self):
        mock = MagicMock()
        async def test_fn():
            mock(time.time())
        now = time.time()
        soon = now + 1
        await util.delay_execution(test_fn(), soon)
        self.assertAlmostEqual(mock.call_args_list[0].args[0], soon, 1) # we aren't very precise
        return


if __name__ == '__main__':
    unittest.main()
