"""identify db

Revision ID: aa10332010e9
Revises: 
Create Date: 2023-12-19 02:34:37.350403

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "aa10332010e9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "bots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("token", sa.String(length=256), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "date_created",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_bots__token", "bots", ["token"], unique=False)
    op.create_table(
        "sheets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bot_id", sa.Integer(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("sheet", sa.Text(), nullable=False),
        sa.Column("index_column", sa.Text(), nullable=False),
        sa.Column("columns", sa.Text(), nullable=False),
        sa.Column("extend_columns", sa.Text(), nullable=True),
        sa.Column(
            "date_created",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["bot_id"],
            ["bots.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bot_id"),
        sa.UniqueConstraint("url"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sheets")
    op.drop_index("ix_bots__token", table_name="bots")
    op.drop_table("bots")
    # ### end Alembic commands ###