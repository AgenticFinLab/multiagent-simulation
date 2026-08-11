#!/usr/bin/env python
"""LTCMCollapse Rag Simulation Runner.

Usage::

    python examples/LTCMCollapse/Rag/run_ltcmcollapse_rag.py \
        -c configs/LTCMCollapse/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LTCMCollapse",
        variant="Rag",
        default_config="configs/LTCMCollapse/Rag/simulation.yml",
        phenomenon="August-September 1998 LTCM crisis - Russian default triggered liquidity crisis",
        load_env=True,
    )
