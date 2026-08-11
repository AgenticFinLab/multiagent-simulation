#!/usr/bin/env python
"""BlackMonday1987 Rag Simulation Runner.

Usage::

    python examples/BlackMonday1987/Rag/run_blackmonday1987_rag.py \
        -c configs/BlackMonday1987/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="BlackMonday1987",
        variant="Rag",
        default_config="configs/BlackMonday1987/Rag/simulation.yml",
        phenomenon="October 19, 1987 stock market crash - Dow fell 22.6% in one day",
        load_env=True,
    )
