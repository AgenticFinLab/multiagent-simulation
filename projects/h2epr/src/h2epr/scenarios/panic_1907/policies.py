"""Conservative event-specific policies for the first two-role slice."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping


KT_ID = "knickerbocker_trust"
NYCH_ID = "new_york_clearing_house"


class ObservedValues(Mapping[str, Any]):
    """Read-only decision view that records the fields a policy consumed."""

    def __init__(
        self,
        values: Mapping[str, Any],
        metadata: Mapping[str, Mapping[str, str]],
    ) -> None:
        self._values = dict(values)
        self._metadata = {key: dict(value) for key, value in metadata.items()}
        if set(self._metadata) != set(self._values):
            raise ValueError("observation_metadata_inventory_mismatch")
        self._accessed: set[str] = set()

    def __getitem__(self, key: str) -> Any:
        self._accessed.add(key)
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    @property
    def accessed(self) -> tuple[str, ...]:
        return tuple(sorted(self._accessed))

    def freshness(self, key: str) -> str:
        self._accessed.add(key)
        return self._metadata[key]["freshness"]

    def availability(self, key: str) -> str:
        self._accessed.add(key)
        return self._metadata[key]["availability"]

    def record_ref(self, key: str) -> str:
        self._accessed.add(key)
        return self._metadata[key]["authoritative_record_ref"]

    def scope_id(self, key: str) -> str:
        self._accessed.add(key)
        return self._metadata[key]["scope_id"]

    def as_of(self, key: str) -> str:
        self._accessed.add(key)
        return self._metadata[key]["as_of"]


@dataclass(frozen=True)
class DecisionPlan:
    commitment_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    semantic_id: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    authority_refs: tuple[str, ...] = ()
    context: Mapping[str, Any] = field(default_factory=dict)
    used_observations: tuple[str, ...] = ()
    used_participant_state: tuple[str, ...] = ()


def _status_reason(value: Any, name: str) -> tuple[str, str | None]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"status_reason_pair_invalid:{name}")
    status, reason = value
    if not isinstance(status, str) or (
        reason is not None and not isinstance(reason, str)
    ):
        raise ValueError(f"status_reason_pair_invalid:{name}")
    return status, reason


def _plan(
    observation: ObservedValues,
    state: ObservedValues,
    *,
    commitment_ids: tuple[str, ...],
    reason_codes: tuple[str, ...],
    semantic_id: str | None = None,
    parameters: Mapping[str, Any] | None = None,
    authority_refs: tuple[str, ...] = (),
    context: Mapping[str, Any] | None = None,
) -> DecisionPlan:
    return DecisionPlan(
        commitment_ids=commitment_ids,
        reason_codes=reason_codes,
        semantic_id=semantic_id,
        parameters=dict(parameters or {}),
        authority_refs=authority_refs,
        context=dict(context or {}),
        used_observations=observation.accessed,
        used_participant_state=state.accessed,
    )


def decide_knickerbocker(
    observation_values: Mapping[str, Any],
    observation_metadata: Mapping[str, Mapping[str, str]],
    participant_state: Mapping[str, Any],
) -> DecisionPlan:
    """Select one bounded response from the current Knickerbocker Definition."""

    observation = ObservedValues(observation_values, observation_metadata)
    state = ObservedValues(
        participant_state,
        {
            name: {"freshness": "current", "availability": "delivered"}
            for name in participant_state
        },
    )

    delivered_disposition, disposition_reason = _status_reason(
        observation["delivered_disposition"], "delivered_disposition"
    )
    if (
        delivered_disposition == "refused"
        and observation.availability("delivered_disposition") == "delivered"
    ):
        posture = state["operational_posture"]
        pressure = observation["withdrawal_pressure"]
        liquidity = observation["internal_liquidity_assessment"]
        channel = observation["clearing_channel_status"]
        authorization = observation["corporate_authorization"]
        if posture == "ordinary" and authorization == "authorized":
            return _plan(
                observation,
                state,
                commitment_ids=("DC-KT-04",),
                reason_codes=(
                    "reason.delivered_scoped_decline_requires_adaptation",
                    f"reason.disposition.{disposition_reason}",
                ),
                semantic_id="prepare_operational_contingency",
                parameters={
                    "contingency_id": "contingency.kt.after_decline.001",
                    "preparation_class_id": "preparation.liquidity_operations",
                    "revisit_trigger_id": "trigger.new_authoritative_result_or_channel_event",
                    "scope_id": "scope.kt.operational_preparation",
                },
                authority_refs=("authority.kt.operational_preparation.001",),
            )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-04",),
            reason_codes=(
                "reason.adverse_disposition_classified_no_new_permitted_response",
                f"reason.current_posture.{posture}",
                f"reason.current_pressure.{pressure}",
                f"reason.current_liquidity.{liquidity}",
                f"reason.current_channel.{channel}",
            ),
        )

    information_request = observation["received_information_request"]
    if (
        information_request is not None
        and observation.availability("received_information_request") == "delivered"
    ):
        package_status = observation["collateral_package_status"]
        authorization = observation["corporate_authorization"]
        request_status = observation["support_request_status"]
        if (
            authorization == "authorized"
            and package_status in {"available", "submitted", "disputed", "unknown"}
            and request_status == "awaiting_information"
        ):
            return _plan(
                observation,
                state,
                commitment_ids=("DC-KT-03",),
                reason_codes=("reason.delivered_information_request_answerable",),
                semantic_id="provide_requested_information",
                parameters={
                    "as_of": "time.focal_information_package",
                    "case_id": "case.kt_nych.001",
                    "disclosure_scope_id": "scope.kt.case_information",
                    "information_item_ids": [
                        "information.asset_liquidity_assessment",
                        "information.collateral_package_status",
                        "information.request_authorization_evidence",
                    ],
                    "provenance_ref_ids": [
                        "claim.fixture.bounded_information_only",
                        observation.record_ref("corporate_authorization"),
                    ],
                    "recipient_id": NYCH_ID,
                    "request_id": "request.kt.support.001",
                },
                authority_refs=("authority.kt.case_disclosure.001",),
            )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-03",),
            reason_codes=("reason.information_response_blocked",),
        )

    request_status = observation["support_request_status"]
    if request_status in {
        "prepared",
        "sent",
        "delivered",
        "awaiting_information",
        "under_review",
    }:
        request_posture = state["request_strategy_posture"]
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-03",),
            reason_codes=(
                "reason.equivalent_request_unresolved",
                f"reason.request_strategy_posture.{request_posture}",
            ),
        )

    liquidity = observation["internal_liquidity_assessment"]
    pressure = observation["withdrawal_pressure"]
    if (
        observation.freshness("internal_liquidity_assessment") != "current"
        or observation.freshness("withdrawal_pressure") != "current"
        or liquidity not in {"strained", "critical"}
        or pressure not in {"elevated", "severe"}
    ):
        last_verified = state["last_verified_condition_time"]
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-01",),
            reason_codes=(
                "reason.material_pressure_gate_open",
                f"reason.last_verified_condition_time.{last_verified}",
            ),
            semantic_id="verify_internal_condition",
            parameters={
                "information_category_ids": [
                    "information.internal_liquidity",
                    "information.withdrawal_pressure",
                ],
                "required_as_of": "time.current_decision_point",
                "responsible_interface_id": "interface.kt.internal_information",
                "verification_request_id": "verification.kt.condition.001",
            },
            authority_refs=("authority.kt.ordinary_information.001",),
        )

    authorization = observation["corporate_authorization"]
    if authorization != "authorized":
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-01", "DC-KT-02"),
            reason_codes=("reason.scoped_authorization_gate_open",),
            semantic_id="seek_institutional_authorization",
            parameters={
                "authorization_request_id": "authorization_request.kt.support.001",
                "scope_id": "scope.kt.support_request",
                "supporting_information_status": "adequate_for_scope",
            },
            authority_refs=("authority.kt.request_governance_decision.001",),
        )

    channel = observation["clearing_channel_status"]
    if (
        channel != "active"
        or observation.freshness("clearing_channel_status") != "current"
        or observation.availability("clearing_channel_status") != "delivered"
    ):
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-02",),
            reason_codes=("reason.active_route_gate_open",),
            semantic_id="request_channel_confirmation",
            parameters={
                "channel_id": "channel.nbc_mediated",
                "confirmation_request_id": "confirmation.kt.channel.001",
                "recipient_id": "national_bank_of_commerce",
                "relationship_ref": "relationship.kt_nbc_clearing",
                "relevant_time": "time.current_decision_point",
            },
            authority_refs=("authority.kt.channel_inquiry.001",),
        )

    asset_status = observation["asset_liquidity_assessment"]
    package_status = observation["collateral_package_status"]
    if (
        observation.availability("asset_liquidity_assessment") != "delivered"
        or observation.availability("collateral_package_status") != "delivered"
        or observation.freshness("asset_liquidity_assessment") != "current"
        or observation.freshness("collateral_package_status") != "current"
        or package_status in {"not_prepared", "preparing"}
    ):
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-01", "DC-KT-02"),
            reason_codes=("reason.request_content_gate_open",),
            semantic_id="prepare_information_package",
            parameters={
                "as_of": "time.current_decision_point",
                "disclosure_scope_id": "scope.kt.support_request",
                "information_category_ids": [
                    "information.asset_liquidity_assessment",
                    "information.collateral_package_status",
                ],
                "package_id": "package.kt.bounded.001",
            },
            authority_refs=("authority.kt.information_preparation.001",),
        )

    return _plan(
        observation,
        state,
        commitment_ids=("DC-KT-02",),
        reason_codes=("reason.all_five_qualitative_gates_closed",),
        semantic_id="submit_support_request",
        parameters={
            "channel_id": "channel.nbc_mediated",
            "expiry_time": None,
            "package_ref_ids": ["package.kt.bounded.001"],
            "qualitative_bound": "amount_unknown",
            "recipient_id": NYCH_ID,
            "request_id": "request.kt.support.001",
            "resource_category_id": "resource.liquidity_support",
            "route_id": "route.nbc_mediated.nych",
            "withdrawal_condition_ids": ["condition.channel_withdrawal"],
        },
        authority_refs=(observation.record_ref("corporate_authorization"),),
        context={"package_material_exists": True},
    )


def decide_nych(
    observation_values: Mapping[str, Any],
    observation_metadata: Mapping[str, Mapping[str, str]],
    participant_state: Mapping[str, Any],
) -> DecisionPlan:
    """Select a conservative procedural response without an invented route."""

    observation = ObservedValues(observation_values, observation_metadata)
    state = ObservedValues(
        participant_state,
        {
            name: {"freshness": "current", "availability": "delivered"}
            for name in participant_state
        },
    )
    delivered_request = observation["delivered_request"]
    route = observation["route_classification"]

    if (
        delivered_request is None
        or observation.availability("delivered_request") != "delivered"
    ):
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-01",),
            reason_codes=("reason.no_delivered_request_no_case_action",),
        )

    if route == "unresolved":
        relationship = observation["relationship_status"]
        eligibility = observation["facility_eligibility"]
        mandate = observation["request_authorization_evidence"]
        classified_route = (
            "member_facility"
            if eligibility in {"eligible", "ineligible"}
            else "unresolved"
        )
        unresolved = []
        if mandate != "sufficient":
            unresolved.append("field.request_authorization")
        if classified_route == "unresolved":
            unresolved.append("field.route_classification")
        unresolved.append("field.financial_information")
        parameters = {
            "case_id": "case.kt_nych.001",
            "channel_id": "channel.nbc_mediated",
            "relationship_ref": observation.record_ref("relationship_status"),
            "represented_institution_id": KT_ID,
            "route_class": classified_route,
            "sender_id": KT_ID,
            "source_request_id": delivered_request,
            "unresolved_field_ids": unresolved,
        }
        if classified_route == "member_facility":
            parameters["facility_id"] = "facility.nych.member_support"
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-01",),
            reason_codes=(
                "reason.delivered_request_requires_classification",
                f"reason.relationship_class.{relationship}",
            ),
            semantic_id="record_and_classify_request",
            parameters=parameters,
            authority_refs=("authority.nych.intake.001",),
        )

    case_disposition, disposition_reason = _status_reason(
        observation["case_disposition_status"], "case_disposition_status"
    )
    communication_state = observation["case_communication_status"]
    result_status, result_reason = _status_reason(
        observation["delivered_case_result"], "delivered_case_result"
    )
    review_state = observation["review_state"]

    if (
        result_status != "none"
        and observation.availability("delivered_case_result") == "delivered"
    ):
        authority = observation["authority_state"]
        if (
            authority == "authorized"
            and result_status == "executed"
            and review_state == "complete"
        ):
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-05",),
                reason_codes=(
                    "reason.delivered_execution_result_requires_case_closure",
                    f"reason.delivered_result.{result_reason}",
                ),
                semantic_id="close_or_reopen_review",
                parameters={
                    "authority_ref": observation.record_ref("authority_state"),
                    "case_id": "case.kt_nych.001",
                    "operation": "close",
                    "reason_code": "reason.executed_result_delivered",
                    "review_act_id": "review_act.nych.close_after_execution.001",
                },
            )
        if (
            authority == "authorized"
            and result_status in {"delayed", "partial", "failed", "withdrawn"}
            and review_state == "closed"
        ):
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-05",),
                reason_codes=(
                    "reason.delivered_adverse_result_requires_successor_review",
                    f"reason.delivered_result.{result_status}",
                    f"reason.delivered_result_detail.{result_reason}",
                ),
                semantic_id="close_or_reopen_review",
                parameters={
                    "authority_ref": observation.record_ref("authority_state"),
                    "case_id": "case.kt_nych.001",
                    "new_event_ref": observation.record_ref(
                        "delivered_case_result"
                    ),
                    "operation": "reopen",
                    "reason_code": f"reason.result_requires_review.{result_status}",
                    "review_act_id": "review_act.nych.reopen_after_result.001",
                },
            )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-05",),
            reason_codes=(
                "reason.delivered_result_follow_up_blocked",
                f"reason.current_review_state.{review_state}",
                f"reason.current_authority_state.{authority}",
            ),
        )

    if case_disposition != "none" and communication_state in {
        "not_issued",
        "expired",
        "failed",
    }:
        authority = observation["authority_state"]
        if authority == "authorized":
            effective_at = observation.as_of("case_disposition_status")
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-05",),
                reason_codes=(
                    "reason.case_disposition_requires_authorized_communication",
                    f"reason.communication_state.{communication_state}",
                ),
                semantic_id="communicate_case_status",
                parameters={
                    "audience_id": KT_ID,
                    "case_disposition_ref": observation.record_ref(
                        "case_disposition_status"
                    ),
                    "case_id": "case.kt_nych.001",
                    "communication_act_id": (
                        "communication_act.nych.case_status."
                        f"{case_disposition}.{communication_state}.001"
                    ),
                    "effective_time": {
                        "lower": effective_at,
                        "upper": effective_at,
                        "precision": "exact_datetime",
                        "timezone": "America/New_York",
                        "uncertainty": "synthetic conformance fixture coordinate",
                    },
                    "issuing_authority_ref": observation.record_ref(
                        "authority_state"
                    ),
                    "procedural_state": (
                        f"status.case_disposition.{case_disposition}"
                    ),
                },
            )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-05",),
            reason_codes=(
                "reason.case_communication_authority_not_available",
                f"reason.current_authority_state.{authority}",
            ),
        )

    information = observation["financial_information_status"]
    if route != "unresolved" and review_state == "not_open" and (
        information != "adequate_for_scope"
    ):
        mandate = observation["request_authorization_evidence"]
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-01", "DC-NYCH-02"),
            reason_codes=(
                "reason.named_case_information_missing",
                f"reason.request_authorization_evidence.{mandate}",
            ),
            semantic_id="request_case_information",
            parameters={
                "case_id": "case.kt_nych.001",
                "information_category_ids": [
                    "information.asset_liquidity_assessment",
                    "information.collateral_package_status",
                    "information.request_authorization_evidence",
                ],
                "information_request_id": "information_request.nych.kt.001",
                "recipient_id": KT_ID,
                "required_as_of": "time.focal_information_package",
                "scope_id": "scope.nych.facility_classification",
            },
            authority_refs=("authority.nych.case_information.001",),
        )

    if information == "adequate_for_scope" and review_state in {
        "not_open",
        "collecting_information",
    }:
        authority = observation["authority_state"]
        if authority != "authorized":
            observation["facility_eligibility"]
            proposed_forum = observation.scope_id("authority_state")
            if authority not in {
                "committee_scope",
                "membership_scope_required",
            } or not proposed_forum.startswith("forum.nych."):
                return _plan(
                    observation,
                    state,
                    commitment_ids=("DC-NYCH-02",),
                    reason_codes=(
                        "reason.review_authority_not_available",
                        "reason.no_competent_forum_identified",
                        f"reason.current_authority_state.{authority}",
                    ),
                )
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-02",),
                reason_codes=(
                    "reason.review_authority_not_available",
                    f"reason.current_authority_state.{authority}",
                ),
                semantic_id="seek_procedural_authority",
                parameters={
                    "authority_question_id": (
                        "authority_question.nych.facility_review.001"
                    ),
                    "authority_request_id": (
                        "authority_request.nych.facility_review.001"
                    ),
                    "case_or_proposal_id": "case.kt_nych.001",
                    "proposed_forum_id": proposed_forum,
                    "route_id": f"route.nych.{route}",
                },
                authority_refs=("authority.nych.procedural_inquiry.001",),
            )
        desired = (
            "collecting_information"
            if review_state == "not_open"
            else "examining"
        )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-02",),
            reason_codes=(f"reason.review_transition.{review_state}_to_{desired}",),
            semantic_id="open_or_continue_review",
            parameters={
                "case_id": "case.kt_nych.001",
                "current_information_status": information,
                "desired_transition": desired,
                "review_act_id": f"review_act.nych.{desired}.001",
                "reviewing_interface_id": "interface.nych.scoped_review",
                "scope_id": "scope.nych.facility_classification",
            },
            authority_refs=(observation.record_ref("authority_state"),),
        )

    if review_state == "decision_ready" and case_disposition == "none":
        eligibility = observation["facility_eligibility"]
        authority = observation["authority_state"]
        if (
            eligibility == "ineligible"
            and route == "member_facility"
            and authority == "authorized"
        ):
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-03", "DC-NYCH-05"),
                reason_codes=("reason.member_facility_ineligible_scoped_only",),
                semantic_id="issue_typed_decline",
                parameters={
                    "case_id": "case.kt_nych.001",
                    "decline_act_id": "decline.nych.facility_scope.001",
                    "facility_or_route_scope_id": "facility.nych.member_support",
                    "issuing_authority_ref": observation.record_ref(
                        "authority_state"
                    ),
                    "reason_code": "facility_ineligible",
                    "recipient_id": KT_ID,
                },
            )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-03",),
            reason_codes=("reason.scoped_decline_prerequisites_not_met",),
        )

    return _plan(
        observation,
        state,
        commitment_ids=("DC-NYCH-05",),
        reason_codes=(
            "reason.no_due_procedural_response",
            f"reason.case_disposition.{case_disposition}",
            f"reason.case_disposition_detail.{disposition_reason or 'none'}",
        ),
    )


__all__ = [
    "DecisionPlan",
    "KT_ID",
    "NYCH_ID",
    "ObservedValues",
    "decide_knickerbocker",
    "decide_nych",
]
