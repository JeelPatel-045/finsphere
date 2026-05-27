"""
FinSphere Chat Service
Answers questions based on the uploaded document context.
When no document is uploaded, gives general financial guidance.
"""

import os
import json
import re
import httpx

from langchain_core.messages import HumanMessage

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
llm = get_llm(temperature=0.2, max_tokens=2048)

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"


# ── Load document context ─────────────────────────────────────────────────────

def _load_doc_context() -> dict | None:
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _format_context_for_prompt(ctx: dict) -> str:
    """Convert document context into a clear prompt section."""
    lines = []
    lines.append(f"=== UPLOADED DOCUMENT ===")
    lines.append(f"File: {ctx.get('filename', 'unknown')}")
    lines.append(f"Type: {ctx.get('document_type', 'unknown').replace('_', ' ').title()}")
    if ctx.get("company_name"):
        lines.append(f"Company: {ctx['company_name']}")
    if ctx.get("period"):
        lines.append(f"Period: {ctx['period']}")
    if ctx.get("summary"):
        lines.append(f"Summary: {ctx['summary']}")

    # Key metrics
    metrics = ctx.get("key_metrics", [])
    if metrics:
        lines.append("\nKEY METRICS:")
        for m in metrics:
            val = m.get("value", "")
            inr = m.get("value_inr", "")
            chg = m.get("change", "")
            label = m.get("label", "")
            line = f"  • {label}: {val}"
            if inr:  line += f" (≈ {inr})"
            if chg:  line += f" [{chg}]"
            lines.append(line)

    # All extracted data
    all_data = ctx.get("all_extracted_data", {})
    if all_data:
        lines.append("\nALL EXTRACTED FIELDS:")
        for k, v in list(all_data.items())[:30]:
            if v and v != "N/A":
                lines.append(f"  {k}: {v}")

    # Full raw text (most important — LLM can reference actual numbers)
    raw = ctx.get("raw_text", "")
    if raw and len(raw) > 50:
        lines.append(f"\nFULL DOCUMENT TEXT:")
        lines.append(raw[:4000])

    return "\n".join(lines)


# ── Intent detection ──────────────────────────────────────────────────────────

_AUDIT_KW    = {"fraud","duplicate","compliance","risk","violation","suspicious","sox","irregular","unauthorized","anomaly"}
_FORECAST_KW = {"forecast","predict","next","future","projection","trend","growth","estimate","outlook"}
_SQL_KW      = {"query","select","show me","list","how many","total","sum","count","table","records","database","fetch"}

def _detect_intent(msg: str) -> str:
    m = msg.lower()
    if any(k in m for k in _AUDIT_KW):    return "audit"
    if any(k in m for k in _FORECAST_KW): return "forecast"
    if any(k in m for k in _SQL_KW):      return "sql"
    return "general"


# ── Prompt builders ────────────────────────────────────────────────────────────

def _build_doc_prompt(message: str, ctx: dict, intent: str) -> str:
    doc_section = _format_context_for_prompt(ctx)
    filename    = ctx.get("filename", "the document")
    doc_type    = ctx.get("document_type", "financial document").replace("_", " ")
    agent       = ctx.get("agent", {}).get("name", "FinSphere AI")

    STYLE = """You are FinSphere AI — a friendly, expert financial analyst helping a user understand their financial document.

COMMUNICATION STYLE:
✦ Use plain English — explain any financial terms you use
✦ Be specific — reference actual numbers from the document
✦ Use bullet points for lists
✦ Give amounts in BOTH: USD millions ($X.XXM) AND INR crores (₹X.XX Cr) [1 USD = ₹83]
✦ Highlight what's GOOD 🟢, what's CONCERNING 🟡, and what's CRITICAL 🔴
✦ If something isn't in the document, say so clearly
✦ End with 1 actionable recommendation when relevant"""

    if intent == "audit":
        instruction = f"""The user is asking about risks, fraud, or compliance issues.
Check the document for: duplicate entries, unusual amounts, missing data, compliance red flags.
Give specific examples with actual figures from the document."""
    elif intent == "forecast":
        instruction = f"""The user wants a forecast or trend analysis.
Based on the historical figures in the document, provide forward-looking projections.
Be clear about what is actual data vs AI projection."""
    elif intent == "sql":
        instruction = f"""The user wants to query or analyse specific data from the document.
Extract and present the requested data in a clear table or list format."""
    else:
        instruction = f"""Answer the question directly from the document data.
Reference specific figures, dates, and line items from the document."""

    return f"""{STYLE}

{doc_section}

Active Agent: {agent}
Document: {filename} ({doc_type})

Instruction: {instruction}

User question: "{message}"

Answer based SPECIFICALLY on the above document data:"""


