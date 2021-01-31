import json
import unittest
from unittest.mock import MagicMock

from pjobq.apptypes import CronJob, JobHandler
import pjobq.logic.jobs.cron as cron

from testutils.fixtures import cron_job
from testutils.mocks import hack_pycron_is_now, mock_event_loop


class TestCron(unittest.TestCase):

    def test_run_scheduled_cron_jobs(self):
        jobs = [cron_job()] * 10
        hack_pycron_is_now(lambda x, y: True)
        mock_event_loop.create_task = MagicMock()
        handler = MagicMock()
        cron.run_scheduled_cron_jobs(
            dt=None,
            cron_jobs=jobs,
            handler=handler
        )
        return


if __name__ == '__main__':
    unittest.main()
