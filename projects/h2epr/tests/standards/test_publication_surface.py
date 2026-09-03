from __future__ import annotations

from pathlib import Path
import re
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]

REQUIRED_PATHS = (
    "agents/agent-definition-template.md",
    "populations/population-model-template.md",
    "scenarios/scenario-definition-template.md",
    "scenarios/scenario-interface-closure-template.md",
    "scenarios/scenario-mechanism-template.md",
    "configs/scenario-configuration-template.md",
    "execution/backend-realization-template.md",
    "execution/execution-cycle-closeout-template.md",
    "templates/event-package/README.md",
    "templates/event-build-brief-template.md",
    "templates/experiment-plan.md",
    "templates/experiment-closeout.md",
    "templates/cross-event-analysis.md",
    "templates/phase-closeout-checklist.md",
    "backends/participant-decision-contract.md",
    "backends/backend-matrix.json",
    "events/current-events.json",
    "schemas/catalog.json",
    "src/h2epr/experiment.py",
    "src/h2epr/publication.py",
    "src/h2epr/repository.py",
    "EXPERIMENT_STANDARD.md",
    "experiments/README.md",
)


class PublicationSurfaceTests(unittest.TestCase):
    def test_required_standard_assets_exist(self) -> None:
        for relative in REQUIRED_PATHS:
            with self.subTest(path=relative):
                self.assertTrue((PROJECT_ROOT / relative).is_file())

    def test_local_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        paths = list(PROJECT_ROOT.rglob("*.md"))
        paths.extend(
            REPOSITORY_ROOT / relative
            for relative in (
                "README.md",
                "projects/README.md",
                "projects/H2EPR.md",
                "docs/structure.md",
            )
        )
        for path in sorted(set(paths)):
            text = path.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                with self.subTest(path=path.relative_to(REPOSITORY_ROOT), target=target):
                    self.assertTrue((path.parent / target).resolve().exists())


if __name__ == "__main__":
    unittest.main()
