"""
FinSphere Reports Route

POST /reports/generate  — LLM generates an executive PDF report for the active document
GET  /reports/export    — Export dashboard data as CSV (Excel-compatible)
"""

import os
import io
import csv
import json
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.core.llm_factory import get_llm

router = APIRouter(prefix="/reports")

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"
_llm = get_llm(temperature=0.1, max_tokens=4000)

NAVY  = (15,  52,  96)
TEAL  = (20, 120, 120)
LIGHT = (245, 247, 250)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_ctx() -> dict | None:
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _fmt_usd(v: float) -> str:
    if not v:
        return "N/A"
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v:,.0f}"
    return f"${v:.2f}"


def _fmt_inr(v: float) -> str:
    if not v:
        return "N/A"
    inr = v * 83
    if abs(inr) >= 10_000_000:
        return f"₹{inr / 10_000_000:.2f} Cr"
    if abs(inr) >= 100_000:
        return f"₹{inr / 100_000:.1f} L"
    return f"₹{inr:,.0f}"


# ── Report prompt ──────────────────────────────────────────────────────────────

_REPORT_PROMPT = """\
You are a senior CFO-level financial analyst at a Big-4 accounting firm.
Generate a comprehensive executive intelligence report based on the financial document below.

=== DOCUMENT CONTEXT ===
File    : {filename}
Type    : {doc_type}
Company : {company}
Summary : {summary}

Key Metrics:
{metrics}

Audit Analysis:
{audit}

Forecast Analysis:
{forecast}
=== END CONTEXT ===

Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{{
  "report_title": "Executive Financial Intelligence Report — {company}",
  "period": "Reporting period covered by this document",
  "executive_summary": "3-4 sentence CFO-level summary: financial health, key risks, and strategic outlook.",
  "key_highlights": [
    "Revenue performance with actual figure and YoY comparison",
    "Profit margin or EBITDA highlight",
    "Top risk or compliance concern with regulation reference",
    "Forward-looking forecast highlight"
  ],
  "financial_performance": {{
    "revenue":   "Revenue figure with currency, period, and brief commentary",
    "expenses":  "Expense figure with key expense drivers",
    "profit":    "Net profit / EBITDA with margin %",
    "cashflow":  "Operating cashflow or liquidity position"
  }},
  "risk_assessment": {{
    "overall_risk": "Low|Medium|High|Critical",
    "risk_score": <0-100>,
    "top_risks": [
      "Risk 1 — cite applicable Indian regulation (e.g. Companies Act 2013 Sec 177, Ind AS 115, GST Act 2017)",
      "Risk 2 — with specific regulatory reference",
      "Risk 3 — with specific regulatory reference"
    ]
  }},
  "compliance_status": {{
    "overall_status": "Compliant|Partially Compliant|Non-Compliant",
    "critical_issues": <int>,
    "high_issues": <int>,
    "recommendations": [
      "Actionable recommendation 1 with timeline",
      "Actionable recommendation 2 with timeline",
      "Actionable recommendation 3 with timeline"
    ]
  }},
  "forecast_outlook": "2-3 sentence forward-looking statement including projected revenue, growth rate, and key assumptions.",
  "cfo_recommendations": [
    "Priority 1 action — specific, measurable, with target date",
    "Priority 2 action — specific, measurable, with target date",
    "Priority 3 action — specific, measurable, with target date",
    "Priority 4 action — risk mitigation action"
  ]
}}
"""


def _gen_report_data(ctx: dict) -> dict | None:
    audit    = ctx.get("audit_analysis") or {}
    fc       = ctx.get("forecast_analysis") or {}
    fc_slim  = {k: v for k, v in fc.items() if k not in ("chartData", "cashflow")}

    prompt = _REPORT_PROMPT.format(
        filename=ctx.get("filename", "unknown"),
        doc_type=ctx.get("document_type", "unknown").replace("_", " "),
        company=ctx.get("company_name", "Unknown Company"),
        summary=ctx.get("summary", "No summary available."),
        metrics=json.dumps(ctx.get("key_metrics", []), indent=2)[:1500],
        audit=json.dumps(audit, indent=2)[:1500],
        forecast=json.dumps(fc_slim, indent=2)[:1000],
    )
    try:
        response = _llm.invoke([HumanMessage(content=prompt)])
        content  = response.content.strip()
        if "```" in content:
            m       = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            content = m.group(1) if m else content
        jm = re.search(r"\{[\s\S]*\}", content)
        return json.loads(jm.group() if jm else content)
    except Exception:
        return None


# ── PDF builder ────────────────────────────────────────────────────────────────

