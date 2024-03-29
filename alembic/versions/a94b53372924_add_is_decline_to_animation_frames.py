"""Add is_decline to animation frames

Revision ID: a94b53372924
Revises: b24e69490762
Create Date: 2024-03-02 22:45:02.924323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a94b53372924'
down_revision = 'b24e69490762'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('animation_frames', sa.Column('is_decline', sa.Boolean(), nullable=True))
    op.create_index('animation_frame_idx_game_id_turn_num_is_decline', 'animation_frames', ['game_id', 'turn_num', 'is_decline'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('animation_frame_idx_game_id_turn_num_is_decline', table_name='animation_frames')
    op.drop_column('animation_frames', 'is_decline')
    # ### end Alembic commands ###
