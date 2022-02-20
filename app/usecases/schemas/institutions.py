from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, constr


class LoginRequest(BaseModel):
    """JSON body model of request"""

    username: constr(max_length=100) = Field(
        ...,
        description="An encrypted, optional username for the linked account.",
        example="myusername",
    )
    password: constr(max_length=100) = Field(
        ...,
        description="An encrypted, optional password for the linked account.",
        example="password",
    )


class MultiFactorWithChallenge(BaseModel):
    sms_code: constr(max_length=10) = Field(
        ...,
        description="The multifactor (sms) authentication code sent to the user's phone.",
        example="149837",
    )
    challenge_id: constr(max_length=100) = Field(
        ...,
        description="The unique identifier for the challenge that Robinhood issues to those who have 2FA disabled on their accounts.",
        example="ca3cf668-404c-49d2-8510-ea9948ff66aa",
    )


class MultiFactorWithoutChallenge(BaseModel):
    sms_code: constr(max_length=10) = Field(
        ...,
        description="The multifactor (sms) authentication code sent to the user's phone.",
        example="149837",
    )


class MultiFactorAuthCodeRequest(BaseModel):
    with_challenge: Optional[MultiFactorWithChallenge] = None
    without_challenge: Optional[MultiFactorWithoutChallenge] = None


class UserCredentials(LoginRequest):
    """Same as LoginRequest"""


class UserVerificationCredentials(MultiFactorAuthCodeRequest):
    """Same as MultiFactorAuthCodeRequest"""


class InstitutionConnectionBase(BaseModel):
    """Institution Connection Base"""

    username: Optional[str] = Field(
        None,
        description="An encrypted, optional username for the linked account.",
        example="myusername",
    )
    password: Optional[str] = Field(
        None,
        description="An encrypted, optional password for the linked account.",
        example="password",
    )
    json_web_token: Optional[str] = Field(
        None,
        description="A JWT for sending authenticated requests to user's brokerage account.",
        example="eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJpYXQiOjE2MzQwNzA3NDcsImV4cCI6MTYzNDY3NTU0Nywid2E6cmFuZCI6IjhiZjRhNzNkOTlkZWM2OTViOGJjNDU2NmYyNmQ1ODY5In0.zf1X_UFHJCmvJ2xGxWMCqLz0QQ7JAk621kWdN9wnpMo",
    )
    refresh_token: Optional[str] = Field(
        None,
        description="A token used to refresh the user's JSON web token, if the account at hand requires it.",
        example="tyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ7",
    )


class UpdateConnectionRepoAdapter(InstitutionConnectionBase):
    """Object send to Repo to update an institution connection"""

    is_active: Optional[bool] = Field(
        None,
        description="Whether or not the connection is currently active.",
        example=True,
    )


class RetrieveManyConnectionsRepoAdapter(BaseModel):
    user_id: Optional[int] = Field(
        None,
        description="The unique identifier of the Pelleum user who this account connection belongs to.",
        example=1,
    )
    institution_id: Optional[str] = Field(
        None,
        description="A foreign key unique identifier for a Pellem supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether or not the connection is currently active.",
        example=True,
    )
    has_refresh_token: Optional[bool] = Field(
        None,
        description="Whether or not the connection has a refresh token.",
        example=True,
    )


class CreateConnectionRepoAdapter(InstitutionConnectionBase):
    institution_id: str = Field(
        ...,
        description="A foreign key unique identifier for a Pellem supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )
    user_id: int = Field(
        ...,
        description="The unique identifier of the Pelleum user who this account connection belongs to.",
        example=1,
    )
    is_active: bool = Field(
        ...,
        description="Whether or not the connection is currently active.",
        example=True,
    )


class InstitutionConnection(CreateConnectionRepoAdapter):
    """Database Model"""

    connection_id: int = Field(
        ..., description="The unique identifier for an account connection.", example=1
    )
    is_active: bool = Field(
        ..., description="Whether or not the account is currently linked.", example=True
    )
    created_at: datetime
    updated_at: datetime


class ConnectionJoinInstitutionJoinPortfolio(InstitutionConnection):
    name: str = Field(
        ...,
        description="The name of a Pelleum supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )


class ConnectionInResponse(BaseModel):
    connection_id: int = Field(
        ..., description="The unique identifier for an account connection.", example=1
    )
    institution_id: str = Field(
        ...,
        description="A foreign key unique identifier for a Pellem supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )
    user_id: int = Field(
        ...,
        description="The unique identifier of the Pelleum user who this account connection belongs to.",
        example=1,
    )
    is_active: bool = Field(
        ...,
        description="Whether or not the connection is currently active.",
        example=True,
    )
    name: str = Field(
        ...,
        description="The name of a Pelleum supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )
    created_at: datetime
    updated_at: datetime


class IndividualHoldingData(BaseModel):
    asset_symbol: str
    quantity: float
    average_buy_price: Optional[float]
    asset_name: Optional[str]


class UserBrokerageHoldings(BaseModel):
    holdings: List[IndividualHoldingData]
    insitution_name: str


class Institution(BaseModel):
    """Database Model"""

    institution_id: str = Field(
        ...,
        description="A primary key unique identifier for a Pelleum supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )
    name: str = Field(
        ...,
        description="The name of a Pelleum supported financial institution.",
        example="Robinhood",
    )
    created_at: datetime
    updated_at: datetime


class RobinhoodInstrument(BaseModel):
    """Database Model"""

    instrument_id: str = Field(
        ...,
        description="A primary key unique identifier for a Robinhood instrument.",
        example="e39ed23a-7bd1-4587-b060-71988d9ef483",
    )
    name: str = Field(
        ...,
        description="The name of a Robinhood instrument.",
        example="Tesla",
    )
    symbol: str = Field(
        ...,
        description="The symbol of a Robinhood instrument.",
        example="TSLA",
    )
    created_at: datetime
    updated_at: datetime


############# Responses #############
class SupportedInstitutions(BaseModel):
    supported_institutions: List[Institution]


class SupportedInstitutionsResponse(BaseModel):
    records: SupportedInstitutions


class UserActiveConnections(BaseModel):
    active_connections: List[ConnectionInResponse]


class UserActiveConnectionsResponse(BaseModel):
    records: UserActiveConnections


class SuccessfulConnectionResponse(BaseModel):
    account_connection_status: str
    connected_at: datetime


class SuccessfulTokenRefreshResponse(BaseModel):
    encrypted_json_web_token: str
    encrypted_refresh_token: str


############# Exceptions #############


class InstitutionException(Exception):
    """Generic exception"""


class UnauthorizedException(InstitutionException):
    """Raised when a 401 unauthorized is returned"""


class InstitutionApiError(InstitutionException):
    """Errors raised by Institution API"""

    status: int
    detail: str
