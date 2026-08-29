from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from masim.integrations.event_process import (
    ActionDisposition,
    ActionIntent,
    canonical_sha256,
)

from h2epr.scenarios.panic_1907.full_roster_v0_1.assembly import (
    PACKAGE_ID,
    PACKAGE_VERSION,
    RUNTIME_BUNDLE_ID,
    RUNTIME_BUNDLE_VERSION,
    build_panic_executable_package_document,
    build_panic_runtime_bundle_document,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.components import (
    COMPONENTS_BY_ID,
    COMPONENTS_BY_ROLE,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.runtime_components import (
    PanicEnvironment,
    PanicObservationProjector,
    PanicRuntimeComponentError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _bundle() -> dict:
    return build_panic_runtime_bundle_document(project_root=PROJECT_ROOT)


def test_runtime_bundle_is_deterministic_and_closes_full_roster() -> None:
    first = _bundle()
    second = _bundle()

    assert first == second
    assert canonical_sha256(first) == canonical_sha256(second)
    assert first["runtime_bundle_id"] == RUNTIME_BUNDLE_ID
    assert first["version"] == RUNTIME_BUNDLE_VERSION
    assert len(first["actor_registry"]) == 16
    assert len(first["carrier_projections"]) == 16
    assert sum(
        len(row["capability_projections"])
        for row in first["carrier_projections"]
    ) == 17
    assert len(first["participant_artifacts"]) == 12
    assert len(first["action_registry"]) == 127
    assert len(first["observation_rules"]) == 88
    assert len(first["communication_routes"]) == 35
    assert len(first["lifecycle_registry"]) == 13
    assert len(first["component_registry"]) == 9


def test_carriers_keep_actor_state_and_configuration_separate() -> None:
    bundle = _bundle()
    carriers = {
        row["actor_id"]: row for row in bundle["carrier_projections"]
    }

    member = carriers["actor.member_bank_alpha"]
    assert {
        row["capability_id"] for row in member["capability_projections"]
    } == {"bank_resource_decision", "call_money_lender"}
    need = carriers["actor.depositor.knickerbocker.need"][
        "capability_projections"
    ][0]
    signal = carriers["actor.depositor.knickerbocker.signal"][
        "capability_projections"
    ][0]
    assert need["configuration_parameters"]["response_profile"] == "need_only"
    assert (
        signal["configuration_parameters"]["response_profile"]
        == "signal_responsive"
    )
    assert (
        need["initial_private_state"][
            "state.knickerbocker_depositor.withdrawal_need"
        ]
        == "none"
    )
    assert need["configuration_parameters"] is not signal[
        "configuration_parameters"
    ]


def test_action_and_observation_references_are_closed() -> None:
    bundle = _bundle()
    actors = {row["actor_id"] for row in bundle["actor_registry"]}
    routes = {row["route_id"] for row in bundle["communication_routes"]}
    actions = {
        (row["actor_id"], row["intent_id"])
        for row in bundle["action_registry"]
    }
    assert len(actions) == 127
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
        if row["expected_outcome"]["intent_id"] is not None
    } == {row["lifecycle_id"] for row in bundle["lifecycle_registry"]}
    assert all(
        set(row["observation_values"]) == set(row["observation_ids"])
        and row["primary_lifecycle_id"] in row["lifecycle_ids"]
        for row in bundle["observation_rules"]
    )

    depositor_actions = {
        (row["capability_id"], row["intent_id"].rsplit(".", 1)[-1]): row
        for row in bundle["action_registry"]
        if row["capability_id"]
        in {"knickerbocker_depositor", "later_trust_depositor"}
    }
    for capability_id in {
        "knickerbocker_depositor",
        "later_trust_depositor",
    }:
        withdrawal = depositor_actions[(capability_id, "request_withdrawal")]
        waiting = depositor_actions[(capability_id, "await_request_result")]
        assert withdrawal["direct_recipient_actor_id"] is not None
        assert {"POL-AMOUNT-01", "POL-SERVICE-01"} <= set(
            withdrawal["scenario_policy_ids"]
        )
        assert waiting["direct_recipient_actor_id"] is None
        assert "POL-SERVICE-01" not in waiting["scenario_policy_ids"]
        assert "POL-AMOUNT-01" not in waiting["scenario_policy_ids"]

    assert {
        policy_id
        for row in bundle["action_registry"]
        for policy_id in row["scenario_policy_ids"]
    } == {
        row["policy_id"]
        for row in bundle["policy_registry"]["scenario_policies"]
    }


def test_component_registry_resolves_real_objects_and_all_scenario_policies() -> None:
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
    checks = PanicEnvironment(bundle).scenario_policy_checks()
    assert len(checks) == 9
    assert {row["status"] for row in checks} == {"pass"}
    assert {row["policy_id"] for row in checks} == {
        row["policy_id"]
        for row in bundle["policy_registry"]["scenario_policies"]
    }


def test_executable_package_binds_the_exact_bundle_and_components() -> None:
    bundle = _bundle()
    bundle_hash = canonical_sha256(bundle)
    package = build_panic_executable_package_document(
        project_root=PROJECT_ROOT,
        runtime_bundle_source_sha256=bundle_hash,
        runtime_bundle_canonical_sha256=bundle_hash,
    )

    assert package["package_id"] == PACKAGE_ID
    assert package["version"] == PACKAGE_VERSION
    assert package["runtime_bundle"]["runtime_bundle_id"] == RUNTIME_BUNDLE_ID
    assert package["runtime_bundle"]["canonical_sha256"] == bundle_hash
    assert len(package["actor_bindings"]) == 16
    assert set(package["component_bindings"]) == set(COMPONENTS_BY_ROLE)
    assert package["masim_usage"]["source_modification_allowed"] is False


def test_runtime_components_fail_closed_on_unknown_scope_or_action() -> None:
    bundle = _bundle()
    projector = PanicObservationProjector(bundle)
    with pytest.raises(
        PanicRuntimeComponentError, match="runtime_projection_scope_unresolved"
    ):
        projector.project(
            actor_id="actor.unknown",
            capability_id="unknown",
            commitment_id="unknown",
            logical_tick=0,
            state=bundle["initial_state"],
        )

    environment = PanicEnvironment(bundle)
    unknown = ActionIntent(
        intent_id="intent.unknown",
        run_id="run.unknown",
        actor_id="actor.knickerbocker_trust",
        logical_tick=0,
        prestate_version=0,
        prestate_sha256=canonical_sha256(bundle["initial_state"]),
        action_type="h2epr.action.0288.unknown",
        parameters={
            "capability_id": "knickerbocker_trust",
            "commitment_id": "unknown",
            "branch_id": "unknown",
            "lifecycle_ids": [],
            "primary_lifecycle_id": "unknown",
            "private_state_updates": {},
        },
        policy_id="h2epr.policy.0288.participant.knickerbocker_trust",
    )
    with pytest.raises(
        PanicRuntimeComponentError, match="runtime_action_not_registered"
    ):
        environment.action_binding(unknown)

    rule = next(
        row
        for row in bundle["observation_rules"]
        if row["expected_outcome"]["intent_id"] is not None
    )
    row = next(
        action
        for action in bundle["action_registry"]
        if action["actor_id"] == rule["actor_id"]
        and action["intent_id"] == rule["expected_outcome"]["intent_id"]
    )
    valid_parameters = {
        "capability_id": rule["capability_id"],
        "commitment_id": rule["commitment_id"],
        "branch_id": rule["expected_outcome"]["branch_id"],
        "lifecycle_ids": rule["lifecycle_ids"],
        "primary_lifecycle_id": rule["primary_lifecycle_id"],
        "private_state_updates": rule["expected_private_state_updates"],
    }
    forged_cases = (
        (
            rule["evaluation_tick"],
            {**valid_parameters, "branch_id": "branch.forged"},
        ),
        (
            rule["evaluation_tick"] + 1,
            valid_parameters,
        ),
        (
            rule["evaluation_tick"],
            {**valid_parameters, "primary_lifecycle_id": "lifecycle.forged"},
        ),
        (
            rule["evaluation_tick"],
            {
                **valid_parameters,
                "private_state_updates": {"state.forged": "forged"},
            },
        ),
        (
            rule["evaluation_tick"],
            {**valid_parameters, "unexpected_parameter": True},
        ),
    )
    for case_index, (logical_tick, parameters) in enumerate(forged_cases):
        forged = ActionIntent(
            intent_id=f"intent.forged.{case_index}",
            run_id="run.bound",
            actor_id=row["actor_id"],
            logical_tick=logical_tick,
            prestate_version=0,
            prestate_sha256=canonical_sha256(bundle["initial_state"]),
            action_type=row["intent_id"],
            parameters=parameters,
            policy_id=row["participant_policy_implementation_id"],
        )
        with pytest.raises(
            PanicRuntimeComponentError,
            match="runtime_action_(binding|parameter_set)_mismatch",
        ):
            environment.action_binding(forged)

    mutated = deepcopy(bundle)
    mutated["communication_routes"] = [
        route
        for route in mutated["communication_routes"]
        if route["route_id"] != row["result_route_id"]
    ]
    with pytest.raises(
        PanicRuntimeComponentError, match="runtime_message_route_unresolved"
    ):
        intent = ActionIntent(
            intent_id="intent.bound",
            run_id="run.bound",
            actor_id=row["actor_id"],
            logical_tick=rule["evaluation_tick"],
            prestate_version=0,
            prestate_sha256=canonical_sha256(bundle["initial_state"]),
            action_type=row["intent_id"],
            parameters=valid_parameters,
            policy_id=row["participant_policy_implementation_id"],
        )
        PanicEnvironment(mutated).messages_for(
            intent,
            ActionDisposition(
                "ad.intent.bound",
                "intent.bound",
                0,
                "accepted",
                "accepted",
            ),
        )
