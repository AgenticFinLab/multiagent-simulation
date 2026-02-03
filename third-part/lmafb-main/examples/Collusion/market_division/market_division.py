"""
This is a Market Division Simulation Runner.
Firms simulate non-competing behavior by dividing the market into regions or customer segments,
and pricing independently within their territories.
"""

import json
import logging

import ray

from dotenv import load_dotenv
from projinit.config import Config
from llmgt.api_utils import load_api_keys
from examples.Collusion.market_division.market_division_coordinator import MarketDivisionCoordinator


if __name__ == "__main__":

    load_dotenv()

    # Initialize configuration
    cfg = Config()
    cfg_dict = Config.to_dict()
    api_keys = load_api_keys()

    # Start Ray
    ray.init(ignore_reinit_error=True)

    # Create the coordinator and run the simulation
    coordinator = MarketDivisionCoordinator.remote(cfg=cfg_dict, api_keys=api_keys)
    results = ray.get(coordinator.run.remote())

    # Save results as JSON
    result_path = cfg.logging.result_path
    with open(f"{result_path}/Simulations.json", "w", encoding="utf-8") as f:
        json.dump(results, f)

    logging.info("Saved results to: %s", result_path)
