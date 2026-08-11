#!/usr/bin/env python
"""EchoChamber Rule-Based Simulation Runner.

Usage::

    python examples/EchoChamber/Rule/run_echo_chamber.py \
        -c configs/EchoChamber/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="EchoChamber",
        variant="Rule-Based",
        default_config="configs/EchoChamber/Rule/simulation.yml",
        phenomenon="Polarization by homophily - like-minded reinforcement drives extremity",
        load_env=False,
    )
