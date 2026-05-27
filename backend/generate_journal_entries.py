"""
Generate sample_journal_entries.csv
  - 400 rows, 22 columns
  - ~25% of rows carry one or more suspicious flags (HIGH / CRITICAL severity)
  - Remaining 75% are clean / low-risk entries

Suspicious patterns embedded
------------------------------
  CRITICAL  Debit != Credit on same journal (unbalanced entry)
  CRITICAL  Entry posted by a terminated employee
  CRITICAL  Duplicate journal (same amount + account + date, different JE ID)
  HIGH      Posted after month-end close (posting_date > period end)
  HIGH      Manual entry in a system-automated account (payroll, depreciation)
  HIGH      Suspense account usage without clearing within 30 days
  HIGH      Round-number amount >= INR 5,00,000
  HIGH      Debit/Credit split just below approval threshold (INR 99,500 - 99,999)
  HIGH      Entry reversed within 24 hours (possible error cover-up)
  MEDIUM    Posted on weekend or public holiday
  MEDIUM    Posting time between 23:00 - 04:00 (off-hours)
  MEDIUM    Missing reference / supporting document number
  MEDIUM    Generic / vague description ("Adjustment", "Correction", "Misc")
  LOW       Posted without approval (approved_by = BLANK)
"""

import csv, random
from datetime import date, timedelta, time

random.seed(7)
OUT = "./uploads/sample_journal_entries.csv"

# ── reference data ────────────────────────────────────────────────────────────

ACCOUNTS = [
    ("1001", "Cash & Cash Equivalents",          "Asset"),
    ("1100", "Accounts Receivable",              "Asset"),
    ("1200", "Prepaid Expenses",                 "Asset"),
    ("1300", "Inventory",                        "Asset"),
    ("1500", "Fixed Assets - Plant & Machinery", "Asset"),
    ("1600", "Accumulated Depreciation",         "Asset"),
    ("1700", "Suspense Account",                 "Asset"),    # HIGH risk if used
    ("2001", "Accounts Payable",                 "Liability"),
    ("2100", "Accrued Liabilities",              "Liability"),
    ("2200", "Short-Term Borrowings",            "Liability"),
    ("2300", "Deferred Revenue",                 "Liability"),
    ("2400", "Tax Payable - GST",                "Liability"),
    ("3001", "Share Capital",                    "Equity"),
    ("3100", "Retained Earnings",                "Equity"),
    ("3200", "Other Comprehensive Income",       "Equity"),
    ("4001", "Revenue - Product Sales",          "Revenue"),
    ("4100", "Revenue - Services",               "Revenue"),
    ("4200", "Other Income",                     "Revenue"),
    ("5001", "Cost of Goods Sold",               "Expense"),
    ("5100", "Salaries & Wages",                 "Expense"),   # auto - manual suspicious
    ("5200", "Depreciation Expense",             "Expense"),   # auto - manual suspicious
    ("5300", "Rent Expense",                     "Expense"),
    ("5400", "Marketing & Advertising",          "Expense"),
    ("5500", "Travel & Entertainment",           "Expense"),
    ("5600", "Professional Fees",                "Expense"),
    ("5700", "Utilities",                        "Expense"),
    ("5800", "Miscellaneous Expense",            "Expense"),
    ("5900", "Interest Expense",                 "Expense"),
]

AUTO_ACCOUNTS = {"5100", "5200"}  # system-generated; manual entries here are suspicious

COST_CENTRES = ["CC-CORP", "CC-SALES", "CC-OPS", "CC-IT", "CC-HR", "CC-FIN", "CC-MFG"]
PROJECTS     = ["PRJ-2024-01", "PRJ-2024-03", "PRJ-2025-01", "PRJ-2025-02", "INTERNAL", "OVERHEAD", ""]

ACTIVE_USERS     = ["Jeel.Patel", "Harshil.Kaneria", "Priya.Shah", "Rahul.Mehta",
                     "Sneha.Iyer", "Vikram.Nair", "Anita.Desai", "System.Auto"]
TERMINATED_USERS = ["Amit.Kumar", "Deepa.Reddy"]   # CRITICAL — should not be posting

APPROVERS        = ["Jeel.Patel", "Harshil.Kaneria", "CFO.Approval", "HOD.Finance", ""]  # "" = no approval

