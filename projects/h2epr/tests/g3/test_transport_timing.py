from __future__ import annotations

from masim.integrations.event_process import AppendOnlyTransport, MessageIntent


def _transport() -> AppendOnlyTransport:
    return AppendOnlyTransport([{"route_id": "route.a.b", "source_id": "a", "target_id": "b", "latency_ticks": 1}])


def _intent(recipient: str = "b") -> MessageIntent:
    return MessageIntent("m1", "run", "i1", "a", recipient, f"route.a.{recipient}", 1, 1, "support_request", {"request_intent_id": "i1"})


def test_one_tick_latency_and_no_same_tick_consumption() -> None:
    transport = _transport()
    assert transport.submit([_intent()], logical_tick=1)[0].status == "queued"
    assert transport.route_due(1) == ((), ())
    assert transport.consume("b", 1) == ()
    deliveries, dispositions = transport.route_due(2)
    assert dispositions[0].status == "delivered"
    assert deliveries[0]["first_consumable_tick"] == 2
    assert transport.consume("b", 2)[0]["message_intent_id"] == "m1"


def test_invalid_route_is_terminal_rejection() -> None:
    disposition = _transport().submit([_intent("c")], logical_tick=1)[0]
    assert disposition.status == "rejected"


def test_unresolved_sets_are_exact_and_recipient_specific() -> None:
    transport = _transport()
    transport.submit([_intent()], logical_tick=1)
    assert transport.unresolved() == (("m1",), ("m1:b",))


def test_duplicate_message_id_is_append_only_terminal_attempt() -> None:
    transport = _transport()
    transport.submit([_intent()], logical_tick=1)
    assert transport.submit([_intent()], logical_tick=1)[0].status == "duplicate"
    assert len(transport.history) == 2
