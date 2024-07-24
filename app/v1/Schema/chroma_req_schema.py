from typing import Optional
from pydantic import BaseModel

class AdditionalInfo(BaseModel):
    subject: str = None
    body: str = None

class langchain_llama_llm(BaseModel):
    prompt: str
    email_part : str = "email_body"
    max_token: int = 500
    llm: str
    collection_name : str
    voice_and_tone : str = None
    additional_info : Optional[AdditionalInfo] = None