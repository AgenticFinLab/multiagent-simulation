#!/usr/bin/env python
"""EchoChamber LLM Simulation Runner.

Usage::

    python examples/EchoChamber/LLM/run_echo_chamber_llm.py \
        -c configs/EchoChamber/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EchoChamber",
        variant="LLM",
        default_config="configs/EchoChamber/LLM/simulation.yml",
        phenomenon="Polarization by homophily - like-minded reinforcement drives extremity",
        load_env=True,
    )
