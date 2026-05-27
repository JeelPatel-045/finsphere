"""
FinSphere Forecasting Route — Document-aware financial forecasting.

On the first request after a new document upload, calls the LLM to generate
real forecasts derived from the document's actual financial metrics.
Caches the result inside active_context.json so subsequent calls are instant.
"""

import os
import json
import re

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory

router = APIRouter()

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
_llm = get_llm(temperature=0.2, max_tokens=3000)


# ── Fallback data shown when no document is loaded ────────────────────────────

_FALLBACK_KPIS = {
    "revenue":      "N/A",
    "revenue_inr":  "N/A",
    "cashflow":     "N/A",
    "cashflow_inr": "N/A",
    "accuracy":     "N/A",
    "confidence":   "N/A",
    "growth_rate":  "N/A",
}

_FALLBACK_TRENDS = [
    {
        "metric":    "No document loaded",
        "value":     "—",
        "direction": "up",
        "detail":    "Upload a financial document to see AI trend analysis",
    }
]

_FALLBACK_RECOMMENDATIONS = [
    {
        "title":    "Upload a Financial Document",
        "detail":   "Upload a PDF, CSV, or Excel financial file to get AI forecasts and CFO-level recommendations specific to your data.",
        "priority": "High",
        "impact":   "Required",
    }
]


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


# ── LLM forecast generation ───────────────────────────────────────────────────

_FORECAST_PROMPT = """\
You are a CFO-level financial analyst AI.  Using the document data below,
generate realistic forward-looking forecasts and strategic recommendations.
You MUST also explain your methodology in simple language for a non-finance audience.

=== DOCUMENT CONTEXT ===
File     : {filename}
Type     : {doc_type}
Company  : {company}
Period   : {period}
Summary  : {summary}

Key Metrics (from document):
{metrics}

Additional Extracted Data:
{extracted}

Document Text (excerpt):
{raw_text}
=== END CONTEXT ===

Return ONLY valid JSON (no explanation, no markdown):
{{
  "kpis": {{
    "revenue":      "$X.XXM",
    "revenue_inr":  "₹X.XX Cr",
    "cashflow":     "$X.XXM",
    "cashflow_inr": "₹X.XX Cr",
    "accuracy":     "XX.X%",
    "confidence":   "XX%",
    "growth_rate":  "+X.X%"
  }},
  "methodology": {{
    "approach":        "One-sentence plain-English summary of the forecasting method used",
    "base_period":     "The actual time period from the document (e.g. Q1 2025)",
    "technique":       "Trend extrapolation | Moving average | Growth rate projection | Seasonal adjustment",
    "data_used":       "Which specific figures from the document were used as the starting point",
    "assumptions":     ["Assumption 1 in plain English", "Assumption 2", "Assumption 3"],
    "confidence_note": "Plain English explanation of how confident we are and why",
    "layman_note":     "2-3 sentence explanation a non-finance person can easily understand"
  }},
  "chartData": [
    {{"month": "Jul '25", "forecast": <raw_number>,  "actual": <raw_number_or_null>}},
    {{"month": "Aug '25", "forecast": <raw_number>,  "actual": null}},
    {{"month": "Sep '25", "forecast": <raw_number>,  "actual": null}},
    {{"month": "Oct '25", "forecast": <raw_number>,  "actual": null}},
    {{"month": "Nov '25", "forecast": <raw_number>,  "actual": null}},
    {{"month": "Dec '25", "forecast": <raw_number>,  "actual": null}}
  ],
  "trends": [
    {{"metric": "Revenue Growth (vs prior period)", "value": "+X%",  "direction": "up",   "detail": "Based on document figures"}},
    {{"metric": "Operational Costs",                "value": "+X%",  "direction": "up",   "detail": "Cost trend from document"}},
    {{"metric": "Profit Margin",                    "value": "XX%",  "direction": "up",   "detail": "Derived from document"}},
    {{"metric": "Cash Flow Health",                 "value": "$X.XXM","direction": "up",  "detail": "Working capital position"}},
    {{"metric": "Vendor Risk Exposure",             "value": "+X%",  "direction": "up",   "detail": "Payables concentration"}},
    {{"metric": "DSO (Days Sales Outstanding)",     "value": "XXd",  "direction": "down", "detail": "Receivables collection speed"}}
  ],
  "cashflow": [
    {{"month": "Jul '25", "cashflow": <int>, "operating": <int>, "investing": <int>, "financing": <int>}},
    {{"month": "Aug '25", "cashflow": <int>, "operating": <int>, "investing": <int>, "financing": <int>}},
    {{"month": "Sep '25", "cashflow": <int>, "operating": <int>, "investing": <int>, "financing": <int>}},
    {{"month": "Oct '25", "cashflow": <int>, "operating": <int>, "investing": <int>, "financing": <int>}},
    {{"month": "Nov '25", "cashflow": <int>, "operating": <int>, "investing": <int>, "financing": <int>}},
    {{"month": "Dec '25", "cashflow": <int>, "operating": <int>, "investing": <int>, "financing": <int>}}
  ],
  "recommendations": [
    {{"title": "Recommendation title", "detail": "Specific action with numbers from the document", "priority": "Critical|High|Medium|Low", "impact": "$X.XXM or narrative"}},
    {{"title": "Second recommendation", "detail": "...", "priority": "High",   "impact": "..."}},
    {{"title": "Third recommendation",  "detail": "...", "priority": "Medium", "impact": "..."}},
    {{"title": "Fourth recommendation", "detail": "...", "priority": "Medium", "impact": "..."}},
    {{"title": "Fifth recommendation",  "detail": "...", "priority": "Low",    "impact": "..."}}
  ]
}}

Rules:
- chartData raw numbers should be in the document's currency units (e.g. if revenue is $1.25M, use 1250000).
- Use ACTUAL numbers from the document as the base; project forward realistically.
- Months are the 6 months following the document's reporting period.
- actual = null for future months; you may fill the first month's actual if it looks like a current period.
- Monetary amounts in BOTH USD ($X.XXM) AND INR (₹X.XX Cr), 1 USD = ₹83.
- recommendations MUST reference specific numbers or issues found in THIS document.
- methodology.layman_note MUST be simple enough for someone with no finance background.\
"""


