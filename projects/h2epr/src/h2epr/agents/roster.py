"""Release-wide Agent mapping and conformance support.

The accepted Markdown products remain the semantic authorities.  This module
hash-checks their frozen release, derives capability-qualified observation and
intent identities, and validates a bounded scenario assembly.  It deliberately
contains no Agent policy, historical outcome, or reducer implementation.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence


ROSTER_MAPPING_SCHEMA_VERSION = "h2epr.roster-mapping-profile.v0_1"
ROSTER_FIXTURE_SCHEMA_VERSION = "h2epr.roster-conformance-fixture.v0_1"

_STABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SEMANTIC_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_COMMITMENT_HEADING = re.compile(
    r"^#### `(?P<commitment>(?:DC|PC)-[A-Z]+-[0-9]+)`", re.MULTILINE
)
_RESULT_BOUNDARY_HEADING = re.compile(
    r"^## .*result boundary\s*$", re.IGNORECASE | re.MULTILINE
)
_TABLE_SEPARATOR = re.compile(r"^:?-{3,}:?$")

_PRODUCT_KINDS = frozenset({"agent_definition", "population_model"})
_UNIT_SCOPES = frozenset(
    {"named_actor", "host_scoped_population", "institution_preserving_population"}
)
_REPRESENTATION_CLASSES = frozenset(
    {
        "aggregate_population_agent",
        "autonomous_participant_agent",
        "institutional_environment_agent",
    }
)
_VISIBILITIES = frozenset({"public", "restricted", "runtime_private"})
_AVAILABILITIES = frozenset({"delivered", "unknown", "unavailable"})
_TRIGGERS = frozenset({"action", "scenario"})


class RosterMappingError(ValueError):
    """The frozen release, derived mapping, or fixture is inconsistent."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise RosterMappingError(f"invalid_{name}")
    return value


def _stable_id(value: Any, name: str) -> str:
    result = _string(value, name)
    if _STABLE_ID.fullmatch(result) is None:
        raise RosterMappingError(f"invalid_{name}")
    return result


def _semantic_id(value: Any, name: str) -> str:
    result = _string(value, name)
    if _SEMANTIC_ID.fullmatch(result) is None:
        raise RosterMappingError(f"invalid_{name}")
    return result


def _sha256(value: Any, name: str) -> str:
    result = _string(value, name)
    if _SHA256.fullmatch(result) is None:
        raise RosterMappingError(f"invalid_{name}")
    return result


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RosterMappingError(f"invalid_{name}")
    return value


def _number(value: Any, name: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RosterMappingError(f"invalid_{name}")
    result = float(value)
    if minimum is not None and result < minimum:
        raise RosterMappingError(f"invalid_{name}")
    return result


def _boolean(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise RosterMappingError(f"invalid_{name}")
    return value


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise RosterMappingError(f"invalid_{name}")
    return value


def _sequence(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise RosterMappingError(f"invalid_{name}")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], name: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = ",".join(sorted(expected - actual))
        extra = ",".join(sorted(actual - expected))
        raise RosterMappingError(
            f"{name}_keys_mismatch:missing={missing}:extra={extra}"
        )


def _unique_strings(
    value: Any,
    name: str,
    *,
    allow_empty: bool = False,
    sorted_required: bool = True,
) -> tuple[str, ...]:
    items = _sequence(value, name)
    if not items and not allow_empty:
        raise RosterMappingError(f"invalid_{name}")
    result = tuple(_stable_id(item, name) for item in items)
    if len(result) != len(set(result)):
        raise RosterMappingError(f"duplicate_{name}")
    if sorted_required and result != tuple(sorted(result)):
        raise RosterMappingError(f"unsorted_{name}")
    return result


def _read_json(path: Path, name: str) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RosterMappingError(f"invalid_json:{name}") from exc
    if not isinstance(result, dict):
        raise RosterMappingError(f"json_object_required:{name}")
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
            and parent.joinpath("releases").is_dir()
        ]
        if not roots:
            raise RosterMappingError("h2epr_project_root_not_found")
        root = roots[0]
    return root


def _project_file(root: Path, value: Any, name: str) -> Path:
    relative = Path(_string(value, name))
    if relative.is_absolute() or ".." in relative.parts:
        raise RosterMappingError(f"unsafe_{name}")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise RosterMappingError(f"unsafe_{name}") from exc
    if not path.is_file():
        raise RosterMappingError(f"missing_{name}:{relative.as_posix()}")
    return path


def _anchored_file(root: Path, anchor: Path, value: Any, name: str) -> Path:
    relative = Path(_string(value, name))
    if relative.is_absolute() or ".." in relative.parts:
        raise RosterMappingError(f"unsafe_{name}")
    path = (anchor / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise RosterMappingError(f"unsafe_{name}") from exc
    if not path.is_file():
        raise RosterMappingError(f"missing_{name}:{relative.as_posix()}")
    return path


def _table_cells(line: str) -> tuple[str, ...]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return ()
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def _table_ids(
    lines: Sequence[str],
    header_index: int,
    name: str,
    *,
    embedded: bool = False,
) -> tuple[str, ...]:
    if header_index + 1 >= len(lines):
        raise RosterMappingError(f"{name}_table_truncated")
    separator = _table_cells(lines[header_index + 1])
    if not separator or any(
        _TABLE_SEPARATOR.fullmatch(cell) is None for cell in separator
    ):
        raise RosterMappingError(f"{name}_table_separator_invalid")
    result: list[str] = []
    for line in lines[header_index + 2 :]:
        cells = _table_cells(line)
        if not cells:
            break
        pattern = r"`([a-z][a-z0-9_]*)`"
        matches = re.findall(pattern, cells[0])
        if len(matches) != 1 or (not embedded and cells[0] != f"`{matches[0]}`"):
            raise RosterMappingError(f"{name}_table_id_invalid:{cells[0]}")
        result.append(matches[0])
    if not result or len(result) != len(set(result)):
        raise RosterMappingError(f"{name}_table_inventory_invalid")
    return tuple(result)


def _parse_observations(markdown: str) -> tuple[str, ...]:
    lines = markdown.splitlines()
    candidates = []
    for index, line in enumerate(lines):
        cells = _table_cells(line)
        if cells and cells[0].casefold() == "observation":
            candidates.append(index)
    if len(candidates) != 1:
        raise RosterMappingError(
            f"observation_table_cardinality:{len(candidates)}"
        )
    return _table_ids(lines, candidates[0], "observation")


def _parse_intents(markdown: str) -> tuple[str, ...]:
    lines = markdown.splitlines()
    headings = [
        index
        for index, line in enumerate(lines)
        if _RESULT_BOUNDARY_HEADING.fullmatch(line) is not None
    ]
    if len(headings) != 1:
        raise RosterMappingError(f"intent_boundary_cardinality:{len(headings)}")
    start = headings[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    table_headers = []
    for index in range(start, end):
        cells = _table_cells(lines[index])
        if cells and index + 1 < end and _table_cells(lines[index + 1]):
            separator = _table_cells(lines[index + 1])
            if separator and all(
                _TABLE_SEPARATOR.fullmatch(cell) is not None for cell in separator
            ):
                table_headers.append(index)
    if len(table_headers) != 1:
        raise RosterMappingError(f"intent_table_cardinality:{len(table_headers)}")
    return _table_ids(lines, table_headers[0], "intent", embedded=True)


def _parse_commitments(markdown: str) -> tuple[str, ...]:
    result = tuple(
        match.group("commitment") for match in _COMMITMENT_HEADING.finditer(markdown)
    )
    if not result or len(result) != len(set(result)):
        raise RosterMappingError("commitment_inventory_invalid")
    return result


@dataclass(frozen=True)
class ObservationPlacement:
    capability_id: str
    reader_observation_id: str
    source_product_id: str
    source_sha256: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.capability_id, self.reader_observation_id)

    @property
    def field_name(self) -> str:
        return f"obs.{self.capability_id}.{self.reader_observation_id}"


@dataclass(frozen=True)
class IntentPlacement:
    event_namespace: str
    capability_id: str
    reader_intent_id: str
    source_product_id: str
    source_sha256: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.capability_id, self.reader_intent_id)

    @property
    def action_type(self) -> str:
        return (
            f"h2epr.action.{self.event_namespace}."
            f"{self.capability_id}.{self.reader_intent_id}"
        )

    @property
    def action_schema_version(self) -> str:
        return (
            f"h2epr.intent.{self.event_namespace}.{self.capability_id}."
            f"{self.reader_intent_id}.v0_1"
        )


@dataclass(frozen=True)
class SemanticProduct:
    product_id: str
    product_kind: str
    event_namespace: str
    capability_id: str
    version: str
    path: str
    content_sha256: str
    runtime_disposition: str
    representation_classes: tuple[str, ...]
    unit_scope: str
    commitment_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]

    @property
    def machine_commitment_ids(self) -> tuple[str, ...]:
        return tuple(
            f"h2epr.commitment.{self.event_namespace}.{self.capability_id}.{item}"
            for item in self.commitment_ids
        )


