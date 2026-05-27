"""
Generate a suspicious / potentially fraudulent invoice for FinSphere risk-detection testing.

Red flags embedded:
  1.  Duplicate invoice number  (same as a real invoice: INV-2025-00847)
  2.  Missing / invalid PO reference  ("N/A")
  3.  Fake / unverifiable GSTIN format
  4.  Round-number amounts (classic fraud indicator)
  5.  Vague line-item descriptions ("Consultancy Services", "Miscellaneous Charges")
  6.  Vendor address is a residential area, not commercial
  7.  Payment routed to a personal savings account (not a current account)
  8.  Invoice date is a Sunday
  9.  Amount is 10x higher than previous invoices from same vendor
 10.  "Approved by" field is blank
 11.  No HSN/SAC codes on line items
 12.  Inconsistent tax: claims IGST but both parties are in the same state (Maharashtra)
"""

import os
from fpdf import FPDF

UPLOAD_DIR = "./uploads"


class SuspiciousPDF(FPDF):
    def header_bar(self, company, tagline, color):
        self.set_fill_color(*color)
        self.rect(0, 0, 210, 36, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 20)
        self.set_xy(12, 7)
        self.cell(0, 9, company, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_x(12)
        self.cell(0, 6, tagline)
        self.set_text_color(0, 0, 0)

    def section_bar(self, title, warn=False):
        self.ln(3)
        if warn:
            self.set_fill_color(180, 30, 30)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(235, 235, 235)
            self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 9)
        self.set_x(12)
        self.cell(186, 7, f"  {title}", fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def kv(self, label, value, bold_value=False):
        self.set_font("Helvetica", "B", 9)
        self.set_x(12)
        self.cell(55, 6, label + ":", new_x="RIGHT", new_y="TOP")
        self.set_font("Helvetica", "B" if bold_value else "", 9)
        self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")

    def flag_note(self, text):
        self.set_fill_color(255, 243, 205)
        self.set_draw_color(200, 150, 0)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 70, 0)
        self.set_x(12)
        self.multi_cell(186, 5, f"  [!]  {text}", border=1, fill=True,
                        new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.ln(1)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(100, 20, 20)
        self.set_text_color(255, 255, 255)
        self.set_x(12)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)

    def table_row(self, values, widths, shade=False):
        self.set_font("Helvetica", "", 9)
        self.set_fill_color(252, 235, 235) if shade else self.set_fill_color(255, 255, 255)
        self.set_x(12)
        for val, w in zip(values, widths):
            self.cell(w, 7, str(val), fill=True, align="C")
        self.ln()

    def total_row(self, label, value, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 9)
        self.set_x(12)
        self.cell(148, 7, label, align="R")
        self.cell(38,  7, value, align="R", new_x="LMARGIN", new_y="NEXT")


pdf = SuspiciousPDF()
pdf.add_page()

# ── header ────────────────────────────────────────────────────────────────────
pdf.header_bar(
    "Alpha Omega Consulting Services",
    "Business Solutions | Advisory | Management Consulting",
    (100, 20, 20),   # dark red — visually "off"
)

# ── invoice meta ──────────────────────────────────────────────────────────────
pdf.set_xy(12, 42)
pdf.set_font("Helvetica", "B", 17)
pdf.set_text_color(100, 20, 20)
pdf.cell(100, 9, "TAX INVOICE", new_x="RIGHT", new_y="TOP")

pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(80, 80, 80)
pdf.set_x(128)
pdf.cell(0, 6, "Invoice No  :  INV-2025-00847",       new_x="LMARGIN", new_y="NEXT")  # DUPLICATE
pdf.set_x(128)
pdf.cell(0, 6, "Invoice Date:  13 April 2025",         new_x="LMARGIN", new_y="NEXT")  # Sunday
pdf.set_x(128)
pdf.cell(0, 6, "Due Date    :  13 April 2025",         new_x="LMARGIN", new_y="NEXT")  # same day (0-day terms)
pdf.set_x(128)
pdf.cell(0, 6, "PO Reference:  N/A",                   new_x="LMARGIN", new_y="NEXT")  # missing PO
pdf.set_x(128)
pdf.cell(0, 6, "Approved By :  [BLANK]",               new_x="LMARGIN", new_y="NEXT")  # no approver

