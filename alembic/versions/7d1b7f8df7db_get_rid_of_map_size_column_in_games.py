"""Get rid of map_size column in games

Revision ID: 7d1b7f8df7db
Revises: 0f6b74ba061b
Create Date: 2023-11-08 18:02:10.280679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d1b7f8df7db'
down_revision = '0f6b74ba061b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'map_size')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('map_size', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###