@dataclass(frozen=True)
class ActorAssembly:
    actor_id: str
    entity_id: str
    participant_artifact_id: str
    representation_class: str
    authority_graph_id: str
    resource_owner_id: str
    relationship_state_id: str
    capability_ids: tuple[str, ...]
    observation_field_names: tuple[str, ...]
    action_types: tuple[str, ...]


@dataclass(frozen=True)
class PopulationUnit:
    unit_id: str
    actor_id: str
    capability_id: str
    institution_entity_id: str
    host_entity_id: str | None
    weight: float
    private_state_owner_id: str
    resource_owner_id: str


@dataclass(frozen=True)
class AuthorityRecord:
    authority_ref: str
    actor_id: str
    capability_id: str
    reader_intent_id: str
    target_actor_ids: tuple[str, ...]
    resource_owner_id: str | None
    record_version: int
    state: str


@dataclass(frozen=True)
class ObservationCase:
    case_id: str
    actor_id: str
    capability_id: str
    reader_observation_id: str
    field_name: str
    host_entity_id: str | None
    availability: str
    visibility: str
    visibility_scope_ids: tuple[str, ...]
    authoritative_record_ref: str | None
    record_version: int
    as_of: str
    decision_time: str
    freshness: str


@dataclass(frozen=True)
class LifecycleEvent:
    event_id: str
    trigger: str
    actor_id: str | None
    capability_id: str | None
    reader_intent_id: str | None
    action_type: str | None
    action_intent_id: str | None
    action_disposition_id: str | None
    idempotency_key: str | None
    target_actor_ids: tuple[str, ...]
    authority_refs: tuple[str, ...]
    resource_owner_id: str | None
    before_state: str
    after_state: str
    before_version: int
    after_version: int
    business_result_id: str
    delivered_observation_id: str | None
    material_parameters: Mapping[str, Any]


@dataclass(frozen=True)
class LifecycleReplay:
    family_id: str
    object_id: str
    owner_actor_id: str
    initial_state: str
    initial_version: int
    final_state: str
    final_version: int
    events: tuple[LifecycleEvent, ...]


@dataclass(frozen=True)
class ConformanceFixture:
    fixture_id: str
    historical_validity_claim: bool
    structural_variants: Mapping[str, str]
    actors: Mapping[str, ActorAssembly]
    population_units: Mapping[str, PopulationUnit]
    authority_records: Mapping[str, AuthorityRecord]
    observation_cases: Mapping[str, ObservationCase]
    funding_lifecycle: LifecycleReplay
    identity_sha256: str


@dataclass(frozen=True)
class RosterMappingProfile:
    profile_id: str
    version: str
    status: str
    event_id: str
    event_namespace: str
    source_release_id: str
    source_release_manifest_sha256: str
    accepted_mapping_id: str
    accepted_mapping_manifest_sha256: str
    profile_sha256: str
    products: Mapping[str, SemanticProduct]
    capabilities: Mapping[str, SemanticProduct]
    observations: Mapping[tuple[str, str], ObservationPlacement]
    intents: Mapping[tuple[str, str], IntentPlacement]
    fixture: ConformanceFixture

    @property
    def commitment_count(self) -> int:
        return sum(len(product.commitment_ids) for product in self.products.values())

    @property
    def observation_count(self) -> int:
        return len(self.observations)

    @property
    def intent_count(self) -> int:
        return len(self.intents)

    @property
    def distinct_reader_observation_count(self) -> int:
        return len({item.reader_observation_id for item in self.observations.values()})

    @property
    def distinct_reader_intent_count(self) -> int:
        return len({item.reader_intent_id for item in self.intents.values()})

    def actor(self, actor_id: str) -> ActorAssembly:
        try:
            return self.fixture.actors[actor_id]
        except KeyError as exc:
            raise RosterMappingError(f"unknown_actor:{actor_id}") from exc

    def intent(self, capability_id: str, reader_intent_id: str) -> IntentPlacement:
        try:
            return self.intents[(capability_id, reader_intent_id)]
        except KeyError as exc:
            raise RosterMappingError(
                f"unknown_intent:{capability_id}:{reader_intent_id}"
            ) from exc


def _manifest_products(
    manifest: Mapping[str, Any], root: Path
) -> Mapping[str, tuple[str, Mapping[str, Any], Path]]:
    products: dict[str, tuple[str, Mapping[str, Any], Path]] = {}
    for manifest_key, kind in (
        ("agent_definitions", "agent_definition"),
        ("population_models", "population_model"),
    ):
        for index, raw_item in enumerate(
            _sequence(manifest.get(manifest_key), manifest_key)
        ):
            item = _mapping(raw_item, f"{manifest_key}_{index}")
            _exact_keys(
                item,
                {"id", "version", "path", "sha256"},
                f"{manifest_key}_{index}",
            )
            product_id = _stable_id(item["id"], "source_product_id")
            if product_id in products:
                raise RosterMappingError(f"duplicate_source_product_id:{product_id}")
            path = _project_file(root, item["path"], "source_product_path")
            expected = _sha256(item["sha256"], "source_product_sha256")
            if _sha256_file(path) != expected:
                raise RosterMappingError(f"source_product_sha256_mismatch:{product_id}")
            products[product_id] = (kind, item, path)
    return MappingProxyType(products)


