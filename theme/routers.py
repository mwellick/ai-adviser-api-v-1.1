from fastapi import APIRouter, Path
from sqlalchemy import select
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


@themes_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_theme(
        name: str,
        description: str,
        db: db_dependency,
        user: user_dependency
):  # TODO Temporary endpoint. To delete it when project goes to prod
    theme = Theme(
        name=name,
        description=description
    )
    db.add(theme)
    await db.commit()


@themes_router.delete("/{theme_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
        db: db_dependency,
        user: user_dependency,
        theme_id: int = Path(gt=0)
):  # TODO Temporary endpoint. To delete it when project goes to prod
    query = select(Theme).where(
        Theme.id == theme_id)

    result = await db.execute(query)

    theme_to_delete = result.scalars().first()

    await db.delete(theme_to_delete)
    await db.commit()
    return None
