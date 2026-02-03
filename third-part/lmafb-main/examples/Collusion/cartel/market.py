"""
Cartel market entrypoint (Terminal #2).
"""

import json
import logging

import ray

from dotenv import load_dotenv
from projinit.config import Config
from examples.Collusion.cartel.cartel_simulation import run_cartel_simulation


def main():
    """main function of market scenario"""
    load_dotenv()
    cfg = Config()
    cfg_dict = cfg.to_dict()
    ray.init(ignore_reinit_error=True)
    history = run_cartel_simulation(cfg_dict)
    result_path = cfg.logging.result_path
    with open(f"{result_path}/Simulations.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    logging.info("Saved results to: %s", result_path)


if __name__ == "__main__":
    main()
