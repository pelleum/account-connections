from abc import ABC, abstractmethod
from typing import Mapping

from app.usecases.schemas import institutions


class IInstitutionService(ABC):
    @abstractmethod
    async def login(self, credentials: institutions.UserCredentials) -> Mapping:
        """Login to institution"""

    @abstractmethod
    async def send_multifactor_auth_code(
        self,
        credentials: institutions.UserCredentialsWithMFA,
        user_id: int,
        institution_id: str,
    ) -> institutions.UserHoldings:
        """Sends multi-factor auth code to instution and returns holdings"""

    @abstractmethod
    async def get_recent_holdings(
        self, encrypted_json_web_token: str
    ) -> institutions.UserHoldings:
        """Returns most recent holdings directly from institution"""
