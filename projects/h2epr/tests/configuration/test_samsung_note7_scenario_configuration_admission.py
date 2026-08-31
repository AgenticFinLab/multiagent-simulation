from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from h2epr.bundles.canonical import sha256_value
from h2epr.configuration import (
    ConfigurationAdmissionError,
    ConfigurationErrorCode,
    build_configuration_preflight_receipt,
    load_scenario_configuration,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_RELATIVE = Path(
    "configs/samsung_note7_battery_recall/scenario-configuration-v0.1/"
    "scenario-configuration.json"
)
MANIFEST_RELATIVE = CONFIG_RELATIVE.parent / "manifest.json"
RECEIPT_RELATIVE = Path(
    "configs/samsung_note7_battery_recall/configuration-admission-v0.1/receipt.json"
)
SOURCE_SHA256 = "8faa3b0a03e57f2ab4ece46a82f16d838476c9562019b8137c7ff0856ee103e9"
MANIFEST_SHA256 = "5086d78cf4dff9d8416f652b30ce206da367c92b82f11bdd42d7636fe0c0d519"
CANONICAL_SHA256 = "e97181d06def36359e1fc73a53d1e7ea220ae9bd614533b07132b7e00fb585fc"

SINGHEALTH_CONFIG = Path(
    "configs/singhealth_data_breach/scenario-configuration-v0.1/"
    "scenario-configuration.json"
)
SINGHEALTH_SOURCE_SHA256 = (
    "00fe7d799b5f944da09c64ddbeea85d2addfc7948bb9f0865316962fe2d37d3d"
)
SINGHEALTH_MANIFEST_SHA256 = (
    "96e9fbc4b6d4a52305450b7f38b0524da3949ff1262d84d8b6222e638d8268a9"
)

VERIFICATION = [
    {
        "check_id": "note7-configuration-admission",
        "status": "pass",
        "summary": "Note7 bounded configuration admission checks passed",
    }
]
TRACKED_VERIFICATION = [
    {
        "check_id": "formal-release-integrity",
        "status": "pass",
        "summary": "repository-wide strict JSON and checksum checks passed",
    },
    {
        "check_id": "note7-configuration-admission",
        "status": "pass",
        "summary": "8 focused Note7 admission checks passed",
    },
    {
        "check_id": "note7-configuration-release",
        "status": "pass",
        "summary": "4 focused Note7 configuration release checks passed",
    },
    {
        "check_id": "note7-mapping-scenario-release",
        "status": "pass",
        "summary": "5 focused Note7 mapping and Scenario release checks passed",
    },
    {
        "check_id": "project-documentation-links",
        "status": "pass",
        "summary": "repository-wide H2EPR local-link check passed",
    },
    {
        "check_id": "singhealth-configuration-regression",
        "status": "pass",
        "summary": "accepted SingHealth semantic configuration still admits unchanged",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(root: Path = PROJECT_ROOT, source: str = SOURCE_SHA256, manifest: str = MANIFEST_SHA256):
    return load_scenario_configuration(
        root / CONFIG_RELATIVE,
        project_root=root,
        expected_source_sha256=source,
        expected_release_manifest_sha256=manifest,
    )


def _replace_checksum(package: Path, filename: str, digest: str) -> None:
    path = package / "SHA256SUMS"
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.endswith(f"  {filename}")]
    assert len(matches) == 1
    lines[matches[0]] = f"{digest}  {filename}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mutated_project(mutation) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name) / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    config_path = root / CONFIG_RELATIVE
    document = json.loads(config_path.read_text(encoding="utf-8"))
    mutation(document)
    config_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    source = _sha256(config_path)
    manifest_path = root / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    next(
        row for row in manifest["artifacts"] if row["kind"] == "scenario_configuration"
    )["sha256"] = source
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest_digest = _sha256(manifest_path)
    _replace_checksum(config_path.parent, "scenario-configuration.json", source)
    _replace_checksum(config_path.parent, "manifest.json", manifest_digest)
    return temporary, root, source, manifest_digest


def test_note7_configuration_admits_exact_nonexecutable_release() -> None:
    admission = _load()
    assert admission.event_id == "H2EPR-0481"
    assert admission.configuration_id == "h2epr.0481.scenario.mechanism-coverage.v0_1"
    assert admission.validation_surface == "h2epr.scenario-configuration-admission.v0_2"
    assert admission.source_sha256 == SOURCE_SHA256
    assert admission.release_manifest_sha256 == MANIFEST_SHA256
    assert admission.canonical_sha256 == CANONICAL_SHA256
    assert admission.coverage["semantic_products"] == 8
    assert admission.coverage["total_semantic_actor_instances"] == 8
    assert admission.coverage["opening_records"] == 34
    assert admission.execution_eligible is False
    assert len(admission.unbound_policy_ids) == 9


def test_note7_preflight_receipt_is_deterministic_and_non_authorizing() -> None:
    admission = _load()
    first = build_configuration_preflight_receipt(
        admission=admission, verification=VERIFICATION
    )
    second = build_configuration_preflight_receipt(
        admission=admission, verification=VERIFICATION
    )
    assert first == second
    preimage = copy.deepcopy(first)
    assert preimage.pop("receipt_sha256") == sha256_value(preimage)
    assert first["verdict"] == "PASS_BOUNDED_CONFIGURATION_ADMISSION"
    assert first["execution_boundary"]["execution_eligible"] is False
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


def test_domain_neutral_and_legacy_structural_vocabularies_both_admit() -> None:
    note7 = _load()
    singhealth = load_scenario_configuration(
        PROJECT_ROOT / SINGHEALTH_CONFIG,
        project_root=PROJECT_ROOT,
        expected_source_sha256=SINGHEALTH_SOURCE_SHA256,
        expected_release_manifest_sha256=SINGHEALTH_MANIFEST_SHA256,
    )
    assert note7.event_id == "H2EPR-0481"
    assert singhealth.event_id == "H2EPR-0616"
    assert note7.schema_sha256 != singhealth.schema_sha256
    assert singhealth.schema_sha256 == (
        "806e7db592375d90aa6c08265d578634f79d80f42898f8bd0378df32c95cb51c"
    )
    assert note7.document["format_identity"].endswith(".v0_2")
    assert singhealth.document["format_identity"].endswith(".v0_1")
    assert note7.document["variant_materialization"].get("exogenous_pressure_profile")
    assert singhealth.document["variant_materialization"].get("attack_pressure_profile")


def test_mixed_structural_vocabulary_fails_closed_schema() -> None:
    def mutation(document):
        document["variant_materialization"]["attack_pressure_profile"] = copy.deepcopy(
            document["variant_materialization"]["exogenous_pressure_profile"]
        )

    temporary, root, source, manifest = _mutated_project(mutation)
    try:
        try:
            _load(root, source, manifest)
        except ConfigurationAdmissionError as error:
            assert error.code is ConfigurationErrorCode.SCHEMA_VALIDATION_FAILED
        else:
            raise AssertionError("mixed vocabulary admitted")
    finally:
        temporary.cleanup()


def test_domain_neutral_format_rejects_complete_legacy_vocabulary() -> None:
    family_names = {
        "exogenous_pressure": "attack_pressure",
        "route_and_delivery": "route_and_delivery",
        "population_assembly": "responsibility_units",
        "authority_capacity": "office_capacity",
        "operational_result": "technical_result",
        "public_action_delivery": "notification",
    }
    materialization_fields = {
        "exogenous_pressure_profile": "attack_pressure_profile",
        "authority_capacity_profile": "office_capacity_profile",
        "operational_result_profile": "technical_result_profile",
        "public_action_delivery_profile": "notification_profile",
    }

    def mutation(document):
        for variant in document["structural_variants"]:
            variant["family"] = family_names[variant["family"]]
        materialization = document["variant_materialization"]
        for neutral, legacy in materialization_fields.items():
            materialization[legacy] = materialization.pop(neutral)
        for overlay in document["sensitivity_overlays"]:
            for operation in overlay["operations"]:
                operation["field"] = materialization_fields.get(
                    operation["field"], operation["field"]
                )

    temporary, root, source, manifest = _mutated_project(mutation)
    try:
        try:
            _load(root, source, manifest)
        except ConfigurationAdmissionError as error:
            assert error.code is ConfigurationErrorCode.SCHEMA_VALIDATION_FAILED
        else:
            raise AssertionError("complete legacy vocabulary admitted as v0.2")
    finally:
        temporary.cleanup()


def test_lineage_capability_transition_must_follow_a_declared_route() -> None:
    def mutation(document):
        sequence = document["bounded_lineage"]["semantic_intent_sequence"]
        consumer_request = sequence.pop(-2)
        sequence.insert(1, consumer_request)

    temporary, root, source, manifest = _mutated_project(mutation)
    try:
        try:
            _load(root, source, manifest)
        except ConfigurationAdmissionError as error:
            assert error.code is ConfigurationErrorCode.ASSEMBLY_INVALID
            assert error.detail == "lineage_capability_transition_unrouted"
        else:
            raise AssertionError("unrouted lineage capability transition admitted")
    finally:
        temporary.cleanup()


def test_outcome_forcing_input_is_rejected() -> None:
    def mutation(document):
        document["exogenous_inputs"][0]["outcome_forcing"] = True

    temporary, root, source, manifest = _mutated_project(mutation)
    try:
        try:
            _load(root, source, manifest)
        except ConfigurationAdmissionError as error:
            assert error.code is ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID
            assert error.detail == "non_outcome_forcing_input_required"
        else:
            raise AssertionError("outcome-forcing input admitted")
    finally:
        temporary.cleanup()


def test_tracked_note7_receipt_is_self_hashed_and_reproducible() -> None:
    receipt = json.loads((PROJECT_ROOT / RECEIPT_RELATIVE).read_text(encoding="utf-8"))
    preimage = copy.deepcopy(receipt)
    assert preimage.pop("receipt_sha256") == sha256_value(preimage)
    assert receipt == build_configuration_preflight_receipt(
        admission=_load(), verification=TRACKED_VERIFICATION
    )
    assert receipt["configuration"]["canonical_sha256"] == CANONICAL_SHA256
    assert receipt["release"]["manifest_sha256"] == MANIFEST_SHA256
    serialized = json.dumps(receipt, sort_keys=True)
    assert "/home/" not in serialized and "worktree" not in serialized
