import asyncio
from time import time
from typing import List

from databases import Database

from app.dependencies import logger
from app.settings import settings
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.schemas import institutions

# import yfinance as yahoo_finance


class RefreshTokensTask:
    def __init__(
        self,
        db: Database,
        institution_repo: IInstitutionRepo,
        institution_services: List[IInstitutionService],
    ):
        self.db = db
        self._institution_repo = institution_repo
        self.institution_services = institution_services

    async def start_task(self):
        await asyncio.sleep(10)
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                logger.exception(e)

            await asyncio.sleep(settings.refresh_tokens_task_frequency)

    async def task(self):
        """Refresh tokens for all linked brokerages that require it."""

        logger.info("[RefreshTokenTask]: Beginning periodic token refresh task.")
        task_start_time = time()
        # 1. Get all active account connenctions that have refresh tokens
        account_connections = (
            await self._institution_repo.retrieve_many_institution_connections(
                query_params=institutions.RetrieveManyConnectionsRepoAdapter(
                    is_active=True, has_refresh_token=True
                )
            )
        )
        logger.info(
            "[RefreshTokenTask]: Retrieved %s account connections to process. Processing now..."
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
                # 2. For each retrieved connection, request new tokens from institution
                encrypted_refreshed_tokens = await service.refresh_token(
                    encrypted_refresh_token=account_connection.refresh_token
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
                    "[RefreshTokenTask]: Received a 401 Unauthorized when attempting to refresh token. Detail: connection_id: %s"
                    % account_connection.connection_id
                )
            except (
                institutions.InstitutionApiError,
                institutions.InstitutionException,
            ) as error:
                logger.warning(
                    "[RefreshTokenTask]: Error refreshing JSON web token - Error: %s"
                    % error
                )
                continue

            # 3. Save new tokens in database
            await self._institution_repo.update_institution_connection(
                connection_id=account_connection.connection_id,
                updated_connection=institutions.UpdateConnectionRepoAdapter(
                    json_web_token=encrypted_refreshed_tokens.encrypted_json_web_token,
                    refresh_token=encrypted_refreshed_tokens.encrypted_refresh_token,
                ),
            )

        task_end_time = time()

        logger.info(
            "[RefreshTokenTask]: Periodic token refresh task completed in %s seconds. Sleeping now..."
            % (task_end_time - task_start_time)
        )
