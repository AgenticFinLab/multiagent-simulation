#!/usr/bin/env python
"""DotComBubble RuleLLM Simulation Runner

1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%

Usage:
    python examples/DotComBubble/RuleLLM/run_dotcombubble_rulellm.py -c configs/DotComBubble/RuleLLM/simulation.yml
"""

import argparse
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import sys

# ``python path/to/script.py`` puts the script's directory (not the repository
# root) first on sys.path.  Prefer this checkout over an older installed masim.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
import ray

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


logger = logging.getLogger("dotcombubble.rulellm.runner")


def _use_fresh_output_dirs(yaml_config: dict) -> Path:
    """Isolate a run from persisted rounds so smoke runs really execute."""
    run_root = Path("EXPERIMENT/DotComBubble/RuleLLM/runs") / datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )
    records = str(run_root / "records")

    yaml_config["setting"]["record_path"] = records
    yaml_config["communication"]["storage_path"] = str(run_root / "communication")
    for player in yaml_config["players"].values():
        player["config"]["extras"]["record_path"] = records
        proxy = player["persona"]["proxy"]
        proxy["storage"]["record_path"] = records
        proxy["storage"]["checkpoint_dir"] = str(run_root / "checkpoints")
        proxy["monitoring"]["record_path"] = str(run_root / "monitoring")

    return run_root


async def main():
    load_dotenv()
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run DotComBubble RuleLLM Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/DotComBubble/RuleLLM/simulation.yml",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        help="Override total_rounds for a short smoke run.",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Write to a new run directory instead of resuming existing records.",
    )
    parser.add_argument(
        "--ray-retries",
        type=int,
        default=5,
        help="Rebuild Ray and resume after a local Ray runtime failure (default: 5).",
    )
    args = parser.parse_args()
    if args.ray_retries < 0:
        parser.error("--ray-retries must be zero or greater")
    
    yaml_config = load_config(args.config)
    if args.rounds is not None:
        if args.rounds <= 0:
            parser.error("--rounds must be a positive integer")
        yaml_config["setting"]["total_rounds"] = args.rounds
    run_root = _use_fresh_output_dirs(yaml_config) if args.fresh else None
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("DotComBubble Simulation - RuleLLM Agents")
    print("=" * 70)
    print("Rounds:     %s" % config.setting["total_rounds"])
    if run_root is not None:
        print("Output:     %s" % run_root)
    print("=" * 70 + "\n")
    
    for attempt in range(args.ray_retries + 1):
        simulator = GeneralSimulator(config)
        try:
            await simulator.setup()
            await simulator.run()
            print("\n" + "=" * 70)
            print("Simulation Complete!")
            print("=" * 70)
            return
        except (ray.exceptions.ActorUnavailableError, ray.exceptions.RaySystemError) as exc:
            if attempt >= args.ray_retries:
                raise
            logger.warning(
                "Ray runtime failed (%s). Rebuilding the local cluster and "
                "resuming from completed records (retry %d/%d).",
                type(exc).__name__,
                attempt + 1,
                args.ray_retries,
            )
        finally:
            await simulator.shutdown()

        # Give Windows a moment to release Ray worker ports and process handles.
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
