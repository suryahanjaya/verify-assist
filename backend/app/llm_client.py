"""
Groq LLM client for VerifyAssist.

Sends prompts to the Groq API (llama-3.3-70b-versatile)
and returns parsed verification results.
"""

import os
import logging
import requests

from app.response_parser import parse_llm_response, FALLBACK_RESPONSE
from app.models import VerifyResponse

logger = logging.getLogger("verifyassist")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
TIMEOUT = 15  # seconds


def _get_api_key() -> str:
    """Read GROQ_API_KEY from environment or raise."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file or export the variable."
        )
    return key


def query_llm(prompt: str) -> VerifyResponse:
    """
    Send a prompt to the Groq API and return a parsed VerifyResponse.

    1. POST to Groq chat completions endpoint
    2. Extract the assistant message content
    3. Parse with response_parser
    4. Return VerifyResponse (or fallback on any failure)
    """
    # --- Validate API key ---------------------------------------------------
    try:
        api_key = _get_api_key()
    except RuntimeError:
        raise  # let main.py handle config errors

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }

    # --- Call Groq API ------------------------------------------------------
    try:
        logger.info("Calling Groq model=%s  prompt_len=%d", GROQ_MODEL, len(prompt))
        response = requests.post(GROQ_URL, headers=headers, json=body, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Groq API timed out after %ds", TIMEOUT)
        return FALLBACK_RESPONSE
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Groq API at %s", GROQ_URL)
        return FALLBACK_RESPONSE
    except requests.exceptions.HTTPError as exc:
        logger.error("Groq API HTTP error: %s — %s", exc, response.text)
        return FALLBACK_RESPONSE
    except requests.exceptions.RequestException as exc:
        logger.error("Groq API request failed: %s", exc)
        return FALLBACK_RESPONSE

    # --- Extract content ----------------------------------------------------
    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        logger.info("Groq response length=%d", len(content))
    except (ValueError, KeyError, IndexError) as exc:
        logger.error("Failed to extract content from Groq response: %s", exc)
        return FALLBACK_RESPONSE

    # --- Parse with response_parser -----------------------------------------
    try:
        result = parse_llm_response(content)
        return result
    except Exception as exc:
        logger.error("Response parsing failed: %s", exc)
        return FALLBACK_RESPONSE
