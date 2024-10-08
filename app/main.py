import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from app.v1.api import v1_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.get("/")
async def root(request: Request):
    return {"message": os.environ.get("OPENAI_API_KEY")}

app.include_router(v1_router)