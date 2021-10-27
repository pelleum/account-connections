from typing import Mapping, Optional, Any

import aiohttp

from app.usecases.interfaces.clients.robinhood import (
    RobinhoodException,
    IRobinhoodClient,
    RobinhoodApiError,
    APIErrorBody,
)
from app.usecases.schemas import robinhood


class RobinhoodClient(IRobinhoodClient):
    def __init__(self, client_session: aiohttp.client.ClientSession):
        self.client_session = client_session
        self.robinhood_base_url = "https://api.robinhood.com"

    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict] = None,
        json_body: Any = None,
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
                resp_json = await response.json()
            except Exception:
                resp_text = await response.text()
                raise RobinhoodException(  # pylint: disable=raise-missing-from
                    f"RobinhoodClient Error: Response status: {response.status}, Response Text: {resp_text}"
                )
            if response.status >= 300:
                try:
                    error = APIErrorBody(**resp_json)
                except Exception:
                    raise RobinhoodException(  # pylint: disable=raise-missing-from
                        f"RobinhoodClient Error: Response status: {response.status}, Response JSON: {resp_json}"
                    )
                raise RobinhoodApiError(
                    f"RobinhoodClient Error: {response.status} - {resp_json}",
                    http_status=response.status,
                    detail=error.detail,
                )

            return resp_json

    async def login(self, payload: robinhood.InitialLoginPayload) -> Mapping:
        """Login to Robinhood and return the response"""
        return await self.api_call(
            method="POST", endpoint="/oauth2/token/", json_body=payload.dict()
        )

    async def get_postitions_data(
        self, access_token: str
    ) -> robinhood.PositionDataResponse:
        """Get posiitions data"""

        headers = {"Authorization": f"Bearer {access_token}"}

        positions_data_json = await self.api_call(
            method="GET", endpoint="/positions/?nonzero=true", headers=headers
        )
        try:
            return robinhood.PositionDataResponse(**positions_data_json)
        except Exception as error:
            raise RobinhoodException(  # pylint: disable=raise-missing-from
                f"RobinhoodClient Error: There was an error when coercing Robinhood's JSON into our PositionDataResponse model.\nRobinhood's JSON: {positions_data_json}\nSpecific Error: {error}"
            )

    async def get_instrument_by_url(
        self, url: str, access_token: str
    ) -> robinhood.InstrumentByURLResponse:
        """Gets instrument, from which, the ticker symbol can be obtained"""

        endpoint = url.split("https://api.robinhood.com", 1)[1]

        headers = {"Authorization": f"Bearer {access_token}"}

        instrument_data_json = await self.api_call(
            method="GET", endpoint=endpoint, headers=headers
        )

        try:
            return robinhood.InstrumentByURLResponse(**instrument_data_json)
        except Exception as error:
            raise RobinhoodException(  # pylint: disable=raise-missing-from
                f"RobinhoodClient Error: There was an error when coercing Robinhood's JSON into our InstrumentByURLResponse model.\nRobinhood's JSON: {instrument_data_json}\nSpecific Error: {error}"
            )

    async def get_name_by_symbol(
        self, symbol: str, access_token: str
    ) -> robinhood.NameDataResponse:
        """Gets asset name by symbol"""

        headers = {"Authorization": f"Bearer {access_token}"}

        name_data_json = await self.api_call(
            method="GET", endpoint=f"/instruments/?symbol={symbol}", headers=headers
        )

        try:
            return robinhood.NameDataResponse(**name_data_json)
        except Exception as error:
            raise RobinhoodException(  # pylint: disable=raise-missing-from
                f"RobinhoodClient Error: There was an error when coercing Robinhood's JSON into our NameDataResponse model.\nRobinhood's JSON: {name_data_json}\nSpecific Error: {error}"
            )
