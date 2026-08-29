"""Runtime components for the Panic of 1907 full-roster Rule package.

The components in this module operate only on the closed runtime bundle. They
do not discover Markdown, import implementations named by input documents, or
infer participant authority from an action label.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timedelta
from typing import Any, Mapping, Sequence

from masim.integrations.event_process import (
    ActionDisposition,
    ActionIntent,
    MessageIntent,
    StateDelta,
    canonical_sha256,
    validate_trace,
)

from .lifecycle_rules import LIFECYCLE_RULES_BY_ID
from .participant import ParticipantDecision, ParticipantDecisionContext
from .registry import participant_policy
from .scenario_rules import (
    AMOUNT_POLICY,
    FACILITY_POLICY,
    INFORMATION_POLICY,
    LIFECYCLE_POLICY,
    RESULT_POLICY,
    REVIEW_POLICY,
    SERVICE_POLICY,
    TIME_POLICY,
    VENUE_POLICY,
    EventWindow,
    InformationProduct,
    ServiceRequest,
    VenueProcess,
)


ENVIRONMENT_ACTOR_ID = "environment.panic_1907"


class PanicRuntimeComponentError(ValueError):
    """A closed runtime value or component invocation is invalid."""


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {
            item.name: _plain(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _short_identity(prefix: str, value: Mapping[str, Any]) -> str:
    return f"{prefix}.{canonical_sha256(value)[:20]}"


@dataclass(frozen=True)
class ProjectedDecision:
    """One admitted participant decision and its optional MASim action."""

    decision: ParticipantDecision
    action_intent: ActionIntent | None


class PanicObservationProjector:
    """Build exact decision contexts from a sealed prestate and bundle rule."""

    implementation_id = "h2epr.component.0288.observation-projector"
    implementation_version = "0.1.0"

    def __init__(self, runtime_bundle: Mapping[str, Any]) -> None:
        rows = tuple(runtime_bundle.get("observation_rules", ()))
        carriers = tuple(runtime_bundle.get("carrier_projections", ()))
        self._rules = {
            (
                row["actor_id"],
                row["capability_id"],
                row["commitment_id"],
            ): copy.deepcopy(dict(row))
            for row in rows
        }
        carrier_rows = tuple(
            {
                "actor_id": carrier["actor_id"],
                **copy.deepcopy(dict(capability)),
            }
            for carrier in carriers
            for capability in carrier["capability_projections"]
        )
        self._carriers = {
            (row["actor_id"], row["capability_id"]): row
            for row in carrier_rows
        }
        if len(self._rules) != len(rows) or len(self._carriers) != len(carrier_rows):
            raise PanicRuntimeComponentError("runtime_projection_identity_duplicate")

    def due_rules(self, logical_tick: int) -> tuple[dict[str, Any], ...]:
        """Return the decision rules scheduled at one logical coordinate."""

        if type(logical_tick) is not int or logical_tick < 0:
            raise PanicRuntimeComponentError("runtime_projection_tick_invalid")
        return tuple(
            copy.deepcopy(row)
            for row in sorted(
                self._rules.values(),
                key=lambda item: (
                    item["evaluation_tick"],
                    item["actor_id"],
                    item["capability_id"],
                    item["commitment_id"],
                ),
            )
            if row["evaluation_tick"] == logical_tick
        )

    def project(
        self,
        *,
        actor_id: str,
        capability_id: str,
        commitment_id: str,
        logical_tick: int,
        state: Mapping[str, Any],
    ) -> ParticipantDecisionContext:
        """Project only the fields declared by one admitted commitment."""

        key = (actor_id, capability_id, commitment_id)
        try:
            rule = self._rules[key]
            carrier = self._carriers[(actor_id, capability_id)]
            actor_state = state["actors"][actor_id]
        except (KeyError, TypeError) as exc:
            raise PanicRuntimeComponentError(
                "runtime_projection_scope_unresolved"
            ) from exc
        if rule["evaluation_tick"] != logical_tick:
            raise PanicRuntimeComponentError("runtime_projection_not_due")
        private_state_ids = tuple(rule["private_state_ids"])
        try:
            private_state = {
                state_id: actor_state[state_id]
                for state_id in private_state_ids
            }
        except KeyError as exc:
            raise PanicRuntimeComponentError(
                "runtime_projection_private_state_missing"
            ) from exc
        observations = copy.deepcopy(rule["observation_values"])
        configuration = copy.deepcopy(carrier["configuration_parameters"])
        if (
            set(observations) != set(rule["observation_ids"])
            or set(private_state) != set(private_state_ids)
            or set(configuration) != set(rule["configuration_parameter_ids"])
        ):
            raise PanicRuntimeComponentError("runtime_projection_field_scope_mismatch")
        return ParticipantDecisionContext(
            actor_id=actor_id,
            capability_id=capability_id,
            commitment_id=commitment_id,
            observations=observations,
            private_state=private_state,
            configuration_parameters=configuration,
        )


class PanicParticipantExecutor:
    """Evaluate admitted participant policies without authoring results."""

    implementation_id = "h2epr.component.0288.participant-executor"
    implementation_version = "0.1.0"

    def evaluate(
        self,
        context: ParticipantDecisionContext,
        *,
        run_id: str,
        logical_tick: int,
        prestate_version: int,
        prestate_sha256: str,
        primary_lifecycle_id: str,
    ) -> ProjectedDecision:
        policy = participant_policy(
            f"h2epr.policy.0288.participant.{context.capability_id}"
        )
        decision = policy.decide(context)
        if primary_lifecycle_id not in decision.lifecycle_ids:
            raise PanicRuntimeComponentError(
                "runtime_primary_lifecycle_outside_decision"
            )
        if decision.intent_id is None:
            return ProjectedDecision(decision=decision, action_intent=None)
        identity = {
            "run_id": run_id,
            "logical_tick": logical_tick,
            "actor_id": context.actor_id,
            "capability_id": context.capability_id,
            "commitment_id": context.commitment_id,
        }
        intent = ActionIntent(
            intent_id=_short_identity("intent.0288", identity),
            run_id=run_id,
            actor_id=context.actor_id,
            logical_tick=logical_tick,
            prestate_version=prestate_version,
            prestate_sha256=prestate_sha256,
            action_type=decision.intent_id,
            parameters={
                "capability_id": decision.capability_id,
                "commitment_id": decision.commitment_id,
                "branch_id": decision.branch_id,
                "lifecycle_ids": list(decision.lifecycle_ids),
                "primary_lifecycle_id": primary_lifecycle_id,
                "private_state_updates": dict(
                    decision.proposed_private_state_updates
                ),
            },
            policy_id=policy.implementation_id,
        )
        return ProjectedDecision(decision=decision, action_intent=intent)


class PanicEnvironment:
    """Adjudicate registered actions and author later-delivered results."""

    implementation_id = "h2epr.component.0288.environment"
    implementation_version = "0.1.0"

    def __init__(self, runtime_bundle: Mapping[str, Any]) -> None:
        action_rows = tuple(runtime_bundle.get("action_registry", ()))
        route_rows = tuple(runtime_bundle.get("communication_routes", ()))
        decision_rows = tuple(runtime_bundle.get("observation_rules", ()))
        self._actions = {
            (row["actor_id"], row["intent_id"]): copy.deepcopy(dict(row))
            for row in action_rows
        }
        self._routes = {
            row["route_id"]: copy.deepcopy(dict(row)) for row in route_rows
        }
        self._decisions = {
            (
                row["actor_id"],
                row["capability_id"],
                row["commitment_id"],
            ): copy.deepcopy(dict(row))
            for row in decision_rows
        }
        self._actor_registry = tuple(
            copy.deepcopy(dict(row))
            for row in runtime_bundle.get("actor_registry", ())
        )
        initial_state = runtime_bundle.get("initial_state", {})
        self._resource_records = tuple(
            copy.deepcopy(dict(row))
            for row in initial_state.get("resource_and_condition_records", ())
        )
        self._relationship_records = tuple(
            copy.deepcopy(dict(row))
            for row in initial_state.get("relationship_records", ())
        )
        if (
            len(self._actions) != len(action_rows)
            or len(self._routes) != len(route_rows)
            or len(self._decisions) != len(decision_rows)
        ):
            raise PanicRuntimeComponentError("runtime_environment_identity_duplicate")

    def action_binding(self, intent: ActionIntent) -> dict[str, Any]:
        try:
            row = self._actions[(intent.actor_id, intent.action_type)]
        except KeyError as exc:
            raise PanicRuntimeComponentError("runtime_action_not_registered") from exc
        parameters = intent.parameters
        required_parameter_ids = {
            "capability_id",
            "commitment_id",
            "branch_id",
            "lifecycle_ids",
            "primary_lifecycle_id",
            "private_state_updates",
        }
        if set(parameters) != required_parameter_ids:
            raise PanicRuntimeComponentError("runtime_action_parameter_set_mismatch")
        decision_key = (
            intent.actor_id,
            parameters["capability_id"],
            parameters["commitment_id"],
        )
        try:
            decision = self._decisions[decision_key]
        except KeyError as exc:
            raise PanicRuntimeComponentError(
                "runtime_action_decision_scope_unresolved"
            ) from exc
        if (
            parameters.get("capability_id") != row["capability_id"]
            or parameters.get("commitment_id") not in row["commitment_ids"]
            or intent.policy_id != row["participant_policy_implementation_id"]
            or intent.logical_tick != decision["evaluation_tick"]
            or intent.action_type != decision["expected_outcome"]["intent_id"]
            or parameters.get("branch_id")
            != decision["expected_outcome"]["branch_id"]
            or list(parameters.get("lifecycle_ids", ()))
            != decision["lifecycle_ids"]
            or parameters.get("primary_lifecycle_id")
            != decision["primary_lifecycle_id"]
            or dict(parameters.get("private_state_updates", {}))
            != decision["expected_private_state_updates"]
        ):
            raise PanicRuntimeComponentError("runtime_action_binding_mismatch")
        return copy.deepcopy(row)

    def messages_for(
        self,
        intent: ActionIntent,
        disposition: ActionDisposition,
    ) -> tuple[MessageIntent, ...]:
        """Create an environment result and any declared directed notice."""

        row = self.action_binding(intent)
        if disposition.status != "accepted":
            return ()
        result = RESULT_POLICY.record(
            action_intent_id=intent.intent_id,
            action_admission="accepted",
            business_disposition_id=_short_identity(
                "disposition.0288", {"intent_id": intent.intent_id}
            ),
            business_disposition="accepted",
            execution_result=(
                "realized" if disposition.state_delta_ids else "no_effect"
            ),
            reason_code=disposition.reason_code,
        )
        messages: list[MessageIntent] = []
        result_route = row["result_route_id"]
        self._require_route(result_route, ENVIRONMENT_ACTOR_ID, intent.actor_id)
        messages.append(
            MessageIntent(
                message_intent_id=_short_identity(
                    "message.0288.result", {"intent_id": intent.intent_id}
                ),
                run_id=intent.run_id,
                source_action_intent_id=intent.intent_id,
                sender_id=ENVIRONMENT_ACTOR_ID,
                recipient_id=intent.actor_id,
                route_id=result_route,
                logical_tick=intent.logical_tick,
                latency_ticks=1,
                message_kind="typed_action_result",
                payload=_plain(result),
            )
        )
        recipient = row["direct_recipient_actor_id"]
        if recipient is not None:
            route_id = row["direct_route_id"]
            self._require_route(route_id, intent.actor_id, recipient)
            messages.append(
                MessageIntent(
                    message_intent_id=_short_identity(
                        "message.0288.notice",
                        {
                            "intent_id": intent.intent_id,
                            "recipient_id": recipient,
                        },
                    ),
                    run_id=intent.run_id,
                    source_action_intent_id=intent.intent_id,
                    sender_id=intent.actor_id,
                    recipient_id=recipient,
                    route_id=route_id,
                    logical_tick=intent.logical_tick,
                    latency_ticks=1,
                    message_kind="declared_participant_communication",
                    payload={
                        "semantic_intent_id": intent.action_type,
                        "commitment_id": intent.parameters["commitment_id"],
                    },
                )
            )
        return tuple(messages)

    def policy_applications(
        self,
        intent: ActionIntent,
        disposition: ActionDisposition,
        *,
        logical_date: str,
    ) -> tuple[dict[str, Any], ...]:
        """Apply the action's declared Scenario policies to its run values."""

        row = self.action_binding(intent)
        try:
            instant = datetime.fromisoformat(f"{logical_date}T00:00:00-05:00")
            actor = next(
                item
                for item in self._actor_registry
                if item["actor_id"] == intent.actor_id
            )
        except (TypeError, ValueError, StopIteration) as exc:
            raise PanicRuntimeComponentError(
                "runtime_policy_application_context_invalid"
            ) from exc
        applications = []
        for policy_id in row["scenario_policy_ids"]:
            if policy_id == "POL-TIME-01":
                result = TIME_POLICY.order_events(
                    (
                        EventWindow(
                            intent.intent_id,
                            instant.isoformat(),
                            instant.isoformat(),
                        ),
                    )
                )
            elif policy_id == "POL-INFO-01":
                route_id = row["direct_route_id"]
                recipient = row["direct_recipient_actor_id"]
                if route_id is None or recipient is None:
                    raise PanicRuntimeComponentError(
                        "runtime_information_policy_route_missing"
                    )
                product = InformationProduct(
                    _short_identity(
                        "information.0288", {"intent_id": intent.intent_id}
                    ),
                    1,
                    instant.isoformat(),
                    (instant + timedelta(days=1)).isoformat(),
                    (instant + timedelta(days=2)).isoformat(),
                )
                result = INFORMATION_POLICY.route_delivery(
                    product,
                    recipient_id=recipient,
                    route_id=route_id,
                    route_admitted=True,
                    delivered_at=None,
                )
            elif policy_id == "POL-SERVICE-01":
                host = row["direct_recipient_actor_id"]
                if host is None:
                    raise PanicRuntimeComponentError(
                        "runtime_service_policy_host_missing"
                    )
                result = SERVICE_POLICY.serve(
                    (
                        ServiceRequest(
                            _short_identity(
                                "service.0288", {"intent_id": intent.intent_id}
                            ),
                            host,
                            intent.actor_id,
                            instant.isoformat(),
                            1,
                        ),
                    ),
                    host_actor_id=host,
                    available_units=1,
                )
            elif policy_id == "POL-REVIEW-01":
                commitment_id = intent.parameters["commitment_id"]
                result = REVIEW_POLICY.classify(
                    required_item_ids=(commitment_id,),
                    present_item_ids=(commitment_id,),
                )
            elif policy_id == "POL-AMOUNT-01":
                result = AMOUNT_POLICY.assess(
                    requested_bound="nonquantified_category_request",
                    delivered_envelope=self._resource_envelope(
                        actor["resource_owner_id"]
                    ),
                    resource_owner_matches=True,
                )
            elif policy_id == "POL-FACILITY-01":
                result = FACILITY_POLICY.eligibility(
                    event_time=instant.isoformat(),
                    membership=self._membership(intent.actor_id),
                )
            elif policy_id == "POL-VENUE-01":
                result = VENUE_POLICY.advance(
                    VenueProcess(
                        _short_identity(
                            "venue.0288", {"intent_id": intent.intent_id}
                        ),
                        intent.actor_id,
                        "request_created",
                        0,
                    ),
                    target_state="request_delivered",
                    cause_kind="delivery",
                )
            elif policy_id == "POL-LIFECYCLE-01":
                result = LIFECYCLE_POLICY.should_revisit("state_change")
            elif policy_id == "POL-RESULT-01":
                result = RESULT_POLICY.record(
                    action_intent_id=intent.intent_id,
                    action_admission=disposition.status,
                    business_disposition_id=(
                        _short_identity(
                            "disposition.0288", {"intent_id": intent.intent_id}
                        )
                        if disposition.status == "accepted"
                        else None
                    ),
                    business_disposition=(
                        "accepted"
                        if disposition.status == "accepted"
                        else "failed"
                    ),
                    execution_result=(
                        "realized"
                        if disposition.state_delta_ids
                        else "no_effect"
                    ),
                    reason_code=disposition.reason_code,
                )
            else:
                raise PanicRuntimeComponentError(
                    f"runtime_scenario_policy_unresolved:{policy_id}"
                )
            applications.append(
                {
                    "policy_id": policy_id,
                    "source_action_intent_id": intent.intent_id,
                    "actor_id": intent.actor_id,
                    "capability_id": intent.parameters["capability_id"],
                    "commitment_id": intent.parameters["commitment_id"],
                    "status": "pass",
                    "result": _plain(result),
                }
            )
        return tuple(applications)

    def _resource_envelope(self, resource_owner_id: str) -> str:
        allowed = {"unknown", "unavailable", "constrained", "bounded_available"}
        return next(
            (
                item["value"]
                for item in self._resource_records
                if item["owner_id"] == resource_owner_id
                and item["value"] in allowed
            ),
            "unknown",
        )

    def _membership(self, actor_id: str) -> str:
        entity_id = next(
            item["entity_id"]
            for item in self._actor_registry
            if item["actor_id"] == actor_id
        )
        for item in self._relationship_records:
            if item["kind"] == "membership" and entity_id in item["parties"]:
                if item["state"] == "active":
                    return "member"
                if item["state"] == "nonmember":
                    return "nonmember"
        return "unknown"

    def _require_route(self, route_id: str, source: str, target: str) -> None:
        route = self._routes.get(route_id)
        if (
            route is None
            or route["source_id"] != source
            or route["target_id"] != target
            or route["latency_ticks"] != 1
        ):
            raise PanicRuntimeComponentError("runtime_message_route_unresolved")

    def scenario_policy_checks(self) -> tuple[dict[str, Any], ...]:
        """Exercise all selected Scenario policies on bounded control values."""

        product = InformationProduct(
            "information.0288.control",
            1,
            "1907-10-21T00:00:00-05:00",
            "1907-10-22T00:00:00-05:00",
            "1907-10-23T00:00:00-05:00",
        )
        delivery = INFORMATION_POLICY.route_delivery(
            product,
            recipient_id="actor.knickerbocker_trust",
            route_id="route.control",
            route_admitted=True,
            delivered_at="1907-10-21T00:00:00-05:00",
        )
        checks = (
            (
                TIME_POLICY,
                TIME_POLICY.order_events(
                    (
                        EventWindow(
                            "event.control.a",
                            "1907-10-21T00:00:00-05:00",
                            "1907-10-21T23:59:59-05:00",
                        ),
                        EventWindow(
                            "event.control.b",
                            "1907-10-22T00:00:00-05:00",
                            "1907-10-22T23:59:59-05:00",
                            ("event.control.a",),
                        ),
                    )
                ),
            ),
            (
                INFORMATION_POLICY,
                INFORMATION_POLICY.compose_observation(
                    (delivery,), required_versions={product.product_id: 1}
                ),
            ),
            (
                SERVICE_POLICY,
                SERVICE_POLICY.serve(
                    (
                        ServiceRequest(
                            "request.control",
                            "actor.knickerbocker_trust",
                            "actor.depositor.knickerbocker.need",
                            "1907-10-22T00:00:00-05:00",
                            1,
                        ),
                    ),
                    host_actor_id="actor.knickerbocker_trust",
                    available_units=1,
                ),
            ),
            (
                REVIEW_POLICY,
                REVIEW_POLICY.classify(
                    required_item_ids=("item.control",),
                    present_item_ids=("item.control",),
                ),
            ),
            (
                AMOUNT_POLICY,
                AMOUNT_POLICY.assess(
                    requested_bound="nonquantified_category_request",
                    delivered_envelope="bounded_available",
                    resource_owner_matches=True,
                ),
            ),
            (
                FACILITY_POLICY,
                FACILITY_POLICY.eligibility(
                    event_time="1907-10-26T00:00:00-05:00",
                    membership="member",
                ),
            ),
            (
                VENUE_POLICY,
                VENUE_POLICY.advance(
                    VenueProcess(
                        "venue.control",
                        "actor.broker_alpha",
                        "request_created",
                        0,
                    ),
                    target_state="request_delivered",
                    cause_kind="delivery",
                ),
            ),
            (LIFECYCLE_POLICY, LIFECYCLE_POLICY.should_revisit("delivery")),
            (
                RESULT_POLICY,
                RESULT_POLICY.record(
                    action_intent_id="intent.control",
                    action_admission="accepted",
                    business_disposition_id="disposition.control",
                    business_disposition="accepted",
                    execution_result="no_effect",
                    reason_code="control_case",
                ),
            ),
        )
        return tuple(
            {
                "policy_id": policy.policy_id,
                "implementation_id": policy.implementation_id,
                "status": "pass",
                "control_result": _plain(result),
            }
            for policy, result in checks
        )


