from unittest.mock import AsyncMock, MagicMock

from pjobq.apphttp import AppHttp
from pjobq.state import State
from pjobq.state.adhoc_scheduler import AdhocSchedulerState
from pjobq.state.cron_scheduler import CronSchedulerState
from pjobq.db import DB
from pjobq.models import AdhocJobModel
from pjobq.models import CronJobModel


class AppHttpMock:
    pass
AppHttp.register(AppHttpMock)
http_mock = AppHttpMock()
http_mock.init = AsyncMock()
http_mock.req = AsyncMock()


class MockEventLoop():
    pass
mock_event_loop = MockEventLoop()
mock_event_loop.create_task = MagicMock()


def hack_pycron_is_now(new_handler):
    import pycron
    pycron.is_now = new_handler
    return


class MockDB:
    pass
DB.register(MockDB)
mock_db = MockDB()
mock_db.add_pg_notify_listener = AsyncMock()
mock_db.fetch = AsyncMock()
mock_db.execute = AsyncMock()


class MockAdhocJobModel:
    pass
AdhocJobModel.register(MockAdhocJobModel)
# TODO: make a fn
mock_adhoc_job_model = MockAdhocJobModel()
mock_adhoc_job_model.get_all_in_range = AsyncMock()
mock_adhoc_job_model.set_job_completed = AsyncMock()


class MockCronJobModel:
    pass
CronJobModel.register(MockCronJobModel)
mock_cron_job_model = MockCronJobModel()
mock_cron_job_model.get_all = AsyncMock()


async def mock_adhoc_scheduler() -> AdhocSchedulerState:
    scheduler = AdhocSchedulerState()
    return await scheduler.init(
        mock_adhoc_job_model
    )


async def mock_cron_scheduler() -> CronSchedulerState:
    scheduler = CronSchedulerState()
    return await scheduler.init(
        mock_cron_job_model
    )


class MockState:
    pass
mock_state = MockState()
