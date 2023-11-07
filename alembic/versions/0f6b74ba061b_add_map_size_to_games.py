"""Add map_size to games

Revision ID: 0f6b74ba061b
Revises: 1c7522340b43
Create Date: 2023-11-07 15:26:56.573309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f6b74ba061b'
down_revision = '1c7522340b43'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('name', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'name')
    # ### end Alembic commands ###
