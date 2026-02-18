"""Single point of LLM instantiation for the entire project.

Why this module exists:
    All LLM construction goes through this one function.  No other module
    should import ChatOpenAI or call init_chat_model directly.  This makes it
    trivial to change providers, add default headers, or swap to a different
    LangChain wrapper later.

OpenRouter integration:
    OpenRouter exposes an OpenAI-compatible API, so we use ChatOpenAI from
    langchain-openai with the base URL overridden to point at OpenRouter.
    The ``model`` parameter uses OpenRouter's format (e.g.
    "anthropic/claude-sonnet-4-20250514").  ``model_provider`` is always
    "openai" because the *API protocol* is OpenAI-compatible regardless of
    the underlying model.
"""

from langchain_openai import ChatOpenAI

from src.config_loader import get_openrouter_api_key

# OpenRouter endpoint — all models are accessed through this single URL.
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def create_llm(model: str) -> ChatOpenAI:
    """Create and return a ChatOpenAI instance configured for OpenRouter.

    Args:
        model: Model identifier in OpenRouter format,
               e.g. "anthropic/claude-sonnet-4-20250514".

    Returns:
        A ready-to-use ChatOpenAI instance.
    """
    api_key = get_openrouter_api_key()

    # ChatOpenAI works with OpenRouter because OpenRouter speaks the
    # OpenAI-compatible chat completions protocol.
    llm = ChatOpenAI(
        model=model,
        openai_api_base=_OPENROUTER_BASE_URL,
        openai_api_key=api_key,
    )
    return llm
