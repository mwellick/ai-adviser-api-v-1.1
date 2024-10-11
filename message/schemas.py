from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    content: str
    is_ai_response: bool
    is_saved: bool

    class Config:
        from_attributes = True


class SavedMessageRead(BaseModel):
    id: int
    user_request: str
    ai_response: str
    chat_id: int | None
    user_message_id: int
    ai_response_id: int

    class Config:
        from_attributes = True
