"""
FinSphere Audit Route — Document-aware risk analysis.

On the first request after a new document upload, calls the LLM to generate
real audit findings from the document content.  Caches the result inside
active_context.json so subsequent calls are instant.
"""

import os
import json
import re

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory

router = APIRouter(prefix="/audit")

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
_llm = get_llm(temperature=0.1, max_tokens=3000)


# ── Fallback data shown when no document is loaded ────────────────────────────

_FALLBACK: dict = {
    "risk_summary": {
        "high_risk_transactions": {
            "count": 0, "amount_usd": "—", "amount_inr": "—",
            "change": "—", "trend": "up",
        },
        "compliance_violations": {"count": 0, "change": "—", "trend": "up"},
        "audit_flags":           {"count": 0, "change": "—", "trend": "down"},
        "ai_risk_score": {"score": 0, "level": "N/A", "change": "—", "trend": "up"},
    },
    "insights": [
        {
            "message":  "No document loaded. Upload a financial document to see AI-powered audit insights.",
            "severity": "info",
        }
    ],
    "transactions": [],
    "violations": [
        {
            "issue":    "No document loaded. Upload a financial document to detect compliance issues.",
            "severity": "Medium",
        }
    ],
    "risk_distribution": [
        {"name": "Critical", "value": 0},
        {"name": "High",     "value": 0},
        {"name": "Medium",   "value": 0},
        {"name": "Low",      "value": 0},
    ],
}


# ── Context helpers ───────────────────────────────────────────────────────────

def _load_ctx() -> dict | None:
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _save_ctx(ctx: dict) -> None:
    os.makedirs(os.path.dirname(ACTIVE_CONTEXT_FILE), exist_ok=True)
    with open(ACTIVE_CONTEXT_FILE, "w") as f:
        json.dump(ctx, f, indent=2)


# ── LLM audit generation ──────────────────────────────────────────────────────

_AUDIT_PROMPT = """\
You are a senior financial auditor AI with deep expertise in Indian corporate law and taxation.
Analyze the document below for risks, fraud indicators, and compliance issues against BOTH
international standards AND Indian government regulations.

=== INDIAN REGULATORY FRAMEWORK TO CHECK ===
CORPORATE LAW:
  - Companies Act 2013 (Sec 129 financial statements, Sec 134 directors report, Sec 177 audit committee,
    Sec 185/186 loans, Sec 188 related party, Schedule II depreciation, Schedule III disclosure format)
  - SEBI LODR 2015 (related party RPT threshold, corporate governance, material disclosures)
  - Ind AS 115 (revenue recognition — 5-step model), Ind AS 116 (leases — right-of-use assets),
    Ind AS 109 (financial instruments — ECL model), Ind AS 36 (impairment), Ind AS 19 (employee benefits)

TAXATION:
  - Income Tax Act 1961 (Sec 194C contractors 1%/2%, Sec 194J professional fees 10%,
    Sec 194I rent 10%, Sec 194H commission 5%, Sec 194Q goods 0.1%, Sec 234B/C advance tax interest)
  - GST Act 2017 (CGST/SGST/IGST classification, Sec 16 ITC eligibility, Sec 17(5) blocked credit,
    e-invoicing above ₹5 Cr, GSTR-9 annual return by 31 Dec, HSN/SAC codes mandatory)
  - Transfer Pricing — Sec 92 arm's length for international transactions

MSME & PAYMENTS:
  - MSMED Act 2006 (45-day payment limit, compound interest at 3x RBI rate for delay)
  - Prevention of Money Laundering Act (PMLA) — suspicious transaction patterns

AUDIT STANDARDS:
  - SA 240 (auditor responsibility regarding fraud)
  - SA 315 (risk assessment procedures)
  - CARO 2020 (audit reporting requirements — loans, fixed assets, inventory, fraud)
=== END FRAMEWORK ===

=== DOCUMENT CONTEXT ===
File      : {filename}
Type      : {doc_type}
Company   : {company}
Summary   : {summary}

Key Metrics:
{metrics}

Extracted Fields:
{extracted}

Document Text (excerpt):
{raw_text}
=== END CONTEXT ===

Return ONLY valid JSON with EXACTLY this structure (no explanation, no markdown):
{{
  "risk_summary": {{
    "high_risk_transactions": {{
      "count": <int>,
      "amount_usd": "$X.XXM",
      "amount_inr": "₹X.XX L",
      "change": "+X",
      "trend": "up"
    }},
    "compliance_violations": {{"count": <int>, "change": "+X", "trend": "up"}},
    "audit_flags":           {{"count": <int>, "change": "-X", "trend": "down"}},
    "ai_risk_score": {{
      "score": <0-100>,
      "level": "Low|Medium|High|Critical",
      "change": "+X",
      "trend": "up"
    }}
  }},
  "insights": [
    {{"message": "Specific finding from this document with actual figures and regulatory reference", "severity": "critical|high|medium|info"}},
    {{"message": "Second specific finding citing applicable Indian law/standard", "severity": "high"}},
    {{"message": "Third finding — tax or GST compliance observation", "severity": "medium"}},
    {{"message": "Fourth finding — general governance or disclosure observation", "severity": "info"}}
  ],
  "transactions": [
    {{
      "id":         "TXN-001",
      "vendor":     "Actual vendor/party from document",
      "amount_usd": "$X.XXM",
      "amount_inr": "₹X.XX L",
      "risk":       "HIGH|MEDIUM|LOW",
      "flag":       "Reason for flagging citing specific section/standard, or null",
      "date":       "YYYY-MM-DD or document period"
    }}
  ],
  "violations": [
    {{
      "issue":      "Specific compliance issue from this document with amounts and context",
      "severity":   "Critical|High|Medium|Low",
      "regulation": "e.g. Ind AS 115, Companies Act 2013 Sec 134, GST Act 2017 Sec 16, Income Tax Act Sec 194J, MSMED Act 2006, SEBI LODR 2015, SA 240"
    }}
  ],
  "risk_distribution": [
    {{"name": "Critical", "value": <0-100>}},
    {{"name": "High",     "value": <0-100>}},
    {{"name": "Medium",   "value": <0-100>}},
    {{"name": "Low",      "value": <0-100>}}
  ]
}}

Rules:
- All findings MUST reference ACTUAL data from the document (real vendors, amounts, dates).
- Amounts in BOTH USD millions ($X.XXM) AND INR lakhs/crores (₹X.XX L or ₹X.XX Cr), 1 USD = ₹83.
- Every violation MUST have a regulation field citing the specific Indian law, section, or standard.
- If the document has no obvious risks, say so in insights rather than inventing fictitious issues.
- risk_distribution values should approximate percentages summing to ~100.
- transactions: list every payment/line-item you can identify from the document.
- violations: base ONLY on what you actually find (missing PO, GST mismatch, duplicates, TDS shortfall, etc.)
- For policy documents: check for outdated standards (Ind AS 18 superseded by Ind AS 115, IAS 17 superseded by Ind AS 116).\
"""


