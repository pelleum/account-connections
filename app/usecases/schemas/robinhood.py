from typing import Optional, List

from pydantic import BaseModel, Field


class InitialLoginPayload(BaseModel):
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


class LoginPayloadWithMFA(InitialLoginPayload):
    """Payload with MFA sent to Robinhood to login"""

    mfa_code: str


class RobhinhoodIndividualHoldingData(BaseModel):
    asset_symbol: str
    quantity: float
    average_by_price: float
    asset_name: str


class RobinhoodUserHoldings(BaseModel):
    holdings: List[RobhinhoodIndividualHoldingData]


############# Responses #############
class SuccessfulLoginResponse(BaseModel):
    """Successful Robinhood login response with token"""

    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    mfa_code: str
    backup_code: Optional[str]


class PositionData(BaseModel):
    """Position Data that gives us the instrument url and the average buy price of the asset"""

    instrument: str = Field(
        ...,
        description="The Robinhood URL for this specific instrument.",
        example="https://api.robinhood.com/instruments/e39ed23a-7bd1-4587-b060-71988d9ef483/",
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


class PositionDataResponse(BaseModel):
    """Position Data Response"""

    results: List[PositionData]


class InstrumentByURLResponse(BaseModel):
    """Instrument data (used to get ticker symbol)"""

    symbol: str = Field(
        ..., description="An individual asset's ticker symbol.", example="TSLA"
    )


class NameData(BaseModel):
    """The data that we're concerned with in a get name by symbol response"""

    name: Optional[str] = Field(
        None, description="An individual asset's name.", example="Tesla"
    )
    simple_name: Optional[str] = Field(
        None, description="An individual asset's name.", example="Tesla"
    )


class NameDataResponse(BaseModel):
    """Get name by symbol response"""

    results: List[NameData]
