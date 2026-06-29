

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a timestamped console handler.

    Args:
        level: Python logging level constant (default: INFO).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and return command-line arguments.

    Args:
        argv: Argument list; defaults to sys.argv[1:] when None.

    Returns:
        Populated Namespace with attributes: input, output, schema.
    """
    parser = argparse.ArgumentParser(
        prog="inspect_schema",
        description=(
            "Stream a JSONL candidate dataset and produce a schema quality report."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="FILE",
        help="Path to the input JSONL file (candidates.jsonl).",
    )
    parser.add_argument(
        "--output",
        default="outputs/schema_report.json",
        metavar="FILE",
        help=(
            "Destination path for the JSON schema report "
            "(default: outputs/schema_report.json)."
        ),
    )
    parser.add_argument(
        "--schema",
        default=None,
        metavar="FILE",
        help=(
            "Optional path to a JSON Schema file. "
            "When supplied, fields present in the dataset but absent from the "
            "schema are listed as unexpected_fields."
        ),
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FieldStats:
    """Accumulated statistics for a single dot-notation field path.

    Attributes:
        present: Number of records in which this field was observed.
        missing: Number of records in which this field was absent.
        types:   Set of Python type names encountered for this field's values.
    """

    present: int = 0
    missing: int = 0
    types: set[str] = field(default_factory=set)

    def record_present(self, value: Any) -> None:
        """Register one occurrence of this field with the given value.

        Args:
            value: The raw Python value extracted from the JSON object.
        """
        self.present += 1
        self.types.add(detect_python_type(value))

    def record_missing(self) -> None:
        """Register one record where this field was absent."""
        self.missing += 1

    def presence_percent(self, total: int) -> float:
        """Return percentage presence rounded to six decimal places.

        Args:
            total: Total number of candidates processed.

        Returns:
            Float in the range [0.0, 100.0].
        """
        if total == 0:
            return 0.0
        return round(self.present / total * 100, 6)


# ---------------------------------------------------------------------------
# Type detection
# ---------------------------------------------------------------------------

def detect_python_type(value: Any) -> str:
    """Return the canonical Python type name for *value*.

    Booleans are reported as ``"bool"`` rather than ``"int"`` because
    ``bool`` is a subclass of ``int`` in Python.

    Args:
        value: Any Python object obtained by json.loads.

    Returns:
        One of: "bool", "int", "float", "str", "list", "dict", "NoneType".
    """
    if isinstance(value, bool):
        return "bool"
    return type(value).__name__


# ---------------------------------------------------------------------------
# Schema path extraction
# ---------------------------------------------------------------------------

def walk_json(
    obj: Any,
    prefix: str = "",
) -> Iterator[tuple[str, Any]]:
    """Recursively yield (dot-notation-path, value) pairs from a JSON object.

    Array indexes are intentionally omitted so that ``skills[0].name`` is
    yielded as ``skills.name``.  When a list element is not a dict it is
    yielded directly under the parent path.

    Args:
        obj:    The JSON value to traverse (dict, list, or scalar).
        prefix: Dot-notation prefix accumulated from parent calls.

    Yields:
        Tuples of (path, value) where path uses dot notation without indexes.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{prefix}.{key}" if prefix else key
            yield child_path, value
            if isinstance(value, (dict, list)):
                yield from walk_json(value, child_path)
    elif isinstance(obj, list):
        for element in obj:
            if isinstance(element, (dict, list)):
                yield from walk_json(element, prefix)
            else:
                # Scalar list element — surface it at the parent path.
                yield prefix, element


# ---------------------------------------------------------------------------
# Expected schema loading
# ---------------------------------------------------------------------------

