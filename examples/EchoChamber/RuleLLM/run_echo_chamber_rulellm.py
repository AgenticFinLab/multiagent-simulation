#!/usr/bin/env python
"""EchoChamber RuleLLM Simulation Runner.

Usage::

    python examples/EchoChamber/RuleLLM/run_echo_chamber_rulellm.py \
        -c configs/EchoChamber/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EchoChamber",
        variant="RuleLLM",
        default_config="configs/EchoChamber/RuleLLM/simulation.yml",
        phenomenon="Polarization by homophily - like-minded reinforcement drives extremity",
        load_env=True,
    )
