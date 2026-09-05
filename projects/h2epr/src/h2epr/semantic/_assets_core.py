"""Shared fail-closed primitives for semantic release admission."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from h2epr.canonical import canonical_sha256, file_sha256


class _AssetAdmissionCoreError(ValueError):
    """A release identity, path, checksum, or source boundary is invalid."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
ALLOWED_LOGICAL_NAMES = ("event_spec", "frozen_evidence", "draft_epg")
REQUIRED_PROHIBITIONS = {
    "reference_epg",
    "held_out_suffix",
    "evaluation_only_content",
    "external_research",
    "network_retrieval",
}
REQUIRED_CLAIM_EXCLUSIONS = {
    "held-out evaluation",
    "historical fit",
    "parameter calibration",
    "causal validity",
    "scientific validity",
    "universal generality",
}


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _AssetAdmissionCoreError(code)


def _safe_file(root: Path, relative_path: Any, label: str) -> Path:
    _require(isinstance(relative_path, str) and bool(relative_path), f"{label}_path_invalid")
    relative = Path(relative_path)
    _require(not relative.is_absolute() and ".." not in relative.parts, f"{label}_path_unsafe")
    path = root / relative
    _require(not path.is_symlink() and path.is_file(), f"{label}_missing_or_unsafe")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise _AssetAdmissionCoreError(f"{label}_escapes_root") from exc
    return path


def _safe_directory(root: Path, relative_path: Any, label: str) -> Path:
    _require(isinstance(relative_path, str) and bool(relative_path), f"{label}_path_invalid")
    relative = Path(relative_path)
    _require(not relative.is_absolute() and ".." not in relative.parts, f"{label}_path_unsafe")
    path = root / relative
    _require(not path.is_symlink() and path.is_dir(), f"{label}_missing_or_unsafe")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise _AssetAdmissionCoreError(f"{label}_escapes_root") from exc
    return path


def _release_artifact_path(
    release_root: Path,
    project_root: Path,
    relative_path: Any,
    label: str,
    *,
    cross_release_role: str | None = None,
) -> Path:
    _require(isinstance(relative_path, str) and bool(relative_path), f"{label}_path_invalid")
    relative = Path(relative_path)
    _require(
        not relative.is_absolute()
        and (cross_release_role is not None or ".." not in relative.parts),
        f"{label}_path_unsafe",
    )
    path = release_root / relative
    _require(not path.is_symlink() and path.is_file(), f"{label}_missing_or_unsafe")
    resolved = path.resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError as exc:
        raise _AssetAdmissionCoreError(f"{label}_escapes_project") from exc
    if cross_release_role is None:
        try:
            resolved.relative_to(release_root.resolve())
        except ValueError as exc:
            raise _AssetAdmissionCoreError(f"{label}_escapes_release") from exc
        return path

    _require(
        cross_release_role
        in {
            "backend_configuration",
            "backend_configuration_admission_receipt",
            "backend_configuration_provenance_coverage",
        },
        f"{label}_cross_release_role_invalid",
    )
    try:
        config_relative = resolved.relative_to((project_root / "configs").resolve())
    except ValueError as exc:
        raise _AssetAdmissionCoreError(f"{label}_escapes_config_release") from exc
    _require(
        "backends" in config_relative.parts,
        f"{label}_config_release_shape_invalid",
    )
    if cross_release_role == "backend_configuration":
        name_valid = path.name.endswith("-configuration.json") and len(
            path.name
        ) > len("-configuration.json")
    elif cross_release_role == "backend_configuration_admission_receipt":
        name_valid = path.name == "admission-receipt.json"
    else:
        name_valid = path.name == "provenance-coverage.json"
    _require(name_valid, f"{label}_config_release_name_invalid")
    return path


def _read_json(path: Path, boundary: Path, label: str) -> dict[str, Any]:
    _require(not path.is_symlink() and path.is_file(), f"{label}_missing_or_unsafe")
    try:
        path.resolve().relative_to(boundary.resolve())
    except ValueError as exc:
        raise _AssetAdmissionCoreError(f"{label}_escapes_boundary") from exc
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _AssetAdmissionCoreError(f"{label}_parse_failure") from exc
    _require(isinstance(value, dict), f"{label}_shape_invalid")
    return value


