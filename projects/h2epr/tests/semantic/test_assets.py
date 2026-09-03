from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from h2epr.benchmark.compiler import (
    SemanticPackageCompileError,
    validate_configuration_provenance_coverage,
)
from h2epr.canonical import canonical_sha256


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _sealed(value: dict, field: str) -> dict:
    value[field] = canonical_sha256(
        {key: item for key, item in value.items() if key != field}
    )
    return value


class StandardAssetTests(unittest.TestCase):
    def test_configuration_coverage_is_exhaustive_and_fail_closed(self) -> None:
        path = (
            PROJECT_ROOT
            / "configs"
            / "panic_1907"
            / "shared"
            / "scenario-configuration.json"
        )
        configuration = json.loads(path.read_text(encoding="utf-8"))
        existing = {row["json_pointer"] for row in configuration["value_provenance"]}
        for setting in configuration["settings"]:
            pointer = f"/settings/{setting}"
            if pointer not in existing:
                configuration["value_provenance"].append(
                    {
                        "json_pointer": pointer,
                        "classification": "structural",
                        "basis": "Explicit test basis for exhaustive coverage.",
                    }
                )
        configuration["value_provenance"].sort(key=lambda row: row["json_pointer"])
        _sealed(configuration, "configuration_sha256")
        coverage = _sealed(
            {
                "schema_version": "h2epr.configuration-provenance-coverage.v4",
                "coverage_id": "h2epr.0288.comparison.test.coverage",
                "configuration_id": configuration["configuration_id"],
                "configuration_sha256": configuration["configuration_sha256"],
                "covered_setting_pointers": [
                    row["json_pointer"] for row in configuration["value_provenance"]
                ],
                "exemptions": [],
                "coverage_sha256": "0" * 64,
            },
            "coverage_sha256",
        )
        validate_configuration_provenance_coverage(
            configuration,
            coverage,
            "shared_configuration",
        )

        incomplete = copy.deepcopy(coverage)
        incomplete["covered_setting_pointers"].pop()
        _sealed(incomplete, "coverage_sha256")
        with self.assertRaisesRegex(
            SemanticPackageCompileError,
            "provenance_declaration_coverage_mismatch",
        ):
            validate_configuration_provenance_coverage(
                configuration,
                incomplete,
                "shared_configuration",
            )

        exempted_configuration = copy.deepcopy(configuration)
        exempted_pointer = exempted_configuration["value_provenance"][-1][
            "json_pointer"
        ]
        exempted_configuration["value_provenance"] = [
            row
            for row in exempted_configuration["value_provenance"]
            if row["json_pointer"] != exempted_pointer
        ]
        _sealed(exempted_configuration, "configuration_sha256")
        reviewed_exemption = _sealed(
            {
                "schema_version": "h2epr.configuration-provenance-coverage.v4",
                "coverage_id": "h2epr.0288.comparison.test.exempted-coverage",
                "configuration_id": exempted_configuration["configuration_id"],
                "configuration_sha256": exempted_configuration[
                    "configuration_sha256"
                ],
                "covered_setting_pointers": [
                    row["json_pointer"]
                    for row in exempted_configuration["value_provenance"]
                ],
                "exemptions": [
                    {
                        "json_pointer": exempted_pointer,
                        "reason": "The admitted dataset supplies no basis.",
                        "review_authority": "independent supervisor",
                        "review_status": "accepted_bounded_unavailability",
                        "successor_trigger": "A declared source supplies a basis.",
                    }
                ],
                "coverage_sha256": "0" * 64,
            },
            "coverage_sha256",
        )
        validate_configuration_provenance_coverage(
            exempted_configuration,
            reviewed_exemption,
            "shared_configuration",
        )

        overlap = copy.deepcopy(coverage)
        overlap["exemptions"] = copy.deepcopy(reviewed_exemption["exemptions"])
        _sealed(overlap, "coverage_sha256")
        with self.assertRaisesRegex(
            SemanticPackageCompileError,
            "provenance_coverage_exemption_overlap",
        ):
            validate_configuration_provenance_coverage(
                configuration,
                overlap,
                "shared_configuration",
            )

    def test_agents_exercise_all_required_boundaries(self) -> None:
        required = (
            "**Normal operation:**",
            "**Missing information:**",
            "**Pending state:**",
            "**Authority denial:**",
            "**Adverse environment result:**",
            "**Perturbation:**",
        )
        paths = sorted(
            (PROJECT_ROOT / "agents" / "defines").glob(
                "*/*.md"
            )
        )
        self.assertGreaterEqual(len(paths), 1)
        for path in paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                self.assertEqual(10, sum(
                    line.startswith("## ") for line in text.splitlines()
                ))
                self.assertIn("## 9. Worked cases and contract falsification", text)
                self.assertIn(
                    "The H2EPR environment owns domain admission",
                    text,
                )
                self.assertNotIn("For a population, this is", text)
                self.assertNotIn("MASim owns admission", text)
                for marker in required:
                    self.assertIn(marker, text)

    def test_populations_do_not_invent_microbehavior(self) -> None:
        required = (
            "**Aggregate action:**",
            "**Contrasting response:**",
            "**Missing information:**",
            "**Aggregation change:**",
            "**Environment rejection:**",
            "**Falsifier:**",
        )
        paths = sorted(
            (PROJECT_ROOT / "populations" / "models").glob(
                "*/*.md"
            )
        )
        self.assertGreaterEqual(len(paths), 1)
        for path in paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                self.assertEqual(10, sum(
                    line.startswith("## ") for line in text.splitlines()
                ))
                self.assertIn("one unweighted aggregate choice unit", text)
                self.assertIn("Unsupported heterogeneity remains unavailable", text)
                self.assertIn(
                    "The H2EPR environment owns domain admission",
                    text,
                )
                self.assertNotIn("MASim owns admission", text)
                for marker in required:
                    self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
