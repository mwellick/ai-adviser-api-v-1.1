from sqlalchemy import select
from database.models import Theme
from dependencies import db_dependency


async def get_all_themes_from_db(db: db_dependency):
    query = select(Theme)
    result = await db.execute(query)
    themes_list = result.scalars().all()
    return themes_list
