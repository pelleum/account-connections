from abc import ABC, abstractmethod
from typing import Mapping, Any

from app.usecases.schemas import institutions


class IInstitutionService(ABC):
    @abstractmethod
    async def login(
        self,
        credentials: institutions.UserCredentials,
        user_id: int,
        institution_id: str,
    ) -> Mapping[str, Any]:
        """Login to Institution"""

    @abstractmethod
    async def send_multifactor_auth_code(
        self,
        verification_proof: institutions.UserVerificationCredentials,
        user_id: int,
        institution_id: str,
    ) -> institutions.UserBrokerageHoldings:
        """Sends multi-factor auth code to institution and returns holdings"""

    @abstractmethod
    async def get_recent_holdings(
        self, encrypted_json_web_token: str
    ) -> institutions.UserBrokerageHoldings:
        """Returns most recent holdings directly from institution"""
