"""Positive participant decisions for the bounded SingHealth lineage.

These policies expose one synthetic conformance branch.  Missing deliveries,
unresolved duplicates, unsupported capacities, and unbound branches fail
closed instead of producing substitute behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from h2epr.bundles.canonical import sha256_value

from .binding import LineageBinding, LineageBindingError
from .environment import LineageEnvironmentV0_1, MessageDelivery, VerificationResult


TECHNICAL_ACTOR_ID = "actor.0616.unit.technical.scm-application-database"
OPERATIONS_ACTOR_ID = (
    "actor.0616.unit.operations.application-scm-coordination"
)
GCIO_ACTOR_ID = "actor.0616.office.singhealth-gcio"

_REOPENING_LIFECYCLES = {
    "never_issued",
    "failed",
    "expired",
    "cancelled",
    "superseded",
}


def _stable_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise LineageBindingError(f"LINEAGE_POLICY_VALUE_INVALID:{label}")
    return value


def _version(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LineageBindingError(f"LINEAGE_POLICY_VALUE_INVALID:{label}")
    return value


def _sorted_ids(values: Sequence[str], label: str) -> list[str]:
    result = [_stable_id(value, label) for value in values]
    if not result or len(result) != len(set(result)):
        raise LineageBindingError(f"LINEAGE_POLICY_VALUE_INVALID:{label}")
    return sorted(result)


def _require_delivery(
    delivery: MessageDelivery,
    *,
    action: Mapping[str, Any],
    message: Mapping[str, Any],
    recipient_id: str,
    label: str,
) -> None:
    if (
        not delivery.delivered
        or delivery.action_intent_id != action["intent_id"]
        or delivery.message_intent_id != message["message_intent_id"]
        or delivery.recipient_id != recipient_id
    ):
        raise LineageBindingError(f"LINEAGE_REQUIRED_DELIVERY_MISSING:{label}")


def _require_reopening_lifecycle(value: str, label: str) -> None:
    if value not in _REOPENING_LIFECYCLES:
        raise LineageBindingError(f"LINEAGE_ACTIVE_EQUIVALENT_INTENT:{label}")


@dataclass(frozen=True)
class LineageDecision:
    decision_policy_id: str
    action_key: str
    commitment_ids: tuple[str, ...]
    semantic_parameters: Mapping[str, Any]


class PositiveLineagePoliciesV0_1:
    """One deterministic conformance branch for three selected participants."""

    TECHNICAL_POLICY_ID = (
        "h2epr.decision.0616.technical.cross_system_finding.v0_1"
    )
    OPERATIONS_POLICY_ID = (
        "h2epr.decision.0616.operations.verify_then_escalate.v0_1"
    )
    GCIO_POLICY_ID = "h2epr.decision.0616.gcio.clarification.v0_1"

    def __init__(self, binding: LineageBinding) -> None:
        self.binding = binding
        self.environment = LineageEnvironmentV0_1(binding)
        actual = {
            item["decision_policy_id"]: tuple(item["action_keys"])
            for item in binding.decision_bindings
        }
        expected = {
            self.TECHNICAL_POLICY_ID: (
                "technical.share_technical_finding",
            ),
            self.OPERATIONS_POLICY_ID: (
                "operations.request_fact_verification",
                "operations.escalate_operational_concern",
            ),
            self.GCIO_POLICY_ID: (
                "gcio.request_operational_clarification",
            ),
        }
        if actual != expected:
            raise LineageBindingError("LINEAGE_DECISION_POLICY_SET_MISMATCH")

    def decide_share_technical_finding(
        self,
        observation: Mapping[str, Any],
        *,
        finding_id: str,
        finding_version: int,
        artifact_ref: str,
        proposition_ref: str,
        event_time_ref: str,
        uncertainty: str,
        requested_attention: str,
        expiry_time: Mapping[str, Any] | None,
    ) -> LineageDecision:
        values = self.binding.read_observation(
            "technical.share_technical_finding", observation
        )
        source_signal_ref = _stable_id(
            values["local_technical_signal"], "local_technical_signal"
        )
        control_state_ref = _stable_id(
            values["local_control_state"], "local_control_state"
        )
        parameters = {
            "artifact_ref": _stable_id(artifact_ref, "artifact_ref"),
            "capacity_id": (
                "capacity.0616.unit.technical.scm-application-database"
            ),
            "control_state_ref": control_state_ref,
            "event_time_ref": _stable_id(event_time_ref, "event_time_ref"),
            "expiry_time": expiry_time,
            "finding_id": _stable_id(finding_id, "finding_id"),
            "finding_version": _version(finding_version, "finding_version"),
            "proposition_ref": _stable_id(proposition_ref, "proposition_ref"),
            "recipient_id": OPERATIONS_ACTOR_ID,
            "requested_attention": requested_attention,
            "route_id": "route.0616.technical_to_operations.finding",
            "sender_id": TECHNICAL_ACTOR_ID,
            "source_record_sha256": sha256_value(
                {
                    "source_signal_ref": source_signal_ref,
                    "control_state_ref": control_state_ref,
                    "artifact_ref": artifact_ref,
                    "proposition_ref": proposition_ref,
                }
            ),
            "source_signal_ref": source_signal_ref,
            "uncertainty": uncertainty,
        }
        return LineageDecision(
            decision_policy_id=self.TECHNICAL_POLICY_ID,
            action_key="technical.share_technical_finding",
            commitment_ids=(
                "h2epr.commitment.0616."
                "technical_administration_and_line_security_staff.situation_b",
            ),
            semantic_parameters=parameters,
        )

    def decide_request_fact_verification(
        self,
        observation: Mapping[str, Any],
        *,
        finding_action: Mapping[str, Any],
        finding_message: Mapping[str, Any],
        finding_delivery: MessageDelivery,
        request_id: str,
        request_version: int,
        claim_ref: str,
        requested_check: str,
        urgency: str,
        review_condition_ref: str,
        expiry_time: Mapping[str, Any] | None,
    ) -> LineageDecision:
        self.binding.validate_message(
            "technical.share_technical_finding", finding_action, finding_message
        )
        _require_delivery(
            finding_delivery,
            action=finding_action,
            message=finding_message,
            recipient_id=OPERATIONS_ACTOR_ID,
            label="technical_finding",
        )
        values = self.binding.read_observation(
            "operations.request_fact_verification", observation
        )
        if (
            values["delivered_role_local_account"]
            != finding_message["message_intent_id"]
            or values["management_route_context"]
            != "opening.0616.route.operations-gcio"
        ):
            raise LineageBindingError("LINEAGE_VERIFICATION_BASIS_MISMATCH")
        _require_reopening_lifecycle(
            values["intent_lifecycle_notice"], "fact_verification"
        )
        finding_values = self.binding.semantic_values(finding_action)
        parameters = {
            "capacity_id": (
                "capacity.0616.unit.operations.application-scm-coordination"
            ),
            "claim_ref": _stable_id(claim_ref, "claim_ref"),
            "expiry_time": expiry_time,
            "recipient_id": TECHNICAL_ACTOR_ID,
            "request_id": _stable_id(request_id, "request_id"),
            "request_version": _version(request_version, "request_version"),
            "requested_check": requested_check,
            "review_condition_ref": _stable_id(
                review_condition_ref, "review_condition_ref"
            ),
            "route_id": (
                "route.0616.operations_to_technical.verification_request"
            ),
            "sender_id": OPERATIONS_ACTOR_ID,
            "source_delivery_ref": finding_delivery.delivery_ref,
            "source_finding_id": finding_values["finding_id"],
            "source_finding_version": finding_values["finding_version"],
            "source_message_ref": finding_message["message_intent_id"],
            "urgency": urgency,
        }
        return LineageDecision(
            decision_policy_id=self.OPERATIONS_POLICY_ID,
            action_key="operations.request_fact_verification",
            commitment_ids=(
                "h2epr.commitment.0616."
                "ihis_operational_and_scm_management.situation_a",
            ),
            semantic_parameters=parameters,
        )

    def decide_escalate_operational_concern(
        self,
        observation: Mapping[str, Any],
        *,
        finding_action: Mapping[str, Any],
        finding_message: Mapping[str, Any],
        finding_delivery: MessageDelivery,
        verification_action: Mapping[str, Any],
        verification_message: Mapping[str, Any],
        verification_delivery: MessageDelivery,
        verification_result: VerificationResult,
        account_id: str,
        account_version: int,
        event_time_ref: str,
        known_fact_refs: Sequence[str],
        uncertainty: str,
        action_ref_ids: Sequence[str],
        open_question_refs: Sequence[str],
        requested_decision: str,
        expiry_time: Mapping[str, Any] | None,
    ) -> LineageDecision:
        self.binding.validate_message(
            "technical.share_technical_finding", finding_action, finding_message
        )
        self.binding.validate_message(
            "operations.request_fact_verification",
            verification_action,
            verification_message,
        )
        _require_delivery(
            finding_delivery,
            action=finding_action,
            message=finding_message,
            recipient_id=OPERATIONS_ACTOR_ID,
            label="technical_finding",
        )
        _require_delivery(
            verification_delivery,
            action=verification_action,
            message=verification_message,
            recipient_id=TECHNICAL_ACTOR_ID,
            label="verification_request",
        )
        finding_values = self.binding.semantic_values(finding_action)
        request_values = self.binding.semantic_values(verification_action)
        if (
            not verification_result.delivered
            or verification_result.request_intent_id
            != verification_action["intent_id"]
            or verification_result.request_id != request_values["request_id"]
            or verification_result.finding_id != finding_values["finding_id"]
            or verification_result.finding_version
            != finding_values["finding_version"]
        ):
            raise LineageBindingError("LINEAGE_VERIFICATION_LINEAGE_MISMATCH")
        values = self.binding.read_observation(
            "operations.escalate_operational_concern", observation
        )
        if (
            values["delivered_role_local_account"]
            != finding_message["message_intent_id"]
            or values["verification_result_notice"] != verification_result.result_id
            or values["management_route_context"]
            != "opening.0616.route.operations-gcio"
        ):
            raise LineageBindingError("LINEAGE_ESCALATION_BASIS_MISMATCH")
        _require_reopening_lifecycle(
            values["intent_lifecycle_notice"], "operational_escalation"
        )
        source_refs = _sorted_ids(
            (
                finding_message["message_intent_id"],
                verification_message["message_intent_id"],
                verification_result.result_id,
            ),
            "source_refs",
        )
        parameters = {
            "account_id": _stable_id(account_id, "account_id"),
            "account_version": _version(account_version, "account_version"),
            "action_ref_ids": _sorted_ids(action_ref_ids, "action_ref_ids"),
            "capacity_id": (
                "capacity.0616.unit.operations.application-scm-coordination"
            ),
            "event_time_ref": _stable_id(event_time_ref, "event_time_ref"),
            "expiry_time": expiry_time,
            "known_fact_refs": _sorted_ids(known_fact_refs, "known_fact_refs"),
            "open_question_refs": _sorted_ids(
                open_question_refs, "open_question_refs"
            ),
            "recipient_id": GCIO_ACTOR_ID,
            "requested_decision": requested_decision,
            "route_id": "route.0616.operations_to_gcio.escalation",
            "sender_id": OPERATIONS_ACTOR_ID,
            "source_delivery_refs": _sorted_ids(
                (
                    finding_delivery.delivery_ref,
                    verification_delivery.delivery_ref,
                    verification_result.delivery_ref,
                ),
                "source_delivery_refs",
            ),
            "source_finding_id": finding_values["finding_id"],
            "source_finding_version": finding_values["finding_version"],
            "source_refs": source_refs,
            "uncertainty": uncertainty,
            "verification_request_id": request_values["request_id"],
            "verification_request_version": request_values["request_version"],
            "verification_result_ref": verification_result.result_id,
            "verification_result_version": verification_result.result_version,
            "verification_status": verification_result.status,
        }
        return LineageDecision(
            decision_policy_id=self.OPERATIONS_POLICY_ID,
            action_key="operations.escalate_operational_concern",
            commitment_ids=(
                "h2epr.commitment.0616."
                "ihis_operational_and_scm_management.situation_b",
            ),
            semantic_parameters=parameters,
        )

    def decide_request_operational_clarification(
        self,
        observation: Mapping[str, Any],
        *,
        escalation_action: Mapping[str, Any],
        escalation_message: Mapping[str, Any],
        escalation_delivery: MessageDelivery,
        clarification_id: str,
        clarification_version: int,
        question_ref: str,
        scope_ref: str,
        urgency: str,
        review_condition_ref: str,
        expiry_time: Mapping[str, Any] | None,
    ) -> LineageDecision:
        self.binding.validate_message(
            "operations.escalate_operational_concern",
            escalation_action,
            escalation_message,
        )
        _require_delivery(
            escalation_delivery,
            action=escalation_action,
            message=escalation_message,
            recipient_id=GCIO_ACTOR_ID,
            label="operational_escalation",
        )
        values = self.binding.read_observation(
            "gcio.request_operational_clarification", observation
        )
        if values["delivered_operational_account"] != escalation_message[
            "message_intent_id"
        ]:
            raise LineageBindingError("LINEAGE_CLARIFICATION_BASIS_MISMATCH")
        _require_reopening_lifecycle(
            values["intent_lifecycle_notice"], "operational_clarification"
        )
        account_values = self.binding.semantic_values(escalation_action)
        parameters = {
            "capacity_id": "capacity.0616.ihis.gcio-service-lead",
            "cited_account_id": account_values["account_id"],
            "cited_account_version": account_values["account_version"],
            "cited_delivery_ref": escalation_delivery.delivery_ref,
            "cited_message_ref": escalation_message["message_intent_id"],
            "clarification_id": _stable_id(
                clarification_id, "clarification_id"
            ),
            "clarification_version": _version(
                clarification_version, "clarification_version"
            ),
            "expiry_time": expiry_time,
            "question_ref": _stable_id(question_ref, "question_ref"),
            "recipient_id": OPERATIONS_ACTOR_ID,
            "reply_route_id": "route.0616.operations_to_gcio.escalation",
            "review_condition_ref": _stable_id(
                review_condition_ref, "review_condition_ref"
            ),
            "route_id": "route.0616.gcio_to_operations.clarification",
            "scope_ref": _stable_id(scope_ref, "scope_ref"),
            "sender_id": GCIO_ACTOR_ID,
            "urgency": urgency,
        }
        return LineageDecision(
            decision_policy_id=self.GCIO_POLICY_ID,
            action_key="gcio.request_operational_clarification",
            commitment_ids=(
                "h2epr.commitment.0616."
                "singhealth_group_chief_information_officer.DC-GCIO-1",
            ),
            semantic_parameters=parameters,
        )


__all__ = [
    "GCIO_ACTOR_ID",
    "OPERATIONS_ACTOR_ID",
    "TECHNICAL_ACTOR_ID",
    "LineageDecision",
    "PositiveLineagePoliciesV0_1",
]
