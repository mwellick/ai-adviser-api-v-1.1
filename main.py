from fastapi import FastAPI

app = FastAPI(
    title="AI Adviser"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
