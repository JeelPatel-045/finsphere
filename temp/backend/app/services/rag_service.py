import chromadb
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="finance_docs")


def ask_finance_question(question: str):
    results = collection.query(query_texts=[question], n_results=3)

    context = "\n".join(results["documents"][0]) if results["documents"] else ""

    prompt = f"""
    You are a finance AI assistant.

    Context:
    {context}

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content