"""Fail-closed carrier binding for the bounded SingHealth lineage.

The accepted Scenario Configuration remains non-executable.  This module
identifies its exact release, derives the released semantic catalog, and
projects only the selected technical--operations--GCIO lineage to Contracts
V1 carriers.
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

from h2epr.artifacts.provenance import runtime_field
from h2epr.bundles.canonical import sha256_value
from h2epr.configuration import (
    ScenarioConfigurationAdmission,
    load_scenario_configuration,
)


BINDING_FORMAT = "h2epr.bounded-lineage-binding.v0_1"
RELEASE_FORMAT = "h2epr.bounded-lineage-binding-release.v0_1"
BINDING_ID = "h2epr.0616.scm-technical-operations-gcio.binding.v0_1"
EVENT_ID = "H2EPR-0616"
FIXTURE_SOURCE_REF = (
    "fixture.h2epr.0616.scm_technical_operations_gcio.positive.v0_1"
)

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_STABLE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,191}$")
_PARAMETER_TYPES = frozenset(
    {
        "enum",
        "integer",
        "nullable_time_interval",
        "sha256",
        "stable_id",
        "stable_id_array",
    }
)
_CARRIERS = frozenset({"parameters", "expiry_time"})
_EXPECTED_ACTION_KEYS = (
    "technical.share_technical_finding",
    "operations.request_fact_verification",
    "operations.escalate_operational_concern",
    "gcio.request_operational_clarification",
)
_EXPECTED_ACTOR_IDS = (
    "actor.0616.unit.technical.scm-application-database",
    "actor.0616.unit.operations.application-scm-coordination",
    "actor.0616.office.singhealth-gcio",
)
_EXPECTED_CAPABILITY_IDS = (
    "technical_administration_and_line_security_staff",
    "ihis_operational_and_scm_management",
    "singhealth_group_chief_information_officer",
)
_EXPECTED_SOURCE_ROUTE_IDS = (
    "opening.0616.route.operations-gcio",
    "opening.0616.route.technical-operations",
)
_EXPECTED_POLICY_IMPLEMENTATIONS = {
    "POL-0616-AUTH-01": "h2epr.policy.0616.auth.capacity_scope.v0_1",
    "POL-0616-INFO-01": "h2epr.policy.0616.info.source_delivery.v0_1",
    "POL-0616-LIFECYCLE-01": (
        "h2epr.policy.0616.lifecycle.typed_idempotency.v0_1"
    ),
    "POL-0616-ROUTE-01": "h2epr.policy.0616.route.exact_delivery.v0_1",
    "POL-0616-TECH-01": (
        "h2epr.policy.0616.tech.verification_result.v0_1"
    ),
    "POL-0616-TIME-01": "h2epr.policy.0616.time.partial_order.v0_1",
}
_EXPECTED_UNBOUND_POLICIES = (
    "POL-0616-COORD-01",
    "POL-0616-INCIDENT-01",
    "POL-0616-NOTIFY-01",
)
_EXPECTED_IMPLEMENTATION_PATHS = {
    "scenario_package": (
        "src/h2epr/scenarios/singhealth_data_breach/__init__.py"
    ),
    "carrier_loader": (
        "src/h2epr/scenarios/singhealth_data_breach/lineage_v0_1/binding.py"
    ),
    "environment_policies": (
        "src/h2epr/scenarios/singhealth_data_breach/lineage_v0_1/environment.py"
    ),
    "participant_policies": (
        "src/h2epr/scenarios/singhealth_data_breach/lineage_v0_1/policies.py"
    ),
    "public_api": (
        "src/h2epr/scenarios/singhealth_data_breach/lineage_v0_1/__init__.py"
    ),
}
_EXPECTED_COVERAGE = {
    "semantic_products": 9,
    "decision_and_population_commitments": 29,
    "observation_placements": 62,
    "private_state_placements": 44,
    "intent_placements": 54,
}


class LineageBindingError(ValueError):
    """The binding, an upstream identity, or a carrier projection is invalid."""


class _DuplicateKey(ValueError):
    pass


def _fail(code: str, detail: str = "") -> None:
    suffix = f":{detail}" if detail else ""
    raise LineageBindingError(f"{code}{suffix}")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail("LINEAGE_JSON_INVALID", label)
        raise AssertionError from exc
    if not isinstance(value, dict):
        _fail("LINEAGE_JSON_OBJECT_REQUIRED", label)
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = ",".join(sorted(expected - actual))
        extra = ",".join(sorted(actual - expected))
        _fail(
            "LINEAGE_FIELDS_MISMATCH",
            f"{label}:missing={missing}:extra={extra}",
        )


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        _fail("LINEAGE_STRING_INVALID", label)
    return value


def _stable_id(value: Any, label: str) -> str:
    result = _string(value, label)
    if _STABLE_ID.fullmatch(result) is None:
        _fail("LINEAGE_STABLE_ID_INVALID", label)
    return result


def _sha256(value: Any, label: str) -> str:
    result = _string(value, label)
    if _SHA256.fullmatch(result) is None:
        _fail("LINEAGE_SHA256_INVALID", label)
    return result


def _boolean(value: Any, label: str) -> bool:
    if type(value) is not bool:
        _fail("LINEAGE_BOOLEAN_INVALID", label)
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        _fail("LINEAGE_INTEGER_INVALID", label)
    return value


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("LINEAGE_OBJECT_REQUIRED", label)
    return value


def _array(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)):
        _fail("LINEAGE_ARRAY_REQUIRED", label)
    return value


def _unique_ids(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
    sorted_required: bool = False,
) -> tuple[str, ...]:
    items = _array(value, label)
    if not items and not allow_empty:
        _fail("LINEAGE_ARRAY_EMPTY", label)
    result = tuple(_stable_id(item, label) for item in items)
    if len(result) != len(set(result)):
        _fail("LINEAGE_ARRAY_DUPLICATE", label)
    if sorted_required and result != tuple(sorted(result)):
        _fail("LINEAGE_ARRAY_UNSORTED", label)
    return result


def _inside(root: Path, relative_value: Any, label: str) -> Path:
    relative = Path(_string(relative_value, label))
    if relative.is_absolute() or ".." in relative.parts:
        _fail("LINEAGE_PATH_UNSAFE", label)
    result = (root / relative).resolve()
    if not result.is_relative_to(root) or not result.is_file():
        _fail("LINEAGE_PATH_INVALID", label)
    return result


def _find_project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        roots = [
            parent
            for parent in path.resolve().parents
            if parent.joinpath("src/h2epr").is_dir()
            and parent.joinpath("contracts/v1").is_dir()
        ]
        if not roots:
            _fail("LINEAGE_PROJECT_ROOT_NOT_FOUND")
        root = roots[0]
    if not root.joinpath("src/h2epr").is_dir():
        _fail("LINEAGE_PROJECT_ROOT_INVALID", root.as_posix())
    return root


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _time_interval(value: Any, label: str, *, nullable: bool = False) -> Any:
    if value is None and nullable:
        return None
    item = _object(value, label)
    _exact_keys(
        item,
        {"lower", "upper", "precision", "timezone", "uncertainty"},
        label,
    )
    lower = _string(item["lower"], f"{label}.lower")
    upper = _string(item["upper"], f"{label}.upper")
    try:
        lower_time = datetime.fromisoformat(lower)
        upper_time = datetime.fromisoformat(upper)
    except ValueError:
        _fail("LINEAGE_TIME_INVALID", label)
    if lower_time.tzinfo is None or upper_time.tzinfo is None or lower_time > upper_time:
        _fail("LINEAGE_TIME_INVALID", label)
    _stable_id(item["precision"], f"{label}.precision")
    _string(item["timezone"], f"{label}.timezone")
    _string(item["uncertainty"], f"{label}.uncertainty")
    return copy.deepcopy(dict(item))


def _runtime_values(fields: Sequence[Mapping[str, Any]], label: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for index, field in enumerate(fields):
        if not isinstance(field, Mapping) or set(field) != {
            "field_name",
            "runtime_value",
        }:
            _fail("LINEAGE_RUNTIME_FIELD_INVALID", f"{label}.{index}")
        name = _stable_id(field["field_name"], f"{label}.{index}.field_name")
        runtime_value = _object(
            field["runtime_value"], f"{label}.{index}.runtime_value"
        )
        if "value" not in runtime_value or name in result:
            _fail("LINEAGE_RUNTIME_FIELD_INVALID", f"{label}.{index}")
        result[name] = runtime_value["value"]
    return result


def _markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    padded = "\n" + text
    start = padded.find(marker)
    if start < 0:
        _fail("LINEAGE_RELEASE_GRAMMAR_MISMATCH", heading)
    body_start = start + len(marker)
    next_heading = re.search(r"\n#{2,3} ", padded[body_start:])
    end = (
        len(padded)
        if next_heading is None
        else body_start + next_heading.start()
    )
    return padded[body_start:end]


def _table_first_column_ids(section: str, label: str) -> tuple[str, ...]:
    result: list[str] = []
    table_started = False
    for line in section.splitlines():
        if line.startswith("|"):
            table_started = True
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            match = re.fullmatch(r"`([^`]+)`", cells[0]) if cells else None
            if match:
                result.append(match.group(1))
        elif table_started and line.strip():
            break
    if not result or len(result) != len(set(result)):
        _fail("LINEAGE_RELEASE_GRAMMAR_MISMATCH", label)
    return tuple(result)


def _population_private_state(text: str, label: str) -> tuple[str, ...]:
    marker = "Each unit may retain"
    start = text.find(marker)
    if start < 0:
        _fail("LINEAGE_RELEASE_GRAMMAR_MISMATCH", label)
    end = text.find("\n\nThese items", start)
    if end < 0:
        _fail("LINEAGE_RELEASE_GRAMMAR_MISMATCH", label)
    result = tuple(re.findall(r"^- `([^`]+)`", text[start:end], flags=re.MULTILINE))
    if not result or len(result) != len(set(result)):
        _fail("LINEAGE_RELEASE_GRAMMAR_MISMATCH", label)
    return result


def _decision_ids(text: str, kind: str, label: str) -> tuple[str, ...]:
    if kind == "agent_definition":
        result = tuple(re.findall(r"^### `([^`]+)` —", text, flags=re.MULTILINE))
    else:
        letters = re.findall(r"^### Situation ([A-Z]) —", text, flags=re.MULTILINE)
        result = tuple(f"situation_{letter.lower()}" for letter in letters)
    if not result or len(result) != len(set(result)):
        _fail("LINEAGE_RELEASE_GRAMMAR_MISMATCH", label)
    return result


def _inventory_catalog(
    text: str,
    heading: str,
    label: str,
) -> Mapping[str, tuple[str, ...]]:
    section = _markdown_section(text, heading)
    result: dict[str, tuple[str, ...]] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2:
            continue
        capability = re.fullmatch(r"`([^`]+)`", cells[0])
        if not capability:
            continue
        values = tuple(re.findall(r"`([^`]+)`", cells[1]))
        if not values or len(values) != len(set(values)):
            _fail("LINEAGE_SEMANTIC_INVENTORY_INVALID", label)
        result[capability.group(1)] = values
    if not result:
        _fail("LINEAGE_SEMANTIC_INVENTORY_INVALID", label)
    return MappingProxyType(result)


def _inventory_counts(text: str) -> Mapping[str, tuple[int, int, int, int]]:
    section = _markdown_section(text, "## 2. Product inventory and runtime disposition")
    result: dict[str, tuple[int, int, int, int]] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            continue
        capability = re.fullmatch(r"`([^`]+)`", cells[1])
        if capability is None or not all(cell.isdigit() for cell in cells[2:6]):
            continue
        result[capability.group(1)] = tuple(int(cell) for cell in cells[2:6])
    if len(result) != 9:
        _fail("LINEAGE_SEMANTIC_INVENTORY_INVALID", "product_counts")
    return MappingProxyType(result)


@dataclass(frozen=True)
class SemanticProduct:
    product_id: str
    capability_id: str
    product_kind: str
    version: str
    project_relative_path: str
    content_sha256: str
    representation_class: str
    observation_ids: tuple[str, ...]
    private_state_ids: tuple[str, ...]
    decision_ids: tuple[str, ...]
    commitment_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]


@dataclass(frozen=True)
class IntentPlacement:
    capability_id: str
    reader_intent_id: str
    action_type: str
    action_schema_version: str


@dataclass(frozen=True)
class DerivedRosterProfile:
    release_id: str
    release_manifest_sha256: str
    mapping_profile_id: str
    mapping_profile_sha256: str
    products: Mapping[str, SemanticProduct]
    capabilities: Mapping[str, SemanticProduct]
    coverage: Mapping[str, int]

    def intent(self, capability_id: str, reader_intent_id: str) -> IntentPlacement:
        try:
            product = self.capabilities[capability_id]
        except KeyError as exc:
            _fail("LINEAGE_CAPABILITY_UNKNOWN", capability_id)
            raise AssertionError from exc
        if reader_intent_id not in product.intent_ids:
            _fail(
                "LINEAGE_INTENT_PLACEMENT_UNKNOWN",
                f"{capability_id}:{reader_intent_id}",
            )
        return IntentPlacement(
            capability_id=capability_id,
            reader_intent_id=reader_intent_id,
            action_type=(
                f"h2epr.action.0616.{capability_id}.{reader_intent_id}"
            ),
            action_schema_version=(
                f"h2epr.intent.0616.{capability_id}.{reader_intent_id}.v0_1"
            ),
        )

    def observation_field(self, capability_id: str, reader_id: str) -> str:
        try:
            product = self.capabilities[capability_id]
        except KeyError as exc:
            _fail("LINEAGE_CAPABILITY_UNKNOWN", capability_id)
            raise AssertionError from exc
        if reader_id not in product.observation_ids:
            _fail(
                "LINEAGE_OBSERVATION_PLACEMENT_UNKNOWN",
                f"{capability_id}:{reader_id}",
            )
        return f"obs.{capability_id}.{reader_id}"


def _product_capabilities(
    admission: ScenarioConfigurationAdmission,
) -> Mapping[str, str]:
    result: dict[str, str] = {}
    for actor in admission.document["named_actors"]:
        result[actor["participant_product_id"]] = actor["capability_id"]
    for unit in admission.document["population_units"]:
        product_id = unit["population_product_id"]
        actor = next(
            row
            for row in admission.document["population_actors"]
            if row["actor_id"] == unit["actor_id"]
        )
        prior = result.setdefault(product_id, actor["capability_id"])
        if prior != actor["capability_id"]:
            _fail("LINEAGE_PRODUCT_CAPABILITY_AMBIGUOUS", product_id)
    return MappingProxyType(result)


def _load_derived_profile(
    root: Path,
    *,
    admission: ScenarioConfigurationAdmission,
    roster_manifest_path: Path,
    roster_manifest_sha256: str,
    semantic_inventory_path: Path,
    semantic_inventory_sha256: str,
    mapping_profile_path: Path,
    mapping_profile_sha256: str,
) -> DerivedRosterProfile:
    if _sha256_file(roster_manifest_path) != roster_manifest_sha256:
        _fail("LINEAGE_ROSTER_MANIFEST_HASH_MISMATCH")
    if _sha256_file(semantic_inventory_path) != semantic_inventory_sha256:
        _fail("LINEAGE_SEMANTIC_INVENTORY_HASH_MISMATCH")
    if _sha256_file(mapping_profile_path) != mapping_profile_sha256:
        _fail("LINEAGE_MAPPING_PROFILE_HASH_MISMATCH")

    mapping_text = mapping_profile_path.read_text(encoding="utf-8")
    required_mapping_tokens = (
        "h2epr.action.0616.<capability_id>.<reader_intent_id>",
        "h2epr.intent.0616.<capability_id>.<reader_intent_id>.v0_1",
        "h2epr.commitment.0616.<capability_id>.<released_decision_id>",
    )
    if any(token not in mapping_text for token in required_mapping_tokens):
        _fail("LINEAGE_MAPPING_PROFILE_GRAMMAR_MISMATCH")

    roster = _read_json(roster_manifest_path, "roster_manifest")
    _exact_keys(
        roster,
        {
            "schema",
            "release_id",
            "version",
            "event_id",
            "released_on",
            "status",
            "integrity_algorithm",
            "roster",
            "semantic_skeleton",
            "evidence_authorities",
            "agent_definitions",
            "population_models",
            "interface_preflights",
            "scenario_dispositions",
            "accepted_owner_decisions",
            "next_stage",
        },
        "roster_manifest",
    )
    if (
        roster["schema"] != "h2epr.roster-definition-release.v0_1"
        or roster["release_id"]
        != "H2EPR-0616-ROSTER-DEFINITION-RELEASE-v0.1"
        or roster["event_id"] != EVENT_ID
        or roster["status"] != "accepted_semantic_release"
    ):
        _fail("LINEAGE_ROSTER_MANIFEST_IDENTITY_MISMATCH")

    inventory_text = semantic_inventory_path.read_text(encoding="utf-8")
    inventory_observations = _inventory_catalog(
        inventory_text,
        "### 3.1 Released observations by capability",
        "observations",
    )
    inventory_private = _inventory_catalog(
        inventory_text,
        "### 4.1 Replayable participant state",
        "private_state",
    )
    inventory_intents = _inventory_catalog(
        inventory_text,
        "### 5.1 Released intents by capability",
        "intents",
    )
    inventory_counts = _inventory_counts(inventory_text)
    product_capabilities = _product_capabilities(admission)

    products: dict[str, SemanticProduct] = {}
    capabilities: dict[str, SemanticProduct] = {}
    raw_products = [
        *(dict(item, product_kind="agent_definition") for item in roster["agent_definitions"]),
        *(dict(item, product_kind="population_model") for item in roster["population_models"]),
    ]
    for index, row in enumerate(raw_products):
        label = f"roster.product.{index}"
        _exact_keys(
            row,
            {"id", "version", "path", "sha256", "product_kind"},
            label,
        )
        product_id = _stable_id(row["id"], f"{label}.id")
        if product_id not in product_capabilities:
            _fail("LINEAGE_PRODUCT_NOT_ASSEMBLED", product_id)
        capability_id = product_capabilities[product_id]
        path = _inside(root, row["path"], f"{label}.path")
        content_sha256 = _sha256(row["sha256"], f"{label}.sha256")
        if _sha256_file(path) != content_sha256:
            _fail("LINEAGE_PRODUCT_HASH_MISMATCH", product_id)
        text = path.read_text(encoding="utf-8")
        observations = _table_first_column_ids(
            _markdown_section(
                text,
                (
                    "### Observation inventory"
                    if row["product_kind"] == "agent_definition"
                    else "### Participant observations"
                ),
            ),
            f"{product_id}.observations",
        )
        intents = _table_first_column_ids(
            _markdown_section(text, "## 7. Intent and result boundary"),
            f"{product_id}.intents",
        )
        private = (
            _table_first_column_ids(
                _markdown_section(text, "### Persistent decision state"),
                f"{product_id}.private_state",
            )
            if row["product_kind"] == "agent_definition"
            else _population_private_state(text, f"{product_id}.private_state")
        )
        decisions = _decision_ids(text, row["product_kind"], product_id)
        if (
            inventory_observations.get(capability_id) != observations
            or inventory_private.get(capability_id) != private
            or inventory_intents.get(capability_id) != intents
            or inventory_counts.get(capability_id)
            != (len(observations), len(private), len(decisions), len(intents))
        ):
            _fail("LINEAGE_PRODUCT_INVENTORY_MISMATCH", capability_id)
        commitments = tuple(
            f"h2epr.commitment.0616.{capability_id}.{decision_id}"
            for decision_id in decisions
        )
        product = SemanticProduct(
            product_id=product_id,
            capability_id=capability_id,
            product_kind=row["product_kind"],
            version=_string(row["version"], f"{label}.version"),
            project_relative_path=path.relative_to(root).as_posix(),
            content_sha256=content_sha256,
            representation_class=(
                "autonomous_participant_agent"
                if row["product_kind"] == "agent_definition"
                else "aggregate_population_agent"
            ),
            observation_ids=observations,
            private_state_ids=private,
            decision_ids=decisions,
            commitment_ids=commitments,
            intent_ids=intents,
        )
        if product_id in products or capability_id in capabilities:
            _fail("LINEAGE_PRODUCT_IDENTITY_DUPLICATE", product_id)
        products[product_id] = product
        capabilities[capability_id] = product

    coverage = {
        "semantic_products": len(products),
        "decision_and_population_commitments": sum(
            len(product.decision_ids) for product in products.values()
        ),
        "observation_placements": sum(
            len(product.observation_ids) for product in products.values()
        ),
        "private_state_placements": sum(
            len(product.private_state_ids) for product in products.values()
        ),
        "intent_placements": sum(
            len(product.intent_ids) for product in products.values()
        ),
    }
    if coverage != _EXPECTED_COVERAGE:
        _fail("LINEAGE_DERIVED_COVERAGE_MISMATCH")
    return DerivedRosterProfile(
        release_id=roster["release_id"],
        release_manifest_sha256=roster_manifest_sha256,
        mapping_profile_id=admission.mapping_profile_id,
        mapping_profile_sha256=mapping_profile_sha256,
        products=MappingProxyType(products),
        capabilities=MappingProxyType(capabilities),
        coverage=MappingProxyType(coverage),
    )


@dataclass(frozen=True)
class ParameterContract:
    name: str
    value_type: str
    carrier: str
    values: tuple[str, ...]

    def validate(self, value: Any) -> Any:
        label = f"parameter.{self.name}"
        if self.value_type == "stable_id":
            return _stable_id(value, label)
        if self.value_type == "sha256":
            return _sha256(value, label)
        if self.value_type == "integer":
            return _integer(value, label)
        if self.value_type == "enum":
            result = _stable_id(value, label)
            if result not in self.values:
                _fail("LINEAGE_PARAMETER_OUTSIDE_DOMAIN", self.name)
            return result
        if self.value_type == "stable_id_array":
            return list(_unique_ids(value, label, sorted_required=True))
        if self.value_type == "nullable_time_interval":
            return _time_interval(value, label, nullable=True)
        raise AssertionError(self.value_type)


@dataclass(frozen=True)
class ObservationContract:
    actor_id: str
    capability_id: str
    reader_observation_id: str
    field_name: str
    value_type: str
    values: tuple[str, ...]

    def validate(self, value: Any) -> Any:
        label = f"observation.{self.actor_id}.{self.reader_observation_id}"
        if self.value_type == "stable_id":
            return _stable_id(value, label)
        if self.value_type == "stable_id_array":
            return list(_unique_ids(value, label, sorted_required=True))
        if self.value_type == "enum":
            result = _stable_id(value, label)
            if result not in self.values:
                _fail("LINEAGE_OBSERVATION_OUTSIDE_DOMAIN", label)
            return result
        raise AssertionError(self.value_type)


@dataclass(frozen=True)
class RouteContract:
    route_id: str
    source_opening_route_id: str
    source_actor_id: str
    target_actor_id: str
    required_source_capacity_id: str
    channel_id: str
    performative: str
    confidentiality: str
    latency_ticks: int

    def as_v1_definition(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "source_id": self.source_actor_id,
            "target_id": self.target_actor_id,
            "performative": self.performative,
            "channel": self.channel_id,
            "confidentiality": self.confidentiality,
            "latency_ticks": self.latency_ticks,
            "expiry_policy": "deliver_if_due_before_expiry",
            "review_state": "reviewed",
        }


@dataclass(frozen=True)
class ActionContract:
    action_key: str
    actor_id: str
    capability_id: str
    reader_intent_id: str
    action_type: str
    action_schema_version: str
    commitment_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    authority_ref_ids: tuple[str, ...]
    target_actor_ids: tuple[str, ...]
    lifecycle_family: str
    adjudication_family: str
    object_id_parameter: str
    object_version_parameter: str
    parameters: tuple[ParameterContract, ...]
    message_route_id: str
    forbidden_self_results: tuple[str, ...]

    @property
    def parameter_by_name(self) -> Mapping[str, ParameterContract]:
        return MappingProxyType({item.name: item for item in self.parameters})


@dataclass(frozen=True)
class PolicyBinding:
    policy_id: str
    semantic_version: str
    selection: str
    implementation_id: str
    status: str


@dataclass(frozen=True)
class LineageBinding:
    release_id: str
    release_manifest_sha256: str
    binding_id: str
    binding_sha256: str
    implementation_sha256s: Mapping[str, str]
    version: str
    configuration: ScenarioConfigurationAdmission
    roster_profile: DerivedRosterProfile
    admission_receipt_sha256: str
    actor_ids: tuple[str, ...]
    capability_ids: tuple[str, ...]
    actors: Mapping[str, Mapping[str, Any]]
    relationship_refs: tuple[str, ...]
    source_route_ids: tuple[str, ...]
    policy_bindings: Mapping[str, PolicyBinding]
    unbound_policy_ids: tuple[str, ...]
    routes: Mapping[str, RouteContract]
    observations: Mapping[tuple[str, str], ObservationContract]
    actions: Mapping[str, ActionContract]
    decision_bindings: tuple[Mapping[str, Any], ...]
    document: Mapping[str, Any]

    def action_definition(self, action_key: str) -> dict[str, Any]:
        contract = self._action(action_key)
        representation = self.roster_profile.capabilities[
            contract.capability_id
        ].representation_class
        return {
            "action_type": contract.action_type,
            "version": contract.action_schema_version,
            "allowed_representation_classes": [representation],
            "parameter_names": sorted(item.name for item in contract.parameters),
            "state_changing": True,
            "review_state": "reviewed",
        }

    def route_definition(self, route_id: str) -> dict[str, Any]:
        try:
            return self.routes[route_id].as_v1_definition()
        except KeyError as exc:
            _fail("LINEAGE_ROUTE_UNKNOWN", route_id)
            raise AssertionError from exc

    def project_observation(
        self,
        action_key: str,
        *,
        observation_id: str,
        values: Mapping[str, Any],
    ) -> dict[str, Any]:
        contract = self._action(action_key)
        _stable_id(observation_id, "observation_id")
        if set(values) != set(contract.observation_ids):
            _fail("LINEAGE_OBSERVATION_INVENTORY_MISMATCH", action_key)
        fields = []
        for reader_id in sorted(values):
            observation = self.observations[(contract.actor_id, reader_id)]
            value = observation.validate(values[reader_id])
            fields.append(
                runtime_field(
                    observation.field_name,
                    value,
                    source_kind="synthetic",
                    source_ref_id=FIXTURE_SOURCE_REF,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_private",
                    visibility_scope_ids=(contract.actor_id,),
                    consumers=(contract.actor_id, "world.reducer"),
                )
            )
        return {"observation_id": observation_id, "fields": fields}

    def read_observation(
        self, action_key: str, payload: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        contract = self._action(action_key)
        _exact_keys(payload, {"observation_id", "fields"}, "observation_payload")
        _stable_id(payload["observation_id"], "observation_payload.observation_id")
        by_field = _runtime_values(payload["fields"], "observation_payload.fields")
        expected = {
            self.observations[(contract.actor_id, reader_id)].field_name: reader_id
            for reader_id in contract.observation_ids
        }
        if set(by_field) != set(expected):
            _fail("LINEAGE_OBSERVATION_CARRIER_MISMATCH", action_key)
        decoded = {
            reader_id: self.observations[(contract.actor_id, reader_id)].validate(
                by_field[field_name]
            )
            for field_name, reader_id in expected.items()
        }
        return MappingProxyType(decoded)

    def project_action(
        self,
        action_key: str,
        *,
        intent_id: str,
        run_id: str,
        logical_tick: int,
        decision_ref: str,
        observation_refs: Sequence[str],
        semantic_parameters: Mapping[str, Any],
        earliest_effect_time: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        contract = self._action(action_key)
        _stable_id(intent_id, "intent_id")
        _stable_id(run_id, "run_id")
        _integer(logical_tick, "logical_tick")
        _stable_id(decision_ref, "decision_ref")
        observation_ids = tuple(
            _stable_id(item, "observation_ref") for item in observation_refs
        )
        if not observation_ids or len(observation_ids) != len(set(observation_ids)):
            _fail("LINEAGE_OBSERVATION_REFS_INVALID", action_key)
        contracts = contract.parameter_by_name
        if set(semantic_parameters) != set(contracts):
            _fail("LINEAGE_PARAMETER_INVENTORY_MISMATCH", action_key)
        validated = {
            name: contracts[name].validate(value)
            for name, value in semantic_parameters.items()
        }
        earliest = (
            None
            if earliest_effect_time is None
            else _time_interval(earliest_effect_time, "earliest_effect_time")
        )
        parameter_fields = self._carrier_fields(contract, validated, "parameters")
        expiry_contract = next(
            item for item in contract.parameters if item.carrier == "expiry_time"
        )
        expiry = validated[expiry_contract.name]
        action = {
            "intent_id": intent_id,
            "run_id": run_id,
            "logical_tick": logical_tick,
            "actor_id": contract.actor_id,
            "action_type": contract.action_type,
            "action_schema_version": contract.action_schema_version,
            "target_entity_ids": list(contract.target_actor_ids),
            "parameters": parameter_fields,
            "claimed_authority_refs": list(contract.authority_ref_ids),
            "resource_offer_or_request": [],
            "earliest_effect_time": earliest,
            "expiry_time": expiry,
            "observation_refs": list(observation_ids),
            "decision_ref": decision_ref,
            "idempotency_key": self._action_idempotency_key(
                contract, validated
            ),
            "visibility": "restricted",
        }
        self.validate_action(action_key, action)
        return action

    def validate_action(self, action_key: str, action: Mapping[str, Any]) -> None:
        contract = self._action(action_key)
        _exact_keys(
            action,
            {
                "intent_id",
                "run_id",
                "logical_tick",
                "actor_id",
                "action_type",
                "action_schema_version",
                "target_entity_ids",
                "parameters",
                "claimed_authority_refs",
                "resource_offer_or_request",
                "earliest_effect_time",
                "expiry_time",
                "observation_refs",
                "decision_ref",
                "idempotency_key",
                "visibility",
            },
            f"action.{action_key}",
        )
        if (
            action["actor_id"] != contract.actor_id
            or action["action_type"] != contract.action_type
            or action["action_schema_version"] != contract.action_schema_version
            or tuple(action["target_entity_ids"]) != contract.target_actor_ids
            or tuple(action["claimed_authority_refs"]) != contract.authority_ref_ids
            or action["resource_offer_or_request"] != []
            or action["visibility"] != "restricted"
        ):
            _fail("LINEAGE_ACTION_ENVELOPE_MISMATCH", action_key)
        values = _runtime_values(action["parameters"], f"action.{action_key}.parameters")
        expected = {
            item.name for item in contract.parameters if item.carrier == "parameters"
        }
        if set(values) != expected:
            _fail("LINEAGE_ACTION_CARRIER_MISMATCH", action_key)
        expiry_contract = next(
            item for item in contract.parameters if item.carrier == "expiry_time"
        )
        combined = {
            **values,
            expiry_contract.name: expiry_contract.validate(action["expiry_time"]),
        }
        validated = {
            name: contract.parameter_by_name[name].validate(value)
            for name, value in combined.items()
        }
        route = self.routes[contract.message_route_id]
        actor = self.actors[contract.actor_id]
        if (
            validated.get("sender_id") != contract.actor_id
            or validated.get("recipient_id") != route.target_actor_id
            or validated.get("capacity_id") != actor["selected_capacity_id"]
            or validated.get("route_id") != route.route_id
        ):
            _fail("LINEAGE_ACTION_SEMANTIC_ENVELOPE_MISMATCH", action_key)
        if set(contract.forbidden_self_results).intersection(validated):
            _fail("LINEAGE_RESULT_CONFLATION", action_key)
        if action["idempotency_key"] != self._action_idempotency_key(
            contract, validated
        ):
            _fail("LINEAGE_ACTION_IDEMPOTENCY_MISMATCH", action_key)

    def project_message(
        self,
        action_key: str,
        action: Mapping[str, Any],
        *,
        message_intent_id: str,
        earliest_delivery_time: Mapping[str, Any],
        correlation_ids: Sequence[str],
    ) -> dict[str, Any]:
        contract = self._action(action_key)
        self.validate_action(action_key, action)
        route = self.routes[contract.message_route_id]
        _stable_id(message_intent_id, "message_intent_id")
        correlations = tuple(
            _stable_id(item, "correlation_id") for item in correlation_ids
        )
        if (
            not correlations
            or len(correlations) != len(set(correlations))
            or action["intent_id"] not in correlations
        ):
            _fail("LINEAGE_CORRELATION_IDS_INVALID", action_key)
        message = {
            "message_intent_id": message_intent_id,
            "run_id": action["run_id"],
            "logical_tick": action["logical_tick"],
            "sender_id": contract.actor_id,
            "recipient_ids": list(contract.target_actor_ids),
            "performative": route.performative,
            "content_schema_version": (
                f"h2epr.message.0616.{contract.capability_id}."
                f"{contract.reader_intent_id}.v0_1"
            ),
            "structured_content": copy.deepcopy(list(action["parameters"])),
            "channel": route.channel_id,
            "confidentiality": route.confidentiality,
            "created_at": copy.deepcopy(action["earliest_effect_time"]),
            "earliest_delivery_time": _time_interval(
                earliest_delivery_time, "earliest_delivery_time"
            ),
            "expiry_time": copy.deepcopy(action["expiry_time"]),
            "decision_ref": action["decision_ref"],
            "idempotency_key": "idem.message."
            + sha256_value(
                {
                    "action_idempotency_key": action["idempotency_key"],
                    "route_id": route.route_id,
                    "binding_id": self.binding_id,
                }
            )[:48],
            "correlation_ids": list(correlations),
        }
        self.validate_message(action_key, action, message)
        return message

    def validate_message(
        self,
        action_key: str,
        action: Mapping[str, Any],
        message: Mapping[str, Any],
    ) -> None:
        contract = self._action(action_key)
        route = self.routes[contract.message_route_id]
        expected_schema = (
            f"h2epr.message.0616.{contract.capability_id}."
            f"{contract.reader_intent_id}.v0_1"
        )
        _exact_keys(
            message,
            {
                "message_intent_id",
                "run_id",
                "logical_tick",
                "sender_id",
                "recipient_ids",
                "performative",
                "content_schema_version",
                "structured_content",
                "channel",
                "confidentiality",
                "created_at",
                "earliest_delivery_time",
                "expiry_time",
                "decision_ref",
                "idempotency_key",
                "correlation_ids",
            },
            f"message.{action_key}",
        )
        if (
            message["run_id"] != action["run_id"]
            or message["logical_tick"] != action["logical_tick"]
            or message["sender_id"] != route.source_actor_id
            or tuple(message["recipient_ids"]) != (route.target_actor_id,)
            or message["performative"] != route.performative
            or message["content_schema_version"] != expected_schema
            or message["channel"] != route.channel_id
            or message["confidentiality"] != route.confidentiality
            or message["decision_ref"] != action["decision_ref"]
            or message["expiry_time"] != action["expiry_time"]
        ):
            _fail("LINEAGE_MESSAGE_ENVELOPE_MISMATCH", action_key)
        if _runtime_values(
            message["structured_content"], f"message.{action_key}.content"
        ) != _runtime_values(action["parameters"], f"action.{action_key}.content"):
            _fail("LINEAGE_MESSAGE_CONTENT_MISMATCH", action_key)
        if action["intent_id"] not in message["correlation_ids"]:
            _fail("LINEAGE_ACTION_CORRELATION_MISSING", action_key)
        expected_key = "idem.message." + sha256_value(
            {
                "action_idempotency_key": action["idempotency_key"],
                "route_id": route.route_id,
                "binding_id": self.binding_id,
            }
        )[:48]
        if message["idempotency_key"] != expected_key:
            _fail("LINEAGE_MESSAGE_IDEMPOTENCY_MISMATCH", action_key)

    def semantic_values(self, action: Mapping[str, Any]) -> dict[str, Any]:
        result = _runtime_values(action["parameters"], "action.parameters")
        result["expiry_time"] = copy.deepcopy(action["expiry_time"])
        return result

    def _action(self, action_key: str) -> ActionContract:
        try:
            return self.actions[action_key]
        except KeyError as exc:
            _fail("LINEAGE_ACTION_UNKNOWN", action_key)
            raise AssertionError from exc

    def _carrier_fields(
        self,
        contract: ActionContract,
        values: Mapping[str, Any],
        carrier: str,
    ) -> list[dict[str, Any]]:
        return [
            runtime_field(
                item.name,
                copy.deepcopy(values[item.name]),
                source_kind="synthetic",
                source_ref_id=FIXTURE_SOURCE_REF,
                claim_ref_ids=("fixture.synthetic.conformance_only",),
                derivation_class="assumed",
                availability_at_t0="not_applicable",
                visibility="runtime_private",
                visibility_scope_ids=(contract.actor_id,),
                consumers=(contract.actor_id, "world.reducer"),
            )
            for item in sorted(contract.parameters, key=lambda entry: entry.name)
            if item.carrier == carrier
        ]

    def _action_idempotency_key(
        self,
        contract: ActionContract,
        semantic_parameters: Mapping[str, Any],
    ) -> str:
        return "idem.action." + sha256_value(
            {
                "binding_id": self.binding_id,
                "action_key": contract.action_key,
                "actor_id": contract.actor_id,
                "object_id": semantic_parameters[contract.object_id_parameter],
                "object_version": semantic_parameters[
                    contract.object_version_parameter
                ],
                "target_actor_ids": list(contract.target_actor_ids),
                "authority_ref_ids": list(contract.authority_ref_ids),
                "semantic_parameters": dict(semantic_parameters),
            }
        )[:48]


def _parse_parameter(value: Any, label: str) -> ParameterContract:
    item = _object(value, label)
    _exact_keys(item, {"name", "value_type", "carrier", "values"}, label)
    value_type = _string(item["value_type"], f"{label}.value_type")
    carrier = _string(item["carrier"], f"{label}.carrier")
    if value_type not in _PARAMETER_TYPES or carrier not in _CARRIERS:
        _fail("LINEAGE_PARAMETER_CONTRACT_INVALID", label)
    values = _unique_ids(item["values"], f"{label}.values", allow_empty=True)
    if (value_type == "enum") != bool(values):
        _fail("LINEAGE_PARAMETER_ENUM_DOMAIN_INVALID", label)
    if (carrier == "expiry_time") != (value_type == "nullable_time_interval"):
        _fail("LINEAGE_EXPIRY_CONTRACT_INVALID", label)
    return ParameterContract(
        name=_stable_id(item["name"], f"{label}.name"),
        value_type=value_type,
        carrier=carrier,
        values=values,
    )


def _parse_route(
    value: Any,
    label: str,
    *,
    actor_rows: Mapping[str, Mapping[str, Any]],
    opening_routes: Mapping[str, Mapping[str, Any]],
) -> RouteContract:
    item = _object(value, label)
    _exact_keys(
        item,
        {
            "route_id",
            "source_opening_route_id",
            "source_actor_id",
            "target_actor_id",
            "required_source_capacity_id",
            "channel_id",
            "performative",
            "confidentiality",
            "latency_ticks",
        },
        label,
    )
    source_id = _stable_id(item["source_actor_id"], f"{label}.source_actor_id")
    target_id = _stable_id(item["target_actor_id"], f"{label}.target_actor_id")
    source_route_id = _stable_id(
        item["source_opening_route_id"], f"{label}.source_opening_route_id"
    )
    if source_id not in actor_rows or target_id not in actor_rows:
        _fail("LINEAGE_ROUTE_ACTOR_OUTSIDE_SCOPE", label)
    try:
        opening = opening_routes[source_route_id]
    except KeyError as exc:
        _fail("LINEAGE_SOURCE_ROUTE_UNKNOWN", source_route_id)
        raise AssertionError from exc
    endpoints = opening["endpoints"]
    valid_pair = (
        source_id in endpoints["side_a"] and target_id in endpoints["side_b"]
    ) or (
        source_id in endpoints["side_b"] and target_id in endpoints["side_a"]
    )
    if (
        opening["directionality"] != "bidirectional_explicit_address_only"
        or opening["addressing_rule"]
        != "one_exact_sender_and_one_exact_recipient_per_message_no_set_broadcast"
        or not valid_pair
    ):
        _fail("LINEAGE_SOURCE_ROUTE_ENDPOINT_MISMATCH", source_route_id)
    capacity_id = _stable_id(
        item["required_source_capacity_id"],
        f"{label}.required_source_capacity_id",
    )
    if capacity_id != actor_rows[source_id]["selected_capacity_id"]:
        _fail("LINEAGE_ROUTE_CAPACITY_MISMATCH", label)
    confidentiality = _string(item["confidentiality"], f"{label}.confidentiality")
    if confidentiality not in {"public", "private", "restricted"}:
        _fail("LINEAGE_ROUTE_CONFIDENTIALITY_INVALID", label)
    return RouteContract(
        route_id=_stable_id(item["route_id"], f"{label}.route_id"),
        source_opening_route_id=source_route_id,
        source_actor_id=source_id,
        target_actor_id=target_id,
        required_source_capacity_id=capacity_id,
        channel_id=_stable_id(item["channel_id"], f"{label}.channel_id"),
        performative=_stable_id(item["performative"], f"{label}.performative"),
        confidentiality=confidentiality,
        latency_ticks=_integer(item["latency_ticks"], f"{label}.latency_ticks", minimum=1),
    )


def _expected_actor_rows(
    admission: ScenarioConfigurationAdmission,
    profile: DerivedRosterProfile,
) -> Mapping[str, Mapping[str, Any]]:
    named_by_id = {row["actor_id"]: row for row in admission.document["named_actors"]}
    populations = {
        row["actor_id"]: row for row in admission.document["population_actors"]
    }
    units = {row["actor_id"]: row for row in admission.document["population_units"]}
    expected: dict[str, Mapping[str, Any]] = {}
    for actor_id in _EXPECTED_ACTOR_IDS[:2]:
        actor = populations[actor_id]
        unit = units[actor_id]
        product = profile.products[unit["population_product_id"]]
        expected[actor_id] = {
            "actor_id": actor_id,
            "entity_id": actor["entity_id"],
            "assembly_kind": "responsibility_unit",
            "unit_id": actor["unit_id"],
            "participant_product_id": product.product_id,
            "capability_id": actor["capability_id"],
            "selected_capacity_id": actor["capacity_id"],
            "host_institution_id": actor["host_institution_id"],
            "assignment_id": actor["assignment_id"],
            "authority_record_id": actor["assignment_id"],
            "authority_graph_id": actor["authority_graph_id"],
            "resource_owner_id": actor["resource_owner_id"],
            "access_scope_ids": list(unit["access_scope_ids"]),
            "definition_sha256": product.content_sha256,
            "representation_class": product.representation_class,
        }
    actor_id = _EXPECTED_ACTOR_IDS[2]
    actor = named_by_id[actor_id]
    product = profile.products[actor["participant_product_id"]]
    expected[actor_id] = {
        "actor_id": actor_id,
        "entity_id": actor["entity_id"],
        "assembly_kind": "office",
        "unit_id": None,
        "participant_product_id": product.product_id,
        "capability_id": actor["capability_id"],
        "selected_capacity_id": "capacity.0616.ihis.gcio-service-lead",
        "host_institution_id": actor["primary_institution_id"],
        "assignment_id": None,
        "authority_record_id": "opening.0616.authority.singhealth-gcio",
        "authority_graph_id": actor["authority_graph_id"],
        "resource_owner_id": actor["resource_owner_id"],
        "access_scope_ids": [],
        "definition_sha256": product.content_sha256,
        "representation_class": product.representation_class,
    }
    if expected[actor_id]["selected_capacity_id"] not in actor["capacity_ids"]:
        _fail("LINEAGE_GCIO_IHIS_CAPACITY_MISSING")
    return MappingProxyType(expected)


def _parse_binding(
    document: Mapping[str, Any],
    *,
    admission: ScenarioConfigurationAdmission,
    profile: DerivedRosterProfile,
    receipt: Mapping[str, Any],
    release_id: str,
    release_manifest_sha256: str,
    binding_sha256: str,
    implementation_sha256s: Mapping[str, str],
) -> LineageBinding:
    _exact_keys(
        document,
        {
            "schema",
            "binding_id",
            "version",
            "status",
            "event_id",
            "configuration",
            "scope",
            "derived_inventory",
            "actors",
            "relationship_refs",
            "policy_bindings",
            "routes",
            "observation_contracts",
            "actions",
            "decision_bindings",
        },
        "binding",
    )
    if (
        document["schema"] != BINDING_FORMAT
        or document["binding_id"] != BINDING_ID
        or document["event_id"] != EVENT_ID
        or document["status"] != "bounded_conformance_binding"
    ):
        _fail("LINEAGE_BINDING_IDENTITY_MISMATCH")
    version = _string(document["version"], "binding.version")

    config = _object(document["configuration"], "binding.configuration")
    _exact_keys(
        config,
        {
            "configuration_id",
            "source_sha256",
            "canonical_sha256",
            "admission_receipt_sha256",
            "mapping_profile_id",
            "mapping_profile_sha256",
        },
        "binding.configuration",
    )
    expected_config = {
        "configuration_id": admission.configuration_id,
        "source_sha256": admission.source_sha256,
        "canonical_sha256": admission.canonical_sha256,
        "admission_receipt_sha256": receipt["receipt_sha256"],
        "mapping_profile_id": admission.mapping_profile_id,
        "mapping_profile_sha256": admission.mapping_profile_sha256,
    }
    if dict(config) != expected_config:
        _fail("LINEAGE_CONFIGURATION_BINDING_MISMATCH")

    scope = _object(document["scope"], "binding.scope")
    _exact_keys(
        scope,
        {
            "lineage_id",
            "purpose",
            "actor_ids",
            "capability_ids",
            "source_route_ids",
            "bound_policy_ids",
            "unbound_policy_ids",
            "excluded_actor_count",
            "excluded_intent_count",
            "logical_tick_start",
            "logical_tick_end",
            "full_configuration_execution_enabled",
            "simulation_enabled",
            "historical_validity_claim",
            "scientific_validity_claim",
            "positive_fixture_exposure",
        },
        "binding.scope",
    )
    if (
        scope["lineage_id"] != admission.document["bounded_lineage"]["id"]
        or scope["purpose"] != "exact_carrier_and_positive_binding_conformance"
    ):
        _fail("LINEAGE_PURPOSE_MISMATCH")
    actor_ids = _unique_ids(scope["actor_ids"], "scope.actor_ids")
    capability_ids = _unique_ids(scope["capability_ids"], "scope.capability_ids")
    source_route_ids = _unique_ids(
        scope["source_route_ids"], "scope.source_route_ids", sorted_required=True
    )
    bound_policy_ids = _unique_ids(
        scope["bound_policy_ids"], "scope.bound_policy_ids", sorted_required=True
    )
    unbound_policy_ids = _unique_ids(
        scope["unbound_policy_ids"], "scope.unbound_policy_ids", sorted_required=True
    )
    if (
        actor_ids != _EXPECTED_ACTOR_IDS
        or capability_ids != _EXPECTED_CAPABILITY_IDS
        or source_route_ids != _EXPECTED_SOURCE_ROUTE_IDS
        or set(bound_policy_ids) != set(_EXPECTED_POLICY_IMPLEMENTATIONS)
        or unbound_policy_ids != _EXPECTED_UNBOUND_POLICIES
        or set(bound_policy_ids).intersection(unbound_policy_ids)
        or set(bound_policy_ids).union(unbound_policy_ids)
        != set(admission.unbound_policy_ids)
        or _integer(scope["excluded_actor_count"], "scope.excluded_actor_count")
        != 10
        or _integer(scope["excluded_intent_count"], "scope.excluded_intent_count")
        != 50
        or _integer(scope["logical_tick_start"], "scope.logical_tick_start") != 0
        or _integer(scope["logical_tick_end"], "scope.logical_tick_end") != 8
    ):
        _fail("LINEAGE_SCOPE_MISMATCH")
    configured_lineage = admission.document["bounded_lineage"]
    if (
        tuple(configured_lineage["participant_ids"]) != actor_ids
        or set(configured_lineage["route_ids"]) != set(source_route_ids)
    ):
        _fail("LINEAGE_CONFIGURATION_SCOPE_MISMATCH")
    for name in (
        "full_configuration_execution_enabled",
        "simulation_enabled",
        "historical_validity_claim",
        "scientific_validity_claim",
    ):
        if _boolean(scope[name], f"scope.{name}"):
            _fail("LINEAGE_SCOPE_ESCALATION_FORBIDDEN", name)
    if scope["positive_fixture_exposure"] != "full_outcome_exposed_synthetic_conformance_only":
        _fail("LINEAGE_EXPOSURE_LABEL_MISMATCH")

    inventory = _object(document["derived_inventory"], "binding.derived_inventory")
    _exact_keys(
        inventory,
        {
            "semantic_products",
            "decision_and_population_commitments",
            "observation_placements",
            "private_state_placements",
            "intent_placements",
            "selected_observation_placements",
            "selected_private_state_placements",
            "selected_decision_placements",
            "selected_intent_placements",
        },
        "binding.derived_inventory",
    )
    selected_products = [profile.capabilities[item] for item in capability_ids]
    expected_inventory = {
        **dict(profile.coverage),
        "selected_observation_placements": sum(
            len(item.observation_ids) for item in selected_products
        ),
        "selected_private_state_placements": sum(
            len(item.private_state_ids) for item in selected_products
        ),
        "selected_decision_placements": sum(
            len(item.decision_ids) for item in selected_products
        ),
        "selected_intent_placements": sum(
            len(item.intent_ids) for item in selected_products
        ),
    }
    if dict(inventory) != expected_inventory:
        _fail("LINEAGE_DERIVED_INVENTORY_MISMATCH")

    expected_actors = _expected_actor_rows(admission, profile)
    actor_rows: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(_array(document["actors"], "binding.actors")):
        label = f"binding.actors.{index}"
        row = dict(_object(raw, label))
        actor_id = _stable_id(row.get("actor_id"), f"{label}.actor_id")
        if actor_id in actor_rows or row != expected_actors.get(actor_id):
            _fail("LINEAGE_ACTOR_BINDING_MISMATCH", actor_id)
        actor_rows[actor_id] = _freeze(row)
    if tuple(actor_rows) != actor_ids:
        _fail("LINEAGE_ACTOR_SCOPE_MISMATCH")

    records = {
        row["id"]: row for row in admission.document["initial_records"]
    }
    relationship_refs = _unique_ids(
        document["relationship_refs"],
        "binding.relationship_refs",
        sorted_required=True,
    )
    if relationship_refs != ("opening.0616.relationship.ihis-singhealth-scm",):
        _fail("LINEAGE_RELATIONSHIP_REF_MISMATCH")
    if any(ref not in records for ref in relationship_refs):
        _fail("LINEAGE_RELATIONSHIP_REF_MISSING")

    policy_selections = {
        row["policy_id"]: row for row in admission.document["policy_selections"]
    }
    policies: dict[str, PolicyBinding] = {}
    for index, raw in enumerate(
        _array(document["policy_bindings"], "binding.policy_bindings")
    ):
        label = f"binding.policy_bindings.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {
                "policy_id",
                "semantic_version",
                "selection",
                "implementation_id",
                "status",
            },
            label,
        )
        policy_id = _stable_id(row["policy_id"], f"{label}.policy_id")
        selected = policy_selections.get(policy_id)
        if (
            policy_id in policies
            or policy_id not in bound_policy_ids
            or selected is None
            or row["semantic_version"] != selected["semantic_version"]
            or row["selection"] != selected["selection"]
            or row["implementation_id"]
            != _EXPECTED_POLICY_IMPLEMENTATIONS[policy_id]
            or row["status"] != "bound_for_bounded_lineage_only"
        ):
            _fail("LINEAGE_POLICY_BINDING_MISMATCH", policy_id)
        policies[policy_id] = PolicyBinding(
            policy_id=policy_id,
            semantic_version=row["semantic_version"],
            selection=row["selection"],
            implementation_id=row["implementation_id"],
            status=row["status"],
        )
    if set(policies) != set(bound_policy_ids):
        _fail("LINEAGE_POLICY_BINDING_INCOMPLETE")

    opening_routes = {
        row["id"]: row
        for row in admission.document["initial_records"]
        if row["family"] == "institutional_route"
    }
    routes: dict[str, RouteContract] = {}
    for index, raw in enumerate(_array(document["routes"], "binding.routes")):
        route = _parse_route(
            raw,
            f"binding.routes.{index}",
            actor_rows=actor_rows,
            opening_routes=opening_routes,
        )
        if route.route_id in routes:
            _fail("LINEAGE_ROUTE_DUPLICATE", route.route_id)
        routes[route.route_id] = route
    if {route.source_opening_route_id for route in routes.values()} != set(
        source_route_ids
    ):
        _fail("LINEAGE_SOURCE_ROUTE_SCOPE_MISMATCH")

    observations: dict[tuple[str, str], ObservationContract] = {}
    for index, raw in enumerate(
        _array(document["observation_contracts"], "binding.observation_contracts")
    ):
        label = f"binding.observation_contracts.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {
                "actor_id",
                "capability_id",
                "reader_observation_id",
                "value_type",
                "values",
            },
            label,
        )
        actor_id = _stable_id(row["actor_id"], f"{label}.actor_id")
        capability_id = _stable_id(row["capability_id"], f"{label}.capability_id")
        reader_id = _stable_id(
            row["reader_observation_id"], f"{label}.reader_observation_id"
        )
        key = (actor_id, reader_id)
        if (
            key in observations
            or actor_id not in actor_rows
            or actor_rows[actor_id]["capability_id"] != capability_id
        ):
            _fail("LINEAGE_OBSERVATION_CONTRACT_INVALID", label)
        field_name = profile.observation_field(capability_id, reader_id)
        value_type = _string(row["value_type"], f"{label}.value_type")
        if value_type not in {"enum", "stable_id", "stable_id_array"}:
            _fail("LINEAGE_OBSERVATION_TYPE_INVALID", label)
        values = _unique_ids(row["values"], f"{label}.values", allow_empty=True)
        if (value_type == "enum") != bool(values):
            _fail("LINEAGE_OBSERVATION_ENUM_DOMAIN_INVALID", label)
        observations[key] = ObservationContract(
            actor_id=actor_id,
            capability_id=capability_id,
            reader_observation_id=reader_id,
            field_name=field_name,
            value_type=value_type,
            values=values,
        )
    expected_observation_keys = {
        (actor_id, reader_id)
        for actor_id, row in actor_rows.items()
        for reader_id in profile.capabilities[row["capability_id"]].observation_ids
    }
    if set(observations) != expected_observation_keys:
        _fail("LINEAGE_OBSERVATION_SCOPE_MISMATCH")

    actions: dict[str, ActionContract] = {}
    for index, raw in enumerate(_array(document["actions"], "binding.actions")):
        label = f"binding.actions.{index}"
        item = _object(raw, label)
        _exact_keys(
            item,
            {
                "action_key",
                "actor_id",
                "capability_id",
                "reader_intent_id",
                "action_type",
                "action_schema_version",
                "commitment_ids",
                "observation_ids",
                "authority_ref_ids",
                "target_actor_ids",
                "lifecycle_family",
                "adjudication_family",
                "object_id_parameter",
                "object_version_parameter",
                "parameters",
                "message_route_id",
                "forbidden_self_results",
            },
            label,
        )
        action_key = _stable_id(item["action_key"], f"{label}.action_key")
        actor_id = _stable_id(item["actor_id"], f"{label}.actor_id")
        capability_id = _stable_id(item["capability_id"], f"{label}.capability_id")
        reader_intent_id = _stable_id(
            item["reader_intent_id"], f"{label}.reader_intent_id"
        )
        if (
            action_key in actions
            or actor_id not in actor_rows
            or actor_rows[actor_id]["capability_id"] != capability_id
        ):
            _fail("LINEAGE_ACTION_ACTOR_INVALID", label)
        placement = profile.intent(capability_id, reader_intent_id)
        if (
            item["action_type"] != placement.action_type
            or item["action_schema_version"] != placement.action_schema_version
        ):
            _fail("LINEAGE_ACTION_MAPPING_MISMATCH", label)
        commitments = _unique_ids(item["commitment_ids"], f"{label}.commitment_ids")
        if not set(commitments).issubset(
            profile.capabilities[capability_id].commitment_ids
        ):
            _fail("LINEAGE_ACTION_COMMITMENT_MISMATCH", label)
        observation_ids = _unique_ids(
            item["observation_ids"], f"{label}.observation_ids"
        )
        if any((actor_id, obs_id) not in observations for obs_id in observation_ids):
            _fail("LINEAGE_ACTION_OBSERVATION_MISMATCH", label)
        authority_refs = _unique_ids(
            item["authority_ref_ids"], f"{label}.authority_ref_ids"
        )
        if authority_refs != (actor_rows[actor_id]["authority_record_id"],):
            _fail("LINEAGE_ACTION_AUTHORITY_MISMATCH", label)
        targets = _unique_ids(item["target_actor_ids"], f"{label}.target_actor_ids")
        if any(target not in actor_rows for target in targets):
            _fail("LINEAGE_ACTION_TARGET_OUTSIDE_SCOPE", label)
        route_id = _stable_id(item["message_route_id"], f"{label}.message_route_id")
        if route_id not in routes:
            _fail("LINEAGE_MESSAGE_ROUTE_UNKNOWN", label)
        route = routes[route_id]
        if route.source_actor_id != actor_id or targets != (route.target_actor_id,):
            _fail("LINEAGE_MESSAGE_ROUTE_TARGET_MISMATCH", label)
        parameters = tuple(
            _parse_parameter(raw_parameter, f"{label}.parameters.{parameter_index}")
            for parameter_index, raw_parameter in enumerate(
                _array(item["parameters"], f"{label}.parameters")
            )
        )
        names = tuple(parameter.name for parameter in parameters)
        if len(names) != len(set(names)) or sum(
            parameter.carrier == "expiry_time" for parameter in parameters
        ) != 1:
            _fail("LINEAGE_PARAMETER_CONTRACT_INVALID", label)
        object_id_parameter = _stable_id(
            item["object_id_parameter"], f"{label}.object_id_parameter"
        )
        object_version_parameter = _stable_id(
            item["object_version_parameter"], f"{label}.object_version_parameter"
        )
        by_name = {parameter.name: parameter for parameter in parameters}
        if (
            object_id_parameter not in by_name
            or by_name[object_id_parameter].value_type != "stable_id"
            or object_version_parameter not in by_name
            or by_name[object_version_parameter].value_type != "integer"
        ):
            _fail("LINEAGE_OBJECT_IDENTITY_CONTRACT_INVALID", label)
        forbidden = _unique_ids(
            item["forbidden_self_results"], f"{label}.forbidden_self_results"
        )
        if set(forbidden).intersection(names):
            _fail("LINEAGE_RESULT_CONFLATION", label)
        actions[action_key] = ActionContract(
            action_key=action_key,
            actor_id=actor_id,
            capability_id=capability_id,
            reader_intent_id=reader_intent_id,
            action_type=placement.action_type,
            action_schema_version=placement.action_schema_version,
            commitment_ids=commitments,
            observation_ids=observation_ids,
            authority_ref_ids=authority_refs,
            target_actor_ids=targets,
            lifecycle_family=_stable_id(
                item["lifecycle_family"], f"{label}.lifecycle_family"
            ),
            adjudication_family=_stable_id(
                item["adjudication_family"], f"{label}.adjudication_family"
            ),
            object_id_parameter=object_id_parameter,
            object_version_parameter=object_version_parameter,
            parameters=parameters,
            message_route_id=route_id,
            forbidden_self_results=forbidden,
        )
    if tuple(actions) != _EXPECTED_ACTION_KEYS:
        _fail("LINEAGE_ACTION_SCOPE_MISMATCH")
    if tuple(
        f"{action.capability_id}.{action.reader_intent_id}"
        for action in actions.values()
    ) != tuple(configured_lineage["semantic_intent_sequence"]):
        _fail("LINEAGE_CONFIGURATION_INTENT_SEQUENCE_MISMATCH")

    decisions: list[Mapping[str, Any]] = []
    decision_actors: set[str] = set()
    covered_actions: set[str] = set()
    for index, raw in enumerate(
        _array(document["decision_bindings"], "binding.decision_bindings")
    ):
        label = f"binding.decision_bindings.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {"decision_policy_id", "actor_id", "action_keys", "status"},
            label,
        )
        actor_id = _stable_id(row["actor_id"], f"{label}.actor_id")
        action_keys = _unique_ids(row["action_keys"], f"{label}.action_keys")
        if (
            actor_id in decision_actors
            or actor_id not in actor_rows
            or row["status"] != "positive_branch_only"
            or any(
                action_key not in actions
                or actions[action_key].actor_id != actor_id
                for action_key in action_keys
            )
        ):
            _fail("LINEAGE_DECISION_BINDING_INVALID", label)
        _stable_id(row["decision_policy_id"], f"{label}.decision_policy_id")
        decision_actors.add(actor_id)
        covered_actions.update(action_keys)
        decisions.append(_freeze(dict(row)))
    if decision_actors != set(actor_ids) or covered_actions != set(actions):
        _fail("LINEAGE_DECISION_BINDING_INCOMPLETE")

    return LineageBinding(
        release_id=release_id,
        release_manifest_sha256=release_manifest_sha256,
        binding_id=BINDING_ID,
        binding_sha256=binding_sha256,
        implementation_sha256s=MappingProxyType(dict(implementation_sha256s)),
        version=version,
        configuration=admission,
        roster_profile=profile,
        admission_receipt_sha256=receipt["receipt_sha256"],
        actor_ids=actor_ids,
        capability_ids=capability_ids,
        actors=MappingProxyType(actor_rows),
        relationship_refs=relationship_refs,
        source_route_ids=source_route_ids,
        policy_bindings=MappingProxyType(policies),
        unbound_policy_ids=unbound_policy_ids,
        routes=MappingProxyType(routes),
        observations=MappingProxyType(observations),
        actions=MappingProxyType(actions),
        decision_bindings=tuple(decisions),
        document=_freeze(copy.deepcopy(dict(document))),
    )


def _validate_receipt(
    path: Path,
    *,
    expected_file_sha256: str,
    expected_receipt_sha256: str,
) -> Mapping[str, Any]:
    if _sha256_file(path) != expected_file_sha256:
        _fail("LINEAGE_ADMISSION_RECEIPT_FILE_HASH_MISMATCH")
    receipt = _read_json(path, "admission_receipt")
    if receipt.get("receipt_sha256") != expected_receipt_sha256:
        _fail("LINEAGE_ADMISSION_RECEIPT_IDENTITY_MISMATCH")
    preimage = copy.deepcopy(receipt)
    preimage.pop("receipt_sha256", None)
    if sha256_value(preimage) != expected_receipt_sha256:
        _fail("LINEAGE_ADMISSION_RECEIPT_SELF_HASH_MISMATCH")
    if receipt.get("verdict") != "PASS_BOUNDED_CONFIGURATION_ADMISSION":
        _fail("LINEAGE_ADMISSION_RECEIPT_NOT_PASSING")
    return receipt


def load_lineage_binding(
    manifest_path: str | Path,
    *,
    expected_manifest_sha256: str,
    project_root: str | Path | None = None,
) -> LineageBinding:
    """Load the exact binding only when its external manifest anchor matches."""

    expected_hash = _sha256(expected_manifest_sha256, "expected_manifest_sha256")
    supplied = Path(manifest_path)
    root = _find_project_root(supplied, project_root)
    path = supplied.resolve() if supplied.is_absolute() else (root / supplied).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        _fail("LINEAGE_MANIFEST_PATH_INVALID")
    raw_hash = _sha256_file(path)
    if raw_hash != expected_hash:
        _fail("LINEAGE_MANIFEST_HASH_MISMATCH")
    manifest = _read_json(path, "binding_manifest")
    _exact_keys(
        manifest,
        {
            "schema",
            "release_id",
            "version",
            "status",
            "event_id",
            "manifest_sha256",
            "binding",
            "selected_products",
            "implementation_surfaces",
            "upstream",
            "authorization",
        },
        "binding_manifest",
    )
    if (
        manifest["schema"] != RELEASE_FORMAT
        or manifest["event_id"] != EVENT_ID
        or manifest["status"] != "bounded_conformance_release"
    ):
        _fail("LINEAGE_MANIFEST_IDENTITY_MISMATCH")
    preimage = copy.deepcopy(manifest)
    self_hash = preimage.pop("manifest_sha256", None)
    if self_hash != sha256_value(preimage):
        _fail("LINEAGE_MANIFEST_SELF_HASH_MISMATCH")

    binding_ref = _object(manifest["binding"], "manifest.binding")
    _exact_keys(binding_ref, {"path", "sha256"}, "manifest.binding")
    binding_path = _inside(root, binding_ref["path"], "manifest.binding.path")
    binding_sha256 = _sha256(binding_ref["sha256"], "manifest.binding.sha256")
    if _sha256_file(binding_path) != binding_sha256:
        _fail("LINEAGE_BINDING_HASH_MISMATCH")

    implementation_sha256s: dict[str, str] = {}
    implementation_paths: dict[str, str] = {}
    for index, raw in enumerate(
        _array(manifest["implementation_surfaces"], "manifest.implementation_surfaces")
    ):
        label = f"manifest.implementation_surfaces.{index}"
        row = _object(raw, label)
        _exact_keys(row, {"kind", "path", "sha256"}, label)
        kind = _stable_id(row["kind"], f"{label}.kind")
        if kind in implementation_sha256s:
            _fail("LINEAGE_IMPLEMENTATION_SURFACE_DUPLICATE", kind)
        surface_path = _inside(root, row["path"], f"{label}.path")
        surface_hash = _sha256(row["sha256"], f"{label}.sha256")
        if _sha256_file(surface_path) != surface_hash:
            _fail("LINEAGE_IMPLEMENTATION_SURFACE_HASH_MISMATCH", kind)
        implementation_paths[kind] = surface_path.relative_to(root).as_posix()
        implementation_sha256s[kind] = surface_hash
    if implementation_paths != _EXPECTED_IMPLEMENTATION_PATHS:
        _fail("LINEAGE_IMPLEMENTATION_SURFACE_SCOPE_MISMATCH")

    upstream = _object(manifest["upstream"], "manifest.upstream")
    _exact_keys(
        upstream,
        {
            "configuration_path",
            "configuration_release_manifest_path",
            "configuration_source_sha256",
            "configuration_release_manifest_sha256",
            "configuration_canonical_sha256",
            "admission_receipt_path",
            "admission_receipt_file_sha256",
            "admission_receipt_sha256",
            "roster_release_manifest_path",
            "roster_release_manifest_sha256",
            "consolidated_mapping_manifest_path",
            "consolidated_mapping_manifest_sha256",
            "semantic_inventory_path",
            "semantic_inventory_sha256",
            "mapping_profile_path",
            "mapping_profile_sha256",
        },
        "manifest.upstream",
    )
    configuration_path = _inside(
        root, upstream["configuration_path"], "upstream.configuration_path"
    )
    configuration_manifest_path = _inside(
        root,
        upstream["configuration_release_manifest_path"],
        "upstream.configuration_release_manifest_path",
    )
    admission = load_scenario_configuration(
        configuration_path,
        expected_source_sha256=_sha256(
            upstream["configuration_source_sha256"],
            "upstream.configuration_source_sha256",
        ),
        expected_release_manifest_sha256=_sha256(
            upstream["configuration_release_manifest_sha256"],
            "upstream.configuration_release_manifest_sha256",
        ),
        project_root=root,
        release_manifest_path=configuration_manifest_path,
    )
    if admission.canonical_sha256 != upstream["configuration_canonical_sha256"]:
        _fail("LINEAGE_CONFIGURATION_CANONICAL_HASH_MISMATCH")
    receipt = _validate_receipt(
        _inside(root, upstream["admission_receipt_path"], "upstream.receipt_path"),
        expected_file_sha256=_sha256(
            upstream["admission_receipt_file_sha256"],
            "upstream.admission_receipt_file_sha256",
        ),
        expected_receipt_sha256=_sha256(
            upstream["admission_receipt_sha256"],
            "upstream.admission_receipt_sha256",
        ),
    )

    mapping_manifest_path = _inside(
        root,
        upstream["consolidated_mapping_manifest_path"],
        "upstream.consolidated_mapping_manifest_path",
    )
    if _sha256_file(mapping_manifest_path) != _sha256(
        upstream["consolidated_mapping_manifest_sha256"],
        "upstream.consolidated_mapping_manifest_sha256",
    ):
        _fail("LINEAGE_MAPPING_RELEASE_MANIFEST_HASH_MISMATCH")
    mapping_manifest = _read_json(mapping_manifest_path, "mapping_manifest")
    if (
        mapping_manifest.get("release_id")
        != "H2EPR-0616-CONSOLIDATED-MAPPING-v0.1"
        or mapping_manifest.get("event_id") != EVENT_ID
        or mapping_manifest.get("status") != "accepted_design_specification"
    ):
        _fail("LINEAGE_MAPPING_RELEASE_IDENTITY_MISMATCH")

    profile = _load_derived_profile(
        root,
        admission=admission,
        roster_manifest_path=_inside(
            root,
            upstream["roster_release_manifest_path"],
            "upstream.roster_release_manifest_path",
        ),
        roster_manifest_sha256=_sha256(
            upstream["roster_release_manifest_sha256"],
            "upstream.roster_release_manifest_sha256",
        ),
        semantic_inventory_path=_inside(
            root,
            upstream["semantic_inventory_path"],
            "upstream.semantic_inventory_path",
        ),
        semantic_inventory_sha256=_sha256(
            upstream["semantic_inventory_sha256"],
            "upstream.semantic_inventory_sha256",
        ),
        mapping_profile_path=_inside(
            root,
            upstream["mapping_profile_path"],
            "upstream.mapping_profile_path",
        ),
        mapping_profile_sha256=_sha256(
            upstream["mapping_profile_sha256"],
            "upstream.mapping_profile_sha256",
        ),
    )
    if (
        profile.mapping_profile_sha256 != admission.mapping_profile_sha256
        or profile.release_manifest_sha256
        != admission.semantic_input_sha256s["roster_definition_release"]
    ):
        _fail("LINEAGE_PROFILE_CONFIGURATION_IDENTITY_MISMATCH")

    selected_products: list[dict[str, str]] = []
    for index, raw in enumerate(
        _array(manifest["selected_products"], "manifest.selected_products")
    ):
        label = f"manifest.selected_products.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {"product_id", "capability_id", "path", "sha256"},
            label,
        )
        product_path = _inside(root, row["path"], f"{label}.path")
        content_sha256 = _sha256(row["sha256"], f"{label}.sha256")
        if _sha256_file(product_path) != content_sha256:
            _fail("LINEAGE_SELECTED_PRODUCT_HASH_MISMATCH", str(index))
        selected_products.append(dict(row))
    expected_selected_products = [
        {
            "product_id": profile.capabilities[capability_id].product_id,
            "capability_id": capability_id,
            "path": profile.capabilities[capability_id].project_relative_path,
            "sha256": profile.capabilities[capability_id].content_sha256,
        }
        for capability_id in _EXPECTED_CAPABILITY_IDS
    ]
    if selected_products != expected_selected_products:
        _fail("LINEAGE_SELECTED_PRODUCT_SCOPE_MISMATCH")

    authorization = _object(manifest["authorization"], "manifest.authorization")
    _exact_keys(
        authorization,
        {
            "owner_decisions",
            "bounded_projection_authorized",
            "bounded_policy_binding_authorized",
            "full_roster_runtime_authorized",
            "simulation_authorized",
            "evaluation_authorized",
            "historical_validity_claim_authorized",
        },
        "manifest.authorization",
    )
    if _unique_ids(
        authorization["owner_decisions"], "authorization.owner_decisions"
    ) != ("OD-BND-01", "OD-BND-02", "OD-BND-03", "OD-BND-04"):
        _fail("LINEAGE_OWNER_AUTHORIZATION_MISMATCH")
    if (
        _boolean(
            authorization["bounded_projection_authorized"],
            "authorization.bounded_projection_authorized",
        )
        is not True
        or _boolean(
            authorization["bounded_policy_binding_authorized"],
            "authorization.bounded_policy_binding_authorized",
        )
        is not True
    ):
        _fail("LINEAGE_BOUND_AUTHORIZATION_MISSING")
    for key in (
        "full_roster_runtime_authorized",
        "simulation_authorized",
        "evaluation_authorized",
        "historical_validity_claim_authorized",
    ):
        if _boolean(authorization[key], f"authorization.{key}"):
            _fail("LINEAGE_AUTHORIZATION_SCOPE_ESCALATION", key)

    return _parse_binding(
        _read_json(binding_path, "binding"),
        admission=admission,
        profile=profile,
        receipt=receipt,
        release_id=_stable_id(manifest["release_id"], "manifest.release_id"),
        release_manifest_sha256=raw_hash,
        binding_sha256=binding_sha256,
        implementation_sha256s=implementation_sha256s,
    )


__all__ = [
    "BINDING_FORMAT",
    "BINDING_ID",
    "EVENT_ID",
    "FIXTURE_SOURCE_REF",
    "DerivedRosterProfile",
    "LineageBinding",
    "LineageBindingError",
    "PolicyBinding",
    "load_lineage_binding",
]