def _parse_capabilities(
    raw_capabilities: Any,
    manifest_products: Mapping[str, tuple[str, Mapping[str, Any], Path]],
    event_namespace: str,
) -> tuple[Mapping[str, SemanticProduct], Mapping[str, SemanticProduct]]:
    capabilities: dict[str, SemanticProduct] = {}
    products: dict[str, SemanticProduct] = {}
    rows = _sequence(raw_capabilities, "capabilities")
    source_ids: list[str] = []
    capability_order: list[str] = []
    for index, raw in enumerate(rows):
        row = _mapping(raw, f"capability_{index}")
        _exact_keys(
            row,
            {
                "capability_id",
                "expected_commitments",
                "expected_intents",
                "expected_observations",
                "product_kind",
                "representation_classes",
                "runtime_disposition",
                "source_product_id",
                "unit_scope",
            },
            f"capability_{index}",
        )
        capability_id = _semantic_id(row["capability_id"], "capability_id")
        product_id = _stable_id(row["source_product_id"], "source_product_id")
        product_kind = _string(row["product_kind"], "product_kind")
        if product_kind not in _PRODUCT_KINDS:
            raise RosterMappingError(f"unknown_product_kind:{product_kind}")
        unit_scope = _string(row["unit_scope"], "unit_scope")
        if unit_scope not in _UNIT_SCOPES:
            raise RosterMappingError(f"unknown_unit_scope:{unit_scope}")
        representation_classes = _unique_strings(
            row["representation_classes"], "representation_classes"
        )
        if not set(representation_classes) <= _REPRESENTATION_CLASSES:
            raise RosterMappingError(
                f"unknown_representation_class:{capability_id}"
            )
        if capability_id in capabilities:
            raise RosterMappingError(f"duplicate_capability_id:{capability_id}")
        if product_id in products:
            raise RosterMappingError(f"duplicate_capability_source:{product_id}")
        try:
            manifest_kind, manifest_item, path = manifest_products[product_id]
        except KeyError as exc:
            raise RosterMappingError(f"unreleased_source_product:{product_id}") from exc
        if manifest_kind != product_kind:
            raise RosterMappingError(f"product_kind_mismatch:{product_id}")
        markdown = path.read_text(encoding="utf-8")
        commitments = _parse_commitments(markdown)
        observations = _parse_observations(markdown)
        intents = _parse_intents(markdown)
        expected = (
            _integer(row["expected_commitments"], "expected_commitments"),
            _integer(row["expected_observations"], "expected_observations"),
            _integer(row["expected_intents"], "expected_intents"),
        )
        actual = (len(commitments), len(observations), len(intents))
        if actual != expected:
            raise RosterMappingError(
                f"capability_inventory_mismatch:{capability_id}:"
                f"expected={expected}:actual={actual}"
            )
        product = SemanticProduct(
            product_id=product_id,
            product_kind=product_kind,
            event_namespace=event_namespace,
            capability_id=capability_id,
            version=_stable_id(manifest_item["version"], "product_version"),
            path=_string(manifest_item["path"], "source_product_path"),
            content_sha256=_sha256(manifest_item["sha256"], "source_product_sha256"),
            runtime_disposition=_stable_id(
                row["runtime_disposition"], "runtime_disposition"
            ),
            representation_classes=representation_classes,
            unit_scope=unit_scope,
            commitment_ids=commitments,
            observation_ids=observations,
            intent_ids=intents,
        )
        for machine_commitment_id in product.machine_commitment_ids:
            _stable_id(machine_commitment_id, "machine_commitment_id")
        capabilities[capability_id] = product
        products[product_id] = product
        capability_order.append(capability_id)
        source_ids.append(product_id)
    if capability_order != sorted(capability_order):
        raise RosterMappingError("capabilities_not_canonical")
    if set(source_ids) != set(manifest_products):
        missing = ",".join(sorted(set(manifest_products) - set(source_ids)))
        extra = ",".join(sorted(set(source_ids) - set(manifest_products)))
        raise RosterMappingError(
            f"release_product_coverage_mismatch:missing={missing}:extra={extra}"
        )
    return MappingProxyType(products), MappingProxyType(capabilities)


def _derive_placements(
    capabilities: Mapping[str, SemanticProduct],
) -> tuple[
    Mapping[tuple[str, str], ObservationPlacement],
    Mapping[tuple[str, str], IntentPlacement],
]:
    observations: dict[tuple[str, str], ObservationPlacement] = {}
    intents: dict[tuple[str, str], IntentPlacement] = {}
    action_types: set[str] = set()
    field_names: set[str] = set()
    for capability_id, product in capabilities.items():
        for reader_id in product.observation_ids:
            item = ObservationPlacement(
                capability_id=capability_id,
                reader_observation_id=reader_id,
                source_product_id=product.product_id,
                source_sha256=product.content_sha256,
            )
            if item.key in observations or item.field_name in field_names:
                raise RosterMappingError(f"observation_identity_collision:{item.key}")
            _stable_id(item.field_name, "observation_field_name")
            observations[item.key] = item
            field_names.add(item.field_name)
        for reader_id in product.intent_ids:
            item = IntentPlacement(
                event_namespace=product.event_namespace,
                capability_id=capability_id,
                reader_intent_id=reader_id,
                source_product_id=product.product_id,
                source_sha256=product.content_sha256,
            )
            if item.key in intents or item.action_type in action_types:
                raise RosterMappingError(f"intent_identity_collision:{item.key}")
            _stable_id(item.action_type, "action_type")
            _stable_id(item.action_schema_version, "action_schema_version")
            intents[item.key] = item
            action_types.add(item.action_type)
    return MappingProxyType(observations), MappingProxyType(intents)


