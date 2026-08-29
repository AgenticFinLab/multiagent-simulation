from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from masim.integrations.event_process import canonical_sha256

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    load_panic_executable_package,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.run_release import (
    EXECUTABLE_PACKAGE_PATH,
    FORMAL_DOCUMENTS,
    RUN_DOCUMENTS,
    RUN_RELEASE_ID,
    RUN_RELEASE_STATUS,
    PanicRunClosureError,
    PanicRunPair,
    PanicRunReleaseCode,
    PanicRunReleaseError,
    build_panic_formal_run_documents,
    build_panic_run_release_manifest,
    load_panic_run_release,
    materialize_panic_run_pair,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = PROJECT_ROOT / "execution/panic_1907/run-and-graph-v0.1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def run_pair(tmp_path_factory: pytest.TempPathFactory) -> PanicRunPair:
    admission = load_panic_executable_package(
        PROJECT_ROOT / EXECUTABLE_PACKAGE_PATH,
        project_root=PROJECT_ROOT,
    )
    return materialize_panic_run_pair(
        admission,
        tmp_path_factory.mktemp("panic-run-pair") / "custody",
    )


def test_pair_materialization_is_byte_identical_and_inventoried(
    run_pair: PanicRunPair,
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
    assert comparison["coverage"]["actors_operated"] == 16
    assert comparison["coverage"]["actor_capability_bindings"] == 17
    assert comparison["coverage"]["commitments_evaluated"] == 88
    assert comparison["coverage"]["scenario_policies_exercised"] == 9
    assert comparison["coverage"]["lifecycle_families_realized"] == 13

    root = run_pair.custody_root
    for _, filename in RUN_DOCUMENTS:
        first = root / "canonical/artifacts" / filename
        second = root / "independent-repeat/artifacts" / filename
        assert first.read_bytes() == second.read_bytes()
    assert (root / "canonical/artifacts/simulation-trace.json").stat().st_size > 6_000_000
    assert (root / "canonical/artifacts/generated-epg.json").stat().st_size > 5_000_000

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
    assert set(checksum_rows) == {
        "INDEX.json",
        "README.md",
        *(
            f"{directory}/{filename}"
            for directory in (
                "canonical/artifacts",
                "independent-repeat/artifacts",
            )
            for _, filename in RUN_DOCUMENTS
        ),
    }
    assert all(_sha256(root / path) == digest for path, digest in checksum_rows.items())
    assert str(root.resolve()) not in (root / "INDEX.json").read_text(
        encoding="utf-8"
    )


def test_run_graph_and_replay_close_exact_expected_vector(
    run_pair: PanicRunPair,
) -> None:
    canonical = run_pair.canonical
    receipt = canonical.execution_receipt
    graph = canonical.generated_epg

    assert canonical.replay_receipt["status"] == "pass"
    assert canonical.replay_receipt["record_count"] == 2002
    assert canonical.replay_receipt["tick_count"] == 32
    assert canonical.run_seal["unresolved_intent_ids"] == []
    assert canonical.run_seal["unresolved_recipient_ids"] == []
    assert receipt["coverage"]["record_counts"]["action_intent"] == 87
    assert receipt["coverage"]["record_counts"][
        "scenario_policy_application"
    ] == 443
    assert len(graph["nodes"]) == 1392
    assert len(graph["edges"]) == 1121
    assert graph["source_trace_sha256"] == canonical_sha256(
        canonical.simulation_trace
    )
    assert graph["source_run_seal_sha256"] == canonical.run_seal[
        "seal_sha256"
    ]


def test_compact_release_rebuilds_and_is_strictly_admitted(
    run_pair: PanicRunPair,
) -> None:
    expected_documents = build_panic_formal_run_documents(
        run_pair.canonical, run_pair.independent_repeat
    )
    released_documents = {
        filename: json.loads((RELEASE_ROOT / filename).read_text(encoding="utf-8"))
        for filename in FORMAL_DOCUMENTS
    }
    assert released_documents == expected_documents

    expected_manifest = build_panic_run_release_manifest(
        expected_documents,
        project_root=PROJECT_ROOT,
    )
    released_manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    assert released_manifest == expected_manifest
    assert released_manifest["release_id"] == RUN_RELEASE_ID
    assert released_manifest["status"] == RUN_RELEASE_STATUS
    assert {
        row["filename"]
        for row in released_manifest["large_artifact_inventory"]
    } == {
        "simulation-trace.json",
        "final-state.json",
        "tick-seals.json",
        "generated-epg.json",
    }
    assert all(
        row["tracked_in_release"] is False
        for row in released_manifest["large_artifact_inventory"]
    )

    admission = load_panic_run_release(
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


def test_release_checksums_cover_the_complete_tracked_surface() -> None:
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
        *FORMAL_DOCUMENTS,
    }
    assert all(_sha256(RELEASE_ROOT / path) == digest for path, digest in rows.items())


def test_compact_admission_rejects_duplicate_json_and_resealed_semantic_drift(
    tmp_path: Path,
) -> None:
    project_copy = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, project_copy)
    release = project_copy / "execution/panic_1907/run-and-graph-v0.1"
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
    with pytest.raises(PanicRunReleaseError) as duplicate_raised:
        load_panic_run_release(
            duplicate,
            project_root=project_copy,
        )
    assert duplicate_raised.value.code is PanicRunReleaseCode.JSON_DUPLICATE_KEY

    original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    forged_manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    forged_manifest["large_artifact_inventory"][0]["source_sha256"] = "f" * 64
    _write_json(manifest_path, forged_manifest)
    with pytest.raises(PanicRunReleaseError) as inventory_raised:
        load_panic_run_release(
            release,
            project_root=project_copy,
        )
    assert inventory_raised.value.code is PanicRunReleaseCode.CLOSURE_MISMATCH
    _write_json(manifest_path, original_manifest)

    replay_path = release / "replay-receipt.json"
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay["status"] = "forged"
    _write_json(replay_path, replay)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    replay_row = next(
        row
        for row in manifest["formal_artifacts"]
        if row["filename"] == "replay-receipt.json"
    )
    replay_row["source_sha256"] = _sha256(replay_path)
    replay_row["canonical_sha256"] = canonical_sha256(replay)
    replay_row["byte_count"] = replay_path.stat().st_size
    _write_json(manifest_path, manifest)

    with pytest.raises(PanicRunReleaseError) as closure_raised:
        load_panic_run_release(
            release,
            project_root=project_copy,
        )
    assert closure_raised.value.code is PanicRunReleaseCode.CLOSURE_MISMATCH


def test_pair_materialization_requires_a_fresh_custody_root(tmp_path: Path) -> None:
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "existing").write_text("preserve", encoding="utf-8")
    admission = load_panic_executable_package(
        PROJECT_ROOT / EXECUTABLE_PACKAGE_PATH,
        project_root=PROJECT_ROOT,
    )
    with pytest.raises(
        PanicRunClosureError, match="panic_run_pair_custody_root_not_fresh"
    ):
        materialize_panic_run_pair(admission, occupied)
    assert (occupied / "existing").read_text(encoding="utf-8") == "preserve"
