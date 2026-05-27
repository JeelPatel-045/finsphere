"""
FinSphere OCR Agent
Extracts ALL structured fields from financial documents using OCR + LLM.
Supports: PDF, PNG, JPEG, TXT, CSV, XLSX
"""

import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.llm import llm


# ── Amount formatting helpers ─────────────────────────────────────────────────

USD_TO_INR = 83.0

def _parse_amount(val) -> float | None:
    """Parse any amount string/number to float."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    # strip currency symbols, commas
    cleaned = re.sub(r"[₹$€£,\s]", "", str(val))
    try:
        return float(cleaned)
    except ValueError:
        return None

def format_millions(amount_usd: float) -> dict:
    """Return both USD millions and INR crore formatted strings."""
    amount_inr = amount_usd * USD_TO_INR
    crore      = amount_inr / 10_000_000
    lakh       = amount_inr / 100_000

    if amount_usd >= 1_000_000:
        usd_str = f"${amount_usd / 1_000_000:.2f}M"
    elif amount_usd >= 1_000:
        usd_str = f"${amount_usd / 1_000:.1f}K"
    else:
        usd_str = f"${amount_usd:,.2f}"

    if crore >= 1:
        inr_str = f"₹{crore:.2f} Cr"
    elif lakh >= 1:
        inr_str = f"₹{lakh:.2f} L"
    else:
        inr_str = f"₹{amount_inr:,.0f}"

    return {"usd": usd_str, "inr": inr_str, "raw_usd": amount_usd, "raw_inr": amount_inr}


# ── Text extraction per file type ─────────────────────────────────────────────

def _extract_text_from_pdf(file_path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages  = [page.extract_text() or "" for page in reader.pages]
        text   = "\n\n".join(pages).strip()
        return text if text else "[PDF has no extractable text — may be scanned image]"
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def _extract_text_from_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
        image = Image.open(file_path)
        # Improve accuracy: convert to greyscale
        image = image.convert("L")
        text  = pytesseract.image_to_string(image, config="--psm 6")
        return text.strip() if text.strip() else "[No text found in image]"
    except Exception as e:
        return f"[Image OCR error: {e}]"


def _extract_text_from_csv(file_path: str) -> str:
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        summary = f"CSV with {len(df)} rows × {len(df.columns)} columns.\n"
        summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
        summary += "First 5 rows:\n"
        summary += df.head(5).to_string(index=False)
        # Stats for numeric columns
        numeric = df.select_dtypes(include="number")
        if not numeric.empty:
            summary += "\n\nNumeric summary:\n"
            summary += numeric.describe().to_string()
        return summary
    except Exception as e:
        return f"[CSV parse error: {e}]"


def _extract_text_from_excel(file_path: str) -> str:
    try:
        import pandas as pd
        xl   = pd.ExcelFile(file_path)
        text = f"Excel workbook with sheets: {', '.join(xl.sheet_names)}\n\n"
        for sheet in xl.sheet_names[:3]:        # max 3 sheets
            df   = pd.read_excel(file_path, sheet_name=sheet)
            text += f"--- Sheet: {sheet} ({len(df)} rows × {len(df.columns)} cols) ---\n"
            text += f"Columns: {', '.join(str(c) for c in df.columns)}\n"
            text += df.head(5).to_string(index=False) + "\n\n"
        return text
    except Exception as e:
        return f"[Excel parse error: {e}]"


def _extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[TXT read error: {e}]"


# ── LLM field extraction ──────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are a financial document AI. Extract ALL available structured information from this document.

Document type: {doc_type}
Document text:
{text}

Return ONLY a valid JSON object (no markdown, no explanation) with every field you can identify.

For an INVOICE / RECEIPT, extract:
- vendor_name, vendor_address, vendor_phone, vendor_email, vendor_gstin
- invoice_number, po_number, reference_number, bill_of_lading
- invoice_date, due_date, payment_terms, payment_status
- currency (USD/INR/etc)
- subtotal, discount, tax_rate, tax_amount, total_amount
- total_usd (convert if INR: divide by 83), total_inr (convert if USD: multiply by 83)
- total_millions_usd (e.g. "$0.05M"), total_millions_inr (e.g. "₹3.75 L")
- line_items: array of {{description, quantity, unit_price_usd, unit_price_inr, total_usd, total_inr}}
- bank_name, account_number, ifsc_code, swift_code, iban
- buyer_name, buyer_address, buyer_gstin
- notes, special_instructions

For a CSV / EXCEL DATA FILE, extract:
- file_type: "data_table"
- total_rows, total_columns
- columns: array of column names
- date_range (if any date column found)
- total_transactions (count)
- total_amount_usd, total_amount_inr, total_millions_usd, total_millions_inr
- top_vendors: array (if vendor column found)
- risk_summary (if risk column found)
- data_preview: first 3 rows as array of objects

For any FINANCIAL REPORT / CONTRACT, extract:
- document_title, parties_involved
- effective_date, expiry_date
- key_financial_terms, payment_schedule
- total_contract_value_usd, total_contract_value_inr
- milestones (array)

Always include:
- document_type: "invoice" | "receipt" | "data_table" | "contract" | "report" | "unknown"
- confidence_score: 0.0-1.0 (how confident you are in extraction quality)
- key_risks: array of strings (any financial risk flags)
- summary: one-sentence document summary

For ALL monetary amounts, express as both USD and INR millions/crores."""

