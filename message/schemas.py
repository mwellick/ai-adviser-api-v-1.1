from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    content: str
    is_ai_response: bool

    class Config:
        from_attributes = True
