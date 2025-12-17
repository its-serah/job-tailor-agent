from __future__ import annotations

from typing import List, Optional

from fastapi import HTTPException

from .agents.generation import GenerationAgent
from .agents.parsing import ParsingAgent
from .agents.planner import PlannerAgent
from .agents.reasoning import ReasoningAgent
from .config import settings
from .llm import LLMClient
from .memory import VectorMemory
from .models.schemas import (
    ApplicationPacket,
    MemoryItem,
    PlanStep,
    ProcessResponse,
    RequirementMatch,
)


class Orchestrator:
    def __init__(self) -> None:
        self.memory = VectorMemory()
        self.llm = LLMClient()
        self.parser = ParsingAgent()
        self.planner = PlannerAgent(self.llm)
        self.reasoner = ReasoningAgent(self.memory)
        self.generator = GenerationAgent(self.llm)

    def add_memory_items(self, items: List[MemoryItem]) -> List[str]:
        ids = []
        for item in items:
            record = self.memory.upsert(
                text=item.text,
                metadata={**item.metadata, **({"label": item.label} if item.label else {})},
                record_id=item.id,
            )
            ids.append(record.id)
        return ids

    def search_memory(self, query: str, top_k: int) -> List[dict]:
        return self.memory.search(query, top_k=top_k)

    async def process(
        self,
        job_url: Optional[str],
        job_text: Optional[str],
        profile_items: List[MemoryItem],
        top_k: Optional[int] = None,
    ) -> ProcessResponse:
        if not job_url and not job_text:
            raise HTTPException(status_code=400, detail="Provide job_url or job_text")

        if profile_items:
            self.add_memory_items(profile_items)

        try:
            requirements = await self.parser.extract_requirements(job_url=job_url, job_text=job_text)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Unable to read job post: {exc}") from exc

        plan: List[PlanStep] = await self.planner.build_plan(requirements)
        matches: List[RequirementMatch] = self.reasoner.match_requirements(
            requirements, top_k=top_k or settings.retrieval_top_k
        )
        packet: ApplicationPacket = await self.generator.generate_packet(requirements, plan, matches)
        return ProcessResponse(
            requirements=requirements,
            plan=plan,
            matches=matches,
            packet=packet,
        )
