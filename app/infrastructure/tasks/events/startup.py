import time
from typing import List

import uvloop
from databases import Database

from app.dependencies import (
    get_all_institution_services,
    get_event_loop,
    get_institution_repo,
    get_portfolio_repo,
)
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.tasks.get_holdings import GetHoldingsTask
from app.infrastructure.tasks.refresh_tokens import RefreshTokensTask


async def start_ongoing_holdings_sync():

    loop = await get_event_loop()
    database = await get_or_create_database()
    institution_repo = await get_institution_repo()
    portfolio_repo = await get_portfolio_repo()
    institution_services = await get_all_institution_services()

    get_holdings_task = GetHoldingsTask(
        db=database,
        institution_repo=institution_repo,
        portfolio_repo=portfolio_repo,
        institution_services=institution_services,
    )
    loop.create_task(get_holdings_task.start_task())


async def start_ongoing_token_refresh():
    loop = await get_event_loop()
    database = await get_or_create_database()
    institution_repo = await get_institution_repo()
    institution_services = await get_all_institution_services()

    refresh_tokens_task = RefreshTokensTask(
        db=database,
        institution_repo=institution_repo,
        institution_services=institution_services,
    )
    loop.create_task(refresh_tokens_task.start_task())
