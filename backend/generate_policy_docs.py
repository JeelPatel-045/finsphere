"""
Generate two professional policy PDFs for FinSphere AI testing.
Wrong information is embedded naturally -- no annotations or flags.
The AI should identify the errors on its own.

Errors embedded (for developer reference only -- NOT visible in PDFs):
  Doc 1 - Accounting Policy Manual:
    - Revenue recognition cites Ind AS 18 (superseded by Ind AS 115 since Apr 2018)
    - Computers depreciation: 20% / 5 yrs  (Schedule II = 33.33% / 3 yrs)
    - Plant & Machinery depreciation: 15% / 10 yrs  (Schedule II = 6.67% / 15 yrs)
    - Lease accounting describes IAS 17 operating/finance split (Ind AS 116 eliminated this)
    - Materiality: 2% of PBT in Sec 8  vs  5% of PAT in Sec 9  (contradictory)
    - Cash flow mandatory under Section 136 (correct: Section 129 / Schedule III)

  Doc 2 - Compliance Framework:
    - GST registration threshold: INR 50 lakhs (correct: INR 40 lakhs for goods)
    - GSTR-9 annual return due 31 October (correct: 31 December)
    - TDS Section 194J professional fees: 7.5% (correct: 10%)
    - TDS Section 194I rent: 15% (correct: 10%)
    - Advance tax 1st instalment due 15 July (correct: 15 June)
    - MSME payment period: 60 days (correct: 45 days under MSMED Act)
    - Audit committee threshold: paid-up capital >= INR 5 crores (correct: INR 10 crores)
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

UPLOAD_DIR = "./uploads"


class PolicyDoc(FPDF):
    NAVY  = (15,  52,  96)
    LGRAY = (245, 245, 245)
    MGRAY = (200, 200, 200)

    def __init__(self, title, subtitle, version, date_str):
        super().__init__()
        self.set_auto_page_break(True, margin=22)
        self.doc_title    = title
        self.doc_subtitle = subtitle
        self.doc_version  = version
        self.doc_date     = date_str

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*self.NAVY)
        self.rect(0, 0, 210, 11, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(255, 255, 255)
        self.set_xy(8, 2)
        self.cell(130, 7, self.doc_title)
        self.set_font("Helvetica", "", 8)
        self.set_x(140)
        self.cell(0, 7, f"Version {self.doc_version}  |  {self.doc_date}", align="R")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_draw_color(*self.MGRAY)
        self.line(12, self.get_y(), 198, self.get_y())
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.set_x(12)
        self.cell(90, 6, "CONFIDENTIAL  --  For Internal Use Only")
        self.cell(0,  6, f"Page {self.page_no() - 1}", align="R")
        self.set_text_color(0, 0, 0)

    def h1(self, text, newpage=False):
        if newpage:
            self.add_page()
        self.ln(3)
        self.set_fill_color(*self.NAVY)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 12)
        self.set_x(12)
        self.cell(186, 9, f"  {text}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def h2(self, text):
        self.ln(2)
        self.set_fill_color(*self.LGRAY)
        self.set_font("Helvetica", "B", 10)
        self.set_x(12)
        self.cell(186, 7, f"  {text}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def h3(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 9)
        self.set_x(14)
        self.cell(186, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def body(self, text, indent=12):
        self.set_font("Helvetica", "", 9)
        self.set_x(indent)
        self.multi_cell(210 - indent - 12, 5.5, text,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, items, indent=20):
        self.set_font("Helvetica", "", 9)
        for item in items:
            self.set_x(indent)
            self.cell(6, 5.5, "-")
            self.multi_cell(210 - indent - 18, 5.5, item,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def numbered(self, items, indent=20):
        self.set_font("Helvetica", "", 9)
        for i, item in enumerate(items, 1):
            self.set_x(indent)
            self.cell(7, 5.5, f"({i})")
            self.multi_cell(210 - indent - 19, 5.5, item,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def table(self, headers, rows, col_widths=None):
        n = len(headers)
        if col_widths is None:
            col_widths = [186 // n] * n
        self.set_font("Helvetica", "B", 8.5)
        self.set_fill_color(*self.NAVY)
        self.set_text_color(255, 255, 255)
        self.set_x(12)
        for h, w in zip(headers, col_widths):
            self.cell(w, 7, h, fill=True, border=0, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 8.5)
        for i, row in enumerate(rows):
            self.set_fill_color(245, 245, 245) if i % 2 == 0 \
                else self.set_fill_color(255, 255, 255)
            self.set_x(12)
            for val, w in zip(row, col_widths):
                self.cell(w, 6.5, str(val), fill=True, border=0)
            self.ln()
        self.ln(3)

    def title_page(self, org):
        self.add_page()
        self.set_fill_color(*self.NAVY)
        self.rect(0, 0, 210, 60, "F")
        self.set_xy(12, 16)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.cell(0, 13, org, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(12)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(180, 210, 255)
        self.cell(0, 8, "Finance & Compliance Division")

        self.set_text_color(0, 0, 0)
        self.set_xy(12, 76)
        self.set_font("Helvetica", "B", 21)
        self.cell(0, 11, self.doc_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(12)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, self.doc_subtitle)

        self.set_xy(12, 118)
        self.set_draw_color(*self.MGRAY)
        meta = [
            ("Document Reference", f"FIN-POL-2025-{self.doc_version.replace('.', '')}"),
            ("Version",             self.doc_version),
            ("Effective Date",      self.doc_date),
            ("Review Cycle",        "Annual -- next review due 01 April 2026"),
            ("Approved By",         "Board of Directors"),
            ("Classification",      "CONFIDENTIAL"),
            ("Owner",               "Chief Financial Officer"),
        ]
        for k, v in meta:
            self.set_x(12)
            self.set_font("Helvetica", "B", 10)
            self.cell(65, 8, k + ":")
            self.set_font("Helvetica", "", 10)
            self.cell(0, 8, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_fill_color(*self.NAVY)
        self.rect(0, 258, 210, 40, "F")
        self.set_xy(12, 265)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, "CONFIDENTIAL -- FOR INTERNAL USE ONLY",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(12)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(180, 210, 255)
        self.cell(0, 6, "Unauthorised distribution or reproduction of this document is strictly prohibited.")
        self.set_x(12)
        self.ln(6)
        self.set_text_color(180, 210, 255)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 5,
            "Questions regarding this policy should be directed to finance@finsphere.ai")
        self.set_text_color(0, 0, 0)


# =============================================================================
#  DOCUMENT 1 -- Accounting Policy Manual
# =============================================================================

def build_accounting_policy():
    pdf = PolicyDoc(
        "Accounting Policy Manual",
        "Standards, Measurement Bases and Financial Reporting Guidelines",
        "v3.2", "01 April 2025"
    )
    pdf.title_page("FinSphere Enterprises Pvt Ltd")
    pdf.add_page()

    # 1. Introduction
    pdf.h1("1.  INTRODUCTION AND SCOPE")
    pdf.body(
        "This Accounting Policy Manual (the 'Manual') establishes the accounting principles, "
        "measurement bases, and reporting standards applicable to FinSphere Enterprises "
        "Pvt Ltd (the 'Company') and its wholly-owned subsidiaries. All members of the "
        "Finance function are required to apply the policies contained herein consistently "
        "across all periods. Any departure from established policy requires prior written "
        "approval from the Chief Financial Officer and must be disclosed in the financial "
        "statements where material."
    )
    pdf.h2("1.1  Basis of Preparation")
    pdf.body(
        "The financial statements are prepared in accordance with Indian Accounting Standards "
        "(Ind AS) as notified under the Companies (Indian Accounting Standards) Rules, 2015, "
        "and the provisions of the Companies Act, 2013. The financial statements are prepared "
        "on an accrual basis using the historical cost convention, except where specific "
        "standards require or permit fair value measurement. The reporting currency is "
        "Indian Rupee (INR). All amounts are presented in INR lakhs unless stated otherwise."
    )
    pdf.h2("1.2  Applicability and Hierarchy")
    pdf.body(
        "In preparing financial statements, management shall apply this Manual as the primary "
        "reference. Where the Manual is silent on a matter, the following hierarchy applies: "
        "(a) applicable Ind AS; (b) ICAI guidance notes; (c) analogous IFRS where an Ind AS "
        "does not exist; (d) management judgement consistent with the Conceptual Framework."
    )
    pdf.h2("1.3  Going Concern Assessment")
    pdf.body(
        "At each reporting date, management formally assesses the Company's ability to "
        "continue as a going concern for a period of at least twelve months. The assessment "
        "considers projected cash flows, committed financing facilities, order book, and "
        "material uncertainties. Where a material uncertainty exists, appropriate disclosure "
        "is made in the financial statements."
    )
    pdf.h2("1.4  Accounting Estimates and Judgements")
    pdf.body(
        "The preparation of financial statements requires management to make estimates and "
        "assumptions that affect the reported amounts of assets, liabilities, revenues, and "
        "expenses. Estimates are based on historical experience and other reasonable factors. "
        "Key areas of estimation include: useful lives of assets, allowance for expected "
        "credit losses, provision for employee benefits, and income tax provisions. "
        "Estimates are reviewed at each reporting date and revised prospectively."
    )

    # 2. Revenue Recognition
    pdf.h1("2.  REVENUE RECOGNITION", newpage=True)
    pdf.body(
        "Revenue is recognised in accordance with Ind AS 18 - Revenue. Revenue from "
        "ordinary activities is measured at the fair value of the consideration received "
        "or receivable, net of trade discounts, volume rebates, and taxes collected on "
        "behalf of third parties. Revenue is recognised only when it is probable that the "
        "economic benefits associated with the transaction will flow to the Company and the "
        "amount of revenue can be measured reliably."
    )
    pdf.h2("2.1  Sale of Goods")
    pdf.body(
        "Revenue from the sale of goods is recognised when all of the following conditions "
        "are satisfied: (a) the significant risks and rewards of ownership of the goods "
        "have been transferred to the buyer; (b) the Company retains neither continuing "
        "managerial involvement nor effective control over the goods sold; (c) the amount "
        "of revenue can be measured reliably; (d) it is probable that economic benefits "
        "will flow to the Company; and (e) the costs incurred or to be incurred in respect "
        "of the transaction can be measured reliably."
    )
    pdf.body(
        "For domestic sales, risks and rewards are typically transferred on dispatch. "
        "For export sales, transfer occurs at the point agreed in the terms of trade "
        "(FOB, CIF, DAP) as specified in the sales contract. Bill-and-hold arrangements "
        "require assessment of whether the customer has requested the arrangement, the "
        "goods are separately identified as the customer's property, and the goods are "
        "ready for delivery."
    )
    pdf.h2("2.2  Rendering of Services")
    pdf.body(
        "Revenue from service contracts is recognised by reference to the stage of "
        "completion of the transaction at the reporting date. Stage of completion is "
        "measured by: surveys of work performed, services performed as a proportion of "
        "total services, or the proportion of costs incurred relative to estimated total "
        "costs of the transaction. Revenue is not recognised when significant uncertainty "
        "exists regarding collectability."
    )
    pdf.h2("2.3  Construction Contracts")
    pdf.body(
        "Long-term construction contracts are accounted for using the percentage of "
        "completion method. Contract revenue and costs are recognised by reference to "
        "the stage of completion of the contract activity. Foreseeable losses on contracts "
        "are recognised immediately as an expense. Amounts due from customers are "
        "presented as contract assets; amounts billed in advance of work performed are "
        "presented as contract liabilities."
    )
    pdf.h2("2.4  Interest, Royalties and Dividends")
    pdf.body(
        "Interest income is recognised using the effective interest method under Ind AS 109. "
        "Royalty income is recognised on an accrual basis in accordance with the substance "
        "of the relevant agreement. Dividend income is recognised when the shareholder's "
        "right to receive payment is established."
    )
    pdf.h2("2.5  Government Grants")
    pdf.body(
        "Government grants are recognised when there is reasonable assurance that the "
        "Company will comply with the conditions attached and the grants will be received. "
        "Grants related to assets are recognised as deferred income and released to the "
        "Statement of Profit and Loss on a systematic basis over the useful life of the "
        "related asset. Grants related to income are recognised in the Statement of "
        "Profit and Loss in the same period as the related expense."
    )

    # 3. PPE and Depreciation
    pdf.h1("3.  PROPERTY, PLANT AND EQUIPMENT", newpage=True)
    pdf.h2("3.1  Recognition")
    pdf.body(
        "An item of property, plant and equipment (PPE) is recognised as an asset when "
        "it is probable that future economic benefits will flow to the Company and the "
        "cost of the asset can be measured reliably. The cost model is applied "
        "subsequently: PPE is carried at cost less accumulated depreciation and "
        "accumulated impairment losses."
    )
    pdf.h2("3.2  Cost Measurement")
    pdf.body(
        "The cost of an item of PPE comprises: (a) its purchase price, including import "
        "duties and non-refundable purchase taxes, after deducting trade discounts and "
        "rebates; (b) directly attributable costs of bringing the asset to the location "
        "and condition for its intended use; and (c) the initial estimate of the costs "
        "of dismantling and restoring the site, to the extent that a provision is "
        "recognised under Ind AS 37. Borrowing costs directly attributable to qualifying "
        "assets are capitalised in accordance with Ind AS 23."
    )
    pdf.h2("3.3  Depreciation Policy and Useful Lives")
    pdf.body(
        "Depreciation is provided on a Straight-Line Method (SLM) basis over the "
        "estimated useful life of each asset. Useful lives have been determined by the "
        "Company's technical experts and are consistent with Schedule II to the "
        "Companies Act, 2013. A residual value of 5% of original cost is assumed for "
        "all asset classes. Depreciation commences when the asset is available for use "
        "and ceases when the asset is derecognised."
    )
    pdf.table(
        ["Asset Category",                 "Useful Life", "SLM Rate",  "Residual Value"],
        [
            ("Factory Buildings",           "30 years",   "3.33%",      "5%"),
            ("Office Buildings",            "60 years",   "1.67%",      "5%"),
            ("Plant & Machinery (General)", "10 years",   "15.00%",     "5%"),
            ("Plant & Machinery (Specific)","15 years",   "6.67%",      "5%"),
            ("Computers & IT Equipment",    "5 years",    "20.00%",     "5%"),
            ("Servers & Networking",        "6 years",    "16.67%",     "5%"),
            ("Furniture & Fixtures",        "10 years",   "10.00%",     "5%"),
            ("Motor Vehicles",              "8 years",    "12.50%",     "5%"),
            ("Electrical Installations",    "10 years",   "10.00%",     "5%"),
            ("Office Equipment",            "5 years",    "20.00%",     "5%"),
            ("Leasehold Improvements",      "Lease term", "Lease term", "Nil"),
        ],
        col_widths=[72, 28, 26, 60]
    )
    pdf.body(
        "Assets individually costing less than INR 5,000 are expensed in the year of "
        "acquisition. Component accounting is applied where a significant component of "
        "an asset has a different useful life from the main asset; each component is "
        "depreciated separately over its own useful life."
    )
    pdf.h2("3.4  Impairment")
    pdf.body(
        "The Company assesses at each reporting date whether there is any indication of "
        "impairment. Where an indication exists, the recoverable amount is estimated as "
        "the higher of fair value less costs of disposal and value in use. An impairment "
        "loss is recognised when the carrying amount exceeds the recoverable amount. "
        "Impairment losses are reversed if conditions improve, limited to the carrying "
        "amount that would have existed had no impairment been recognised."
    )
    pdf.h2("3.5  Derecognition")
    pdf.body(
        "An asset is derecognised on disposal or when no future economic benefits are "
        "expected. The gain or loss arising on derecognition is included in the Statement "
        "of Profit and Loss. Fixed assets retired from active use and held for disposal "
        "are stated at the lower of net book value and net realisable value."
    )

    # 4. Intangible Assets
    pdf.h1("4.  INTANGIBLE ASSETS")
    pdf.h2("4.1  Recognition and Measurement")
    pdf.body(
        "Intangible assets are recognised when the asset is identifiable, it is probable "
        "that future economic benefits will flow to the Company, and the cost of the asset "
        "can be measured reliably. Intangible assets are stated at cost less accumulated "
        "amortisation and accumulated impairment losses."
    )
    pdf.table(
        ["Intangible Asset",        "Amortisation Period",  "Method",         "Ind AS Reference"],
        [
            ("Purchased Software",   "5 years",              "SLM",            "Ind AS 38"),
            ("Internally Dev. SW",   "3 years",              "SLM",            "Ind AS 38"),
            ("Customer Contracts",   "Contract term",        "SLM",            "Ind AS 38"),
            ("Trademarks",           "10 years",             "SLM",            "Ind AS 38"),
            ("Goodwill",             "Not amortised",        "Annual impairment","Ind AS 103"),
        ],
        col_widths=[52, 40, 36, 58]
    )

    # 5. Inventories
    pdf.h1("5.  INVENTORIES")
    pdf.h2("5.1  Measurement")
    pdf.body(
        "Inventories are stated at the lower of cost and net realisable value in "
        "accordance with Ind AS 2. Cost is determined on a weighted-average cost formula. "
        "Net realisable value is the estimated selling price in the ordinary course of "
        "business less the estimated costs of completion and the estimated costs necessary "
        "to make the sale. Write-downs to NRV are recorded on a line-by-line basis."
    )
    pdf.h2("5.2  Cost Inclusions")
    pdf.bullet([
        "Raw Materials: invoice cost, freight, insurance, applicable taxes net of recoverable credits.",
        "Work-in-Progress: direct materials, direct labour, and absorbed manufacturing overheads.",
        "Finished Goods: full production cost including systematic allocation of fixed and variable overheads at normal capacity.",
        "Stores and Spares: purchase cost on weighted-average basis; critical spares are capitalised if they meet the PPE recognition criteria.",
    ])
    pdf.h2("5.3  Inventory Count")
    pdf.body(
        "A full physical inventory count is conducted at 31 March each year. Mid-year "
        "cycle counts are performed on a rotational basis for high-value and fast-moving "
        "items. Differences between physical count and system balances exceeding INR 50,000 "
        "per location require a reconciliation report approved by the Plant Controller."
    )

    # 6. Leases
    pdf.h1("6.  LEASES", newpage=True)
    pdf.h2("6.1  Lessee Accounting -- Classification")
    pdf.body(
        "The Company classifies each lease at inception as either a finance lease or an "
        "operating lease. A lease is classified as a finance lease if it transfers "
        "substantially all the risks and rewards incidental to ownership of the underlying "
        "asset. All other leases are classified as operating leases."
    )
    pdf.h2("6.2  Finance Leases")
    pdf.body(
        "Assets held under finance leases are recognised at the lower of the fair value "
        "of the leased asset and the present value of the minimum lease payments at the "
        "inception of the lease. The corresponding liability is included in borrowings. "
        "Lease payments are allocated between the liability and finance charges using the "
        "effective interest method. The asset is depreciated over the shorter of its "
        "useful life or the lease term."
    )
    pdf.h2("6.3  Operating Leases")
    pdf.body(
        "Lease payments under operating leases are charged to the Statement of Profit "
        "and Loss on a straight-line basis over the term of the lease, unless another "
        "systematic basis is more representative of the time pattern of the benefit. "
        "Lease incentives received are recognised as a liability and released on a "
        "straight-line basis over the lease term as a reduction of rental expense."
    )
    pdf.h2("6.4  Short-Term and Low-Value Exemptions")
    pdf.body(
        "The Company applies the practical expedient for leases with a term of 12 months "
        "or less and for leases of underlying assets with a fair value below INR 3,50,000 "
        "when new. Lease payments for such leases are recognised as an expense in the "
        "Statement of Profit and Loss on a straight-line basis over the lease term."
    )
    pdf.h2("6.5  Lessor Accounting")
    pdf.body(
        "Leases in which the Company acts as lessor are classified as finance or operating "
        "leases. Amounts due under finance leases are recorded as receivables at the net "
        "investment in the lease. Finance income is recognised over the lease term using "
        "the effective interest method. For operating leases, rental income is recognised "
        "on a straight-line basis over the lease term."
    )

    # 7. Financial Instruments
    pdf.h1("7.  FINANCIAL INSTRUMENTS (Ind AS 109)")
    pdf.h2("7.1  Classification of Financial Assets")
    pdf.body(
        "On initial recognition, financial assets are classified as: (a) measured at "
        "amortised cost (AC), if the asset is held within a business model whose objective "
        "is to collect contractual cash flows and the contractual terms give rise to cash "
        "flows that are solely payments of principal and interest (SPPI); (b) measured at "
        "fair value through other comprehensive income (FVOCI); or (c) measured at fair "
        "value through profit or loss (FVTPL). The classification is determined at initial "
        "recognition and reclassification is permitted only when the business model changes."
    )
    pdf.h2("7.2  Expected Credit Loss (ECL) Model")
    pdf.body(
        "The Company applies the simplified approach under Ind AS 109 for trade receivables, "
        "recognising lifetime ECLs from initial recognition. A provision matrix based on "
        "historical observed default rates is maintained and adjusted for forward-looking "
        "macroeconomic information. For other financial assets, the general three-stage "
        "model is applied."
    )
    pdf.table(
        ["Ageing Bucket",   "ECL Provision Rate",  "Risk Classification"],
        [
            ("0 - 30 days",   "0.50%",  "Standard"),
            ("31 - 60 days",  "2.00%",  "Watch"),
            ("61 - 90 days",  "7.00%",  "Special Mention"),
            ("91 - 180 days", "20.00%", "Sub-Standard"),
            ("181 - 365 days","50.00%", "Doubtful"),
            ("> 365 days",    "100.00%","Loss / Written Off"),
        ],
        col_widths=[44, 36, 106]
    )

    # 8. Provisions and Taxation
    pdf.h1("8.  PROVISIONS, CONTINGENCIES AND TAXATION", newpage=True)
    pdf.h2("8.1  Provisions")
    pdf.body(
        "A provision is recognised when the Company has a present obligation (legal or "
        "constructive) as a result of a past event, it is probable that an outflow of "
        "economic resources will be required to settle the obligation, and a reliable "
        "estimate of the amount can be made. Provisions are measured at the best estimate "
        "of the expenditure required and are discounted where the effect of the time value "
        "of money is material."
    )
    pdf.h2("8.2  Employee Benefits")
    pdf.body(
        "Short-term employee benefits are recognised as an expense in the period in which "
        "the employee renders service. Defined contribution obligations (EPF, ESI) are "
        "recognised when the contribution is due. The gratuity liability, a defined benefit "
        "obligation, is determined annually by an independent actuary using the projected "
        "unit credit method in accordance with Ind AS 19."
    )
    pdf.h2("8.3  Current Tax")
    pdf.body(
        "Current tax is determined based on taxable income computed in accordance with the "
        "provisions of the Income Tax Act, 1961. The Company has opted for the concessional "
        "tax regime under Section 115BAA, resulting in an effective rate of 25.168% "
        "(including surcharge and health and education cess). Current tax assets and "
        "liabilities are offset where the Company has a legally enforceable right of offset."
    )
    pdf.h2("8.4  Deferred Tax")
    pdf.body(
        "Deferred tax is recognised on temporary differences between the carrying amounts "
        "in the financial statements and the corresponding tax bases. Deferred tax assets "
        "are recognised to the extent it is probable that sufficient future taxable profit "
        "will be available. Deferred tax liabilities are recognised for all taxable "
        "temporary differences."
    )
    pdf.h2("8.5  Materiality Threshold for Tax Disclosures")
    pdf.body(
        "For the purpose of recognising and disclosing current tax provisions, an item is "
        "considered material if it exceeds 2.0% of profit before tax or INR 50,000, "
        "whichever is lower. Amounts below this threshold are aggregated and disclosed "
        "in the notes as 'sundry tax provisions'."
    )

    # 9. Financial Reporting
    pdf.h1("9.  FINANCIAL REPORTING AND DISCLOSURES")
    pdf.h2("9.1  Financial Statements")
    pdf.body(
        "The Company prepares annual financial statements comprising: (a) Balance Sheet "
        "as at 31 March; (b) Statement of Profit and Loss for the year ended 31 March; "
        "(c) Statement of Changes in Equity; (d) Cash Flow Statement; (e) Notes including "
        "a summary of significant accounting policies and other explanatory information. "
        "Comparative figures for the previous year are presented for all items."
    )
    pdf.h2("9.2  Cash Flow Statement")
    pdf.body(
        "The Cash Flow Statement, mandatory for all companies under Section 136 of the "
        "Companies Act, 2013, is prepared using the Indirect Method for operating "
        "activities. Cash flows from investing and financing activities are presented "
        "on a gross basis. Cash and cash equivalents include bank balances and short-term "
        "deposits with an original maturity of three months or less."
    )
    pdf.h2("9.3  Segment Reporting")
    pdf.body(
        "Operating segments are reported in accordance with Ind AS 108, consistent with "
        "internal reporting reviewed by the Chief Operating Decision Maker. The Company "
        "currently has two reportable segments: Technology Products and Advisory Services. "
        "Inter-segment revenues are eliminated on consolidation."
    )
    pdf.h2("9.4  Materiality")
    pdf.body(
        "For the purpose of disclosures, an item is considered material if its omission "
        "or misstatement, individually or in aggregate, could reasonably be expected to "
        "influence the economic decisions of users. The Company applies a materiality "
        "threshold of 5% of Profit After Tax or INR 25,00,000, whichever is lower, "
        "for disclosure decisions."
    )
    pdf.h2("9.5  Related Party Disclosures")
    pdf.body(
        "Related party relationships, transactions and outstanding balances are disclosed "
        "in the financial statements in accordance with Ind AS 24. All related party "
        "transactions are reviewed and approved by the Audit Committee prior to execution. "
        "Transactions with Key Management Personnel are separately disclosed."
    )

    # 10. Foreign Currency
    pdf.h1("10.  FOREIGN CURRENCY TRANSACTIONS", newpage=True)
    pdf.h2("10.1  Functional and Presentation Currency")
    pdf.body(
        "The functional and presentation currency of the Company is Indian Rupee (INR). "
        "The functional currency of each foreign subsidiary or branch is determined based "
        "on the primary economic environment in which it operates."
    )
    pdf.h2("10.2  Translation of Foreign Currency Items")
    pdf.body(
        "Foreign currency transactions are translated at the exchange rate prevailing on "
        "the transaction date. Monetary items outstanding at the reporting date are "
        "retranslated at the closing rate. Non-monetary items measured at historical cost "
        "are not retranslated. Exchange differences are recognised in the Statement of "
        "Profit and Loss, except those qualifying for hedge accounting treatment."
    )
    pdf.h2("10.3  Hedge Accounting")
    pdf.body(
        "Where the Company designates a financial instrument as a hedging instrument in "
        "a qualifying cash flow or fair value hedge relationship, it applies Ind AS 109 "
        "hedge accounting. Formal documentation of the hedge relationship, risk management "
        "objective and effectiveness testing is required at inception. Hedge effectiveness "
        "is assessed prospectively and retrospectively at each reporting date."
    )

    # Appendix A
    pdf.h1("APPENDIX A  --  CHART OF ACCOUNTS (EXTRACT)", newpage=True)
    pdf.body("The following is an extract of the Company's chart of accounts. "
             "The full chart is maintained in the ERP system.")
    pdf.table(
        ["Code", "Account Name",                   "Classification", "Normal Balance"],
        [
            ("1001", "Cash at Bank -- Current",        "Current Asset",    "Debit"),
            ("1002", "Cash at Bank -- EEFC",            "Current Asset",    "Debit"),
            ("1100", "Trade Receivables",               "Current Asset",    "Debit"),
            ("1150", "Less: ECL Provision",             "Current Asset",    "Credit"),
            ("1200", "Inventories",                     "Current Asset",    "Debit"),
            ("1300", "Prepaid Expenses",                "Current Asset",    "Debit"),
            ("1400", "Advance Tax / TDS Receivable",    "Current Asset",    "Debit"),
            ("1500", "PPE -- Gross Block",              "Non-Current Asset","Debit"),
            ("1550", "Less: Accum. Depreciation",       "Non-Current Asset","Credit"),
            ("1600", "Intangible Assets -- Net",        "Non-Current Asset","Debit"),
            ("1700", "Capital Work-in-Progress",        "Non-Current Asset","Debit"),
            ("2001", "Trade Payables -- MSME",          "Current Liability","Credit"),
            ("2002", "Trade Payables -- Others",        "Current Liability","Credit"),
            ("2100", "Accrued Expenses",                "Current Liability","Credit"),
            ("2200", "Short-Term Borrowings",           "Current Liability","Credit"),
            ("2400", "GST Payable (Net)",               "Current Liability","Credit"),
            ("2500", "TDS Payable",                     "Current Liability","Credit"),
            ("2600", "Advance from Customers",          "Current Liability","Credit"),
            ("3001", "Share Capital",                   "Equity",           "Credit"),
            ("3100", "Securities Premium",              "Equity",           "Credit"),
            ("3200", "Retained Earnings",               "Equity",           "Credit"),
            ("3300", "Other Comprehensive Income",      "Equity",           "Credit"),
            ("4001", "Revenue -- Technology Products",  "Revenue",          "Credit"),
            ("4100", "Revenue -- Advisory Services",    "Revenue",          "Credit"),
            ("4200", "Other Operating Income",          "Revenue",          "Credit"),
            ("5001", "Cost of Goods Sold",              "Expense",          "Debit"),
            ("5100", "Salaries and Wages",              "Expense",          "Debit"),
            ("5200", "Depreciation and Amortisation",   "Expense",          "Debit"),
            ("5300", "Rent and Occupancy",              "Expense",          "Debit"),
            ("5400", "Marketing and Advertising",       "Expense",          "Debit"),
            ("5500", "Travel and Conveyance",           "Expense",          "Debit"),
            ("5600", "Professional and Legal Fees",     "Expense",          "Debit"),
            ("5700", "IT and Subscription Costs",       "Expense",          "Debit"),
            ("5800", "Finance Costs",                   "Expense",          "Debit"),
            ("5900", "Income Tax Expense",              "Expense",          "Debit"),
        ],
        col_widths=[18, 72, 42, 54]
    )

    # Appendix B
    pdf.h1("APPENDIX B  --  DOCUMENT AMENDMENT HISTORY")
    pdf.table(
        ["Version", "Date",          "Author",           "Summary of Changes"],
        [
            ("v1.0",  "01 Apr 2021",  "Priya Shah, CFO",  "Initial issue"),
            ("v2.0",  "01 Apr 2023",  "Rahul Mehta, FC",  "Added Ind AS 116 lease section; updated ECL matrix"),
            ("v2.1",  "15 Oct 2023",  "Priya Shah, CFO",  "Minor clarifications to depreciation policy"),
            ("v3.0",  "01 Apr 2024",  "Harshil Kaneria",  "Revised revenue recognition section; updated tax rates"),
            ("v3.2",  "01 Apr 2025",  "Jeel Patel, CFO",  "Updated useful lives table; hedge accounting section added"),
        ],
        col_widths=[18, 28, 48, 92]
    )

    out = f"{UPLOAD_DIR}/sample_accounting_policy.pdf"
    pdf.output(out)
    return out


# =============================================================================
#  DOCUMENT 2 -- Compliance Framework
# =============================================================================

def build_compliance_framework():
    pdf = PolicyDoc(
        "Internal Controls & Compliance Framework",
        "Regulatory Obligations, Tax Compliance and Audit Procedures",
        "v2.1", "01 April 2025"
    )
    pdf.title_page("FinSphere Enterprises Pvt Ltd")
    pdf.add_page()

    # 1. Purpose
    pdf.h1("1.  PURPOSE AND SCOPE")
    pdf.body(
        "This Compliance Framework establishes the regulatory obligations, internal control "
        "requirements, and audit procedures applicable to FinSphere Enterprises Pvt Ltd. "
        "It is intended to ensure that the Company meets all statutory, regulatory, and "
        "contractual requirements on a timely basis and that financial information is "
        "reliable, complete, and presented fairly. Compliance with this Framework is "
        "mandatory for all Finance, Accounts, and Procurement personnel."
    )
    pdf.body(
        "The Framework covers: Goods and Services Tax (GST), Tax Deducted at Source (TDS) "
        "and Tax Collected at Source (TCS), Advance Tax, MSME vendor payment obligations, "
        "Corporate governance and Audit Committee requirements, and the Annual Compliance "
        "Calendar. This document should be read alongside the Accounting Policy Manual "
        "(FIN-POL-2025-32) and the Delegation of Authority Matrix."
    )

    # 2. GST
    pdf.h1("2.  GOODS AND SERVICES TAX (GST) COMPLIANCE")
    pdf.h2("2.1  Registration and Threshold")
    pdf.body(
        "Under the Central Goods and Services Tax Act, 2017, every supplier engaged in "
        "the taxable supply of goods or services whose aggregate turnover in a financial "
        "year exceeds INR 50,00,000 is required to obtain GST registration. The Company's "
        "annual turnover significantly exceeds this threshold. GST registrations are "
        "maintained in every state and union territory where the Company has a fixed "
        "place of business or effects inter-state supplies."
    )
    pdf.body(
        "All new business establishments must notify the Finance Controller within 10 "
        "working days of commencement so that a fresh GST registration application can "
        "be filed under Section 25. Failure to register within 30 days of crossing the "
        "threshold attracts a penalty equal to 10% of the tax due, subject to a minimum "
        "of INR 10,000."
    )
    pdf.h2("2.2  GST Return Filing Obligations")
    pdf.body(
        "The following return types are applicable to the Company. All returns must be "
        "filed by the Finance team on or before the prescribed due dates. Delayed filing "
        "attracts late fees and, in the case of GSTR-3B, interest at 18% per annum on "
        "the outstanding tax liability."
    )
    pdf.table(
        ["Return Form", "Frequency",  "Filing Deadline",           "Late Fee"],
        [
            ("GSTR-1",  "Monthly",    "11th of the following month","INR 50/day (INR 20/day for nil return)"),
            ("GSTR-3B", "Monthly",    "20th of the following month","INR 50/day + interest 18% p.a."),
            ("GSTR-9",  "Annual",     "31st October",               "INR 200/day, max 0.50% of turnover"),
            ("GSTR-9C", "Annual",     "31st October",               "Same deadline as GSTR-9"),
            ("GSTR-7",  "Monthly",    "10th of the following month","INR 50/day (if TDS deducted under GST)"),
        ],
        col_widths=[26, 22, 46, 92]
    )
    pdf.h2("2.3  Input Tax Credit (ITC) Policy")
    pdf.body(
        "ITC is available on all inward supplies of goods and services used in the "
        "course or furtherance of business, subject to the conditions under Section 16 "
        "of the CGST Act. ITC must be claimed within the earlier of: (a) the due date "
        "of filing the return for September of the next financial year, or (b) the date "
        "of filing the annual return. Blocked credits under Section 17(5) must be "
        "identified at the time of booking and reversed immediately."
    )
    pdf.bullet([
        "All vendor invoices must carry valid GSTIN, HSN/SAC codes, and the correct tax rate.",
        "ITC claims must be matched against GSTR-2B before being availed in GSTR-3B.",
        "Provisional ITC claimed in excess of matched ITC must be reversed with interest.",
        "Purchases from composition dealers and unregistered vendors do not carry ITC.",
    ])
    pdf.h2("2.4  E-Invoicing and E-Way Bill")
    pdf.body(
        "The Company is required to generate e-invoices through the Invoice Registration "
        "Portal (IRP) for all B2B taxable supplies above INR 50,000. The Invoice Reference "
        "Number (IRN) and QR code must be incorporated into the final invoice before "
        "issuance. E-way bills are mandatory for all inter-state movements of goods "
        "exceeding INR 50,000 in value."
    )

    # 3. TDS
    pdf.h1("3.  TAX DEDUCTED AT SOURCE (TDS) COMPLIANCE", newpage=True)
    pdf.h2("3.1  Applicable TDS Rates")
    pdf.body(
        "The Company is required to deduct TDS at source on the following categories "
        "of payments. TDS is deducted at the time of credit or payment, whichever is "
        "earlier. If the payee fails to furnish their PAN, TDS is deducted at 20% or "
        "the applicable rate, whichever is higher."
    )
    pdf.table(
        ["Section", "Nature of Payment",         "Threshold (INR)",    "Rate",   "Higher rate (no PAN)"],
        [
            ("192",  "Salary",                    "Basic exemption",   "Slab",   "Slab rate"),
            ("194",  "Dividend",                  "2,500",             "10%",    "20%"),
            ("194A", "Interest -- Banks",         "40,000",            "10%",    "20%"),
            ("194A", "Interest -- Others",        "5,000",             "10%",    "20%"),
            ("194C", "Payments to Contractors",   "30,000 / 1,00,000", "1%/2%",  "20%"),
            ("194H", "Commission / Brokerage",    "15,000",            "5%",     "20%"),
            ("194I", "Rent -- Land & Building",   "2,40,000 p.a.",     "15%",    "20%"),
            ("194I", "Rent -- Plant & Machinery", "2,40,000 p.a.",     "2%",     "20%"),
            ("194J", "Professional Fees",         "30,000",            "7.5%",   "20%"),
            ("194J", "Technical Services",        "30,000",            "2%",     "20%"),
            ("194Q", "Purchase of Goods",         "50 lakhs p.a.",     "0.1%",   "5%"),
            ("194R", "Perquisites / Benefits",    "20,000",            "10%",    "20%"),
        ],
        col_widths=[18, 52, 38, 18, 60]
    )
    pdf.h2("3.2  TDS Deposit Deadlines")
    pdf.body(
        "TDS deducted during a month must be deposited to the government account by the "
        "7th of the following month (30th April for deductions in March). Delayed deposit "
        "attracts simple interest at 1.5% per month or part thereof from the date of "
        "deduction to the date of deposit."
    )
    pdf.h2("3.3  TDS Return Filing")
    pdf.table(
        ["Quarter",       "Period",          "Due Date for Return Filing"],
        [
            ("Q1",         "April -- June",   "31st July"),
            ("Q2",         "July -- Sept",    "31st October"),
            ("Q3",         "Oct -- Dec",      "31st January"),
            ("Q4",         "Jan -- March",    "31st May"),
        ],
        col_widths=[30, 60, 96]
    )
    pdf.body(
        "TDS certificates (Form 16 / Form 16A) must be issued to deductees within "
        "15 days of the due date for filing the quarterly TDS return. Form 26AS "
        "reconciliation is performed by the Finance team on a monthly basis."
    )

    # 4. Advance Tax
    pdf.h1("4.  ADVANCE TAX")
    pdf.h2("4.1  Applicability and Computation")
    pdf.body(
        "Every company whose estimated tax liability for the assessment year exceeds "
        "INR 10,000 is required to pay advance tax in four instalments under Section 207 "
        "of the Income Tax Act, 1961. The Finance team prepares an advance tax computation "
        "in May / June of each year based on projected annual taxable income. The "
        "computation is reviewed by the CFO and submitted to the tax consultant for "
        "independent verification before the first instalment date."
    )
    pdf.h2("4.2  Instalment Schedule")
    pdf.table(
        ["Instalment", "Due Date",       "Cumulative % of Estimated Tax", "Interest for Shortfall"],
        [
            ("First",   "15th July",     "Not less than 15%",             "Section 234C -- 1% per month"),
            ("Second",  "15th September","Not less than 45%",             "Section 234C -- 1% per month"),
            ("Third",   "15th December", "Not less than 75%",             "Section 234C -- 1% per month"),
            ("Fourth",  "15th March",    "100%",                          "Section 234B for aggregate shortfall"),
        ],
        col_widths=[22, 30, 60, 74]
    )
    pdf.body(
        "Where the actual tax liability at year-end exceeds the advance tax paid by more "
        "than 10%, interest under Section 234B is levied at 1% per month on the shortfall "
        "from 1 April of the assessment year to the date of assessment or payment. "
        "The tax consultant reviews each instalment against the latest profit projections "
        "and recommends top-up payments where necessary."
    )

    # 5. MSME
    pdf.h1("5.  MSME VENDOR PAYMENT POLICY")
    pdf.h2("5.1  Regulatory Background")
    pdf.body(
        "The Micro, Small and Medium Enterprises Development (MSMED) Act, 2006 imposes "
        "an obligation on buyers to pay MSME suppliers within the agreed credit period, "
        "which shall not exceed 60 days from the date of acceptance or deemed acceptance "
        "of goods or services. Where no agreement exists, payment must be made within "
        "15 days. Amounts outstanding beyond the statutory period attract compound "
        "interest at three times the Reserve Bank of India bank rate."
    )
    pdf.body(
        "The Company is additionally required to file Form MSME-1 with the Registrar of "
        "Companies on a half-yearly basis, disclosing outstanding amounts owed to MSME "
        "suppliers for more than 45 days. The Finance team maintains an MSME register "
        "updated every quarter based on vendor declarations (Udyam Registration Certificates)."
    )
    pdf.h2("5.2  Internal Payment SLA")
    pdf.body(
        "To ensure compliance, the Company has set an internal payment target of 60 days "
        "for all MSME vendors. The Accounts Payable team generates a weekly ageing report "
        "of MSME outstanding invoices. Any invoice outstanding beyond 45 days is escalated "
        "to the Finance Controller for immediate payment authorisation. The CFO reviews "
        "MSME outstanding balances at each month-end close."
    )
    pdf.h2("5.3  Vendor Onboarding Requirements")
    pdf.bullet([
        "All vendors must declare their MSME status during onboarding using the Vendor Registration Form.",
        "MSME vendors must provide a valid Udyam Registration Certificate (URC).",
        "MSME status must be re-verified annually or upon expiry of the URC.",
        "Procurement must not finalise any purchase order with an MSME vendor without MSME flag in ERP.",
    ])

    # 6. Corporate Governance
    pdf.h1("6.  CORPORATE GOVERNANCE", newpage=True)
    pdf.h2("6.1  Audit Committee -- Applicability")
    pdf.body(
        "In accordance with Section 177 of the Companies Act, 2013, an Audit Committee "
        "is mandatory for every listed company and every unlisted public company having "
        "a paid-up share capital of INR 5,00,00,000 (five crores) or more. The Company's "
        "current paid-up capital exceeds this threshold and accordingly maintains a duly "
        "constituted Audit Committee."
    )
    pdf.h2("6.2  Audit Committee Composition and Meetings")
    pdf.body(
        "The Audit Committee comprises a minimum of three directors. A majority of members, "
        "including the Chairperson, shall be independent directors. The CFO, Head of "
        "Internal Audit, and Statutory Auditor are permanent invitees. The Committee "
        "meets at least four times per year with a gap of not more than 120 days between "
        "consecutive meetings. Quorum requires two members or one-third of total members, "
        "whichever is greater, with at least two independent directors."
    )
    pdf.h2("6.3  Audit Committee Responsibilities")
    pdf.bullet([
        "Oversight of the financial reporting process and integrity of financial statements.",
        "Recommending appointment, remuneration and terms of engagement of Statutory Auditors.",
        "Reviewing the adequacy and effectiveness of internal financial controls.",
        "Reviewing the findings of internal audit reports and monitoring corrective actions.",
        "Granting prior approval for all related party transactions and omnibus approvals for recurring transactions.",
        "Reviewing the risk management framework and material risks identified.",
        "Overseeing the vigil mechanism / whistleblower policy.",
        "Reviewing utilisation of proceeds from public issues and rights issues, if any.",
    ])
    pdf.h2("6.4  Board Reporting")
    pdf.body(
        "The CFO presents a quarterly financial review to the Board including: "
        "(a) consolidated P&L vs budget; (b) cash flow summary and liquidity position; "
        "(c) material litigations and contingent liabilities; (d) significant accounting "
        "judgements and estimates; (e) compliance status on all statutory obligations; "
        "(f) related party transaction summary."
    )

    # 7. Compliance Calendar
    pdf.h1("7.  ANNUAL COMPLIANCE CALENDAR")
    pdf.h2("7.1  Monthly Recurring Compliances")
    pdf.table(
        ["By Date", "Compliance Activity",                    "Statute",      "Owner"],
        [
            ("7th",    "Deposit TDS / TCS (non-March)",        "Income Tax",   "Tax Team"),
            ("10th",   "GSTR-7 filing (if applicable)",        "GST",          "Tax Team"),
            ("11th",   "GSTR-1 filing (monthly filers)",       "GST",          "Tax Team"),
            ("15th",   "PF contribution deposit",              "EPFO",         "HR Finance"),
            ("20th",   "GSTR-3B filing and tax payment",       "GST",          "Tax Team"),
            ("21st",   "IEC renewal (if applicable)",          "DGFT",         "Corp Secretary"),
            ("25th",   "ESI contribution deposit",             "ESIC",         "HR Finance"),
            ("Last",   "Month-end close and reconciliations",  "Internal",     "Finance"),
        ],
        col_widths=[18, 80, 34, 54]
    )
    pdf.h2("7.2  Quarterly Compliances")
    pdf.table(
        ["Due Date",    "Activity",                               "Statute",      "Owner"],
        [
            ("31 July",   "Q1 TDS return (Form 26Q / 24Q)",      "Income Tax",   "Tax Team"),
            ("31 Oct",    "Q2 TDS return (Form 26Q / 24Q)",      "Income Tax",   "Tax Team"),
            ("31 Jan",    "Q3 TDS return (Form 26Q / 24Q)",      "Income Tax",   "Tax Team"),
            ("30 Apr",    "Q4 TDS return (Form 26Q / 24Q)",      "Income Tax",   "Tax Team"),
            ("15 Jun",    "Advance tax -- 1st instalment",        "Income Tax",   "Tax Team"),
            ("15 Sep",    "Advance tax -- 2nd instalment",        "Income Tax",   "Tax Team"),
            ("15 Dec",    "Advance tax -- 3rd instalment",        "Income Tax",   "Tax Team"),
            ("15 Mar",    "Advance tax -- 4th instalment",        "Income Tax",   "Tax Team"),
        ],
        col_widths=[28, 72, 32, 54]
    )
    pdf.h2("7.3  Annual Compliances")
    pdf.table(
        ["Due Date",      "Activity",                                     "Statute",         "Owner"],
        [
            ("30 Sep",     "AGM (within 6 months of financial year end)", "Companies Act",   "Corp Secretary"),
            ("30 days/AGM","ROC Filing -- AOC-4 (Financial Statements)",  "MCA",             "Corp Secretary"),
            ("60 days/AGM","ROC Filing -- MGT-7 (Annual Return)",         "MCA",             "Corp Secretary"),
            ("30 Oct",     "GSTR-9 Annual Return",                        "GST",             "Tax Team"),
            ("30 Oct",     "GSTR-9C Reconciliation Statement",            "GST",             "Tax Team"),
            ("30 Sep",     "Income Tax Return -- Companies (ITR-6)",      "Income Tax",      "Tax Team"),
            ("30 Sep",     "Transfer Pricing Report -- Form 3CEB",        "Income Tax",      "Tax Team"),
            ("30 Apr",     "TDS Certificate issuance -- Form 16A (Q4)",   "Income Tax",      "Tax Team"),
            ("30 Jun",     "Form MSME-1 -- H2 half-year filing",          "MSMED Act / MCA", "Finance"),
            ("31 Oct",     "Form MSME-1 -- H1 half-year filing",          "MSMED Act / MCA", "Finance"),
            ("31 Mar",     "Year-end physical inventory verification",     "Internal Policy", "Operations"),
            ("31 Mar",     "Fixed asset physical verification",            "Internal Policy", "Finance"),
        ],
        col_widths=[28, 76, 36, 46]
    )

    # 8. Internal Audit
    pdf.h1("8.  INTERNAL AUDIT FRAMEWORK", newpage=True)
    pdf.h2("8.1  Charter and Independence")
    pdf.body(
        "The Internal Audit function operates under a charter approved by the Audit "
        "Committee. The Head of Internal Audit reports functionally to the Audit Committee "
        "Chairperson and administratively to the CFO. Internal audit personnel have no "
        "operational responsibilities and are independent from the activities they audit. "
        "The function follows the International Standards for the Professional Practice "
        "of Internal Auditing issued by the Institute of Internal Auditors (IIA)."
    )
    pdf.h2("8.2  Risk-Based Audit Plan")
    pdf.body(
        "The annual internal audit plan is developed using a risk-based methodology. "
        "All auditable entities within the Company are assessed for inherent risk using "
        "criteria including financial magnitude, regulatory sensitivity, operational "
        "complexity, prior audit findings, and management changes. The plan is submitted "
        "to the Audit Committee for approval in March each year."
    )
    pdf.h2("8.3  Audit Universe")
    pdf.table(
        ["Audit Area",                  "Risk Category", "Cycle",       "Last Completed"],
        [
            ("Revenue & Receivables",   "High",          "Quarterly",   "Q4 FY 2024-25"),
            ("Vendor Payments & AP",    "High",          "Quarterly",   "Q4 FY 2024-25"),
            ("Payroll Processing",      "High",          "Semi-Annual", "H2 FY 2024-25"),
            ("Treasury & Banking",      "High",          "Semi-Annual", "H2 FY 2024-25"),
            ("Fixed Assets",            "Medium",        "Annual",      "FY 2024-25"),
            ("Inventory Management",    "Medium",        "Semi-Annual", "H2 FY 2024-25"),
            ("GST Compliance",          "High",          "Quarterly",   "Q4 FY 2024-25"),
            ("TDS / Direct Tax",        "High",          "Quarterly",   "Q4 FY 2024-25"),
            ("IT General Controls",     "High",          "Annual",      "FY 2024-25"),
            ("Related Party Txns",      "High",          "Annual",      "FY 2024-25"),
            ("Capital Expenditure",     "Medium",        "Annual",      "FY 2023-24"),
            ("Contracts Management",    "Medium",        "Annual",      "FY 2023-24"),
            ("Forex & Hedging",         "Medium",        "Annual",      "FY 2024-25"),
        ],
        col_widths=[60, 28, 30, 68]
    )
    pdf.h2("8.4  Audit Finding Classifications")
    pdf.table(
        ["Rating",    "Description",                                                   "Resolution SLA"],
        [
            ("Critical",  "Direct financial exposure or serious regulatory breach",     "15 days"),
            ("High",      "Material control weakness; significant risk of misstatement","30 days"),
            ("Medium",    "Moderate control gap; process improvement required",         "60 days"),
            ("Low",       "Minor observation; best-practice recommendation",            "90 days"),
        ],
        col_widths=[22, 120, 44]
    )

    # 9. Whistleblower
    pdf.h1("9.  VIGIL MECHANISM AND WHISTLEBLOWER POLICY")
    pdf.body(
        "In terms of Section 177(9) of the Companies Act, 2013 and the Company's Code of "
        "Conduct, a formal Vigil Mechanism is established for directors, employees, and "
        "other stakeholders to report genuine concerns of unethical behaviour, suspected "
        "fraud, or violations of law or Company policy. Reports may be made to the "
        "Whistleblower Officer or directly to the Audit Committee Chairperson via the "
        "dedicated email address ethics@finsphere.ai."
    )
    pdf.body(
        "All reports are treated with strict confidentiality and are investigated by the "
        "Internal Audit function under the oversight of the Audit Committee. The Company "
        "ensures that no adverse employment action is taken against any person who makes "
        "a report in good faith. Anonymous reports are accepted; however, they may limit "
        "the scope of investigation. Frivolous or malicious complaints will be addressed "
        "in accordance with the Company's disciplinary policy."
    )

    # 10. Policy Governance
    pdf.h1("10.  POLICY GOVERNANCE AND REVIEW")
    pdf.body(
        "This Framework is reviewed annually by the Finance Controller and approved by "
        "the CFO before each financial year commencement. Material changes in law or "
        "regulation are incorporated by way of an amendment circular within 30 days of "
        "the change taking effect. All amendment circulars are circulated to the Finance "
        "team and uploaded to the Company's policy repository on the intranet."
    )
    pdf.h2("10.1  Amendment History")
    pdf.table(
        ["Version", "Date",          "Author",            "Key Changes"],
        [
            ("v1.0",  "01 Apr 2022",  "Priya Shah, CFO",   "Initial issue"),
            ("v1.1",  "01 Jul 2022",  "Rahul Mehta, FC",   "Updated GST e-invoicing thresholds"),
            ("v2.0",  "01 Apr 2024",  "Harshil Kaneria",   "Revised TDS rates; added 194Q/194R; MSME section expanded"),
            ("v2.1",  "01 Apr 2025",  "Jeel Patel, CFO",   "Updated compliance calendar; advance tax section revised"),
        ],
        col_widths=[18, 28, 48, 92]
    )

    out = f"{UPLOAD_DIR}/sample_compliance_framework.pdf"
    pdf.output(out)
    return out


if __name__ == "__main__":
    p1 = build_accounting_policy()
    print(f"Generated: {p1}  ({os.path.getsize(p1):,} bytes)")

    p2 = build_compliance_framework()
    print(f"Generated: {p2}  ({os.path.getsize(p2):,} bytes)")

    print("\nDone.")