DOCUMENT_TYPES   = ["Purchase Invoice", "Sales Invoice", "Payment Voucher", "Receipt Voucher",
                     "Journal Voucher", "Credit Note", "Debit Note", "Payroll Journal",
                     "Depreciation Run", "Month-End Accrual", "Reversal Entry", "Adjustment"]

DESCRIPTIONS_CLEAN = [
    "Vendor payment - {vendor} Invoice {ref}",
    "Customer receipt - Order {ref}",
    "Monthly rent payment - {period}",
    "Payroll disbursement - {period}",
    "Depreciation charge - {period}",
    "GST input credit claim - {period}",
    "Prepaid insurance amortisation - {period}",
    "Interest on working capital loan - {period}",
    "Goods receipt - PO {ref}",
    "Sales revenue recognition - Contract {ref}",
    "Utility bills - {period}",
    "Professional fees - Audit {period}",
    "Travel reimbursement - Employee {ref}",
    "Fixed asset capitalisation - {ref}",
    "Accrual for pending invoices - {period}",
]

DESCRIPTIONS_SUSPICIOUS = [
    "Adjustment",                        # vague
    "Correction entry",                  # vague
    "Miscellaneous",                     # vague
    "Year-end adjustment",               # vague
    "Per management instruction",        # no detail
    "Reclassification",                  # vague
    "One-time charge",                   # no detail
    "As discussed",                      # no reference
    "Balance correction",                # vague
    "Sundry",                            # vague
]

VENDORS  = ["TechSupplies Ltd", "Global Logistics Inc", "Apex Consulting",
            "OfficeMax India", "BlueSky Networks", "Zenith Analytics"]
PERIODS  = ["Jan-2025", "Feb-2025", "Mar-2025", "Apr-2025",
            "Dec-2024", "Nov-2024", "Oct-2024", "Q4-2024", "Q1-2025"]

PUBLIC_HOLIDAYS = {
    date(2025, 1, 26), date(2025, 3, 14), date(2025, 3, 31),
    date(2025, 4, 14), date(2025, 4, 18), date(2025, 5, 1),
    date(2024, 10, 2), date(2024, 11, 1), date(2024, 12, 25),
}


def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def period_end(d: date) -> date:
    """Last calendar day of d's month."""
    if d.month == 12:
        return date(d.year, 12, 31)
    return date(d.year, d.month + 1, 1) - timedelta(days=1)


def fmt_inr(v):
    return f"{v:,.2f}" if v else ""


def clean_desc(templates):
    t = random.choice(templates)
    return t.format(
        vendor=random.choice(VENDORS),
        ref=f"REF-{random.randint(10000,99999)}",
        period=random.choice(PERIODS),
    )


# ── build rows ────────────────────────────────────────────────────────────────

rows = []
used_je = set()           # for duplicate detection
suspense_open = {}        # je_id -> date opened, to track uncleared suspense

START = date(2024, 7, 1)
END   = date(2025, 3, 31)

# We'll generate clean entries first, then inject suspicious ones
def make_clean_entry(je_id: int, entry_date: date) -> dict:
    acc = random.choice(ACCOUNTS)
    amt = round(random.uniform(10_000, 4_80_000), 2)   # < 5L to avoid round-number flag
    # small random cents to avoid round numbers
    amt += random.choice([0.45, 1.25, 3.75, 7.50, 11.00, 22.50, 47.80])
    dr  = amt if random.random() > 0.5 else 0
    cr  = amt if dr == 0 else 0
    posting_date = entry_date
    ph  = entry_date
    return {
        "journal_id":       f"JE-{je_id:05d}",
        "entry_date":       entry_date.strftime("%Y-%m-%d"),
        "posting_date":     posting_date.strftime("%Y-%m-%d"),
        "fiscal_period":    entry_date.strftime("%b-%Y"),
        "fiscal_year":      str(entry_date.year),
        "account_code":     acc[0],
        "account_name":     acc[1],
        "account_type":     acc[2],
        "debit_inr":        fmt_inr(dr),
        "credit_inr":       fmt_inr(cr),
        "net_amount_inr":   fmt_inr(amt),
        "description":      clean_desc(DESCRIPTIONS_CLEAN),
        "reference_no":     f"DOC-{random.randint(100000,999999)}",
        "cost_center":      random.choice(COST_CENTRES),
        "project_code":     random.choice(PROJECTS),
        "document_type":    random.choice(DOCUMENT_TYPES),
        "posted_by":        random.choice(ACTIVE_USERS),
        "approved_by":      random.choice([a for a in APPROVERS if a]),
        "posting_time":     f"{random.randint(8,18):02d}:{random.randint(0,59):02d}",
        "source":           random.choice(["System", "System", "Manual", "Interface"]),
        "is_reversal":      "No",
        "reversal_of":      "",
        "suspicious_flags": "",
        "risk_score":       random.randint(2, 25),
        "risk_level":       "LOW",
    }


