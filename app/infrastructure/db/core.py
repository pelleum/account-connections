from typing import Optional

import databases
from databases import Database

from app.settings import settings
from app.dependencies import logger

DATABASE: Optional[Database] = None


async def get_or_create_database() -> Database:
    global DATABASE
    if DATABASE is not None:
        return DATABASE

    DATABASE = databases.Database(settings.database_url, min_size=5)

    await DATABASE.connect()
    logger.info("Connected to Database!")
    return DATABASE
