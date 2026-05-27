import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory
from app.core.config import settings

# ── Clients ───────────────────────────────────────────────────────────────────

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
llm = get_llm()

chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
collection    = chroma_client.get_or_create_collection(name="finance_docs")

# ── Service function ──────────────────────────────────────────────────────────

def ask_finance_question(question: str) -> str:
    """Retrieve relevant document context and answer a finance question."""
    results = collection.query(query_texts=[question], n_results=3)
    context = (
        "\n".join(results["documents"][0])
        if results.get("documents")
        else "No relevant documents found in the knowledge base."
    )

    prompt = (
        "You are a finance AI assistant with access to the company knowledge base.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )
    response = llm.invoke(prompt)
    return response.content
