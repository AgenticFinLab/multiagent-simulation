"""Repository-level integrity checks for formal H2EPR assets."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


H2EPR_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PUBLICATION_ENTRY_POINTS = (
    "README.md",
    "projects/README.md",
    "projects/H2EPR.md",
    "docs/structure.md",
    "docs/development-environment.md",
)
CHECKSUM_LINE = re.compile(r"^([0-9a-f]{64}) ([ *])(.+)$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
GENERATED_DIRECTORY_NAMES = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
}


def _repository_paths(*pathspecs: str) -> tuple[Path, ...]:
    """Return source paths while excluding generated local directories."""

    paths: set[Path] = set()
    for pathspec in pathspecs:
        source = REPOSITORY_ROOT / pathspec
        if not source.exists():
            raise AssertionError(f"publication surface is missing: {pathspec}")
        candidates = (source,) if source.is_file() else source.rglob("*")
        for path in candidates:
            relative = path.relative_to(REPOSITORY_ROOT)
            if any(
                part in GENERATED_DIRECTORY_NAMES or part.endswith(".egg-info")
                for part in relative.parts
            ):
                continue
            if not path.is_file():
                continue
            candidate = path.resolve()
            if not candidate.is_relative_to(REPOSITORY_ROOT):
                raise AssertionError(f"repository path escapes root: {relative}")
            paths.add(candidate)
    return tuple(sorted(paths))


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _markdown_destination(raw_destination: str) -> str:
    destination = raw_destination.strip()
    if destination.startswith("<"):
        closing = destination.find(">")
        if closing == -1:
            return destination
        destination = destination[1:closing]
    else:
        destination = destination.split(maxsplit=1)[0]
    return _percent_decode(destination)


def _percent_decode(value: str) -> str:
    encoded = bytearray()
    index = 0
    while index < len(value):
        hex_pair = value[index + 1 : index + 3]
        if (
            value[index] == "%"
            and len(hex_pair) == 2
            and all(character in "0123456789abcdefABCDEF" for character in hex_pair)
        ):
            encoded.append(int(hex_pair, 16))
            index += 3
        else:
            encoded.extend(value[index].encode("utf-8"))
            index += 1
    return encoded.decode("utf-8")


def test_formal_json_is_strictly_parseable() -> None:
    formal_json = tuple(
        path
        for path in _repository_paths("projects/h2epr")
        if path.suffix == ".json"
        and path.relative_to(H2EPR_ROOT).parts[0] != "tests"
    )
    assert formal_json, "no formal H2EPR JSON discovered"

    failures: list[str] = []
    for path in formal_json:
        try:
            json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_constant,
            )
        except (OSError, UnicodeError, ValueError) as error:
            failures.append(f"{path.relative_to(REPOSITORY_ROOT)}: {error}")
    assert not failures, "formal JSON failures:\n" + "\n".join(failures)


def test_release_checksum_inventories_resolve_and_match() -> None:
    inventories = tuple(
        path
        for path in _repository_paths("projects/h2epr")
        if path.name == "SHA256SUMS"
    )
    assert inventories, "no H2EPR checksum inventories discovered"

    failures: list[str] = []
    for inventory in inventories:
        root = inventory.parent.resolve()
        seen: set[str] = set()
        rows = inventory.read_text(encoding="utf-8").splitlines()
        if not rows:
            failures.append(f"{inventory.relative_to(REPOSITORY_ROOT)}: empty")
            continue
        for line_number, row in enumerate(rows, start=1):
            match = CHECKSUM_LINE.fullmatch(row)
            if match is None:
                failures.append(
                    f"{inventory.relative_to(REPOSITORY_ROOT)}:{line_number}: "
                    "invalid sha256sum row"
                )
                continue
            expected, _, filename = match.groups()
            if filename in seen:
                failures.append(
                    f"{inventory.relative_to(REPOSITORY_ROOT)}:{line_number}: "
                    f"duplicate target {filename}"
                )
                continue
            seen.add(filename)
            target = (root / filename).resolve()
            if not target.is_relative_to(root):
                failures.append(
                    f"{inventory.relative_to(REPOSITORY_ROOT)}:{line_number}: "
                    f"target escapes release directory: {filename}"
                )
            elif not target.is_file():
                failures.append(
                    f"{inventory.relative_to(REPOSITORY_ROOT)}:{line_number}: "
                    f"missing target {filename}"
                )
            elif _sha256(target) != expected:
                failures.append(
                    f"{inventory.relative_to(REPOSITORY_ROOT)}:{line_number}: "
                    f"checksum mismatch for {filename}"
                )
    assert not failures, "checksum inventory failures:\n" + "\n".join(failures)


def test_publication_surface_local_links_resolve() -> None:
    markdown_paths = tuple(
        path
        for path in _repository_paths("projects/h2epr", *PUBLICATION_ENTRY_POINTS)
        if path.suffix == ".md"
    )
    assert markdown_paths, "no H2EPR publication Markdown discovered"

    failures: list[str] = []
    for document in markdown_paths:
        text = document.read_text(encoding="utf-8")
        for raw_destination in MARKDOWN_LINK.findall(text):
            destination = _markdown_destination(raw_destination)
            if (
                not destination
                or destination.startswith("#")
                or destination.startswith("//")
                or URI_SCHEME.match(destination)
            ):
                continue
            local_part = destination.split("#", 1)[0].split("?", 1)[0]
            if not local_part:
                continue
            if local_part.startswith("/"):
                target = (REPOSITORY_ROOT / local_part.lstrip("/")).resolve()
            else:
                target = (document.parent / local_part).resolve()
            if not target.is_relative_to(REPOSITORY_ROOT):
                failures.append(
                    f"{document.relative_to(REPOSITORY_ROOT)}: "
                    f"link escapes repository: {destination}"
                )
            elif not target.exists():
                failures.append(
                    f"{document.relative_to(REPOSITORY_ROOT)}: "
                    f"missing link target: {destination}"
                )
    assert not failures, "publication link failures:\n" + "\n".join(failures)
