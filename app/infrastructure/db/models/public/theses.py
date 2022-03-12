import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

THESES = sa.Table(
    "theses",
    METADATA,
    sa.Column("thesis_id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        index=True,
    ),
    sa.Column("username", sa.String, nullable=False, index=True),
    sa.Column("title", sa.String, nullable=False),
    sa.Column("content", sa.Text, nullable=False),
    sa.Column("sources", sa.ARRAY(sa.String), nullable=True),
    sa.Column("asset_symbol", sa.String, nullable=False, index=True),
    sa.Column("sentiment", sa.String, nullable=False),
    sa.Column("is_authors_current", sa.Boolean, nullable=False, default=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)

sa.UniqueConstraint(THESES.c.user_id, THESES.c.title)
