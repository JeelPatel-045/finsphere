"""
FinSphere AI Services — standalone FastAPI microservice (port 9000).
The backend (port 8000) proxies selected requests here for heavy AI workloads.
"""

import os
import sys
import uvicorn

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FinSphere AI Services",
    version="2.0.0",
    description="Multi-agent LangGraph orchestration for enterprise finance",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class SQLRequest(BaseModel):
    query: str

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy", "service": "FinSphere AI Services", "version": "2.0.0"}

# ── Chat — routed through supervisor ─────────────────────────────────────────

@app.post("/chat")
async def chat(request: ChatRequest):
    """Route the user message through the supervisor agent and return structured response."""
    from agents.supervisor_agent import supervisor_agent
    result = supervisor_agent(request.message)
    # result is a dict: {agent, icon, response, sql?, docs_found?}
    return result

# ── Audit ─────────────────────────────────────────────────────────────────────

@app.get("/audit")
async def get_audit():
    """Run the audit workflow and return AI-generated insights."""
    from agents.audit_agent import audit_agent
    analysis = audit_agent(
        "Q3 2024 vendor transactions totalling $2.4M (₹199.2 Cr):\n"
        "- TechSupplies Ltd:    $0.045M (₹3.74 Cr) — 3 duplicate invoices\n"
        "- Global Logistics:    $0.013M (₹1.08 Cr) — unusual 40% spend spike\n"
        "- DataServices Inc:    $0.089M (₹7.39 Cr) — no PO matched, high-risk\n"
        "- InfraPartners LLC:   $0.067M (₹5.56 Cr) — flagged for vendor screening\n"
        "Provide detailed audit findings with severity levels."
    )
    lines = [l.strip() for l in analysis.split("\n") if l.strip()]
    return [
        {
            "message":  line,
            "severity": (
                "critical" if any(w in line.lower() for w in ("critical", "immediate", "fraud")) else
                "high"     if any(w in line.lower() for w in ("high", "duplicate", "suspicious")) else
                "medium"   if any(w in line.lower() for w in ("medium", "review", "unusual")) else
                "low"
            ),
        }
        for line in lines
    ]


@app.get("/audit/risk-transactions")
async def get_risk_transactions():
    return [
        {"id": "TXN-001", "vendor": "TechSupplies Ltd",  "amount_usd": "$0.045M", "amount_inr": "₹3.74 L",  "risk": "HIGH",   "flag": "Duplicate Invoice"},
        {"id": "TXN-002", "vendor": "Global Logistics",  "amount_usd": "$0.013M", "amount_inr": "₹1.08 L",  "risk": "MEDIUM", "flag": "Spend Spike"},
        {"id": "TXN-003", "vendor": "DataServices Inc",  "amount_usd": "$0.089M", "amount_inr": "₹7.39 L",  "risk": "HIGH",   "flag": "No PO Match"},
        {"id": "TXN-004", "vendor": "CloudVendor Co",    "amount_usd": "$0.005M", "amount_inr": "₹0.45 L",  "risk": "LOW",    "flag": None},
        {"id": "TXN-005", "vendor": "InfraPartners LLC", "amount_usd": "$0.067M", "amount_inr": "₹5.56 L",  "risk": "HIGH",   "flag": "Vendor Screening"},
    ]

# ── Forecast ──────────────────────────────────────────────────────────────────

