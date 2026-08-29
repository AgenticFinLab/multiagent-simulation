"""Runtime components for the SingHealth full-roster Rule package.

These components operate only on the admitted runtime bundle. They do not
discover Markdown, resolve implementation names dynamically, or infer
participant authority from an action label.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence

from masim.integrations.event_process import (
    ActionDisposition,
    ActionIntent,
    MessageIntent,
    StateDelta,
    canonical_sha256,
    validate_trace,
)

from h2epr.execution import ParticipantDecision, ParticipantDecisionContext

from .lifecycle_rules import LIFECYCLE_RULES_BY_ID
from .registry import participant_policies_by_capability
from .scenario_rules import (
    AUTHORITY_POLICY,
    COORDINATION_POLICY,
    INCIDENT_POLICY,
    INFORMATION_POLICY,
    LIFECYCLE_POLICY,
    NOTIFICATION_POLICY,
    ROUTE_POLICY,
    TECHNICAL_POLICY,
    TIME_POLICY,
    AuthorityClaim,
    AuthorityContext,
    InformationProduct,
    ScheduledEvent,
    TechnicalActionRequest,
)


ENVIRONMENT_ACTOR_ID = "environment.singhealth_data_breach"


class SingHealthRuntimeComponentError(ValueError):
    """A closed SingHealth runtime value or invocation is invalid."""


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {
            item.name: _plain(getattr(value, item.name)) for item in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _short_identity(prefix: str, value: Mapping[str, Any]) -> str:
    return f"{prefix}.{canonical_sha256(value)[:20]}"


def _instant(logical_date: str) -> datetime:
    try:
        return datetime.fromisoformat(f"{logical_date}T00:00:00+08:00")
    except (TypeError, ValueError) as exc:
        raise SingHealthRuntimeComponentError(
            "singhealth_runtime_logical_date_invalid"
        ) from exc


@dataclass(frozen=True)
class ProjectedDecision:
    """One admitted participant decision and its optional MASim action."""

    decision: ParticipantDecision
    action_intent: ActionIntent | None


class SingHealthObservationProjector:
    """Build exact participant contexts from one sealed prestate."""

    implementation_id = "h2epr.component.0616.observation-projector"
    implementation_version = "0.1.0"

    def __init__(self, runtime_bundle: Mapping[str, Any]) -> None:
        rows = tuple(runtime_bundle.get("observation_rules", ()))
        carriers = tuple(runtime_bundle.get("carrier_projections", ()))
        self._rules = {
            (row["actor_id"], row["capability_id"], row["commitment_id"]): (
                copy.deepcopy(dict(row))
            )
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
        if len(self._rules) != len(rows) or len(self._carriers) != len(
            carrier_rows
        ):
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_projection_identity_duplicate"
            )

    def due_rules(self, logical_tick: int) -> tuple[dict[str, Any], ...]:
        """Return decision rules scheduled at one logical coordinate."""

        if type(logical_tick) is not int or logical_tick < 0:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_projection_tick_invalid"
            )
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
        """Project only fields declared by one admitted commitment."""

        key = (actor_id, capability_id, commitment_id)
        try:
            rule = self._rules[key]
            carrier = self._carriers[(actor_id, capability_id)]
            actor_state = state["actors"][actor_id]
        except (KeyError, TypeError) as exc:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_projection_scope_unresolved"
            ) from exc
        if rule["evaluation_tick"] != logical_tick:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_projection_not_due"
            )
        try:
            private_state = {
                state_id: actor_state[state_id]
                for state_id in rule["private_state_ids"]
            }
        except KeyError as exc:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_projection_private_state_missing"
            ) from exc
        observations = copy.deepcopy(rule["observation_values"])
        configuration = copy.deepcopy(carrier["configuration_parameters"])
        if (
            set(observations) != set(rule["observation_ids"])
            or set(private_state) != set(rule["private_state_ids"])
            or set(configuration)
            != set(rule["configuration_parameter_ids"])
        ):
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_projection_field_scope_mismatch"
            )
        return ParticipantDecisionContext(
            actor_id=actor_id,
            capability_id=capability_id,
            commitment_id=commitment_id,
            observations=observations,
            private_state=private_state,
            configuration_parameters=configuration,
        )


class SingHealthParticipantExecutor:
    """Evaluate admitted participant policies without authoring results."""

    implementation_id = "h2epr.component.0616.participant-executor"
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
        try:
            policy = participant_policies_by_capability()[context.capability_id]
        except KeyError as exc:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_participant_policy_unresolved"
            ) from exc
        decision = policy.decide(context)
        if primary_lifecycle_id not in decision.lifecycle_ids:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_primary_lifecycle_outside_decision"
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
            intent_id=_short_identity("intent.0616", identity),
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


class SingHealthEnvironment:
    """Adjudicate registered actions and author later-delivered results."""

    implementation_id = "h2epr.component.0616.environment"
    implementation_version = "0.1.0"

    def __init__(self, runtime_bundle: Mapping[str, Any]) -> None:
        action_rows = tuple(runtime_bundle.get("action_registry", ()))
        route_rows = tuple(runtime_bundle.get("communication_routes", ()))
        decision_rows = tuple(runtime_bundle.get("observation_rules", ()))
        actor_rows = tuple(runtime_bundle.get("actor_registry", ()))
        self._actions = {
            (row["actor_id"], row["intent_id"]): copy.deepcopy(dict(row))
            for row in action_rows
        }
        self._routes = {
            row["route_id"]: copy.deepcopy(dict(row)) for row in route_rows
        }
        self._decisions = {
            (row["actor_id"], row["capability_id"], row["commitment_id"]): (
                copy.deepcopy(dict(row))
            )
            for row in decision_rows
        }
        self._actors = {
            row["actor_id"]: copy.deepcopy(dict(row)) for row in actor_rows
        }
        if (
            len(self._actions) != len(action_rows)
            or len(self._routes) != len(route_rows)
            or len(self._decisions) != len(decision_rows)
            or len(self._actors) != len(actor_rows)
        ):
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_environment_identity_duplicate"
            )

    def action_binding(self, intent: ActionIntent) -> dict[str, Any]:
        try:
            row = self._actions[(intent.actor_id, intent.action_type)]
            parameters = intent.parameters
            decision = self._decisions[
                (
                    intent.actor_id,
                    parameters["capability_id"],
                    parameters["commitment_id"],
                )
            ]
        except (KeyError, TypeError) as exc:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_action_not_registered"
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
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_action_binding_mismatch"
            )
        return copy.deepcopy(row)

    def admit_action(
        self,
        intent: ActionIntent,
        state: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Check exact carrier authority and any technical preconditions."""

        row = self.action_binding(intent)
        try:
            actor_state = state["actors"][intent.actor_id]
            context = row["authority_context"]
        except (KeyError, TypeError) as exc:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_authority_context_missing"
            ) from exc
        capacity_id = context["capacity_id"]
        authority_ref = context["authority_ref"]
        relationship_ref = context["relationship_ref"]
        access_ref = context["access_ref"]
        resource_owner_id = context["resource_owner_id"]
        disposition = AUTHORITY_POLICY.evaluate(
            AuthorityClaim(
                claim_id=_short_identity(
                    "authority-claim.0616", {"intent_id": intent.intent_id}
                ),
                actor_id=intent.actor_id,
                capacity_id=capacity_id,
                authority_ref=authority_ref,
                relationship_ref=relationship_ref,
                access_ref=access_ref,
                resource_owner_id=resource_owner_id,
            ),
            AuthorityContext(
                active_capacity_ids=tuple(actor_state["capacity_ids"]),
                effective_authority_refs=(actor_state["authority_graph_id"],),
                relationship_refs=(relationship_ref,),
                access_refs=tuple(
                    (
                        *actor_state["access_scope_ids"],
                        *actor_state["effective_scope_record_ids"],
                    )
                ),
                resource_owner_id=actor_state["resource_owner_id"],
                resource_available=True,
            ),
        )
        if not disposition.accepted:
            raise SingHealthRuntimeComponentError(
                f"singhealth_runtime_authority_rejected:{disposition.reason_code}"
            )
        controls: dict[str, Any] = {"authority": _plain(disposition)}
        if "POL-0616-TECH-01" in row["scenario_policy_ids"]:
            request = TechnicalActionRequest(
                request_id=_short_identity(
                    "technical-request.0616", {"intent_id": intent.intent_id}
                ),
                actor_id=intent.actor_id,
                target_id=context["technical_target_id"],
                target_version=state["state_version"],
                authority_ref=authority_ref,
                access_ref=access_ref,
                resource_owner_id=resource_owner_id,
            )
            technical = TECHNICAL_POLICY.adjudicate(
                request,
                authority_matches=True,
                prestate_matches=True,
                access_granted=True,
                resource_owner_matches=True,
                feasible=True,
            )
            if not technical.accepted:
                raise SingHealthRuntimeComponentError(
                    "singhealth_runtime_technical_admission_rejected"
                )
            controls["technical"] = _plain(technical)
        return row, controls

    def messages_for(
        self,
        intent: ActionIntent,
        disposition: ActionDisposition,
    ) -> tuple[MessageIntent, ...]:
        """Create one typed result and any one-recipient semantic notice."""

        row = self.action_binding(intent)
        if disposition.status != "accepted":
            return ()
        lifecycle_admission = LIFECYCLE_POLICY.admit_intent(
            intent_id=intent.intent_id,
            idempotency_key=_short_identity(
                "idempotency.0616", {"intent_id": intent.intent_id}
            ),
            semantic_admitted=True,
            prior_dispositions={},
        )
        result = LIFECYCLE_POLICY.record_result(
            lifecycle_admission,
            result_id=_short_identity(
                "result.0616", {"intent_id": intent.intent_id}
            ),
            result_kind=(
                "completed" if disposition.state_delta_ids else "accepted"
            ),
            state_delta_id=(
                disposition.state_delta_ids[0]
                if disposition.state_delta_ids
                else None
            ),
        )
        result_route = row["result_route_id"]
        self._require_route(result_route, ENVIRONMENT_ACTOR_ID, intent.actor_id)
        messages = [
            MessageIntent(
                message_intent_id=_short_identity(
                    "message.0616.result", {"intent_id": intent.intent_id}
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
        ]
        recipient = row["direct_recipient_id"]
        if recipient is not None:
            route_id = row["direct_route_id"]
            self._require_route(route_id, intent.actor_id, recipient)
            messages.append(
                MessageIntent(
                    message_intent_id=_short_identity(
                        "message.0616.notice",
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
        """Apply every policy declared for the action to bounded run values."""

        row = self.action_binding(intent)
        instant = _instant(logical_date)
        applications = []
        for policy_id in row["scenario_policy_ids"]:
            result = self._apply_policy(
                policy_id,
                row=row,
                intent=intent,
                disposition=disposition,
                instant=instant,
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

    def _apply_policy(
        self,
        policy_id: str,
        *,
        row: Mapping[str, Any],
        intent: ActionIntent,
        disposition: ActionDisposition,
        instant: datetime,
    ) -> Any:
        recipient = row["direct_recipient_id"]
        route_id = row["direct_route_id"]
        context = row["authority_context"]
        if policy_id == "POL-0616-TIME-01":
            return TIME_POLICY.order_events(
                (
                    ScheduledEvent(
                        intent.intent_id,
                        instant.isoformat(),
                        "participant_decision_and_issue",
                    ),
                )
            )
        if policy_id == "POL-0616-INFO-01":
            if recipient is None or route_id is None:
                raise SingHealthRuntimeComponentError(
                    "singhealth_runtime_information_route_missing"
                )
            product = InformationProduct(
                product_id=_short_identity(
                    "information.0616", {"intent_id": intent.intent_id}
                ),
                version=1,
                producer_id=intent.actor_id,
                issued_at=instant.isoformat(),
                as_of_time=instant.isoformat(),
                fresh_until=(instant + timedelta(days=1)).isoformat(),
                expires_at=(instant + timedelta(days=2)).isoformat(),
                visibility_recipient_ids=(recipient,),
            )
            return INFORMATION_POLICY.route_delivery(
                product,
                delivery_id=_short_identity(
                    "delivery.0616", {"intent_id": intent.intent_id}
                ),
                recipient_id=recipient,
                route_id=route_id,
                route_admitted=True,
                transported=False,
                delivered_at=None,
            )
        if policy_id == "POL-0616-TECH-01":
            admission = TECHNICAL_POLICY.adjudicate(
                TechnicalActionRequest(
                    request_id=_short_identity(
                        "technical-request.0616",
                        {"intent_id": intent.intent_id},
                    ),
                    actor_id=intent.actor_id,
                    target_id=context["technical_target_id"],
                    target_version=intent.prestate_version,
                    authority_ref=context["authority_ref"],
                    access_ref=context["access_ref"],
                    resource_owner_id=context["resource_owner_id"],
                ),
                authority_matches=True,
                prestate_matches=True,
                access_granted=True,
                resource_owner_matches=True,
                feasible=True,
            )
            return TECHNICAL_POLICY.record_result(
                admission,
                result_id=_short_identity(
                    "technical-result.0616", {"intent_id": intent.intent_id}
                ),
                result_kind="executed",
                reason_code="canonical_mechanism_coverage_execution",
                authoritative_delta_id=(
                    disposition.state_delta_ids[0]
                    if disposition.state_delta_ids
                    else None
                ),
            )
        if policy_id == "POL-0616-ROUTE-01":
            if recipient is None or route_id is None:
                raise SingHealthRuntimeComponentError(
                    "singhealth_runtime_route_target_missing"
                )
            record = ROUTE_POLICY.issue(
                message_id=_short_identity(
                    "route-message.0616", {"intent_id": intent.intent_id}
                ),
                issuer_id=intent.actor_id,
                recipient_id=recipient,
                route_id=route_id,
                cause_id=intent.intent_id,
            )
            return ROUTE_POLICY.admit_route(
                record,
                recipient_eligible=True,
                route_available=True,
                cause_id=intent.intent_id,
            )
        if policy_id == "POL-0616-COORD-01":
            record = COORDINATION_POLICY.open(
                process_id=_short_identity(
                    "coordination.0616", {"intent_id": intent.intent_id}
                ),
                owner_id=intent.actor_id,
                cause_id=intent.intent_id,
            )
            return COORDINATION_POLICY.admit(
                record,
                authority_admitted=True,
                capacity_available=True,
                cause_id=intent.intent_id,
            )
        if policy_id == "POL-0616-AUTH-01":
            return AUTHORITY_POLICY.evaluate(
                AuthorityClaim(
                    claim_id=_short_identity(
                        "authority-claim.0616",
                        {"intent_id": intent.intent_id},
                    ),
                    actor_id=intent.actor_id,
                    capacity_id=context["capacity_id"],
                    authority_ref=context["authority_ref"],
                    relationship_ref=context["relationship_ref"],
                    access_ref=context["access_ref"],
                    resource_owner_id=context["resource_owner_id"],
                ),
                AuthorityContext(
                    active_capacity_ids=(context["capacity_id"],),
                    effective_authority_refs=(context["authority_ref"],),
                    relationship_refs=(context["relationship_ref"],),
                    access_refs=(context["access_ref"],),
                    resource_owner_id=context["resource_owner_id"],
                    resource_available=True,
                ),
            )
        if policy_id == "POL-0616-INCIDENT-01":
            record = INCIDENT_POLICY.open(
                incident_id=_short_identity(
                    "incident.0616", {"intent_id": intent.intent_id}
                ),
                cause_id=intent.intent_id,
            )
            return INCIDENT_POLICY.begin_review(
                record, cause_id=intent.intent_id
            )
        if policy_id == "POL-0616-LIFECYCLE-01":
            admission = LIFECYCLE_POLICY.admit_intent(
                intent_id=intent.intent_id,
                idempotency_key=_short_identity(
                    "idempotency.0616", {"intent_id": intent.intent_id}
                ),
                semantic_admitted=disposition.status == "accepted",
                prior_dispositions={},
            )
            if not admission.accepted:
                return admission
            return LIFECYCLE_POLICY.record_result(
                admission,
                result_id=_short_identity(
                    "result.0616", {"intent_id": intent.intent_id}
                ),
                result_kind=(
                    "completed" if disposition.state_delta_ids else "accepted"
                ),
                state_delta_id=(
                    disposition.state_delta_ids[0]
                    if disposition.state_delta_ids
                    else None
                ),
            )
        if policy_id == "POL-0616-NOTIFY-01":
            record = NOTIFICATION_POLICY.open(
                plan_id=_short_identity(
                    "notification-plan.0616", {"intent_id": intent.intent_id}
                ),
                cause_id=intent.intent_id,
            )
            return NOTIFICATION_POLICY.advance_preparation(
                record,
                target_state_id="drafting",
                cause_id=intent.intent_id,
            )
        raise SingHealthRuntimeComponentError(
            f"singhealth_runtime_scenario_policy_unresolved:{policy_id}"
        )

    def _require_route(self, route_id: str, source: str, target: str) -> None:
        route = self._routes.get(route_id)
        if (
            route is None
            or route["source_id"] != source
            or route["target_id"] != target
            or route["latency_ticks"] != 1
            or route["fanout"] != "single_recipient"
        ):
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_message_route_unresolved"
            )

    def scenario_policy_checks(self) -> tuple[dict[str, Any], ...]:
        """Exercise all selected policies on bounded control values."""

        instant = datetime(2018, 6, 11, tzinfo=timezone(timedelta(hours=8)))
        product = InformationProduct(
            "information.0616.control",
            1,
            "actor.0616.office.sirm",
            instant.isoformat(),
            instant.isoformat(),
            (instant + timedelta(days=1)).isoformat(),
            (instant + timedelta(days=2)).isoformat(),
            ("actor.0616.office.cluster-iso",),
        )
        delivery = INFORMATION_POLICY.route_delivery(
            product,
            delivery_id="delivery.0616.control",
            recipient_id="actor.0616.office.cluster-iso",
            route_id="route.0616.control",
            route_admitted=True,
            transported=True,
            delivered_at=instant.isoformat(),
        )
        technical_admission = TECHNICAL_POLICY.adjudicate(
            TechnicalActionRequest(
                "technical-request.0616.control",
                "actor.0616.unit.technical.security-engineering",
                "asset.0616.monitoring-control.assigned-context",
                0,
                "authority.0616.control",
                "access.0616.control",
                "resource-owner.0616.ihis",
            ),
            authority_matches=True,
            prestate_matches=True,
            access_granted=True,
            resource_owner_matches=True,
            feasible=True,
        )
        route_record = ROUTE_POLICY.issue(
            message_id="message.0616.control",
            issuer_id="actor.0616.office.sirm",
            recipient_id="actor.0616.office.cluster-iso",
            route_id="route.0616.control",
            cause_id="cause.0616.control",
        )
        coordination = COORDINATION_POLICY.open(
            process_id="coordination.0616.control",
            owner_id="actor.0616.office.sirm",
            cause_id="cause.0616.control",
        )
        authority_claim = AuthorityClaim(
            "authority-claim.0616.control",
            "actor.0616.office.sirm",
            "capacity.0616.ihis.sirm",
            "authority.0616.office.sirm",
            "opening.0616.relationship.ihis-singhealth-scm",
            "authority.0616.office.sirm",
            "resource-owner.0616.ihis",
        )
        authority_context = AuthorityContext(
            ("capacity.0616.ihis.sirm",),
            ("authority.0616.office.sirm",),
            ("opening.0616.relationship.ihis-singhealth-scm",),
            ("authority.0616.office.sirm",),
            "resource-owner.0616.ihis",
            True,
        )
        incident = INCIDENT_POLICY.open(
            incident_id="incident.0616.control",
            cause_id="cause.0616.control",
        )
        lifecycle = LIFECYCLE_POLICY.admit_intent(
            intent_id="intent.0616.control",
            idempotency_key="idempotency.0616.control",
            semantic_admitted=True,
            prior_dispositions={},
        )
        notification = NOTIFICATION_POLICY.open(
            plan_id="notification-plan.0616.control",
            cause_id="cause.0616.control",
        )
        checks = (
            (
                TIME_POLICY,
                TIME_POLICY.order_events(
                    (
                        ScheduledEvent(
                            "event.0616.control",
                            instant.isoformat(),
                            "participant_decision_and_issue",
                        ),
                    )
                ),
            ),
            (
                INFORMATION_POLICY,
                INFORMATION_POLICY.project_observation(
                    delivery,
                    observation_id="observation.0616.control",
                    frozen_at=instant.isoformat(),
                ),
            ),
            (
                TECHNICAL_POLICY,
                TECHNICAL_POLICY.record_result(
                    technical_admission,
                    result_id="technical-result.0616.control",
                    result_kind="executed",
                    reason_code="control_case",
                ),
            ),
            (
                ROUTE_POLICY,
                ROUTE_POLICY.admit_route(
                    route_record,
                    recipient_eligible=True,
                    route_available=True,
                    cause_id="cause.0616.control",
                ),
            ),
            (
                COORDINATION_POLICY,
                COORDINATION_POLICY.admit(
                    coordination,
                    authority_admitted=True,
                    capacity_available=True,
                    cause_id="cause.0616.control",
                ),
            ),
            (
                AUTHORITY_POLICY,
                AUTHORITY_POLICY.evaluate(authority_claim, authority_context),
            ),
            (
                INCIDENT_POLICY,
                INCIDENT_POLICY.begin_review(
                    incident, cause_id="cause.0616.control"
                ),
            ),
            (LIFECYCLE_POLICY, lifecycle),
            (
                NOTIFICATION_POLICY,
                NOTIFICATION_POLICY.advance_preparation(
                    notification,
                    target_state_id="drafting",
                    cause_id="cause.0616.control",
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


class SingHealthReducer:
    """Apply participant state and lifecycle effects authoritatively."""

    implementation_id = "h2epr.component.0616.reducer"
    implementation_version = "0.1.0"

    def __init__(self, runtime_bundle: Mapping[str, Any]) -> None:
        self._environment = SingHealthEnvironment(runtime_bundle)

    def apply_batch(
        self,
        state: dict[str, Any],
        intents: tuple[ActionIntent, ...],
        run_seed: int,
        logical_tick: int,
    ) -> tuple[list[ActionDisposition], list[StateDelta]]:
        if type(run_seed) is not int or run_seed < 0:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_seed_invalid"
            )
        dispositions: list[ActionDisposition] = []
        deltas: list[StateDelta] = []
        for intent in intents:
            try:
                self._environment.admit_action(intent, state)
                actor_state = state["actors"][intent.actor_id]
            except (SingHealthRuntimeComponentError, KeyError, TypeError):
                dispositions.append(
                    ActionDisposition(
                        f"ad.{intent.intent_id}",
                        intent.intent_id,
                        logical_tick,
                        "rejected",
                        "action_binding_or_authority_invalid",
                    )
                )
                continue
            if intent.intent_id in state["prior_dispositions"]:
                dispositions.append(
                    ActionDisposition(
                        f"ad.{intent.intent_id}",
                        intent.intent_id,
                        logical_tick,
                        "rejected",
                        "duplicate_prior_disposition",
                    )
                )
                continue
            owned: list[str] = []
            for state_id, after in sorted(
                dict(intent.parameters["private_state_updates"]).items()
            ):
                if state_id not in actor_state:
                    raise SingHealthRuntimeComponentError(
                        "singhealth_runtime_private_state_target_missing"
                    )
                before = actor_state[state_id]
                if before == after:
                    continue
                delta = StateDelta(
                    _short_identity(
                        "delta.0616.private",
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
            lifecycle_id = intent.parameters["primary_lifecycle_id"]
            try:
                rule = LIFECYCLE_RULES_BY_ID[lifecycle_id]
            except KeyError as exc:
                raise SingHealthRuntimeComponentError(
                    "singhealth_runtime_lifecycle_unresolved"
                ) from exc
            object_id = _short_identity(
                "object.0616", {"intent_id": intent.intent_id}
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
            lifecycle_delta = StateDelta(
                _short_identity(
                    "delta.0616.lifecycle", {"intent_id": intent.intent_id}
                ),
                intent.intent_id,
                "__world__",
                "lifecycle_objects",
                before_objects,
                after_objects,
                "authoritative_lifecycle_transition",
            )
            deltas.append(lifecycle_delta)
            owned.append(lifecycle_delta.delta_id)
            before_dispositions = copy.deepcopy(state["prior_dispositions"])
            state["prior_dispositions"][intent.intent_id] = (
                f"ad.{intent.intent_id}"
            )
            after_dispositions = copy.deepcopy(state["prior_dispositions"])
            idempotency_delta = StateDelta(
                _short_identity(
                    "delta.0616.idempotency", {"intent_id": intent.intent_id}
                ),
                intent.intent_id,
                "__world__",
                "prior_dispositions",
                before_dispositions,
                after_dispositions,
                "authoritative_idempotency_record",
            )
            deltas.append(idempotency_delta)
            owned.append(idempotency_delta.delta_id)
            dispositions.append(
                ActionDisposition(
                    f"ad.{intent.intent_id}",
                    intent.intent_id,
                    logical_tick,
                    "accepted",
                    "accepted_by_singhealth_authoritative_reducer",
                    tuple(owned),
                )
            )
        return dispositions, deltas


class SingHealthTraceCompiler:
    """Compile one validated SingHealth trace into a trace-closed graph."""

    implementation_id = "h2epr.component.0616.trace-compiler"
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
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_trace_invalid:" + ",".join(errors)
            )
        if not rows or rows[-1]["record_type"] != "run_seal":
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_trace_run_seal_missing"
            )
        if rows[-1]["payload"]["seal_sha256"] != run_seal_sha256:
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_trace_run_seal_mismatch"
            )
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
                relation = (
                    "adjudicates"
                    if node["node_type"] == "action_disposition"
                    else "causes"
                )
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
                    "edge_id": _short_identity(
                        "epg.edge.0616", edge_preimage
                    ),
                    **edge_preimage,
                }
            )
        if any(
            edge["source_node_id"] not in node_ids
            or edge["target_node_id"] not in node_ids
            for edge in edges
        ):
            raise SingHealthRuntimeComponentError(
                "singhealth_runtime_epg_edge_unresolved"
            )
        preimage = {
            "format_identity": "h2epr.generated-epg.v0_1",
            "event_id": "H2EPR-0616",
            "run_id": rows[0]["run_id"],
            "source_trace_sha256": canonical_sha256(rows),
            "source_run_seal_sha256": run_seal_sha256,
            "nodes": nodes,
            "edges": edges,
            "claim_boundary": {
                "historical_calibration": False,
                "historical_validation": False,
                "scientific_validity_claim": False,
                "output_interpretation": (
                    "simulation_generated_mechanism_coverage"
                ),
            },
        }
        return {**preimage, "seal": {"artifact_sha256": canonical_sha256(preimage)}}


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
    "ProjectedDecision",
    "SingHealthEnvironment",
    "SingHealthObservationProjector",
    "SingHealthParticipantExecutor",
    "SingHealthReducer",
    "SingHealthRuntimeComponentError",
    "SingHealthTraceCompiler",
]
