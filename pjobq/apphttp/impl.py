from abc import ABC, abstractmethod
import logging
from typing import Optional

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

    async def req(self, method: str, url: str, data: Optional[str] = "") -> int:
        logging.debug("http req %s %s", method, url)
        async with self.session.request(method, url, data=data) as res:
            if not res.ok:
                logging.error("http request %s %s failed", method, url)
            return res.status
        return
