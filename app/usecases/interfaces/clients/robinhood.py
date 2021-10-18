from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from app.usecases.schemas import robinhood


class RobinhoodException(Exception):
    pass


class RobinhoodApiError(RobinhoodException):
    """Errors raised by Robinhood's API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.http_status = kwargs.get("http_status")
        self.detail = kwargs.get("detail")


class IRobinhoodClient(ABC):
    @abstractmethod
    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict] = None,
        json_body: Any = None,
    ) -> Mapping[str, Any]:
        """Facilitate actual API call"""

    @abstractmethod
    async def login(self, payload: robinhood.InitialLoginPayload) -> Mapping:
        """Login to Robinhood"""
