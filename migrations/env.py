import pathlib
import sys
from logging.config import fileConfig
from os import getenv

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

sys.path[0] = str(pathlib.Path(__file__).parents[1].resolve())
load_dotenv()

# Import Tables
from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.institutions import (
    INSTITUTION_CONNECTIONS,
    INSTITUTIONS,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

target_metadata = METADATA


url = getenv("ALEMBIC_DATABASE_URL")


config.set_main_option("sqlalchemy.url", url)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != getenv("SCHEMA"):
        return False
    else:
        return True


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=getenv("SCHEMA"),
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
