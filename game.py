from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    map_size = Column(Integer, nullable=False)

    launched = Column(Boolean, nullable=False, default=False, server_default='f')

    def to_json(self):
        return {
            "id": self.id,
            "map_size": self.map_size,
            "created_at": self.created_at.timestamp(),
        }