from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from h2epr.bundles.canonical import sha256_value
from h2epr.configuration import (
    ConfigurationAdmissionError,
    ConfigurationErrorCode,
    ConfigurationFailureClass,
    build_configuration_preflight_receipt,
    load_scenario_configuration,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_RELATIVE = Path(
    "configs/panic_1907/scenario-configuration-v0.1/scenario-configuration.json"
)
MANIFEST_RELATIVE = CONFIG_RELATIVE.parent / "manifest.json"
RECEIPT_RELATIVE = Path("configs/panic_1907/configuration-admission-v0.1/receipt.json")
ACCEPTED_SOURCE_SHA256 = (
    "6f931e81482d2a511220c467e578565b6b949b41c80874b13f56a172d9ed5e22"
)
ACCEPTED_MANIFEST_SHA256 = (
    "be9f9fb3c81380d9b6ba31414667b7594032d22a42d88b9fa3ea2abf5cf72f24"
)
ACCEPTED_CANONICAL_SHA256 = (
    "fce44a347aa6504b5d26f6a3901753c1b4547359f85fed9ec1a860a92196359f"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(
    root: Path = PROJECT_ROOT,
    *,
    source_sha256: str = ACCEPTED_SOURCE_SHA256,
    manifest_sha256: str = ACCEPTED_MANIFEST_SHA256,
):
    return load_scenario_configuration(
        root / CONFIG_RELATIVE,
        project_root=root,
        expected_source_sha256=source_sha256,
        expected_release_manifest_sha256=manifest_sha256,
    )


def _copy_project(tmp_path: Path) -> Path:
    root = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    return root


def _replace_checksum(package: Path, filename: str, digest: str) -> None:
    path = package / "SHA256SUMS"
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.endswith(f"  {filename}")]
    assert len(matches) == 1
    lines[matches[0]] = f"{digest}  {filename}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _rewrite_package(
    root: Path,
    mutation,
    *,
    manifest_mutation=None,
    compact: bool = False,
) -> tuple[str, str]:
    config_path = root / CONFIG_RELATIVE
    package = config_path.parent
    document = json.loads(config_path.read_text(encoding="utf-8"))
    mutation(document)
    config_path.write_text(
        (
            json.dumps(document, ensure_ascii=False, separators=(",", ":"))
            if compact
            else json.dumps(document, ensure_ascii=False, indent=2)
        )
        + "\n",
        encoding="utf-8",
    )
    source_sha256 = _sha256(config_path)
    manifest_path = root / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact = next(
        item for item in manifest["artifacts"] if item["kind"] == "scenario_configuration"
    )
    artifact["sha256"] = source_sha256
    if manifest_mutation is not None:
        manifest_mutation(manifest)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_sha256 = _sha256(manifest_path)
    _replace_checksum(package, "scenario-configuration.json", source_sha256)
    _replace_checksum(package, "manifest.json", manifest_sha256)
    return source_sha256, manifest_sha256


def _repository_context() -> dict[str, object]:
    paths = (
        "configs/schemas/event-scenario-configuration-v0.1.schema.json",
        "src/h2epr/configuration/errors.py",
        "src/h2epr/configuration/loader.py",
    )
    return {
        "root": "projects/h2epr",
        "branch": "h2epr-event-simulation",
        "baseline_commit": "a" * 40,
        "worktree_state": "authorized_configuration_admission_changes_present",
        "validation_surface_sha256s": {
            path: _sha256(PROJECT_ROOT / path) for path in paths
        },
    }


VERIFICATION = [
    {
        "command": "pytest projects/h2epr/tests/configuration",
        "result": "pass",
        "summary": "focused configuration admission checks passed",
    }
]


def test_accepted_configuration_admits_with_exact_nonexecutable_identity() -> None:
    admission = _load()

    assert admission.configuration_id == (
        "h2epr.0288.scenario.mechanism-coverage.v0_1"
    )
    assert admission.source_sha256 == ACCEPTED_SOURCE_SHA256
    assert admission.canonical_sha256 == ACCEPTED_CANONICAL_SHA256
    assert admission.release_manifest_sha256 == ACCEPTED_MANIFEST_SHA256
    assert admission.coverage["total_actors"] == 16
    assert admission.coverage["population_units"] == 10
    assert admission.coverage["observation_placements"] == 115
    assert admission.coverage["intent_placements"] == 107
    assert admission.execution_eligible is False
    assert len(admission.unbound_policy_ids) == 9
    with pytest.raises(TypeError):
        admission.document["purpose"] = "changed"


def test_preflight_receipt_is_deterministic_and_does_not_authorize_e6() -> None:
    admission = _load()
    first = build_configuration_preflight_receipt(
        admission=admission,
        repository_context=_repository_context(),
        verification=VERIFICATION,
    )
    second = build_configuration_preflight_receipt(
        admission=admission,
        repository_context=_repository_context(),
        verification=VERIFICATION,
    )

    assert first == second
    preimage = copy.deepcopy(first)
    receipt_sha256 = preimage.pop("receipt_sha256")
    assert receipt_sha256 == sha256_value(preimage)
    assert first["verdict"] == "PASS_BOUNDED_CONFIGURATION_ADMISSION"
    assert all(row["status"] == "pass" for row in first["gates"])
    assert first["execution_boundary"]["execution_eligible"] is False
    assert first["authorization"] == {
        "configuration_surface_only": True,
        "carrier_projection_authorized": False,
        "policy_implementation_authorized": False,
        "runtime_authorized": False,
        "simulation_authorized": False,
        "evaluation_authorized": False,
    }


