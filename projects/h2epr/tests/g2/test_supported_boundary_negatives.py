from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

import h2epr.bundles as bundle_api
from h2epr.bundles import build_panic_1907_bundle_set
from h2epr.bundles.canonical import construction_bundle_hash, runtime_bundle_hash
from h2epr.bundles.source_profile import authorized_development_descriptors, verify_authorized_development_profile
from h2epr.bundles.validation import runtime_value_errors, validate_bundle_pair, validate_execution_manifest
from h2epr.construction import Availability, ReviewState, SourceDescriptor, SourceKind


REPO_ROOT = Path(__file__).parents[4]
PROJECT_ROOT = REPO_ROOT / "projects/h2epr"
INPUT_ROOT = REPO_ROOT / "data/h2epr/development_samples_v1"


@pytest.fixture(scope="module")
def candidate():
    return build_panic_1907_bundle_set(INPUT_ROOT)


def _reseal_pair(construction: dict, runtime: dict) -> None:
    construction["construction_seal"]["content_sha256"] = construction_bundle_hash(construction)
    digest = construction["construction_seal"]["content_sha256"]
    for parent in (runtime["source_construction_bundle"], runtime["artifact_identity"]["parent_artifacts"][0]):
        parent["artifact_sha256"] = digest
    runtime["artifact_sha256"] = runtime_bundle_hash(runtime)


def test_unlisted_cross_event_and_forbidden_source_descriptors_reject() -> None:
    descriptors = authorized_development_descriptors()
    with pytest.raises(ValueError, match="profile_mismatch"):
        verify_authorized_development_profile(descriptors[:-1])
    target_dir = "H2EPR-" + "0288"
    extra = SourceDescriptor("unlisted", SourceKind.EVENT_SPEC, f"events/{target_dir}/event_spec.json", "0" * 64, Availability.CONSTRUCTION_ONLY, ReviewState.REVIEWED)
    with pytest.raises(ValueError, match="profile_mismatch"):
        verify_authorized_development_profile((*descriptors, extra))
    forbidden_name = "reference_" + "epg.json"
    forbidden = SourceDescriptor("held-out", "target_suffix", f"events/{target_dir}/{forbidden_name}", "0" * 64, Availability.UNAVAILABLE, ReviewState.REJECTED)
    with pytest.raises(ValueError, match="profile_mismatch"):
        verify_authorized_development_profile((*descriptors[:-1], forbidden))


def test_identity_relabel_and_ancestry_mismatch_reject(candidate) -> None:
    construction = copy.deepcopy(candidate.constructions["balanced"])
    runtime = copy.deepcopy(candidate.event_bundles["balanced"])
    construction["artifact_identity"]["construction_state"] = "architecture_generic"
    construction["construction_seal"]["content_sha256"] = construction_bundle_hash(construction)
    errors = validate_bundle_pair(construction, runtime)
    assert any("CONSTRUCTION_SCHEMA" in item or "TARGET_IDENTITY" in item for item in errors)

    construction = copy.deepcopy(candidate.constructions["balanced"])
    runtime = copy.deepcopy(candidate.event_bundles["balanced"])
    runtime["source_construction_bundle"]["artifact_id"] = "substituted.parent"
    runtime["artifact_sha256"] = runtime_bundle_hash(runtime)
    errors = validate_bundle_pair(construction, runtime)
    assert "SOURCE_CONSTRUCTION_PARENT_MISMATCH" in errors


def test_missing_provenance_and_visibility_mismatch_reject(candidate) -> None:
    runtime = copy.deepcopy(candidate.event_bundles["balanced"])
    value = runtime["event_identity"]
    value["provenance"][0]["visibility"] = "runtime_private"
    assert "PROVENANCE_RUNTIME_METADATA_MISMATCH" in runtime_value_errors(runtime)
    del value["provenance"]
    errors = validate_bundle_pair(candidate.constructions["balanced"], runtime)
    assert any(item.startswith("RUNTIME_SCHEMA") for item in errors)


