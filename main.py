from fastapi import FastAPI
from user_auth.routers import router

app = FastAPI(
    title="AI Adviser"
)
app.include_router(router)
