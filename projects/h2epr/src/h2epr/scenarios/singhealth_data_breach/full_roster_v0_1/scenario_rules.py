"""Scenario Rule policies selected by the SingHealth configuration."""

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


def _aware_time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ScenarioPolicyError(f"time_invalid:{label}")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ScenarioPolicyError(f"time_invalid:{label}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ScenarioPolicyError(f"time_timezone_missing:{label}")
    return parsed


def _optional_time(value: object, label: str) -> datetime | None:
    return None if value is None else _aware_time(value, label)


def _nonnegative_integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ScenarioPolicyError(f"nonnegative_integer_invalid:{label}")
    return value


def _boolean(value: object, reason_code: str) -> bool:
    if type(value) is not bool:
        raise ScenarioPolicyError(reason_code)
    return value


def _unique_ids(values: Sequence[str], label: str) -> tuple[str, ...]:
    result = tuple(_stable_id(value, label) for value in values)
    if len(result) != len(set(result)):
        raise ScenarioPolicyError(f"stable_id_duplicate:{label}")
    return result


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
class ScheduledEvent:
    event_id: str
    event_time: str
    phase_id: str
    predecessor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventTimePolicy(ScenarioPolicy):
    """Order causal predecessors, time, phase, and residual stable IDs."""

    phase_order: tuple[str, ...] = ()
    reopening_trigger_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        if (
            not self.phase_order
            or len(self.phase_order) != len(set(self.phase_order))
            or not self.reopening_trigger_ids
            or len(self.reopening_trigger_ids)
            != len(set(self.reopening_trigger_ids))
        ):
            raise ScenarioPolicyError("time_policy_boundary_incomplete")
        for value in (*self.phase_order, *self.reopening_trigger_ids):
            _stable_id(value, "time_policy_identity")

    def order_events(self, events: Sequence[ScheduledEvent]) -> tuple[str, ...]:
        phase_rank = {phase: index for index, phase in enumerate(self.phase_order)}
        parsed: dict[str, tuple[ScheduledEvent, datetime]] = {}
        for event in events:
            event_id = _stable_id(event.event_id, "event_id")
            if event_id in parsed:
                raise ScenarioPolicyError("time_event_duplicate")
            if event.phase_id not in phase_rank:
                raise ScenarioPolicyError("time_phase_unknown")
            predecessors = _unique_ids(event.predecessor_ids, "predecessor_id")
            parsed[event_id] = (
                replace(event, predecessor_ids=predecessors),
                _aware_time(event.event_time, "event_time"),
            )
        for event_id, (event, timestamp) in parsed.items():
            for predecessor_id in event.predecessor_ids:
                if predecessor_id not in parsed:
                    raise ScenarioPolicyError("time_predecessor_unknown")
                predecessor, predecessor_time = parsed[predecessor_id]
                if predecessor_time > timestamp or (
                    predecessor_time == timestamp
                    and phase_rank[predecessor.phase_id]
                    > phase_rank[event.phase_id]
                ):
                    raise ScenarioPolicyError(
                        f"time_causal_precedence_conflict:{predecessor_id}:{event_id}"
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
                key=lambda item: (
                    parsed[item][1],
                    phase_rank[parsed[item][0].phase_id],
                    item,
                ),
            )
            emitted.append(selected)
            emitted_set.add(selected)
            remaining.remove(selected)
        return tuple(emitted)

    def should_reopen(self, trigger_id: str) -> bool:
        _stable_id(trigger_id, "reopening_trigger_id")
        return trigger_id in self.reopening_trigger_ids


@dataclass(frozen=True)
class InformationProduct:
    product_id: str
    version: int
    producer_id: str
    issued_at: str
    as_of_time: str
    fresh_until: str | None
    expires_at: str | None
    visibility_recipient_ids: tuple[str, ...]
    supersedes_version: int | None = None


@dataclass(frozen=True)
class InformationDelivery:
    delivery_id: str
    product_id: str
    version: int
    recipient_id: str
    route_id: str
    route_disposition: str
    transport_disposition: str
    delivery_disposition: str
    delivered_at: str | None
    freshness: str


@dataclass(frozen=True)
class FrozenObservation:
    observation_id: str
    product_id: str
    product_version: int
    recipient_id: str
    delivery_id: str
    frozen_at: str
    freshness: str


@dataclass(frozen=True)
class InformationPolicy(ScenarioPolicy):
    """Keep production, route, delivery, freshness, and correction distinct."""

    def route_delivery(
        self,
        product: InformationProduct,
        *,
        delivery_id: str,
        recipient_id: str,
        route_id: str,
        route_admitted: bool,
        transported: bool,
        delivered_at: str | None,
    ) -> InformationDelivery:
        product_id = _stable_id(product.product_id, "product_id")
        _stable_id(product.producer_id, "producer_id")
        delivery = _stable_id(delivery_id, "delivery_id")
        recipient = _stable_id(recipient_id, "recipient_id")
        route = _stable_id(route_id, "route_id")
        version = _nonnegative_integer(product.version, "product_version")
        issued = _aware_time(product.issued_at, "issued_at")
        as_of = _aware_time(product.as_of_time, "as_of_time")
        fresh_until = _optional_time(product.fresh_until, "fresh_until")
        expiry = _optional_time(product.expires_at, "expires_at")
        visibility = _unique_ids(
            product.visibility_recipient_ids,
            "visibility_recipient_id",
        )
        admitted = _boolean(
            route_admitted,
            "information_route_admission_invalid",
        )
        transported_flag = _boolean(
            transported,
            "information_transport_flag_invalid",
        )
        if as_of > issued:
            raise ScenarioPolicyError("information_as_of_after_issue")
        if fresh_until is not None and fresh_until < as_of:
            raise ScenarioPolicyError("information_freshness_before_as_of")
        if expiry is not None and expiry < issued:
            raise ScenarioPolicyError("information_expiry_before_issue")
        if product.supersedes_version is not None:
            supersedes = _nonnegative_integer(
                product.supersedes_version,
                "supersedes_version",
            )
            if supersedes >= version:
                raise ScenarioPolicyError("information_supersession_invalid")
        visible = recipient in visibility
        if not admitted or not visible:
            if transported_flag or delivered_at is not None:
                raise ScenarioPolicyError("information_delivery_without_route")
            return InformationDelivery(
                delivery_id=delivery,
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition=(
                    "rejected" if not admitted else "visibility_rejected"
                ),
                transport_disposition="not_transported",
                delivery_disposition="not_delivered",
                delivered_at=None,
                freshness="unavailable",
            )
        if not transported_flag:
            if delivered_at is not None:
                raise ScenarioPolicyError("information_delivery_without_transport")
            return InformationDelivery(
                delivery_id=delivery,
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition="admitted",
                transport_disposition="pending",
                delivery_disposition="pending",
                delivered_at=None,
                freshness="unavailable",
            )
        if delivered_at is None:
            return InformationDelivery(
                delivery_id=delivery,
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition="admitted",
                transport_disposition="transported",
                delivery_disposition="pending",
                delivered_at=None,
                freshness="unavailable",
            )
        delivered = _aware_time(delivered_at, "delivered_at")
        if delivered < issued:
            raise ScenarioPolicyError("information_delivery_before_issue")
        if expiry is not None and delivered > expiry:
            return InformationDelivery(
                delivery_id=delivery,
                product_id=product_id,
                version=version,
                recipient_id=recipient,
                route_id=route,
                route_disposition="admitted",
                transport_disposition="transported",
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
            delivery_id=delivery,
            product_id=product_id,
            version=version,
            recipient_id=recipient,
            route_id=route,
            route_disposition="admitted",
            transport_disposition="transported",
            delivery_disposition="delivered",
            delivered_at=delivered_at,
            freshness=freshness,
        )

    def project_observation(
        self,
        delivery: InformationDelivery,
        *,
        observation_id: str,
        frozen_at: str,
    ) -> FrozenObservation:
        if delivery.delivery_disposition != "delivered" or not delivery.delivered_at:
            raise ScenarioPolicyError("information_projection_without_delivery")
        frozen = _aware_time(frozen_at, "frozen_at")
        if frozen < _aware_time(delivery.delivered_at, "delivered_at"):
            raise ScenarioPolicyError("information_projection_before_delivery")
        return FrozenObservation(
            observation_id=_stable_id(observation_id, "observation_id"),
            product_id=_stable_id(delivery.product_id, "product_id"),
            product_version=_nonnegative_integer(
                delivery.version,
                "product_version",
            ),
            recipient_id=_stable_id(delivery.recipient_id, "recipient_id"),
            delivery_id=_stable_id(delivery.delivery_id, "delivery_id"),
            frozen_at=frozen_at,
            freshness=delivery.freshness,
        )


@dataclass(frozen=True)
class TechnicalActionRequest:
    request_id: str
    actor_id: str
    target_id: str
    target_version: int
    authority_ref: str
    access_ref: str
    resource_owner_id: str


@dataclass(frozen=True)
class TechnicalAdmission:
    request_id: str
    accepted: bool
    reason_code: str
    target_id: str
    target_version: int
    authoritative_delta_id: str | None = None


@dataclass(frozen=True)
class TechnicalResult:
    result_id: str
    request_id: str
    result_kind: str
    reason_code: str
    authoritative_delta_id: str | None


@dataclass(frozen=True)
class TechnicalPolicy(ScenarioPolicy):
    """Adjudicate prerequisites without selecting a technical result."""

    result_kinds: tuple[str, ...] = ()

    def adjudicate(
        self,
        request: TechnicalActionRequest,
        *,
        authority_matches: bool,
        prestate_matches: bool,
        access_granted: bool,
        resource_owner_matches: bool,
        feasible: bool,
    ) -> TechnicalAdmission:
        request_id = _stable_id(request.request_id, "technical_request_id")
        target_id = _stable_id(request.target_id, "technical_target_id")
        _stable_id(request.actor_id, "technical_actor_id")
        _stable_id(request.authority_ref, "technical_authority_ref")
        _stable_id(request.access_ref, "technical_access_ref")
        _stable_id(request.resource_owner_id, "technical_resource_owner_id")
        version = _nonnegative_integer(request.target_version, "target_version")
        checks = (
            (
                _boolean(authority_matches, "technical_authority_flag_invalid"),
                "technical_authority_mismatch",
            ),
            (
                _boolean(prestate_matches, "technical_prestate_flag_invalid"),
                "technical_prestate_mismatch",
            ),
            (
                _boolean(access_granted, "technical_access_flag_invalid"),
                "technical_access_denied",
            ),
            (
                _boolean(
                    resource_owner_matches,
                    "technical_resource_owner_flag_invalid",
                ),
                "technical_resource_owner_mismatch",
            ),
            (
                _boolean(feasible, "technical_feasibility_flag_invalid"),
                "technical_infeasible",
            ),
        )
        failed = next((reason for passed, reason in checks if not passed), None)
        return TechnicalAdmission(
            request_id=request_id,
            accepted=failed is None,
            reason_code=failed or "technical_admitted_pending_execution",
            target_id=target_id,
            target_version=version,
            authoritative_delta_id=None,
        )

    def record_result(
        self,
        admission: TechnicalAdmission,
        *,
        result_id: str,
        result_kind: str,
        reason_code: str,
        authoritative_delta_id: str | None = None,
    ) -> TechnicalResult:
        if not admission.accepted:
            raise ScenarioPolicyError("technical_result_without_admission")
        if result_kind not in self.result_kinds:
            raise ScenarioPolicyError("technical_result_kind_unsupported")
        delta = (
            None
            if authoritative_delta_id is None
            else _stable_id(authoritative_delta_id, "authoritative_delta_id")
        )
        return TechnicalResult(
            result_id=_stable_id(result_id, "technical_result_id"),
            request_id=_stable_id(admission.request_id, "technical_request_id"),
            result_kind=result_kind,
            reason_code=_stable_id(reason_code, "technical_result_reason"),
            authoritative_delta_id=delta,
        )


@dataclass(frozen=True)
class MessageRouteRecord:
    message_id: str
    issuer_id: str
    recipient_id: str
    route_id: str
    state_id: str
    version: int
    causal_parent_ids: tuple[str, ...]


@dataclass(frozen=True)
class MessageRouteTransition:
    applied: bool
    reason_code: str
    before: MessageRouteRecord
    after: MessageRouteRecord


@dataclass(frozen=True)
class RoutePolicy(ScenarioPolicy):
    """Separate issue, route, transport, delivery, and acknowledgement."""

    transitions: tuple[tuple[str, str], ...] = ()

    def issue(
        self,
        *,
        message_id: str,
        issuer_id: str,
        recipient_id: str,
        route_id: str,
        cause_id: str,
    ) -> MessageRouteRecord:
        return MessageRouteRecord(
            message_id=_stable_id(message_id, "message_id"),
            issuer_id=_stable_id(issuer_id, "issuer_id"),
            recipient_id=_stable_id(recipient_id, "recipient_id"),
            route_id=_stable_id(route_id, "route_id"),
            state_id="issued",
            version=0,
            causal_parent_ids=(_stable_id(cause_id, "cause_id"),),
        )

    def admit_route(
        self,
        record: MessageRouteRecord,
        *,
        recipient_eligible: bool,
        route_available: bool,
        cause_id: str,
    ) -> MessageRouteTransition:
        self._validate_record(record)
        if record.state_id != "issued":
            return MessageRouteTransition(
                False,
                "route_admission_prestate_invalid",
                record,
                record,
            )
        eligible = _boolean(
            recipient_eligible,
            "route_recipient_eligibility_flag_invalid",
        )
        available = _boolean(
            route_available,
            "route_availability_flag_invalid",
        )
        if not eligible:
            target, reason = "route_rejected", "route_recipient_ineligible"
        elif not available:
            target, reason = "delayed", "route_unavailable"
        else:
            target, reason = "route_admitted", "route_admitted"
        return self._transition(record, target, cause_id, reason)

    def advance(
        self,
        record: MessageRouteRecord,
        *,
        target_state_id: str,
        cause_id: str,
    ) -> MessageRouteTransition:
        self._validate_record(record)
        if target_state_id not in {
            "transported",
            "delivered",
            "acknowledged",
            "failed",
            "corrected",
        }:
            return MessageRouteTransition(
                False,
                "route_target_state_unknown",
                record,
                record,
            )
        if (record.state_id, target_state_id) not in self.transitions:
            return MessageRouteTransition(
                False,
                "route_transition_invalid",
                record,
                record,
            )
        return self._transition(
            record,
            target_state_id,
            cause_id,
            "route_transition_applied",
        )

    def _transition(
        self,
        record: MessageRouteRecord,
        target_state_id: str,
        cause_id: str,
        reason_code: str,
    ) -> MessageRouteTransition:
        cause = _stable_id(cause_id, "cause_id")
        after = replace(
            record,
            state_id=target_state_id,
            version=record.version + 1,
            causal_parent_ids=tuple(
                dict.fromkeys((*record.causal_parent_ids, cause))
            ),
        )
        return MessageRouteTransition(True, reason_code, record, after)

    def _validate_record(self, record: MessageRouteRecord) -> None:
        for value in (
            record.message_id,
            record.issuer_id,
            record.recipient_id,
            record.route_id,
            *record.causal_parent_ids,
        ):
            _stable_id(value, "message_route_record")
        states = {source for source, _ in self.transitions} | {
            target for _, target in self.transitions
        }
        if (
            record.state_id not in states
            or type(record.version) is not int
            or record.version < 0
            or len(record.causal_parent_ids) != len(set(record.causal_parent_ids))
        ):
            raise ScenarioPolicyError("route_record_invalid")


@dataclass(frozen=True)
class CoordinationRecord:
    process_id: str
    owner_id: str
    state_id: str
    version: int
    invitee_ids: tuple[str, ...] = ()
    invitation_delivered_ids: tuple[str, ...] = ()
    attendee_ids: tuple[str, ...] = ()
    presented_material_ids: tuple[str, ...] = ()
    assignee_ids: tuple[str, ...] = ()
    result_ids: tuple[str, ...] = ()
    record_delivery_id: str | None = None
    causal_parent_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CoordinationTransition:
    applied: bool
    reason_code: str
    before: CoordinationRecord
    after: CoordinationRecord


@dataclass(frozen=True)
class CoordinationPolicy(ScenarioPolicy):
    """Keep requests, invitations, attendance, material, and results distinct."""

    transitions: tuple[tuple[str, str], ...] = ()

    def open(
        self,
        *,
        process_id: str,
        owner_id: str,
        cause_id: str,
    ) -> CoordinationRecord:
        return CoordinationRecord(
            process_id=_stable_id(process_id, "coordination_process_id"),
            owner_id=_stable_id(owner_id, "coordination_owner_id"),
            state_id="requested",
            version=0,
            causal_parent_ids=(_stable_id(cause_id, "cause_id"),),
        )

    def admit(
        self,
        record: CoordinationRecord,
        *,
        authority_admitted: bool,
        capacity_available: bool,
        cause_id: str,
    ) -> CoordinationTransition:
        self._validate_record(record)
        if record.state_id != "requested":
            return CoordinationTransition(
                False,
                "coordination_admission_prestate_invalid",
                record,
                record,
            )
        authority = _boolean(
            authority_admitted,
            "coordination_authority_flag_invalid",
        )
        capacity = _boolean(
            capacity_available,
            "coordination_capacity_flag_invalid",
        )
        if not authority:
            return self._transition(
                record,
                "rejected",
                cause_id,
                "coordination_unauthorized",
            )
        if not capacity:
            return self._transition(
                record,
                "rejected",
                cause_id,
                "coordination_capacity_unavailable",
            )
        return self._transition(
            record,
            "admitted",
            cause_id,
            "coordination_admitted",
        )

    def advance(
        self,
        record: CoordinationRecord,
        *,
        target_state_id: str,
        cause_id: str,
        invitee_ids: Sequence[str] = (),
        attendee_ids: Sequence[str] = (),
        presented_material_ids: Sequence[str] = (),
        assignee_ids: Sequence[str] = (),
        result_ids: Sequence[str] = (),
        record_delivery_id: str | None = None,
    ) -> CoordinationTransition:
        self._validate_record(record)
        if target_state_id in {"admitted", "rejected"}:
            return CoordinationTransition(
                False,
                "coordination_admission_requires_authority_check",
                record,
                record,
            )
        if (record.state_id, target_state_id) not in self.transitions:
            return CoordinationTransition(
                False,
                "coordination_transition_invalid",
                record,
                record,
            )
        invitees = _unique_ids(invitee_ids, "coordination_invitee_id")
        attendees = _unique_ids(attendee_ids, "coordination_attendee_id")
        materials = _unique_ids(
            presented_material_ids,
            "coordination_material_id",
        )
        assignees = _unique_ids(assignee_ids, "coordination_assignee_id")
        results = _unique_ids(result_ids, "coordination_result_id")
        updates: dict[str, object] = {}
        if target_state_id == "invited":
            if not invitees:
                raise ScenarioPolicyError("coordination_invitee_required")
            updates["invitee_ids"] = invitees
            updates["invitation_delivered_ids"] = invitees
        elif target_state_id == "invitation_partial":
            if not invitees or not set(invitees) < set(record.invitee_ids):
                raise ScenarioPolicyError(
                    "coordination_invitation_partial_invalid"
                )
            updates["invitation_delivered_ids"] = invitees
        elif target_state_id == "attended":
            eligible_attendees = (
                record.invitation_delivered_ids or record.invitee_ids
            )
            if not attendees or not set(attendees) <= set(eligible_attendees):
                raise ScenarioPolicyError("coordination_attendance_invalid")
            updates["attendee_ids"] = attendees
        elif target_state_id == "material_presented":
            if not record.attendee_ids or not materials:
                raise ScenarioPolicyError("coordination_material_invalid")
            updates["presented_material_ids"] = materials
        elif target_state_id == "action_assigned":
            if not assignees:
                raise ScenarioPolicyError("coordination_assignee_required")
            updates["assignee_ids"] = assignees
        elif target_state_id == "result_recorded":
            if not results:
                raise ScenarioPolicyError("coordination_result_required")
            updates["result_ids"] = results
        elif target_state_id == "record_delivered":
            if record_delivery_id is None:
                raise ScenarioPolicyError(
                    "coordination_record_delivery_required"
                )
            updates["record_delivery_id"] = _stable_id(
                record_delivery_id,
                "coordination_record_delivery_id",
            )
        return self._transition(
            record,
            target_state_id,
            cause_id,
            "coordination_transition_applied",
            **updates,
        )

    def _transition(
        self,
        record: CoordinationRecord,
        target_state_id: str,
        cause_id: str,
        reason_code: str,
        **updates: object,
    ) -> CoordinationTransition:
        cause = _stable_id(cause_id, "cause_id")
        after = replace(
            record,
            state_id=target_state_id,
            version=record.version + 1,
            causal_parent_ids=tuple(
                dict.fromkeys((*record.causal_parent_ids, cause))
            ),
            **updates,
        )
        return CoordinationTransition(True, reason_code, record, after)

    def _validate_record(self, record: CoordinationRecord) -> None:
        for value in (
            record.process_id,
            record.owner_id,
            *record.invitee_ids,
            *record.invitation_delivered_ids,
            *record.attendee_ids,
            *record.presented_material_ids,
            *record.assignee_ids,
            *record.result_ids,
            *record.causal_parent_ids,
        ):
            _stable_id(value, "coordination_record")
        if record.record_delivery_id is not None:
            _stable_id(
                record.record_delivery_id,
                "coordination_record_delivery_id",
            )
        states = {source for source, _ in self.transitions} | {
            target for _, target in self.transitions
        }
        if (
            record.state_id not in states
            or type(record.version) is not int
            or record.version < 0
            or any(
                len(values) != len(set(values))
                for values in (
                    record.invitee_ids,
                    record.invitation_delivered_ids,
                    record.attendee_ids,
                    record.presented_material_ids,
                    record.assignee_ids,
                    record.result_ids,
                    record.causal_parent_ids,
                )
            )
            or not set(record.invitation_delivered_ids)
            <= set(record.invitee_ids)
            or not set(record.attendee_ids)
            <= set(record.invitation_delivered_ids or record.invitee_ids)
        ):
            raise ScenarioPolicyError("coordination_record_invalid")


@dataclass(frozen=True)
class AuthorityClaim:
    claim_id: str
    actor_id: str
    capacity_id: str
    authority_ref: str
    relationship_ref: str
    access_ref: str
    resource_owner_id: str


@dataclass(frozen=True)
class AuthorityContext:
    active_capacity_ids: tuple[str, ...]
    effective_authority_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    access_refs: tuple[str, ...]
    resource_owner_id: str
    resource_available: bool


@dataclass(frozen=True)
class AuthorityDisposition:
    claim_id: str
    accepted: bool
    reason_code: str


@dataclass(frozen=True)
class AuthorityPolicy(ScenarioPolicy):
    """Check capacity, authority, relationship, access, and resource scope."""

    def evaluate(
        self,
        claim: AuthorityClaim,
        context: AuthorityContext,
    ) -> AuthorityDisposition:
        claim_id = _stable_id(claim.claim_id, "authority_claim_id")
        for value in (
            claim.actor_id,
            claim.capacity_id,
            claim.authority_ref,
            claim.relationship_ref,
            claim.access_ref,
            claim.resource_owner_id,
            context.resource_owner_id,
        ):
            _stable_id(value, "authority_scope")
        capacities = _unique_ids(
            context.active_capacity_ids,
            "active_capacity_id",
        )
        authorities = _unique_ids(
            context.effective_authority_refs,
            "effective_authority_ref",
        )
        relationships = _unique_ids(
            context.relationship_refs,
            "relationship_ref",
        )
        access = _unique_ids(context.access_refs, "access_ref")
        available = _boolean(
            context.resource_available,
            "authority_resource_availability_flag_invalid",
        )
        checks = (
            (claim.capacity_id in capacities, "authority_capacity_inactive"),
            (
                claim.authority_ref in authorities,
                "authority_scope_not_effective",
            ),
            (
                claim.relationship_ref in relationships,
                "authority_relationship_missing",
            ),
            (claim.access_ref in access, "authority_access_missing"),
            (
                claim.resource_owner_id == context.resource_owner_id,
                "authority_resource_owner_mismatch",
            ),
            (available, "authority_resource_unavailable"),
        )
        failed = next((reason for passed, reason in checks if not passed), None)
        return AuthorityDisposition(
            claim_id=claim_id,
            accepted=failed is None,
            reason_code=failed or "authority_scope_admitted",
        )


@dataclass(frozen=True)
class IncidentRecord:
    incident_id: str
    state_id: str
    version: int
    provisional_assessment: str | None = None
    proposed_category: str | None = None
    authoritative_category: str | None = None
    report_id: str | None = None
    institutional_acceptance: str | None = None
    causal_parent_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class IncidentTransition:
    applied: bool
    reason_code: str
    before: IncidentRecord
    after: IncidentRecord


@dataclass(frozen=True)
class IncidentPolicy(ScenarioPolicy):
    """Separate participant proposals from classification and report state."""

    def open(self, *, incident_id: str, cause_id: str) -> IncidentRecord:
        return IncidentRecord(
            incident_id=_stable_id(incident_id, "incident_id"),
            state_id="suspected",
            version=0,
            causal_parent_ids=(_stable_id(cause_id, "cause_id"),),
        )

    def begin_review(
        self,
        record: IncidentRecord,
        *,
        cause_id: str,
    ) -> IncidentTransition:
        return self._advance(
            record,
            expected_states=("suspected", "reopened"),
            target_state_id="under_review",
            cause_id=cause_id,
            reason_code="incident_review_opened",
        )

    def propose_category(
        self,
        record: IncidentRecord,
        *,
        category: str,
        cause_id: str,
    ) -> IncidentTransition:
        return self._advance(
            record,
            expected_states=("provisionally_assessed", "revised"),
            target_state_id="category_proposed",
            cause_id=cause_id,
            reason_code="incident_category_proposed",
            proposed_category=_stable_id(category, "proposed_category"),
        )

    def record_assessment(
        self,
        record: IncidentRecord,
        *,
        assessment: str,
        cause_id: str,
    ) -> IncidentTransition:
        return self._advance(
            record,
            expected_states=("under_review",),
            target_state_id="provisionally_assessed",
            cause_id=cause_id,
            reason_code="incident_provisional_assessment_recorded",
            provisional_assessment=_stable_id(
                assessment,
                "provisional_assessment",
            ),
        )

    def classify(
        self,
        record: IncidentRecord,
        *,
        category: str,
        authority_admitted: bool,
        cause_id: str,
    ) -> IncidentTransition:
        self._validate_record(record)
        admitted = _boolean(
            authority_admitted,
            "incident_authority_flag_invalid",
        )
        if record.state_id != "category_proposed" or not admitted:
            return IncidentTransition(
                False,
                (
                    "incident_classification_prestate_invalid"
                    if record.state_id != "category_proposed"
                    else "incident_classification_unauthorized"
                ),
                record,
                record,
            )
        return self._advance(
            record,
            expected_states=("category_proposed",),
            target_state_id="institutionally_classified",
            cause_id=cause_id,
            reason_code="incident_institutionally_classified",
            authoritative_category=_stable_id(
                category,
                "authoritative_category",
            ),
        )

    def issue_report(
        self,
        record: IncidentRecord,
        *,
        report_id: str,
        authority_admitted: bool,
        cause_id: str,
    ) -> IncidentTransition:
        self._validate_record(record)
        if not _boolean(
            authority_admitted,
            "incident_reporting_authority_flag_invalid",
        ):
            return IncidentTransition(
                False,
                "incident_reporting_unauthorized",
                record,
                record,
            )
        return self._advance(
            record,
            expected_states=("institutionally_classified",),
            target_state_id="report_issued",
            cause_id=cause_id,
            reason_code="incident_report_issued",
            report_id=_stable_id(report_id, "incident_report_id"),
        )

    def deliver_report(
        self,
        record: IncidentRecord,
        *,
        cause_id: str,
    ) -> IncidentTransition:
        return self._advance(
            record,
            expected_states=("report_issued",),
            target_state_id="report_delivered",
            cause_id=cause_id,
            reason_code="incident_report_delivered",
        )

    def record_institutional_response(
        self,
        record: IncidentRecord,
        *,
        accepted: bool,
        cause_id: str,
    ) -> IncidentTransition:
        disposition = _boolean(
            accepted,
            "incident_acceptance_flag_invalid",
        )
        return self._advance(
            record,
            expected_states=("report_delivered",),
            target_state_id=(
                "institutionally_accepted"
                if disposition
                else "institutionally_rejected"
            ),
            cause_id=cause_id,
            reason_code=(
                "incident_report_accepted"
                if disposition
                else "incident_report_rejected"
            ),
            institutional_acceptance=("accepted" if disposition else "rejected"),
        )

    def _advance(
        self,
        record: IncidentRecord,
        *,
        expected_states: Sequence[str],
        target_state_id: str,
        cause_id: str,
        reason_code: str,
        **updates: object,
    ) -> IncidentTransition:
        self._validate_record(record)
        if record.state_id not in expected_states:
            return IncidentTransition(
                False,
                "incident_transition_invalid",
                record,
                record,
            )
        cause = _stable_id(cause_id, "cause_id")
        after = replace(
            record,
            state_id=target_state_id,
            version=record.version + 1,
            causal_parent_ids=tuple(
                dict.fromkeys((*record.causal_parent_ids, cause))
            ),
            **updates,
        )
        return IncidentTransition(True, reason_code, record, after)

    def _validate_record(self, record: IncidentRecord) -> None:
        for value in (
            record.incident_id,
            *record.causal_parent_ids,
        ):
            _stable_id(value, "incident_record")
        for optional in (
            record.provisional_assessment,
            record.proposed_category,
            record.authoritative_category,
            record.report_id,
        ):
            if optional is not None:
                _stable_id(optional, "incident_record_optional")
        if (
            type(record.version) is not int
            or record.version < 0
            or len(record.causal_parent_ids) != len(set(record.causal_parent_ids))
        ):
            raise ScenarioPolicyError("incident_record_invalid")


@dataclass(frozen=True)
class IntentAdmission:
    intent_id: str
    idempotency_key: str
    accepted: bool
    duplicate: bool
    reason_code: str
    prior_disposition_id: str | None


@dataclass(frozen=True)
class AdjudicatedResult:
    result_id: str
    intent_id: str
    result_kind: str
    state_delta_id: str | None


@dataclass(frozen=True)
class ResultObservation:
    observation_id: str
    result_id: str
    recipient_id: str
    delivery_id: str


@dataclass(frozen=True)
class LifecyclePolicy(ScenarioPolicy):
    """Keep idempotency, disposition, result, delta, and observation separate."""

    result_kinds: tuple[str, ...] = ()

    def admit_intent(
        self,
        *,
        intent_id: str,
        idempotency_key: str,
        semantic_admitted: bool,
        prior_dispositions: Mapping[str, str],
    ) -> IntentAdmission:
        intent = _stable_id(intent_id, "intent_id")
        key = _stable_id(idempotency_key, "idempotency_key")
        admitted = _boolean(
            semantic_admitted,
            "lifecycle_semantic_admission_flag_invalid",
        )
        prior = prior_dispositions.get(key)
        if prior is not None:
            return IntentAdmission(
                intent_id=intent,
                idempotency_key=key,
                accepted=False,
                duplicate=True,
                reason_code="lifecycle_duplicate_prior_disposition",
                prior_disposition_id=_stable_id(
                    prior,
                    "prior_disposition_id",
                ),
            )
        return IntentAdmission(
            intent_id=intent,
            idempotency_key=key,
            accepted=admitted,
            duplicate=False,
            reason_code=(
                "lifecycle_intent_admitted"
                if admitted
                else "lifecycle_intent_rejected"
            ),
            prior_disposition_id=None,
        )

    def record_result(
        self,
        admission: IntentAdmission,
        *,
        result_id: str,
        result_kind: str,
        state_delta_id: str | None = None,
    ) -> AdjudicatedResult:
        if not admission.accepted or admission.duplicate:
            raise ScenarioPolicyError("lifecycle_result_without_new_admission")
        if result_kind not in self.result_kinds:
            raise ScenarioPolicyError("lifecycle_result_kind_unsupported")
        return AdjudicatedResult(
            result_id=_stable_id(result_id, "result_id"),
            intent_id=_stable_id(admission.intent_id, "intent_id"),
            result_kind=result_kind,
            state_delta_id=(
                None
                if state_delta_id is None
                else _stable_id(state_delta_id, "state_delta_id")
            ),
        )

    def project_observation(
        self,
        result: AdjudicatedResult,
        *,
        observation_id: str,
        recipient_id: str,
        delivery_id: str,
    ) -> ResultObservation:
        return ResultObservation(
            observation_id=_stable_id(observation_id, "observation_id"),
            result_id=_stable_id(result.result_id, "result_id"),
            recipient_id=_stable_id(recipient_id, "recipient_id"),
            delivery_id=_stable_id(delivery_id, "delivery_id"),
        )


@dataclass(frozen=True)
class NotificationRecord:
    plan_id: str
    state_id: str
    version: int
    content_version: int
    audience_ids: tuple[str, ...] = ()
    authorization_ref: str | None = None
    issue_ref: str | None = None
    delivered_recipient_ids: tuple[str, ...] = ()
    failed_recipient_ids: tuple[str, ...] = ()
    causal_parent_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class NotificationTransition:
    applied: bool
    reason_code: str
    before: NotificationRecord
    after: NotificationRecord


@dataclass(frozen=True)
class NotificationPolicy(ScenarioPolicy):
    """Separate preparation, consultation, authorization, issue, and delivery."""

    preparation_transitions: tuple[tuple[str, str], ...] = ()

    def open(self, *, plan_id: str, cause_id: str) -> NotificationRecord:
        return NotificationRecord(
            plan_id=_stable_id(plan_id, "notification_plan_id"),
            state_id="preparation_requested",
            version=0,
            content_version=0,
            causal_parent_ids=(_stable_id(cause_id, "cause_id"),),
        )

    def advance_preparation(
        self,
        record: NotificationRecord,
        *,
        target_state_id: str,
        cause_id: str,
        audience_ids: Sequence[str] = (),
    ) -> NotificationTransition:
        self._validate_record(record)
        if (record.state_id, target_state_id) not in self.preparation_transitions:
            return NotificationTransition(
                False,
                "notification_preparation_transition_invalid",
                record,
                record,
            )
        updates: dict[str, object] = {}
        audiences = _unique_ids(audience_ids, "notification_audience_id")
        if target_state_id == "readiness_assessed":
            if not audiences:
                raise ScenarioPolicyError("notification_audience_required")
            updates["audience_ids"] = audiences
        return self._transition(
            record,
            target_state_id,
            cause_id,
            "notification_preparation_advanced",
            **updates,
        )

    def authorize(
        self,
        record: NotificationRecord,
        *,
        granted: bool,
        authorization_ref: str,
        cause_id: str,
    ) -> NotificationTransition:
        self._validate_record(record)
        if record.state_id != "readiness_assessed":
            return NotificationTransition(
                False,
                "notification_authorization_prestate_invalid",
                record,
                record,
            )
        admitted = _boolean(
            granted,
            "notification_authorization_flag_invalid",
        )
        return self._transition(
            record,
            "authorized" if admitted else "authorization_declined",
            cause_id,
            (
                "notification_authorized"
                if admitted
                else "notification_authorization_declined"
            ),
            authorization_ref=_stable_id(
                authorization_ref,
                "notification_authorization_ref",
            ),
        )

    def issue(
        self,
        record: NotificationRecord,
        *,
        issue_ref: str,
        cause_id: str,
    ) -> NotificationTransition:
        self._validate_record(record)
        if record.state_id != "authorized":
            return NotificationTransition(
                False,
                "notification_issue_without_authorization",
                record,
                record,
            )
        return self._transition(
            record,
            "issued",
            cause_id,
            "notification_issued",
            issue_ref=_stable_id(issue_ref, "notification_issue_ref"),
        )

    def record_delivery(
        self,
        record: NotificationRecord,
        *,
        recipient_id: str,
        delivered: bool,
        cause_id: str,
    ) -> NotificationTransition:
        self._validate_record(record)
        if record.state_id not in {
            "issued",
            "delivery_partial",
            "delivery_failed",
        }:
            return NotificationTransition(
                False,
                "notification_delivery_prestate_invalid",
                record,
                record,
            )
        recipient = _stable_id(recipient_id, "notification_recipient_id")
        if recipient not in record.audience_ids:
            return NotificationTransition(
                False,
                "notification_recipient_ineligible",
                record,
                record,
            )
        resolved = set(record.delivered_recipient_ids) | set(
            record.failed_recipient_ids
        )
        if recipient in resolved:
            return NotificationTransition(
                False,
                "notification_recipient_already_resolved",
                record,
                record,
            )
        success = _boolean(
            delivered,
            "notification_delivery_flag_invalid",
        )
        delivered_ids = tuple(
            sorted(
                (
                    *record.delivered_recipient_ids,
                    *((recipient,) if success else ()),
                )
            )
        )
        failed_ids = tuple(
            sorted(
                (
                    *record.failed_recipient_ids,
                    *((recipient,) if not success else ()),
                )
            )
        )
        all_resolved = set(delivered_ids) | set(failed_ids) == set(
            record.audience_ids
        )
        if all_resolved and not failed_ids:
            state = "delivery_completed"
        elif all_resolved and not delivered_ids:
            state = "delivery_failed"
        else:
            state = "delivery_partial"
        return self._transition(
            record,
            state,
            cause_id,
            (
                "notification_recipient_delivered"
                if success
                else "notification_recipient_failed"
            ),
            delivered_recipient_ids=delivered_ids,
            failed_recipient_ids=failed_ids,
        )

    def correct(
        self,
        record: NotificationRecord,
        *,
        cause_id: str,
    ) -> NotificationTransition:
        self._validate_record(record)
        if record.state_id not in {
            "issued",
            "delivery_partial",
            "delivery_failed",
            "delivery_completed",
        }:
            return NotificationTransition(
                False,
                "notification_correction_prestate_invalid",
                record,
                record,
            )
        return self._transition(
            record,
            "revised",
            cause_id,
            "notification_corrected_new_version",
            content_version=record.content_version + 1,
            authorization_ref=None,
            issue_ref=None,
            delivered_recipient_ids=(),
            failed_recipient_ids=(),
        )

    def _transition(
        self,
        record: NotificationRecord,
        target_state_id: str,
        cause_id: str,
        reason_code: str,
        **updates: object,
    ) -> NotificationTransition:
        cause = _stable_id(cause_id, "cause_id")
        after = replace(
            record,
            state_id=target_state_id,
            version=record.version + 1,
            causal_parent_ids=tuple(
                dict.fromkeys((*record.causal_parent_ids, cause))
            ),
            **updates,
        )
        return NotificationTransition(True, reason_code, record, after)

    def _validate_record(self, record: NotificationRecord) -> None:
        for value in (
            record.plan_id,
            *record.audience_ids,
            *record.delivered_recipient_ids,
            *record.failed_recipient_ids,
            *record.causal_parent_ids,
        ):
            _stable_id(value, "notification_record")
        for optional in (record.authorization_ref, record.issue_ref):
            if optional is not None:
                _stable_id(optional, "notification_record_optional")
        if (
            type(record.version) is not int
            or record.version < 0
            or type(record.content_version) is not int
            or record.content_version < 0
            or set(record.delivered_recipient_ids)
            & set(record.failed_recipient_ids)
            or not (
                set(record.delivered_recipient_ids)
                | set(record.failed_recipient_ids)
            )
            <= set(record.audience_ids)
        ):
            raise ScenarioPolicyError("notification_record_invalid")


PHASE_ORDER = (
    "exogenous_input_admission",
    "scenario_process_or_technical_event",
    "information_product_production",
    "route_transport_and_delivery",
    "observation_projection_and_freeze",
    "participant_decision_and_issue",
    "adjudication",
    "execution_and_typed_result",
    "reducer_state_delta",
    "later_information_or_observation",
)

TIME_POLICY = EventTimePolicy(
    policy_id="POL-0616-TIME-01",
    selection="event_driven_partial_order_with_declared_same_time_precedence",
    implementation_id="h2epr.policy.0616.scenario.time",
    implementation_version="0.1.0",
    owner_layer="scheduler",
    governed_semantic_ids=(
        "scenario.0616.time.event_partial_order_and_reopening",
    ),
    rejection_reason_codes=(
        "time_event_duplicate",
        "time_phase_unknown",
        "time_predecessor_unknown",
        "time_causal_precedence_conflict",
        "time_predecessor_cycle",
    ),
    phase_order=PHASE_ORDER,
    reopening_trigger_ids=(
        "new_material_evidence",
        "failed_or_expired_intent",
        "recurrent_activity",
        "correction",
        "authority_or_capacity_change",
    ),
)

INFORMATION_POLICY = InformationPolicy(
    policy_id="POL-0616-INFO-01",
    selection=(
        "source_version_route_delivery_freshness_correction_and_visibility_separated"
    ),
    implementation_id="h2epr.policy.0616.scenario.information",
    implementation_version="0.1.0",
    owner_layer="information",
    governed_semantic_ids=(
        "scenario.0616.information.source_route_delivery_freshness_correction",
    ),
    rejection_reason_codes=(
        "information_supersession_invalid",
        "information_delivery_without_route",
        "information_delivery_without_transport",
        "information_projection_without_delivery",
        "information_visibility_rejected",
    ),
)

TECHNICAL_POLICY = TechnicalPolicy(
    policy_id="POL-0616-TECH-01",
    selection=(
        "authority_prestate_access_and_feasibility_adjudicated_without_selected_result"
    ),
    implementation_id="h2epr.policy.0616.scenario.technical",
    implementation_version="0.1.0",
    owner_layer="environment",
    governed_semantic_ids=(
        "scenario.0616.technical.authority_prestate_access_feasibility",
    ),
    rejection_reason_codes=(
        "technical_authority_mismatch",
        "technical_prestate_mismatch",
        "technical_access_denied",
        "technical_resource_owner_mismatch",
        "technical_infeasible",
        "technical_result_kind_unsupported",
    ),
    result_kinds=(
        "blocked",
        "failed",
        "delayed",
        "scheduled",
        "executed",
        "partial",
        "effective",
        "no_effect",
        "adverse",
        "reversed",
        "recurrent",
        "persisted",
        "detected",
        "contained",
    ),
)

ROUTE_POLICY = RoutePolicy(
    policy_id="POL-0616-ROUTE-01",
    selection=(
        "named_recipient_routes_with_distinct_issue_transport_delivery_and_acknowledgement"
    ),
    implementation_id="h2epr.policy.0616.scenario.route",
    implementation_version="0.1.0",
    owner_layer="environment",
    governed_semantic_ids=(
        "scenario.0616.route.issue_transport_delivery_acknowledgement",
    ),
    rejection_reason_codes=(
        "route_recipient_ineligible",
        "route_unavailable",
        "route_transition_invalid",
        "route_target_state_unknown",
        "route_admission_prestate_invalid",
    ),
    transitions=(
        ("issued", "route_admitted"),
        ("issued", "route_rejected"),
        ("issued", "delayed"),
        ("delayed", "route_admitted"),
        ("delayed", "failed"),
        ("route_admitted", "transported"),
        ("route_admitted", "failed"),
        ("transported", "delivered"),
        ("transported", "failed"),
        ("delivered", "acknowledged"),
        ("delivered", "corrected"),
        ("acknowledged", "corrected"),
    ),
)

COORDINATION_POLICY = CoordinationPolicy(
    policy_id="POL-0616-COORD-01",
    selection=(
        "invitation_attendance_presented_material_assignment_and_result_separated"
    ),
    implementation_id="h2epr.policy.0616.scenario.coordination",
    implementation_version="0.1.0",
    owner_layer="environment",
    governed_semantic_ids=(
        "scenario.0616.coordination.meeting_sirt_assignment",
    ),
    rejection_reason_codes=(
        "coordination_unauthorized",
        "coordination_capacity_unavailable",
        "coordination_transition_invalid",
        "coordination_attendance_invalid",
        "coordination_material_invalid",
    ),
    transitions=(
        ("requested", "admitted"),
        ("requested", "rejected"),
        ("admitted", "invited"),
        ("invited", "invitation_partial"),
        ("invited", "attended"),
        ("invited", "no_attendance"),
        ("invitation_partial", "attended"),
        ("invitation_partial", "no_attendance"),
        ("attended", "material_presented"),
        ("material_presented", "decision_recorded"),
        ("decision_recorded", "action_assigned"),
        ("decision_recorded", "result_recorded"),
        ("action_assigned", "result_recorded"),
        ("result_recorded", "record_delivered"),
        ("record_delivered", "closed"),
        ("no_attendance", "closed"),
        ("rejected", "closed"),
    ),
)

AUTHORITY_POLICY = AuthorityPolicy(
    policy_id="POL-0616-AUTH-01",
    selection="capacity_qualified_authority_relationship_access_and_resource_checks",
    implementation_id="h2epr.policy.0616.scenario.authority",
    implementation_version="0.1.0",
    owner_layer="environment",
    governed_semantic_ids=(
        "scenario.0616.authority.capacity_relationship_access_resource",
    ),
    rejection_reason_codes=(
        "authority_capacity_inactive",
        "authority_scope_not_effective",
        "authority_relationship_missing",
        "authority_access_missing",
        "authority_resource_owner_mismatch",
        "authority_resource_unavailable",
    ),
)

INCIDENT_POLICY = IncidentPolicy(
    policy_id="POL-0616-INCIDENT-01",
    selection=(
        "proposal_assessment_category_report_and_institutional_acceptance_separated"
    ),
    implementation_id="h2epr.policy.0616.scenario.incident",
    implementation_version="0.1.0",
    owner_layer="reducer",
    governed_semantic_ids=(
        "scenario.0616.incident.assessment_category_reporting_direction",
    ),
    rejection_reason_codes=(
        "incident_transition_invalid",
        "incident_classification_unauthorized",
        "incident_reporting_unauthorized",
        "incident_issue_without_classification",
        "incident_acceptance_without_delivery",
    ),
)

LIFECYCLE_POLICY = LifecyclePolicy(
    policy_id="POL-0616-LIFECYCLE-01",
    selection=(
        "typed_lifecycle_idempotency_adjudication_result_delta_and_later_observation"
    ),
    implementation_id="h2epr.policy.0616.scenario.lifecycle",
    implementation_version="0.1.0",
    owner_layer="reducer",
    governed_semantic_ids=(
        "scenario.0616.lifecycle.typed_adjudication_result_observation",
        "lifecycle.0616.participant_intent",
        "lifecycle.0616.information_product",
        "lifecycle.0616.investigation_or_verification_request",
        "lifecycle.0616.local_control_request",
        "lifecycle.0616.meeting_or_consultation",
        "lifecycle.0616.response_team_activation",
        "lifecycle.0616.incident_assessment_and_category",
        "lifecycle.0616.report_and_notification",
        "lifecycle.0616.investigation_assignment",
        "lifecycle.0616.outreach_plan",
        "lifecycle.0616.attack_and_technical_effect",
    ),
    rejection_reason_codes=(
        "lifecycle_duplicate_prior_disposition",
        "lifecycle_intent_rejected",
        "lifecycle_result_without_new_admission",
        "lifecycle_result_kind_unsupported",
        "lifecycle_invalid_transition",
    ),
    result_kinds=(
        "accepted",
        "pending",
        "partial",
        "completed",
        "declined",
        "failed",
        "expired",
        "cancelled",
        "superseded",
        "no_effect",
        "adverse",
    ),
)

NOTIFICATION_POLICY = NotificationPolicy(
    policy_id="POL-0616-NOTIFY-01",
    selection=(
        "preparation_consultation_authorization_issue_delivery_and_correction_separated"
    ),
    implementation_id="h2epr.policy.0616.scenario.notification",
    implementation_version="0.1.0",
    owner_layer="reducer",
    governed_semantic_ids=(
        "scenario.0616.notification.preparation_authorization_delivery",
    ),
    rejection_reason_codes=(
        "notification_preparation_transition_invalid",
        "notification_issue_without_authorization",
        "notification_recipient_ineligible",
        "notification_recipient_already_resolved",
        "notification_correction_prestate_invalid",
    ),
    preparation_transitions=(
        ("preparation_requested", "drafting"),
        ("drafting", "consultation"),
        ("drafting", "readiness_assessed"),
        ("consultation", "revised"),
        ("consultation", "readiness_assessed"),
        ("revised", "consultation"),
        ("revised", "readiness_assessed"),
    ),
)

SCENARIO_POLICIES = (
    AUTHORITY_POLICY,
    COORDINATION_POLICY,
    INCIDENT_POLICY,
    INFORMATION_POLICY,
    LIFECYCLE_POLICY,
    NOTIFICATION_POLICY,
    ROUTE_POLICY,
    TECHNICAL_POLICY,
    TIME_POLICY,
)
SCENARIO_POLICIES_BY_ID: Mapping[str, ScenarioPolicy] = MappingProxyType(
    {policy.policy_id: policy for policy in SCENARIO_POLICIES}
)

if len(SCENARIO_POLICIES_BY_ID) != len(SCENARIO_POLICIES):
    raise ValueError("singhealth_scenario_policy_registry_duplicate")


__all__ = [
    "AUTHORITY_POLICY",
    "COORDINATION_POLICY",
    "INCIDENT_POLICY",
    "INFORMATION_POLICY",
    "LIFECYCLE_POLICY",
    "NOTIFICATION_POLICY",
    "ROUTE_POLICY",
    "SCENARIO_POLICIES",
    "SCENARIO_POLICIES_BY_ID",
    "TECHNICAL_POLICY",
    "TIME_POLICY",
    "AdjudicatedResult",
    "AuthorityClaim",
    "AuthorityContext",
    "AuthorityDisposition",
    "CoordinationRecord",
    "CoordinationTransition",
    "FrozenObservation",
    "IncidentRecord",
    "IncidentTransition",
    "InformationDelivery",
    "InformationProduct",
    "IntentAdmission",
    "MessageRouteRecord",
    "MessageRouteTransition",
    "NotificationRecord",
    "NotificationTransition",
    "ResultObservation",
    "ScheduledEvent",
    "ScenarioPolicy",
    "ScenarioPolicyError",
    "TechnicalActionRequest",
    "TechnicalAdmission",
    "TechnicalResult",
]
