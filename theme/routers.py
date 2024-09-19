from fastapi import APIRouter
from starlette import status
from dependencies import db_dependency, user_dependency
from .crud import get_themes_list
from .schemas import ThemeRead
from database.models import Theme

themes_router = APIRouter(
    prefix="/themes",
    tags=["themes"]
)


@themes_router.get(
    "/",
    response_model=list[ThemeRead],
    status_code=status.HTTP_200_OK
)
async def get_all_themes(db: db_dependency):
    return await get_themes_list(db)


@themes_router.post("/create")
async def create_theme(db: db_dependency, user: user_dependency):
    theme = Theme(
    )
    ...
