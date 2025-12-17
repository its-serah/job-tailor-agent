from __future__ import annotations

from typing import List, Optional

from ..memory import VectorMemory
from ..models.schemas import RequirementMatch, SearchResult


class ReasoningAgent:
    def __init__(self, memory: VectorMemory) -> None:
        self.memory = memory

    def match_requirements(self, requirements: List[str], top_k: int = 3) -> List[RequirementMatch]:
        matches: List[RequirementMatch] = []
        for req in requirements:
            search_results = self.memory.search(req, top_k=top_k)
            matches.append(
                RequirementMatch(
                    requirement=req,
                    matches=[
                        SearchResult(
                            id=hit["id"],
                            text=hit["text"],
                            score=hit["score"],
                            metadata=hit["metadata"],
                        )
                        for hit in search_results
                    ],
                )
            )
        return matches
