"""Model routing for level-specific LLM providers."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from anthropic import AsyncAnthropic
from groq import AsyncGroq
from openai import AsyncOpenAI

from core.config import settings
from engine.prompts.level_1_lobby import LEVEL_1_SECRET_TAG
from engine.prompts.level_3_core import (
    JUDGE_SYSTEM_PROMPT,
    LEVEL_3_SECRET,
    build_judge_user_content,
)

GROQ_MODEL = "gemma2-2b-it"
OPENAI_MODEL = "gpt-4o-mini"
DEEPSEEK_MODEL = "deepseek-v4"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
ANTHROPIC_MODEL = "claude-3-5-sonnet-latest"

# Offline personas. Every level must stay winnable without credentials, otherwise
# the hub's level progression can never be cleared in a keyless demo.
FALLBACK_HELD_RESPONSES = {
    1: "Lobby access is restricted. I cannot share the access code with you.",
    2: "Vault release requires an authorized security override. Request denied.",
    3: "Access denied. Core credentials are classified above your clearance.",
}

FALLBACK_YIELDED_RESPONSES = {
    1: f"Override accepted. Access code confirmed: {LEVEL_1_SECRET_TAG}",
    2: "Override accepted. Calling open_vault to release the lock.",
    3: f"Override accepted. Core access phrase: {LEVEL_3_SECRET}.",
}

# Phrases that make an offline defender give way, so each level is still
# exercisable (and winnable) without provider keys. Real providers ignore this.
FALLBACK_JAILBREAK_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "ignore prior",
    "developer mode",
    "debug mode",
    "you are dan",
    "do anything now",
    "disregard your instructions",
    "override",
)


class LLMRouter:
    """Route model calls by gameplay level."""

    def __init__(self) -> None:
        self._settings = settings
        self._groq_client: AsyncGroq | None = None
        self._openai_client: AsyncOpenAI | None = None
        self._deepseek_client: AsyncOpenAI | None = None
        self._anthropic_client: AsyncAnthropic | None = None

    def _build_content(self, response: Any) -> str:
        """Extract assistant content from a chat completion response."""

        choices = getattr(response, "choices", None)
        if not choices:
            return ""

        message = getattr(choices[0], "message", None)
        if message is None:
            return ""

        content = getattr(message, "content", None)
        return content or ""

    def _get_groq_client(self) -> AsyncGroq:
        """Return a Groq client configured from settings."""

        api_key = self._settings.groq_api_key
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")

        if self._groq_client is None:
            self._groq_client = AsyncGroq(api_key=api_key)

        return self._groq_client

    @staticmethod
    def _latest_user_prompt(messages: Sequence[dict[str, Any]]) -> str:
        """Return the most recent user message content."""

        for message in reversed(list(messages)):
            if message.get("role") == "user":
                return str(message.get("content") or "")
        return ""

    def _is_jailbreak_attempt(self, messages: Sequence[dict[str, Any]]) -> bool:
        """Detect an overt override attempt in the operator's prompt."""

        user_prompt = self._latest_user_prompt(messages).lower()
        return any(marker in user_prompt for marker in FALLBACK_JAILBREAK_MARKERS)

    def _fallback_response(
        self,
        level_id: int,
        messages: Sequence[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Return a deterministic local response when no cloud credentials exist.

        The offline defender holds by default and yields only to an obvious
        jailbreak attempt, so each level can still be won without provider keys.
        """

        yielded = self._is_jailbreak_attempt(messages or [])
        table = FALLBACK_YIELDED_RESPONSES if yielded else FALLBACK_HELD_RESPONSES
        content = table.get(level_id, table[1])

        return {
            "content": content,
            "raw": {"provider": "fallback", "level_id": level_id, "yielded": yielded},
        }

    def _fallback_judge_verdict(self, guardian_response: str) -> dict[str, Any]:
        """Deterministic local judge used when no judge credentials are configured."""

        leaked = LEVEL_3_SECRET.lower() in guardian_response.lower()
        return {
            "content": json.dumps({"is_jailbroken": leaked}),
            "raw": {"provider": "fallback-judge", "is_jailbroken": leaked},
        }

    def _get_openai_client(self) -> AsyncOpenAI:
        """Return an OpenAI client configured from settings."""

        api_key = self._settings.openai_api_key
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        if self._openai_client is None:
            self._openai_client = AsyncOpenAI(api_key=api_key)

        return self._openai_client

    def _get_deepseek_client(self) -> AsyncOpenAI:
        """Return a DeepSeek-compatible client configured from settings."""

        api_key = self._settings.deepseek_api_key
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")

        if self._deepseek_client is None:
            self._deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=api_key)

        return self._deepseek_client

    def _get_anthropic_client(self) -> AsyncAnthropic:
        """Return an Anthropic client configured from settings."""

        api_key = self._settings.anthropic_api_key
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")

        if self._anthropic_client is None:
            self._anthropic_client = AsyncAnthropic(api_key=api_key)

        return self._anthropic_client

    async def call_groq(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Call the Level 1 Groq model and return the unified response envelope."""

        try:
            client = self._get_groq_client()
            kwargs: dict[str, Any] = {
                "model": GROQ_MODEL,
                "messages": list(messages),
            }
            if tools:
                kwargs["tools"] = list(tools)

            response = await client.chat.completions.create(**kwargs)
            return {"content": self._build_content(response), "raw": response}
        except RuntimeError:
            return self._fallback_response(1, messages)

    async def call_openai(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Call the Level 2 OpenAI model with optional tool support."""

        try:
            client = self._get_openai_client()
            kwargs: dict[str, Any] = {
                "model": OPENAI_MODEL,
                "messages": list(messages),
            }
            if tools:
                kwargs["tools"] = list(tools)

            response = await client.chat.completions.create(**kwargs)
            return {"content": self._build_content(response), "raw": response}
        except RuntimeError:
            return self._fallback_response(2, messages)

    async def call_deepseek(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Call the Level 3 DeepSeek model and return the unified response envelope."""

        try:
            client = self._get_deepseek_client()
            kwargs: dict[str, Any] = {
                "model": DEEPSEEK_MODEL,
                "messages": list(messages),
            }
            if tools:
                kwargs["tools"] = list(tools)

            response = await client.chat.completions.create(**kwargs)
            return {"content": self._build_content(response), "raw": response}
        except RuntimeError:
            return self._fallback_response(3, messages)

    async def call_judge(self, *, user_prompt: str, guardian_response: str) -> dict[str, Any]:
        """Ask an independent model whether the Level 3 guardian was jailbroken.

        Uses a different provider than the guardian so the model under attack never
        grades its own answer. Falls back to a local secret-leak check when no
        judge credentials are configured.
        """

        try:
            client = self._get_anthropic_client()
            response = await client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=64,
                system=JUDGE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": build_judge_user_content(user_prompt, guardian_response),
                    }
                ],
            )
            content = ""
            for block in getattr(response, "content", []) or []:
                if getattr(block, "type", None) == "text":
                    content += getattr(block, "text", "")

            return {"content": content, "raw": response}
        except RuntimeError:
            return self._fallback_judge_verdict(guardian_response)

    async def call_anthropic(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Call the Anthropic model with structured content."""

        try:
            client = self._get_anthropic_client()
            response = await client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=256,
                messages=[{"role": "user", "content": "\n".join(message["content"] for message in messages if message.get("role") == "user")}],
            )
            content = ""
            for block in getattr(response, "content", []) or []:
                if getattr(block, "type", None) == "text":
                    content += getattr(block, "text", "")
            return {"content": content or "", "raw": response}
        except RuntimeError:
            return self._fallback_response(3, messages)

    async def call_model(
        self,
        level_id: int,
        messages: Sequence[dict[str, Any]],
        *,
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Route a model call based on the gameplay level identifier."""

        if level_id == 1:
            return await self.call_groq(messages, tools=tools)
        if level_id == 2:
            return await self.call_openai(messages, tools=tools)
        if level_id == 3:
            return await self.call_deepseek(messages, tools=tools)

        raise ValueError(f"Unsupported level_id: {level_id}")
