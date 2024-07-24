from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from app.v1.Schema.chroma_req_schema import langchain_llama_llm
from app.v1.helpers.langchian_vector_store import LangChainVectorStore


emailTemplate_router = APIRouter(prefix="/email_template")


@emailTemplate_router.post("/email_template")
async def langchain_chroma_pdf_collection(req :langchain_llama_llm):
    try:

        res = await LangChainVectorStore.langchain_openai_llm_with_reply(
            query=req.prompt,
            collection_name=req.collection_name,
            email_part = req.email_part,
            max_token = req.max_token,
            voice_and_tone = req.voice_and_tone,
            additional_info = req.additional_info
        )
        return {
            "status" : 200,
            "message" : "Success",
            "data" : res
        }
    except Exception as e:
        print(e)
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)