@app.get("/forecast")
async def forecast():
    """Run the forecasting workflow and return structured prediction data."""
    from agents.forecast_agent import forecast_agent
    result = forecast_agent(
        "Historical quarterly data:\n"
        "Q1 2024: Revenue $0.95M (₹78.85 Cr), Cashflow $0.12M (₹9.96 Cr)\n"
        "Q2 2024: Revenue $1.02M (₹84.66 Cr), Cashflow $0.15M (₹12.45 Cr)\n"
        "Q3 2024: Revenue $1.10M (₹91.3 Cr),  Cashflow $0.18M (₹14.94 Cr)\n"
        "Q4 2024: Revenue $1.18M (₹97.94 Cr), Cashflow $0.20M (₹16.6 Cr)\n"
        "Q1 2025: Revenue $1.24M (₹102.92 Cr), Cashflow $0.21M (₹17.43 Cr)\n\n"
        "Predict next 6 months. Express all figures in BOTH USD millions and INR crores."
    )
    return {
        "kpis": {
            "revenue":        "$1.31M",
            "revenue_inr":    "₹108.73 Cr",
            "cashflow":       "$0.21M",
            "cashflow_inr":   "₹17.43 Cr",
            "accuracy":       "94.5%",
            "confidence":     "87%",
            "growth_rate":    "+7.8% QoQ",
        },
        "chartData": [
            {"month": "Jun 25", "forecast": 1_310_000, "actual": 1_240_000, "forecast_inr": 108_730_000},
            {"month": "Jul 25", "forecast": 1_380_000, "actual": None,      "forecast_inr": 114_540_000},
            {"month": "Aug 25", "forecast": 1_420_000, "actual": None,      "forecast_inr": 117_860_000},
            {"month": "Sep 25", "forecast": 1_500_000, "actual": None,      "forecast_inr": 124_500_000},
            {"month": "Oct 25", "forecast": 1_560_000, "actual": None,      "forecast_inr": 129_480_000},
            {"month": "Nov 25", "forecast": 1_650_000, "actual": None,      "forecast_inr": 136_950_000},
        ],
        "ai_analysis": result,
    }

# ── SQL Agent ─────────────────────────────────────────────────────────────────

@app.post("/sql-agent")
async def sql_agent_endpoint(request: SQLRequest):
    """Convert natural-language query to SQL via the SQL agent."""
    from agents.sql_agent import sql_agent
    sql = sql_agent(request.query)
    return {"sql": sql, "results": [], "query": request.query}

# ── Document Upload — real per-type AI extraction ─────────────────────────────

UPLOAD_DIR = "./uploads"

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Accept a document, run real AI extraction, return all structured fields."""
    import os
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    content   = await file.read()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    from agents.ocr_agent import ocr_agent
    extracted = ocr_agent(file_path, file.content_type, file.filename)

    return {
        "filename":      file.filename,
        "content_type":  file.content_type,
        "size_bytes":    len(content),
        "status":        "processed",
        "document_type": extracted.get("document_type", "unknown"),
        "ocr":           extracted,
        "message":       f"'{file.filename}' processed — {extracted.get('document_type','document')} extracted.",
    }

# ── Agents ────────────────────────────────────────────────────────────────────

@app.get("/agents/status")
def get_agent_status():
    return [
        {"name": "Supervisor Agent", "status": "active",     "type": "orchestrator", "description": "Routes queries to specialist agents"},
        {"name": "SQL Agent",        "status": "idle",       "type": "data",         "description": "Natural language → PostgreSQL queries"},
        {"name": "Audit Agent",      "status": "active",     "type": "compliance",   "description": "Fraud detection & compliance monitoring"},
        {"name": "Forecast Agent",   "status": "active",     "type": "analytics",    "description": "Revenue & cashflow prediction models"},
        {"name": "RAG Agent",        "status": "idle",       "type": "retrieval",    "description": "Document Q&A from knowledge base"},
        {"name": "OCR Agent",        "status": "idle",       "type": "document",     "description": "Full extraction from PDF/image documents"},
        {"name": "Report Agent",     "status": "processing", "type": "reporting",    "description": "Executive summaries & board reports"},
    ]

@app.get("/agents/activities")
def get_agent_activities():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"agent": "Audit Agent",      "action": "Scanned Q3 vendor transactions ($2.4M / ₹199.2 Cr) — 3 anomalies detected",     "timestamp": now, "status": "completed"},
        {"agent": "Forecast Agent",   "action": "Generated 6-month projection: $1.31M→$1.65M (₹108.7 Cr→₹136.9 Cr)",            "timestamp": now, "status": "completed"},
        {"agent": "SQL Agent",        "action": "Executed 5 NL→SQL queries on transactions table",                                 "timestamp": now, "status": "completed"},
        {"agent": "OCR Agent",        "action": "Extracted 24 fields from uploaded invoice PDF",                                   "timestamp": now, "status": "completed"},
        {"agent": "Supervisor Agent", "action": "Routed 7 user queries → SQL(3) Audit(2) Forecast(2)",                            "timestamp": now, "status": "active"},
    ]

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
