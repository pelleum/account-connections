from typing import List
import time

from databases import Database
import uvloop

from app.dependencies import (
    get_event_loop,
    get_institution_repo,
    get_portfolio_repo,
    get_all_institution_services,
)
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.tasks.get_holdings import GetHoldingsTask
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService


async def start_ongoing_holdings_sync():

    loop: uvloop.Loop = await get_event_loop()
    database: Database = await get_or_create_database()
    institution_repo: IInstitutionRepo = await get_institution_repo()
    portfolio_repo: IPortfolioRepo = await get_portfolio_repo()
    institution_services: List[
        IInstitutionService
    ] = await get_all_institution_services()

    get_holdings_task = GetHoldingsTask(
        db=database,
        institution_repo=institution_repo,
        portfolio_repo=portfolio_repo,
        institution_services=institution_services,
    )
    loop.create_task(get_holdings_task.start_task())