#!/usr/bin/env python
"""Flash Crash RuleLLM Simulation Analysis.

The RuleLLM variant embeds the deterministic Rule mechanism as text
instructions inside an LLM persona prompt (see
``examples/FlashCrash/RuleLLM/explain.md §4``). Per
``masim/skills/implement-simulation-skill/09-step5-to-10-review.md §7.2``,
RuleLLM analysis requires NO additional scenario-specific function — the
core metrics are identical to the Rule variant.

This module therefore simply re-exports ``Rule.analysis.main``. All
metrics from ``analysis-bases.md §2``, all 8 plots from §7, and the
standard output-file contract are produced by the underlying pipeline.

Usage:
    python examples/FlashCrash/RuleLLM/analysis.py \
        -c configs/FlashCrash/RuleLLM/simulation.yml
"""

from __future__ import annotations

from examples.FlashCrash.Rule.analysis import main


if __name__ == "__main__":
    main()


__all__ = ["main"]
