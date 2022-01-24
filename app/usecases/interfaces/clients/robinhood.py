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


class RobinhoodUnauthorizedException(Exception):
    """Raised when a 401 unauthorized is returned"""


class APIErrorBody(BaseModel):
    detail: str


class IRobinhoodClient(ABC):
    @abstractmethod
    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Facilitate actual API call"""

    @abstractmethod
    async def login(
        self, payload: robinhood.LoginPayload, challenge_id: str = None
    ) -> Mapping[str, Any]:
        """Login to Robinhood and return the response"""

    @abstractmethod
    async def respond_to_challenge(
        self, challenge_code: str, challenge_id: str
    ) -> None:
        """Respond to challenge issued by Robinhood for those with 2FA disabled"""

    @abstractmethod
    async def get_positions_data(
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
