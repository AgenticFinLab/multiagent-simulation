#!/usr/bin/env python
"""FlashCrash RAG Simulation Runner (thin shim).

Usage:
    python examples/FlashCrash/Rag/run_flash_crash_ragllm.py
    python examples/FlashCrash/Rag/run_flash_crash_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash",
        default_config="configs/FlashCrash/Rag/simulation.yml",
    )
