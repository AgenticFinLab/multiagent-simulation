#!/usr/bin/env python
"""DotComBubble Rule-Based Simulation Runner

1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%

Usage:
    python -m examples.DotComBubble.Rule.run_dotcombubble \
        -c configs/DotComBubble/Rule/simulation.yml --steps 2 \
        --output-root EXPERIMENT/DotComBubble/Rule/smoke
"""

import argparse
import asyncio
from pathlib import Path

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def run_simulation(
    config_path: str,
    steps: int | None = None,
    output_root: str | None = None,
):
    """Run the configured Rule simulation and return its result batch."""
    yaml_config = load_config(config_path)
    if steps is not None:
        if steps < 1:
            raise ValueError("steps must be at least 1")
        yaml_config["setting"]["total_rounds"] = steps
    if output_root is not None:
        root = Path(output_root)
        record_path = str(root / "records")
        yaml_config["setting"]["record_path"] = record_path
        yaml_config["communication"]["storage_path"] = str(
            root / "communication"
        )
        yaml_config["players"]["market"]["config"]["extras"][
            "record_path"
        ] = record_path
        for player in yaml_config["players"].values():
            proxy = player["persona"]["proxy"]
            proxy["storage"]["record_path"] = record_path
            proxy["storage"]["checkpoint_dir"] = str(root / "checkpoints")
            proxy["monitoring"]["record_path"] = str(root / "monitoring")
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("DotComBubble Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: 1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%")
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 70 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
        return results
    finally:
        await simulator.shutdown()


def parse_args():
    """Parse command-line arguments without starting the simulator."""
    parser = argparse.ArgumentParser(
        description="Run DotComBubble Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/DotComBubble/Rule/simulation.yml",
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="Override total_rounds for a short smoke run",
    )
    parser.add_argument(
        "--output-root",
        help="Store records and messages in an isolated output directory",
    )
    return parser.parse_args()


if __name__ == "__main__":
    setup_logging()
    args = parse_args()
    asyncio.run(run_simulation(args.config, args.steps, args.output_root))
