from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from masim.integrations.event_process import canonical_sha256

from h2epr.scenarios.cross_event_conformance_v0_1 import (
    CONFORMANCE_ID,
    RELEASE_ID,
    RELEASE_PATH,
    RELEASE_STATUS,
    CrossEventConformanceCode,
    CrossEventConformanceError,
    build_cross_event_conformance,
    build_cross_event_release_manifest,
    load_cross_event_conformance_release,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = PROJECT_ROOT / RELEASE_PATH


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def conformance() -> dict[str, object]:
    return build_cross_event_conformance(project_root=PROJECT_ROOT)


def test_both_event_paths_close_one_shared_contract(
    conformance: dict[str, object],
) -> None:
    assert conformance["conformance_id"] == CONFORMANCE_ID
    assert conformance["status"] == "pass"
    assert [row["event_id"] for row in conformance["events"]] == [
        "H2EPR-0288",
        "H2EPR-0616",
    ]
    assert conformance["verified_properties"] == {
        "both_compact_releases_fail_closed_and_admitted": True,
        "both_full_roster_executable_parents_resolved": True,
        "both_materialization_pairs_byte_identical": True,
        "both_authoritative_replays_closed": True,
        "both_generated_epgs_trace_closed": True,
        "both_transports_resolved_at_completion": True,
        "event_specific_coverage_values_preserved": True,
        "masim_used_as_read_only_base_framework": True,
    }
    assert conformance["shared_contract"]["materializations_per_event"] == 2
    assert len(conformance["shared_contract"]["complete_run_documents"]) == 8
    assert len(conformance["shared_contract"]["compact_release_documents"]) == 6


def test_event_vectors_remain_distinct_and_complete(
    conformance: dict[str, object],
) -> None:
    panic, singhealth = conformance["events"]
    assert panic["full_roster_coverage"] == {
        "actors_operated": 16,
        "actor_capability_bindings": 17,
        "commitments_evaluated": 88,
        "scenario_policies_exercised": 9,
        "lifecycle_families_realized": 13,
    }
    assert singhealth["full_roster_coverage"] == {
        "actors_operated": 13,
        "actor_capability_bindings": 13,
        "commitments_evaluated": 41,
        "scenario_policies_exercised": 9,
        "lifecycle_families_realized": 11,
    }
    assert panic["execution_inventory"]["logical_coordinate_count"] == 32
    assert panic["execution_inventory"]["trace_record_count"] == 2002
    assert panic["generated_epg_inventory"]["node_count"] == 1392
    assert panic["generated_epg_inventory"]["edge_count"] == 1121
    assert singhealth["execution_inventory"]["logical_coordinate_count"] == 50
    assert singhealth["execution_inventory"]["trace_record_count"] == 1554
    assert singhealth["generated_epg_inventory"]["node_count"] == 752
    assert singhealth["generated_epg_inventory"]["edge_count"] == 623
    assert all(
        row["closure"] == {
            "deterministic_materialization_pair": True,
            "authoritative_replay": True,
            "trace_derived_graph": True,
            "unresolved_message_intent_count": 0,
            "unresolved_graph_reference_count": 0,
        }
        for row in (panic, singhealth)
    )


def test_release_rebuilds_and_is_strictly_admitted(
    conformance: dict[str, object],
) -> None:
    released_conformance = json.loads(
        (RELEASE_ROOT / "conformance.json").read_text(encoding="utf-8")
    )
    assert released_conformance == conformance
    expected_manifest = build_cross_event_release_manifest(
        conformance,
        project_root=PROJECT_ROOT,
    )
    released_manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    assert released_manifest == expected_manifest
    assert released_manifest["release_id"] == RELEASE_ID
    assert released_manifest["status"] == RELEASE_STATUS

    admission = load_cross_event_conformance_release(
        RELEASE_ROOT,
        project_root=PROJECT_ROOT,
        expected_manifest_source_sha256=_sha256(
            RELEASE_ROOT / "manifest.json"
        ),
    )
    assert admission.accepted is True
    assert admission.event_ids == ("H2EPR-0288", "H2EPR-0616")
    assert admission.compact_releases_closed is True
    assert admission.shared_contract_closed is True
    assert admission.event_specific_semantics_preserved is True
    with pytest.raises(TypeError):
        admission.conformance_document["status"] = "forged"


def test_checksums_cover_the_complete_owned_surface() -> None:
    rows = {
        relative: digest
        for digest, relative in (
            line.split("  ", 1)
            for line in (RELEASE_ROOT / "SHA256SUMS")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    assert set(rows) == {
        "manifest.json",
        "README.md",
        "substantive-review.md",
        "conformance.json",
    }
    assert all(
        _sha256(RELEASE_ROOT / relative) == digest
        for relative, digest in rows.items()
    )


def test_admission_rejects_duplicate_checksum_and_coordinated_drift(
    tmp_path: Path,
) -> None:
    project_copy = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, project_copy)
    release = project_copy / RELEASE_PATH
    manifest_path = release / "manifest.json"

    duplicate = release / "duplicate-manifest.json"
    duplicate.write_text(
        manifest_path.read_text(encoding="utf-8").replace(
            "{\n",
            f'{{\n  "release_id": "{RELEASE_ID}",\n',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(CrossEventConformanceError) as duplicate_raised:
        load_cross_event_conformance_release(
            duplicate,
            project_root=project_copy,
        )
    assert duplicate_raised.value.code is (
        CrossEventConformanceCode.JSON_DUPLICATE_KEY
    )

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
    forged["events"][0]["full_roster_coverage"]["actors_operated"] = 15
    _write_json(conformance_path, forged)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["conformance_artifact"]["source_sha256"] = _sha256(
        conformance_path
    )
    manifest["conformance_artifact"]["canonical_sha256"] = canonical_sha256(
        forged
    )
    manifest["conformance_artifact"]["byte_count"] = (
        conformance_path.stat().st_size
    )
    _write_json(manifest_path, manifest)
    names = (
        "manifest.json",
        "README.md",
        "substantive-review.md",
        "conformance.json",
    )
    (release / "SHA256SUMS").write_text(
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


def test_release_does_not_claim_masim_ownership_or_scientific_validity(
    conformance: dict[str, object],
) -> None:
    manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["masim_boundary"] == {
        "package_version": "0.0.1",
        "usage": "read_only_public_interfaces",
        "source_modification_allowed": False,
    }
    assert manifest["implementation_sources"] == [
        {
            "path": "src/h2epr/scenarios/cross_event_conformance_v0_1.py",
            "sha256": _sha256(
                PROJECT_ROOT
                / "src/h2epr/scenarios/cross_event_conformance_v0_1.py"
            ),
        }
    ]
    assert conformance["claim_boundary"] == {
        "construction_exposure": "full_event_evidence",
        "historical_calibration": False,
        "historical_validation": False,
        "known_outcome_fitting": False,
        "held_out_evaluation": False,
        "scientific_validity_claim": False,
        "output_interpretation": "simulation_generated_mechanism_coverage",
    }
