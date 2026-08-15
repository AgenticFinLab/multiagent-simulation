from __future__ import annotations

import pytest

from masim.integrations.event_process import ActionDisposition, ActionIntent, MessageIntent, ObservationEnvelope, StateDelta


HASH = "a" * 64


def test_closed_action_intent_accepts_logical_scientific_fields() -> None:
    value = ActionIntent("i1", "r1", "a1", 1, 0, HASH, "no_op", {"reason_code": "test"}, "p1")
    assert value.to_dict()["logical_tick"] == 1


@pytest.mark.parametrize("field,value", [("logical_tick", -1), ("prestate_sha256", "short")])
def test_action_intent_rejects_invalid_coordinates(field: str, value: object) -> None:
    kwargs = dict(intent_id="i1", run_id="r1", actor_id="a1", logical_tick=1, prestate_version=0, prestate_sha256=HASH, action_type="no_op", parameters={}, policy_id="p1")
    kwargs[field] = value
    with pytest.raises(ValueError):
        ActionIntent(**kwargs)


def test_message_is_single_recipient_and_rejects_self_route() -> None:
    with pytest.raises(ValueError, match="self_message"):
        MessageIntent("m1", "r1", "i1", "a1", "a1", "route.a1.a1", 1, 1, "notice", {})


def test_nonaccepted_disposition_cannot_claim_state_delta() -> None:
    with pytest.raises(ValueError, match="nonaccepted"):
        ActionDisposition("d1", "i1", 1, "rejected", "invalid", ("delta.1",))


def test_observation_requires_same_physical_and_logical_tick() -> None:
    with pytest.raises(ValueError, match="physical_logical"):
        ObservationEnvelope("a1", 2, 1, 0, 0, HASH, {}, {})


def test_state_delta_rejects_zero_effect() -> None:
    with pytest.raises(ValueError, match="zero_effect"):
        StateDelta("d1", "i1", "a1", "x", 1, 1, "test")
