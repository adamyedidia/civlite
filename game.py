from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.types import Enum as SQLEnum

from database import Base

from enum import Enum as PyEnum

class TimerStatus(PyEnum):
    NORMAL = "NORMAL"
    OVERTIME = "OVERTIME"
    PAUSED = "PAUSED"

class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    name = Column(String, nullable=False)

    launched = Column(Boolean, nullable=False, default=False, server_default='f')
    game_over = Column(Boolean, nullable=False, default=False, server_default='f')

    seconds_per_turn = Column(Integer, nullable=True)
    timer_status = Column(SQLEnum(TimerStatus), nullable=False, default=TimerStatus.NORMAL, server_default='NORMAL')
    turn_num = Column(Integer, nullable=False, default=1, server_default='1')
    next_forced_roll_at = Column(Integer, nullable=True)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.timestamp(),
        }