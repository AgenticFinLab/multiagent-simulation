"""Backend-independent receipt admission and content-sensitive Rule choices."""

from __future__ import annotations

import asyncio
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from h2epr.benchmark.package import load_event_package
from h2epr.runtime.benchmark_runner import BenchmarkEngine, materialize_run
from h2epr.runtime.environment import build_environment
from h2epr.runtime.information import matching_receipts, payload_error
from h2epr.masim_kernel import ActionIntent, MessageIntent
from h2epr.canonical import canonical_sha256
from h2epr._publication_core import _verify_trace_semantics

from synthetic import SIGNAL_CASE as V, build_synthetic_event
from runtime.test_participant_behavior import _behavioral_rules, _outcome_neutral


REQUIREMENT = {
    "message_kind": V.message_kind, "sender_id": V.first_actor,
    "selection": "latest", "payload_equals": {"status": "qualified"},
}
DOMAIN = {"status": {"value_type": "string",
                     "allowed_values": ["qualified", "unresolved", "withdrawn"]}}


def _mechanism(value):
    _outcome_neutral(value)
    value["message_kinds"][0]["payload_fields"] = copy.deepcopy(DOMAIN)
    handler = next(row for row in value["intent_handlers"] if row["intent_id"] == V.second_intent)
    handler["information_requirements"] = [copy.deepcopy(REQUIREMENT)]


def _rules(value, status="qualified"):
    _behavioral_rules(value)
    value["decision_rules"][0]["messages"][0]["payload"] = {"status": status}
    value["decision_rules"][1]["guards"][0].update(REQUIREMENT)


class InformationContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _build(self, status="qualified"):
        return build_synthetic_event(
            self.root, V, mechanism_transform=_mechanism,
            rule_settings_transform=lambda value: _rules(value, status))

    def test_latest_negative_or_ambiguous_report_does_not_revive_old_positive(self):
        def receipt(status, tick):
            return {"message_kind": V.message_kind, "sender_id": V.first_actor,
                    "first_consumable_tick": tick, "payload": {"status": status}}
        positive = receipt("qualified", 1)
        for status in ("withdrawn", "unresolved"):
            with self.subTest(status=status):
                self.assertFalse(matching_receipts(REQUIREMENT, [positive, receipt(status, 2)], 2))
                self.assertFalse(matching_receipts(REQUIREMENT, [positive, receipt(status, 1)], 1))
        self.assertTrue(matching_receipts(REQUIREMENT, [receipt("unresolved", 1), receipt("qualified", 2)], 2))
        self.assertFalse(matching_receipts(REQUIREMENT, [receipt("qualified", 2)], 1))

    def test_payload_is_closed_typed_and_empty_is_not_positive(self):
        for payload in ({}, {"status": True}, {"status": "invented"},
                        {"status": "qualified", "extra": 1}):
            with self.subTest(payload=payload):
                self.assertIsNotNone(payload_error(payload, {"payload_fields": DOMAIN}))
        self.assertIsNone(payload_error({"status": "unresolved"}, {"payload_fields": DOMAIN}))
        self.assertIsNone(payload_error({}, {}))  # An untyped notification is distinct.

    def test_negative_report_produces_valid_open_run(self):
        event = self._build("unresolved")
        receipt = materialize_run(package_root=event.package_root, data_root=event.data_root,
                                  output_root=self.root / "negative")
        self.assertTrue(receipt["replay_passed"])
        self.assertFalse(receipt["outcome_assessments"][0]["met"])

    def test_environment_denies_backend_bypass_without_received_content(self):
        event = self._build()
        package = load_event_package(event.package_root, event.data_root, "rule")
        engine = BenchmarkEngine(package, backend_name="rule", run_seed=0)
        async def check():
            await engine.setup()
            await engine.run_coordinate(engine.timeline[0])
            await engine.shutdown()
        asyncio.run(check())
        observation = next(row["payload"] for row in engine.trace.records
                           if row["record_type"] == "observation"
                           and row["payload"]["contract"]["actor_id"] == V.second_actor)
        # Make world feasibility true. This still cannot stand in for receipt.
        state = copy.deepcopy(package.scenario["initial_state"])
        state["entities"][V.entity_id]["status"] = V.intermediate_value
        action = ActionIntent(intent_id="bypass", run_id=engine.manifest["run_id"],
                              actor_id=V.second_actor, logical_tick=1, prestate_version=0,
                              prestate_sha256=canonical_sha256(state), action_type=V.second_intent,
                              parameters={"target_id": V.entity_id}, policy_id="untrusted.policy")
        environment = build_environment(package.scenario)
        dispositions, deltas = environment.apply_batch(copy.deepcopy(state), (action,), 0, 1)
        self.assertEqual("admission_observation_missing", dispositions[0].reason_code)
        environment.bind_observations({V.second_actor: observation})
        dispositions, deltas = environment.apply_batch(copy.deepcopy(state), (action,), 0, 1)
        self.assertEqual("information_requirement_not_met", dispositions[0].reason_code)
        self.assertEqual([], deltas)

        stale = copy.deepcopy(observation)
        stale["contract"]["logical_tick"] = 0
        environment.bind_observations({V.second_actor: stale})
        dispositions, deltas = environment.apply_batch(copy.deepcopy(state), (action,), 0, 1)
        self.assertEqual("admission_observation_stale", dispositions[0].reason_code)
        self.assertEqual([], deltas)

    def test_compiler_rejects_malformed_typed_message(self):
        with self.assertRaisesRegex(ValueError, "rule_message_payload_invalid"):
            self._build("invented")

    def test_compiler_rejects_content_predicate_without_typed_declaration(self):
        def untyped(value):
            _mechanism(value)
            del value["message_kinds"][0]["payload_fields"]
        with self.assertRaisesRegex(ValueError, "information_requirement_field_untyped"):
            build_synthetic_event(self.root, V, mechanism_transform=untyped,
                                  rule_settings_transform=_rules)

    def test_current_singhealth_findings_require_positive_content(self):
        project = Path(__file__).resolve().parents[2]
        mechanism = json.loads((project / "scenarios/singhealth_data_breach/scenario-mechanism.json").read_text())
        rule = json.loads((project / "configs/singhealth_data_breach/backends/rule/rule-configuration.json").read_text())
        declaration = next(row for row in mechanism["message_kinds"] if row["message_kind"] == "coi_findings")
        guards = [guard for row in rule["settings"]["decision_rules"] for guard in row["guards"]
                  if guard.get("message_kind") == "coi_findings"]
        self.assertEqual(2, len(guards))
        self.assertIsNotNone(payload_error({}, declaration))
        for guard in guards:
            for status in ("qualified findings and recommendations", "unresolved", "withdrawn"):
                receipt = {"message_kind": "coi_findings", "sender_id": guard["sender_id"],
                           "first_consumable_tick": 1, "payload": {"status": status}}
                self.assertIsNone(payload_error(receipt["payload"], declaration))
                self.assertEqual(status == "qualified findings and recommendations",
                                 bool(matching_receipts(guard, [receipt], 1)))

    def test_compiler_rejects_an_unimplemented_prefix_clean_vocabulary_claim(self):
        def false_profile(value):
            value["observation_contract"]["vocabulary_exposure"] = "historically_prefix_clean"
        with self.assertRaisesRegex(ValueError, "schema_invalid|configuration_vocabulary_exposure_unsupported"):
            build_synthetic_event(self.root, V, shared_settings_transform=false_profile)

    def test_shared_admission_rejects_early_rule_bypass_then_reopens_on_receipt(self):
        def bypass(value):
            _rules(value)
            value["decision_rules"][1]["guards"] = value["decision_rules"][1]["guards"][1:]
        def delay(value):
            value["communication_routes"][0]["latency_ticks"] = 2
        event = build_synthetic_event(self.root, V, mechanism_transform=_mechanism,
                                     shared_settings_transform=delay, rule_settings_transform=bypass)
        root = self.root / "bypass"
        receipt = materialize_run(package_root=event.package_root, data_root=event.data_root, output_root=root)
        trace = [json.loads(line) for line in (root / "simulation_trace.jsonl").read_text().splitlines()]
        decisions = [(row["logical_tick"], row["payload"]["status"], row["payload"]["reason_code"])
                     for row in trace if row["record_type"] == "action_disposition"
                     and row["payload"]["action_type"] == V.second_intent]
        self.assertEqual([(2, "rejected", "information_requirement_not_met"),
                          (3, "accepted", "admitted_applied")], decisions)
        package = load_event_package(event.package_root, event.data_root, "rule")
        _verify_trace_semantics(trace, package, json.loads((root / "run_manifest.json").read_text()))
        self.assertTrue(receipt["outcome_assessments"][0]["met"])

    def test_runtime_rejects_malformed_backend_message(self):
        event = self._build()
        package = load_event_package(event.package_root, event.data_root, "rule")
        engine = BenchmarkEngine(package, backend_name="rule", run_seed=0)
        decide = engine.backend.decide
        async def invalid(observations):
            results = await decide(observations)
            action, messages = results[V.first_actor]
            results[V.first_actor] = (action, (MessageIntent(**{**messages[0].to_dict(), "payload": {}}),))
            return results
        async def check():
            await engine.setup()
            try:
                with patch.object(engine.backend, "decide", invalid):
                    await engine.run_coordinate(engine.timeline[0])
            finally:
                await engine.shutdown()
        with self.assertRaisesRegex(RuntimeError, "message_payload_field_mismatch"):
            asyncio.run(check())

    def test_publisher_rederives_common_admission_before_acceptance(self):
        event = self._build()
        root = self.root / "positive"
        materialize_run(package_root=event.package_root, data_root=event.data_root, output_root=root)
        package = load_event_package(event.package_root, event.data_root, "rule")
        trace = [json.loads(line) for line in (root / "simulation_trace.jsonl").read_text().splitlines()]
        manifest = json.loads((root / "run_manifest.json").read_text())
        _verify_trace_semantics(trace, package, manifest)
        row = next(row for row in trace if row["record_type"] == "action_disposition")
        row["payload"]["reason_code"] = "producer_claim"
        with self.assertRaisesRegex(ValueError, "run_shared_admission_not_reproduced"):
            _verify_trace_semantics(trace, package, manifest)
