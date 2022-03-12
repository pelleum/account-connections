from typing import Optional

from databases import Database
from passlib.context import CryptContext
from sqlalchemy import and_

from app.infrastructure.db.models.public.users import USERS
from app.usecases.interfaces.repos.user_repo import IUsersRepo
from app.usecases.schemas import users


class UsersRepo(IUsersRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, new_user: users.UserCreate, password_context: CryptContext
    ) -> users.UserInDB:
        """Creates user -- only used for unit tests"""

        hashed_password = password_context.hash(new_user.password)

        create_user_insert_stmt = USERS.insert().values(
            email=new_user.email,
            username=new_user.username,
            hashed_password=hashed_password,
            gender=new_user.gender,
            birthdate=new_user.birthdate,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )

        await self.db.execute(create_user_insert_stmt)

        return await self.retrieve_user_with_filter(username=new_user.username)

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
