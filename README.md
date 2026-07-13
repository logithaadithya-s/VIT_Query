# Research Paper Intelligence Platform

A **Next.js** frontend + **FastAPI** backend for college staff to upload research papers, detect plagiarism, and discover research gaps using an AI agent.

## Features

- **Premium Next.js UI** — dark glassmorphism design with animations
- **Paper upload & storage** — PDF, DOCX, TXT with metadata
- **Plagiarism detection** — TF-IDF similarity + passage matching; blocks 70%+ duplicates
- **Field analytics** — charts for active fields, gaps, keywords, departments
- **AI Research Agent** — analyzes what's being worked on vs. what needs attention
- **Agent integrations** — OpenAI, Ollama (local), Claude, LangGraph (documented in UI)

## Quick Start

```bash
# 1. Backend setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py          # optional sample papers

# 2. Frontend setup
cd frontend && npm install && cd ..

# 3. Run both (recommended)
python main.py
```

Open **http://localhost:3000**

### Run separately

```bash
# Terminal 1 — API
uvicorn app.main:app --reload --port 8000

# Terminal 2 — UI
cd frontend && npm run dev
```

## AI Agent Setup (Optional)

The built-in rules engine works without any API key. For smarter analysis:

```bash
# OpenAI (recommended)
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini

# Or local Ollama (free, private)
ollama run llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

Then visit the **AI Agent** page and click "Re-run Analysis".

### Recommended agents to integrate

| Agent | Best For | Setup |
|-------|----------|-------|
| **OpenAI GPT-4o** | Rich gap analysis, project ideas | `OPENAI_API_KEY` env var |
| **Ollama (local)** | Privacy, offline, zero cost | Run `ollama run llama3.2` |
| **Anthropic Claude** | Long-context corpus analysis | Extend `research_agent.py` |
| **LangGraph** | Multi-step retrieve → analyze → recommend | Agent framework |
| **Cursor MCP Agent** | Automated repo reviews | Connect to `/api/analytics/agent-insights` |

## Project Structure

```
├── frontend/              # Next.js app (primary UI)
│   └── src/app/           # Pages: dashboard, upload, agent, etc.
├── app/                   # FastAPI backend
│   ├── routers/
│   └── services/
│       ├── plagiarism.py
│       ├── field_analyzer.py
│       └── research_agent.py   # AI agent
├── data/                  # SQLite + uploads
├── main.py                # Starts both servers
└── seed_data.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/papers/upload` | Upload paper |
| POST | `/api/papers/check-plagiarism` | Check without saving |
| GET | `/api/analytics/overview` | Dashboard analytics |
| GET | `/api/analytics/agent-insights` | AI research analysis |
| GET | `/api/analytics/agent-suggestions` | Agent integration guide |

## Tech Stack

- **Frontend:** Next.js 16, TypeScript, Tailwind CSS, Framer Motion, Recharts
- **Backend:** FastAPI, SQLAlchemy, scikit-learn
- **AI Agent:** OpenAI / Ollama / rules engine fallback
