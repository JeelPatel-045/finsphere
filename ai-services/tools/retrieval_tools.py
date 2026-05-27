from vectorstore.chroma_manager import get_vectorstore


def retrieve_documents(query: str):

    db = get_vectorstore()

    docs = db.similarity_search(query, k=3)

    return [doc.page_content for doc in docs]