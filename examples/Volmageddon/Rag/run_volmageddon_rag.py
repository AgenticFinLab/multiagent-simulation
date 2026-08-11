#!/usr/bin/env python
"""Volmageddon Rag Simulation Runner.

Usage::

    python examples/Volmageddon/Rag/run_volmageddon_rag.py \
        -c configs/Volmageddon/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="Volmageddon",
        variant="Rag",
        default_config="configs/Volmageddon/Rag/simulation.yml",
        phenomenon="February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours",
        load_env=True,
    )
