"""Parse the standardised ``## Parameters`` table from agent handbooks.

Every file under ``examples/AGENT_POOL/ExtractedExampleInvestors/unique/``
follows the agent-design rubric and exposes a ``## Parameters`` GitHub
markdown table with the canonical columns:

    | Parameter | Type | Default | Valid Range | Sensitivity |
    | Description | Impact | Source |

Some files use slight header variants (extra spaces, ``Range`` instead of
``Valid Range``).  This module is tolerant of those surface differences;
it only requires that the first column be ``Parameter`` (or ``Symbol``)
and that ``Default`` and ``Type`` columns be present.

The output ``ParamSpec`` is intentionally minimal — it surfaces enough
metadata to render an editable Streamlit widget (numeric, enum, or
free-text fallback) without trying to interpret every nuance of the
handbook prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


_SECTION_RE = re.compile(r"^##\s+Parameters\s*$", re.MULTILINE)
_NEXT_HEADER_RE = re.compile(r"^##\s+\S", re.MULTILINE)
# A parameter symbol: letters, digits, underscores, plus a few greek
# letters that show up in handbook tables (e.g. α, θ, ρ, σ, λ).  We only
# strip the surrounding back-ticks; the symbol itself is preserved
# verbatim so users see what the handbook prescribes.
_BACKTICK_RE = re.compile(r"^`(.+)`$")


@dataclass
class ParamSpec:
    """A single row of an agent's ``## Parameters`` table."""

    symbol: str
    type: str
    default: str
    valid_range: str
    sensitivity: str
    description: str
    impact: str
    source: str
    # Schema-2 (older handbook) extras: a separate human-readable Name
    # column and a Units column.  Captured so the UI can show users a
    # plain-language label instead of the code-like symbol.
    name: str = ""
    units: str = ""
    # Best-effort coercions for editor wiring.
    default_value: Any = None
    enum_values: list[str] = field(default_factory=list)
    numeric_low: Optional[float] = None
    numeric_high: Optional[float] = None
    is_numeric: bool = False
    is_integer: bool = False

    # ------------------------------------------------------------------
    @property
    def display_label(self) -> str:
        """Human-readable label for the parameter row.

        Priority: schema-2 ``Name`` column → ``Description`` (used by
        schema 1) → a label derived from the symbol (de-dotted, with
        ``[i]`` brackets stripped and underscores replaced).  Never
        empty.
        """
        if self.name:
            return self.name
        if self.description:
            return self.description
        # Derive a friendly label from the raw symbol.
        derived = re.sub(r"\[[^\]]*\]", "", self.symbol)
        derived = derived.replace(".", " ").replace("_", " ").strip()
        return derived or self.symbol

    @property
    def kind(self) -> str:
        """Coarse widget kind: ``"enum"``, ``"int"``, ``"float"``, or ``"text"``."""
        if self.enum_values:
            return "enum"
        if self.is_integer:
            return "int"
        if self.is_numeric:
            return "float"
        return "text"


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def parse_parameters_table(markdown: str) -> list[ParamSpec]:
    """Return the parsed ``## Parameters`` rows of a handbook.

    Args:
        markdown: full contents of an agent ``.md`` file.

    Returns:
        A list of :class:`ParamSpec`, one per row of the table.  Returns
        an empty list if the section or table is missing.
    """
    section = _slice_parameters_section(markdown)
    if not section:
        return []

    rows = _table_rows(section)
    if not rows:
        return []

    header, *body = rows
    columns = _normalise_header(header)
    if "parameter" not in columns and "symbol" not in columns:
        return []

    specs: list[ParamSpec] = []
    for raw_row in body:
        cells = _split_row(raw_row)
        if len(cells) < 2:
            continue
        record = _zip_to_record(columns, cells)
        symbol = (record.get("parameter") or record.get("symbol") or "").strip()
        symbol = _strip_backticks(symbol)
        if not symbol or symbol.lower().startswith("--"):
            continue
        spec = _build_spec(symbol, record)
        if spec is not None:
            specs.append(spec)
    return specs


@lru_cache(maxsize=128)
def parse_parameters_file_cached(path: str, mtime_ns: int) -> tuple[ParamSpec, ...]:
    """Cached file parse keyed on ``(path, mtime_ns)``.

    Streamlit re-runs the page on every interaction; the explicit mtime
    in the cache key keeps the cache cheap *and* invalidates whenever
    the underlying handbook is edited on disk.
    """
    text = Path(path).read_text(encoding="utf-8")
    return tuple(parse_parameters_table(text))


def parse_parameters_file(path: str | Path) -> list[ParamSpec]:
    """Read ``path`` and return the parsed parameter table."""
    p = Path(path)
    try:
        mtime_ns = p.stat().st_mtime_ns
    except FileNotFoundError:
        return []
    return list(parse_parameters_file_cached(str(p), mtime_ns))


# ----------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------


def _slice_parameters_section(markdown: str) -> str:
    """Return the ``## Parameters`` section body, up to the next ``##``."""
    if not markdown:
        return ""
    m = _SECTION_RE.search(markdown)
    if not m:
        return ""
    start = m.end()
    rest = markdown[start:]
    end_match = _NEXT_HEADER_RE.search(rest)
    return rest[: end_match.start()] if end_match else rest


def _table_rows(section: str) -> list[str]:
    """Pick out lines that look like markdown table rows.

    A table row starts with a ``|`` (after optional whitespace) and ends
    with a ``|``.  The alignment row (``|---|---|``) is dropped.
    """
    rows: list[str] = []
    for raw in section.splitlines():
        line = raw.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        # Skip the alignment row.
        inside = line.strip("|").strip()
        if inside and set(inside.replace("|", "").replace(":", "").replace("-", "").replace(" ", "")) == set():
            continue
        rows.append(line)
    return rows