def _gen_forecast(ctx: dict) -> dict | None:
    """Return structured forecast dict, or None if LLM call fails."""
    prompt = _FORECAST_PROMPT.format(
        filename=ctx.get("filename", "unknown"),
        doc_type=ctx.get("document_type", "unknown").replace("_", " "),
        company=ctx.get("company_name", "Unknown"),
        period=ctx.get("period", "Unknown"),
        summary=ctx.get("summary", ""),
        metrics=json.dumps(ctx.get("key_metrics", []), indent=2),
        extracted=json.dumps(ctx.get("all_extracted_data", {}), indent=2)[:2000],
        raw_text=ctx.get("raw_text", "")[:2500],
    )
    try:
        response = _llm.invoke([HumanMessage(content=prompt)])
        content  = response.content.strip()
        if "```" in content:
            m       = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            content = m.group(1) if m else content
        jm   = re.search(r"\{[\s\S]*\}", content)
        data = json.loads(jm.group() if jm else content)
        # Validate that we got actual content (not an empty shell)
        return data if data.get("kpis") or data.get("chartData") else None
    except Exception:
        return None          # caller decides whether to cache


_FALLBACK_FULL = {
    "kpis":            _FALLBACK_KPIS,
    "chartData":       [],
    "trends":          _FALLBACK_TRENDS,
    "cashflow":        [],
    "recommendations": _FALLBACK_RECOMMENDATIONS,
}


def _get_forecast_data() -> dict:
    """Return cached forecast, or generate + cache it on first call.
    Never caches a failed/empty result — so the next request will retry.
    """
    ctx = _load_ctx()
    if not ctx:
        return _FALLBACK_FULL.copy()

    cached = ctx.get("forecast_analysis")
    # Accept cached result only if it has real content
    if cached and (cached.get("kpis") or cached.get("chartData")):
        return cached

    # First time, or previous result was empty — (re)generate
    analysis = _gen_forecast(ctx)
    if analysis:                          # only persist a real LLM result
        ctx["forecast_analysis"] = analysis
        _save_ctx(ctx)
        return analysis

    return _FALLBACK_FULL.copy()         # show fallback but do NOT cache it


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/forecast")
async def get_forecast():
    data = _get_forecast_data()
    return {
        "kpis":        data.get("kpis",        _FALLBACK_KPIS),
        "chartData":   data.get("chartData",   []),
        "methodology": data.get("methodology", {}),
    }


@router.get("/forecast/methodology")
async def get_forecast_methodology():
    return _get_forecast_data().get("methodology", {})


@router.get("/forecast/trends")
async def get_trend_analysis():
    return _get_forecast_data().get("trends", _FALLBACK_TRENDS)


@router.get("/forecast/cashflow")
async def get_cashflow_forecast():
    return _get_forecast_data().get("cashflow", [])


@router.get("/forecast/recommendations")
async def get_ai_recommendations():
    return _get_forecast_data().get("recommendations", _FALLBACK_RECOMMENDATIONS)


@router.post("/forecast/refresh")
async def refresh_forecast():
    """Force-regenerate forecast analysis for the current document."""
    ctx = _load_ctx()
    if not ctx:
        return {"message": "No document loaded."}
    ctx.pop("forecast_analysis", None)
    _save_ctx(ctx)
    _get_forecast_data()               # regenerate now
    return {"message": "Forecast analysis refreshed successfully."}
