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


if __name__ == "__main__":
    unittest.main()
