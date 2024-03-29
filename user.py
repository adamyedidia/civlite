
from sqlalchemy import Column, DateTime, Integer, String, func
from database import Base

BOT_USERNAMES = ['BOT_ALICE', 'BOT_BOB', 'BOT_CAROL', 'BOT_DAVE', 'BOT_EVE', 'BOT_FRANK', 'BOT_GRACE', 'BOT_HEIDI']

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)


def add_or_get_user(sess, username: str) -> User:
    user = sess.query(User).filter(User.username == username).first()

    if user is None:
        user = User(
            username=username,
        )
        sess.add(user)
        sess.commit()

    return user


def add_bot_users(sess) -> None:
    for username in BOT_USERNAMES:
        add_or_get_user(sess, username)