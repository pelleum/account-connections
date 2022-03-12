from typing import Any, Mapping

import pytest
from databases import Database

from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios
from app.usecases.schemas.users import UserInDB
from tests.conftest import TEST_ASSET_NAME, TEST_ASSET_SYMBOL


@pytest.mark.asyncio
async def test_upsert_asset(
    portfolio_repo: IPortfolioRepo,
    inserted_institution: str,
    inserted_user_object: UserInDB,
    test_db: Database,
):

    # 1. Create new asset
    await portfolio_repo.upsert_asset(
        new_asset=portfolios.UpsertAssetRepoAdapter(
            user_id=inserted_user_object.user_id,
            institution_id=inserted_institution,
            name=TEST_ASSET_NAME,
            asset_symbol=TEST_ASSET_SYMBOL,
            quantity=23.485,
        )
    )
    expected_fields = [field for field in portfolios.AssetInDB.__fields__]
    # 2. Create assertions
    test_asset = await test_db.fetch_one(
        "SELECT * FROM assets WHERE user_id = :user_id AND asset_symbol = :asset_symbol AND institution_id = :institution_id",
        {
            "user_id": inserted_user_object.user_id,
            "asset_symbol": TEST_ASSET_SYMBOL,
            "institution_id": inserted_institution,
        },
    )

    assert test_asset["asset_symbol"] == TEST_ASSET_SYMBOL
    assert test_asset["institution_id"] == inserted_institution
    assert test_asset["user_id"] == inserted_user_object.user_id
    assert test_asset["quantity"] == 23.485
    for key in expected_fields:
        assert key in expected_fields

    # 3. Update asset (quantity updated)
    await portfolio_repo.upsert_asset(
        new_asset=portfolios.UpsertAssetRepoAdapter(
            user_id=inserted_user_object.user_id,
            institution_id=inserted_institution,
            name="Bitcoin",
            asset_symbol=TEST_ASSET_SYMBOL,
            quantity=100.023,
        )
    )

    test_asset = await test_db.fetch_one(
        "SELECT * FROM assets WHERE user_id = :user_id AND asset_symbol = :asset_symbol AND institution_id = :institution_id",
        {
            "user_id": inserted_user_object.user_id,
            "asset_symbol": TEST_ASSET_SYMBOL,
            "institution_id": inserted_institution,
        },
    )
    # 4. Update assertions
    assert test_asset["asset_symbol"] == TEST_ASSET_SYMBOL
    assert test_asset["institution_id"] == inserted_institution
    assert test_asset["user_id"] == inserted_user_object.user_id
    assert test_asset["quantity"] == 100.023
    for key in expected_fields:
        assert key in expected_fields


@pytest.mark.asyncio
async def test_update_asset(
    portfolio_repo: IPortfolioRepo, inserted_asset: Mapping[str, str], test_db: Database
) -> None:

    # 1. Update the asset
    await portfolio_repo.update_asset(
        user_id=inserted_asset["user_id"],
        asset_symbol=inserted_asset["asset_symbol"],
        institution_id=inserted_asset["institution_id"],
        updated_asset=portfolios.UpdateAssetRepoAdapter(quantity=123.45),
    )

    expected_fields = [field for field in portfolios.AssetInDB.__fields__]
    test_asset = await test_db.fetch_one(
        "SELECT * FROM assets WHERE user_id = :user_id AND asset_symbol = :asset_symbol AND institution_id = :institution_id",
        {
            "user_id": inserted_asset["user_id"],
            "asset_symbol": inserted_asset["asset_symbol"],
            "institution_id": inserted_asset["institution_id"],
        },
    )
    # 2. Assertions
    assert test_asset["asset_symbol"] == inserted_asset["asset_symbol"]
    assert test_asset["institution_id"] == inserted_asset["institution_id"]
    assert test_asset["user_id"] == inserted_asset["user_id"]
    assert test_asset["quantity"] == 123.45
    for key in expected_fields:
        assert key in expected_fields


@pytest.mark.asyncio
async def test_retrieve_brokerage_assets(
    portfolio_repo: IPortfolioRepo, many_inserted_assets: Mapping[str, Any]
) -> None:

    inserted_asset_names = [
        asset["name"] for asset in many_inserted_assets["inserted_assets"]
    ]
    inserted_asset_symbols = [
        asset["asset_symbol"] for asset in many_inserted_assets["inserted_assets"]
    ]

    brokerage_assets = await portfolio_repo.retrieve_brokerage_assets(
        user_id=many_inserted_assets["user_id"],
        institution_id=many_inserted_assets["institution_id"],
    )

    assert len(brokerage_assets) == len(many_inserted_assets["inserted_assets"])
    for asset in brokerage_assets:
        assert isinstance(asset, portfolios.AssetInDB)
        assert asset.name in inserted_asset_names
        assert asset.asset_symbol in inserted_asset_symbols


@pytest.mark.asyncio
async def test_delete(
    portfolio_repo: IPortfolioRepo, inserted_asset: Mapping[str, str], test_db: Database
) -> None:

    # 1. Retrieve asset to delete
    test_asset = await test_db.fetch_one(
        "SELECT * FROM assets WHERE user_id = :user_id AND asset_symbol = :asset_symbol AND institution_id = :institution_id",
        {
            "user_id": inserted_asset["user_id"],
            "asset_symbol": inserted_asset["asset_symbol"],
            "institution_id": inserted_asset["institution_id"],
        },
    )

    # 2. Delete asset by asset_id
    await portfolio_repo.delete(asset_id=test_asset["asset_id"])

    # 3. Ensure it no longer exists in the database
    deleted_asset = await test_db.fetch_one(
        "SELECT * FROM assets WHERE user_id = :user_id AND asset_symbol = :asset_symbol AND institution_id = :institution_id",
        {
            "user_id": inserted_asset["user_id"],
            "asset_symbol": inserted_asset["asset_symbol"],
            "institution_id": inserted_asset["institution_id"],
        },
    )

    assert not deleted_asset
