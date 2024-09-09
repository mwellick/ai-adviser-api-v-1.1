from fastapi import APIRouter, Path
from dependencies import db_dependency
from starlette import status
from database.models import Message
from .schemas import MessageCreate

messages_router = APIRouter(
    prefix="/chat",
    tags=["messages"]
)


@messages_router.post("/{chat_id}/message", status_code=status.HTTP_201_CREATED)
async def create_message(
        db: db_dependency,
        message: MessageCreate,
        chat_id: int = Path(gt=0)
):
    message = Message(
        content=message.content,
        chat_id=chat_id
    )

    db.add(message)
    await db.commit()
    return message
