from typing import Mapping, List, Optional, Union

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
        # Add ILogger here!
    ):
        self.robinhood_client = robinhood_client
        self._insitution_repo = institution_repo
        self.encryption_service = encryption_service
        self.institution_name = "Robinhood"

    async def login(
        self,
        credentials: institutions.UserCredentials,
        user_id: int,
        institution_id: str,
    ) -> Union[Mapping, robinhood.CreateOrUpdateAssetsOnLogin]:
        """Login to Robinhood"""

        # 1. See if an account-connection is already active
        previous_connection = (
            await self._insitution_repo.retrieve_institution_connection(
                user_id=user_id, institution_id=institution_id
            )
        )

        if previous_connection:
            if previous_connection.is_active:
                raise await pelleum_errors.PelleumErrors(
                    detail=f"User with user_id, {user_id}, already has an active account connection with Robinhood."
                ).account_exists()

        # 2. Construct payload to send to Robinhood
        payload = robinhood.LoginPayload(
            client_id=settings.robinhood_client_id,
            expires_in=86400,
            grant_type="password",
            username=credentials.username,
            password=credentials.password,
            scope="internal",
            challenge_type="sms",
            device_token=settings.robinhood_device_token,
        )

        # 3. Login to Robinhood
        robinhood_json_response = await self.robinhood_client.login(payload=payload)
        forbidden_returned_data = ("access_token", "refresh_token")

        for key in robinhood_json_response:
            # This will only ever be the case for those with 2FA disabled on their accounts
            if key in forbidden_returned_data:
                successful_login_response = robinhood.SuccessfulLoginResponse(
                    **robinhood_json_response
                )
                if previous_connection:
                    connection: institutions.InstitutionConnection = (
                        await self.update_credentials(
                            connection_id=previous_connection.connection_id,
                            successful_login_response=successful_login_response,
                        )
                    )
                else:
                    connection: institutions.InstitutionConnection = (
                        await self.save_credentials(
                            user_id=user_id,
                            institution_id=institution_id,
                            login_credentials=credentials,
                            successful_login_response=successful_login_response,
                        )
                    )

                return robinhood.CreateOrUpdateAssetsOnLogin(
                    action="update" if previous_connection else "create",
                    brokerage_portfolio=await self.get_recent_holdings(
                        encrypted_json_web_token=connection.json_web_token
                    ),
                )

        if previous_connection:
            if (
                previous_connection.username != credentials.username
                or previous_connection.password != credentials.password
            ):
                # Update account-connection object in database
                await self.update_credentials(
                    login_credentials=credentials,
                    connection_id=previous_connection.connection_id,
                )
        else:
            await self.save_credentials(
                login_credentials=credentials,
                user_id=user_id,
                institution_id=institution_id,
            )

        return robinhood_json_response

    async def send_multifactor_auth_code(
        self,
        verification_proof: institutions.UserVerificationCredentials,
        user_id: int,
        institution_id: str,
    ) -> institutions.UserHoldings:
        """Sends multi-factor auth code to Robinhood and returns holdings"""

        previous_connection = (
            await self._insitution_repo.retrieve_institution_connection(
                user_id=user_id, institution_id=institution_id
            )
        )

        # 1. Ensure account-connection already exists in our database (raise error if not)
        if not previous_connection:
            raise await pelleum_errors.PelleumErrors(
                detail="Robinhood connection for this user does not exist. Please link account."
            ).invalid_resource_id()

        # 2. Ensure the connection is not already active
        if previous_connection.is_active:
            raise await pelleum_errors.PelleumErrors(
                detail=f"User with user_id, {user_id}, already has an active account connection with Robinhood."
            ).account_exists()

        # 3. Decrypt Robinhood credentials
        decrypted_username = await self.encryption_service.decrypt(
            encrypted_secret=previous_connection.username
        )
        decrypted_password = await self.encryption_service.decrypt(
            encrypted_secret=previous_connection.password
        )

        # 4. Construct Robinhood login payload object
        payload = robinhood.LoginPayload(
            client_id=settings.robinhood_client_id,
            expires_in=86400,
            grant_type="password",
            username=decrypted_username,
            password=decrypted_password,
            scope="internal",
            challenge_type="sms",
            device_token=settings.robinhood_device_token,
            mfa_code=verification_proof.sms_code
            if verification_proof.sms_code
            else None,
        )

        # A previous connection exists, but it's not active, so get new access token
        if verification_proof.challenge_id:
            # Send request to supply challenge_id and code (pass the challenge)
            await self.robinhood_client.respond_to_challenge(
                challenge_code=verification_proof.sms_code,
                challenge_id=verification_proof.challenge_id,
            )
            # Send login request with challenge_id in the header
            response_json = await self.robinhood_client.login(
                payload=payload,
                challenge_id=verification_proof.challenge_id,
            )
        else:
            # Challenge not needed, proceed with mfa
            response_json = await self.robinhood_client.login(payload=payload)

        successful_login_response = robinhood.SuccessfulLoginResponse(**response_json)
        # Update connection in our database
        updated_connection: institutions.InstitutionConnection = (
            await self.update_credentials(
                successful_login_response=successful_login_response,
                connection_id=previous_connection.connection_id,
            )
        )
        # Retrieve and save our most recent holdings
        return await self.get_recent_holdings(
            encrypted_json_web_token=updated_connection.json_web_token
        )

    async def get_recent_holdings(
        self, encrypted_json_web_token: str
    ) -> institutions.UserHoldings:
        """Returns most recent holdings directly from Robinhood"""

        # 1. Decrypt JSON web token
        json_web_token = await self.encryption_service.decrypt(
            encrypted_secret=encrypted_json_web_token
        )

        user_holdings = []

        # 2. Retrieve positions data from Robinhood
        positions_data: robinhood.PositionDataResponse = (
            await self.robinhood_client.get_postitions_data(access_token=json_web_token)
        )

        # 3. See the instruments we're already tracking
        instrument_tracking: robinhood.InstrumentTracking = (
            await self.get_tracked_instruments(
                robinhood_instruments=positions_data.results
            )
        )

        # 4. Build institutions.UserHoldings
        for robinhood_instrument in positions_data.results:
            tracked_instrument: Optional[
                institutions.RobinhoodInstrument
            ] = instrument_tracking.tracked_instruments.get(
                robinhood_instrument.instrument_id
            )
            if tracked_instrument:
                # We're already tracking this instrument, so no need to reach out to Robinhood!
                user_holdings.append(
                    institutions.IndividualHoldingData(
                        asset_symbol=tracked_instrument.symbol,
                        quantity=robinhood_instrument.quantity,
                        average_buy_price=robinhood_instrument.average_buy_price,
                        asset_name=tracked_instrument.name,
                    )
                )
            else:
                # We're not tracking this instrument, so reach out to Robinhood for the name and the ticker symbol
                instrument_data: robinhood.InstrumentByURLResponse = (
                    await self.robinhood_client.get_instrument_by_url(
                        url=robinhood_instrument.instrument, access_token=json_web_token
                    )
                )
                ticker_symbol = instrument_data.symbol

                name_data: robinhood.NameDataResponse = (
                    await self.robinhood_client.get_name_by_symbol(
                        symbol=ticker_symbol, access_token=json_web_token
                    )
                )
                asset_name = name_data.results[0].name

                user_holdings.append(
                    institutions.IndividualHoldingData(
                        asset_symbol=ticker_symbol,
                        quantity=robinhood_instrument.quantity,
                        average_buy_price=robinhood_instrument.average_buy_price,
                        asset_name=asset_name,
                    )
                )

                # 5. Save previously untracked instrument in our database
                await self._insitution_repo.create_robinhood_instrument(
                    instrument_id=robinhood_instrument.instrument_id,
                    name=asset_name,
                    symbol=ticker_symbol,
                )

        return institutions.UserHoldings(
            holdings=user_holdings, insitution_name=self.institution_name
        )

    async def save_credentials(
        self,
        user_id: str,
        institution_id: str,
        login_credentials: Optional[institutions.UserCredentials] = None,
        successful_login_response: Optional[robinhood.SuccessfulLoginResponse] = None,
    ) -> institutions.InstitutionConnection:
        """Saves user's Robinhood credentials in our database"""

        if login_credentials:
            encrypted_username: str = await self.encryption_service.encrypt(
                secret=login_credentials.username
            )
            encrypted_password: str = await self.encryption_service.encrypt(
                secret=login_credentials.password
            )

        if successful_login_response:
            encrypted_json_web_token: str = await self.encryption_service.encrypt(
                secret=successful_login_response.access_token
            )
            encrypted_refresh_token: str = await self.encryption_service.encrypt(
                secret=successful_login_response.refresh_token
            )

        return await self._insitution_repo.create(
            connection_data=institutions.CreateConnectionRepoAdapter(
                institution_id=institution_id,
                user_id=user_id,
                username=encrypted_username,
                password=encrypted_password,
                json_web_token=encrypted_json_web_token
                if successful_login_response
                else None,
                refresh_token=encrypted_refresh_token
                if successful_login_response
                else None,
                is_active=bool(successful_login_response),
            )
        )

    async def update_credentials(
        self,
        connection_id: int,
        login_credentials: Optional[institutions.UserCredentials] = None,
        successful_login_response: Optional[robinhood.SuccessfulLoginResponse] = None,
    ) -> Optional[institutions.InstitutionConnection]:
        """Updates Robinhood user's credentials in our database"""

        if login_credentials:
            decrypted_username = await self.encryption_service.encrypt(
                secret=login_credentials.username
            )
            decrypted_password = await self.encryption_service.encrypt(
                secret=login_credentials.password
            )

            await self._insitution_repo.update_institution_connection(
                connection_id=connection_id,
                updated_connection=institutions.UpdateConnectionRepoAdapter(
                    username=decrypted_username,
                    password=decrypted_password,
                ),
            )

        if successful_login_response:
            encrypted_json_web_token: str = await self.encryption_service.encrypt(
                secret=successful_login_response.access_token
            )
            encrypted_refresh_token: str = await self.encryption_service.encrypt(
                secret=successful_login_response.refresh_token
            )

            return await self._insitution_repo.update_institution_connection(
                connection_id=connection_id,
                updated_connection=institutions.UpdateConnectionRepoAdapter(
                    is_active=True,
                    json_web_token=encrypted_json_web_token,
                    refresh_token=encrypted_refresh_token,
                ),
            )

    async def get_tracked_instruments(
        self, robinhood_instruments: List[robinhood.PositionData]
    ) -> robinhood.InstrumentTracking:
        """Returns the the instruments we're tracking in our database as a dictionary
        where the keys are instrument_ids and the values are pydantic
        institutions.RobinhoodInstrument objects"""

        robinhood_instrument_ids: List[str] = [
            instrument.instrument_id for instrument in robinhood_instruments
        ]

        tracked_instruments: List[
            institutions.RobinhoodInstrument
        ] = await self._insitution_repo.retrieve_robinhood_instruments(
            instrument_ids=robinhood_instrument_ids
        )

        tracked_instruments_dict: Mapping = {}
        for tracked_instrument in tracked_instruments:
            tracked_instruments_dict[
                tracked_instrument.instrument_id
            ] = tracked_instrument

        return robinhood.InstrumentTracking(
            tracked_instruments=tracked_instruments_dict,
        )
