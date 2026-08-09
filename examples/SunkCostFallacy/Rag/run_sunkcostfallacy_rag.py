#!/usr/bin/env python
"""SunkCostFallacy Rag Simulation Runner.

Usage::

    python examples/SunkCostFallacy/Rag/run_sunkcostfallacy_rag.py \
        -c configs/SunkCostFallacy/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SunkCostFallacy",
        variant="Rag",
        default_config="configs/SunkCostFallacy/Rag/simulation.yml",
        phenomenon="Investors irrationally hold losing positions to justify prior investment",
        load_env=True,
    )
