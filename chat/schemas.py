from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ChatCreate(BaseModel):
    theme_id: int
    user_id: Optional[int] = None  # user or guest


class ChatRead(BaseModel):
    id: int
    created_at: datetime
    theme_id: int
    user_id: Optional[int] = None  # user or guest
    is_saved: bool

    class Config:
        from_attributes = True
