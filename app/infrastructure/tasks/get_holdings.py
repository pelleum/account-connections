from typing import List

from databases import Database
import asyncio

from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.schemas import portfolios
from app.usecases.schemas import institutions
from app.dependencies import logger


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
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                logger.exception(e)

            await asyncio.sleep()

    async def task(self):

        all_portfolios: List[
            portfolios.PortfolioInDB
        ] = await self._portfolio_repo.retrieve_all_portfolios()

        for portfolio in all_portfolios:
            user_account_connections: List[
                institutions.InstitutionConnectionJoinInstitution
            ] = await self._institution_repo.retrieve_many_institution_connections(
                user_id=portfolio.user_id
            )

            users_services = []
            for account_connection in user_account_connections:
                users_services.append(
                    (
                        service
                        for service in self.institution_services
                        if service.institution_name == account_connection.name
                    )
                )

            # TODO: use asyncio gather here for multiple independent requests to services

        # 1. Retrieve ALL portfolios (this will likely have to be paginated... maybe not)  X
        # 2. For each of those users (will likely have to do a join), grab the JWTs   X
        # 3. Reach out to robinhood for each of those users, grab the stuff
        # 4. Put it in portfolios and assets table... how?
        # If there's a new asset, need to create new... So each time, need to refernce current assets
        # For assets that already exist, need to update those
        # If there's an asset that does not exist, need to delete it (soft delete it)
        # Check db, if same, update, if diff, act accordingly
