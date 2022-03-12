import os
from typing import Any, List, Mapping

import asyncpg
import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext

from app.dependencies import (
    get_current_active_user,
    get_institution_repo,
    get_institution_service,
    get_portfolio_repo,
    get_users_repo,
)

# Repos
from app.infrastructure.db.repos.institution_repo import InstitutionRepo
from app.infrastructure.db.repos.portfolio_repo import PortfolioRepo
from app.infrastructure.db.repos.user_repo import UsersRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.repos.user_repo import IUsersRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService

# Other
from app.usecases.schemas import institutions, portfolios, users
from app.usecases.services.encryption import EncryptionService

# Services
from app.usecases.services.robinhood import RobinhoodService
from tests.mocks import test_robinhood_client

DEFAULT_NUMBER_OF_INSERTED_OBJECTS = 3
NON_HASHED_USER_PASSWORD = "AFGADaHAF$HADFHA1R"
TEST_USERNAME = "inserted_name"
TEST_INSITUTION_ID = "331e8f42-574c-4df6-b2c2-20b348e4ad8a"
TEST_ASSET_NAME = "Bitcoin"
TEST_ASSET_SYMBOL = "BTC"
MULTIPLE_TEST_ASSETS = (
    {"name": "Tesla", "asset_symbol": "TSLA"},
    {"name": "Bitcoin", "asset_symbol": "BTC"},
)

# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    return "postgres://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5444"),
        database_name=os.getenv("POSTGRES_DB", "pelleum-dev-test"),
    )


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE public.assets CASCADE")
    await test_db.execute("TRUNCATE public.users CASCADE")
    await test_db.execute("TRUNCATE account_connections.institutions CASCADE")
    await test_db.execute(
        "TRUNCATE account_connections.institution_connections CASCADE"
    )
    await test_db.execute("TRUNCATE account_connections.robinhood_instruments CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def portfolio_repo(test_db: Database) -> IPortfolioRepo:
    return PortfolioRepo(db=test_db)


@pytest_asyncio.fixture
async def user_repo(test_db: Database) -> IUsersRepo:
    return UsersRepo(db=test_db)


@pytest_asyncio.fixture
async def institution_repo(test_db: Database) -> IInstitutionRepo:
    return InstitutionRepo(db=test_db)


# Services
@pytest_asyncio.fixture
async def robinhood_service(
    test_db: Database,
    institution_repo: IInstitutionRepo,
    portfolio_repo: IPortfolioRepo,
) -> IInstitutionService:
    """RobinhoodService with a Mocked Robinhood client"""
    return RobinhoodService(
        robinhood_client=test_robinhood_client.MockRobinhoodClient(),
        institution_repo=institution_repo,
        portfolio_repo=portfolio_repo,
        encryption_service=EncryptionService(),
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_user_object(
    user_repo: IUsersRepo,
) -> users.UserInDB:
    """Inserts a user object into the database for other tests."""

    return await user_repo.create(
        new_user=users.UserCreate(
            email="inserted@test.com",
            username=TEST_USERNAME,
            password=NON_HASHED_USER_PASSWORD,
            gender="FEMALE",
            birthdate="2002-11-27T06:00:00.000Z",
        ),
        password_context=CryptContext(schemes=["bcrypt"], deprecated="auto"),
    )


@pytest_asyncio.fixture
async def many_inserted_users(
    user_repo: IUsersRepo,
) -> List[users.UserInDB]:
    """Inserts a user object into the database for other tests."""

    inserted_users = []
    for i, _ in enumerate(range(DEFAULT_NUMBER_OF_INSERTED_OBJECTS)):
        inserted_users.append(
            await user_repo.create(
                new_user=users.UserCreate(
                    email=f"inserted{i}@test.com",
                    username=f"{TEST_USERNAME}{i}",
                    password=NON_HASHED_USER_PASSWORD,
                    gender="FEMALE" if i % 2 == 0 else "MALE",
                    birthdate="2002-11-27T06:00:00.000Z",
                ),
                password_context=CryptContext(schemes=["bcrypt"], deprecated="auto"),
            )
        )
    return inserted_users


@pytest_asyncio.fixture
async def inserted_institution(test_db: Database) -> str:
    """Inserts a Pelleum-supported institution into the database"""
    try:
        await test_db.execute(
            "INSERT INTO account_connections.institutions (institution_id, name) "
            "VALUES (:test_institution_id, 'Robinhood');",
            {"test_institution_id": TEST_INSITUTION_ID},
        )
    except asyncpg.exceptions.UniqueViolationError:
        pass

    return TEST_INSITUTION_ID


@pytest_asyncio.fixture
async def inserted_asset(
    portfolio_repo: IPortfolioRepo,
    inserted_institution: str,
    inserted_user_object: users.UserInDB,
) -> Mapping[str, str]:
    """Inserts an asset for other tests to utilize."""

    await portfolio_repo.upsert_asset(
        new_asset=portfolios.UpsertAssetRepoAdapter(
            user_id=inserted_user_object.user_id,
            institution_id=inserted_institution,
            name=TEST_ASSET_NAME,
            asset_symbol=TEST_ASSET_SYMBOL,
            quantity=23.485,
        )
    )

    return {
        "user_id": inserted_user_object.user_id,
        "asset_symbol": TEST_ASSET_SYMBOL,
        "institution_id": inserted_institution,
    }


@pytest_asyncio.fixture
async def many_inserted_assets(
    portfolio_repo: IPortfolioRepo,
    inserted_institution: str,
    inserted_user_object: users.UserInDB,
) -> Mapping[str, Any]:
    """Inserts an asset for other tests to utilize."""

    for asset in MULTIPLE_TEST_ASSETS:
        await portfolio_repo.upsert_asset(
            new_asset=portfolios.UpsertAssetRepoAdapter(
                user_id=inserted_user_object.user_id,
                institution_id=inserted_institution,
                name=asset["name"],
                asset_symbol=asset["asset_symbol"],
                quantity=23.485,
            )
        )

    return {
        "user_id": inserted_user_object.user_id,
        "inserted_assets": MULTIPLE_TEST_ASSETS,
        "institution_id": inserted_institution,
    }


@pytest_asyncio.fixture
async def inserted_institution_connection(
    institution_repo: IInstitutionRepo,
    inserted_institution: str,
    many_inserted_assets: Mapping[str, Any],
) -> institutions.InstitutionConnection:
    """Inserts a user's institution connection for other tests to utilize."""

    return await institution_repo.upsert(
        connection_data=institutions.CreateConnectionRepoAdapter(
            institution_id=inserted_institution,
            user_id=many_inserted_assets["user_id"],
            is_active=True,
        )
    )


@pytest_asyncio.fixture
async def many_institution_connections(
    institution_repo: IInstitutionRepo,
    inserted_institution: str,
    many_inserted_users: List[users.UserInDB],
) -> List[institutions.InstitutionConnection]:

    institution_connecitons = []
    for user in many_inserted_users:
        institution_connecitons.append(
            await institution_repo.upsert(
                connection_data=institutions.CreateConnectionRepoAdapter(
                    institution_id=inserted_institution,
                    user_id=user.user_id,
                    is_active=True,
                )
            )
        )

    return institution_connecitons


@pytest_asyncio.fixture
def test_app(
    inserted_user_object: users.UserInDB,
    user_repo: IUsersRepo,
    portfolio_repo: IPortfolioRepo,
    institution_repo: IInstitutionRepo,
    robinhood_service: IInstitutionService,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_current_active_user] = lambda: inserted_user_object
    app.dependency_overrides[get_users_repo] = lambda: user_repo
    app.dependency_overrides[get_institution_repo] = lambda: institution_repo
    app.dependency_overrides[get_portfolio_repo] = lambda: portfolio_repo
    app.dependency_overrides[get_institution_service] = lambda: robinhood_service
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
