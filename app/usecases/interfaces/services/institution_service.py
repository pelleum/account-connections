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
        user_id: str,
        institution_id: str,
    ) -> None:
        """Sends multifactore authentication code to institution"""

    @abstractmethod
    async def encrypt(self, secret: str) -> str:
        """Returns encrypted secret"""
