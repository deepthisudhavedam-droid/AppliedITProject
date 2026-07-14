from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WardrobeItemResponse(BaseModel):
    id: int
    user_id: int
    stored_filename: str
    original_filename: str
    image_url: str
    thumbnail_url: Optional[str] = None
    content_type: str
    file_size: int
    category: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
