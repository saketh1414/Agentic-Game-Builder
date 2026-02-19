"""
LLM configuration — plug your Gemini API key here or via environment variable.
"""
import os
from crewai import LLM


def get_llm() -> LLM:
    """
    Returns a configured Gemini LLM for use with CrewAI agents.

    Set your API key via environment variable:
        export GEMINI_API_KEY="your-key-here"

    Or replace the string below directly (not recommended for production).
    """
    api_key = os.environ.get("GEMINI_API_KEY", "Enter your API KEY here")

    return LLM(
        model="gemini/gemini-2.5-pro",  # Most powerful model — swap to gemini-2.0-flash for faster response
        # model="gemini/gemini-2.0-flash",   # Fast, capable model — swap to gemini-1.5-pro for more power
        api_key=api_key,
        temperature=0.3,                    # Lower temp = more deterministic code generation
        max_tokens=8192,
    )
