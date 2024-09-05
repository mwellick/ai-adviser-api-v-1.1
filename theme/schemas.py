from pydantic import BaseModel


class ThemeRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
