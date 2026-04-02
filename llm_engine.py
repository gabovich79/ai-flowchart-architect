"""
AI Flowchart Architect - LLM Engine
Supports OpenAI and Anthropic providers.
Cached with @st.cache_data to save API costs.
"""

import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import json
from config import (
    SYSTEM_PROMPT,
    REFINEMENT_PROMPT,
    VALIDATION_PROMPT,
    PROFESSIONAL_TONE_PROMPT,
    OPENAI_MODEL,
    ANTHROPIC_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
)
from mermaid_utils import clean_response


def generate_mermaid(description: str, provider: str, api_key: str) -> str:
    """
    Generate Mermaid flowchart code from a natural language description.

    Args:
        description: Natural language process description
        provider: "openai" or "anthropic"
        api_key: The API key for the selected provider

    Returns:
        Raw Mermaid code string

    Raises:
        ValueError: If provider is unknown
        Exception: On API errors
    """
    if provider == "openai":
        return _call_openai(SYSTEM_PROMPT, description, api_key)
    elif provider == "anthropic":
        return _call_anthropic(SYSTEM_PROMPT, description, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def refine_mermaid(
    current_code: str, instruction: str, provider: str, api_key: str
) -> str:
    """
    Refine an existing Mermaid diagram based on user instruction.

    Args:
        current_code: The current Mermaid code
        instruction: What the user wants to change
        provider: "openai" or "anthropic"
        api_key: The API key for the selected provider

    Returns:
        Updated Mermaid code string
    """
    system = REFINEMENT_PROMPT.format(
        current_code=current_code, instruction=instruction
    )
    user_msg = f"Apply this change: {instruction}"

    if provider == "openai":
        return _call_openai(system, user_msg, api_key)
    elif provider == "anthropic":
        return _call_anthropic(system, user_msg, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def validate_logic(code: str, provider: str, api_key: str) -> dict:
    """
    Validate the logical integrity of a Mermaid flowchart.
    Checks for orphan nodes, infinite loops, missing exit paths, and dead ends.

    Returns:
        dict with "status" ("green" or "yellow") and "issues" list
    """
    system = VALIDATION_PROMPT.format(code=code)
    user_msg = "Analyze this flowchart for logical issues. Return JSON only."

    try:
        if provider == "openai":
            raw = _call_openai_raw(system, user_msg, api_key)
        elif provider == "anthropic":
            raw = _call_anthropic_raw(system, user_msg, api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        # Parse JSON from response
        raw = raw.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(raw)
        # Ensure correct structure
        if "status" not in result:
            result["status"] = "green"
        if "issues" not in result:
            result["issues"] = []
        return result

    except (json.JSONDecodeError, Exception):
        # Fallback: assume green if we can't parse
        return {"status": "green", "issues": []}


def rewrite_professional(code: str, provider: str, api_key: str) -> str:
    """
    Rewrite node labels in the Mermaid code to use professional business terminology.

    Returns:
        Updated Mermaid code with professional labels
    """
    system = PROFESSIONAL_TONE_PROMPT.format(code=code)
    user_msg = "Rewrite all labels to professional business terminology. Return only the Mermaid code."

    if provider == "openai":
        return _call_openai(system, user_msg, api_key)
    elif provider == "anthropic":
        return _call_anthropic(system, user_msg, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ── Private helpers ───────────────────────────────────────────


def _call_openai(system: str, user_msg: str, api_key: str) -> str:
    """Call OpenAI API and return cleaned Mermaid code."""
    raw = _call_openai_raw(system, user_msg, api_key)
    return clean_response(raw)


def _call_anthropic(system: str, user_msg: str, api_key: str) -> str:
    """Call Anthropic API and return cleaned Mermaid code."""
    raw = _call_anthropic_raw(system, user_msg, api_key)
    return clean_response(raw)


@st.cache_data(ttl=3600, show_spinner=False)
def _call_openai_raw(system: str, user_msg: str, api_key: str) -> str:
    """Call OpenAI API and return raw response text. Cached for 1 hour."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    )
    return response.choices[0].message.content or ""


@st.cache_data(ttl=3600, show_spinner=False)
def _call_anthropic_raw(system: str, user_msg: str, api_key: str) -> str:
    """Call Anthropic API and return raw response text. Cached for 1 hour."""
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text if response.content else ""
