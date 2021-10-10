from abc import ABC, abstractmethod
from typing import Union

from app.usecases.schemas import users


class IUserRepo(ABC):
    @abstractmethod
    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Union[users.UserInDB, None]:
        """Retrieves user from database"""