def _gen_audit(ctx: dict) -> dict | None:
    """Return structured audit dict, or None if LLM call fails."""
    prompt = _AUDIT_PROMPT.format(
        filename=ctx.get("filename", "unknown"),
        doc_type=ctx.get("document_type", "unknown").replace("_", " "),
        company=ctx.get("company_name", "Unknown"),
        summary=ctx.get("summary", ""),
        metrics=json.dumps(ctx.get("key_metrics", []), indent=2),
        extracted=json.dumps(ctx.get("all_extracted_data", {}), indent=2)[:2000],
        raw_text=ctx.get("raw_text", "")[:3500],
    )
    try:
        response = _llm.invoke([HumanMessage(content=prompt)])
        content  = response.content.strip()
        if "```" in content:
            m       = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            content = m.group(1) if m else content
        jm   = re.search(r"\{[\s\S]*\}", content)
        return json.loads(jm.group() if jm else content)
    except Exception:
        return None          # caller decides whether to cache


def _get_audit_data() -> dict:
    """Return cached audit analysis, or generate + cache it on first call.
    Never caches fallback/failure — so the next request will retry the LLM.
    """
    ctx = _load_ctx()
    if not ctx:
        return _FALLBACK.copy()

    cached = ctx.get("audit_analysis")
    # Skip the cache if it is just the generic fallback message (stale from a
    # previous run where the LLM was unavailable).
    if cached and cached.get("insights") != _FALLBACK["insights"]:
        return cached

    # First time, or previous result was the fallback — (re)generate
    analysis = _gen_audit(ctx)
    if analysis:                          # only persist a real LLM result
        ctx["audit_analysis"] = analysis
        _save_ctx(ctx)
        return analysis

    return _FALLBACK.copy()              # show fallback but do NOT cache it


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
async def get_audit_insights():
    return _get_audit_data().get("insights", _FALLBACK["insights"])


@router.get("/risk-transactions")
async def get_risk_transactions():
    return _get_audit_data().get("transactions", [])


@router.get("/violations")
async def get_compliance_violations():
    return _get_audit_data().get("violations", _FALLBACK["violations"])


@router.get("/risk-score")
async def get_risk_score_distribution():
    return _get_audit_data().get("risk_distribution", _FALLBACK["risk_distribution"])


@router.get("/risk-summary")
async def get_risk_summary():
    return _get_audit_data().get("risk_summary", _FALLBACK["risk_summary"])


@router.post("/refresh")
async def refresh_audit():
    """Force-regenerate audit analysis for the current document."""
    ctx = _load_ctx()
    if not ctx:
        return {"message": "No document loaded."}
    ctx.pop("audit_analysis", None)
    _save_ctx(ctx)
    _get_audit_data()                  # regenerate now
    return {"message": "Audit analysis refreshed successfully."}
