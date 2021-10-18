from typing import Mapping, Optional, Any

import aiohttp

from app.usecases.interfaces.clients.robinhood import (
    RobinhoodException,
    IRobinhoodClient,
    RobinhoodApiError,
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
                raise RobinhoodApiError(
                    f"RobinhoodClient Error: {response.status} - {resp_json}",
                    http_status=response.status,
                    detail=resp_json["detail"],
                )

            return resp_json

    async def login(self, payload: robinhood.InitialLoginPayload) -> Mapping:
        """Login to Robinhood and return the response"""
        return await self.api_call(
            method="POST", endpoint="/oauth2/token/", json_body=payload.dict()
        )
