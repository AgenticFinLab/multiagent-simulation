from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from h2epr.benchmark.compiler import compile_event_package
from h2epr.benchmark.package import EventPackageError, load_event_package
from h2epr.canonical import file_sha256

from support import (
    DATA_ROOT,
    PROJECT_ROOT,
    CURRENT_CASES,
    assembly_path,
    package_root,
)


class AssetAndPackageTests(unittest.TestCase):
    def test_all_three_formal_packages_close(self) -> None:
        for (
            event_id,
            slug,
            roster_count,
            actor_count,
            tick_count,
            _trace_count,
            _node_count,
            _edge_count,
        ) in CURRENT_CASES:
            with self.subTest(event_id=event_id):
                package = load_event_package(package_root(slug), DATA_ROOT, "rule")
                self.assertEqual(event_id, package.manifest["event_id"])
                self.assertEqual(roster_count, package.participants["participant_count"])
                self.assertEqual(actor_count, len(package.scenario["active_actor_ids"]))
                self.assertEqual(tick_count, len(package.scenario["timeline"]))
                self.assertEqual("full_draft_exposed", package.manifest["source_exposure"])
                self.assertEqual(
                    ["event_spec", "frozen_evidence", "draft_epg"],
                    [
                        row["logical_name"]
                        for row in package.source_profile["allowed_inputs"]
                    ],
                )
                self.assertEqual(
                    [
                        ("rule", "implemented"),
                        ("llm", "planned"),
                        ("rulellm", "planned"),
                    ],
                    [
                        (row["backend"], row["status"])
                        for row in package.manifest["backend_bindings"]
                    ],
                )

    def test_compiler_is_byte_deterministic_for_every_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for _event_id, slug, *_ in CURRENT_CASES:
                with self.subTest(slug=slug):
                    left = root / f"{slug}-left"
                    right = root / f"{slug}-right"
                    first = compile_event_package(
                        project_root=PROJECT_ROOT,
                        data_root=DATA_ROOT,
                        assembly_path=assembly_path(slug),
                        output_root=left,
                    )
                    second = compile_event_package(
                        project_root=PROJECT_ROOT,
                        data_root=DATA_ROOT,
                        assembly_path=assembly_path(slug),
                        output_root=right,
                    )
                    self.assertEqual(first, second)
                    relative_files = sorted(
                        path.relative_to(left)
                        for path in left.rglob("*")
                        if path.is_file()
                    )
                    self.assertEqual(
                        relative_files,
                        sorted(
                            path.relative_to(right)
                            for path in right.rglob("*")
                            if path.is_file()
                        ),
                    )
                    for relative in relative_files:
                        self.assertEqual(
                            file_sha256(left / relative), file_sha256(right / relative)
                        )
                        self.assertEqual(
                            file_sha256(left / relative),
                            file_sha256(package_root(slug) / relative),
                        )

    def test_planned_backends_fail_closed(self) -> None:
        for _event_id, slug, *_ in CURRENT_CASES:
            for backend in ("llm", "rulellm"):
                with self.subTest(slug=slug, backend=backend), self.assertRaisesRegex(
                    EventPackageError, f"backend_not_implemented:{backend}"
                ):
                    load_event_package(package_root(slug), DATA_ROOT, backend)

    def test_human_semantic_parents_and_scenarios_use_stable_modules(self) -> None:
        agent_headings = [
            "## 1. Model overview",
            "## 2. Benchmark participant and representation",
            "## 3. Dataset basis and provenance",
            "## 4. Event role, relationships, and authority",
            "## 5. Decision situations, observations, and state",
            "## 6. Admissible decision semantics",
            "## 7. Intent and environment-result boundary",
            "## 8. Configurable dimensions and uncertainty",
            "## 9. Worked cases and contract falsification",
            "## 10. Limitations and source anchors",
        ]
        population_headings = [
            "## 1. Model overview",
            "## 2. Population scope and representation",
            "## 3. Dataset basis and provenance",
            "## 4. Event role and relationships",
            "## 5. Decision situations, observations, and state",
            "## 6. Choice model and heterogeneity",
            "## 7. Intent and environment-result boundary",
            "## 8. Configuration and uncertainty",
            "## 9. Worked cases and falsification",
            "## 10. Limitations and source anchors",
        ]
        scenario_headings = [
            "## 1. Model overview",
            "## 2. Event boundary and process coverage",
            "## 3. Dataset basis, exposure, and time boundary",
            "## 4. Temporal structure and exogenous inputs",
            "## 5. Participant assembly and causal ownership",
            "## 6. World, institutions, relationships, and resources",
            "## 7. Observation and communication routing",
            "## 8. Intent, adjudication, lifecycle, and result",
            "## 9. Configuration, variants, termination, and identity",
            "## 10. Worked cases, falsification, and limitations",
        ]
        for _event_id, slug, *_ in CURRENT_CASES:
            package = load_event_package(package_root(slug), DATA_ROOT, "rule")
            for parent in package.participant_semantic_index["parents"]:
                text = (PROJECT_ROOT / parent["relative_path"]).read_text(
                    encoding="utf-8"
                )
                observed = [line for line in text.splitlines() if line.startswith("## ")]
                expected = (
                    agent_headings
                    if parent["representation_kind"] == "agent"
                    else population_headings
                )
                with self.subTest(slug=slug, actor=parent["actor_id"]):
                    self.assertEqual(expected, observed)
            scenario = (
                PROJECT_ROOT / "scenarios" / slug / "scenario-definition.md"
            ).read_text(encoding="utf-8")
            with self.subTest(slug=slug, artifact="scenario-definition"):
                self.assertEqual(
                    scenario_headings,
                    [
                        line
                        for line in scenario.splitlines()
                        if line.startswith("## ")
                    ],
                )

    def test_every_current_checksum_inventory_is_exact(self) -> None:
        inventories = sorted(PROJECT_ROOT.rglob("SHA256SUMS"))
        self.assertEqual(25, len(inventories))
        for inventory in inventories:
            root = inventory.parent
            with self.subTest(root=root.relative_to(PROJECT_ROOT)):
                declared = {}
                for line in inventory.read_text(encoding="utf-8").splitlines():
                    digest, relative_path = line.split("  ", 1)
                    self.assertNotIn(relative_path, declared)
                    declared[relative_path] = digest
                actual = {
                    path.relative_to(root).as_posix()
                    for path in root.rglob("*")
                    if path.is_file() and path.name != "SHA256SUMS"
                }
                self.assertEqual(set(declared), actual)
                for relative_path, digest in declared.items():
                    self.assertEqual(file_sha256(root / relative_path), digest)

    def test_common_implementation_contains_no_event_constants(self) -> None:
        sources = (
            "semantic/_assets_core.py",
            "semantic/assets.py",
            "benchmark/_compiler_core.py",
            "benchmark/compiler.py",
            "benchmark/package.py",
            "backends/_rule_core.py",
            "backends/rule.py",
            "backends/registry.py",
            "runtime/_environment_core.py",
            "runtime/environment.py",
            "runtime/_runner_core.py",
            "runtime/benchmark_runner.py",
            "runtime/generated_epg.py",
            "conformance.py",
            "publication.py",
            "experiment.py",
            "cli.py",
        )
        forbidden = (
            "H2EPR-0288",
            "H2EPR-0616",
            "H2EPR-0481",
            "panic_1907",
            "singhealth_data_breach",
            "samsung_note7_battery_recall",
            "jp_morgan",
            "whitefly",
            "samsung_sdi",
        )
        for relative in sources:
            text = (PROJECT_ROOT / "src" / "h2epr" / relative).read_text(
                encoding="utf-8"
            )
            for value in forbidden:
                with self.subTest(source=relative, forbidden=value):
                    self.assertNotIn(value, text)


if __name__ == "__main__":
    unittest.main()
