from fastapi import APIRouter
from starlette import status
from dependencies import db_dependency
from .crud import get_themes_list
from .schemas import ThemeRead

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
