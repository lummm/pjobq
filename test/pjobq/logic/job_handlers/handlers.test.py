import json
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from pjobq.apptypes import HttpJob
import pjobq.logic.job_handlers.handlers as handlers

from testutils.mocks import http_mock
from testutils.fixtures import http_job


class TestJobHandlers(IsolatedAsyncioTestCase):

    async def test_handle_http(self):
        http_mock.req = AsyncMock(return_value=200)
        await handlers.handle_http(http_mock, http_job())
        return


if __name__ == '__main__':
    unittest.main()
