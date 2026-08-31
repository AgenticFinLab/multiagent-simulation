from __future__ import annotations

import hashlib
import json
from pathlib import Path

from h2epr.scenarios.cross_event_conformance_v0_2 import (
    build_cross_event_conformance,
    build_cross_event_release_manifest,
    load_cross_event_conformance_release,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = PROJECT_ROOT / "execution/cross-event-conformance-v0.2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_three_event_conformance_rebuilds_exactly() -> None:
    released = json.loads(
        (RELEASE_ROOT / "conformance.json").read_text(encoding="utf-8")
    )
    rebuilt = build_cross_event_conformance(project_root=PROJECT_ROOT)
    assert released == rebuilt
    assert [row["event_id"] for row in rebuilt["events"]] == [
        "H2EPR-0288",
        "H2EPR-0616",
        "H2EPR-0481",
    ]
    assert all(rebuilt["verified_properties"].values())


def test_three_event_release_manifest_and_admission_close() -> None:
    conformance = build_cross_event_conformance(project_root=PROJECT_ROOT)
    manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest == build_cross_event_release_manifest(
        conformance,
        project_root=PROJECT_ROOT,
    )
    admission = load_cross_event_conformance_release(
        RELEASE_ROOT,
        project_root=PROJECT_ROOT,
        expected_manifest_source_sha256=_sha256(
            RELEASE_ROOT / "manifest.json"
        ),
    )
    assert admission.accepted is True
    assert admission.event_ids == (
        "H2EPR-0288",
        "H2EPR-0616",
        "H2EPR-0481",
    )
    assert admission.compact_releases_closed is True
    assert admission.shared_contract_closed is True
    assert admission.event_specific_semantics_preserved is True


def test_three_event_checksum_inventory_closes() -> None:
    rows = {
        name: digest
        for digest, name in (
            line.split("  ", 1)
            for line in (RELEASE_ROOT / "SHA256SUMS")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    assert set(rows) == {
        "manifest.json",
        "README.md",
        "conformance.json",
        "substantive-review.md",
    }
    assert all(
        _sha256(RELEASE_ROOT / name) == digest
        for name, digest in rows.items()
    )
