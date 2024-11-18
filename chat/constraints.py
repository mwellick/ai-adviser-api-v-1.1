from typing import Union
from fastapi import HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload, selectinload
from starlette import status
from dependencies import db_dependency, user_dependency
from database.models import Chat, Theme
from .schemas import ChatCreate, GuestChatCreate


async def validate_create_chat_with_available_theme(
    db: db_dependency, chat: Union[ChatCreate, GuestChatCreate]
):
    query = select(Theme).where(Theme.id == chat.theme_id)
    result = await db.execute(query)
    theme_list = result.scalars().first()
    if not theme_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose an existing theme",
        )


async def check_chat_history(user: user_dependency, db: db_dependency):
    query = (
        select(Chat)
        .options(joinedload(Chat.user), selectinload(Chat.messages))
        .where(Chat.user_id == user.get("id"))
        .order_by(desc(Chat.created_at))
    )

    result = await db.execute(query)
    chats_list = result.scalars().all()
    if not chats_list:
        return []
    return chats_list


async def check_existing_chat(user: user_dependency, db: db_dependency, chat_id: int):
    query = (
        select(Chat)
        .options(joinedload(Chat.user), joinedload(Chat.messages))
        .where(Chat.user_id == user.get("id"), Chat.id == chat_id)
    )

    result = await db.execute(query)

    chat = result.scalars().first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )
    chat.messages.sort(key=lambda m: m.created_at)
    return chat
