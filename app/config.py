from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    llm_provider: str | None = Field(default=None, env="LLM_PROVIDER")
    llm_api_key: str | None = Field(default=None, env="LLM_API_KEY")
    llm_base_url: str | None = Field(default=None, env="LLM_BASE_URL")
    max_requirements: int = Field(default=30, env="MAX_REQUIREMENTS")
    retrieval_top_k: int = Field(default=3, env="RETRIEVAL_TOP_K")
    cors_allow_origins: list[str] = Field(default=["*"], env="CORS_ALLOW_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
