from pydantic import BaseModel


class ThemeRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class ThemeCreate(BaseModel):  # TODO Temporary schema. To delete it when project goes to prod
    name: str
    description: str
