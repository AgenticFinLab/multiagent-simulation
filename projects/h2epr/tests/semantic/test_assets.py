from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from h2epr.benchmark.compiler import (
    SemanticPackageCompileError,
    validate_configuration_provenance_coverage,
)
from h2epr.canonical import canonical_sha256
from h2epr.benchmark._compiler_core import _draft_roster
from h2epr.semantic._assets_core import (
    _AssetAdmissionCoreError,
    _validate_source_documents,
)

from support import PROJECT_ROOT
from synthetic import SIGNAL_CASE, build_synthetic_event


def _sealed(value: dict, field: str) -> dict:
    value[field] = canonical_sha256(
        {key: item for key, item in value.items() if key != field}
    )
    return value


class StandardAssetTests(unittest.TestCase):
    def test_configuration_coverage_is_exhaustive_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = build_synthetic_event(Path(temporary), SIGNAL_CASE)
            root = case.project_root / "configs" / case.slug / "shared"
            configuration = json.loads(
                (root / "scenario-configuration.json").read_text(encoding="utf-8")
            )
            coverage = json.loads(
                (root / "provenance-coverage.json").read_text(encoding="utf-8")
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
                    "coverage_id": "h2epr.synthetic.exempted-coverage",
                    "configuration_id": exempted_configuration[
                        "configuration_id"
                    ],
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
                            "reason": "The admitted fixture supplies no basis.",
                            "review_authority": "independent reviewer",
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
            overlap["exemptions"] = copy.deepcopy(
                reviewed_exemption["exemptions"]
            )
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

    def test_agent_template_owns_semantics_without_backend_policy(self) -> None:
        text = (
            PROJECT_ROOT / "agents" / "agent-definition-template.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(text.lower().split())
        self.assertEqual(
            10,
            sum(line.startswith("## ") for line in text.splitlines()),
        )
        for phrase in (
            "represented decision interface",
            "dataset basis and provenance",
            "admissible decision semantics",
            "environment-owned result",
            "configurable dimensions and uncertainty",
            "worked cases and contract falsification",
            "condition for a successor",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)
        self.assertIn(
            "rule code, an llm, or rulellm admission selects within that set",
            normalized,
        )

    def test_population_template_requires_real_choice_and_aggregation(self) -> None:
        text = (
            PROJECT_ROOT / "populations" / "population-model-template.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(text.lower().split())
        self.assertEqual(
            10,
            sum(line.startswith("## ") for line in text.splitlines()),
        )
        for phrase in (
            "choice unit",
            "aggregation boundary",
            "observed group labels",
            "heterogeneity",
            "environment-owned",
            "missing microdata",
            "successor conditions",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)
        self.assertIn("do not select exact distribution parameters here", normalized)


class SourceDocumentShapeTests(unittest.TestCase):
    @staticmethod
    def documents() -> dict:
        def wrap(value: str) -> dict:
            return {"value": value}

        participant = {
            "participant_id": "P_1",
            "name": wrap("Observer later deciding"),
            "participant_type": wrap("organization"),
            "base_role": wrap("participant"),
            "actions": [],
        }
        later = copy.deepcopy(participant)
        later["actions"] = [{"name": wrap("respond"), "timestamp": wrap("later")}]
        episodes = [
            {
                "episode_id": f"E{number}",
                "name": wrap("Synthetic episode"),
                "start_time": wrap("unknown"),
                "end_time": wrap("unknown"),
                "participants": [value],
            }
            for number, value in enumerate((participant, later), 1)
        ]
        return {
            "event_spec": {
                "public_event_id": "H2EPR-9997",
                "title": "Synthetic passive appearance",
                "schema_version": "synthetic",
            },
            "frozen_evidence": {
                "public_event_id": "H2EPR-9997",
                "source_count": 1,
                "sources": [{"source_id": "synthetic-only"}],
            },
            "draft_epg": {
                "event_id": "synthetic-passive-appearance",
                "title": wrap("Synthetic passive appearance"),
                "start_time": wrap("unknown"),
                "end_time": wrap("unknown"),
                "stages": [{
                    "stage_id": "S1",
                    "name": wrap("Synthetic stage"),
                    "start_time": wrap("unknown"),
                    "end_time": wrap("unknown"),
                    "episodes": episodes,
                }],
            },
        }

    def test_empty_actions_preserves_a_passive_appearance(self) -> None:
        documents = self.documents()
        before = copy.deepcopy(documents)
        _validate_source_documents(documents, "H2EPR-9997")
        roster, _ = _draft_roster(documents["draft_epg"])
        self.assertEqual(1, len(roster))
        self.assertEqual(
            ["draft_epg:S1/E1/P_1", "draft_epg:S1/E2/P_1"],
            roster[0]["appearance_refs"],
        )
        self.assertEqual(before, documents)

    def test_missing_or_non_list_actions_still_fail_closed(self) -> None:
        for invalid in (None, {}, "", True, 0, "missing"):
            with self.subTest(invalid=invalid):
                documents = self.documents()
                participant = documents["draft_epg"]["stages"][0]["episodes"][0]["participants"][0]
                if invalid == "missing":
                    participant.pop("actions")
                else:
                    participant["actions"] = invalid
                with self.assertRaisesRegex(
                    _AssetAdmissionCoreError, "draft_actions_invalid:E1:P_1"
                ):
                    _validate_source_documents(documents, "H2EPR-9997")

    def test_nonempty_action_wrappers_still_require_valid_structure(self) -> None:
        for invalid in (
            None,
            {},
            {"name": "unwrapped", "timestamp": {"value": "now"}},
            {"name": {"value": "respond"}, "timestamp": "unwrapped"},
        ):
            with self.subTest(invalid=invalid):
                documents = self.documents()
                participant = documents["draft_epg"]["stages"][0]["episodes"][0]["participants"][0]
                participant["actions"] = [invalid]
                with self.assertRaisesRegex(_AssetAdmissionCoreError, "draft_action"):
                    _validate_source_documents(documents, "H2EPR-9997")


if __name__ == "__main__":
    unittest.main()
