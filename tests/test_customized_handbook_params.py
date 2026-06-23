"""Tests for ``masim.interface.customized.handbook_params``."""

from __future__ import annotations

from pathlib import Path

import pytest

from masim.interface.customized.handbook_params import (
    parse_parameters_file,
    parse_parameters_table,
)


PROFILE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "AGENT_POOL"
    / "ExtractedExampleInvestors"
    / "unique"
)


@pytest.mark.parametrize(
    "stem",
    [
        "NoiseTrader",
        "ValueFundamentalInvestor",
        "MomentumTrendTrader",
        "AnchoringBiasInvestor",
        "FramingEffectTrader",
    ],
)
def test_parses_known_handbooks(stem: str) -> None:
    """Each curated handbook produces a non-empty, well-formed table."""
    path = PROFILE_ROOT / f"{stem}.md"
    assert path.exists(), f"Missing handbook fixture: {path}"
    specs = parse_parameters_file(path)
    assert specs, f"No parameters parsed from {stem}.md"
    # Every spec must have a non-empty symbol.
    assert all(spec.symbol for spec in specs)
    # At least one numeric default in each handbook (sanity).
    assert any(spec.default_value is not None for spec in specs)


def test_enum_extraction() -> None:
    """`enum<a, b>` types yield distinct option lists."""
    md = """
## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `mode`    | `enum<alpha, beta, gamma>` | `alpha` | enum | high | Mode selector | demo | demo |
"""
    specs = parse_parameters_table(md)
    assert len(specs) == 1
    spec = specs[0]
    assert spec.kind == "enum"
    assert spec.enum_values == ["alpha", "beta", "gamma"]
    assert spec.default_value == "alpha"


def test_numeric_range_parse() -> None:
    md = """
## Parameters

| Parameter | Type    | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|---------|---------|-------------|-------------|-------------|--------|--------|
| `alpha`   | `float` | `0.5`   | `[0, 1]`    | high        | demo        | demo   | demo   |
| `beta`    | `int`   | `5`     | `[1, 250]`  | low         | demo        | demo   | demo   |
| `gamma`   | `float` | `1.0`   | `> 0`       | low         | demo        | demo   | demo   |
"""
    specs = parse_parameters_table(md)
    assert [s.symbol for s in specs] == ["alpha", "beta", "gamma"]
    assert specs[0].numeric_low == 0.0 and specs[0].numeric_high == 1.0
    assert specs[1].kind == "int" and specs[1].default_value == 5
    assert specs[2].numeric_low == 0.0 and specs[2].numeric_high is None


def test_missing_section_returns_empty() -> None:
    assert parse_parameters_table("# Just a title") == []
    assert parse_parameters_table("") == []
