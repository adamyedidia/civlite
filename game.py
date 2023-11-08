from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    name = Column(String, nullable=False)

    launched = Column(Boolean, nullable=False, default=False, server_default='f')

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.timestamp(),
        }