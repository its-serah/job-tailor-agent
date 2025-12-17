from __future__ import annotations

from typing import List, Optional

from ..llm import LLMClient
from ..models.schemas import ApplicationPacket, PlanStep, RequirementMatch


class GenerationAgent:
    def __init__(self, llm: Optional[LLMClient] = None) -> None:
        self.llm = llm or LLMClient()

    async def generate_packet(
        self,
        requirements: List[str],
        plan: List[PlanStep],
        matches: List[RequirementMatch],
    ) -> ApplicationPacket:
        cover_letter = self._compose_cover_letter(requirements, matches)
        tailored_bullets = self._build_tailored_bullets(matches)
        talking_points = self._build_talking_points(matches)
        return ApplicationPacket(
            cover_letter=cover_letter,
            tailored_bullets=tailored_bullets,
            talking_points=talking_points,
        )

    def _compose_cover_letter(self, requirements: List[str], matches: List[RequirementMatch]) -> str:
        top_reqs = requirements[:3]
        top_reqs_text = "; ".join(top_reqs) if top_reqs else "the role"
        strongest = []
        for match in matches:
            if not match.matches:
                continue
            strongest.append(match.matches[0].text)
        strongest = strongest[:3]
        strengths_text = " | ".join(strongest) if strongest else "relevant experience from my background"
        lines = [
            "Dear Hiring Team,",
            f"I am excited about this role and its focus on {top_reqs_text}.",
            f"My closest fit includes: {strengths_text}.",
            "I can quickly map your priorities to proven outcomes and ship a tailored application packet for your review.",
            "Thank you for your consideration.",
        ]
        return "\n".join(lines)

    def _build_tailored_bullets(self, matches: List[RequirementMatch]) -> List[str]:
        bullets: List[str] = []
        for match in matches:
            if not match.matches:
                continue
            best = match.matches[0]
            bullets.append(f"{match.requirement}: {best.text} (score {best.score:.2f})")
        return bullets

    def _build_talking_points(self, matches: List[RequirementMatch]) -> List[str]:
        flat_hits = []
        for match in matches:
            for hit in match.matches:
                flat_hits.append((hit.score, hit))
        flat_hits.sort(key=lambda x: x[0], reverse=True)
        talking_points = []
        for _, hit in flat_hits[:5]:
            label = hit.metadata.get("label", "experience")
            talking_points.append(f"{label}: {hit.text} (relevance {hit.score:.2f})")
        return talking_points
