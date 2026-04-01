"""
Simple in-memory cache to avoid repeated LLM calls for identical inputs.

Uses a dict keyed by a SHA-256 hash of the request fields.
No TTL — cache lives for the lifetime of the process.
"""

import hashlib
import json
import logging
from typing import Optional

from app.models import VerifyRequest, VerifyResponse

logger = logging.getLogger("verifyassist")

_cache: dict[str, VerifyResponse] = {}


def _make_key(request: VerifyRequest) -> str:
    """Deterministic cache key from request content."""
    payload = json.dumps(
        {
            "warning_message": request.warning_message,
            "category": request.category,
            "code_snippet": request.code_snippet,
            "optional_context": request.optional_context,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def get(request: VerifyRequest) -> Optional[VerifyResponse]:
    """Return cached response or None."""
    key = _make_key(request)
    hit = _cache.get(key)
    if hit:
        logger.info("Cache HIT  key=%s…", key[:12])
    return hit


def put(request: VerifyRequest, response: VerifyResponse) -> None:
    """Store a response in the cache."""
    key = _make_key(request)
    _cache[key] = response
    logger.info("Cache STORE key=%s…  total_entries=%d", key[:12], len(_cache))


def size() -> int:
    """Current number of cached entries."""
    return len(_cache)


def clear() -> None:
    """Flush the entire cache."""
    _cache.clear()
    logger.info("Cache CLEARED")
