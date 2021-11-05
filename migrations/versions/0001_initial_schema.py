"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2021-10-26 19:14:46.217583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "institutions",
        sa.Column("institution_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("institution_id"),
        schema="account_connections",
    )
    op.create_table(
        "robinhood_instruments",
        sa.Column("instrument_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("instrument_id"),
        schema="account_connections",
    )
    op.create_table(
        "institution_connections",
        sa.Column("connection_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("institution_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("json_web_token", sa.String(), nullable=True),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"],
            ["account_connections.institutions.institution_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("connection_id"),
        schema="account_connections",
    )
    op.create_index(
        op.f("ix_account_connections_institution_connections_institution_id"),
        "institution_connections",
        ["institution_id"],
        unique=False,
        schema="account_connections",
    )
    op.create_index(
        op.f("ix_account_connections_institution_connections_user_id"),
        "institution_connections",
        ["user_id"],
        unique=False,
        schema="account_connections",
    )
    op.create_index(
        "ix_user_id_institution_id",
        "institution_connections",
        ["user_id", "institution_id"],
        unique=True,
        schema="account_connections",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "ix_user_id_institution_id",
        table_name="institution_connections",
        schema="account_connections",
    )
    op.drop_index(
        op.f("ix_account_connections_institution_connections_user_id"),
        table_name="institution_connections",
        schema="account_connections",
    )
    op.drop_index(
        op.f("ix_account_connections_institution_connections_institution_id"),
        table_name="institution_connections",
        schema="account_connections",
    )
    op.drop_table("institution_connections", schema="account_connections")
    op.drop_table("robinhood_instruments", schema="account_connections")
    op.drop_table("institutions", schema="account_connections")
    # ### end Alembic commands ###
