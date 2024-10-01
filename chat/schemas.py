from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from message.schemas import MessageRead


class ChatCreate(BaseModel):
    theme_id: int
    user_id: Optional[int] = None  # user or guest


class ChatCreated(BaseModel):
    id: int
    theme_id: int
    user_id: Optional[int] = None  # user or guest
    created_at: datetime


class GuestChatCreated(BaseModel):
    id: int


class ChatRead(BaseModel):
    id: int
    created_at: datetime
    theme_id: int
    user_id: Optional[int] = None  # user or guest
    messages: list[MessageRead]

    class Config:
        from_attributes = True

    @classmethod
    def get_first_chat_message(cls, message: MessageRead):
        first_message = message.messages[0] if message.messages else []

        return cls(
            id=message.id,
            created_at=message.created_at,
            theme_id=message.theme_id,
            user_id=message.user_id,
            messages=[first_message] if first_message else []
        )


class RetrieveChat(BaseModel):
    created_at: datetime
    theme_id: int
    user_id: Optional[int] = None  # user or guest
    messages: list[MessageRead]
