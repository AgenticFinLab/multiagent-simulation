from __future__ import annotations

from pathlib import Path
import re
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = PROJECT_ROOT / "skills"

EXPECTED = {
    "agent-definition",
    "agent-definition-review",
    "backend-realization",
    "benchmark-event-simulation",
    "benchmark-input-admission",
    "event-agent-batch",
    "event-scenario-design",
    "experiment-planning",
    "generated-process-analysis",
    "population-model",
    "roster-mapping-conformance",
    "run-release-verification",
    "scenario-configuration",
}

AGENT_DEFINITION_REFERENCES = {
    "annotated-failure-example.md",
    "complete-synthetic-example.md",
    "dataset-provenance-and-exposure.md",
    "decision-commitments-and-intents.md",
    "guide.md",
    "observations-and-state.md",
    "publication-and-completion.md",
    "representation-and-authority.md",
    "worked-cases-and-falsification.md",
}

AGENT_DEFINITION_HEADINGS = [
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


def _case_coverage_errors(example: str) -> list[str]:
    """Check case references and substantive bodies, not domain truth."""
    cases = dict(re.findall(
        r"^### `(case\.[a-z_]+)`[^\n]*\n(.*?)(?=^### |^## |\Z)",
        example, re.MULTILINE | re.DOTALL))
    matrix = re.findall(
        r"^\| `(case\.[a-z_]+)` \| `(decision\.[a-z_]+)` \| `([a-z_]+)` \| ([^|]+) \| ([^|]+) \|$",
        example, re.MULTILINE)
    errors = []
    if not matrix or set(cases) != {row[0] for row in matrix}:
        errors.append("case_matrix_mismatch")
    decisions = set(re.findall(r"^### `(decision\.[a-z_]+)`", example, re.MULTILINE))
    intent_section = example.split("## 7. Intent and environment-result boundary", 1)[1].split("### Message output surface", 1)[0]
    intents = set(re.findall(r"^\| `([a-z_]+)` \|", intent_section, re.MULTILINE))
    if decisions != {row[1] for row in matrix} or intents != {row[2] for row in matrix}:
        errors.append("uncovered_contract")
    for case, decision, intent, information, result in matrix:
        body = cases.get(case, "")
        if (decision not in body or intent not in body or len(body.split()) < 40
                or len(information.split()) < 3 or len(result.split()) < 3):
            errors.append("case_content_incomplete:" + case)
    return errors


class SkillInventoryTests(unittest.TestCase):
    def test_skill_inventory_is_exact_and_named_consistently(self) -> None:
        paths = sorted(SKILL_ROOT.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in paths})
        for path in paths:
            with self.subTest(skill=path.parent.name):
                text = path.read_text(encoding="utf-8")
                match = re.search(r"^name: ([a-z0-9-]+)$", text, re.MULTILINE)
                self.assertIsNotNone(match)
                self.assertEqual(path.parent.name, match.group(1))
                self.assertIn("description:", text)
                self.assertIn("[references/guide.md](references/guide.md)", text)
                self.assertNotIn("reference_epg.json` as input", text.lower())
                guide = path.parent / "references" / "guide.md"
                self.assertTrue(guide.is_file())
                guide_text = guide.read_text(encoding="utf-8")
                self.assertGreaterEqual(len(guide_text.splitlines()), 40)
                self.assertIn("## ", guide_text)
                self.assertTrue(
                    any(
                        token in guide_text.lower()
                        for token in ("failure routing", "failure", "falsifier")
                    )
                )
                self.assertTrue(
                    any(
                        token in guide_text.lower()
                        for token in ("completion evidence", "handoff")
                    )
                )

    def test_agent_definition_method_is_progressively_disclosed(self) -> None:
        package = SKILL_ROOT / "agent-definition"
        skill = (package / "SKILL.md").read_text(encoding="utf-8")
        guide = (package / "references" / "guide.md").read_text(
            encoding="utf-8"
        )
        actual = {
            path.name
            for path in (package / "references").glob("*.md")
        }
        self.assertEqual(AGENT_DEFINITION_REFERENCES, actual)
        self.assertLessEqual(len(skill.splitlines()), 80)

        routed_text = skill + "\n" + guide
        routed_names = {
            Path(target).name
            for target in re.findall(r"\]\(([^)]+\.md)\)", routed_text)
        }
        for name in sorted(AGENT_DEFINITION_REFERENCES):
            with self.subTest(reference=name):
                self.assertIn(name, routed_names)

    def test_agent_definition_example_is_complete_and_cross_referenced(self) -> None:
        example = (
            SKILL_ROOT
            / "agent-definition"
            / "references"
            / "complete-synthetic-example.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            AGENT_DEFINITION_HEADINGS,
            [line for line in example.splitlines() if line.startswith("## ")],
        )
        self.assertNotRegex(example, r"<[^>\n]+>")

        commitments = set(
            re.findall(
                r"^### `(decision\.[a-z0-9_.]+)`",
                example,
                re.MULTILINE,
            )
        )
        observation_section = example.split(
            "### Observation inventory", 1
        )[1].split("### Persistent state surface", 1)[0]
        observations = set(
            re.findall(
                r"^\| `(obs\.[a-z0-9_.]+)` \|",
                observation_section,
                re.MULTILINE,
            )
        )
        state_section = example.split(
            "### Persistent state surface", 1
        )[1].split("## 6. Admissible decision semantics", 1)[0]
        state_fields = set(
            re.findall(
                r"^\| `(entities\.[a-z0-9_.]+)` \|",
                state_section,
                re.MULTILINE,
            )
        )
        intent_section = example.split(
            "## 7. Intent and environment-result boundary", 1
        )[1].split("## 8. Configurable dimensions and uncertainty", 1)[0]
        intents = set(
            re.findall(
                r"^\| `([a-z][a-z0-9_]*)` \|",
                intent_section.split("### Message output surface", 1)[0],
                re.MULTILINE,
            )
        )
        message_section = intent_section.split(
            "### Message output surface", 1
        )[1]
        message_types = set(
            re.findall(
                r"^\| `([a-z][a-z0-9_]*)` \|",
                message_section,
                re.MULTILINE,
            )
        )
        self.assertEqual(
            {"decision.response_request", "decision.operational_notice"},
            commitments,
        )
        self.assertEqual(
            {
                "obs.delivered_messages",
                "obs.participant_memory",
                "obs.pending_lifecycles",
                "obs.public_state",
            },
            observations,
        )
        self.assertEqual(
            {
                "entities.office.request_status",
                "entities.communication.operational_notice_status",
                "entities.navigation.restriction_status",
            },
            state_fields,
        )
        self.assertEqual(
            {
                "issue_operational_notice",
                "request_navigation_restriction",
                "request_report_clarification",
                "withdraw_own_request",
            },
            intents,
        )
        self.assertEqual(
            {
                "navigation_restriction_request",
                "operational_notice",
                "report_clarification_request",
                "request_withdrawal_notice",
            },
            message_types,
        )
        for semantic_id in (
            commitments
            | observations
            | state_fields
            | intents
            | message_types
        ):
            with self.subTest(semantic_id=semantic_id):
                self.assertGreaterEqual(example.count(semantic_id), 2)

        self.assertIn("illustrative authoring example", example)
        self.assertIn("H2EPR-0000", example)
        self.assertIn(
            "h2epr.0000.agent.harbor_response_office.v1",
            example,
        )
        self.assertIn("no release disposition", example)
        self.assertIn("environment may admit or reject", example)
        self.assertNotIn("agent_harbor_response_office", example)
        self.assertNotRegex(example, r"\b(?:DC|OBS|ST|INT)-")

    def test_case_coverage_rejects_deleted_bodies_and_uncovered_intents(self):
        example = (SKILL_ROOT / "agent-definition/references/complete-synthetic-example.md").read_text()
        self.assertEqual([], _case_coverage_errors(example))
        mutations = [
            re.sub(r"(^### `case\.[^\n]+\n).*?(?=^### |^## )", r"\1", example,
                   flags=re.MULTILINE | re.DOTALL),
            re.sub(r"^\| `case.withdrawal`.*\n", "", example, flags=re.MULTILINE),
            example.replace("| `decision.operational_notice` | `issue_operational_notice` |",
                            "| `decision.response_request` | `request_navigation_restriction` |"),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                self.assertTrue(_case_coverage_errors(mutation))


if __name__ == "__main__":
    unittest.main()
