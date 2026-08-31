from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from masim.integrations.event_process import canonical_sha256

from h2epr.scenarios.cross_event_conformance_v0_2 import (
    RELEASE_PATH,
    CrossEventConformanceCode,
    CrossEventConformanceError,
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
    with pytest.raises(TypeError):
        admission.conformance_document["status"] = "forged"


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


def test_three_event_admission_rejects_integrity_and_coordinated_drift(
    tmp_path: Path,
) -> None:
    project_copy = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, project_copy)
    release = project_copy / RELEASE_PATH
    checksum_path = release / "SHA256SUMS"
    original_checksums = checksum_path.read_text(encoding="utf-8")
    checksum_path.write_text(
        ("0" if original_checksums[0] != "0" else "1")
        + original_checksums[1:],
        encoding="utf-8",
    )
    with pytest.raises(CrossEventConformanceError) as checksum_raised:
        load_cross_event_conformance_release(
            release,
            project_root=project_copy,
        )
    assert checksum_raised.value.code is (
        CrossEventConformanceCode.CHECKSUM_MISMATCH
    )
    checksum_path.write_text(original_checksums, encoding="utf-8")

    conformance_path = release / "conformance.json"
    forged = json.loads(conformance_path.read_text(encoding="utf-8"))
    forged["events"][2]["full_roster_coverage"]["actors_operated"] = 9
    conformance_path.write_text(
        json.dumps(forged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_path = release / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["conformance_artifact"].update(
        {
            "source_sha256": _sha256(conformance_path),
            "canonical_sha256": canonical_sha256(forged),
            "byte_count": conformance_path.stat().st_size,
        }
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    names = (
        "manifest.json",
        "README.md",
        "conformance.json",
        "substantive-review.md",
    )
    checksum_path.write_text(
        "".join(f"{_sha256(release / name)}  {name}\n" for name in names),
        encoding="utf-8",
    )
    with pytest.raises(CrossEventConformanceError) as drift_raised:
        load_cross_event_conformance_release(
            release,
            project_root=project_copy,
        )
    assert drift_raised.value.code is (
        CrossEventConformanceCode.CONFORMANCE_MISMATCH
    )
