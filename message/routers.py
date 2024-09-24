from fastapi import APIRouter, Path, Request, Response
from starlette import status
from dependencies import db_dependency

from .crud import message_create
from .schemas import MessageCreate
from dotenv import load_dotenv

from .utils import generate_guest_response, set_cookie, get_cookie

load_dotenv()

messages_router = APIRouter(
    tags=["messages"]
)

MAX_MESSAGES = 5


@messages_router.post("/chats/{chat_id}/guest/message", status_code=status.HTTP_201_CREATED)
async def create_message_by_guest(
        db: db_dependency,
        request: Request,
        response: Response,
        message: MessageCreate,
        chat_id: int = Path(gt=0),
):
    chat_data_cookies = await get_cookie(request, "guest_chat_data")

    chat_id = chat_data_cookies.get("chat_id")
    theme_id = chat_data_cookies.get("theme_id")

    messages = await get_cookie(request, "guest_messages")

    if not isinstance(messages, list):
        messages = []

    messages.append(
        {
            "content": message.content,
            "chat_id": chat_id,
            "theme_id": theme_id,
            "is_ai_response": False
        }
    )

    if len(messages) > MAX_MESSAGES:
        messages = messages[:MAX_MESSAGES]

    await set_cookie(response, "guest_messages", messages, max_age=1800)

    ai_response = await generate_guest_response(db, messages)
    response_message = {"response": ai_response}

    return response_message


@messages_router.post("/chats/{chat_id}/message", status_code=status.HTTP_201_CREATED)
async def create_message(
        db: db_dependency,
        message: MessageCreate,
        chat_id: int = Path(gt=0)
):
    response = await message_create(db, message, chat_id)

    return response
