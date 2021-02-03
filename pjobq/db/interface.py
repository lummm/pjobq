from abc import ABC, abstractmethod
from typing import Any

import asyncpg  # type: ignore

from ..apptypes import PgNotifyListener


class DB(ABC):
    "database interface, specific to Postgres"

    @abstractmethod
    async def init(self) -> None:
        "init the database connection.  should be idenpotent"
        pass

    @abstractmethod
    async def add_pg_notify_listener(self, channel: str, cb: PgNotifyListener) -> None:
        """
        Add a listener for pg_notify events.
        All listeners share a dedicated db connection.
        """
        pass

    @abstractmethod
    async def fetch(self, sql: str, bindargs: list[Any] = []) -> list[asyncpg.Record]:
        "fetch the results of an arbitrary sql query"
        pass

    @abstractmethod
    async def execute(self, sql: str, bindargs: list[Any] = []) -> None:
        "exwecute arbitrary sql"
        pass
