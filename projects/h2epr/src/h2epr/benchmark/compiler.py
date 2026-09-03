"""Compile the stable semantic package core and attach backends independently."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from h2epr.canonical import (
    CANONICALIZATION_VERSION,
    canonical_sha256,
    file_sha256,
    write_json,
)
from h2epr.semantic.assets import (
    AssetAdmissionError,
    StandardAssetSet,
    load_release_json,
    load_standard_assets,
)

from ._compiler_core import (
    _SemanticPackageCompileCoreError,
    _compiled_participants,
    _load_instance as _load_release_instance,
    _resolve_json_pointer,
    _validate_semantic_closure,
    _validate_rule_release,
    _derive_configuration_admission_receipt,
    _validate_configuration_value_provenance,
)


class SemanticPackageCompileError(ValueError):
    """The current core or a backend attachment violates its contract."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
BACKEND_ORDER = ("rule", "llm", "rulellm")

# Stable names for contract logic shared with the current compiler.
derive_configuration_admission_receipt = (
    _derive_configuration_admission_receipt
)
validate_configuration_value_provenance = (
    _validate_configuration_value_provenance
)


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise SemanticPackageCompileError(code)


def _validate(
    value: Mapping[str, Any],
    schema_name: str,
    label: str,
    *,
    version: int,
) -> None:
    if version not in {2, 3, 4}:
        raise SemanticPackageCompileError("schema_protocol_version_unknown")
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise SemanticPackageCompileError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def _self_hash(value: Mapping[str, Any], field: str, label: str) -> None:
    expected = canonical_sha256(
        {key: item for key, item in value.items() if key != field}
    )
    _require(value.get(field) == expected, f"{label}_self_hash_mismatch")


def _load_instance(
    assets: StandardAssetSet,
    backend: str,
    *,
    role: str,
    schema_name: str,
    hash_field: str,
    version: int,
) -> dict[str, Any]:
    try:
        value = load_release_json(assets.backend_releases[backend], role)
    except (AssetAdmissionError, KeyError) as exc:
        raise SemanticPackageCompileError(
            f"backend_release_role_unavailable:{backend}:{role}"
        ) from exc
    _validate(value, schema_name, role, version=version)
    _self_hash(value, hash_field, role)
    return value


def _component(path: Path, root: Path, artifact_id: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "relative_path": path.relative_to(root).as_posix(),
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
    }


def package_core_sha256(manifest: Mapping[str, Any]) -> str:
    """Hash semantic execution inputs while excluding backend attachment state."""

    excluded = {
        "backend_catalog_sha256",
        "backend_bindings",
        "manifest_sha256",
        "package_sha256",
    }
    return canonical_sha256(
        {key: item for key, item in manifest.items() if key not in excluded}
    )


def package_manifest_sha256(manifest: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {key: item for key, item in manifest.items() if key != "manifest_sha256"}
    )


def backend_binding_sha256(binding: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {key: item for key, item in binding.items() if key != "binding_sha256"}
    )


