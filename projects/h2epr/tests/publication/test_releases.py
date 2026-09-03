from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import jsonschema

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import canonical_sha256, file_sha256, write_json
from h2epr.publication import PublicationError, publish_rule_run_release
from h2epr.runtime.benchmark_runner import OUTPUT_ROLES, materialize_run

from support import (
    CURRENT_EVENTS,
    DATA_ROOT,
    PROJECT_ROOT,
    REPOSITORY_ROOT,
    SCHEMA_ROOT,
    package_root,
)
from synthetic import SIGNAL_CASE, build_synthetic_event


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_inventory(test: unittest.TestCase, root: Path) -> None:
    declared = {}
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, relative_path = line.split("  ", 1)
        test.assertNotIn(relative_path, declared)
        declared[relative_path] = digest
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    test.assertEqual(set(declared), actual)
    for relative_path, digest in declared.items():
        test.assertEqual(digest, file_sha256(root / relative_path))


class FormalReleaseTests(unittest.TestCase):
    def test_current_packages_and_compact_releases_close(self) -> None:
        for event in CURRENT_EVENTS:
            package = load_event_package(package_root(event), DATA_ROOT, "rule")
            root = PROJECT_ROOT / event["rule_run_release_relative_path"]
            manifest = _read(root / "run-manifest.json")
            receipt = _read(root / "run-receipt.json")
            determinism = _read(root / "determinism-receipt.json")
            identity = _read(root / "generated-id-conformance.json")
            for artifact, schema_name in (
                (manifest, "run-manifest.schema.json"),
                (receipt, "run-receipt.schema.json"),
                (determinism, "determinism-receipt.schema.json"),
                (identity, "conformance-receipt.schema.json"),
            ):
                schema = _read(SCHEMA_ROOT / schema_name)
                jsonschema.Draft202012Validator(schema).validate(artifact)
            with self.subTest(event_id=event["event_id"]):
                self.assertEqual(package.package_sha256, manifest["package_sha256"])
                self.assertEqual(package.binding_sha256, manifest["binding_sha256"])
                self.assertEqual(manifest["run_id"], receipt["run_id"])
                self.assertTrue(receipt["replay_passed"])
                self.assertTrue(receipt["trace_coverage_passed"])
                self.assertEqual(0, receipt["unresolved_transport_count"])
                self.assertEqual(
                    len(package.scenario["active_actor_ids"]),
                    receipt["counts"]["actors"],
                )
                self.assertEqual(
                    len(package.scenario["timeline"]),
                    receipt["counts"]["ticks"],
                )
                self.assertGreater(receipt["counts"]["trace_records"], 0)
                self.assertGreaterEqual(
                    receipt["counts"]["graph_nodes"],
                    receipt["counts"]["trace_records"],
                )
                self.assertGreater(receipt["counts"]["graph_edges"], 0)
                self.assertTrue(determinism["all_byte_identical"])
                self.assertTrue(identity["passed"])
                self.assertEqual(
                    list(OUTPUT_ROLES),
                    [row["relative_path"] for row in receipt["output_files"]],
                )
                for row in manifest["h2epr_runtime_sources"]:
                    self.assertEqual(
                        row["sha256"],
                        file_sha256(PROJECT_ROOT / row["relative_path"]),
                    )
                for row in manifest["masim_kernel_sources"]:
                    self.assertEqual(
                        row["sha256"],
                        file_sha256(REPOSITORY_ROOT / row["relative_path"]),
                    )
                _assert_inventory(self, root)

    def test_current_cross_event_receipt_closes(self) -> None:
        root = PROJECT_ROOT / "releases" / "cross-event" / "rule"
        if len(CURRENT_EVENTS) < 2:
            self.assertFalse(root.exists())
            return
        receipt = _read(root / "conformance-receipt.json")
        schema = _read(SCHEMA_ROOT / "conformance-receipt.schema.json")
        jsonschema.Draft202012Validator(schema).validate(receipt)
        self.assertEqual(
            [event["event_id"] for event in CURRENT_EVENTS],
            receipt["left_identity"]["event_ids"],
        )
        self.assertTrue(receipt["passed"])
        self.assertTrue(all(row["passed"] for row in receipt["checks"]))
        self.assertEqual(
            receipt["receipt_sha256"],
            canonical_sha256(
                {
                    key: value
                    for key, value in receipt.items()
                    if key != "receipt_sha256"
                }
            ),
        )
        _assert_inventory(self, root)

    def test_current_readings_record_full_scan_and_closure(self) -> None:
        for event in CURRENT_EVENTS:
            package = load_event_package(package_root(event), DATA_ROOT, "rule")
            release = PROJECT_ROOT / event["rule_run_release_relative_path"]
            receipt = _read(release / "run-receipt.json")
            root = (
                PROJECT_ROOT
                / Path(event["simulation_reading_relative_path"]).parent
            )
            reading = (root / "simulation-reading.md").read_text(encoding="utf-8")
            with self.subTest(event_id=event["event_id"]):
                self.assertEqual(
                    [
                        "## Run identity",
                        "## Complete-output coverage",
                        "## Generated trajectory",
                        "## Mechanism reading",
                        "## Limitations",
                    ],
                    [
                        line
                        for line in reading.splitlines()
                        if line.startswith("## ")
                    ],
                )
                self.assertIn("terminal", reading.lower())
                for value in (
                    package.package_sha256,
                    package.binding_sha256,
                    receipt["run_id"],
                    receipt["trace_sha256"],
                    receipt["final_state_sha256"],
                    receipt["generated_epg_sha256"],
                ):
                    self.assertIn(value, reading)


class PublicationAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.event = build_synthetic_event(cls.root, SIGNAL_CASE)
        cls.package = cls.event.package_root
        cls.data_root = cls.event.data_root
        locator = (
            ".local-runtime/h2epr-simulation/runs/tests/"
            f"{cls.event.slug}/rule/publication"
        )
        cls.canonical = cls.root / "canonical"
        cls.repeat = cls.root / "repeat"
        cls.probe = cls.root / "probe"
        materialize_run(
            package_root=cls.package,
            data_root=cls.data_root,
            output_root=cls.canonical,
            backend="rule",
            run_seed=0,
            identity_variant="canonical",
            custody_locator=locator,
        )
        materialize_run(
            package_root=cls.package,
            data_root=cls.data_root,
            output_root=cls.repeat,
            backend="rule",
            run_seed=0,
            identity_variant="canonical",
            custody_locator=locator,
        )
        materialize_run(
            package_root=cls.package,
            data_root=cls.data_root,
            output_root=cls.probe,
            backend="rule",
            run_seed=0,
            identity_variant="generated-id-probe",
            custody_locator=locator + "-probe",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def _reseal_inventory(root: Path) -> None:
        receipt = _read(root / "run_receipt.json")
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

    def test_publisher_independently_reproduces_candidate(self) -> None:
        release = self.root / "published"
        summary = publish_rule_run_release(
            package_root=self.package,
            data_root=self.data_root,
            canonical_root=self.canonical,
            repeat_root=self.repeat,
            probe_root=self.probe,
            release_root=release,
            event_title=self.event.title,
            simulation_reading_link="../../../reports/example.md",
        )
        self.assertEqual(self.event.event_id, summary["event_id"])
        _assert_inventory(self, release)

    def test_publisher_rejects_resealed_graph_identity_forgery(self) -> None:
        forged = self.root / "forged-graph"
        shutil.copytree(self.canonical, forged)
        graph = _read(forged / "generated_epg.json")
        graph["event_id"] = "H2EPR-9999"
        graph["seal"]["artifact_sha256"] = canonical_sha256(
            {key: value for key, value in graph.items() if key != "seal"}
        )
        write_json(forged / "generated_epg.json", graph)
        receipt = _read(forged / "run_receipt.json")
        receipt["generated_epg_sha256"] = graph["seal"]["artifact_sha256"]
        write_json(forged / "run_receipt.json", receipt)
        self._reseal_inventory(forged)
        release = self.root / "forged-release"
        with self.assertRaisesRegex(
            PublicationError,
            "run_generated_epg_not_independently_derived",
        ):
            publish_rule_run_release(
                package_root=self.package,
                data_root=self.data_root,
                canonical_root=forged,
                repeat_root=self.repeat,
                probe_root=self.probe,
                release_root=release,
                event_title=self.event.title,
                simulation_reading_link="../../../reports/example.md",
            )
        self.assertFalse(release.exists())


if __name__ == "__main__":
    unittest.main()
