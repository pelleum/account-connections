from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from pydantic import BaseModel

from app.usecases.schemas import robinhood


class RobinhoodException(Exception):
    pass


class RobinhoodApiError(RobinhoodException):
    """Errors raised by Robinhood's API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.http_status = kwargs.get("http_status")
        self.detail = kwargs.get("detail")


class APIErrorBody(BaseModel):
    detail: str


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

    @abstractmethod
    async def get_postitions_data(
        self, access_token: str
    ) -> robinhood.PositionDataResponse:
        """Get posiitions data"""

    @abstractmethod
    async def get_instrument_by_url(
        self, url: str, access_token: str
    ) -> robinhood.InstrumentByURLResponse:
        """Gets instrument, from which, the ticker symbol can be obtained"""

    @abstractmethod
    async def get_name_by_symbol(
        self, symbol: str, access_token: str
    ) -> robinhood.NameDataResponse:
        """Gets asset name by symbol"""
