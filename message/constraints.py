from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette import status
from fastapi import HTTPException
from database.models import Message, Chat, SavedMessages
from dependencies import user_dependency, db_dependency


async def check_saved_messages_history(user: user_dependency, db: db_dependency):
    query = select(Message).options(
        joinedload(Message.chat)
    ).join(Chat).where(
        Chat.user_id == user.get("id")
    ).where(Message.is_saved == True)

    result = await db.execute(query)
    saved_chats = result.scalars().all()
    if not saved_chats:
        return []
    return saved_chats


async def check_db_saved_messages(user: user_dependency, db: db_dependency):
    query = select(SavedMessages).where(SavedMessages.user_id == user.get("id"))
    result = await db.execute(query)
    saved = result.scalars().all()
    if not saved:
        raise HTTPException(
            detail="Not found any saved messages",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return saved


async def check_existing_message(user: user_dependency, db: db_dependency, message_id: int):
    query = select(Message).options(
        joinedload(Message.chat).joinedload(Chat.user)
    ).join(Chat).where(
        Chat.user_id == user.get("id")
    ).where(Message.id == message_id)

    result = await db.execute(query)

    message = result.scalars().first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return message


async def check_existing_saved_message(
        user: user_dependency,
        db: db_dependency,
        saved_message_id: int
):
    query = select(SavedMessages).where(
        SavedMessages.user_id == user.get("id")
    ).where(SavedMessages.id == saved_message_id)

    result = await db.execute(query)

    saved_message = result.scalars().first()
    if not saved_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved message not found"
        )
    return saved_message
