import asyncio
from time import time
from typing import List

from databases import Database

from app.dependencies import logger
from app.settings import settings
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.schemas import institutions, portfolios

# import yfinance as yahoo_finance


class GetHoldingsTask:
    def __init__(
        self,
        db: Database,
        institution_repo: IInstitutionRepo,
        portfolio_repo: IPortfolioRepo,
        institution_services: List[IInstitutionService],
    ):
        self.db = db
        self._institution_repo = institution_repo
        self._portfolio_repo = portfolio_repo
        self.institution_services = institution_services

    async def start_task(self):
        await asyncio.sleep(60 * 60 * 12)
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                logger.exception(e)

            await asyncio.sleep(settings.asset_update_task_frequency)

    async def task(self):
        """Sync all Pelleum portfolios with linked brokerage portfolios."""
        logger.info(
            "[GetHoldingsTask]: Beginning periodic brokerage account sync task."
        )
        task_start_time = time()
        # 1. Get all account connenctions TODO: set this up for batches
        account_connections = (
            await self._institution_repo.retrieve_many_institution_connections(
                query_params=institutions.RetrieveManyConnectionsRepoAdapter(
                    is_active=True
                ),
                skip_locked=True,
            )
        )
        logger.info(
            "[GetHoldingsTask]: Retrieved %s account connections to process. Processing now..."
            % len(account_connections)
        )

        for account_connection in account_connections:
            service = next(
                (
                    service
                    for service in self.institution_services
                    if service.institution_name == account_connection.name
                ),
                None,
            )

            try:
                # 2. For each account connection, get user's holdings from brokerage API
                brokerage_portfolio = await service.get_recent_holdings(
                    encrypted_json_web_token=account_connection.json_web_token
                )

                newly_created_asset_symbols = await self.sync_with_brokerage_data(
                    user_id=account_connection.user_id,
                    institution_id=account_connection.institution_id,
                    brokerage_portfolio=brokerage_portfolio,
                )

                # 4. Only update asset in our database if NOT recently added (no need to update if it was just added)
                for asset in brokerage_portfolio.holdings:
                    if asset.asset_symbol not in newly_created_asset_symbols:

                        await self._portfolio_repo.update_asset(
                            user_id=account_connection.user_id,
                            asset_symbol=asset.asset_symbol,
                            institution_id=account_connection.institution_id,
                            updated_asset=portfolios.UpdateAssetRepoAdapter(
                                is_up_to_date=True,
                                quantity=asset.quantity,
                                average_buy_price=asset.average_buy_price,
                            ),
                        )
            except institutions.UnauthorizedException:
                # A 401 was returned, so update this connection's is_active column to False
                await self._institution_repo.update_institution_connection(
                    connection_id=account_connection.connection_id,
                    updated_connection=institutions.UpdateConnectionRepoAdapter(
                        is_active=False
                    ),
                )
                logger.warning(
                    "[GetHoldingsTask]: Received a 401 Unauthorized when attempting to update assets. Detail: connection_id: %s"
                    % account_connection.connection_id
                )
            except (
                institutions.InstitutionApiError,
                institutions.InstitutionException,
            ):
                continue

        task_end_time = time()

        logger.info(
            "[GetHoldingsTask]: Periodic brokerage account sync completed in %s seconds. Sleeping now..."
            % (task_end_time - task_start_time)
        )

    async def sync_with_brokerage_data(
        self,
        user_id: int,
        institution_id: str,
        brokerage_portfolio: institutions.UserBrokerageHoldings,
    ) -> List[str]:
        """Adds new holdings and deletes old holdings"""

        tracked_assets = await self._portfolio_repo.retrieve_brokerage_assets(
            user_id=user_id, institution_id=institution_id
        )

        tracked_asset_symbols = [asset.asset_symbol for asset in tracked_assets]
        brokerage_asset_symbols = [
            holding.asset_symbol for holding in brokerage_portfolio.holdings
        ]

        # 1. If we're tracking assets the user no longer has, add them to a list to delete from our database
        assets_to_delete_from_db = [
            asset
            for asset in tracked_assets
            if asset.asset_symbol not in brokerage_asset_symbols
        ]

        # 2. If the user's brokerage has assets we're not tracking, add them to a list to add to our database
        assets_to_add_to_db = [
            asset
            for asset in brokerage_portfolio.holdings
            if asset.asset_symbol not in tracked_asset_symbols
        ]

        # 3. For each asset the user no longer owns, delete from our database
        for asset in assets_to_delete_from_db:
            await self._portfolio_repo.delete(asset_id=asset.asset_id)

        # 4. For each asset we're not tracking, insert asset into our database
        for asset in assets_to_add_to_db:
            await self._portfolio_repo.upsert_asset(
                new_asset=portfolios.UpsertAssetRepoAdapter(
                    average_buy_price=asset.average_buy_price
                    if asset.average_buy_price
                    else None,
                    user_id=user_id,
                    institution_id=institution_id,
                    name=asset.asset_name,
                    asset_symbol=asset.asset_symbol,
                    quantity=asset.quantity,
                )
            )

        # 5. Return a list of the newly inserted asset symbols
        return [asset.asset_symbol for asset in assets_to_add_to_db]

    # async def get_asset_price(self, asset_symbol: str) -> float:
    #     """Retrieve current asset price"""
    #     # TODO: Integrate with API directly, too much uneccessary stuff (this will be becessary)
    #     return yahoo_finance.Ticker(asset_symbol).history(period="1d")["Close"][0]
