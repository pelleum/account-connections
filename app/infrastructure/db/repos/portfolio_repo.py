from typing import List, Optional

from databases import Database
from sqlalchemy import and_, delete, insert
from sqlalchemy.dialects.postgresql import insert

from app.infrastructure.db.models.public.portfolio import ASSETS
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios


class PortfolioRepo(IPortfolioRepo):
    def __init__(self, db: Database):
        self.db = db

    async def upsert_asset(self, new_asset: portfolios.UpsertAssetRepoAdapter) -> None:
        """Creates or updates new asset"""

        asset_insert_statement = insert(ASSETS).values(
            user_id=new_asset.user_id,
            institution_id=new_asset.institution_id,
            thesis_id=new_asset.thesis_id,
            asset_symbol=new_asset.asset_symbol,
            name=new_asset.name,
            position_value=new_asset.position_value,
            quantity=new_asset.quantity,
            skin_rating=new_asset.skin_rating,
            average_buy_price=new_asset.average_buy_price,
            total_contribution=new_asset.total_contribution,
            is_up_to_date=True,
        )

        upsert_stmt = asset_insert_statement.on_conflict_do_update(
            index_elements=[
                ASSETS.c.user_id,
                ASSETS.c.asset_symbol,
                ASSETS.c.institution_id,
            ],
            set_=dict(
                position_value=new_asset.position_value,
                quantity=new_asset.quantity,
                average_buy_price=new_asset.average_buy_price,
                total_contribution=new_asset.total_contribution,
            ),
        )

        await self.db.execute(upsert_stmt)

    async def update_asset(
        self,
        user_id: int,
        asset_symbol: str,
        institution_id: int,
        updated_asset: portfolios.UpdateAssetRepoAdapter,
    ) -> None:
        """
        Update an individual asset holding by the composite index, (user_id,
        asset_symbol, and institution_id)
        """

        conditions = [
            ASSETS.c.user_id == user_id,
            ASSETS.c.asset_symbol == asset_symbol,
            ASSETS.c.institution_id == institution_id,
        ]

        query = ASSETS.update()

        updated_asset_raw = updated_asset.dict()
        update_asset_dict = {}

        for key, value in updated_asset_raw.items():
            if value is not None:
                update_asset_dict[key] = value

        query = query.values(update_asset_dict)

        asset_update_statemnent = query.where(and_(*conditions))

        await self.db.execute(asset_update_statemnent)

    async def retrieve_asset(
        self,
        asset_id: int = None,
        user_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""
        # TODO: Might not need this function... It's here just in case

        conditions = []

        if asset_id:
            conditions.append(ASSETS.c.asset_id == asset_id)

        if user_id:
            conditions.append(ASSETS.c.user_id == user_id)

        if asset_symbol:
            conditions.append(ASSETS.c.asset_symbol == asset_symbol)

        if institution_id:
            conditions.append(ASSETS.c.institution_id == institution_id)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_asset()"
            )

        query = ASSETS.select().where(and_(*conditions))
        result = await self.db.fetch_one(query)
        return portfolios.AssetInDB(**result) if result else None

    async def retrieve_brokerage_assets(
        self,
        user_id: int,
        institution_id: str,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by user_id"""

        conditions = []

        if user_id:
            conditions.append(ASSETS.c.user_id == user_id)

        if institution_id:
            conditions.append(ASSETS.c.institution_id == institution_id)

        query = ASSETS.select().where(and_(*conditions))
        results = await self.db.fetch_all(query)
        return [portfolios.AssetInDB(**result) for result in results]

    async def delete(
        self,
        asset_id: Optional[int] = None,
        users_institution: Optional[portfolios.UsersInstitutionRepoAdapter] = None,
    ) -> None:
        """Delete asset(s)"""

        conditions = []

        if asset_id:
            conditions.append(ASSETS.c.asset_id == asset_id)

        if users_institution:
            conditions.extend(
                [
                    ASSETS.c.user_id == users_institution.user_id,
                    ASSETS.c.institution_id == users_institution.institution_id,
                ]
            )

        delete_statement = delete(ASSETS).where(and_(*conditions))

        await self.db.execute(delete_statement)
