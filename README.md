# FinSphere AI — Enterprise Financial Intelligence Platform

> Multi-agent, AI-powered financial platform built with **Next.js 14**, **FastAPI**, and **LangGraph**.  
> Upload any financial document — invoice, balance sheet, CSV, PDF — and interact with it through AI-powered audit, forecasting, compliance checks, and conversational Q&A.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [High-Level Architecture](#high-level-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Backend Architecture](#backend-architecture)
5. [Database Schema](#database-schema)
6. [AI & LLM Stack](#ai--llm-stack)
7. [AI Microservice — LangGraph Agents](#ai-microservice--langgraph-agents)
8. [Data Flow Walkthrough](#data-flow-walkthrough)
9. [Security Architecture](#security-architecture)
10. [Key Design Decisions](#key-design-decisions)
11. [Full API Reference](#full-api-reference)
12. [Tech Stack Summary](#tech-stack-summary)

---

## Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| Python | 3.10+ |
| PostgreSQL | 14+ (optional — app works without it) |

### Environment Variables

**`backend/.env`**
```env
LLM_PROVIDER=openrouter          # or "groq"
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
GROQ_API_KEY=your_groq_key       # alternate provider
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finsphere
CHROMA_DB_DIR=./chroma_db
AI_SERVICE_URL=http://localhost:9000
```

**`ai-services/.env`**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key
GROQ_API_KEY=your_groq_key
CHROMA_DB_DIR=./chroma_db
```

**`frontend/.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

> Get a free OpenRouter key → https://openrouter.ai  
> Get a free Groq key → https://console.groq.com

### Install & Run

**Frontend**
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000
```

**AI Services (optional)**
```bash
cd ai-services
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
# → http://localhost:9000
```

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                           │
│                    Next.js 14  (port 3000)                      │
│       Dashboard │ Chat │ Audit │ Forecast │ Agents │ Docs        │
└────────────────────────────┬────────────────────────────────────┘
                             │  REST API  (Axios + JWT)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API SERVER                          │
│                   FastAPI + Uvicorn  (port 8000)                │
│   Auth │ Chat │ Dashboard │ Audit │ Forecast │ Reports │ SQL     │
└─────┬───────────────────────────┬───────────────────────────────┘
      │                           │
      │  SQLAlchemy ORM           │  LangChain / LangGraph
      ▼                           ▼
┌──────────────┐       ┌─────────────────────────────────────────┐
│  PostgreSQL  │       │         LLM Provider  (API call)        │
│  (port 5432) │       │  OpenRouter — Llama 3.3 70B  (default)  │
│              │       │  Groq      — Llama 3.3 70B  (alternate) │
└──────────────┘       └─────────────────────────────────────────┘
      │                           │
      ▼                           ▼
┌──────────────┐       ┌─────────────────────────────────────────┐
│   Chroma DB  │       │  AI Services Microservice (port 9000)   │
│ (embeddings) │       │  LangGraph Agents + ML Models           │
└──────────────┘       └─────────────────────────────────────────┘
```

### Root Folder Layout

```
Finsphere/
├── frontend/        ← Next.js 14 UI (port 3000)
├── backend/         ← FastAPI REST API (port 8000)
├── ai-services/     ← FastAPI AI microservice — LangGraph (port 9000)
├── frontend1/       ← Legacy alternate frontend (unused)
├── temp/            ← Temporary scratch files
└── README.md
```

---

## Frontend Architecture

### Technology

| Concern | Library |
|---------|---------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + Radix UI |
| State | Zustand |
| Charts | Recharts |
| HTTP client | Axios with JWT interceptor |
| Icons | Lucide React |
| Forms | React Hook Form |
| Animations | Framer Motion |
| Toasts | Sonner |

### Pages

| Route | Description |
|-------|-------------|
| `/` | Redirect to `/dashboard` |
| `/dashboard` | KPI cards, revenue chart, risk heatmap, 6-month forecast |
| `/chat` | AI finance copilot — document-aware conversational Q&A |
| `/audit` | Compliance violations, suspicious transactions, risk score chart |
| `/forecasting` | Revenue forecast, cashflow projection, CFO recommendations |
| `/agents` | Agent pool status, activity feed, execution graph |
| `/documents` | Drag-drop upload, document list, extracted insights |
| `/sql-agent` | Natural language → SQL query builder + results table |
| `/login` | Authentication |
| `/signup` | User registration |
| `/profile` | User account & avatar settings |
| `/settings` | App preferences (currency, theme, LLM provider) |

### Component Tree

```
app/layout.tsx                     ← Root (Sidebar + TopNavbar)
│
├── dashboard/page.tsx
│   ├── DashboardHeader            ← "AI Report" PDF + "Export" CSV buttons
│   ├── KPICards                   ← Revenue / Expenses / Profit / Cashflow (live)
│   ├── RevenueChart               ← Bar + Line chart, YTD computed dynamically
│   ├── RiskHeatmap                ← Severity tiles from audit cache
│   └── ForecastChart              ← 6-month projection line
│
├── audit/page.tsx
│   ├── RiskSummaryCards           ← 4 KPI cards (counts + AI risk score)
│   ├── ComplianceViolations       ← Violations list with regulation badge
│   ├── RiskScoreChart             ← Doughnut: Critical / High / Medium / Low
│   ├── SuspiciousTransactions     ← Flagged payments table
│   ├── AuditInsights              ← AI narrative findings (severity tagged)
│   └── AgentActivityFeed          ← What each agent did + timestamps
│
├── forecasting/page.tsx
│   ├── ForecastKPIs               ← Growth rate, confidence, peak revenue
│   ├── RevenueForecastChart       ← Line chart (actuals + projected)
│   ├── CashFlowForecast           ← Cashflow bar projection
│   ├── ForecastMethodology        ← Explains Prophet vs exponential smoothing
│   ├── TrendAnalysis              ← Up / Down / Neutral trend cards
│   └── AIRecommendations          ← CFO-level actionable items
│
├── chat/page.tsx
│   ├── SuggestedPrompts           ← Quick-start questions
│   ├── MessageBubble              ← User / AI message bubbles
│   ├── TypingIndicator            ← AI thinking animation
│   └── PromptInput                ← Chat input + send button
│
└── documents/page.tsx
    ├── UploadZone                 ← Drag-drop or click to upload
    ├── UploadedDocuments          ← History of all uploads
    ├── OCRResultsCard             ← Extracted raw text preview
    ├── DocumentAnalysis           ← Key metrics & insights summary
    └── InvoiceInsights            ← Vendor, invoice#, tax, amounts
```

### State Management (Zustand)

```
authStore      → user, token, setAuth(), logout()          [persisted to localStorage]
uploadStore    → uploading, uploadedFiles[], activeDocument, upload()
chatStore      → messages[], isLoading, sendMessage()
dashboardStore → kpis, charts, loading
auditStore     → riskData, violations, transactions, refreshAudit()
forecastStore  → forecast, methodology, recommendations, refreshForecast()
agentStore     → agentStatuses[], activityFeed, pollAgentStatus()
```

### Services Layer

```
upload.service.ts    → uploadDocument(), fetchDocuments(), fetchActiveContext()
chat.service.ts      → sendMessage(), getHistory()
dashboard.service.ts → fetchKPIs(), fetchRevenue(), fetchRiskHeatmap()
audit.service.ts     → fetchAuditAnalysis(), fetchRiskTransactions(), refreshAudit()
forecast.service.ts  → fetchForecast(), fetchMethodology(), refreshForecast()
agents.service.ts    → fetchAgentStatus(), fetchActivityFeed()
sql.service.ts       → executeQuery(), fetchSchema()
```

---

## Backend Architecture

### Folder Structure

```
backend/
├── app/
│   ├── main.py                   ← FastAPI app + CORS + DB startup
│   ├── api/
│   │   ├── router.py             ← Registers all 12 routers under /api
│   │   └── routes/
│   │       ├── auth.py           ← /api/auth
│   │       ├── chat.py           ← /api/chat
│   │       ├── dashboard.py      ← /api/dashboard
│   │       ├── audit.py          ← /api/audit
│   │       ├── forecasting.py    ← /api/forecast
│   │       ├── reports.py        ← /api/reports  (PDF + CSV export)
│   │       ├── upload.py         ← /api/documents
│   │       ├── agents.py         ← /api/agents
│   │       ├── sql_agent.py      ← /api/sql-agent
│   │       ├── search.py         ← /api/search
│   │       ├── notifications.py  ← /api/notifications
│   │       └── settings_route.py ← /api/settings
│   ├── core/
│   │   ├── database.py           ← SQLAlchemy engine + SessionLocal
│   │   ├── llm_factory.py        ← get_llm() — provider-agnostic LLM
│   │   ├── security.py           ← JWT create/verify, bcrypt hashing
│   │   └── config.py             ← Pydantic Settings loaded from .env
│   ├── models/                   ← SQLAlchemy ORM table definitions
│   └── services/                 ← Business logic (chat, OCR, forecast, SQL)
├── uploads/                      ← Uploaded files + active_context.json cache
└── requirements.txt
```

### Core Modules

**`llm_factory.py`** — Single source of truth for all LLM calls
```python
# Switch between providers with one env var — no code changes needed
LLM_PROVIDER = "openrouter"  # or "groq"

get_llm() → ChatOpenAI pointing to OpenRouter (Llama 3.3 70B, free tier)
          → ChatGroq   pointing to Groq       (Llama 3.3 70B, rate-limited)
```

**`database.py`** — Graceful PostgreSQL with SQLite fallback
```python
SessionLocal = sessionmaker(engine)
get_db()     → yields a DB session; returns None if DB unavailable
               (app keeps running — reads fall back to active_context.json)
```

**`security.py`** — JWT + bcrypt
```python
create_access_token(data)   → signed HS256 JWT
verify_token(token)         → returns payload or raises 401
hash_password / verify_password  → passlib + bcrypt
```

---

## Database Schema

```
┌──────────────────────────────────────────┐
│                  users                   │
│  id · email (unique) · name              │
│  hashed_password · role · avatar_color   │
│  is_active · created_at                  │
└──────────────┬───────────────────────────┘
               │ 1 : N
               ▼
┌──────────────────────────────────────────┐
│               documents                  │
│  id · filename · content_type            │
│  document_type · company_name · period   │
│  summary · currency                      │
│  key_metrics (JSON) · insights (JSON)    │
│  risks (JSON) · positives (JSON)         │
│  raw_numbers (JSON) · raw_text           │
│  file_path · created_at                  │
└──────────────┬───────────────────────────┘
               │ 1 : N
               ▼
┌──────────────────────────────────────────┐
│             chat_messages                │
│  id · document_id · role · content       │
│  created_at                              │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│             notifications                │
│  id · title · message · type · is_read   │
│  created_at                              │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│             user_settings                │
│  id · currency · usd_to_inr_rate         │
│  theme · llm_provider · date_format      │
│  language · notifications_enabled        │
└──────────────────────────────────────────┘
```

---

## AI & LLM Stack

### Document Processing Pipeline

```
User uploads file (PDF / CSV / Excel / Image / TXT)
                │
                ▼
        File Type Detection
   ┌────┬──────┬───────┬────────┐
   PDF  CSV   Excel   Image    TXT
   │    │      │        │        │
  pypdf pandas pandas Tesseract  read()
  PyMuPDF                OCR
                │
                ▼
        Raw Text Extracted
                │
                ▼
        LLM Extraction Prompt  →  JSON output:
        ┌────────────────────────────────────┐
        │  document_type, company, period    │
        │  currency, summary                 │
        │  key_metrics[]                     │
        │  insights[], risks[], positives[]  │
        │  raw_numbers { revenue, expenses,  │
        │                profit, cashflow }  │
        │  suggested_questions[]             │
        └────────────────────────────────────┘
                │
                ▼
  Save to PostgreSQL (documents table)
  Save to uploads/active_context.json  ← fast cache for all routes
  Create notification
  Return to frontend
```

### Audit AI Pipeline

```
GET /api/audit  (or POST /api/audit/refresh)
        │
        ▼
Check active_context.json
├── cached? → return instantly (no LLM call)
└── not cached?
        │
        ▼
LLM Audit Prompt — Indian Regulatory Framework
┌──────────────────────────────────────────────────────┐
│  CORPORATE LAW                                       │
│    Companies Act 2013 — Sec 129, 134, 177, 185,      │
│                          186, 188, Schedule II/III   │
│    SEBI LODR 2015 — RPT thresholds, governance       │
│    Ind AS 115 (revenue) · 116 (leases)               │
│    Ind AS 109 (ECL) · 36 (impairment) · 19 (benefits)│
│                                                      │
│  TAXATION                                            │
│    Income Tax Act — Sec 194C/J/I/H/Q (TDS sections) │
│    GST Act 2017 — Sec 16 ITC, e-invoicing, GSTR-9   │
│    Transfer Pricing — Sec 92 arm's length            │
│                                                      │
│  MSME & PAYMENTS                                     │
│    MSMED Act 2006 — 45-day payment limit             │
│    PMLA — suspicious transaction patterns            │
│                                                      │
│  AUDIT STANDARDS                                     │
│    SA 240 (fraud responsibility) · SA 315 (risk)     │
│    CARO 2020 — audit reporting requirements          │
└──────────────────────────────────────────────────────┘
        │
        ▼
Returns structured JSON:
  risk_summary    → 4 KPI card values
  insights[]      → severity: critical / high / medium / info
  transactions[]  → risk: HIGH / MEDIUM / LOW  +  flag reason
  violations[]    → issue + severity + regulation reference
  risk_distribution[] → pie chart percentages
        │
        ▼
Cached in active_context.json  →  all audit endpoints return instantly
```

### AI Report Generation

```
POST /api/reports/generate
        │
        ▼
Load active_context.json (document + audit + forecast data)
        │
        ▼
LLM Report Prompt  →  Structured JSON:
  executive_summary · key_highlights[]
  financial_performance {}
  risk_assessment { overall_risk, risk_score, top_risks[] }
  compliance_status { overall_status, issues, recommendations[] }
  forecast_outlook · cfo_recommendations[]
        │
        ▼
fpdf builds multi-page PDF in-process:
  Cover page → Executive Summary → Key Highlights →
  Financial Performance → Risk Assessment →
  Compliance & Regulatory Status → Forecast Outlook →
  CFO Recommendations → Appendix (Key Metrics table)
        │
        ▼
Streamed to browser as  FinSphere_Report_YYYYMMDD.pdf
```

### Document Context Cache

```
uploads/active_context.json  ← single source of truth for all routes
┌───────────────────────────────────────────────────────┐
│  filename, document_type, company_name, currency      │
│  summary, key_metrics[], raw_numbers{}                │
│  raw_text  (first 50 000 chars)                       │
│  audit_analysis {}    ← written after first LLM call  │
│  forecast_analysis {} ← written after first forecast  │
└───────────────────────────────────────────────────────┘

All backend routes (dashboard, chat, audit, forecast)
read from this file first → instant page loads,
no repeated LLM calls on every refresh.
```

---

## AI Microservice — LangGraph Agents

```
ai-services/
├── agents/
│   ├── supervisor_agent.py   ← Routes user intent to the right agent
│   ├── audit_agent.py        ← Fraud & compliance detection
│   ├── forecast_agent.py     ← Revenue & cashflow projection
│   ├── sql_agent.py          ← NL → SQL translation
│   ├── rag_agent.py          ← Document retrieval + summarization
│   ├── ocr_agent.py          ← Image / scanned PDF → text
│   └── report_agent.py       ← Structured report assembly
│
├── langgraph/
│   ├── graph_builder.py      ← Compile StateGraph
│   ├── nodes.py              ← Node function per agent
│   └── edges.py              ← Conditional routing logic
│
├── models/
│   ├── anomaly_detection.py  ← Isolation Forest, One-Class SVM
│   ├── risk_scoring.py       ← Transaction risk scoring
│   └── forecasting_model.py  ← Prophet, exponential smoothing
│
└── vectorstore/
    ├── chroma_manager.py     ← Chroma DB CRUD
    └── embedding_service.py  ← sentence-transformers embeddings
```

### Multi-Agent Execution Flow

```
User query
    │
    ▼
Supervisor Agent  (routes by detected intent)
    │
    ├──► Audit Agent       → compliance check + fraud flags
    ├──► Forecast Agent    → 6-month projection + CFO recommendations
    ├──► SQL Agent         → NL → SQL → execute → results table
    ├──► RAG Agent         → vector search → relevant chunks → answer
    ├──► OCR Agent         → image / scanned PDF → extracted text
    └──► Report Agent      → compile final structured report
```

---

## Data Flow Walkthrough

### Chat Flow

```
1. User types message
2. POST /api/chat  { message }
3. Backend loads active_context.json
4. Intent detection (keyword match: fraud / forecast / general)
5. Build context-aware LLM prompt with:
   document metadata · key metrics · insights · raw text
6. LLM.invoke() → response string
7. Both messages saved to chat_messages table (linked to document)
8. Response returned to frontend
```

### Forecast Flow

```
1. GET /api/forecast
2. Load active_context.json
3. Cached? → return instantly
4. Not cached: LLM generates 6-month forecast JSON:
   chartData[] · kpis {} · methodology · recommendations[]
5. For CSV/tabular data: Prophet or exponential smoothing used
6. Cached in active_context.json
7. Endpoints (chart, KPIs, methodology, trends, cashflow)
   all served from cache
```

### SQL Agent Flow

```
1. POST /api/sql-agent  { query: "What was total revenue in Q3?" }
2. LLM translates NL → SQL using few-shot examples in prompt
3. Execute against target DB (schema fetched from GET /sql-agent/schema)
4. Return results + suggested visualization type
```

### Report + Export Flow

```
AI Report  →  POST /api/reports/generate
               LLM → JSON → fpdf → PDF binary → download

CSV Export →  GET  /api/reports/export
               Build CSV from context (metrics, violations,
               transactions, forecast) → UTF-8 BOM → download
               (UTF-8 BOM ensures correct display in Excel)
```

---

## Security Architecture

```
Registration  →  Password bcrypt-hashed (cost 12) → stored in users table
Login         →  bcrypt verify → create JWT (HS256, 30-min expiry)
                 → stored in localStorage + HttpOnly cookie

Every request →  Axios interceptor adds "Authorization: Bearer <token>"
Backend       →  python-jose decodes + verifies token → extracts user_id
Middleware    →  Next.js middleware.ts protects all routes
                 → unauthenticated requests redirected to /login

CORS          →  backend allows only http://localhost:3000
               →  ai-services allows * (internal network only)
```

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| **JSON cache (`active_context.json`)** | All routes read from one file — instant page loads, no repeated LLM calls per request |
| **Provider-agnostic LLM via `get_llm()`** | Switch between OpenRouter (free) and Groq (fast) with a single env var — no code changes |
| **Graceful DB fallback** | App runs without PostgreSQL — ideal for demos; falls back to JSON file for document data |
| **Indian regulatory audit prompt** | Explicitly covers Companies Act, Ind AS, GST Act, Income Tax Act, MSMED Act, SEBI LODR, SA standards |
| **Audit failure not cached** | If LLM fails, the fallback message is shown but NOT cached — next request retries the LLM automatically |
| **fpdf for PDF reports** | No third-party service dependency — PDF built entirely in-process and streamed as a response |
| **Zustand over Redux** | Dramatically less boilerplate; straightforward for this scale of state |
| **Next.js App Router** | File-based routing, server components, built-in middleware auth guard |
| **UTF-8 BOM on CSV export** | Ensures CSV opens correctly in Microsoft Excel without garbled characters |

---

## Full API Reference

### Auth — `/api/auth`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login → returns JWT |
| GET | `/api/auth/me` | Current user info |
| PATCH | `/api/auth/me` | Update profile |

### Documents — `/api/documents`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload & extract financial document |
| GET | `/api/documents/list` | All uploaded documents |
| GET | `/api/documents/active-context` | Currently loaded document metadata |

### Dashboard — `/api/dashboard`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/kpis` | Revenue, expenses, profit, cashflow KPIs |
| GET | `/api/dashboard/revenue` | Monthly revenue chart data |
| GET | `/api/dashboard/risk-heatmap` | Risk severity tiles |
| GET | `/api/dashboard/forecast-chart` | 6-month projection |

### Audit — `/api/audit`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/audit` | Full audit findings |
| GET | `/api/audit/violations` | Compliance violations with regulation reference |
| GET | `/api/audit/risk-transactions` | High-risk flagged transactions |
| GET | `/api/audit/risk-score` | Risk distribution (Critical/High/Medium/Low) |
| GET | `/api/audit/risk-summary` | 4 KPI card values |
| POST | `/api/audit/refresh` | Force re-analyze current document |

### Forecast — `/api/forecast`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/forecast` | Full 6-month forecast |
| GET | `/api/forecast/methodology` | How the forecast was computed |
| GET | `/api/forecast/trends` | Trend analysis (up/down/neutral) |
| GET | `/api/forecast/cashflow` | Cashflow projection |
| GET | `/api/forecast/recommendations` | CFO-level recommendations |
| POST | `/api/forecast/refresh` | Recalculate forecast |

### Chat — `/api/chat`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message → AI reply |
| GET | `/api/chat/history` | Load conversation history |
| DELETE | `/api/chat/history` | Clear chat |

### Reports — `/api/reports`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/generate` | Generate AI executive PDF report |
| GET | `/api/reports/export` | Export all dashboard data as CSV |

### Agents — `/api/agents`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents/status` | Agent pool status (active/idle/processing) |
| GET | `/api/agents/activities` | Agent execution log |

### SQL Agent — `/api/sql-agent`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sql-agent` | Natural language → SQL → execute → results |
| GET | `/api/sql-agent/schema` | Available tables & columns |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search` | Full-text search across documents |
| GET | `/api/notifications` | User notifications |
| PATCH | `/api/notifications/{id}/read` | Mark notification as read |
| PATCH | `/api/notifications/read-all` | Mark all as read |
| GET | `/api/settings` | User preferences |
| PATCH | `/api/settings` | Update preferences |
| GET | `/health` | Health check |

---

## Tech Stack Summary

| Layer | Technology | Role |
|-------|------------|------|
| **Frontend** | Next.js 14, React 18, TypeScript | SPA with App Router |
| **UI** | Tailwind CSS, Radix UI, Framer Motion | Styling & components |
| **State** | Zustand | Lightweight client-side state |
| **Charts** | Recharts | Financial data visualization |
| **Tables** | @tanstack/react-table | Paginated data tables |
| **Backend** | FastAPI, Uvicorn | Async REST API server |
| **LLM** | LangChain + OpenRouter / Groq | AI inference (Llama 3.3 70B) |
| **Agents** | LangGraph | Multi-agent orchestration |
| **Database** | PostgreSQL + SQLAlchemy | Persistent relational storage |
| **Vector DB** | Chroma + sentence-transformers | RAG embeddings & retrieval |
| **PDF Read** | pypdf, PyMuPDF, Tesseract (OCR) | Document text extraction |
| **PDF Write** | fpdf2 | AI report PDF generation |
| **Spreadsheets** | pandas | CSV & Excel processing |
| **Forecasting** | Prophet, scikit-learn | Time-series ML models |
| **Auth** | JWT (python-jose), bcrypt | Security |
| **HTTP Client** | Axios | API communication from frontend |

---

*Built by Jeel Patel · FinSphere AI v2.0*
