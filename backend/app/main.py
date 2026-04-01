"""
VerifyAssist — FastAPI backend for LLM-powered static analysis verification.

Run:
    uvicorn app.main:app --reload
"""

import logging
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import VerifyRequest, VerifyResponse, Classification
from app.prompt_builder import build_prompt
from app.response_parser import parse_llm_response, FALLBACK_RESPONSE
from app.llm_client import call_llm
from app import cache

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()  # reads .env in cwd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("verifyassist")


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("VerifyAssist starting up …")
    yield
    logger.info("VerifyAssist shutting down — cache had %d entries.", cache.size())


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="VerifyAssist",
    version="0.1.0",
    description=(
        "Real-time LLM-powered verification of static analysis warnings. "
        "Send a warning + code snippet and receive a structured classification."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["health"])
async def root():
    """Health-check endpoint."""
    return {
        "service": "VerifyAssist",
        "version": "0.1.0",
        "status": "running",
        "cache_entries": cache.size(),
    }


@app.post(
    "/verify",
    response_model=VerifyResponse,
    tags=["verification"],
    summary="Verify a static analysis warning",
    description=(
        "Accepts a static analysis warning with code context, sends it to an LLM, "
        "and returns a structured classification (TRUE_POSITIVE / FALSE_POSITIVE / TOLERABLE) "
        "with confidence, explanation, and evidence."
    ),
)
async def verify_warning(request: VerifyRequest) -> VerifyResponse:
    """Core verification endpoint."""

    # 1. Check cache --------------------------------------------------------
    cached_result = cache.get(request)
    if cached_result is not None:
        cached_result.cached = True
        return cached_result

    # 2. Build prompt -------------------------------------------------------
    system_prompt, user_prompt = build_prompt(request)
    logger.info(
        "Verifying warning: category=%s  snippet_len=%d",
        request.category,
        len(request.code_snippet),
    )

    # 3. Call LLM -----------------------------------------------------------
    start = time.perf_counter()
    try:
        raw_response = await call_llm(system_prompt, user_prompt)
    except RuntimeError as exc:
        # Missing API key or config error
        logger.error("Configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        # Transient OpenAI errors
        logger.error("LLM call failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"LLM service error: {exc}",
        )
    elapsed = time.perf_counter() - start
    logger.info("LLM responded in %.2f s", elapsed)

    # 4. Parse response -----------------------------------------------------
    try:
        result = parse_llm_response(raw_response)
    except Exception as exc:
        logger.error("Response parsing failed: %s", exc)
        result = FALLBACK_RESPONSE

    # 5. Cache & return -----------------------------------------------------
    cache.put(request, result)
    return result


@app.delete("/cache", tags=["admin"], summary="Clear the in-memory cache")
async def clear_cache():
    """Flush all cached verification results."""
    count = cache.size()
    cache.clear()
    return {"cleared": count}
