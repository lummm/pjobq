import asyncio
import json
import time
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from pjobq.constants import NOTIFY_UPDATE_CMD

import pjobq.logic.scheduling.adhoc as adhoc

from testutils.fixtures import http_job, adhoc_job
from testutils.mocks import (
    mock_event_loop,
    mock_adhoc_job_model,
    mock_db,
    mock_adhoc_scheduler
)


class TestAdhoc(IsolatedAsyncioTestCase):

    async def test_run_adhoc_job(self):
        job = http_job()
        handler = AsyncMock()
        await adhoc.run_adhoc_job(
            mock_adhoc_job_model,
            handler,
            job
        )
        handler.assert_called_with(job)
        mock_adhoc_job_model.set_job_completed \
            .assert_called_with(job.job_id)
        return

    async def test_schedule_adhoc_jobs(self):
        loop = asyncio.get_event_loop()
        scheduler_state = await mock_adhoc_scheduler()
        now = time.time()
        handler = AsyncMock()
        spacing = 0.01
        jobs = [
            adhoc_job(
                "job" + str(now + (i * spacing)),
                now + (i * spacing)
            )
            for i in range(1, 5)
        ]
        adhoc.schedule_adhoc_jobs(
            scheduler_state,
            loop,
            jobs,
            handler,
        )
        for i in range(1, 5):
            await asyncio.sleep(spacing)
            handler.assert_called_with(jobs[i - 1])
        return

    async def test_on_adhoc_table_notify_factory(self):
        loop = mock_event_loop
        scheduler = await mock_adhoc_scheduler()
        handler = MagicMock()
        on_notify = adhoc.on_adhoc_table_notify_factory(loop, scheduler, handler)
        on_notify(NOTIFY_UPDATE_CMD)
        loop.create_task.assert_called()
        return

    async def test_reload_jobs_in_adhoc_window(self):
        loop = mock_event_loop
        handler = MagicMock()
        scheduler = await mock_adhoc_scheduler()
        scheduler.start_time = 100
        scheduler.end_time = 200
        await adhoc.reload_jobs_in_adhoc_window(loop, handler, scheduler)
        scheduler.adhoc_job_model.get_all_in_range.assert_called_with(100, 200)
        return


if __name__ == '__main__':
    unittest.main()
