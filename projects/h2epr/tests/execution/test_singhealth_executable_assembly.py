from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from masim.integrations.event_process import ActionIntent, canonical_sha256

from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.assembly import (
    PACKAGE_ID,
    PACKAGE_VERSION,
    RUNTIME_BUNDLE_ID,
    RUNTIME_BUNDLE_VERSION,
    build_singhealth_executable_package_document,
    build_singhealth_runtime_bundle_document,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.components import (
    COMPONENTS_BY_ID,
    COMPONENTS_BY_ROLE,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1.runtime_components import (
    SingHealthEnvironment,
    SingHealthObservationProjector,
    SingHealthRuntimeComponentError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _bundle() -> dict:
    return build_singhealth_runtime_bundle_document(project_root=PROJECT_ROOT)


def test_runtime_bundle_is_deterministic_and_closes_full_roster() -> None:
    first = _bundle()
    second = _bundle()

    assert first == second
    assert canonical_sha256(first) == canonical_sha256(second)
    assert first["runtime_bundle_id"] == RUNTIME_BUNDLE_ID
    assert first["version"] == RUNTIME_BUNDLE_VERSION
    assert len(first["actor_registry"]) == 13
    assert len(first["carrier_projections"]) == 13
    assert sum(
        len(row["capability_projections"])
        for row in first["carrier_projections"]
    ) == 13
    assert len(first["participant_artifacts"]) == 9
    assert len(first["action_registry"]) == 74
    assert len(first["observation_rules"]) == 41
    assert len(first["communication_routes"]) == 46
    assert len(first["initial_state"]["route_records"]) == 8
    assert len(first["lifecycle_registry"]) == 11
    assert len(first["component_registry"]) == 9
    assert len(first["clock"]["logical_ticks"]) == 50


def test_population_carriers_keep_unit_scope_and_state_separate() -> None:
    bundle = _bundle()
    carriers = {
        row["actor_id"]: row for row in bundle["carrier_projections"]
    }
    security = carriers[
        "actor.0616.unit.technical.security-engineering"
    ]
    database = carriers[
        "actor.0616.unit.technical.scm-application-database"
    ]

    assert security["assignment_id"] != database["assignment_id"]
    assert security["capacity_ids"] != database["capacity_ids"]
    assert security["access_scope_ids"] != database["access_scope_ids"]
    assert security["capability_projections"][0][
        "participant_policy_implementation_id"
    ] == database["capability_projections"][0][
        "participant_policy_implementation_id"
    ]
    assert security["capability_projections"][0][
        "initial_private_state"
    ] is not database["capability_projections"][0]["initial_private_state"]

    sirm = carriers["actor.0616.office.sirm"]
    assert sirm["effective_scope_record_ids"] == [
        "opening.0616.authority.sirm"
    ]
    assert sirm["capability_projections"][0][
        "initial_private_state_sources"
    ]["state.security_incident_response_manager.coverage_assessment"] == (
        "opening.0616.authority.sirm"
    )


def test_action_observation_route_and_lifecycle_references_close() -> None:
    bundle = _bundle()
    actors = {row["actor_id"] for row in bundle["actor_registry"]}
    routes = {row["route_id"] for row in bundle["communication_routes"]}
    lifecycles = {
        row["lifecycle_id"] for row in bundle["lifecycle_registry"]
    }
    actions = {
        (row["actor_id"], row["intent_id"])
        for row in bundle["action_registry"]
    }

    assert len(actions) == 74
    assert all(row["actor_id"] in actors for row in bundle["action_registry"])
    assert all(
        row["result_route_id"] in routes
        and (
            row["direct_route_id"] is None
            or row["direct_route_id"] in routes
        )
        for row in bundle["action_registry"]
    )
    assert {
        row["primary_lifecycle_id"]
        for row in bundle["observation_rules"]
    } == lifecycles
    tick_rows = {
        row["logical_tick"]: row for row in bundle["clock"]["logical_ticks"]
    }
    assert all(
        tick_rows[row["evaluation_tick"]]["phase_id"]
        == "participant_decision_and_issue"
        and set(row["observation_values"]) == set(row["observation_ids"])
        and row["primary_lifecycle_id"] in row["lifecycle_ids"]
        and row["expected_outcome"]["intent_id"] is not None
        for row in bundle["observation_rules"]
    )
    assert {
        policy_id
        for row in bundle["action_registry"]
        for policy_id in row["scenario_policy_ids"]
    } == {
        row["policy_id"]
        for row in bundle["policy_registry"]["scenario_policies"]
    }


def test_component_registry_resolves_and_controls_all_scenario_policies() -> None:
    bundle = _bundle()

    assert set(COMPONENTS_BY_ROLE) == {
        "policy_registry",
        "scheduler",
        "observation_projector",
        "participant_executor",
        "message_transport",
        "environment",
        "reducer",
        "trace",
        "compiler",
    }
    assert len(COMPONENTS_BY_ID) == 9
    assert all(
        component.implementation is not None
        for component in COMPONENTS_BY_ROLE.values()
    )
    checks = SingHealthEnvironment(bundle).scenario_policy_checks()
    assert len(checks) == 9
    assert {row["status"] for row in checks} == {"pass"}
    assert {row["policy_id"] for row in checks} == {
        row["policy_id"]
        for row in bundle["policy_registry"]["scenario_policies"]
    }


def test_executable_package_binds_exact_bundle_and_read_only_masim() -> None:
    bundle = _bundle()
    bundle_hash = canonical_sha256(bundle)
    package = build_singhealth_executable_package_document(
        project_root=PROJECT_ROOT,
        runtime_bundle_source_sha256=bundle_hash,
        runtime_bundle_canonical_sha256=bundle_hash,
    )

    assert package["package_id"] == PACKAGE_ID
    assert package["version"] == PACKAGE_VERSION
    assert package["runtime_bundle"]["runtime_bundle_id"] == RUNTIME_BUNDLE_ID
    assert package["runtime_bundle"]["canonical_sha256"] == bundle_hash
    assert len(package["actor_bindings"]) == 13
    assert set(package["component_bindings"]) == set(COMPONENTS_BY_ROLE)
    assert package["masim_usage"]["source_modification_allowed"] is False


def test_runtime_components_fail_closed_on_unknown_or_forged_scope() -> None:
    bundle = _bundle()
    projector = SingHealthObservationProjector(bundle)
    with pytest.raises(
        SingHealthRuntimeComponentError,
        match="singhealth_runtime_projection_scope_unresolved",
    ):
        projector.project(
            actor_id="actor.0616.unknown",
            capability_id="unknown",
            commitment_id="unknown",
            logical_tick=0,
            state=bundle["initial_state"],
        )

    environment = SingHealthEnvironment(bundle)
    rule = bundle["observation_rules"][0]
    valid = ActionIntent(
        intent_id="intent.0616.test",
        run_id="run.0616.test",
        actor_id=rule["actor_id"],
        logical_tick=rule["evaluation_tick"],
        prestate_version=0,
        prestate_sha256=canonical_sha256(bundle["initial_state"]),
        action_type=rule["expected_outcome"]["intent_id"],
        parameters={
            "capability_id": rule["capability_id"],
            "commitment_id": rule["commitment_id"],
            "branch_id": rule["expected_outcome"]["branch_id"],
            "lifecycle_ids": rule["lifecycle_ids"],
            "primary_lifecycle_id": rule["primary_lifecycle_id"],
            "private_state_updates": rule["expected_private_state_updates"],
        },
        policy_id=(
            f"h2epr.policy.0616.participant.{rule['capability_id']}"
        ),
    )
    assert environment.action_binding(valid)["actor_id"] == rule["actor_id"]

    forged_parameters = {
        **dict(valid.parameters),
        "branch_id": "branch.0616.forged",
    }
    forged = ActionIntent(
        intent_id=valid.intent_id,
        run_id=valid.run_id,
        actor_id=valid.actor_id,
        logical_tick=valid.logical_tick,
        prestate_version=valid.prestate_version,
        prestate_sha256=valid.prestate_sha256,
        action_type=valid.action_type,
        parameters=forged_parameters,
        policy_id=valid.policy_id,
    )
    with pytest.raises(
        SingHealthRuntimeComponentError,
        match="singhealth_runtime_action_binding_mismatch",
    ):
        environment.action_binding(forged)

    state = deepcopy(bundle["initial_state"])
    state["actors"][valid.actor_id]["capacity_ids"] = []
    with pytest.raises(
        SingHealthRuntimeComponentError,
        match="singhealth_runtime_authority_rejected",
    ):
        environment.admit_action(valid, state)
