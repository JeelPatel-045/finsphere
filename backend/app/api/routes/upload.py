"""
FinSphere Document Upload Route
Accepts financial documents, runs real AI extraction,
stores full context for chat to use, and returns clean analysis.
"""

import os
import re
import json

from fastapi         import APIRouter, UploadFile, File, HTTPException, Depends
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory
from app.core.database import get_db
from app.models.documents import Document
from app.models.notification import Notification

router = APIRouter(prefix="/documents")

UPLOAD_DIR          = "./uploads"
METADATA_FILE       = "./uploads/metadata.json"
ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"   # ← used by chat

ALLOWED_TYPES = {
    "application/pdf",
    "text/csv",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/plain",
}

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
_llm = get_llm(temperature=0.1, max_tokens=2048)


# ── Metadata helpers ──────────────────────────────────────────────────────────

def _load_metadata() -> list:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(METADATA_FILE):
        return []
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_metadata(records: list):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(METADATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

def _save_active_context(ctx: dict):
    """Save document context so chat can reference it."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(ACTIVE_CONTEXT_FILE, "w") as f:
        json.dump(ctx, f, indent=2)

def load_active_context() -> dict | None:
    """Load the most recently uploaded document's context."""
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


# ── Text extraction per file type ─────────────────────────────────────────────

def _text_from_pdf(path: str) -> str:
    """Extract text from PDF.
    1st attempt: pypdf text layer (fast, works for digital PDFs).
    2nd attempt: page-by-page image OCR via pymupdf (works for scanned/image PDFs).
    """
    # --- attempt 1: embedded text ---
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages  = [p.extract_text() or "" for p in reader.pages]
        text   = "\n\n".join(pages).strip()
        if text and len(text) > 100:          # got meaningful text
            return text
    except Exception:
        pass

    # --- attempt 2: OCR via pymupdf (fitz) ---
    try:
        import fitz                           # pymupdf
        import pytesseract
        from PIL import Image
        import io

        doc   = fitz.open(path)
        parts = []
        for page in doc:
            # Render at 200 DPI for good OCR accuracy
            pix  = page.get_pixmap(dpi=200)
            img  = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
            text = pytesseract.image_to_string(img, config="--psm 6")
            if text.strip():
                parts.append(text.strip())
        doc.close()
        combined = "\n\n".join(parts).strip()
        if combined:
            return combined
    except Exception:
        pass

    # --- attempt 3: try pytesseract directly on the first page as image ---
    try:
        import pytesseract
        from PIL import Image
        # Sometimes PDFs are stored as single-page images
        img  = Image.open(path).convert("L")
        text = pytesseract.image_to_string(img, config="--psm 6").strip()
        if text and len(text) > 50:
            return text
    except Exception:
        pass

    return "[No extractable text — document may be a scanned image PDF]"

def _text_from_image(path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(path).convert("L")
        return pytesseract.image_to_string(img, config="--psm 6").strip() or "[No text found in image]"
    except Exception as e:
        return f"[OCR error: {e}]"

def _text_from_csv(path: str) -> str:
    try:
        import pandas as pd
        df   = pd.read_csv(path)
        text = f"CSV — {len(df)} rows × {len(df.columns)} columns\nColumns: {', '.join(df.columns.tolist())}\n\nData:\n"
        text += df.to_string(index=False)
        num = df.select_dtypes(include="number")
        if not num.empty:
            text += f"\n\nSummary stats:\n{num.describe().to_string()}"
        return text
    except Exception as e:
        return f"[CSV error: {e}]"

def _text_from_excel(path: str) -> str:
    try:
        import pandas as pd
        xl   = pd.ExcelFile(path)
        text = f"Excel — sheets: {', '.join(xl.sheet_names)}\n\n"
        for sheet in xl.sheet_names[:3]:
            df   = pd.read_excel(path, sheet_name=sheet)
            text += f"Sheet '{sheet}':\n{df.to_string(index=False)}\n\n"
        return text
    except Exception as e:
        return f"[Excel error: {e}]"

def _text_from_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[TXT error: {e}]"


# ── Agent mapping ─────────────────────────────────────────────────────────────

def _get_agent(content_type: str, ext: str, doc_type: str) -> dict:
    ct = (content_type or "").lower()
    dt = (doc_type or "").lower()

    if ct in ("image/jpeg", "image/png") or ext in (".jpg", ".jpeg", ".png"):
        return {"name": "OCR Agent",        "icon": "🔎", "reason": "Image file — running optical character recognition"}
    if ct == "text/csv" or ext == ".csv":
        return {"name": "Data Analysis Agent", "icon": "📊", "reason": "CSV file — analysing transaction data"}
    if ct in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel") or ext in (".xlsx", ".xls"):
        return {"name": "Data Analysis Agent", "icon": "📊", "reason": "Excel file — analysing spreadsheet data"}
    if "invoice" in dt or "receipt" in dt:
        return {"name": "Invoice Audit Agent",   "icon": "🧾", "reason": "Invoice detected — running audit and GST validation"}
    if "income" in dt or "p&l" in dt or "profit" in dt or "loss" in dt:
        return {"name": "P&L Analysis Agent",    "icon": "💹", "reason": "Income statement detected — analysing profitability"}
    if "balance" in dt:
        return {"name": "Balance Sheet Agent",   "icon": "⚖️",  "reason": "Balance sheet detected — analysing financial position"}
    if "cash" in dt and "flow" in dt:
        return {"name": "Cashflow Agent",        "icon": "💧", "reason": "Cash flow statement — analysing liquidity"}
    return {"name": "Financial Document Agent",  "icon": "📄", "reason": "Financial document detected — running full AI analysis"}


# ── LLM extraction ────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """\
You are a financial document AI. Extract ALL information from this document.

Filename : {filename}
Doc type hint: {doc_type_hint}

Document content:
{text}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "document_type": "income_statement|balance_sheet|cash_flow|invoice|receipt|transaction_data|financial_report|unknown",
  "company_name": "",
  "period":       "",
  "currency":     "USD|INR|EUR",
  "summary":      "One sentence plain-English description of what this document is",

  "key_metrics": [
    {{"label": "Metric name",   "value": "$X.XXM",  "value_inr": "₹X.XX Cr", "change": "+X%", "good": true, "source": "Extracted directly from document line X"}}
  ],

  "insights": [
    "Plain English insight 1 — what this means for the business",
    "Plain English insight 2 — something worth noting",
    "Plain English insight 3 — risk or opportunity"
  ],

  "suggested_questions": [
    "Specific question relevant to THIS document",
    "Second relevant question",
    "Third relevant question",
    "Fourth relevant question"
  ],

  "risks":     ["Specific risk flag from this document"],
  "positives": ["Specific positive indicator from this document"],

  "raw_numbers": {{
    "revenue":              0.0,
    "expenses":             0.0,
    "profit":               0.0,
    "gross_margin_pct":     0.0,
    "operating_margin_pct": 0.0
  }},

  "all_extracted_data": {{}}
}}

