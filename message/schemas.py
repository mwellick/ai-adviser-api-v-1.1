from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(MessageCreate):
    id: int

    class Config:
        from_attributes = True
