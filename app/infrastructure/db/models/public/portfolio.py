# NOTE: These models are currenly just mirroring the portfolio models constructed in the service, pelleum-api
import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.account_connections.institutions import INSTITUTIONS
from app.infrastructure.db.models.public.users import USERS

ASSETS = sa.Table(
    "assets",
    METADATA,
    sa.Column("asset_id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey(USERS.c.user_id),
        index=True,
    ),
    sa.Column(
        "institution_id",
        sa.String,
        sa.ForeignKey(INSTITUTIONS.c.institution_id),
    ),
    sa.Column(
        "thesis_id",
        sa.BigInteger,
        sa.ForeignKey("theses.thesis_id"),
        nullable=True,
        index=True,
    ),
    sa.Column("asset_symbol", sa.String, nullable=False),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("quantity", sa.Float, nullable=False),
    sa.Column("position_value", sa.Float, nullable=False),
    sa.Column("skin_rating", sa.Float, nullable=True),
    sa.Column("average_buy_price", sa.Float, nullable=True),
    sa.Column("total_contribution", sa.Float, nullable=True),
    sa.Column("is_up_to_date", sa.Boolean, nullable=False, default=True),
    sa.Column("update_errors", sa.Text, nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)

sa.Index(
    "ix_user_id_asset_symbol_institution_id",
    ASSETS.c.user_id,
    ASSETS.c.asset_symbol,
    ASSETS.c.institution_id,
    unique=True,
)
