from unittest.mock import AsyncMock, MagicMock

from pjobq.apphttp import AppHttp


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