def _llm_extract(raw_text: str, doc_type: str, filename: str) -> dict:
    """Use LLM to extract all structured fields from raw text."""
    # Truncate if too long (keep first 4000 chars for speed)
    text_sample = raw_text[:4000] if len(raw_text) > 4000 else raw_text

    prompt = EXTRACTION_PROMPT.format(doc_type=doc_type, text=text_sample)

    try:
        response = llm.invoke(prompt)
        content  = response.content.strip()

        # Strip markdown fences if present
        if "```" in content:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            content = match.group(1) if match else content

        # Find JSON object in response
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(content)

        data["filename"]  = filename
        data["raw_text_preview"] = raw_text[:300] if raw_text else ""
        return data

    except Exception as e:
        return {
            "document_type":     doc_type,
            "filename":          filename,
            "extraction_error":  str(e),
            "raw_text_preview":  raw_text[:500] if raw_text else "",
            "confidence_score":  0.0,
            "summary":           f"Extracted from {filename} — manual review recommended.",
            "key_risks":         [],
        }


# ── Public interface ──────────────────────────────────────────────────────────

def ocr_agent(file_path: str, content_type: str = "", filename: str = "") -> dict:
    """
    Route to the right extraction method based on file type.
    Returns a rich structured JSON with ALL extracted fields.
    """
    fname    = filename or os.path.basename(file_path)
    ct_lower = (content_type or "").lower()
    ext      = os.path.splitext(fname)[1].lower()

    # ── PDF ──────────────────────────────────────────────────────────────────
    if ct_lower == "application/pdf" or ext == ".pdf":
        raw_text = _extract_text_from_pdf(file_path)
        return _llm_extract(raw_text, "invoice_or_report", fname)

    # ── Images ───────────────────────────────────────────────────────────────
    elif ct_lower in ("image/jpeg", "image/png") or ext in (".jpg", ".jpeg", ".png"):
        raw_text = _extract_text_from_image(file_path)
        return _llm_extract(raw_text, "invoice_or_receipt", fname)

    # ── CSV ──────────────────────────────────────────────────────────────────
    elif ct_lower == "text/csv" or ext == ".csv":
        raw_text = _extract_text_from_csv(file_path)
        return _llm_extract(raw_text, "data_table", fname)

    # ── Excel ─────────────────────────────────────────────────────────────────
    elif ct_lower in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ) or ext in (".xlsx", ".xls"):
        raw_text = _extract_text_from_excel(file_path)
        return _llm_extract(raw_text, "data_table", fname)

    # ── Plain text ────────────────────────────────────────────────────────────
    elif ct_lower == "text/plain" or ext == ".txt":
        raw_text = _extract_text_from_txt(file_path)
        return _llm_extract(raw_text, "financial_document", fname)

    else:
        return {
            "document_type":    "unknown",
            "filename":         fname,
            "extraction_error": f"Unsupported file type: {content_type}",
            "confidence_score": 0.0,
            "summary":          "File type not supported for extraction.",
            "key_risks":        [],
        }
