"""
Generate FinSphere sample data:
  - uploads/sample_transactions.csv      (500 rows)
  - uploads/sample_vendor_payments.csv   (200 rows)
  - uploads/sample_quarterly_pnl.csv     (quarterly P&L, 3 years)
  - uploads/sample_invoice_TechNova.pdf
  - uploads/sample_invoice_GlobalLogistics.pdf
"""

import csv
import random
import os
from datetime import date, timedelta
from fpdf import FPDF

random.seed(42)
UPLOAD_DIR = "./uploads"

# ── helpers ──────────────────────────────────────────────────────────────────

def rand_date(start: date, end: date) -> str:
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")

def fmt_inr(amount: float) -> str:
    return f"INR{amount:,.2f}"

def fmt_usd(amount: float) -> str:
    return f"${amount:,.2f}"


# ══════════════════════════════════════════════════════════════════════════════
# 1.  TRANSACTIONS  (500 rows)
# ══════════════════════════════════════════════════════════════════════════════

ACCOUNTS = [
    "TechSupplies Ltd", "Global Logistics Inc", "DataServices Corp",
    "CloudVendor Co", "InfraPartners LLC", "OfficeMax India",
    "ServerStack Pvt Ltd", "Zenith Analytics", "Apex Consulting",
    "BlueSky Networks", "ClearPath Finance", "Digital Horizon",
    "EduTech Solutions", "Frontier Systems", "GreenOps Ltd",
]

TRANSACTION_TYPES = [
    "Vendor Payment", "Payroll", "Utilities", "Rent", "Marketing",
    "Travel & Expense", "Subscription", "Professional Services",
    "IT Infrastructure", "Office Supplies", "Insurance", "Tax Payment",
]

FLAGS = [None, None, None, None, None,   # 5/8 unflagged
         "Duplicate Invoice", "No PO Reference", "Spend Spike",
]

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]

START = date(2023, 1, 1)
END   = date(2025, 3, 31)