def _parse_actor(
    raw: Any,
    index: int,
    capabilities: Mapping[str, SemanticProduct],
) -> ActorAssembly:
    row = _mapping(raw, f"actor_{index}")
    _exact_keys(
        row,
        {
            "actor_id",
            "authority_graph_id",
            "capability_ids",
            "entity_id",
            "participant_artifact_id",
            "relationship_state_id",
            "representation_class",
            "resource_owner_id",
        },
        f"actor_{index}",
    )
    actor_id = _stable_id(row["actor_id"], "actor_id")
    representation = _string(row["representation_class"], "representation_class")
    if representation not in _REPRESENTATION_CLASSES:
        raise RosterMappingError(f"unknown_representation_class:{actor_id}")
    capability_ids = _unique_strings(row["capability_ids"], "actor_capability_ids")
    observation_fields: set[str] = set()
    action_types: set[str] = set()
    for capability_id in capability_ids:
        try:
            capability = capabilities[capability_id]
        except KeyError as exc:
            raise RosterMappingError(
                f"actor_capability_unresolved:{actor_id}:{capability_id}"
            ) from exc
        if representation not in capability.representation_classes:
            raise RosterMappingError(
                f"actor_representation_incompatible:{actor_id}:{capability_id}"
            )
        observation_fields.update(
            f"obs.{capability_id}.{item}" for item in capability.observation_ids
        )
        action_types.update(
            f"h2epr.action.{capability.event_namespace}.{capability_id}.{item}"
            for item in capability.intent_ids
        )
    return ActorAssembly(
        actor_id=actor_id,
        entity_id=_stable_id(row["entity_id"], "actor_entity_id"),
        participant_artifact_id=_stable_id(
            row["participant_artifact_id"], "participant_artifact_id"
        ),
        representation_class=representation,
        authority_graph_id=_stable_id(row["authority_graph_id"], "authority_graph_id"),
        resource_owner_id=_stable_id(row["resource_owner_id"], "resource_owner_id"),
        relationship_state_id=_stable_id(
            row["relationship_state_id"], "relationship_state_id"
        ),
        capability_ids=capability_ids,
        observation_field_names=tuple(sorted(observation_fields)),
        action_types=tuple(sorted(action_types)),
    )


def _parse_population_units(
    raw_units: Any,
    actors: Mapping[str, ActorAssembly],
    capabilities: Mapping[str, SemanticProduct],
) -> Mapping[str, PopulationUnit]:
    units: dict[str, PopulationUnit] = {}
    assignments: set[tuple[str, str]] = set()
    private_state_owners: set[str] = set()
    for index, raw in enumerate(_sequence(raw_units, "population_units")):
        row = _mapping(raw, f"population_unit_{index}")
        _exact_keys(
            row,
            {
                "actor_id",
                "capability_id",
                "host_entity_id",
                "institution_entity_id",
                "private_state_owner_id",
                "resource_owner_id",
                "unit_id",
                "weight",
            },
            f"population_unit_{index}",
        )
        unit_id = _stable_id(row["unit_id"], "unit_id")
        actor_id = _stable_id(row["actor_id"], "unit_actor_id")
        capability_id = _semantic_id(row["capability_id"], "unit_capability_id")
        try:
            actor = actors[actor_id]
            capability = capabilities[capability_id]
        except KeyError as exc:
            raise RosterMappingError(
                f"population_unit_reference_unresolved:{unit_id}"
            ) from exc
        if capability.product_kind != "population_model":
            raise RosterMappingError(f"population_unit_uses_named_definition:{unit_id}")
        if capability_id not in actor.capability_ids:
            raise RosterMappingError(f"population_capability_not_on_actor:{unit_id}")
        assignment = (actor_id, capability_id)
        if assignment in assignments:
            raise RosterMappingError(
                f"duplicate_population_capability_assignment:{actor_id}:{capability_id}"
            )
        assignments.add(assignment)
        institution_entity_id = _stable_id(
            row["institution_entity_id"], "institution_entity_id"
        )
        host_raw = row["host_entity_id"]
        host_entity_id = (
            None if host_raw is None else _stable_id(host_raw, "host_entity_id")
        )
        if capability.unit_scope == "host_scoped_population":
            if host_entity_id is None or host_entity_id not in {
                item.entity_id for item in actors.values()
            }:
                raise RosterMappingError(f"host_scope_unresolved:{unit_id}")
            if host_entity_id == institution_entity_id:
                raise RosterMappingError(f"host_scope_collapsed_into_unit:{unit_id}")
        elif capability.unit_scope == "institution_preserving_population":
            if host_entity_id is not None or institution_entity_id != actor.entity_id:
                raise RosterMappingError(
                    f"institution_preserving_scope_mismatch:{unit_id}"
                )
        else:
            raise RosterMappingError(f"named_capability_has_population_unit:{unit_id}")
        resource_owner = _stable_id(row["resource_owner_id"], "unit_resource_owner_id")
        if resource_owner != actor.resource_owner_id:
            raise RosterMappingError(f"population_resource_owner_mismatch:{unit_id}")
        private_owner = _stable_id(
            row["private_state_owner_id"], "private_state_owner_id"
        )
        if private_owner in private_state_owners:
            raise RosterMappingError(f"shared_population_private_state:{private_owner}")
        private_state_owners.add(private_owner)
        if unit_id in units:
            raise RosterMappingError(f"duplicate_unit_id:{unit_id}")
        units[unit_id] = PopulationUnit(
            unit_id=unit_id,
            actor_id=actor_id,
            capability_id=capability_id,
            institution_entity_id=institution_entity_id,
            host_entity_id=host_entity_id,
            weight=_number(row["weight"], "unit_weight", minimum=0.0000001),
            private_state_owner_id=private_owner,
            resource_owner_id=resource_owner,
        )
    expected_assignments = {
        (actor.actor_id, capability_id)
        for actor in actors.values()
        for capability_id in actor.capability_ids
        if capabilities[capability_id].product_kind == "population_model"
    }
    if assignments != expected_assignments:
        raise RosterMappingError("population_assignment_coverage_mismatch")
    return MappingProxyType(units)


def _parse_authority_records(
    raw_records: Any,
    actors: Mapping[str, ActorAssembly],
    intents: Mapping[tuple[str, str], IntentPlacement],
) -> Mapping[str, AuthorityRecord]:
    records: dict[str, AuthorityRecord] = {}
    for index, raw in enumerate(_sequence(raw_records, "authority_records")):
        row = _mapping(raw, f"authority_record_{index}")
        _exact_keys(
            row,
            {
                "actor_id",
                "authority_ref",
                "capability_id",
                "reader_intent_id",
                "record_version",
                "resource_owner_id",
                "state",
                "target_actor_ids",
            },
            f"authority_record_{index}",
        )
        authority_ref = _stable_id(row["authority_ref"], "authority_ref")
        actor_id = _stable_id(row["actor_id"], "authority_actor_id")
        capability_id = _semantic_id(
            row["capability_id"], "authority_capability_id"
        )
        reader_intent_id = _semantic_id(
            row["reader_intent_id"], "authority_reader_intent_id"
        )
        try:
            actor = actors[actor_id]
            intents[(capability_id, reader_intent_id)]
        except KeyError as exc:
            raise RosterMappingError(
                f"authority_record_reference_unresolved:{authority_ref}"
            ) from exc
        if capability_id not in actor.capability_ids:
            raise RosterMappingError(
                f"authority_capability_not_on_actor:{authority_ref}"
            )
        targets = _unique_strings(
            row["target_actor_ids"], "authority_target_actor_ids"
        )
        if not set(targets) <= set(actors):
            raise RosterMappingError(f"authority_target_unresolved:{authority_ref}")
        resource_raw = row["resource_owner_id"]
        resource_owner = (
            None
            if resource_raw is None
            else _stable_id(resource_raw, "authority_resource_owner_id")
        )
        if resource_owner is not None and resource_owner != actor.resource_owner_id:
            raise RosterMappingError(
                f"authority_resource_owner_mismatch:{authority_ref}"
            )
        state = _semantic_id(row["state"], "authority_state")
        if state != "authorized":
            raise RosterMappingError(f"fixture_authority_not_granted:{authority_ref}")
        if authority_ref in records:
            raise RosterMappingError(f"duplicate_authority_ref:{authority_ref}")
        records[authority_ref] = AuthorityRecord(
            authority_ref=authority_ref,
            actor_id=actor_id,
            capability_id=capability_id,
            reader_intent_id=reader_intent_id,
            target_actor_ids=targets,
            resource_owner_id=resource_owner,
            record_version=_integer(row["record_version"], "authority_record_version"),
            state=state,
        )
    return MappingProxyType(records)


