import uuid
from typing import Any, Mapping

import pytest
import pytest_asyncio
from databases import Database
from httpx import AsyncClient

from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.schemas import institutions


@pytest_asyncio.fixture
async def create_post_request_json() -> Mapping[str, str]:
    return {
        "content": "This is a test post.",
        "asset_symbol": "AAPL",
        "sentiment": "Bear",
    }


@pytest_asyncio.fixture
async def inserted_inactive_institution_connection(
    institution_repo: IInstitutionRepo,
    inserted_institution: str,
    many_inserted_assets: Mapping[str, Any],
) -> institutions.InstitutionConnection:
    """Inserts a user's institution connection for other tests to utilize."""

    return await institution_repo.upsert(
        connection_data=institutions.CreateConnectionRepoAdapter(
            institution_id=inserted_institution,
            user_id=many_inserted_assets["user_id"],
            is_active=False,
            username="/l3GqvFNIYK6I5fxKzG+bQ==q77txElAyvEtPDCN0Hs85A==",
            password="/l3GqvFNIYK6I5fxKzG+bQ==q77txElAyvEtPDCN0Hs85A==",
        )
    )


@pytest.mark.asyncio
async def test_get_all_supported_institutions(
    test_client: AsyncClient, inserted_institution: str
) -> None:

    endpoint = "/private/institutions"

    response = await test_client.get(endpoint)
    response_data = response.json()
    expected_response_fields = [
        field for field in institutions.SupportedInstitutionsResponse.__fields__
    ]

    # Assertions
    assert response.status_code == 200
    for key in response_data.keys():
        assert key in expected_response_fields


@pytest.mark.asyncio
async def test_retrieve_active_institution_connections(
    test_client: AsyncClient,
    inserted_institution_connection: institutions.InstitutionConnection,
) -> None:

    endpoint = f"/private/institutions/connections"

    # Test successful user creation
    response = await test_client.get(endpoint)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    for key, value in response_data["records"]["active_connections"][0].items():
        if key != "created_at" and key != "updated_at" and key != "name":
            assert value == inserted_institution_connection.dict().get(key)


@pytest.mark.asyncio
async def test_delete_institution_connection(
    test_client: AsyncClient,
    inserted_institution_connection: institutions.InstitutionConnection,
    test_db: Database,
) -> None:

    endpoint = f"/private/institutions/{inserted_institution_connection.institution_id}"

    # 1. Hit the endpoint
    response = await test_client.delete(endpoint)

    # 2. Ensure data was deleted from the database
    test_connection = await test_db.fetch_one(
        "SELECT * FROM account_connections.institution_connections WHERE connection_id=:connection_id",
        {
            "connection_id": inserted_institution_connection.connection_id,
        },
    )

    test_assets = await test_db.fetch_one(
        "SELECT * FROM public.assets WHERE user_id=:user_id AND institution_id=:institution_id",
        {
            "user_id": inserted_institution_connection.user_id,
            "institution_id": inserted_institution_connection.institution_id,
        },
    )

    # Response Assertions
    assert response.status_code == 200

    # Database Assertions
    assert not test_connection
    assert not test_assets

    # Test the case where an invalid institution_id is supplied
    invalid_endpoint = f"/private/institutions/institution-id-that-does-not-exist"
    response = await test_client.delete(invalid_endpoint)
    # Assertions
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_login_to_institution(
    test_client: AsyncClient, inserted_institution: str
) -> None:

    endpoint = f"/private/institutions/login/{inserted_institution}"

    json = {"username": "my-user-name", "password": "my-password"}

    response = await test_client.post(endpoint, json=json)
    response_data = response.json()
    expected_response_fields = [
        field for field in institutions.SuccessfulConnectionResponse.__fields__
    ]

    # Assertions
    assert response.status_code == 200
    for key in response_data.keys():
        assert key in expected_response_fields


@pytest.mark.asyncio
async def test_verify_login_with_code(
    test_client: AsyncClient,
    inserted_inactive_institution_connection: institutions.InstitutionConnection,
) -> None:

    endpoint = f"/private/institutions/login/{inserted_inactive_institution_connection.institution_id}/verify"

    json = {"without_challenge": {"sms_code": "471690"}}

    response = await test_client.post(endpoint, json=json)
    response_data = response.json()
    expected_response_fields = [
        field for field in institutions.SuccessfulConnectionResponse.__fields__
    ]

    # Assertions
    assert response.status_code == 201
    for key in response_data.keys():
        assert key in expected_response_fields

    # Test the case where an invalid institution_id is supplied
    invalid_endpoint = (
        f"/private/institutions/login/institution-id-that-does-not-exist/verify"
    )
    response = await test_client.post(invalid_endpoint, json=json)
    # Assertions
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_verify_login_with_code_duplicate(
    test_client: AsyncClient,
    inserted_institution_connection: institutions.InstitutionConnection,
) -> None:
    """Test case where user already has an active connection"""

    endpoint = f"/private/institutions/login/{inserted_institution_connection.institution_id}/verify"

    json = {"without_challenge": {"sms_code": "471690"}}

    response = await test_client.post(endpoint, json=json)

    # Assertions
    assert response.status_code == 409
