from __future__ import annotations

import unittest

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.experiment import ExperimentAdmissionError, admit_experiment_plan

from support import CURRENT_EVENTS, DATA_ROOT, PROJECT_ROOT, package_root


def _file_ref(relative_path: str) -> dict[str, str]:
    return {
        "relative_path": relative_path,
        "sha256": file_sha256(PROJECT_ROOT / relative_path),
    }


def _seal(plan: dict) -> dict:
    plan["plan_sha256"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "plan_sha256"}
    )
    return plan


def _individual_rule_plan(event: dict[str, str]) -> dict:
    package = load_event_package(package_root(event), DATA_ROOT, "rule")
    slug = event["event_slug"]
    return _seal(
        {
            "schema_version": "h2epr.experiment-plan.v3",
            "plan_id": f"h2epr.experiment.current.{slug}.rule.test",
            "plan_version": "1.0.0",
            "purpose": "Verify one current Rule package without execution.",
            "rows": [
                {
                    "row_id": f"{slug}.rule",
                    "event_id": event["event_id"],
                    "package_relative_path": event["package_relative_path"],
                    "package_sha256": package.package_sha256,
                    "backend": "rule",
                    "binding_sha256": package.binding_sha256,
                    "seeds": [0],
                    "identity_variant": "canonical",
                    "custody_root": (
                        ".local-runtime/h2epr-simulation/experiments/"
                        f"current-rule/{slug}"
                    ),
                }
            ],
            "comparison_groups": [],
            "scheduling": {
                "max_parallel_runs": 1,
                "wall_timeout_seconds": 3600,
                "stall_timeout_seconds": 600,
                "progress_poll_seconds": 10,
            },
            "failure_policy": {
                "retry_limit": 0,
                "retryable_classes": [],
                "preserve_failed_custody": True,
            },
            "analysis_contracts": [
                {
                    "analysis_id": "simulation-reading",
                    "scope": "simulation_only",
                    "definition": _file_ref("templates/simulation-reading.md"),
                }
            ],
            "claim_boundary": {
                "supports": ["individual executable-row admission"],
                "does_not_support": [
                    "held-out evaluation",
                    "historical fit",
                    "parameter calibration",
                    "causal validity",
                    "scientific validity",
                    "universal generality",
                ],
            },
            "plan_sha256": "0" * 64,
        }
    )


class CurrentExperimentAdmissionTests(unittest.TestCase):
    def test_each_current_rule_package_is_individually_admittable(self) -> None:
        admitted = []
        for event in CURRENT_EVENTS:
            with self.subTest(event_id=event["event_id"]):
                receipt = admit_experiment_plan(
                    project_root=PROJECT_ROOT,
                    data_root=DATA_ROOT,
                    plan=_individual_rule_plan(event),
                )
                self.assertTrue(receipt["admitted"])
                self.assertEqual(1, receipt["row_count"])
                self.assertEqual(1, receipt["backend_counts"]["rule"])
                admitted.append(event["event_id"])
        self.assertEqual(
            [event["event_id"] for event in CURRENT_EVENTS],
            admitted,
        )

    def test_planned_backend_fails_closed_for_every_current_event(self) -> None:
        checked = []
        for event in CURRENT_EVENTS:
            plan = _individual_rule_plan(event)
            row = plan["rows"][0]
            row["backend"] = "llm"
            row["binding_sha256"] = "0" * 64
            row["model_provenance"] = {
                "provider": "unavailable-provider",
                "model_id": "unavailable-model",
                "model_version": "unavailable-version",
                "service_mode": "local",
                "prompt_contract": _file_ref(
                    "backends/llm-prompt-contract-template.md"
                ),
                "response_contract": _file_ref(
                    "schemas/participant-decision.schema.json"
                ),
                "decoding_parameters": [
                    {"name": "temperature", "value": 0, "basis": "test control"}
                ],
                "max_attempts": 1,
            }
            _seal(plan)
            with self.subTest(event_id=event["event_id"]), self.assertRaisesRegex(
                ExperimentAdmissionError,
                "experiment_backend_unavailable:.*backend_not_implemented:llm",
            ):
                admit_experiment_plan(
                    project_root=PROJECT_ROOT,
                    data_root=DATA_ROOT,
                    plan=plan,
                )
            checked.append(event["event_id"])
        self.assertEqual(
            [event["event_id"] for event in CURRENT_EVENTS],
            checked,
        )


if __name__ == "__main__":
    unittest.main()
