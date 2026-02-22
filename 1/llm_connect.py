# llm_connect.py — Reusable OpenRouter LLM connection
#
# Provides a factory function that returns a ChatOpenAI instance
# configured for OpenRouter. Any script can call get_llm() to
# get a ready-to-use LangChain chat model.

from pathlib import Path

import yaml
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load .env once at import time
load_dotenv()

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Load config.yaml (sits next to this file)
_CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(_CONFIG_PATH) as f:
    _CONFIG = yaml.safe_load(f)

_DEFAULT_MODEL: str = _CONFIG["model"]["default"]


def get_llm(
    model: str = _DEFAULT_MODEL,
    temperature: float = 0,
) -> ChatOpenAI:
    """Return a ChatOpenAI instance pointed at OpenRouter.

    Args:
        model: OpenRouter model identifier (e.g. "anthropic/claude-sonnet-4.6").
        temperature: Sampling temperature (0 = deterministic).
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Add it to your .env file."
        )

    return ChatOpenAI(
        model=model,
        base_url=_OPENROUTER_BASE_URL,
        api_key=api_key,
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "LangChain Learning",
        },
    )
