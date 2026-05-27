from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


def get_vectorstore():

    embeddings = OpenAIEmbeddings()

    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    return db