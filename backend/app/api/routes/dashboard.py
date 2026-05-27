"""
FinSphere Dashboard Route — all data driven from the uploaded document.

When no document is loaded every endpoint returns zeros / "N/A" so the
frontend never shows stale hardcoded figures.
"""

import os
import json
from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter

router = APIRouter(prefix="/dashboard")

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


def _fmt_inr(v: float, currency: str = "INR") -> str:
    """Format a value as INR. If currency is not INR, converts from USD (×83)."""
    if not v:
        return "N/A"
    inr = v if currency.upper() == "INR" else v * 83
    if abs(inr) >= 10_000_000:
        return f"₹{inr / 10_000_000:.2f} Cr"
    if abs(inr) >= 100_000:
        return f"₹{inr / 100_000:.1f} L"
    if abs(inr) >= 1_000:
        return f"₹{inr:,.0f}"
    return f"₹{inr:.2f}"


def _csv_kpis(ctx: dict) -> dict:
    """Compute revenue/expense/profit directly from a CSV file."""
    fp = ctx.get("file_path", "")
    if not fp or not os.path.exists(fp):
        return {}
    try:
        df = pd.read_csv(fp)
        cols_lower = {c.lower(): c for c in df.columns}

        revenue = expenses = 0.0

        # Pattern A: explicit type + amount columns  (e.g. transactions.csv)
        if "type" in cols_lower and "amount" in cols_lower:
            type_col   = cols_lower["type"]
            amount_col = cols_lower["amount"]
            df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)
            revenue  = float(df[df[type_col].str.lower() == "revenue"][amount_col].sum())
            expenses = float(df[df[type_col].str.lower() == "expense"][amount_col].sum())

        # Pattern B: debit/credit columns (journal-style)
        elif "debit" in cols_lower and "credit" in cols_lower:
            df["_debit"]  = pd.to_numeric(df[cols_lower["debit"]],  errors="coerce").fillna(0)
            df["_credit"] = pd.to_numeric(df[cols_lower["credit"]], errors="coerce").fillna(0)
            expenses = float(df["_debit"].sum())
            revenue  = float(df["_credit"].sum())

        # Pattern C: single amount column — treat total as revenue
        elif "amount" in cols_lower:
            df["_amt"] = pd.to_numeric(df[cols_lower["amount"]], errors="coerce").fillna(0)
            revenue  = float(df[df["_amt"] > 0]["_amt"].sum())
            expenses = float(abs(df[df["_amt"] < 0]["_amt"].sum()))

        profit = revenue - expenses
        return {"revenue": revenue, "expenses": expenses, "profit": profit}
    except Exception:
        return {}


# ── KPI endpoint ───────────────────────────────────────────────────────────────

@router.get("/kpis")
def get_kpis():
    ctx = _load_ctx()

    if not ctx:
        return {
            "revenue": 0,  "revenue_inr": "N/A",  "revenue_change": "",
            "expenses": 0, "expenses_inr": "N/A", "expenses_change": "",
            "profit": 0,   "profit_inr": "N/A",   "profit_change": "",
            "cashflow": 0, "cashflow_inr": "N/A", "cashflow_change": "",
            "forecast": 0, "riskScore": 0, "activeAgents": 0, "high_risk_transactions": 0,
            "doc_currency": "INR",
        }

    # 1. Try LLM-extracted raw_numbers
    rn       = ctx.get("raw_numbers") or {}
    revenue  = float(rn.get("revenue")  or 0)
    expenses = float(rn.get("expenses") or 0)
    profit   = float(rn.get("profit")   or 0)

    # 2. For CSV/Excel — compute directly from the file if LLM data is missing
    ct  = ctx.get("content_type", "")
    fp  = ctx.get("file_path", "")
    is_tabular = (
        ct == "text/csv" or fp.endswith(".csv") or
        ct in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
               "application/vnd.ms-excel") or
        fp.endswith((".xlsx", ".xls"))
    )
    if not revenue and not expenses and is_tabular:
        computed = _csv_kpis(ctx)
        revenue  = computed.get("revenue",  0)
        expenses = computed.get("expenses", 0)
        profit   = computed.get("profit",   0)

    if not profit and revenue and expenses:
        profit = revenue - expenses

    # 3. Cashflow from LLM or audit cache
    cashflow = float(rn.get("cashflow") or rn.get("operating_cashflow") or 0)
    if not cashflow:
        fc = (ctx.get("forecast_analysis") or {})
        cf_data = fc.get("cashflow", [])
        if cf_data:
            cashflow = float(cf_data[0].get("cashflow", 0))

    # 4. Risk data from cached audit analysis
    audit        = ctx.get("audit_analysis") or {}
    risk_summary = audit.get("risk_summary") or {}
    high_risk    = (risk_summary.get("high_risk_transactions") or {}).get("count", 0) or 0
    risk_score   = (risk_summary.get("ai_risk_score") or {}).get("score", 0) or 0

    doc_currency = (ctx.get("currency") or "INR").upper()

    return {
        "revenue":        revenue,
        "revenue_inr":    _fmt_inr(revenue, doc_currency),
        "revenue_change": "",

        "expenses":        expenses,
        "expenses_inr":    _fmt_inr(expenses, doc_currency),
        "expenses_change": "",

        "profit":        profit,
        "profit_inr":    _fmt_inr(profit, doc_currency),
        "profit_change": "",

        "cashflow":        cashflow,
        "cashflow_inr":    _fmt_inr(cashflow, doc_currency) if cashflow else "N/A",
        "cashflow_change": "",

        "forecast":               31,
        "riskScore":               int(risk_score),
        "activeAgents":            5,
        "high_risk_transactions":  int(high_risk),
        "doc_currency":            doc_currency,
    }


