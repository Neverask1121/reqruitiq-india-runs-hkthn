"""Candidate record parsing utilities."""

from __future__ import annotations

from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    """Return *value* if it is a dict, otherwise an empty dict."""
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    """Return *value* if it is a list, otherwise an empty list."""
    return value if isinstance(value, list) else []


def parse_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Extract the candidate fields required by the processing pipeline.

    The function is intentionally defensive: missing or malformed sections are
    replaced with empty containers so downstream normalization can proceed.
    """

    candidate = _as_dict(candidate)

    parsed: dict[str, Any] = {
        "candidate_id": candidate.get("candidate_id", ""),
        "profile": _as_dict(candidate.get("profile")),
        "career_history": _as_list(candidate.get("career_history")),
        "education": _as_list(candidate.get("education")),
        "skills": _as_list(candidate.get("skills")),
        "certifications": _as_list(candidate.get("certifications")),
        "languages": _as_list(candidate.get("languages")),
        "redrob_signals": _as_dict(candidate.get("redrob_signals")),
    }

    return parsed
