from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database import Base

class AnimationFrame(Base):
    __tablename__ = "animation_frames"

    id = Column(Integer, primary_key=True)

    game_id = Column(String, ForeignKey("games.id"))
    game = relationship("Game", backref="game_state_records")

    turn_num = Column(Integer, nullable=False)
    player_num = Column(Integer)
    frame_num = Column(Integer, nullable=False)
    is_decline = Column(Boolean, nullable=True)

    game_state = Column(JSONB)
    data = Column(JSONB)

    __table_args__ = (
        Index("animation_frame_idx_game_turn_num_player_num_frame_num", 
              "game_id", "turn_num", "player_num", "frame_num", unique=True),
        Index("animation_frame_idx_game_player_num_frame_num_turn_num",
              "game_id", "player_num", "frame_num", "turn_num"),
        Index('animation_frame_idx_game_id_turn_num_is_decline', 
              "game_id", "turn_num", "is_decline", unique=True),
    )

