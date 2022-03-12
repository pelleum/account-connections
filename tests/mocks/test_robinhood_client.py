import uuid
from typing import Any, Mapping, Optional

from app.usecases.interfaces.clients.robinhood import IRobinhoodClient
from app.usecases.schemas import robinhood


class MockRobinhoodClient(IRobinhoodClient):
    """Mocks the Robinhood client"""

    def __init__(self):
        pass

    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Facilitate actual API call"""

    async def login(
        self, payload: robinhood.LoginPayload, challenge_id: Optional[str] = None
    ) -> Mapping[str, Any]:
        """Login to Robinhood and return the response"""

        return {
            "access_token": str(uuid.uuid4()),
            "expires_in": 100000,
            "token_type": "bearer",
            "scope": "something",
            "refresh_token": str(uuid.uuid4()),
        }

    async def respond_to_challenge(
        self, challenge_code: str, challenge_id: str
    ) -> None:
        """Respond to challenge issued by Robinhood for those with 2FA disabled"""

    async def get_positions_data(
        self, access_token: str
    ) -> robinhood.PositionDataResponse:
        """Get posiitions data"""

        position_data_list = []
        for _ in range(3):
            instrument_id = str(uuid.uuid4())
            position_data_list.append(
                {
                    "instrument": f"https://api.robinhood.com/instruments/{instrument_id}/",
                    "instrument_id": instrument_id,
                    "average_buy_price": "631.0196",
                    "quantity": "29.04380500",
                }
            )

        return robinhood.PositionDataResponse(**{"results": position_data_list})

    async def get_instrument_by_url(
        self, url: str, access_token: str
    ) -> robinhood.InstrumentByURLResponse:
        """Gets instrument, from which, the ticker symbol can be obtained"""

        return robinhood.InstrumentByURLResponse(symbol="TSLA")

    async def get_name_by_symbol(
        self, symbol: str, access_token: str
    ) -> robinhood.NameDataResponse:
        """Gets asset name by symbol"""

        return robinhood.NameDataResponse(results=[robinhood.NameData(name="BTC")])
