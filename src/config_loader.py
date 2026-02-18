"""Load application configuration from config.yaml and environment variables.

Why this module exists:
    Centralizes all configuration access so the rest of the app never reads
    config.yaml or .env directly.  Secrets (API keys) come from environment
    variables only; non-secret settings come from config.yaml.
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Project root is one level up from src/
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Load .env file so os.environ picks up the values
load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> dict[str, object]:
    """Read config.yaml and return its contents as a dictionary.

    Returns:
        Parsed YAML configuration dictionary.

    Raises:
        FileNotFoundError: If config.yaml does not exist.
    """
    config_path = PROJECT_ROOT / "config.yaml"
    with open(config_path, "r") as f:
        config: dict[str, object] = yaml.safe_load(f)
    return config


def get_openrouter_api_key() -> str:
    """Return the OpenRouter API key from the environment.

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set or is empty.
    """
    key: Optional[str] = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set. "
            "Copy .env.example to .env and add your key."
        )
    return key
