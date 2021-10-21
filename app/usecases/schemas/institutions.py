from typing import Optional, List
from datetime import datetime

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


class MultiFactorAuthCodeRequest(LoginRequest):
    mfa_code: constr(max_length=10) = Field(
        None,
        description="The multifactor (sms) authentication code sent to the user's phone.",
        example="149837",
    )


class UserCredentials(LoginRequest):
    """Same as LoginRequest"""


class UserCredentialsWithMFA(MultiFactorAuthCodeRequest):
    """Same as MultiFactorAuthCodeRequest"""


class UpdateConnectionRepoAdapter(BaseModel):
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
    is_active: Optional[bool] = Field(
        None,
        description="Whether or not the connection is currently active.",
        example=True,
    )


class CreateConnectionRepoAdapter(UpdateConnectionRepoAdapter):
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


class InstitutionConnectionJoinInstitution(InstitutionConnection):
    name: str = Field(
        ...,
        description="The name of a Pelleum supported financial institution.",
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )


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
        example="098736bd-fd4a-4414-bb27-bc4c87f74e0c",
    )
    created_at: datetime
    updated_at: datetime


############# Responses #############
class SupportedInstitutions(BaseModel):
    supported_institutions: List[Institution]


class SupportedInstitutionsResponse(BaseModel):
    records: SupportedInstitutions


class SuccessfulConnectionResponse(BaseModel):
    account_connection_status: str
    connected_at: datetime
