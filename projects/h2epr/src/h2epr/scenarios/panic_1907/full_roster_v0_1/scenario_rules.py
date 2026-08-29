"""Full-event Scenario Rule policies selected by the Panic configuration."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from types import MappingProxyType
from typing import Mapping, Sequence


class ScenarioPolicyError(ValueError):
    """A Scenario Rule received an unsupported or incoherent input."""


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
        raise ScenarioPolicyError(f"stable_id_invalid:{label}")
    return value


@dataclass(frozen=True)
class ScenarioPolicy:
    """Stable identity and semantic ownership for one selected policy."""

    policy_id: str
    selection: str
    implementation_id: str
    implementation_version: str
    owner_layer: str
    governed_semantic_ids: tuple[str, ...]
    rejection_reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        for value in (
            self.policy_id,
            self.selection,
            self.implementation_id,
            self.implementation_version,
            *self.governed_semantic_ids,
            *self.rejection_reason_codes,
        ):
            _stable_id(value, "scenario_policy_identity")
        if self.owner_layer not in {
            "scheduler",
            "information",
            "environment",
            "reducer",
        }:
            raise ScenarioPolicyError("scenario_policy_owner_layer_invalid")
        if (
            not self.governed_semantic_ids
            or len(self.governed_semantic_ids)
            != len(set(self.governed_semantic_ids))
            or not self.rejection_reason_codes
            or len(self.rejection_reason_codes)
            != len(set(self.rejection_reason_codes))
        ):
            raise ScenarioPolicyError("scenario_policy_boundary_incomplete")


@dataclass(frozen=True)
class EventWindow:
    event_id: str
    earliest_time: str
    latest_time: str
    predecessor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class PartialOrderPolicy(ScenarioPolicy):
    """Preserve predecessors and windows before the residual stable-ID tie."""

    def order_events(self, events: Sequence[EventWindow]) -> tuple[str, ...]:
        parsed: dict[str, tuple[EventWindow, datetime, datetime]] = {}
        for event in events:
            event_id = _stable_id(event.event_id, "event_id")
            if event_id in parsed:
                raise ScenarioPolicyError("time_event_duplicate")
            predecessors = tuple(
                _stable_id(item, "predecessor_id")
                for item in event.predecessor_ids
            )
            if len(predecessors) != len(set(predecessors)):
                raise ScenarioPolicyError("time_predecessor_duplicate")
            earliest = _aware_time(event.earliest_time, "earliest_time")
            latest = _aware_time(event.latest_time, "latest_time")
            if earliest > latest:
                raise ScenarioPolicyError("time_window_inverted")
            parsed[event_id] = (event, earliest, latest)
        for event_id, (event, _, latest) in parsed.items():
            for predecessor_id in event.predecessor_ids:
                if predecessor_id not in parsed:
                    raise ScenarioPolicyError("time_predecessor_unknown")
                predecessor_earliest = parsed[predecessor_id][1]
                if predecessor_earliest > latest:
                    raise ScenarioPolicyError(
                        f"time_causal_window_conflict:{predecessor_id}:{event_id}"
                    )
        remaining = set(parsed)
        emitted: list[str] = []
        emitted_set: set[str] = set()
        while remaining:
            ready = tuple(
                event_id
                for event_id in remaining
                if set(parsed[event_id][0].predecessor_ids) <= emitted_set
            )
            if not ready:
                raise ScenarioPolicyError("time_predecessor_cycle")
            selected = min(
                ready,
                key=lambda item: (parsed[item][1], parsed[item][2], item),
            )
            emitted.append(selected)
            emitted_set.add(selected)
            remaining.remove(selected)
        return tuple(emitted)


@dataclass(frozen=True)
class InformationProduct:
    product_id: str
    version: int
    issued_at: str
    fresh_until: str | None
    expires_at: str | None
    supersedes_version: int | None = None


@dataclass(frozen=True)
class InformationDelivery:
    product_id: str
    version: int
    recipient_id: str
    route_id: str
    route_disposition: str
    delivery_disposition: str
    delivered_at: str | None
    freshness: str


@dataclass(frozen=True)
class CompoundObservation:
    status: str
    component_versions: Mapping[str, int]
    unavailable_component_ids: tuple[str, ...]


@dataclass(frozen=True)
class InformationPolicy(ScenarioPolicy):
    """Keep issue, route, delivery, freshness, and version coherence distinct."""

    def route_delivery(
        self,
        product: InformationProduct,
        *,
        recipient_id: str,
        route_id: str,
        route_admitted: bool,
        delivered_at: str | None,
    ) -> InformationDelivery:
        product_id = _stable_id(product.product_id, "product_id")
        recipient = _stable_id(recipient_id, "recipient_id")
        route = _stable_id(route_id, "route_id")
        version = _nonnegative_integer(product.version, "product_version")
        issued = _aware_time(product.issued_at, "issued_at")
        fresh_until = _optional_time(product.fresh_until, "fresh_until")
        expiry = _optional_time(product.expires_at, "expires_at")
        if type(route_admitted) is not bool:
            raise ScenarioPolicyError("information_route_admission_invalid")
        if fresh_until is not None and fresh_until < issued:
            raise ScenarioPolicyError("information_freshness_before_issue")
        if expiry is not None and expiry < issued:
            raise ScenarioPolicyError("information_expiry_before_issue")
        if product.supersedes_version is not None:
            supersedes = _nonnegative_integer(
                product.supersedes_version,
                "supersedes_version",
            )
            if supersedes >= version:
                raise ScenarioPolicyError("information_supersession_invalid")
        if not route_admitted:
            if delivered_at is not None:
                raise ScenarioPolicyError("information_delivery_without_route")
            return InformationDelivery(
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition="rejected",
                delivery_disposition="not_delivered",
                delivered_at=None,
                freshness="unavailable",
            )
        if delivered_at is None:
            return InformationDelivery(
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition="admitted",
                delivery_disposition="pending",
                delivered_at=None,
                freshness="unavailable",
            )
        delivered = _aware_time(delivered_at, "delivered_at")
        if delivered < issued:
            raise ScenarioPolicyError("information_delivery_before_issue")
        if expiry is not None and delivered > expiry:
            return InformationDelivery(
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition="admitted",
                delivery_disposition="expired",
                delivered_at=None,
                freshness="unavailable",
            )
        freshness = (
            "fresh"
            if fresh_until is None or delivered <= fresh_until
            else "stale"
        )
        return InformationDelivery(
            product_id=product_id,
            version=version,
            recipient_id=recipient,
            route_id=route,
            route_disposition="admitted",
            delivery_disposition="delivered",
            delivered_at=delivered_at,
            freshness=freshness,
        )

    def compose_observation(
        self,
        deliveries: Sequence[InformationDelivery],
        *,
        required_versions: Mapping[str, int],
    ) -> CompoundObservation:
        required = {
            _stable_id(product_id, "required_product_id"): _nonnegative_integer(
                version,
                "required_version",
            )
            for product_id, version in required_versions.items()
        }
        if not required:
            raise ScenarioPolicyError("information_compound_empty")
        delivered: dict[str, InformationDelivery] = {}
        for item in deliveries:
            product_id = _stable_id(item.product_id, "delivered_product_id")
            _nonnegative_integer(item.version, "delivered_product_version")
            _stable_id(item.recipient_id, "delivered_recipient_id")
            _stable_id(item.route_id, "delivered_route_id")
            if item.route_disposition not in {"admitted", "rejected"} or (
                item.delivery_disposition
                not in {"not_delivered", "pending", "expired", "delivered"}
            ):
                raise ScenarioPolicyError("information_delivery_record_invalid")
            if product_id in delivered:
                raise ScenarioPolicyError("information_compound_duplicate")
            delivered[product_id] = item
        unavailable = tuple(
            sorted(
                product_id
                for product_id, version in required.items()
                if product_id not in delivered
                or delivered[product_id].delivery_disposition != "delivered"
                or delivered[product_id].version != version
            )
        )
        status = "available" if not unavailable else "unavailable"
        return CompoundObservation(
            status=status,
            component_versions=MappingProxyType(dict(sorted(required.items()))),
            unavailable_component_ids=unavailable,
        )


@dataclass(frozen=True)
class ServiceRequest:
    request_id: str
    host_actor_id: str
    claimant_actor_id: str
    admitted_at: str
    requested_units: int


@dataclass(frozen=True)
class ServiceResult:
    request_id: str
    disposition: str
    realized_units: int
    requested_units: int
    queue_position: int


@dataclass(frozen=True)
class HostServicePolicy(ScenarioPolicy):
    """Apply host-local FIFO service with explicit partial results."""

    def serve(
        self,
        requests: Sequence[ServiceRequest],
        *,
        host_actor_id: str,
        available_units: int,
    ) -> tuple[ServiceResult, ...]:
        host = _stable_id(host_actor_id, "host_actor_id")
        remaining = _nonnegative_integer(available_units, "available_units")
        parsed: list[tuple[datetime, ServiceRequest]] = []
        request_ids: set[str] = set()
        for request in requests:
            request_id = _stable_id(request.request_id, "request_id")
            if request_id in request_ids:
                raise ScenarioPolicyError("service_request_duplicate")
            request_ids.add(request_id)
            if _stable_id(request.host_actor_id, "request_host") != host:
                raise ScenarioPolicyError("service_host_scope_mismatch")
            _stable_id(request.claimant_actor_id, "claimant_actor_id")
            _positive_integer(
                request.requested_units,
                "requested_units",
            )
            parsed.append(
                (_aware_time(request.admitted_at, "admitted_at"), request)
            )
        ordered = sorted(parsed, key=lambda item: (item[0], item[1].request_id))
        results: list[ServiceResult] = []
        for index, (_, request) in enumerate(ordered, start=1):
            realized = min(remaining, request.requested_units)
            remaining -= realized
            if realized == request.requested_units:
                disposition = "paid"
            elif realized:
                disposition = "partial"
            else:
                disposition = "delayed"
            results.append(
                ServiceResult(
                    request_id=request.request_id,
                    disposition=disposition,
                    realized_units=realized,
                    requested_units=request.requested_units,
                    queue_position=index,
                )
            )
        return tuple(results)


@dataclass(frozen=True)
class ReviewResult:
    classification: str
    present_item_ids: tuple[str, ...]
    missing_item_ids: tuple[str, ...]
    disputed_item_ids: tuple[str, ...]


@dataclass(frozen=True)
class TypedReviewPolicy(ScenarioPolicy):
    """Classify declared information requirements without a hidden score."""

    def classify(
        self,
        *,
        required_item_ids: Sequence[str],
        present_item_ids: Sequence[str],
        disputed_item_ids: Sequence[str] = (),
        conditionally_omittable_item_ids: Sequence[str] = (),
    ) -> ReviewResult:
        required = _unique_ids(required_item_ids, "required_item_ids")
        present = _unique_ids(
            present_item_ids,
            "present_item_ids",
            allow_empty=True,
        )
        disputed = _unique_ids(
            disputed_item_ids,
            "disputed_item_ids",
            allow_empty=True,
        )
        omittable = _unique_ids(
            conditionally_omittable_item_ids,
            "conditionally_omittable_item_ids",
            allow_empty=True,
        )
        if not set(present) <= set(required) or not set(disputed) <= set(required):
            raise ScenarioPolicyError("review_item_outside_requirements")
        if set(present) & set(disputed) or not set(omittable) <= set(required):
            raise ScenarioPolicyError("review_item_class_conflict")
        missing = tuple(sorted(set(required) - set(present) - set(disputed)))
        if disputed:
            classification = "disputed"
        elif not missing:
            classification = "complete"
        elif set(missing) <= set(omittable):
            classification = "conditionally_complete"
        else:
            classification = "incomplete"
        return ReviewResult(
            classification=classification,
            present_item_ids=tuple(sorted(present)),
            missing_item_ids=missing,
            disputed_item_ids=tuple(sorted(disputed)),
        )


@dataclass(frozen=True)
class AmountAssessment:
    requested_bound: str
    delivered_envelope: str
    disposition: str
    realized_amount: None = None


@dataclass(frozen=True)
class QualitativeAmountPolicy(ScenarioPolicy):
    """Admit a declared qualitative request without allocating resources."""

    def assess(
        self,
        *,
        requested_bound: str,
        delivered_envelope: str,
        resource_owner_matches: bool,
    ) -> AmountAssessment:
        if requested_bound not in {
            "amount_unknown",
            "bounded_minimum",
            "bounded_maximum",
            "bounded_range",
            "nonquantified_category_request",
        }:
            raise ScenarioPolicyError("amount_requested_bound_unsupported")
        if delivered_envelope not in {
            "unknown",
            "unavailable",
            "constrained",
            "bounded_available",
        }:
            raise ScenarioPolicyError("amount_resource_envelope_unsupported")
        if type(resource_owner_matches) is not bool:
            raise ScenarioPolicyError("amount_resource_owner_flag_invalid")
        if not resource_owner_matches:
            disposition = "resource_owner_mismatch"
        elif delivered_envelope == "unavailable":
            disposition = "outside_delivered_envelope"
        elif delivered_envelope == "unknown":
            disposition = "requires_delivered_resource_information"
        else:
            disposition = "admissible_for_owner_decision"
        return AmountAssessment(
            requested_bound=requested_bound,
            delivered_envelope=delivered_envelope,
            disposition=disposition,
        )


_FACILITY_ACTIVATION = "1907-10-26T00:00:00-05:00"


@dataclass(frozen=True)
class DatedFacilityPolicy(ScenarioPolicy):
    """Expose member application eligibility only after dated activation."""

    def eligibility(self, *, event_time: str, membership: str) -> str:
        current = _aware_time(event_time, "event_time")
        activation = _aware_time(_FACILITY_ACTIVATION, "facility_activation")
        if membership not in {"member", "nonmember", "unknown"}:
            raise ScenarioPolicyError("facility_membership_unsupported")
        if current < activation:
            return "not_applicable"
        if membership == "member":
            return "eligible_to_apply"
        if membership == "nonmember":
            return "ineligible_nonmember"
        return "unknown_pending_membership_information"


@dataclass(frozen=True)
class VenueProcess:
    process_id: str
    owner_actor_id: str
    state: str
    version: int


@dataclass(frozen=True)
class VenueTransition:
    accepted: bool
    reason_code: str
    before: VenueProcess
    after: VenueProcess


_VENUE_TRANSITIONS: Mapping[tuple[str, str], str] = MappingProxyType(
    {
        ("request_created", "request_delivered"): "delivery",
        ("request_delivered", "offer_received"): "offer",
        ("offer_received", "compatibility_confirmed"): "compatibility_result",
        ("compatibility_confirmed", "matched"): "match",
        ("matched", "booked"): "booking",
        ("booked", "transfer_pending"): "transfer_instruction",
        ("transfer_pending", "transferred"): "transfer_result",
        ("transferred", "settlement_pending"): "settlement_instruction",
        ("settlement_pending", "settled"): "settlement_result",
    }
)


@dataclass(frozen=True)
class ExplicitVenuePolicy(ScenarioPolicy):
    """Require request, offer, match, booking, transfer, and settlement stages."""

    def advance(
        self,
        process: VenueProcess,
        *,
        target_state: str,
        cause_kind: str,
    ) -> VenueTransition:
        _stable_id(process.process_id, "venue_process_id")
        _stable_id(process.owner_actor_id, "venue_owner_actor_id")
        _nonnegative_integer(process.version, "venue_version")
        _stable_id(target_state, "venue_target_state")
        _stable_id(cause_kind, "venue_cause_kind")
        expected_cause = _VENUE_TRANSITIONS.get((process.state, target_state))
        if expected_cause != cause_kind:
            return VenueTransition(
                accepted=False,
                reason_code="venue_stage_or_cause_invalid",
                before=process,
                after=process,
            )
        after = replace(
            process,
            state=target_state,
            version=process.version + 1,
        )
        return VenueTransition(
            accepted=True,
            reason_code="venue_transition_applied",
            before=process,
            after=after,
        )


@dataclass(frozen=True)
class CarryForwardRecord:
    object_id: str
    owner_actor_id: str
    state: str
    version: int
    reason_code: str
    next_event_id: str
    terminal: bool = False


@dataclass(frozen=True)
class EventRevisitPolicy(ScenarioPolicy):
    """Revisit only on declared causes and preserve unresolved horizon state."""

    def should_revisit(self, trigger_kind: str) -> bool:
        if trigger_kind not in {
            "delivery",
            "state_change",
            "deadline",
            "phase_opportunity",
            "none",
        }:
            raise ScenarioPolicyError("lifecycle_revisit_trigger_unsupported")
        return trigger_kind != "none"

    def carry_forward(
        self,
        *,
        object_id: str,
        owner_actor_id: str,
        state: str,
        version: int,
        reason_code: str,
        next_event_id: str,
    ) -> CarryForwardRecord:
        return CarryForwardRecord(
            object_id=_stable_id(object_id, "object_id"),
            owner_actor_id=_stable_id(owner_actor_id, "owner_actor_id"),
            state=_stable_id(state, "state"),
            version=_nonnegative_integer(version, "version"),
            reason_code=_stable_id(reason_code, "reason_code"),
            next_event_id=_stable_id(next_event_id, "next_event_id"),
        )


@dataclass(frozen=True)
class LayeredResult:
    action_intent_id: str
    action_admission: str
    business_disposition_id: str | None
    business_disposition: str
    execution_result: str
    reason_code: str
    delivered: bool
    delivery_ref: str | None


@dataclass(frozen=True)
class TypedResultPolicy(ScenarioPolicy):
    """Keep admission, disposition, execution, and later delivery separate."""

    def record(
        self,
        *,
        action_intent_id: str,
        action_admission: str,
        business_disposition_id: str | None,
        business_disposition: str,
        execution_result: str,
        reason_code: str,
    ) -> LayeredResult:
        if action_admission not in {
            "accepted",
            "rejected",
            "partial",
            "delayed",
            "superseded",
            "failed",
        }:
            raise ScenarioPolicyError("result_action_admission_unsupported")
        if business_disposition not in {
            "accepted",
            "conditioned",
            "declined",
            "delayed",
            "partial",
            "withdrawn",
            "expired",
            "failed",
            "no_disposition",
            "other_scoped_decline",
            "not_applicable",
        }:
            raise ScenarioPolicyError("result_business_disposition_unsupported")
        if execution_result not in {
            "not_applicable",
            "scheduled",
            "partial",
            "realized",
            "delayed",
            "no_effect",
            "failed",
            "withdrawn",
            "expired",
        }:
            raise ScenarioPolicyError("result_execution_result_unsupported")
        if action_admission != "accepted" and execution_result not in {
            "not_applicable",
            "no_effect",
            "failed",
        }:
            raise ScenarioPolicyError("result_execution_without_admission")
        disposition_id = (
            None
            if business_disposition_id is None
            else _stable_id(
                business_disposition_id,
                "business_disposition_id",
            )
        )
        return LayeredResult(
            action_intent_id=_stable_id(action_intent_id, "action_intent_id"),
            action_admission=action_admission,
            business_disposition_id=disposition_id,
            business_disposition=_stable_id(
                business_disposition,
                "business_disposition",
            ),
            execution_result=_stable_id(execution_result, "execution_result"),
            reason_code=_stable_id(reason_code, "reason_code"),
            delivered=False,
            delivery_ref=None,
        )

    def deliver(self, result: LayeredResult, *, delivery_ref: str) -> LayeredResult:
        if result.delivered:
            raise ScenarioPolicyError("result_already_delivered")
        return replace(
            result,
            delivered=True,
            delivery_ref=_stable_id(delivery_ref, "delivery_ref"),
        )


def _policy_fields(
    policy_id: str,
    selection: str,
    owner_layer: str,
    governed_semantic_ids: Sequence[str],
    *rejection_reason_codes: str,
) -> dict[str, object]:
    return {
        "policy_id": policy_id,
        "selection": selection,
        "implementation_id": (
            "h2epr.policy.0288.scenario."
            f"{policy_id.lower().replace('-', '_')}"
        ),
        "implementation_version": "0.1.0",
        "owner_layer": owner_layer,
        "governed_semantic_ids": tuple(governed_semantic_ids),
        "rejection_reason_codes": tuple(rejection_reason_codes),
    }


TIME_POLICY = PartialOrderPolicy(
    **_policy_fields(
        "POL-TIME-01",
        "partial_order_with_stable_residual_tie_break",
        "scheduler",
        ("scenario.0288.time.partial_order_stable_residual_tie_break",),
        "time_event_invalid",
        "predecessor_unknown",
        "causal_order_conflict",
        "predecessor_cycle",
    )
)
INFORMATION_POLICY = InformationPolicy(
    **_policy_fields(
        "POL-INFO-01",
        "issue_route_delivery_and_freshness_separated",
        "information",
        ("scenario.0288.information.issue_route_delivery_freshness",),
        "information_input_invalid",
        "route_not_admitted",
        "delivery_expired",
        "mixed_version_compound_observation",
    )
)
SERVICE_POLICY = HostServicePolicy(
    **_policy_fields(
        "POL-SERVICE-01",
        "host_fifo_with_partial_service_and_stable_id_ties",
        "environment",
        ("scenario.0288.service.host_fifo_partial_service",),
        "service_input_invalid",
        "host_scope_mismatch",
        "duplicate_request",
    )
)
REVIEW_POLICY = TypedReviewPolicy(
    **_policy_fields(
        "POL-REVIEW-01",
        "typed_information_completeness_without_hidden_score",
        "environment",
        ("scenario.0288.review.typed_information_completeness",),
        "review_input_invalid",
        "review_item_outside_requirements",
        "review_item_class_conflict",
    )
)
AMOUNT_POLICY = QualitativeAmountPolicy(
    **_policy_fields(
        "POL-AMOUNT-01",
        "qualitative_bounded_band_no_auto_allocation",
        "environment",
        ("scenario.0288.amount.qualitative_bounded_band",),
        "amount_input_unsupported",
        "resource_owner_mismatch",
        "resource_information_missing",
    )
)
FACILITY_POLICY = DatedFacilityPolicy(
    **_policy_fields(
        "POL-FACILITY-01",
        "member_only_after_dated_activation",
        "environment",
        ("scenario.0288.facility.dated_member_activation",),
        "facility_time_invalid",
        "facility_membership_unsupported",
    )
)
VENUE_POLICY = ExplicitVenuePolicy(
    **_policy_fields(
        "POL-VENUE-01",
        "explicit_request_offer_match_booking_transfer_and_settlement",
        "environment",
        ("scenario.0288.venue.explicit_market_process",),
        "venue_input_invalid",
        "venue_stage_or_cause_invalid",
    )
)
LIFECYCLE_POLICY = EventRevisitPolicy(
    **_policy_fields(
        "POL-LIFECYCLE-01",
        "event_or_phase_revisit_with_horizon_carry_forward",
        "reducer",
        (
            "scenario.0288.lifecycle.event_revisit_horizon_carry_forward",
            "lifecycle.0288.governance_and_authority",
            "lifecycle.0288.information_and_examination",
            "lifecycle.0288.support_and_request_case",
            "lifecycle.0288.proposal_and_plan",
            "lifecycle.0288.solicitation_and_independent_reply",
            "lifecycle.0288.resource_commitment_and_execution",
            "lifecycle.0288.credit_and_clearing_relationship",
            "lifecycle.0288.institutional_communication",
            "lifecycle.0288.withdrawal_service_and_payment",
            "lifecycle.0288.collateral_and_facility_application",
            "lifecycle.0288.call_loan_contract",
            "lifecycle.0288.replacement_funding",
            "lifecycle.0288.position_reduction_and_venue_execution",
        ),
        "revisit_trigger_unsupported",
        "carry_forward_input_invalid",
    )
)
RESULT_POLICY = TypedResultPolicy(
    **_policy_fields(
        "POL-RESULT-01",
        "typed_disposition_result_and_later_delivery",
        "reducer",
        ("scenario.0288.result.typed_disposition_and_later_delivery",),
        "result_input_invalid",
        "execution_without_admission",
        "result_already_delivered",
    )
)


SCENARIO_POLICIES: tuple[ScenarioPolicy, ...] = (
    AMOUNT_POLICY,
    FACILITY_POLICY,
    INFORMATION_POLICY,
    LIFECYCLE_POLICY,
    RESULT_POLICY,
    REVIEW_POLICY,
    SERVICE_POLICY,
    TIME_POLICY,
    VENUE_POLICY,
)


def _aware_time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ScenarioPolicyError(f"time_invalid:{label}")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ScenarioPolicyError(f"time_invalid:{label}") from exc
    if result.tzinfo is None:
        raise ScenarioPolicyError(f"time_invalid:{label}")
    return result


def _optional_time(value: object, label: str) -> datetime | None:
    return None if value is None else _aware_time(value, label)


def _nonnegative_integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ScenarioPolicyError(f"integer_invalid:{label}")
    return value


def _positive_integer(value: object, label: str) -> int:
    result = _nonnegative_integer(value, label)
    if result == 0:
        raise ScenarioPolicyError(f"integer_invalid:{label}")
    return result


def _unique_ids(
    values: Sequence[str],
    label: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    result = tuple(_stable_id(value, label) for value in values)
    if (not result and not allow_empty) or len(result) != len(set(result)):
        raise ScenarioPolicyError(f"stable_id_sequence_invalid:{label}")
    return result


__all__ = [
    "AMOUNT_POLICY",
    "AmountAssessment",
    "CarryForwardRecord",
    "CompoundObservation",
    "DatedFacilityPolicy",
    "EventRevisitPolicy",
    "EventWindow",
    "ExplicitVenuePolicy",
    "FACILITY_POLICY",
    "HostServicePolicy",
    "INFORMATION_POLICY",
    "InformationDelivery",
    "InformationPolicy",
    "InformationProduct",
    "LIFECYCLE_POLICY",
    "LayeredResult",
    "PartialOrderPolicy",
    "QualitativeAmountPolicy",
    "RESULT_POLICY",
    "REVIEW_POLICY",
    "ReviewResult",
    "SCENARIO_POLICIES",
    "SERVICE_POLICY",
    "ScenarioPolicy",
    "ScenarioPolicyError",
    "ServiceRequest",
    "ServiceResult",
    "TIME_POLICY",
    "TypedResultPolicy",
    "TypedReviewPolicy",
    "VENUE_POLICY",
    "VenueProcess",
    "VenueTransition",
]
