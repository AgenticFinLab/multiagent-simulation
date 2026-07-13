#!/usr/bin/env python3
"""Structural conformance audit for AGENT_POOL profiles against
`masim/skills/agent-design-skill.md` §2 (canonical section order),
§3 (section-by-section requirements), and §6 (Validation Checklist).

Read-only. Prints a structured report. Exit code = number of profiles
with at least one FAIL (0 = all scanned profiles are structurally
conformant).

Invocation modes (backing the Contract Polish Hook 5 in
`masim/skills/implement-simulation-skill/06-step2-agent-design.md`):

    # Repo-wide sweep (all domains, all profiles)
    python scripts/audit_agent_handbook.py

    # Single domain
    python scripts/audit_agent_handbook.py --domain finance

    # Single profile
    python scripts/audit_agent_handbook.py --profile examples/AGENT_POOL/finance/disposition-investor.md

    # Restrict to a single check family
    python scripts/audit_agent_handbook.py --check sections   # §2 canonical order
    python scripts/audit_agent_handbook.py --check summary    # §3.2
    python scripts/audit_agent_handbook.py --check theory     # §3.4
    python scripts/audit_agent_handbook.py --check purpose    # §3.5
    python scripts/audit_agent_handbook.py --check behavior   # §3.6
    python scripts/audit_agent_handbook.py --check io         # §3.6.0 I/O Contract
    python scripts/audit_agent_handbook.py --check params     # §3.7
    python scripts/audit_agent_handbook.py --check examples   # §3.8
    python scripts/audit_agent_handbook.py --check verify     # §3.9
    python scripts/audit_agent_handbook.py --check refs       # §3.10
    python scripts/audit_agent_handbook.py --check provenance # §3.11
    python scripts/audit_agent_handbook.py --check all        # (default)

Exit code = number of profiles with at least one FAIL under the
selected check family.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_POOL = ROOT / "examples" / "AGENT_POOL"

# §2 canonical top-level section headers (exact text, in order).
# The handbook mandates these 11 sections, in this order.
# Patterns use inline (?m) so they work whether passed as raw strings
# or compiled via re.compile() without flags.
# An optional numeric prefix (e.g. `## 1 Summary`, `## 3.4 Theoretical
# Foundation`) is tolerated — many existing profiles number their sections.
_NUM = r"(?:\d+(?:\.\d+)*\s+)?"
CANONICAL_SECTIONS: list[tuple[str, str]] = [
    ("title",            r"(?m)^#\s+.+"),                                  # §3.1 H1
    ("summary",          r"(?m)^##\s+" + _NUM + r"Summary\s*$"),           # §3.2
    ("definition",       r"(?m)^##\s+" + _NUM + r"Definition and Goals\s*$"),  # §3.3
    ("theory",           r"(?m)^##\s+" + _NUM + r"Theoretical Foundation\s*$"),  # §3.4
    ("purpose",          r"(?m)^##\s+" + _NUM + r"Design Purpose and Activation Triggers\s*$"),  # §3.5
    ("behavior",         r"(?m)^##\s+" + _NUM + r"Behavioral Framework\s*$"),  # §3.6
    ("params",           r"(?m)^##\s+" + _NUM + r"Parameters\s*$"),        # §3.7
    ("examples",         r"(?m)^##\s+" + _NUM + r"Worked Numerical Examples?\s*$"),  # §3.8
    ("verify",           r"(?m)^##\s+" + _NUM + r"(?:Behavioral )?(?:Validation|Verification) and Calibration\s*$"),  # §3.9 (accepts Validation/Verification, with or without Behavioral prefix)
    ("refs",             r"(?m)^##\s+" + _NUM + r"Academic References\s*$"),  # §3.10
    ("provenance",       r"(?m)^##\s+" + _NUM + r"Design Provenance(?: and Versioning)?\s*$"),  # §3.11
]

# §3.6 required H4 sub-blocks (handbook §3.6 mandates >=6, in this order).
REQUIRED_H4: list[tuple[str, re.Pattern]] = [
    ("io_contract",       re.compile(r"(?m)^#{3,4}\s+.*I/O Contract")),
    ("info_set",          re.compile(r"(?m)^#{3,4}\s+.*Decision Information Set")),
    ("mechanism",         re.compile(r"(?m)^#{3,4}\s+.*Core Behavioral Mechanism")),
    ("action_space",      re.compile(r"(?m)^#{3,4}\s+.*Action Space")),
    ("math_model",        re.compile(r"(?m)^#{3,4}\s+.*Mathematical Model")),
    ("behavioral_props",  re.compile(r"(?m)^#{3,4}\s+.*Behavioral Properties")),
]

# §3.2 Summary required row labels (handbook §3.2 minimum 7 rows).
SUMMARY_REQUIRED_ROWS = [
    "Archetype", "Theory Family", "Behavioral Tendency",
    "Time Horizon", "Risk Tolerance", "Information Asymmetry", "Determinism",
]

# §3.4 Theoretical Foundation required labelled lines (handbook §3.4 depth rules).
THEORY_REQUIRED_LINES = [
    "Theory / Study", "Citation", "Core Insight", "Mathematical Formulation",
    "Empirical Evidence", "Relevance to This Agent", "Calibration Source",
    "Falsification Conditions", "Alternative Theories",
]

# §3.5 Design Purpose required fields (handbook §3.5 eight fields).
PURPOSE_REQUIRED_FIELDS = [
    "Purpose", "Call Frequency", "Prerequisite Signals",
    "Missing-Signal Policy", "Activation Triggers", "Deactivation Conditions",
    "Behavioral Adaptation by Condition", "Environmental Dependencies",
]

# §3.6.0 I/O Contract required blocks (handbook §3.6.0 five required blocks).
IO_REQUIRED_BLOCKS = [
    ("inputs",        re.compile(r"#####?\s+Inputs\s*\(per decision call\)", re.MULTILINE | re.IGNORECASE)),
    ("outputs",       re.compile(r"#####?\s+Outputs\s*\(per decision call\)", re.MULTILINE | re.IGNORECASE)),
    ("constraints",   re.compile(r"#####?\s+Content Constraints", re.MULTILINE | re.IGNORECASE)),
    ("serialization", re.compile(r"#####?\s+Serialization Format", re.MULTILINE | re.IGNORECASE)),
    ("reminder",      re.compile(r"#####?\s+Implementer Contract Reminder", re.MULTILINE | re.IGNORECASE)),
]

# §3.7 Parameters canonical 8 columns (handbook §3.7).
PARAMS_CANONICAL_COLUMNS = [
    "Parameter", "Type", "Default", "Valid Range",
    "Sensitivity", "Description", "Impact", "Source",
]

# §3.11 Design Provenance required rows (handbook §3.11).
PROVENANCE_REQUIRED_ROWS = [
    "Author", "Created", "Version", "Change log", "Status",
]

# Placeholder / stub markers that indicate incomplete authoring.
# Any match on a non-code-fence line is a FAIL. The polish pipeline treats
# any TODO / placeholder as a blocking defect — conformant profiles must
# be fully authored.
PLACEHOLDER_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("TODO",        re.compile(r"(?m)^[^`\n]*\bTODO\b")),
    ("TBD",         re.compile(r"(?m)^[^`\n]*\bTBD\b")),
    ("FIXME",       re.compile(r"(?m)^[^`\n]*\bFIXME\b")),
    ("XXX",         re.compile(r"(?m)^[^`\n]*\bXXX\b")),
    ("PLACEHOLDER", re.compile(r"(?m)^[^`\n]*\bPLACEHOLDER\b")),
    ("stub status", re.compile(r"(?mi)^\|\s*Status\s*\|\s*stub\s*\|")),
    ("stub marker", re.compile(r"(?mi)^>\s*Status:\s*stub\b")),
    ("auto-generated placeholder",
                    re.compile(r"(?mi)auto-generated placeholder")),
    ("fill this",   re.compile(r"(?mi)\bfill\s+(this|the)\s+.*\s+(section|field|row|block)\b")),
    ("insert here", re.compile(r"(?mi)\binsert\s+.*\s+here\b")),
]

CHECK_FAMILIES = (
    "sections", "summary", "theory", "purpose", "behavior", "io",
    "params", "examples", "verify", "refs", "provenance", "todo", "all",
)


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------

def load_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def find_section(text: str, pattern: re.Pattern) -> tuple[int, int] | None:
    """Return (start, end) character offsets of the section whose H2 matches
    `pattern`, where `end` is the start of the next same-or-higher-level
    heading (or EOF). Returns None if not found."""
    m = pattern.search(text)
    if not m:
        return None
    start = m.start()
    # Find next H1/H2 after this match.
    next_heading = re.search(r"(?m)^#{1,2}\s+\S", text[m.end():])
    end = m.end() + next_heading.start() if next_heading else len(text)
    return start, end


def count_table_rows(block: str) -> int:
    """Count data rows in a markdown table (excludes header + separator)."""
    rows = 0
    in_table = False
    seen_sep = False
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            if not in_table:
                in_table = True
                seen_sep = False
                continue
            # separator line: |---|---|
            if re.fullmatch(r"\|[\s\-:|]+\|", s):
                seen_sep = True
                continue
            if seen_sep:
                rows += 1
        else:
            in_table = False
            seen_sep = False
    return rows


def first_table_column_count(block: str) -> int | None:
    """Return the column count of the first table found in `block`, or None."""
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            return len(cells)
    return None


def extract_table_first_column_values(block: str) -> list[str]:
    """Return the first-column cell values of every data row in the first
    table found in `block` (skips header and separator rows)."""
    values: list[str] = []
    in_table = False
    seen_sep = False
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            if not in_table:
                # header row — skip
                in_table = True
                seen_sep = False
                continue
            if re.fullmatch(r"\|[\s\-:|]+\|", s):
                seen_sep = True
                continue
            if seen_sep:
                cells = [c.strip() for c in s.strip("|").split("|")]
                if cells:
                    values.append(cells[0])
        else:
            in_table = False
            seen_sep = False
    return values


def count_h4_blocks(text: str, pattern: re.Pattern) -> int:
    return len(pattern.findall(text))


def count_cases(block: str) -> tuple[int, bool]:
    """Count worked-example cases and detect an edge case. A case is any
    H3 or H4 heading whose title starts with `Case` or `Edge Case`
    (case-insensitive)."""
    cases = 0
    has_edge = False
    for m in re.finditer(r"^#{3,4}\s+(.+?)\s*$", block, re.MULTILINE):
        title = m.group(1).strip()
        tl = title.lower()
        if tl.startswith("edge case") or tl.startswith("edge-case"):
            has_edge = True
            cases += 1
        elif tl.startswith("case"):
            cases += 1
    return cases, has_edge


# ---------------------------------------------------------------------------
# Per-check implementations. Each returns a list of (severity, message)
# tuples. severity ∈ {"FAIL", "WARN"}.
# ---------------------------------------------------------------------------

@dataclass
class Findings:
    items: list[tuple[str, str]] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.items.append(("FAIL", msg))

    def warn(self, msg: str) -> None:
        self.items.append(("WARN", msg))

    @property
    def fail_count(self) -> int:
        return sum(1 for s, _ in self.items if s == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for s, _ in self.items if s == "WARN")


def check_sections(text: str) -> Findings:
    f = Findings()
    found: list[str] = []
    for key, pat in CANONICAL_SECTIONS:
        if re.search(pat, text, re.MULTILINE):
            found.append(key)
        else:
            f.fail(f"missing required §3 section: {key}")
    # Order check: every found section must appear in canonical order.
    positions: list[tuple[int, str]] = []
    for key, pat in CANONICAL_SECTIONS:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            positions.append((m.start(), key))
    positions.sort()
    order = [k for _, k in positions]
    if order != found:
        f.fail(f"section order mismatch: found {order}, expected {found}")
    # H1 title check: must be sentence-cased role phrase, not code.
    h1 = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if h1:
        title = h1.group(1).strip()
        if re.search(r"[A-Z][a-z]+[A-Z]", title):  # CamelCase identifier
            f.warn(f"H1 looks like a code identifier: '{title}'")
    else:
        f.fail("no H1 title found (§3.1)")
    return f


def check_summary(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[1][1]))
    if not span:
        f.fail("§3.2 Summary section missing")
        return f
    block = text[span[0]:span[1]]
    rows = count_table_rows(block)
    if rows < 7:
        f.fail(f"§3.2 Summary has {rows} rows; minimum is 7")
    first_col = extract_table_first_column_values(block)
    first_col_lower = [c.lower() for c in first_col]
    for req in SUMMARY_REQUIRED_ROWS:
        if req.lower() not in first_col_lower:
            f.fail(f"§3.2 missing required row label: '{req}'")
    return f


def check_theory(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[3][1]))
    if not span:
        f.fail("§3.4 Theoretical Foundation section missing")
        return f
    block = text[span[0]:span[1]]
    # Count theory sub-blocks: lines starting with **<Name>**: or **<Name>** —
    # (handbook shows the colon form; many existing profiles use an em-dash
    # or en-dash separator, which is also accepted).
    sub_blocks = re.findall(
        r"^\*\*([^*]+)\*\*\s*(?:[:\-—–])", block, re.MULTILINE
    )
    if len(sub_blocks) < 1:
        f.fail("§3.4 has 0 theory sub-blocks; minimum is 1")
    # For each sub-block, check the 9 labelled lines.
    # Split block by sub-block headers.
    parts = re.split(r"(?m)^\*\*[^*]+\*\*\s*[:\-—–]", block)[1:]  # skip preamble
    for i, (name, part) in enumerate(zip(sub_blocks, parts), start=1):
        present_lines = 0
        for req in THEORY_REQUIRED_LINES:
            if re.search(re.escape(req), part, re.IGNORECASE):
                present_lines += 1
            else:
                f.fail(f"§3.4 sub-block #{i} '{name}' missing labelled line: '{req}'")
        # Mathematical Formulation must not be placeholder.
        mf_match = re.search(
            r"Mathematical Formulation\s*:\s*(.+?)(?:\n|$)", part, re.IGNORECASE
        )
        if mf_match:
            val = mf_match.group(1).strip()
            if val.lower() in {"complex model", "tbd", "todo", "n/a", ""}:
                f.fail(f"§3.4 sub-block #{i} 'Mathematical Formulation' is a placeholder")
    return f


def check_purpose(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[4][1]))
    if not span:
        f.fail("§3.5 Design Purpose and Activation Triggers section missing")
        return f
    block = text[span[0]:span[1]]
    # Check each of the 8 required fields.
    for req in PURPOSE_REQUIRED_FIELDS:
        if not re.search(re.escape(req), block, re.IGNORECASE):
            f.fail(f"§3.5 missing required field: '{req}'")
    # Behavioral Adaptation table must have >=2 rows.
    adapt_match = re.search(
        r"Behavioral Adaptation by Condition\s*\n(.*?)(?:\n\s*\n|\Z)",
        block, re.IGNORECASE | re.DOTALL,
    )
    if adapt_match:
        adapt_block = adapt_match.group(1)
        adapt_rows = count_table_rows(adapt_block)
        if adapt_rows < 2:
            f.fail(f"§3.5 Behavioral Adaptation table has {adapt_rows} rows; minimum is 2")
    return f


def check_behavior(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[5][1]))
    if not span:
        f.fail("§3.6 Behavioral Framework section missing")
        return f
    block = text[span[0]:span[1]]
    for key, pat in REQUIRED_H4:
        if not pat.search(block):
            f.fail(f"§3.6 missing required H4 sub-block: {key}")
    # §3.6.2 Core Behavioral Mechanism must have 5–10 numbered steps.
    mech_span = None
    mech_pat = re.compile(r"^#{3,4}\s+.*Core Behavioral Mechanism", re.MULTILINE)
    m = mech_pat.search(block)
    if m:
        start = m.end()
        # Find next H4 or end of block.
        next_h4 = re.search(r"(?m)^#{3,4}\s+\S", block[start:])
        end = start + next_h4.start() if next_h4 else len(block)
        mech_span = (start, end)
    if mech_span:
        mech_block = block[mech_span[0]:mech_span[1]]
        steps = re.findall(r"^\s*\d+[.)]\s+\S", mech_block, re.MULTILINE)
        n = len(steps)
        if n < 5:
            f.fail(f"§3.6.2 Core Behavioral Mechanism has {n} numbered steps; minimum is 5")
        elif n > 10:
            f.warn(f"§3.6.2 Core Behavioral Mechanism has {n} steps; handbook recommends <=10")
    return f


def check_io(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[5][1]))
    if not span:
        f.fail("§3.6 Behavioral Framework section missing (needed for §3.6.0 I/O Contract)")
        return f
    block = text[span[0]:span[1]]
    for key, pat in IO_REQUIRED_BLOCKS:
        if not pat.search(block):
            f.fail(f"§3.6.0 I/O Contract missing required block: {key}")
    # Serialization Format must declare the literal <analysis>/<decision> tag pattern.
    if re.search(r"Serialization Format", block, re.IGNORECASE):
        ser_span = find_section(
            block, re.compile(r"#####?\s+Serialization Format", re.IGNORECASE)
        )
        if ser_span:
            ser_block = block[ser_span[0]:ser_span[1]]
            if "<analysis>" not in ser_block or "<decision>" not in ser_block:
                f.fail("§3.6.0 Serialization Format does not declare <analysis>/<decision> tag pattern")
    return f


def check_params(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[6][1]))
    if not span:
        f.fail("§3.7 Parameters section missing")
        return f
    block = text[span[0]:span[1]]
    rows = count_table_rows(block)
    if rows < 3:
        f.fail(f"§3.7 has {rows} parameter rows; minimum is 3 (or explicit justification)")
    cols = first_table_column_count(block)
    if cols is not None and cols < 8:
        f.fail(f"§3.7 table has {cols} columns; canonical is 8 ({', '.join(PARAMS_CANONICAL_COLUMNS)})")
    return f


def check_examples(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[7][1]))
    if not span:
        f.fail("§3.8 Worked Numerical Examples section missing")
        return f
    block = text[span[0]:span[1]]
    cases, has_edge = count_cases(block)
    if cases < 3:
        f.fail(f"§3.8 has {cases} worked cases; minimum is 3 primary cases + 1 edge case")
    if not has_edge:
        f.fail("§3.8 has no edge case (handbook §3.8 requires >=1 edge case)")
    return f


def check_verify(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[8][1]))
    if not span:
        f.fail("§3.9 Behavioral Verification and Calibration section missing")
        return f
    block = text[span[0]:span[1]]
    # At least 3 sanity bounds as IF-THEN / IF ... THEN ...
    if_then = re.findall(r"\bIF\b.*\bTHEN\b", block, re.IGNORECASE)
    if len(if_then) < 3:
        f.fail(f"§3.9 has {len(if_then)} IF-THEN sanity bounds; minimum is 3")
    # §3.9.1 Ablation Hooks table
    if not re.search(r"Ablation", block, re.IGNORECASE):
        f.fail("§3.9 missing Ablation Hooks sub-block")
    return f


def check_refs(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[9][1]))
    if not span:
        f.fail("§3.10 Academic References section missing")
        return f
    block = text[span[0]:span[1]]
    rows = count_table_rows(block)
    if rows < 1:
        f.fail("§3.10 Academic References table has 0 rows; must list every citation in the spec")
    return f


def check_provenance(text: str) -> Findings:
    f = Findings()
    span = find_section(text, re.compile(CANONICAL_SECTIONS[10][1]))
    if not span:
        f.fail("§3.11 Design Provenance section missing")
        return f
    block = text[span[0]:span[1]]
    first_col = extract_table_first_column_values(block)
    first_col_lower = [c.lower() for c in first_col]
    for req in PROVENANCE_REQUIRED_ROWS:
        if req.lower() not in first_col_lower:
            f.fail(f"§3.11 missing required row: '{req}'")
    return f


def check_todo(text: str) -> Findings:
    """Scan the whole profile for placeholder / TODO markers.

    Lines inside fenced code blocks (``` ... ```) are excluded, because
    worked-example cases sometimes show literal placeholder tokens as
    part of the demonstration. Everything outside a code fence that
    matches any PLACEHOLDER_PATTERNS is a FAIL.
    """
    f = Findings()
    in_fence = False
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for label, pat in PLACEHOLDER_PATTERNS:
            if pat.search(raw):
                snippet = raw.strip()[:80]
                f.fail(f"placeholder marker [{label}] at line {line_no}: {snippet!r}")
    return f


CHECK_DISPATCH = {
    "sections":   check_sections,
    "summary":    check_summary,
    "theory":     check_theory,
    "purpose":    check_purpose,
    "behavior":   check_behavior,
    "io":         check_io,
    "params":     check_params,
    "examples":   check_examples,
    "verify":     check_verify,
    "refs":       check_refs,
    "provenance": check_provenance,
    "todo":       check_todo,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Structural conformance audit for AGENT_POOL profiles against "
            "agent-design-skill.md §2/§3/§6. Backs Polish Hook 5 in "
            "implement-simulation-skill/06-step2-agent-design.md."
        )
    )
    p.add_argument("--domain", default=None,
                   help="Restrict to one domain folder under examples/AGENT_POOL/.")
    p.add_argument("--profile", default=None,
                   help="Restrict to a single profile .md path (absolute or repo-relative).")
    p.add_argument("--check", default="all", choices=CHECK_FAMILIES,
                   help="Restrict the report and exit-code contribution to one check family.")
    p.add_argument("--max-profiles", type=int, default=0,
                   help="Stop after scanning N profiles (0 = unlimited). Useful for triage.")
    p.add_argument("--fail-fast", action="store_true",
                   help="Stop at the first profile with any FAIL.")
    return p.parse_args(argv)


def iter_profiles(args: argparse.Namespace) -> list[Path]:
    if args.profile:
        path = Path(args.profile)
        if not path.is_absolute():
            path = ROOT / path
        return [path] if path.is_file() else []
    base = AGENT_POOL
    if args.domain:
        base = base / args.domain
        if not base.is_dir():
            return []
        return sorted(p for p in base.glob("*.md") if p.is_file())
    # No --domain: walk every domain sub-folder that contains .md profiles.
    # Skip non-folder entries (e.g. README.md) and the agent_images tree.
    out: list[Path] = []
    for child in sorted(AGENT_POOL.iterdir()):
        if not child.is_dir():
            continue
        if child.name in {"agent_images", "icons"}:
            continue
        out.extend(sorted(p for p in child.glob("*.md") if p.is_file()))
    return out


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    profiles = iter_profiles(args)
    if not profiles:
        print("ERROR: no profiles matched the given filters.", file=sys.stderr)
        return 2

    want = {c: (args.check in ("all", c)) for c in CHECK_FAMILIES if c != "all"}

    total = 0
    profiles_with_fail = 0
    profiles_with_warn = 0
    per_profile: list[tuple[Path, Findings]] = []

    for path in profiles:
        if 0 < args.max_profiles <= total:
            break
        total += 1
        text = load_text(path)
        if not text:
            agg = Findings()
            agg.fail(f"could not read file: {path}")
            per_profile.append((path, agg))
            profiles_with_fail += 1
            if args.fail_fast:
                break
            continue
        agg = Findings()
        for key, fn in CHECK_DISPATCH.items():
            if not want[key]:
                continue
            sub = fn(text)
            for sev, msg in sub.items:
                agg.items.append((sev, f"[{key}] {msg}"))
        per_profile.append((path, agg))
        if agg.fail_count > 0:
            profiles_with_fail += 1
            if args.fail_fast:
                break
        if agg.warn_count > 0:
            profiles_with_warn += 1

    # ==================== REPORT ====================
    print("=" * 78)
    print("AGENT HANDBOOK STRUCTURAL CONFORMANCE AUDIT")
    print("=" * 78)
    print(f"Profiles scanned       : {total}")
    print(f"Check family           : {args.check}")
    print(f"Profiles with FAIL     : {profiles_with_fail}")
    print(f"Profiles with WARN only: {profiles_with_warn}")
    print()

    # Summary table first.
    print(f"{'Profile':<50} {'FAIL':>5} {'WARN':>5}")
    print("-" * 62)
    for path, findings in per_profile:
        rel = path.relative_to(ROOT) if str(path).startswith(str(ROOT)) else path
        rel_s = str(rel)
        if len(rel_s) > 48:
            rel_s = "…" + rel_s[-47:]
        print(f"{rel_s:<50} {findings.fail_count:>5} {findings.warn_count:>5}")
    print()

    # Detailed findings for failing profiles.
    for path, findings in per_profile:
        if not findings.items:
            continue
        rel = path.relative_to(ROOT) if str(path).startswith(str(ROOT)) else path
        print("-" * 78)
        print(f"  {rel}")
        print("-" * 78)
        for sev, msg in findings.items:
            print(f"    [{sev}] {msg}")
        print()

    print("=" * 78)
    print(f"TOTAL PROFILES WITH ISSUES (check={args.check}): "
          f"{profiles_with_fail} FAIL, {profiles_with_warn} WARN-only")
    print("=" * 78)
    return 0 if profiles_with_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
