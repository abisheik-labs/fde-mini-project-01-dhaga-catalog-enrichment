"""
Deterministic Color Normalizer for Dhaga & Co.
Maps 90+ messy color spellings to 16 canonical color buckets.
This is implemented as DETERMINISTIC CODE per the Code vs Model line rule:
exact matching, dictionary lookup, and normalized aliases do not waste LLM tokens.
"""

import re
from typing import Tuple
from config import CANONICAL_COLOR_MAP
from core.schemas import ColorNormalizationResult


def clean_text(text: str) -> str:
    """Lowercases, removes special characters, and trims whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', ' ', text)
    return " ".join(text.split())


def normalize_color(raw_color: str) -> ColorNormalizationResult:
    """
    Standardizes a raw messy color string into one of Dhaga's 16 canonical colors.
    
    Resolution Strategy (Deterministic Line):
    1. Direct Canonical Key Match (e.g. 'NAVY_BLUE' -> 'NAVY_BLUE')
    2. Normalized Exact Alias Match (e.g. 'dusty gulabi' -> 'RANI_PINK')
    3. Keyword Substring Match (e.g. 'deep royal navy blue' matches 'royal navy' -> 'NAVY_BLUE')
    4. Unmapped Fallback -> 'UNMAPPED_AMBIGUOUS' (Triggers Human Review)
    """
    cleaned = clean_text(raw_color)
    
    if not cleaned:
        return ColorNormalizationResult(
            original_color=raw_color,
            canonical_color="UNMAPPED_AMBIGUOUS",
            confidence=0.0,
            is_canonical=False
        )

    # 1. Direct key match
    upper_key = cleaned.replace(" ", "_").upper()
    if upper_key in CANONICAL_COLOR_MAP:
        return ColorNormalizationResult(
            original_color=raw_color,
            canonical_color=upper_key,
            confidence=1.0,
            is_canonical=True
        )

    # 2. Exact alias match
    for canonical_name, aliases in CANONICAL_COLOR_MAP.items():
        for alias in aliases:
            if cleaned == alias.lower():
                return ColorNormalizationResult(
                    original_color=raw_color,
                    canonical_color=canonical_name,
                    confidence=1.0,
                    is_canonical=True
                )

    # 3. Substring / multi-word keyword match (ordered by alias length descending)
    all_aliases = []
    for canonical_name, aliases in CANONICAL_COLOR_MAP.items():
        for alias in aliases:
            all_aliases.append((len(alias), alias.lower(), canonical_name))
    all_aliases.sort(key=lambda x: x[0], reverse=True)

    for _, alias, canonical_name in all_aliases:
        # Check if alias is a whole phrase in cleaned text
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, cleaned):
            return ColorNormalizationResult(
                original_color=raw_color,
                canonical_color=canonical_name,
                confidence=0.90,
                is_canonical=True
            )

    # 4. Fallback if no match
    return ColorNormalizationResult(
        original_color=raw_color,
        canonical_color="UNMAPPED_AMBIGUOUS",
        confidence=0.0,
        is_canonical=False
    )
