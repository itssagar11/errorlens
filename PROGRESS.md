# ErrorLens - Progress Tracker

## Project Overview
AI-powered error triage platform for Spring Boot microservices.
Automatically classifies production errors using Agentic AI + RAG.

## Developer
- Name: Sagar Bisht
- GitHub: itssagar11
- Role: Associate Software Engineer @ Wissen Technology

---

## Tech Stack
| Layer | Tech |
|---|---|
| Frontend | React + TailwindCSS |
| Backend | FastAPI (Python) |
| AI Agent | LangGraph |
| LLM | OpenAI GPT-4o |
| Vector DB (RAG) | Pinecone |
| Mock Splunk | FastAPI (Python) |
| Deployment | Vercel (frontend) + Railway (backend) |
| Containerization | Docker + docker-compose |

---

## System Architecture
```
React UI (Vercel)
    ↓
FastAPI Backend (Railway) :8000
    ↓
┌───────────────────────────┐
│         AI Agent          │
│  Tool 1: fetch_trace      │ → Mock Splunk (Railway) :8001
│  Tool 2: check_health     │ → Mock Splunk (Railway) :8001
│  Tool 3: search_kb (RAG)  │ → Pinecone
│  Tool 4: error_frequency  │ → Mock Splunk (Railway) :8001
└───────────────────────────┘
    ↓
Verdict: category + severity + reasoning + action
```

## API Design
```
Mock Splunk (port 8001)
├── GET  /splunk/logs                # fetch logs with filters
├── GET  /splunk/logs/{unique_id}    # fetch single log by txnId
├── GET  /splunk/health/{service}    # service health at a time
└── GET  /splunk/apps                # list all applications

ErrorLens Backend (port 8000)
├── POST /api/errors/analyse         # main - fetch + triage
├── GET  /api/errors/filters         # available apps, sites etc
└── GET  /api/health                 # backend health check
```

---

## Folder Structure
```
errorlens/
├── mock_splunk/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── data/
│       ├── logs/
│       │   ├── payment-service.log
│       │   ├── trade-service.log
│       │   ├── auth-service.log
│       │   ├── notification-service.log
│       │   └── user-profile-service.log
│       ├── service_health.json
│       └── knowledge_base/
│           └── resolved_errors.json
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py
│   ├── routers/
│   │   ├── errors.py
│   │   └── health.py
│   ├── services/
│   │   ├── splunk_service.py
│   │   └── triage_service.py
│   └── agent/
│       ├── agent.py
│       ├── tools.py
│       └── prompts.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FilterPanel.jsx
│   │   │   ├── ErrorCard.jsx
│   │   │   ├── SeverityBadge.jsx
│   │   │   └── ReasoningPanel.jsx
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   └── services/
│   │       └── api.js
│   └── package.json
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   └── api-reference.md
├── docker-compose.yml
├── .env.example
├── PROGRESS.md               ← YOU ARE HERE
└── README.md

---

## Sessions

### Session 1 — 28 March 2026
**Status:** Project setup
**Decisions Made:**
- App name: ErrorLens
- GitHub repo: itssagar11/errorlens
- Starting with Mock Splunk first
- Log format: Real Spring Boot .log file format
- Agentic AI + RAG combined approach
- Single repo for everything

**Completed:**
- [x] System design
- [x] Folder structure decided
- [x] Tech stack finalized
- [x] GitHub repo created
- [x] PROGRESS.md created

**Next Session — Start Here:**
1. Create folder structure
2. Create mock Spring Boot .log files (5 services)
3. Build mock_splunk/main.py (FastAPI)
4. Test Splunk API with Postman

---

## Key Interview Talking Points
- Agentic AI vs RAG — agent dynamically decides what to investigate
- Why LangGraph — multi-step reasoning, agent controls the flow
- Why Mock Splunk as separate service — mirrors real architecture, easy to swap
- Log parsing — handles real Spring Boot format with/without stack traces
- RAG layer — past resolved errors as knowledge base, semantic search via Pinecone

---

## Resume Line (update as we build)
"Built ErrorLens — an agentic AI + RAG platform that auto-triages 
production Spring Boot errors by dynamically investigating stack traces, 
service health, and historical error patterns using LangGraph + OpenAI + Pinecone"
```

---