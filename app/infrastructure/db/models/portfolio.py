# NOTE: These models are currenly just mirroring the portfolio models constructed in the service, pelleum-api
import sqlalchemy as sa
from app.infrastructure.db.metadata import METADATA


PORTFOLIOS = sa.Table(
    "portfolios",
    METADATA,
    sa.Column("portfolio_id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        index=True,
    ),
    sa.Column("aggregated_value", sa.Float, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
)


ASSETS = sa.Table(
    "assets",
    METADATA,
    sa.Column("asset_id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "portfolio_id",
        sa.BigInteger,
        sa.ForeignKey("portfolios.portfolio_id"),
        index=True,
    ),
    sa.Column(
        "thesis_id",
        sa.BigInteger,
        sa.ForeignKey("theses.thesis_id"),
        nullable=True,
        index=True,
    ),
    sa.Column("asset_symbol", sa.String, nullable=False),
    sa.Column("position_value", sa.Float, nullable=False),
    sa.Column("skin_rating", sa.Float, nullable=True),
    sa.Column("average_buy_price", sa.Float, nullable=True),
    sa.Column("total_contribution", sa.Float, nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
)

sa.UniqueConstraint(ASSETS.c.portfolio_id, ASSETS.c.asset_symbol)
