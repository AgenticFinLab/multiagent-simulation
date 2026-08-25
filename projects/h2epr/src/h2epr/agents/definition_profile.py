"""Lightweight structural checks for new-format Agent Definition candidates.

The checker enforces the public ten-module reading profile and a few
machine-auditable inventory links. It deliberately does not judge evidence,
behavioral quality, historical validity, or runtime conformance.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Sequence


EXPECTED_MODULES = (
    "1. Model overview",
    "2. Historical participant and representation",
    "3. Evidence and theoretical foundation",
    "4. Institutional role and relationships",
    "5. Decision situations, information, and state",
    "6. Behavioral model",
    "7. Intent and result boundary",
    "8. Operationalization and uncertainty",
    "9. Worked cases and falsification",
    "10. Limitations and references",
)

REQUIRED_OVERVIEW_FIELDS = (
    "Historical participant",
    "Modeled role",
    "Event and interval",
    "Primary decision situations",
    "Decision cadence",
    "Decision form",
    "State authority",
    "Evidence use and explanatory scope",
)

_H1 = re.compile(r"^# (?!#)(?P<title>\S.*)$", re.MULTILINE)
_H2 = re.compile(r"^## (?!#)(?P<title>\S.*)$", re.MULTILINE)
_COMMITMENT_HEADING = re.compile(
    r"^#{3,4} `(?P<identity>DC-[A-Z][A-Z0-9]*-[0-9]+)`(?:\s|$)",
    re.MULTILINE,
)
_COMMITMENT_REFERENCE = re.compile(r"\bDC-[A-Z][A-Z0-9]*-[0-9]+\b")
_SEMANTIC_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_CODE_SPAN = re.compile(r"`([^`]+)`")
_INTENT_LABEL = re.compile(
    r"\*\*(?:Permitted\s+intents?|Intents?)\.\*\*(?P<value>.*?)(?=\n\n\*\*|\n#{2,4} |\Z)",
    re.DOTALL,
)

_PUBLICATION_SURFACE_RULES = (
    (
        "project_identity_metadata",
        re.compile(
            r"^\|\s*(?:Definition identity|Model identity|Agent identity|"
            r"Definition ID|Model ID|Semantic version|Identity, version, and status)\s*\||"
            r"^(?:Version|Semantic version)\s+`?\d+\.\d+(?:\.\d+)?`?(?![\w.])",
            re.MULTILINE | re.IGNORECASE,
        ),
        "move stable IDs and semantic versions to a release or project manifest",
    ),
    (
        "workflow_status_metadata",
        re.compile(
            r"(?:FULL_DRAFT_EXPOSED|OUTCOME_EXPOSED|READY_FOR_REFERENCE_CANDIDATE|"
            r"MAPPING_EXTENSION_EXPECTED|KNOWN_FIT|CONCRETE_CARRIER_COUNTEREXAMPLE|"
            r"PASS_[A-Z0-9_]+)|^(?:Review )?Status\s*:|"
            r"^\|\s*(?:Evidence|Calibration|Model|Review|Release|Workflow|Publication)\s+status\s*\|",
            re.MULTILINE | re.IGNORECASE,
        ),
        "replace internal workflow labels with ordinary scholarly prose",
    ),
    (
        "project_provenance_metadata",
        re.compile(
            r"^#{3,4}\s+(?:Design )?Provenance\s*$|^Provenance:\s*$|"
            r"\b(?:Git|repository) commit\b|\bmethod baseline\b|\b[0-9a-f]{40}\b",
            re.MULTILINE | re.IGNORECASE,
        ),
        "keep Git identities, hashes, and method baselines in project provenance records",
    ),
    (
        "local_workflow_metadata",
        re.compile(
            r"\b(?:standard|deep) production profile\b|\bOD-[A-Z0-9-]+\b|"
            r"\bnon-executable\b",
            re.IGNORECASE,
        ),
        "remove local production depth, owner-decision, and executability labels",
    ),
    (
        "implementation_authorization_metadata",
        re.compile(
            r"(?:(?:does not|doesn't|cannot|not)[ \t]+(?:itself[ \t]+)?authorize[ \t]+"
            r"(?:mapping|configuration|policy|binding|runtime|simulation|implementation)|"
            r"authorizes?[ \t]+no[ \t]+(?:mapping|configuration|policy|binding|runtime|simulation|implementation))",
            re.IGNORECASE,
        ),
        "state the model boundary substantively instead of listing later phases it does not authorize",
    ),
    (
        "local_path_metadata",
        re.compile(r"(?:/home/[^\s`]+|\.local-runtime/[^\s`]+)"),
        "remove local filesystem paths from publication-facing artifacts",
    ),
)


@dataclass(frozen=True)
class DefinitionFormatIssue:
    """One deterministic structural-profile finding."""

    code: str
    detail: str


def check_publication_surface(text: str) -> tuple[DefinitionFormatIssue, ...]:
    """Reject project-only metadata from a publication-facing research text."""

    return tuple(
        DefinitionFormatIssue(code, detail)
        for code, pattern, detail in _PUBLICATION_SURFACE_RULES
        if pattern.search(text)
    )


def _cells(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


def _is_separator(row: tuple[str, ...]) -> bool:
    return bool(row) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)


def _tables(section: str) -> tuple[tuple[tuple[str, ...], ...], ...]:
    tables: list[tuple[tuple[str, ...], ...]] = []
    current: list[tuple[str, ...]] = []
    for line in section.splitlines() + [""]:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            current.append(_cells(line))
            continue
        if len(current) >= 2:
            tables.append(tuple(current))
        current = []
    return tuple(tables)


def _section(text: str, module: str) -> str:
    marker = f"## {module}"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def _first_column_inventory(
    section: str,
    *,
    header_word: str,
) -> tuple[tuple[str, str], ...]:
    """Return semantic ID and full row text for matching inventory tables."""

    entries: list[tuple[str, str]] = []
    for table in _tables(section):
        header = table[0]
        if not header or header_word.casefold() not in header[0].casefold():
            continue
        rows = table[2:] if len(table) > 1 and _is_separator(table[1]) else table[1:]
        for row in rows:
            if not row:
                continue
            candidates = [
                value
                for value in _CODE_SPAN.findall(row[0])
                if _SEMANTIC_ID.fullmatch(value)
            ]
            if len(candidates) == 1:
                entries.append((candidates[0], " | ".join(row)))
            else:
                entries.append(("", " | ".join(row)))
    return tuple(entries)


def _commitment_bodies(text: str) -> dict[str, str]:
    matches = tuple(_COMMITMENT_HEADING.finditer(text))
    bodies: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bodies[match.group("identity")] = text[match.end() : end]
    return bodies


def _permitted_intents(body: str) -> tuple[str, ...] | None:
    match = _INTENT_LABEL.search(body)
    if match:
        return tuple(
            value
            for value in _CODE_SPAN.findall(match.group("value"))
            if _SEMANTIC_ID.fullmatch(value)
        )

    for table in _tables(body):
        for row in table:
            if not row or row[0].casefold() != "permitted intents":
                continue
            return tuple(
                value
                for value in _CODE_SPAN.findall(" ".join(row[1:]))
                if _SEMANTIC_ID.fullmatch(value)
            )
    return None


def check_definition_text(text: str) -> tuple[DefinitionFormatIssue, ...]:
    """Check one new candidate against the lightweight public profile."""

    issues = list(check_publication_surface(text))

    titles = tuple(match.group("title") for match in _H1.finditer(text))
    if len(titles) != 1:
        issues.append(
            DefinitionFormatIssue("h1_cardinality", f"expected 1 H1, found {len(titles)}")
        )

    modules = tuple(match.group("title") for match in _H2.finditer(text))
    if modules != EXPECTED_MODULES:
        issues.append(
            DefinitionFormatIssue(
                "module_profile_mismatch",
                "expected exact ten-module order; found " + repr(modules),
            )
        )

    overview = _section(text, EXPECTED_MODULES[0])
    overview_rows = {
        row[0]: row[1:]
        for table in _tables(overview)
        for row in table
        if row and row[0] in REQUIRED_OVERVIEW_FIELDS
    }
    missing_fields = tuple(
        field for field in REQUIRED_OVERVIEW_FIELDS if field not in overview_rows
    )
    if missing_fields:
        issues.append(
            DefinitionFormatIssue(
                "overview_fields_missing", ", ".join(missing_fields)
            )
        )

    behavior = _section(text, EXPECTED_MODULES[5])
    commitment_matches = tuple(_COMMITMENT_HEADING.finditer(behavior))
    commitment_ids = tuple(match.group("identity") for match in commitment_matches)
    if not commitment_ids:
        issues.append(
            DefinitionFormatIssue("commitment_inventory_missing", "no Decision Commitment heading")
        )
    elif len(commitment_ids) != len(set(commitment_ids)):
        issues.append(
            DefinitionFormatIssue("commitment_identity_duplicate", repr(commitment_ids))
        )

    defined_commitments = set(commitment_ids)
    referenced_commitments = set(_COMMITMENT_REFERENCE.findall(text))
    dangling_commitments = sorted(referenced_commitments - defined_commitments)
    if dangling_commitments:
        issues.append(
            DefinitionFormatIssue(
                "commitment_reference_dangling", ", ".join(dangling_commitments)
            )
        )

    information = _section(text, EXPECTED_MODULES[4])
    observation_rows = _first_column_inventory(information, header_word="Observation")
    observation_ids = tuple(identity for identity, _ in observation_rows if identity)
    malformed_observations = sum(1 for identity, _ in observation_rows if not identity)
    if not observation_rows:
        issues.append(
            DefinitionFormatIssue(
                "observation_inventory_missing",
                "module 5 needs a table whose first header contains Observation",
            )
        )
    if malformed_observations:
        issues.append(
            DefinitionFormatIssue(
                "observation_identity_invalid",
                f"{malformed_observations} row(s) need one snake_case ID in the first cell",
            )
        )
    if len(observation_ids) != len(set(observation_ids)):
        issues.append(
            DefinitionFormatIssue("observation_identity_duplicate", repr(observation_ids))
        )
    for identity, row_text in observation_rows:
        has_collective_consumer = re.search(
            r"\b(?:all|every)\s+(?:substantive\s+)?commitments?\b",
            row_text,
            re.IGNORECASE,
        )
        if (
            identity
            and not _COMMITMENT_REFERENCE.search(row_text)
            and "contextual" not in row_text.casefold()
            and not has_collective_consumer
        ):
            issues.append(
                DefinitionFormatIssue(
                    "observation_consumer_missing",
                    f"{identity} needs a Decision Commitment consumer or explicit contextual label",
                )
            )

    intent_section = _section(text, EXPECTED_MODULES[6])
    intent_rows = _first_column_inventory(intent_section, header_word="Intent")
    intent_ids = tuple(identity for identity, _ in intent_rows if identity)
    malformed_intents = sum(1 for identity, _ in intent_rows if not identity)
    if not intent_rows:
        issues.append(
            DefinitionFormatIssue(
                "intent_inventory_missing",
                "module 7 needs a table whose first header contains Intent",
            )
        )
    if malformed_intents:
        issues.append(
            DefinitionFormatIssue(
                "intent_identity_invalid",
                f"{malformed_intents} row(s) need one snake_case ID in the first cell",
            )
        )
    if len(intent_ids) != len(set(intent_ids)):
        issues.append(DefinitionFormatIssue("intent_identity_duplicate", repr(intent_ids)))

    declared_intents = set(intent_ids)
    referenced_intents: set[str] = set()
    for commitment_id, body in _commitment_bodies(behavior).items():
        permitted = _permitted_intents(body)
        if permitted is None:
            issues.append(
                DefinitionFormatIssue(
                    "commitment_intent_link_missing",
                    f"{commitment_id} needs a Permitted intent(s) entry",
                )
            )
            continue
        if not permitted and not re.search(r"\b(?:abstention|no substantive intent)\b", body, re.IGNORECASE):
            issues.append(
                DefinitionFormatIssue(
                    "commitment_response_unspecified",
                    f"{commitment_id} declares neither an intent nor an explicit no-intent response",
                )
            )
        referenced_intents.update(permitted)

    unknown_intents = sorted(referenced_intents - declared_intents)
    if unknown_intents:
        issues.append(
            DefinitionFormatIssue("intent_reference_dangling", ", ".join(unknown_intents))
        )
    orphan_intents = sorted(declared_intents - referenced_intents)
    if orphan_intents:
        issues.append(
            DefinitionFormatIssue("intent_without_commitment", ", ".join(orphan_intents))
        )

    return tuple(issues)


def check_definition_file(path: str | Path) -> tuple[DefinitionFormatIssue, ...]:
    """Read and check one UTF-8 Definition candidate."""

    return check_definition_text(Path(path).read_text(encoding="utf-8"))


def _render(path: Path, issues: Iterable[DefinitionFormatIssue]) -> tuple[str, ...]:
    findings = tuple(issues)
    if not findings:
        return (f"PASS {path}",)
    return (f"FAIL {path}",) + tuple(
        f"  {issue.code}: {issue.detail}" for issue in findings
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for candidate authoring and review."""

    parser = argparse.ArgumentParser(
        description="Check new H2EPR Agent Definition candidates against the public format profile."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)

    failed = False
    for path in args.paths:
        try:
            issues = check_definition_file(path)
        except (OSError, UnicodeError) as exc:
            issues = (DefinitionFormatIssue("definition_unreadable", str(exc)),)
        for line in _render(path, issues):
            print(line)
        failed = failed or bool(issues)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
