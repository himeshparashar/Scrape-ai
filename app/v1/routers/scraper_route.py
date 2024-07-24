
from fastapi import HTTPException, APIRouter

from app.v1.Schema.scraper_req_schema import WebScrapperReq
from app.v1.helpers.langchian_vector_store import LangChainVectorStore
from app.v1.services.web_scraper import WebScrapper
from app.v1.helpers.text_loader import text_loader

knowledgebase_router = APIRouter(prefix="/knowledgebase")


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
            print("**********************")
            print(is_added)
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
