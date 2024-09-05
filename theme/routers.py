from fastapi import APIRouter
from sqlalchemy import select
from starlette import status
from dependencies import db_dependency
from database.models import Theme
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
    query = select(Theme)
    result = await db.execute(query)
    themes_list = result.scalars().all()
    return themes_list