class PanicReducer:
    """Apply participant private-state and lifecycle effects authoritatively."""

    implementation_id = "h2epr.component.0288.reducer"
    implementation_version = "0.1.0"

    def __init__(self, runtime_bundle: Mapping[str, Any]) -> None:
        self._environment = PanicEnvironment(runtime_bundle)

    def apply_batch(
        self,
        state: dict[str, Any],
        intents: tuple[ActionIntent, ...],
        run_seed: int,
        logical_tick: int,
    ) -> tuple[list[ActionDisposition], list[StateDelta]]:
        if type(run_seed) is not int or run_seed < 0:
            raise PanicRuntimeComponentError("runtime_seed_invalid")
        dispositions: list[ActionDisposition] = []
        deltas: list[StateDelta] = []
        for intent in intents:
            try:
                self._environment.action_binding(intent)
                actor_state = state["actors"][intent.actor_id]
            except (PanicRuntimeComponentError, KeyError, TypeError):
                dispositions.append(
                    ActionDisposition(
                        f"ad.{intent.intent_id}",
                        intent.intent_id,
                        logical_tick,
                        "rejected",
                        "action_binding_or_actor_invalid",
                    )
                )
                continue
            owned: list[str] = []
            updates = dict(intent.parameters["private_state_updates"])
            for state_id, after in sorted(updates.items()):
                if state_id not in actor_state:
                    raise PanicRuntimeComponentError(
                        "runtime_private_state_target_missing"
                    )
                before = actor_state[state_id]
                if before == after:
                    continue
                delta = StateDelta(
                    _short_identity(
                        "delta.0288.private",
                        {"intent_id": intent.intent_id, "state_id": state_id},
                    ),
                    intent.intent_id,
                    intent.actor_id,
                    state_id,
                    before,
                    after,
                    "participant_private_state_update",
                )
                actor_state[state_id] = after
                deltas.append(delta)
                owned.append(delta.delta_id)

            lifecycle_ids = tuple(intent.parameters["lifecycle_ids"])
            if lifecycle_ids:
                lifecycle_id = intent.parameters["primary_lifecycle_id"]
                try:
                    rule = LIFECYCLE_RULES_BY_ID[lifecycle_id]
                except KeyError as exc:
                    raise PanicRuntimeComponentError(
                        "runtime_lifecycle_unresolved"
                    ) from exc
                object_id = _short_identity(
                    "object.0288", {"intent_id": intent.intent_id}
                )
                record = rule.open_record(
                    object_id=object_id,
                    owner_actor_id=intent.actor_id,
                    initial_state_id=rule.initial_state_ids[0],
                    causal_parent_ids=(intent.intent_id,),
                )
                target = next(
                    target_state
                    for source_state, target_state in rule.transitions
                    if source_state == record.state_id
                )
                transition = rule.transition(
                    record,
                    target_state_id=target,
                    cause_id=intent.intent_id,
                )
                before_objects = copy.deepcopy(state["lifecycle_objects"])
                state["lifecycle_objects"][object_id] = _plain(transition.after)
                after_objects = copy.deepcopy(state["lifecycle_objects"])
                delta = StateDelta(
                    _short_identity(
                        "delta.0288.lifecycle", {"intent_id": intent.intent_id}
                    ),
                    intent.intent_id,
                    "__world__",
                    "lifecycle_objects",
                    before_objects,
                    after_objects,
                    "authoritative_lifecycle_transition",
                )
                deltas.append(delta)
                owned.append(delta.delta_id)
            dispositions.append(
                ActionDisposition(
                    f"ad.{intent.intent_id}",
                    intent.intent_id,
                    logical_tick,
                    "accepted",
                    "accepted_by_panic_authoritative_reducer",
                    tuple(owned),
                )
            )
        return dispositions, deltas


