#!/usr/bin/env python
"""Volmageddon RuleLLM Simulation Runner.

Usage::

    python examples/Volmageddon/RuleLLM/run_volmageddon_rulellm.py \
        -c configs/Volmageddon/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="Volmageddon",
        variant="RuleLLM",
        default_config="configs/Volmageddon/RuleLLM/simulation.yml",
        phenomenon="February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours",
        load_env=True,
    )
