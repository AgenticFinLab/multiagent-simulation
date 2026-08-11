#!/usr/bin/env python
"""GFC2008 LLM Simulation Runner.

Usage::

    python examples/GFC2008/LLM/run_gfc2008_llm.py \
        -c configs/GFC2008/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GFC2008",
        variant="LLM",
        default_config="configs/GFC2008/LLM/simulation.yml",
        phenomenon="2007-2009 financial crisis - Housing bubble burst triggered global recession",
        load_env=True,
    )
