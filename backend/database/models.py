from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .connection import Base


class User(Base):
    """Represents a registered user account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), nullable=False)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    wardrobe_items = relationship(
        "WardrobeItem",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class WardrobeItem(Base):
    """Represents an image uploaded by a user for wardrobe analysis."""
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stored_filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    category = Column(String(80), nullable=True)
    color = Column(String(80), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="wardrobe_items")
