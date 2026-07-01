

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
class ParseStats:
    """Mutable counters populated during JSONL streaming.

    Attributes:
        skipped_lines: Non-blank lines that could not be parsed as a JSON
                       object (malformed JSON or a non-object top-level value).
        blank_lines:   Empty or whitespace-only lines encountered and ignored.
    """

    skipped_lines: int = 0
    blank_lines: int = 0


@dataclass
class FieldStats:
    """Accumulated statistics for a single dot-notation field path.

    Attributes:
        present: Number of candidates in which this field was observed at
                 least once.  A path that appears multiple times within a
                 single candidate (e.g. across repeated array elements) is
                 counted exactly once per candidate.
        missing: Number of candidates in which this field was entirely absent.
        types:   Union of all Python type names observed for this field's
                 values across every candidate and every array element.
    """

    present: int = 0
    missing: int = 0
    types: set[str] = field(default_factory=set)

    def mark_present(self) -> None:
        """Increment the presence counter by one.

        Must be called at most once per (candidate, path) pair regardless of
        how many times the path appears within array elements of that candidate.
        Calling it more than once per candidate inflates the presence count and
        corrupts the missing count for all other fields.
        """
        self.present += 1

    def update_types(self, observed_types: set[str]) -> None:
        """Merge *observed_types* into the cumulative type set.

        Args:
            observed_types: Python type-name strings observed in one or more
                            occurrences of this path within a single candidate.
        """
        self.types.update(observed_types)

    def record_missing(self) -> None:
        """Increment the missing counter by one.

        Called once for every candidate in which this field path is absent.
        """
        self.missing += 1

    def presence_percent(self, total: int) -> float:
        """Return percentage presence rounded to six decimal places.

        Args:
            total: Total number of valid candidates processed.

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
    ``bool`` is a subclass of ``int`` in Python and ``isinstance(True, int)``
    returns ``True``.

    Args:
        value: Any Python object obtained by ``json.loads``.

    Returns:
        One of: ``"bool"``, ``"int"``, ``"float"``, ``"str"``, ``"list"``,
        ``"dict"``, ``"NoneType"``.
    """
    if isinstance(value, bool):
        return "bool"
    return type(value).__name__


# ---------------------------------------------------------------------------
# JSON Schema utilities
# ---------------------------------------------------------------------------

def _resolve_ref(ref: str, root_schema: dict[str, Any]) -> Any | None:
    """Resolve a local JSON Pointer ``$ref`` against *root_schema*.

    Only document-local (``#``-anchored) references are resolved.  External
    URIs and bare relative paths are not supported and return ``None``.
    JSON Pointer escape sequences are handled per RFC 6901
    (``~1`` → ``/``, ``~0`` → ``~``).

    Args:
        ref:         The raw ``$ref`` string value (e.g.
                     ``"#/$defs/CandidateProfile"``).
        root_schema: The root JSON Schema document used as the resolution base.

    Returns:
        The resolved schema node, or ``None`` when resolution fails (unknown
        pointer token, out-of-range list index, or non-local reference).
    """
    if not isinstance(ref, str):
        return None
    if ref == "#":
        return root_schema
    if not ref.startswith("#/"):
        # External URI or relative path — not supported.
        return None

    pointer = ref[2:]  # Strip the leading "#/"
    parts = pointer.split("/")
    node: Any = root_schema

    for part in parts:
        # Apply JSON Pointer escape sequences (RFC 6901 §3).
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if part not in node:
                logger.debug(
                    "$ref resolution failed: token %r not found in object (ref=%r)",
                    part, ref,
                )
                return None
            node = node[part]
        elif isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                logger.debug(
                    "$ref resolution failed: token %r is not a valid list index "
                    "(ref=%r)",
                    part, ref,
                )
                return None
        else:
            logger.debug(
                "$ref resolution failed: cannot index into %s at token %r "
                "(ref=%r)",
                type(node).__name__, part, ref,
            )
            return None

    return node


