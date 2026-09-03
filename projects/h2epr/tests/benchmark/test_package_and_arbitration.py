from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from h2epr.backends.registry import BackendRegistryError, build_backend
from h2epr.benchmark.compiler import (
    BACKEND_ATTACHMENT_BUILDERS,
    package_core_sha256,
)
from h2epr.canonical import canonical_sha256
from h2epr.masim_kernel import ActionIntent, AuthoritativeReducer
from h2epr.runtime.environment import DeclarativeEnvironment
from h2epr.runtime.benchmark_runner import _decision_message_projection
from synthetic import SIGNAL_CASE, build_synthetic_event


def _scenario() -> dict:
    return {
        "mechanism": {
            "conflict_policy": (
                "reject_distinct_concurrent_writes_allow_idempotent_same_value"
            ),
            "state_fields": [
                {
                    "entity_id": "world",
                    "field_name": "status",
                    "value_type": "string",
                    "allowed_values": ["open", "left", "right", "closed"],
                }
            ],
            "intent_handlers": [
                {
                    "intent_id": "choose_left",
                    "eligible_actors": ["actor_a"],
                    "eligible_targets": ["world"],
                    "target_parameter": "target_id",
                    "parameter_domains": [
                        {
                            "parameter": "target_id",
                            "value_type": "string",
                            "allowed_values": ["world"],
                        }
                    ],
                    "preconditions": [],
                    "effects": [
                        {
                            "entity_id": "world",
                            "field_name": "status",
                            "operation": "set",
                            "value": "left",
                        }
                    ],
                },
                {
                    "intent_id": "choose_right",
                    "eligible_actors": ["actor_b"],
                    "eligible_targets": ["world"],
                    "target_parameter": "target_id",
                    "parameter_domains": [
                        {
                            "parameter": "target_id",
                            "value_type": "string",
                            "allowed_values": ["world"],
                        }
                    ],
                    "preconditions": [],
                    "effects": [
                        {
                            "entity_id": "world",
                            "field_name": "status",
                            "operation": "set",
                            "value": "right",
                        }
                    ],
                },
                {
                    "intent_id": "close",
                    "eligible_actors": ["actor_a", "actor_b"],
                    "eligible_targets": ["world"],
                    "target_parameter": "target_id",
                    "parameter_domains": [
                        {
                            "parameter": "target_id",
                            "value_type": "string",
                            "allowed_values": ["world"],
                        }
                    ],
                    "preconditions": [],
                    "effects": [
                        {
                            "entity_id": "world",
                            "field_name": "status",
                            "operation": "set",
                            "value": "closed",
                        }
                    ],
                },
            ],
        }
    }


def _intent(actor: str, action: str, opaque: str) -> ActionIntent:
    opening = {"state_version": 0, "entities": {"world": {"status": "open"}}}
    return ActionIntent(
        intent_id=f"intent.{opaque}",
        run_id="run.test",
        actor_id=actor,
        logical_tick=1,
        prestate_version=0,
        prestate_sha256=canonical_sha256(opening),
        action_type=action,
        parameters={"target_id": "world"},
        policy_id="policy.test",
    )


def _normalized(result) -> dict:
    actor_by_intent = {
        row.intent_id: actor
        for actor, row in result["intents"].items()
    }
    return {
        "state": result["state"],
        "dispositions": sorted(
            (
                actor_by_intent[row.intent_id],
                row.status,
                row.reason_code,
                len(row.state_delta_ids),
            )
            for row in result["dispositions"]
        ),
        "deltas": sorted(
            (
                actor_by_intent[row.source_intent_id],
                row.entity_id,
                row.field_name,
                row.before,
                row.after,
            )
            for row in result["deltas"]
        ),
    }


