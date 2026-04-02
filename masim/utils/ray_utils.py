"""Ray Cluster Utilities for MASim.

Provides helpers for Ray initialization and actor naming:
- ensure_ray():            Initialize Ray cluster; reconnect if namespace differs.
- get_actor_name():        Construct deterministic Ray actor names.
- _resolve_num_cpus():     Resolve CPU count from config or auto-detect.
- _resolve_object_store_memory(): Resolve Plasma store size from config or policy.

Usage:
    from masim.utils.ray_utils import ensure_ray, get_actor_name

    ensure_ray(ray_config)
    actor_name = get_actor_name(simulation_id, player_id)
"""

import logging
import math
import os
from typing import Any, Dict

import psutil
import ray


logger = logging.getLogger("masim.utils.ray")


# =============================================================================
# Internal Resolvers
# =============================================================================


def _resolve_num_cpus(cfg_value) -> int:
    """
    Resolve num_cpus from config value or auto-detect.

    Config accepts:
        null  → leave 1 CPU for OS, use rest for Ray
        int   → use exactly that many
        float → fraction of logical CPUs (e.g. 0.5 = half)
    """
    total = os.cpu_count() or 1
    if cfg_value is None:
        # Leave 1 CPU for OS/other processes
        return max(1, total - 1)
    if isinstance(cfg_value, float) and cfg_value < 1.0:
        return max(1, math.floor(total * cfg_value))
    return int(cfg_value)


def _resolve_object_store_memory(cfg_value) -> int:
    """
    Resolve Ray Plasma object store size from config value or policy.

    Sizing basis (code-derived for typical non-LLM simulations):
        Per round, these objects pass through the store:
          - Phase 2: N_players x TurnResult (~600 B each)
          - Phase 3 collect: N_players x pending_info list (~300 B each)
          - Phase 3 dispatch: N_messages x Message (~400 B each, JSON)
        Typical 7-player simulation: ~10 KB actual payload/round.
        Ray minimum allocation is 64 KB per object regardless of size.
        At ~26 objects/round x 64 KB = ~1.6 MB peak concurrent in-flight.
        All refs are freed after ray.get() within the same round phase.
        128 MB (default_max_gb=0.125) provides 80x headroom over peak.
        LLM simulations with large prompt payloads should raise max_gb.

    Config accepts:
        null              -> default policy: 15% of available RAM, capped at 128 MB
        int               -> exact bytes
        {fraction, max_gb} -> fraction of available RAM with GB ceiling
    """
    available = psutil.virtual_memory().available
    if cfg_value is None:
        # Default: 15% of available RAM, max 128 MB (sufficient for non-LLM simulations)
        return min(int(available * 0.15), 128 * 1024**2)
    if isinstance(cfg_value, int):
        return cfg_value
    if isinstance(cfg_value, dict):
        fraction = cfg_value["fraction"]
        max_bytes = int(cfg_value["max_gb"] * 1024**3)
        return min(int(available * fraction), max_bytes)
    return int(cfg_value)


# =============================================================================
# Public API
# =============================================================================


def ensure_ray(ray_config: Dict[str, Any]) -> None:
    """
    Initialize Ray cluster; reconnect if namespace differs.

    Args:
        ray_config: Ray configuration dict from YAML (ray.*)

    This function handles three scenarios:
    1. Ray not initialized → Initialize with config
    2. Ray initialized with same namespace → Do nothing
    3. Ray initialized with different namespace → Shutdown and reinitialize

    num_cpus and object_store_memory are resolved at runtime from current
    system conditions via _resolve_num_cpus() and _resolve_object_store_memory().
    """
    init_kwargs = {
        "namespace": ray_config["namespace"],
    }

    if "logging_level" in ray_config:
        level_str = ray_config["logging_level"]
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }
        init_kwargs["logging_level"] = level_map[level_str]

    if "address" in ray_config and ray_config["address"]:
        init_kwargs["address"] = ray_config["address"]

    # Resolve CPU count from current system state
    init_kwargs["num_cpus"] = _resolve_num_cpus(ray_config.get("num_cpus"))

    if ray_config.get("num_gpus") is not None:
        init_kwargs["num_gpus"] = ray_config["num_gpus"]

    # Resolve object store size from current available RAM
    init_kwargs["object_store_memory"] = _resolve_object_store_memory(
        ray_config.get("object_store_memory")
    )

    if "runtime_env" in ray_config and ray_config["runtime_env"]:
        init_kwargs["runtime_env"] = ray_config["runtime_env"]

    logger.info(
        "Ray init: num_cpus=%d, object_store_memory=%d MB",
        init_kwargs["num_cpus"],
        init_kwargs["object_store_memory"] // (1024**2),
    )

    if ray.is_initialized():
        current_ns = ray.get_runtime_context().namespace
        if current_ns == ray_config["namespace"]:
            return
        ray.shutdown()

    ray.init(**init_kwargs)


def get_actor_name(prefix: str, entity_id: str) -> str:
    """
    Construct a deterministic Ray actor name.

    Args:
        prefix: Actor name prefix (usually simulation_id)
        entity_id: Entity identifier (player_id)

    Returns:
        Actor name in format "{prefix}::{entity_id}"
    """
    return f"{prefix}::{entity_id}"


__all__ = [
    "ensure_ray",
    "get_actor_name",
]
