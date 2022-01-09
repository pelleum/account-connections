from databases import Database

from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.institution_repo import InstitutionRepo
from app.infrastructure.db.repos.portfolio_repo import PortfolioRepo
from app.infrastructure.db.repos.user_repo import UsersRepo


async def get_users_repo():
    database: Database = await get_or_create_database()
    return UsersRepo(db=database)


async def get_institution_repo():
    database: Database = await get_or_create_database()
    return InstitutionRepo(db=database)


async def get_portfolio_repo():
    database: Database = await get_or_create_database()
    return PortfolioRepo(db=database)
