import json

from fastapi import APIRouter, Path, Request, Response

from dependencies import db_dependency

from .crud import message_create
from .schemas import MessageCreate
from dotenv import load_dotenv

from .utils import generate_guest_response

load_dotenv()

messages_router = APIRouter(
    prefix="/chat",
    tags=["messages"]
)

MAX_MESSAGES = 10


@messages_router.post("/{chat_id}/message")
async def create_message(
        db: db_dependency,
        request: Request,
        response: Response,
        message: MessageCreate,
        chat_id: int = Path(gt=0)
):
    chat_data_cookies = request.cookies.get("guest_chat_data")
    cookie_chat_id = ""
    if chat_data_cookies is not None:
        chat_data = json.loads(chat_data_cookies)
        cookie_chat_id = chat_data.get("chat_id")

    if cookie_chat_id is None:
        response = await message_create(db, message, chat_id)
    else:
        chat_data_cookies = request.cookies.get("guest_chat_data")
        if chat_data_cookies:
            chat_data = json.loads(chat_data_cookies)
            chat_id = chat_data.get("chat_id")
            theme_id = chat_data.get("theme_id")

    messages_cookies = request.cookies.get("guest_messages")
    messages = json.loads(messages_cookies) if messages_cookies else []

    messages.append(
        {
            "content": message.content,
            "chat_id": chat_id,
            "theme_id": theme_id
        }
    )
    response.set_cookie(
        key="guest_messages",
        value=json.dumps(messages),
        max_age=0,
        httponly=True,
        secure=True
    )

    ai_response = await generate_guest_response(messages)
    response_message = {"response": ai_response}

    return response_message
