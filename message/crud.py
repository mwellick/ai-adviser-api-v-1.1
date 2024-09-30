from datetime import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import joinedload
from dependencies import db_dependency, user_dependency
from database.models import Message, Chat, SavedMessages
from chat.constraints import check_existing_chat
from .constraints import check_saved_messages_history, check_existing_saved_message, check_db_saved_messages, \
    check_existing_message
from .schemas import MessageCreate, MessageRead, SavedMessageRead
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


async def get_message(db: db_dependency, chat_id: int, message_id: int):
    message_query = select(Message).where(
        and_(Message.chat_id == chat_id, Message.id == message_id)
    ).order_by(desc(Message.created_at))

    result = await db.execute(message_query)
    return result.scalars().first()


async def get_previous_message(db: db_dependency, message_created_at: datetime, chat_id: int):
    previous_message_query = select(Message).where(
        and_(
            Message.chat_id == chat_id,
            Message.created_at < message_created_at,
            Message.is_ai_response == False  #
        )
    ).order_by(desc(Message.created_at))

    result = await db.execute(previous_message_query)
    return result.scalars().first()


async def get_existing_saved_message(
        db: db_dependency,
        user: user_dependency,
        user_request: str,
        ai_response: str
):
    saved_message_query = select(SavedMessages).where(
        and_(
            SavedMessages.user_id == user.get("id"),
            SavedMessages.user_request == user_request,
            SavedMessages.ai_response == ai_response
        )
    )
    result = await db.execute(saved_message_query)
    return result.scalars().first()


async def save_of_delete_from_db(
        db: db_dependency,
        user: user_dependency,
        user_request: str,
        ai_response: str,
        save: bool

):
    if save is True:
        save_to_db = SavedMessages(
            user_request=user_request,
            ai_response=ai_response,
            user_id=user.get("id")
        )
        db.add(save_to_db)

    elif save is False:
        saved_message_query = await get_existing_saved_message(
            db,
            user,
            user_request,
            ai_response
        )
        if saved_message_query:
            await db.delete(saved_message_query)

    await db.commit()
    return None


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
    await check_existing_message(user, db, message_id)

    message = await get_message(db, chat_id, message_id)

    message.is_saved = save

    if message.is_ai_response:
        previous_message = await get_previous_message(db, message.created_at, chat_id)

        if previous_message:
            previous_message.is_saved = save

        saved_messages_query = await get_existing_saved_message(
            db,
            user,
            previous_message.content,
            message.content
        )
        if save is True:
            if saved_messages_query is None:
                await save_of_delete_from_db(
                    db,
                    user,
                    previous_message.content,
                    message.content,
                    True
                )
        elif save is False:
            if saved_messages_query is not None:
                await save_of_delete_from_db(
                    db,
                    user,
                    previous_message.content,
                    message.content,
                    False
                )
    return None


async def get_saved_messages_list(user: user_dependency, db: db_dependency):
    query = select(Message).options(joinedload(Message.chat)).join(Chat).where(
        Chat.user_id == user.get("id")
    ).where(Message.is_saved == True)

    query_result = await db.execute(query)
    saved_messages = query_result.scalars().all()

    if saved_messages:
        return [
            MessageRead.model_validate(
                saved, from_attributes=True
            ) for saved in saved_messages
        ]

    saved_message_query = select(SavedMessages).where(
        SavedMessages.user_id == user.get("id")
    )
    saved_messages_query = await db.execute(saved_message_query)
    saved_messages_result = saved_messages_query.scalars().all()
    if saved_messages_result:
        return [
            SavedMessageRead.model_validate(
                saved, from_attributes=True
            ) for saved in saved_messages_result
        ]

    await check_saved_messages_history(user, db)

    return []


async def delete_specific_saved_message(
        user: user_dependency,
        db: db_dependency,
        saved_message_id: int
):
    query = select(SavedMessages).where(
        SavedMessages.user_id == user.get("id")
    ).where(SavedMessages.id == saved_message_id)

    result = await db.execute(query)

    saved_message_to_delete = result.scalars().first()

    await check_existing_saved_message(user, db, saved_message_id)
    await db.delete(saved_message_to_delete)
    await db.commit()
    return None


async def delete_saved_messages(
        user: user_dependency,
        db: db_dependency
):
    query = select(SavedMessages).where(
        SavedMessages.user_id == user.get("id")
    )

    result = await db.execute(query)
    delete_all = result.scalars().all()

    await check_db_saved_messages(user, db)

    for saved_message in delete_all:
        await db.delete(saved_message)

    await db.commit()