class PanicTraceCompiler:
    """Compile one validated Panic trace into a trace-closed event graph."""

    implementation_id = "h2epr.component.0288.trace-compiler"
    implementation_version = "0.1.0"

    _NODE_RECORD_TYPES = {
        "exogenous_input_release",
        "participant_decision",
        "action_intent",
        "scenario_policy_application",
        "action_disposition",
        "message_intent",
        "message_disposition",
        "state_delta",
        "carry_forward",
    }

    def compile(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        run_seal_sha256: str,
    ) -> dict[str, Any]:
        rows = [copy.deepcopy(dict(row)) for row in records]
        errors = validate_trace(rows)
        if errors:
            raise PanicRuntimeComponentError(
                "runtime_trace_invalid:" + ",".join(errors)
            )
        if not rows or rows[-1]["record_type"] != "run_seal":
            raise PanicRuntimeComponentError("runtime_trace_run_seal_missing")
        if rows[-1]["payload"]["seal_sha256"] != run_seal_sha256:
            raise PanicRuntimeComponentError("runtime_trace_run_seal_mismatch")
        nodes: list[dict[str, Any]] = []
        node_by_action: dict[str, str] = {}
        node_by_message: dict[str, str] = {}
        for row in rows:
            if row["record_type"] not in self._NODE_RECORD_TYPES:
                continue
            node_id = f"epg.node.{row['trace_id']}"
            node = {
                "node_id": node_id,
                "node_type": row["record_type"],
                "logical_tick": row["logical_tick"],
                "source_trace_id": row["trace_id"],
                "source_record_sha256": row["record_hash"],
                "participants": _participants(row),
                "payload": copy.deepcopy(row["payload"]),
            }
            nodes.append(node)
            if row["record_type"] == "action_intent":
                node_by_action[row["payload"]["intent_id"]] = node_id
            elif row["record_type"] == "message_intent":
                node_by_message[row["payload"]["message_intent_id"]] = node_id

        node_ids = {node["node_id"] for node in nodes}
        edges: list[dict[str, Any]] = []
        for node in nodes:
            payload = node["payload"]
            source: str | None = None
            relation: str | None = None
            if node["node_type"] in {"action_disposition", "state_delta"}:
                source = node_by_action.get(
                    payload.get("intent_id") or payload.get("source_intent_id")
                )
                relation = "adjudicates" if node["node_type"] == "action_disposition" else "causes"
            elif node["node_type"] == "message_intent":
                source = node_by_action.get(payload["source_action_intent_id"])
                relation = "emits"
            elif node["node_type"] == "scenario_policy_application":
                source = node_by_action.get(payload["source_action_intent_id"])
                relation = "governs"
            elif node["node_type"] == "message_disposition":
                source = node_by_message.get(payload["message_intent_id"])
                relation = "routes"
            if source is None or relation is None:
                continue
            edge_preimage = {
                "source_node_id": source,
                "target_node_id": node["node_id"],
                "relation": relation,
                "source_trace_ids": [
                    source.removeprefix("epg.node."),
                    node["source_trace_id"],
                ],
            }
            edges.append(
                {
                    "edge_id": _short_identity("epg.edge.0288", edge_preimage),
                    **edge_preimage,
                }
            )
        if any(
            edge["source_node_id"] not in node_ids
            or edge["target_node_id"] not in node_ids
            for edge in edges
        ):
            raise PanicRuntimeComponentError("runtime_epg_edge_unresolved")
        preimage = {
            "format_identity": "h2epr.generated-epg.v0_1",
            "event_id": "H2EPR-0288",
            "run_id": rows[0]["run_id"],
            "source_trace_sha256": canonical_sha256(rows),
            "source_run_seal_sha256": run_seal_sha256,
            "nodes": nodes,
            "edges": edges,
            "claim_boundary": {
                "historical_calibration": False,
                "historical_validation": False,
                "scientific_validity_claim": False,
                "output_interpretation": "simulation_generated_mechanism_coverage",
            },
        }
        return {
            **preimage,
            "seal": {"artifact_sha256": canonical_sha256(preimage)},
        }


def _participants(row: Mapping[str, Any]) -> list[str]:
    payload = row["payload"]
    values = []
    for key in ("actor_id", "sender_id", "recipient_id", "owner_actor_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.startswith("actor."):
            values.append(value)
    return sorted(set(values))


__all__ = [
    "ENVIRONMENT_ACTOR_ID",
    "PanicEnvironment",
    "PanicObservationProjector",
    "PanicParticipantExecutor",
    "PanicReducer",
    "PanicRuntimeComponentError",
    "PanicTraceCompiler",
    "ProjectedDecision",
]
