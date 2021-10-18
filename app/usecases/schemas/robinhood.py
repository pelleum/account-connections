from typing import Optional

from pydantic import BaseModel


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


############# Responses #############
class SuccessfulLoginResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    mfa_code: str
    backup_code: Optional[str]
