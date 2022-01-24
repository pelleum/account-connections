from enum import Enum
from typing import Any, List, Mapping, Optional, Union

from pydantic import BaseModel, Field

from app.usecases.schemas import institutions

############# Our API Robinhood Models #############


class LoginAction(str, Enum):
    UPDATE = "UPDATE"
    CREATE = "CREATE"


class CreateOrUpdateAssetsOnLogin(BaseModel):
    action: LoginAction
    brokerage_portfolio: institutions.UserBrokerageHoldings


class InstrumentTracking(BaseModel):
    tracked_instruments: Optional[Mapping[str, Any]]


############# Robinhood Client Exceptions #############
class RobinhoodException(institutions.InstitutionException):
    """Generic Robinhood exception"""


class RobinhoodApiError(institutions.InstitutionApiError, RobinhoodException):
    """Errors raised by Robinhood's API"""

    status: int
    detail: str


class APIErrorBody(BaseModel):
    detail: str


############# Robinhood Client Models #############


class LoginPayload(BaseModel):
    """Payload initially sent to Robinhood to login"""

    client_id: str
    expires_in: int
    grant_type: str
    username: Optional[str]
    password: Optional[str]
    scope: str
    challenge_type: str
    refresh_token: Optional[str]
    device_token: str
    mfa_code: Optional[str] = None


class PositionData(BaseModel):
    """Position Data that gives us the instrument url and the average buy price of the asset"""

    instrument: str = Field(
        ...,
        description="The Robinhood URL for this specific instrument.",
        example="https://api.robinhood.com/instruments/e39ed23a-7bd1-4587-b060-71988d9ef483/",
    )
    instrument_id: str = Field(
        ...,
        description="The Robinhood unique identifier for this instrument.",
        example="e39ed23a-7bd1-4587-b060-71988d9ef483",
    )
    average_buy_price: str = Field(
        ...,
        description="The user's average buy price for this specific asset.",
        example="631.0196",
    )
    quantity: str = Field(
        ...,
        description="The number of shares of the asset the user owns.",
        example="29.04380500",
    )


class NameData(BaseModel):
    """The data that we're concerned with in a get name by symbol response"""

    name: Optional[str] = Field(
        None, description="An individual asset's name.", example="Tesla"
    )
    simple_name: Optional[str] = Field(
        None, description="An individual asset's name.", example="Tesla"
    )


############# Robinhood Client Responses #############


class SuccessfulLoginResponse(BaseModel):
    """Successful Robinhood login response with token."""

    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    mfa_code: Optional[str]
    backup_code: Optional[str]


class PositionDataResponse(BaseModel):
    """Position Data Response"""

    results: List[PositionData] = None


class InstrumentByURLResponse(BaseModel):
    """Instrument data (used to get ticker symbol)"""

    symbol: str = Field(
        ..., description="An individual asset's ticker symbol.", example="TSLA"
    )


class NameDataResponse(BaseModel):
    """Get name by symbol response"""

    results: List[NameData]


class RobinhoodClientResponse(BaseModel):
    """Response from Robinhood Client. The response body is optional
    to account for a potential 401, in which case, the body will not fit
    any of the desired models, but the status is still needed."""

    status: int
    response_body: Optional[
        Union[
            SuccessfulLoginResponse,
            NameDataResponse,
            InstrumentByURLResponse,
            PositionDataResponse,
        ]
    ] = None
