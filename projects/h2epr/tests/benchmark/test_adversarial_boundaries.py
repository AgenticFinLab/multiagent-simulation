from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from h2epr.benchmark.compiler import (
    derive_configuration_admission_receipt,
    validate_configuration_value_provenance,
)
from h2epr.benchmark.package import EventPackageError, load_event_package
from h2epr.masim_kernel import ActionIntent
from h2epr.runtime.benchmark_runner import materialize_run
from h2epr.runtime.environment import build_environment
from h2epr.runtime.generated_epg import GeneratedEPGError, validate_generated_epg
from h2epr.semantic.assets import AssetAdmissionError, _release_artifact_path

from synthetic import SIGNAL_CASE, build_synthetic_event


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class AdversarialBoundaryTests(unittest.TestCase):
    def test_release_artifact_cannot_escape_its_declared_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary) / "project"
            release_root = project_root / "release"
            release_root.mkdir(parents=True)
            (project_root / "outside.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(AssetAdmissionError, "artifact_path_unsafe"):
                _release_artifact_path(
                    release_root,
                    project_root,
                    "../outside.json",
                    "artifact",
                )
            with self.assertRaisesRegex(
                AssetAdmissionError,
                "artifact_escapes_config_release",
            ):
                _release_artifact_path(
                    release_root,
                    project_root,
                    "../outside.json",
                    "artifact",
                    cross_release_role="backend_configuration",
                )

    def test_configuration_provenance_pointers_resolve_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            package = load_event_package(case.package_root, case.data_root, "rule")
            validate_configuration_value_provenance(
                package.shared_configuration,
                "shared_configuration",
            )

            missing = copy.deepcopy(package.shared_configuration)
            missing["value_provenance"][0]["json_pointer"] = (
                "/settings/nonexistent"
            )
            with self.assertRaisesRegex(
                ValueError,
                "value_provenance:0:/settings/nonexistent_target_missing",
            ):
                validate_configuration_value_provenance(
                    missing,
                    "shared_configuration",
                )

            duplicate = copy.deepcopy(package.shared_configuration)
            duplicate["value_provenance"].append(
                copy.deepcopy(duplicate["value_provenance"][0])
            )
            with self.assertRaisesRegex(ValueError, "_duplicate"):
                validate_configuration_value_provenance(
                    duplicate,
                    "shared_configuration",
                )

    def test_shared_configuration_receipt_is_independently_rederived(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            slug = case.slug
            project = case.project_root
            roster = _read(project / "agents" / "rosters" / slug / "roster.json")
            actor_map = _read(
                project / "agents" / "rosters" / slug / "actor-map.json"
            )
            interface = _read(
                project
                / "agents"
                / "interfaces"
                / slug
                / "participant-interface.json"
            )
            scenario_interface = _read(
                project / "scenarios" / slug / "scenario-interface.json"
            )
            mechanism = _read(
                project / "scenarios" / slug / "scenario-mechanism.json"
            )
            configuration_root = project / "configs" / slug / "shared"
            configuration = _read(
                configuration_root / "scenario-configuration.json"
            )
            tracked = _read(configuration_root / "admission-receipt.json")
            draft = _read(
                case.data_root
                / "development_samples_v1"
                / "events"
                / case.event_id
                / "draft_epg.json"
            )
            derived = derive_configuration_admission_receipt(
                configuration=configuration,
                roster=roster,
                actor_map=actor_map,
                participant_interface=interface,
                scenario_interface=scenario_interface,
                mechanism=mechanism,
                draft=draft,
            )
            self.assertEqual(tracked, derived)
            forged = copy.deepcopy(tracked)
            forged["checks"][0]["evidence_sha256"] = "0" * 64
            self.assertNotEqual(forged, derived)

    def test_invalid_parameter_fails_without_partial_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            package = load_event_package(case.package_root, case.data_root, "rule")
            environment = build_environment(package.scenario)
            state = copy.deepcopy(package.scenario["initial_state"])
            invalid = ActionIntent(
                intent_id="intent.synthetic.invalid",
                run_id="run.test",
                actor_id=SIGNAL_CASE.first_actor,
                logical_tick=1,
                prestate_version=0,
                prestate_sha256="0" * 64,
                action_type=SIGNAL_CASE.first_intent,
                parameters={"target_id": "unknown_target"},
                policy_id="policy.test",
            )
            dispositions, deltas = environment.apply_batch(
                state,
                (invalid,),
                0,
                1,
            )
            self.assertEqual("rejected", dispositions[0].status)
            self.assertEqual(
                "parameter_domain_violation:target_id",
                dispositions[0].reason_code,
            )
            self.assertFalse(deltas)
            self.assertEqual(
                SIGNAL_CASE.initial_value,
                state["entities"][SIGNAL_CASE.entity_id]["status"],
            )

    def test_package_configuration_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = build_synthetic_event(root, SIGNAL_CASE)
            candidate = root / "tampered-package"
            shutil.copytree(case.package_root, candidate)
            path = candidate / "backend-bindings" / "rule-configuration.json"
            value = _read(path)
            value["settings"]["decision_rules"][0]["priority"] += 1
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(
                EventPackageError,
                "backend_configuration_self_hash_mismatch",
            ):
                load_event_package(candidate, case.data_root, "rule")

    def test_generated_epg_rejects_missing_trace_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = build_synthetic_event(root, SIGNAL_CASE)
            run_root = root / "run"
            materialize_run(
                package_root=case.package_root,
                data_root=case.data_root,
                output_root=run_root,
                custody_locator=(
                    ".local-runtime/h2epr-simulation/runs/tests/"
                    "synthetic-signal/trace-coverage"
                ),
            )
            graph = _read(run_root / "generated_epg.json")
            trace = [
                json.loads(line)
                for line in (run_root / "simulation_trace.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            trace_node = next(
                row
                for row in graph["nodes"]
                if row["node_type"].startswith("trace_record.")
            )
            graph["nodes"].remove(trace_node)
            graph["edges"] = [
                row
                for row in graph["edges"]
                if trace_node["node_id"]
                not in {row["source_id"], row["target_id"]}
            ]
            with self.assertRaisesRegex(
                GeneratedEPGError,
                "generated_epg_trace_coverage_mismatch",
            ):
                validate_generated_epg(graph, trace)


if __name__ == "__main__":
    unittest.main()
