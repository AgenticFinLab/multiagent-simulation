from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from h2epr.benchmark.package import EventPackage, load_event_package
from h2epr.canonical import (
    canonical_sha256,
    file_sha256,
    write_json,
    write_jsonl,
)
from h2epr.conformance import (
    ConformanceError,
    build_cross_event_contract_receipt,
    build_identity_invariance_receipt,
)
from h2epr.masim_kernel import (
    RunSeal,
    TickSeal,
    canonical_sha256 as masim_sha256,
)
from h2epr.publication import (
    PublicationError,
    _derive_coordinate_results,
    _derive_run_counts,
    publish_rule_run_release,
)
from h2epr.runtime.benchmark_runner import (
    OUTPUT_ROLES,
    build_determinism_receipt,
    materialize_run,
)
from h2epr.runtime.generated_epg import (
    compile_generated_epg,
    validate_generated_epg,
)

from support import DATA_ROOT, CURRENT_CASES, package_root


class RuntimeAndConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.cases = {}
        for event_id, slug, *_ in CURRENT_CASES:
            package = load_event_package(package_root(slug), DATA_ROOT, "rule")
            left = cls.root / f"{slug}-left"
            right = cls.root / f"{slug}-right"
            probe = cls.root / f"{slug}-probe"
            canonical_locator = (
                f".local-runtime/h2epr-simulation/runs/benchmark/{slug}/"
                "rule/materialization-a"
            )
            left_receipt = materialize_run(
                package_root=package_root(slug),
                data_root=DATA_ROOT,
                output_root=left,
                backend="rule",
                run_seed=0,
                identity_variant="canonical",
                custody_locator=canonical_locator,
            )
            materialize_run(
                package_root=package_root(slug),
                data_root=DATA_ROOT,
                output_root=right,
                backend="rule",
                run_seed=0,
                identity_variant="canonical",
                custody_locator=canonical_locator,
            )
            materialize_run(
                package_root=package_root(slug),
                data_root=DATA_ROOT,
                output_root=probe,
                backend="rule",
                run_seed=0,
                identity_variant="generated-id-probe",
                custody_locator=(
                    f".local-runtime/h2epr-simulation/runs/benchmark/{slug}/"
                    "rule/identity-probe"
                ),
            )
            identity = build_identity_invariance_receipt(left, probe)
            cls.cases[event_id] = {
                "slug": slug,
                "package": package,
                "left": left,
                "right": right,
                "probe": probe,
                "receipt": left_receipt,
                "identity": identity,
            }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_replay_trace_graph_transport_and_counts_close(self) -> None:
        expected = {
            event_id: (ticks, traces, nodes, edges)
            for (
                event_id,
                _slug,
                _roster,
                _actors,
                ticks,
                traces,
                nodes,
                edges,
            ) in CURRENT_CASES
        }
        for event_id, case in self.cases.items():
            receipt = case["receipt"]
            ticks, traces, nodes, edges = expected[event_id]
            with self.subTest(event_id=event_id):
                self.assertTrue(receipt["replay_passed"])
                self.assertTrue(receipt["trace_coverage_passed"])
                self.assertEqual(0, receipt["unresolved_transport_count"])
                self.assertEqual(ticks, receipt["counts"]["ticks"])
                self.assertEqual(traces, receipt["counts"]["trace_records"])
                self.assertEqual(nodes, receipt["counts"]["graph_nodes"])
                self.assertEqual(edges, receipt["counts"]["graph_edges"])
                graph = json.loads(
                    (case["left"] / "generated_epg.json").read_text(encoding="utf-8")
                )
                trace = [
                    json.loads(line)
                    for line in (case["left"] / "simulation_trace.jsonl")
                    .read_text(encoding="utf-8")
                    .splitlines()
                ]
                validate_generated_epg(graph, trace)
                self.assertEqual(traces, graph["trace_coverage"]["record_count"])
                self.assertEqual(
                    traces, graph["trace_coverage"]["referenced_record_count"]
                )

    def test_a_b_bytes_and_identity_perturbation_both_close(self) -> None:
        for event_id, case in self.cases.items():
            with self.subTest(event_id=event_id):
                identity = case["identity"]
                self.assertTrue(identity["passed"])
                self.assertTrue(all(row["passed"] for row in identity["checks"]))
                determinism = build_determinism_receipt(
                    left_root=case["left"],
                    right_root=case["right"],
                    package=case["package"],
                    identity_conformance_receipt_sha256=identity["receipt_sha256"],
                )
                self.assertTrue(determinism["all_byte_identical"])
                self.assertEqual(
                    identity["receipt_sha256"],
                    determinism["identity_conformance_receipt_sha256"],
                )
                for filename in (*OUTPUT_ROLES, "run_receipt.json"):
                    self.assertEqual(
                        file_sha256(case["left"] / filename),
                        file_sha256(case["right"] / filename),
                    )

    def test_every_non_noop_rule_action_is_admitted(self) -> None:
        for event_id, case in self.cases.items():
            rows = [
                json.loads(line)
                for line in (case["left"] / "simulation_trace.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            dispositions = [
                row["payload"]
                for row in rows
                if row["record_type"] == "action_disposition"
                and row["payload"]["action_type"] != "no_op"
            ]
            with self.subTest(event_id=event_id):
                self.assertTrue(dispositions)
                self.assertTrue(
                    all(row["status"] == "accepted" for row in dispositions)
                )
                self.assertTrue(
                    all(
                        row["reason_code"]
                        in {"admitted_applied", "admitted_no_effect"}
                        for row in dispositions
                    )
                )

    def test_three_event_contract_conformance_closes(self) -> None:
        receipt = build_cross_event_contract_receipt(
            [
                (case["package"], case["left"])
                for case in self.cases.values()
            ]
        )
        self.assertTrue(receipt["passed"])
        self.assertEqual(8, len(receipt["checks"]))
        self.assertTrue(all(row["passed"] for row in receipt["checks"]))

    def test_cross_event_conformance_is_not_fixed_to_three_cases(self) -> None:
        cases = [
            (case["package"], case["left"])
            for case in self.cases.values()
        ]
        receipt = build_cross_event_contract_receipt(cases[:2])
        identity = next(
            row
            for row in receipt["checks"]
            if row["check_id"] == "distinct_event_identities"
        )
        self.assertEqual(2, identity["evidence"]["event_count"])
        self.assertTrue(receipt["passed"])
        with self.assertRaisesRegex(
            ConformanceError,
            "cross_event_contract_failed:distinct_event_identities",
        ):
            build_cross_event_contract_receipt([cases[0], cases[0]])

    def test_release_publisher_closes_and_rejects_custody_tamper(self) -> None:
        case = self.cases["H2EPR-0288"]
        release = self.root / "published-release"
        summary = publish_rule_run_release(
            package_root=package_root(case["slug"]),
            data_root=DATA_ROOT,
            canonical_root=case["left"],
            repeat_root=case["right"],
            probe_root=case["probe"],
            release_root=release,
            event_title="Panic of 1907",
            simulation_reading_link="../../../reports/example.md",
        )
        self.assertEqual("H2EPR-0288", summary["event_id"])
        self.assertEqual(
            {
                "README.md",
                "SHA256SUMS",
                "determinism-receipt.json",
                "generated-id-conformance.json",
                "run-manifest.json",
                "run-receipt.json",
            },
            {path.name for path in release.iterdir()},
        )

        tampered = self.root / "tampered-custody"
        shutil.copytree(case["left"], tampered)
        final_state = tampered / "final_state.json"
        final_state.write_text(
            final_state.read_text(encoding="utf-8") + " ",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            PublicationError,
            "run_output_size_mismatch:final_state.json",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=tampered,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "rejected-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )
        self.assertFalse((self.root / "rejected-release").exists())

    def test_release_publisher_rederives_replay_and_trace_evidence(self) -> None:
        case = self.cases["H2EPR-0288"]

        forged_replay = self.root / "forged-replay-custody"
        shutil.copytree(case["left"], forged_replay)
        replay = json.loads(
            (forged_replay / "replay_receipt.json").read_text(encoding="utf-8")
        )
        replay["replayed_state_sha256"] = "0" * 64
        replay["receipt_sha256"] = canonical_sha256(
            {key: value for key, value in replay.items() if key != "receipt_sha256"}
        )
        write_json(forged_replay / "replay_receipt.json", replay)
        self._reseal_run_receipt_inventory(forged_replay)
        with self.assertRaisesRegex(
            PublicationError,
            "replay_receipt_evidence_mismatch",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged_replay,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "forged-replay-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )

    def test_release_publisher_rederives_manifest_trace_summaries_and_counts(
        self,
    ) -> None:
        case = self.cases["H2EPR-0288"]

        forged_manifest = self.root / "forged-manifest-custody"
        shutil.copytree(case["left"], forged_manifest)
        manifest = json.loads(
            (forged_manifest / "run_manifest.json").read_text(encoding="utf-8")
        )
        manifest["run_settings"]["seed"] = 1
        manifest["run_manifest_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in manifest.items()
                if key != "run_manifest_sha256"
            }
        )
        write_json(forged_manifest / "run_manifest.json", manifest)
        receipt = json.loads(
            (forged_manifest / "run_receipt.json").read_text(encoding="utf-8")
        )
        receipt["run_manifest_sha256"] = manifest["run_manifest_sha256"]
        write_json(forged_manifest / "run_receipt.json", receipt)
        self._reseal_run_receipt_inventory(forged_manifest)
        with self.assertRaisesRegex(PublicationError, "run_seed_mismatch"):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged_manifest,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "forged-manifest-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )

        forged_summary = self.root / "forged-summary-custody"
        shutil.copytree(case["left"], forged_summary)
        coordinate_results = json.loads(
            (forged_summary / "coordinate_results.json").read_text(
                encoding="utf-8"
            )
        )
        coordinate_results[0]["action_intent_count"] += 1
        write_json(forged_summary / "coordinate_results.json", coordinate_results)
        self._reseal_run_receipt_inventory(forged_summary)
        with self.assertRaisesRegex(
            PublicationError,
            "coordinate_results_not_trace_derived",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged_summary,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "forged-summary-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )

        forged_counts = self.root / "forged-counts-custody"
        shutil.copytree(case["left"], forged_counts)
        receipt = json.loads(
            (forged_counts / "run_receipt.json").read_text(encoding="utf-8")
        )
        receipt["counts"]["action.no_op"] += 1
        write_json(forged_counts / "run_receipt.json", receipt)
        self._reseal_run_receipt_inventory(forged_counts)
        with self.assertRaisesRegex(
            PublicationError,
            "run_count_evidence_mismatch",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged_counts,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "forged-counts-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )

        forged_trace = self.root / "forged-trace-custody"
        shutil.copytree(case["left"], forged_trace)
        rows = [
            json.loads(line)
            for line in (forged_trace / "simulation_trace.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        rows[0]["payload"]["coordinate_id"] = "forged.coordinate"
        write_jsonl(forged_trace / "simulation_trace.jsonl", rows)
        receipt = json.loads(
            (forged_trace / "run_receipt.json").read_text(encoding="utf-8")
        )
        receipt["trace_sha256"] = canonical_sha256(rows)
        write_json(forged_trace / "run_receipt.json", receipt)
        self._reseal_run_receipt_inventory(forged_trace)
        with self.assertRaisesRegex(
            PublicationError,
            "run_trace_invalid:RECORD_HASH_MISMATCH",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged_trace,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "forged-trace-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )

    def test_release_publisher_rejects_fully_resealed_semantic_forgery(
        self,
    ) -> None:
        case = self.cases["H2EPR-0288"]
        forged = self.root / "fully-resealed-semantic-forgery"
        shutil.copytree(case["left"], forged)
        self._forge_semantically_inconsistent_decision(
            forged,
            case["package"],
        )
        with self.assertRaisesRegex(
            PublicationError,
            "run_decision_action_mismatch",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "semantic-forgery-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )
        self.assertFalse((self.root / "semantic-forgery-release").exists())

    def test_release_publisher_recompiles_generated_epg(self) -> None:
        case = self.cases["H2EPR-0288"]
        forged = self.root / "forged-graph-identity"
        shutil.copytree(case["left"], forged)
        graph = json.loads(
            (forged / "generated_epg.json").read_text(encoding="utf-8")
        )
        graph["event_id"] = "H2EPR-9999"
        graph["seal"]["artifact_sha256"] = canonical_sha256(
            {key: value for key, value in graph.items() if key != "seal"}
        )
        write_json(forged / "generated_epg.json", graph)
        receipt = json.loads(
            (forged / "run_receipt.json").read_text(encoding="utf-8")
        )
        receipt["generated_epg_sha256"] = graph["seal"]["artifact_sha256"]
        write_json(forged / "run_receipt.json", receipt)
        self._reseal_run_receipt_inventory(forged)
        with self.assertRaisesRegex(
            PublicationError,
            "run_generated_epg_not_independently_derived",
        ):
            publish_rule_run_release(
                package_root=package_root(case["slug"]),
                data_root=DATA_ROOT,
                canonical_root=forged,
                repeat_root=case["right"],
                probe_root=case["probe"],
                release_root=self.root / "forged-graph-release",
                event_title="Panic of 1907",
                simulation_reading_link="../../../reports/example.md",
            )

    @staticmethod
    def _forge_semantically_inconsistent_decision(
        root: Path,
        package: EventPackage,
    ) -> None:
        manifest = json.loads(
            (root / "run_manifest.json").read_text(encoding="utf-8")
        )
        rows = [
            json.loads(line)
            for line in (root / "simulation_trace.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        decision = next(
            row for row in rows if row["record_type"] == "participant_decision"
        )
        decision["payload"]["action"]["action_type"] = (
            "forged_unpermitted_action"
        )

        rebuilt = []
        tick_seals = []
        run_seal = None
        for original in rows:
            row = copy.deepcopy(original)
            logical_tick = row["logical_tick"]
            if row["record_type"] == "tick_seal":
                preseal = [
                    item
                    for item in rebuilt
                    if item["logical_tick"] == logical_tick
                    and item["record_type"] not in {"tick_seal", "run_seal"}
                ]
                tick_seal = TickSeal(
                    manifest["run_id"],
                    logical_tick,
                    manifest["run_manifest_sha256"],
                    preseal[0]["record_hash"],
                    preseal[-1]["record_hash"],
                    row["payload"]["state_sha256"],
                    len(preseal),
                ).sealed()
                row["payload"] = tick_seal.to_dict()
                tick_seals.append(tick_seal)
            elif row["record_type"] == "run_seal":
                old = row["payload"]
                run_seal = RunSeal(
                    manifest["run_id"],
                    manifest["run_manifest_sha256"],
                    tuple(item.seal_sha256 for item in tick_seals),
                    masim_sha256(rebuilt),
                    old["final_state_sha256"],
                    tuple(old["unresolved_intent_ids"]),
                    tuple(old["unresolved_recipient_ids"]),
                ).sealed()
                row["payload"] = run_seal.to_dict()
            row["previous_record_hash"] = (
                rebuilt[-1]["record_hash"] if rebuilt else "0" * 64
            )
            row["record_hash"] = masim_sha256(
                {key: value for key, value in row.items() if key != "record_hash"}
            )
            rebuilt.append(row)
        assert run_seal is not None

        write_jsonl(root / "simulation_trace.jsonl", rebuilt)
        write_json(
            root / "tick_seals.json",
            [item.to_dict() for item in tick_seals],
        )
        write_json(root / "run_seal.json", run_seal.to_dict())
        graph = compile_generated_epg(package, manifest, rebuilt)
        write_json(root / "generated_epg.json", graph)
        write_json(
            root / "coordinate_results.json",
            _derive_coordinate_results(rebuilt, package),
        )

        replay = json.loads(
            (root / "replay_receipt.json").read_text(encoding="utf-8")
        )
        replay["trace_sha256"] = canonical_sha256(rebuilt)
        replay["receipt_sha256"] = canonical_sha256(
            {key: value for key, value in replay.items() if key != "receipt_sha256"}
        )
        write_json(root / "replay_receipt.json", replay)

        receipt = json.loads(
            (root / "run_receipt.json").read_text(encoding="utf-8")
        )
        receipt["trace_sha256"] = canonical_sha256(rebuilt)
        receipt["run_seal_sha256"] = run_seal.seal_sha256
        receipt["generated_epg_sha256"] = graph["seal"]["artifact_sha256"]
        receipt["counts"] = _derive_run_counts(rebuilt, package, graph)
        write_json(root / "run_receipt.json", receipt)
        RuntimeAndConformanceTests._reseal_run_receipt_inventory(root)

    @staticmethod
    def _reseal_run_receipt_inventory(root: Path) -> None:
        receipt = json.loads(
            (root / "run_receipt.json").read_text(encoding="utf-8")
        )
        for row in receipt["output_files"]:
            path = root / row["relative_path"]
            row["sha256"] = file_sha256(path)
            row["size_bytes"] = path.stat().st_size
        receipt["custody"]["inventory_sha256"] = canonical_sha256(
            receipt["output_files"]
        )
        receipt["receipt_sha256"] = canonical_sha256(
            {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        )
        write_json(root / "run_receipt.json", receipt)


if __name__ == "__main__":
    unittest.main()
