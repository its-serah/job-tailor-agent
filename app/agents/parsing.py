from __future__ import annotations

import re
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from ..config import settings


class ParsingAgent:
    def __init__(self, max_requirements: int = settings.max_requirements) -> None:
        self.max_requirements = max_requirements

    async def _fetch_url(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def _html_to_text(self, raw: str) -> str:
        soup = BeautifulSoup(raw, "html.parser")
        return soup.get_text(" ", strip=True)

    def _split_into_requirements(self, text: str) -> List[str]:
        candidates = re.split(r"(?:\n|\r|\u2022|•|- )", text)
        cleaned = []
        for cand in candidates:
            normalized = re.sub(r"\s+", " ", cand).strip()
            if len(normalized.split()) < 4:
                continue
            cleaned.append(normalized)
        # Deduplicate while preserving order
        seen = set()
        unique: List[str] = []
        for item in cleaned:
            if item not in seen:
                unique.append(item)
                seen.add(item)
        return unique[: self.max_requirements]

    async def extract_requirements(self, job_url: Optional[str] = None, job_text: Optional[str] = None) -> List[str]:
        if not job_url and not job_text:
            raise ValueError("Provide either job_url or job_text")
        raw = job_text
        if job_url:
            raw = await self._fetch_url(job_url)
        if not raw:
            return []
        text = self._html_to_text(raw)
        return self._split_into_requirements(text)
