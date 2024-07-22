from pydantic import BaseModel

class WebScrapperReq(BaseModel):
    urls: str
    collection_name : str
    collection_id : str
    user_id : str
    tags : list[str]


class CreateCollectionRequest(BaseModel):
    collection_name: str
    text: str
    file_path: str = None