import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from app.v1.api import v1_router

load_dotenv()
app = FastAPI()


app.get("/")
async def root(request: Request):
    return {"message": os.environ.get("OPENAI_API_KEY")}


app.include_router(v1_router)