CRITICAL RULES FOR FIELD NAME FLEXIBILITY:
- Do NOT require exact field names. Extract by MEANING, not by label.
  Examples of equivalent fields you should treat the same:
  * "vendor name" = "supplier name" = "seller" = "billed by" = "from" = "payee"
  * "buyer" = "client" = "bill to" = "customer" = "purchaser" = "sold to"
  * "invoice number" = "bill number" = "ref number" = "document number" = "order ID"
  * "due date" = "payment due" = "pay by" = "maturity date"
  * "subtotal" = "net amount" = "amount before tax"
  * "tax" = "GST" = "VAT" = "service tax" = "TDS"
  * "total" = "grand total" = "amount due" = "total payable" = "net payable"
  * "revenue" = "sales" = "income" = "turnover" = "receipts"
  * "expenses" = "costs" = "expenditure" = "outgoings" = "disbursements"
  * "profit" = "net income" = "surplus" = "earnings" = "bottom line"
- Extract EVERY field you can find — use the actual label from the document in all_extracted_data.
- key_metrics: include 5–8 of the MOST IMPORTANT numbers — use ACTUAL figures from the document.
- Amounts MUST appear in BOTH document currency AND INR crores (₹X.XX Cr), 1 USD = ₹83.
- Add a "source" field to each key_metric explaining how the value was obtained.
- insights: plain English a non-finance person can understand.
- suggested_questions: specific to THIS document's content.
- all_extracted_data: every field you can identify, using the document's own label as key.\
"""

_INVOICE_EXTRA_PROMPT = """\
This document appears to be an INVOICE, RECEIPT, or BILL.
Extract ALL of the following — using whatever labels the document uses:
  - Any reference/invoice/bill/order number
  - Seller/vendor/supplier/billed-by party name and address
  - Buyer/client/bill-to/customer party name and address
  - Each line item (description, quantity, rate/unit_price, amount)
  - Net/subtotal amount (before tax)
  - All taxes (GST, VAT, service tax, TDS, IGST, CGST, SGST — whatever is present)
  - Grand total / total payable / net payable
  - Payment terms, due date, currency
  - Any registration numbers (GSTIN, PAN, CIN, etc.)
  - Payment status if mentioned
Place all fields in all_extracted_data (using the document's own label) AND as key_metrics where relevant.
"""