def test_tracked_receipt_self_hash_and_validation_surface_are_exact() -> None:
    receipt = json.loads((PROJECT_ROOT / RECEIPT_RELATIVE).read_text(encoding="utf-8"))
    preimage = copy.deepcopy(receipt)
    expected_receipt_sha256 = preimage.pop("receipt_sha256")

    assert sha256_value(preimage) == expected_receipt_sha256
    for relative, expected_sha256 in receipt["repository"][
        "validation_surface_sha256s"
    ].items():
        assert _sha256(PROJECT_ROOT / relative) == expected_sha256
    assert receipt["execution_boundary"]["execution_eligible"] is False


def test_canonical_identity_is_independent_of_json_presentation(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    source_sha256, manifest_sha256 = _rewrite_package(
        root, lambda document: None, compact=True
    )

    reformatted = _load(
        root, source_sha256=source_sha256, manifest_sha256=manifest_sha256
    )
    assert source_sha256 != ACCEPTED_SOURCE_SHA256
    assert reformatted.canonical_sha256 == ACCEPTED_CANONICAL_SHA256


def test_missing_expected_identity_is_rejected_before_admission() -> None:
    with pytest.raises(ConfigurationAdmissionError) as raised:
        load_scenario_configuration(PROJECT_ROOT / CONFIG_RELATIVE)

    assert raised.value.code is ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID
    assert raised.value.failure_class is ConfigurationFailureClass.PREFLIGHT_CONTEXT


def test_project_root_and_prefixed_relative_configuration_path_resolve_once() -> None:
    admission = load_scenario_configuration(
        Path("projects/h2epr") / CONFIG_RELATIVE,
        project_root=Path("projects/h2epr"),
        expected_source_sha256=ACCEPTED_SOURCE_SHA256,
        expected_release_manifest_sha256=ACCEPTED_MANIFEST_SHA256,
    )

    assert admission.project_relative_path == CONFIG_RELATIVE.as_posix()


def test_raw_source_drift_fails_against_external_identity(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    config_path = root / CONFIG_RELATIVE
    config_path.write_text(
        config_path.read_text(encoding="utf-8") + " ", encoding="utf-8"
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root)
    assert raised.value.code is ConfigurationErrorCode.INTEGRITY_MISMATCH
    assert raised.value.pointer == "/configuration"


def test_duplicate_json_key_fails_before_hash_or_schema_repair(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    config_path = root / CONFIG_RELATIVE
    text = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        text.replace(
            '  "schema": "h2epr.event-scenario-configuration.v0_1",',
            '  "schema": "h2epr.event-scenario-configuration.v0_1",\n'
            '  "schema": "h2epr.event-scenario-configuration.v0_1",',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=_sha256(config_path))
    assert raised.value.code is ConfigurationErrorCode.JSON_DUPLICATE_KEY


def test_unsupported_schema_version_has_stable_code(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    source_sha256, manifest_sha256 = _rewrite_package(
        root,
        lambda document: document.__setitem__(
            "schema", "h2epr.event-scenario-configuration.v9_9"
        ),
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.SCHEMA_VERSION_UNSUPPORTED
    assert raised.value.failure_class is ConfigurationFailureClass.STRUCTURE


def test_unknown_top_level_field_fails_schema_and_routes_p2(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    source_sha256, manifest_sha256 = _rewrite_package(
        root, lambda document: document.__setitem__("runtime_defaults", {})
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.SCHEMA_VALIDATION_FAILED
    receipt = build_configuration_preflight_receipt(
        error=raised.value,
        attempted_configuration_path=CONFIG_RELATIVE.as_posix(),
        repository_context=_repository_context(),
        verification=VERIFICATION,
    )
    assert receipt["verdict"] == "FAIL_CONFIGURATION_SURFACE"
    assert next(row for row in receipt["gates"] if row["gate"] == "P2")[
        "status"
    ] == "fail"
    assert receipt["failure"]["code"] == "CONFIG_SCHEMA_VALIDATION_FAILED"


def test_semantic_input_hash_cannot_drift_with_repacked_config(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["semantic_inputs"]["mapping_profile_sha256"] = "0" * 64

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH
    assert raised.value.failure_class is ConfigurationFailureClass.SEMANTIC_REFERENCE


def test_unknown_capability_fails_reference_gate(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["named_actors"][0]["capability_ids"] = ["missing_capability"]

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.REFERENCE_UNRESOLVED


def test_duplicate_entity_fails_actor_assembly_gate(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["named_actors"][1]["entity_id"] = document["named_actors"][0][
            "entity_id"
        ]

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.ASSEMBLY_INVALID
    assert "duplicate=" in raised.value.detail


def test_opening_need_and_dated_activation_must_agree(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["population_units"][0]["opening_private_need"] = "immediate"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.ASSEMBLY_INVALID
    assert raised.value.detail == "opening_activation_mismatch"


def test_overlay_target_must_resolve_to_exact_typed_field(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["sensitivity_overlays"][3]["operations"][0][
            "field"
        ] = "missing_field"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.OVERLAY_TARGET_INVALID


def test_coverage_expectation_is_derived_not_trusted(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["validation_expectations"]["named_actors"] = 8

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.COVERAGE_MISMATCH


def test_v0_1_cannot_enable_execution_with_unbound_policies(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["execution_boundary"]["execution_eligible"] = True

    def manifest_mutation(manifest):
        manifest["configuration"]["execution_eligible"] = True
        manifest["authorization"]["execution_eligible"] = True

    source_sha256, manifest_sha256 = _rewrite_package(
        root, mutation, manifest_mutation=manifest_mutation
    )
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID
    assert raised.value.failure_class is ConfigurationFailureClass.EXECUTION_BOUNDARY
