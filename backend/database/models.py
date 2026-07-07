import uuid
from sqlalchemy import Column, String, DateTime, func
from .connection import Base


class User(Base):
    """Represents a registered user account."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(80), nullable=False)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
