# AI Local Business Intelligence Agent

A multi-agent system (FastAPI + LangGraph backend, Next.js dashboard) that researches a local business's
market, competitors, reviews, and website, then produces an evidence-labeled intelligence report with
prioritized recommendations. Includes a live "Agent Trace" panel and a RAG-grounded "Ask Your Local
Market" chat.

This has been built and verified end-to-end in **mock mode**, which uses realistic generated data so the
whole pipeline (research → competitor analysis → review intelligence → market gaps → insights →
recommendations → dashboard → chat) runs and demos without any API keys. Flip `MOCK_MODE=false` and add
real keys to pull live data.

## What's real vs. mocked by default

- The agent graph, evidence-linking, DB persistence, streaming, dashboard, and chat are all fully
  functional real code — verified by running the pipeline directly and over HTTP.
- With no `GOOGLE_PLACES_API_KEY`, `local_business_research` and `review_intelligence` generate realistic
  mock competitors/reviews instead of hitting the real Google Places API.
- With no `ANTHROPIC_API_KEY`, the Market Gap, Insight Generator, and Recommendation agents fall back to
  deterministic rule-based logic instead of LLM calls, and Ask Your Local Market falls back to a templated
  answer built directly from retrieved evidence instead of an LLM-composed one.
- This means the demo works out of the box, and gets smarter (real competitors, real reviews, richer
  LLM-generated insights) the moment you add real keys.

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Visit `http://127.0.0.1:8000/` — you should see `{"status": "ok", "mock_mode": true}`.

### Environment variables (backend/.env)

| Variable | Purpose | Required for real data? |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string, defaults to local SQLite | No |
| `ANTHROPIC_API_KEY` | Enables real LLM reasoning for planning, gaps, insights, recommendations, and chat | No (falls back to rules) |
| `GOOGLE_PLACES_API_KEY` | Enables real competitor/review data via Google Places | No (falls back to mock data) |
| `TAVILY_API_KEY` | Enables real web search in the research step | No |
| `MOCK_MODE` | Force mock data even if keys are present, set to `false` to prefer live APIs when keys exist | — |
| `LLM_MODEL` | Anthropic model name | — |
| `CORS_ORIGINS` | Comma-separated origins allowed to call the API | — |

## Frontend setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:3000`, type a query like `Coffee shop in Indiranagar, Bangalore`, and watch the
Agent Trace panel populate the dashboard live.

## Project structure

```
backend/
  app/
    main.py                 FastAPI app entrypoint, CORS, table creation
    api/                     runs.py (CRUD + SSE stream), ask.py (RAG chat)
    agents/                  one file per agent node + graph.py wiring them with LangGraph
    tools/                   places_api, web_search, scraper, sentiment, geo, llm
    db/                      SQLAlchemy models, session, CRUD helpers
    core/                    settings, in-memory cache, in-memory event bus for streaming
frontend/
  app/                       landing page + dynamic dashboard route
  components/                AgentTrace, CompetitorTable, charts, PriorityActionPlan,
                              EvidenceLog, AskMarketChat
  lib/                       typed API client + shared types
```

## How the evidence-labeling requirement is enforced

Every claim in the system carries one of four labels — FACT, OBSERVATION, AI_INSIGHT, RECOMMENDATION —
and this is enforced structurally, not just by prompting:

- `FACT` and `OBSERVATION` records are only ever created by tool-calling agents (Places API results,
  scraped website data, computed sentiment/topic counts) — never by the LLM.
- Every `AI_INSIGHT` the Market Gap and Insight Generator agents produce must carry at least one
  `supporting_evidence_ids` entry; insights without evidence are dropped before being added to state.
  When running with an LLM, the same evidence-index requirement is enforced in the prompt and re-checked
  in code.
- Every `RECOMMENDATION` must reference the `insight_ids` it addresses, so you can always click from a
  recommendation → the insight behind it → the evidence behind that.
- The dashboard renders each of these with a distinct color (gray/blue/purple/green) so the provenance is
  visible at a glance, not just in the data model.

## Extending to live data

1. Get a Google Places API key (Places API + Places Details enabled) and a Tavily API key.
2. Get an Anthropic API key.
3. Set all three in `backend/.env` and set `MOCK_MODE=false`.
4. Restart the backend. `local_business_research`, `review_intelligence`, and `website_analyzer` will now
   hit real data, and `market_gap`, `insight_generator`, `recommendation_agent`, and `ask_market` will use
   real Claude reasoning grounded in that data.

## Known limitations / stretch items not yet built

- No vector database (pgvector/Chroma) yet — Ask Your Local Market uses keyword-overlap retrieval over the
  evidence table, which is fast and dependency-light but less semantically precise than embeddings. Swap
  `agents/ask_market.py`'s `retrieve_relevant_evidence` for an embedding-based lookup if you have time.
- No map view of competitors (list/table only).
- No PDF/exportable report — the dashboard itself is the report.
- Sentiment/topic extraction is keyword-based rather than a trained classifier, by design, to keep the
  MVP fast, dependency-light, and fully explainable for a demo.
