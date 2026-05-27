"""
FinSphere AI SQL Agent

Converts natural language questions to PostgreSQL queries and returns results.
When a document is loaded:
  - CSV/Excel → actually queries the file with pandas
  - Other types → returns results derived from extracted document data
When no document is loaded → returns demo results.
"""

import os
import json
import re

import pandas as pd
from fastapi          import APIRouter
from pydantic         import BaseModel
from langchain_core.messages import HumanMessage

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory

router = APIRouter()

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
# Lower temperature for SQL generation — more deterministic output
_llm = get_llm(temperature=0.0, max_tokens=1000)

DB_SCHEMA = [
    {
        "table":   "transactions",
        "columns": ["id", "account_name", "transaction_type", "amount", "quarter", "risk_score"],
    },
    {
        "table":   "vendors",
        "columns": ["vendor_id", "vendor_name", "payment_amount", "risk_level", "country"],
    },
    {
        "table":   "audit_logs",
        "columns": ["audit_id", "risk_score", "compliance_status", "description", "created_at"],
    },
    {
        "table":   "journal_entries",
        "columns": ["entry_id", "account_name", "debit", "credit", "quarter", "approved_by"],
    },
]


class SQLRequest(BaseModel):
    query: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_ctx() -> dict | None:
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _clean_sql(raw: str) -> str:
    """Strip any wrapping (code fences, agent tags, explanations) from an LLM SQL response."""
    text = raw.strip()
    # Remove agent tag if present (e.g. **[Agent — file]**\n\n)
    text = re.sub(r"^\*\*\[.*?\]\*\*\s*\n+", "", text, flags=re.DOTALL)
    # Remove markdown code fences
    if "```" in text:
        m    = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", text)
        text = m.group(1) if m else text.replace("```sql", "").replace("```", "").strip()
    # If it still has prose before the first SELECT/WITH/INSERT/UPDATE/DELETE, trim it
    sql_start = re.search(r"\b(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE)\b", text, re.IGNORECASE)
    if sql_start:
        text = text[sql_start.start():]
    return text.strip()


def _generate_sql(question: str, ctx: dict | None, csv_columns: list[str] | None = None) -> str:
    """Call LLM with a SQL-only prompt — uses actual CSV columns when available."""
    if csv_columns:
        cols_str   = ", ".join(csv_columns)
        table_name = "uploaded_data"
        schema_ctx = f"""\
The user has uploaded a CSV file. Simulate SQL as if its data is in a table:
  {table_name}({cols_str})
"""
    elif ctx:
        doc_type = ctx.get("document_type", "financial_document").replace("_", " ")
        company  = ctx.get("company_name", "the company")
        filename = ctx.get("filename", "document")
        metrics  = json.dumps(ctx.get("key_metrics", []), indent=2)[:600]
        schema_ctx = f"""\
The user has uploaded a {doc_type} from {company} (file: {filename}).

Key metrics from the document:
{metrics}

Simulate SQL as if this financial data is stored in a relational database with tables:
  transactions(id, account_name, transaction_type, amount_usd, quarter, risk_score, vendor, flag)
  vendors(vendor_id, vendor_name, total_payments, risk_level, country, last_payment_date)
  journal_entries(entry_id, account_name, debit, credit, quarter, approved_by, description)
  financial_metrics(metric_name, value, period, currency)
"""
    else:
        schema_ctx = """\
Tables available:
  transactions(id, account_name, transaction_type, amount, quarter, risk_score)
  vendors(vendor_id, vendor_name, payment_amount, risk_level, country)
  audit_logs(audit_id, risk_score, compliance_status, description, created_at)
  journal_entries(entry_id, account_name, debit, credit, quarter, approved_by)
"""

    prompt = f"""\
You are a PostgreSQL expert for a financial analytics system.
{schema_ctx}
Convert the question below to a well-formatted, executable PostgreSQL query.
Return ONLY the SQL — no explanation, no prose, no markdown fences, no comments.

Question: {question}

SQL:"""

    try:
        response = _llm.invoke([HumanMessage(content=prompt)])
        return _clean_sql(response.content)
    except Exception:
        fallback_col = csv_columns[0] if csv_columns else "id"
        table        = "uploaded_data" if csv_columns else "transactions"
        return f"SELECT *\nFROM {table}\nORDER BY {fallback_col}\nLIMIT 10;"


_SAFE_BUILTINS = {
    "len": len, "sum": sum, "min": min, "max": max, "abs": abs,
    "round": round, "sorted": sorted, "list": list, "dict": dict,
    "str": str, "int": int, "float": float, "bool": bool,
    "range": range, "enumerate": enumerate, "zip": zip,
    "map": map, "filter": filter, "print": print,
    "True": True, "False": False, "None": None,
}


