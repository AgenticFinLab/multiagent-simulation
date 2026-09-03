from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.experiment import (
    ExperimentAdmissionError,
    admit_experiment_plan,
)

from support import (
    DATA_ROOT,
    PROJECT_ROOT,
    CURRENT_CASES,
    package_root,
)


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


def _three_event_rule_plan() -> dict:
    rows = []
    for event_id, slug, *_ in CURRENT_CASES:
        package = load_event_package(package_root(slug), DATA_ROOT, "rule")
        rows.append(
            {
                "row_id": f"{slug}.rule",
                "event_id": event_id,
                "package_relative_path": (
                    f"events/{slug}/package"
                ),
                "package_sha256": package.package_sha256,
                "backend": "rule",
                "binding_sha256": package.binding_sha256,
                "seeds": [0],
                "identity_variant": "canonical",
                "custody_root": (
                    ".local-runtime/h2epr-simulation/experiments/"
                    f"three-event-rule/{slug}"
                ),
            }
        )
    return _seal(
        {
            "schema_version": "h2epr.experiment-plan.v3",
            "plan_id": "h2epr.experiment.three-event-rule.test",
            "plan_version": "0.1.0",
            "purpose": "Exercise experiment admission across three Rule packages.",
            "rows": rows,
            "comparison_groups": [
                {
                    "group_id": "three-event-rule-contract",
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
                "supports": [
                    "experiment-plan integrity and executable-row admission"
                ],
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


class ExperimentAdmissionControlTests(unittest.TestCase):
    def test_three_event_rule_matrix_is_admitted_without_execution(self) -> None:
        receipt = admit_experiment_plan(
            project_root=PROJECT_ROOT,
            data_root=DATA_ROOT,
            plan=_three_event_rule_plan(),
        )
        self.assertTrue(receipt["admitted"])
        self.assertEqual(3, receipt["row_count"])
        self.assertEqual(3, receipt["run_count"])
        self.assertEqual(
            {"rule": 3, "llm": 0, "rulellm": 0},
            receipt["backend_counts"],
        )
        self.assertEqual(8, len(receipt["checks"]))

    def test_duplicate_or_escaping_custody_is_rejected(self) -> None:
        duplicate = _three_event_rule_plan()
        duplicate["rows"][1]["custody_root"] = duplicate["rows"][0][
            "custody_root"
        ]
        _seal(duplicate)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_custody_duplicate",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=duplicate,
            )

        alias = _three_event_rule_plan()
        alias["rows"][1]["custody_root"] = (
            alias["rows"][0]["custody_root"] + "/"
        )
        _seal(alias)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_custody_duplicate",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=alias,
            )

        escaping = _three_event_rule_plan()
        escaping["rows"][0]["custody_root"] = (
            ".local-runtime/h2epr-simulation/experiments/../escape"
        )
        _seal(escaping)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_custody_path_unsafe",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=escaping,
            )

    def test_planned_backend_cannot_enter_an_experiment_matrix(self) -> None:
        plan = _three_event_rule_plan()
        row = plan["rows"][0]
        row["backend"] = "llm"
        row["binding_sha256"] = "0" * 64
        row["model_provenance"] = {
            "provider": "test-provider",
            "model_id": "test-model",
            "model_version": "test-version",
            "service_mode": "local",
            "prompt_contract": _file_ref(
                "backends/llm-prompt-contract-template.md"
            ),
            "response_contract": _file_ref(
                "schemas/participant-decision.schema.json"
            ),
            "decoding_parameters": [
                {"name": "temperature", "value": 0, "basis": "test"}
            ],
            "max_attempts": 1,
        }
        _seal(plan)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_backend_unavailable:panic_1907.rule:backend_not_implemented:llm",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=plan,
            )

    def test_timeout_and_retry_semantics_fail_closed(self) -> None:
        plan = _three_event_rule_plan()
        plan["scheduling"]["stall_timeout_seconds"] = 4000
        _seal(plan)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_timeout_order_invalid",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=plan,
            )

        plan = _three_event_rule_plan()
        plan["failure_policy"]["retryable_classes"] = ["stall"]
        _seal(plan)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_retry_policy_incoherent",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=plan,
            )

    def test_cross_event_model_comparison_requires_full_control_parity(self) -> None:
        plan = _three_event_rule_plan()
        plan["rows"] = plan["rows"][:2]
        for index, row in enumerate(plan["rows"]):
            row["backend"] = "llm"
            row["binding_sha256"] = str(index + 1) * 64
            row["model_provenance"] = {
                "provider": "test-provider",
                "model_id": "test-model",
                "model_version": "test-version",
                "service_mode": "local",
                "prompt_contract": _file_ref(
                    "backends/llm-prompt-contract-template.md"
                ),
                "response_contract": _file_ref(
                    "schemas/participant-decision.schema.json"
                ),
                "decoding_parameters": [
                    {
                        "name": "temperature",
                        "value": index,
                        "basis": "fixed comparison control",
                    }
                ],
                "max_attempts": 1,
            }
        plan["comparison_groups"][0]["row_ids"] = [
            row["row_id"] for row in plan["rows"]
        ]
        _seal(plan)

        def _package(_root, _data, _backend):
            row = next(
                row
                for row in plan["rows"]
                if row["package_relative_path"] in _root.as_posix()
            )
            return SimpleNamespace(
                manifest={"event_id": row["event_id"]},
                package_sha256=row["package_sha256"],
                binding_sha256=row["binding_sha256"],
            )

        with patch(
            "h2epr.experiment.load_event_package",
            side_effect=_package,
        ), self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_model_control_mismatch",
        ):
            admit_experiment_plan(
                project_root=PROJECT_ROOT,
                data_root=DATA_ROOT,
                plan=plan,
            )

if __name__ == "__main__":
    unittest.main()
