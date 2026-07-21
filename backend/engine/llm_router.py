from groq import AsyncGroq
from openai import AsyncOpenAI

from core.config import settings

OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# NOTE: cloud model names are placeholders from the proposal - confirm exact
# ids with each provider's docs before relying on them.
LEVEL_MODELS = {
    1: {"cloud": "gemma2-9b-it", "ollama": "gemma2:2b"},
    2: {"cloud": "gpt-4o-mini", "ollama": "llama3.1"},
    3: {"cloud": "deepseek-chat", "ollama": "llama3.1"},
}


def _level_1_client() -> tuple[AsyncGroq | AsyncOpenAI, str]:
    if settings.groq_api_key:
        return AsyncGroq(api_key=settings.groq_api_key), LEVEL_MODELS[1]["cloud"]
    return AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama"), LEVEL_MODELS[1]["ollama"]


def _level_2_client() -> tuple[AsyncOpenAI, str]:
    if settings.openai_api_key:
        return AsyncOpenAI(api_key=settings.openai_api_key), LEVEL_MODELS[2]["cloud"]
    return AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama"), LEVEL_MODELS[2]["ollama"]


def _level_3_client() -> tuple[AsyncOpenAI, str]:
    if settings.deepseek_api_key:
        return AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=settings.deepseek_api_key), LEVEL_MODELS[3]["cloud"]
    return AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama"), LEVEL_MODELS[3]["ollama"]


_LEVEL_CLIENTS = {1: _level_1_client, 2: _level_2_client, 3: _level_3_client}


async def route_prompt(level_id: int, messages: list[dict], tools: list[dict] | None = None):
    """Send messages to the model assigned to level_id and return the raw
    chat completion. Falls back to a local Ollama model (OpenAI-compatible
    endpoint) when the relevant cloud API key isn't set, so the game loop
    is testable without every teammate holding every API key."""
    get_client = _LEVEL_CLIENTS.get(level_id)
    if get_client is None:
        raise ValueError(f"Unknown level_id: {level_id}")

    client, model = get_client()
    kwargs = {"model": model, "messages": messages}
    if tools:
        kwargs["tools"] = tools

    return await client.chat.completions.create(**kwargs)
