from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload, selectinload
from dependencies import db_dependency, user_dependency
from database.models import Chat
from .schemas import ChatCreate, ChatRead
from .constraints import (
    validate_create_chat_with_available_theme,
    check_chat_history,
    check_existing_chat
)


async def chat_create(db: db_dependency, chat: ChatCreate):
    await validate_create_chat_with_available_theme(db, chat)

    if chat.user_id is None:
        create_chat = Chat(
            theme_id=chat.theme_id,
            user_id=None
        )
        return create_chat

    create_chat = Chat(
        theme_id=chat.theme_id,
        user_id=chat.user_id
    )
    db.add(create_chat)
    await db.commit()
    return create_chat


async def get_chats_list(user: user_dependency, db: db_dependency):
    query = select(Chat).options(joinedload(Chat.user), selectinload(Chat.messages)).where(
        Chat.user_id == user.get("id")
    ).order_by(desc(Chat.created_at))

    result = await db.execute(query)

    chats = result.scalars().all()
    chats_list = [ChatRead.get_first_chat_message(chat) for chat in chats]

    return chats_list


async def get_chat_by_id(user: user_dependency, db: db_dependency, chat_id: int):
    query = select(Chat).options(joinedload(Chat.messages)).where(Chat.id == chat_id)
    result = await db.execute(query)
    await check_existing_chat(user, db, chat_id)
    chat = result.scalars().first()
    return chat


async def delete_all_chat_history(user: user_dependency, db: db_dependency):
    query = select(Chat).options(joinedload(Chat.user)).where(
        Chat.user_id == user.get("id"))
    result = await db.execute(query)
    delete_all = result.scalars().all()

    await check_chat_history(user, db)

    for chat in delete_all:
        await db.delete(chat)

    await db.commit()


async def delete_specific_chat(
        user: user_dependency,
        db: db_dependency,
        chat_id: int
):
    query = select(Chat).options(joinedload(Chat.user)).where(
        Chat.user_id == user.get("id")
    ).where(Chat.id == chat_id)

    result = await db.execute(query)

    chat_to_delete = result.scalars().first()

    await check_existing_chat(user, db, chat_id)
    await db.delete(chat_to_delete)
    await db.commit()