def _clean_expr(raw: str) -> str:
    """Strip markdown fences and leading prose from an LLM pandas expression."""
    text = raw.strip()
    if "```" in text:
        m    = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", text)
        text = m.group(1).strip() if m else text.replace("```python", "").replace("```", "").strip()
    # Take only the last non-empty line if LLM included explanation before the expression
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in reversed(lines):
        if line.startswith("df") or line.startswith("result") or line.startswith("pd."):
            return line
    return lines[-1] if lines else text


def _df_to_rows(result, limit: int = 20) -> list[dict]:
    import numpy as np
    if isinstance(result, pd.DataFrame):
        result = result.head(limit)
    elif isinstance(result, pd.Series):
        result = result.head(limit).reset_index().rename(columns={0: "value"})
    elif not isinstance(result, list):
        result = [{"result": str(result)}]
    if isinstance(result, (pd.DataFrame,)):
        records = result.to_dict("records")
    elif isinstance(result, list):
        records = result
    else:
        records = [{"result": str(result)}]
    # Stringify all values; replace NaN with empty string
    cleaned = []
    for row in records[:limit]:
        cleaned.append({
            str(k): ("" if (isinstance(v, float) and np.isnan(v)) else str(v)[:120])
            for k, v in row.items()
        })
    return cleaned


def _query_csv(file_path: str, question: str) -> tuple[list[dict], str]:
    """Answer the question by querying the CSV with pandas.

    Returns (rows, source_note) where source_note describes how the data was obtained.
    Strategy:
      1. LLM-generated pandas expression — smart, question-aware.
      2. Keyword-based pandas filter — no LLM, always returns real rows.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        return [], f"Could not read CSV: {exc}"

    cols_preview = (
        f"Columns ({len(df.columns)}): {', '.join(df.columns.tolist())}\n"
        f"Row count: {len(df)}\n"
        f"dtypes:\n{df.dtypes.to_string()}\n"
        f"Sample (first 3 rows):\n{df.head(3).to_string(index=False)}"
    )

    # ── Attempt 1: LLM-generated pandas expression ────────────────────────────
    llm_error = ""
    try:
        pandas_prompt = f"""\
You have a pandas DataFrame `df` with the following structure:
{cols_preview}

