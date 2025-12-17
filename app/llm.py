from __future__ import annotations

import textwrap
from typing import Optional

from .config import settings


class LLMClient:
    """
    Minimal LLM client with an offline fallback so the system works without API keys.
    Plug your provider (OpenAI/Claude/Gemini/etc.) inside `generate` when configured.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.provider = provider or settings.llm_provider
        self.api_key = api_key or settings.llm_api_key
        self.base_url = base_url or settings.llm_base_url

    @property
    def is_configured(self) -> bool:
        return bool(self.provider and self.api_key)

    async def generate(self, prompt: str) -> str:
        if not self.is_configured:
            return self._offline_generate(prompt)
        # This is intentionally left unimplemented to avoid accidental external calls.
        # Hook in your provider SDK or HTTP call here.
        return self._offline_generate(prompt)

    def _offline_generate(self, prompt: str) -> str:
        trimmed = textwrap.shorten(prompt.replace("\n", " "), width=240, placeholder=" ...")
        return f"[offline-llm] Prompt received: {trimmed}"
