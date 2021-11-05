from typing import Optional

import uvloop
import asyncio

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

loop: Optional[uvloop.Loop] = None


async def get_event_loop() -> uvloop.Loop:
    global loop  # pylint: disable = global-statement
    if loop is None:
        loop = asyncio.get_event_loop()

    return loop
