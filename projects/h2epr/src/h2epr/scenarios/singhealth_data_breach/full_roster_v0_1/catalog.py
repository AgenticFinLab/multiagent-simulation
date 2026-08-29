"""Exact authoring catalog for SingHealth full-roster Rule execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from h2epr.configuration import (
    ConfigurationAdmissionError,
    load_scenario_configuration,
)
from h2epr.execution import (
    ExecutionIOError,
    path_within,
    read_json_object,
    source_sha256_bytes,
    source_sha256_path,
)

from .semantic_inventory import CAPABILITY_INVENTORIES, LIFECYCLE_FAMILIES


EVENT_ID = "H2EPR-0616"
EVENT_NAMESPACE = "0616"
CONFIGURATION_ID = "h2epr.0616.scenario.mechanism-coverage.v0_1"
CONFIGURATION_VERSION = "0.1.0"
CONFIGURATION_PATH = Path(
    "configs/singhealth_data_breach/scenario-configuration-v0.1/"
    "scenario-configuration.json"
)
CONFIGURATION_SOURCE_SHA256 = (
    "00fe7d799b5f944da09c64ddbeea85d2addfc7948bb9f0865316962fe2d37d3d"
)
CONFIGURATION_CANONICAL_SHA256 = (
    "288c1539221cce894545234cbc477f342e609ee92130cfc9925426e9d0edb9fd"
)
CONFIGURATION_RELEASE_MANIFEST_SHA256 = (
    "96e9fbc4b6d4a52305450b7f38b0524da3949ff1262d84d8b6222e638d8268a9"
)
MAPPING_PROFILE_ID = "h2epr.roster-consolidated-mapping.0616.v0_1"
MAPPING_PROFILE_PATH = Path(
    "agents/bindings/singhealth_data_breach/consolidated/"
    "mapping-specification.md"
)
MAPPING_PROFILE_SHA256 = (
    "1249dbe94dcad61b40c4e543435186e6e71eaab0d95c7f2877e31c0e3575a1bb"
)
SEMANTIC_INVENTORY_PATH = Path(
    "agents/bindings/singhealth_data_breach/consolidated/semantic-inventory.md"
)
SEMANTIC_INVENTORY_SHA256 = (
    "a9a7f2ceaf2ce0727bbf6f81399b0da00a88d5b64b7198a7ecf105b1d9f3578f"
)
ROSTER_RELEASE_MANIFEST_PATH = Path(
    "releases/singhealth_data_breach/roster-definition-v0.1/manifest.json"
)
ROSTER_RELEASE_MANIFEST_SHA256 = (
    "188f5117f02958997f8e1140d3d19fcbada296b1750223d8b3025e1cf537625e"
)


class SingHealthPolicyCatalogError(ValueError):
    """An accepted parent or exact execution inventory is invalid."""


@dataclass(frozen=True)
class CapabilityPlacement:
    """One configured actor-capability realization scope."""

    realization_key: str
    actor_id: str
    entity_id: str
    participant_product_id: str
    representation_class: str
    institution_id: str
    resource_owner_id: str
    authority_graph_id: str
    capacity_ids: tuple[str, ...]
    capability_id: str
    source_product_version: str
    source_product_path: str
    source_product_sha256: str
    commitment_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    private_state_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]
    configuration_parameter_bindings: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class SingHealthPolicyCatalog:
    """Closed inventory against which executable SingHealth assets are checked."""

    event_id: str
    configuration_id: str
    configuration_version: str
    mapping_profile_id: str
    placements: Mapping[str, CapabilityPlacement]
    selected_policy_ids: tuple[str, ...]
    selected_policy_pointers: Mapping[str, str]
    policy_governed_semantic_ids: Mapping[str, tuple[str, ...]]
    lifecycle_ids: tuple[str, ...]
    coverage: Mapping[str, int]


@dataclass(frozen=True)
class _ReleasedProduct:
    product_id: str
    product_kind: str
    version: str
    path: str
    sha256: str


def _project_root(supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        root = next(
            (
                parent
                for parent in Path(__file__).resolve().parents
                if parent.joinpath("src/h2epr").is_dir()
                and parent.joinpath("configs").is_dir()
            ),
            Path(),
        )
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_PROJECT_ROOT_INVALID"
        )
    return root


def _duplicates(values: Sequence[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _released_products(root: Path) -> Mapping[str, _ReleasedProduct]:
    path = root / ROSTER_RELEASE_MANIFEST_PATH
    try:
        manifest, raw = read_json_object(path, pointer="/roster_release_manifest")
    except ExecutionIOError as exc:
        raise SingHealthPolicyCatalogError(
            f"SINGHEALTH_CATALOG_ROSTER_REJECTED:{exc.code.value}"
        ) from exc
    if source_sha256_bytes(raw) != ROSTER_RELEASE_MANIFEST_SHA256:
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_ROSTER_INTEGRITY_MISMATCH"
        )
    if (
        manifest.get("schema") != "h2epr.roster-definition-release.v0_1"
        or manifest.get("status") != "accepted_semantic_release"
        or manifest.get("event_id") != EVENT_ID
    ):
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_ROSTER_IDENTITY_MISMATCH"
        )

    products: dict[str, _ReleasedProduct] = {}
    for collection, kind in (
        ("agent_definitions", "agent_definition"),
        ("population_models", "population_model"),
    ):
        rows = manifest.get(collection)
        if not isinstance(rows, list):
            raise SingHealthPolicyCatalogError(
                f"SINGHEALTH_CATALOG_ROSTER_COLLECTION_INVALID:{collection}"
            )
        for row in rows:
            if not isinstance(row, dict) or set(row) != {
                "id",
                "version",
                "path",
                "sha256",
            }:
                raise SingHealthPolicyCatalogError(
                    f"SINGHEALTH_CATALOG_PRODUCT_INVALID:{collection}"
                )
            product_id = row["id"]
            if not all(
                isinstance(row[field], str) and row[field]
                for field in ("id", "version", "path", "sha256")
            ) or product_id in products:
                raise SingHealthPolicyCatalogError(
                    f"SINGHEALTH_CATALOG_PRODUCT_INVALID:{collection}"
                )
            try:
                product_path = path_within(
                    root,
                    root / row["path"],
                    pointer=f"/roster_release_manifest/{collection}/{product_id}",
                )
            except ExecutionIOError as exc:
                raise SingHealthPolicyCatalogError(
                    f"SINGHEALTH_CATALOG_PRODUCT_PATH_REJECTED:{exc.code.value}"
                ) from exc
            if (
                not product_path.is_file()
                or source_sha256_path(product_path) != row["sha256"]
            ):
                raise SingHealthPolicyCatalogError(
                    f"SINGHEALTH_CATALOG_PRODUCT_INTEGRITY_MISMATCH:{product_id}"
                )
            products[product_id] = _ReleasedProduct(
                product_id=product_id,
                product_kind=kind,
                version=row["version"],
                path=row["path"],
                sha256=row["sha256"],
            )
    return MappingProxyType(products)


def _validate_static_inventory(products: Mapping[str, _ReleasedProduct]) -> None:
    expected_product_ids = {
        inventory.product_id for inventory in CAPABILITY_INVENTORIES.values()
    }
    if set(products) != expected_product_ids:
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_PRODUCT_COVERAGE_MISMATCH"
        )
    for capability_id, inventory in CAPABILITY_INVENTORIES.items():
        product = products[inventory.product_id]
        if product.product_kind != inventory.product_kind:
            raise SingHealthPolicyCatalogError(
                f"SINGHEALTH_CATALOG_PRODUCT_KIND_MISMATCH:{capability_id}"
            )
        for name, values in (
            ("commitment", inventory.released_decision_ids),
            ("observation", inventory.observation_ids),
            ("private_state", inventory.private_state_ids),
            ("intent", inventory.intent_ids),
        ):
            if not values or _duplicates(values):
                raise SingHealthPolicyCatalogError(
                    f"SINGHEALTH_CATALOG_{name.upper()}_INVENTORY_INVALID:"
                    f"{capability_id}"
                )
    product_counts = {
        "decision_and_population_commitments": sum(
            len(item.released_decision_ids)
            for item in CAPABILITY_INVENTORIES.values()
        ),
        "observation_placements": sum(
            len(item.observation_ids) for item in CAPABILITY_INVENTORIES.values()
        ),
        "private_state_placements": sum(
            len(item.private_state_ids)
            for item in CAPABILITY_INVENTORIES.values()
        ),
        "intent_placements": sum(
            len(item.intent_ids) for item in CAPABILITY_INVENTORIES.values()
        ),
        "lifecycle_families": len(LIFECYCLE_FAMILIES),
    }
    if product_counts != {
        "decision_and_population_commitments": 29,
        "observation_placements": 62,
        "private_state_placements": 44,
        "intent_placements": 54,
        "lifecycle_families": 11,
    }:
        raise SingHealthPolicyCatalogError(
            f"SINGHEALTH_CATALOG_STATIC_COVERAGE_MISMATCH:{product_counts}"
        )


def _machine_ids(
    capability_id: str,
    names: Sequence[str],
    *,
    kind: str,
) -> tuple[str, ...]:
    prefixes = {
        "commitment": f"h2epr.commitment.{EVENT_NAMESPACE}.{capability_id}.",
        "observation": f"obs.{capability_id}.",
        "private_state": f"state.{capability_id}.",
        "intent": f"h2epr.action.{EVENT_NAMESPACE}.{capability_id}.",
    }
    return tuple(f"{prefixes[kind]}{name}" for name in names)


def _placement(
    *,
    actor: Mapping[str, Any],
    product_id: str,
    representation_class: str,
    institution_id: str,
    capacity_ids: tuple[str, ...],
    products: Mapping[str, _ReleasedProduct],
) -> CapabilityPlacement:
    actor_id = str(actor["actor_id"])
    capability_id = str(actor["capability_id"])
    try:
        inventory = CAPABILITY_INVENTORIES[capability_id]
        product = products[product_id]
    except KeyError as exc:
        raise SingHealthPolicyCatalogError(
            f"SINGHEALTH_CATALOG_CAPABILITY_UNRESOLVED:{actor_id}:{capability_id}"
        ) from exc
    if inventory.product_id != product_id:
        raise SingHealthPolicyCatalogError(
            f"SINGHEALTH_CATALOG_PRODUCT_BINDING_MISMATCH:"
            f"{actor_id}:{capability_id}"
        )
    realization_key = f"{actor_id}::{capability_id}"
    return CapabilityPlacement(
        realization_key=realization_key,
        actor_id=actor_id,
        entity_id=str(actor["entity_id"]),
        participant_product_id=product_id,
        representation_class=representation_class,
        institution_id=institution_id,
        resource_owner_id=str(actor["resource_owner_id"]),
        authority_graph_id=str(actor["authority_graph_id"]),
        capacity_ids=capacity_ids,
        capability_id=capability_id,
        source_product_version=product.version,
        source_product_path=product.path,
        source_product_sha256=product.sha256,
        commitment_ids=_machine_ids(
            capability_id,
            inventory.released_decision_ids,
            kind="commitment",
        ),
        observation_ids=_machine_ids(
            capability_id,
            inventory.observation_ids,
            kind="observation",
        ),
        private_state_ids=_machine_ids(
            capability_id,
            inventory.private_state_ids,
            kind="private_state",
        ),
        intent_ids=_machine_ids(
            capability_id,
            inventory.intent_ids,
            kind="intent",
        ),
        configuration_parameter_bindings=(),
    )


def build_singhealth_policy_catalog(
    *, project_root: str | Path | None = None
) -> SingHealthPolicyCatalog:
    """Resolve accepted parents and expand the exact 13-actor inventory."""

    root = _project_root(project_root)
    try:
        configuration = load_scenario_configuration(
            root / CONFIGURATION_PATH,
            project_root=root,
            expected_source_sha256=CONFIGURATION_SOURCE_SHA256,
            expected_release_manifest_sha256=(
                CONFIGURATION_RELEASE_MANIFEST_SHA256
            ),
        )
    except ConfigurationAdmissionError as exc:
        raise SingHealthPolicyCatalogError(
            f"SINGHEALTH_CATALOG_CONFIGURATION_REJECTED:{exc.code.value}"
        ) from exc
    if (
        configuration.event_id != EVENT_ID
        or configuration.configuration_id != CONFIGURATION_ID
        or configuration.version != CONFIGURATION_VERSION
        or configuration.canonical_sha256 != CONFIGURATION_CANONICAL_SHA256
        or configuration.mapping_profile_id != MAPPING_PROFILE_ID
        or configuration.mapping_profile_sha256 != MAPPING_PROFILE_SHA256
    ):
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_PARENT_IDENTITY_MISMATCH"
        )
    if (
        not (root / SEMANTIC_INVENTORY_PATH).is_file()
        or source_sha256_path(root / SEMANTIC_INVENTORY_PATH)
        != SEMANTIC_INVENTORY_SHA256
    ):
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_SEMANTIC_INVENTORY_INTEGRITY_MISMATCH"
        )

    products = _released_products(root)
    _validate_static_inventory(products)
    document = configuration.document
    units_by_actor = {
        str(unit["actor_id"]): unit for unit in document["population_units"]
    }
    placements: dict[str, CapabilityPlacement] = {}
    for actor in document["named_actors"]:
        placement = _placement(
            actor=actor,
            product_id=str(actor["participant_product_id"]),
            representation_class="autonomous_participant_agent",
            institution_id=str(actor["primary_institution_id"]),
            capacity_ids=tuple(str(item) for item in actor["capacity_ids"]),
            products=products,
        )
        if placement.realization_key in placements:
            raise SingHealthPolicyCatalogError(
                f"SINGHEALTH_CATALOG_REALIZATION_DUPLICATE:"
                f"{placement.realization_key}"
            )
        placements[placement.realization_key] = placement
    for actor in document["population_actors"]:
        actor_id = str(actor["actor_id"])
        try:
            unit = units_by_actor[actor_id]
        except KeyError as exc:
            raise SingHealthPolicyCatalogError(
                f"SINGHEALTH_CATALOG_POPULATION_UNIT_UNRESOLVED:{actor_id}"
            ) from exc
        placement = _placement(
            actor=actor,
            product_id=str(unit["population_product_id"]),
            representation_class="aggregate_population_agent",
            institution_id=str(actor["host_institution_id"]),
            capacity_ids=(str(actor["capacity_id"]),),
            products=products,
        )
        if placement.realization_key in placements:
            raise SingHealthPolicyCatalogError(
                f"SINGHEALTH_CATALOG_REALIZATION_DUPLICATE:"
                f"{placement.realization_key}"
            )
        placements[placement.realization_key] = placement

    policy_rows = tuple(document["policy_selections"])
    policy_ids = tuple(sorted(str(row["policy_id"]) for row in policy_rows))
    if _duplicates(policy_ids):
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_POLICY_DUPLICATE"
        )
    policy_pointers = MappingProxyType(
        {
            str(row["policy_id"]): f"/policy_selections/{index}"
            for index, row in enumerate(policy_rows)
        }
    )
    lifecycle_ids = tuple(
        f"lifecycle.{EVENT_NAMESPACE}.{family}"
        for family in LIFECYCLE_FAMILIES
    )
    policy_governed_semantic_ids = MappingProxyType(
        {
            "POL-0616-AUTH-01": (
                "scenario.0616.authority.capacity_relationship_access_resource",
            ),
            "POL-0616-COORD-01": (
                "scenario.0616.coordination.meeting_sirt_assignment",
            ),
            "POL-0616-INCIDENT-01": (
                "scenario.0616.incident.assessment_category_reporting_direction",
            ),
            "POL-0616-INFO-01": (
                "scenario.0616.information.source_route_delivery_freshness_correction",
            ),
            "POL-0616-LIFECYCLE-01": (
                "scenario.0616.lifecycle.typed_adjudication_result_observation",
                *lifecycle_ids,
            ),
            "POL-0616-NOTIFY-01": (
                "scenario.0616.notification.preparation_authorization_delivery",
            ),
            "POL-0616-ROUTE-01": (
                "scenario.0616.route.issue_transport_delivery_acknowledgement",
            ),
            "POL-0616-TECH-01": (
                "scenario.0616.technical.authority_prestate_access_feasibility",
            ),
            "POL-0616-TIME-01": (
                "scenario.0616.time.event_partial_order_and_reopening",
            ),
        }
    )
    if set(policy_governed_semantic_ids) != set(policy_ids):
        raise SingHealthPolicyCatalogError(
            "SINGHEALTH_CATALOG_POLICY_SEMANTICS_MISMATCH"
        )

    placement_values = tuple(placements.values())
    coverage = MappingProxyType(
        {
            "semantic_products": len(CAPABILITY_INVENTORIES),
            "product_decision_commitments": sum(
                len(item.released_decision_ids)
                for item in CAPABILITY_INVENTORIES.values()
            ),
            "product_observation_placements": sum(
                len(item.observation_ids)
                for item in CAPABILITY_INVENTORIES.values()
            ),
            "product_private_state_placements": sum(
                len(item.private_state_ids)
                for item in CAPABILITY_INVENTORIES.values()
            ),
            "product_intent_placements": sum(
                len(item.intent_ids)
                for item in CAPABILITY_INVENTORIES.values()
            ),
            "actor_instances": len(placement_values),
            "actor_capability_bindings": len(placement_values),
            "population_units": len(document["population_units"]),
            "exogenous_inputs": len(document["exogenous_inputs"]),
            "structural_selections": len(document["structural_variants"]),
            "decision_commitments": sum(
                len(item.commitment_ids) for item in placement_values
            ),
            "observation_placements": sum(
                len(item.observation_ids) for item in placement_values
            ),
            "private_state_placements": sum(
                len(item.private_state_ids) for item in placement_values
            ),
            "configuration_parameter_bindings": sum(
                len(item.configuration_parameter_bindings)
                for item in placement_values
            ),
            "intent_placements": sum(
                len(item.intent_ids) for item in placement_values
            ),
            "lifecycle_families": len(lifecycle_ids),
            "selected_policies": len(policy_ids),
        }
    )
    expected_coverage = {
        "semantic_products": 9,
        "product_decision_commitments": 29,
        "product_observation_placements": 62,
        "product_private_state_placements": 44,
        "product_intent_placements": 54,
        "actor_instances": 13,
        "actor_capability_bindings": 13,
        "population_units": 6,
        "exogenous_inputs": 6,
        "structural_selections": 6,
        "decision_commitments": 41,
        "observation_placements": 82,
        "private_state_placements": 60,
        "configuration_parameter_bindings": 0,
        "intent_placements": 74,
        "lifecycle_families": 11,
        "selected_policies": 9,
    }
    if dict(coverage) != expected_coverage:
        raise SingHealthPolicyCatalogError(
            f"SINGHEALTH_CATALOG_COVERAGE_MISMATCH:{dict(coverage)}"
        )
    return SingHealthPolicyCatalog(
        event_id=EVENT_ID,
        configuration_id=CONFIGURATION_ID,
        configuration_version=CONFIGURATION_VERSION,
        mapping_profile_id=MAPPING_PROFILE_ID,
        placements=MappingProxyType(dict(sorted(placements.items()))),
        selected_policy_ids=policy_ids,
        selected_policy_pointers=policy_pointers,
        policy_governed_semantic_ids=policy_governed_semantic_ids,
        lifecycle_ids=lifecycle_ids,
        coverage=coverage,
    )


__all__ = [
    "CONFIGURATION_CANONICAL_SHA256",
    "CONFIGURATION_ID",
    "CONFIGURATION_PATH",
    "CONFIGURATION_RELEASE_MANIFEST_SHA256",
    "CONFIGURATION_SOURCE_SHA256",
    "CONFIGURATION_VERSION",
    "CapabilityPlacement",
    "EVENT_ID",
    "EVENT_NAMESPACE",
    "MAPPING_PROFILE_ID",
    "MAPPING_PROFILE_PATH",
    "MAPPING_PROFILE_SHA256",
    "ROSTER_RELEASE_MANIFEST_PATH",
    "ROSTER_RELEASE_MANIFEST_SHA256",
    "SEMANTIC_INVENTORY_PATH",
    "SEMANTIC_INVENTORY_SHA256",
    "SingHealthPolicyCatalog",
    "SingHealthPolicyCatalogError",
    "build_singhealth_policy_catalog",
]