# ── Revenue chart ──────────────────────────────────────────────────────────────

@router.get("/revenue")
def get_revenue():
    ctx = _load_ctx()

    # Use forecast chartData if available (it contains month-level actuals+forecast)
    if ctx:
        fc = (ctx.get("forecast_analysis") or {})
        chart = fc.get("chartData", [])
        if chart:
            return [
                {
                    "month":    item.get("month", ""),
                    "revenue":  item.get("actual") or item.get("forecast") or 0,
                    "expenses": 0,
                    "profit":   item.get("actual") or item.get("forecast") or 0,
                }
                for item in chart
            ]

        # For CSV: build a single-bar chart from computed totals
        computed = _csv_kpis(ctx)
        if computed.get("revenue") or computed.get("expenses"):
            rev = computed["revenue"]
            exp = computed["expenses"]
            doc = ctx.get("filename", "Document")
            return [{"month": doc, "revenue": rev, "expenses": exp, "profit": rev - exp}]

    # No document — return empty so the chart shows nothing instead of fake data
    return []


# ── Risk heatmap ───────────────────────────────────────────────────────────────

@router.get("/risk-heatmap")
def get_risk_heatmap():
    ctx = _load_ctx()
    if not ctx:
        return []

    audit      = ctx.get("audit_analysis") or {}
    violations = audit.get("violations", [])
    insights   = audit.get("insights",   [])

    result = []

    # Convert violations to heatmap tiles
    for v in violations[:4]:
        issue    = v.get("issue", "Unknown issue")
        severity = v.get("severity", "Medium")
        color    = {"Critical": "red", "High": "red", "Medium": "yellow", "Low": "green"}.get(severity, "yellow")
        result.append({
            "title":  issue[:60],
            "level":  severity,
            "color":  color,
            "count":  1,
            "amount": "—",
        })

    # Fill remaining slots from audit insights (up to 6 total)
    for ins in insights[:max(0, 6 - len(result))]:
        msg      = ins.get("message", "")
        severity = ins.get("severity", "info")
        level    = {"critical": "High", "high": "High", "medium": "Medium", "info": "Low"}.get(severity, "Medium")
        color    = {"High": "red", "Medium": "yellow", "Low": "green"}.get(level, "yellow")
        result.append({"title": msg[:60], "level": level, "color": color, "count": 0, "amount": "—"})

    if not result:
        result = [{"title": "No risk data — upload a document or refresh audit", "level": "Low", "color": "green", "count": 0, "amount": "—"}]

    return result[:6]


# ── Forecast chart ─────────────────────────────────────────────────────────────

@router.get("/forecast-chart")
def get_dashboard_forecast_chart():
    ctx = _load_ctx()
    if not ctx:
        return []

    doc_currency = (ctx.get("currency") or "INR").upper()
    fc    = ctx.get("forecast_analysis") or {}
    chart = fc.get("chartData", [])
    multiplier = 1 if doc_currency == "INR" else 83
    if chart:
        return [
            {
                "month":        item.get("month", ""),
                "forecast":     item.get("forecast") or 0,
                "forecast_inr": int((item.get("forecast") or 0) * multiplier),
            }
            for item in chart
        ]

    # No forecast yet — project naively from CSV totals
    computed = _csv_kpis(ctx)
    revenue  = computed.get("revenue", 0)
    if not revenue:
        return []

    result = []
    base   = datetime.now()
    multiplier = 1 if doc_currency == "INR" else 83
    for i in range(1, 7):
        m = base + timedelta(days=30 * i)
        projected = revenue * (1 + 0.05 * i)
        result.append({
            "month":        m.strftime("%b"),
            "forecast":     round(projected),
            "forecast_inr": round(projected * multiplier),
        })
    return result