def _build_pdf(ctx: dict, rd: dict | None) -> bytes:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    company  = ctx.get("company_name", "FinSphere Enterprises")
    src_file = ctx.get("filename", "Financial Document")
    now_str  = datetime.now().strftime("%d %B %Y  %I:%M %p")
    rd       = rd or {}

    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=22)
    pdf.add_page()

    # ── Cover ──────────────────────────────────────────────────────────────────
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 65, "F")

    pdf.set_xy(12, 10)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, company, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(180, 210, 255)
    pdf.cell(0, 6, rd.get("report_title", "Executive Financial Intelligence Report"))

    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(12, 78)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 9, "EXECUTIVE INTELLIGENCE REPORT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(80, 5.5, f"Period: {rd.get('period', 'See document')}")
    pdf.cell(0,  5.5, f"Generated: {now_str}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, f"Source document: {src_file}")

    pdf.set_text_color(0, 0, 0)

    def section(title: str):
        pdf.ln(5)
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(12)
        pdf.cell(186, 8, f"  {title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    def body(text: str, indent: int = 12):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(indent)
        pdf.multi_cell(210 - indent - 12, 5.5, str(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def kv(label: str, value: str, indent: int = 12):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_x(indent)
        pdf.cell(40, 5.5, f"{label}:")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(210 - indent - 40 - 12, 5.5, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def bullet_list(items: list, indent: int = 18):
        pdf.set_font("Helvetica", "", 9)
        for item in items:
            pdf.set_x(indent)
            pdf.cell(5, 5.5, "-")
            pdf.multi_cell(210 - indent - 17, 5.5, str(item), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(0.5)

    # ── Executive Summary ──────────────────────────────────────────────────────
    section("1.  EXECUTIVE SUMMARY")
    body(rd.get("executive_summary", ctx.get("summary", "No summary available.")))

    # ── Key Highlights ─────────────────────────────────────────────────────────
    highlights = rd.get("key_highlights", [])
    if highlights:
        section("2.  KEY HIGHLIGHTS")
        bullet_list(highlights)

    # ── Financial Performance ──────────────────────────────────────────────────
    fin = rd.get("financial_performance", {})
    if fin:
        section("3.  FINANCIAL PERFORMANCE")
        for k, v in fin.items():
            kv(k.replace("_", " ").title(), v)

    # ── Risk Assessment ────────────────────────────────────────────────────────
    risk = rd.get("risk_assessment", {})
    pdf.add_page()
    section("4.  RISK ASSESSMENT")
    if risk:
        kv("Overall Risk",  str(risk.get("overall_risk", "N/A")))
        kv("AI Risk Score", f"{risk.get('risk_score', 0)} / 100")
        top_risks = risk.get("top_risks", [])
        if top_risks:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_x(12)
            pdf.cell(0, 5.5, "Top Risks Identified:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            bullet_list(top_risks)
    else:
        body("No risk data available. Upload a financial document and refresh the audit analysis.")

    # ── Compliance Status ──────────────────────────────────────────────────────
    comp = rd.get("compliance_status", {})
    section("5.  COMPLIANCE & REGULATORY STATUS")
    if comp:
        kv("Overall Status",   str(comp.get("overall_status", "N/A")))
        kv("Critical Issues",  str(comp.get("critical_issues", 0)))
        kv("High Issues",      str(comp.get("high_issues", 0)))
        recs = comp.get("recommendations", [])
        if recs:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_x(12)
            pdf.cell(0, 5.5, "Recommended Actions:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            bullet_list(recs)

    # ── Forecast Outlook ───────────────────────────────────────────────────────
    outlook = rd.get("forecast_outlook", "")
    if outlook:
        section("6.  FORECAST OUTLOOK")
        body(outlook)

    # ── CFO Recommendations ────────────────────────────────────────────────────
    cfo_recs = rd.get("cfo_recommendations", [])
    if cfo_recs:
        section("7.  CFO RECOMMENDATIONS")
        pdf.set_font("Helvetica", "", 9)
        for i, rec in enumerate(cfo_recs, 1):
            pdf.set_x(12)
            pdf.cell(8, 5.5, f"{i}.")
            pdf.multi_cell(178, 5.5, str(rec), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)

    # ── Raw Metrics Appendix ───────────────────────────────────────────────────
    metrics = ctx.get("key_metrics", [])
    if metrics:
        pdf.add_page()
        section("APPENDIX — KEY METRICS FROM DOCUMENT")
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(255, 255, 255)
        pdf.set_x(12)
        pdf.cell(93, 7, "Metric", fill=True, border=0)
        pdf.cell(93, 7, "Value",  fill=True, border=0)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 8.5)
        for i, m in enumerate(metrics):
            pdf.set_fill_color(245, 245, 245) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
            pdf.set_x(12)
            if isinstance(m, dict):
                pdf.cell(93, 6, str(m.get("label", "")), fill=True)
                pdf.cell(93, 6, str(m.get("value", "")), fill=True)
            else:
                pdf.cell(186, 6, str(m), fill=True)
            pdf.ln()

    # ── Footer on each page ────────────────────────────────────────────────────
    pdf.set_y(-14)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(150, 150, 150)
    pdf.set_x(12)
    pdf.cell(93, 5, "FinSphere AI  —  Confidential  —  Not for external distribution")
    pdf.cell(93, 5, f"Generated: {now_str}", align="R")

    return pdf.output()


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_report():
    """Generate an AI executive PDF report for the active document."""
    ctx = _load_ctx()
    if not ctx:
        raise HTTPException(status_code=400, detail="No document loaded. Upload a document first.")

    report_data = _gen_report_data(ctx)
    pdf_bytes   = _build_pdf(ctx, report_data)

    fname = f"FinSphere_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/export")
async def export_data():
    """Export dashboard data as CSV (Excel-compatible UTF-8 BOM)."""
    ctx      = _load_ctx()
    output   = io.StringIO()
    writer   = csv.writer(output)
    now_str  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not ctx:
        writer.writerow(["FinSphere AI — No document loaded"])
        content = output.getvalue()
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="finsphere_export.csv"'},
        )

    company  = ctx.get("company_name", "Unknown")
    src_file = ctx.get("filename", "unknown")
    rn       = ctx.get("raw_numbers") or {}
    audit    = ctx.get("audit_analysis") or {}
    rs       = audit.get("risk_summary") or {}
    fc       = ctx.get("forecast_analysis") or {}

    # ── Header block ──────────────────────────────────────────────────────────
    writer.writerow(["FinSphere AI — Dashboard Export"])
    writer.writerow(["Company",          company])
    writer.writerow(["Source Document",  src_file])
    writer.writerow(["Exported At",      now_str])
    writer.writerow([])

    # ── Financial Metrics ─────────────────────────────────────────────────────
    writer.writerow(["FINANCIAL METRICS"])
    writer.writerow(["Metric", "Value (USD)", "Value (INR)"])
    for field in ["revenue", "expenses", "profit", "cashflow"]:
        val = float(rn.get(field) or 0)
        writer.writerow([field.title(), _fmt_usd(val), _fmt_inr(val)])
    writer.writerow([])

    # ── Risk Summary ──────────────────────────────────────────────────────────
    writer.writerow(["RISK SUMMARY"])
    writer.writerow(["Metric", "Value"])
    risk_sc = (rs.get("ai_risk_score") or {})
    writer.writerow(["AI Risk Score",         f"{risk_sc.get('score', 0)} / 100  ({risk_sc.get('level', 'N/A')})"])
    writer.writerow(["High Risk Transactions", (rs.get("high_risk_transactions") or {}).get("count", 0)])
    writer.writerow(["Compliance Violations",  (rs.get("compliance_violations")  or {}).get("count", 0)])
    writer.writerow(["Audit Flags",            (rs.get("audit_flags")            or {}).get("count", 0)])
    writer.writerow([])

    # ── Compliance Violations ─────────────────────────────────────────────────
    violations = audit.get("violations", [])
    if violations:
        writer.writerow(["COMPLIANCE VIOLATIONS"])
        writer.writerow(["Issue", "Severity", "Regulation / Standard"])
        for v in violations:
            writer.writerow([v.get("issue", ""), v.get("severity", ""), v.get("regulation", "")])
        writer.writerow([])

    # ── Flagged Transactions ──────────────────────────────────────────────────
    transactions = audit.get("transactions", [])
    if transactions:
        writer.writerow(["FLAGGED TRANSACTIONS"])
        writer.writerow(["ID", "Vendor / Party", "Amount (USD)", "Amount (INR)", "Risk", "Flag", "Date"])
        for t in transactions:
            writer.writerow([
                t.get("id", ""),       t.get("vendor", ""),
                t.get("amount_usd", ""), t.get("amount_inr", ""),
                t.get("risk", ""),     t.get("flag", ""),
                t.get("date", ""),
            ])
        writer.writerow([])

    # ── Forecast Data ─────────────────────────────────────────────────────────
    chart = fc.get("chartData", [])
    if chart:
        writer.writerow(["REVENUE FORECAST"])
        writer.writerow(["Month", "Actual / Forecast (USD)", "Forecast INR"])
        for c in chart:
            val = c.get("forecast") or c.get("actual") or 0
            writer.writerow([c.get("month", ""), _fmt_usd(val), _fmt_inr(val)])
        writer.writerow([])

    # ── Key Metrics ───────────────────────────────────────────────────────────
    metrics = ctx.get("key_metrics", [])
    if metrics:
        writer.writerow(["KEY METRICS FROM DOCUMENT"])
        writer.writerow(["Label", "Value"])
        for m in metrics:
            if isinstance(m, dict):
                writer.writerow([m.get("label", ""), m.get("value", "")])
            else:
                writer.writerow([str(m)])

    content = output.getvalue()
    fname   = f"FinSphere_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
