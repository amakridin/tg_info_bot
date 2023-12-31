"""bot_description_added

Revision ID: 710fc553e127
Revises: aa10332010e9
Create Date: 2023-12-27 11:49:40.718360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '710fc553e127'
down_revision = 'aa10332010e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bots', sa.Column('description', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bots', 'description')
    # ### end Alembic commands ###
