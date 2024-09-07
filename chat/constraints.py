from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select, desc
from starlette import status
from dependencies import db_dependency, user_dependency
from database.models import Chat, Theme
from .schemas import ChatCreate, ChatRead


async def validate_create_chat_with_available_theme(db: db_dependency, chat: ChatCreate):
    query = select(Theme).where(Theme.id == chat.theme_id)
    result = await db.execute(query)
    theme_list = result.scalars().first()
    if not theme_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose an existing theme"
        )


async def check_chat_history(user: user_dependency, db: db_dependency):
    query = select(Chat).where(
        Chat.user_id == user.get("id")
    ).order_by(desc(Chat.created_at))

    result = await db.execute(query)
    chats_list = result.scalars().all()
    if not chats_list:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return chats_list


async def check_saved_chat_history(user: user_dependency, db: db_dependency):
    query = select(Chat).where(
        Chat.user_id == user.get("id")
    ).where(Chat.is_saved == True)

    result = await db.execute(query)
    saved_chats = result.scalars().all()
    if not saved_chats:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return saved_chats


async def check_existing_chat(user: user_dependency, db: db_dependency, chat_id: int):
    query = select(Chat).where(
        Chat.user_id == user.get("id")
    ).where(Chat.id == chat_id)

    result = await db.execute(query)

    chat_to_delete = result.scalars().first()
    if not chat_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return None