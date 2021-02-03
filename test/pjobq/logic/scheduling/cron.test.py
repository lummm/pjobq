import json
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from pjobq.apptypes import CronJob, JobHandler
import pjobq.logic.scheduling.cron as cron

from testutils.fixtures import cron_job
from testutils.mocks import hack_pycron_is_now, mock_event_loop


class TestCron(IsolatedAsyncioTestCase):

    async def test_run_scheduled_cron_jobs(self):
        jobs = [cron_job()] * 10
        hack_pycron_is_now(lambda x, y: True)
        handler = AsyncMock()
        await cron.run_scheduled_cron_jobs(
            dt=None,
            cron_jobs=jobs,
            handler=handler
        )
        self.assertEqual(len(handler.call_args_list), 10)
        return


if __name__ == '__main__':
    unittest.main()
