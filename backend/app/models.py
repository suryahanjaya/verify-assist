"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from enum import Enum


class Classification(str, Enum):
    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    TOLERABLE = "TOLERABLE"


class VerifyRequest(BaseModel):
    """Incoming verification request from the IDE plugin or API consumer."""

    warning_message: str = Field(
        ...,
        min_length=1,
        description="The static analysis warning message to verify.",
        examples=["Potential null pointer dereference at line 42"],
    )
    category: str = Field(
        ...,
        min_length=1,
        description="Warning category from the static analyzer.",
        examples=["NULL_POINTER_DEREFERENCE"],
    )
    code_snippet: str = Field(
        ...,
        min_length=1,
        description="The code snippet that triggered the warning.",
        examples=[
            'public void process(User user) {\n    user.getName();\n}'
        ],
    )
    optional_context: str = Field(
        default="",
        description="Any additional context (imports, caller info, data flow, etc.).",
        examples=["user parameter may be null when called from handleRequest()"],
    )


class VerifyResponse(BaseModel):
    """Structured verification result returned to the consumer."""

    classification: Classification = Field(
        ...,
        description="Verdict: TRUE_POSITIVE, FALSE_POSITIVE, or TOLERABLE.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence in the classification (0.0–1.0).",
    )
    explanation: str = Field(
        ...,
        description="Human-readable reasoning for the classification.",
    )
    evidence: str = Field(
        ...,
        description="Specific code lines, variables, or logic supporting the verdict.",
    )
    cached: bool = Field(
        default=False,
        description="Whether the result was served from the in-memory cache.",
    )
