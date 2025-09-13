from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
	llm_provider: Literal["openai", "anthropic"]
	openai_api_key: Optional[str]
	anthropic_api_key: Optional[str]
	http_timeout: int
	checkpoint_path: str


def get_settings() -> Settings:
	load_dotenv()
	provider = os.getenv("LLM_PROVIDER", "openai").lower()
	if provider not in {"openai", "anthropic"}:
		provider = "openai"
	return Settings(
		llm_provider=provider,
		openai_api_key=os.getenv("OPENAI_API_KEY"),
		anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
		http_timeout=int(os.getenv("HTTP_TIMEOUT", "30")),
		checkpoint_path=os.getenv("CHECKPOINT_PATH", ".checkpoints/litrev.sqlite"),
	)
