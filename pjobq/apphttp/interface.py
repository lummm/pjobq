from abc import ABC, abstractmethod


class AppHttp(ABC):
    "app http interface"

    @abstractmethod
    async def init(self) -> None:
        "init the http client.  Idempotent."
        pass

    @abstractmethod
    async def req(self, method: str, url: str, **kwargs) -> int:
        "Perform a request, returning the status code."
        pass
