from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from masim.integrations.event_process import canonical_sha256

from h2epr.execution import (
    FORMAL_RUN_DOCUMENTS,
    RUN_DOCUMENTS,
    ExecutionIOCode,
    ExecutionIOError,
    RunClosureCode,
    RunClosureError,
    RunComparisonIdentity,
    RunCustodyError,
    RunCustodyIdentity,
    build_formal_run_documents,
    build_graph_receipt,
    compare_run_artifacts,
    materialize_run_pair,
    path_within,
    read_json_object,
    validate_compact_run_closure,
    validate_run_artifacts,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    load_panic_executable_package,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.run_release import (
    EXECUTABLE_PACKAGE_PATH,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.runtime_execution import (
    PanicRunArtifacts,
    materialize_panic_run,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = PROJECT_ROOT / "execution/panic_1907/run-and-graph-v0.1"
COMPARISON_IDENTITY = RunComparisonIdentity(
    event_id="H2EPR-0288",
    comparison_id="h2epr.0288.run-comparison.canonical.v0_1",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _released_documents() -> dict[str, object]:
    return {
        filename: json.loads((RELEASE_ROOT / filename).read_text(encoding="utf-8"))
        for filename in FORMAL_RUN_DOCUMENTS
    }


@pytest.fixture(scope="module")
def panic_artifacts(
    tmp_path_factory: pytest.TempPathFactory,
) -> PanicRunArtifacts:
    admission = load_panic_executable_package(
        PROJECT_ROOT / EXECUTABLE_PACKAGE_PATH,
        project_root=PROJECT_ROOT,
    )
    return materialize_panic_run(
        admission,
        tmp_path_factory.mktemp("shared-kernel-panic") / "engine",
    )


def test_shared_full_closure_matches_the_accepted_panic_release(
    panic_artifacts: PanicRunArtifacts,
) -> None:
    summary = validate_run_artifacts(panic_artifacts)
    assert summary.event_id == "H2EPR-0288"
    assert summary.trace_record_count == 2002
    assert summary.graph_node_count == 1392
    assert summary.graph_edge_count == 1121

    released = _released_documents()
    assert build_graph_receipt(panic_artifacts) == released[
        "generated-epg-receipt.json"
    ]
    assert build_formal_run_documents(
        panic_artifacts,
        panic_artifacts,
        COMPARISON_IDENTITY,
    ) == released


def test_shared_compact_closure_admits_the_accepted_panic_release() -> None:
    manifest = json.loads((RELEASE_ROOT / "manifest.json").read_text())
    closure = validate_compact_run_closure(
        manifest,
        _released_documents(),
        expected_event_id="H2EPR-0288",
        expected_coverage={
            "actors_operated": 16,
            "actor_capability_bindings": 17,
            "commitments_evaluated": 88,
            "scenario_policies_exercised": 9,
            "lifecycle_families_realized": 13,
        },
    )
    assert closure.deterministic_pair is True
    assert closure.replay_closed is True
    assert closure.graph_closed is True


def test_full_closure_rejects_resealed_unresolved_graph_reference(
    panic_artifacts: PanicRunArtifacts,
) -> None:
    forged = copy.deepcopy(panic_artifacts)
    forged.generated_epg["nodes"][0]["source_trace_id"] = "missing.trace"
    graph_preimage = {
        key: copy.deepcopy(value)
        for key, value in forged.generated_epg.items()
        if key != "seal"
    }
    graph_sha = canonical_sha256(graph_preimage)
    forged.generated_epg["seal"]["artifact_sha256"] = graph_sha
    forged.execution_receipt["generated_epg_sha256"] = graph_sha
    with pytest.raises(RunClosureError) as raised:
        validate_run_artifacts(forged)
    assert raised.value.code is RunClosureCode.GRAPH_REFERENCE_MISMATCH


def test_full_closure_rejects_detached_tick_seal_document(
    panic_artifacts: PanicRunArtifacts,
) -> None:
    forged = copy.deepcopy(panic_artifacts)
    forged.tick_seals[0]["seal_sha256"] = "f" * 64
    with pytest.raises(RunClosureError) as raised:
        validate_run_artifacts(forged)
    assert raised.value.code is RunClosureCode.TRACE_SEAL_MISMATCH


def test_comparison_rejects_valid_but_nonidentical_materializations(
    panic_artifacts: PanicRunArtifacts,
) -> None:
    changed = copy.deepcopy(panic_artifacts)
    changed.execution_receipt["claim_boundary"] = {
        **changed.execution_receipt["claim_boundary"],
        "engineering_note": "independent semantic drift",
    }
    with pytest.raises(RunClosureError) as raised:
        compare_run_artifacts(
            panic_artifacts,
            changed,
            COMPARISON_IDENTITY,
        )
    assert raised.value.code is RunClosureCode.DETERMINISM_MISMATCH


def test_shared_custody_preserves_complete_pair_without_path_identity(
    panic_artifacts: PanicRunArtifacts,
    tmp_path: Path,
) -> None:
    def materializer(operational_root: Path) -> PanicRunArtifacts:
        operational_root.mkdir(parents=True)
        return copy.deepcopy(panic_artifacts)

    pair = materialize_run_pair(
        materializer,
        tmp_path / "custody",
        comparison_identity=COMPARISON_IDENTITY,
        custody_identity=RunCustodyIdentity(
            event_id="H2EPR-0288",
            guide_title="Panic of 1907 run custody v0.1",
        ),
    )
    assert pair.determinism_comparison == _released_documents()[
        "determinism-comparison.json"
    ]
    expected = {
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
    checksum_rows = {
        relative: digest
        for digest, relative in (
            line.split("  ", 1)
            for line in (pair.custody_root / "SHA256SUMS")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    assert set(checksum_rows) == expected
    assert all(
        _sha256(pair.custody_root / relative) == digest
        for relative, digest in checksum_rows.items()
    )
    assert str(pair.custody_root.resolve()) not in (
        pair.custody_root / "INDEX.json"
    ).read_text(encoding="utf-8")


def test_shared_custody_is_non_destructive(
    panic_artifacts: PanicRunArtifacts,
    tmp_path: Path,
) -> None:
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    marker = occupied / "preserve"
    marker.write_text("preserve", encoding="utf-8")
    with pytest.raises(RunCustodyError, match="root_not_fresh"):
        materialize_run_pair(
            lambda _: panic_artifacts,
            occupied,
            comparison_identity=COMPARISON_IDENTITY,
            custody_identity=RunCustodyIdentity(
                event_id="H2EPR-0288",
                guide_title="Panic of 1907 run custody v0.1",
            ),
        )
    assert marker.read_text(encoding="utf-8") == "preserve"


def test_strict_json_and_path_helpers_fail_closed(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"value": 1, "value": 2}\n', encoding="utf-8")
    with pytest.raises(ExecutionIOError) as duplicate_raised:
        read_json_object(duplicate, pointer="/document")
    assert duplicate_raised.value.code is ExecutionIOCode.JSON_DUPLICATE_KEY

    root = tmp_path / "root"
    root.mkdir()
    with pytest.raises(ExecutionIOError) as path_raised:
        path_within(root, tmp_path / "outside.json", pointer="/path")
    assert path_raised.value.code is ExecutionIOCode.PATH_UNSAFE


def test_compact_closure_rejects_rehashed_semantic_drift() -> None:
    manifest = json.loads((RELEASE_ROOT / "manifest.json").read_text())
    documents = copy.deepcopy(_released_documents())
    documents["execution-receipt.json"]["coverage"]["actors_operated"] = 15
    with pytest.raises(RunClosureError) as raised:
        validate_compact_run_closure(
            manifest,
            documents,
            expected_event_id="H2EPR-0288",
            expected_coverage={"actors_operated": 16},
        )
    assert raised.value.code is RunClosureCode.COMPACT_CLOSURE_MISMATCH


def test_compact_closure_rejects_coordinated_large_inventory_drift() -> None:
    manifest = json.loads((RELEASE_ROOT / "manifest.json").read_text())
    manifest["large_artifact_inventory"][0]["source_sha256"] = "f" * 64
    with pytest.raises(RunClosureError) as raised:
        validate_compact_run_closure(
            manifest,
            _released_documents(),
            expected_event_id="H2EPR-0288",
        )
    assert raised.value.code is RunClosureCode.COMPACT_CLOSURE_MISMATCH


def test_shared_kernel_source_has_no_event_specific_dependency() -> None:
    source_root = PROJECT_ROOT / "src/h2epr/execution"
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(source_root.glob("*.py"))
    )
    assert all(
        fragment not in text
        for fragment in (
            "h2epr.scenarios",
            "panic_1907",
            "singhealth_data_breach",
            "H2EPR-0288",
            "H2EPR-0616",
        )
    )
