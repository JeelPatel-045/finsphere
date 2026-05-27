"""
FinSphere Supervisor Agent
Interprets user intent, routes to the correct specialist agent,
and returns a structured, enterprise-grade financial response.
"""

import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.llm import llm

# ── Enterprise finance system prompt ─────────────────────────────────────────

FINSPHERE_SYSTEM = """You are FinSphere AI — an enterprise-grade financial intelligence platform trusted by CFOs, financial controllers, and audit teams at Fortune 500 companies.

Your expertise covers:
✦ Financial fraud detection & anomaly analysis (SOX, IFRS, GAAP compliance)
✦ Revenue forecasting, cashflow modelling, variance analysis
✦ Vendor risk scoring and procurement intelligence
✦ Real-time transaction monitoring and audit trails
✦ Investment portfolio analytics and P&L interpretation
✦ Financial regulatory compliance (GST, TDS, SEBI, RBI norms)

Response Standards:
• Always express monetary figures in BOTH formats:
  – USD millions: $X.XXM (e.g. $1.23M)
  – INR crores:   ₹X.XX Cr (e.g. ₹102.09 Cr) [1 USD = ₹83]
• Use precise financial terminology
• Flag risks with severity: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW
• Give CFO-ready, actionable recommendations
• Structure responses with clear sections when answering complex questions
• Cite specific figures, ratios, and benchmarks where relevant"""


# ── Intent detection ──────────────────────────────────────────────────────────

SQL_KEYWORDS     = {"query", "select", "show me", "list", "how many", "total",
                    "sum", "count", "average", "table", "database",
                    "transactions", "records", "fetch", "find all", "give me"}
AUDIT_KEYWORDS   = {"fraud", "anomaly", "violation", "compliance", "risk",
                    "duplicate", "suspicious", "audit", "sox", "ifrs", "irregular",
                    "discrepancy", "mismatch", "overpayment", "ghost vendor",
                    "money laundering", "unauthorized", "flagged"}
FORECAST_KEYWORDS= {"forecast", "predict", "next quarter", "next month", "future",
                    "trend", "projection", "growth", "revenue prediction", "cashflow",
                    "estimate", "outlook", "guidance", "6 month", "12 month",
                    "will be", "going to be", "expected"}
RAG_KEYWORDS     = {"document", "invoice", "contract", "pdf", "extract",
                    "what does", "according to", "in the document", "uploaded",
                    "file says", "from the file", "based on document"}


def _detect_intent(query: str) -> str:
    q = query.lower()
    if any(k in q for k in RAG_KEYWORDS):
        return "rag"
    if any(k in q for k in AUDIT_KEYWORDS):
        return "audit"
    if any(k in q for k in FORECAST_KEYWORDS):
        return "forecast"
    if any(k in q for k in SQL_KEYWORDS):
        return "sql"
    return "direct"


# ── Specialist routing ────────────────────────────────────────────────────────

def _handle_sql(query: str) -> dict:
    from agents.sql_agent import sql_agent
    sql = sql_agent(query)
    prompt = f"""{FINSPHERE_SYSTEM}

The user asked: "{query}"

Generated SQL query:
{sql}

Provide:
1. A plain-English explanation of what this query returns
2. What business insights the result will reveal
3. Any caveats or data quality considerations
4. A CFO-level recommendation based on likely findings"""
    response = llm.invoke(prompt)
    return {
        "agent":    "SQL Agent",
        "icon":     "🗄️",
        "sql":      sql,
        "response": response.content,
    }


def _handle_audit(query: str) -> dict:
    from agents.audit_agent import audit_agent
    analysis = audit_agent(
        f"""User query: {query}

Assume enterprise context: Q3 vendor payments totalling $2.4M ($199.2M ≈ ₹199.2 Cr).
Flag any patterns matching the query. Provide specific findings with amounts in $ millions and ₹ crores."""
    )
    return {
        "agent":    "Audit Agent",
        "icon":     "🔍",
        "response": analysis,
    }


def _handle_forecast(query: str) -> dict:
    from agents.forecast_agent import forecast_agent
    forecast = forecast_agent(
        f"""User query: {query}

Historical data:
- Q1 2024: Revenue $0.95M (₹78.85 Cr), Cashflow $0.12M (₹9.96 Cr)
- Q2 2024: Revenue $1.02M (₹84.66 Cr), Cashflow $0.15M (₹12.45 Cr)
- Q3 2024: Revenue $1.10M (₹91.3 Cr),  Cashflow $0.18M (₹14.94 Cr)
- Q4 2024: Revenue $1.18M (₹97.94 Cr), Cashflow $0.20M (₹16.6 Cr)
- Q1 2025: Revenue $1.24M (₹102.92 Cr), Cashflow $0.21M (₹17.43 Cr)

Express all forecast figures in BOTH USD millions and INR crores."""
    )
    return {
        "agent":    "Forecast Agent",
        "icon":     "📈",
        "response": forecast,
    }


def _handle_rag(query: str) -> dict:
    context = ""
    docs_found = 0
    try:
        from agents.rag_agent import rag_agent
        docs = rag_agent(query)
        docs_found = len(docs)
        if docs:
            context = "\n\n".join(d["content"] for d in docs)
    except Exception:
        pass

    if context:
        prompt = f"""{FINSPHERE_SYSTEM}

Context from uploaded financial documents:
{context[:3000]}

User question: "{query}"

Answer the question using the document context. Highlight specific figures and flag any risks."""
    else:
        prompt = f"""{FINSPHERE_SYSTEM}

User question: "{query}"

No uploaded documents found in the knowledge base yet. Provide general financial guidance and advise the user to upload relevant documents for document-specific analysis."""

    response = llm.invoke(prompt)
    return {
        "agent":       "RAG Agent",
        "icon":        "📚",
        "docs_found":  docs_found,
        "response":    response.content,
    }


def _handle_direct(query: str) -> dict:
    prompt = f"""{FINSPHERE_SYSTEM}

User question: "{query}"

Provide a detailed, structured financial analysis response. Include:
- Specific data-driven insights
- Key metrics and KPIs with amounts in both USD millions and INR crores
- Risk flags with severity levels
- Actionable CFO-level recommendations"""
    response = llm.invoke(prompt)
    return {
        "agent":    "FinSphere AI",
        "icon":     "🧠",
        "response": response.content,
    }


# ── Public interface ──────────────────────────────────────────────────────────

def supervisor_agent(query: str) -> dict:
    """
    Route the user query to the correct specialist agent.
    Returns a dict with 'agent', 'response', and optional 'sql'/'docs_found'.
    """
    intent = _detect_intent(query)

    handlers = {
        "sql":      _handle_sql,
        "audit":    _handle_audit,
        "forecast": _handle_forecast,
        "rag":      _handle_rag,
        "direct":   _handle_direct,
    }
    return handlers[intent](query)