def _llm_extract(raw_text: str, filename: str, doc_type_hint: str = "") -> dict:
    sample = raw_text[:8000]          # increased from 5000 → 8000 chars
    is_invoice = any(kw in doc_type_hint.lower() or kw in filename.lower()
                     for kw in ("invoice", "receipt", "bill", "voucher"))
    extra = _INVOICE_EXTRA_PROMPT if is_invoice else ""
    prompt = (EXTRACTION_PROMPT + "\n" + extra).format(
        filename=filename, doc_type_hint=doc_type_hint or "unknown", text=sample
    )
    try:
        response = _llm.invoke([HumanMessage(content=prompt)])
        content  = response.content.strip()
        if "```" in content:
            match   = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            content = match.group(1) if match else content
        jm   = re.search(r"\{[\s\S]*\}", content)
        data = json.loads(jm.group() if jm else content)
        data["filename"] = filename
        return data
    except Exception as e:
        return {
            "document_type":    "unknown",
            "filename":         filename,
            "summary":          f"Document '{filename}' uploaded. Could not auto-extract — ask questions in chat.",
            "key_metrics":      [],
            "insights":         ["Document uploaded successfully.", "Ask a question in the AI Chat to analyse this document."],
            "suggested_questions": ["What does this document contain?", "Summarise the key financial figures."],
            "risks":            [],
            "positives":        [],
            "extraction_error": str(e),
        }


# ── AI Insights generation ────────────────────────────────────────────────────

def _gen_insights(extracted: dict) -> list:
    insights = []
    risks    = extracted.get("risks", [])
    for r in risks[:3]:
        insights.append({"title": str(r)[:60], "level": "High"})
    if not insights:
        dt = str(extracted.get("document_type", "")).lower()
        insights = [
            {"title": "Document analysed by AI",    "level": "Valid"},
            {"title": "Ready for chat Q&A",          "level": "Valid"},
            {"title": "Ask questions in AI Chat",    "level": "Pending"},
        ]
    return insights[:6]


# ── Route helpers ─────────────────────────────────────────────────────────────

