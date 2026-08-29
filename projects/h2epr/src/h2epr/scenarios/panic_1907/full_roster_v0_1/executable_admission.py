"""Fail-closed admission for the Panic executable successor and bundle."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import masim
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from masim.integrations.event_process import canonical_bytes, canonical_sha256

from .assembly import (
    PACKAGE_ID,
    PACKAGE_VERSION,
    POLICY_REALIZATION_PATH,
    POLICY_REALIZATION_SOURCE_SHA256,
    RUNTIME_BUNDLE_ID,
    RUNTIME_BUNDLE_PATH,
    RUNTIME_BUNDLE_VERSION,
    build_panic_executable_package_document,
    build_panic_runtime_bundle_document,
)
from .components import COMPONENTS_BY_ID, COMPONENTS_BY_ROLE
from .runtime_components import PanicEnvironment


PACKAGE_SCHEMA_PATH = Path(
    "execution/schemas/executable-scenario-package-v0.1.schema.json"
)
POLICY_SCHEMA_PATH = Path(
    "execution/schemas/policy-realization-v0.1.schema.json"
)


class ExecutableAdmissionCode(str, Enum):
    """Stable rejection classes for the event-local executable boundary."""

    PREFLIGHT_INVALID = "PANIC_EXECUTABLE_PREFLIGHT_INVALID"
    SOURCE_NOT_FOUND = "PANIC_EXECUTABLE_SOURCE_NOT_FOUND"
    PATH_UNSAFE = "PANIC_EXECUTABLE_PATH_UNSAFE"
    INTEGRITY_MISMATCH = "PANIC_EXECUTABLE_INTEGRITY_MISMATCH"
    JSON_INVALID = "PANIC_EXECUTABLE_JSON_INVALID"
    JSON_DUPLICATE_KEY = "PANIC_EXECUTABLE_JSON_DUPLICATE_KEY"
    SCHEMA_INVALID = "PANIC_EXECUTABLE_SCHEMA_INVALID"
    SCHEMA_VALIDATION_FAILED = "PANIC_EXECUTABLE_SCHEMA_VALIDATION_FAILED"
    PACKAGE_IDENTITY_MISMATCH = "PANIC_EXECUTABLE_PACKAGE_IDENTITY_MISMATCH"
    BUNDLE_IDENTITY_MISMATCH = "PANIC_EXECUTABLE_BUNDLE_IDENTITY_MISMATCH"
    BUNDLE_MATERIALIZATION_MISMATCH = (
        "PANIC_EXECUTABLE_BUNDLE_MATERIALIZATION_MISMATCH"
    )
    PACKAGE_MATERIALIZATION_MISMATCH = (
        "PANIC_EXECUTABLE_PACKAGE_MATERIALIZATION_MISMATCH"
    )
    COMPONENT_UNRESOLVED = "PANIC_EXECUTABLE_COMPONENT_UNRESOLVED"
    MASIM_BOUNDARY_MISMATCH = "PANIC_EXECUTABLE_MASIM_BOUNDARY_MISMATCH"
    COVERAGE_MISMATCH = "PANIC_EXECUTABLE_COVERAGE_MISMATCH"


class ExecutableAdmissionError(ValueError):
    """One typed rejection with an optional document pointer."""

    def __init__(
        self,
        code: ExecutableAdmissionCode,
        *,
        pointer: str = "",
        detail: str = "",
    ) -> None:
        self.code = code
        self.pointer = pointer
        self.detail = detail
        parts = [code.value]
        if pointer:
            parts.append(pointer)
        if detail:
            parts.append(detail)
        super().__init__(":".join(parts))


class _DuplicateKey(ValueError):
    pass


@dataclass(frozen=True)
class ExecutableAdmission:
    """Immutable result of package, bundle, and component admission."""

    package_id: str
    package_version: str
    package_path: str
    package_source_sha256: str
    package_canonical_sha256: str
    runtime_bundle_id: str
    runtime_bundle_version: str
    runtime_bundle_path: str
    runtime_bundle_source_sha256: str
    runtime_bundle_canonical_sha256: str
    schema_id: str
    schema_sha256: str
    deterministic_materialization: bool
    component_complete: bool
    execution_eligible: bool
    accepted: bool
    coverage: Mapping[str, int]
    package_document: Mapping[str, Any]
    runtime_bundle_document: Mapping[str, Any]


def _fail(
    code: ExecutableAdmissionCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise ExecutableAdmissionError(code, pointer=pointer, detail=detail)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def _read_json(path: Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    if not path.is_file():
        _fail(
            ExecutableAdmissionCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=path.as_posix(),
        )
    raw = path.read_bytes()
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except _DuplicateKey as exc:
        _fail(
            ExecutableAdmissionCode.JSON_DUPLICATE_KEY,
            pointer=pointer,
            detail=str(exc),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail(
            ExecutableAdmissionCode.JSON_INVALID,
            pointer=pointer,
            detail=type(exc).__name__,
        )
    if not isinstance(value, dict):
        _fail(
            ExecutableAdmissionCode.JSON_INVALID,
            pointer=pointer,
            detail="object_required",
        )
    return value, raw


def _project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        root = next(
            (
                parent
                for parent in path.resolve().parents
                if parent.joinpath("src/h2epr").is_dir()
                and parent.joinpath("execution/schemas").is_dir()
            ),
            Path(),
        )
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        _fail(ExecutableAdmissionCode.PREFLIGHT_INVALID, detail="project_root")
    return root


def _inside(root: Path, path: Path, *, pointer: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail(
            ExecutableAdmissionCode.PATH_UNSAFE,
            pointer=pointer,
            detail=path.as_posix(),
        )
    return resolved


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return copy.deepcopy(value)


def _validate_package_schema(
    root: Path, document: Mapping[str, Any]
) -> tuple[str, str]:
    package_path = _inside(
        root, root / PACKAGE_SCHEMA_PATH, pointer="/package_schema"
    )
    policy_path = _inside(
        root, root / POLICY_SCHEMA_PATH, pointer="/policy_schema"
    )
    package_schema, package_raw = _read_json(
        package_path, pointer="/package_schema"
    )
    policy_schema, _ = _read_json(policy_path, pointer="/policy_schema")
    try:
        Draft202012Validator.check_schema(package_schema)
        Draft202012Validator.check_schema(policy_schema)
        registry = Registry().with_resources(
            (
                (
                    package_schema["$id"],
                    Resource.from_contents(package_schema),
                ),
                (
                    policy_schema["$id"],
                    Resource.from_contents(policy_schema),
                ),
            )
        )
    except (SchemaError, KeyError) as exc:
        _fail(
            ExecutableAdmissionCode.SCHEMA_INVALID,
            pointer="/package_schema",
            detail=type(exc).__name__,
        )
    errors = sorted(
        Draft202012Validator(package_schema, registry=registry).iter_errors(
            document
        ),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        error = errors[0]
        pointer = "/" + "/".join(
            str(item).replace("~", "~0").replace("/", "~1")
            for item in error.absolute_path
        )
        _fail(
            ExecutableAdmissionCode.SCHEMA_VALIDATION_FAILED,
            pointer=pointer,
            detail=f"validator={error.validator}",
        )
    return package_schema["$id"], hashlib.sha256(package_raw).hexdigest()


def _verify_components(
    package: Mapping[str, Any], bundle: Mapping[str, Any]
) -> None:
    bindings = package["component_bindings"]
    if set(bindings) != set(COMPONENTS_BY_ROLE):
        _fail(
            ExecutableAdmissionCode.COMPONENT_UNRESOLVED,
            pointer="/component_bindings",
            detail="role_set_mismatch",
        )
    for role, reference in bindings.items():
        component = COMPONENTS_BY_ROLE[role]
        if (
            reference["implementation_id"] != component.implementation_id
            or reference["implementation_version"]
            != component.implementation_version
            or COMPONENTS_BY_ID.get(component.implementation_id) is not component
            or component.implementation is None
        ):
            _fail(
                ExecutableAdmissionCode.COMPONENT_UNRESOLVED,
                pointer=f"/component_bindings/{role}",
                detail="static_resolution_mismatch",
            )
    bundle_rows = {row["role"]: row for row in bundle["component_registry"]}
    if len(bundle_rows) != 9 or set(bundle_rows) != set(bindings):
        _fail(
            ExecutableAdmissionCode.COMPONENT_UNRESOLVED,
            pointer="/runtime_bundle/component_registry",
            detail="bundle_role_set_mismatch",
        )
    for role, row in bundle_rows.items():
        if (
            row["implementation_id"] != bindings[role]["implementation_id"]
            or row["implementation_version"]
            != bindings[role]["implementation_version"]
        ):
            _fail(
                ExecutableAdmissionCode.COMPONENT_UNRESOLVED,
                pointer=f"/runtime_bundle/component_registry/{role}",
                detail="package_bundle_component_mismatch",
            )
    checks = PanicEnvironment(bundle).scenario_policy_checks()
    if len(checks) != 9 or {row["status"] for row in checks} != {"pass"}:
        _fail(
            ExecutableAdmissionCode.COMPONENT_UNRESOLVED,
            pointer="/runtime_bundle/policy_registry/scenario_policies",
            detail="scenario_policy_control_failed",
        )


def _verify_coverage(bundle: Mapping[str, Any]) -> dict[str, int]:
    actor_count = len(bundle["actor_registry"])
    carrier_count = len(bundle["carrier_projections"])
    placement_count = sum(
        len(row["capability_projections"])
        for row in bundle["carrier_projections"]
    )
    action_count = len(bundle["action_registry"])
    observation_count = len(bundle["observation_rules"])
    lifecycle_count = len(bundle["lifecycle_registry"])
    route_count = len(bundle["communication_routes"])
    expected = bundle["coverage_expectations"]
    if (
        actor_count != 16
        or carrier_count != 16
        or placement_count != expected["actor_capability_bindings"]
        or action_count != expected["intent_placements"]
        or observation_count != expected["decision_commitments"]
        or lifecycle_count != expected["lifecycle_families"]
        or route_count != 35
    ):
        _fail(
            ExecutableAdmissionCode.COVERAGE_MISMATCH,
            pointer="/runtime_bundle",
            detail=(
                f"actors={actor_count}:carriers={carrier_count}:"
                f"placements={placement_count}:actions={action_count}:"
                f"observations={observation_count}:lifecycles={lifecycle_count}:"
                f"routes={route_count}"
            ),
        )
    routes = {row["route_id"] for row in bundle["communication_routes"]}
    if any(
        row["result_route_id"] not in routes
        or (
            row["direct_route_id"] is not None
            and row["direct_route_id"] not in routes
        )
        for row in bundle["action_registry"]
    ):
        _fail(
            ExecutableAdmissionCode.COVERAGE_MISMATCH,
            pointer="/runtime_bundle/action_registry",
            detail="route_reference_unresolved",
        )
    return {
        "actor_instances": actor_count,
        "actor_carriers": carrier_count,
        "actor_capability_bindings": placement_count,
        "action_bindings": action_count,
        "decision_observation_rules": observation_count,
        "communication_routes": route_count,
        "lifecycle_families": lifecycle_count,
        "runtime_components": len(bundle["component_registry"]),
    }


def load_panic_executable_package(
    path: str | Path,
    *,
    project_root: str | Path | None = None,
    expected_source_sha256: str | None = None,
) -> ExecutableAdmission:
    """Admit an exact accepted package and its referenced runtime bundle."""

    package_path = Path(path)
    root = _project_root(package_path, project_root)
    package_path = _inside(root, package_path, pointer="/package")
    package, package_raw = _read_json(package_path, pointer="/package")
    package_source_sha = hashlib.sha256(package_raw).hexdigest()
    if expected_source_sha256 is not None and package_source_sha != expected_source_sha256:
        _fail(
            ExecutableAdmissionCode.INTEGRITY_MISMATCH,
            pointer="/package",
            detail="expected_source_sha256_mismatch",
        )
    schema_id, schema_sha = _validate_package_schema(root, package)
    if (
        package.get("package_id") != PACKAGE_ID
        or package.get("version") != PACKAGE_VERSION
        or package.get("status") != "accepted_executable_package"
        or package.get("execution_eligible") is not True
    ):
        _fail(
            ExecutableAdmissionCode.PACKAGE_IDENTITY_MISMATCH,
            pointer="/package_id",
        )

    bundle_ref = package["runtime_bundle"]
    if (
        bundle_ref["runtime_bundle_id"] != RUNTIME_BUNDLE_ID
        or bundle_ref["version"] != RUNTIME_BUNDLE_VERSION
        or bundle_ref["path"] != RUNTIME_BUNDLE_PATH.as_posix()
        or package["policy_realization"]["path"]
        != POLICY_REALIZATION_PATH.as_posix()
        or package["policy_realization"]["sha256"]
        != POLICY_REALIZATION_SOURCE_SHA256
    ):
        _fail(
            ExecutableAdmissionCode.BUNDLE_IDENTITY_MISMATCH,
            pointer="/runtime_bundle",
        )
    bundle_path = _inside(
        root, root / bundle_ref["path"], pointer="/runtime_bundle/path"
    )
    bundle, bundle_raw = _read_json(bundle_path, pointer="/runtime_bundle")
    bundle_source_sha = hashlib.sha256(bundle_raw).hexdigest()
    bundle_canonical_sha = canonical_sha256(bundle)
    if (
        bundle_source_sha != bundle_ref["source_sha256"]
        or bundle_canonical_sha != bundle_ref["canonical_sha256"]
    ):
        _fail(
            ExecutableAdmissionCode.INTEGRITY_MISMATCH,
            pointer="/runtime_bundle",
            detail="package_reference_hash_mismatch",
        )
    if (
        bundle.get("runtime_bundle_id") != RUNTIME_BUNDLE_ID
        or bundle.get("version") != RUNTIME_BUNDLE_VERSION
        or bundle.get("status") != "accepted_runtime_bundle"
        or bundle.get("package_id") != PACKAGE_ID
        or bundle.get("package_version") != PACKAGE_VERSION
    ):
        _fail(
            ExecutableAdmissionCode.BUNDLE_IDENTITY_MISMATCH,
            pointer="/runtime_bundle/runtime_bundle_id",
        )

    first = build_panic_runtime_bundle_document(project_root=root)
    second = build_panic_runtime_bundle_document(project_root=root)
    if canonical_bytes(first) != canonical_bytes(second):
        _fail(
            ExecutableAdmissionCode.BUNDLE_MATERIALIZATION_MISMATCH,
            pointer="/runtime_bundle",
            detail="independent_build_disagreement",
        )
    if canonical_bytes(bundle) != canonical_bytes(first):
        _fail(
            ExecutableAdmissionCode.BUNDLE_MATERIALIZATION_MISMATCH,
            pointer="/runtime_bundle",
            detail="released_bundle_differs_from_static_build",
        )
    expected_package = build_panic_executable_package_document(
        runtime_bundle_source_sha256=bundle_source_sha,
        runtime_bundle_canonical_sha256=bundle_canonical_sha,
        project_root=root,
    )
    if package != expected_package:
        _fail(
            ExecutableAdmissionCode.PACKAGE_MATERIALIZATION_MISMATCH,
            pointer="/package",
            detail="released_package_differs_from_static_build",
        )
    if (
        package["masim_usage"]["package_version"] != masim.__version__
        or package["masim_usage"]["mode"] != "read_only_public_interfaces"
        or package["masim_usage"]["source_modification_allowed"] is not False
    ):
        _fail(
            ExecutableAdmissionCode.MASIM_BOUNDARY_MISMATCH,
            pointer="/masim_usage",
        )
    _verify_components(package, bundle)
    coverage = _verify_coverage(bundle)
    return ExecutableAdmission(
        package_id=PACKAGE_ID,
        package_version=PACKAGE_VERSION,
        package_path=package_path.relative_to(root).as_posix(),
        package_source_sha256=package_source_sha,
        package_canonical_sha256=canonical_sha256(package),
        runtime_bundle_id=RUNTIME_BUNDLE_ID,
        runtime_bundle_version=RUNTIME_BUNDLE_VERSION,
        runtime_bundle_path=bundle_path.relative_to(root).as_posix(),
        runtime_bundle_source_sha256=bundle_source_sha,
        runtime_bundle_canonical_sha256=bundle_canonical_sha,
        schema_id=schema_id,
        schema_sha256=schema_sha,
        deterministic_materialization=True,
        component_complete=True,
        execution_eligible=True,
        accepted=True,
        coverage=MappingProxyType(coverage),
        package_document=_freeze(package),
        runtime_bundle_document=_freeze(bundle),
    )


__all__ = [
    "ExecutableAdmission",
    "ExecutableAdmissionCode",
    "ExecutableAdmissionError",
    "load_panic_executable_package",
]
