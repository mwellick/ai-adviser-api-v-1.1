import json
import os
from openai import AsyncOpenAI, AsyncStream
from fastapi import Request, Response
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionChunk
from sqlalchemy import select, asc
from sqlalchemy.orm import joinedload
from database.models import Message, Theme
from dependencies import db_dependency
from database.models import Chat

load_dotenv()

OPEN_AI_KEY = os.environ.get("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPEN_AI_KEY)


async def generate_response(db: db_dependency, chat_id: int):
    query = select(Message).where(Message.chat_id == chat_id).order_by(asc(Message.created_at))
    result = await db.execute(query)
    all_messages = result.scalars().all()

    query_chat = select(Chat).options(joinedload(Chat.theme)).where(Chat.id == chat_id)
    res = await db.execute(query_chat)

    chat = res.scalars().first()

    ai_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Respond in Markdown format."
        }
    ]

    for message in all_messages:
        role = "user" if not message.is_ai_response else "assistant"
        ai_messages.append({"role": role, "content": message.content})

    ai_messages.append({"role": "user", "content": chat.theme.name})

    ai_response = await client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=1,
        max_tokens=250,
        frequency_penalty=0.7,
        presence_penalty=1.0,
        top_p=0.8,
        stream=True,
        messages=ai_messages
    )

    processed_response = await process_ai_response(ai_response)

    ai_message = Message(
        content=processed_response,
        chat_id=chat_id,
        is_ai_response=True
    )
    db.add(ai_message)
    await db.commit()

    return ai_message


async def generate_guest_response(db: db_dependency, messages: list):
    theme_id = messages[-1]["theme_id"]

    query = select(Theme).where(Theme.id == theme_id)
    result = await db.execute(query)
    theme = result.scalars().first()

    ai_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Respond in Markdown format."
        }
    ]

    for message in messages:
        role = "user" if not message["is_ai_response"] else "assistant"
        ai_messages.append({"role": role, "content": message["content"]})

    if theme is not None:
        ai_messages.append(
            {
                "role": "user",
                "content": f"Theme: {theme.name}"
            }
        )
    else:
        print("Theme not found!")

    ai_response = await client.chat.completions.create(
        model="gpt-4",
        temperature=0.7,
        max_tokens=200,
        frequency_penalty=0.5,
        presence_penalty=0.7,
        top_p=0.3,
        stream=True,
        messages=ai_messages
    )

    return await process_ai_response(ai_response)


async def process_ai_response(ai_response: AsyncStream[ChatCompletionChunk]):
    ai_res = ""
    try:
        if ai_response:
            async for chunk in ai_response:
                if chunk.choices[0].delta.content is not None:
                    ai_res += chunk.choices[0].delta.content
    except Exception:
        raise Exception("An unexpected error occurred during generating a response.")

    return ai_res.strip()


async def get_cookie(request: Request, cookie_name: str):
    cookie_data = request.cookies.get(cookie_name)
    if cookie_data:
        try:
            return json.loads(cookie_data)
        except json.JSONDecodeError:
            return {}
    return {}


async def set_cookie(response: Response, cookie_name: str, data, max_age=0):
    response.set_cookie(
        key=cookie_name,
        value=json.dumps(data),
        max_age=max_age,
        httponly=True,
        secure=False
    )
