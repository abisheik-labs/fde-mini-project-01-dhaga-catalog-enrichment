"""
Configuration settings, pricing constants, temperatures, and taxonomy for Dhaga & Co.
Cataloging Pipeline Accelerator.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_setting(name: str, default: str = "") -> str:
    """Read the value from env, then Streamlit secrets when running in deployment."""
    value = os.getenv(name)
    if value is not None and value.strip():
        return value.strip()

    try:
        import streamlit as st
        secret_value = st.secrets.get(name)
        if secret_value is not None:
            return str(secret_value).strip()
    except Exception:
        pass

    legacy_aliases = {
        "GROQ_API_KEY": ["OPENROUTER_API_KEY", "OPENAI_API_KEY"],
    }
    for alias in legacy_aliases.get(name, []):
        value = os.getenv(alias)
        if value is not None and value.strip():
            return value.strip()
        try:
            import streamlit as st
            secret_value = st.secrets.get(alias)
            if secret_value is not None:
                return str(secret_value).strip()
        except Exception:
            pass

    return default


# Groq API Configuration
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = _get_setting("GROQ_API_KEY", "")

# Two Models Minimum Configuration (Groq)
CHEAP_MODEL = _get_setting("CHEAP_MODEL", "openai/gpt-oss-20b")
STRONG_MODEL = _get_setting("STRONG_MODEL", "openai/gpt-oss-120b")

# Alternative model choices
FALLBACK_CHEAP_MODEL = "openai/gpt-oss-20b"
FALLBACK_STRONG_MODEL = "openai/gpt-oss-120b"

# Stated Temperatures (Per Brief Ground Rules)
TEMP_EXTRACTION = 0.0      # Deterministic extraction & category routing (no creative drift)
TEMP_EVALUATION = 0.1      # Strict brand safety & schema guardrail adherence
TEMP_COPY = 0.7            # Creative, natural Hinglish product copy & occasion tags

# Dhaga & Co. Business & Pricing Constants
MIN_CATALOG_PRICE = 399
MAX_CATALOG_PRICE = 1499
AVERAGE_ORDER_VALUE = 840
WEEKLY_NEW_SKUS = 400
MONTHLY_NEW_SKUS = 1600
HOURS_PER_MANUAL_SKU = 0.25 # ~15 minutes per SKU manually
EST_MANUAL_HOURLY_COST_INR = 250.0 # ~₹250/hr listing agent payroll

# OpenRouter Pricing per 1M tokens (USD)
# Approximate Gemini 2.5 Flash / Pro pricing on OpenRouter
CHEAP_MODEL_INPUT_PRICE_PER_M = 0.075   # $0.075 per 1M input tokens
CHEAP_MODEL_OUTPUT_PRICE_PER_M = 0.300  # $0.30 per 1M output tokens

STRONG_MODEL_INPUT_PRICE_PER_M = 1.250  # $1.25 per 1M input tokens
STRONG_MODEL_OUTPUT_PRICE_PER_M = 5.000 # $5.00 per 1M output tokens

USD_TO_INR = 86.5  # Standard currency conversion

# Standard Canonical 16-Color Taxonomy
# Solves the client problem: "Colour has been typed about ninety different ways"
CANONICAL_COLOR_MAP: Dict[str, List[str]] = {
    "NAVY_BLUE": [
        "navy blue", "navy", "dark navy", "midnight navy", "deep royal navy blue",
        "ink blue", "marine blue", "dark blue", "faded navy", "indigo navy"
    ],
    "ROYAL_BLUE": [
        "royal blue", "bright royal blue", "electric blue", "cobalt blue", "raja blue",
        "deep blue", "vibrant blue"
    ],
    "SKY_BLUE": [
        "sky blue", "light blue", "aasmaani", "light faded aasmaani", "powder blue",
        "baby blue", "ice blue", "pastel blue"
    ],
    "RANI_PINK": [
        "rani pink", "rani", "gulabi", "dusty gulabi", "dark gulabi", "hot pink",
        "magenta", "fuchsia", "rani pinkish red", "rani pinkish magenta", "deep pink"
    ],
    "BABY_PINK": [
        "baby pink", "light pink", "blush pink", "pastel pink", "soft pink",
        "rose pink", "powder pink", "peach pink"
    ],
    "MAROON": [
        "maroon", "deep maroon", "wine maroon", "dark red", "blood red",
        "tamatar red", "crimson", "burgundy", "cherry red", "laal"
    ],
    "MUSTARD_YELLOW": [
        "mustard yellow", "mustard", "haldi yellow", "haldi", "deep yellow",
        "dark yellow", "ochre", "sarson yellow"
    ],
    "LEMON_YELLOW": [
        "lemon yellow", "light yellow", "peela", "bright yellow", "pastel yellow",
        "sunshine yellow", "pale yellow"
    ],
    "EMERALD_GREEN": [
        "emerald green", "bottle green", "dark green", "forest green", "mehendi green",
        "mehndi green", "deep green", "peacock green"
    ],
    "MINT_GREEN": [
        "mint green", "pista green", "pista", "light green", "sea green",
        "pastel green", "sage green"
    ],
    "OFF_WHITE": [
        "off-white", "off white", "cream", "creamish", "creamish badami", "badami",
        "ivory", "eggshell white", "milk white", "safed"
    ],
    "PURE_BLACK": [
        "black", "pure black", "jet black", "kaala", "midnight black", "charcoal black"
    ],
    "RUST_ORANGE": [
        "rust orange", "rust", "orange", "bhagwa", "narangi", "tangerine",
        "brick red", "terracotta"
    ],
    "CORAL_PEACH": [
        "peach", "coral", "coral peach", "light orange", "apricot", "salmon"
    ],
    "WINE_PURPLE": [
        "wine", "purple", "baingani", "jamuni", "violet", "lavender", "dark purple",
        "plum"
    ],
    "METALLIC_GOLD": [
        "gold", "golden", "metallic gold", "antique gold", "sona", "zari gold",
        "copper gold"
    ]
}