def extract_schema_paths(
    schema_node: Any,
    prefix: str = "",
    *,
    root_schema: dict[str, Any] | None = None,
    _visited_refs: frozenset[str] = frozenset(),
) -> set[str]:
    """Recursively extract all expected field paths from a JSON Schema node.

    Handles the following JSON Schema keywords:

    * ``properties``        – object property definitions.
    * ``items``             – array item schema; supports both a single schema
                              (all elements share one schema) and a list of
                              schemas (tuple validation).
    * ``allOf``             – intersection combiner.
    * ``anyOf``             – union combiner.
    * ``oneOf``             – exclusive-union combiner.
    * ``$ref``              – local ``#``-anchored JSON Pointer references,
                              resolved against the root schema document.
    * ``$defs``/``definitions`` – definition stores are resolved implicitly
                              when a ``$ref`` points into them; they are not
                              walked unconditionally, as their paths depend on
                              where each definition is referenced.

    Array indexes are omitted from all paths.  ``$ref`` cycles are detected
    via *_visited_refs* and silently broken to prevent infinite recursion.
    Per JSON Schema draft-07 semantics, a ``$ref`` replaces all sibling
    keywords in the same schema object.

    Args:
        schema_node:     A value representing (part of) a JSON Schema.
                         Non-dict values return an empty set immediately.
        prefix:          Dot-notation prefix accumulated from parent calls.
        root_schema:     The root JSON Schema document for ``$ref`` resolution.
                         Populated automatically on the first call; must be
                         supplied explicitly by recursive internal calls.
        _visited_refs:   Frozenset of ``$ref`` strings already visited on the
                         current call stack, used for cycle detection.

    Returns:
        Set of dot-notation field path strings declared by this schema.
    """
    paths: set[str] = set()

    if not isinstance(schema_node, dict):
        return paths

    # Establish root_schema on the top-level call.
    if root_schema is None:
        root_schema = schema_node

    # ------------------------------------------------------------------
    # $ref — resolve first; per draft-07 a $ref replaces sibling keywords.
    # ------------------------------------------------------------------
    if "$ref" in schema_node:
        ref_value = schema_node["$ref"]
        if isinstance(ref_value, str) and ref_value not in _visited_refs:
            resolved = _resolve_ref(ref_value, root_schema)
            if resolved is not None:
                paths |= extract_schema_paths(
                    resolved,
                    prefix,
                    root_schema=root_schema,
                    _visited_refs=_visited_refs | {ref_value},
                )
            else:
                logger.warning(
                    "Could not resolve $ref %r — skipping.", ref_value
                )
        elif isinstance(ref_value, str) and ref_value in _visited_refs:
            logger.debug("Cycle detected for $ref %r — skipping.", ref_value)
        # Per draft-07: $ref replaces all sibling keywords.
        return paths

    # ------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------
    if "properties" in schema_node:
        props = schema_node["properties"]
        if isinstance(props, dict):
            for prop_name, sub_schema in props.items():
                child_path = f"{prefix}.{prop_name}" if prefix else prop_name
                paths.add(child_path)
                paths |= extract_schema_paths(
                    sub_schema,
                    child_path,
                    root_schema=root_schema,
                    _visited_refs=_visited_refs,
                )

    # ------------------------------------------------------------------
    # items — single schema for all array elements, or tuple-validation
    # list where each position carries its own schema.
    # ------------------------------------------------------------------
    if "items" in schema_node:
        items = schema_node["items"]
        if isinstance(items, list):
            # Tuple validation: each positional schema is walked at the same
            # prefix because array indexes are intentionally omitted.
            for item_schema in items:
                paths |= extract_schema_paths(
                    item_schema,
                    prefix,
                    root_schema=root_schema,
                    _visited_refs=_visited_refs,
                )
        elif isinstance(items, dict):
            paths |= extract_schema_paths(
                items,
                prefix,
                root_schema=root_schema,
                _visited_refs=_visited_refs,
            )

    # ------------------------------------------------------------------
    # Schema combiners: allOf, anyOf, oneOf
    # ------------------------------------------------------------------
    for combiner_key in ("allOf", "anyOf", "oneOf"):
        if combiner_key in schema_node:
            combiner_list = schema_node[combiner_key]
            if isinstance(combiner_list, list):
                for sub_schema in combiner_list:
                    paths |= extract_schema_paths(
                        sub_schema,
                        prefix,
                        root_schema=root_schema,
                        _visited_refs=_visited_refs,
                    )

    return paths


