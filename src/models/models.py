from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from src.db.db_connector import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "url_shortener"}

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    token = Column(String)
    is_active = Column(Boolean, default=True)

    urls = relationship("URL", back_populates="user")


class URL(Base):
    __tablename__ = "urls"
    __table_args__ = {"schema": "url_shortener"}

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    target_url = Column(String, index=True)
    short_url = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("url_shortener.users.id"))
    type = Column(Enum("public", "private", name="url_type"), default="public")

    user = relationship("User", back_populates="urls")