def _aware_time(value: Any, name: str) -> tuple[str, datetime]:
    text = _string(value, name)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise RosterMappingError(f"invalid_{name}") from exc
    if parsed.tzinfo is None:
        raise RosterMappingError(f"timezone_required:{name}")
    return text, parsed


def _parse_observation_cases(
    raw_cases: Any,
    actors: Mapping[str, ActorAssembly],
    units: Mapping[str, PopulationUnit],
    observations: Mapping[tuple[str, str], ObservationPlacement],
) -> Mapping[str, ObservationCase]:
    cases: dict[str, ObservationCase] = {}
    units_by_assignment = {
        (unit.actor_id, unit.capability_id): unit for unit in units.values()
    }
    for index, raw in enumerate(_sequence(raw_cases, "observation_cases")):
        row = _mapping(raw, f"observation_case_{index}")
        _exact_keys(
            row,
            {
                "actor_id",
                "as_of",
                "authoritative_record_ref",
                "availability",
                "capability_id",
                "case_id",
                "decision_time",
                "freshness",
                "host_entity_id",
                "reader_observation_id",
                "record_version",
                "visibility",
                "visibility_scope_ids",
            },
            f"observation_case_{index}",
        )
        case_id = _stable_id(row["case_id"], "observation_case_id")
        actor_id = _stable_id(row["actor_id"], "observation_actor_id")
        capability_id = _semantic_id(
            row["capability_id"], "observation_capability_id"
        )
        reader_id = _semantic_id(
            row["reader_observation_id"], "reader_observation_id"
        )
        try:
            actor = actors[actor_id]
            placement = observations[(capability_id, reader_id)]
        except KeyError as exc:
            raise RosterMappingError(
                f"observation_case_reference_unresolved:{case_id}"
            ) from exc
        if capability_id not in actor.capability_ids:
            raise RosterMappingError(f"observation_capability_not_on_actor:{case_id}")
        visibility = _string(row["visibility"], "observation_visibility")
        availability = _string(row["availability"], "observation_availability")
        if visibility not in _VISIBILITIES or availability not in _AVAILABILITIES:
            raise RosterMappingError(f"observation_domain_invalid:{case_id}")
        scopes = _unique_strings(
            row["visibility_scope_ids"], "observation_visibility_scope_ids"
        )
        if visibility == "runtime_private" and scopes != (actor_id,):
            raise RosterMappingError(f"private_observation_scope_mismatch:{case_id}")
        host_raw = row["host_entity_id"]
        host_id = None if host_raw is None else _stable_id(host_raw, "host_entity_id")
        unit = units_by_assignment.get((actor_id, capability_id))
        if unit is not None and unit.host_entity_id is not None:
            if host_id != unit.host_entity_id:
                raise RosterMappingError(f"host_observation_scope_mismatch:{case_id}")
        elif host_id is not None:
            raise RosterMappingError(f"unexpected_host_observation_scope:{case_id}")
        record_raw = row["authoritative_record_ref"]
        record_ref = (
            None
            if record_raw is None
            else _stable_id(record_raw, "authoritative_record_ref")
        )
        if availability == "delivered" and record_ref is None:
            raise RosterMappingError(f"delivered_observation_missing_record:{case_id}")
        as_of_text, as_of = _aware_time(row["as_of"], "observation_as_of")
        decision_text, decision_time = _aware_time(
            row["decision_time"], "observation_decision_time"
        )
        if as_of > decision_time:
            raise RosterMappingError(f"future_observation:{case_id}")
        if case_id in cases:
            raise RosterMappingError(f"duplicate_observation_case:{case_id}")
        cases[case_id] = ObservationCase(
            case_id=case_id,
            actor_id=actor_id,
            capability_id=capability_id,
            reader_observation_id=reader_id,
            field_name=placement.field_name,
            host_entity_id=host_id,
            availability=availability,
            visibility=visibility,
            visibility_scope_ids=scopes,
            authoritative_record_ref=record_ref,
            record_version=_integer(row["record_version"], "record_version"),
            as_of=as_of_text,
            decision_time=decision_text,
            freshness=_stable_id(row["freshness"], "freshness"),
        )
    return MappingProxyType(cases)


def _flat_value(value: Any, name: str) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list) and all(
        item is None or isinstance(item, (str, bool, int, float)) for item in value
    ):
        return tuple(value)
    raise RosterMappingError(f"nonflat_material_parameter:{name}")


def expected_roster_idempotency_key(
    profile_id: str,
    object_id: str,
    object_version: int,
    actor_id: str,
    action_type: str,
    target_actor_ids: Sequence[str],
    material_parameters: Mapping[str, Any],
) -> str:
    """Return the deterministic key for one mapped business-object action."""

    payload = {
        "action_type": action_type,
        "actor_id": actor_id,
        "material_parameters": dict(material_parameters),
        "object_id": object_id,
        "object_version": object_version,
        "profile_id": profile_id,
        "target_actor_ids": list(target_actor_ids),
    }
    return f"idempotency.roster.{_sha256_bytes(_canonical_json(payload))[:32]}"


