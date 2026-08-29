from __future__ import annotations

import hashlib
import json
from pathlib import Path

from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    build_singhealth_policy_realization_document,
    load_singhealth_policy_realization,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = (
    PROJECT_ROOT
    / "execution/singhealth_data_breach/policy-realization-v0.1"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_singhealth_policy_realization_release_is_strictly_admitted() -> None:
    manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    realization = manifest["realization"]

    admission = load_singhealth_policy_realization(
        RELEASE_ROOT / realization["path"],
        project_root=PROJECT_ROOT,
        expected_source_sha256=realization["source_sha256"],
    )

    assert admission.accepted is True
    assert admission.canonical_sha256 == realization["canonical_sha256"]
    assert admission.schema_sha256 == realization["schema_sha256"]
    assert manifest["coverage"]["registered_implementations"] == 29


def test_singhealth_policy_realization_is_reproducible() -> None:
    released = json.loads(
        (RELEASE_ROOT / "policy-realization.json").read_text(encoding="utf-8")
    )

    assert released == build_singhealth_policy_realization_document(
        project_root=PROJECT_ROOT
    )


def test_singhealth_policy_manifest_and_checksums_close() -> None:
    manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    for artifact in manifest["artifacts"]:
        assert _sha256(RELEASE_ROOT / artifact["path"]) == artifact["sha256"]
    for source in manifest["implementation_sources"]:
        assert _sha256(PROJECT_ROOT / source["path"]) == source["sha256"]

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
        "policy-realization.json",
        "substantive-review.md",
    }
    for name, digest in rows.items():
        assert _sha256(RELEASE_ROOT / name) == digest
