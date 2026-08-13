from __future__ import annotations

import pytest

from support.case_registry import (
    canonical_case_population,
    public_case_id,
    public_case_partition,
)


CASES = [case for case in canonical_case_population() if public_case_partition(case) == "communication"]


@pytest.mark.parametrize("case", CASES, ids=public_case_id)
def test_communication_behavior_case(case: dict) -> None:
    assert case["status"] == "pass", case
