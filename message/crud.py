from dependencies import db_dependency
from database.models import Message
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
