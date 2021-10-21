from typing import List
from sqlalchemy import desc

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

    async def retrieve_all_portfolios(self) -> List[portfolios.PortfolioInDB]:
        """Retrieve all Pelleum portfolios"""

        query = PORTFOLIOS.select().order_by(desc(PORTFOLIOS.c.created_at))

        query_results = await self.db.fetch_all(query)
        return [portfolios.PortfolioInDB(**result) for result in query_results]

    async def create_asset(self, new_asset: portfolios.AssetRepoAdapter) -> None:
        """Creates new asset"""

        asset_insert_statement = ASSETS.insert().values(
            portfolio_id=new_asset.portfolio_id,
            thesis_id=new_asset.portfolio_id,
            asset_symbol=new_asset.asset_symbol,
            position_value=new_asset.position_value,
            skin_rating=new_asset.skin_rating,
            average_buy_price=new_asset.average_buy_price,
            total_contribution=new_asset.total_contribution,
        )

        await self.db.execute(asset_insert_statement)

    async def update_asset(
        self,
        asset_id: int,
        updated_asset: portfolios.UpdateAssetRepoAdapter,
    ) -> None:
        """Update an indiviual asset holding by asset_id"""

        query = ASSETS.update()

        updated_asset_raw = updated_asset.dict()
        update_asset_dict = {}

        for key, value in updated_asset_raw.items():
            if value is not None:
                update_asset_dict[key] = value

        query = query.values(update_asset_dict)

        asset_update_statemnent = query.where(ASSETS.c.asset_id == asset_id)

        await self.db.execute(asset_update_statemnent)