def _split_row(row: str) -> list[str]:
    """Split a markdown table row, honouring escaped pipes ``\\|``."""
    # Replace ``\|`` with a sentinel so we can split on ``|`` cleanly.
    sentinel = "\x00PIPE\x00"
    cleaned = row.strip().strip("|").replace(r"\|", sentinel)
    cells = [c.strip().replace(sentinel, "|") for c in cleaned.split("|")]
    return cells


def _normalise_header(row: str) -> list[str]:
    """Return lowercased, whitespace-collapsed header column names."""
    cells = _split_row(row)
    return [re.sub(r"\s+", " ", cell.strip().lower()) for cell in cells]


def _zip_to_record(columns: list[str], cells: list[str]) -> dict[str, str]:
    """Match cells back to header columns, padding/truncating as needed."""
    out: dict[str, str] = {}
    for col, cell in zip(columns, cells):
        # Some handbook columns are literally "valid range" — collapse to
        # the canonical key without the leading word.
        key = col
        if col in ("valid range", "range"):
            key = "valid_range"
        elif " " in col:
            key = col.replace(" ", "_")
        out[key] = cell
    return out


def _build_spec(symbol: str, record: dict[str, str]) -> Optional[ParamSpec]:
    """Construct a :class:`ParamSpec` and best-effort numeric coercions."""
    type_str = _strip_backticks(record.get("type", "").strip())
    default_str = record.get("default", "").strip()
    valid_range = record.get("valid_range", "").strip()
    if not valid_range:
        # Older handbooks use a bare ``Range`` column without ``Valid``.
        valid_range = record.get("range", "").strip()
    sensitivity = record.get("sensitivity", "").strip()
    description = record.get("description", "").strip()
    if not description:
        # Older handbooks use ``Notes`` for the same role.
        description = record.get("notes", "").strip()
    impact = record.get("impact", "").strip()
    source = record.get("source", "").strip()
    name = record.get("name", "").strip()
    units = record.get("units", "").strip()

    spec = ParamSpec(
        symbol=symbol,
        type=type_str,
        default=default_str,
        valid_range=valid_range,
        sensitivity=sensitivity,
        description=description,
        impact=impact,
        source=source,
        name=_strip_backticks(name),
        units=_strip_backticks(units),
    )
    spec.enum_values = _extract_enum_values(type_str)
    spec.is_integer = _looks_integer(type_str)
    spec.is_numeric = spec.is_integer or _looks_float(type_str)

    spec.default_value = _coerce_default(default_str, spec)
    low, high = _coerce_range(valid_range, spec)
    spec.numeric_low = low
    spec.numeric_high = high
    return spec


def _strip_backticks(text: str) -> str:
    if not text:
        return text
    m = _BACKTICK_RE.match(text.strip())
    if m:
        return m.group(1).strip()
    return text.strip()


def _extract_enum_values(type_str: str) -> list[str]:
    """Pull values out of an ``enum<a, b, c>`` type cell."""
    if not type_str:
        return []
    m = re.search(r"enum<([^>]+)>", type_str, flags=re.IGNORECASE)
    if not m:
        return []
    raw = m.group(1)
    return [v.strip() for v in raw.split(",") if v.strip()]


def _looks_integer(type_str: str) -> bool:
    return bool(type_str) and type_str.lower().startswith("int")


def _looks_float(type_str: str) -> bool:
    if not type_str:
        return False
    lo = type_str.lower()
    return any(token in lo for token in ("float", "number", "real"))


def _coerce_default(default_str: str, spec: ParamSpec) -> Any:
    """Best-effort coercion of the default cell into a Python value."""
    if not default_str:
        return None
    raw = _strip_backticks(default_str).strip()
    if not raw:
        return None
    if spec.enum_values:
        # Match against enum values verbatim; fall back to raw string.
        for v in spec.enum_values:
            if raw == v or raw == f"`{v}`":
                return v
        return raw
    if spec.is_integer:
        try:
            return int(raw.replace(",", "").replace("_", ""))
        except ValueError:
            pass
    if spec.is_numeric:
        try:
            return float(raw.replace(",", "").replace("_", ""))
        except ValueError:
            pass
    # Booleans are uncommon but cheap to detect.
    low = raw.lower()
    if low in ("true", "false"):
        return low == "true"
    return raw


def _coerce_range(range_str: str, spec: ParamSpec) -> tuple[Optional[float], Optional[float]]:
    """Best-effort parse of a ``[a, b]`` / ``> 0`` / ``≥ 0`` range cell."""
    if not range_str or spec.enum_values:
        return None, None
    text = _strip_backticks(range_str)
    # Closed/open intervals: [a, b], (a, b], [a, b)
    m = re.search(r"[\[\(]\s*([-+]?[\d\.eE+-]+)\s*,\s*([-+]?[\d\.eE+-]+|∞|inf|infty)\s*[\]\)]", text)
    if m:
        low = _safe_float(m.group(1))
        high = _safe_float(m.group(2))
        return low, high
    # ``>= 0`` / ``> 0`` / ``≥ 0``.
    m2 = re.search(r"(?:>=|≥)\s*([-+]?[\d\.eE+-]+)", text)
    if m2:
        return _safe_float(m2.group(1)), None
    m3 = re.search(r">\s*([-+]?[\d\.eE+-]+)", text)
    if m3:
        return _safe_float(m3.group(1)), None
    return None, None


def _safe_float(token: str) -> Optional[float]:
    if token is None:
        return None
    t = token.strip().lower()
    if t in ("∞", "inf", "infty", "+inf", "+∞"):
        return float("inf")
    if t in ("-∞", "-inf", "-infty"):
        return float("-inf")
    try:
        return float(t)
    except ValueError:
        return None
