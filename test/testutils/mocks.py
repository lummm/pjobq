from unittest.mock import AsyncMock, MagicMock

from pjobq.apphttp import AppHttp
from pjobq.state import State
from pjobq.state.adhoc_scheduler import AdhocSchedulerState
from pjobq.db import DB
from pjobq.models import AdhocJobModel


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
mock_adhoc_job_model = MockAdhocJobModel()
mock_adhoc_job_model.get_all_in_range = AsyncMock()
mock_adhoc_job_model.set_job_completed = AsyncMock()


async def mock_adhoc_scheduler():
    scheduler = AdhocSchedulerState()
    return await scheduler.init(
        mock_adhoc_job_model
    )


class MockState:
    pass
mock_state = MockState()
