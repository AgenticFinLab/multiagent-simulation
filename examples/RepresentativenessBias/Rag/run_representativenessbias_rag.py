#!/usr/bin/env python
"""RepresentativenessBias Rag Simulation Runner.

Usage::

    python examples/RepresentativenessBias/Rag/run_representativenessbias_rag.py \
        -c configs/RepresentativenessBias/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="RepresentativenessBias",
        variant="Rag",
        default_config="configs/RepresentativenessBias/Rag/simulation.yml",
        phenomenon="Small-sample pattern matching causes overgeneralization of recent returns as regime shifts",
        load_env=True,
    )
