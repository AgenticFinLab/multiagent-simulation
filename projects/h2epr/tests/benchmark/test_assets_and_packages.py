from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from h2epr.benchmark.compiler import compile_event_package
from h2epr.benchmark.package import EventPackageError, load_event_package
from h2epr.canonical import file_sha256

from support import CURRENT_EVENTS, DATA_ROOT, PROJECT_ROOT
from synthetic import DISPATCH_CASE, SIGNAL_CASE, build_synthetic_event


AGENT_HEADINGS = [
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
POPULATION_HEADINGS = [
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
SCENARIO_HEADINGS = [
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


def _files(root: Path) -> list[Path]:
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    )


def _assert_inventory(test: unittest.TestCase, root: Path) -> None:
    inventory = root / "SHA256SUMS"
    declared: dict[str, str] = {}
    for line in inventory.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        test.assertNotIn(relative, declared)
        declared[relative] = digest
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    test.assertEqual(actual, set(declared))
    for relative, digest in declared.items():
        test.assertEqual(digest, file_sha256(root / relative))


class AssetAndPackageTests(unittest.TestCase):
    def test_two_unrelated_synthetic_packages_close_the_same_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for vocabulary in (SIGNAL_CASE, DISPATCH_CASE):
                with self.subTest(event_id=vocabulary.event_id):
                    case = build_synthetic_event(root, vocabulary)
                    package = load_event_package(
                        case.package_root,
                        case.data_root,
                        "rule",
                    )
                    self.assertEqual(case.event_id, package.manifest["event_id"])
                    self.assertEqual(2, package.participants["participant_count"])
                    self.assertEqual(2, len(package.scenario["active_actor_ids"]))
                    self.assertEqual(3, len(package.scenario["timeline"]))
                    self.assertEqual(
                        "full_draft_exposed",
                        package.manifest["source_exposure"],
                    )
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

    def test_compiler_is_byte_deterministic_without_a_real_event_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = build_synthetic_event(root, SIGNAL_CASE)
            left = root / "compile-left"
            right = root / "compile-right"
            first = compile_event_package(
                project_root=case.project_root,
                data_root=case.data_root,
                assembly_path=case.assembly_path,
                output_root=left,
            )
            second = compile_event_package(
                project_root=case.project_root,
                data_root=case.data_root,
                assembly_path=case.assembly_path,
                output_root=right,
            )
            self.assertEqual(first, second)
            self.assertEqual(_files(left), _files(right))
            self.assertEqual(_files(left), _files(case.package_root))
            for relative in _files(left):
                self.assertEqual(
                    file_sha256(left / relative),
                    file_sha256(right / relative),
                )
                self.assertEqual(
                    file_sha256(left / relative),
                    file_sha256(case.package_root / relative),
                )

    def test_planned_backends_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            for backend in ("llm", "rulellm"):
                with self.subTest(backend=backend), self.assertRaisesRegex(
                    EventPackageError,
                    f"backend_not_implemented:{backend}",
                ):
                    load_event_package(case.package_root, case.data_root, backend)

    def test_human_templates_have_one_stable_reading_order(self) -> None:
        templates = {
            "agents/agent-definition-template.md": AGENT_HEADINGS,
            "populations/population-model-template.md": POPULATION_HEADINGS,
            "scenarios/scenario-definition-template.md": SCENARIO_HEADINGS,
        }
        for relative, expected in templates.items():
            text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(template=relative):
                self.assertEqual(
                    expected,
                    [line for line in text.splitlines() if line.startswith("## ")],
                )

    def test_synthetic_release_inventories_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            inventories = sorted(case.project_root.rglob("SHA256SUMS"))
            self.assertGreaterEqual(len(inventories), 5)
            for inventory in inventories:
                with self.subTest(root=inventory.parent):
                    _assert_inventory(self, inventory.parent)

    def test_common_python_contains_no_current_or_literal_event_identity(self) -> None:
        identities = {
            row["event_id"] for row in CURRENT_EVENTS
        } | {
            row["event_slug"] for row in CURRENT_EVENTS
        }
        exact_event_id = re.compile(r"H2EPR-[0-9]{4}")
        for path in (PROJECT_ROOT / "src" / "h2epr").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(source=path.relative_to(PROJECT_ROOT)):
                self.assertIsNone(exact_event_id.search(text))
                for identity in identities:
                    self.assertNotIn(identity, text)

    def test_current_registry_rows_load_without_becoming_test_oracles(self) -> None:
        for row in CURRENT_EVENTS:
            with self.subTest(event_id=row["event_id"]):
                package = load_event_package(
                    PROJECT_ROOT / row["package_relative_path"],
                    DATA_ROOT,
                    "rule",
                )
                self.assertEqual(row["event_id"], package.manifest["event_id"])


if __name__ == "__main__":
    unittest.main()
