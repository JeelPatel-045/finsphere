import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

embeddings   = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore  = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings,
)


def rag_agent(query: str) -> list:
    """Retrieve the top-k most relevant finance documents for the given query."""
    docs = vectorstore.similarity_search(query, k=4)
    return [{"content": d.page_content, "metadata": d.metadata} for d in docs]
