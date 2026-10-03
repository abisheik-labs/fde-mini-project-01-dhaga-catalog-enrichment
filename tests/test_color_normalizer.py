"""Unit tests for deterministic color normalization."""

import pytest
from core.color_normalizer import normalize_color


def test_exact_alias_match():
    res = normalize_color("dusty gulabi")
    assert res.is_canonical is True
    assert res.canonical_color == "RANI_PINK"
    assert res.confidence == 1.0


def test_keyword_match():
    res = normalize_color("royal midnight navy blue")
    assert res.is_canonical is True
    assert res.canonical_color == "NAVY_BLUE"
    assert res.confidence >= 0.9


def test_hinglish_vernacular_names():
    res_safed = normalize_color("safed")
    assert res_safed.canonical_color == "OFF_WHITE"

    res_tamatar = normalize_color("tamatar red")
    assert res_tamatar.canonical_color == "MAROON"

    res_haldi = normalize_color("haldi yellow")
    assert res_haldi.canonical_color == "MUSTARD_YELLOW"


def test_unmapped_ambiguous_fails_visibly():
    res = normalize_color("weird mixture blend")
    assert res.is_canonical is False
    assert res.canonical_color == "UNMAPPED_AMBIGUOUS"
    assert res.confidence == 0.0
