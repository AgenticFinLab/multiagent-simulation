from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from masim.integrations.event_process import canonical_sha256

from h2epr.execution import (
    FORMAL_RUN_DOCUMENTS,
    RUN_DOCUMENTS,
    RunCustodyError,
    RunPair,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    load_singhealth_executable_package,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.run_release import (
    EXECUTABLE_PACKAGE_PATH,
    EXPECTED_COVERAGE,
    IMPLEMENTATION_SOURCE_PATHS,
    RUN_RELEASE_ID,
    RUN_RELEASE_STATUS,
    SingHealthRunReleaseCode,
    SingHealthRunReleaseError,
    build_singhealth_formal_run_documents,
    build_singhealth_run_release_manifest,
    load_singhealth_run_release,
    materialize_singhealth_run_pair,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = (
    PROJECT_ROOT
    / "execution/singhealth_data_breach/run-and-graph-v0.1"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def run_pair(tmp_path_factory: pytest.TempPathFactory) -> RunPair:
    admission = load_singhealth_executable_package(
        PROJECT_ROOT / EXECUTABLE_PACKAGE_PATH,
        project_root=PROJECT_ROOT,
    )
    return materialize_singhealth_run_pair(
        admission,
        tmp_path_factory.mktemp("singhealth-run-pair") / "custody",
    )


def test_pair_is_byte_identical_and_uses_shared_custody(
    run_pair: RunPair,
) -> None:
    comparison = run_pair.determinism_comparison
    assert comparison["status"] == "pass"
    assert comparison["all_source_bytes_identical"] is True
    assert comparison["all_canonical_documents_identical"] is True
    assert comparison["materializations"] == [
        "canonical",
        "independent_repeat",
    ]
    assert len(comparison["document_comparisons"]) == len(RUN_DOCUMENTS) == 8
    assert {
        name: comparison["coverage"][name]
        for name in EXPECTED_COVERAGE
    } == dict(EXPECTED_COVERAGE)

    root = run_pair.custody_root
    for _, filename in RUN_DOCUMENTS:
        first = root / "canonical/artifacts" / filename
        second = root / "independent-repeat/artifacts" / filename
        assert first.read_bytes() == second.read_bytes()
    assert (
        root / "canonical/artifacts/simulation-trace.json"
    ).stat().st_size > 3_000_000
    assert (
        root / "canonical/artifacts/generated-epg.json"
    ).stat().st_size > 2_000_000

    checksum_rows = {
        relative: digest
        for digest, relative in (
            line.split("  ", 1)
            for line in (root / "SHA256SUMS")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    assert len(checksum_rows) == 18
    assert all(
        _sha256(root / relative) == digest
        for relative, digest in checksum_rows.items()
    )
    assert str(root.resolve()) not in (root / "INDEX.json").read_text(
        encoding="utf-8"
    )


def test_run_replay_and_graph_close_expected_vector(
    run_pair: RunPair,
) -> None:
    canonical = run_pair.canonical
    receipt = canonical.execution_receipt
    graph = canonical.generated_epg

    assert canonical.replay_receipt["status"] == "pass"
    assert canonical.replay_receipt["record_count"] == 1554
    assert canonical.replay_receipt["tick_count"] == 50
    assert canonical.run_seal["unresolved_intent_ids"] == []
    assert canonical.run_seal["unresolved_recipient_ids"] == []
    assert receipt["coverage"]["record_counts"] == {
        "action_disposition": 41,
        "action_intent": 41,
        "carry_forward": 41,
        "completion": 1,
        "exogenous_input_release": 6,
        "message_disposition": 146,
        "message_intent": 73,
        "observation": 650,
        "participant_decision": 41,
        "run_seal": 1,
        "scenario_policy_application": 222,
        "state_delta": 141,
        "tick_commit": 50,
        "tick_open": 50,
        "tick_seal": 50,
    }
    assert len(graph["nodes"]) == 752
    assert len(graph["edges"]) == 623
    assert graph["source_trace_sha256"] == canonical_sha256(
        canonical.simulation_trace
    )
    assert graph["source_run_seal_sha256"] == canonical.run_seal[
        "seal_sha256"
    ]


def test_compact_release_rebuilds_and_is_strictly_admitted(
    run_pair: RunPair,
) -> None:
    expected_documents = build_singhealth_formal_run_documents(run_pair)
    released_documents = {
        filename: json.loads(
            (RELEASE_ROOT / filename).read_text(encoding="utf-8")
        )
        for filename in FORMAL_RUN_DOCUMENTS
    }
    assert released_documents == expected_documents

    expected_manifest = build_singhealth_run_release_manifest(
        expected_documents,
        project_root=PROJECT_ROOT,
    )
    released_manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    assert released_manifest == expected_manifest
    assert released_manifest["release_id"] == RUN_RELEASE_ID
    assert released_manifest["status"] == RUN_RELEASE_STATUS
    assert [
        Path(row["path"])
        for row in released_manifest["implementation_sources"]
    ] == list(IMPLEMENTATION_SOURCE_PATHS)
    assert all(
        row["tracked_in_release"] is False
        for row in released_manifest["large_artifact_inventory"]
    )

    admission = load_singhealth_run_release(
        RELEASE_ROOT,
        project_root=PROJECT_ROOT,
        expected_manifest_source_sha256=_sha256(
            RELEASE_ROOT / "manifest.json"
        ),
    )
    assert admission.accepted is True
    assert admission.deterministic_pair is True
    assert admission.replay_closed is True
    assert admission.graph_closed is True
    with pytest.raises(TypeError):
        admission.formal_documents["run-seal.json"]["seal_sha256"] = "forged"


def test_checksums_cover_the_complete_tracked_surface() -> None:
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
        *FORMAL_RUN_DOCUMENTS,
    }
    assert all(
        _sha256(RELEASE_ROOT / relative) == digest
        for relative, digest in rows.items()
    )


def test_admission_rejects_duplicate_and_coordinated_drift(
    tmp_path: Path,
) -> None:
    project_copy = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, project_copy)
    release = (
        project_copy
        / "execution/singhealth_data_breach/run-and-graph-v0.1"
    )
    manifest_path = release / "manifest.json"
    duplicate = release / "duplicate-manifest.json"
    duplicate.write_text(
        manifest_path.read_text(encoding="utf-8").replace(
            "{\n",
            '{\n  "release_id": "duplicate",\n',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(SingHealthRunReleaseError) as duplicate_raised:
        load_singhealth_run_release(
            duplicate,
            project_root=project_copy,
        )
    assert duplicate_raised.value.code is (
        SingHealthRunReleaseCode.JSON_DUPLICATE_KEY
    )

    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    forged = copy.deepcopy(original)
    forged["large_artifact_inventory"][0]["source_sha256"] = "f" * 64
    _write_json(manifest_path, forged)
    with pytest.raises(SingHealthRunReleaseError) as closure_raised:
        load_singhealth_run_release(release, project_root=project_copy)
    assert closure_raised.value.code is (
        SingHealthRunReleaseCode.CLOSURE_MISMATCH
    )
    _write_json(manifest_path, original)

    forged = copy.deepcopy(original)
    forged["executable_parent"]["package_source_sha256"] = "e" * 64
    _write_json(manifest_path, forged)
    with pytest.raises(SingHealthRunReleaseError) as parent_raised:
        load_singhealth_run_release(release, project_root=project_copy)
    assert parent_raised.value.code is (
        SingHealthRunReleaseCode.EXECUTABLE_PARENT_MISMATCH
    )


def test_pair_materialization_is_non_destructive(tmp_path: Path) -> None:
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    marker = occupied / "preserve"
    marker.write_text("preserve", encoding="utf-8")
    admission = load_singhealth_executable_package(
        PROJECT_ROOT / EXECUTABLE_PACKAGE_PATH,
        project_root=PROJECT_ROOT,
    )
    with pytest.raises(RunCustodyError, match="root_not_fresh"):
        materialize_singhealth_run_pair(admission, occupied)
    assert marker.read_text(encoding="utf-8") == "preserve"
