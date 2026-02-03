"""
Cartel investors entrypoint (Terminal #1).
Starts all investors as detached Ray actors and keeps the process alive.
"""

import asyncio
import logging
from typing import Dict, Any

import ray

from dotenv import load_dotenv
from projinit.config import Config
from llmgt.proxy.investor_proxy import RayInvestorProxy
from llmgt.investor.base import BaseInvestor, BaseInvestorConfig
from llmgt.ray_general.ray_simulation import ensure_ray, load_class


async def _keep_alive():
    """must keep alive"""
    while True:
        await asyncio.sleep(3600)


def main():
    """the main function of investor scenario"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    load_dotenv()
    cfg = Config()
    cfg_dict = cfg.to_dict()
    market_block: Dict[str, Any] = cfg_dict["model"]["market"]
    ray_opts = market_block.get("ray", {}) or {}
    ensure_ray(ray_opts)
    ray.init(ignore_reinit_error=True)

    actor_prefix = cfg_dict.get("model", {}).get("actor_prefix", "cartel_agent")

    investors_block: Dict[str, Dict[str, Any]] = market_block["investors"]
    env_overrides = (market_block.get("extras", {}) or {}).get(
        "env_overrides",
        cfg_dict.get("extras", {}) or {},
    )
    global_prompt = cfg_dict.get("model", {}).get("system_prompt")

    started = []
    for inv_id, inv_cfg in investors_block.items():
        if inv_id == "_template":
            continue

        investor_class = load_class(inv_cfg["class"])
        assert issubclass(
            investor_class, BaseInvestor
        ), f"{investor_class} must subclass BaseInvestor"

        inv_cfg_raw = inv_cfg.get("config") or {}
        if "system_prompt" not in inv_cfg_raw and global_prompt:
            inv_cfg_raw["system_prompt"] = global_prompt

        inv_obj = investor_class(
            BaseInvestorConfig(investor_id=inv_id, extras=inv_cfg_raw)
        )

        RayInvestorProxy.options(
            name=f"{actor_prefix}::{inv_id}",
            lifetime="detached",
        ).remote(inv_obj, env_overrides=env_overrides)

        started.append(inv_id)

    print(f"[investors] detached actors started: {started}")
    print("Holding process for detached actors. Press Ctrl+C to exit.")
    try:
        asyncio.run(_keep_alive())
    except KeyboardInterrupt:
        logging.info("Investor process interrupted; exiting.")


if __name__ == "__main__":
    main()
