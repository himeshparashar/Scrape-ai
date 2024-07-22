
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, SeleniumURLLoader, PyPDFLoader
from fastapi.exceptions import HTTPException
import uuid
import os
from langchain_community.docstore.document import Document


async def text_splitter(documents : str, chunk_size : int = 1000, chunk_overlap : int = 0):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    return docs


async def url_text_loader(urls : list[str]):
    loader = SeleniumURLLoader(urls=urls)
    data = loader.load()
    docs = await text_splitter(data)
    return docs

async def pdf_text_loader(pdf_path : str):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    docs = await text_splitter(documents)
    return docs

async def text_loader(text : str, chunk_size : int = 1000, chunk_overlap : int = 0):
    try:
        if not text:
            raise HTTPException(status_code=400, detail="Text should not be empty.")
        ROOT_DIR = os.path.abspath(os.curdir)
        temp_folder = os.path.join(ROOT_DIR, "text_vector")

        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        if os.path.exists(temp_folder) and os.path.isdir(temp_folder):
            current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            file_name = f"{str(uuid.uuid4())}__{current_time}.txt"
            file_path = f"{temp_folder}\{file_name}"
            if not os.path.exists(file_path) and not os.path.isfile(file_path):
                with open(file_path, 'w', encoding="utf-8") as f:
                    f.write(text)
            loader = TextLoader(file_path, autodetect_encoding=True)
            documents = loader.load()
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
            docs = await text_splitter(documents)
            return docs
        else:
            return []
    except Exception as e:
        print(e)
        return []


async def process_text(docs : list[str], collection_name : str)->(list, list, list):
    v_documents = []
    v_metadata = []
    v_ids = []
    # v_embedd = []

    for doc in docs:
        v_documents.append(doc.page_content)
        v_metadata.append({"title":collection_name, "source" : doc.metadata['source']})
        v_ids.append(str(uuid.uuid4()))
        # v_embedd.append(openai_ef(doc.page_content))

    return v_documents, v_metadata, v_ids