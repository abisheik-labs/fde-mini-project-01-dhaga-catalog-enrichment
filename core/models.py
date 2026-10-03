"""LangChain model clients for the Dhaga & Co. Groq-backed pipeline."""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from config import (
    GROQ_BASE_URL,
    GROQ_API_KEY,
    CHEAP_MODEL,
    STRONG_MODEL,
    TEMP_EXTRACTION,
    TEMP_EVALUATION,
    TEMP_COPY
)


def get_llm(
    model_name: str,
    temperature: float,
    api_key: Optional[str] = None
) -> Optional[ChatOpenAI]:
    """
    Returns a Groq-backed LangChain ChatOpenAI instance.
    """
    key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
    if not key or key.strip() == "" or key.strip().startswith("your_"):
        return None

    return ChatOpenAI(
        model=model_name,
        openai_api_base=GROQ_BASE_URL,
        openai_api_key=key.strip(),
        temperature=temperature,
        max_tokens=2048,
        request_timeout=30,
        max_retries=2
    )


def get_cheap_extraction_llm(api_key: Optional[str] = None):
    """Cheap/Fast model at Temperature 0.0 for category routing & attribute extraction."""
    return get_llm(CHEAP_MODEL, TEMP_EXTRACTION, api_key)


def get_strong_copy_llm(api_key: Optional[str] = None):
    """Strong/Creative model at Temperature 0.7 for Hinglish copy & occasion tags."""
    return get_llm(STRONG_MODEL, TEMP_COPY, api_key)


def get_strong_evaluator_llm(api_key: Optional[str] = None):
    """Strong/Judgment model at Temperature 0.1 for evaluator-optimizer guardrail."""
    return get_llm(STRONG_MODEL, TEMP_EVALUATION, api_key)
