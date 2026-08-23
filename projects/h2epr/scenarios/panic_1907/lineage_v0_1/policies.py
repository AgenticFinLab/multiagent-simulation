"""Positive-branch participant decisions for the bounded three-role lineage.

Unsupported branches fail closed.  They are not silently converted into a
fallback action; broader decision coverage remains outside this binding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from h2epr.bundles.canonical import sha256_value

from .binding import LineageBinding, LineageBindingError
from .environment import LineageEnvironmentV0_1


KT_ACTOR_ID = "actor.knickerbocker_trust"
NBC_ACTOR_ID = "actor.national_bank_of_commerce"
NYCH_ACTOR_ID = "actor.new_york_clearing_house"


@dataclass(frozen=True)
class LineageDecision:
    decision_policy_id: str
    action_key: str
    commitment_ids: tuple[str, ...]
    semantic_parameters: Mapping[str, Any]


class PositiveLineagePoliciesV0_1:
    """One deterministic, exposed conformance branch for KT, NBC, and NYCH."""

    KT_POLICY_ID = "h2epr.decision.0288.kt.gated_request.v0_1"
    NBC_POLICY_ID = "h2epr.decision.0288.nbc.pure_forward.v0_1"
    NYCH_POLICY_ID = "h2epr.decision.0288.nych.conservative_intake.v0_1"

    def __init__(self, binding: LineageBinding) -> None:
        self.binding = binding
        self.environment = LineageEnvironmentV0_1(binding)
        actual = {
            item["decision_policy_id"]: tuple(item["action_keys"])
            for item in binding.decision_bindings
        }
        expected = {
            self.KT_POLICY_ID: ("kt.submit_support_request",),
            self.NBC_POLICY_ID: ("nbc.forward_request_with_provenance",),
            self.NYCH_POLICY_ID: (
                "nych.issue_typed_decline",
                "nych.record_and_classify_request",
            ),
        }
        if actual != expected:
            raise LineageBindingError("LINEAGE_DECISION_POLICY_SET_MISMATCH")

    def decide_kt_request(
        self,
        observation: Mapping[str, Any],
        *,
        request_id: str,
        request_version: int,
        mandate_ref: str,
        withdrawal_condition_ids: Sequence[str],
        expiry_time: Mapping[str, Any] | None,
    ) -> LineageDecision:
        values = self.binding.read_observation(
            "kt.submit_support_request", observation
        )
        if (
            values["internal_liquidity_assessment"] not in {"strained", "critical"}
            or values["withdrawal_pressure"] not in {"elevated", "severe"}
            or values["corporate_authorization"] != "authorized"
            or values["clearing_channel_status"] != "active"
            or values["support_request_status"] != "none"
        ):
            raise LineageBindingError("LINEAGE_KT_POSITIVE_GATES_NOT_CLOSED")
        _stable_id(request_id, "request_id")
        _nonnegative_integer(request_version, "request_version")
        _stable_id(mandate_ref, "mandate_ref")
        withdrawal_ids = _sorted_ids(
            withdrawal_condition_ids, "withdrawal_condition_ids"
        )
        request_content = {
            "request_id": request_id,
            "request_version": request_version,
            "represented_sender_id": "entity.knickerbocker_trust",
            "final_recipient_id": NYCH_ACTOR_ID,
            "mandate_ref": mandate_ref,
            "route_id": "route.0288.kt_to_nbc.support_request",
            "channel_id": "channel.0288.kt_nbc.institutional_request",
            "resource_category_id": "resource.liquidity_support",
            "qualitative_bound": "amount_unknown",
            "withdrawal_condition_ids": list(withdrawal_ids),
            "expiry_time": expiry_time,
            "asset_liquidity_assessment": values["asset_liquidity_assessment"],
            "collateral_package_status": values["collateral_package_status"],
        }
        parameters = {
            "channel_id": request_content["channel_id"],
            "expiry_time": expiry_time,
            "final_recipient_id": request_content["final_recipient_id"],
            "mandate_ref": mandate_ref,
            "qualitative_bound": request_content["qualitative_bound"],
            "represented_sender_id": request_content["represented_sender_id"],
            "request_content_sha256": sha256_value(request_content),
            "request_id": request_id,
            "request_version": request_version,
            "resource_category_id": request_content["resource_category_id"],
            "route_id": request_content["route_id"],
            "withdrawal_condition_ids": list(withdrawal_ids),
        }
        return LineageDecision(
            decision_policy_id=self.KT_POLICY_ID,
            action_key="kt.submit_support_request",
            commitment_ids=("DC-KT-02",),
            semantic_parameters=parameters,
        )

    def decide_nbc_forward(
        self,
        observation: Mapping[str, Any],
        *,
        kt_action: Mapping[str, Any],
        kt_message: Mapping[str, Any],
    ) -> LineageDecision:
        self.binding.validate_message(
            "kt.submit_support_request", kt_action, kt_message
        )
        values = self.binding.read_observation(
            "nbc.forward_request_with_provenance", observation
        )
        if (
            values["counterparty_request"] != kt_message["message_intent_id"]
            or values["clearing_relationship_status"] != "active"
            or values["message_and_notice_status"] != "delivered"
            or values["nbc_corporate_authority"] != "authorized"
        ):
            raise LineageBindingError("LINEAGE_NBC_PURE_FORWARD_BASIS_MISSING")
        original = self.binding.semantic_values(kt_action)
        if (
            original["final_recipient_id"] != NYCH_ACTOR_ID
            or tuple(kt_message["recipient_ids"]) != (NBC_ACTOR_ID,)
        ):
            raise LineageBindingError("LINEAGE_NBC_ORIGINAL_ROUTE_MISMATCH")
        parameters = {
            "channel_id": "channel.0288.nbc_nych.institutional_forward",
            "expiry_time": original["expiry_time"],
            "final_recipient_id": NYCH_ACTOR_ID,
            "intermediary_role": "courier",
            "mandate_ref": original["mandate_ref"],
            "original_action_ref": kt_action["intent_id"],
            "original_message_ref": kt_message["message_intent_id"],
            "original_request_content_sha256": original[
                "request_content_sha256"
            ],
            "original_sender_id": KT_ACTOR_ID,
            "represented_sender_id": original["represented_sender_id"],
            "request_id": original["request_id"],
            "request_version": original["request_version"],
            "route_id": "route.0288.nbc_to_nych.support_request",
        }
        return LineageDecision(
            decision_policy_id=self.NBC_POLICY_ID,
            action_key="nbc.forward_request_with_provenance",
            commitment_ids=("DC-NBC-02",),
            semantic_parameters=parameters,
        )

    def decide_nych_classification(
        self,
        observation: Mapping[str, Any],
        *,
        nbc_action: Mapping[str, Any],
        nbc_message: Mapping[str, Any],
        case_id: str,
        case_version: int,
    ) -> LineageDecision:
        self.binding.validate_message(
            "nbc.forward_request_with_provenance", nbc_action, nbc_message
        )
        values = self.binding.read_observation(
            "nych.record_and_classify_request", observation
        )
        expected_relationships = (
            "rel.kt_nych.membership",
            "rel.nbc_nych.membership",
        )
        if (
            values["delivered_request"] != nbc_message["message_intent_id"]
            or tuple(values["relationship_status"]) != expected_relationships
            or values["route_classification"] != "nonmember_clearing_matter"
            or values["facility_eligibility"] != "not_applicable"
            or values["request_authorization_evidence"] != "sufficient"
        ):
            raise LineageBindingError("LINEAGE_NYCH_INTAKE_BASIS_MISMATCH")
        relationships = {
            row["record_id"]: row
            for row in self.binding.configuration.document["initial_records"][
                "relationships"
            ]
        }
        if (
            relationships["rel.kt_nych.membership"]["state"] != "nonmember"
            or relationships["rel.nbc_nych.membership"]["state"] != "active"
        ):
            raise LineageBindingError("LINEAGE_NYCH_RELATIONSHIP_STATE_MISMATCH")
        forward = self.binding.semantic_values(nbc_action)
        review = self.environment.classify_information(
            required_item_ids=(
                "item.mandate",
                "item.request_content",
                "item.route_provenance",
            ),
            present_item_ids=(
                "item.mandate",
                "item.request_content",
                "item.route_provenance",
            ),
        )
        parameters = {
            "authorization_evidence": values["request_authorization_evidence"],
            "case_id": _stable_id(case_id, "case_id"),
            "case_version": _nonnegative_integer(case_version, "case_version"),
            "delivered_message_ref": nbc_message["message_intent_id"],
            "expiry_time": forward["expiry_time"],
            "facility_eligibility": values["facility_eligibility"],
            "information_status": review.classification,
            "intermediary_id": NBC_ACTOR_ID,
            "intermediary_role": forward["intermediary_role"],
            "original_sender_id": forward["original_sender_id"],
            "relationship_ref_ids": list(expected_relationships),
            "request_id": forward["request_id"],
            "request_version": forward["request_version"],
            "route_classification": values["route_classification"],
            "unresolved_field_ids": ["authority.nych.alternative_route"],
        }
        return LineageDecision(
            decision_policy_id=self.NYCH_POLICY_ID,
            action_key="nych.record_and_classify_request",
            commitment_ids=("DC-NYCH-01",),
            semantic_parameters=parameters,
        )

    def decide_nych_scoped_decline(
        self,
        observation: Mapping[str, Any],
        *,
        classification_action: Mapping[str, Any],
        disposition_id: str,
        expiry_time: Mapping[str, Any] | None,
    ) -> LineageDecision:
        self.binding.validate_action(
            "nych.record_and_classify_request", classification_action
        )
        values = self.binding.read_observation(
            "nych.issue_typed_decline", observation
        )
        if (
            values["route_classification"] != "nonmember_clearing_matter"
            or values["facility_eligibility"] != "not_applicable"
            or values["authority_state"]
            != "no_competent_authority_identified"
            or values["review_state"] != "decision_ready"
            or values["case_disposition_status"] != "none"
        ):
            raise LineageBindingError("LINEAGE_NYCH_DECLINE_BASIS_MISMATCH")
        classified = self.binding.semantic_values(classification_action)
        parameters = {
            "case_id": classified["case_id"],
            "case_version": classified["case_version"] + 1,
            "channel_id": "channel.0288.nych_kt.case_result",
            "disposition_id": _stable_id(disposition_id, "disposition_id"),
            "disposition_scope_id": "scope.nych.alternative_route",
            "expiry_time": expiry_time,
            "reason_code": "no_competent_authority",
            "request_id": classified["request_id"],
            "request_version": classified["request_version"],
            "route_id": "route.0288.nych_to_kt.case_disposition",
            "scope_limit": "named_route_only_not_universal",
        }
        return LineageDecision(
            decision_policy_id=self.NYCH_POLICY_ID,
            action_key="nych.issue_typed_decline",
            commitment_ids=("DC-NYCH-03", "DC-NYCH-05"),
            semantic_parameters=parameters,
        )


def _stable_id(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
        or len(value) > 128
        or not value[0].isalnum()
        or any(
            character
            not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-"
            for character in value
        )
    ):
        raise LineageBindingError(f"LINEAGE_DECISION_STABLE_ID_INVALID:{label}")
    return value


def _nonnegative_integer(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise LineageBindingError(f"LINEAGE_DECISION_INTEGER_INVALID:{label}")
    return value


def _sorted_ids(value: Sequence[str], label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise LineageBindingError(f"LINEAGE_DECISION_IDS_INVALID:{label}")
    result = tuple(_stable_id(item, label) for item in value)
    if not result or len(result) != len(set(result)) or result != tuple(sorted(result)):
        raise LineageBindingError(f"LINEAGE_DECISION_IDS_INVALID:{label}")
    return result


__all__ = [
    "KT_ACTOR_ID",
    "LineageDecision",
    "NBC_ACTOR_ID",
    "NYCH_ACTOR_ID",
    "PositiveLineagePoliciesV0_1",
]