def _parse_lifecycle(
    raw: Any,
    profile_id: str,
    actors: Mapping[str, ActorAssembly],
    intents: Mapping[tuple[str, str], IntentPlacement],
    authority_records: Mapping[str, AuthorityRecord],
) -> LifecycleReplay:
    value = _mapping(raw, "funding_lifecycle")
    _exact_keys(
        value,
        {
            "events",
            "expected_terminal_state",
            "family_id",
            "initial_state",
            "initial_version",
            "object_id",
            "owner_actor_id",
        },
        "funding_lifecycle",
    )
    family_id = _semantic_id(value["family_id"], "lifecycle_family_id")
    if family_id != "replacement_funding":
        raise RosterMappingError(f"unexpected_lifecycle_family:{family_id}")
    object_id = _stable_id(value["object_id"], "lifecycle_object_id")
    owner_actor_id = _stable_id(value["owner_actor_id"], "lifecycle_owner_actor_id")
    if owner_actor_id not in actors:
        raise RosterMappingError("lifecycle_owner_unresolved")
    initial_state = _semantic_id(value["initial_state"], "lifecycle_initial_state")
    initial_version = _integer(value["initial_version"], "lifecycle_initial_version")
    expected_terminal = _semantic_id(
        value["expected_terminal_state"], "expected_terminal_state"
    )
    current_state = initial_state
    current_version = initial_version
    events: list[LifecycleEvent] = []
    layer_ids: set[str] = set()
    seen_event_ids: set[str] = set()
    action_capabilities: set[str] = set()
    for index, raw_event in enumerate(_sequence(value["events"], "lifecycle_events")):
        row = _mapping(raw_event, f"lifecycle_event_{index}")
        _exact_keys(
            row,
            {
                "actor_id",
                "after_state",
                "after_version",
                "authority_refs",
                "before_state",
                "before_version",
                "business_result_id",
                "capability_id",
                "delivered_observation_id",
                "event_id",
                "material_parameters",
                "reader_intent_id",
                "resource_owner_id",
                "target_actor_ids",
                "trigger",
            },
            f"lifecycle_event_{index}",
        )
        event_id = _stable_id(row["event_id"], "lifecycle_event_id")
        if event_id in seen_event_ids:
            raise RosterMappingError(f"duplicate_lifecycle_event:{event_id}")
        seen_event_ids.add(event_id)
        before_state = _semantic_id(row["before_state"], "before_state")
        after_state = _semantic_id(row["after_state"], "after_state")
        before_version = _integer(row["before_version"], "before_version")
        after_version = _integer(row["after_version"], "after_version")
        if before_state != current_state or before_version != current_version:
            raise RosterMappingError(f"lifecycle_replay_gap:{event_id}")
        if after_state == before_state or after_version != before_version + 1:
            raise RosterMappingError(f"lifecycle_transition_invalid:{event_id}")
        trigger = _string(row["trigger"], "lifecycle_trigger")
        if trigger not in _TRIGGERS:
            raise RosterMappingError(f"unknown_lifecycle_trigger:{event_id}")
        targets = _unique_strings(
            row["target_actor_ids"],
            "lifecycle_target_actor_ids",
            allow_empty=True,
        )
        if not set(targets) <= set(actors):
            raise RosterMappingError(f"lifecycle_target_unresolved:{event_id}")
        authority_refs = _unique_strings(
            row["authority_refs"], "lifecycle_authority_refs", allow_empty=True
        )
        parameters_raw = _mapping(row["material_parameters"], "material_parameters")
        parameters = MappingProxyType(
            {
                _semantic_id(name, "material_parameter_name"): _flat_value(
                    parameter, name
                )
                for name, parameter in sorted(parameters_raw.items())
            }
        )
        business_result_id = _stable_id(
            row["business_result_id"], "business_result_id"
        )
        delivered_raw = row["delivered_observation_id"]
        delivered_id = (
            None
            if delivered_raw is None
            else _stable_id(delivered_raw, "delivered_observation_id")
        )
        actor_id: str | None = None
        capability_id: str | None = None
        reader_intent_id: str | None = None
        action_type: str | None = None
        action_intent_id: str | None = None
        action_disposition_id: str | None = None
        idempotency_key: str | None = None
        resource_owner_raw = row["resource_owner_id"]
        resource_owner_id = (
            None
            if resource_owner_raw is None
            else _stable_id(resource_owner_raw, "lifecycle_resource_owner_id")
        )
        if trigger == "action":
            actor_id = _stable_id(row["actor_id"], "lifecycle_actor_id")
            capability_id = _semantic_id(
                row["capability_id"], "lifecycle_capability_id"
            )
            reader_intent_id = _semantic_id(
                row["reader_intent_id"], "lifecycle_reader_intent_id"
            )
            try:
                actor = actors[actor_id]
                intent = intents[(capability_id, reader_intent_id)]
            except KeyError as exc:
                raise RosterMappingError(
                    f"lifecycle_action_reference_unresolved:{event_id}"
                ) from exc
            if capability_id not in actor.capability_ids:
                raise RosterMappingError(
                    f"lifecycle_capability_not_on_actor:{event_id}"
                )
            if not authority_refs:
                raise RosterMappingError(
                    f"lifecycle_action_authority_missing:{event_id}"
                )
            if (
                resource_owner_id is not None
                and resource_owner_id != actor.resource_owner_id
            ):
                raise RosterMappingError(
                    f"lifecycle_resource_owner_mismatch:{event_id}"
                )
            for authority_ref in authority_refs:
                try:
                    authority = authority_records[authority_ref]
                except KeyError as exc:
                    raise RosterMappingError(
                        f"lifecycle_authority_unresolved:{event_id}:{authority_ref}"
                    ) from exc
                if (
                    authority.actor_id != actor_id
                    or authority.capability_id != capability_id
                    or authority.reader_intent_id != reader_intent_id
                    or authority.target_actor_ids != targets
                    or authority.resource_owner_id != resource_owner_id
                ):
                    raise RosterMappingError(
                        f"lifecycle_authority_scope_mismatch:{event_id}:{authority_ref}"
                    )
            action_type = intent.action_type
            action_capabilities.add(capability_id)
            action_intent_id = f"intent.{event_id}"
            action_disposition_id = f"disposition.{event_id}"
            idempotency_key = expected_roster_idempotency_key(
                profile_id,
                object_id,
                before_version,
                actor_id,
                action_type,
                targets,
                parameters,
            )
        else:
            if any(
                row[name] is not None
                for name in ("actor_id", "capability_id", "reader_intent_id")
            ):
                raise RosterMappingError(
                    f"scenario_event_has_actor_semantics:{event_id}"
                )
            if authority_refs or resource_owner_id is not None or targets or parameters:
                raise RosterMappingError(
                    f"scenario_event_has_action_payload:{event_id}"
                )
        current_ids = {
            item
            for item in (
                action_intent_id,
                action_disposition_id,
                business_result_id,
                delivered_id,
            )
            if item is not None
        }
        if len(current_ids) != sum(
            item is not None
            for item in (
                action_intent_id,
                action_disposition_id,
                business_result_id,
                delivered_id,
            )
        ):
            raise RosterMappingError(f"result_layer_identity_collision:{event_id}")
        if layer_ids & current_ids:
            raise RosterMappingError(f"lifecycle_layer_id_reused:{event_id}")
        layer_ids.update(current_ids)
        event = LifecycleEvent(
            event_id=event_id,
            trigger=trigger,
            actor_id=actor_id,
            capability_id=capability_id,
            reader_intent_id=reader_intent_id,
            action_type=action_type,
            action_intent_id=action_intent_id,
            action_disposition_id=action_disposition_id,
            idempotency_key=idempotency_key,
            target_actor_ids=targets,
            authority_refs=authority_refs,
            resource_owner_id=resource_owner_id,
            before_state=before_state,
            after_state=after_state,
            before_version=before_version,
            after_version=after_version,
            business_result_id=business_result_id,
            delivered_observation_id=delivered_id,
            material_parameters=parameters,
        )
        events.append(event)
        current_state = after_state
        current_version = after_version
    if current_state != expected_terminal:
        raise RosterMappingError(
            f"lifecycle_terminal_state_mismatch:{current_state}:{expected_terminal}"
        )
    required_capabilities = {"call_money_broker_borrower", "call_money_lender"}
    if not required_capabilities <= action_capabilities:
        raise RosterMappingError("broker_lender_lifecycle_coverage_missing")
    return LifecycleReplay(
        family_id=family_id,
        object_id=object_id,
        owner_actor_id=owner_actor_id,
        initial_state=initial_state,
        initial_version=initial_version,
        final_state=current_state,
        final_version=current_version,
        events=tuple(events),
    )


