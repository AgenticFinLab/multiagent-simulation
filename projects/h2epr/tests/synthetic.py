"""Build small, event-neutral packages for framework contract tests.

The fixtures in this module are generated inside a temporary directory.  They
exercise the same release, compiler, runtime, replay, graph, and publication
paths as a repository event without making any historical event a hidden test
oracle.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from h2epr.benchmark._compiler_core import (
    _derive_configuration_admission_receipt,
    _derive_rule_configuration_admission_receipt,
)
from h2epr.benchmark.compiler import compile_event_package
from h2epr.canonical import canonical_sha256, file_sha256, write_json
from h2epr.semantic.assets import (
    assembly_sha256,
    backend_catalog_sha256,
    semantic_assembly_sha256,
)

from support import PROJECT_ROOT


SHA_PLACEHOLDER = "0" * 64
IMPLEMENTATION_PATHS = (
    "src/h2epr/backends/interface.py",
    "src/h2epr/backends/_rule_core.py",
    "src/h2epr/backends/rule.py",
    "src/h2epr/backends/registry.py",
    "src/h2epr/runtime/information.py",
)
CLAIM_EXCLUSIONS = (
    "held-out evaluation",
    "historical fit",
    "parameter calibration",
    "causal validity",
    "scientific validity",
    "universal generality",
)
PROHIBITED_INPUTS = (
    "reference_epg",
    "held_out_suffix",
    "evaluation_only_content",
    "external_research",
    "network_retrieval",
)


@dataclass(frozen=True)
class SyntheticVocabulary:
    event_id: str
    slug: str
    title: str
    first_actor: str
    second_actor: str
    entity_id: str
    initial_value: str
    intermediate_value: str
    terminal_value: str
    first_intent: str
    second_intent: str
    message_kind: str


@dataclass(frozen=True)
class SyntheticEvent:
    event_id: str
    slug: str
    title: str
    project_root: Path
    data_root: Path
    assembly_path: Path
    package_root: Path


SIGNAL_CASE = SyntheticVocabulary(
    event_id="H2EPR-9001",
    slug="synthetic_signal",
    title="Synthetic signal process",
    first_actor="initiator",
    second_actor="responders",
    entity_id="process",
    initial_value="idle",
    intermediate_value="active",
    terminal_value="closed",
    first_intent="activate_process",
    second_intent="close_process",
    message_kind="activation_notice",
)


DISPATCH_CASE = SyntheticVocabulary(
    event_id="H2EPR-9002",
    slug="synthetic_dispatch",
    title="Synthetic dispatch process",
    first_actor="publisher",
    second_actor="observers",
    entity_id="record",
    initial_value="queued",
    intermediate_value="announced",
    terminal_value="acknowledged",
    first_intent="announce_record",
    second_intent="acknowledge_record",
    message_kind="record_notice",
)


def _sealed(value: dict[str, Any], field: str) -> dict[str, Any]:
    value[field] = SHA_PLACEHOLDER
    value[field] = canonical_sha256(
        {key: item for key, item in value.items() if key != field}
    )
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, value)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _artifact(
    root: Path,
    *,
    artifact_id: str,
    artifact_version: str,
    role: str,
    relative_path: str,
) -> dict[str, Any]:
    path = root / relative_path
    return {
        "artifact_id": artifact_id,
        "artifact_version": artifact_version,
        "role": role,
        "relative_path": relative_path,
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
    }


def _write_inventory(root: Path) -> None:
    rows = [
        f"{file_sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "SHA256SUMS"
    ]
    (root / "SHA256SUMS").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _release(
    root: Path,
    *,
    event_id: str,
    release_id: str,
    release_kind: str,
    artifacts: Iterable[dict[str, Any]],
    semantic_parent_ids: Iterable[str] = (),
) -> dict[str, Any]:
    _write_text(
        root / "README.md",
        "# Synthetic contract release\n\n"
        "This temporary release exists only for event-neutral framework tests.",
    )
    manifest: dict[str, Any] = {
        "schema_version": "h2epr.semantic-release-manifest.v2",
        "release_id": release_id,
        "release_version": "1.0.0",
        "event_id": event_id,
        "release_kind": release_kind,
        "artifacts": list(artifacts),
        "manifest_sha256": SHA_PLACEHOLDER,
    }
    parents = list(semantic_parent_ids)
    if parents:
        manifest["semantic_parent_ids"] = parents
    _sealed(manifest, "manifest_sha256")
    _write(root / "manifest.json", manifest)
    _write_inventory(root)
    return manifest


def _provenance_coverage(configuration: Mapping[str, Any]) -> dict[str, Any]:
    pointers = sorted(row["json_pointer"] for row in configuration["value_provenance"])
    return _sealed(
        {
            "schema_version": "h2epr.configuration-provenance-coverage.v4",
            "coverage_id": f"{configuration['configuration_id']}.provenance-coverage",
            "configuration_id": configuration["configuration_id"],
            "configuration_sha256": configuration["configuration_sha256"],
            "covered_setting_pointers": pointers,
            "exemptions": [],
            "coverage_sha256": SHA_PLACEHOLDER,
        },
        "coverage_sha256",
    )


def _source_documents(
    data_root: Path,
    vocabulary: SyntheticVocabulary,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    event_spec = {
        "schema_version": "h2epr.synthetic-event-spec.v1",
        "public_event_id": vocabulary.event_id,
        "title": vocabulary.title,
    }
    frozen_evidence = {
        "schema_version": "h2epr.synthetic-frozen-evidence.v1",
        "public_event_id": vocabulary.event_id,
        "source_count": 1,
        "sources": [
            {
                "source_id": "synthetic-source-1",
                "scope": "contract-test-only",
            }
        ],
    }

    def wrapped(value: str) -> dict[str, str]:
        return {"value": value}

    draft_epg = {
        "event_id": vocabulary.event_id,
        "title": wrapped(vocabulary.title),
        "start_time": wrapped("2000-01-01"),
        "end_time": wrapped("2000-01-02"),
        "stages": [
            {
                "stage_id": "S1",
                "name": wrapped("Synthetic transition"),
                "start_time": wrapped("2000-01-01"),
                "end_time": wrapped("2000-01-02"),
                "episodes": [
                    {
                        "episode_id": "E1",
                        "name": wrapped("Opening action"),
                        "start_time": wrapped("2000-01-01"),
                        "end_time": wrapped("2000-01-01"),
                        "participants": [
                            {
                                "participant_id": "P_1",
                                "name": wrapped(vocabulary.first_actor.replace("_", " ").title()),
                                "participant_type": wrapped("organization"),
                                "base_role": wrapped("initiator"),
                                "actions": [
                                    {
                                        "name": wrapped(vocabulary.first_intent),
                                        "timestamp": wrapped("2000-01-01"),
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "episode_id": "E2",
                        "name": wrapped("Closing action"),
                        "start_time": wrapped("2000-01-02"),
                        "end_time": wrapped("2000-01-02"),
                        "participants": [
                            {
                                "participant_id": "P_2",
                                "name": wrapped(vocabulary.second_actor.replace("_", " ").title()),
                                "participant_type": wrapped("population"),
                                "base_role": wrapped("responder"),
                                "actions": [
                                    {
                                        "name": wrapped(vocabulary.second_intent),
                                        "timestamp": wrapped("2000-01-02"),
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        ],
    }
    source_root = (
        data_root
        / "development_samples_v1"
        / "events"
        / vocabulary.event_id
    )
    for name, value in (
        ("event_spec", event_spec),
        ("frozen_evidence", frozen_evidence),
        ("draft_epg", draft_epg),
    ):
        _write(source_root / f"{name}.json", value)
    return event_spec, frozen_evidence, draft_epg


def build_synthetic_event(
    workspace: Path,
    vocabulary: SyntheticVocabulary,
    *,
    mechanism_transform: Callable[[dict[str, Any]], None] | None = None,
    shared_settings_transform: Callable[[dict[str, Any]], None] | None = None,
    rule_settings_transform: Callable[[dict[str, Any]], None] | None = None,
) -> SyntheticEvent:
    """Compile a temporary fixture, including caller-declared negative cases.

    Transforms run before dependent receipts and identities are derived. They
    never mutate an admitted package or bypass normal compiler admission.
    """

    project_root = workspace / "project"
    data_root = workspace / "data"
    project_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)
    for relative_path in IMPLEMENTATION_PATHS:
        target = project_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / relative_path, target)
    for relative_path in (
        "templates/simulation-reading.md",
        "templates/cross-event-analysis.md",
        "backends/llm-prompt-contract-template.md",
        "schemas/participant-decision.schema.json",
    ):
        target = project_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / relative_path, target)

    _source_documents(data_root, vocabulary)
    code = vocabulary.event_id.removeprefix("H2EPR-")
    prefix = f"h2epr.synthetic.{code}"
    version = "1.0.0"
    active_ids = sorted([vocabulary.first_actor, vocabulary.second_actor])
    source_root = (
        data_root
        / "development_samples_v1"
        / "events"
        / vocabulary.event_id
    )
    allowed_inputs = []
    for logical_name in ("event_spec", "frozen_evidence", "draft_epg"):
        path = source_root / f"{logical_name}.json"
        allowed_inputs.append(
            {
                "logical_name": logical_name,
                "relative_path": (
                    Path("development_samples_v1")
                    / "events"
                    / vocabulary.event_id
                    / f"{logical_name}.json"
                ).as_posix(),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    source_profile = _sealed(
        {
            "schema_version": "h2epr.source-profile.v3",
            "profile_id": f"{prefix}.source-profile.v1",
            "profile_version": version,
            "event_id": vocabulary.event_id,
            "event_slug": vocabulary.slug,
            "exposure_mode": "full_draft_exposed",
            "protocol_eligibility": "synthetic_contract_test_only",
            "allowed_inputs": allowed_inputs,
            "prohibited_inputs": list(PROHIBITED_INPUTS),
            "discovery_policy": "direct_paths_only_no_sibling_inventory",
            "dataset_limitations": [
                "The event is synthetic and carries no historical meaning."
            ],
            "claim_boundary": {
                "supports": ["event-neutral engineering contract tests"],
                "does_not_support": list(CLAIM_EXCLUSIONS),
            },
            "profile_sha256": SHA_PLACEHOLDER,
        },
        "profile_sha256",
    )
    source_profile_path = project_root / "events" / vocabulary.slug / "source-profile.json"
    _write(source_profile_path, source_profile)

    first_name = vocabulary.first_actor.replace("_", " ").title()
    second_name = vocabulary.second_actor.replace("_", " ").title()
    roster_id = f"{prefix}.roster.v1"
    roster = _sealed(
        {
            "schema_version": "h2epr.participant-roster.v2",
            "roster_id": roster_id,
            "roster_version": version,
            "event_id": vocabulary.event_id,
            "source_profile_id": source_profile["profile_id"],
            "participant_count": 2,
            "occurrence_count": 2,
            "source_id_gaps": [],
            "source_id_gap_interpretation": "No numeric source identifiers are missing.",
            "participants": [
                {
                    "source_participant_id": "P_1",
                    "canonical_name": first_name,
                    "observed_names": [first_name],
                    "observed_types": ["organization"],
                    "observed_roles": ["initiator"],
                    "appearance_refs": ["draft_epg:S1/E1/P_1"],
                },
                {
                    "source_participant_id": "P_2",
                    "canonical_name": second_name,
                    "observed_names": [second_name],
                    "observed_types": ["population"],
                    "observed_roles": ["responder"],
                    "appearance_refs": ["draft_epg:S1/E2/P_2"],
                },
            ],
            "roster_sha256": SHA_PLACEHOLDER,
        },
        "roster_sha256",
    )
    actor_map_id = f"{prefix}.actor-map.v1"
    first_parent_id = f"{prefix}.agent.{vocabulary.first_actor}.v1"
    second_parent_id = f"{prefix}.population.{vocabulary.second_actor}.v1"
    actor_map = _sealed(
        {
            "schema_version": "h2epr.actor-map.v2",
            "actor_map_id": actor_map_id,
            "actor_map_version": version,
            "event_id": vocabulary.event_id,
            "roster_id": roster_id,
            "mappings": [
                {
                    "source_participant_id": "P_1",
                    "disposition": "named_agent",
                    "target_id": vocabulary.first_actor,
                    "rationale": "The synthetic Draft assigns the opening action.",
                    "losses": ["No undeclared internal state is synthesized."],
                },
                {
                    "source_participant_id": "P_2",
                    "disposition": "population",
                    "target_id": vocabulary.second_actor,
                    "rationale": "The synthetic Draft assigns the closing response.",
                    "losses": ["No individual variation is synthesized."],
                },
            ],
            "runtime_actors": [
                {
                    "actor_id": vocabulary.first_actor,
                    "representation_kind": "agent",
                    "semantic_parent_id": first_parent_id,
                    "source_participant_ids": ["P_1"],
                },
                {
                    "actor_id": vocabulary.second_actor,
                    "representation_kind": "population",
                    "semantic_parent_id": second_parent_id,
                    "source_participant_ids": ["P_2"],
                },
            ],
            "actor_map_sha256": SHA_PLACEHOLDER,
        },
        "actor_map_sha256",
    )
    roster_root = project_root / "agents" / "rosters" / vocabulary.slug
    _write(roster_root / "roster.json", roster)
    _write(roster_root / "actor-map.json", actor_map)
    roster_manifest = _release(
        roster_root,
        event_id=vocabulary.event_id,
        release_id=f"{prefix}.roster-release.v1",
        release_kind="roster",
        artifacts=(
            _artifact(
                roster_root,
                artifact_id=roster_id,
                artifact_version=version,
                role="participant_roster",
                relative_path="roster.json",
            ),
            _artifact(
                roster_root,
                artifact_id=actor_map_id,
                artifact_version=version,
                role="actor_map",
                relative_path="actor-map.json",
            ),
        ),
        semantic_parent_ids=(source_profile["profile_id"],),
    )

    parent_rows = []
    for actor_id, kind, parent_id, participant_id, anchor in (
        (
            vocabulary.first_actor,
            "agent",
            first_parent_id,
            "P_1",
            "draft_epg:S1/E1/P_1",
        ),
        (
            vocabulary.second_actor,
            "population",
            second_parent_id,
            "P_2",
            "draft_epg:S1/E2/P_2",
        ),
    ):
        if kind == "agent":
            relative = Path("agents") / "defines" / vocabulary.slug / f"{actor_id}.md"
        else:
            relative = Path("populations") / "models" / vocabulary.slug / f"{actor_id}.md"
        _write_text(
            project_root / relative,
            f"# {actor_id}\n\n"
            f"Source anchor: `{anchor}`.\n\n"
            "This semantic parent is a minimal synthetic contract fixture. It "
            "declares no behavior beyond the participant interface.",
        )
        parent_rows.append(
            {
                "semantic_parent_id": parent_id,
                "actor_id": actor_id,
                "representation_kind": kind,
                "relative_path": relative.as_posix(),
                "sha256": file_sha256(project_root / relative),
                "source_participant_ids": [participant_id],
                "source_anchor_refs": [anchor],
            }
        )

    observation_ids = [
        "obs.public_state",
        "obs.delivered_messages",
        "obs.pending_lifecycles",
        "obs.participant_memory",
    ]
    lifecycle_ids = ["action_disposition", "message_delivery"]
    observation_registry = _sealed(
        {
            "schema_version": "h2epr.observation-registry.v2",
            "registry_id": f"{prefix}.observation-registry.v1",
            "registry_version": version,
            "event_id": vocabulary.event_id,
            "observations": [
                {
                    "observation_id": "obs.public_state",
                    "meaning": "Sealed public state at coordinate open.",
                    "producer": "h2epr.runtime.benchmark_runner.v3",
                    "consumers": active_ids,
                    "availability": "Before decision collection.",
                    "missing_behavior": "Fail the run.",
                    "visibility": "public",
                },
                {
                    "observation_id": "obs.delivered_messages",
                    "meaning": "Messages delivered at this coordinate.",
                    "producer": "masim.AppendOnlyTransport",
                    "consumers": active_ids,
                    "availability": "After due-message routing.",
                    "missing_behavior": "Use an empty list.",
                    "visibility": "delivered_message",
                },
                {
                    "observation_id": "obs.pending_lifecycles",
                    "meaning": "This actor's outgoing nonterminal message lifecycle references.",
                    "producer": "masim.AppendOnlyTransport",
                    "consumers": active_ids,
                    "availability": "At every coordinate.",
                    "missing_behavior": "Use an empty list.",
                    "visibility": "lifecycle_reference",
                },
                {
                    "observation_id": "obs.participant_memory",
                    "meaning": "Trace-derived received messages and own prior action dispositions.",
                    "producer": "h2epr.runtime.benchmark_runner.v3",
                    "consumers": active_ids,
                    "availability": "At coordinate open; current deliveries join before decisions.",
                    "missing_behavior": "Empty on the first coordinate; malformed memory fails.",
                    "visibility": "actor_private",
                },
            ],
            "registry_sha256": SHA_PLACEHOLDER,
        },
        "registry_sha256",
    )
    intent_registry = _sealed(
        {
            "schema_version": "h2epr.intent-registry.v2",
            "registry_id": f"{prefix}.intent-registry.v1",
            "registry_version": version,
            "event_id": vocabulary.event_id,
            "intents": [
                {
                    "intent_id": vocabulary.first_intent,
                    "meaning": "Apply the opening synthetic transition.",
                    "eligible_actors": [vocabulary.first_actor],
                    "eligible_targets": [vocabulary.entity_id],
                    "payload_contract": "Exactly the declared target parameter.",
                    "authority_owner": "h2epr.environment.declarative.v4",
                    "environment_handler": f"declared:{vocabulary.first_intent}",
                    "lifecycle_id": "action_disposition",
                },
                {
                    "intent_id": vocabulary.second_intent,
                    "meaning": "Apply the closing synthetic transition.",
                    "eligible_actors": [vocabulary.second_actor],
                    "eligible_targets": [vocabulary.entity_id],
                    "payload_contract": "Exactly the declared target parameter.",
                    "authority_owner": "h2epr.environment.declarative.v4",
                    "environment_handler": f"declared:{vocabulary.second_intent}",
                    "lifecycle_id": "action_disposition",
                },
                {
                    "intent_id": "no_op",
                    "meaning": "Make no event-state change.",
                    "eligible_actors": active_ids,
                    "eligible_targets": active_ids,
                    "payload_contract": "Actor target and declared reason code.",
                    "authority_owner": "h2epr.environment.declarative.v4",
                    "environment_handler": "declared:no_op",
                    "lifecycle_id": "action_disposition",
                },
            ],
            "registry_sha256": SHA_PLACEHOLDER,
        },
        "registry_sha256",
    )
    lifecycle_registry = _sealed(
        {
            "schema_version": "h2epr.lifecycle-registry.v2",
            "registry_id": f"{prefix}.lifecycle-registry.v1",
            "registry_version": version,
            "event_id": vocabulary.event_id,
            "lifecycles": [
                {
                    "lifecycle_id": "action_disposition",
                    "initial_state": "submitted",
                    "terminal_states": ["accepted", "rejected"],
                    "transitions": [
                        {
                            "from": "submitted",
                            "to": "accepted",
                            "owner": "masim.AuthoritativeReducer",
                            "trigger": "intent admission passes",
                        },
                        {
                            "from": "submitted",
                            "to": "rejected",
                            "owner": "masim.AuthoritativeReducer",
                            "trigger": "intent admission fails",
                        },
                    ],
                },
                {
                    "lifecycle_id": "message_delivery",
                    "initial_state": "pending",
                    "terminal_states": [
                        "delivered",
                        "expired",
                        "rejected",
                        "duplicate",
                        "failed",
                    ],
                    "transitions": [
                        {
                            "from": "pending",
                            "to": state,
                            "owner": "masim.AppendOnlyTransport",
                            "trigger": f"transport reaches {state}",
                        }
                        for state in (
                            "delivered",
                            "expired",
                            "rejected",
                            "duplicate",
                            "failed",
                        )
                    ],
                },
            ],
            "registry_sha256": SHA_PLACEHOLDER,
        },
        "registry_sha256",
    )
    interface_id = f"{prefix}.participant-interface.v1"
    participant_interface = _sealed(
        {
            "schema_version": "h2epr.participant-interface.v2",
            "interface_id": interface_id,
            "interface_version": version,
            "event_id": vocabulary.event_id,
            "actor_map_id": actor_map_id,
            "actors": [
                {
                    "actor_id": vocabulary.first_actor,
                    "representation_kind": "agent",
                    "semantic_parent_id": first_parent_id,
                    "observation_ids": observation_ids,
                    "intent_ids": [vocabulary.first_intent, "no_op"],
                    "lifecycle_ids": lifecycle_ids,
                    "persistent_state_fields": [
                        f"entities.{vocabulary.entity_id}.status"
                    ],
                },
                {
                    "actor_id": vocabulary.second_actor,
                    "representation_kind": "population",
                    "semantic_parent_id": second_parent_id,
                    "observation_ids": observation_ids,
                    "intent_ids": [vocabulary.second_intent, "no_op"],
                    "lifecycle_ids": lifecycle_ids,
                    "persistent_state_fields": [
                        f"entities.{vocabulary.entity_id}.status"
                    ],
                },
            ],
            "interface_sha256": SHA_PLACEHOLDER,
        },
        "interface_sha256",
    )
    semantic_index = _sealed(
        {
            "schema_version": "h2epr.participant-semantic-index.v3",
            "index_id": f"{prefix}.participant-semantic-index.v1",
            "index_version": version,
            "event_id": vocabulary.event_id,
            "actor_map_id": actor_map_id,
            "parents": parent_rows,
            "index_sha256": SHA_PLACEHOLDER,
        },
        "index_sha256",
    )
    interface_root = project_root / "agents" / "interfaces" / vocabulary.slug
    interface_files = (
        ("observation-registry.json", observation_registry),
        ("intent-registry.json", intent_registry),
        ("lifecycle-registry.json", lifecycle_registry),
        ("participant-interface.json", participant_interface),
        ("participant-semantic-index.json", semantic_index),
    )
    for filename, value in interface_files:
        _write(interface_root / filename, value)
    interface_roles = (
        ("observation_registry", observation_registry["registry_id"], "observation-registry.json"),
        ("intent_registry", intent_registry["registry_id"], "intent-registry.json"),
        ("lifecycle_registry", lifecycle_registry["registry_id"], "lifecycle-registry.json"),
        ("participant_interface", interface_id, "participant-interface.json"),
        ("participant_semantic_index", semantic_index["index_id"], "participant-semantic-index.json"),
    )
    interface_manifest = _release(
        interface_root,
        event_id=vocabulary.event_id,
        release_id=f"{prefix}.participant-interface-release.v1",
        release_kind="participant_interfaces",
        artifacts=(
            _artifact(
                interface_root,
                artifact_id=artifact_id,
                artifact_version=version,
                role=role,
                relative_path=filename,
            )
            for role, artifact_id, filename in interface_roles
        ),
        semantic_parent_ids=(actor_map_id, first_parent_id, second_parent_id),
    )

    scenario_interface_id = f"{prefix}.scenario-interface.v1"
    mechanism_id = f"{prefix}.scenario-mechanism.v1"
    scenario_interface = _sealed(
        {
            "schema_version": "h2epr.scenario-interface.v2",
            "scenario_interface_id": scenario_interface_id,
            "scenario_interface_version": version,
            "event_id": vocabulary.event_id,
            "actor_ids": active_ids,
            "state_fields": [
                {
                    "field_id": "state_version",
                    "owner": "runtime",
                    "visibility": "public",
                    "update_authority": "runtime.environment.v4",
                    "value_domain": "integer; monotonically increasing",
                },
                {
                    "field_id": f"entities.{vocabulary.entity_id}.status",
                    "owner": vocabulary.entity_id,
                    "visibility": "public",
                    "update_authority": "runtime.environment.v4",
                    "value_domain": (
                        "string; allowed="
                        f"[{vocabulary.initial_value}, {vocabulary.intermediate_value}, "
                        f"{vocabulary.terminal_value}]"
                    ),
                },
            ],
            "observation_registry_id": observation_registry["registry_id"],
            "intent_registry_id": intent_registry["registry_id"],
            "lifecycle_registry_id": lifecycle_registry["registry_id"],
            "environment_implementation_id": "h2epr.environment.declarative.v4",
            "annotation_implementation_id": "h2epr.annotations.declarative.v3",
            "clock_contract": "Three ordered logical coordinates.",
            "route_contract": "Declared directed routes with positive tick latency.",
            "termination_contract": "All coordinates and transport complete; invariant holds.",
            "scenario_interface_sha256": SHA_PLACEHOLDER,
        },
        "scenario_interface_sha256",
    )
    target_domain = [
        {
            "parameter": "target_id",
            "value_type": "string",
            "allowed_values": [vocabulary.entity_id],
        }
    ]
    mechanism = _sealed(
        {
            "schema_version": "h2epr.scenario-mechanism.v4",
            "mechanism_id": mechanism_id,
            "mechanism_version": version,
            "event_id": vocabulary.event_id,
            "state_fields": [
                {
                    "entity_id": vocabulary.entity_id,
                    "field_name": "status",
                    "value_type": "string",
                    "allowed_values": [
                        vocabulary.initial_value,
                        vocabulary.intermediate_value,
                        vocabulary.terminal_value,
                    ],
                    "visibility": "public",
                    "update_authority": "runtime.environment.v4",
                }
            ],
            "intent_handlers": [
                {
                    "intent_id": vocabulary.first_intent,
                    "eligible_actors": [vocabulary.first_actor],
                    "eligible_targets": [vocabulary.entity_id],
                    "target_parameter": "target_id",
                    "parameter_domains": target_domain,
                    "preconditions": [
                        {
                            "entity_id": vocabulary.entity_id,
                            "field_name": "status",
                            "operator": "equals",
                            "value": vocabulary.initial_value,
                        }
                    ],
                    "effects": [
                        {
                            "operation": "set",
                            "entity_id": vocabulary.entity_id,
                            "field_name": "status",
                            "value": vocabulary.intermediate_value,
                            "delta_class": "synthetic_transition",
                        }
                    ],
                },
                {
                    "intent_id": vocabulary.second_intent,
                    "eligible_actors": [vocabulary.second_actor],
                    "eligible_targets": [vocabulary.entity_id],
                    "target_parameter": "target_id",
                    "parameter_domains": target_domain,
                    "preconditions": [
                        {
                            "entity_id": vocabulary.entity_id,
                            "field_name": "status",
                            "operator": "equals",
                            "value": vocabulary.intermediate_value,
                        }
                    ],
                    "effects": [
                        {
                            "operation": "set",
                            "entity_id": vocabulary.entity_id,
                            "field_name": "status",
                            "value": vocabulary.terminal_value,
                            "delta_class": "synthetic_transition",
                        }
                    ],
                },
                {
                    "intent_id": "no_op",
                    "eligible_actors": active_ids,
                    "eligible_targets": active_ids,
                    "target_parameter": "target_id",
                    "parameter_domains": [
                        {
                            "parameter": "target_id",
                            "value_type": "string",
                            "allowed_values": active_ids,
                        },
                        {
                            "parameter": "reason_code",
                            "value_type": "string",
                            "allowed_values": ["no_declared_rule_matched"],
                        },
                    ],
                    "preconditions": [],
                    "effects": [],
                },
            ],
            "message_kinds": [
                {
                    "message_kind": vocabulary.message_kind,
                    "eligible_senders": [vocabulary.first_actor],
                    "eligible_recipients": [vocabulary.second_actor],
                    "payload_contract": "A JSON object without state-write authority.",
                }
            ],
            "annotations": [
                {
                    "annotation_id": f"{prefix}.terminal",
                    "label": "Synthetic terminal state",
                    "when_all": [
                        {
                            "entity_id": vocabulary.entity_id,
                            "field_name": "status",
                            "operator": "equals",
                            "value": vocabulary.terminal_value,
                        }
                    ],
                    "participant_ids": active_ids,
                    "one_shot": True,
                }
            ],
            "conflict_policy": (
                "reject_distinct_concurrent_writes_allow_idempotent_same_value"
            ),
            "termination_invariants": [
                {
                    "entity_id": vocabulary.entity_id,
                    "field_name": "status",
                    "operator": "equals",
                    "value": vocabulary.terminal_value,
                }
            ],
            "mechanism_sha256": SHA_PLACEHOLDER,
        },
        "mechanism_sha256",
    )
    if mechanism_transform is not None:
        mechanism_transform(mechanism)
        _sealed(mechanism, "mechanism_sha256")
    scenario_root = project_root / "scenarios" / vocabulary.slug
    _write(scenario_root / "scenario-interface.json", scenario_interface)
    _write(scenario_root / "scenario-mechanism.json", mechanism)
    _write_text(
        scenario_root / "scenario-definition.md",
        "# Synthetic scenario definition\n\n"
        "The first actor opens one declared transition. A one-tick message "
        "enables the second actor to close it. The environment alone owns "
        "state mutation. This fixture has no historical interpretation.",
    )
    scenario_manifest = _release(
        scenario_root,
        event_id=vocabulary.event_id,
        release_id=f"{prefix}.scenario-definition-release.v1",
        release_kind="scenario_definition",
        artifacts=(
            _artifact(
                scenario_root,
                artifact_id=f"{prefix}.scenario-definition.v1",
                artifact_version=version,
                role="scenario_definition",
                relative_path="scenario-definition.md",
            ),
            _artifact(
                scenario_root,
                artifact_id=scenario_interface_id,
                artifact_version=version,
                role="scenario_interface",
                relative_path="scenario-interface.json",
            ),
            _artifact(
                scenario_root,
                artifact_id=mechanism_id,
                artifact_version=version,
                role="scenario_mechanism",
                relative_path="scenario-mechanism.json",
            ),
        ),
        semantic_parent_ids=(interface_id,),
    )

    shared_configuration_id = f"{prefix}.comparison.v1"
    timeline = [
        {
            "logical_tick": 1,
            "coordinate_id": f"{vocabulary.slug}.c01",
            "stage_id": "S1",
            "episode_id": "E1",
            "label": "opening transition",
            "source_time": "2000-01-01",
        },
        {
            "logical_tick": 2,
            "coordinate_id": f"{vocabulary.slug}.c02",
            "stage_id": "S1",
            "episode_id": "E2",
            "label": "closing transition",
            "source_time": "2000-01-02",
        },
        {
            "logical_tick": 3,
            "coordinate_id": f"{vocabulary.slug}.c03",
            "stage_id": "S1",
            "episode_id": "E2",
            "label": "terminal delivery barrier",
            "source_time": "post-transition",
        },
    ]
    shared_settings = {
        "purpose": "Exercise the event-neutral benchmark-simulation contract.",
        "exposure_mode": "full_draft_exposed",
        "active_actor_ids": active_ids,
        "timeline": timeline,
        "initial_state": {
            "state_version": 0,
            "entities": {
                vocabulary.entity_id: {"status": vocabulary.initial_value}
            },
        },
        "communication_routes": [
            {
                "route_id": (
                    f"route.{vocabulary.first_actor}.to.{vocabulary.second_actor}"
                ),
                "source_id": vocabulary.first_actor,
                "target_id": vocabulary.second_actor,
                "latency_ticks": 1,
            }
        ],
        "observation_contract": {
            "vocabulary_exposure": "declared_event_vocabulary",
            "schema_version": "h2epr.participant-observation.v3",
            "sealed_prestate_per_coordinate": True,
            "message_delivery_phase": "before_decision_collection",
            "same_coordinate_write_visibility": "forbidden",
        },
        "termination": {
            "require_all_ticks": True,
            "require_no_unresolved_messages": True,
        },
        "assumptions": [
            "Logical coordinates and one-tick latency are synthetic contract choices."
        ],
    }
    if shared_settings_transform is not None:
        shared_settings_transform(shared_settings)
    shared_configuration = _sealed(
        {
            "schema_version": "h2epr.scenario-configuration.v3",
            "configuration_id": shared_configuration_id,
            "configuration_version": version,
            "event_id": vocabulary.event_id,
            "configuration_kind": "shared_comparison",
            "semantic_parent_ids": [
                roster_id,
                actor_map_id,
                interface_id,
                scenario_interface_id,
                mechanism_id,
            ],
            "settings": shared_settings,
            "value_provenance": [
                {
                    "json_pointer": f"/settings/{key}",
                    "classification": "synthetic",
                    "basis": "Declared solely for the event-neutral contract fixture.",
                }
                for key in sorted(shared_settings)
            ],
            "configuration_sha256": SHA_PLACEHOLDER,
        },
        "configuration_sha256",
    )
    shared_admission = _derive_configuration_admission_receipt(
        configuration=shared_configuration,
        roster=roster,
        actor_map=actor_map,
        participant_interface=participant_interface,
        scenario_interface=scenario_interface,
        mechanism=mechanism,
        draft=(
            __import__("json").loads(
                (source_root / "draft_epg.json").read_text(encoding="utf-8")
            )
        ),
    )
    shared_coverage = _provenance_coverage(shared_configuration)
    shared_root = project_root / "configs" / vocabulary.slug / "shared"
    _write(shared_root / "scenario-configuration.json", shared_configuration)
    _write(shared_root / "admission-receipt.json", shared_admission)
    _write(shared_root / "provenance-coverage.json", shared_coverage)
    shared_manifest = _release(
        shared_root,
        event_id=vocabulary.event_id,
        release_id=f"{prefix}.scenario-configuration-release.v1",
        release_kind="scenario_configuration",
        artifacts=(
            _artifact(
                shared_root,
                artifact_id=shared_configuration_id,
                artifact_version=version,
                role="scenario_configuration",
                relative_path="scenario-configuration.json",
            ),
            _artifact(
                shared_root,
                artifact_id=shared_admission["receipt_id"],
                artifact_version=version,
                role="configuration_admission_receipt",
                relative_path="admission-receipt.json",
            ),
            _artifact(
                shared_root,
                artifact_id=shared_coverage["coverage_id"],
                artifact_version=version,
                role="configuration_provenance_coverage",
                relative_path="provenance-coverage.json",
            ),
        ),
        semantic_parent_ids=shared_configuration["semantic_parent_ids"],
    )

    rule_configuration_id = f"{prefix}.rule.v1"
    rule_settings = {
        "policy_id": f"{prefix}.rule-policy.v1",
        "deterministic": True,
        "model_access": "denied",
        "network_access": "denied",
        "default_action": "no_op",
        "decision_rules": [
            {
                "rule_id": f"{vocabulary.slug}.r01.open",
                "actor_id": vocabulary.first_actor,
                "coordinate_id": timeline[0]["coordinate_id"],
                "priority": 10,
                "guards": [],
                "action": {
                    "action_type": vocabulary.first_intent,
                    "parameters": {"target_id": vocabulary.entity_id},
                },
                "messages": [
                    {
                        "recipient_id": vocabulary.second_actor,
                        "message_type": vocabulary.message_kind,
                        "payload": {"status": vocabulary.intermediate_value},
                    }
                ],
                "reason": "The synthetic Draft exposes the opening action.",
            },
            {
                "rule_id": f"{vocabulary.slug}.r02.close",
                "actor_id": vocabulary.second_actor,
                "coordinate_id": timeline[1]["coordinate_id"],
                "priority": 10,
                "guards": [
                    {
                        "kind": "message_received",
                        "message_kind": vocabulary.message_kind,
                        "sender_id": vocabulary.first_actor,
                    }
                ],
                "action": {
                    "action_type": vocabulary.second_intent,
                    "parameters": {"target_id": vocabulary.entity_id},
                },
                "messages": [],
                "reason": "The delivered message enables the closing action.",
            },
        ],
    }
    if rule_settings_transform is not None:
        rule_settings_transform(rule_settings)
    rule_configuration = _sealed(
        {
            "schema_version": "h2epr.scenario-configuration.v3",
            "configuration_id": rule_configuration_id,
            "configuration_version": version,
            "event_id": vocabulary.event_id,
            "configuration_kind": "backend_rule",
            "semantic_parent_ids": [shared_configuration_id, interface_id],
            "settings": rule_settings,
            "value_provenance": [
                {
                    "json_pointer": f"/settings/{key}",
                    "classification": "synthetic",
                    "basis": "Declared solely for the event-neutral Rule fixture.",
                }
                for key in sorted(rule_settings)
            ],
            "configuration_sha256": SHA_PLACEHOLDER,
        },
        "configuration_sha256",
    )
    rule_admission = _derive_rule_configuration_admission_receipt(
        configuration=rule_configuration,
        shared_configuration=shared_configuration,
        participant_interface=participant_interface,
        mechanism=mechanism,
    )
    rule_coverage = _provenance_coverage(rule_configuration)
    rule_config_root = (
        project_root / "configs" / vocabulary.slug / "backends" / "rule"
    )
    _write(rule_config_root / "rule-configuration.json", rule_configuration)
    _write(rule_config_root / "admission-receipt.json", rule_admission)
    _write(rule_config_root / "provenance-coverage.json", rule_coverage)
    _release(
        rule_config_root,
        event_id=vocabulary.event_id,
        release_id=f"{prefix}.rule-configuration-release.v1",
        release_kind="scenario_configuration",
        artifacts=(
            _artifact(
                rule_config_root,
                artifact_id=rule_configuration_id,
                artifact_version=version,
                role="backend_configuration",
                relative_path="rule-configuration.json",
            ),
            _artifact(
                rule_config_root,
                artifact_id=rule_admission["receipt_id"],
                artifact_version=version,
                role="backend_configuration_admission_receipt",
                relative_path="admission-receipt.json",
            ),
            _artifact(
                rule_config_root,
                artifact_id=rule_coverage["coverage_id"],
                artifact_version=version,
                role="backend_configuration_provenance_coverage",
                relative_path="provenance-coverage.json",
            ),
        ),
        semantic_parent_ids=rule_configuration["semantic_parent_ids"],
    )

    implementation_sources = [
        {
            "relative_path": relative_path,
            "sha256": file_sha256(project_root / relative_path),
        }
        for relative_path in IMPLEMENTATION_PATHS
    ]
    realization_id = f"{prefix}.rule-realization.v1"
    realization = _sealed(
        {
            "schema_version": "h2epr.backend-realization.v2",
            "realization_id": realization_id,
            "realization_version": version,
            "event_id": vocabulary.event_id,
            "backend": "rule",
            "semantic_parent_ids": [
                actor_map_id,
                interface_id,
                scenario_interface_id,
                mechanism_id,
                shared_configuration_id,
                rule_configuration_id,
            ],
            "configuration_id": rule_configuration_id,
            "decision_interface": "h2epr.participant-decision.v2",
            "implementation_id": "h2epr.backend.rule.declarative.v4",
            "actor_realizations": [
                {
                    "actor_id": vocabulary.first_actor,
                    "semantic_parent_id": first_parent_id,
                    "implementation_entry": (
                        "h2epr.backends.rule.DeclarativeRuleBackend"
                    ),
                    "observation_ids": observation_ids,
                    "intent_ids": [vocabulary.first_intent, "no_op"],
                },
                {
                    "actor_id": vocabulary.second_actor,
                    "semantic_parent_id": second_parent_id,
                    "implementation_entry": (
                        "h2epr.backends.rule.DeclarativeRuleBackend"
                    ),
                    "observation_ids": observation_ids,
                    "intent_ids": [vocabulary.second_intent, "no_op"],
                },
            ],
            "failure_routing": {
                "invalid_contract": "fail package admission",
                "invalid_intent": "emit a typed rejected disposition",
                "transport_failure": "fail the run with terminal evidence",
                "backend_substitution": "forbidden",
            },
            "implementation_sources": implementation_sources,
            "realization_sha256": SHA_PLACEHOLDER,
        },
        "realization_sha256",
    )
    realization_root = project_root / "execution" / vocabulary.slug / "rule"
    _write(realization_root / "realization.json", realization)
    relative_configuration = os.path.relpath(
        rule_config_root / "rule-configuration.json", realization_root
    )
    relative_admission = os.path.relpath(
        rule_config_root / "admission-receipt.json", realization_root
    )
    relative_coverage = os.path.relpath(
        rule_config_root / "provenance-coverage.json", realization_root
    )
    realization_manifest = _release(
        realization_root,
        event_id=vocabulary.event_id,
        release_id=f"{prefix}.rule-realization-release.v1",
        release_kind="backend_realization",
        artifacts=(
            _artifact(
                realization_root,
                artifact_id=realization_id,
                artifact_version=version,
                role="backend_realization",
                relative_path="realization.json",
            ),
            _artifact(
                realization_root,
                artifact_id=rule_configuration_id,
                artifact_version=version,
                role="backend_configuration",
                relative_path=relative_configuration,
            ),
            _artifact(
                realization_root,
                artifact_id=rule_admission["receipt_id"],
                artifact_version=version,
                role="backend_configuration_admission_receipt",
                relative_path=relative_admission,
            ),
            _artifact(
                realization_root,
                artifact_id=rule_coverage["coverage_id"],
                artifact_version=version,
                role="backend_configuration_provenance_coverage",
                relative_path=relative_coverage,
            ),
        ),
        semantic_parent_ids=realization["semantic_parent_ids"],
    )

    def declaration(root: Path, manifest: Mapping[str, Any]) -> dict[str, str]:
        return {
            "release_id": manifest["release_id"],
            "release_root": root.relative_to(project_root).as_posix(),
            "manifest_sha256": manifest["manifest_sha256"],
        }

    assembly: dict[str, Any] = {
        "schema_version": "h2epr.event-package-assembly.v4",
        "assembly_id": f"{prefix}.assembly.v1",
        "assembly_version": version,
        "event_id": vocabulary.event_id,
        "package_id": f"h2epr.event-package.synthetic.{code}.v1",
        "package_version": version,
        "compiler_id": "h2epr.semantic-package-compiler.v4",
        "source_profile": {
            "artifact_id": source_profile["profile_id"],
            "relative_path": source_profile_path.relative_to(project_root).as_posix(),
            "artifact_sha256": source_profile["profile_sha256"],
        },
        "semantic_releases": {
            "roster": declaration(roster_root, roster_manifest),
            "participant_interfaces": declaration(
                interface_root, interface_manifest
            ),
            "scenario_definition": declaration(
                scenario_root, scenario_manifest
            ),
            "scenario_configuration": declaration(
                shared_root, shared_manifest
            ),
        },
        "backend_releases": {
            "rule": {
                "status": "implemented",
                **declaration(realization_root, realization_manifest),
            },
            "llm": {"status": "planned"},
            "rulellm": {"status": "planned"},
        },
        "semantic_assembly_sha256": SHA_PLACEHOLDER,
        "backend_catalog_sha256": SHA_PLACEHOLDER,
        "assembly_sha256": SHA_PLACEHOLDER,
    }
    assembly["semantic_assembly_sha256"] = semantic_assembly_sha256(assembly)
    assembly["backend_catalog_sha256"] = backend_catalog_sha256(assembly)
    assembly["assembly_sha256"] = assembly_sha256(assembly)
    assembly_path = project_root / "events" / vocabulary.slug / "package-assembly.json"
    _write(assembly_path, assembly)
    package_root = project_root / "events" / vocabulary.slug / "package"
    compile_event_package(
        project_root=project_root,
        data_root=data_root,
        assembly_path=assembly_path,
        output_root=package_root,
    )
    return SyntheticEvent(
        event_id=vocabulary.event_id,
        slug=vocabulary.slug,
        title=vocabulary.title,
        project_root=project_root,
        data_root=data_root,
        assembly_path=assembly_path,
        package_root=package_root,
    )


__all__ = [
    "DISPATCH_CASE",
    "SIGNAL_CASE",
    "SyntheticEvent",
    "SyntheticVocabulary",
    "build_synthetic_event",
]