def load_expected_schema(schema_path: str | Path) -> set[str]:
    """Load a JSON Schema file and return the set of expected field paths.

    The file is opened with the ``utf-8-sig`` codec so that an optional UTF-8
    BOM is transparently stripped before parsing.

    Args:
        schema_path: Filesystem path to a JSON Schema (``.json``) file.

    Returns:
        Set of dot-notation field path strings extracted from the schema.

    Raises:
        FileNotFoundError: If *schema_path* does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValueError: If the top-level parsed value is not a JSON object.
    """
    path = Path(schema_path)
    logger.info("Loading expected schema from: %s", path.resolve())
    with path.open(encoding="utf-8-sig") as fh:
        raw_schema: Any = json.load(fh)
    if not isinstance(raw_schema, dict):
        raise ValueError(
            f"Schema file {path} must contain a JSON object at the top level; "
            f"got {type(raw_schema).__name__}."
        )
    expected: set[str] = extract_schema_paths(raw_schema)
    logger.info("Expected schema contains %d field path(s).", len(expected))
    return expected


# ---------------------------------------------------------------------------
# Dataset traversal
# ---------------------------------------------------------------------------

def walk_json(
    obj: Any,
    prefix: str = "",
) -> Iterator[tuple[str, Any]]:
    """Recursively yield ``(dot-notation-path, value)`` for every leaf value.

    Only scalar (non-container) values are yielded.  Intermediate ``dict``
    and ``list`` nodes are used purely to drive recursion; they are never
    surfaced to the caller.  This keeps path semantics clean and eliminates
    the need for callers to filter intermediate nodes.

    Array indexes are intentionally omitted so that ``skills[0].name`` is
    yielded as ``("skills.name", value)``.  Scalar elements of a list are
    yielded under the list's parent path (e.g. an element of a ``"tags"``
    list becomes ``("tags", value)``).

    Edge-case behaviour:

    * Empty dicts ``{}`` and empty lists ``[]`` produce no output — the field
      is treated as absent from that candidate for counting purposes.
    * ``null`` JSON values (Python ``None``) are treated as scalars and
      yielded normally; callers see type ``"NoneType"``.
    * Nested lists are flattened to the nearest named ancestor path.
    * Arbitrarily deep nesting is handled via standard recursion; Python's
      default call-stack limit of 1 000 frames is sufficient for all realistic
      JSONL candidate data.

    Args:
        obj:    The JSON value to traverse (dict, list, or scalar).
        prefix: Dot-notation prefix accumulated from parent calls.

    Yields:
        Tuples of ``(path, value)`` where *path* uses dot notation without
        array indexes and *value* is a scalar (non-dict, non-list) value.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                yield from walk_json(value, child_path)
            else:
                yield child_path, value
    elif isinstance(obj, list):
        for element in obj:
            if isinstance(element, (dict, list)):
                yield from walk_json(element, prefix)
            else:
                yield prefix, element


# ---------------------------------------------------------------------------
# Per-candidate inspection
# ---------------------------------------------------------------------------

def inspect_candidate(
    candidate: dict[str, Any],
    field_registry: dict[str, FieldStats],
    all_known_paths: set[str],
    candidates_before: int,
) -> None:
    """Update *field_registry* with the fields observed in *candidate*.

    Operates in four explicit phases to guarantee correct counts:

    1. **Collect** – Walk *candidate* and build a ``{path: set_of_types}``
       mapping.  Because ``walk_json`` may yield the same path multiple times
       (e.g. the same key appears in every element of an array), we accumulate
       types into a set and deduplicate at the path level.  This ensures that
       ``present`` is incremented exactly once per candidate per path, not once
       per array element.

    2. **Register** – For each observed path, create or update a
       ``FieldStats`` entry.  Paths seen for the first time are back-filled
       with ``missing = candidates_before`` to account for every prior
       candidate in which the path was absent.

    3. **Mark missing** – For every path that existed before this candidate
       but was not observed here, increment its ``missing`` counter.

    4. **Expand index** – Update *all_known_paths* with any newly discovered
       paths so that subsequent candidates can correctly detect absences.

    Args:
        candidate:         Parsed JSON object for one candidate.
        field_registry:    Mutable mapping of path → ``FieldStats`` updated
                           in place.
        all_known_paths:   Set of every path first observed in prior
                           candidates, updated in place.
        candidates_before: Exact count of candidates processed before this
                           one.  Passed explicitly to avoid fragile inference
                           from registry state.
    """
    # ------------------------------------------------------------------
    # Phase 1: Collect all paths and their observed types.
    # defaultdict(set) deduplicates repeated paths from array elements.
    # ------------------------------------------------------------------
    candidate_paths: defaultdict[str, set[str]] = defaultdict(set)
    for path, value in walk_json(candidate):
        candidate_paths[path].add(detect_python_type(value))

    observed_paths: set[str] = set(candidate_paths.keys())

    # ------------------------------------------------------------------
    # Phase 2: Create or update FieldStats for every observed path.
    # ------------------------------------------------------------------
    for path, types in candidate_paths.items():
        if path not in field_registry:
            # First time this path is seen: back-fill the missing count for
            # every prior candidate, each of which lacked this field.
            field_registry[path] = FieldStats(missing=candidates_before)
        field_registry[path].mark_present()
        field_registry[path].update_types(types)

    # ------------------------------------------------------------------
    # Phase 3: Increment missing count for known paths absent here.
    # ------------------------------------------------------------------
    for missing_path in all_known_paths - observed_paths:
        field_registry[missing_path].record_missing()

    # ------------------------------------------------------------------
    # Phase 4: Expand the known-path index with any new discoveries.
    # ------------------------------------------------------------------
    all_known_paths.update(observed_paths)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    field_registry: dict[str, FieldStats],
    total_candidates: int,
    expected_paths: set[str] | None,
    parse_stats: ParseStats,
    input_file: str | None = None,
    schema_file: str | None = None,
) -> dict[str, Any]:
    """Build the final schema quality report dictionary.

    The ``fields`` mapping is keyed in lexicographic sort order so the report
    is deterministic regardless of processing order or insertion history.
    ``optional_fields`` and ``inconsistent_types`` are populated during the
    same sorted iteration and therefore require no secondary sort.

    Args:
        field_registry:   Mapping of path → ``FieldStats`` after a full
                          dataset scan.
        total_candidates: Count of JSONL lines successfully parsed as valid
                          JSON objects and processed by the pipeline.
        expected_paths:   Field paths extracted from a supplied JSON Schema,
                          or ``None`` when no schema was provided.
        parse_stats:      Stream counters accumulated during JSONL parsing.
        input_file:       Resolved path of the input JSONL file, included as
                          provenance metadata (``None`` if not supplied).
        schema_file:      Resolved path of the JSON Schema file, or ``None``.

    Returns:
        Dictionary ready to be serialised as pretty-printed JSON.
    """
    fields_detail: dict[str, Any] = {}
    optional_fields: list[str] = []
    inconsistent_types: list[str] = []

    # Iterate in sorted order; both subsidiary lists are therefore already
    # sorted and do not need a secondary sorted() call.
    for path in sorted(field_registry):
        stats = field_registry[path]
        sorted_types = sorted(stats.types)

        fields_detail[path] = {
            "present": stats.present,
            "missing": stats.missing,
            "presence_percent": stats.presence_percent(total_candidates),
            "types": sorted_types,
        }

        # A field is optional when it is absent in at least one candidate.
        if stats.present < total_candidates:
            optional_fields.append(path)

        # A field has inconsistent types when more than one Python type is seen.
        if len(stats.types) > 1:
            inconsistent_types.append(path)

    # Unexpected fields: present in the dataset but absent from the schema.
    if expected_paths is not None:
        discovered = set(field_registry.keys())
        unexpected_fields: list[str] = sorted(discovered - expected_paths)
    else:
        unexpected_fields = []

    report: dict[str, Any] = {
        "dataset_summary": {
            "total_candidates": total_candidates,
            "skipped_lines": parse_stats.skipped_lines,
            "blank_lines": parse_stats.blank_lines,
            "unique_fields": len(field_registry),
            "input_file": input_file,
            "schema_file": schema_file,
        },
        "fields": fields_detail,
        "optional_fields": optional_fields,
        "inconsistent_types": inconsistent_types,
        "unexpected_fields": unexpected_fields,
    }

    return report


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------

def save_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Serialise *report* as indented UTF-8 JSON to *output_path*.

    Uses an atomic write strategy: the JSON is written to a sibling
    ``<name>.tmp`` file in the same directory, then renamed over the
    destination with ``Path.replace()``.  On POSIX systems the rename is
    atomic; on Windows it is as close to atomic as the OS allows.  A partial
    or interrupted write therefore never corrupts an existing report at the
    destination path.  The temporary file is removed on failure.

    Parent directories are created automatically.

    Args:
        report:      The report dictionary to write.
        output_path: Destination file path (``str`` or ``Path``).

    Raises:
        OSError: If the destination directory cannot be created or the file
                 cannot be written or renamed.
    """
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (dest.name + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False, sort_keys=False)
            fh.write("\n")
        tmp.replace(dest)
    except Exception:
        # Best-effort cleanup of the incomplete temporary file.
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise
    logger.info("Schema report written to: %s", dest.resolve())


