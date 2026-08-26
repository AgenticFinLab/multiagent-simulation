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
    "configs/singhealth_data_breach/scenario-configuration-v0.1/"
    "scenario-configuration.json"
)
MANIFEST_RELATIVE = CONFIG_RELATIVE.parent / "manifest.json"
RECEIPT_RELATIVE = Path(
    "configs/singhealth_data_breach/configuration-admission-v0.1/receipt.json"
)
ACCEPTED_SOURCE_SHA256 = (
    "00fe7d799b5f944da09c64ddbeea85d2addfc7948bb9f0865316962fe2d37d3d"
)
ACCEPTED_MANIFEST_SHA256 = (
    "96e9fbc4b6d4a52305450b7f38b0524da3949ff1262d84d8b6222e638d8268a9"
)
ACCEPTED_CANONICAL_SHA256 = (
    "288c1539221cce894545234cbc477f342e609ee92130cfc9925426e9d0edb9fd"
)

VERIFICATION = [
    {
        "check_id": "singhealth-configuration-admission",
        "status": "pass",
        "summary": "SingHealth bounded configuration admission checks passed",
    }
]

TRACKED_VERIFICATION = [
    {
        "check_id": "singhealth-configuration-admission",
        "status": "pass",
        "summary": "18 focused SingHealth admission checks passed",
    },
    {
        "check_id": "panic-configuration-regression",
        "status": "pass",
        "summary": "18 focused Panic admission checks passed",
    },
    {
        "check_id": "h2epr-project-suite",
        "status": "pass",
        "summary": "802 H2EPR project checks passed",
    },
    {
        "check_id": "formal-release-integrity",
        "status": "pass",
        "summary": "ten formal release checksum packages passed",
    },
    {
        "check_id": "project-documentation-links",
        "status": "pass",
        "summary": "423 project-local Markdown targets passed",
    },
]


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
    matches = [
        index for index, line in enumerate(lines) if line.endswith(f"  {filename}")
    ]
    assert len(matches) == 1
    lines[matches[0]] = f"{digest}  {filename}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _rewrite_package(
    root: Path,
    mutation,
    *,
    manifest_mutation=None,
) -> tuple[str, str]:
    config_path = root / CONFIG_RELATIVE
    document = json.loads(config_path.read_text(encoding="utf-8"))
    mutation(document)
    config_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    source_sha256 = _sha256(config_path)

    manifest_path = root / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact = next(
        item
        for item in manifest["artifacts"]
        if item["kind"] == "scenario_configuration"
    )
    artifact["sha256"] = source_sha256
    if manifest_mutation is not None:
        manifest_mutation(manifest)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_sha256 = _sha256(manifest_path)
    package = config_path.parent
    _replace_checksum(package, "scenario-configuration.json", source_sha256)
    _replace_checksum(package, "manifest.json", manifest_sha256)
    return source_sha256, manifest_sha256


def test_accepted_semantic_configuration_admits_exact_nonexecutable_release() -> None:
    admission = _load()

    assert admission.configuration_id == (
        "h2epr.0616.scenario.mechanism-coverage.v0_1"
    )
    assert admission.validation_surface == (
        "h2epr.scenario-configuration-admission.v0_2"
    )
    assert admission.source_sha256 == ACCEPTED_SOURCE_SHA256
    assert admission.canonical_sha256 == ACCEPTED_CANONICAL_SHA256
    assert admission.release_manifest_sha256 == ACCEPTED_MANIFEST_SHA256
    assert admission.mapping_profile_id == (
        "h2epr.roster-consolidated-mapping.0616.v0_1"
    )
    assert admission.coverage["semantic_products"] == 9
    assert admission.coverage["decision_and_population_commitments"] == 29
    assert admission.coverage["observation_placements"] == 62
    assert admission.coverage["private_state_placements"] == 44
    assert admission.coverage["intent_placements"] == 54
    assert admission.coverage["lifecycle_families"] == 11
    assert admission.coverage["total_semantic_actor_instances"] == 13
    assert admission.execution_eligible is False
    assert len(admission.unbound_policy_ids) == 9
    with pytest.raises(TypeError):
        admission.document["purpose"] = "changed"


