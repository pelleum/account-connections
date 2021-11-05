from typing import List, Optional
from sqlalchemy import desc, and_, delete

from databases import Database

from app.infrastructure.db.models.portfolio import PORTFOLIOS, ASSETS
from app.usecases.schemas import portfolios
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo


class PortfolioRepo(IPortfolioRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create_portfolio(self, user_id: int, aggregated_value: float) -> None:
        """Creates new portfolio"""

        portfolio_insert_statement = PORTFOLIOS.insert().values(
            user_id=user_id, aggregated_value=aggregated_value
        )

        await self.db.execute(portfolio_insert_statement)

    async def retrieve_portfolio(
        self, user_id: str
    ) -> Optional[portfolios.PortfolioInDB]:
        """Retrieve portfolio by user_id"""

        query = PORTFOLIOS.select().where(PORTFOLIOS.c.user_id == user_id)

        result = await self.db.fetch_one(query)
        if result:
            return portfolios.PortfolioInDB(**result)

    async def retrieve_all_portfolios(self) -> List[portfolios.PortfolioInDB]:
        """Retrieve all Pelleum portfolios"""

        query = PORTFOLIOS.select().order_by(desc(PORTFOLIOS.c.created_at))

        query_results = await self.db.fetch_all(query)
        return [portfolios.PortfolioInDB(**result) for result in query_results]

    async def create_asset(self, new_asset: portfolios.CreateAssetRepoAdapter) -> None:
        """Creates new asset"""

        asset_insert_statement = ASSETS.insert().values(
            portfolio_id=new_asset.portfolio_id,
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

        await self.db.execute(asset_insert_statement)

    async def update_asset(
        self,
        portfolio_id: int,
        asset_symbol: str,
        institution_id: int,
        updated_asset: portfolios.UpdateAssetRepoAdapter,
    ) -> None:
        """
        Update an individual asset holding by the composite index, (portfolio_id,
        asset_symbol, and institution_id)
        """

        conditions = []

        if portfolio_id:
            conditions.append(ASSETS.c.portfolio_id == portfolio_id)

        if asset_symbol:
            conditions.append(ASSETS.c.asset_symbol == asset_symbol)

        if institution_id:
            conditions.append(ASSETS.c.institution_id == institution_id)

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
        portfolio_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""
        # TODO: Might not need this function... It's here just in case

        conditions = []

        if asset_id:
            conditions.append(ASSETS.c.asset_id == asset_id)

        if portfolio_id:
            conditions.append(ASSETS.c.portfolio_id == portfolio_id)

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
        portfolio_id: int,
        institution_id: str,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by portfolio_id"""

        conditions = []

        if portfolio_id:
            conditions.append(ASSETS.c.portfolio_id == portfolio_id)

        if institution_id:
            conditions.append(ASSETS.c.institution_id == institution_id)

        query = ASSETS.select().where(and_(*conditions))
        results = await self.db.fetch_all(query)
        return [portfolios.AssetInDB(**result) for result in results]

    async def delete_asset(self, asset_id: int) -> None:
        """Delete asset"""

        delete_statement = delete(ASSETS).where(ASSETS.c.asset_id == asset_id)

        await self.db.execute(delete_statement)
