from __future__ import annotations

from pathlib import Path

from h2epr.runtime.adapter import build_accepted_run_input


REPO_ROOT = Path(__file__).parents[4]
INPUT_ROOT = REPO_ROOT / "data/h2epr/development_samples_v1"
CASES = tuple(f"{profile}.seed.{seed}" for profile in ("low_stress", "balanced", "high_stress") for seed in (0, 1, 2))


def test_exact_nine_rows_have_stable_distinct_run_identity() -> None:
    first = [build_accepted_run_input(INPUT_ROOT, case).run_manifest for case in CASES]
    second = [build_accepted_run_input(INPUT_ROOT, case).run_manifest for case in CASES]
    assert first == second
    assert len({item["run_id"] for item in first}) == 9
    assert [item["case_id"] for item in first] == list(CASES)


def test_all_rows_retain_demo_contamination_identity() -> None:
    for case in CASES:
        manifest = build_accepted_run_input(INPUT_ROOT, case).run_manifest
        assert manifest["protocol_context"]["contamination_status"] == "full_draft_exposed"
        assert manifest["protocol_context"]["protocol_eligibility"] == "architecture_demo_only"
