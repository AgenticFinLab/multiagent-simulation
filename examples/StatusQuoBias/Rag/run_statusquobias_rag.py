#!/usr/bin/env python
"""StatusQuoBias Rag Simulation Runner.

Usage::

    python examples/StatusQuoBias/Rag/run_statusquobias_rag.py \
        -c configs/StatusQuoBias/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="StatusQuoBias",
        variant="Rag",
        default_config="configs/StatusQuoBias/Rag/simulation.yml",
        phenomenon="Psychological inertia suppresses portfolio rebalancing, causing persistent mispricing",
        load_env=True,
    )
