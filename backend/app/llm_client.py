"""
Async OpenAI client wrapper for VerifyAssist.
"""

import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger("verifyassist")

# Lazy-initialised client (created on first call)
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Return (and cache) an AsyncOpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. "
                "Create a .env file or export the variable."
            )
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Send a chat-completion request to OpenAI and return the raw
    assistant reply as a string.

    Raises:
        RuntimeError  – if the API key is missing.
        openai.OpenAIError – on transient API failures (caller handles).
    """
    client = _get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    logger.info("Calling OpenAI model=%s  prompt_len=%d", model, len(user_prompt))

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=600,
    )

    content = response.choices[0].message.content or ""
    logger.info("LLM response length=%d tokens_used=%s", len(content), response.usage)
    return content
