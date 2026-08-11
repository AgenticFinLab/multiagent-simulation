#!/usr/bin/env python
"""LUNACollapse Rag Simulation Runner.

Usage::

    python examples/LUNACollapse/Rag/run_lunacollapse_rag.py \
        -c configs/LUNACollapse/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LUNACollapse",
        variant="Rag",
        default_config="configs/LUNACollapse/Rag/simulation.yml",
        phenomenon="May 2022 Terra/LUNA crash - $40B wiped out in algorithmic stablecoin death spiral",
        load_env=True,
    )
