"""Fail-closed loading for the current core and selected backend attachment."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from h2epr.canonical import canonical_sha256, file_sha256

from .compiler import (
    BACKEND_ORDER,
    backend_binding_sha256,
    package_core_sha256,
    package_manifest_sha256,
    validate_configuration_provenance_coverage,
)


class EventPackageError(ValueError):
    """A package core, attachment, or implementation source is invalid."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
ALLOWED_NAMES = ("event_spec", "frozen_evidence", "draft_epg")


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise EventPackageError(code)


def _read_json(path: Path, boundary: Path, label: str) -> dict[str, Any]:
    _require(
        path.is_file() and not path.is_symlink(),
        f"{label}_missing_or_unsafe",
    )
    try:
        path.resolve().relative_to(boundary.resolve())
    except ValueError as exc:
        raise EventPackageError(f"{label}_escapes_boundary") from exc
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EventPackageError(f"{label}_parse_failure") from exc
    _require(isinstance(value, dict), f"{label}_shape_invalid")
    return value


def _safe_path(root: Path, relative_path: Any, label: str) -> Path:
    _require(
        isinstance(relative_path, str) and bool(relative_path),
        f"{label}_path_invalid",
    )
    relative = Path(relative_path)
    _require(
        not relative.is_absolute() and ".." not in relative.parts,
        f"{label}_path_unsafe",
    )
    path = root / relative
    _require(
        path.is_file() and not path.is_symlink(),
        f"{label}_missing_or_unsafe",
    )
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise EventPackageError(f"{label}_escapes_root") from exc
    return path


def _validate(
    value: Mapping[str, Any],
    schema_name: str,
    label: str,
    *,
    version: int,
) -> None:
    if version not in {2, 3, 4}:
        raise EventPackageError("schema_protocol_version_unknown")
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise EventPackageError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def _self_hash(value: Mapping[str, Any], field: str, label: str) -> None:
    expected = canonical_sha256(
        {key: item for key, item in value.items() if key != field}
    )
    _require(value.get(field) == expected, f"{label}_self_hash_mismatch")


def _verify_file_ref(root: Path, row: Mapping[str, Any], label: str) -> Path:
    path = _safe_path(root, row.get("relative_path"), label)
    _require(
        path.stat().st_size == row.get("size_bytes"),
        f"{label}_size_mismatch",
    )
    _require(file_sha256(path) == row.get("sha256"), f"{label}_hash_mismatch")
    return path


def _verify_source_profile(profile: Mapping[str, Any], data_root: Path) -> None:
    _validate(
        profile,
        "source-profile.schema.json",
        "source_profile",
        version=3,
    )
    _self_hash(profile, "profile_sha256", "source_profile")
    names = tuple(row["logical_name"] for row in profile["allowed_inputs"])
    _require(names == ALLOWED_NAMES, "source_profile_logical_name_sequence_mismatch")
    for row in profile["allowed_inputs"]:
        expected = (
            Path("development_samples_v1")
            / "events"
            / profile["event_id"]
            / f"{row['logical_name']}.json"
        ).as_posix()
        _require(
            row["relative_path"] == expected,
            f"source_direct_path_mismatch:{row['logical_name']}",
        )
        path = _safe_path(
            data_root,
            row["relative_path"],
            f"source:{row['logical_name']}",
        )
        _require(
            path.stat().st_size == row["size_bytes"],
            f"source_size_mismatch:{row['logical_name']}",
        )
        _require(
            file_sha256(path) == row["sha256"],
            f"source_hash_mismatch:{row['logical_name']}",
        )


def _verify_implementation_sources(rows: list[Mapping[str, Any]]) -> None:
    paths = [row["relative_path"] for row in rows]
    _require(len(paths) == len(set(paths)), "implementation_source_duplicate")
    for row in rows:
        relative = Path(row["relative_path"])
        _require(
            not relative.is_absolute() and ".." not in relative.parts,
            "implementation_source_path_unsafe",
        )
        path = PROJECT_ROOT / relative
        _require(
            path.is_file() and not path.is_symlink(),
            f"implementation_source_missing:{row['relative_path']}",
        )
        _require(
            file_sha256(path) == row["sha256"],
            f"implementation_source_hash_mismatch:{row['relative_path']}",
        )


