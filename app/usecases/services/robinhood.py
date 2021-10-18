from typing import Mapping

from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.interfaces.clients.robinhood import IRobinhoodClient
from app.usecases.schemas import institutions
from app.usecases.schemas import robinhood
from app.settings import settings
from app.libraries import pelleum_errors


class RobinhoodService(IInstitutionService):
    def __init__(
        self, robinhood_client: IRobinhoodClient, institution_repo: IInstitutionRepo
    ):
        self.robinhood_client = robinhood_client
        self._insitution_repo = institution_repo

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

    async def save_credentials(
        self,
        successful_login_response: robinhood.SuccessfulLoginResponse,
        user_id: str,
        institution_id: str,
    ) -> None:
        """Saves user's Robinhood credentials in our database"""

        await self._insitution_repo.create(
            connection_data=institutions.CreateConnectionRepoAdapter(
                institution_id=institution_id,
                user_id=user_id,
                json_web_token=successful_login_response.access_token,
                refresh_token=successful_login_response.refresh_token,
            )
        )