Write a SINGLE Python expression (no assignments, no imports) that answers: "{question}"
Rules:
- Must evaluate to a DataFrame, Series, or list of dicts.
- Use only `df` and `pd` — both are already available.
- Standard Python builtins (len, sum, min, max, sorted, etc.) are available.
- Return ONLY the expression — no explanation, no markdown, no comments.\
"""
        resp = _llm.invoke([HumanMessage(content=pandas_prompt)])
        expr = _clean_expr(resp.content)

        local  = {"df": df.copy(), "pd": pd}
        result = eval(expr, {"__builtins__": _SAFE_BUILTINS}, local)
        rows   = _df_to_rows(result)
        if rows:
            return rows, f"Queried {len(rows)} rows from {os.path.basename(file_path)} using AI-generated filter"
        llm_error = "LLM expression returned 0 rows"
    except Exception as exc:
        llm_error = str(exc)

    # ── Attempt 2: Keyword-based pandas filter ────────────────────────────────
    try:
        q        = question.lower()
        num_cols = df.select_dtypes(include="number").columns.tolist()
        str_cols = [c for c in df.columns if df[c].dtype == object]

        keywords_to_pattern = [
            (("flag", "risk", "suspicious", "flagged", "high risk"), "flag|high|risk|suspicious"),
            (("revenue",), "revenue|income|sales"),
            (("expense", "cost"), "expense|cost|payment"),
            (("vendor", "supplier", "payee"), "vendor|supplier|payee"),
            (("duplicate", "dup"), "duplicate|dup"),
        ]
        for triggers, pattern in keywords_to_pattern:
            if any(k in q for k in triggers):
                for col in str_cols:
                    mask = df[col].str.contains(pattern, case=False, na=False)
                    if mask.any():
                        rows = _df_to_rows(df[mask])
                        return rows, f"Filtered {len(rows)} rows matching '{pattern}' in column '{col}'"

        # Top N by largest numeric column
        if num_cols and any(k in q for k in ("top", "highest", "largest", "most", "max", "biggest")):
            n       = 10
            top_col = num_cols[0]
            # Try to find a more relevant numeric column
            for col in num_cols:
                if any(k in col.lower() for k in ("amount", "total", "payment", "value", "revenue", "sales")):
                    top_col = col
                    break
            rows = _df_to_rows(df.nlargest(n, top_col))
            return rows, f"Top {n} rows by '{top_col}'"

        # Default: first 20 rows with a note
        rows = _df_to_rows(df)
        note = f"Showing first {len(rows)} of {len(df)} rows from {os.path.basename(file_path)}"
        if llm_error:
            note += f" (AI filter failed: {llm_error[:80]})"
        return rows, note
    except Exception as exc:
        return [], f"Query failed: {exc}"


def _results_from_context(question: str, ctx: dict) -> list[dict]:
    """Build result rows from extracted document data (for non-CSV documents)."""
    q        = question.lower()
    doc_type = ctx.get("document_type", "document")
    filename = ctx.get("filename", "document")
    currency = (ctx.get("currency") or "INR").upper()

    # 1. Try audit transactions cache first
    audit = ctx.get("audit_analysis", {})
    txns  = audit.get("transactions", [])
    if txns:
        if "high" in q or "risk" in q:
            filtered = [t for t in txns if t.get("risk") == "HIGH"]
            return (filtered or txns)[:10]
        if "duplicate" in q:
            dup = [t for t in txns if "duplicate" in (t.get("flag") or "").lower()]
            return (dup or txns)[:10]
        return txns[:10]

    # 2. Key metrics table — always show, rename value_usd → value
    metrics = ctx.get("key_metrics", [])
    if metrics:
        rows = []
        for m in metrics:
            rows.append({
                "metric":   m.get("label", ""),
                "value":    m.get("value_inr") or m.get("value", ""),
                "currency": currency,
                "change":   m.get("change", "—"),
            })
        return rows

    # 3. Raw extracted numbers from LLM
    rn = ctx.get("raw_numbers") or {}
    if rn:
        rows = []
        for k, v in rn.items():
            if v is not None and v != 0:
                rows.append({"field": k.replace("_", " ").title(), "value": v, "currency": currency})
        if rows:
            return rows

    # 4. Plain insights
    insights = ctx.get("insights") or ctx.get("plain_insights") or []
    if insights:
        return [{"finding": ins} for ins in insights[:10]]

    # 5. Minimal document summary
    return [{
        "document":  filename,
        "type":      doc_type,
        "currency":  currency,
        "note":      f"'{filename}' is a {doc_type.replace('_', ' ')}. "
                     "Run Audit or Forecast to extract structured data, then query again.",
    }]


# ── Demo fallback rows (only when no document is loaded) ─────────────────────

_DEMO_RESULTS = [
    {"account": "TechSupplies Ltd",  "amount": "₹37,51,600", "risk_score": "87 — HIGH",   "flag": "Duplicate Invoice"},
    {"account": "Global Logistics",  "amount": "₹10,62,400", "risk_score": "54 — MEDIUM", "flag": "Spend Spike"},
    {"account": "DataServices Inc",  "amount": "₹73,87,000", "risk_score": "91 — HIGH",   "flag": "No PO Reference"},
    {"account": "CloudVendor Co",    "amount": "₹4,48,200",  "risk_score": "12 — LOW",    "flag": "—"},
    {"account": "InfraPartners LLC", "amount": "₹55,85,900", "risk_score": "78 — HIGH",   "flag": "Vendor Screening"},
]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/sql-agent")
async def run_sql_agent(request: SQLRequest):
    ctx          = _load_ctx()
    results:     list[dict] = []
    source_note: str        = ""
    csv_columns: list[str] | None = None

    if ctx:
        fp = ctx.get("file_path", "")
        ct = ctx.get("content_type", "")
        is_csv   = ct == "text/csv" or fp.endswith(".csv")
        is_excel = ct in (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ) or fp.endswith((".xlsx", ".xls"))

        if is_csv and os.path.exists(fp):
            results, source_note = _query_csv(fp, request.query)
            try:
                csv_columns = pd.read_csv(fp, nrows=0).columns.tolist()
            except Exception:
                pass
        elif is_excel and os.path.exists(fp):
            try:
                df      = pd.read_excel(fp)
                tmp_csv = fp + "_tmp.csv"
                df.to_csv(tmp_csv, index=False)
                results, source_note = _query_csv(tmp_csv, request.query)
                csv_columns = df.columns.tolist()
                os.remove(tmp_csv)
            except Exception:
                results, source_note = _results_from_context(request.query, ctx), "Extracted from document"

        if not results:
            results     = _results_from_context(request.query, ctx)
            source_note = "Derived from document analysis"

    if not results:
        results     = _DEMO_RESULTS
        source_note = "Demo data — upload a document to query real data"

    sql = _generate_sql(request.query, ctx, csv_columns)

    return {
        "sql":    sql,
        "results": results,
        "query":  request.query,
        "source": source_note,
        "row_count": len(results),
    }


@router.get("/sql-agent/results")
async def get_sql_results():
    ctx = _load_ctx()
    if ctx:
        return _results_from_context("all transactions", ctx)
    return _DEMO_RESULTS


@router.get("/sql-agent/schema")
async def get_db_schema():
    return DB_SCHEMA


# ── Dynamic sample queries ─────────────────────────────────────────────────────

_QUERIES_BY_TYPE: dict[str, list[str]] = {
    "invoice": [
        "Show all line items and their amounts",
        "What is the total invoice amount including taxes?",
        "List all GST components (CGST, SGST, IGST)",
        "Who is the vendor and what is the invoice date?",
        "Show payment terms and due date",
    ],
    "receipt": [
        "What is the total amount paid?",
        "Show all charges and fees in this receipt",
        "What taxes were applied?",
        "When was this payment made?",
        "Show vendor details and payment method",
    ],
    "balance_sheet": [
        "Show total assets vs total liabilities",
        "What is the current ratio (current assets / current liabilities)?",
        "List all equity components",
        "Show non-current assets breakdown",
        "What is the debt-to-equity ratio?",
    ],
    "income_statement": [
        "What is the net profit for the period?",
        "Show revenue breakdown by category",
        "What is the gross profit margin?",
        "List all operating expenses",
        "How does this period compare to the previous period?",
    ],
    "cash_flow": [
        "Show operating cash flow components",
        "What is the net change in cash?",
        "List all investing activities",
        "What are the major financing activities?",
        "Is operating cash flow positive or negative?",
    ],
    "policy": [
        "List all compliance requirements mentioned",
        "What are the key financial thresholds?",
        "Show all regulatory references (GST, Companies Act, etc.)",
        "What are the approved vendor payment terms?",
        "List all audit requirements",
    ],
    "financial_report": [
        "Show top KPIs from this report",
        "What are the key financial highlights?",
        "List all risk factors mentioned",
        "Show revenue and profit trends",
        "What are the management recommendations?",
    ],
    "transaction_data": [
        "Show top 10 transactions by amount",
        "Find all high-risk or flagged transactions",
        "Count transactions by type",
        "What is the total value of all transactions?",
        "List duplicate or suspicious entries",
    ],
}

_DEFAULT_QUERIES = [
    "Show all key metrics from this document",
    "What is the total financial value?",
    "List all important figures and amounts",
    "Show any risk or compliance issues",
    "Summarize the main financial data",
]


@router.get("/sql-agent/sample-queries")
async def get_sample_queries():
    ctx = _load_ctx()
    if not ctx:
        return {
            "queries": [
                "Show top 10 vendors by total payment amount",
                "Find all transactions with high risk score",
                "Count duplicate invoices by vendor",
                "List payments above ₹5,00,000 ordered by amount",
                "Which vendors have no approved PO reference?",
            ],
            "doc_type": None,
            "filename": None,
        }

    doc_type = ctx.get("document_type", "other")
    filename = ctx.get("filename", "document")
    currency = (ctx.get("currency") or "INR").upper()

    # Base queries from doc type
    base = list(_QUERIES_BY_TYPE.get(doc_type, _DEFAULT_QUERIES))

    # Inject actual values from key_metrics into queries
    metrics = ctx.get("key_metrics") or []
    rn      = ctx.get("raw_numbers") or {}
    company = ctx.get("company_name") or ""

    enriched = []
    for q in base[:5]:
        # Personalise with company name if available
        if company and "vendor" in q.lower():
            q = q.replace("vendor", company[:30])
        enriched.append(q)

    # Add a metric-specific query if we have real values
    if metrics:
        first = metrics[0]
        label = first.get("label", "")
        val   = first.get("value_inr") or first.get("value", "")
        if label and val:
            enriched.insert(0, f"What is the {label.lower()} and how does it compare?")
            enriched = enriched[:5]

    if rn.get("revenue") and doc_type not in ("invoice", "receipt"):
        rev = rn["revenue"]
        sym = "₹" if currency == "INR" else "$"
        enriched.insert(0, f"Show revenue breakdown — total is {sym}{rev:,.2f}")
        enriched = enriched[:5]

    return {
        "queries":  enriched,
        "doc_type": doc_type,
        "filename": filename,
    }
