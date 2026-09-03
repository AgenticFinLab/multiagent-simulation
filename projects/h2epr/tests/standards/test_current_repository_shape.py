from __future__ import annotations

import copy
import ast
import json
import re
import tempfile
from pathlib import Path
import unittest

from h2epr.canonical import canonical_sha256
from h2epr.benchmark.package import load_event_package
from h2epr.repository import (
    CurrentEventRegistryError,
    load_current_event_registry,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT.parents[1] / "data" / "h2epr"
EXCLUDED_TREE_PARTS = {"build", "__pycache__", ".pytest_cache"}
DEVELOPMENT_GENERATION = re.compile(
    r"(^|/)(?:v\d+|[^/]*(?:v0\.\d+|_v\d+|-v\d+)[^/]*)(?:/|$)"
)


def _files(relative: str) -> set[str]:
    root = PROJECT_ROOT / relative
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }


class CurrentRepositoryShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_current_event_registry(PROJECT_ROOT)
        cls.events = cls.registry["events"]

    def test_current_event_packages_have_one_exact_role_surface(self) -> None:
        expected = {
            "README.md",
            "SHA256SUMS",
            "manifest.json",
            "source-profile.json",
            "semantic-assets.json",
            "participants.json",
            "participant-interface.json",
            "participant-semantic-index.json",
            "scenario.json",
            "shared-configuration.json",
            "shared-configuration-provenance.json",
            "backend-bindings/rule.json",
            "backend-bindings/rule-realization.json",
            "backend-bindings/rule-configuration.json",
            "backend-bindings/rule-configuration-provenance.json",
        }
        for row in self.events:
            with self.subTest(slug=row["event_slug"]):
                self.assertEqual(
                    expected,
                    _files(row["package_relative_path"]),
                )
                package = load_event_package(
                    PROJECT_ROOT / row["package_relative_path"],
                    DATA_ROOT,
                    "rule",
                )
                self.assertEqual(row["event_id"], package.manifest["event_id"])

    def test_current_semantic_and_execution_releases_are_symmetric(self) -> None:
        surfaces = {
            "roster_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "manifest.json",
                "roster.json",
                "actor-map.json",
            },
            "participant_interface_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "manifest.json",
                "observation-registry.json",
                "intent-registry.json",
                "lifecycle-registry.json",
                "participant-interface.json",
                "participant-semantic-index.json",
            },
            "scenario_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "manifest.json",
                "scenario-definition.md",
                "scenario-interface.json",
                "scenario-mechanism.json",
                "interface-closure.md",
            },
            "shared_configuration_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "manifest.json",
                "configuration-design.md",
                "scenario-configuration.json",
                "admission-receipt.json",
                "provenance-coverage.json",
            },
            "rule_configuration_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "manifest.json",
                "rule-configuration.json",
                "admission-receipt.json",
                "provenance-coverage.json",
            },
            "rule_execution_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "manifest.json",
                "realization.json",
                "rule-realization.md",
            },
            "rule_run_release_relative_path": {
                "README.md",
                "SHA256SUMS",
                "run-manifest.json",
                "run-receipt.json",
                "determinism-receipt.json",
                "generated-id-conformance.json",
            },
            "report_root": {
                "simulation-reading.md",
            },
        }
        for field, expected in surfaces.items():
            for row in self.events:
                relative = (
                    str(Path(row["simulation_reading_relative_path"]).parent)
                    if field == "report_root"
                    else row[field]
                )
                with self.subTest(surface=relative):
                    self.assertEqual(expected, _files(relative))

    def test_event_entries_share_current_completion_structure(self) -> None:
        expected_headings = [
            "## Event assets",
            "## Backend status",
            "## Current result",
            "## Claim boundary",
        ]
        for row in self.events:
            path = PROJECT_ROOT / "events" / row["event_slug"] / "README.md"
            text = path.read_text(encoding="utf-8")
            with self.subTest(slug=row["event_slug"]):
                self.assertEqual(
                    expected_headings,
                    [line for line in text.splitlines() if line.startswith("## ")],
                )
                self.assertNotIn("review candidate", text.lower())
                self.assertNotIn("review is deferred", text.lower())

    def test_current_indexes_name_every_event(self) -> None:
        indexes = (
            "README.md",
            "agents/README.md",
            "populations/README.md",
            "scenarios/README.md",
            "configs/README.md",
            "events/README.md",
            "execution/README.md",
            "releases/README.md",
            "reports/README.md",
        )
        for relative in indexes:
            text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
            for row in self.events:
                slug = row["event_slug"]
                with self.subTest(index=relative, slug=slug):
                    self.assertTrue(
                        slug in text or row["event_id"] in text,
                        f"{relative} does not identify {slug}",
                    )

    def test_reader_facing_tree_has_no_parallel_development_generation(self) -> None:
        violations = []
        for path in PROJECT_ROOT.rglob("*"):
            relative = path.relative_to(PROJECT_ROOT)
            if set(relative.parts) & EXCLUDED_TREE_PARTS:
                continue
            if any(part.endswith(".egg-info") for part in relative.parts):
                continue
            if path.is_file() and DEVELOPMENT_GENERATION.search(
                relative.as_posix()
            ):
                violations.append(relative.as_posix())
        self.assertEqual([], violations)

    def test_public_python_surface_has_stable_names(self) -> None:
        suffix = re.compile(r"(?:_v\d+|V\d+)$")
        violations = []
        source_root = PROJECT_ROOT / "src" / "h2epr"
        for path in source_root.rglob("*.py"):
            relative = path.relative_to(source_root)
            if any(part.startswith("_") for part in relative.parts):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_") and suffix.search(node.name):
                        violations.append(f"{relative}:{node.lineno}:{node.name}")
        self.assertEqual([], violations)

    def test_common_python_contains_no_event_identity(self) -> None:
        identities = {
            row["event_id"] for row in self.events
        } | {
            row["event_slug"] for row in self.events
        }
        violations = []
        for path in (PROJECT_ROOT / "src" / "h2epr").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for identity in identities:
                if identity in text:
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{identity}"
                    )
        self.assertEqual([], violations)

    def test_process_only_surfaces_are_not_published(self) -> None:
        forbidden = (
            "BENCHMARK_SIMULATION_PLAN.md",
            "reports/framework",
            "templates/workflow-feedback.md",
        )
        for relative in forbidden:
            with self.subTest(path=relative):
                self.assertFalse((PROJECT_ROOT / relative).exists())

    def test_fourth_event_enters_registry_without_python_event_tuple(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            events = []
            for index in range(4):
                slug = f"synthetic_event_{index}"
                root = project_root / "assets" / slug
                root.mkdir(parents=True)
                source = root / "source-profile.json"
                assembly = root / "package-assembly.json"
                reading = root / "simulation-reading.md"
                source.write_text("{}\n", encoding="utf-8")
                assembly.write_text("{}\n", encoding="utf-8")
                reading.write_text("# Reading\n", encoding="utf-8")
                events.append(
                    {
                        "event_id": f"H2EPR-{9000 + index}",
                        "event_slug": slug,
                        "title": f"Synthetic event {index}",
                        "source_profile_relative_path": source.relative_to(
                            project_root
                        ).as_posix(),
                        "package_assembly_relative_path": assembly.relative_to(
                            project_root
                        ).as_posix(),
                        "simulation_reading_relative_path": reading.relative_to(
                            project_root
                        ).as_posix(),
                        **{
                            field: root.relative_to(project_root).as_posix()
                            for field in (
                                "package_relative_path",
                                "roster_release_relative_path",
                                "participant_interface_release_relative_path",
                                "scenario_release_relative_path",
                                "shared_configuration_release_relative_path",
                                "rule_configuration_release_relative_path",
                                "rule_execution_release_relative_path",
                                "rule_run_release_relative_path",
                            )
                        },
                    }
                )
            registry = {
                "schema_version": "h2epr.current-event-registry.v4",
                "registry_id": "h2epr.current-events.synthetic",
                "registry_version": "0.4.0",
                "events": events,
                "registry_sha256": "0" * 64,
            }
            registry["registry_sha256"] = canonical_sha256(
                {
                    key: value
                    for key, value in registry.items()
                    if key != "registry_sha256"
                }
            )
            registry_path = project_root / "current-events.json"
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            loaded = load_current_event_registry(project_root, registry_path)
            self.assertEqual(4, len(loaded["events"]))

            duplicate = copy.deepcopy(registry)
            duplicate["events"][3]["event_id"] = duplicate["events"][0][
                "event_id"
            ]
            duplicate["registry_sha256"] = canonical_sha256(
                {
                    key: value
                    for key, value in duplicate.items()
                    if key != "registry_sha256"
                }
            )
            registry_path.write_text(
                json.dumps(duplicate, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                CurrentEventRegistryError,
                "current_event_id_duplicate",
            ):
                load_current_event_registry(project_root, registry_path)


if __name__ == "__main__":
    unittest.main()
