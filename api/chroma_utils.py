from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List
import aiofiles
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
# print(openai_api_key)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
embedding_function = OpenAIEmbeddings(api_key = openai_api_key)
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

async def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".html"):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    documents = await asyncio.get_event_loop().run_in_executor(None, loader.load)

    return await asyncio.get_event_loop().run_in_executor(None, text_splitter.split_documents, documents)

async def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = await load_and_split_document(file_path)
        for split in splits:
            split.metadata["file_id"] = file_id

        await asyncio.get_event_loop().run_in_executor(None, vectorstore.add_documents, splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    
async def delete_doc_from_chroma(file_id: int) -> bool:
    try:
        docs = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: vectorstore.get(where={"file_id": file_id})
        )
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: vectorstore._collection.delete(where={"file_id": file_id})
        )
        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False