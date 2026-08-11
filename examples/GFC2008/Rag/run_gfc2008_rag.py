#!/usr/bin/env python
"""GFC2008 Rag Simulation Runner.

Usage::

    python examples/GFC2008/Rag/run_gfc2008_rag.py \
        -c configs/GFC2008/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GFC2008",
        variant="Rag",
        default_config="configs/GFC2008/Rag/simulation.yml",
        phenomenon="2007-2009 financial crisis - Housing bubble burst triggered global recession",
        load_env=True,
    )