def _build_general_prompt(message: str, intent: str) -> str:
    STYLE = """You are FinSphere AI — a friendly, expert financial analyst.

COMMUNICATION STYLE:
✦ Use plain, simple English
✦ Explain financial terms when you use them
✦ Give amounts in USD millions ($X.XXM) AND INR crores (₹X.XX Cr)
✦ Flag issues as: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 OK
✦ Be specific with numbers and percentages
✦ End with 1 practical action step"""

    NOTE = """⚠️ No financial document is currently uploaded.
Providing general financial guidance based on industry knowledge.
Upload a PDF, CSV, or Excel file for analysis specific to your data."""

    if intent == "audit":
        guidance = "Provide general guidance on fraud detection, compliance, and financial audit best practices."
    elif intent == "forecast":
        guidance = "Provide general financial forecasting methodology and industry benchmarks."
    elif intent == "sql":
        guidance = "Describe what financial data would typically be in a database and how to query it."
    else:
        guidance = "Answer the financial question with general best-practice guidance."

    return f"""{STYLE}

{NOTE}

{guidance}

User question: "{message}"

Answer:"""


# ── AI-service proxy ───────────────────────────────────────────────────────────

def _try_ai_service(message: str) -> str | None:
    try:
        url = f"{settings.AI_SERVICE_URL}/chat"
        with httpx.Client(timeout=20) as client:
            resp = client.post(url, json={"message": message})
            resp.raise_for_status()
            data = resp.json()
            # ai-service returns {agent, response, ...}
            agent = data.get("agent", "FinSphere AI")
            reply = data.get("response", "")
            if reply:
                return f"**[{agent}]**\n\n{reply}"
    except Exception:
        pass
    return None


# ── Public interface ───────────────────────────────────────────────────────────

def generate_ai_response(message: str) -> str:
    """
    1. Check for uploaded document context
    2. If document exists → answer FROM the document
    3. If no document → general financial guidance
    """
    intent = _detect_intent(message)
    ctx    = _load_doc_context()

    if ctx and ctx.get("raw_text") or ctx and ctx.get("key_metrics"):
        # ── Document is loaded → answer from document ─────────────────────────
        prompt = _build_doc_prompt(message, ctx, intent)
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            agent    = ctx.get("agent", {}).get("name", "FinSphere AI")
            return f"**[{agent} — {ctx.get('filename', 'Document')}]**\n\n{response.content}"
        except Exception as e:
            err = str(e)[:400]
            # Surface rate-limit / auth errors gracefully
            if "rate_limit" in err.lower() or "429" in err:
                return (
                    f"**[FinSphere AI — Rate Limit]**\n\n"
                    "⚠️ The AI API daily token limit has been reached. "
                    "Please wait a few minutes and try again.\n\n"
                    f"*Technical detail: {err[:200]}*"
                )
            return (
                f"**[FinSphere AI — Error]**\n\n"
                f"⚠️ Could not process your request: {err[:300]}\n\n"
                "Please try again shortly."
            )

    else:
        # ── No document → general guidance ───────────────────────────────────
        prompt = _build_general_prompt(message, intent)
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return (
                f"**[FinSphere AI — No document loaded]**\n\n{response.content}\n\n"
                "---\n💡 *Upload a financial document (PDF, CSV, Excel) on the **Documents** page "
                "to get answers specific to your data.*"
            )
        except Exception as e:
            err = str(e)[:400]
            if "rate_limit" in err.lower() or "429" in err:
                return (
                    "**[FinSphere AI — Rate Limit]**\n\n"
                    "⚠️ The AI API daily token limit has been reached. "
                    "Please wait a few minutes and try again."
                )
            return (
                f"**[FinSphere AI — Error]**\n\n"
                f"⚠️ Could not process your request: {err[:300]}\n\n"
                "Please try again shortly."
            )
