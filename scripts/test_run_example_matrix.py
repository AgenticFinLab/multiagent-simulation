#!/usr/bin/env python
"""Local tests for run_example_matrix.py."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).with_name("run_example_matrix.py")


def load_runner_module():
    spec = importlib.util.spec_from_file_location("run_example_matrix", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RunExampleMatrixTest(unittest.TestCase):
    def test_discovers_all_configured_experiments(self):
        module = load_runner_module()
        root = Path(__file__).resolve().parents[1]

        experiments = module.discover_experiments(root)
        expected_ids = set()
        for config in (root / "configs").glob("*/*/simulation.yml"):
            scenario, mechanism = config.relative_to(root / "configs").parts[:2]
            if scenario == "TEMPLATES":
                continue
            if sorted((root / "examples" / scenario / mechanism).glob("run_*.py")):
                expected_ids.add(f"{scenario}__{mechanism}")

        self.assertEqual(len(experiments), len(expected_ids))
        self.assertEqual(len({exp.experiment_id for exp in experiments}), len(expected_ids))
        self.assertIn("AssetBubble__Rule", {exp.experiment_id for exp in experiments})
        self.assertEqual(
            (experiments[0].scenario, experiments[0].mechanism),
            sorted(
                ((exp.scenario, exp.mechanism) for exp in experiments),
                key=lambda item: (
                    item[0],
                    module.MECHANISM_ORDER.get(item[1], 99),
                    item[1],
                ),
            )[0],
        )
        self.assertTrue(experiments[0].runner.exists())
        self.assertTrue(experiments[0].config.exists())

    def test_builds_conda_command_without_shell_string_interpolation(self):
        module = load_runner_module()
        root = Path(__file__).resolve().parents[1]
        experiment = module.discover_experiments(root)[0]

        command = module.build_command(
            experiment=experiment,
            conda_bin=Path("/opt/conda/bin/conda"),
            conda_env="LMSim",
        )

        self.assertEqual(
            command[0:6],
            [
                "/opt/conda/bin/conda",
                "run",
                "--no-capture-output",
                "-n",
                "LMSim",
                "python",
            ],
        )
        self.assertEqual(command[-2], "-c")
        self.assertEqual(Path(command[-1]).name, "simulation.yml")

    def test_builds_child_environment_with_runtime_safety_defaults(self):
        module = load_runner_module()

        with patch.dict(os.environ, {}, clear=True):
            env = module.build_child_env()

        self.assertEqual(env["MPLCONFIGDIR"], "/tmp/masim-matplotlib")
        self.assertEqual(env["TOKENIZERS_PARALLELISM"], "false")
        self.assertEqual(env["WANDB_MODE"], "disabled")
        self.assertEqual(env["PYTHONUNBUFFERED"], "1")
        self.assertEqual(env["MASIM_RAY_NUM_CPUS"], "16")
        self.assertEqual(env["OMP_NUM_THREADS"], "1")
        self.assertEqual(env["MKL_NUM_THREADS"], "1")
        self.assertEqual(env["OPENBLAS_NUM_THREADS"], "1")
        self.assertEqual(env["NUMEXPR_NUM_THREADS"], "1")

    def test_extracts_round_progress_from_simulator_and_launcher_logs(self):
        module = load_runner_module()

        progress = module.extract_round_progress(
            "\n".join(
                [
                    "13:50:32 [INFO]     Round 172/200",
                    "13:51:14 [INFO]     Round 173/200",
                    "  progress round=180/200",
                    "14:01:39 [INFO]     Round 174/200",
                ]
            )
        )

        self.assertEqual(progress.max_round, 180)
        self.assertEqual(progress.total_rounds, 200)

    def test_stall_watchdog_keeps_recent_progress_and_flags_stale_progress(self):
        module = load_runner_module()
        progress = module.RoundProgress(max_round=179, total_rounds=200)

        self.assertIsNone(
            module.stall_timeout_reason(
                now_perf=1000.0,
                last_progress_perf=950.0,
                stall_timeout_seconds=60,
                progress=progress,
            )
        )

        reason = module.stall_timeout_reason(
            now_perf=1011.0,
            last_progress_perf=950.0,
            stall_timeout_seconds=60,
            progress=progress,
        )
        self.assertIn("stall_timeout", reason)
        self.assertIn("179/200", reason)

    def test_writes_manifest_and_report_for_dry_run(self):
        module = load_runner_module()
        root = Path(__file__).resolve().parents[1]
        experiments = module.discover_experiments(root)[:2]

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            module.write_manifest(output_dir, experiments)
            results = [
                module.RunResult.from_dry_run(exp, index=i + 1, total=len(experiments))
                for i, exp in enumerate(experiments)
            ]
            module.write_results(output_dir, results)
            module.write_report(output_dir, results)

            self.assertTrue((output_dir / "manifest.json").exists())
            self.assertTrue((output_dir / "results.json").exists())
            self.assertTrue((output_dir / "results.csv").exists())
            report = (output_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("Example Run Matrix Report", report)
            self.assertIn("DRY_RUN", report)

    def test_default_output_dir_uses_runs_layout(self):
        module = load_runner_module()
        root = Path("/workspace/multiagent-simulation")

        output_dir = module.default_output_dir(root)

        self.assertEqual(output_dir.parent, root / "EXPERIMENT" / "runs")
        self.assertIn("matrix", output_dir.name)

    def test_prepares_isolated_config_snapshot_with_artifact_paths(self):
        module = load_runner_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "multiagent-simulation"
            config_dir = root / "configs" / "DispositionEffect" / "Rule"
            runner_dir = root / "examples" / "DispositionEffect" / "Rule"
            config_dir.mkdir(parents=True)
            runner_dir.mkdir(parents=True)
            (runner_dir / "run_disposition.py").write_text("print('ok')\n", encoding="utf-8")
            (config_dir / "simulation.yml").write_text(
                '\n'.join(
                    [
                        "setting:",
                        '  record_path: "EXPERIMENT/DispositionEffect/Rule/records"',
                        "players: !include players.yml",
                        "topology: !include topology.yml",
                        "communication:",
                        '  storage_path: "EXPERIMENT/DispositionEffect/Rule/communication"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (config_dir / "players.yml").write_text(
                '\n'.join(
                    [
                        "market:",
                        "  config:",
                        "    extras:",
                        '      record_path: "EXPERIMENT/DispositionEffect/Rule/records"',
                        "  persona: !include persona.yml",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (config_dir / "persona.yml").write_text(
                '\n'.join(
                    [
                        "proxy:",
                        "  storage:",
                        '    checkpoint_dir: "EXPERIMENT/DispositionEffect/Rule/checkpoints"',
                        '    record_path: "EXPERIMENT/DispositionEffect/Rule/records"',
                        "  monitoring:",
                        '    record_path: "EXPERIMENT/DispositionEffect/Rule/monitoring"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (config_dir / "topology.yml").write_text("edges: []\n", encoding="utf-8")
            experiment = module.discover_experiments(root)[0]
            output_dir = root / "EXPERIMENT" / "runs" / "remote-rule-baseline"
            prepared = module.prepare_isolated_experiments(
                root=root,
                output_dir=output_dir,
                experiments=[experiment],
            )

            self.assertEqual(len(prepared), 1)
            isolated = prepared[0]
            self.assertEqual(
                isolated.config,
                output_dir / "configs" / "DispositionEffect" / "Rule" / "simulation.yml",
            )
            self.assertTrue(isolated.config.exists())
            self.assertTrue(
                (output_dir / "configs" / "DispositionEffect" / "Rule" / "players.yml").exists()
            )
            self.assertTrue(
                (output_dir / "configs" / "DispositionEffect" / "Rule" / "persona.yml").exists()
            )
            self.assertTrue(
                (output_dir / "artifacts" / "DispositionEffect" / "Rule" / "records").is_dir()
            )
            self.assertTrue(
                (output_dir / "artifacts" / "DispositionEffect" / "Rule" / "communication").is_dir()
            )
            self.assertTrue(
                (output_dir / "artifacts" / "DispositionEffect" / "Rule" / "monitoring").is_dir()
            )
            self.assertTrue(
                (output_dir / "artifacts" / "DispositionEffect" / "Rule" / "checkpoints").is_dir()
            )

            simulation_text = isolated.config.read_text(encoding="utf-8")
            players_text = (
                output_dir / "configs" / "DispositionEffect" / "Rule" / "players.yml"
            ).read_text(encoding="utf-8")
            persona_text = (
                output_dir / "configs" / "DispositionEffect" / "Rule" / "persona.yml"
            ).read_text(encoding="utf-8")

            self.assertIn(
                "EXPERIMENT/runs/remote-rule-baseline/artifacts/DispositionEffect/Rule/records",
                simulation_text,
            )
            self.assertIn(
                "EXPERIMENT/runs/remote-rule-baseline/artifacts/DispositionEffect/Rule/communication",
                simulation_text,
            )
            self.assertIn(
                "EXPERIMENT/runs/remote-rule-baseline/artifacts/DispositionEffect/Rule/records",
                players_text,
            )
            self.assertIn(
                "EXPERIMENT/runs/remote-rule-baseline/artifacts/DispositionEffect/Rule/checkpoints",
                persona_text,
            )
            self.assertIn("persona: !include persona.yml", players_text)
            self.assertIn("players: !include players.yml", simulation_text)


if __name__ == "__main__":
    unittest.main()
