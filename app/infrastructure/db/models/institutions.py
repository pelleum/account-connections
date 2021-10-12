import sqlalchemy as sa
from sqlalchemy import schema
from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.users import USERS


INSTITUTIONS = sa.Table(
    "institutions",
    METADATA,
    sa.Column("institution_id", sa.String, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
    schema="account-connections"
)


INSTITUTION_CONNECTIONS = sa.Table(
    "institution_connections",
    METADATA,
    sa.Column("connection_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "institution_id",
        sa.String,
        sa.ForeignKey("account-connections.institutions.institution_id"),
        index=True,
    ),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey(USERS.c.user_id),
        index=True,
    ),
    sa.Column("username", sa.String, nullable=True),
    sa.Column("password", sa.String, nullable=True),
    sa.Column("json_web_token", sa.String, nullable=True),
    sa.Column("refresh_token", sa.String, nullable=True),
    sa.Column("is_active", sa.Boolean, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
    schema="account-connections"
)
