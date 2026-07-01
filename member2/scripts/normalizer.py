"""Normalization helpers for candidate profile fields."""

from __future__ import annotations

import re
from typing import Any

_SPACE_RE = re.compile(r"\s+")

_COMMON_VARIANTS: dict[str, str] = {
    "c plus plus": "c++",
    "c plus+ plus": "c++",
    "c#": "c#",
    "c sharp": "c#",
    "node js": "node.js",
    "react js": "react.js",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "my sql": "mysql",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    "machine learning": "machine learning",
    "artificial intelligence": "artificial intelligence",
    "b tech": "b.tech",
    "b e": "b.e.",
    "m tech": "m.tech",
    "m e": "m.e.",
    "ph d": "ph.d.",
}

_TITLE_VARIANTS: dict[str, str] = {
    "software developer": "software engineer",
    "swe": "software engineer",
    "sr software engineer": "senior software engineer",
    "sde": "software development engineer",
}

_DEGREE_VARIANTS: dict[str, str] = {
    "bachelor of technology": "b.tech",
    "bachelor of engineering": "b.e.",
    "master of technology": "m.tech",
    "master of engineering": "m.e.",
    "doctor of philosophy": "ph.d.",
    "bachelor of science": "b.sc.",
    "master of science": "m.sc.",
}

_LOCATION_VARIANTS: dict[str, str] = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "poona": "pune",
}


def _normalize_text(value: Any) -> str:
    """Normalize text to lowercase, trimmed, and single-spaced form."""
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = _SPACE_RE.sub(" ", text)
    return text


def _apply_variants(text: str, variants: dict[str, str]) -> str:
    """Apply whole-string or embedded common variant substitutions."""
    if not text:
        return text
    if text in variants:
        return variants[text]
    for source, target in variants.items():
        if source in text:
            text = text.replace(source, target)
    return text


def normalize_skill(value: Any) -> str:
    """Normalize a skill name while preserving meaningful acronyms."""
    text = _normalize_text(value)
    text = _apply_variants(text, _COMMON_VARIANTS)
    return text


def normalize_company(value: Any) -> str:
    """Normalize a company name."""
    text = _normalize_text(value)
    text = text.replace("&", "and")
    text = _apply_variants(text, _COMMON_VARIANTS)
    return text


def normalize_title(value: Any) -> str:
    """Normalize a job title."""
    text = _normalize_text(value)
    text = _apply_variants(text, _TITLE_VARIANTS)
    return text


def normalize_location(value: Any) -> str:
    """Normalize a location string."""
    text = _normalize_text(value)
    text = _apply_variants(text, _LOCATION_VARIANTS)
    return text


def normalize_degree(value: Any) -> str:
    """Normalize a degree name."""
    text = _normalize_text(value)
    text = _apply_variants(text, _DEGREE_VARIANTS)
    text = _apply_variants(text, _COMMON_VARIANTS)
    return text
