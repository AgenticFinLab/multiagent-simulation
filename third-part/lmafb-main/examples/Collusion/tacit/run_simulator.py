"""
Tacit simulator entrypoint (Terminal #3).
Connects to existing investor and market actors to run simulation.
"""

import json
import logging

from dotenv import load_dotenv
from llmgt.utils import log_tag
from projinit.config import Config
from llmgt.ray_general.ray_simulation import Simulation


def main():
    """Main function to run simulation using existing actors."""

    # Load the configuration file
    cfg = Config()
    cfg_dict = cfg.to_dict()

    # Set the environment via dotenv
    load_dotenv()

    # Create simulation instance (it will handle Ray initialization via ensure_ray)
    simulation = Simulation(
        cfg=cfg_dict,
        actor_prefix="Tacit",
    )

    logging.info(
        "%s Starting simulation coordinator...",
        log_tag.START_TAG
    )

    logging.info(
        "%s Connecting to existing actors and running simulation...",
        log_tag.CONNECT_TAG,
    )

    history = simulation.run()

    # Save results
    result_path = cfg.logging.result_path
    result_file = f"{result_path}/demo_simulation_results.json"

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, default=str)

    logging.info(
        "%s Saved results to: %s",
        log_tag.SAVE_TAG,
        result_file
    )

    logging.info(
        "%s Simulation completed successfully!",
        log_tag.COMPLETE_TAG
    )


if __name__ == "__main__":
    main()
