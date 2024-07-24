
from app.v1.routers.scraper_route import knowledgebase_router
from app.v1.routers.email_template import emailTemplate_router
from fastapi import APIRouter


v1_router = APIRouter(prefix="/v1")
v1_router.include_router(knowledgebase_router, tags=['Knowlwdge Base'])
v1_router.include_router(emailTemplate_router, tags=['Email Template'])
