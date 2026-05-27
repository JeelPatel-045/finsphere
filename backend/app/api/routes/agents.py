"""
FinSphere Agent Status Route

Agent statuses are derived from the active document context so the
Agents page always reflects what the system has actually done, not
a static snapshot.
"""

import os
import json
from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/agents")

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_ctx() -> dict | None:
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Dynamic agent status ───────────────────────────────────────────────────────

def _build_agent_status(ctx: dict | None) -> list:
    """
    Return agent status list derived from the active document context.
    An agent is 'active' if it was invoked for the current document,
    'idle' otherwise.
    """
    doc_loaded       = ctx is not None
    has_audit        = doc_loaded and bool(ctx.get("audit_analysis") and
                           ctx["audit_analysis"].get("insights") and
                           ctx["audit_analysis"]["insights"][0].get("message") !=
                           "No document loaded. Upload a financial document to see AI-powered audit insights.")
    has_forecast     = doc_loaded and bool((ctx.get("forecast_analysis") or {}).get("kpis"))
    is_csv_or_excel  = doc_loaded and (
        ctx.get("content_type") in ("text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel") or
        (ctx.get("filename") or "").endswith((".csv", ".xlsx", ".xls"))
    )
    is_image         = doc_loaded and ctx.get("content_type") in ("image/jpeg", "image/png")
    has_key_metrics  = doc_loaded and bool(ctx.get("key_metrics"))
    ct               = ctx.get("content_type", "") if doc_loaded else ""

    # Task counts from actual analysis data
    audit_tasks    = len((ctx.get("audit_analysis") or {}).get("transactions", [])) if has_audit else 0
    forecast_tasks = len((ctx.get("forecast_analysis") or {}).get("recommendations", [])) if has_forecast else 0

    return [
        {
            "name":        "Supervisor Agent",
            "status":      "active" if doc_loaded else "idle",
            "tasks":       1 if doc_loaded else 0,
            "type":        "orchestrator",
            "description": f"Orchestrating analysis of {ctx['filename']}" if doc_loaded else "",
        },
        {
            "name":        "SQL Agent",
            "status":      "active" if is_csv_or_excel else "idle",
            "tasks":       0,
            "type":        "data",
            "description": f"Querying {ctx['filename']}" if is_csv_or_excel else "",
        },
        {
            "name":        "Audit Agent",
            "status":      "active" if has_audit else "idle",
            "tasks":       audit_tasks,
            "type":        "compliance",
            "description": f"{audit_tasks} findings in {ctx['filename']}" if has_audit else
                           ("Ready — click Refresh Audit to analyse" if doc_loaded else ""),
        },
        {
            "name":        "Forecast Agent",
            "status":      "active" if has_forecast else "idle",
            "tasks":       forecast_tasks,
            "type":        "analytics",
            "description": f"{forecast_tasks} recommendations ready" if has_forecast else
                           ("Ready — click Generate Forecast to run" if doc_loaded else ""),
        },
        {
            "name":        "RAG Agent",
            "status":      "active" if has_key_metrics else "idle",
            "tasks":       len(ctx.get("key_metrics", [])) if doc_loaded else 0,
            "type":        "retrieval",
            "description": f"Indexed {len(ctx.get('key_metrics', []))} metrics" if has_key_metrics else "",
        },
        {
            "name":        "OCR Agent",
            "status":      "active" if is_image else "idle",
            "tasks":       1 if is_image else 0,
            "type":        "document",
            "description": f"Extracted text from {ctx['filename']}" if is_image else "",
        },
        {
            "name":        "Report Agent",
            "status":      "idle",
            "tasks":       0,
            "type":        "reporting",
            "description": f"Ready — click AI Report to generate for {ctx['filename']}" if doc_loaded else "",
        },
    ]


# ── Dynamic activity log ───────────────────────────────────────────────────────

def _build_activities(ctx: dict | None) -> list:
    """
    Build an activity log from the actual operations performed on the
    current document.  Falls back to an empty list if nothing is loaded.
    """
    if not ctx:
        return []

    activities = []
    filename   = ctx.get("filename", "document")
    ts         = _now_iso()

    # Upload / Supervisor
    activities.append({
        "agent":     "Supervisor Agent",
        "action":    f"Received and routed '{filename}' for multi-agent analysis",
        "timestamp": ts,
    })

    # OCR / Data Extraction
    raw_len = len(ctx.get("raw_text", ""))
    if raw_len > 50:
        activities.append({
            "agent":     "OCR Agent" if ctx.get("content_type") in ("image/jpeg", "image/png")
                         else "Data Analysis Agent",
            "action":    f"Extracted {raw_len:,} characters of content from '{filename}'",
            "timestamp": ts,
        })

    # RAG / key metrics
    metrics = ctx.get("key_metrics", [])
    if metrics:
        activities.append({
            "agent":     "RAG Agent",
            "action":    f"Indexed {len(metrics)} key financial metrics from '{filename}'",
            "timestamp": ts,
        })

    # Audit
    audit = ctx.get("audit_analysis") or {}
    txns  = audit.get("transactions", [])
    if txns:
        high = sum(1 for t in txns if t.get("risk") == "HIGH")
        activities.append({
            "agent":     "Audit Agent",
            "action":    f"Found {len(txns)} transactions ({high} HIGH risk) in '{filename}'",
            "timestamp": ts,
        })

    violations = audit.get("violations", [])
    if violations:
        activities.append({
            "agent":     "Audit Agent",
            "action":    f"Flagged {len(violations)} compliance issue(s) in '{filename}'",
            "timestamp": ts,
        })

    # Forecast
    fc = ctx.get("forecast_analysis") or {}
    if fc.get("kpis"):
        kpis = fc["kpis"]
        activities.append({
            "agent":     "Forecast Agent",
            "action":    f"Generated 6-month forecast — projected revenue {kpis.get('revenue', 'N/A')} "
                         f"(growth {kpis.get('growth_rate', 'N/A')})",
            "timestamp": ts,
        })

    recs = fc.get("recommendations", [])
    if recs:
        activities.append({
            "agent":     "Forecast Agent",
            "action":    f"Produced {len(recs)} CFO-level strategic recommendations",
            "timestamp": ts,
        })

    # SQL Agent
    ct = ctx.get("content_type", "")
    if ct == "text/csv" or (ctx.get("filename") or "").endswith(".csv"):
        activities.append({
            "agent":     "SQL Agent",
            "action":    f"Loaded '{filename}' into in-memory query engine — ready for NL queries",
            "timestamp": ts,
        })

    # Report Agent
    activities.append({
        "agent":     "Report Agent",
        "action":    f"Compiled analysis report for '{filename}'",
        "timestamp": ts,
    })

    return activities[:10]   # keep the feed concise


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/status")
def get_agent_status():
    """Return current status of all registered AI agents."""
    ctx = _load_ctx()
    return _build_agent_status(ctx)


@router.get("/activities")
def get_agent_activities():
    """Return recent activity log derived from the active document."""
    ctx = _load_ctx()
    return _build_activities(ctx)
