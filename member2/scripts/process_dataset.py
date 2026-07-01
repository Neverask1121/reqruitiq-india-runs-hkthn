"""Process the candidate dataset into a normalized JSON artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

try:
    from .normalizer import (
        normalize_company,
        normalize_degree,
        normalize_location,
        normalize_skill,
        normalize_title,
    )
    from .parser import parse_candidate
except ImportError:  # pragma: no cover - direct script execution fallback
    from normalizer import (  # type: ignore
        normalize_company,
        normalize_degree,
        normalize_location,
        normalize_skill,
        normalize_title,
    )
    from parser import parse_candidate  # type: ignore


SCRIPT_DIR = Path(__file__).resolve().parent
MEMBER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = MEMBER_DIR.parent
INPUT_PATH = PROJECT_ROOT / "dataset" / "candidates.jsonl"
OUTPUT_PATH = MEMBER_DIR / "outputs" / "parsed_candidates.json"


def _safe_string(value: Any) -> str:
    """Return a string value or an empty string."""
    if value is None:
        return ""
    return str(value)


def _normalize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Normalize the candidate profile section."""
    normalized = dict(profile)
    if "location" in normalized:
        normalized["location"] = normalize_location(normalized.get("location"))
    if "current_company" in normalized:
        normalized["current_company"] = normalize_company(
            normalized.get("current_company")
        )
    if "current_title" in normalized:
        normalized["current_title"] = normalize_title(normalized.get("current_title"))
    return normalized


def _normalize_career_history(career_history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize career history entries."""
    normalized_history: list[dict[str, Any]] = []
    for item in career_history:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        entry["company"] = normalize_company(entry.get("company"))
        entry["title"] = normalize_title(entry.get("title"))
        normalized_history.append(entry)
    return normalized_history


def _normalize_education(education: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize education entries."""
    normalized_education: list[dict[str, Any]] = []
    for item in education:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        entry["institution"] = _safe_string(entry.get("institution")).strip()
        entry["degree"] = normalize_degree(entry.get("degree"))
        entry["field_of_study"] = _safe_string(entry.get("field_of_study")).strip().lower()
        normalized_education.append(entry)
    return normalized_education


def _normalize_skills(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize skill names."""
    normalized_skills: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for item in skills:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        entry["name"] = normalize_skill(entry.get("name"))
        key = (
            entry.get("name"),
            entry.get("proficiency"),
            entry.get("endorsements"),
            entry.get("duration_months"),
        )
        if key in seen:
            continue
        seen.add(key)
        normalized_skills.append(entry)
    return normalized_skills


def _normalize_languages(languages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize language entries."""
    normalized_languages: list[dict[str, Any]] = []
    for item in languages:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        entry["language"] = _safe_string(entry.get("language")).strip().lower()
        entry["proficiency"] = _safe_string(entry.get("proficiency")).strip().lower()
        normalized_languages.append(entry)
    return normalized_languages


def _normalize_redrob_signals(redrob_signals: dict[str, Any]) -> dict[str, Any]:
    """Normalize platform signals with light-touch cleanup."""
    if not isinstance(redrob_signals, dict):
        return {}
    normalized = dict(redrob_signals)
    preferred_mode = normalized.get("preferred_work_mode")
    if preferred_mode is not None:
        normalized["preferred_work_mode"] = str(preferred_mode).strip().lower()
    return normalized


def normalize_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Parse and normalize a single candidate record."""
    parsed = parse_candidate(candidate)
    parsed["candidate_id"] = _safe_string(parsed.get("candidate_id")).strip()
    parsed["profile"] = _normalize_profile(parsed.get("profile", {}))
    parsed["career_history"] = _normalize_career_history(parsed.get("career_history", []))
    parsed["education"] = _normalize_education(parsed.get("education", []))
    parsed["skills"] = _normalize_skills(parsed.get("skills", []))
    parsed["certifications"] = [
        cert for cert in parsed.get("certifications", []) if isinstance(cert, dict)
    ]
    parsed["languages"] = _normalize_languages(parsed.get("languages", []))
    parsed["redrob_signals"] = _normalize_redrob_signals(
        parsed.get("redrob_signals", {})
    )
    return parsed


def iter_candidates(input_path: Path) -> Iterator[dict[str, Any]]:
    """Yield candidate records from JSONL or JSON input."""
    try:
        with input_path.open("r", encoding="utf-8") as handle:
            first_non_ws = ""
            position = handle.tell()
            while True:
                char = handle.read(1)
                if not char:
                    break
                if not char.isspace():
                    first_non_ws = char
                    break
            handle.seek(position)
            if first_non_ws == "[":
                data = json.load(handle)
                if isinstance(data, list):
                    for record in data:
                        if isinstance(record, dict):
                            yield record
                return
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    yield record
    except FileNotFoundError:
        return


def save_candidates(candidates: Iterator[dict[str, Any]], output_path: Path) -> None:
    """Persist cleaned candidates as a JSON array."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("[\n")
        first = True
        for candidate in candidates:
            if not first:
                handle.write(",\n")
            json.dump(candidate, handle, ensure_ascii=False)
            first = False
        handle.write("\n]\n")


def main() -> None:
    """Run the end-to-end dataset processing pipeline."""
    cleaned = (normalize_candidate(candidate) for candidate in iter_candidates(INPUT_PATH))
    save_candidates(cleaned, OUTPUT_PATH)


if __name__ == "__main__":
    main()
