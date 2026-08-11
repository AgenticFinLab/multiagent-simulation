#!/usr/bin/env python
"""EchoChamber Rag Simulation Runner.

Usage::

    python examples/EchoChamber/Rag/run_echochamber_rag.py \
        -c configs/EchoChamber/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="EchoChamber",
        variant="Rag",
        default_config="configs/EchoChamber/Rag/simulation.yml",
        phenomenon="Polarization by homophily - like-minded reinforcement drives extremity",
        load_env=True,
    )
