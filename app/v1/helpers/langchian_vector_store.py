
from fastapi import HTTPException
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from langchain_qdrant import QdrantVectorStore, Qdrant


print(os.environ.get('OPENAI_API_KEY'))
print("############################################")


class LangChainVectorStore:
    
    
    @classmethod
    async def run_db(self, docs : list, collection_name : str, metadata:dict):
        try:
            open_embeddings = OpenAIEmbeddings(api_key=os.environ.get('OPENAI_API_KEY'), model="text-embedding-ada-002", max_retries=2) 

            
            url = "<---qdrant url here --->"
            qdrant = QdrantVectorStore.from_documents(
                docs,
                open_embeddings,
                url=url,
                prefer_grpc=True,
                api_key=os.environ.get('QDRANT_API_KEY'),
                collection_name="my_documents",
            )


            qdrant = QdrantVectorStore.from_existing_collection(
                embeddings=open_embeddings,
                collection_name="my_documents",
                url="http://localhost:6333",
            )
            return True
        except Exception as e:
            error_message = f"{str(e)}"
            return error_message
        
    @classmethod
    async def langchain_similar_doc_search(self, collection_name : str, query : str):
        vector_db = Chroma(
            persist_directory=self.db_dir, 
            embedding_function=self.open_embeddings, 
            collection_name=collection_name,            
        )
        documents = vector_db.similarity_search_by_vector_with_relevance_scores(
            self.open_embeddings.embed_query(query),
            k = 5
        )
        return documents
    

