"""State/message activation, bounded memory, and outcome-neutral evidence."""

from __future__ import annotations

import asyncio
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import canonical_sha256, file_sha256, write_json
from h2epr.conformance import build_identity_invariance_receipt
from h2epr.publication import PublicationError, _verify_custody, publish_rule_run_release
from h2epr._publication_core import _verify_trace_semantics
from h2epr.runtime.benchmark_runner import BenchmarkEngine, materialize_run

from synthetic import SIGNAL_CASE as V, build_synthetic_event


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _behavioral_rules(settings):
    for row in settings["decision_rules"]:
        row.pop("coordinate_id")
        row["activation"] = {
            "start_coordinate_id": f"{V.slug}.c01",
            "end_coordinate_id": f"{V.slug}.c03",
            "retry_policy": "on_new_information",
        }
    settings["decision_rules"][0]["guards"] = [{
        "kind": "state", "entity_id": V.entity_id, "field_name": "status",
        "operator": "equals", "value": V.initial_value,
    }]
    response = settings["decision_rules"][1]
    response["guards"][0]["kind"] = "message_known"
    response["guards"].append({
        "kind": "state", "entity_id": V.entity_id, "field_name": "status",
        "operator": "equals", "value": V.intermediate_value,
    })


def _outcome_neutral(mechanism):
    expectation = mechanism["termination_invariants"].pop()
    mechanism["outcome_expectations"] = [{
        "expectation_id": "process_closed",
        "label": "The configured response closes the process",
        **expectation,
    }]


class ParticipantBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def _build(self, *, shared=None, rules=_behavioral_rules, mechanism=None):
        def world(value):
            _outcome_neutral(value)
            if mechanism is not None:
                mechanism(value)
        return build_synthetic_event(
            self.root, V, mechanism_transform=world,
            shared_settings_transform=shared, rule_settings_transform=rules,
        )

    def _run(self, event, name="run", variant="canonical"):
        root = self.root / name
        receipt = materialize_run(
            package_root=event.package_root, data_root=event.data_root,
            output_root=root, identity_variant=variant,
            custody_locator=(
                f".local-runtime/h2epr-simulation/runs/tests/behavior/{variant}"
            ),
        )
        trace = [json.loads(line) for line in
                 (root / "simulation_trace.jsonl").read_text().splitlines()]
        return root, receipt, trace

    @staticmethod
    def _actions(trace, actor):
        return [(row["logical_tick"], row["payload"]["action_type"])
                for row in trace if row["record_type"] == "action_intent"
                and row["payload"]["actor_id"] == actor]

    def test_delayed_information_reopens_a_choice_within_its_window(self):
        def delay(settings):
            settings["communication_routes"][0]["latency_ticks"] = 2
        event = self._build(shared=delay)
        _, receipt, trace = self._run(event)
        self.assertEqual([(1, "no_op"), (2, "no_op"), (3, V.second_intent)],
                         self._actions(trace, V.second_actor))
        self.assertTrue(receipt["replay_passed"])
        self.assertTrue(receipt["outcome_assessments"][0]["met"])

    def test_received_information_persists_beyond_its_delivery_tick(self):
        def later_response(settings):
            _behavioral_rules(settings)
            settings["decision_rules"][1]["activation"][
                "start_coordinate_id"] = f"{V.slug}.c03"
        event = self._build(rules=later_response)
        root, _, trace = self._run(event)
        observations = [row["payload"]["contract"] for row in trace
                        if row["record_type"] == "observation"
                        and row["payload"]["contract"]["actor_id"] == V.second_actor]
        self.assertEqual([], observations[2]["delivered_messages"])
        self.assertEqual(1, len(observations[2]["memory"]["received_messages"]))
        self.assertEqual((3, V.second_intent), self._actions(trace, V.second_actor)[-1])
        graph = _read(root / "generated_epg.json")
        def record_node(kind, tick):
            return next("record." + row["trace_id"] for row in trace
                        if row["record_type"] == kind and row["logical_tick"] == tick
                        and (kind != "observation" or
                             row["payload"]["contract"]["actor_id"] == V.second_actor))
        current = record_node("observation", 3)
        prior = record_node("observation", 2)
        delivery = next("record." + row["trace_id"] for row in trace
                        if row["record_type"] == "message_disposition"
                        and row["payload"]["status"] == "delivered")
        edge_keys = {(row["edge_type"], row["source_id"], row["target_id"])
                     for row in graph["edges"]}
        self.assertIn(("retains_memory_from", current, prior), edge_keys)
        self.assertIn(("received_from", prior, delivery), edge_keys)
        for row in trace:
            if row["record_type"] == "observation":
                self.assertEqual({"coordinate_id", "logical_tick"},
                                 set(row["payload"]["runtime"]["coordinate"]))

    def test_recipient_cannot_observe_an_undelivered_notice_in_memory(self):
        event = self._build()
        package = load_event_package(event.package_root, event.data_root, "rule")
        engine = BenchmarkEngine(package, backend_name="rule", run_seed=0)
        async def first_tick():
            await engine.setup()
            await engine.run_coordinate(engine.timeline[0])
            await engine.shutdown()
        asyncio.run(first_tick())
        self.assertEqual([], engine._pending_lifecycles(V.second_actor))
        self.assertTrue(engine._pending_lifecycles(V.first_actor))
        self.assertEqual([], engine.participant_memory[V.second_actor]["received_messages"])

    def test_known_message_can_expire_for_a_decision_without_erasing_memory(self):
        def stale(settings):
            _behavioral_rules(settings)
            response = settings["decision_rules"][1]
            response["activation"]["start_coordinate_id"] = f"{V.slug}.c03"
            response["guards"][0]["max_age_ticks"] = 0
        event = self._build(rules=stale)
        _, receipt, trace = self._run(event)
        self.assertEqual([(1, "no_op"), (2, "no_op"), (3, "no_op")],
                         self._actions(trace, V.second_actor))
        self.assertFalse(receipt["outcome_assessments"][0]["met"])

    def test_reversed_window_fails_at_admission(self):
        def reversed_window(settings):
            _behavioral_rules(settings)
            activation = settings["decision_rules"][0]["activation"]
            activation["start_coordinate_id"] = f"{V.slug}.c03"
            activation["end_coordinate_id"] = f"{V.slug}.c01"
        with self.assertRaisesRegex(ValueError, "rule_activation_window_reversed"):
            self._build(rules=reversed_window)

    def test_visibility_disagreement_fails_at_admission(self):
        def hide_state(mechanism):
            mechanism["state_fields"][0]["visibility"] = "environment_private"
        with self.assertRaisesRegex(ValueError, "scenario_interface_state_authority_mismatch"):
            self._build(mechanism=hide_state)

    def test_reordering_rule_rows_does_not_change_selection(self):
        event = self._build()
        package = load_event_package(event.package_root, event.data_root, "rule")
        from h2epr.backends.rule import DeclarativeRuleBackend
        # Unit-level ordering probe. Package resealing/admission is exercised
        # separately; both backend inputs below have the same declared rows.
        candidate = copy.deepcopy(package)
        rules = candidate.backend_configuration["settings"]["decision_rules"]
        fallback = copy.deepcopy(rules[0])
        fallback.update(rule_id="explicit_fallback", priority=20, guards=[], messages=[])
        fallback["action"] = {"action_type": "no_op", "parameters": {
            "target_id": V.first_actor, "reason_code": "no_declared_rule_matched",
        }}
        rules.append(fallback)
        backend = DeclarativeRuleBackend(candidate, run_id="run.row-order", run_seed=0)
        rules.reverse()
        reversed_backend = DeclarativeRuleBackend(candidate, run_id="run.row-order", run_seed=0)
        engine = BenchmarkEngine(package, backend_name="rule", run_seed=0)
        observations = {actor: engine._observation_bundle(
            actor_id=actor, coordinate=engine.timeline[0], state=engine.reducer.state,
            prestate_sha256=canonical_sha256(engine.reducer.state), delivered_messages=(),
        ) for actor in engine.actor_ids}
        left = asyncio.run(backend.decide(observations))
        right = asyncio.run(reversed_backend.decide(observations))
        self.assertEqual(V.first_intent, left[V.first_actor][0].action_type)
        self.assertEqual(left, right)

    def test_independent_verifier_rejects_invented_memories_and_outcomes(self):
        event = self._build()
        root, receipt, trace = self._run(event)
        package = load_event_package(event.package_root, event.data_root, "rule")
        forged_trace = copy.deepcopy(trace)
        observation = next(row["payload"]["contract"] for row in forged_trace
                           if row["record_type"] == "observation")
        observation["memory"]["own_actions"].append({
            "logical_tick": 1, "action_type": V.first_intent,
            "parameters": {"target_id": V.entity_id}, "status": "accepted",
            "reason_code": "admitted_applied", "lifecycle_state": "applied",
        })
        with self.assertRaisesRegex(PublicationError, "run_observation_memory_not_trace_derived"):
            _verify_trace_semantics(forged_trace, package, _read(root / "run_manifest.json"))
        receipt["outcome_assessments"][0]["met"] = False
        receipt["receipt_sha256"] = canonical_sha256({
            key: value for key, value in receipt.items() if key != "receipt_sha256"
        })
        write_json(root / "run_receipt.json", receipt)
        with self.assertRaisesRegex(PublicationError, "run_outcome_assessment_not_independently_derived"):
            _verify_custody(root, package, expected_identity_variant="canonical")

    def test_rejection_is_known_and_retry_waits_for_changed_information(self):
        def premature(settings):
            _behavioral_rules(settings)
            settings["decision_rules"][1]["guards"] = []
        event = self._build(rules=premature)
        _, receipt, trace = self._run(event)
        dispositions = [row["payload"] for row in trace
                        if row["record_type"] == "action_disposition"
                        and row["payload"]["actor_id"] == V.second_actor]
        self.assertEqual("rejected", dispositions[0]["status"])
        self.assertEqual("accepted", dispositions[1]["status"])
        self.assertEqual("no_op", dispositions[2]["action_type"])
        observation = next(row["payload"]["contract"] for row in trace
                           if row["record_type"] == "observation"
                           and row["logical_tick"] == 2
                           and row["payload"]["contract"]["actor_id"] == V.second_actor)
        self.assertEqual("rejected", observation["memory"]["own_actions"][0]["status"])
        self.assertTrue(receipt["replay_passed"])

    def test_unchanged_denial_is_not_retried_at_every_tick(self):
        def unavailable(mechanism):
            mechanism["intent_handlers"][1]["preconditions"][0]["value"] = V.terminal_value
        event = self._build(mechanism=unavailable)
        _, receipt, trace = self._run(event)
        self.assertEqual([(1, "no_op"), (2, V.second_intent), (3, "no_op")],
                         self._actions(trace, V.second_actor))
        self.assertFalse(receipt["outcome_assessments"][0]["met"])

    def test_open_outcome_publishes_with_replay_and_determinism_intact(self):
        def unavailable(mechanism):
            mechanism["intent_handlers"][1]["preconditions"][0]["value"] = V.terminal_value
        event = self._build(mechanism=unavailable)
        left, receipt, _ = self._run(event, "a")
        right, _, _ = self._run(event, "b")
        probe, _, _ = self._run(event, "probe", "generated-id-probe")
        self.assertFalse(receipt["outcome_assessments"][0]["met"])
        self.assertTrue(receipt["replay_passed"])
        self.assertEqual(V.intermediate_value,
                         _read(left / "final_state.json")["entities"][V.entity_id]["status"])
        self.assertEqual(file_sha256(left / "run_receipt.json"),
                         file_sha256(right / "run_receipt.json"))
        self.assertTrue(build_identity_invariance_receipt(left, probe)["passed"])
        publish_rule_run_release(
            package_root=event.package_root, data_root=event.data_root,
            canonical_root=left, repeat_root=right, probe_root=probe,
            release_root=self.root / "release", event_title=event.title,
            simulation_reading_link="../../../reports/example.md",
        )

    def test_failed_attempt_preserves_prefix_and_cannot_look_complete(self):
        event = build_synthetic_event(self.root, V)
        original = BenchmarkEngine.run_coordinate
        async def fail_second(engine, coordinate):
            if coordinate["logical_tick"] == 2:
                raise RuntimeError("synthetic_backend_unavailable")
            return await original(engine, coordinate)
        with patch.object(BenchmarkEngine, "run_coordinate", fail_second):
            with self.assertRaisesRegex(RuntimeError, "synthetic_backend_unavailable"):
                self._run(event)
        root = self.root / "run"
        failure = _read(root / "failure-receipt.json")
        self.assertEqual("failed", failure["status"])
        self.assertEqual([1], failure["sealed_logical_ticks"])
        self.assertTrue((root / "simulation_trace.jsonl").is_file())
        self.assertFalse((root / "run_receipt.json").exists())
        self.assertFalse((root / "run_seal.json").exists())
        package = load_event_package(event.package_root, event.data_root, "rule")
        with self.assertRaisesRegex(PublicationError, "failed_attempt_not_publishable"):
            _verify_custody(root, package, expected_identity_variant="canonical")
        with self.assertRaises(FileExistsError):
            self._run(event)

    def test_transport_failure_still_blocks_a_complete_release(self):
        def late(settings):
            settings["communication_routes"][0]["latency_ticks"] = 5
        event = self._build(shared=late)
        with self.assertRaisesRegex(RuntimeError, "unresolved_transport_at_termination"):
            self._run(event)
        failure = _read(self.root / "run" / "failure-receipt.json")
        self.assertEqual([1, 2, 3], failure["sealed_logical_ticks"])
        self.assertEqual(1, len(failure["unresolved_message_intent_ids"]))
        self.assertFalse((self.root / "run" / "run_receipt.json").exists())

    def test_setup_failure_preserves_an_empty_attempt(self):
        event = build_synthetic_event(self.root, V)
        async def unavailable(engine):
            raise RuntimeError("synthetic_setup_unavailable")
        with patch.object(BenchmarkEngine, "setup", unavailable):
            with self.assertRaisesRegex(RuntimeError, "synthetic_setup_unavailable"):
                self._run(event)
        failure = _read(self.root / "run" / "failure-receipt.json")
        self.assertEqual([], failure["sealed_logical_ticks"])
        self.assertEqual(0, failure["trace_record_count"])


if __name__ == "__main__":
    unittest.main()
