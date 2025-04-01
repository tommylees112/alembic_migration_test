import sqlalchemy as sa
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from alembic_migrate.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)

    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=sa.text("CURRENT_TIMESTAMP"))

    author = relationship("User", back_populates="posts")


# SQLAlchemy representation of our analytics view
# The actual view definition is in views.py
class ActiveUser(Base):
    __tablename__ = "active_users"
    __table_args__ = {"info": {"is_view": True}}

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(100))
    post_count = Column(Integer)
    last_post_date = Column(DateTime)