def _parse_fixture(
    raw: Any,
    profile_id: str,
    capabilities: Mapping[str, SemanticProduct],
    observations: Mapping[tuple[str, str], ObservationPlacement],
    intents: Mapping[tuple[str, str], IntentPlacement],
) -> ConformanceFixture:
    value = _mapping(raw, "conformance_fixture")
    _exact_keys(
        value,
        {
            "actors",
            "authority_records",
            "fixture_id",
            "funding_lifecycle",
            "historical_validity_claim",
            "observation_cases",
            "population_units",
            "schema",
            "structural_variants",
        },
        "conformance_fixture",
    )
    if value["schema"] != ROSTER_FIXTURE_SCHEMA_VERSION:
        raise RosterMappingError("fixture_schema_version_mismatch")
    if _boolean(value["historical_validity_claim"], "historical_validity_claim"):
        raise RosterMappingError("historical_validity_claim_forbidden")
    actors: dict[str, ActorAssembly] = {}
    entity_ids: set[str] = set()
    artifact_ids: set[str] = set()
    actor_order: list[str] = []
    named_capabilities: set[str] = set()
    for index, raw_actor in enumerate(_sequence(value["actors"], "actors")):
        actor = _parse_actor(raw_actor, index, capabilities)
        if actor.actor_id in actors:
            raise RosterMappingError(f"duplicate_actor_id:{actor.actor_id}")
        if actor.entity_id in entity_ids:
            raise RosterMappingError(f"duplicate_actor_for_entity:{actor.entity_id}")
        if actor.participant_artifact_id in artifact_ids:
            raise RosterMappingError(
                f"duplicate_participant_artifact:{actor.participant_artifact_id}"
            )
        for capability_id in actor.capability_ids:
            if capabilities[capability_id].product_kind == "agent_definition":
                if capability_id in named_capabilities:
                    raise RosterMappingError(
                        f"named_capability_instantiated_twice:{capability_id}"
                    )
                named_capabilities.add(capability_id)
        actors[actor.actor_id] = actor
        entity_ids.add(actor.entity_id)
        artifact_ids.add(actor.participant_artifact_id)
        actor_order.append(actor.actor_id)
    if actor_order != sorted(actor_order):
        raise RosterMappingError("actors_not_canonical")
    actors_proxy = MappingProxyType(actors)
    units = _parse_population_units(
        value["population_units"], actors_proxy, capabilities
    )
    authority_records = _parse_authority_records(
        value["authority_records"], actors_proxy, intents
    )
    observation_cases = _parse_observation_cases(
        value["observation_cases"], actors_proxy, units, observations
    )
    lifecycle = _parse_lifecycle(
        value["funding_lifecycle"],
        profile_id,
        actors_proxy,
        intents,
        authority_records,
    )
    variants_raw = _mapping(value["structural_variants"], "structural_variants")
    if not variants_raw:
        raise RosterMappingError("structural_variants_required")
    variants = MappingProxyType(
        {
            _semantic_id(name, "variant_name"): _stable_id(
                variant, "variant_value"
            )
            for name, variant in sorted(variants_raw.items())
        }
    )
    identity_payload = {"fixture": value, "profile_id": profile_id}
    return ConformanceFixture(
        fixture_id=_stable_id(value["fixture_id"], "fixture_id"),
        historical_validity_claim=False,
        structural_variants=variants,
        actors=actors_proxy,
        population_units=units,
        authority_records=authority_records,
        observation_cases=observation_cases,
        funding_lifecycle=lifecycle,
        identity_sha256=_sha256_bytes(_canonical_json(identity_payload)),
    )


def _validate_accepted_mapping_inputs(
    manifest: Mapping[str, Any],
    manifest_path: Path,
    root: Path,
    source_manifest_sha256: str,
) -> None:
    if manifest.get("schema") != "h2epr.consolidated-mapping-release.v0_1":
        raise RosterMappingError("accepted_mapping_schema_version_mismatch")
    if manifest.get("status") != "accepted_design_specification":
        raise RosterMappingError("accepted_mapping_status_mismatch")
    if manifest.get("integrity_algorithm") != "sha256":
        raise RosterMappingError("accepted_mapping_integrity_algorithm_mismatch")

    source = _mapping(manifest.get("source_release"), "accepted_source_release")
    if source.get("manifest_sha256") != source_manifest_sha256:
        raise RosterMappingError("accepted_mapping_source_release_mismatch")
    checksums_path = _project_file(
        root,
        source.get("checksums_path"),
        "accepted_source_release_checksums",
    )
    checksums_sha256 = _sha256(
        source.get("checksums_sha256"),
        "accepted_source_release_checksums_sha256",
    )
    if _sha256_file(checksums_path) != checksums_sha256:
        raise RosterMappingError("accepted_source_release_checksums_sha256_mismatch")

    expected_kinds = {
        "carrier_review",
        "guide",
        "mapping_specification",
        "semantic_inventory",
        "substantive_review",
    }
    observed_kinds: set[str] = set()
    observed_paths: set[str] = set()
    for index, raw_artifact in enumerate(
        _sequence(manifest.get("artifacts"), "accepted_mapping_artifacts")
    ):
        artifact = _mapping(raw_artifact, f"accepted_mapping_artifact_{index}")
        _exact_keys(
            artifact,
            {"kind", "path", "sha256"},
            f"accepted_mapping_artifact_{index}",
        )
        kind = _semantic_id(artifact["kind"], "accepted_mapping_artifact_kind")
        relative_path = _string(
            artifact["path"], "accepted_mapping_artifact_path"
        )
        if kind in observed_kinds or relative_path in observed_paths:
            raise RosterMappingError("duplicate_accepted_mapping_artifact")
        artifact_path = _anchored_file(
            root,
            manifest_path.parent,
            relative_path,
            "accepted_mapping_artifact_path",
        )
        expected_sha256 = _sha256(
            artifact["sha256"], "accepted_mapping_artifact_sha256"
        )
        if _sha256_file(artifact_path) != expected_sha256:
            raise RosterMappingError(
                f"accepted_mapping_artifact_sha256_mismatch:{kind}"
            )
        observed_kinds.add(kind)
        observed_paths.add(relative_path)
    if observed_kinds != expected_kinds:
        raise RosterMappingError("accepted_mapping_artifact_coverage_mismatch")

    owner = _mapping(manifest.get("owner_decision"), "accepted_owner_decision")
    _exact_keys(
        owner,
        {"id", "path", "resolved_items", "sha256"},
        "accepted_owner_decision",
    )
    _stable_id(owner["id"], "accepted_owner_decision_id")
    _unique_strings(owner["resolved_items"], "accepted_owner_resolved_items")
    owner_path = _project_file(
        root, owner["path"], "accepted_owner_decision_path"
    )
    owner_sha256 = _sha256(
        owner["sha256"], "accepted_owner_decision_sha256"
    )
    if _sha256_file(owner_path) != owner_sha256:
        raise RosterMappingError("accepted_owner_decision_sha256_mismatch")


