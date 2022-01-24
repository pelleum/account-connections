from typing import Any, Mapping, Optional

import aiohttp

from app.usecases.interfaces.clients.robinhood import IRobinhoodClient
from app.usecases.schemas import robinhood
from app.usecases.schemas.institutions import UnauthorizedException


class RobinhoodClient(IRobinhoodClient):
    def __init__(self, client_session: aiohttp.client.ClientSession):
        self.client_session = client_session
        self.robinhood_base_url = "https://api.robinhood.com"

    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Facilitate actual API call"""

        async with self.client_session.request(
            method,
            self.robinhood_base_url + endpoint,
            headers=headers,
            json=json_body,
            verify_ssl=False,
        ) as response:
            try:
                response_json = await response.json()
            except Exception:
                response_text = await response.text()
                raise robinhood.RobinhoodException(  # pylint: disable=raise-missing-from
                    f"RobinhoodClient Error: Response status: {response.status}, Response Text: {response_text}"
                )

            if response.status >= 300:
                if response.status == 401:
                    raise UnauthorizedException()

                if "challenge" in response_json:
                    return response_json

                # if neither of the above are true, raise error
                try:
                    error = robinhood.APIErrorBody(**response_json)
                except Exception:
                    raise robinhood.RobinhoodException(  # pylint: disable=raise-missing-from
                        f"RobinhoodClient Error: Response status: {response.status}, Response JSON: {response_json}"
                    )
                raise robinhood.RobinhoodApiError(
                    status=response.status,
                    detail=error.detail,
                )

            return response_json

    async def login(
        self, payload: robinhood.LoginPayload, challenge_id: Optional[str] = None
    ) -> Mapping[str, Any]:
        """Login to Robinhood and return the response"""

        payload_raw = payload.dict()

        if payload.grant_type == "refresh_token":
            del payload_raw["username"]
            del payload_raw["password"]
        else:
            if not payload.mfa_code:
                del payload_raw["mfa_code"]

        return await self.api_call(
            method="POST",
            endpoint="/oauth2/token/",
            json_body=payload_raw,
            headers={"X-ROBINHOOD-CHALLENGE-RESPONSE-ID": challenge_id}
            if challenge_id
            else None,
        )

    async def respond_to_challenge(
        self, challenge_code: str, challenge_id: str
    ) -> None:
        """Respond to challenge issued by Robinhood for those with 2FA disabled"""

        await self.api_call(
            method="POST",
            endpoint=f"/challenge/{challenge_id}/respond/",
            json_body={"response": challenge_code},
        )

    async def get_positions_data(
        self, access_token: str
    ) -> robinhood.PositionDataResponse:
        """Get posiitions data"""

        headers = {"Authorization": f"Bearer {access_token}"}

        positions_response_json = await self.api_call(
            method="GET", endpoint="/positions/?nonzero=true", headers=headers
        )
        try:
            return robinhood.PositionDataResponse(**positions_response_json)
        except Exception as error:
            raise robinhood.RobinhoodException(  # pylint: disable=raise-missing-from
                f"RobinhoodClient Error: There was an error when coercing Robinhood's JSON into our PositionDataResponse model.\nRobinhood's JSON: {positions_data_json}\nSpecific Error: {error}"
            )

    async def get_instrument_by_url(
        self, url: str, access_token: str
    ) -> robinhood.InstrumentByURLResponse:
        """Gets instrument, from which, the ticker symbol can be obtained"""

        endpoint = url.split("https://api.robinhood.com", 1)[1]

        headers = {"Authorization": f"Bearer {access_token}"}

        instrument_response_json = await self.api_call(
            method="GET", endpoint=endpoint, headers=headers
        )

        try:
            return robinhood.InstrumentByURLResponse(**instrument_response_json)
        except Exception as error:
            raise robinhood.RobinhoodException(  # pylint: disable=raise-missing-from
                f"RobinhoodClient Error: There was an error when coercing Robinhood's JSON into our InstrumentByURLResponse model.\nRobinhood's JSON: {instrument_data_json}\nSpecific Error: {error}"
            )

    async def get_name_by_symbol(
        self, symbol: str, access_token: str
    ) -> robinhood.NameDataResponse:
        """Gets asset name by symbol"""

        headers = {"Authorization": f"Bearer {access_token}"}

        name_response_json = await self.api_call(
            method="GET", endpoint=f"/instruments/?symbol={symbol}", headers=headers
        )

        try:
            return robinhood.NameDataResponse(**name_response_json)
        except Exception as error:
            raise robinhood.RobinhoodException(  # pylint: disable=raise-missing-from
                f"RobinhoodClient Error: There was an error when coercing Robinhood's JSON into our NameDataResponse model.\nRobinhood's JSON: {name_data_json}\nSpecific Error: {error}"
            )