def test_historical_scheduler_and_parent_hash_mutation_reject(candidate) -> None:
    runtime = copy.deepcopy(candidate.event_bundles["balanced"])
    runtime["exogenous_manifest"] = [{"historical_replay": True}]
    runtime["artifact_sha256"] = runtime_bundle_hash(runtime)
    errors = validate_bundle_pair(candidate.constructions["balanced"], runtime)
    assert "HISTORICAL_EXOGENOUS_NOT_EMPTY" in errors
    runtime = copy.deepcopy(candidate.event_bundles["balanced"])
    runtime["source_construction_bundle"]["artifact_sha256"] = "f" * 64
    runtime["artifact_sha256"] = runtime_bundle_hash(runtime)
    assert "SOURCE_CONSTRUCTION_PARENT_MISMATCH" in validate_bundle_pair(candidate.constructions["balanced"], runtime)


def test_absolute_manifest_name_and_bundle_hash_mutation_reject(candidate) -> None:
    manifest = copy.deepcopy(candidate.execution_manifest)
    manifest["execution_matrix"][0]["profile_event_bundle_logical_name"] = "/tmp/event.json"
    manifest["execution_matrix"][1]["profile_event_bundle_sha256"] = "0" * 64
    errors = validate_execution_manifest(manifest, candidate.event_bundles)
    assert "ABSOLUTE_OR_TRAVERSING_LOGICAL_NAME" in errors
    assert "MATRIX_BUNDLE_HASH_MISMATCH" in errors


def test_runtime_behavior_structures_must_match_construction_projection(candidate) -> None:
    construction = candidate.constructions["balanced"]
    mutations = (
        (
            "PARTICIPANT_ARTIFACT_PROJECTION_MISMATCH",
            lambda runtime: runtime["participant_artifacts"][0].__setitem__(
                "action_space_refs",
                runtime["participant_artifacts"][0]["action_space_refs"][:-1],
            ),
        ),
        (
            "ACTION_REGISTRY_PROJECTION_MISMATCH",
            lambda runtime: runtime["action_registry"].reverse(),
        ),
        (
            "COMMUNICATION_ROUTE_PROJECTION_MISMATCH",
            lambda runtime: runtime["communication_routes"].reverse(),
        ),
        (
            "OBSERVATION_ACCESS_PROJECTION_MISMATCH",
            lambda runtime: runtime["observation_access_rules"].reverse(),
        ),
    )
    for expected_error, mutate in mutations:
        runtime = copy.deepcopy(candidate.event_bundles["balanced"])
        mutate(runtime)
        runtime["artifact_sha256"] = runtime_bundle_hash(runtime)
        errors = validate_bundle_pair(construction, runtime)
        assert expected_error in errors
        assert "RUNTIME_HASH_MISMATCH" not in errors


def test_execution_matrix_rejects_relative_cross_profile_logical_name(candidate) -> None:
    manifest = copy.deepcopy(candidate.execution_manifest)
    row = next(
        item
        for item in manifest["execution_matrix"]
        if item["profile_id"] == "balanced" and item["run_seed"] == 0
    )
    row["profile_event_bundle_logical_name"] = "event_bundles/high_stress.json"
    errors = validate_execution_manifest(manifest, candidate.event_bundles)
    assert "MATRIX_BUNDLE_LOGICAL_NAME_MISMATCH" in errors
    assert "MATRIX_BUNDLE_HASH_MISMATCH" not in errors


def test_g2_public_api_has_no_runtime_invocation() -> None:
    prohibited = {"run", "execute", "simulate", "start_simulation", "run_simulation"}
    assert prohibited.isdisjoint(bundle_api.__all__)


def test_production_imports_exclude_runtime_model_and_evaluation_dependencies() -> None:
    source_root = PROJECT_ROOT / "src/h2epr"
    forbidden_roots = {"masim", "ray", "lmbase", "torch", "openai"}
    forbidden_fragments = {"rag", "evaluation", "reference"}
    violations = []
    source_paths = [source_root / "__init__.py"]
    for package in ("artifacts", "bundles", "policies", "world"):
        source_paths.extend((source_root / package).rglob("*.py"))
    for path in sorted(source_paths):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                root = name.split(".")[0].lower()
                if root in forbidden_roots or any(fragment in name.lower() for fragment in forbidden_fragments):
                    violations.append(f"{path.relative_to(PROJECT_ROOT)}:{name}")
    assert violations == []
