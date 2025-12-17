from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    id: Optional[str] = None
    text: str
    label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryIngestRequest(BaseModel):
    items: List[MemoryItem]


class MemoryItemResponse(MemoryItem):
    id: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class RequirementSet(BaseModel):
    requirements: List[str]


class PlanStep(BaseModel):
    title: str
    detail: str
    order: int


class RequirementMatch(BaseModel):
    requirement: str
    matches: List[SearchResult]


class ApplicationPacket(BaseModel):
    cover_letter: str
    tailored_bullets: List[str]
    talking_points: List[str]


class ProcessRequest(BaseModel):
    job_url: Optional[str] = None
    job_text: Optional[str] = None
    profile_items: List[MemoryItem] = Field(default_factory=list)
    top_k: Optional[int] = None


class ProcessResponse(BaseModel):
    requirements: List[str]
    plan: List[PlanStep]
    matches: List[RequirementMatch]
    packet: ApplicationPacket
