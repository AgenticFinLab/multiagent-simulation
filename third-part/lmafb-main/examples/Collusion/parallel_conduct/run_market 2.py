"""
Parallel-Conduct market entrypoint (Terminal #2).
Starts all markets as detached Ray actors and keeps the process alive.
"""

import asyncio
import logging

from dotenv import load_dotenv
from llmgt.utils import log_tag
from projinit.config import Config
from llmgt.ray_general.ray_simulation import launch_market_proxies


async def _keep_alive():
    """must keep alive"""
    while True:
        await asyncio.sleep(3600)


def main():
    """the main function of market scenario"""

    # Load the configuration file
    cfg = Config()
    cfg_dict = cfg.to_dict()

    # Set the environment via dotenv
    load_dotenv()

    # Launch the market proxies
    simulation_config = cfg_dict["model"]["simulation"]
    started = launch_market_proxies(
        actor_prefix="Parallel",
        ray_config=simulation_config["ray"],
        market_configs=simulation_config["markets"],
        investor_configs=simulation_config["investors"],
        env_overrides=simulation_config["extras"]["env_overrides"],
    )

    logging.info(
        "%s Launched #%d markets",
        log_tag.START_TAG,
        len(started)
    )

    logging.info(
        "%s Holding process for detached actors. Press Ctrl+C to exit.",
        log_tag.COMPLETE_TAG,
    )

    try:
        asyncio.run(_keep_alive())
    except KeyboardInterrupt:
        logging.info(
            "%s Market process interrupted; exiting.",
            log_tag.TERMINAL_TAG
        )


if __name__ == "__main__":
    main()
