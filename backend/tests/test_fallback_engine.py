import asyncio

from core.config import settings
from engine.llm_router import LLMRouter


def test_call_model_falls_back_to_local_response_when_provider_keys_are_missing(monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", None)
    monkeypatch.setattr(settings, "openai_api_key", None)
    monkeypatch.setattr(settings, "deepseek_api_key", None)

    router = LLMRouter()
    result = asyncio.run(
        router.call_model(
            1,
            [{"role": "system", "content": "You are a test bot."}],
            tools=None,
        )
    )

    assert result["content"]
    assert "fallback" in result["content"].lower()
