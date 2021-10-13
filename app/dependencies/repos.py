from app.infrastructure.db.repos.user_repo import UsersRepo
from app.infrastructure.db.core import get_or_create_database


async def get_users_repo():
    database = await get_or_create_database()
    return UsersRepo(db=database)
