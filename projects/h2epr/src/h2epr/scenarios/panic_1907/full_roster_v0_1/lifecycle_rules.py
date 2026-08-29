"""Authoritative lifecycle rules for the thirteen Panic business families."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Mapping, Sequence


class LifecycleRuleError(ValueError):
    """A lifecycle definition or supplied record is structurally invalid."""


def _stable_id(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
        or len(value) > 192
        or not value[0].isalnum()
        or any(
            character
            not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-"
            for character in value
        )
    ):
        raise LifecycleRuleError(f"stable_id_invalid:{label}")
    return value


@dataclass(frozen=True)
class LifecycleRecord:
    object_id: str
    lifecycle_id: str
    owner_actor_id: str
    state_id: str
    version: int
    terminal: bool
    predecessor_object_id: str | None = None
    causal_parent_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class LifecycleTransitionResult:
    applied: bool
    reason_code: str
    cause_id: str
    before: LifecycleRecord
    after: LifecycleRecord


@dataclass(frozen=True)
class LifecycleRule:
    """One closed state graph with typed, non-mutating invalid transitions."""

    lifecycle_id: str
    implementation_id: str
    implementation_version: str
    owner_layer: str
    participant_capability_ids: tuple[str, ...]
    state_ids: tuple[str, ...]
    initial_state_ids: tuple[str, ...]
    terminal_state_ids: tuple[str, ...]
    transitions: tuple[tuple[str, str], ...]
    invalid_transition_behavior: str = "typed_failure_without_state_change"

    def __post_init__(self) -> None:
        for value in (
            self.lifecycle_id,
            self.implementation_id,
            self.implementation_version,
            *self.participant_capability_ids,
            *self.state_ids,
            *self.initial_state_ids,
            *self.terminal_state_ids,
        ):
            _stable_id(value, "lifecycle_definition")
        if (
            self.owner_layer != "reducer"
            or self.invalid_transition_behavior
            != "typed_failure_without_state_change"
            or not self.participant_capability_ids
            or not self.state_ids
            or not self.initial_state_ids
            or len(self.participant_capability_ids)
            != len(set(self.participant_capability_ids))
            or len(self.state_ids) != len(set(self.state_ids))
            or len(self.initial_state_ids) != len(set(self.initial_state_ids))
            or len(self.terminal_state_ids) != len(set(self.terminal_state_ids))
            or not set(self.initial_state_ids) <= set(self.state_ids)
            or not set(self.terminal_state_ids) <= set(self.state_ids)
            or not self.transitions
            or len(self.transitions) != len(set(self.transitions))
            or any(
                source not in self.state_ids or target not in self.state_ids
                for source, target in self.transitions
            )
        ):
            raise LifecycleRuleError(
                f"lifecycle_definition_invalid:{self.lifecycle_id}"
            )

    def open_record(
        self,
        *,
        object_id: str,
        owner_actor_id: str,
        initial_state_id: str,
        predecessor_object_id: str | None = None,
        causal_parent_ids: Sequence[str] = (),
    ) -> LifecycleRecord:
        if initial_state_id not in self.initial_state_ids:
            raise LifecycleRuleError("lifecycle_initial_state_invalid")
        predecessor = (
            None
            if predecessor_object_id is None
            else _stable_id(predecessor_object_id, "predecessor_object_id")
        )
        parents = tuple(
            _stable_id(item, "causal_parent_id") for item in causal_parent_ids
        )
        if len(parents) != len(set(parents)):
            raise LifecycleRuleError("lifecycle_causal_parent_duplicate")
        return LifecycleRecord(
            object_id=_stable_id(object_id, "object_id"),
            lifecycle_id=self.lifecycle_id,
            owner_actor_id=_stable_id(owner_actor_id, "owner_actor_id"),
            state_id=initial_state_id,
            version=0,
            terminal=initial_state_id in self.terminal_state_ids,
            predecessor_object_id=predecessor,
            causal_parent_ids=parents,
        )

    def transition(
        self,
        record: LifecycleRecord,
        *,
        target_state_id: str,
        cause_id: str,
    ) -> LifecycleTransitionResult:
        self._validate_record(record)
        cause = _stable_id(cause_id, "cause_id")
        if target_state_id not in self.state_ids:
            return LifecycleTransitionResult(
                applied=False,
                reason_code="lifecycle_target_state_unknown",
                cause_id=cause,
                before=record,
                after=record,
            )
        if (record.state_id, target_state_id) not in self.transitions:
            return LifecycleTransitionResult(
                applied=False,
                reason_code="lifecycle_transition_invalid",
                cause_id=cause,
                before=record,
                after=record,
            )
        after = replace(
            record,
            state_id=target_state_id,
            version=record.version + 1,
            terminal=target_state_id in self.terminal_state_ids,
            causal_parent_ids=tuple(
                dict.fromkeys((*record.causal_parent_ids, cause))
            ),
        )
        return LifecycleTransitionResult(
            applied=True,
            reason_code="lifecycle_transition_applied",
            cause_id=cause,
            before=record,
            after=after,
        )

    def _validate_record(self, record: LifecycleRecord) -> None:
        if (
            record.lifecycle_id != self.lifecycle_id
            or record.state_id not in self.state_ids
            or type(record.version) is not int
            or record.version < 0
            or type(record.terminal) is not bool
            or record.terminal != (record.state_id in self.terminal_state_ids)
        ):
            raise LifecycleRuleError("lifecycle_record_invalid")
        _stable_id(record.object_id, "object_id")
        _stable_id(record.owner_actor_id, "owner_actor_id")
        if record.predecessor_object_id is not None:
            _stable_id(record.predecessor_object_id, "predecessor_object_id")
        parents = tuple(
            _stable_id(item, "causal_parent_id")
            for item in record.causal_parent_ids
        )
        if len(parents) != len(set(parents)):
            raise LifecycleRuleError("lifecycle_record_parent_duplicate")


def _chain(*states: str) -> tuple[tuple[str, str], ...]:
    return tuple(zip(states, states[1:]))


def _rule(
    family: str,
    *,
    capabilities: Sequence[str],
    states: Sequence[str],
    initials: Sequence[str],
    terminals: Sequence[str],
    transitions: Sequence[tuple[str, str]],
) -> LifecycleRule:
    lifecycle_id = f"lifecycle.0288.{family}"
    return LifecycleRule(
        lifecycle_id=lifecycle_id,
        implementation_id=f"h2epr.lifecycle.0288.{family}",
        implementation_version="0.1.0",
        owner_layer="reducer",
        participant_capability_ids=tuple(capabilities),
        state_ids=tuple(states),
        initial_state_ids=tuple(initials),
        terminal_state_ids=tuple(terminals),
        transitions=tuple(transitions),
    )


GOVERNANCE_AND_AUTHORITY = _rule(
    "governance_and_authority",
    capabilities=(
        "bank_resource_decision",
        "j_pierpont_morgan",
        "knickerbocker_trust",
        "lincoln_trust_company",
        "national_bank_of_commerce",
        "new_york_clearing_house",
        "trust_company_of_america",
    ),
    states=(
        "not_requested",
        "requested",
        "pending",
        "authorized",
        "denied",
        "disputed",
        "superseded",
        "expired",
    ),
    initials=("not_requested",),
    terminals=("authorized", "denied", "superseded", "expired"),
    transitions=(
        *_chain("not_requested", "requested", "pending"),
        ("pending", "authorized"),
        ("pending", "denied"),
        ("pending", "disputed"),
        ("pending", "expired"),
        ("disputed", "pending"),
        ("disputed", "superseded"),
        ("authorized", "superseded"),
        ("denied", "superseded"),
        ("superseded", "requested"),
    ),
)

INFORMATION_AND_EXAMINATION = _rule(
    "information_and_examination",
    capabilities=(
        "bank_resource_decision",
        "j_pierpont_morgan",
        "knickerbocker_trust",
        "lincoln_trust_company",
        "national_bank_of_commerce",
        "new_york_clearing_house",
        "trust_company_of_america",
        "trust_presidents_committee",
    ),
    states=(
        "requested",
        "admitted",
        "pending",
        "produced",
        "issued",
        "delivered",
        "disputed",
        "corrected",
        "withdrawn",
        "expired",
        "closed",
    ),
    initials=("requested",),
    terminals=("withdrawn", "expired", "closed"),
    transitions=(
        *_chain(
            "requested",
            "admitted",
            "pending",
            "produced",
            "issued",
            "delivered",
        ),
        ("requested", "withdrawn"),
        ("admitted", "expired"),
        ("pending", "expired"),
        ("delivered", "disputed"),
        ("delivered", "closed"),
        ("disputed", "corrected"),
        ("disputed", "closed"),
        ("corrected", "issued"),
        ("corrected", "closed"),
    ),
)

SUPPORT_AND_REQUEST_CASE = _rule(
    "support_and_request_case",
    capabilities=(
        "j_pierpont_morgan",
        "knickerbocker_trust",
        "national_bank_of_commerce",
        "new_york_clearing_house",
        "trust_company_of_america",
        "trust_presidents_committee",
    ),
    states=(
        "draft",
        "authorized",
        "issued",
        "hop_delivered",
        "received",
        "classified",
        "reviewing",
        "information_needed",
        "referred",
        "declined",
        "conditioned",
        "delayed",
        "partial",
        "executed",
        "failed",
        "withdrawn",
        "closed",
        "reopened",
    ),
    initials=("draft",),
    terminals=("failed", "withdrawn", "closed"),
    transitions=(
        *_chain(
            "draft",
            "authorized",
            "issued",
            "hop_delivered",
            "received",
            "classified",
        ),
        ("authorized", "withdrawn"),
        ("classified", "reviewing"),
        ("classified", "information_needed"),
        ("classified", "referred"),
        ("classified", "declined"),
        ("classified", "conditioned"),
        ("classified", "delayed"),
        ("information_needed", "reviewing"),
        ("referred", "reviewing"),
        ("referred", "declined"),
        ("reviewing", "conditioned"),
        ("reviewing", "declined"),
        ("reviewing", "delayed"),
        ("reviewing", "partial"),
        ("reviewing", "executed"),
        ("reviewing", "failed"),
        ("conditioned", "reviewing"),
        ("conditioned", "partial"),
        ("conditioned", "executed"),
        ("conditioned", "declined"),
        ("delayed", "reviewing"),
        ("delayed", "failed"),
        ("partial", "executed"),
        ("partial", "failed"),
        ("partial", "closed"),
        ("declined", "closed"),
        ("executed", "closed"),
        ("failed", "closed"),
        ("withdrawn", "closed"),
        ("closed", "reopened"),
        ("reopened", "reviewing"),
    ),
)

PROPOSAL_AND_PLAN = _rule(
    "proposal_and_plan",
    capabilities=(
        "j_pierpont_morgan",
        "knickerbocker_trust",
        "new_york_clearing_house",
        "trust_presidents_committee",
    ),
    states=(
        "draft",
        "circulating",
        "revising",
        "ready_for_assembly",
        "assembled",
        "authorized",
        "scheduled",
        "withdrawn",
        "expired",
        "closed",
    ),
    initials=("draft",),
    terminals=("withdrawn", "expired", "closed"),
    transitions=(
        ("draft", "circulating"),
        ("draft", "withdrawn"),
        ("circulating", "revising"),
        ("circulating", "ready_for_assembly"),
        ("circulating", "expired"),
        ("revising", "circulating"),
        ("revising", "withdrawn"),
        *_chain(
            "ready_for_assembly",
            "assembled",
            "authorized",
            "scheduled",
            "closed",
        ),
        ("assembled", "revising"),
        ("authorized", "withdrawn"),
    ),
)

SOLICITATION_AND_INDEPENDENT_REPLY = _rule(
    "solicitation_and_independent_reply",
    capabilities=(
        "bank_resource_decision",
        "j_pierpont_morgan",
        "trust_presidents_committee",
    ),
    states=(
        "prepared",
        "issued",
        "delivered",
        "reviewing",
        "conditioned",
        "committed",
        "declined",
        "disputed",
        "expired",
        "superseded",
    ),
    initials=("prepared",),
    terminals=("committed", "declined", "expired", "superseded"),
    transitions=(
        *_chain("prepared", "issued", "delivered", "reviewing"),
        ("issued", "expired"),
        ("delivered", "expired"),
        ("reviewing", "conditioned"),
        ("reviewing", "committed"),
        ("reviewing", "declined"),
        ("reviewing", "disputed"),
        ("conditioned", "reviewing"),
        ("conditioned", "committed"),
        ("conditioned", "declined"),
        ("disputed", "reviewing"),
        ("prepared", "superseded"),
        ("issued", "superseded"),
    ),
)

RESOURCE_COMMITMENT_AND_EXECUTION = _rule(
    "resource_commitment_and_execution",
    capabilities=(
        "bank_resource_decision",
        "j_pierpont_morgan",
        "new_york_clearing_house",
        "trust_company_of_america",
        "trust_presidents_committee",
    ),
    states=(
        "available",
        "offered",
        "reserved",
        "committed",
        "scheduled",
        "partial",
        "executed",
        "no_effect",
        "failed",
        "released",
        "reversed",
        "expired",
    ),
    initials=("available",),
    terminals=(
        "executed",
        "no_effect",
        "failed",
        "released",
        "reversed",
        "expired",
    ),
    transitions=(
        *_chain(
            "available",
            "offered",
            "reserved",
            "committed",
            "scheduled",
        ),
        ("offered", "expired"),
        ("offered", "released"),
        ("reserved", "released"),
        ("reserved", "expired"),
        ("committed", "released"),
        ("scheduled", "partial"),
        ("scheduled", "executed"),
        ("scheduled", "no_effect"),
        ("scheduled", "failed"),
        ("partial", "executed"),
        ("partial", "failed"),
        ("executed", "reversed"),
    ),
)

CREDIT_AND_CLEARING_RELATIONSHIP = _rule(
    "credit_and_clearing_relationship",
    capabilities=("knickerbocker_trust", "national_bank_of_commerce"),
    states=(
        "active_current",
        "review_due",
        "proposed_conditioned",
        "notice_prepared",
        "notice_issued",
        "delivered",
        "ending_at_time",
        "inactive",
        "booked_adjusted",
        "repaid",
        "failed",
        "disputed",
        "closed",
    ),
    initials=("active_current",),
    terminals=("inactive", "repaid", "failed", "closed"),
    transitions=(
        ("active_current", "review_due"),
        ("active_current", "booked_adjusted"),
        ("review_due", "active_current"),
        ("review_due", "proposed_conditioned"),
        ("review_due", "notice_prepared"),
        ("review_due", "disputed"),
        ("proposed_conditioned", "active_current"),
        ("proposed_conditioned", "notice_prepared"),
        *_chain(
            "notice_prepared",
            "notice_issued",
            "delivered",
            "ending_at_time",
            "inactive",
        ),
        ("notice_issued", "failed"),
        ("delivered", "disputed"),
        ("disputed", "review_due"),
        ("booked_adjusted", "repaid"),
        ("booked_adjusted", "failed"),
        ("repaid", "closed"),
        ("inactive", "closed"),
    ),
)

INSTITUTIONAL_COMMUNICATION = _rule(
    "institutional_communication",
    capabilities=(
        "j_pierpont_morgan",
        "knickerbocker_depositor",
        "knickerbocker_trust",
        "later_trust_depositor",
        "lincoln_trust_company",
        "national_bank_of_commerce",
        "new_york_clearing_house",
        "trust_company_of_america",
        "trust_presidents_committee",
    ),
    states=(
        "proposal",
        "pending_authority",
        "authorized",
        "narrowed_withheld",
        "issued",
        "transport_pending",
        "delivered",
        "failed",
        "expired",
        "corrected_superseded",
        "closed",
    ),
    initials=("proposal",),
    terminals=("narrowed_withheld", "failed", "expired", "closed"),
    transitions=(
        *_chain("proposal", "pending_authority", "authorized", "issued"),
        ("pending_authority", "narrowed_withheld"),
        ("authorized", "narrowed_withheld"),
        ("issued", "transport_pending"),
        ("transport_pending", "delivered"),
        ("transport_pending", "failed"),
        ("transport_pending", "expired"),
        ("delivered", "corrected_superseded"),
        ("delivered", "closed"),
        ("corrected_superseded", "issued"),
        ("corrected_superseded", "closed"),
    ),
)

WITHDRAWAL_SERVICE_AND_PAYMENT = _rule(
    "withdrawal_service_and_payment",
    capabilities=(
        "knickerbocker_depositor",
        "knickerbocker_trust",
        "later_trust_depositor",
        "trust_company_of_america",
    ),
    states=(
        "choice",
        "request_created",
        "admitted",
        "rejected",
        "queued",
        "serving",
        "partial",
        "paid",
        "alternate_form",
        "delayed",
        "failed",
        "unavailable",
        "expired",
        "cancelled",
        "claim_updated",
        "closed",
    ),
    initials=("choice",),
    terminals=(
        "rejected",
        "paid",
        "failed",
        "unavailable",
        "expired",
        "cancelled",
        "closed",
    ),
    transitions=(
        ("choice", "request_created"),
        ("choice", "closed"),
        ("request_created", "admitted"),
        ("request_created", "rejected"),
        ("request_created", "cancelled"),
        ("admitted", "queued"),
        ("admitted", "delayed"),
        ("queued", "serving"),
        ("queued", "delayed"),
        ("queued", "expired"),
        ("serving", "partial"),
        ("serving", "paid"),
        ("serving", "alternate_form"),
        ("serving", "failed"),
        ("serving", "unavailable"),
        ("partial", "serving"),
        ("partial", "claim_updated"),
        ("paid", "claim_updated"),
        ("alternate_form", "claim_updated"),
        ("delayed", "queued"),
        ("delayed", "expired"),
        ("claim_updated", "closed"),
    ),
)

COLLATERAL_AND_FACILITY_APPLICATION = _rule(
    "collateral_and_facility_application",
    capabilities=(
        "bank_resource_decision",
        "call_money_broker_borrower",
        "trust_company_of_america",
    ),
    states=(
        "draft",
        "submitted",
        "reviewing",
        "information_needed",
        "eligible",
        "ineligible",
        "accepted",
        "declined",
        "issued_booked",
        "partial",
        "released",
        "failed",
        "expired",
    ),
    initials=("draft",),
    terminals=("ineligible", "declined", "released", "failed", "expired"),
    transitions=(
        *_chain("draft", "submitted", "reviewing"),
        ("submitted", "expired"),
        ("reviewing", "information_needed"),
        ("reviewing", "eligible"),
        ("reviewing", "ineligible"),
        ("reviewing", "declined"),
        ("information_needed", "reviewing"),
        ("information_needed", "expired"),
        ("eligible", "accepted"),
        ("eligible", "declined"),
        ("accepted", "issued_booked"),
        ("accepted", "partial"),
        ("accepted", "failed"),
        ("issued_booked", "released"),
        ("partial", "issued_booked"),
        ("partial", "failed"),
    ),
)

CALL_LOAN_CONTRACT = _rule(
    "call_loan_contract",
    capabilities=("call_money_broker_borrower", "call_money_lender"),
    states=(
        "active",
        "review_due",
        "continued",
        "term_change_proposed",
        "call_issued",
        "call_delivered",
        "borrower_responding",
        "repayment_pending",
        "partial",
        "repaid",
        "defaulted",
        "failed",
        "closed",
    ),
    initials=("active",),
    terminals=("repaid", "defaulted", "failed", "closed"),
    transitions=(
        ("active", "review_due"),
        ("review_due", "continued"),
        ("review_due", "term_change_proposed"),
        ("review_due", "call_issued"),
        ("continued", "review_due"),
        ("term_change_proposed", "continued"),
        ("term_change_proposed", "call_issued"),
        ("call_issued", "call_delivered"),
        ("call_issued", "failed"),
        *_chain("call_delivered", "borrower_responding", "repayment_pending"),
        ("borrower_responding", "defaulted"),
        ("repayment_pending", "partial"),
        ("repayment_pending", "repaid"),
        ("repayment_pending", "defaulted"),
        ("partial", "repayment_pending"),
        ("partial", "repaid"),
        ("repaid", "closed"),
        ("defaulted", "closed"),
    ),
)

REPLACEMENT_FUNDING = _rule(
    "replacement_funding",
    capabilities=("call_money_broker_borrower", "call_money_lender"),
    states=(
        "request",
        "delivered_reviewing",
        "offer_conditioned",
        "revision",
        "accepted",
        "declined",
        "matching",
        "booked",
        "transfer_pending",
        "partial",
        "funded",
        "repayment_pending",
        "repaid",
        "defaulted",
        "expired",
        "closed",
    ),
    initials=("request",),
    terminals=("declined", "repaid", "defaulted", "expired", "closed"),
    transitions=(
        ("request", "delivered_reviewing"),
        ("request", "expired"),
        ("delivered_reviewing", "offer_conditioned"),
        ("delivered_reviewing", "declined"),
        ("delivered_reviewing", "expired"),
        ("offer_conditioned", "revision"),
        ("offer_conditioned", "accepted"),
        ("offer_conditioned", "declined"),
        ("revision", "offer_conditioned"),
        ("revision", "expired"),
        *_chain(
            "accepted",
            "matching",
            "booked",
            "transfer_pending",
        ),
        ("matching", "expired"),
        ("transfer_pending", "partial"),
        ("transfer_pending", "funded"),
        ("partial", "transfer_pending"),
        ("partial", "funded"),
        ("funded", "repayment_pending"),
        ("funded", "closed"),
        ("repayment_pending", "repaid"),
        ("repayment_pending", "defaulted"),
        ("repaid", "closed"),
        ("defaulted", "closed"),
    ),
)

POSITION_REDUCTION_AND_VENUE_EXECUTION = _rule(
    "position_reduction_and_venue_execution",
    capabilities=("call_money_broker_borrower",),
    states=(
        "authorized",
        "requested",
        "admitted",
        "rejected",
        "pending_match",
        "partial",
        "executed",
        "settlement_pending",
        "settled",
        "failed",
        "cancelled",
        "expired",
    ),
    initials=("authorized",),
    terminals=("rejected", "settled", "failed", "cancelled", "expired"),
    transitions=(
        ("authorized", "requested"),
        ("requested", "admitted"),
        ("requested", "rejected"),
        ("requested", "cancelled"),
        ("admitted", "pending_match"),
        ("admitted", "expired"),
        ("pending_match", "partial"),
        ("pending_match", "executed"),
        ("pending_match", "failed"),
        ("pending_match", "cancelled"),
        ("partial", "pending_match"),
        ("partial", "executed"),
        ("executed", "settlement_pending"),
        ("settlement_pending", "settled"),
        ("settlement_pending", "failed"),
    ),
)


LIFECYCLE_RULES: tuple[LifecycleRule, ...] = (
    CALL_LOAN_CONTRACT,
    COLLATERAL_AND_FACILITY_APPLICATION,
    CREDIT_AND_CLEARING_RELATIONSHIP,
    GOVERNANCE_AND_AUTHORITY,
    INFORMATION_AND_EXAMINATION,
    INSTITUTIONAL_COMMUNICATION,
    POSITION_REDUCTION_AND_VENUE_EXECUTION,
    PROPOSAL_AND_PLAN,
    REPLACEMENT_FUNDING,
    RESOURCE_COMMITMENT_AND_EXECUTION,
    SOLICITATION_AND_INDEPENDENT_REPLY,
    SUPPORT_AND_REQUEST_CASE,
    WITHDRAWAL_SERVICE_AND_PAYMENT,
)

LIFECYCLE_RULES_BY_ID: Mapping[str, LifecycleRule] = MappingProxyType(
    {rule.lifecycle_id: rule for rule in LIFECYCLE_RULES}
)

if len(LIFECYCLE_RULES_BY_ID) != len(LIFECYCLE_RULES):
    raise LifecycleRuleError("lifecycle_rule_identity_duplicate")


__all__ = [
    "CALL_LOAN_CONTRACT",
    "COLLATERAL_AND_FACILITY_APPLICATION",
    "CREDIT_AND_CLEARING_RELATIONSHIP",
    "GOVERNANCE_AND_AUTHORITY",
    "INFORMATION_AND_EXAMINATION",
    "INSTITUTIONAL_COMMUNICATION",
    "LIFECYCLE_RULES",
    "LIFECYCLE_RULES_BY_ID",
    "LifecycleRecord",
    "LifecycleRule",
    "LifecycleRuleError",
    "LifecycleTransitionResult",
    "POSITION_REDUCTION_AND_VENUE_EXECUTION",
    "PROPOSAL_AND_PLAN",
    "REPLACEMENT_FUNDING",
    "RESOURCE_COMMITMENT_AND_EXECUTION",
    "SOLICITATION_AND_INDEPENDENT_REPLY",
    "SUPPORT_AND_REQUEST_CASE",
    "WITHDRAWAL_SERVICE_AND_PAYMENT",
]
