#!/usr/bin/env python
"""FramingEffect Rag Simulation Runner.

Usage::

    python examples/FramingEffect/Rag/run_framingeffect_rag.py \
        -c configs/FramingEffect/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FramingEffect",
        variant="Rag",
        default_config="configs/FramingEffect/Rag/simulation.yml",
        phenomenon="Gain/loss frames elicit asymmetric risk attitudes, generating bias-driven order flow",
        load_env=True,
    )
