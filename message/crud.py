from sqlalchemy import select, and_, desc
from sqlalchemy.orm import joinedload
from dependencies import db_dependency, user_dependency
from database.models import Message, Chat
from chat.constraints import check_existing_chat
from .constraints import check_saved_messages_history, check_existing_message
from .schemas import MessageCreate
from .utils import generate_response


async def message_create(db: db_dependency, message: MessageCreate, chat_id: int):
    message = Message(
        content=message.content,
        chat_id=chat_id

    )
    db.add(message)
    await db.commit()

    response = await generate_response(db, chat_id)

    return response


async def save_or_unsafe_specific_message(
        user: user_dependency,
        save: bool,
        db: db_dependency,
        chat_id: int,
        message_id: int
):
    query = select(Chat).options(joinedload(Chat.user)).where(
        Chat.user_id == user.get("id")
    ).where(Chat.id == chat_id)

    result = await db.execute(query)

    result.scalars().first()

    await check_existing_chat(user, db, chat_id)

    message_query = select(Message).where(
        and_(Message.chat_id == chat_id, Message.id == message_id)
    ).order_by(desc(Message.created_at))

    result = await db.execute(message_query)

    await check_existing_message(user, db, message_id)

    message = result.scalars().first()

    message.is_saved = save

    if message.is_ai_response:
        previous_message_query = select(Message).where(
            and_(
                Message.chat_id == chat_id,
                Message.created_at < message.created_at,
                Message.is_ai_response == False  #
            )
        ).order_by(desc(Message.created_at))

        result = await db.execute(previous_message_query)
        previous_message = result.scalars().first()

        if previous_message:
            previous_message.is_saved = save

    await db.commit()
    return None


async def get_saved_messages_list(user: user_dependency, db: db_dependency):
    query = select(Message).options(joinedload(Message.chat)).join(Chat).where(
        Chat.user_id == user.get("id")
    ).where(Message.is_saved == True)

    result = await db.execute(query)

    await check_saved_messages_history(user, db)

    saved_chats = result.scalars().all()
    return saved_chats
