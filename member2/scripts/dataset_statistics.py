

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from collections import Counter, defaultdict
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
        Populated Namespace with attributes: input, output.
    """
    parser = argparse.ArgumentParser(
        prog="dataset_statistics",
        description=(
            "Stream a JSONL candidate dataset and produce descriptive "
            "statistics: field presence, Python type distribution, "
            "string/numeric/list statistics, null counts, and per-candidate "
            "completeness."
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
        default="outputs/dataset_statistics.json",
        metavar="FILE",
        help=(
            "Destination path for the JSON statistics report "
            "(default: outputs/dataset_statistics.json)."
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
class FieldStatistics:
    """Streaming statistics accumulated for a single dot-notation field path.

    Every attribute is an incremental accumulator (a running count, sum, or
    running min/max). No individual observed value is ever retained, so a
    single instance occupies constant memory regardless of how many
    candidates or occurrences contributed to it. With one instance per
    discovered field path, total memory across the whole run stays at
    O(number_of_unique_fields), exactly as required for streaming over
    datasets that may exceed one million candidates.

    Attributes:
        present:          Candidates in which this path was observed at
                          least once. A path that occurs multiple times
                          within a single candidate (e.g. across repeated
                          list elements) is counted exactly once per
                          candidate — mirroring inspect_schema.py's
                          presence semantics so the two reports stay
                          comparable.
        missing:          Candidates in which this path was entirely absent.
        type_counts:      Occurrence-level counts of every Python type seen
                          at this path (str/int/float/bool/dict/list/
                          NoneType). Unlike `present`, this is NOT
                          deduplicated per candidate: a list of three
                          strings contributes three "str" occurrences. This
                          is what allows a field to carry both a "list"
                          occurrence (the container itself) and "str"
                          occurrences (its scalar elements).
        string_count:     Number of "str"-typed occurrences seen.
        string_min_length / string_max_length / string_length_sum:
                          Running min, max, and sum of `len(value)` over
                          every "str" occurrence.
        numeric_count:    Number of "int"/"float"-typed occurrences seen
                          (booleans are excluded; see detect_python_type).
        numeric_min / numeric_max / numeric_sum:
                          Running min, max, and sum over every numeric
                          occurrence. Kept as `int | float` rather than
                          force-cast to float so integer fields are not
                          cosmetically turned into floats in the report.
        list_count:       Number of "list"-typed occurrences seen.
        list_min_length / list_max_length / list_length_sum:
                          Running min, max, and sum of `len(value)` over
                          every "list" occurrence — the container's own
                          element count, not its descendants' statistics.
    """

    present: int = 0
    missing: int = 0
    type_counts: Counter[str] = field(default_factory=Counter)

    string_count: int = 0
    string_min_length: int = 0
    string_max_length: int = 0
    string_length_sum: int = 0

    numeric_count: int = 0
    numeric_min: int | float = 0
    numeric_max: int | float = 0
    numeric_sum: int | float = 0

    list_count: int = 0
    list_min_length: int = 0
    list_max_length: int = 0
    list_length_sum: int = 0

    def mark_present(self) -> None:
        """Increment the presence counter by one.

        Must be called at most once per (candidate, path) pair regardless of
        how many occurrences of the path were observed within that
        candidate. Calling it more than once per candidate inflates the
        presence count and corrupts the missing count for all other fields.
        """
        self.present += 1

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

    def record_type(self, type_name: str) -> None:
        """Increment the occurrence count for *type_name* by one.

        Args:
            type_name: Canonical Python type name, as returned by
                       detect_python_type().
        """
        self.type_counts[type_name] += 1

    def record_string(self, length: int) -> None:
        """Fold one string occurrence's length into the running statistics.

        Args:
            length: ``len(value)`` for the observed string.
        """
        if self.string_count == 0:
            self.string_min_length = length
            self.string_max_length = length
        elif length < self.string_min_length:
            self.string_min_length = length
        elif length > self.string_max_length:
            self.string_max_length = length
        self.string_length_sum += length
        self.string_count += 1

    def record_numeric(self, value: int | float) -> None:
        """Fold one numeric occurrence into the running min/max/sum.

        Non-finite floats (``NaN``, ``inf``, ``-inf``) are intentionally
        excluded: standard JSON has no literal for them, the standard
        library's permissive parser will nonetheless accept the
        non-standard ``NaN``/``Infinity``/``-Infinity`` tokens, and letting
        such a value flow into min/max/sum would both corrupt the
        statistics and risk emitting non-standard tokens back out into the
        report JSON.

        Args:
            value: The observed ``int`` or ``float`` value.
        """
        if not math.isfinite(value):
            logger.debug("Skipping non-finite numeric value: %r", value)
            return
        if self.numeric_count == 0:
            self.numeric_min = value
            self.numeric_max = value
        elif value < self.numeric_min:
            self.numeric_min = value
        elif value > self.numeric_max:
            self.numeric_max = value
        self.numeric_sum += value
        self.numeric_count += 1

    def record_list(self, length: int) -> None:
        """Fold one list occurrence's element count into the running stats.

        Args:
            length: ``len(value)`` for the observed list (its own element
                    count, not a recursive count of descendant fields).
        """
        if self.list_count == 0:
            self.list_min_length = length
            self.list_max_length = length
        elif length < self.list_min_length:
            self.list_min_length = length
        elif length > self.list_max_length:
            self.list_max_length = length
        self.list_length_sum += length
        self.list_count += 1

    def average_string_length(self) -> float:
        """Return the mean string length, or 0.0 if none were observed."""
        if self.string_count == 0:
            return 0.0
        return round(self.string_length_sum / self.string_count, 6)

    def average_numeric(self) -> float:
        """Return the arithmetic mean, or 0.0 if no numeric values exist."""
        if self.numeric_count == 0:
            return 0.0
        return round(self.numeric_sum / self.numeric_count, 6)

    def average_list_length(self) -> float:
        """Return the mean list length, or 0.0 if none were observed."""
        if self.list_count == 0:
            return 0.0
        return round(self.list_length_sum / self.list_count, 6)


@dataclass
class RunningCountStats:
    """Streaming min/max/mean accumulator for a sequence of integer counts.

    Used for both `fields_per_candidate` (every distinct path touched by a
    candidate) and `populated_leaf_fields` (candidate completeness). No
    individual count is retained — only the running minimum, maximum, total,
    and number of observations — keeping memory at O(1) regardless of
    dataset size.

    Attributes:
        count:   Number of values recorded.
        minimum: Running minimum of all recorded values.
        maximum: Running maximum of all recorded values.
        total:   Running sum of all recorded values.
    """

    count: int = 0
    minimum: int = 0
    maximum: int = 0
    total: int = 0

    def record(self, value: int) -> None:
        """Fold one observation into the running minimum/maximum/sum.

        Args:
            value: A single non-negative integer observation.
        """
        if self.count == 0:
            self.minimum = value
            self.maximum = value
        elif value < self.minimum:
            self.minimum = value
        elif value > self.maximum:
            self.maximum = value
        self.total += value
        self.count += 1

    def mean(self) -> float:
        """Return the arithmetic mean, or 0.0 if nothing was recorded."""
        if self.count == 0:
            return 0.0
        return round(self.total / self.count, 6)


@dataclass(frozen=True)
class CandidateFieldCounts:
    """Per-candidate counts produced by a single update_statistics() call.

    Attributes:
        fields_observed:       Total distinct field paths encountered
                               anywhere in the candidate. Containers
                               (dict/list), scalars, and explicit nulls each
                               count once per path, regardless of how many
                               occurrences contributed to that path.
        populated_leaf_fields: Count of distinct paths that resolved to at
                               least one non-null scalar (str/int/float/
                               bool) value somewhere in the candidate.
                               Container-typed paths (dict/list) and
                               null-only paths are excluded, since they are
                               not themselves leaf values.
    """

    fields_observed: int
    populated_leaf_fields: int


# ---------------------------------------------------------------------------
# Type detection
# ---------------------------------------------------------------------------

#: Canonical Python type names tracked in the type-distribution report,
#: fixed in this order so every field's entry has a deterministic key order.
_PYTHON_TYPES: tuple[str, ...] = (
    "str", "int", "float", "bool", "dict", "list", "NoneType",
)

#: Scalar (non-container, non-null) type names that count as a "populated
#: leaf field" when observed for a given path within a candidate.
_LEAF_TYPES: frozenset[str] = frozenset({"str", "int", "float", "bool"})


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
# Traversal
# ---------------------------------------------------------------------------

def walk_json(obj: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Recursively walk *obj*, yielding ``(path, value)`` for every field.

    Unlike a leaf-only walker, this yields the value found at *every* dict
    key — including container-typed values — before recursing into it. That
    is what lets a field such as ``"skills"`` carry a ``"list"`` occurrence
    for the container itself, in addition to whatever occurrences its
    descendants (``"skills.name"``) contribute; a leaf-only walker could
    never report ``dict``/``list`` as observed field types at all.

    Traversal rules:

    * Dict keys become dot-notation path segments: ``{"profile":
      {"location": "NY"}}`` yields ``("profile", {...})`` and then
      ``("profile.location", "NY")``.
    * Array indexes are always omitted. A dict element of a list is walked
      under the *list's own path* (e.g. an element of ``"skills"`` surfaces
      as ``("skills.name", ...)``, never ``"skills[0].name"``).
    * A scalar element of a list is yielded directly under the list's own
      path (e.g. an element of ``"tags": ["python", "java"]`` becomes
      ``("tags", "python")``), in addition to the one ``("tags", [...])``
      occurrence already yielded for the list container itself.
    * Empty dicts (``{}``) and empty lists (``[]``) are yielded once, for
      the container itself, with no further occurrences — the field is
      still "present" with a recorded type and (for lists) length zero.
    * ``null`` values are yielded as plain scalars; callers see type
      ``"NoneType"``.

    Arbitrarily deep nesting is handled via standard recursion; Python's
    default call-stack limit of 1 000 frames is sufficient for all realistic
    JSONL candidate data.

    Args:
        obj:    The JSON value to traverse (dict, list, or scalar).
        prefix: Dot-notation prefix accumulated from parent calls.

    Yields:
        Tuples of ``(path, value)`` where *path* uses dot notation without
        array indexes and *value* is the raw value observed at that path
        for this occurrence (scalar, dict, or list).
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{prefix}.{key}" if prefix else key
            yield child_path, value
            if isinstance(value, dict):
                yield from walk_json(value, child_path)
            elif isinstance(value, list):
                yield from _walk_list(value, child_path)
    elif isinstance(obj, list):
        yield from _walk_list(obj, prefix)


def _walk_list(items: list[Any], prefix: str) -> Iterator[tuple[str, Any]]:
    """Flatten the elements of a list onto *prefix*, omitting indexes.

    Args:
        items:  The list to flatten.
        prefix: The dot-notation path of the list field that owns *items*.

    Yields:
        Tuples of ``(path, value)`` for every element, recursing into dict
        and (nested) list elements so deeply nested structures still
        collapse onto dot-notation paths with no array indexes anywhere.
    """
    for element in items:
        if isinstance(element, dict):
            yield from walk_json(element, prefix)
        elif isinstance(element, list):
            # A nested list still gets its own container occurrence
            # (type "list", with its own length) before being flattened.
            yield prefix, element
            yield from _walk_list(element, prefix)
        else:
            yield prefix, element


# ---------------------------------------------------------------------------
# Per-candidate update
# ---------------------------------------------------------------------------

def update_statistics(
    candidate: dict[str, Any],
    field_registry: dict[str, FieldStatistics],
    all_known_paths: set[str],
    candidates_before: int,
) -> CandidateFieldCounts:
    """Update *field_registry* with the fields observed in *candidate*.

    Operates in four explicit phases, mirroring inspect_schema.py's
    inspect_candidate(), to guarantee correct counts:

    1. **Collect** – Walk *candidate* and build a
       ``{path: [observed_values]}`` mapping. Because walk_json() can yield
       the same path multiple times (a list's container occurrence plus one
       occurrence per element), every value is appended rather than
       deduplicated — type distribution and string/numeric/list statistics
       need every individual occurrence.
    2. **Register** – For each observed path, create or update a
       ``FieldStatistics`` entry. Paths seen for the first time are
       back-filled with ``missing = candidates_before`` to account for
       every prior candidate in which the path was absent. ``present`` is
       still incremented exactly once per (candidate, path) pair, regardless
       of how many occurrences were collected for it in phase 1.
    3. **Mark missing** – For every path that existed before this candidate
       but was not observed here, increment its ``missing`` counter.
    4. **Expand index** – Update *all_known_paths* with any newly
       discovered paths so that subsequent candidates can correctly detect
       absences.

    Args:
        candidate:         Parsed JSON object for one candidate.
        field_registry:    Mutable mapping of path → ``FieldStatistics``
                           updated in place.
        all_known_paths:   Set of every path first observed in prior
                           candidates, updated in place.
        candidates_before: Exact count of candidates processed before this
                           one. Passed explicitly to avoid fragile inference
                           from registry state.

    Returns:
        A ``CandidateFieldCounts`` summarising this candidate's distinct
        field count and populated-leaf-field count, for the caller to fold
        into its own running ``RunningCountStats`` accumulators. No
        candidate data is retained beyond the lifetime of this call.
    """
    # ------------------------------------------------------------------
    # Phase 1: Collect every occurrence, grouped by path.
    # ------------------------------------------------------------------
    candidate_observations: defaultdict[str, list[Any]] = defaultdict(list)
    for path, value in walk_json(candidate):
        candidate_observations[path].append(value)

    observed_paths: set[str] = set(candidate_observations.keys())
    populated_leaf_fields = 0

    # ------------------------------------------------------------------
    # Phase 2: Create or update FieldStatistics for every observed path.
    # ------------------------------------------------------------------
    for path, values in candidate_observations.items():
        if path not in field_registry:
            # First time this path is seen: back-fill the missing count for
            # every prior candidate, each of which lacked this field.
            field_registry[path] = FieldStatistics(missing=candidates_before)
        stats = field_registry[path]
        stats.mark_present()

        is_populated_leaf = False
        for value in values:
            type_name = detect_python_type(value)
            stats.record_type(type_name)

            if type_name == "str":
                stats.record_string(len(value))
                is_populated_leaf = True
            elif type_name in ("int", "float"):
                stats.record_numeric(value)
                is_populated_leaf = True
            elif type_name == "bool":
                is_populated_leaf = True
            elif type_name == "list":
                stats.record_list(len(value))
            # "dict" and "NoneType" occurrences need no extra numeric
            # accumulator and never count as a populated leaf value.

        if is_populated_leaf:
            populated_leaf_fields += 1

    # ------------------------------------------------------------------
    # Phase 3: Increment missing count for known paths absent here.
    # ------------------------------------------------------------------
    for missing_path in all_known_paths - observed_paths:
        field_registry[missing_path].record_missing()

    # ------------------------------------------------------------------
    # Phase 4: Expand the known-path index with any new discoveries.
    # ------------------------------------------------------------------
    all_known_paths.update(observed_paths)

    return CandidateFieldCounts(
        fields_observed=len(observed_paths),
        populated_leaf_fields=populated_leaf_fields,
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    field_registry: dict[str, FieldStatistics],
    total_candidates: int,
    fields_per_candidate: RunningCountStats,
    completeness: RunningCountStats,
    parse_stats: ParseStats,
    input_file: str | None = None,
) -> dict[str, Any]:
    """Build the final dataset statistics report dictionary.

    Every per-field mapping is keyed in lexicographic sort order so the
    report is deterministic regardless of processing order or insertion
    history.

    Args:
        field_registry:        Mapping of path → ``FieldStatistics`` after
                               a full dataset scan.
        total_candidates:      Count of JSONL lines successfully parsed as
                               valid JSON objects and processed.
        fields_per_candidate:  Running min/max/mean of distinct field paths
                               touched per candidate.
        completeness:          Running min/max/mean of populated leaf
                               fields per candidate.
        parse_stats:           Stream counters accumulated during JSONL
                               parsing.
        input_file:            Resolved path of the input JSONL file,
                               included as provenance metadata.

    Returns:
        Dictionary ready to be serialised as pretty-printed JSON.
    """
    field_presence: dict[str, Any] = {}
    type_distribution: dict[str, Any] = {}
    string_statistics: dict[str, Any] = {}
    numeric_statistics: dict[str, Any] = {}
    list_statistics: dict[str, Any] = {}
    null_statistics: dict[str, int] = {}

    for path in sorted(field_registry):
        stats = field_registry[path]

        field_presence[path] = {
            "present": stats.present,
            "missing": stats.missing,
            "presence_percent": stats.presence_percent(total_candidates),
        }

        type_distribution[path] = {
            type_name: stats.type_counts.get(type_name, 0)
            for type_name in _PYTHON_TYPES
        }

        null_statistics[path] = stats.type_counts.get("NoneType", 0)

        if stats.string_count > 0:
            string_statistics[path] = {
                "minimum_length": stats.string_min_length,
                "maximum_length": stats.string_max_length,
                "average_length": stats.average_string_length(),
            }

        if stats.numeric_count > 0:
            numeric_statistics[path] = {
                "minimum": stats.numeric_min,
                "maximum": stats.numeric_max,
                "mean": stats.average_numeric(),
            }

        if stats.list_count > 0:
            list_statistics[path] = {
                "minimum_length": stats.list_min_length,
                "maximum_length": stats.list_max_length,
                "average_length": stats.average_list_length(),
            }

    report: dict[str, Any] = {
        "dataset_summary": {
            "total_candidates": total_candidates,
            "unique_fields": len(field_registry),
            "average_fields_per_candidate": fields_per_candidate.mean(),
            "minimum_fields_per_candidate": fields_per_candidate.minimum,
            "maximum_fields_per_candidate": fields_per_candidate.maximum,
            "skipped_lines": parse_stats.skipped_lines,
            "blank_lines": parse_stats.blank_lines,
            "input_file": input_file,
        },
        "field_presence": field_presence,
        "type_distribution": type_distribution,
        "string_statistics": string_statistics,
        "numeric_statistics": numeric_statistics,
        "list_statistics": list_statistics,
        "null_statistics": null_statistics,
        "candidate_completeness": {
            "minimum": completeness.minimum,
            "maximum": completeness.maximum,
            "average": completeness.mean(),
        },
    }

    return report


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------

def save_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Serialise *report* as indented UTF-8 JSON to *output_path*.

    Uses an atomic write strategy: the JSON is written to a sibling
    ``<name>.tmp`` file in the same directory, then renamed over the
    destination with ``Path.replace()``. On POSIX systems the rename is
    atomic; on Windows it is as close to atomic as the OS allows. A partial
    or interrupted write therefore never corrupts an existing report at the
    destination path.

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
    logger.info("Statistics report written to: %s", dest.resolve())


# ---------------------------------------------------------------------------
# JSONL streaming
# ---------------------------------------------------------------------------

def stream_jsonl(
    input_path: Path,
    stats: ParseStats | None = None,
) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield ``(line_number, parsed_object)`` for every valid JSON object line.

    Blank lines are silently skipped and counted in *stats*. Lines that fail
    JSON parsing, or whose top-level value is not a ``dict``, are skipped
    with a ``WARNING`` log entry and also counted in *stats*.

    The file is opened with the ``utf-8-sig`` codec so that an optional
    UTF-8 BOM at the start of the file is transparently stripped before the
    first ``json.loads`` call; without this, a BOM causes a
    ``JSONDecodeError`` on line 1.

    The file is read strictly line-by-line; the dataset is never loaded
    into memory, keeping memory complexity at O(unique_fields) regardless
    of dataset size.

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
    """Entry point. Parse arguments, stream the dataset, build and save report.

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

    # Streaming pass — memory stays O(unique_fields) throughout.
    field_registry: dict[str, FieldStatistics] = {}
    all_known_paths: set[str] = set()
    total_candidates: int = 0
    parse_stats = ParseStats()
    fields_per_candidate = RunningCountStats()
    completeness = RunningCountStats()

    logger.info("Streaming dataset: %s", input_path.resolve())

    for _lineno, candidate in stream_jsonl(input_path, parse_stats):
        counts = update_statistics(
            candidate, field_registry, all_known_paths, total_candidates
        )
        fields_per_candidate.record(counts.fields_observed)
        completeness.record(counts.populated_leaf_fields)
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
        fields_per_candidate,
        completeness,
        parse_stats,
        input_file=str(input_path.resolve()),
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
