"""
This is a Bid Rigging Simulation Runner.
Agents simulate strategic bidding behavior, where firms may coordinate to determine bid winners across multiple rounds.
"""

import json
import logging

import ray

from dotenv import load_dotenv
from projinit.config import Config
from llmgt.api_utils import load_api_keys
from examples.Collusion.bid_rigging.bid_rigging_coordinator import BidRiggingCoordinator


if __name__ == "__main__":

    load_dotenv()

    # Initialize configuration
    cfg = Config()
    cfg_dict = Config.to_dict()
    api_keys = load_api_keys()

    # Start Ray
    ray.init(ignore_reinit_error=True)

    # Create the coordinator and run the simulation
    coordinator = BidRiggingCoordinator.remote(cfg=cfg_dict, api_keys=api_keys)
    results = ray.get(coordinator.run.remote())

    # Save results as JSON
    result_path = cfg.logging.result_path
    with open(f"{result_path}/Simulations.json", "w", encoding="utf-8") as f:
        json.dump(results, f)

    logging.info("Saved results to: %s", result_path)