def extract_schema_paths(schema_node: Any, prefix: str = "") -> set[str]:
    """Recursively extract all expected field paths from a JSON Schema object.

    Handles the common JSON Schema keywords: ``properties``, ``items``,
    ``allOf``, ``anyOf``, ``oneOf``, and ``$defs`` / ``definitions``.

    Args:
        schema_node: A dict representing (part of) a JSON Schema.
        prefix:      Dot-notation prefix accumulated from parent calls.

    Returns:
        Set of dot-notation field path strings.
    """
    paths: set[str] = set()

    if not isinstance(schema_node, dict):
        return paths

    # Direct properties
    if "properties" in schema_node:
        for prop_name, sub_schema in schema_node["properties"].items():
            child_path = f"{prefix}.{prop_name}" if prefix else prop_name
            paths.add(child_path)
            paths |= extract_schema_paths(sub_schema, child_path)

    # Array items
    if "items" in schema_node:
        paths |= extract_schema_paths(schema_node["items"], prefix)

    # Combiners
    for combiner_key in ("allOf", "anyOf", "oneOf"):
        if combiner_key in schema_node:
            for sub_schema in schema_node[combiner_key]:
                paths |= extract_schema_paths(sub_schema, prefix)

    # Definitions / $defs (not walked into automatically; only if referenced
    # by a $ref – skip $ref resolution to keep stdlib-only and avoid cycles)
    return paths


