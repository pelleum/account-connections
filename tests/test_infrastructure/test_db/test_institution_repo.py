import uuid
from typing import List

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.schemas import institutions
from app.usecases.schemas.users import UserInDB
from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS


@pytest_asyncio.fixture
async def inserted_robinhood_instrument(institution_repo: IInstitutionRepo) -> str:

    instrument_id = str(uuid.uuid4())
    await institution_repo.create_robinhood_instrument(
        instrument_id=instrument_id, name="Tesla", symbol="TSLA"
    )
    return instrument_id


@pytest.mark.asyncio
async def test_upsert(
    institution_repo: IInstitutionRepo,
    inserted_institution: str,
    inserted_user_object: UserInDB,
):

    # 1. Create new connection
    test_institution_connection = await institution_repo.upsert(
        connection_data=institutions.CreateConnectionRepoAdapter(
            institution_id=inserted_institution,
            user_id=inserted_user_object.user_id,
            is_active=True,
        )
    )

    # 2. Create assertions
    assert isinstance(test_institution_connection, institutions.InstitutionConnection)
    assert test_institution_connection.connection_id
    assert test_institution_connection.user_id == inserted_user_object.user_id
    assert test_institution_connection.is_active == True

    # 3. Update connection
    test_institution_connection = await institution_repo.upsert(
        connection_data=institutions.CreateConnectionRepoAdapter(
            institution_id=inserted_institution,
            user_id=inserted_user_object.user_id,
            is_active=True,
            json_web_token="some-token",
            refresh_token="some-other-token",
        )
    )

    # 4. Update assertions
    assert isinstance(test_institution_connection, institutions.InstitutionConnection)
    assert test_institution_connection.connection_id
    assert test_institution_connection.user_id == inserted_user_object.user_id
    assert test_institution_connection.is_active == True
    assert test_institution_connection.json_web_token == "some-token"
    assert test_institution_connection.refresh_token == "some-other-token"


@pytest.mark.asyncio
async def test_retrieve_institution(
    institution_repo: IInstitutionRepo, inserted_institution: str
) -> None:

    test_institution = await institution_repo.retrieve_institution(
        institution_id=inserted_institution
    )

    assert isinstance(test_institution, institutions.Institution)
    assert test_institution.institution_id == inserted_institution
    assert test_institution.name


@pytest.mark.asyncio
async def test_retrieve_all_institutions(
    institution_repo: IInstitutionRepo, inserted_institution: str
) -> None:

    all_test_institutions = await institution_repo.retrieve_all_institutions()

    assert len(all_test_institutions) > 0
    for institution in all_test_institutions:
        assert isinstance(institution, institutions.Institution)


@pytest.mark.asyncio
async def test_retrieve_institution_connection(
    institution_repo: IInstitutionRepo,
    inserted_institution_connection: institutions.InstitutionConnection,
) -> None:

    test_connection = await institution_repo.retrieve_institution_connection(
        connection_id=inserted_institution_connection.connection_id
    )

    assert isinstance(test_connection, institutions.InstitutionConnection)
    assert (
        test_connection.connection_id == inserted_institution_connection.connection_id
    )
    assert test_connection.user_id == inserted_institution_connection.user_id
    assert test_connection.is_active == inserted_institution_connection.is_active


@pytest.mark.asyncio
async def test_update_institution_connection(
    institution_repo: IInstitutionRepo,
    inserted_institution_connection: institutions.InstitutionConnection,
) -> None:

    updated_test_connection = await institution_repo.update_institution_connection(
        connection_id=inserted_institution_connection.connection_id,
        updated_connection=institutions.UpdateConnectionRepoAdapter(
            json_web_token="some-updated-token",
            refresh_token="some-other-updated-token",
        ),
    )

    assert isinstance(updated_test_connection, institutions.InstitutionConnection)
    assert (
        updated_test_connection.connection_id
        == inserted_institution_connection.connection_id
    )
    assert updated_test_connection.user_id == inserted_institution_connection.user_id
    assert updated_test_connection.json_web_token == "some-updated-token"
    assert updated_test_connection.refresh_token == "some-other-updated-token"


@pytest.mark.asyncio
async def test_retrieve_many_institution_connections(
    institution_repo: IInstitutionRepo,
    many_institution_connections: List[institutions.InstitutionConnection],
) -> None:

    test_connections = await institution_repo.retrieve_many_institution_connections(
        query_params=institutions.RetrieveManyConnectionsRepoAdapter(is_active=True)
    )

    assert len(test_connections) >= DEFAULT_NUMBER_OF_INSERTED_OBJECTS
    for connection in test_connections:
        assert isinstance(connection, institutions.InstitutionConnection)


@pytest.mark.asyncio
async def test_create_robinhood_instrument(
    institution_repo: IInstitutionRepo, test_db: Database
) -> None:

    instrument_id = str(uuid.uuid4())
    await institution_repo.create_robinhood_instrument(
        instrument_id=instrument_id, name="Tesla", symbol="TSLA"
    )

    inserted_instrument = await test_db.fetch_one(
        "SELECT * FROM account_connections.robinhood_instruments WHERE symbol = 'TSLA'"
    )

    assert inserted_instrument["instrument_id"] == instrument_id
    assert inserted_instrument["name"] == "Tesla"
    assert inserted_instrument["symbol"] == "TSLA"


@pytest.mark.asyncio
async def test_retrieve_robinhood_instruments(
    institution_repo: IInstitutionRepo, inserted_robinhood_instrument: str
) -> None:

    retrieved_instruments = await institution_repo.retrieve_robinhood_instruments(
        instrument_ids=[inserted_robinhood_instrument]
    )

    assert len(retrieved_instruments) > 0
    for instrument in retrieved_instruments:
        assert isinstance(instrument, institutions.RobinhoodInstrument)


@pytest.mark.asyncio
async def test_delete(
    institution_repo: IInstitutionRepo,
    test_db: Database,
    inserted_institution_connection: institutions.InstitutionConnection,
) -> None:
    # 1. Delete connection by connection_id
    await institution_repo.delete(
        connection_id=inserted_institution_connection.connection_id
    )

    # 2. Ensure it no longer exists in the database
    connection = await test_db.fetch_one(
        "SELECT * FROM account_connections.institution_connections WHERE connection_id = :connection_id",
        {"connection_id": inserted_institution_connection.connection_id},
    )

    assert not connection
