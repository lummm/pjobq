from unittest.mock import AsyncMock

from pjobq.apphttp import AppHttp


class AppHttpMock:
    pass

AppHttp.register(AppHttpMock)

http_mock = AppHttpMock()
http_mock.init = AsyncMock()
http_mock.req = AsyncMock()