def _publish_package_surface(
    package_root: Path,
    manifest: Mapping[str, Any],
) -> None:
    readme = f"""# {manifest['event_id']} event package

This directory is the compiled, backend-neutral benchmark package plus its
explicitly attached backend bindings. `manifest.json` is the machine authority
for package identity, component hashes, backend availability, source exposure,
and claim limits.

Rule is attached through the registered backend factory. LLM and RuleLLM remain
planned and fail closed. Backend attachment changes the manifest identity but
cannot change `package_sha256`, which seals the shared event semantics.

`SHA256SUMS` is the exact directory inventory. A schema, parent, path, content,
provenance, implementation, or inventory mismatch rejects admission. The
package supports dataset-conditioned engineering and method verification only;
it establishes no historical fit, calibration, held-out result, causal claim,
scientific validity, or universal generality.
"""
    (package_root / "README.md").write_text(readme, encoding="utf-8")
    rows = []
    for path in sorted(package_root.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            rows.append(
                f"{file_sha256(path)}  "
                f"{path.relative_to(package_root).as_posix()}"
            )
    (package_root / "SHA256SUMS").write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def validate_configuration_provenance_coverage(
    configuration: Mapping[str, Any],
    coverage: Mapping[str, Any],
    label: str,
) -> None:
    """Close every selected top-level setting to provenance or an exemption."""

    _validate(
        coverage,
        "configuration-provenance-coverage.schema.json",
        f"{label}_provenance_coverage",
        version=4,
    )
    _self_hash(
        coverage,
        "coverage_sha256",
        f"{label}_provenance_coverage",
    )
    _require(
        coverage["configuration_id"] == configuration["configuration_id"]
        and coverage["configuration_sha256"]
        == configuration["configuration_sha256"],
        f"{label}_provenance_configuration_identity_mismatch",
    )
    expected = {f"/settings/{key}" for key in configuration["settings"]}
    declared = {row["json_pointer"] for row in configuration["value_provenance"]}
    covered = set(coverage["covered_setting_pointers"])
    exempted = {row["json_pointer"] for row in coverage["exemptions"]}
    _require(
        declared == covered,
        f"{label}_provenance_declaration_coverage_mismatch",
    )
    _require(
        not (covered & exempted),
        f"{label}_provenance_coverage_exemption_overlap",
    )
    _require(
        covered | exempted == expected,
        f"{label}_provenance_top_level_incomplete",
    )
    for pointer in sorted(covered | exempted):
        try:
            _resolve_json_pointer(configuration, pointer, label)
        except _SemanticPackageCompileCoreError as exc:
            raise SemanticPackageCompileError(str(exc)) from exc


def _load_assets_and_semantics(
    *, project_root: Path, data_root: Path, assembly_path: Path
) -> tuple[StandardAssetSet, dict[str, dict[str, Any]]]:
    try:
        assets = load_standard_assets(
            project_root=project_root,
            data_root=data_root,
            assembly_path=assembly_path,
        )
        roster_release = assets.releases["roster"]
        interface_release = assets.releases["participant_interfaces"]
        scenario_release = assets.releases["scenario_definition"]
        configuration_release = assets.releases["scenario_configuration"]
        values = {
            "roster": _load_release_instance(
                roster_release,
                role="participant_roster",
                schema_name="participant-roster.schema.json",
                hash_field="roster_sha256",
                version=2,
            ),
            "actor_map": _load_release_instance(
                roster_release,
                role="actor_map",
                schema_name="actor-map.schema.json",
                hash_field="actor_map_sha256",
                version=2,
            ),
            "observation_registry": _load_release_instance(
                interface_release,
                role="observation_registry",
                schema_name="observation-registry.schema.json",
                hash_field="registry_sha256",
                version=2,
            ),
            "intent_registry": _load_release_instance(
                interface_release,
                role="intent_registry",
                schema_name="intent-registry.schema.json",
                hash_field="registry_sha256",
                version=2,
            ),
            "lifecycle_registry": _load_release_instance(
                interface_release,
                role="lifecycle_registry",
                schema_name="lifecycle-registry.schema.json",
                hash_field="registry_sha256",
                version=2,
            ),
            "participant_interface": _load_release_instance(
                interface_release,
                role="participant_interface",
                schema_name="participant-interface.schema.json",
                hash_field="interface_sha256",
                version=2,
            ),
            "participant_semantic_index": _load_release_instance(
                interface_release,
                role="participant_semantic_index",
                schema_name="participant-semantic-index.schema.json",
                hash_field="index_sha256",
                version=3,
            ),
            "scenario_interface": _load_release_instance(
                scenario_release,
                role="scenario_interface",
                schema_name="scenario-interface.schema.json",
                hash_field="scenario_interface_sha256",
                version=2,
            ),
            "shared_configuration": _load_release_instance(
                configuration_release,
                role="scenario_configuration",
                schema_name="scenario-configuration.schema.json",
                hash_field="configuration_sha256",
                version=3,
            ),
            "configuration_admission": _load_release_instance(
                configuration_release,
                role="configuration_admission_receipt",
                schema_name="configuration-admission-receipt.schema.json",
                hash_field="receipt_sha256",
                version=3,
            ),
        }
        mechanism = load_release_json(
            scenario_release,
            "scenario_mechanism",
        )
        _validate(
            mechanism,
            "scenario-mechanism.schema.json",
            "scenario_mechanism",
            version=4,
        )
        _self_hash(mechanism, "mechanism_sha256", "scenario_mechanism")
        values["scenario_mechanism"] = mechanism
        event_ids = {
            assets.assembly["event_id"],
            *(
                row["event_id"]
                for key, row in values.items()
                if key != "configuration_admission"
            ),
        }
        _require(
            len(event_ids) == 1,
            "semantic_instance_event_identity_mismatch",
        )
        _validate_configuration_value_provenance(
            values["shared_configuration"],
            "shared_configuration",
        )
        _validate_semantic_closure(
            assets,  # type: ignore[arg-type]
            values,
            expected_environment_implementation_id=(
                "h2epr.environment.declarative.v4"
            ),
        )
        coverage = load_release_json(
            assets.releases["scenario_configuration"],
            "configuration_provenance_coverage",
        )
        validate_configuration_provenance_coverage(
            values["shared_configuration"],
            coverage,
            "shared_configuration",
        )
        values["shared_configuration_provenance"] = coverage
    except (AssetAdmissionError, _SemanticPackageCompileCoreError) as exc:
        raise SemanticPackageCompileError(str(exc)) from exc
    return assets, values


def _compiled_scenario(
    values: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    interface = values["participant_interface"]
    scenario_interface = values["scenario_interface"]
    mechanism = values["scenario_mechanism"]
    configuration = values["shared_configuration"]
    settings = configuration["settings"]
    result = {
        "schema_version": "h2epr.compiled-scenario.v4",
        "event_id": configuration["event_id"],
        "scenario_id": scenario_interface["scenario_interface_id"].replace(
            "scenario-interface", "compiled-scenario"
        ),
        "scenario_interface_id": scenario_interface["scenario_interface_id"],
        "mechanism_id": mechanism["mechanism_id"],
        "mechanism_sha256": mechanism["mechanism_sha256"],
        "configuration_id": configuration["configuration_id"],
        "configuration_sha256": configuration["configuration_sha256"],
        "purpose": settings["purpose"],
        "exposure_mode": settings["exposure_mode"],
        "timeline": copy.deepcopy(settings["timeline"]),
        "active_actor_ids": copy.deepcopy(settings["active_actor_ids"]),
        "action_spaces": {
            row["actor_id"]: copy.deepcopy(row["intent_ids"])
            for row in sorted(
                interface["actors"], key=lambda item: item["actor_id"]
            )
        },
        "communication_routes": copy.deepcopy(
            settings["communication_routes"]
        ),
        "initial_state": copy.deepcopy(settings["initial_state"]),
        "mechanism": copy.deepcopy(mechanism),
        "observation_contract": copy.deepcopy(
            settings["observation_contract"]
        ),
        "termination": copy.deepcopy(settings["termination"]),
        "assumptions": copy.deepcopy(settings["assumptions"]),
    }
    _validate(
        result,
        "compiled-scenario.schema.json",
        "compiled_scenario",
        version=4,
    )
    return result


def compile_event_package_core(
    *,
    project_root: Path,
    data_root: Path,
    assembly_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Compile only backend-neutral bytes; all backend rows remain unattached."""

    if output_root.exists():
        raise FileExistsError("event_package_output_root_must_be_absent")
    assets, values = _load_assets_and_semantics(
        project_root=project_root,
        data_root=data_root,
        assembly_path=assembly_path,
    )
    participants = _compiled_participants(values)
    scenario = _compiled_scenario(values)

    output_root.mkdir(parents=True)
    paths = {
        "source_profile": output_root / "source-profile.json",
        "semantic_assets": output_root / "semantic-assets.json",
        "compiled_participants": output_root / "participants.json",
        "participant_interface": output_root / "participant-interface.json",
        "participant_semantic_index": output_root
        / "participant-semantic-index.json",
        "compiled_scenario": output_root / "scenario.json",
        "shared_configuration": output_root / "shared-configuration.json",
        "shared_configuration_provenance": output_root
        / "shared-configuration-provenance.json",
    }
    write_json(paths["source_profile"], assets.source_profile)
    write_json(paths["compiled_participants"], participants)
    write_json(paths["participant_interface"], values["participant_interface"])
    write_json(
        paths["participant_semantic_index"],
        values["participant_semantic_index"],
    )
    write_json(paths["compiled_scenario"], scenario)
    write_json(paths["shared_configuration"], values["shared_configuration"])
    write_json(
        paths["shared_configuration_provenance"],
        values["shared_configuration_provenance"],
    )

    semantic_index = {
        "schema_version": "h2epr.semantic-asset-index.v4",
        "index_id": assets.assembly["assembly_id"].replace(
            "assembly", "semantic-index"
        ),
        "index_version": assets.assembly["assembly_version"],
        "event_id": assets.assembly["event_id"],
        "assembly_id": assets.assembly["assembly_id"],
        "semantic_assembly_sha256": assets.assembly[
            "semantic_assembly_sha256"
        ],
        "source_profile_id": assets.source_profile["profile_id"],
        "releases": [
            {
                "release_kind": kind,
                "release_id": release.manifest["release_id"],
                "manifest_sha256": release.manifest["manifest_sha256"],
                "source_relative_path": release.root.relative_to(
                    assets.project_root
                ).as_posix(),
            }
            for kind, release in sorted(assets.releases.items())
        ],
        "index_sha256": "0" * 64,
    }
    semantic_index["index_sha256"] = canonical_sha256(
        {
            key: item
            for key, item in semantic_index.items()
            if key != "index_sha256"
        }
    )
    _validate(
        semantic_index,
        "semantic-asset-index.schema.json",
        "semantic_asset_index",
        version=4,
    )
    write_json(paths["semantic_assets"], semantic_index)

    components = [
        _component(
            paths["compiled_participants"],
            output_root,
            "compiled_participants",
        ),
        _component(
            paths["participant_interface"],
            output_root,
            "participant_interface",
        ),
        _component(
            paths["participant_semantic_index"],
            output_root,
            "participant_semantic_index",
        ),
        _component(
            paths["compiled_scenario"],
            output_root,
            "compiled_scenario",
        ),
        _component(
            paths["shared_configuration"],
            output_root,
            "shared_configuration",
        ),
        _component(
            paths["shared_configuration_provenance"],
            output_root,
            "shared_configuration_provenance",
        ),
    ]
    manifest = {
        "schema_version": "h2epr.event-package.manifest.v4",
        "package_id": assets.assembly["package_id"],
        "package_version": assets.assembly["package_version"],
        "event_id": assets.assembly["event_id"],
        "canonicalization_version": CANONICALIZATION_VERSION,
        "source_profile": _component(
            paths["source_profile"],
            output_root,
            assets.source_profile["profile_id"],
        ),
        "source_exposure": assets.source_profile["exposure_mode"],
        "protocol_eligibility": assets.source_profile["protocol_eligibility"],
        "semantic_assembly_sha256": assets.assembly[
            "semantic_assembly_sha256"
        ],
        "semantic_assets": _component(
            paths["semantic_assets"],
            output_root,
            semantic_index["index_id"],
        ),
        "components": components,
        "backend_catalog_sha256": assets.assembly["backend_catalog_sha256"],
        "backend_bindings": [
            {"backend": backend, "status": "planned"}
            for backend in BACKEND_ORDER
        ],
        "claim_boundary": copy.deepcopy(assets.source_profile["claim_boundary"]),
        "package_sha256": "0" * 64,
        "manifest_sha256": "0" * 64,
    }
    manifest["package_sha256"] = package_core_sha256(manifest)
    manifest["manifest_sha256"] = package_manifest_sha256(manifest)
    _validate(
        manifest,
        "event-package-manifest.schema.json",
        "package_manifest",
        version=4,
    )
    write_json(output_root / "manifest.json", manifest)
    return copy.deepcopy(manifest)


def _build_rule_binding(
    *,
    assets: StandardAssetSet,
    values: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
    output_root: Path,
) -> tuple[dict[str, Any], Path]:
    backend = "rule"
    realization = _load_instance(
        assets,
        backend,
        role="backend_realization",
        schema_name="backend-realization.schema.json",
        hash_field="realization_sha256",
        version=2,
    )
    configuration = _load_instance(
        assets,
        backend,
        role="backend_configuration",
        schema_name="scenario-configuration.schema.json",
        hash_field="configuration_sha256",
        version=3,
    )
    admission = _load_instance(
        assets,
        backend,
        role="backend_configuration_admission_receipt",
        schema_name="configuration-admission-receipt.schema.json",
        hash_field="receipt_sha256",
        version=3,
    )
    provenance = _load_instance(
        assets,
        backend,
        role="backend_configuration_provenance_coverage",
        schema_name="configuration-provenance-coverage.schema.json",
        hash_field="coverage_sha256",
        version=4,
    )
    validate_configuration_provenance_coverage(
        configuration,
        provenance,
        "backend_configuration",
    )
    try:
        _validate_rule_release(
            assets=assets,  # type: ignore[arg-type]
            values=values,
            realization=realization,
            backend_configuration=configuration,
            backend_configuration_admission=admission,
            expected_implementation_id="h2epr.backend.rule.declarative.v4",
        )
    except _SemanticPackageCompileCoreError as exc:
        raise SemanticPackageCompileError(str(exc)) from exc

    binding_root = output_root / "backend-bindings"
    binding_root.mkdir(exist_ok=True)
    realization_path = binding_root / "rule-realization.json"
    configuration_path = binding_root / "rule-configuration.json"
    provenance_path = binding_root / "rule-configuration-provenance.json"
    write_json(realization_path, realization)
    write_json(configuration_path, configuration)
    write_json(provenance_path, provenance)
    scenario = _compiled_scenario(values)
    settings = configuration["settings"]
    binding = {
        "schema_version": "h2epr.backend-binding.v4",
        "binding_id": f"{manifest['package_id']}.rule-binding",
        "binding_version": assets.assembly["package_version"],
        "event_id": manifest["event_id"],
        "package_sha256": manifest["package_sha256"],
        "backend": backend,
        "decision_interface": "h2epr.participant-decision.v2",
        "realization_id": realization["realization_id"],
        "realization_sha256": realization["realization_sha256"],
        "realization_relative_path": realization_path.name,
        "configuration_id": configuration["configuration_id"],
        "configuration_sha256": configuration["configuration_sha256"],
        "configuration_relative_path": configuration_path.name,
        "configuration_provenance_coverage_id": provenance["coverage_id"],
        "configuration_provenance_coverage_sha256": provenance[
            "coverage_sha256"
        ],
        "configuration_provenance_relative_path": provenance_path.name,
        "implementation_id": realization["implementation_id"],
        "implementation_version": realization["realization_version"],
        "actor_ids": copy.deepcopy(scenario["active_actor_ids"]),
        "action_spaces": copy.deepcopy(scenario["action_spaces"]),
        "run_defaults": {
            "seed": 0,
            "tick_count": len(scenario["timeline"]),
        },
        "deterministic": settings["deterministic"],
        "model_access": settings["model_access"],
        "network_access": settings["network_access"],
        "failure_routing": copy.deepcopy(realization["failure_routing"]),
        "implementation_sources": copy.deepcopy(
            realization["implementation_sources"]
        ),
        "binding_sha256": "0" * 64,
    }
    binding["binding_sha256"] = backend_binding_sha256(binding)
    _validate(
        binding,
        "backend-binding.schema.json",
        "rule_binding",
        version=4,
    )
    binding_path = binding_root / "rule.json"
    write_json(binding_path, binding)
    return binding, binding_path


BACKEND_ATTACHMENT_BUILDERS = {
    "rule": _build_rule_binding,
}


def attach_backend(
    *,
    project_root: Path,
    data_root: Path,
    assembly_path: Path,
    package_root: Path,
    backend: str,
) -> dict[str, Any]:
    """Attach one implemented backend without changing package core identity."""

    _require(backend in BACKEND_ORDER, f"backend_unknown:{backend}")
    assets, values = _load_assets_and_semantics(
        project_root=project_root,
        data_root=data_root,
        assembly_path=assembly_path,
    )
    manifest_path = package_root / "manifest.json"
    _require(manifest_path.is_file(), "package_manifest_missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate(
        manifest,
        "event-package-manifest.schema.json",
        "package_manifest",
        version=4,
    )
    original_core = manifest["package_sha256"]
    _require(
        original_core == package_core_sha256(manifest),
        "package_core_hash_mismatch",
    )
    _require(
        manifest["semantic_assembly_sha256"]
        == assets.assembly["semantic_assembly_sha256"],
        "package_semantic_assembly_mismatch",
    )
    _require(
        manifest["backend_catalog_sha256"]
        == assets.assembly["backend_catalog_sha256"],
        "package_backend_catalog_mismatch",
    )
    declaration = assets.assembly["backend_releases"][backend]
    _require(
        declaration["status"] == "implemented",
        f"backend_not_implemented:{backend}",
    )
    selected = next(
        row for row in manifest["backend_bindings"] if row["backend"] == backend
    )
    _require(selected["status"] == "planned", f"backend_already_attached:{backend}")

    _require(
        backend in BACKEND_ATTACHMENT_BUILDERS,
        f"backend_factory_unavailable:{backend}",
    )
    binding, binding_path = BACKEND_ATTACHMENT_BUILDERS[backend](
        assets=assets,
        values=values,
        manifest=manifest,
        output_root=package_root,
    )
    replacement = {
        "backend": backend,
        "status": "implemented",
        "binding_id": binding["binding_id"],
        "binding_sha256": binding["binding_sha256"],
        "relative_path": binding_path.relative_to(package_root).as_posix(),
        "sha256": file_sha256(binding_path),
        "size_bytes": binding_path.stat().st_size,
    }
    manifest["backend_bindings"] = [
        replacement if row["backend"] == backend else row
        for row in manifest["backend_bindings"]
    ]
    _require(
        package_core_sha256(manifest) == original_core,
        "backend_attachment_changed_package_core",
    )
    manifest["manifest_sha256"] = package_manifest_sha256(manifest)
    _validate(
        manifest,
        "event-package-manifest.schema.json",
        "package_manifest",
        version=4,
    )
    write_json(manifest_path, manifest)
    return copy.deepcopy(manifest)


def compile_event_package(
    *,
    project_root: Path,
    data_root: Path,
    assembly_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Atomically compile the core and every declared implemented attachment."""

    if output_root.exists():
        raise FileExistsError("event_package_output_root_must_be_absent")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{output_root.name}.compile-",
            dir=output_root.parent,
        )
    )
    try:
        compile_event_package_core(
            project_root=project_root,
            data_root=data_root,
            assembly_path=assembly_path,
            output_root=temporary / "package",
        )
        assets = load_standard_assets(
            project_root=project_root,
            data_root=data_root,
            assembly_path=assembly_path,
        )
        for backend in BACKEND_ORDER:
            if assets.assembly["backend_releases"][backend]["status"] == "implemented":
                attach_backend(
                    project_root=project_root,
                    data_root=data_root,
                    assembly_path=assembly_path,
                    package_root=temporary / "package",
                    backend=backend,
                )
        manifest = json.loads(
            (temporary / "package" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        _publish_package_surface(temporary / "package", manifest)
        (temporary / "package").rename(output_root)
        return manifest
    except Exception:
        if output_root.exists():
            shutil.rmtree(output_root)
        raise
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


__all__ = [
    "BACKEND_ATTACHMENT_BUILDERS",
    "BACKEND_ORDER",
    "SemanticPackageCompileError",
    "attach_backend",
    "backend_binding_sha256",
    "compile_event_package_core",
    "compile_event_package",
    "derive_configuration_admission_receipt",
    "package_core_sha256",
    "package_manifest_sha256",
    "validate_configuration_provenance_coverage",
    "validate_configuration_value_provenance",
]
