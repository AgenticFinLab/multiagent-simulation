#!/usr/bin/env python
"""EndowmentEffect Rag Simulation Runner.

Usage::

    python examples/EndowmentEffect/Rag/run_endowmenteffect_rag.py \
        -c configs/EndowmentEffect/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="EndowmentEffect",
        variant="Rag",
        default_config="configs/EndowmentEffect/Rag/simulation.yml",
        phenomenon="Ownership-induced loss aversion suppresses trade volume and inflates transaction prices",
        load_env=True,
    )