pdf.set_text_color(0, 0, 0)

# ── red-flag annotations ──────────────────────────────────────────────────────
pdf.ln(2)
pdf.flag_note(
    "Invoice number INV-2025-00847 was previously issued by TechNova Solutions on 15-Apr-2025. "
    "Duplicate invoice numbers across vendors indicate possible double-billing fraud."
)
pdf.flag_note(
    "Invoice date 13-Apr-2025 is a Sunday. Legitimate invoices are rarely issued on weekends."
)
pdf.flag_note(
    "PO Reference is N/A. All vendor payments above INR 50,000 require an approved Purchase Order "
    "per internal procurement policy (Ref: Fin-Policy-2024-07)."
)

# ── seller ────────────────────────────────────────────────────────────────────
pdf.section_bar("BILLED BY (SELLER / VENDOR)")
pdf.kv("Company",   "Alpha Omega Consulting Services")
pdf.kv("Address",   "Flat 204, Shanti Niwas, Goregaon West, Mumbai - 400104")   # residential
pdf.kv("GSTIN",     "27AAAAO9999X1ZZ")     # fake/unverifiable format
pdf.kv("PAN",       "AAAAO9999X")
pdf.kv("Email",     "alphaomega.consult99@gmail.com")   # gmail, not corporate
pdf.kv("Phone",     "+91-98XXXXXXXX")      # masked number

pdf.ln(1)
pdf.flag_note(
    "Vendor address is a residential flat in Goregaon West -- not a registered commercial office. "
    "GSTIN 27AAAAO9999X1ZZ has not been verified against the GST portal. "
    "Contact email uses a free Gmail domain rather than a corporate domain."
)

# ── buyer ─────────────────────────────────────────────────────────────────────
pdf.section_bar("BILL TO (BUYER / CLIENT / PURCHASER)")
pdf.kv("Company",   "FinSphere Enterprises Pvt Ltd")
pdf.kv("Address",   "Office 901, Pinnacle Tower, SG Highway, Ahmedabad - 380054")
pdf.kv("GSTIN",     "24AABCF9012K1ZQ")
pdf.kv("Contact",   "Harshil Kaneria")

pdf.ln(1)
pdf.flag_note(
    "Seller is in Maharashtra (state code 27) and buyer is in Gujarat (state code 24). "
    "Inter-state supply requires IGST. However, line items below apply CGST + SGST (intra-state), "
    "which is INCORRECT for this transaction -- possible tax evasion or clerical fraud."
)

# ── line items ────────────────────────────────────────────────────────────────
pdf.section_bar("LINE ITEMS", warn=True)

cols   = ["#", "Description",                "HSN/SAC",   "Qty",  "Rate (INR)",    "Amount (INR)"]
widths = [10,   80,                            22,           10,    32,               32]

pdf.table_header(cols, widths)

items = [
    (1, "Consultancy Services (General)",  "---",  1,  "5,00,000.00",   "5,00,000.00"),
    (2, "Management Advisory Fees",        "---",  1,  "5,00,000.00",   "5,00,000.00"),
    (3, "Project Coordination Charges",   "---",  1,  "2,50,000.00",   "2,50,000.00"),
    (4, "Miscellaneous Business Expenses", "---",  1,  "2,50,000.00",   "2,50,000.00"),
]

for i, row in enumerate(items):
    pdf.table_row(row, widths, shade=(i % 2 == 0))

pdf.ln(2)
pdf.flag_note(
    "All four line items have vague, non-specific descriptions with no deliverables, "
    "milestones, or scope of work defined. HSN/SAC codes are missing on all items. "
    "All amounts are exact round numbers (5,00,000 / 2,50,000) -- statistically improbable "
    "for legitimate service invoices."
)

