#!/usr/bin/env python
"""CurrencyCrisis Rag Simulation Runner.

Usage::

    python examples/CurrencyCrisis/Rag/run_currencycrisis_rag.py \
        -c configs/CurrencyCrisis/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CurrencyCrisis",
        variant="Rag",
        default_config="configs/CurrencyCrisis/Rag/simulation.yml",
        phenomenon="Self-fulfilling speculative attacks deplete central-bank reserves and force peg abandonment",
        load_env=True,
    )
