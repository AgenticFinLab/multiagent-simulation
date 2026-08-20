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

    delivered_disposition = observation["delivered_disposition"]
    if (
        delivered_disposition == "facility_scoped_decline"
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
                reason_codes=("reason.delivered_scoped_decline_requires_adaptation",),
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
        information_request != "none"
        and observation.availability("received_information_request") == "delivered"
    ):
        package_status = observation["collateral_package_status"]
        authorization = observation["corporate_authorization"]
        request_status = observation["support_request_status"]
        if authorization == "authorized" and package_status in {
            "bounded_unknown",
            "prepared_bounded",
        } and request_status == "awaiting_information":
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
                    ],
                    "provenance_ref_ids": [
                        "claim.fixture.bounded_information_only"
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
        return _plan(
            observation,
            state,
            commitment_ids=("DC-KT-03",),
            reason_codes=("reason.equivalent_request_unresolved",),
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
        asset_status == "missing"
        or package_status == "missing"
        or observation.freshness("asset_liquidity_assessment") != "current"
        or observation.freshness("collateral_package_status") != "current"
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
        authority_refs=("authority.kt.support_request.001",),
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
    case_status = observation["case_disposition_status"]
    review_state = observation["review_state"]
    delivered_request = observation["delivered_request"]

    if (
        case_status == "case_received"
        and observation.availability("delivered_request") == "delivered"
    ):
        relationship = observation["relationship_status"]
        route = observation["route_classification"]
        eligibility = observation["facility_eligibility"]
        mandate = observation["request_authorization_evidence"]
        unresolved = []
        if mandate != "authorized":
            unresolved.append("field.request_authorization")
        unresolved.append("field.financial_information")
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-01",),
            reason_codes=("reason.delivered_request_requires_classification",),
            semantic_id="record_and_classify_request",
            parameters={
                "case_id": "case.kt_nych.001",
                "channel_id": "channel.nbc_mediated",
                "facility_id": "facility.nych.member_support",
                "relationship_ref": "relationship.kt_nbc_nych.001",
                "represented_institution_id": KT_ID,
                "route_class": route,
                "sender_id": KT_ID,
                "source_request_id": delivered_request,
                "unresolved_field_ids": unresolved,
            },
            authority_refs=("authority.nych.intake.001",),
        )

    if case_status == "case_classified":
        information = observation["financial_information_status"]
        mandate = observation["request_authorization_evidence"]
        disposition = observation["case_communication_status"]
        if information != "adequate_for_scope":
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-01", "DC-NYCH-02"),
                reason_codes=("reason.named_case_information_missing",),
                semantic_id="request_case_information",
                parameters={
                    "case_id": "case.kt_nych.001",
                    "information_category_ids": [
                        "information.asset_liquidity_assessment",
                        "information.collateral_package_status",
                    ],
                    "information_request_id": "information_request.nych.kt.001",
                    "recipient_id": KT_ID,
                    "required_as_of": "time.focal_information_package",
                    "scope_id": "scope.nych.facility_classification",
                },
                authority_refs=("authority.nych.case_information.001",),
            )
        return _plan(
            observation,
            state,
            commitment_ids=("DC-NYCH-02",),
            reason_codes=(
                f"reason.classified_case_no_procedural_step.{mandate}.{disposition}",
            ),
        )

    if case_status == "case_under_review" and review_state in {
        "not_open",
        "collecting_information",
    }:
        information = observation["financial_information_status"]
        authority = observation["authority_state"]
        if authority != "authorized":
            return _plan(
                observation,
                state,
                commitment_ids=("DC-NYCH-02",),
                reason_codes=("reason.review_authority_not_available",),
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
            authority_refs=("authority.nych.facility_disposition.001",),
        )

    if case_status == "case_disposition_ready":
        eligibility = observation["facility_eligibility"]
        route = observation["route_classification"]
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
                    "issuing_authority_ref": "authority.nych.facility_disposition.001",
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
        commitment_ids=("DC-NYCH-01",),
        reason_codes=("reason.no_due_procedural_response",),
    )


__all__ = [
    "DecisionPlan",
    "KT_ID",
    "NYCH_ID",
    "ObservedValues",
    "decide_knickerbocker",
    "decide_nych",
]
