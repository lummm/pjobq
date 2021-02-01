import json
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

import pjobq.logic.jobs.adhoc as adhoc

from testutils.fixtures import http_job
from testutils.mocks import mock_event_loop, mock_adhoc_job_model, mock_db


class TestAdhoc(IsolatedAsyncioTestCase):

    async def test_run_adhoc_job(self):
        job = http_job()
        handler = AsyncMock()
        await adhoc.run_adhoc_job(
            mock_db,
            mock_adhoc_job_model,
            handler,
            job
        )
        handler.assert_called_with(job)
        mock_adhoc_job_model.set_job_completed \
            .assert_called_with(mock_db, job.job_id)
        return


if __name__ == '__main__':
    unittest.main()