def _validate_schema(
    value: Mapping[str, Any], schema_name: str, label: str, *, version: int
) -> None:
    if version not in {2, 3, 4}:
        raise _AssetAdmissionCoreError("schema_protocol_version_unknown")
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _AssetAdmissionCoreError(f"{label}_schema_invalid:{exc.json_path}") from exc


def _self_hash(value: Mapping[str, Any], field: str, label: str) -> None:
    expected = canonical_sha256({key: item for key, item in value.items() if key != field})
    _require(value.get(field) == expected, f"{label}_self_hash_mismatch")


def _field_value(value: Any, label: str) -> Any:
    _require(isinstance(value, Mapping) and "value" in value, f"{label}_value_wrapper_invalid")
    return value["value"]


def _validate_source_documents(
    documents: Mapping[str, Mapping[str, Any]], event_id: str
) -> None:
    spec = documents["event_spec"]
    _require(spec.get("public_event_id") == event_id, "event_spec_identity_mismatch")
    _require(isinstance(spec.get("title"), str) and bool(spec["title"]), "event_spec_title_invalid")
    _require(isinstance(spec.get("schema_version"), str), "event_spec_schema_version_invalid")

    frozen = documents["frozen_evidence"]
    _require(frozen.get("public_event_id") == event_id, "frozen_evidence_identity_mismatch")
    sources = frozen.get("sources")
    _require(isinstance(sources, list) and bool(sources), "frozen_evidence_sources_invalid")
    _require(frozen.get("source_count") == len(sources), "frozen_evidence_source_count_mismatch")
    for index, source in enumerate(sources):
        _require(isinstance(source, Mapping), f"frozen_evidence_source_shape:{index}")

    draft = documents["draft_epg"]
    for field in ("event_id", "title", "start_time", "end_time", "stages"):
        _require(field in draft, f"draft_field_missing:{field}")
    _require(
        isinstance(draft["event_id"], str) and bool(draft["event_id"]),
        "draft_event_id_invalid",
    )
    _field_value(draft["title"], "draft_title")
    _field_value(draft["start_time"], "draft_start_time")
    _field_value(draft["end_time"], "draft_end_time")
    stages = draft["stages"]
    _require(isinstance(stages, list) and bool(stages), "draft_stages_invalid")
    stage_ids: set[str] = set()
    episode_ids: set[str] = set()
    occurrence_count = 0
    for stage in stages:
        _require(isinstance(stage, Mapping), "draft_stage_shape_invalid")
        stage_id = stage.get("stage_id")
        _require(isinstance(stage_id, str) and stage_id.startswith("S"), "draft_stage_id_invalid")
        _require(stage_id not in stage_ids, f"draft_stage_id_duplicate:{stage_id}")
        stage_ids.add(stage_id)
        for field in ("name", "start_time", "end_time"):
            _field_value(stage.get(field), f"draft_stage_{stage_id}_{field}")
        episodes = stage.get("episodes")
        _require(isinstance(episodes, list) and bool(episodes), f"draft_stage_episodes_invalid:{stage_id}")
        for episode in episodes:
            _require(isinstance(episode, Mapping), "draft_episode_shape_invalid")
            episode_id = episode.get("episode_id")
            _require(isinstance(episode_id, str) and episode_id.startswith("E"), "draft_episode_id_invalid")
            _require(episode_id not in episode_ids, f"draft_episode_id_duplicate:{episode_id}")
            episode_ids.add(episode_id)
            for field in ("name", "start_time", "end_time"):
                _field_value(episode.get(field), f"draft_episode_{episode_id}_{field}")
            participants = episode.get("participants")
            _require(isinstance(participants, list) and bool(participants), f"draft_participants_invalid:{episode_id}")
            seen_in_episode: set[str] = set()
            for participant in participants:
                _require(isinstance(participant, Mapping), "draft_participant_shape_invalid")
                participant_id = participant.get("participant_id")
                _require(
                    isinstance(participant_id, str) and participant_id.startswith("P_"),
                    "draft_participant_id_invalid",
                )
                _require(
                    participant_id not in seen_in_episode,
                    f"draft_participant_duplicate:{episode_id}:{participant_id}",
                )
                seen_in_episode.add(participant_id)
                for field in ("name", "participant_type", "base_role"):
                    _field_value(
                        participant.get(field),
                        f"draft_participant_{episode_id}_{participant_id}_{field}",
                    )
                actions = participant.get("actions")
                # An occurrence may be passive; later episodes can expose choices.
                # Preserve it in the roster without inventing an action row.
                _require(
                    isinstance(actions, list),
                    f"draft_actions_invalid:{episode_id}:{participant_id}",
                )
                for action in actions:
                    _require(isinstance(action, Mapping), "draft_action_shape_invalid")
                    _field_value(action.get("name"), "draft_action_name")
                    _field_value(action.get("timestamp"), "draft_action_timestamp")
                occurrence_count += 1
    _require(occurrence_count > 0, "draft_occurrence_count_zero")


