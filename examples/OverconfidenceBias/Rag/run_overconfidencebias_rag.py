#!/usr/bin/env python
"""OverconfidenceBias Rag Simulation Runner.

Usage::

    python examples/OverconfidenceBias/Rag/run_overconfidencebias_rag.py \
        -c configs/OverconfidenceBias/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="OverconfidenceBias",
        variant="Rag",
        default_config="configs/OverconfidenceBias/Rag/simulation.yml",
        phenomenon="Overconfidence bias causes traders to overestimate precision and trade excessively",
        load_env=True,
    )
