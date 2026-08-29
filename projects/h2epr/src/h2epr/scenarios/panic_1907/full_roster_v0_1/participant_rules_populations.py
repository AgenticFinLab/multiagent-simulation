"""Panic Rule policies for the five released population capabilities."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .participant import RuleParticipantPolicy
from .specification import branch, decision, observation_id, policy, state_id


Domain = tuple[str, ...]


def _only(source: Mapping[str, Domain], names: Sequence[str]) -> dict[str, Domain]:
    return {name: source[name] for name in names}


def _o(capability: str, name: str) -> str:
    return observation_id(capability, name)


def _s(capability: str, name: str) -> str:
    return state_id(capability, name)


MIXED_SIGNAL_RULES: Domain = (
    "adverse_dominant",
    "reassurance_dominant",
    "need_only_under_conflict",
)
AMOUNT_METHODS: Domain = (
    "qualitative_bounded_band",
    "scenario_authorized_band",
    "fixed_sensitivity_within_capacity",
)


KDP = "knickerbocker_depositor"
KDP_OBSERVATIONS: Mapping[str, Domain] = {
    "remaining_claim": ("unknown", "positive", "zero"),
    "private_withdrawal_need": ("unknown", "none", "deferrable", "immediate"),
    "institution_signal": (
        "unknown",
        "neutral",
        "adverse",
        "reassuring",
        "mixed",
        "disputed",
    ),
    "service_access_observation": (
        "unknown",
        "normal",
        "delayed",
        "restricted",
        "unavailable",
    ),
    "peer_activity_observation": (
        "unknown",
        "none_observed",
        "limited",
        "substantial",
    ),
    "own_request_status": (
        "none",
        "created",
        "delivered",
        "pending",
        "partial",
        "paid",
        "failed",
        "expired",
        "cancelled",
    ),
    "own_request_result": (
        "none",
        "paid",
        "partial",
        "failed",
        "expired",
        "cancelled",
        "delayed",
        "unavailable",
    ),
}
KDP_STATE: Mapping[str, Domain] = {
    "withdrawal_need": ("unknown", "none", "deferrable", "immediate"),
    "response_profile": ("need_only", "signal_responsive", "access_responsive"),
    "dated_information_inventory": (
        "empty",
        "neutral",
        "adverse",
        "reassuring",
        "mixed",
        "disputed",
    ),
    "last_consumed_request_result_references": ("none", "consumed"),
}
KDP_PARAMETERS: Mapping[str, Domain] = {
    "response_profile": ("need_only", "signal_responsive", "access_responsive"),
    "mixed_signal_rule": MIXED_SIGNAL_RULES,
}


KNICKERBOCKER_DEPOSITOR_POLICY = policy(
    KDP,
    (
        decision(
            KDP,
            "PC-KDP-01",
            observation_domains=_only(
                KDP_OBSERVATIONS,
                ("remaining_claim", "private_withdrawal_need", "own_request_status"),
            ),
            state_domains=KDP_STATE,
            configuration_parameter_domains=KDP_PARAMETERS,
            branches=(
                branch(
                    KDP,
                    "request_withdrawal",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "private_withdrawal_need"): "immediate",
                        _o(KDP, "own_request_status"): "none",
                    },
                    state_updates={_s(KDP, "withdrawal_need"): "immediate"},
                ),
                branch(
                    KDP,
                    "retain_for_interval",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "private_withdrawal_need"): "none",
                        _o(KDP, "own_request_status"): "none",
                    },
                    state_updates={_s(KDP, "withdrawal_need"): "none"},
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
        decision(
            KDP,
            "PC-KDP-02",
            observation_domains=_only(
                KDP_OBSERVATIONS,
                (
                    "remaining_claim",
                    "private_withdrawal_need",
                    "institution_signal",
                    "own_request_status",
                ),
            ),
            state_domains=KDP_STATE,
            configuration_parameter_domains=KDP_PARAMETERS,
            branches=(
                branch(
                    KDP,
                    "request_withdrawal",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "institution_signal"): "adverse",
                        "response_profile": "signal_responsive",
                        _o(KDP, "own_request_status"): "none",
                    },
                    state_updates={
                        _s(KDP, "dated_information_inventory"): "adverse"
                    },
                ),
                branch(
                    KDP,
                    "request_withdrawal",
                    branch_name="request_withdrawal_mixed_adverse",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "institution_signal"): "mixed",
                        "response_profile": "signal_responsive",
                        "mixed_signal_rule": "adverse_dominant",
                        _o(KDP, "own_request_status"): "none",
                    },
                    state_updates={_s(KDP, "dated_information_inventory"): "mixed"},
                ),
                branch(
                    KDP,
                    "retain_for_interval",
                    when_all={
                        _o(KDP, "institution_signal"): "reassuring",
                        _o(KDP, "own_request_status"): "none",
                    },
                    state_updates={
                        _s(KDP, "dated_information_inventory"): "reassuring"
                    },
                ),
                branch(
                    KDP,
                    "await_request_result",
                    when_all={
                        _o(KDP, "own_request_status"): (
                            "created",
                            "delivered",
                            "pending",
                        )
                    },
                ),
            ),
            lifecycle_names=(
                "withdrawal_service_and_payment",
                "institutional_communication",
            ),
        ),
        decision(
            KDP,
            "PC-KDP-03",
            observation_domains=_only(
                KDP_OBSERVATIONS,
                (
                    "remaining_claim",
                    "private_withdrawal_need",
                    "service_access_observation",
                    "peer_activity_observation",
                    "own_request_status",
                    "own_request_result",
                ),
            ),
            state_domains=KDP_STATE,
            configuration_parameter_domains=KDP_PARAMETERS,
            branches=(
                branch(
                    KDP,
                    "request_withdrawal",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "service_access_observation"): (
                            "delayed",
                            "restricted",
                            "unavailable",
                        ),
                        "response_profile": "access_responsive",
                        _o(KDP, "own_request_status"): "none",
                    },
                ),
                branch(
                    KDP,
                    "request_withdrawal",
                    branch_name="request_withdrawal_peer_activity",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "peer_activity_observation"): "substantial",
                        "response_profile": "access_responsive",
                        _o(KDP, "own_request_status"): "none",
                    },
                ),
                branch(
                    KDP,
                    "retain_for_interval",
                    when_all={
                        _o(KDP, "service_access_observation"): "normal",
                        _o(KDP, "private_withdrawal_need"): "none",
                        _o(KDP, "own_request_status"): "none",
                    },
                ),
                branch(
                    KDP,
                    "await_request_result",
                    when_all={_o(KDP, "own_request_status"): "pending"},
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
        decision(
            KDP,
            "PC-KDP-04",
            observation_domains=_only(
                KDP_OBSERVATIONS,
                ("remaining_claim", "own_request_status", "own_request_result"),
            ),
            state_domains=KDP_STATE,
            configuration_parameter_domains=KDP_PARAMETERS,
            branches=(
                branch(
                    KDP,
                    "await_request_result",
                    when_all={
                        _o(KDP, "own_request_status"): (
                            "created",
                            "delivered",
                            "pending",
                        )
                    },
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
        decision(
            KDP,
            "PC-KDP-05",
            observation_domains=_only(
                KDP_OBSERVATIONS,
                (
                    "remaining_claim",
                    "private_withdrawal_need",
                    "service_access_observation",
                    "own_request_status",
                    "own_request_result",
                ),
            ),
            state_domains=KDP_STATE,
            configuration_parameter_domains=KDP_PARAMETERS,
            branches=(
                branch(
                    KDP,
                    "request_withdrawal",
                    when_all={
                        _o(KDP, "remaining_claim"): "positive",
                        _o(KDP, "own_request_result"): ("failed", "expired"),
                        _o(KDP, "own_request_status"): (
                            "failed",
                            "expired",
                            "cancelled",
                        ),
                    },
                ),
                branch(
                    KDP,
                    "retain_for_interval",
                    when_all={
                        _o(KDP, "own_request_result"): "paid",
                        _o(KDP, "remaining_claim"): "zero",
                    },
                    state_updates={
                        _s(
                            KDP, "last_consumed_request_result_references"
                        ): "consumed"
                    },
                ),
                branch(
                    KDP,
                    "await_request_result",
                    when_all={
                        _o(KDP, "own_request_result"): ("partial", "delayed")
                    },
                    state_updates={
                        _s(
                            KDP, "last_consumed_request_result_references"
                        ): "consumed"
                    },
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
    ),
    configuration_parameter_ids=tuple(KDP_PARAMETERS),
)


LDP = "later_trust_depositor"
LDP_OBSERVATIONS: Mapping[str, Domain] = {
    "host_institution": ("present", "missing"),
    "remaining_claim": ("unknown", "positive", "zero"),
    "private_withdrawal_need": ("unknown", "none", "deferrable", "immediate"),
    "host_signal": (
        "unknown",
        "neutral",
        "adverse",
        "reassuring",
        "mixed",
        "disputed",
    ),
    "public_contagion_signal": (
        "unknown",
        "neutral",
        "adverse",
        "reassuring",
        "mixed",
        "disputed",
    ),
    "service_access_observation": (
        "unknown",
        "normal",
        "delayed",
        "restricted",
        "unavailable",
    ),
    "peer_activity_observation": (
        "unknown",
        "none_observed",
        "limited",
        "substantial",
    ),
    "own_request_status": (
        "none",
        "created",
        "delivered",
        "pending",
        "partial",
        "paid",
        "failed",
        "expired",
        "cancelled",
        "unavailable",
    ),
    "own_request_result": (
        "none",
        "paid_cash",
        "paid_certified_check",
        "partial",
        "delayed",
        "failed",
        "expired",
        "cancelled",
        "unavailable",
    ),
}
LDP_STATE: Mapping[str, Domain] = {
    "private_need": ("unknown", "none", "deferrable", "immediate"),
    "response_profile_conflict_rule": (
        "need_only",
        "host_signal_responsive",
        "contagion_and_access_responsive",
        *MIXED_SIGNAL_RULES,
    ),
    "dated_information_inventory": (
        "empty",
        "neutral",
        "adverse",
        "reassuring",
        "mixed",
        "disputed",
    ),
    "last_consumed_request_result_references": ("none", "consumed"),
}
LDP_PARAMETERS: Mapping[str, Domain] = {
    "response_profile": (
        "need_only",
        "host_signal_responsive",
        "contagion_and_access_responsive",
    ),
    "mixed_signal_rule": MIXED_SIGNAL_RULES,
}


LATER_TRUST_DEPOSITOR_POLICY = policy(
    LDP,
    (
        decision(
            LDP,
            "PC-LDP-01",
            observation_domains=_only(
                LDP_OBSERVATIONS,
                (
                    "host_institution",
                    "remaining_claim",
                    "private_withdrawal_need",
                    "own_request_status",
                ),
            ),
            state_domains=LDP_STATE,
            configuration_parameter_domains=LDP_PARAMETERS,
            branches=(
                branch(
                    LDP,
                    "request_withdrawal",
                    when_all={
                        _o(LDP, "host_institution"): "present",
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "private_withdrawal_need"): "immediate",
                        _o(LDP, "own_request_status"): "none",
                    },
                    state_updates={_s(LDP, "private_need"): "immediate"},
                ),
                branch(
                    LDP,
                    "retain_for_interval",
                    when_all={
                        _o(LDP, "host_institution"): "present",
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "private_withdrawal_need"): "none",
                        _o(LDP, "own_request_status"): "none",
                    },
                    state_updates={_s(LDP, "private_need"): "none"},
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
        decision(
            LDP,
            "PC-LDP-02",
            observation_domains=_only(
                LDP_OBSERVATIONS,
                (
                    "host_institution",
                    "remaining_claim",
                    "private_withdrawal_need",
                    "host_signal",
                    "public_contagion_signal",
                    "own_request_status",
                ),
            ),
            state_domains=LDP_STATE,
            configuration_parameter_domains=LDP_PARAMETERS,
            branches=(
                branch(
                    LDP,
                    "request_withdrawal",
                    when_all={
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "host_signal"): "adverse",
                        "response_profile": (
                            "host_signal_responsive",
                            "contagion_and_access_responsive",
                        ),
                        _o(LDP, "own_request_status"): "none",
                    },
                    state_updates={
                        _s(LDP, "dated_information_inventory"): "adverse"
                    },
                ),
                branch(
                    LDP,
                    "request_withdrawal",
                    branch_name="request_withdrawal_public_contagion",
                    when_all={
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "public_contagion_signal"): "adverse",
                        "response_profile": "contagion_and_access_responsive",
                        _o(LDP, "own_request_status"): "none",
                    },
                    state_updates={
                        _s(LDP, "dated_information_inventory"): "adverse"
                    },
                ),
                branch(
                    LDP,
                    "request_withdrawal",
                    branch_name="request_withdrawal_mixed_adverse",
                    when_all={
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "host_signal"): "mixed",
                        "response_profile": (
                            "host_signal_responsive",
                            "contagion_and_access_responsive",
                        ),
                        "mixed_signal_rule": "adverse_dominant",
                        _o(LDP, "own_request_status"): "none",
                    },
                    state_updates={_s(LDP, "dated_information_inventory"): "mixed"},
                ),
                branch(
                    LDP,
                    "retain_for_interval",
                    when_all={
                        _o(LDP, "host_signal"): "reassuring",
                        _o(LDP, "own_request_status"): "none",
                    },
                    state_updates={
                        _s(LDP, "dated_information_inventory"): "reassuring"
                    },
                ),
                branch(
                    LDP,
                    "await_request_result",
                    when_all={_o(LDP, "own_request_status"): "pending"},
                ),
            ),
            lifecycle_names=(
                "withdrawal_service_and_payment",
                "institutional_communication",
            ),
        ),
        decision(
            LDP,
            "PC-LDP-03",
            observation_domains=_only(
                LDP_OBSERVATIONS,
                (
                    "host_institution",
                    "remaining_claim",
                    "private_withdrawal_need",
                    "service_access_observation",
                    "peer_activity_observation",
                    "own_request_status",
                    "own_request_result",
                ),
            ),
            state_domains=LDP_STATE,
            configuration_parameter_domains=LDP_PARAMETERS,
            branches=(
                branch(
                    LDP,
                    "request_withdrawal",
                    when_all={
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "service_access_observation"): (
                            "delayed",
                            "restricted",
                            "unavailable",
                        ),
                        "response_profile": "contagion_and_access_responsive",
                        _o(LDP, "own_request_status"): "none",
                    },
                ),
                branch(
                    LDP,
                    "request_withdrawal",
                    branch_name="request_withdrawal_peer_activity",
                    when_all={
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "peer_activity_observation"): "substantial",
                        "response_profile": "contagion_and_access_responsive",
                        _o(LDP, "own_request_status"): "none",
                    },
                ),
                branch(
                    LDP,
                    "retain_for_interval",
                    when_all={
                        _o(LDP, "service_access_observation"): "normal",
                        _o(LDP, "private_withdrawal_need"): "none",
                        _o(LDP, "own_request_status"): "none",
                    },
                ),
                branch(
                    LDP,
                    "await_request_result",
                    when_all={_o(LDP, "own_request_status"): "pending"},
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
        decision(
            LDP,
            "PC-LDP-04",
            observation_domains=_only(
                LDP_OBSERVATIONS,
                (
                    "host_institution",
                    "remaining_claim",
                    "own_request_status",
                    "own_request_result",
                ),
            ),
            state_domains=LDP_STATE,
            configuration_parameter_domains=LDP_PARAMETERS,
            branches=(
                branch(
                    LDP,
                    "await_request_result",
                    when_all={
                        _o(LDP, "own_request_status"): (
                            "created",
                            "delivered",
                            "pending",
                        )
                    },
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
        decision(
            LDP,
            "PC-LDP-05",
            observation_domains=_only(
                LDP_OBSERVATIONS,
                (
                    "host_institution",
                    "remaining_claim",
                    "private_withdrawal_need",
                    "service_access_observation",
                    "own_request_status",
                    "own_request_result",
                ),
            ),
            state_domains=LDP_STATE,
            configuration_parameter_domains=LDP_PARAMETERS,
            branches=(
                branch(
                    LDP,
                    "request_withdrawal",
                    when_all={
                        _o(LDP, "remaining_claim"): "positive",
                        _o(LDP, "own_request_result"): ("failed", "expired"),
                        _o(LDP, "own_request_status"): (
                            "failed",
                            "expired",
                            "cancelled",
                            "unavailable",
                        ),
                    },
                ),
                branch(
                    LDP,
                    "retain_for_interval",
                    when_all={
                        _o(LDP, "own_request_result"): (
                            "paid_cash",
                            "paid_certified_check",
                        ),
                        _o(LDP, "remaining_claim"): "zero",
                    },
                    state_updates={
                        _s(
                            LDP, "last_consumed_request_result_references"
                        ): "consumed"
                    },
                ),
                branch(
                    LDP,
                    "await_request_result",
                    when_all={
                        _o(LDP, "own_request_result"): ("partial", "delayed")
                    },
                    state_updates={
                        _s(
                            LDP, "last_consumed_request_result_references"
                        ): "consumed"
                    },
                ),
            ),
            lifecycle_names=("withdrawal_service_and_payment",),
        ),
    ),
    configuration_parameter_ids=tuple(LDP_PARAMETERS),
)


BANK = "bank_resource_decision"
BANK_OBSERVATIONS: Mapping[str, Domain] = {
    "institution_profile": ("present", "missing", "disputed"),
    "decision_authority": ("absent", "authorized", "pending", "denied", "disputed"),
    "own_resource_envelope": (
        "unknown",
        "unavailable",
        "constrained",
        "bounded_available",
    ),
    "solicitation_or_request": ("absent", "complete", "incomplete", "disputed"),
    "applicant_information": ("absent", "incomplete", "adequate", "disputed"),
    "facility_state": (
        "inactive",
        "active_eligible",
        "active_ineligible",
        "unknown",
    ),
    "own_collateral_projection": (
        "none",
        "controlled_nonzero",
        "ineligible",
        "disputed",
        "unknown",
    ),
    "commitment_or_application_state": (
        "none",
        "offer_pending",
        "committed",
        "application_pending",
        "partial",
        "failed",
        "executed",
        "expired",
        "cancelled",
    ),
    "relationship_or_exposure_observation": (
        "none",
        "qualifying",
        "nonqualifying",
        "disputed",
    ),
}
BANK_STATE: Mapping[str, Domain] = {
    "participation_posture": (
        "obligation_only",
        "relationship_conditioned",
        "collective_support_permissive",
    ),
    "information_inventory": ("empty", "incomplete", "adequate", "consumed"),
    "last_consumed_offer_application_resource_versions": ("none", "consumed"),
}
BANK_PARAMETERS: Mapping[str, Domain] = {
    "participation_posture": (
        "obligation_only",
        "relationship_conditioned",
        "collective_support_permissive",
    ),
    "certificate_use_posture": (
        "no_certificate_use",
        "material_need_conditioned",
        "early_access_permissive",
    ),
    "amount_method": AMOUNT_METHODS,
}


BANK_RESOURCE_DECISION_POLICY = policy(
    BANK,
    (
        decision(
            BANK,
            "PC-CBC-01",
            observation_domains=_only(
                BANK_OBSERVATIONS,
                (
                    "institution_profile",
                    "decision_authority",
                    "own_resource_envelope",
                    "solicitation_or_request",
                    "applicant_information",
                    "commitment_or_application_state",
                    "relationship_or_exposure_observation",
                ),
            ),
            state_domains=BANK_STATE,
            configuration_parameter_domains=BANK_PARAMETERS,
            branches=(
                branch(
                    BANK,
                    "request_proposal_information",
                    when_all={_o(BANK, "solicitation_or_request"): "incomplete"},
                    state_updates={_s(BANK, "information_inventory"): "incomplete"},
                ),
                branch(
                    BANK,
                    "refer_or_decline_proposal",
                    when_all={_o(BANK, "decision_authority"): "denied"},
                ),
                branch(
                    BANK,
                    "make_conditional_contribution_offer",
                    when_all={
                        _o(BANK, "applicant_information"): "adequate",
                        _o(BANK, "own_resource_envelope"): "constrained",
                        "participation_posture": (
                            "relationship_conditioned",
                            "collective_support_permissive",
                        ),
                    },
                ),
                branch(
                    BANK,
                    "commit_owned_resource",
                    when_all={
                        _o(BANK, "applicant_information"): "adequate",
                        _o(BANK, "own_resource_envelope"): "bounded_available",
                        "participation_posture": "collective_support_permissive",
                    },
                ),
                branch(
                    BANK,
                    "await_commitment_or_application_result",
                    when_all={
                        _o(BANK, "commitment_or_application_state"): "offer_pending"
                    },
                ),
            ),
            lifecycle_names=(
                "solicitation_and_independent_reply",
                "resource_commitment_and_execution",
            ),
        ),
        decision(
            BANK,
            "PC-CBC-02",
            observation_domains=_only(
                BANK_OBSERVATIONS,
                (
                    "institution_profile",
                    "decision_authority",
                    "own_resource_envelope",
                    "solicitation_or_request",
                    "applicant_information",
                    "relationship_or_exposure_observation",
                ),
            ),
            state_domains=BANK_STATE,
            configuration_parameter_domains=BANK_PARAMETERS,
            branches=(
                branch(
                    BANK,
                    "request_proposal_information",
                    when_all={_o(BANK, "applicant_information"): "incomplete"},
                    state_updates={_s(BANK, "information_inventory"): "incomplete"},
                ),
                branch(
                    BANK,
                    "refer_or_decline_proposal",
                    when_all={_o(BANK, "decision_authority"): "denied"},
                ),
                branch(
                    BANK,
                    "make_conditional_contribution_offer",
                    when_all={
                        _o(BANK, "decision_authority"): "authorized",
                        _o(BANK, "own_resource_envelope"): "constrained",
                    },
                ),
                branch(
                    BANK,
                    "commit_owned_resource",
                    when_all={
                        _o(BANK, "decision_authority"): "authorized",
                        _o(BANK, "own_resource_envelope"): "bounded_available",
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "governance_and_authority",
                "resource_commitment_and_execution",
            ),
        ),
        decision(
            BANK,
            "PC-CBC-03",
            observation_domains=_only(
                BANK_OBSERVATIONS,
                (
                    "decision_authority",
                    "own_resource_envelope",
                    "solicitation_or_request",
                    "applicant_information",
                    "relationship_or_exposure_observation",
                ),
            ),
            state_domains=BANK_STATE,
            configuration_parameter_domains=BANK_PARAMETERS,
            branches=(
                branch(
                    BANK,
                    "refer_or_decline_proposal",
                    when_all={
                        _o(BANK, "solicitation_or_request"): "complete",
                        "participation_posture": "obligation_only",
                    },
                ),
                branch(
                    BANK,
                    "make_conditional_contribution_offer",
                    when_all={
                        _o(
                            BANK, "relationship_or_exposure_observation"
                        ): "qualifying",
                        "participation_posture": "relationship_conditioned",
                    },
                ),
                branch(
                    BANK,
                    "commit_owned_resource",
                    when_all={
                        _o(BANK, "own_resource_envelope"): "bounded_available",
                        "participation_posture": "collective_support_permissive",
                    },
                ),
            ),
            lifecycle_names=("resource_commitment_and_execution",),
        ),
        decision(
            BANK,
            "PC-CBC-04",
            observation_domains=_only(
                BANK_OBSERVATIONS,
                (
                    "decision_authority",
                    "own_resource_envelope",
                    "commitment_or_application_state",
                ),
            ),
            state_domains=BANK_STATE,
            configuration_parameter_domains=BANK_PARAMETERS,
            branches=(
                branch(
                    BANK,
                    "revise_or_cancel_commitment",
                    when_all={
                        _o(BANK, "commitment_or_application_state"): (
                            "partial",
                            "failed",
                            "expired",
                        )
                    },
                ),
                branch(
                    BANK,
                    "await_commitment_or_application_result",
                    when_all={
                        _o(BANK, "commitment_or_application_state"): (
                            "offer_pending",
                            "committed",
                        )
                    },
                ),
            ),
            lifecycle_names=("resource_commitment_and_execution",),
        ),
        decision(
            BANK,
            "PC-CBC-05",
            observation_domains=_only(
                BANK_OBSERVATIONS,
                (
                    "institution_profile",
                    "decision_authority",
                    "own_resource_envelope",
                    "facility_state",
                    "own_collateral_projection",
                    "commitment_or_application_state",
                ),
            ),
            state_domains=BANK_STATE,
            configuration_parameter_domains=BANK_PARAMETERS,
            branches=(
                branch(
                    BANK,
                    "apply_for_member_certificate",
                    when_all={
                        _o(BANK, "decision_authority"): "authorized",
                        _o(BANK, "facility_state"): "active_eligible",
                        _o(BANK, "own_collateral_projection"): "controlled_nonzero",
                        _o(BANK, "commitment_or_application_state"): "none",
                        "certificate_use_posture": (
                            "material_need_conditioned",
                            "early_access_permissive",
                        ),
                    },
                ),
                branch(
                    BANK,
                    "submit_controlled_collateral",
                    when_all={
                        _o(BANK, "facility_state"): "active_eligible",
                        _o(BANK, "own_collateral_projection"): "controlled_nonzero",
                        _o(
                            BANK, "commitment_or_application_state"
                        ): "application_pending",
                    },
                ),
            ),
            lifecycle_names=("collateral_and_facility_application",),
        ),
        decision(
            BANK,
            "PC-CBC-06",
            observation_domains=_only(
                BANK_OBSERVATIONS,
                (
                    "own_resource_envelope",
                    "own_collateral_projection",
                    "commitment_or_application_state",
                ),
            ),
            state_domains=BANK_STATE,
            configuration_parameter_domains=BANK_PARAMETERS,
            branches=(
                branch(
                    BANK,
                    "revise_or_cancel_commitment",
                    when_all={
                        _o(BANK, "commitment_or_application_state"): (
                            "partial",
                            "failed",
                            "expired",
                        )
                    },
                    state_updates={
                        _s(
                            BANK, "last_consumed_offer_application_resource_versions"
                        ): "consumed"
                    },
                ),
                branch(
                    BANK,
                    "await_commitment_or_application_result",
                    when_all={
                        _o(BANK, "commitment_or_application_state"): (
                            "offer_pending",
                            "committed",
                            "application_pending",
                        )
                    },
                ),
            ),
            lifecycle_names=(
                "resource_commitment_and_execution",
                "collateral_and_facility_application",
            ),
        ),
    ),
    configuration_parameter_ids=tuple(BANK_PARAMETERS),
)


LENDER = "call_money_lender"
LENDER_OBSERVATIONS: Mapping[str, Domain] = {
    "institution_profile": ("present", "missing", "disputed"),
    "decision_authority": ("absent", "authorized", "pending", "denied", "disputed"),
    "own_resource_envelope": (
        "unknown",
        "unavailable",
        "constrained",
        "bounded_available",
    ),
    "own_liquidity_need": (
        "unknown",
        "stable",
        "constrained",
        "material_recovery_need",
    ),
    "existing_call_loan": ("absent", "active", "incomplete", "disputed", "closed"),
    "contractual_status": (
        "current",
        "unknown",
        "review_due",
        "call_right_available",
        "call_required",
    ),
    "borrower_request": ("absent", "complete", "incomplete", "disputed"),
    "borrower_information": ("absent", "incomplete", "adequate", "disputed"),
    "collateral_projection": (
        "none",
        "controlled",
        "conditionable",
        "ineligible",
        "disputed",
    ),
    "term_assessment_basis": ("absent", "complete", "incomplete", "disputed"),
    "market_or_pool_route": (
        "unavailable",
        "direct",
        "regular_bank",
        "loan_stand",
        "pool",
        "unknown",
    ),
    "market_observation": ("absent", "current", "stressed", "disputed"),
    "own_loan_lifecycle": (
        "none",
        "call_pending",
        "offer_pending",
        "offer_failed",
        "matched",
        "booked",
        "repaid",
        "defaulted",
        "expired",
        "closed",
    ),
}
LENDER_STATE: Mapping[str, Domain] = {
    "existing_exposure_posture": (
        "contractual_continuation_baseline",
        "liquidity_recovery",
        "relationship_accommodation",
    ),
    "new_lending_posture": (
        "no_new_call_credit",
        "relationship_conditioned",
        "market_support_permissive",
    ),
    "term_compatibility_assessment": (
        "unknown",
        "within_current_envelope",
        "bounded_change_required",
        "outside_current_envelope",
    ),
    "information_inventory": ("empty", "incomplete", "adequate", "consumed"),
    "last_consumed_lifecycle_resource_versions": ("none", "consumed"),
}
LENDER_PARAMETERS: Mapping[str, Domain] = {
    "existing_exposure_posture": (
        "contractual_continuation_baseline",
        "liquidity_recovery",
        "relationship_accommodation",
    ),
    "new_lending_posture": (
        "no_new_call_credit",
        "relationship_conditioned",
        "market_support_permissive",
    ),
    "amount_method": AMOUNT_METHODS,
}


CALL_MONEY_LENDER_POLICY = policy(
    LENDER,
    (
        decision(
            LENDER,
            "PC-CML-01",
            observation_domains=_only(
                LENDER_OBSERVATIONS,
                (
                    "institution_profile",
                    "decision_authority",
                    "own_resource_envelope",
                    "own_liquidity_need",
                    "existing_call_loan",
                    "contractual_status",
                    "borrower_information",
                    "term_assessment_basis",
                    "market_observation",
                    "own_loan_lifecycle",
                ),
            ),
            state_domains=LENDER_STATE,
            configuration_parameter_domains=LENDER_PARAMETERS,
            branches=(
                branch(
                    LENDER,
                    "request_call_loan_information",
                    when_all={
                        _o(LENDER, "contractual_status"): "unknown",
                        _o(LENDER, "own_loan_lifecycle"): "none",
                    },
                    state_updates={
                        _s(LENDER, "information_inventory"): "incomplete"
                    },
                ),
                branch(
                    LENDER,
                    "continue_call_loan_for_interval",
                    when_all={
                        _o(LENDER, "contractual_status"): "current",
                        _s(
                            LENDER, "term_compatibility_assessment"
                        ): "within_current_envelope",
                    },
                ),
                branch(
                    LENDER,
                    "propose_call_loan_term_change",
                    when_all={
                        _o(LENDER, "contractual_status"): "review_due",
                        _s(
                            LENDER, "term_compatibility_assessment"
                        ): "bounded_change_required",
                    },
                ),
                branch(
                    LENDER,
                    "issue_call_or_reduction_notice",
                    when_all={_o(LENDER, "contractual_status"): "call_required"},
                ),
                branch(
                    LENDER,
                    "await_call_loan_result",
                    when_all={_o(LENDER, "own_loan_lifecycle"): "call_pending"},
                ),
            ),
            lifecycle_names=("call_loan_contract",),
        ),
        decision(
            LENDER,
            "PC-CML-02",
            observation_domains=_only(
                LENDER_OBSERVATIONS,
                (
                    "decision_authority",
                    "own_resource_envelope",
                    "own_liquidity_need",
                    "existing_call_loan",
                    "contractual_status",
                    "term_assessment_basis",
                    "own_loan_lifecycle",
                ),
            ),
            state_domains=LENDER_STATE,
            configuration_parameter_domains=LENDER_PARAMETERS,
            branches=(
                branch(
                    LENDER,
                    "request_call_loan_information",
                    when_all={
                        _o(LENDER, "decision_authority"): "absent",
                        _o(LENDER, "contractual_status"): "unknown",
                    },
                ),
                branch(
                    LENDER,
                    "continue_call_loan_for_interval",
                    when_all={
                        _o(LENDER, "contractual_status"): "current",
                        _s(
                            LENDER, "term_compatibility_assessment"
                        ): "within_current_envelope",
                        "existing_exposure_posture": (
                            "contractual_continuation_baseline",
                            "relationship_accommodation",
                        ),
                    },
                ),
                branch(
                    LENDER,
                    "propose_call_loan_term_change",
                    when_all={
                        _s(
                            LENDER, "term_compatibility_assessment"
                        ): "bounded_change_required"
                    },
                ),
                branch(
                    LENDER,
                    "issue_call_or_reduction_notice",
                    when_all={_o(LENDER, "contractual_status"): "call_required"},
                ),
                branch(
                    LENDER,
                    "issue_call_or_reduction_notice",
                    branch_name="issue_call_for_liquidity_recovery",
                    when_all={
                        _o(LENDER, "contractual_status"): "call_right_available",
                        _o(LENDER, "own_liquidity_need"): "material_recovery_need",
                        "existing_exposure_posture": "liquidity_recovery",
                    },
                ),
            ),
            lifecycle_names=("call_loan_contract",),
        ),
        decision(
            LENDER,
            "PC-CML-03",
            observation_domains=_only(
                LENDER_OBSERVATIONS,
                (
                    "decision_authority",
                    "own_resource_envelope",
                    "borrower_request",
                    "borrower_information",
                    "collateral_projection",
                    "term_assessment_basis",
                    "market_or_pool_route",
                    "market_observation",
                    "own_loan_lifecycle",
                ),
            ),
            state_domains=LENDER_STATE,
            configuration_parameter_domains=LENDER_PARAMETERS,
            branches=(
                branch(
                    LENDER,
                    "request_call_loan_information",
                    when_all={_o(LENDER, "borrower_information"): "incomplete"},
                    state_updates={
                        _s(LENDER, "information_inventory"): "incomplete"
                    },
                ),
                branch(
                    LENDER,
                    "make_conditional_call_loan_offer",
                    when_all={
                        _o(LENDER, "borrower_request"): "complete",
                        _s(
                            LENDER, "term_compatibility_assessment"
                        ): "within_current_envelope",
                        "new_lending_posture": (
                            "relationship_conditioned",
                            "market_support_permissive",
                        ),
                    },
                ),
                branch(
                    LENDER,
                    "decline_call_loan_request",
                    when_all={
                        _o(LENDER, "borrower_request"): "complete",
                        "new_lending_posture": "no_new_call_credit",
                    },
                ),
                branch(
                    LENDER,
                    "await_call_loan_result",
                    when_all={_o(LENDER, "own_loan_lifecycle"): "offer_pending"},
                ),
            ),
            lifecycle_names=(
                "replacement_funding",
                "call_loan_contract",
            ),
        ),
        decision(
            LENDER,
            "PC-CML-04",
            observation_domains=_only(
                LENDER_OBSERVATIONS,
                (
                    "decision_authority",
                    "own_resource_envelope",
                    "borrower_request",
                    "borrower_information",
                    "collateral_projection",
                    "term_assessment_basis",
                    "market_or_pool_route",
                    "market_observation",
                ),
            ),
            state_domains=LENDER_STATE,
            configuration_parameter_domains=LENDER_PARAMETERS,
            branches=(
                branch(
                    LENDER,
                    "make_conditional_call_loan_offer",
                    when_all={
                        _o(LENDER, "decision_authority"): "authorized",
                        _o(LENDER, "own_resource_envelope"): "bounded_available",
                        _s(
                            LENDER, "term_compatibility_assessment"
                        ): "within_current_envelope",
                        "new_lending_posture": (
                            "relationship_conditioned",
                            "market_support_permissive",
                        ),
                    },
                ),
                branch(
                    LENDER,
                    "decline_call_loan_request",
                    when_all={
                        _o(LENDER, "borrower_request"): "complete",
                        "new_lending_posture": "no_new_call_credit",
                    },
                ),
            ),
            lifecycle_names=("replacement_funding",),
        ),
        decision(
            LENDER,
            "PC-CML-05",
            observation_domains=_only(
                LENDER_OBSERVATIONS,
                (
                    "own_resource_envelope",
                    "existing_call_loan",
                    "borrower_request",
                    "own_loan_lifecycle",
                ),
            ),
            state_domains=LENDER_STATE,
            configuration_parameter_domains=LENDER_PARAMETERS,
            branches=(
                branch(
                    LENDER,
                    "revise_or_cancel_call_loan_offer",
                    when_all={
                        _o(LENDER, "own_loan_lifecycle"): (
                            "offer_failed",
                            "expired",
                        )
                    },
                    state_updates={
                        _s(
                            LENDER, "last_consumed_lifecycle_resource_versions"
                        ): "consumed"
                    },
                ),
                branch(
                    LENDER,
                    "await_call_loan_result",
                    when_all={
                        _o(LENDER, "own_loan_lifecycle"): (
                            "call_pending",
                            "offer_pending",
                            "matched",
                            "booked",
                        )
                    },
                ),
            ),
            lifecycle_names=(
                "call_loan_contract",
                "replacement_funding",
            ),
        ),
    ),
    configuration_parameter_ids=tuple(LENDER_PARAMETERS),
)


BORROWER = "call_money_broker_borrower"
BORROWER_OBSERVATIONS: Mapping[str, Domain] = {
    "borrower_profile": ("present", "missing", "disputed"),
    "decision_authority": ("absent", "authorized", "partial", "denied", "disputed"),
    "call_obligation": ("absent", "valid", "incomplete", "disputed", "closed"),
    "controlled_resource_projection": ("unknown", "none", "partial", "sufficient"),
    "funding_route": (
        "unavailable",
        "regular_bank",
        "direct",
        "loan_stand",
        "pool",
        "unknown",
    ),
    "collateral_package": (
        "none",
        "controlled",
        "stale",
        "disputed",
        "unknown",
    ),
    "settlement_obligation": ("none", "current", "material_due", "unknown"),
    "funding_offer": (
        "none",
        "compatible",
        "conditionable",
        "incompatible",
        "expired",
        "disputed",
    ),
    "own_business_lifecycles": (
        "none",
        "clarification_pending",
        "clarification_failed",
        "funding_request_pending",
        "funding_request_expired",
        "collateral_revision_required",
        "offer_pending",
        "offer_received_compatible",
        "offer_received_conditionable",
        "offer_received_incompatible",
        "booked",
        "repayment_due",
        "repayment_pending",
        "reduction_authorized",
        "reduction_pending",
        "funding_routes_exhausted",
        "partial",
        "failed",
        "expired",
        "closed",
    ),
    "market_observation": ("absent", "current", "stressed", "disputed"),
}
BORROWER_STATE: Mapping[str, Domain] = {
    "funding_response_posture": (
        "renewal_or_replacement_first",
        "parallel_funding_and_reduction",
        "controlled_repayment_first",
    ),
    "information_inventory": ("empty", "incomplete", "adequate", "consumed"),
    "last_consumed_business_record_versions": ("none", "consumed"),
}
BORROWER_PARAMETERS: Mapping[str, Domain] = {
    "funding_response_posture": (
        "renewal_or_replacement_first",
        "parallel_funding_and_reduction",
        "controlled_repayment_first",
    ),
    "amount_method": AMOUNT_METHODS,
}


CALL_MONEY_BROKER_BORROWER_POLICY = policy(
    BORROWER,
    (
        decision(
            BORROWER,
            "PC-CMB-01",
            observation_domains=_only(
                BORROWER_OBSERVATIONS,
                (
                    "borrower_profile",
                    "decision_authority",
                    "call_obligation",
                    "own_business_lifecycles",
                ),
            ),
            state_domains=BORROWER_STATE,
            configuration_parameter_domains=BORROWER_PARAMETERS,
            branches=(
                branch(
                    BORROWER,
                    "request_call_or_term_clarification",
                    when_all={
                        _o(BORROWER, "call_obligation"): (
                            "incomplete",
                            "disputed",
                        )
                    },
                    state_updates={
                        _s(BORROWER, "information_inventory"): "incomplete"
                    },
                ),
            ),
            lifecycle_names=("call_loan_contract",),
        ),
        decision(
            BORROWER,
            "PC-CMB-02",
            observation_domains=_only(
                BORROWER_OBSERVATIONS,
                (
                    "decision_authority",
                    "call_obligation",
                    "controlled_resource_projection",
                    "funding_route",
                    "settlement_obligation",
                    "own_business_lifecycles",
                ),
            ),
            state_domains=BORROWER_STATE,
            configuration_parameter_domains=BORROWER_PARAMETERS,
            branches=(
                branch(
                    BORROWER,
                    "authorize_controlled_repayment",
                    when_all={
                        _o(BORROWER, "controlled_resource_projection"): "sufficient",
                        "funding_response_posture": "controlled_repayment_first",
                    },
                ),
                branch(
                    BORROWER,
                    "request_call_loan_renewal_or_replacement",
                    when_all={
                        _o(BORROWER, "controlled_resource_projection"): "partial",
                        _o(BORROWER, "funding_route"): "regular_bank",
                        "funding_response_posture": "renewal_or_replacement_first",
                    },
                ),
                branch(
                    BORROWER,
                    "request_authorized_position_reduction",
                    when_all={
                        _o(BORROWER, "decision_authority"): "authorized",
                        "funding_response_posture": "parallel_funding_and_reduction",
                    },
                ),
                branch(
                    BORROWER,
                    "record_funding_inability",
                    when_all={
                        _o(BORROWER, "controlled_resource_projection"): "none",
                        _o(BORROWER, "funding_route"): "unavailable",
                    },
                ),
                branch(
                    BORROWER,
                    "await_funding_or_repayment_result",
                    when_all={
                        _o(BORROWER, "own_business_lifecycles"): (
                            "clarification_pending",
                            "funding_request_pending",
                            "offer_pending",
                            "repayment_pending",
                            "reduction_pending",
                        )
                    },
                ),
            ),
            lifecycle_names=(
                "call_loan_contract",
                "replacement_funding",
                "position_reduction_and_venue_execution",
            ),
        ),
        decision(
            BORROWER,
            "PC-CMB-03",
            observation_domains=_only(
                BORROWER_OBSERVATIONS,
                (
                    "decision_authority",
                    "call_obligation",
                    "funding_route",
                    "collateral_package",
                    "own_business_lifecycles",
                    "market_observation",
                ),
            ),
            state_domains=BORROWER_STATE,
            configuration_parameter_domains=BORROWER_PARAMETERS,
            branches=(
                branch(
                    BORROWER,
                    "request_call_loan_renewal_or_replacement",
                    when_all={
                        _o(BORROWER, "funding_route"): (
                            "regular_bank",
                            "direct",
                            "loan_stand",
                            "pool",
                        ),
                        _o(BORROWER, "own_business_lifecycles"): "none",
                    },
                ),
                branch(
                    BORROWER,
                    "submit_controlled_collateral_proposal",
                    when_all={
                        _o(BORROWER, "collateral_package"): "controlled",
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "funding_request_pending",
                    },
                ),
                branch(
                    BORROWER,
                    "await_funding_or_repayment_result",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "funding_request_pending"
                    },
                ),
            ),
            lifecycle_names=(
                "replacement_funding",
                "collateral_and_facility_application",
            ),
        ),
        decision(
            BORROWER,
            "PC-CMB-04",
            observation_domains=_only(
                BORROWER_OBSERVATIONS,
                (
                    "decision_authority",
                    "funding_route",
                    "collateral_package",
                    "funding_offer",
                    "own_business_lifecycles",
                    "market_observation",
                ),
            ),
            state_domains=BORROWER_STATE,
            configuration_parameter_domains=BORROWER_PARAMETERS,
            branches=(
                branch(
                    BORROWER,
                    "submit_controlled_collateral_proposal",
                    when_all={
                        _o(BORROWER, "collateral_package"): "controlled",
                        _o(BORROWER, "funding_offer"): "none",
                    },
                ),
                branch(
                    BORROWER,
                    "accept_call_loan_offer",
                    when_all={_o(BORROWER, "funding_offer"): "compatible"},
                ),
                branch(
                    BORROWER,
                    "request_call_loan_offer_revision",
                    when_all={_o(BORROWER, "funding_offer"): "conditionable"},
                ),
                branch(
                    BORROWER,
                    "decline_call_loan_offer",
                    when_all={_o(BORROWER, "funding_offer"): "incompatible"},
                ),
                branch(
                    BORROWER,
                    "record_funding_inability",
                    when_all={
                        _o(BORROWER, "collateral_package"): (
                            "stale",
                            "disputed",
                        ),
                        _o(BORROWER, "funding_route"): "unavailable",
                    },
                ),
            ),
            lifecycle_names=(
                "collateral_and_facility_application",
                "replacement_funding",
            ),
        ),
        decision(
            BORROWER,
            "PC-CMB-05",
            observation_domains=_only(
                BORROWER_OBSERVATIONS,
                (
                    "decision_authority",
                    "call_obligation",
                    "controlled_resource_projection",
                    "settlement_obligation",
                    "own_business_lifecycles",
                ),
            ),
            state_domains=BORROWER_STATE,
            configuration_parameter_domains=BORROWER_PARAMETERS,
            branches=(
                branch(
                    BORROWER,
                    "authorize_controlled_repayment",
                    when_all={
                        _o(BORROWER, "controlled_resource_projection"): "sufficient",
                        _o(BORROWER, "settlement_obligation"): "material_due",
                    },
                ),
                branch(
                    BORROWER,
                    "request_authorized_position_reduction",
                    when_all={
                        _o(BORROWER, "decision_authority"): "authorized",
                        _o(BORROWER, "controlled_resource_projection"): "partial",
                    },
                ),
            ),
            lifecycle_names=(
                "call_loan_contract",
                "position_reduction_and_venue_execution",
            ),
        ),
        decision(
            BORROWER,
            "PC-CMB-06",
            observation_domains=BORROWER_OBSERVATIONS,
            state_domains=BORROWER_STATE,
            configuration_parameter_domains=BORROWER_PARAMETERS,
            branches=(
                branch(
                    BORROWER,
                    "request_call_or_term_clarification",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "clarification_failed"
                    },
                ),
                branch(
                    BORROWER,
                    "request_call_loan_renewal_or_replacement",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "funding_request_expired"
                    },
                ),
                branch(
                    BORROWER,
                    "submit_controlled_collateral_proposal",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "collateral_revision_required"
                    },
                ),
                branch(
                    BORROWER,
                    "accept_call_loan_offer",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "offer_received_compatible"
                    },
                ),
                branch(
                    BORROWER,
                    "request_call_loan_offer_revision",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "offer_received_conditionable"
                    },
                ),
                branch(
                    BORROWER,
                    "decline_call_loan_offer",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "offer_received_incompatible"
                    },
                ),
                branch(
                    BORROWER,
                    "authorize_controlled_repayment",
                    when_all={
                        _o(BORROWER, "own_business_lifecycles"): "repayment_due"
                    },
                ),
                branch(
                    BORROWER,
                    "request_authorized_position_reduction",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "reduction_authorized"
                    },
                ),
                branch(
                    BORROWER,
                    "record_funding_inability",
                    when_all={
                        _o(
                            BORROWER, "own_business_lifecycles"
                        ): "funding_routes_exhausted"
                    },
                ),
                branch(
                    BORROWER,
                    "await_funding_or_repayment_result",
                    when_all={
                        _o(BORROWER, "own_business_lifecycles"): (
                            "clarification_pending",
                            "funding_request_pending",
                            "offer_pending",
                            "repayment_pending",
                            "reduction_pending",
                        )
                    },
                ),
            ),
            lifecycle_names=(
                "call_loan_contract",
                "replacement_funding",
                "collateral_and_facility_application",
                "position_reduction_and_venue_execution",
            ),
        ),
    ),
    configuration_parameter_ids=tuple(BORROWER_PARAMETERS),
)


POPULATION_PARTICIPANT_POLICIES: tuple[RuleParticipantPolicy, ...] = (
    KNICKERBOCKER_DEPOSITOR_POLICY,
    LATER_TRUST_DEPOSITOR_POLICY,
    BANK_RESOURCE_DECISION_POLICY,
    CALL_MONEY_LENDER_POLICY,
    CALL_MONEY_BROKER_BORROWER_POLICY,
)


__all__ = [
    "BANK_RESOURCE_DECISION_POLICY",
    "CALL_MONEY_BROKER_BORROWER_POLICY",
    "CALL_MONEY_LENDER_POLICY",
    "KNICKERBOCKER_DEPOSITOR_POLICY",
    "LATER_TRUST_DEPOSITOR_POLICY",
    "POPULATION_PARTICIPANT_POLICIES",
]