@dataclass(frozen=True)
class EventPackage:
    root: Path
    manifest: dict[str, Any]
    source_profile: dict[str, Any]
    semantic_assets: dict[str, Any]
    participants: dict[str, Any]
    participant_interface: dict[str, Any]
    participant_semantic_index: dict[str, Any]
    scenario: dict[str, Any]
    shared_configuration: dict[str, Any]
    shared_configuration_provenance: dict[str, Any]
    binding: dict[str, Any]
    realization: dict[str, Any]
    backend_configuration: dict[str, Any]
    backend_configuration_provenance: dict[str, Any]

    @property
    def package_sha256(self) -> str:
        return self.manifest["package_sha256"]

    @property
    def binding_sha256(self) -> str:
        return self.binding["binding_sha256"]


def load_event_package(
    package_root: Path,
    data_root: Path,
    backend: str = "rule",
) -> EventPackage:
    _require(backend in BACKEND_ORDER, f"backend_unknown:{backend}")
    _require(
        package_root.is_dir() and not package_root.is_symlink(),
        "package_root_missing_or_unsafe",
    )
    package_root = package_root.resolve()
    manifest = _read_json(package_root / "manifest.json", package_root, "manifest")
    _validate(
        manifest,
        "event-package-manifest.schema.json",
        "manifest",
        version=4,
    )
    _require(
        manifest["package_sha256"] == package_core_sha256(manifest),
        "package_hash_mismatch",
    )
    _require(
        manifest["manifest_sha256"] == package_manifest_sha256(manifest),
        "manifest_hash_mismatch",
    )

    profile_path = _verify_file_ref(
        package_root,
        manifest["source_profile"],
        "source_profile",
    )
    semantic_path = _verify_file_ref(
        package_root,
        manifest["semantic_assets"],
        "semantic_assets",
    )
    source_profile = _read_json(profile_path, package_root, "source_profile")
    semantic_assets = _read_json(semantic_path, package_root, "semantic_assets")
    _verify_source_profile(source_profile, data_root.resolve())
    _validate(
        semantic_assets,
        "semantic-asset-index.schema.json",
        "semantic_assets",
        version=4,
    )
    _self_hash(semantic_assets, "index_sha256", "semantic_assets")
    _require(
        source_profile["profile_id"] == manifest["source_profile"]["artifact_id"],
        "source_profile_id_mismatch",
    )
    _require(
        source_profile["event_id"] == manifest["event_id"],
        "source_profile_event_mismatch",
    )
    _require(
        semantic_assets["event_id"] == manifest["event_id"],
        "semantic_assets_event_mismatch",
    )
    _require(
        semantic_assets["semantic_assembly_sha256"]
        == manifest["semantic_assembly_sha256"],
        "semantic_assembly_identity_mismatch",
    )

    component_rows = manifest["components"]
    by_id = {row["artifact_id"]: row for row in component_rows}
    _require(
        len(by_id) == len(component_rows),
        "component_artifact_id_duplicate",
    )
    required = {
        "compiled_participants",
        "participant_interface",
        "participant_semantic_index",
        "compiled_scenario",
        "shared_configuration",
        "shared_configuration_provenance",
    }
    _require(set(by_id) == required, "component_universe_mismatch")
    paths = {
        artifact_id: _verify_file_ref(
            package_root,
            row,
            f"component:{artifact_id}",
        )
        for artifact_id, row in by_id.items()
    }
    participants = _read_json(
        paths["compiled_participants"],
        package_root,
        "compiled_participants",
    )
    participant_interface = _read_json(
        paths["participant_interface"],
        package_root,
        "participant_interface",
    )
    participant_semantic_index = _read_json(
        paths["participant_semantic_index"],
        package_root,
        "participant_semantic_index",
    )
    scenario = _read_json(
        paths["compiled_scenario"],
        package_root,
        "compiled_scenario",
    )
    shared_configuration = _read_json(
        paths["shared_configuration"],
        package_root,
        "shared_configuration",
    )
    shared_configuration_provenance = _read_json(
        paths["shared_configuration_provenance"],
        package_root,
        "shared_configuration_provenance",
    )
    _validate(
        participants,
        "compiled-participants.schema.json",
        "compiled_participants",
        version=2,
    )
    _validate(
        participant_interface,
        "participant-interface.schema.json",
        "participant_interface",
        version=2,
    )
    _validate(
        participant_semantic_index,
        "participant-semantic-index.schema.json",
        "participant_semantic_index",
        version=3,
    )
    _validate(
        scenario,
        "compiled-scenario.schema.json",
        "compiled_scenario",
        version=4,
    )
    _validate(
        shared_configuration,
        "scenario-configuration.schema.json",
        "shared_configuration",
        version=3,
    )
    _validate(
        shared_configuration_provenance,
        "configuration-provenance-coverage.schema.json",
        "shared_configuration_provenance",
        version=4,
    )
    _self_hash(participant_interface, "interface_sha256", "participant_interface")
    _self_hash(
        participant_semantic_index,
        "index_sha256",
        "participant_semantic_index",
    )
    _self_hash(
        shared_configuration,
        "configuration_sha256",
        "shared_configuration",
    )
    _self_hash(
        shared_configuration_provenance,
        "coverage_sha256",
        "shared_configuration_provenance",
    )
    _require(
        shared_configuration_provenance["configuration_id"]
        == shared_configuration["configuration_id"]
        and shared_configuration_provenance["configuration_sha256"]
        == shared_configuration["configuration_sha256"],
        "shared_configuration_provenance_identity_mismatch",
    )
    validate_configuration_provenance_coverage(
        shared_configuration,
        shared_configuration_provenance,
        "shared_configuration",
    )
    _validate(
        scenario["mechanism"],
        "scenario-mechanism.schema.json",
        "scenario_mechanism",
        version=4,
    )
    _self_hash(scenario["mechanism"], "mechanism_sha256", "scenario_mechanism")

    active_ids = scenario["active_actor_ids"]
    runtime_ids = sorted(row["actor_id"] for row in participants["runtime_actors"])
    interface_ids = sorted(
        row["actor_id"] for row in participant_interface["actors"]
    )
    semantic_ids = sorted(
        row["actor_id"] for row in participant_semantic_index["parents"]
    )
    _require(
        runtime_ids == interface_ids == semantic_ids == active_ids,
        "package_actor_closure_failure",
    )
    _require(
        scenario["configuration_sha256"]
        == shared_configuration["configuration_sha256"],
        "scenario_configuration_identity_mismatch",
    )
    _require(
        scenario["mechanism_sha256"] == scenario["mechanism"]["mechanism_sha256"],
        "scenario_mechanism_identity_mismatch",
    )
    _require(
        scenario["exposure_mode"] == manifest["source_exposure"],
        "scenario_exposure_mode_mismatch",
    )

    backend_rows = manifest["backend_bindings"]
    _require(
        [row["backend"] for row in backend_rows] == list(BACKEND_ORDER),
        "backend_catalog_order_mismatch",
    )
    selected = next(row for row in backend_rows if row["backend"] == backend)
    if selected["status"] != "implemented":
        raise EventPackageError(f"backend_not_implemented:{backend}")
    binding_path = _verify_file_ref(
        package_root,
        selected,
        f"binding:{backend}",
    )
    binding = _read_json(binding_path, package_root, f"binding:{backend}")
    _validate(
        binding,
        "backend-binding.schema.json",
        f"binding:{backend}",
        version=4,
    )
    _require(
        binding["binding_sha256"] == backend_binding_sha256(binding),
        "binding_hash_mismatch",
    )
    _require(binding["binding_id"] == selected["binding_id"], "binding_id_mismatch")
    _require(
        binding["binding_sha256"] == selected["binding_sha256"],
        "binding_identity_mismatch",
    )
    _require(
        binding["package_sha256"] == manifest["package_sha256"],
        "binding_package_identity_mismatch",
    )
    _require(
        binding["event_id"] == manifest["event_id"],
        "binding_event_identity_mismatch",
    )
    _require(binding["backend"] == backend, "binding_backend_mismatch")
    _require(binding["actor_ids"] == active_ids, "binding_actor_universe_mismatch")
    _require(
        binding["action_spaces"] == scenario["action_spaces"],
        "binding_action_space_mismatch",
    )
    _require(
        binding["run_defaults"]["tick_count"] == len(scenario["timeline"]),
        "binding_tick_count_mismatch",
    )

    binding_root = binding_path.parent
    realization_path = _safe_path(
        binding_root,
        binding["realization_relative_path"],
        "backend_realization",
    )
    configuration_path = _safe_path(
        binding_root,
        binding["configuration_relative_path"],
        "backend_configuration",
    )
    provenance_path = _safe_path(
        binding_root,
        binding["configuration_provenance_relative_path"],
        "backend_configuration_provenance",
    )
    realization = _read_json(
        realization_path,
        package_root,
        "backend_realization",
    )
    backend_configuration = _read_json(
        configuration_path,
        package_root,
        "backend_configuration",
    )
    backend_configuration_provenance = _read_json(
        provenance_path,
        package_root,
        "backend_configuration_provenance",
    )
    _validate(
        realization,
        "backend-realization.schema.json",
        "backend_realization",
        version=2,
    )
    _validate(
        backend_configuration,
        "scenario-configuration.schema.json",
        "backend_configuration",
        version=3,
    )
    _validate(
        backend_configuration_provenance,
        "configuration-provenance-coverage.schema.json",
        "backend_configuration_provenance",
        version=4,
    )
    _self_hash(realization, "realization_sha256", "backend_realization")
    _self_hash(
        backend_configuration,
        "configuration_sha256",
        "backend_configuration",
    )
    _self_hash(
        backend_configuration_provenance,
        "coverage_sha256",
        "backend_configuration_provenance",
    )
    _require(
        realization["event_id"]
        == backend_configuration["event_id"]
        == manifest["event_id"],
        "backend_attachment_event_identity_mismatch",
    )
    _require(realization["backend"] == backend, "realization_backend_mismatch")
    _require(
        realization["realization_id"] == binding["realization_id"],
        "binding_realization_id_mismatch",
    )
    _require(
        realization["realization_sha256"] == binding["realization_sha256"],
        "binding_realization_hash_mismatch",
    )
    _require(
        backend_configuration["configuration_id"] == binding["configuration_id"],
        "binding_configuration_id_mismatch",
    )
    _require(
        backend_configuration["configuration_sha256"]
        == binding["configuration_sha256"],
        "binding_configuration_hash_mismatch",
    )
    _require(
        backend_configuration_provenance["coverage_id"]
        == binding["configuration_provenance_coverage_id"]
        and backend_configuration_provenance["coverage_sha256"]
        == binding["configuration_provenance_coverage_sha256"]
        and backend_configuration_provenance["configuration_id"]
        == backend_configuration["configuration_id"]
        and backend_configuration_provenance["configuration_sha256"]
        == backend_configuration["configuration_sha256"],
        "binding_configuration_provenance_identity_mismatch",
    )
    validate_configuration_provenance_coverage(
        backend_configuration,
        backend_configuration_provenance,
        "backend_configuration",
    )
    _require(
        realization["configuration_id"]
        == backend_configuration["configuration_id"],
        "realization_configuration_mismatch",
    )
    _require(
        realization["implementation_id"] == binding["implementation_id"],
        "realization_implementation_mismatch",
    )
    _require(
        realization["implementation_sources"] == binding["implementation_sources"],
        "implementation_source_inventory_mismatch",
    )
    _verify_implementation_sources(realization["implementation_sources"])

    return EventPackage(
        package_root,
        manifest,
        source_profile,
        semantic_assets,
        participants,
        participant_interface,
        participant_semantic_index,
        scenario,
        shared_configuration,
        shared_configuration_provenance,
        binding,
        realization,
        backend_configuration,
        backend_configuration_provenance,
    )


__all__ = ["EventPackage", "EventPackageError", "load_event_package"]
