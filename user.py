
from sqlalchemy import Column, DateTime, Integer, String, func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)