def load_roster_mapping_profile(
    profile_path: str | Path,
    *,
    project_root: str | Path | None = None,
) -> RosterMappingProfile:
    """Load and fail-closed validate the accepted release-wide mapping profile."""

    path = Path(profile_path).resolve()
    root = _find_project_root(path, project_root)
    value = _read_json(path, "roster_mapping_profile")
    _exact_keys(
        value,
        {
            "accepted_mapping",
            "capabilities",
            "conformance_fixture",
            "coverage",
            "event_id",
            "event_namespace",
            "profile_id",
            "schema",
            "source_release",
            "status",
            "version",
        },
        "roster_mapping_profile",
    )
    if value["schema"] != ROSTER_MAPPING_SCHEMA_VERSION:
        raise RosterMappingError("mapping_profile_schema_version_mismatch")
    profile_id = _stable_id(value["profile_id"], "profile_id")
    version = _stable_id(value["version"], "profile_version")
    if version != "0.1":
        raise RosterMappingError("mapping_profile_version_mismatch")
    status = _stable_id(value["status"], "profile_status")
    if status != "conformance_only":
        raise RosterMappingError("mapping_profile_status_mismatch")
    event_id = _stable_id(value["event_id"], "event_id")
    event_namespace = _stable_id(value["event_namespace"], "event_namespace")

    source = _mapping(value["source_release"], "source_release")
    _exact_keys(
        source,
        {"manifest_path", "manifest_sha256", "release_id"},
        "source_release",
    )
    source_path = _project_file(
        root, source["manifest_path"], "source_release_manifest"
    )
    source_sha = _sha256(source["manifest_sha256"], "source_release_manifest_sha256")
    if _sha256_file(source_path) != source_sha:
        raise RosterMappingError("source_release_manifest_sha256_mismatch")
    source_manifest = _read_json(source_path, "source_release_manifest")
    source_release_id = _stable_id(source["release_id"], "source_release_id")
    if source_manifest.get("release_id") != source_release_id:
        raise RosterMappingError("source_release_id_mismatch")
    if source_manifest.get("event_id") != event_id:
        raise RosterMappingError("source_release_event_id_mismatch")
    manifest_products = _manifest_products(source_manifest, root)
    if len(manifest_products) != 12:
        raise RosterMappingError(
            f"source_product_count_mismatch:{len(manifest_products)}"
        )

    accepted = _mapping(value["accepted_mapping"], "accepted_mapping")
    _exact_keys(
        accepted,
        {"manifest_path", "manifest_sha256", "release_id"},
        "accepted_mapping",
    )
    accepted_path = _project_file(
        root, accepted["manifest_path"], "accepted_mapping_manifest"
    )
    accepted_sha = _sha256(
        accepted["manifest_sha256"], "accepted_mapping_manifest_sha256"
    )
    if _sha256_file(accepted_path) != accepted_sha:
        raise RosterMappingError("accepted_mapping_manifest_sha256_mismatch")
    accepted_manifest = _read_json(accepted_path, "accepted_mapping_manifest")
    accepted_mapping_id = _stable_id(accepted["release_id"], "accepted_mapping_id")
    if accepted_manifest.get("release_id") != accepted_mapping_id:
        raise RosterMappingError("accepted_mapping_id_mismatch")
    if accepted_manifest.get("event_id") != event_id:
        raise RosterMappingError("accepted_mapping_event_id_mismatch")
    _validate_accepted_mapping_inputs(
        accepted_manifest,
        accepted_path,
        root,
        source_sha,
    )

    products, capabilities = _parse_capabilities(
        value["capabilities"], manifest_products, event_namespace
    )
    observations, intents = _derive_placements(capabilities)
    coverage = _mapping(value["coverage"], "coverage")
    _exact_keys(
        coverage,
        {
            "commitments",
            "distinct_reader_intents",
            "distinct_reader_observations",
            "intent_placements",
            "observation_placements",
            "semantic_products",
        },
        "coverage",
    )
    actual_coverage = {
        "commitments": sum(len(item.commitment_ids) for item in products.values()),
        "distinct_reader_intents": len(
            {item.reader_intent_id for item in intents.values()}
        ),
        "distinct_reader_observations": len(
            {item.reader_observation_id for item in observations.values()}
        ),
        "intent_placements": len(intents),
        "observation_placements": len(observations),
        "semantic_products": len(products),
    }
    expected_coverage = {
        name: _integer(coverage[name], f"coverage_{name}") for name in coverage
    }
    if actual_coverage != expected_coverage:
        raise RosterMappingError(
            "release_coverage_mismatch:"
            f"expected={expected_coverage}:actual={actual_coverage}"
        )
    accepted_coverage = accepted_manifest.get("coverage", {})
    if any(
        accepted_coverage.get(source_name) != actual_coverage[target_name]
        for source_name, target_name in (
            ("decision_and_population_commitments", "commitments"),
            ("observation_placements", "observation_placements"),
            ("intent_placements", "intent_placements"),
        )
    ):
        raise RosterMappingError("accepted_mapping_coverage_mismatch")
    fixture = _parse_fixture(
        value["conformance_fixture"],
        profile_id,
        capabilities,
        observations,
        intents,
    )
    return RosterMappingProfile(
        profile_id=profile_id,
        version=version,
        status=status,
        event_id=event_id,
        event_namespace=event_namespace,
        source_release_id=source_release_id,
        source_release_manifest_sha256=source_sha,
        accepted_mapping_id=accepted_mapping_id,
        accepted_mapping_manifest_sha256=accepted_sha,
        profile_sha256=_sha256_file(path),
        products=products,
        capabilities=capabilities,
        observations=observations,
        intents=intents,
        fixture=fixture,
    )
