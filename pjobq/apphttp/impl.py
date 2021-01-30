from abc import ABC, abstractmethod
import logging

import aiohttp
from .interface import AppHttp


class AppHttpImpl(AppHttp):
    "app http interface"

    session: aiohttp.ClientSession

    async def init(self) -> None:
        if getattr(self, "session", None):
            await self.session.close()
        self.session = aiohttp.ClientSession()
        return

    async def req(self, method: str, url: str, **kwargs) -> int:
        async with self.session.request(method, url, **kwargs) as res:
            if not res.ok:
                logging.error("http request %s %s failed", method, url)
            return res.status
        return
