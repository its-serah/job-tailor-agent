from __future__ import annotations

import textwrap
from typing import List, Optional

from ..llm import LLMClient
from ..models.schemas import PlanStep


class PlannerAgent:
    def __init__(self, llm: Optional[LLMClient] = None) -> None:
        self.llm = llm or LLMClient()

    async def build_plan(self, requirements: List[str], profile_summary: str = "") -> List[PlanStep]:
        if not requirements:
            return []
        condensed = textwrap.shorten(" | ".join(requirements), width=260, placeholder=" ...")
        prompt = (
            "You are designing a concise tailoring plan for a job application. "
            "Return 4-6 numbered steps covering role analysis, evidence selection, narrative shaping, "
            "and deliverable creation. Keep each step under 30 words.\n\n"
            f"Requirements: {condensed}\nProfile hint: {profile_summary}"
        )
        _ = await self.llm.generate(prompt)
        # Deterministic fallback keeps runtime offline but still captures intent.
        return self._fallback_plan(requirements)

    def _fallback_plan(self, requirements: List[str]) -> List[PlanStep]:
        highlights = ", ".join(requirements[:3]) if requirements else "role expectations"
        templates = [
            ("Clarify the role", f"Distill the top asks ({highlights}) into a 3-line summary and confirm scope."),
            ("Pull strongest evidence", "Surface 3-5 projects/skills that directly match the asks; note quantifiable outcomes."),
            ("Map requirements to proof", "Draft one link per requirement tying evidence to impact; flag any gaps to address."),
            ("Shape the narrative", "Compose a short story arc: motivation, relevant wins, and how you de-risk the hire."),
            ("Build the packet", "Generate cover letter, tailored bullets, and talking points with the mapped evidence."),
        ]
        return [
            PlanStep(title=title, detail=detail, order=i + 1)
            for i, (title, detail) in enumerate(templates)
        ]