# ── 300 clean entries ─────────────────────────────────────────────────────────
for i in range(1, 301):
    d = rand_date(START, END)
    rows.append(make_clean_entry(i, d))

# ── 100 suspicious entries ────────────────────────────────────────────────────
suspicious_templates = [

    # 1. CRITICAL — unbalanced entry (debit != credit)
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "debit_inr":        fmt_inr(round(random.uniform(50_000, 3_00_000), 2)),
        "credit_inr":       fmt_inr(round(random.uniform(10_000, 80_000), 2)),   # different!
        "description":      "Year-end adjustment",
        "suspicious_flags": "CRITICAL: Debit != Credit — unbalanced journal entry",
        "risk_score":       97,
        "risk_level":       "CRITICAL",
    },

    # 2. CRITICAL — posted by terminated employee
    lambda je: {
        **make_clean_entry(je, rand_date(date(2025, 1, 1), END)),
        "journal_id":       f"JE-{je:05d}",
        "posted_by":        random.choice(TERMINATED_USERS),
        "approved_by":      "",
        "description":      random.choice(DESCRIPTIONS_SUSPICIOUS),
        "suspicious_flags": "CRITICAL: Posted by terminated employee — access should have been revoked",
        "risk_score":       99,
        "risk_level":       "CRITICAL",
    },

    # 3. CRITICAL — duplicate (same account + same amount as an earlier entry)
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "account_code":     rows[random.randint(0, 50)]["account_code"],
        "account_name":     rows[random.randint(0, 50)]["account_name"],
        "net_amount_inr":   rows[random.randint(0, 50)]["net_amount_inr"],
        "debit_inr":        rows[random.randint(0, 50)]["debit_inr"],
        "credit_inr":       rows[random.randint(0, 50)]["credit_inr"],
        "description":      "Duplicate posting",
        "suspicious_flags": "CRITICAL: Duplicate journal — same account and amount as prior entry",
        "risk_score":       95,
        "risk_level":       "CRITICAL",
    },

    # 4. HIGH — posted after month-end close
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "posting_date":     (period_end(rand_date(START, END)) + timedelta(days=random.randint(3, 15))).strftime("%Y-%m-%d"),
        "description":      "Per management instruction",
        "suspicious_flags": "HIGH: Posting date is after period close — backdated or overridden entry",
        "risk_score":       82,
        "risk_level":       "HIGH",
    },

    # 5. HIGH — manual entry in auto account (payroll / depreciation)
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "account_code":     random.choice(["5100", "5200"]),
        "account_name":     "Salaries & Wages" if random.random() > 0.5 else "Depreciation Expense",
        "source":           "Manual",
        "description":      random.choice(["Adjustment", "Correction entry", "Salary adjustment"]),
        "suspicious_flags": "HIGH: Manual journal entry in a system-automated account (payroll/depreciation)",
        "risk_score":       85,
        "risk_level":       "HIGH",
    },

    # 6. HIGH — suspense account, no clearing reference
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "account_code":     "1700",
        "account_name":     "Suspense Account",
        "reference_no":     "",
        "description":      "Suspense - to be cleared",
        "suspicious_flags": "HIGH: Amount parked in Suspense Account with no clearing reference or timeline",
        "risk_score":       78,
        "risk_level":       "HIGH",
    },

    # 7. HIGH — round number >= 5 lakh
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "net_amount_inr":   fmt_inr(random.choice([5_00_000, 7_50_000, 10_00_000, 15_00_000, 20_00_000, 50_00_000])),
        "debit_inr":        fmt_inr(random.choice([5_00_000, 7_50_000, 10_00_000, 15_00_000])),
        "credit_inr":       "",
        "description":      random.choice(DESCRIPTIONS_SUSPICIOUS),
        "suspicious_flags": "HIGH: Exact round-number amount >= INR 5,00,000 — statistically improbable for genuine transactions",
        "risk_score":       76,
        "risk_level":       "HIGH",
    },

    # 8. HIGH — just-below approval threshold (99,500 – 99,999)
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "net_amount_inr":   fmt_inr(round(random.uniform(99_500, 99_999), 2)),
        "debit_inr":        fmt_inr(round(random.uniform(99_500, 99_999), 2)),
        "credit_inr":       "",
        "approved_by":      "",
        "description":      "One-time charge",
        "suspicious_flags": "HIGH: Amount just below INR 1,00,000 approval threshold — possible threshold-splitting",
        "risk_score":       80,
        "risk_level":       "HIGH",
    },

    # 9. HIGH — reversed within 24 hours (error cover-up indicator)
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "is_reversal":      "Yes",
        "reversal_of":      f"JE-{random.randint(1, 300):05d}",
        "description":      "Reversal - per CFO",
        "posting_time":     f"{random.randint(0, 6):02d}:{random.randint(0, 59):02d}",   # early AM
        "suspicious_flags": "HIGH: Entry reversed within 24 hours of original posting — possible error concealment",
        "risk_score":       74,
        "risk_level":       "HIGH",
    },

    # 10. MEDIUM — weekend / public holiday posting
    lambda je: {
        **make_clean_entry(je, random.choice(list(PUBLIC_HOLIDAYS) +
            [date(2024, 10, 5), date(2024, 11, 16), date(2025, 1, 11),  # Saturdays
             date(2024, 12, 8), date(2025, 2, 2), date(2025, 3, 23)])), # Sundays
        "journal_id":       f"JE-{je:05d}",
        "description":      random.choice(DESCRIPTIONS_SUSPICIOUS),
        "suspicious_flags": "MEDIUM: Entry posted on a weekend or public holiday — unusual timing",
        "risk_score":       55,
        "risk_level":       "MEDIUM",
    },

    # 11. MEDIUM — off-hours posting (11 PM – 4 AM)
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "posting_time":     f"{random.choice([23, 0, 1, 2, 3, 4]):02d}:{random.randint(0,59):02d}",
        "description":      random.choice(DESCRIPTIONS_SUSPICIOUS),
        "suspicious_flags": "MEDIUM: Posted between 23:00-04:00 — off-hours manual entry requires explanation",
        "risk_score":       58,
        "risk_level":       "MEDIUM",
    },

    # 12. MEDIUM — missing reference / document number
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "reference_no":     "",
        "description":      "Adjustment",
        "suspicious_flags": "MEDIUM: No reference or supporting document number attached",
        "risk_score":       50,
        "risk_level":       "MEDIUM",
    },

    # 13. MEDIUM — vague description + no approver
    lambda je: {
        **make_clean_entry(je, rand_date(START, END)),
        "journal_id":       f"JE-{je:05d}",
        "approved_by":      "",
        "description":      random.choice(DESCRIPTIONS_SUSPICIOUS),
        "suspicious_flags": "MEDIUM: Vague description with no approver — bypassed review workflow",
        "risk_score":       62,
        "risk_level":       "MEDIUM",
    },
]

