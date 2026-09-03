from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.experiment import ExperimentAdmissionError, admit_experiment_plan

from synthetic import DISPATCH_CASE, SIGNAL_CASE, SyntheticEvent, build_synthetic_event


def _file_ref(project_root: Path, relative_path: str) -> dict[str, str]:
    return {
        "relative_path": relative_path,
        "sha256": file_sha256(project_root / relative_path),
    }


def _seal(plan: dict) -> dict:
    plan["plan_sha256"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "plan_sha256"}
    )
    return plan


def _rule_plan(cases: list[SyntheticEvent]) -> dict:
    project_root = cases[0].project_root
    rows = []
    for case in cases:
        package = load_event_package(case.package_root, case.data_root, "rule")
        rows.append(
            {
                "row_id": f"{case.slug}.rule",
                "event_id": case.event_id,
                "package_relative_path": case.package_root.relative_to(
                    project_root
                ).as_posix(),
                "package_sha256": package.package_sha256,
                "backend": "rule",
                "binding_sha256": package.binding_sha256,
                "seeds": [0],
                "identity_variant": "canonical",
                "custody_root": (
                    ".local-runtime/h2epr-simulation/experiments/"
                    f"synthetic-contract/{case.slug}"
                ),
            }
        )
    return _seal(
        {
            "schema_version": "h2epr.experiment-plan.v3",
            "plan_id": "h2epr.experiment.synthetic-rule.test",
            "plan_version": "1.0.0",
            "purpose": "Exercise admission across two unrelated Rule packages.",
            "rows": rows,
            "comparison_groups": [
                {
                    "group_id": "synthetic-rule-contract",
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
                    "definition": _file_ref(
                        project_root,
                        "templates/simulation-reading.md",
                    ),
                },
                {
                    "analysis_id": "cross-event-analysis",
                    "scope": "cross_event_contract",
                    "definition": _file_ref(
                        project_root,
                        "templates/cross-event-analysis.md",
                    ),
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
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.cases = [
            build_synthetic_event(root, vocabulary)
            for vocabulary in (SIGNAL_CASE, DISPATCH_CASE)
        ]
        self.project_root = self.cases[0].project_root
        self.data_root = self.cases[0].data_root

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_two_event_rule_matrix_is_admitted_without_execution(self) -> None:
        receipt = admit_experiment_plan(
            project_root=self.project_root,
            data_root=self.data_root,
            plan=_rule_plan(self.cases),
        )
        self.assertTrue(receipt["admitted"])
        self.assertEqual(2, receipt["row_count"])
        self.assertEqual(2, receipt["run_count"])
        self.assertEqual(
            {"rule": 2, "llm": 0, "rulellm": 0},
            receipt["backend_counts"],
        )
        self.assertEqual(8, len(receipt["checks"]))
        for case in self.cases:
            self.assertFalse(
                (
                    self.project_root.parent
                    / ".local-runtime"
                    / "h2epr-simulation"
                    / "experiments"
                    / "synthetic-contract"
                    / case.slug
                ).exists()
            )

    def test_duplicate_or_escaping_custody_is_rejected(self) -> None:
        duplicate = _rule_plan(self.cases)
        duplicate["rows"][1]["custody_root"] = duplicate["rows"][0][
            "custody_root"
        ]
        _seal(duplicate)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_custody_duplicate",
        ):
            admit_experiment_plan(
                project_root=self.project_root,
                data_root=self.data_root,
                plan=duplicate,
            )

        alias = _rule_plan(self.cases)
        alias["rows"][1]["custody_root"] = (
            alias["rows"][0]["custody_root"] + "/"
        )
        _seal(alias)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_custody_duplicate",
        ):
            admit_experiment_plan(
                project_root=self.project_root,
                data_root=self.data_root,
                plan=alias,
            )

        escaping = _rule_plan(self.cases)
        escaping["rows"][0]["custody_root"] = (
            ".local-runtime/h2epr-simulation/experiments/../escape"
        )
        _seal(escaping)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_custody_path_unsafe",
        ):
            admit_experiment_plan(
                project_root=self.project_root,
                data_root=self.data_root,
                plan=escaping,
            )

    def test_planned_backend_cannot_enter_an_experiment_matrix(self) -> None:
        plan = _rule_plan(self.cases)
        row = plan["rows"][0]
        row["backend"] = "llm"
        row["binding_sha256"] = "0" * 64
        row["model_provenance"] = {
            "provider": "test-provider",
            "model_id": "test-model",
            "model_version": "test-version",
            "service_mode": "local",
            "prompt_contract": _file_ref(
                self.project_root,
                "backends/llm-prompt-contract-template.md",
            ),
            "response_contract": _file_ref(
                self.project_root,
                "schemas/participant-decision.schema.json",
            ),
            "decoding_parameters": [
                {"name": "temperature", "value": 0, "basis": "test"}
            ],
            "max_attempts": 1,
        }
        _seal(plan)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_backend_unavailable:synthetic_signal.rule:"
            "backend_not_implemented:llm",
        ):
            admit_experiment_plan(
                project_root=self.project_root,
                data_root=self.data_root,
                plan=plan,
            )

    def test_timeout_and_retry_semantics_fail_closed(self) -> None:
        plan = _rule_plan(self.cases)
        plan["scheduling"]["stall_timeout_seconds"] = 4000
        _seal(plan)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_timeout_order_invalid",
        ):
            admit_experiment_plan(
                project_root=self.project_root,
                data_root=self.data_root,
                plan=plan,
            )

        plan = _rule_plan(self.cases)
        plan["failure_policy"]["retryable_classes"] = ["stall"]
        _seal(plan)
        with self.assertRaisesRegex(
            ExperimentAdmissionError,
            "experiment_retry_policy_incoherent",
        ):
            admit_experiment_plan(
                project_root=self.project_root,
                data_root=self.data_root,
                plan=plan,
            )

    def test_cross_event_model_comparison_requires_full_control_parity(self) -> None:
        plan = _rule_plan(self.cases)
        for index, row in enumerate(plan["rows"]):
            row["backend"] = "llm"
            row["binding_sha256"] = str(index + 1) * 64
            row["model_provenance"] = {
                "provider": "test-provider",
                "model_id": "test-model",
                "model_version": "test-version",
                "service_mode": "local",
                "prompt_contract": _file_ref(
                    self.project_root,
                    "backends/llm-prompt-contract-template.md",
                ),
                "response_contract": _file_ref(
                    self.project_root,
                    "schemas/participant-decision.schema.json",
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
        _seal(plan)

        def _package(root: Path, _data: Path, _backend: str):
            row = next(
                row
                for row in plan["rows"]
                if row["package_relative_path"] in root.as_posix()
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
                project_root=self.project_root,
                data_root=self.data_root,
                plan=plan,
            )


if __name__ == "__main__":
    unittest.main()