class PackageAndArbitrationTests(unittest.TestCase):
    def _reduce(self, rows: list[ActionIntent]) -> dict:
        opening = {
            "state_version": 0,
            "entities": {"world": {"status": "open"}},
        }
        environment = DeclarativeEnvironment(_scenario())
        reducer = AuthoritativeReducer(opening, environment.apply_batch)
        reduced = reducer.reduce(rows, logical_tick=1, run_seed=0)
        return {
            "state": reduced.state,
            "dispositions": reduced.dispositions,
            "deltas": reduced.deltas,
            "intents": {row.actor_id: row for row in rows},
        }

    def test_distinct_concurrent_writers_are_all_rejected(self) -> None:
        left = [
            _intent("actor_a", "choose_left", "z-last"),
            _intent("actor_b", "choose_right", "a-first"),
        ]
        right = [
            _intent("actor_b", "choose_right", "z-last"),
            _intent("actor_a", "choose_left", "a-first"),
        ]
        first = _normalized(self._reduce(left))
        second = _normalized(self._reduce(right))
        self.assertEqual(first, second)
        self.assertEqual("open", first["state"]["entities"]["world"]["status"])
        self.assertEqual(
            [
                ("actor_a", "rejected", "concurrent_field_conflict", 0),
                ("actor_b", "rejected", "concurrent_field_conflict", 0),
            ],
            first["dispositions"],
        )

    def test_idempotent_writers_use_semantic_serialization_only(self) -> None:
        left = [
            _intent("actor_a", "close", "z-last"),
            _intent("actor_b", "close", "a-first"),
        ]
        right = [
            _intent("actor_b", "close", "z-last"),
            _intent("actor_a", "close", "a-first"),
        ]
        first = _normalized(self._reduce(left))
        second = _normalized(self._reduce(right))
        self.assertEqual(first, second)
        self.assertEqual("closed", first["state"]["entities"]["world"]["status"])
        self.assertEqual(
            [
                ("actor_a", "accepted", "admitted_applied", 1),
                ("actor_b", "accepted", "admitted_no_effect", 0),
            ],
            first["dispositions"],
        )

    def test_decision_message_projection_excludes_opaque_identity(self) -> None:
        base = {
            "message_id": "msg.first",
            "message_intent_id": "intent.first",
            "intent_content_sha256": "1" * 64,
            "sender_id": "actor_a",
            "recipient_id": "actor_b",
            "send_tick": 1,
            "due_tick": 2,
            "message_kind": "notice",
            "payload": {"status": "ready"},
        }
        successor = copy.deepcopy(base)
        successor.update(
            {
                "message_id": "msg.second",
                "message_intent_id": "intent.second",
                "intent_content_sha256": "2" * 64,
            }
        )
        self.assertEqual(
            _decision_message_projection(base),
            _decision_message_projection(successor),
        )

    def test_unregistered_implemented_backend_fails_before_setup(self) -> None:
        package = SimpleNamespace(
            binding={
                "backend": "llm",
                "implementation_id": "h2epr.backend.llm.unregistered.test",
            }
        )
        with self.assertRaisesRegex(
            BackendRegistryError,
            "backend_factory_unavailable:llm",
        ):
            build_backend(
                package,  # type: ignore[arg-type]
                backend_name="llm",
                run_id="run.test",
                run_seed=0,
            )

    def test_current_implemented_attachments_have_registered_builders(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            assembly = json.loads(case.assembly_path.read_text(encoding="utf-8"))
            implemented = {
                backend
                for backend, declaration in assembly["backend_releases"].items()
                if declaration["status"] == "implemented"
            }
            self.assertEqual({"rule"}, implemented)
            self.assertLessEqual(implemented, set(BACKEND_ATTACHMENT_BUILDERS))

    def test_backend_catalog_successor_keeps_package_core_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            source = json.loads(
                (case.package_root / "manifest.json").read_text(encoding="utf-8")
            )
            base = copy.deepcopy(source)
            successor = copy.deepcopy(base)
            successor["backend_catalog_sha256"] = "3" * 64
            successor["backend_bindings"][0] = {
                **successor["backend_bindings"][0],
                "binding_sha256": "4" * 64,
            }
            self.assertEqual(
                package_core_sha256(base),
                package_core_sha256(successor),
            )


if __name__ == "__main__":
    unittest.main()
