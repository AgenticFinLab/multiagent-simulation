from __future__ import annotations

import unittest

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.experiment import ExperimentAdmissionError
from h2epr.experiment import admit_experiment_plan

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


def _current_rule_plan() -> dict:
    rows = []
    for event in CURRENT_EVENTS:
        package = load_event_package(package_root(event), DATA_ROOT, "rule")
        slug = event["event_slug"]
        rows.append(
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
        )
    return _seal(
        {
            "schema_version": "h2epr.experiment-plan.v3",
            "plan_id": "h2epr.experiment.current-rule.v4.test",
            "plan_version": "0.4.0",
            "purpose": "Verify current v4 package admission without execution.",
            "rows": rows,
            "comparison_groups": [
                {
                    "group_id": "current-rule-contract",
                    "comparison_kind": "cross_event_contract",
                    "row_ids": [row["row_id"] for row in rows],
                }
            ],
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
                },
                {
                    "analysis_id": "cross-event-analysis",
                    "scope": "cross_event_contract",
                    "definition": _file_ref("templates/cross-event-analysis.md"),
                },
            ],
            "claim_boundary": {
                "supports": ["v4 experiment-plan admission"],
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
    def test_current_rule_matrix_is_admitted(self) -> None:
        receipt = admit_experiment_plan(
            project_root=PROJECT_ROOT,
            data_root=DATA_ROOT,
            plan=_current_rule_plan(),
        )
        self.assertTrue(receipt["admitted"])
        self.assertEqual(len(CURRENT_EVENTS), receipt["row_count"])
        self.assertEqual(len(CURRENT_EVENTS), receipt["backend_counts"]["rule"])

    def test_planned_backend_fails_closed(self) -> None:
        plan = _current_rule_plan()
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
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_backend_unavailable:.*backend_not_implemented:llm",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=plan,
            )


if __name__ == "__main__":
    unittest.main()
