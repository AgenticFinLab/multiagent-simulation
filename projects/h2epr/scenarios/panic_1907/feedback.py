"""Deterministic policy-and-binding feedback matrix for the first two roles."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from h2epr.agents import load_executable_mapping

from .policies import KT_ID, NYCH_ID, decide_knickerbocker, decide_nych


@dataclass(frozen=True)
class BehaviorFeedbackResult:
    """Outcome of one synthetic, non-simulation behavior perturbation."""

    case_id: str
    actor_id: str
    expected_semantic_id: str | None
    actual_semantic_id: str | None
    expected_commitment_ids: tuple[str, ...]
    actual_commitment_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    binding_valid: bool
    passed: bool
    expected_rejection: str | None = None
    diagnostic: str | None = None


@dataclass(frozen=True)
class _BehaviorCase:
    case_id: str
    actor_id: str
    values: Mapping[str, Any]
    metadata: Mapping[str, Mapping[str, str]]
    participant_state: Mapping[str, Any]
    expected_semantic_id: str | None
    expected_commitment_ids: tuple[str, ...]
    expected_rejection: str | None = None


def _metadata(actor_id: str, values: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    return {
        name: {
            "authoritative_record_ref": f"record.feedback.{actor_id}.{name}",
            "as_of": "1907-10-21T12:00:00-05:00",
            "freshness": "current",
            "availability": "delivered",
            "scope_id": f"scope.feedback.{actor_id}",
        }
        for name in values
    }


def _kt_case(
    case_id: str,
    expected_semantic_id: str | None,
    expected_commitment_ids: tuple[str, ...],
    *,
    values: Mapping[str, Any] | None = None,
    freshness: Mapping[str, str] | None = None,
    availability: Mapping[str, str] | None = None,
    participant_state: Mapping[str, Any] | None = None,
    expected_rejection: str | None = None,
) -> _BehaviorCase:
    actual_values = {
        "asset_liquidity_assessment": "unknown",
        "clearing_channel_status": "active",
        "collateral_package_status": "available",
        "corporate_authorization": "authorized",
        "delivered_disposition": ["none", None],
        "internal_liquidity_assessment": "critical",
        "received_information_request": None,
        "support_request_status": "none",
        "withdrawal_pressure": "severe",
    }
    actual_values.update(copy.deepcopy(dict(values or {})))
    metadata = _metadata(KT_ID, actual_values)
    metadata["corporate_authorization"]["authoritative_record_ref"] = (
        "authority.kt.support_request.001"
    )
    metadata["corporate_authorization"]["scope_id"] = (
        "scope.kt.support_request"
    )
    metadata["delivered_disposition"]["availability"] = "unavailable"
    metadata["received_information_request"]["availability"] = "unavailable"
    for name, value in dict(freshness or {}).items():
        metadata[name]["freshness"] = value
    for name, value in dict(availability or {}).items():
        metadata[name]["availability"] = value
    state = {
        "last_verified_condition_time": "time.focal_synthetic_input",
        "operational_posture": "ordinary",
        "request_strategy_posture": "no_active_request",
    }
    state.update(copy.deepcopy(dict(participant_state or {})))
    return _BehaviorCase(
        case_id,
        KT_ID,
        actual_values,
        metadata,
        state,
        expected_semantic_id,
        expected_commitment_ids,
        expected_rejection,
    )


def _nych_case(
    case_id: str,
    expected_semantic_id: str | None,
    expected_commitment_ids: tuple[str, ...],
    *,
    values: Mapping[str, Any] | None = None,
    availability: Mapping[str, str] | None = None,
    record_refs: Mapping[str, str] | None = None,
    participant_state: Mapping[str, Any] | None = None,
    expected_rejection: str | None = None,
) -> _BehaviorCase:
    actual_values = {
        "authority_state": "authorized",
        "case_communication_status": "not_issued",
        "case_disposition_status": ["none", None],
        "delivered_case_result": ["none", None],
        "delivered_request": "request.kt.support.001",
        "facility_eligibility": "ineligible",
        "financial_information_status": "incomplete",
        "relationship_status": "relationship.nonmember_clearing",
        "request_authorization_evidence": "sufficient",
        "resource_proposal_status": "none",
        "review_state": "not_open",
        "route_classification": "unresolved",
    }
    actual_values.update(copy.deepcopy(dict(values or {})))
    metadata = _metadata(NYCH_ID, actual_values)
    metadata["authority_state"]["authoritative_record_ref"] = (
        "authority.nych.case_process.001"
    )
    metadata["authority_state"]["scope_id"] = {
        "authorized": "scope.nych.facility_classification",
        "committee_scope": "forum.nych.executive_committee",
        "membership_scope_required": "forum.nych.membership",
    }.get(
        actual_values["authority_state"],
        "scope.nych.no_competent_forum_identified",
    )
    metadata["request_authorization_evidence"]["scope_id"] = (
        "scope.kt.support_request"
    )
    metadata["delivered_case_result"]["availability"] = "unavailable"
    for name, value in dict(availability or {}).items():
        metadata[name]["availability"] = value
    for name, value in dict(record_refs or {}).items():
        metadata[name]["authoritative_record_ref"] = value
    state = {
        "last_consumed_record_versions": "none",
        "procedural_assessment_posture": "case_received",
    }
    state.update(copy.deepcopy(dict(participant_state or {})))
    return _BehaviorCase(
        case_id,
        NYCH_ID,
        actual_values,
        metadata,
        state,
        expected_semantic_id,
        expected_commitment_ids,
        expected_rejection,
    )


def behavior_feedback_cases() -> tuple[_BehaviorCase, ...]:
    """Return the frozen Cycle 4 perturbations; none starts a simulator."""

    return (
        _kt_case(
            "CC-01",
            "verify_internal_condition",
            ("DC-KT-01",),
            freshness={"internal_liquidity_assessment": "stale"},
        ),
        _kt_case(
            "CC-02",
            "verify_internal_condition",
            ("DC-KT-01",),
            values={
                "internal_liquidity_assessment": "strained",
                "withdrawal_pressure": "ordinary",
            },
        ),
        _kt_case(
            "CC-03",
            "verify_internal_condition",
            ("DC-KT-01",),
            values={"internal_liquidity_assessment": "unknown"},
        ),
        _kt_case("CC-04", "submit_support_request", ("DC-KT-02",)),
        _kt_case(
            "CC-05",
            None,
            ("DC-KT-03",),
            values={"support_request_status": "under_review"},
            participant_state={"request_strategy_posture": "active_request"},
        ),
        _kt_case(
            "FB-KT-AUTHORITY",
            "seek_institutional_authorization",
            ("DC-KT-01", "DC-KT-02"),
            values={"corporate_authorization": "pending"},
        ),
        _kt_case(
            "FB-KT-CHANNEL",
            "request_channel_confirmation",
            ("DC-KT-02",),
            values={"clearing_channel_status": "inactive"},
        ),
        _kt_case(
            "FB-KT-CONTENT",
            "prepare_information_package",
            ("DC-KT-01", "DC-KT-02"),
            values={"collateral_package_status": "preparing"},
        ),
        _kt_case(
            "FB-KT-INFORMATION-REQUEST",
            "provide_requested_information",
            ("DC-KT-03",),
            values={
                "received_information_request": "information_request.nych.kt.001",
                "support_request_status": "awaiting_information",
            },
            availability={"received_information_request": "delivered"},
        ),
        _kt_case(
            "CC-10",
            "prepare_operational_contingency",
            ("DC-KT-04",),
            values={
                "delivered_disposition": ["refused", "facility_ineligible"]
            },
            availability={"delivered_disposition": "delivered"},
        ),
        _nych_case(
            "CC-06",
            None,
            ("DC-NYCH-01",),
            values={
                "delivered_request": None,
                "financial_information_status": "not_received",
                "request_authorization_evidence": "absent",
            },
            availability={"delivered_request": "unavailable"},
        ),
        _nych_case(
            "CC-07",
            "record_and_classify_request",
            ("DC-NYCH-01",),
        ),
        _nych_case(
            "FB-NYCH-INFORMATION",
            "request_case_information",
            ("DC-NYCH-01", "DC-NYCH-02"),
            values={"route_classification": "member_facility"},
        ),
        _nych_case(
            "FB-NYCH-AUTHORITY",
            "seek_procedural_authority",
            ("DC-NYCH-02",),
            values={
                "authority_state": "committee_scope",
                "financial_information_status": "adequate_for_scope",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "FB-NYCH-NO-COMPETENT-FORUM",
            None,
            ("DC-NYCH-02",),
            values={
                "authority_state": "unknown",
                "financial_information_status": "adequate_for_scope",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "FB-NYCH-OPEN-REVIEW",
            "open_or_continue_review",
            ("DC-NYCH-02",),
            values={
                "financial_information_status": "adequate_for_scope",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "FB-NYCH-CONTINUE-REVIEW",
            "open_or_continue_review",
            ("DC-NYCH-02",),
            values={
                "financial_information_status": "adequate_for_scope",
                "review_state": "collecting_information",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "CC-08",
            "issue_typed_decline",
            ("DC-NYCH-03", "DC-NYCH-05"),
            values={
                "financial_information_status": "adequate_for_scope",
                "review_state": "decision_ready",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "CC-09",
            "communicate_case_status",
            ("DC-NYCH-05",),
            values={
                "case_communication_status": "failed",
                "case_disposition_status": [
                    "facility_declined",
                    "facility_ineligible",
                ],
                "financial_information_status": "adequate_for_scope",
                "review_state": "decision_ready",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "FB-NYCH-NO-DUE-FOLLOW-UP",
            None,
            ("DC-NYCH-05",),
            values={
                "case_communication_status": "delivered",
                "case_disposition_status": [
                    "facility_declined",
                    "facility_ineligible",
                ],
                "financial_information_status": "adequate_for_scope",
                "review_state": "decision_ready",
                "route_classification": "member_facility",
            },
        ),
        _nych_case(
            "FB-NYCH-UNREACHABLE-PROPOSAL",
            None,
            (),
            values={
                "case_communication_status": "delivered",
                "case_disposition_status": [
                    "conditioned_proposal",
                    "conditions_recorded",
                ],
                "financial_information_status": "adequate_for_scope",
                "resource_proposal_status": "conditionally_authorized",
                "review_state": "decision_ready",
                "route_classification": "member_facility",
            },
            expected_rejection=(
                "conditioned_proposal_unreachable_in_conservative_variant"
            ),
        ),
        _nych_case(
            "FB-NYCH-RESULT-WITHOUT-PROPOSAL",
            None,
            (),
            values={
                "case_communication_status": "delivered",
                "case_disposition_status": [
                    "pending",
                    "review_pending",
                ],
                "delivered_case_result": ["failed", "execution_failed"],
                "financial_information_status": "adequate_for_scope",
                "review_state": "closed",
                "route_classification": "member_facility",
            },
            availability={"delivered_case_result": "delivered"},
            expected_rejection=(
                "proposal_result_unreachable_in_conservative_variant"
            ),
        ),
    )


def run_behavior_feedback_matrix(
    binding_path: str | Path,
) -> tuple[BehaviorFeedbackResult, ...]:
    """Evaluate policy responsiveness and exact binding conformance."""

    mapping = load_executable_mapping(Path(binding_path).resolve())
    results: list[BehaviorFeedbackResult] = []
    for case in behavior_feedback_cases():
        plan = None
        diagnostic = None
        binding_valid = False
        try:
            mapping.validate_observation_values(
                actor_id=case.actor_id,
                values=case.values,
                availability={
                    name: metadata["availability"]
                    for name, metadata in case.metadata.items()
                },
            )
            plan = (
                decide_knickerbocker(
                    case.values, case.metadata, case.participant_state
                )
                if case.actor_id == KT_ID
                else decide_nych(case.values, case.metadata, case.participant_state)
            )
            if plan.semantic_id is not None:
                projection = mapping.validate_semantic_intent(
                    actor_id=case.actor_id,
                    semantic_id=plan.semantic_id,
                    commitment_ids=plan.commitment_ids,
                    used_observations=plan.used_observations,
                    used_participant_state=plan.used_participant_state,
                    parameters=plan.parameters,
                    authority_refs=plan.authority_refs,
                    context=plan.context,
                )
                authority_observation = {
                    "close_or_reopen_review": "authority_state",
                    "communicate_case_status": "authority_state",
                    "issue_typed_decline": "authority_state",
                    "open_or_continue_review": "authority_state",
                    "submit_support_request": "corporate_authorization",
                }.get(plan.semantic_id)
                if authority_observation is not None:
                    expected_authority = case.metadata[authority_observation][
                        "authoritative_record_ref"
                    ]
                    if expected_authority not in projection.claimed_authority_refs:
                        raise ValueError(
                            "selected_intent_authority_not_observation_bound"
                        )
            else:
                participant = mapping.participants[case.actor_id]
                if (
                    not plan.commitment_ids
                    or not set(plan.commitment_ids)
                    <= set(participant.decision_commitments)
                ):
                    raise ValueError("no_intent_commitment_outside_definition")
                if (
                    not plan.used_observations
                    or not set(plan.used_observations) <= participant.observations
                ):
                    raise ValueError("no_intent_observation_basis_invalid")
                if not set(plan.used_participant_state) <= set(
                    participant.participant_state
                ):
                    raise ValueError("no_intent_participant_state_invalid")
                if not plan.reason_codes:
                    raise ValueError("no_intent_reason_missing")
            binding_valid = True
        except ValueError as error:
            diagnostic = f"{type(error).__name__}:{error}"

        actual_semantic_id = plan.semantic_id if plan is not None else None
        actual_commitments = plan.commitment_ids if plan is not None else ()
        if case.expected_rejection is not None:
            passed = (
                not binding_valid
                and diagnostic is not None
                and case.expected_rejection in diagnostic
            )
        else:
            passed = (
                binding_valid
                and actual_semantic_id == case.expected_semantic_id
                and actual_commitments == case.expected_commitment_ids
            )
        results.append(
            BehaviorFeedbackResult(
                case_id=case.case_id,
                actor_id=case.actor_id,
                expected_semantic_id=case.expected_semantic_id,
                actual_semantic_id=actual_semantic_id,
                expected_commitment_ids=case.expected_commitment_ids,
                actual_commitment_ids=actual_commitments,
                reason_codes=plan.reason_codes if plan is not None else (),
                binding_valid=binding_valid,
                passed=passed,
                expected_rejection=case.expected_rejection,
                diagnostic=diagnostic,
            )
        )
    return tuple(results)


__all__ = [
    "BehaviorFeedbackResult",
    "behavior_feedback_cases",
    "run_behavior_feedback_matrix",
]
