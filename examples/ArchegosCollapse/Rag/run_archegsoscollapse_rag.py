#!/usr/bin/env python
"""ArchegosCollapse Rag Simulation Runner.

Usage::

    python examples/ArchegosCollapse/Rag/run_archegsoscollapse_rag.py \
        -c configs/ArchegosCollapse/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ArchegosCollapse",
        variant="Rag",
        default_config="configs/ArchegosCollapse/Rag/simulation.yml",
        phenomenon="March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales",
        load_env=True,
    )