def load_expected_schema(schema_path: str) -> set[str]:
    """Load a JSON Schema file and return the set of expected field paths.

    Args:
        schema_path: Filesystem path to a JSON Schema (.json) file.

    Returns:
        Set of dot-notation field path strings extracted from the schema.

    Raises:
        FileNotFoundError: If *schema_path* does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    path = Path(schema_path)
    logger.info("Loading expected schema from: %s", path)
    with path.open(encoding="utf-8") as fh:
        raw_schema: Any = json.load(fh)
    expected: set[str] = extract_schema_paths(raw_schema)
    logger.info("Expected schema contains %d field paths.", len(expected))
    return expected


# ---------------------------------------------------------------------------
# Per-candidate inspection
# ---------------------------------------------------------------------------

def inspect_candidate(
    candidate: dict[str, Any],
    field_registry: dict[str, FieldStats],
    all_known_paths: set[str],
) -> None:
    """Update *field_registry* with the fields found in *candidate*.

    For every field path already seen in previous candidates that is
    absent from the current candidate, the missing counter is incremented.

    Args:
        candidate:      Parsed JSON object for one candidate.
        field_registry: Mutable mapping of path → FieldStats (updated in place).
        all_known_paths: Set of every path encountered so far (updated in place).
    """
    observed_paths: set[str] = set()

    for path, value in walk_json(candidate):
        # Do not record intermediate dict/list nodes — only leaf / typed values.
        if isinstance(value, (dict, list)):
            continue
        observed_paths.add(path)
        if path not in field_registry:
            field_registry[path] = FieldStats()
        field_registry[path].record_present(value)

    # Fields seen in previous candidates but absent here.
    for missing_path in all_known_paths - observed_paths:
        field_registry[missing_path].record_missing()

    # New paths discovered in this candidate must be back-filled for every
    # previous candidate (each of which was effectively missing this field).
    new_paths = observed_paths - all_known_paths
    total_before = sum(
        field_registry[p].present + field_registry[p].missing
        for p in all_known_paths
    )
    # Approximate: use the running total for one of the existing fields.
    # More precisely, count how many candidates came before this one.
    # We infer "candidates seen before this one" from any already-known field.
    if all_known_paths:
        sample_path = next(iter(all_known_paths))
        candidates_before: int = (
            field_registry[sample_path].present
            + field_registry[sample_path].missing
        )
    else:
        candidates_before = 0

    for new_path in new_paths:
        # Back-fill missing count for all previous candidates.
        field_registry[new_path].missing = candidates_before

    all_known_paths.update(observed_paths)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    field_registry: dict[str, FieldStats],
    total_candidates: int,
    expected_paths: set[str] | None,
) -> dict[str, Any]:
    """Build the final schema quality report dictionary.

    Args:
        field_registry:   Mapping of path → FieldStats after full dataset scan.
        total_candidates: Total number of JSONL lines successfully parsed.
        expected_paths:   Set of field paths from a supplied JSON Schema, or
                          None when no schema was provided.

    Returns:
        Dict ready to be serialised as JSON.
    """
    fields_detail: dict[str, Any] = {}
    optional_fields: list[str] = []
    inconsistent_types: list[str] = []

    for path in sorted(field_registry):
        stats = field_registry[path]
        sorted_types = sorted(stats.types)

        fields_detail[path] = {
            "present": stats.present,
            "missing": stats.missing,
            "presence_percent": stats.presence_percent(total_candidates),
            "types": sorted_types,
        }

        if stats.present < total_candidates:
            optional_fields.append(path)

        if len(stats.types) > 1:
            inconsistent_types.append(path)

    # Unexpected fields
    if expected_paths is not None:
        discovered = set(field_registry.keys())
        unexpected_fields: list[str] = sorted(discovered - expected_paths)
    else:
        unexpected_fields = []

    report: dict[str, Any] = {
        "dataset_summary": {
            "total_candidates": total_candidates,
            "unique_fields": len(field_registry),
        },
        "fields": fields_detail,
        "optional_fields": sorted(optional_fields),
        "inconsistent_types": sorted(inconsistent_types),
        "unexpected_fields": unexpected_fields,
    }

    return report


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------

def save_report(report: dict[str, Any], output_path: str) -> None:
    """Serialise *report* as indented UTF-8 JSON to *output_path*.

    Parent directories are created automatically.

    Args:
        report:      The report dictionary to write.
        output_path: Destination file path (string or Path-compatible).

    Raises:
        OSError: If the file cannot be written.
    """
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    logger.info("Schema report written to: %s", dest.resolve())


# ---------------------------------------------------------------------------
# JSONL streaming
# ---------------------------------------------------------------------------

def stream_jsonl(input_path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield (line_number, parsed_object) for every valid JSON line.

    Blank lines and lines that fail JSON parsing are skipped with a warning.
    The file is read line-by-line so memory usage stays O(unique_fields).

    Args:
        input_path: Path to a UTF-8 encoded JSONL file.

    Yields:
        Tuples of (1-based line number, parsed dict).

    Raises:
        FileNotFoundError: If *input_path* does not exist.
    """
    with input_path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping line %d – JSON parse error: %s", lineno, exc
                )
                continue
            if not isinstance(obj, dict):
                logger.warning(
                    "Skipping line %d – expected JSON object, got %s.",
                    lineno,
                    type(obj).__name__,
                )
                continue
            yield lineno, obj


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point.  Parse args, stream dataset, build and save report.

    Args:
        argv: Optional argument list (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    setup_logging()
    args = parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return 1

    # Optionally load expected schema.
    expected_paths: set[str] | None = None
    if args.schema is not None:
        try:
            expected_paths = load_expected_schema(args.schema)
        except FileNotFoundError:
            logger.error("Schema file not found: %s", args.schema)
            return 1
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse schema file: %s", exc)
            return 1

    # Streaming pass over the dataset.
    field_registry: dict[str, FieldStats] = {}
    all_known_paths: set[str] = set()
    total_candidates = 0

    logger.info("Streaming dataset: %s", input_path)

    for lineno, candidate in stream_jsonl(input_path):
        total_candidates += 1
        inspect_candidate(candidate, field_registry, all_known_paths)

        if total_candidates % 100_000 == 0:
            logger.info(
                "Progress: %d candidates processed, %d unique fields discovered.",
                total_candidates,
                len(field_registry),
            )

    logger.info(
        "Finished streaming. Total candidates: %d | Unique fields: %d",
        total_candidates,
        len(field_registry),
    )

    # Build report.
    report = generate_report(field_registry, total_candidates, expected_paths)

    # Persist report.
    try:
        save_report(report, args.output)
    except OSError as exc:
        logger.error("Failed to write report: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())