# ── totals ────────────────────────────────────────────────────────────────────
pdf.total_row("Subtotal",           "INR 15,00,000.00")
pdf.total_row("CGST @ 9%  [!WRONG TAX TYPE!]", "INR  1,35,000.00")
pdf.total_row("SGST @ 9%  [!WRONG TAX TYPE!]", "INR  1,35,000.00")

pdf.set_fill_color(100, 20, 20)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Helvetica", "B", 11)
pdf.set_x(12)
pdf.cell(148, 9, "TOTAL AMOUNT DUE", fill=True, align="R")
pdf.cell(38,  9, "INR 17,70,000.00", fill=True, align="R",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

pdf.ln(2)
pdf.set_font("Helvetica", "B", 9)
pdf.set_x(12)
pdf.cell(0, 6, "Amount in Words:  Seventeen Lakh Seventy Thousand Rupees Only",
         new_x="LMARGIN", new_y="NEXT")

# ── payment details ───────────────────────────────────────────────────────────
pdf.section_bar("PAYMENT DETAILS", warn=True)
pdf.kv("Bank Name",    "Kotak Mahindra Bank")
pdf.kv("Account Name", "Mr. Ramesh Patel")           # personal name, not company
pdf.kv("Account No",   "9876543210")                 # savings account format
pdf.kv("IFSC Code",    "KKBK0001234")
pdf.kv("Account Type", "Savings Account")            # should be Current for business

pdf.ln(1)
pdf.flag_note(
    "Bank account is held in the name of an individual ('Mr. Ramesh Patel') and is a Savings Account. "
    "Business entities must use Current Accounts. Routing payments to a personal savings account "
    "is a strong indicator of fraudulent billing or vendor impersonation."
)

# ── risk summary box ──────────────────────────────────────────────────────────
pdf.ln(2)
pdf.set_fill_color(255, 230, 230)
pdf.set_draw_color(180, 30, 30)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(120, 0, 0)
pdf.set_x(12)
pdf.cell(186, 8, "  RISK ASSESSMENT SUMMARY  --  DO NOT PROCESS WITHOUT REVIEW", fill=True,
         border=1, new_x="LMARGIN", new_y="NEXT")

risks = [
    "  [CRITICAL]  Duplicate invoice number (INV-2025-00847) already paid to different vendor",
    "  [HIGH]      No PO reference -- violates procurement policy Fin-Policy-2024-07",
    "  [HIGH]      Payment to personal savings account, not business current account",
    "  [HIGH]      Incorrect tax type: CGST/SGST applied on inter-state supply (should be IGST)",
    "  [HIGH]      Vendor GSTIN not verifiable -- possible fictitious vendor",
    "  [MEDIUM]    Invoice issued on a Sunday (13-Apr-2025)",
    "  [MEDIUM]    Vague line-item descriptions -- no deliverables or scope defined",
    "  [MEDIUM]    All amounts are exact round numbers -- statistically suspicious",
    "  [MEDIUM]    Vendor address is residential, not a registered commercial premises",
    "  [LOW]       Vendor contact uses a free Gmail address",
    "  [LOW]       No authorised signatory or digital signature on invoice",
    "  [LOW]       Approval field is blank -- no internal approver recorded",
]

pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(100, 0, 0)
for r in risks:
    pdf.set_x(12)
    pdf.cell(186, 5.5, r, fill=True, border="LR", new_x="LMARGIN", new_y="NEXT")

# closing border line
pdf.set_x(12)
pdf.cell(186, 0, "", border="B", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.set_draw_color(0, 0, 0)

out = f"{UPLOAD_DIR}/sample_invoice_SUSPICIOUS_AlphaOmega.pdf"
pdf.output(out)
print(f"Generated: {out}  ({os.path.getsize(out):,} bytes)")