def _validate_checksums(root: Path) -> None:
    checksum_path = _safe_file(root, "SHA256SUMS", "checksum_inventory")
    observed: dict[str, str] = {}
    for line_number, line in enumerate(
        checksum_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        parts = line.split("  ", 1)
        _require(len(parts) == 2, f"checksum_row_invalid:{line_number}")
        digest, relative_path = parts
        _require(relative_path not in observed, f"checksum_path_duplicate:{relative_path}")
        path = _safe_file(root, relative_path, f"checksum_target:{relative_path}")
        _require(file_sha256(path) == digest, f"checksum_mismatch:{relative_path}")
        observed[relative_path] = digest
    expected = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    _require(set(observed) == expected, "checksum_inventory_not_exact")
    _require({"README.md", "manifest.json"} <= expected, "release_publication_surface_incomplete")


@dataclass(frozen=True)
class _ReleaseAssets:
    project_root: Path
    root: Path
    manifest: dict[str, Any]
    artifact_paths: dict[str, Path]

    def one(self, role: str) -> Path:
        matches = [
            self.artifact_paths[row["artifact_id"]]
            for row in self.manifest["artifacts"]
            if row["role"] == role
        ]
        if len(matches) != 1:
            raise _AssetAdmissionCoreError(f"release_artifact_role_cardinality:{role}")
        return matches[0]


def _load_release(
    project_root: Path,
    declaration: Mapping[str, Any],
    expected_kind: str,
) -> _ReleaseAssets:
    root = _safe_directory(project_root, declaration.get("release_root"), f"{expected_kind}_release")
    manifest = _read_json(root / "manifest.json", project_root, f"{expected_kind}_manifest")
    _validate_schema(manifest, "semantic-release-manifest.schema.json", f"{expected_kind}_manifest", version=2)
    _self_hash(manifest, "manifest_sha256", f"{expected_kind}_manifest")
    _require(manifest["release_kind"] == expected_kind, f"{expected_kind}_release_kind_mismatch")
    _require(manifest["release_id"] == declaration.get("release_id"), f"{expected_kind}_release_id_mismatch")
    _require(
        manifest["manifest_sha256"] == declaration.get("manifest_sha256"),
        f"{expected_kind}_manifest_identity_mismatch",
    )
    artifact_paths: dict[str, Path] = {}
    roles: set[str] = set()
    for artifact in manifest["artifacts"]:
        artifact_id = artifact["artifact_id"]
        role = artifact["role"]
        _require(artifact_id not in artifact_paths, f"release_artifact_id_duplicate:{artifact_id}")
        _require(role not in roles, f"release_artifact_role_duplicate:{role}")
        path = _release_artifact_path(
            root,
            project_root,
            artifact["relative_path"],
            f"release_artifact:{artifact_id}",
            cross_release_role=(
                role
                if expected_kind == "backend_realization"
                and role
                in {
                    "backend_configuration",
                    "backend_configuration_admission_receipt",
                    "backend_configuration_provenance_coverage",
                }
                else None
            ),
        )
        _require(path.stat().st_size == artifact["size_bytes"], f"release_artifact_size_mismatch:{artifact_id}")
        _require(file_sha256(path) == artifact["sha256"], f"release_artifact_hash_mismatch:{artifact_id}")
        artifact_paths[artifact_id] = path
        roles.add(role)
    _validate_checksums(root)
    return _ReleaseAssets(project_root, root, manifest, artifact_paths)
