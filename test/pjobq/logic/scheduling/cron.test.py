import json
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from pjobq.constants import NOTIFY_UPDATE_CMD

import pjobq.logic.scheduling.cron as cron

from testutils.fixtures import cron_job
from testutils.mocks import hack_pycron_is_now, mock_event_loop, mock_cron_scheduler


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

    async def reload_cron_jobs_test(self):
        jobs = [cron_job()] * 5
        scheduler = await mock_cron_scheduler()
        scheduler.cron_job_model.get_all = AsyncMock(return_value=jobs)
        await cron.reload_cron_jobs(scheduler)
        self.assertEqual(scheduler.cron_jobs, jobs)
        return

    async def on_cron_table_notify_test(self):
        loop = mock_event_loop
        scheduler = await mock_cron_scheduler()
        handler = MagicMock()
        on_notify = cron.on_cron_table_notify_factory(loop, scheduler)
        on_notify(NOTIFY_UPDATE_CMD)
        loop.create_task.assert_called()
        return


if __name__ == '__main__':
    unittest.main()
