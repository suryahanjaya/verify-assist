"""
Parses the raw LLM text response into a structured VerifyResponse.
"""

import re
import logging
from app.models import VerifyResponse, Classification

logger = logging.getLogger("verifyassist")

# Patterns to extract each field from the LLM output
_CLASSIFICATION_RE = re.compile(
    r"CLASSIFICATION:\s*(TRUE_POSITIVE|FALSE_POSITIVE|TOLERABLE)",
    re.IGNORECASE,
)
_CONFIDENCE_RE = re.compile(
    r"CONFIDENCE:\s*([\d.]+)",
    re.IGNORECASE,
)
_EXPLANATION_RE = re.compile(
    r"EXPLANATION:\s*(.+?)(?=\nEVIDENCE:|\Z)",
    re.IGNORECASE | re.DOTALL,
)
_EVIDENCE_RE = re.compile(
    r"EVIDENCE:\s*(.+)",
    re.IGNORECASE | re.DOTALL,
)

# Fallback response when parsing fails completely
FALLBACK_RESPONSE = VerifyResponse(
    classification=Classification.TOLERABLE,
    confidence=0.3,
    explanation="Failed to parse model response. Manual review recommended.",
    evidence="N/A",
    cached=False,
)


def parse_llm_response(raw_text: str) -> VerifyResponse:
    """
    Extract CLASSIFICATION, CONFIDENCE, EXPLANATION, and EVIDENCE
    from the raw LLM output string.

    Falls back to a safe default if any required field cannot be parsed.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("Received empty LLM response — returning fallback.")
        return FALLBACK_RESPONSE

    # --- Classification ---
    cls_match = _CLASSIFICATION_RE.search(raw_text)
    if not cls_match:
        logger.warning("Could not parse CLASSIFICATION from LLM response.")
        return FALLBACK_RESPONSE
    classification = Classification(cls_match.group(1).upper())

    # --- Confidence ---
    conf_match = _CONFIDENCE_RE.search(raw_text)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
            confidence = max(0.0, min(1.0, confidence))  # clamp
        except ValueError:
            confidence = 0.5
    else:
        logger.warning("Could not parse CONFIDENCE — defaulting to 0.5.")
        confidence = 0.5

    # --- Explanation ---
    expl_match = _EXPLANATION_RE.search(raw_text)
    explanation = expl_match.group(1).strip() if expl_match else "No explanation provided."

    # --- Evidence ---
    evid_match = _EVIDENCE_RE.search(raw_text)
    evidence = evid_match.group(1).strip() if evid_match else "No evidence provided."

    return VerifyResponse(
        classification=classification,
        confidence=confidence,
        explanation=explanation,
        evidence=evidence,
        cached=False,
    )
