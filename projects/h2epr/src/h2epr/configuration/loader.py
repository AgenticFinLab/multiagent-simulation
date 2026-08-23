"""Fail-closed admission for one exact H2EPR Scenario Configuration.

The loader validates an accepted configuration release as a static semantic
input.  It deliberately does not project Contracts V1 carriers, bind a policy,
or authorize execution.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from h2epr.agents import RosterMappingError, RosterMappingProfile
from h2epr.agents import load_roster_mapping_profile
from h2epr.bundles.canonical import canonical_bytes, sha256_value

from .errors import (
    ConfigurationAdmissionError,
    ConfigurationErrorCode,
    ConfigurationFailureClass,
)


CONFIGURATION_FORMAT_ID = "h2epr.event-scenario-configuration.v0_1"
CONFIGURATION_ADMISSION_VERSION = "h2epr.scenario-configuration-admission.v0_1"
CONFIGURATION_RECEIPT_FORMAT = "h2epr.configuration-admission-receipt.v0_1"
CONFIGURATION_CANONICALIZATION = "h2epr_cjson.v1.full_configuration_document"
CONFIGURATION_SCHEMA_RELATIVE_PATH = Path(
    "configs/schemas/event-scenario-configuration-v0.1.schema.json"
)
CONFIGURATION_RELEASE_SCHEMA = "h2epr.event-scenario-configuration-release.v0_1"
CONFIGURATION_RELEASE_STATUS = "accepted_non_executable_configuration"

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_COMMIT = re.compile(r"^[a-f0-9]{40}$")


class _DuplicateKey(ValueError):
    pass


def _raise(
    code: ConfigurationErrorCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise ConfigurationAdmissionError(code, pointer=pointer, detail=detail)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"nonstandard_constant={value}")


def _parse_json_bytes(value: bytes, *, pointer: str) -> dict[str, Any]:
    try:
        document = json.loads(
            value.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateKey as exc:
        _raise(
            ConfigurationErrorCode.JSON_DUPLICATE_KEY,
            pointer=pointer,
            detail=f"key={exc}",
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _raise(
            ConfigurationErrorCode.JSON_INVALID,
            pointer=pointer,
            detail=type(exc).__name__,
        )
    if not isinstance(document, dict):
        _raise(
            ConfigurationErrorCode.JSON_INVALID,
            pointer=pointer,
            detail="object_required",
        )
    return document


def _read_json(path: Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    if not path.is_file():
        _raise(
            ConfigurationErrorCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=path.as_posix(),
        )
    raw = path.read_bytes()
    return _parse_json_bytes(raw, pointer=pointer), raw


def _find_project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
        if not root.is_dir():
            _raise(
                ConfigurationErrorCode.PROJECT_ROOT_NOT_FOUND,
                detail=root.as_posix(),
            )
        return root
    for parent in path.resolve().parents:
        if (
            parent.joinpath("src/h2epr").is_dir()
            and parent.joinpath("configs").is_dir()
            and parent.joinpath("agents").is_dir()
        ):
            return parent
    _raise(ConfigurationErrorCode.PROJECT_ROOT_NOT_FOUND)


def _inside_root(path: Path, root: Path, *, pointer: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _raise(
            ConfigurationErrorCode.PATH_UNSAFE,
            pointer=pointer,
            detail=path.as_posix(),
        )
    return resolved


def _resolved_file(
    root: Path,
    anchor: Path,
    value: Any,
    *,
    pointer: str,
    allow_parent: bool = False,
) -> Path:
    if not isinstance(value, str) or not value or value.strip() != value:
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer=pointer,
            detail="relative_path_required",
        )
    relative = Path(value)
    if relative.is_absolute() or (not allow_parent and ".." in relative.parts):
        _raise(
            ConfigurationErrorCode.PATH_UNSAFE,
            pointer=pointer,
            detail=value,
        )
    path = _inside_root(anchor / relative, root, pointer=pointer)
    if not path.is_file():
        _raise(
            ConfigurationErrorCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=value,
        )
    return path


def _object(value: Any, *, pointer: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer=pointer,
            detail="object_required",
        )
    return value


def _array(value: Any, *, pointer: str) -> list[Any]:
    if not isinstance(value, list):
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer=pointer,
            detail="array_required",
        )
    return value


def _string(value: Any, *, pointer: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer=pointer,
            detail="nonempty_string_required",
        )
    return value


def _sha256(value: Any, *, pointer: str) -> str:
    result = _string(value, pointer=pointer)
    if _SHA256.fullmatch(result) is None:
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer=pointer,
            detail="sha256_required",
        )
    return result


def _json_pointer(parts: Sequence[Any]) -> str:
    if not parts:
        return "/"
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped)


@dataclass(frozen=True)
class _ReleaseContext:
    release_id: str
    manifest_sha256: str
    semantic_input_sha256s: Mapping[str, str]
    semantic_input_paths: Mapping[str, Path]
    mapping_profile_path: Path
    coverage: Mapping[str, int]


@dataclass(frozen=True)
class ScenarioConfigurationAdmission:
    """Immutable result of successful bounded configuration admission."""

    project_relative_path: str
    configuration_id: str
    version: str
    status: str
    event_id: str
    purpose: str
    source_sha256: str
    canonical_sha256: str
    canonicalization: str
    schema_document_id: str
    schema_sha256: str
    release_id: str
    release_manifest_sha256: str
    mapping_profile_id: str
    mapping_profile_sha256: str
    semantic_input_sha256s: Mapping[str, str]
    coverage: Mapping[str, int]
    execution_eligible: bool
    unbound_policy_ids: tuple[str, ...]
    document: Mapping[str, Any]


def _validate_checksum_inventory(
    root: Path,
    package_dir: Path,
    required_paths: set[Path],
) -> None:
    checksum_path = package_dir / "SHA256SUMS"
    if not checksum_path.is_file():
        _raise(
            ConfigurationErrorCode.CHECKSUM_INVENTORY_INVALID,
            pointer="/SHA256SUMS",
            detail="missing",
        )
    observed: dict[Path, str] = {}
    try:
        lines = checksum_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        _raise(
            ConfigurationErrorCode.CHECKSUM_INVENTORY_INVALID,
            pointer="/SHA256SUMS",
            detail="utf8_required",
        )
    for index, line in enumerate(lines):
        parts = line.split("  ", 1)
        pointer = f"/SHA256SUMS/{index}"
        if len(parts) != 2 or _SHA256.fullmatch(parts[0]) is None or not parts[1]:
            _raise(
                ConfigurationErrorCode.CHECKSUM_INVENTORY_INVALID,
                pointer=pointer,
                detail="sha256_double_space_path_required",
            )
        path = _resolved_file(
            root,
            package_dir,
            parts[1],
            pointer=pointer,
            allow_parent=True,
        )
        if path in observed:
            _raise(
                ConfigurationErrorCode.CHECKSUM_INVENTORY_INVALID,
                pointer=pointer,
                detail="duplicate_resolved_path",
            )
        observed[path] = parts[0]
        if _sha256_file(path) != parts[0]:
            _raise(
                ConfigurationErrorCode.INTEGRITY_MISMATCH,
                pointer=pointer,
                detail="checksum_entry_mismatch",
            )
    missing = sorted(path.as_posix() for path in required_paths - set(observed))
    if missing:
        _raise(
            ConfigurationErrorCode.CHECKSUM_INVENTORY_INVALID,
            pointer="/SHA256SUMS",
            detail="required_path_unlisted=" + ",".join(missing),
        )


_SEMANTIC_INPUT_SPECS = {
    "scenario_definition_release": (
        "manifest_path",
        "manifest_sha256",
        "scenario_release_manifest_sha256",
    ),
    "scenario_definition": (
        "path",
        "sha256",
        "scenario_definition_sha256",
    ),
    "scenario_interface_closure": ("path", "sha256", None),
    "roster_definition_release": (
        "manifest_path",
        "manifest_sha256",
        "roster_release_manifest_sha256",
    ),
    "consolidated_mapping": (
        "manifest_path",
        "manifest_sha256",
        "consolidated_mapping_manifest_sha256",
    ),
    "mapping_profile": ("path", "sha256", "mapping_profile_sha256"),
    "evidence_ledger": ("path", "sha256", "evidence_ledger_sha256"),
    "source_register": ("path", "sha256", "source_register_sha256"),
}


def _load_release_context(
    root: Path,
    config_path: Path,
    source_sha256: str,
    manifest_path: Path,
    expected_manifest_sha256: str,
) -> tuple[_ReleaseContext, Mapping[str, Any]]:
    manifest_path = _inside_root(manifest_path, root, pointer="/release_manifest")
    if not manifest_path.is_file():
        _raise(
            ConfigurationErrorCode.SOURCE_NOT_FOUND,
            pointer="/release_manifest",
            detail=manifest_path.as_posix(),
        )
    manifest_raw = manifest_path.read_bytes()
    if _sha256_bytes(manifest_raw) != expected_manifest_sha256:
        _raise(
            ConfigurationErrorCode.INTEGRITY_MISMATCH,
            pointer="/release_manifest",
            detail="expected_release_manifest_sha256_mismatch",
        )
    manifest = _parse_json_bytes(manifest_raw, pointer="/release_manifest")
    if manifest.get("schema") != CONFIGURATION_RELEASE_SCHEMA:
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer="/release_manifest/schema",
            detail="unsupported_release_schema",
        )
    if manifest.get("status") != CONFIGURATION_RELEASE_STATUS:
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer="/release_manifest/status",
            detail="accepted_non_executable_status_required",
        )
    if manifest.get("integrity_algorithm") != "sha256":
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer="/release_manifest/integrity_algorithm",
            detail="sha256_required",
        )
    release_id = _string(
        manifest.get("release_id"), pointer="/release_manifest/release_id"
    )
    package_dir = manifest_path.parent
    required_paths = {manifest_path}
    expected_kinds = {
        "guide",
        "scenario_configuration",
        "configuration_design",
        "definition_closure",
        "substantive_review",
    }
    observed_kinds: set[str] = set()
    observed_paths: set[Path] = set()
    configuration_artifact_found = False
    for index, raw in enumerate(
        _array(manifest.get("artifacts"), pointer="/release_manifest/artifacts")
    ):
        pointer = f"/release_manifest/artifacts/{index}"
        item = _object(raw, pointer=pointer)
        kind = _string(item.get("kind"), pointer=f"{pointer}/kind")
        path = _resolved_file(
            root,
            package_dir,
            item.get("path"),
            pointer=f"{pointer}/path",
        )
        expected = _sha256(item.get("sha256"), pointer=f"{pointer}/sha256")
        if kind in observed_kinds or path in observed_paths:
            _raise(
                ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
                pointer=pointer,
                detail="duplicate_artifact",
            )
        if _sha256_file(path) != expected:
            _raise(
                ConfigurationErrorCode.INTEGRITY_MISMATCH,
                pointer=pointer,
                detail=f"artifact={kind}",
            )
        if kind == "scenario_configuration":
            configuration_artifact_found = path == config_path
            if source_sha256 != expected:
                _raise(
                    ConfigurationErrorCode.INTEGRITY_MISMATCH,
                    pointer=pointer,
                    detail="configuration_source_sha256_mismatch",
                )
        observed_kinds.add(kind)
        observed_paths.add(path)
        required_paths.add(path)
    if observed_kinds != expected_kinds or not configuration_artifact_found:
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer="/release_manifest/artifacts",
            detail="artifact_coverage_mismatch",
        )

    semantic = _object(
        manifest.get("semantic_inputs"), pointer="/release_manifest/semantic_inputs"
    )
    if set(semantic) != set(_SEMANTIC_INPUT_SPECS):
        _raise(
            ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
            pointer="/release_manifest/semantic_inputs",
            detail="semantic_input_coverage_mismatch",
        )
    input_hashes: dict[str, str] = {}
    input_paths: dict[str, Path] = {}
    for name, (path_key, hash_key, _) in _SEMANTIC_INPUT_SPECS.items():
        pointer = f"/release_manifest/semantic_inputs/{name}"
        item = _object(semantic[name], pointer=pointer)
        path = _resolved_file(
            root,
            root,
            item.get(path_key),
            pointer=f"{pointer}/{path_key}",
        )
        expected = _sha256(item.get(hash_key), pointer=f"{pointer}/{hash_key}")
        if _sha256_file(path) != expected:
            _raise(
                ConfigurationErrorCode.INTEGRITY_MISMATCH,
                pointer=pointer,
                detail=f"semantic_input={name}",
            )
        input_hashes[name] = expected
        input_paths[name] = path
        required_paths.add(path)

    owner = _object(
        manifest.get("owner_decision"), pointer="/release_manifest/owner_decision"
    )
    owner_path = _resolved_file(
        root,
        root,
        owner.get("path"),
        pointer="/release_manifest/owner_decision/path",
    )
    owner_sha = _sha256(
        owner.get("sha256"), pointer="/release_manifest/owner_decision/sha256"
    )
    if _sha256_file(owner_path) != owner_sha:
        _raise(
            ConfigurationErrorCode.INTEGRITY_MISMATCH,
            pointer="/release_manifest/owner_decision",
            detail="owner_decision_sha256_mismatch",
        )
    required_paths.add(owner_path)
    _validate_checksum_inventory(root, package_dir, required_paths)

    coverage_raw = _object(
        manifest.get("coverage"), pointer="/release_manifest/coverage"
    )
    coverage: dict[str, int] = {}
    for name, value in coverage_raw.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            _raise(
                ConfigurationErrorCode.RELEASE_MANIFEST_INVALID,
                pointer=f"/release_manifest/coverage/{name}",
                detail="nonnegative_integer_required",
            )
        coverage[name] = value
    context = _ReleaseContext(
        release_id=release_id,
        manifest_sha256=_sha256_bytes(manifest_raw),
        semantic_input_sha256s=MappingProxyType(input_hashes),
        semantic_input_paths=MappingProxyType(input_paths),
        mapping_profile_path=input_paths["mapping_profile"],
        coverage=MappingProxyType(coverage),
    )
    return context, manifest


def _load_and_validate_schema(
    root: Path, document: Mapping[str, Any]
) -> tuple[str, str]:
    if document.get("schema") != CONFIGURATION_FORMAT_ID:
        _raise(
            ConfigurationErrorCode.SCHEMA_VERSION_UNSUPPORTED,
            pointer="/schema",
            detail=f"expected={CONFIGURATION_FORMAT_ID}",
        )
    schema_path = _resolved_file(
        root,
        root,
        CONFIGURATION_SCHEMA_RELATIVE_PATH.as_posix(),
        pointer="/configuration_schema",
    )
    schema, schema_raw = _read_json(schema_path, pointer="/configuration_schema")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        _raise(
            ConfigurationErrorCode.SCHEMA_INVALID,
            pointer="/configuration_schema",
            detail=exc.validator or "draft_2020_12",
        )
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            document
        ),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        _raise(
            ConfigurationErrorCode.SCHEMA_VALIDATION_FAILED,
            pointer=_json_pointer(list(error.absolute_path)),
            detail=f"validator={error.validator}",
        )
    schema_id = schema.get("$id")
    if not isinstance(schema_id, str) or not schema_id:
        _raise(
            ConfigurationErrorCode.SCHEMA_INVALID,
            pointer="/configuration_schema/$id",
            detail="id_required",
        )
    return schema_id, _sha256_bytes(schema_raw)


def _canonical_identity(document: Mapping[str, Any]) -> str:
    try:
        encoded = canonical_bytes(document)
        roundtrip = _parse_json_bytes(encoded, pointer="/canonical_roundtrip")
    except ConfigurationAdmissionError:
        raise
    except (TypeError, ValueError) as exc:
        _raise(
            ConfigurationErrorCode.CANONICALIZATION_FAILED,
            detail=type(exc).__name__,
        )
    if roundtrip != document:
        _raise(
            ConfigurationErrorCode.CANONICALIZATION_FAILED,
            detail="semantic_roundtrip_mismatch",
        )
    return _sha256_bytes(encoded)


def _validate_release_document_consistency(
    document: Mapping[str, Any],
    manifest: Mapping[str, Any],
    release: _ReleaseContext,
) -> None:
    expected_metadata = {
        "id": document["configuration_id"],
        "version": document["version"],
        "purpose": document["purpose"],
        "timezone": document["clock"]["timezone"],
        "start": document["clock"]["start"],
        "primary_window": (
            f"{document['clock']['primary_window_start']}/"
            f"{document['clock']['primary_window_end']}"
        ),
        "analytic_horizon": document["clock"]["analytic_horizon"],
        "execution_eligible": document["execution_boundary"]["execution_eligible"],
        "historical_calibration": document["historical_calibration"],
        "historical_validation": document["historical_validation"],
        "known_outcome_fitting": document["known_outcome_fitting"],
    }
    metadata = _object(
        manifest.get("configuration"), pointer="/release_manifest/configuration"
    )
    for name, expected in expected_metadata.items():
        if metadata.get(name) != expected:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/release_manifest/configuration/{name}",
                detail="configuration_metadata_mismatch",
            )
    if manifest.get("event_id") != document["event_id"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/event_id",
            detail="release_event_id_mismatch",
        )
    if document["status"] != manifest.get("status"):
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/status",
            detail="release_status_mismatch",
        )
    authorization = _object(
        manifest.get("authorization"), pointer="/release_manifest/authorization"
    )
    if authorization.get("configuration_semantics_accepted") is not True:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/release_manifest/authorization/configuration_semantics_accepted",
            detail="accepted_semantics_required",
        )
    if authorization.get("execution_eligible") is not document[
        "execution_boundary"
    ]["execution_eligible"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/release_manifest/authorization/execution_eligible",
            detail="configuration_execution_boundary_mismatch",
        )
    for authorization_key, configuration_key in (
        ("historical_calibration_authorized", "historical_calibration"),
        ("historical_validation_claim_authorized", "historical_validation"),
    ):
        if authorization.get(authorization_key) is not document[configuration_key]:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/release_manifest/authorization/{authorization_key}",
                detail="configuration_claim_boundary_mismatch",
            )
    semantic = document["semantic_inputs"]
    manifest_semantic = manifest["semantic_inputs"]
    scenario_release_id = manifest_semantic["scenario_definition_release"].get(
        "release_id"
    )
    if semantic["scenario_definition_id"] != scenario_release_id:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/semantic_inputs/scenario_definition_id",
            detail="scenario_definition_release_id_mismatch",
        )
    for name, (_, _, configuration_key) in _SEMANTIC_INPUT_SPECS.items():
        if configuration_key is None:
            continue
        if semantic[configuration_key] != release.semantic_input_sha256s[name]:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/semantic_inputs/{configuration_key}",
                detail=f"release_input={name}",
            )


def _duplicates(values: Sequence[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return duplicates


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _value_type(value: Any) -> type[Any]:
    if isinstance(value, bool):
        return bool
    if isinstance(value, (int, float)):
        return float
    return type(value)


def _validate_semantics(
    document: Mapping[str, Any],
    profile: RosterMappingProfile,
    release_coverage: Mapping[str, int],
) -> tuple[Mapping[str, int], tuple[str, ...]]:
    if profile.event_id != document["event_id"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/event_id",
            detail="mapping_profile_event_mismatch",
        )
    named = document["named_actors"]
    populations = document["population_actors"]
    actors = [*named, *populations]
    identity_fields = (
        "actor_id",
        "entity_id",
        "participant_artifact_id",
        "authority_graph_id",
        "resource_owner_id",
    )
    for field in identity_fields:
        duplicates = _duplicates([row[field] for row in actors])
        if duplicates:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/{field}",
                detail="duplicate=" + ",".join(sorted(duplicates)),
            )
    actor_by_id = {row["actor_id"]: row for row in actors}
    population_actor_ids = {row["actor_id"] for row in populations}
    entity_ids = {row["entity_id"] for row in actors}
    named_capabilities: set[str] = set()
    population_capabilities: set[str] = set()
    for group_name, rows, expected_kind, observed in (
        ("named_actors", named, "agent_definition", named_capabilities),
        (
            "population_actors",
            populations,
            "population_model",
            population_capabilities,
        ),
    ):
        for index, actor in enumerate(rows):
            for capability_id in actor["capability_ids"]:
                try:
                    capability = profile.capabilities[capability_id]
                except KeyError:
                    _raise(
                        ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                        pointer=f"/{group_name}/{index}/capability_ids",
                        detail=f"capability={capability_id}",
                    )
                if capability.product_kind != expected_kind:
                    _raise(
                        ConfigurationErrorCode.ASSEMBLY_INVALID,
                        pointer=f"/{group_name}/{index}/capability_ids",
                        detail=f"product_kind={capability.product_kind}",
                    )
                if expected_kind == "agent_definition" and capability_id in observed:
                    _raise(
                        ConfigurationErrorCode.ASSEMBLY_INVALID,
                        pointer=f"/{group_name}/{index}/capability_ids",
                        detail=f"named_capability_reused={capability_id}",
                    )
                observed.add(capability_id)
    expected_named = {
        key
        for key, capability in profile.capabilities.items()
        if capability.product_kind == "agent_definition"
    }
    expected_population = set(profile.capabilities) - expected_named
    if named_capabilities != expected_named or population_capabilities != expected_population:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/named_actors",
            detail="released_capability_coverage_mismatch",
        )

    units = document["population_units"]
    duplicate_units = _duplicates([row["unit_id"] for row in units])
    if duplicate_units:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/population_units",
            detail="duplicate_unit=" + ",".join(sorted(duplicate_units)),
        )
    expected_pairs = {
        (actor["actor_id"], capability_id)
        for actor in populations
        for capability_id in actor["capability_ids"]
    }
    observed_pairs: set[tuple[str, str]] = set()
    unit_by_id: dict[str, Mapping[str, Any]] = {}
    for index, unit in enumerate(units):
        pointer = f"/population_units/{index}"
        actor = actor_by_id.get(unit["actor_id"])
        if actor is None or unit["actor_id"] not in population_actor_ids:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/actor_id",
                detail="population_actor_required",
            )
        capability_id = unit["capability_id"]
        if capability_id not in actor["capability_ids"]:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"{pointer}/capability_id",
                detail="capability_not_on_actor",
            )
        pair = (unit["actor_id"], capability_id)
        if pair in observed_pairs:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=pointer,
                detail="actor_capability_unit_reused",
            )
        observed_pairs.add(pair)
        capability = profile.capabilities[capability_id]
        if capability.unit_scope == "host_scoped_population":
            if unit.get("host_entity_id") not in entity_ids:
                _raise(
                    ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                    pointer=f"{pointer}/host_entity_id",
                    detail="host_entity_unresolved",
                )
        elif capability.unit_scope == "institution_preserving_population":
            if unit.get("institution_entity_id") != actor["entity_id"]:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/institution_entity_id",
                    detail="institution_identity_mismatch",
                )
        else:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=pointer,
                detail=f"unexpected_unit_scope={capability.unit_scope}",
            )
        unit_by_id[unit["unit_id"]] = unit
    if observed_pairs != expected_pairs:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/population_units",
            detail="actor_capability_unit_coverage_mismatch",
        )

    record_ids: list[str] = []
    initial = document["initial_records"]
    for index, record in enumerate(initial["authority"]):
        record_ids.append(record["record_id"])
        if record["actor_id"] not in actor_by_id:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"/initial_records/authority/{index}/actor_id",
                detail="actor_unresolved",
            )
    for index, record in enumerate(initial["relationships"]):
        record_ids.append(record["record_id"])
        if not set(record["parties"]) <= entity_ids:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"/initial_records/relationships/{index}/parties",
                detail="entity_unresolved",
            )
    for index, record in enumerate(initial["resource_and_condition_projections"]):
        record_ids.append(record["record_id"])
        if record["owner_id"] not in entity_ids:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=(
                    f"/initial_records/resource_and_condition_projections/"
                    f"{index}/owner_id"
                ),
                detail="resource_owner_unresolved",
            )
    for index, record in enumerate(initial["business_objects"]):
        record_ids.append(record["object_id"])
        if (
            record["owner_actor_id"] not in actor_by_id
            or record["counterparty_actor_id"] not in actor_by_id
        ):
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"/initial_records/business_objects/{index}",
                detail="business_actor_unresolved",
            )
    if _duplicates(record_ids):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/initial_records",
            detail="record_identity_reused",
        )

    clock = document["clock"]
    ordered_times = [
        _parse_time(clock[name])
        for name in (
            "start",
            "primary_window_start",
            "primary_window_end",
            "analytic_horizon",
        )
    ]
    if ordered_times != sorted(ordered_times):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/clock",
            detail="temporal_order_invalid",
        )

    exogenous = document["exogenous_inputs"]
    duplicate_inputs = _duplicates([row["input_id"] for row in exogenous])
    if duplicate_inputs:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/exogenous_inputs",
            detail="duplicate_input=" + ",".join(sorted(duplicate_inputs)),
        )
    input_by_id = {row["input_id"]: row for row in exogenous}
    for index, item in enumerate(exogenous):
        pointer = f"/exogenous_inputs/{index}"
        if "event_window" in item:
            lower, upper = (_parse_time(value) for value in item["event_window"])
            if lower > upper or lower < ordered_times[0] or upper > ordered_times[-1]:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/event_window",
                    detail="outside_configuration_clock",
                )
        if not set(item.get("target_unit_ids", ())) <= set(unit_by_id):
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/target_unit_ids",
                detail="unit_unresolved",
            )
    for index, unit in enumerate(units):
        activation = unit.get("private_need_activation")
        if not activation or activation["mode"] != "dated_exogenous_input":
            continue
        input_id = activation["input_id"]
        target_input = input_by_id.get(input_id)
        if (
            target_input is None
            or unit["unit_id"] not in target_input.get("target_unit_ids", ())
            or unit.get("opening_private_need") != "none"
        ):
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/population_units/{index}/private_need_activation",
                detail="opening_activation_mismatch",
            )

    overlay_ids = [row["overlay_id"] for row in document["sensitivity_overlays"]]
    if _duplicates(overlay_ids):
        _raise(
            ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
            pointer="/sensitivity_overlays",
            detail="duplicate_overlay_id",
        )
    registries: dict[str, Mapping[str, Any]] = {
        "population_unit": unit_by_id,
        "exogenous_input": input_by_id,
        "clock": {"clock": clock},
    }
    for overlay_index, overlay in enumerate(document["sensitivity_overlays"]):
        for operation_index, operation in enumerate(overlay["operations"]):
            pointer = (
                f"/sensitivity_overlays/{overlay_index}/operations/{operation_index}"
            )
            kind = operation["target_kind"]
            target_id = operation["target_id"]
            field = operation["field"]
            if kind == "structural_variant":
                if target_id not in document["structural_variants"] or field != "selection":
                    _raise(
                        ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                        pointer=pointer,
                        detail="structural_target_unresolved",
                    )
                target_value = document["structural_variants"][target_id]
            else:
                target = registries[kind].get(target_id)
                if target is None or field not in target:
                    _raise(
                        ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                        pointer=pointer,
                        detail="typed_target_unresolved",
                    )
                target_value = target[field]
            if _value_type(target_value) is not _value_type(operation["value"]):
                _raise(
                    ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                    pointer=f"{pointer}/value",
                    detail="replacement_type_mismatch",
                )

    expectations = document["validation_expectations"]
    actual_coverage = {
        "semantic_products": len(profile.products),
        "observation_placements": profile.observation_count,
        "intent_placements": profile.intent_count,
        "named_actors": len(named),
        "population_actors": len(populations),
        "population_units": len(units),
        "exogenous_inputs": len(exogenous),
        "structural_selections": len(document["structural_variants"]),
        "selected_policy_semantics": len(document["policy_selections"]),
        "sensitivity_overlays": len(document["sensitivity_overlays"]),
        "total_actors": len(actors),
    }
    for name in (
        "semantic_products",
        "observation_placements",
        "intent_placements",
        "named_actors",
        "population_actors",
        "population_units",
    ):
        if expectations[name] != actual_coverage[name]:
            _raise(
                ConfigurationErrorCode.COVERAGE_MISMATCH,
                pointer=f"/validation_expectations/{name}",
                detail=f"actual={actual_coverage[name]}",
            )
    for name in (
        "one_actor_per_entity",
        "one_resource_owner_per_entity",
        "host_scope_required_for_depositor_units",
        "intent_result_separation_required",
        "deterministic_replay_required",
    ):
        if expectations[name] is not True:
            _raise(
                ConfigurationErrorCode.COVERAGE_MISMATCH,
                pointer=f"/validation_expectations/{name}",
                detail="required_true_invariant",
            )
    release_coverage_names = {
        "semantic_products": "semantic_products",
        "observation_placements": "observation_placements",
        "intent_placements": "intent_placements",
        "named_actors": "named_actors",
        "population_actors": "population_actors",
        "population_units": "population_capability_units",
        "exogenous_inputs": "exogenous_inputs",
        "structural_selections": "structural_selections",
        "selected_policy_semantics": "selected_policy_semantics",
        "sensitivity_overlays": "sensitivity_overlays",
        "total_actors": "total_actors",
    }
    for name, actual in actual_coverage.items():
        release_name = release_coverage_names[name]
        if release_coverage.get(release_name) != actual:
            _raise(
                ConfigurationErrorCode.COVERAGE_MISMATCH,
                pointer=f"/release_manifest/coverage/{release_name}",
                detail=f"actual={actual}",
            )

    policies = document["policy_selections"]
    unbound = tuple(
        sorted(
            policy_id
            for policy_id, selection in policies.items()
            if selection["implementation_status"] == "unbound"
        )
    )
    boundary = document["execution_boundary"]
    if boundary["execution_eligible"] is not False:
        _raise(
            ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID,
            pointer="/execution_boundary/execution_eligible",
            detail="v0_1_admission_is_non_executable_only",
        )
    if not boundary["required_before_execution"]:
        _raise(
            ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID,
            pointer="/execution_boundary/required_before_execution",
            detail="missing_prerequisites_required",
        )
    if unbound and "unbound_selected_policy" not in document["completion_policy"][
        "failed_closed"
    ]:
        _raise(
            ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID,
            pointer="/completion_policy/failed_closed",
            detail="unbound_policy_failure_missing",
        )
    return MappingProxyType(actual_coverage), unbound


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def load_scenario_configuration(
    configuration_path: str | Path,
    *,
    expected_source_sha256: str | None = None,
    expected_release_manifest_sha256: str | None = None,
    project_root: str | Path | None = None,
    release_manifest_path: str | Path | None = None,
) -> ScenarioConfigurationAdmission:
    """Load, identify, and statically admit one accepted configuration release."""

    if (
        not isinstance(expected_source_sha256, str)
        or _SHA256.fullmatch(expected_source_sha256) is None
        or not isinstance(expected_release_manifest_sha256, str)
        or _SHA256.fullmatch(expected_release_manifest_sha256) is None
    ):
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/expected_identity",
            detail="configuration_and_release_sha256_required",
        )
    supplied_path = Path(configuration_path)
    root = _find_project_root(supplied_path, project_root)
    if project_root is not None and not supplied_path.is_absolute():
        cwd_candidate = supplied_path.resolve()
        path_candidate = (
            cwd_candidate if cwd_candidate.is_relative_to(root) else root / supplied_path
        )
    else:
        path_candidate = supplied_path
    path = _inside_root(path_candidate, root, pointer="/configuration_path")
    if not path.is_file():
        _raise(
            ConfigurationErrorCode.SOURCE_NOT_FOUND,
            pointer="/configuration",
            detail=path.as_posix(),
        )
    raw = path.read_bytes()
    source_sha256 = _sha256_bytes(raw)
    if source_sha256 != expected_source_sha256:
        _raise(
            ConfigurationErrorCode.INTEGRITY_MISMATCH,
            pointer="/configuration",
            detail="expected_source_sha256_mismatch",
        )
    document = _parse_json_bytes(raw, pointer="/configuration")
    if release_manifest_path is None:
        manifest_path = path.parent / "manifest.json"
    else:
        supplied_manifest = Path(release_manifest_path)
        if supplied_manifest.is_absolute():
            manifest_path = supplied_manifest
        else:
            cwd_manifest = supplied_manifest.resolve()
            manifest_path = (
                cwd_manifest
                if cwd_manifest.is_relative_to(root)
                else root / supplied_manifest
            )
    release, manifest = _load_release_context(
        root,
        path,
        source_sha256,
        manifest_path,
        expected_release_manifest_sha256,
    )
    schema_id, schema_sha256 = _load_and_validate_schema(root, document)
    canonical_sha256 = _canonical_identity(document)
    _validate_release_document_consistency(document, manifest, release)
    try:
        profile = load_roster_mapping_profile(
            release.mapping_profile_path, project_root=root
        )
    except RosterMappingError as exc:
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_inputs/mapping_profile_sha256",
            detail=str(exc),
        )
    coverage, unbound = _validate_semantics(document, profile, release.coverage)
    return ScenarioConfigurationAdmission(
        project_relative_path=path.relative_to(root).as_posix(),
        configuration_id=document["configuration_id"],
        version=document["version"],
        status=document["status"],
        event_id=document["event_id"],
        purpose=document["purpose"],
        source_sha256=source_sha256,
        canonical_sha256=canonical_sha256,
        canonicalization=CONFIGURATION_CANONICALIZATION,
        schema_document_id=schema_id,
        schema_sha256=schema_sha256,
        release_id=release.release_id,
        release_manifest_sha256=release.manifest_sha256,
        mapping_profile_id=profile.profile_id,
        mapping_profile_sha256=release.semantic_input_sha256s["mapping_profile"],
        semantic_input_sha256s=release.semantic_input_sha256s,
        coverage=coverage,
        execution_eligible=False,
        unbound_policy_ids=unbound,
        document=_freeze(copy.deepcopy(document)),
    )


def _validate_repository_context(value: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "root",
        "branch",
        "baseline_commit",
        "worktree_state",
        "validation_surface_sha256s",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/repository",
            detail="repository_fields_mismatch",
        )
    result = {name: value[name] for name in required - {"validation_surface_sha256s"}}
    if any(
        not isinstance(result[name], str) or not result[name]
        for name in ("root", "branch", "worktree_state")
    ) or _GIT_COMMIT.fullmatch(result["baseline_commit"]) is None:
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/repository",
            detail="repository_identity_invalid",
        )
    hashes = value["validation_surface_sha256s"]
    if not isinstance(hashes, Mapping) or not hashes:
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/repository/validation_surface_sha256s",
            detail="nonempty_mapping_required",
        )
    normalized_hashes: dict[str, str] = {}
    for path, digest in sorted(hashes.items()):
        if (
            not isinstance(path, str)
            or not path
            or Path(path).is_absolute()
            or ".." in Path(path).parts
            or not isinstance(digest, str)
            or _SHA256.fullmatch(digest) is None
        ):
            _raise(
                ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
                pointer="/repository/validation_surface_sha256s",
                detail="path_or_sha256_invalid",
            )
        normalized_hashes[path] = digest
    result["validation_surface_sha256s"] = normalized_hashes
    return {name: result[name] for name in sorted(result)}


def _validate_verification(value: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/verification",
            detail="nonempty_sequence_required",
        )
    result: list[dict[str, str]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, Mapping) or set(raw) != {"command", "result", "summary"}:
            _raise(
                ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
                pointer=f"/verification/{index}",
                detail="verification_fields_mismatch",
            )
        row = {key: raw[key] for key in ("command", "result", "summary")}
        if (
            any(not isinstance(row[key], str) or not row[key] for key in row)
            or row["result"] not in {"pass", "fail"}
        ):
            _raise(
                ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
                pointer=f"/verification/{index}",
                detail="verification_value_invalid",
            )
        result.append(row)
    return result


_FAILURE_GATE = {
    ConfigurationFailureClass.PREFLIGHT_CONTEXT: "P0",
    ConfigurationFailureClass.SOURCE: "P1",
    ConfigurationFailureClass.INTEGRITY: "P1",
    ConfigurationFailureClass.STRUCTURE: "P2",
    ConfigurationFailureClass.SEMANTIC_REFERENCE: "P3",
    ConfigurationFailureClass.ASSEMBLY: "P3",
    ConfigurationFailureClass.EXECUTION_BOUNDARY: "P4",
}


def build_configuration_preflight_receipt(
    *,
    repository_context: Mapping[str, Any],
    verification: Sequence[Mapping[str, Any]],
    admission: ScenarioConfigurationAdmission | None = None,
    error: ConfigurationAdmissionError | None = None,
    attempted_configuration_path: str = "",
) -> dict[str, Any]:
    """Build one deterministic pass or failure receipt for E5 static admission."""

    if (admission is None) == (error is None):
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/receipt",
            detail="exactly_one_of_admission_or_error_required",
        )
    repository = _validate_repository_context(repository_context)
    checks = _validate_verification(verification)
    if admission is not None and any(row["result"] != "pass" for row in checks):
        _raise(
            ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID,
            pointer="/verification",
            detail="passing_admission_requires_passing_verification",
        )
    gate_names = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
    if error is None:
        gates = [{"gate": name, "status": "pass"} for name in gate_names]
        configuration = {
            "path": admission.project_relative_path,
            "configuration_id": admission.configuration_id,
            "version": admission.version,
            "status": admission.status,
            "event_id": admission.event_id,
            "source_sha256": admission.source_sha256,
            "canonical_sha256": admission.canonical_sha256,
            "canonicalization": admission.canonicalization,
            "schema_document_id": admission.schema_document_id,
            "schema_sha256": admission.schema_sha256,
        }
        release = {
            "release_id": admission.release_id,
            "manifest_sha256": admission.release_manifest_sha256,
            "mapping_profile_id": admission.mapping_profile_id,
            "mapping_profile_sha256": admission.mapping_profile_sha256,
        }
        execution = {
            "execution_eligible": False,
            "unbound_policy_ids": list(admission.unbound_policy_ids),
        }
        failure = None
        verdict = "PASS_BOUNDED_CONFIGURATION_ADMISSION"
        semantic_inputs = dict(admission.semantic_input_sha256s)
        coverage = dict(admission.coverage)
    else:
        failure_gate = _FAILURE_GATE[error.failure_class]
        failure_index = gate_names.index(failure_gate)
        gates = [
            {
                "gate": name,
                "status": (
                    "pass"
                    if index < failure_index
                    else "fail"
                    if index == failure_index
                    else "not_run"
                ),
            }
            for index, name in enumerate(gate_names)
        ]
        configuration = {"path": attempted_configuration_path}
        release = None
        execution = None
        failure = {
            "failure_class": error.failure_class.value,
            "code": error.code.value,
            "pointer": error.pointer,
            "diagnostic": error.detail,
        }
        verdict = (
            "RETURN_TO_CONFIGURATION"
            if error.failure_class
            in {ConfigurationFailureClass.ASSEMBLY, ConfigurationFailureClass.EXECUTION_BOUNDARY}
            else "RETURN_TO_SCENARIO_MAPPING_OR_RELEASE"
            if error.failure_class == ConfigurationFailureClass.SEMANTIC_REFERENCE
            else "BLOCKED_BY_AUTHORIZATION_SCOPE"
            if error.failure_class == ConfigurationFailureClass.PREFLIGHT_CONTEXT
            else "FAIL_CONFIGURATION_SURFACE"
        )
        semantic_inputs = {}
        coverage = {}
    receipt: dict[str, Any] = {
        "schema": CONFIGURATION_RECEIPT_FORMAT,
        "validation_surface": CONFIGURATION_ADMISSION_VERSION,
        "repository": repository,
        "configuration": configuration,
        "release": release,
        "semantic_inputs": semantic_inputs,
        "coverage": coverage,
        "execution_boundary": execution,
        "gates": gates,
        "verification": checks,
        "failure": failure,
        "verdict": verdict,
        "authorization": {
            "configuration_surface_only": True,
            "carrier_projection_authorized": False,
            "policy_implementation_authorized": False,
            "runtime_authorized": False,
            "simulation_authorized": False,
            "evaluation_authorized": False,
        },
        "next_legal_stage": "separately_authorized_E6_carrier_projection",
    }
    receipt["receipt_sha256"] = sha256_value(receipt)
    return receipt


__all__ = [
    "CONFIGURATION_ADMISSION_VERSION",
    "CONFIGURATION_CANONICALIZATION",
    "CONFIGURATION_FORMAT_ID",
    "CONFIGURATION_RECEIPT_FORMAT",
    "CONFIGURATION_SCHEMA_RELATIVE_PATH",
    "ScenarioConfigurationAdmission",
    "build_configuration_preflight_receipt",
    "load_scenario_configuration",
]
