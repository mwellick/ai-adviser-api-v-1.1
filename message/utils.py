import json
import os
from openai import AsyncOpenAI, AsyncStream
from fastapi import Request, Response
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionChunk
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from database.models import Message
from dependencies import db_dependency
from database.models import Chat

load_dotenv()

OPEN_AI_KEY = os.environ.get("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPEN_AI_KEY)


async def generate_response(db: db_dependency, chat_id: int):
    query = select(Message).where(Message.chat_id == chat_id).order_by(desc(Message.created_at)).limit(1)
    result = await db.execute(query)
    last_message = result.scalar_one_or_none()
    query_chat = select(Chat).options(joinedload(Chat.theme)).where(Chat.id == chat_id)
    res = await db.execute(query_chat)
    chat = res.scalars().first()

    ai_response = await client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=1,
        max_tokens=350,
        frequency_penalty=0.7,
        presence_penalty=1.0,
        top_p=0.8,
        stream=True,
        messages=[
            {"role": "system",
             "content": last_message.content
             },
            {"role": "user",
             "content": chat.theme.name
             }

        ]
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


async def generate_guest_response(messages: list):
    user_message = messages[-1]["content"] if messages else ""

    ai_response = await client.chat.completions.create(
        model="gpt-4",
        temperature=0.7,
        max_tokens=250,
        frequency_penalty=0.5,
        presence_penalty=0.7,
        top_p=0.3,
        stream=True,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
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
    return json.loads(cookie_data) if cookie_data else []


async def set_cookie(response: Response, cookie_name: str, data, max_age=0):
    response.set_cookie(
        key=cookie_name,
        value=json.dumps(data),
        max_age=max_age,
        httponly=True,
        secure=True
    )
