from typing import Optional

from databases import Database
from sqlalchemy import and_

from app.infrastructure.db.models.users import USERS
from app.usecases.interfaces.user_repo import IUserRepo
from app.usecases.schemas import users


class UsersRepo(IUserRepo):
    def __init__(self, db: Database):
        self.db = db

    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Optional[users.UserInDB]:
        """Retrieves user from database"""

        conditions = []

        if user_id:
            conditions.append(USERS.c.user_id == user_id)

        if email:
            conditions.append(USERS.c.email == email)

        if username:
            conditions.append(USERS.c.username == username)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a parameter to query by to the function, retrieve_user_with_filter()"
            )

        query = USERS.select().where(and_(*conditions))

        result = await self.db.fetch_one(query)
        return users.UserInDB(**result) if result else None
