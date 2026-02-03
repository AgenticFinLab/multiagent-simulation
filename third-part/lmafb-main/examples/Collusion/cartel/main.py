"""
This is a Cartel Collusion Simulation Runner (Ray version).
Firms coordinate prices over multiple rounds, simulating the behavior of a price-fixing cartel.
"""

import json
import logging
import asyncio

import ray

from dotenv import load_dotenv, dotenv_values

from examples.Collusion.cartel.cartel_investor import CartelInvestor
from projinit.config import Config
from examples.Collusion.cartel.cartel_simulation import run_cartel_simulation
from llmgt.agent import initialize_common as _initialize_common_async


def _initialize_common_sync(cfg_payload: dict, rule_text: str):
    """Sync wrapper for the async agent initializer."""
    return asyncio.run(_initialize_common_async(cfg_payload, rule_text))


@ray.remote
def run_cartel_job(cfg_dict, rule_text, agents_raw, rounds_total):
    """
    Ray remote task to execute the cartel simulation using the Simulation framework.
    Uses distinct parameter names to avoid shadowing outer-scope variables.
    """
    investors = {
        aid: CartelInvestor(agent_obj=obj, investor_id=aid)
        for aid, obj in agents_raw.items()
    }
    return run_cartel_simulation(
        cfg_dict=cfg_dict,
        rule=rule_text,
        investors=investors,
        rounds=rounds_total,  # 或 total_rounds=... 看你的旧签名
    )


def main():
    """main function to run the cartel simulation"""
    load_dotenv(override=True)
    dotenv_values(".env")

    cfg_obj = Config()
    cfg_dict = cfg_obj.to_dict()

    default_rule_text = "Set a fair product price for this round that avoids competition and reflects market stability."

    agents_raw, _wf, _ckpt, _prev_prices, rounds_total, _history, rule_from_init = (
        _initialize_common_sync(cfg_dict, default_rule_text)
    )
    rule_text = rule_from_init or default_rule_text

    ray.init(ignore_reinit_error=True)
    try:
        results = ray.get(
            run_cartel_job.remote(cfg_dict, rule_text, agents_raw, rounds_total)
        )
    finally:
        ray.shutdown()

    result_path = cfg_obj.logging.result_path
    with open(f"{result_path}/Simulations.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logging.info("Saved results to: %s", result_path)


if __name__ == "__main__":
    main()