def test_semantic_preflight_receipt_is_deterministic_and_non_authorizing() -> None:
    admission = _load()
    first = build_configuration_preflight_receipt(
        admission=admission,
        verification=VERIFICATION,
    )
    second = build_configuration_preflight_receipt(
        admission=admission,
        verification=VERIFICATION,
    )

    assert first == second
    preimage = copy.deepcopy(first)
    receipt_sha256 = preimage.pop("receipt_sha256")
    assert receipt_sha256 == sha256_value(preimage)
    assert first["validation_surface"] == (
        "h2epr.scenario-configuration-admission.v0_2"
    )
    assert first["verdict"] == "PASS_BOUNDED_CONFIGURATION_ADMISSION"
    assert first["execution_boundary"]["execution_eligible"] is False
    assert all(row["status"] == "pass" for row in first["gates"])
    assert not any(
        first["authorization"][name]
        for name in (
            "carrier_projection_authorized",
            "policy_implementation_authorized",
            "runtime_authorized",
            "simulation_authorized",
            "evaluation_authorized",
        )
    )


def test_tracked_semantic_receipt_is_self_hashed_and_portable() -> None:
    receipt = json.loads((PROJECT_ROOT / RECEIPT_RELATIVE).read_text(encoding="utf-8"))
    preimage = copy.deepcopy(receipt)
    expected_receipt_sha256 = preimage.pop("receipt_sha256")

    assert sha256_value(preimage) == expected_receipt_sha256
    assert receipt["validation_surface"] == (
        "h2epr.scenario-configuration-admission.v0_2"
    )
    assert receipt["configuration"]["source_sha256"] == ACCEPTED_SOURCE_SHA256
    assert receipt["configuration"]["canonical_sha256"] == (
        ACCEPTED_CANONICAL_SHA256
    )
    assert receipt["release"]["manifest_sha256"] == ACCEPTED_MANIFEST_SHA256
    assert receipt["execution_boundary"]["execution_eligible"] is False
    assert "repository" not in receipt
    receipt_text = json.dumps(receipt, sort_keys=True)
    assert "/home/" not in receipt_text
    assert "h2epr-event-simulation" not in receipt_text
    assert "worktree" not in receipt_text
    assert receipt == build_configuration_preflight_receipt(
        admission=_load(),
        verification=TRACKED_VERIFICATION,
    )


def test_semantic_source_drift_fails_external_identity(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    path = root / CONFIG_RELATIVE
    path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root)
    assert raised.value.code is ConfigurationErrorCode.INTEGRITY_MISMATCH
    assert raised.value.pointer == "/configuration"


def test_semantic_duplicate_key_fails_before_release_repair(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    path = root / CONFIG_RELATIVE
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            '  "format_identity":',
            '  "format_identity": "duplicate",\n  "format_identity":',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=_sha256(path))
    assert raised.value.code is ConfigurationErrorCode.JSON_DUPLICATE_KEY


