from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship
from database import Base
from game import Game
from user import User


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)

    game_id = Column(String, ForeignKey("games.id"))
    game = relationship(Game, backref="players")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)

    player_num = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    is_bot = Column(Boolean, nullable=False, default=False, server_default="false")
    vitality_multiplier = Column(Float, nullable=False, default=1.0, server_default="1.0")

    __table_args__ = (
        Index("player_idx_game_player_num", "game_id", "player_num", unique=True),
        Index("player_idx_user_game", "user_id", "game_id", unique=True),
    )

    def to_json(self):
        return {
            "is_bot": self.is_bot,
            "vitality_multiplier": self.vitality_multiplier,
            "username": self.user.username,
            "player_num": self.player_num,
        }