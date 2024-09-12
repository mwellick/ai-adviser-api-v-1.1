import os
from fastapi import APIRouter, Path
from openai import AsyncOpenAI
from dependencies import db_dependency
from starlette import status

from .crud import message_create
from .schemas import MessageCreate
from dotenv import load_dotenv

load_dotenv()

messages_router = APIRouter(
    prefix="/chat",
    tags=["messages"]
)

OPEN_AI_KEY = os.environ.get("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPEN_AI_KEY)


@messages_router.post("/{chat_id}/message", status_code=status.HTTP_201_CREATED)
async def create_message(
        db: db_dependency,
        message: MessageCreate,
        chat_id: int = Path(gt=0)
):
    response = await message_create(db, message, chat_id)

    return response
