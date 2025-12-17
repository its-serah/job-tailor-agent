from __future__ import annotations

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logging_config import setup_logging
from .models.schemas import MemoryIngestRequest, ProcessRequest, ProcessResponse, SearchRequest, SearchResult
from .orchestrator import Orchestrator

setup_logging()

app = FastAPI(title="Job Application Multi-Agent Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
orchestrator = Orchestrator()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/memory", response_model=List[str])
async def ingest_memory(payload: MemoryIngestRequest) -> List[str]:
    return orchestrator.add_memory_items(payload.items)


@app.post("/memory/search", response_model=List[SearchResult])
async def search_memory(payload: SearchRequest) -> List[SearchResult]:
    hits = orchestrator.search_memory(payload.query, payload.top_k)
    return [SearchResult(**hit) for hit in hits]


@app.post("/process", response_model=ProcessResponse)
async def process_job(payload: ProcessRequest) -> ProcessResponse:
    return await orchestrator.process(
        job_url=payload.job_url,
        job_text=payload.job_text,
        profile_items=payload.profile_items,
        top_k=payload.top_k,
    )