def test_semantic_unsupported_format_has_stable_failure(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    source_sha256, manifest_sha256 = _rewrite_package(
        root,
        lambda document: document.__setitem__(
            "format_identity", "h2epr.scenario-configuration-semantic-candidate.v9_9"
        ),
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.SCHEMA_VERSION_UNSUPPORTED
    assert raised.value.pointer == "/format_identity"


def test_semantic_unknown_field_is_rejected_by_closed_schema(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    source_sha256, manifest_sha256 = _rewrite_package(
        root,
        lambda document: document.__setitem__("runtime_defaults", {}),
    )

    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.SCHEMA_VALIDATION_FAILED
    assert raised.value.failure_class is ConfigurationFailureClass.STRUCTURE
    receipt = build_configuration_preflight_receipt(
        error=raised.value,
        attempted_configuration_path=CONFIG_RELATIVE.as_posix(),
        validation_surface="h2epr.scenario-configuration-admission.v0_2",
        verification=VERIFICATION,
    )
    assert receipt["validation_surface"] == (
        "h2epr.scenario-configuration-admission.v0_2"
    )
    assert next(row for row in receipt["gates"] if row["gate"] == "P2")[
        "status"
    ] == "fail"


def test_semantic_input_hash_drift_cannot_be_repacked(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["semantic_inputs"]["mapping_profile_sha256"] = "0" * 64

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH
    assert raised.value.failure_class is ConfigurationFailureClass.SEMANTIC_REFERENCE


def test_agent_product_type_mismatch_fails_assembly(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["named_actors"][0]["participant_product_id"] = (
            document["population_units"][0]["population_product_id"]
        )

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.ASSEMBLY_INVALID
    assert raised.value.detail == "agent_product_coverage_mismatch"


def test_capability_set_must_match_accepted_mapping(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["named_actors"][0]["capability_id"] = "invented_capability"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.COVERAGE_MISMATCH
    assert raised.value.detail == "released_capability_coverage_mismatch"


def test_duplicate_actor_identity_fails_assembly(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["named_actors"][1]["actor_id"] = document["named_actors"][0][
            "actor_id"
        ]

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.ASSEMBLY_INVALID
    assert "duplicate_actor_id=" in raised.value.detail


def test_lineage_route_must_resolve(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["bounded_lineage"]["route_ids"][0] = "opening.missing.route"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.REFERENCE_UNRESOLVED
    assert raised.value.pointer == "/bounded_lineage/route_ids"


def test_route_addressing_must_remain_exact(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        route = next(
            record
            for record in document["initial_records"]
            if record["family"] == "institutional_route"
        )
        route["addressing_rule"] = "broadcast_to_all"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.ASSEMBLY_INVALID
    assert raised.value.detail == "exact_route_addressing_required"


def test_exogenous_target_must_resolve_in_declared_registry(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["exogenous_inputs"][0]["target_ids"] = ["process.missing"]

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.REFERENCE_UNRESOLVED
    assert raised.value.detail.startswith("typed_target_unresolved=")


def test_overlay_target_must_resolve_to_exact_typed_field(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["sensitivity_overlays"][0]["operations"][1][
            "field"
        ] = "route_delivery_profile"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.OVERLAY_TARGET_INVALID
    assert raised.value.detail == "materialization_target_mismatch"


def test_coverage_is_derived_from_exact_releases_and_graph(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["validation_expectations"]["private_state_placements"] = 43

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.COVERAGE_MISMATCH
    assert raised.value.detail == "mapping_actual=44"


def test_semantic_configuration_cannot_enable_execution(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["execution_boundary"]["execution_eligible"] = True

    def manifest_mutation(manifest):
        manifest["configuration"]["execution_eligible"] = True
        manifest["execution_boundary"]["execution_eligible"] = True

    source_sha256, manifest_sha256 = _rewrite_package(
        root, mutation, manifest_mutation=manifest_mutation
    )
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID
    assert raised.value.failure_class is ConfigurationFailureClass.EXECUTION_BOUNDARY


def test_unbound_policy_cannot_be_silently_marked_implemented(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)

    def mutation(document):
        document["policy_selections"][0]["implementation_status"] = "implemented"

    source_sha256, manifest_sha256 = _rewrite_package(root, mutation)
    with pytest.raises(ConfigurationAdmissionError) as raised:
        _load(root, source_sha256=source_sha256, manifest_sha256=manifest_sha256)
    assert raised.value.code is ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID
    assert raised.value.detail == (
        "all_policy_implementations_must_be_unbound_fail_closed"
    )