# ---------------------------------------------------------------------------
# JSONL streaming
# ---------------------------------------------------------------------------

def stream_jsonl(
    input_path: Path,
    stats: ParseStats | None = None,
) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield ``(line_number, parsed_object)`` for every valid JSON object line.

    Blank lines are silently skipped and counted in *stats*.  Lines that fail
    JSON parsing, or whose top-level value is not a ``dict``, are skipped with
    a ``WARNING`` log entry and also counted in *stats*.

    The file is opened with the ``utf-8-sig`` codec so that an optional UTF-8
    BOM at the start of the file is transparently stripped before the first
    ``json.loads`` call; without this, a BOM causes a ``JSONDecodeError`` on
    line 1.

    The file is read strictly line-by-line; the dataset is never loaded into
    memory, keeping memory complexity at O(unique_fields) regardless of dataset
    size.

    Args:
        input_path: Path to a UTF-8 (optionally BOM-prefixed) JSONL file.
        stats:      Optional ``ParseStats`` instance mutated in place to
                    accumulate ``skipped_lines`` and ``blank_lines`` counts.
                    A fresh instance is created internally when ``None``.

    Yields:
        Tuples of ``(1-based line number, parsed dict)``.

    Raises:
        FileNotFoundError: If *input_path* does not exist.
        OSError:           On any other file-read failure.
    """
    if stats is None:
        stats = ParseStats()

    with input_path.open(encoding="utf-8-sig") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            stripped = raw_line.strip()
            if not stripped:
                stats.blank_lines += 1
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping line %d – JSON parse error: %s", lineno, exc
                )
                stats.skipped_lines += 1
                continue
            if not isinstance(obj, dict):
                logger.warning(
                    "Skipping line %d – expected a JSON object, got %s.",
                    lineno,
                    type(obj).__name__,
                )
                stats.skipped_lines += 1
                continue
            yield lineno, obj


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point.  Parse arguments, stream the dataset, build and save report.

    Args:
        argv: Optional argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code: ``0`` on success, ``1`` on error.
    """
    setup_logging()
    args = parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path.resolve())
        return 1
    if not input_path.is_file():
        logger.error(
            "Input path exists but is not a regular file: %s", input_path.resolve()
        )
        return 1

    # Optionally load the expected schema for unexpected-field detection.
    expected_paths: set[str] | None = None
    schema_file: str | None = None
    if args.schema is not None:
        try:
            expected_paths = load_expected_schema(args.schema)
            schema_file = str(Path(args.schema).resolve())
        except FileNotFoundError:
            logger.error("Schema file not found: %s", args.schema)
            return 1
        except json.JSONDecodeError as exc:
            logger.error("Schema file contains invalid JSON: %s", exc)
            return 1
        except ValueError as exc:
            logger.error("Schema file is invalid: %s", exc)
            return 1

    # Streaming pass — memory stays O(unique_fields) throughout.
    field_registry: dict[str, FieldStats] = {}
    all_known_paths: set[str] = set()
    total_candidates: int = 0
    parse_stats = ParseStats()

    logger.info("Streaming dataset: %s", input_path.resolve())

    for _lineno, candidate in stream_jsonl(input_path, parse_stats):
        # Pass total_candidates (not yet incremented) as candidates_before so
        # that the value exactly equals the number of candidates processed
        # before the current one.
        inspect_candidate(
            candidate, field_registry, all_known_paths, total_candidates
        )
        total_candidates += 1

        if total_candidates % 100_000 == 0:
            logger.info(
                "Progress: %d candidates processed, %d unique fields discovered.",
                total_candidates,
                len(field_registry),
            )

    logger.info(
        "Finished. total_candidates=%d | unique_fields=%d | skipped_lines=%d",
        total_candidates,
        len(field_registry),
        parse_stats.skipped_lines,
    )

    # Build the report.
    report = generate_report(
        field_registry,
        total_candidates,
        expected_paths,
        parse_stats,
        input_file=str(input_path.resolve()),
        schema_file=schema_file,
    )

    # Persist the report atomically.
    try:
        save_report(report, args.output)
    except OSError as exc:
        logger.error("Failed to write report to %s: %s", args.output, exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())