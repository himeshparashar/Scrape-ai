
from fastapi import HTTPException
from langchain_chroma import Chroma
from langchain_community.vectorstores import Chroma
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from nltk import word_tokenize
from nltk.corpus import stopwords
import nltk
import string
from app.v1.Schema.chroma_req_schema import AdditionalInfo
from dotenv import load_dotenv
import uuid

load_dotenv()


class LangChainVectorStore:
    db = None
    ROOT_DIR = os.path.abspath(os.curdir)
    db_dir = os.path.join(ROOT_DIR, "chroma_db")
    open_embeddings = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"), model="text-embedding-ada-002",
                                       max_retries=2)

    @classmethod
    async def uu_ids(self, docs : list) ->list:
        # Create a list of ids for each document based on the content
        ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in docs]
        return ids

    @classmethod
    async def unique_ids(self, docs : list) ->list:
        # Create a list of unique ids for each document based on the content
        ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in docs]
        unique_ids = list(set(ids))
        return unique_ids

    @classmethod
    async def unique_docs(self, docs : list) ->list:
        # Ensure that only docs that correspond to unique ids are kept and that only one of the duplicate ids is kept
        ids = await self.uu_ids(docs=docs)
        seen_ids = set()
        unique_docs = [doc for doc, id in zip(docs, ids) if id not in seen_ids and (seen_ids.add(id) or True)]
        return unique_docs
    
    @classmethod
    async def run_db(self, docs : list, collection_name : str, metadata:dict):
        try:
            unique_docs = await self.unique_docs(docs=docs)
            unique_ids = await self.unique_ids(docs=docs)
            db = Chroma.from_documents(
                unique_docs,
                self.open_embeddings,
                ids=unique_ids,
                persist_directory=self.db_dir,
                collection_name=collection_name,
                collection_metadata=metadata
            )
            db.persist()
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

    @classmethod
    async def langchain_openai_llm_with_reply(
            self,
            query: str,
            collection_name: str,
            email_part: str,
            voice_and_tone: str,
            additional_info: AdditionalInfo,
            max_token: int = 2000,
    ):
        try:
            nltk.download('stopwords')
            nltk.download('punkt')
            stop = set(stopwords.words('english') + list(string.punctuation))
            tags = [i for i in word_tokenize(query.lower()) if i not in stop]
            raw_query = ",".join(tags)

            llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-3.5-turbo",
                api_key=os.environ.get("OPENAI_API_KEY"),
                max_tokens=1000,
                cache=False
            )

            context_data_kn = await LangChainVectorStore.langchain_similar_doc_search(
                collection_name=collection_name,
                query=raw_query,
            )
            context_data = ""
            if context_data_kn:
                for r in context_data_kn:
                    p, s = r
                    context_data += p.page_content + "\n"

            if email_part == "email_body":
                if additional_info is None:
                    context_data += context_data + "\n" + voice_and_tone
                    print("****************inside none")
                    template = """
                       {query}\n
                       Context:\n
                       {context_data}
                       """
                else:
                    print("****************outside none")
                    context_data = context_data + "\n" + "\n" + additional_info.body
                    print("****************inside none")
                    template = """
                       {query}\n
                       customer_reply:\n
                       {context_data}
                       """
            else:
                template = """
                   Imagine you are an email writer for a marketing campaign strategist. 
                   You have been tasked with creating an attention-grabbing subject line. 
                   Your goal is to generate excitement and curiosity among recipients while conveying the unique selling points of the product.
                   Craft a subject line that will captivate the audience and increase open rates.
                   Lenght: {max_token}\n
                   user_query:{query}.\n
                   context_data:\n
                   {context_data}
                   """

            prompt = PromptTemplate(template=template, input_variables=["query", "max_token", "context_data"])
            llm_chain = LLMChain(prompt=prompt, llm=llm)
            max_token = llm_chain._get_num_tokens(template)
            if max_token > 4000:
                raise HTTPException(status_code=400, detail="Token limit exceeded.")
            res = llm_chain.run(query=query, max_token=max_token, context_data=context_data)
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Sorry, no match found for your query")
    

