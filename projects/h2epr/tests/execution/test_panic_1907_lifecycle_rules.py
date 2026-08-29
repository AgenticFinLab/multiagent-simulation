from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

import pytest

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    build_panic_policy_catalog,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.lifecycle_rules import (
    LIFECYCLE_RULES,
    LifecycleRecord,
    LifecycleRuleError,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.registry import (
    implementation_versions,
    lifecycle_rule,
    lifecycle_rules,
    participant_policies,
)


def test_lifecycle_registry_closes_the_catalog_and_participant_references() -> None:
    catalog = build_panic_policy_catalog()
    registry = lifecycle_rules()
    versions = implementation_versions()
    participants_by_lifecycle: dict[str, set[str]] = defaultdict(set)
    for participant in participant_policies().values():
        for decision in participant.decisions.values():
            for lifecycle_id in decision.lifecycle_ids:
                participants_by_lifecycle[lifecycle_id].add(
                    participant.capability_id
                )

    assert {rule.lifecycle_id for rule in LIFECYCLE_RULES} == set(
        catalog.lifecycle_ids
    )
    assert len(registry) == 13
    assert len(versions) == 34
    for rule in LIFECYCLE_RULES:
        assert set(rule.participant_capability_ids) == participants_by_lifecycle[
            rule.lifecycle_id
        ]
        assert registry[rule.implementation_id] is rule
        assert lifecycle_rule(rule.implementation_id) is rule
        assert versions[rule.implementation_id] == "0.1.0"
    with pytest.raises(KeyError, match="unknown_lifecycle_rule"):
        lifecycle_rule("h2epr.lifecycle.0288.unknown")


def test_every_declared_lifecycle_state_is_reachable_from_an_initial_state() -> None:
    for rule in LIFECYCLE_RULES:
        reached = set(rule.initial_state_ids)
        changed = True
        while changed:
            changed = False
            for source, target in rule.transitions:
                if source in reached and target not in reached:
                    reached.add(target)
                    changed = True
        assert reached == set(rule.state_ids), rule.lifecycle_id


def test_every_declared_lifecycle_transition_is_deterministic_and_versioned() -> None:
    for rule in LIFECYCLE_RULES:
        for index, (source, target) in enumerate(rule.transitions):
            record = LifecycleRecord(
                object_id=f"object.{index}",
                lifecycle_id=rule.lifecycle_id,
                owner_actor_id="actor.owner",
                state_id=source,
                version=4,
                terminal=source in rule.terminal_state_ids,
                causal_parent_ids=("event.open",),
            )

            first = rule.transition(
                record,
                target_state_id=target,
                cause_id="event.transition",
            )
            second = rule.transition(
                record,
                target_state_id=target,
                cause_id="event.transition",
            )

            assert first == second
            assert first.applied is True
            assert first.before is record
            assert first.after.state_id == target
            assert first.after.version == 5
            assert first.after.terminal == (target in rule.terminal_state_ids)
            assert first.after.causal_parent_ids == (
                "event.open",
                "event.transition",
            )


def test_invalid_lifecycle_transitions_are_typed_and_non_mutating() -> None:
    for rule in LIFECYCLE_RULES:
        record = rule.open_record(
            object_id=f"object.{rule.lifecycle_id.rsplit('.', 1)[-1]}",
            owner_actor_id="actor.owner",
            initial_state_id=rule.initial_state_ids[0],
            causal_parent_ids=("event.open",),
        )
        unknown = rule.transition(
            record,
            target_state_id="unknown_state",
            cause_id="event.invalid",
        )
        duplicate = rule.transition(
            record,
            target_state_id=record.state_id,
            cause_id="event.invalid",
        )

        assert unknown.applied is False
        assert unknown.reason_code == "lifecycle_target_state_unknown"
        assert unknown.after is record
        assert duplicate.applied is False
        assert duplicate.reason_code == "lifecycle_transition_invalid"
        assert duplicate.after is record


def test_malformed_lifecycle_records_fail_before_reduction() -> None:
    rule = LIFECYCLE_RULES[0]
    record = rule.open_record(
        object_id="object.valid",
        owner_actor_id="actor.owner",
        initial_state_id=rule.initial_state_ids[0],
    )

    with pytest.raises(LifecycleRuleError, match="lifecycle_record_invalid"):
        rule.transition(
            replace(record, lifecycle_id="lifecycle.0288.wrong"),
            target_state_id=rule.transitions[0][1],
            cause_id="event.transition",
        )
    with pytest.raises(LifecycleRuleError, match="lifecycle_record_invalid"):
        rule.transition(
            replace(record, terminal=not record.terminal),
            target_state_id=rule.transitions[0][1],
            cause_id="event.transition",
        )
    with pytest.raises(LifecycleRuleError, match="lifecycle_initial_state_invalid"):
        rule.open_record(
            object_id="object.invalid",
            owner_actor_id="actor.owner",
            initial_state_id=rule.transitions[0][1],
        )
