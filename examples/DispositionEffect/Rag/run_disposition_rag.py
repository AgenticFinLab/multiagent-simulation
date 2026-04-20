"""DispositionEffect Rag - RAG-augmented simulation runner."""

import sys
import asyncio
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from masim.interface.simulation_runner import run_simulation_with_progress


async def main():
    """Run DispositionEffect Rag simulation."""
    if len(sys.argv) >= 3 and sys.argv[1] == "-c":
        config_path = sys.argv[2]
    else:
        config_path = "configs/DispositionEffect/Rag/simulation.yml"

    print(f"Starting DispositionEffect Rag simulation...")
    print(f"Config: {config_path}")
    print("-" * 50)

    async for status in run_simulation_with_progress(config_path):
        print(
            f"Round {status.round_num}/{status.total_rounds}: "
            f"{status.progress_pct:.1f}% - {status.message}"
        )

    print("-" * 50)
    print("Simulation complete!")
    print(f"Results saved to: EXPERIMENT/DispositionEffect/Rag/")


if __name__ == "__main__":
    asyncio.run(main())
