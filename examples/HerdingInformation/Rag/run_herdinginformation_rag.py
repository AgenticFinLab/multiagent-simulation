#!/usr/bin/env python
"""HerdingInformation Rag Simulation Runner.

Usage::

    python examples/HerdingInformation/Rag/run_herdinginformation_rag.py \
        -c configs/HerdingInformation/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="HerdingInformation",
        variant="Rag",
        default_config="configs/HerdingInformation/Rag/simulation.yml",
        phenomenon="Information cascade - individuals ignore private signals and follow the crowd",
        load_env=True,
    )
