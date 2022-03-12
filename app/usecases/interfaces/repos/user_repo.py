from abc import ABC, abstractmethod
from typing import Union

from passlib.context import CryptContext

from app.usecases.schemas import users


class IUsersRepo(ABC):
    @abstractmethod
    async def create(
        self, new_user: users.UserCreate, password_context: CryptContext
    ) -> users.UserInDB:
        """Creates user"""

    @abstractmethod
    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Union[users.UserInDB, None]:
        """Retrieves user from database"""
