"""Fail-closed admission for the current package core and backend catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from h2epr.canonical import canonical_sha256, file_sha256

from ._assets_core import (
    ALLOWED_LOGICAL_NAMES,
    REQUIRED_CLAIM_EXCLUSIONS,
    REQUIRED_PROHIBITIONS,
    _AssetAdmissionCoreError,
    _ReleaseAssets,
    _load_release,
    _read_json,
    _release_artifact_path as _core_release_artifact_path,
    _safe_file,
    _self_hash,
    _validate_schema,
    _validate_source_documents,
)


class AssetAdmissionError(_AssetAdmissionCoreError):
    """An assembly identity or one of its admitted parents is invalid."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise AssetAdmissionError(code)


def _release_artifact_path(
    release_root: Path,
    project_root: Path,
    relative_path: Any,
    label: str,
    *,
    cross_release_role: str | None = None,
) -> Path:
    """Apply the stable release-path boundary and normalize its typed error."""

    try:
        return _core_release_artifact_path(
            release_root,
            project_root,
            relative_path,
            label,
            cross_release_role=cross_release_role,
        )
    except _AssetAdmissionCoreError as exc:
        raise AssetAdmissionError(str(exc)) from exc


def _validate_current(value: Mapping[str, Any], schema_name: str, label: str) -> None:
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise AssetAdmissionError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def semantic_assembly_sha256(assembly: Mapping[str, Any]) -> str:
    """Seal only the semantic package inputs, never backend availability."""

    excluded = {
        "backend_releases",
        "semantic_assembly_sha256",
        "backend_catalog_sha256",
        "assembly_sha256",
    }
    return canonical_sha256(
        {key: value for key, value in assembly.items() if key not in excluded}
    )


def backend_catalog_sha256(assembly: Mapping[str, Any]) -> str:
    """Seal backend status and releases against one semantic assembly."""

    return canonical_sha256(
        {
            "semantic_assembly_sha256": assembly["semantic_assembly_sha256"],
            "backend_releases": assembly["backend_releases"],
        }
    )


def assembly_sha256(assembly: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in assembly.items() if key != "assembly_sha256"}
    )


@dataclass(frozen=True)
class StandardAssetSet:
    project_root: Path
    data_root: Path
    assembly_path: Path
    assembly: dict[str, Any]
    source_profile_path: Path
    source_profile: dict[str, Any]
    source_documents: dict[str, dict[str, Any]]
    releases: dict[str, _ReleaseAssets]
    backend_releases: dict[str, _ReleaseAssets]


def load_standard_assets(
    *, project_root: Path, data_root: Path, assembly_path: Path
) -> StandardAssetSet:
    project_root = project_root.resolve()
    data_root = data_root.resolve()
    try:
        assembly = _read_json(assembly_path, project_root, "package_assembly")
        _validate_current(
            assembly,
            "event-package-assembly.schema.json",
            "package_assembly",
        )
        _require(
            assembly["semantic_assembly_sha256"]
            == semantic_assembly_sha256(assembly),
            "semantic_assembly_hash_mismatch",
        )
        _require(
            assembly["backend_catalog_sha256"]
            == backend_catalog_sha256(assembly),
            "backend_catalog_hash_mismatch",
        )
        _require(
            assembly["assembly_sha256"] == assembly_sha256(assembly),
            "package_assembly_self_hash_mismatch",
        )

        profile_row = assembly["source_profile"]
        profile_path = _safe_file(
            project_root,
            profile_row["relative_path"],
            "source_profile",
        )
        profile = _read_json(profile_path, project_root, "source_profile")
        _validate_schema(
            profile,
            "source-profile.schema.json",
            "source_profile",
            version=3,
        )
        _self_hash(profile, "profile_sha256", "source_profile")
        _require(
            profile["profile_id"] == profile_row["artifact_id"],
            "source_profile_id_mismatch",
        )
        _require(
            profile["profile_sha256"] == profile_row["artifact_sha256"],
            "source_profile_identity_mismatch",
        )
        _require(
            profile["event_id"] == assembly["event_id"],
            "source_profile_event_identity_mismatch",
        )
        _require(
            tuple(row["logical_name"] for row in profile["allowed_inputs"])
            == ALLOWED_LOGICAL_NAMES,
            "source_profile_logical_name_sequence_mismatch",
        )
        _require(
            REQUIRED_PROHIBITIONS <= set(profile["prohibited_inputs"]),
            "source_profile_prohibition_incomplete",
        )
        _require(
            REQUIRED_CLAIM_EXCLUSIONS
            <= set(profile["claim_boundary"]["does_not_support"]),
            "source_profile_claim_boundary_incomplete",
        )

        documents: dict[str, dict[str, Any]] = {}
        for row in profile["allowed_inputs"]:
            logical_name = row["logical_name"]
            expected_path = (
                Path("development_samples_v1")
                / "events"
                / assembly["event_id"]
                / f"{logical_name}.json"
            ).as_posix()
            _require(
                row["relative_path"] == expected_path,
                f"source_direct_path_mismatch:{logical_name}",
            )
            path = _safe_file(
                data_root,
                row["relative_path"],
                f"source:{logical_name}",
            )
            _require(
                path.stat().st_size == row["size_bytes"],
                f"source_size_mismatch:{logical_name}",
            )
            _require(
                file_sha256(path) == row["sha256"],
                f"source_hash_mismatch:{logical_name}",
            )
            documents[logical_name] = _read_json(
                path,
                data_root,
                f"source:{logical_name}",
            )
        _validate_source_documents(documents, assembly["event_id"])

        releases = {
            kind: _load_release(project_root, declaration, kind)
            for kind, declaration in assembly["semantic_releases"].items()
        }
        backend_releases: dict[str, _ReleaseAssets] = {}
        for backend, declaration in assembly["backend_releases"].items():
            if declaration["status"] == "implemented":
                backend_releases[backend] = _load_release(
                    project_root,
                    declaration,
                    "backend_realization",
                )
        event_ids = {
            assembly["event_id"],
            profile["event_id"],
            *(release.manifest["event_id"] for release in releases.values()),
            *(
                release.manifest["event_id"]
                for release in backend_releases.values()
            ),
        }
        _require(
            len(event_ids) == 1,
            "semantic_asset_event_identity_mismatch",
        )
    except AssetAdmissionError:
        raise
    except _AssetAdmissionCoreError as exc:
        raise AssetAdmissionError(str(exc)) from exc

    return StandardAssetSet(
        project_root,
        data_root,
        assembly_path,
        assembly,
        profile_path,
        profile,
        documents,
        releases,
        backend_releases,
    )


def load_release_json(
    release: _ReleaseAssets,
    role: str,
) -> dict[str, Any]:
    try:
        return _read_json(
            release.one(role),
            release.project_root,
            f"release_role:{role}",
        )
    except _AssetAdmissionCoreError as exc:
        raise AssetAdmissionError(str(exc)) from exc


__all__ = [
    "AssetAdmissionError",
    "StandardAssetSet",
    "assembly_sha256",
    "backend_catalog_sha256",
    "load_release_json",
    "load_standard_assets",
    "semantic_assembly_sha256",
]
