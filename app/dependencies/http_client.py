from typing import Optional

import aiohttp

client_session: Optional[aiohttp.client.ClientSession] = None


async def get_client_session() -> aiohttp.client.ClientSession:
    global client_session  # pylint: disable = global-statement
    if client_session is None:
        client_session = aiohttp.ClientSession()

    return client_session
