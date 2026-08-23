"""Append-only single-recipient message transport with logical timing."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .model import MessageDisposition, MessageIntent
from .seals import canonical_sha256


TERMINAL = {"delivered", "expired", "rejected", "duplicate", "failed"}


class AppendOnlyTransport:
    def __init__(self, routes: Iterable[dict]) -> None:
        self._routes = {item["route_id"]: dict(item) for item in routes}
        self._intents: dict[str, MessageIntent] = {}
        self._history: list[MessageDisposition] = []
        self._delivered: dict[tuple[int, str], list[dict]] = defaultdict(list)

    @property
    def history(self) -> tuple[MessageDisposition, ...]:
        return tuple(self._history)

    def submit(self, intents: Iterable[MessageIntent], *, logical_tick: int) -> tuple[MessageDisposition, ...]:
        emitted: list[MessageDisposition] = []
        for intent in sorted(intents, key=lambda item: item.message_intent_id):
            route = self._routes.get(intent.route_id)
            status, reason = "queued", "route_accepted"
            predecessor_disposition_id = None
            duplicate_of_intent_id = None
            if intent.logical_tick != logical_tick:
                status, reason = "rejected", "send_tick_mismatch"
            elif intent.message_intent_id in self._intents:
                status, reason = "duplicate", "duplicate_message_intent_id"
                predecessor_disposition_id = self._latest_lifecycle()[
                    intent.message_intent_id
                ].disposition_id
                duplicate_of_intent_id = intent.message_intent_id
            elif not route or route.get("source_id") != intent.sender_id or route.get("target_id") != intent.recipient_id:
                status, reason = "rejected", "route_mismatch"
            elif route.get("latency_ticks") != intent.latency_ticks:
                status, reason = "rejected", "latency_mismatch"
            disposition = MessageDisposition(
                f"md.{intent.message_intent_id}.{len(self._history)}",
                intent.message_intent_id,
                intent.sender_id,
                intent.recipient_id,
                logical_tick,
                status,
                reason,
                predecessor_disposition_id=predecessor_disposition_id,
                duplicate_of_intent_id=duplicate_of_intent_id,
            )
            self._history.append(disposition)
            emitted.append(disposition)
            if status == "queued":
                self._intents[intent.message_intent_id] = intent
        return tuple(emitted)

    def route_due(self, logical_tick: int) -> tuple[tuple[dict, ...], tuple[MessageDisposition, ...]]:
        deliveries: list[dict] = []
        emitted: list[MessageDisposition] = []
        latest = self._latest_lifecycle()
        for intent_id in sorted(self._intents):
            intent = self._intents[intent_id]
            if latest[intent_id].status in TERMINAL:
                continue
            due_tick = intent.logical_tick + intent.latency_ticks
            if logical_tick < due_tick:
                continue
            payload = {
                "message_id": f"msg.{intent_id}",
                "message_intent_id": intent_id,
                "sender_id": intent.sender_id,
                "recipient_id": intent.recipient_id,
                "send_tick": intent.logical_tick,
                "earliest_delivery_tick": due_tick,
                "due_tick": due_tick,
                "first_consumable_tick": logical_tick,
                "message_kind": intent.message_kind,
                "payload": dict(intent.payload),
                "intent_content_sha256": canonical_sha256(intent.to_dict()),
            }
            disposition = MessageDisposition(
                f"md.{intent_id}.{len(self._history)}",
                intent_id,
                intent.sender_id,
                intent.recipient_id,
                logical_tick,
                "delivered",
                "delivered_after_actor_barrier",
                predecessor_disposition_id=latest[intent_id].disposition_id,
            )
            self._history.append(disposition)
            self._delivered[(logical_tick, intent.recipient_id)].append(payload)
            deliveries.append(payload)
            emitted.append(disposition)
        return tuple(deliveries), tuple(emitted)

    def consume(self, actor_id: str, logical_tick: int) -> tuple[dict, ...]:
        matches = self._delivered.pop((logical_tick, actor_id), [])
        return tuple(sorted(matches, key=lambda item: item["message_intent_id"]))

    def unresolved(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        latest = self._latest_lifecycle()
        unresolved = sorted(key for key, value in latest.items() if value.status not in TERMINAL)
        recipients = sorted(f"{key}:{latest[key].recipient_id}" for key in unresolved)
        return tuple(unresolved), tuple(recipients)

    def _latest_lifecycle(self) -> dict[str, MessageDisposition]:
        """Return lifecycle dispositions without letting duplicate attempts replace them."""
        latest: dict[str, MessageDisposition] = {}
        for item in self._history:
            if item.status != "duplicate":
                latest[item.message_intent_id] = item
        return latest
