"""
Builds the structured prompt sent to the LLM for warning verification.
"""

from app.models import VerifyRequest

SYSTEM_PROMPT = """\
You are a senior software engineer specializing in static analysis, debugging, and code quality.

Your task is to verify whether a static analysis warning is valid.

Analyze the warning using the provided code and context.

Classify the warning into ONE of these categories:
- TRUE_POSITIVE: The warning indicates a real bug that should be fixed
- FALSE_POSITIVE: The warning is incorrect or not applicable
- TOLERABLE: The issue exists but is minor or acceptable in context

RULES:
- Do NOT guess. Base your answer only on the code and context.
- Be precise and technical.
- If information is missing, reduce confidence.
- Avoid generic explanations.
- Always refer to specific parts of the code.\
"""

USER_PROMPT_TEMPLATE = """\
Warning Message:
{warning_message}

Warning Category:
{category}

Code Snippet:
```
{code_snippet}
```

Additional Context:
{optional_context}

---

Respond in this STRICT format (no markdown, no extra text):

CLASSIFICATION: <TRUE_POSITIVE or FALSE_POSITIVE or TOLERABLE>
CONFIDENCE: <number between 0.0 and 1.0>
EXPLANATION: <clear reasoning in 2-3 sentences>
EVIDENCE: <specific code lines, variables, or logic that support your decision>\
"""


def build_prompt(request: VerifyRequest) -> tuple[str, str]:
    """
    Build the (system_message, user_message) pair for the LLM call.

    Returns:
        Tuple of (system_prompt, user_prompt) strings.
    """
    context = request.optional_context if request.optional_context else "None provided."

    user_prompt = USER_PROMPT_TEMPLATE.format(
        warning_message=request.warning_message,
        category=request.category,
        code_snippet=request.code_snippet,
        optional_context=context,
    )

    return SYSTEM_PROMPT, user_prompt
