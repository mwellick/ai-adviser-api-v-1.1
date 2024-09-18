from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    content: str
    is_ai_response: bool

    class Config:
        from_attributes = True