def _extract_doc(file_path: str, content_type: str, filename: str) -> tuple[str, dict]:
    """Returns (raw_text, extracted_fields)."""
    ct  = (content_type or "").lower()
    ext = os.path.splitext(filename)[1].lower()

    if   ct == "application/pdf" or ext == ".pdf":
        raw = _text_from_pdf(file_path)
    elif ct in ("image/jpeg", "image/png") or ext in (".jpg", ".jpeg", ".png"):
        raw = _text_from_image(file_path)
    elif ct == "text/csv" or ext == ".csv":
        raw = _text_from_csv(file_path)
    elif ct in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ) or ext in (".xlsx", ".xls"):
        raw = _text_from_excel(file_path)
    elif ct == "text/plain" or ext == ".txt":
        raw = _text_from_txt(file_path)
    else:
        raw = ""

    # Pass the filename as a doc-type hint (e.g. "invoice_q3.pdf" hints at invoice type)
    extracted = _llm_extract(raw, filename, doc_type_hint=filename)
    return raw, extracted


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400,
            detail=f"Unsupported: {file.content_type}. Allowed: PDF, CSV, Excel, PNG, JPEG, TXT")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content   = await file.read()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Real AI extraction
    raw_text, extracted = _extract_doc(file_path, file.content_type, file.filename)
    agent               = _get_agent(file.content_type,
                                      os.path.splitext(file.filename)[1].lower(),
                                      extracted.get("document_type", ""))
    insights            = _gen_insights(extracted)

    # ── Save active context for chat ──────────────────────────────────────────
    # review_checklist and audit_analysis are intentionally NOT carried over —
    # they should be regenerated fresh for the new document.
    context = {
        **extracted,
        "raw_text":     raw_text,
        "file_path":    file_path,
        "content_type": file.content_type,
        "size_bytes":   len(content),
        "agent":        agent,
    }
    _save_active_context(context)

    # ── Persist to PostgreSQL ─────────────────────────────────────────────────
    doc = Document(
        filename=file.filename,
        content_type=file.content_type,
        file_type=os.path.splitext(file.filename)[1].lower(),
        size_bytes=len(content),
        status="processed",
        document_type=extracted.get("document_type", "unknown"),
        company_name=extracted.get("company_name"),
        period=extracted.get("period"),
        summary=extracted.get("summary"),
        currency=extracted.get("currency", "USD"),
        key_metrics=extracted.get("key_metrics", []),
        insights=extracted.get("insights", []),
        risks=extracted.get("risks", []),
        positives=extracted.get("positives", []),
        raw_numbers=extracted.get("raw_numbers", {}),
        all_extracted=extracted.get("all_extracted_data", {}),
        suggested_qs=extracted.get("suggested_questions", []),
        raw_text=raw_text[:50000] if raw_text else None,
        file_path=file_path,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # ── Create notification ───────────────────────────────────────────────────
    doc_type_label = extracted.get("document_type", "document").replace("_", " ").title()
    notif = Notification(
        title=f"Document Analysed: {file.filename}",
        message=f"{doc_type_label} processed by {agent['name']}. {len(extracted.get('key_metrics', []))} metrics extracted.",
        type="success",
    )
    db.add(notif)
    db.commit()

    # Persist legacy metadata list (keeps backwards compatibility)
    records = _load_metadata()
    record  = {
        "id":            doc.id,
        "filename":      file.filename,
        "content_type":  file.content_type,
        "size_bytes":    len(content),
        "status":        "processed",
        "document_type": extracted.get("document_type", "unknown"),
    }
    records.insert(0, record)
    _save_metadata(records)

    return {
        **record,
        "message":       f"'{file.filename}' analysed by {agent['name']}.",
        "agent":         agent,
        "ocr":           extracted,
        "insights":      insights,
        "key_metrics":   extracted.get("key_metrics", []),
        "plain_insights":extracted.get("insights", []),
        "suggested_questions": extracted.get("suggested_questions", []),
        "summary":       extracted.get("summary", ""),
        "document_type": extracted.get("document_type", "unknown"),
    }


@router.get("/active-context")
def get_active_context():
    """Return the currently loaded document's context (for frontend status display)."""
    ctx = load_active_context()
    if not ctx:
        return {"loaded": False}
    return {
        "loaded":       True,
        "filename":     ctx.get("filename"),
        "document_type":ctx.get("document_type"),
        "summary":      ctx.get("summary"),
        "company_name": ctx.get("company_name"),
        "period":       ctx.get("period"),
        "key_metrics":  ctx.get("key_metrics", []),
        "agent":        ctx.get("agent"),
        "suggested_questions": ctx.get("suggested_questions", []),
        "plain_insights": ctx.get("insights", []),
    }


@router.get("")
@router.get("/list")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(50).all()
    if docs:
        return [
            {
                "id":            d.id,
                "filename":      d.filename,
                "content_type":  d.content_type,
                "size_bytes":    d.size_bytes,
                "status":        d.status,
                "document_type": d.document_type,
                "created_at":    d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ]
    return _load_metadata()


@router.get("/ocr")
def get_ocr_result():
    ctx = load_active_context()
    return ctx or {"summary": "No document uploaded yet."}


@router.get("/insights")
def get_invoice_insights():
    ctx = load_active_context()
    if not ctx:
        return []
    return _gen_insights(ctx)


# ── Smart Review Checklist ────────────────────────────────────────────────────

_CHECKLIST_PROMPT = """\
You are a senior financial reviewer with deep expertise in Indian corporate law,
taxation, and accounting standards. A document has been uploaded and you must
generate a SPECIFIC review checklist for it — every item must reference ACTUAL
data found in this document (real vendor names, invoice numbers, actual amounts,
real clause text, specific line items).

=== DOCUMENT ===
File        : {filename}
Type        : {doc_type}
Company     : {company}
Period      : {period}
Summary     : {summary}

Key Metrics : {metrics}
Extracted   : {extracted}
Raw Text    : {raw_text}
=== END ===

CHECKS TO PERFORM BY DOCUMENT TYPE:

INVOICE / RECEIPT:
  - GSTIN format and state code match between seller and buyer
  - HSN/SAC codes present on all line items
  - Tax type: IGST for inter-state (different state codes), CGST+SGST for intra-state
  - PO reference number (mandatory for payments > ₹50,000 per standard policy)
  - Authorised signatory / approver field filled
  - Bank account type: savings account is suspicious for business; must be current account
  - Invoice date: weekend/public holiday dates are unusual
  - Duplicate invoice number risk (flag if number looks sequential or reused)
  - Round-number amounts (exact round figures are a statistical fraud indicator)
  - Vendor address type (residential address for a business entity is a red flag)
  - Payment terms and due date reasonableness
  - Email domain (free Gmail/Yahoo for a business entity is suspicious)

ACCOUNTING POLICY / COMPLIANCE DOCUMENT:
  - Revenue recognition: Ind AS 115 (not superseded Ind AS 18 / IAS 18)
  - Lease accounting: Ind AS 116 (not superseded IAS 17 / Ind AS 17)
  - Depreciation — Computers: Schedule II = 33.33% / 3 years (not 20% / 5 years)
  - Depreciation — Plant & Machinery: Schedule II = 6.67% / 15 years (not 15% / 10 years)
  - GST registration threshold: ₹40 lakhs for goods (not ₹50 lakhs)
  - GSTR-9 annual return due: 31 December (not 31 October)
  - TDS Section 194J professional fees: 10% (not 7.5%)
  - TDS Section 194I rent: 10% (not 15%)
  - Advance tax 1st instalment: 15 June (not 15 July)
  - MSME payment period: 45 days (not 60 days per MSMED Act 2006)
  - Audit committee threshold: paid-up capital ≥ ₹10 crores (not ₹5 crores)
  - Materiality threshold consistency across sections

BALANCE SHEET / FINANCIAL STATEMENTS:
  - Schedule III format compliance (Companies Act 2013)
  - Current ratio (current assets / current liabilities — should be > 1)
  - Debt-equity ratio (flag if > 2)
  - Related party transaction disclosures (Companies Act 2013 Sec 188)
  - Depreciation rates vs Companies Act Schedule II
  - Going concern indicators
  - CARO 2020 reporting requirements

CSV / TRANSACTION DATA:
  - Duplicate transaction IDs or amounts on same date
  - Missing required fields (amount, date, category)
  - Statistical outliers (amounts 3+ standard deviations from mean)
  - Round-number concentration
  - Weekend/holiday transactions at unusual volumes

Return ONLY valid JSON (no markdown, no explanation):
{{
  "document_type": "invoice|policy|balance_sheet|income_statement|transaction_data|other",
  "review_score": <0-100>,
  "score_label": "Excellent|Good|Needs Attention|At Risk|Critical",
  "summary": "One-sentence assessment referencing the actual document",
  "priority_actions": [
    "Specific urgent action referencing actual document data",
    "Second specific urgent action"
  ],
  "checklist": [
    {{
      "id": "chk-001",
      "category": "GST & Tax Compliance|Documentation|Fraud Indicators|Accounting Standards|Corporate Law|Data Quality",
      "title": "Short check title (max 8 words)",
      "detail": "Specific finding with ACTUAL data from the document — vendor name, amount, clause text, etc.",
      "status": "pass|warn|fail|info",
      "severity": "critical|high|medium|low|info",
      "regulation": "e.g. GST Act 2017 Sec 16 | Ind AS 115 | Schedule II | MSMED Act 2006 | SA 240",
      "action": "What the user should do to resolve or verify this"
    }}
  ]
}}

Rules:
- Every fail/warn item MUST quote actual data from the document.
- Pass items should confirm what is correct with the actual value.
- Minimum 6 checklist items, maximum 15.
- review_score: 100 = perfect, 0 = critical failure. Deduct heavily for critical/high items.
- Only flag violations you can actually see evidence of in the document text.\
"""


def _gen_review_checklist(ctx: dict) -> dict | None:
    prompt = _CHECKLIST_PROMPT.format(
        filename=ctx.get("filename", "unknown"),
        doc_type=ctx.get("document_type", "unknown").replace("_", " "),
        company=ctx.get("company_name", "Unknown"),
        period=ctx.get("period", "N/A"),
        summary=ctx.get("summary", ""),
        metrics=json.dumps(ctx.get("key_metrics", []), indent=2)[:1200],
        extracted=json.dumps(ctx.get("all_extracted_data", {}), indent=2)[:2000],
        raw_text=ctx.get("raw_text", "")[:4000],
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


_CHECKLIST_FALLBACK: dict = {
    "document_type": "unknown",
    "review_score":  0,
    "score_label":   "No Document",
    "summary":       "No document loaded. Upload a financial document to generate a review checklist.",
    "priority_actions": [],
    "checklist": [],
}


@router.get("/review-checklist")
def get_review_checklist(refresh: bool = False):
    """
    Return a document-type-specific review checklist with pass/warn/fail status.
    Generated by the LLM on first call; cached in active_context.json on subsequent calls.
    Pass ?refresh=true to force regeneration.
    """
    ctx = load_active_context()
    if not ctx:
        return _CHECKLIST_FALLBACK.copy()

    if not refresh:
        cached = ctx.get("review_checklist")
        if cached and cached.get("checklist"):
            return cached

    result = _gen_review_checklist(ctx)
    if result and result.get("checklist"):
        ctx["review_checklist"] = result
        _save_active_context(ctx)
        return result

    return _CHECKLIST_FALLBACK.copy()
