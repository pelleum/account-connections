from fastapi import FastAPI
import uvicorn
import click

from app.infrastructure.web.endpoints.public import institutions
from app.infrastructure.web.endpoints.private import example as example_private
from app.infrastructure.web.endpoints import health
from app.dependencies import get_event_loop, get_client_session

# This line must be imported after app.dependencies to avoid a circular import (dependencies calls get_user_repo, which depends on get_or_create_database).
from app.infrastructure.db.core import get_or_create_database


from app.settings import settings


def setup_app():
    app = FastAPI(
        title="Account Connections API",
        description="The following are endpoints for the Pelleum account-connections service.",
    )
    app.include_router(institutions.institution_router, prefix="/public/institutions")
    app.include_router(example_private.example_private_router, prefix="/private")
    app.include_router(health.health_router, prefix="/health")

    return app


fastapi_app = setup_app()


@fastapi_app.on_event("startup")
async def startup_event():
    await get_event_loop()
    await get_client_session()
    await get_or_create_database()


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    # Close client session
    client_session = await get_client_session()
    await client_session.close()

    # Close database connection once db exists
    DATABASE = await get_or_create_database()
    if DATABASE.is_connected:
        await DATABASE.disconnect()


@click.command()
@click.option("--reload", is_flag=True)
def main(reload=False):

    kwargs = {"reload": reload}

    uvicorn.run(
        "app.infrastructure.web.setup:fastapi_app",
        loop="uvloop",
        host=settings.server_host,
        port=settings.server_port,
        **kwargs,
    )