for i in range(301, 401):
    template = random.choice(suspicious_templates)
    row = template(i)
    rows.append(row)


# ── shuffle so suspicious rows are scattered ─────────────────────────────────
random.shuffle(rows)

# ── write CSV ─────────────────────────────────────────────────────────────────
FIELDS = [
    "journal_id", "entry_date", "posting_date", "fiscal_period", "fiscal_year",
    "account_code", "account_name", "account_type",
    "debit_inr", "credit_inr", "net_amount_inr",
    "description", "reference_no",
    "cost_center", "project_code", "document_type",
    "posted_by", "approved_by", "posting_time",
    "source", "is_reversal", "reversal_of",
    "suspicious_flags", "risk_score", "risk_level",
]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)

import os
total      = len(rows)
suspicious = sum(1 for r in rows if r["suspicious_flags"])
critical   = sum(1 for r in rows if r["risk_level"] == "CRITICAL")
high       = sum(1 for r in rows if r["risk_level"] == "HIGH")
medium     = sum(1 for r in rows if r["risk_level"] == "MEDIUM")
low        = sum(1 for r in rows if r["risk_level"] == "LOW")

print(f"Generated: {OUT}  ({os.path.getsize(OUT):,} bytes)")
print(f"Total rows : {total}")
print(f"Suspicious : {suspicious} ({suspicious*100//total}%)")
print(f"  CRITICAL : {critical}")
print(f"  HIGH     : {high}")
print(f"  MEDIUM   : {medium}")
print(f"  LOW      : {low}")
print(f"Columns    : {len(FIELDS)}  ->  {', '.join(FIELDS)}")
