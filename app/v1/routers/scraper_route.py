import os
from fastapi import FastAPI, HTTPException, Request, APIRouter
from langchain_openai import OpenAI

from app.v1.Schema.scraper_req_schema import CreateCollectionRequest, WebScrapperReq
from app.v1.helpers.langchian_vector_store import LangChainVectorStore
from app.v1.services.web_scraper import WebScrapper
from app.v1.helpers.text_loader import text_loader, text_splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# from qdrant_client import QdrantClient, VectorParams, Distance, PointStruct

knowledgebase_router = APIRouter(prefix="/knowledgebase")

# client = QdrantClient(
#     url=os.getenv("QDRANT_URL"),
#     api_key=os.getenv("QDRANT_API_KEY"),
#     timeout=500
# )

# openai_client = OpenAI()


@knowledgebase_router.post("/urls")
async def web_knowledge_base(req : WebScrapperReq):
    try:
        webs = WebScrapper()
        web_data = webs._run_scrape_page(req.urls)
        print("##################################################")
        print(web_data)
        print("##################################################")
        web_data_loader = await text_loader(web_data)
        if web_data is not None:
            collection_name = req.collection_name+"_"+req.collection_id
            metadata = {
                "collection_name": collection_name,
                "collection_id": req.collection_id,
                "user_id": req.user_id,
            }
            is_added = await LangChainVectorStore.run_db(
                docs = web_data_loader, 
                collection_name = collection_name,
                metadata=metadata, 

            )
            if is_added == True:
                return {
                    "status": 201,
                    "message": "Knowledgebase added"
                }
            else:
                return {
                    "status": 400,
                    "message": f"Something went wrong. {is_added} "
                }
        return {
            "status": 404,
            "message": "Website has no scrappable pages."
        }
    except Exception as e:
        print(e)
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    



# @knowledgebase_router.post("/create_collection")
# async def create_item(request: CreateCollectionRequest):
#     try:
#         if client.collection_exists(request.collection_name):
#             return f"collection with name '{request.collection_name}' is already present"
#         else:

#             text_splitter = RecursiveCharacterTextSplitter(chunk_size=800,
#                                                            chunk_overlap=400)
#             texts = text_splitter.split_text(texts)

#             result = openai_client.embeddings.create(input=texts, model="text-embedding-3-large")

#             client.create_collection(
#                 request.collection_name,
#                 vectors_config=VectorParams(
#                     size=3072,
#                     distance=Distance.COSINE,
#                 ),
#             )

#             points = [
#                 PointStruct(
#                     id=idx,
#                     vector=data.embedding,
#                     payload={"text": text},
#                 )
#                 for idx, (data, text) in enumerate(zip(result.data, texts))
#             ]

#             client.upsert(request.collection_name, points)

#             return {"message": f"Collection with name {request.collection_name} created successfully"}

#     except Exception as e:
#         return {"message": f"Error while creating collection. The error is: {e}"}