transactions = []
for i in range(1, 501):
    account  = random.choice(ACCOUNTS)
    tx_type  = random.choice(TRANSACTION_TYPES)
    amount   = round(random.uniform(500, 150_000), 2)
    risk     = random.randint(5, 99)
    flag     = random.choice(FLAGS)
    txdate   = rand_date(START, END)
    quarter  = QUARTERS[(int(txdate[5:7]) - 1) // 3]
    approved = random.choice(["Jeel Patel", "Harshil Kaneria", "Priya Shah", "Rahul Mehta", "Auto-Approved"])

    transactions.append({
        "id":               i,
        "date":             txdate,
        "account_name":     account,
        "transaction_type": tx_type,
        "amount_inr":       round(amount * 83, 2),
        "amount_usd":       amount,
        "quarter":          quarter,
        "risk_score":       risk,
        "risk_level":       "HIGH" if risk >= 75 else ("MEDIUM" if risk >= 40 else "LOW"),
        "flag":             flag or "",
        "approved_by":      approved,
        "status":           random.choice(["Cleared", "Cleared", "Cleared", "Pending", "Under Review"]),
        "reference_no":     f"TXN-{2023 + (i % 3)}-{i:05d}",
    })

with open(f"{UPLOAD_DIR}/sample_transactions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
    writer.writeheader()
    writer.writerows(transactions)

print("✓ sample_transactions.csv — 500 rows")


# ══════════════════════════════════════════════════════════════════════════════
# 2.  VENDOR PAYMENTS  (200 rows)
# ══════════════════════════════════════════════════════════════════════════════

VENDORS = [
    ("TechSupplies Ltd",    "India",         "IT Hardware"),
    ("Global Logistics Inc","Singapore",     "Logistics"),
    ("DataServices Corp",   "USA",           "Data Services"),
    ("CloudVendor Co",      "USA",           "Cloud"),
    ("InfraPartners LLC",   "UK",            "Infrastructure"),
    ("Zenith Analytics",    "India",         "Analytics"),
    ("Apex Consulting",     "India",         "Consulting"),
    ("BlueSky Networks",    "Germany",       "Networking"),
    ("ClearPath Finance",   "India",         "Finance"),
    ("Digital Horizon",     "UAE",           "Software"),
    ("Frontier Systems",    "India",         "IT Services"),
    ("GreenOps Ltd",        "Netherlands",  "Operations"),
    ("Pacific Rim Exports", "Japan",         "Export"),
    ("NorthStar Solutions", "Canada",        "HR Services"),
    ("SilverBridge Corp",   "India",         "Bridge Finance"),
]

vendor_payments = []
for i in range(1, 201):
    v_name, country, category = random.choice(VENDORS)
    payment  = round(random.uniform(5_000, 500_000), 2)
    risk_val = random.randint(5, 95)
    invoices = random.randint(1, 12)
    has_po   = random.choice([True, True, True, False])   # 75% have PO
    late     = random.choice([False, False, False, True]) # 25% late

    vendor_payments.append({
        "vendor_id":          f"V-{i:04d}",
        "vendor_name":        v_name,
        "category":           category,
        "country":            country,
        "total_payment_inr":  round(payment * 83, 2),
        "total_payment_usd":  payment,
        "invoice_count":      invoices,
        "avg_payment_inr":    round((payment * 83) / invoices, 2),
        "risk_level":         "HIGH" if risk_val >= 75 else ("MEDIUM" if risk_val >= 40 else "LOW"),
        "risk_score":         risk_val,
        "has_po_reference":   has_po,
        "late_payment":       late,
        "last_payment_date":  rand_date(date(2024, 1, 1), date(2025, 3, 31)),
        "payment_terms":      random.choice(["Net 30", "Net 45", "Net 60", "Immediate"]),
        "compliance_status":  "COMPLIANT" if (has_po and not late) else "NON-COMPLIANT",
    })

with open(f"{UPLOAD_DIR}/sample_vendor_payments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=vendor_payments[0].keys())
    writer.writeheader()
    writer.writerows(vendor_payments)

print("✓ sample_vendor_payments.csv — 200 rows")


# ══════════════════════════════════════════════════════════════════════════════
# 3.  QUARTERLY P&L  (12 quarters × metrics)
# ══════════════════════════════════════════════════════════════════════════════

quarters_list = []
revenue_base  = 8_500_000
for yr in range(2022, 2025):
    for q in range(1, 5):
        if yr == 2025 and q > 1:
            break
        growth  = random.uniform(0.03, 0.12)
        revenue = round(revenue_base * (1 + growth), 2)
        cogs    = round(revenue * random.uniform(0.38, 0.45), 2)
        gross   = round(revenue - cogs, 2)
        opex    = round(revenue * random.uniform(0.22, 0.30), 2)
        ebitda  = round(gross - opex, 2)
        depn    = round(revenue * 0.04, 2)
        ebit    = round(ebitda - depn, 2)
        interest= round(revenue * random.uniform(0.01, 0.03), 2)
        ebt     = round(ebit - interest, 2)
        tax     = round(ebt * 0.25, 2) if ebt > 0 else 0
        net_inc = round(ebt - tax, 2)

        quarters_list.append({
            "period":               f"Q{q} {yr}",
            "year":                 yr,
            "quarter":              f"Q{q}",
            "revenue_inr":          round(revenue * 83, 2),
            "revenue_usd":          revenue,
            "cogs_inr":             round(cogs * 83, 2),
            "gross_profit_inr":     round(gross * 83, 2),
            "gross_margin_pct":     round((gross / revenue) * 100, 2),
            "operating_expenses_inr": round(opex * 83, 2),
            "ebitda_inr":           round(ebitda * 83, 2),
            "ebitda_margin_pct":    round((ebitda / revenue) * 100, 2),
            "depreciation_inr":     round(depn * 83, 2),
            "ebit_inr":             round(ebit * 83, 2),
            "interest_expense_inr": round(interest * 83, 2),
            "ebt_inr":              round(ebt * 83, 2),
            "tax_inr":              round(tax * 83, 2),
            "net_income_inr":       round(net_inc * 83, 2),
            "net_margin_pct":       round((net_inc / revenue) * 100, 2),
            "yoy_revenue_growth_pct": round(growth * 100, 2),
        })
        revenue_base = revenue

with open(f"{UPLOAD_DIR}/sample_quarterly_pnl.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=quarters_list[0].keys())
    writer.writeheader()
    writer.writerows(quarters_list)

print("✓ sample_quarterly_pnl.csv — 12 quarters")


# ══════════════════════════════════════════════════════════════════════════════
# 4.  INVOICE PDFs
# ══════════════════════════════════════════════════════════════════════════════

class InvoicePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(False)

    def header_bar(self, company: str, tagline: str, color: tuple):
        self.set_fill_color(*color)
        self.rect(0, 0, 210, 38, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 22)
        self.set_xy(12, 8)
        self.cell(0, 10, company, ln=True)
        self.set_font("Helvetica", "", 10)
        self.set_x(12)
        self.cell(0, 6, tagline)
        self.set_text_color(0, 0, 0)

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(240, 240, 240)
        self.set_x(12)
        self.cell(186, 7, f"  {title}", fill=True, ln=True)
        self.ln(2)

    def kv(self, label: str, value: str, x: float = 12, w: float = 55):
        self.set_font("Helvetica", "B", 9)
        self.set_x(x)
        self.cell(w, 6, label + ":", ln=False)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, value, ln=True)

    def table_header(self, cols: list, widths: list):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(30, 64, 175)
        self.set_text_color(255, 255, 255)
        self.set_x(12)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, border=0, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)

    def table_row(self, values: list, widths: list, fill: bool = False):
        self.set_font("Helvetica", "", 9)
        self.set_fill_color(248, 250, 252) if fill else self.set_fill_color(255, 255, 255)
        self.set_x(12)
        for val, w in zip(values, widths):
            self.cell(w, 7, str(val), border=0, fill=True, align="C")
        self.ln()

    def total_row(self, label: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.set_x(12)
        self.cell(148, 7, label, align="R")
        self.cell(38, 7, value, align="R", ln=True)


# ── Invoice 1: TechNova Solutions → Apex Financial Services ──────────────────

pdf = InvoicePDF()
pdf.add_page()

pdf.header_bar("TechNova Solutions Pvt Ltd", "Enterprise Software & Cloud Services", (15, 52, 96))

pdf.set_xy(12, 44)
pdf.set_font("Helvetica", "B", 18)
pdf.set_text_color(15, 52, 96)
pdf.cell(100, 10, "TAX INVOICE", ln=False)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.set_x(130)
pdf.cell(0, 6, "Invoice No:  INV-2025-00847", ln=True)
pdf.set_x(130)
pdf.cell(0, 6, "Invoice Date:  15 April 2025", ln=True)
pdf.set_x(130)
pdf.cell(0, 6, "Due Date:  15 May 2025", ln=True)
pdf.set_x(130)
pdf.cell(0, 6, "PO Reference:  PO-APX-2025-114", ln=True)

pdf.set_text_color(0, 0, 0)
pdf.ln(4)
pdf.section_title("SELLER / BILLED BY")
pdf.kv("Company",   "TechNova Solutions Pvt Ltd")
pdf.kv("Address",   "Unit 4B, Cyber Park, Whitefield, Bengaluru -560066")
pdf.kv("GSTIN",     "29AABCT1234F1ZX")
pdf.kv("PAN",       "AABCT1234F")
pdf.kv("Email",     "billing@technova.in")
pdf.kv("Phone",     "+91-80-4567-8900")

pdf.ln(3)
pdf.section_title("BUYER / BILL TO")
pdf.kv("Company",   "Apex Financial Services Ltd")
pdf.kv("Address",   "12th Floor, One BKC, Bandra Kurla Complex, Mumbai -400051")
pdf.kv("GSTIN",     "27AAACA5678B2ZY")
pdf.kv("Contact",   "Jeel Patel  |  jeel.patel@apexfinancial.in")

pdf.ln(3)
pdf.section_title("LINE ITEMS")

cols   = ["#", "Description", "HSN/SAC", "Qty", "Unit Price (INR)", "Discount", "Amount (INR)"]
widths = [10,   68,             22,        12,    28,               18,          28]

pdf.table_header(cols, widths)

line_items = [
    (1, "Cloud Platform Licence (Annual)",        "998315", 1,  "4,25,000.00", "0%",     "4,25,000.00"),
    (2, "AI Analytics Module -Standard",         "998315", 1,  "2,80,000.00", "5%",     "2,66,000.00"),
    (3, "API Integration & Setup (Professional)", "998316", 1,  "95,000.00",   "0%",     "95,000.00"),
    (4, "24x7 Premium Support (12 months)",       "998314", 12, "8,500.00",    "0%",     "1,02,000.00"),
    (5, "Data Migration Services (one-time)",     "998316", 1,  "55,000.00",   "10%",    "49,500.00"),
]

for i, row in enumerate(line_items):
    pdf.table_row(row, widths, fill=(i % 2 == 0))

pdf.ln(2)
subtotal  = 9_37_500.00
cgst      = 84_375.00
sgst      = 84_375.00
total     = 11_06_250.00

pdf.total_row("Subtotal",          "INR 9,37,500.00")
pdf.total_row("CGST @ 9%",         "INR   84,375.00")
pdf.total_row("SGST @ 9%",         "INR   84,375.00")
pdf.set_fill_color(15, 52, 96)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Helvetica", "B", 11)
pdf.set_x(12)
pdf.cell(148, 9, "TOTAL AMOUNT DUE", fill=True, align="R")
pdf.cell(38, 9, "INR11,06,250.00", fill=True, align="R", ln=True)
pdf.set_text_color(0, 0, 0)

pdf.ln(4)
pdf.set_font("Helvetica", "B", 9)
pdf.set_x(12)
pdf.cell(0, 6, "Amount in Words:  Eleven Lakh Six Thousand Two Hundred and Fifty Rupees Only", ln=True)

pdf.ln(3)
pdf.section_title("BANK DETAILS")
pdf.kv("Bank Name",    "HDFC Bank Ltd")
pdf.kv("Account Name", "TechNova Solutions Pvt Ltd")
pdf.kv("Account No",   "50200012345678")
pdf.kv("IFSC Code",    "HDFC0001234")
pdf.kv("Branch",       "Whitefield, Bengaluru")

pdf.ln(3)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(120, 120, 120)
pdf.set_x(12)
pdf.multi_cell(186, 5, (
    "Terms & Conditions: Payment due within 30 days of invoice date. Late payment attracts 1.5% per month. "
    "This is a computer-generated invoice and does not require a physical signature. "
    "Subject to Bengaluru jurisdiction. GSTIN registered under Karnataka."
))

path1 = f"{UPLOAD_DIR}/sample_invoice_TechNova.pdf"
pdf.output(path1)
print(f"✓ {path1}")


# ── Invoice 2: Global Logistics India → FinSphere Enterprises ────────────────

pdf2 = InvoicePDF()
pdf2.add_page()

pdf2.header_bar("Global Logistics India Pvt Ltd",
                "Freight Forwarding | Customs Clearance | Last-Mile Delivery",
                (5, 105, 92))

pdf2.set_xy(12, 44)
pdf2.set_font("Helvetica", "B", 18)
pdf2.set_text_color(5, 105, 92)
pdf2.cell(100, 10, "COMMERCIAL INVOICE", ln=False)
pdf2.set_font("Helvetica", "", 10)
pdf2.set_text_color(100, 100, 100)
pdf2.set_x(128)
pdf2.cell(0, 6, "Bill Number:  GLI-INV-BOM-20250389",  ln=True)
pdf2.set_x(128)
pdf2.cell(0, 6, "Bill Date:  22 March 2025",           ln=True)
pdf2.set_x(128)
pdf2.cell(0, 6, "Payment Due:  21 April 2025",         ln=True)
pdf2.set_x(128)
pdf2.cell(0, 6, "Order ID:  ORD-FS-2025-089",          ln=True)

pdf2.set_text_color(0, 0, 0)
pdf2.ln(4)
pdf2.section_title("FROM (SUPPLIER / SELLER)")
pdf2.kv("Company",   "Global Logistics India Pvt Ltd")
pdf2.kv("Address",   "Warehouse 7, JNPT Road, Nhava Sheva, Navi Mumbai -400707")
pdf2.kv("GSTIN",     "27AABCG4567H1ZP")
pdf2.kv("Email",     "accounts@globallogistics.in")
pdf2.kv("Phone",     "+91-22-6789-0123")

pdf2.ln(3)
pdf2.section_title("TO (CLIENT / PURCHASER / SOLD TO)")
pdf2.kv("Company",   "FinSphere Enterprises Pvt Ltd")
pdf2.kv("Address",   "Office 901, Pinnacle Tower, SG Highway, Ahmedabad -380054")
pdf2.kv("GSTIN",     "24AABCF9012K1ZQ")
pdf2.kv("Contact",   "Harshil Kaneria  |  procurement@finsphere.ai")

pdf2.ln(3)
pdf2.section_title("SHIPMENT DETAILS")
pdf2.kv("Origin",      "Mumbai (BOM)")
pdf2.kv("Destination", "Ahmedabad (AMD)")
pdf2.kv("Mode",        "Road Freight -Full Truck Load (FTL)")
pdf2.kv("AWB / LR No", "GLI-LR-2025-44892")
pdf2.kv("Gross Weight","1,240 kg")

pdf2.ln(3)
pdf2.section_title("CHARGES")

cols2   = ["#", "Service Description",              "SAC",   "Qty", "Rate (INR)",   "Amount (INR)"]
widths2 = [10,   80,                                  20,      12,    32,           32]

pdf2.table_header(cols2, widths2)

items2 = [
    (1, "Full Truck Load (FTL) Mumbai-Ahmedabad",  "996511", 1,  "28,500.00",  "28,500.00"),
    (2, "Fuel Surcharge (12%)",                   "996511", 1,  "3,420.00",   "3,420.00"),
    (3, "Loading & Unloading Charges",            "996719", 2,  "1,800.00",   "3,600.00"),
    (4, "Transit Insurance (0.25% of cargo val)", "997134", 1,  "2,250.00",   "2,250.00"),
    (5, "Customs Documentation Fee",              "998399", 1,  "1,500.00",   "1,500.00"),
    (6, "Door Delivery -Last Mile",              "996511", 1,  "4,200.00",   "4,200.00"),
]

for i, row in enumerate(items2):
    pdf2.table_row(row, widths2, fill=(i % 2 == 0))

pdf2.ln(2)
pdf2.total_row("Subtotal",         "INR 43,470.00")
pdf2.total_row("IGST @ 18%",       "INR  7,824.60")
pdf2.set_fill_color(5, 105, 92)
pdf2.set_text_color(255, 255, 255)
pdf2.set_font("Helvetica", "B", 11)
pdf2.set_x(12)
pdf2.cell(148, 9, "TOTAL PAYABLE", fill=True, align="R")
pdf2.cell(38,  9, "INR51,294.60",   fill=True, align="R", ln=True)
pdf2.set_text_color(0, 0, 0)

pdf2.ln(4)
pdf2.set_font("Helvetica", "B", 9)
pdf2.set_x(12)
pdf2.cell(0, 6, "Amount in Words:  Fifty-One Thousand Two Hundred and Ninety-Four Rupees and Sixty Paise Only", ln=True)

pdf2.ln(3)
pdf2.section_title("PAYMENT DETAILS")
pdf2.kv("Bank",          "ICICI Bank Ltd")
pdf2.kv("Account Name",  "Global Logistics India Pvt Ltd")
pdf2.kv("Account No",    "012345678901")
pdf2.kv("IFSC",          "ICIC0000123")
pdf2.kv("UPI",           "globallogistics@icici")

pdf2.ln(3)
pdf2.set_font("Helvetica", "I", 8)
pdf2.set_text_color(120, 120, 120)
pdf2.set_x(12)
pdf2.multi_cell(186, 5, (
    "E&OE -Errors and Omissions Excepted. Goods once dispatched will not be accepted back without prior written "
    "approval. In case of damage during transit, claims must be filed within 48 hours of delivery. "
    "Interest @ 2% per month will be charged on overdue amounts. Subject to Mumbai jurisdiction."
))

path2 = f"{UPLOAD_DIR}/sample_invoice_GlobalLogistics.pdf"
pdf2.output(path2)
print(f"✓ {path2}")

print("\nAll sample data generated successfully.")
