# Job Application Multi-Agent Workflow

A lightweight FastAPI controller that orchestrates parsing, planning, retrieval, reasoning, and generation steps for tailoring job applications. It keeps the heavy cognitive work inside agents and leaves review/submission to you.

## Stack & modules
- FastAPI controller (`app/main.py`) with `/process`, `/memory`, and `/memory/search`.
- Parsing agent (`agents/parsing.py`) fetches a provided job URL or raw text and extracts requirement-like lines.
- Planner agent (`agents/planner.py`) builds a concise step-by-step tailoring plan (LLM pluggable, offline fallback).
- Vector memory (`memory.py`) stores skills/projects/publications/CV bullets with TF-IDF embeddings and cosine similarity (FAISS/Chroma-style interface).
- Reasoning agent (`agents/reasoning.py`) maps each requirement to the closest memory hits.
- Generation agent (`agents/generation.py`) drafts a packet: cover letter snippet, tailored bullets, and talking points.
- Orchestrator (`orchestrator.py`) wires everything together.

## Quickstart (local dev)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

FastAPI docs: http://127.0.0.1:8000/docs

## Running with Docker
Build and run the container:
```bash
docker build -t job-tailor-agent .
docker run -p 8000:8000 --env-file .env job-tailor-agent
```

The API will be available at `http://127.0.0.1:8000`.

## Development workflow
- Run the app locally:
  ```bash
  make run
  ```
- Run the test suite:
  ```bash
  make test
  ```

## Example usage
1) Load profile memory (skills/projects/publications/CV bullets):
```bash
curl -X POST http://127.0.0.1:8000/memory \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"label": "skill", "text": "Built multi-agent job tailoring workflow with FastAPI orchestrator and vector memory; reduced drafting time by 80%"},
      {"label": "project", "text": "Deployed LLM planner + reasoning agents using embeddings to map requirements to CV bullets; shipped in Cursor/Claude"},
      {"label": "publication", "text": "Wrote about pragmatic agentic workflows using Claude, Gemini, and Codex backed by FAISS-like retrieval"}
    ]
  }'
```

2) Process a job post (either `job_url` or `job_text`):
```bash
curl -X POST http://127.0.0.1:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "job_text": "We need an engineer to design agentic workflows, build FastAPI services, and use embeddings for semantic retrieval.",
    "top_k": 3
  }'
```

3) Search memory directly:
```bash
curl -X POST http://127.0.0.1:8000/memory/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"agentic workflows\", \"top_k\": 2}"
```

## Notes
- LLM calls run offline by default (see `llm.py`). Set `LLM_PROVIDER` and `LLM_API_KEY` env vars and plug your client code inside `LLMClient.generate` to hit Claude/Gemini/Codex/etc.
- The parsing agent only acts on links you manually provide; no crawling or mass automation is included.
- Memory items persist in-process; restart the server to clear, or extend `VectorMemory` with persistence as needed.

## Environment variables
- `LLM_PROVIDER` – optional, name of your LLM provider.
- `LLM_API_KEY` – optional, key for your LLM provider.
- `LLM_BASE_URL` – optional, override base URL for self-hosted / custom endpoints.
- `MAX_REQUIREMENTS` – max number of requirements to extract from a job post (default: 30).
- `RETRIEVAL_TOP_K` – default number of memory items to retrieve per requirement (default: 3).
- `CORS_ALLOW_ORIGINS` – optional, JSON list of allowed origins for CORS (default: ["*"]).
