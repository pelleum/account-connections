from typing import Mapping

from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.interfaces.services.encryption_service import IEncryptionService
from app.usecases.interfaces.clients.robinhood import IRobinhoodClient
from app.usecases.schemas import institutions
from app.usecases.schemas import robinhood
from app.settings import settings
from app.libraries import pelleum_errors


class RobinhoodService(IInstitutionService):
    def __init__(
        self,
        robinhood_client: IRobinhoodClient,
        institution_repo: IInstitutionRepo,
        encryption_service: IEncryptionService,
    ):
        self.robinhood_client = robinhood_client
        self._insitution_repo = institution_repo
        self.encryption_service = encryption_service
        self.institution_name = "Robinhood"

    async def login(
        self,
        credentials: institutions.UserCredentials,
    ) -> Mapping:
        """Login to Robinhood"""

        payload = robinhood.InitialLoginPayload(
            client_id=settings.robinhood_client_id,
            expires_in=86400,
            grant_type="password",
            username=credentials.username,
            password=credentials.password,
            scope="internal",
            challenge_type="sms",
            device_token=settings.robinhood_device_token,
        )

        return await self.robinhood_client.login(payload=payload)

    async def send_multifactor_auth_code(
        self,
        credentials: institutions.UserCredentialsWithMFA,
        user_id: int,
        institution_id: str,
    ) -> None:
        """Sends multi-factor auth code to Robinhood and processes response"""

        payload = robinhood.LoginPayloadWithMFA(
            client_id=settings.robinhood_client_id,
            expires_in=86400,
            grant_type="password",
            username=credentials.username,
            password=credentials.password,
            scope="internal",
            challenge_type="sms",
            device_token=settings.robinhood_device_token,
            mfa_code=credentials.mfa_code,
        )

        previous_connection = (
            await self._insitution_repo.retrieve_institution_connection(
                user_id=user_id, institution_id=institution_id
            )
        )

        if previous_connection:
            if previous_connection.is_active:
                raise await pelleum_errors.PelleumErrors(
                    detail=f"User with user_id, {user_id}, already has an active account connection with the institution, {institution_id}"
                ).account_exists()

            response_json = await self.robinhood_client.login(payload=payload)
            successful_login_response = robinhood.SuccessfulLoginResponse(
                **response_json
            )

            await self._insitution_repo.update_institution_connection(
                connection_id=previous_connection.connection_id,
                updated_connection=institutions.UpdateConnectionRepoAdapter(
                    is_active=True,
                    json_web_token=successful_login_response.access_token,
                    refresh_token=successful_login_response.refresh_token,
                ),
            )
        else:
            response_json = await self.robinhood_client.login(payload=payload)
            successful_login_response = robinhood.SuccessfulLoginResponse(
                **response_json
            )

            await self.save_credentials(
                successful_login_response=successful_login_response,
                user_id=user_id,
                institution_id=institution_id,
            )

    async def get_recent_holdings(
        self, encrypted_json_web_token
    ) -> robinhood.RobinhoodUserHoldings:
        """Returns most recent holdings directly from Robinhood"""

        json_web_token = await self.encryption_service.decrypt(
            encrypted_secret=encrypted_json_web_token
        )

        user_holdings = []

        # 1. Retrieve positions dictionary
        positions_data: robinhood.PositionDataResponse = (
            await self.robinhood_client.get_postitions_data(access_token=json_web_token)
        )

        # 2. For each position, get the asset's ticker symbol
        for position in positions_data.results:
            instrument_data: robinhood.InstrumentByURLResponse = (
                await self.robinhood_client.get_instrument_by_url(
                    url=position.instrument, access_token=json_web_token
                )
            )
            ticker_symbol = instrument_data.symbol

            # 3. Get asset name by its ticker symbol
            name_data: robinhood.NameDataResponse = (
                await self.robinhood_client.get_name_by_symbol(
                    symbol=ticker_symbol, access_token=json_web_token
                )
            )
            asset_name = name_data.results[0].name

            user_holdings.append(
                robinhood.RobhinhoodIndividualHoldingData(
                    asset_symbol=ticker_symbol,
                    quantity=position.quantity,
                    average_by_price=position.average_buy_price,
                    asset_name=asset_name,
                )
            )

        return robinhood.RobinhoodUserHoldings(holdings=user_holdings)

    async def save_credentials(
        self,
        successful_login_response: robinhood.SuccessfulLoginResponse,
        user_id: str,
        institution_id: str,
    ) -> None:
        """Saves user's Robinhood credentials in our database"""

        encrypted_json_web_token: str = await self.encryption_service.encrypt(
            secret=successful_login_response.access_token
        )
        encrypted_refresh_token: str = await self.encryption_service.encrypt(
            secret=successful_login_response.refresh_token
        )

        await self._insitution_repo.create(
            connection_data=institutions.CreateConnectionRepoAdapter(
                institution_id=institution_id,
                user_id=user_id,
                json_web_token=encrypted_json_web_token,
                refresh_token=encrypted_refresh_token,
            )
        )
