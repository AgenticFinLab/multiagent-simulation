"""MASim Configuration Loader

Provides YAML configuration loading with:
- !include tag support for file composition
- Path resolution relative to the config file
- Environment variable interpolation
- Validation helpers
- Logging configuration
- load_class(): Dynamic class loading from module path string

Usage:
    from masim.utils.config import load_config, setup_logging, load_class

    setup_logging()  # Configure logging with sensible defaults
    cfg = load_config("configs/Demo/simulation.yml")
    logger.info(cfg["players"])  # Loaded from players.yml via !include

    PlayerClass = load_class("mypackage.players:MyPlayer")
"""

import copy
import importlib
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


class IncludeLoader(yaml.SafeLoader):
    """
    Custom YAML loader that supports !include tag.

    The !include tag allows loading content from external YAML files.
    Paths are resolved relative to the including file's directory.

    Example:
        # In simulation.yml
        players: !include players.yml
        topology: !include topology.yml

        # Can also use subdirectories
        market_config: !include markets/equity.yml
    """

    def __init__(self, stream, base_path: Optional[Path] = None):
        """
        Initialize the loader.

        Args:
            stream: YAML content stream
            base_path: Base directory for resolving !include paths
        """
        super().__init__(stream)
        if base_path is None:
            if hasattr(stream, "name"):
                self._base_path = Path(stream.name).parent
            else:
                self._base_path = Path.cwd()
        else:
            self._base_path = base_path

    def include(self, node: yaml.Node) -> Any:
        """
        Handle !include tag.

        Args:
            node: YAML node containing the include path

        Returns:
            Loaded content from the included file
        """
        # Get the include path
        include_path = self.construct_scalar(node)

        # Resolve relative to the current file's directory
        full_path = self._base_path / include_path

        if not full_path.exists():
            raise FileNotFoundError(
                f"Include file not found: {full_path} "
                f"(referenced from {self._base_path})"
            )

        # Load the included file with the same loader
        with open(full_path, "r", encoding="utf-8") as f:
            return yaml.load(f, lambda stream: IncludeLoader(stream, full_path.parent))


# Register the !include constructor
IncludeLoader.add_constructor("!include", IncludeLoader.include)


def expand_player_instances(config: Dict[str, Any]) -> None:
    """
    Expand player templates into individual named instances.

    Reads the top-level `num_instances` field from each player block
    (between 'class' and 'config').  This field is REQUIRED for every player —
    omitting it raises KeyError so misconfigured files fail fast.
    For num_instances == 1 the original key is kept unchanged.
    For num_instances > 1 the base key is replaced by base_key_1 … base_key_N,
    each with its own identity and display name.
    topology['sources'] and topology['connections'] are rewritten in-place to
    use the expanded instance keys.

    Mutates config['players'] and config['topology'] in-place.
    Called automatically by load_config() after env-var interpolation.
    Raises KeyError if config is missing required 'players', 'topology', or
    any player block is missing 'num_instances'.

    Naming: base key "foo" with num_instances: 3  →  "foo_1", "foo_2", "foo_3"

    Args:
        config: Full loaded configuration dict (with 'players' and 'topology' keys).
    """
    players = config["players"]

    new_players: Dict[str, Any] = {}
    # Maps each base key to its list of expanded instance keys.
    # For num_instances == 1: identity mapping {base_key: [base_key]}.
    base_to_instances: Dict[str, List[str]] = {}

    for base_key, cfg in players.items():
        # num_instances is REQUIRED — no default, no .get(). Missing key = config error.
        if "num_instances" not in cfg:
            raise KeyError(
                f"Player '{base_key}' is missing required field 'num_instances'. "
                f"Set num_instances: 1 for a single instance."
            )
        n = int(cfg["num_instances"])
        if n <= 0:
            raise ValueError(
                f"Player '{base_key}' has invalid num_instances: {n}. Must be >= 1."
            )

        if n == 1:
            # No expansion — keep original key unchanged
            new_players[base_key] = cfg
            base_to_instances[base_key] = [base_key]
        else:
            instances = []
            for i in range(1, n + 1):
                inst_key = f"{base_key}_{i}"
                inst_cfg = copy.deepcopy(cfg)
                inst_cfg["config"]["identity"] = inst_key
                # top-level display name: "Disposition Investor 1", "Disposition Investor 2", …
                inst_cfg["name"] = f"{cfg['name']} {i}"
                new_players[inst_key] = inst_cfg
                instances.append(inst_key)
            base_to_instances[base_key] = instances

    config["players"] = new_players

    # Rewrite topology sources and connections to use fully-expanded instance keys
    topo = config["topology"]

    # Expand sources: each base key → its instance keys (identity if n == 1)
    new_sources: List[str] = []
    for s in topo["sources"]:
        new_sources.extend(base_to_instances[s] if s in base_to_instances else [s])
    topo["sources"] = new_sources

    # Expand connections: sender keys and all target lists
    new_conns: Dict[str, List[str]] = {}
    for sender, targets in topo["connections"].items():
        sender_instances = (
            base_to_instances[sender] if sender in base_to_instances else [sender]
        )
        expanded_targets: List[str] = []
        for t in targets:
            expanded_targets.extend(
                base_to_instances[t] if t in base_to_instances else [t]
            )
        for si in sender_instances:
            new_conns[si] = expanded_targets
    topo["connections"] = new_conns


def load_config(
    config_path: Union[str, Path],
    env_interpolate: bool = True,
) -> Dict[str, Any]:
    """
    Load a YAML configuration file with !include support.

    Args:
        config_path: Path to the main configuration file
        env_interpolate: Whether to interpolate environment variables

    Returns:
        Loaded configuration dictionary

    Example:
        cfg = load_config("configs/Demo/simulation.yml")

        # Access nested configs loaded via !include
        players = cfg["players"]
        topology = cfg["topology"]
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.load(f, lambda stream: IncludeLoader(stream, config_path.parent))

    if env_interpolate:
        config = _interpolate_env_vars(config)

    expand_player_instances(config)

    return config


def _interpolate_env_vars(obj: Any) -> Any:
    """
    Recursively interpolate environment variables in strings.

    Supports:
        ${VAR_NAME} - Required variable (raises if not set)
        ${VAR_NAME:-default} - Optional with default

    Args:
        obj: Object to process (dict, list, or scalar)

    Returns:
        Object with interpolated values
    """
    if isinstance(obj, dict):
        return {k: _interpolate_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_interpolate_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        return _interpolate_string(obj)
    else:
        return obj


def _interpolate_string(s: str) -> str:
    """
    Interpolate environment variables in a string.

    Args:
        s: String potentially containing ${VAR} patterns

    Returns:
        String with variables replaced
    """
    # Pattern: ${VAR_NAME} or ${VAR_NAME:-default}
    pattern = r"\$\{([^}:]+)(?::-([^}]*))?\}"

    def replace(match):
        var_name = match.group(1)
        default = match.group(2)

        if var_name in os.environ:
            return os.environ[var_name]
        elif default is not None:
            return default
        else:
            raise ValueError(
                f"Environment variable '{var_name}' is not set and no default provided"
            )

    return re.sub(pattern, replace, s)


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate a loaded configuration.

    Checks for:
        - Required top-level sections
        - Valid player configurations
        - Valid topology settings

    Args:
        config: Loaded configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    # Check required sections
    required_sections = ["setting", "players"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")

    # Validate players
    players = config["players"]
    if not players:
        raise ValueError("At least one player must be defined")

    for player_id, player_cfg in players.items():
        if "class" not in player_cfg:
            raise ValueError(f"Player '{player_id}' missing 'class' field")
        if "config" not in player_cfg:
            raise ValueError(f"Player '{player_id}' missing 'config' field")

    # Validate topology if present
    if "topology" in config:
        topology = config["topology"]
        if "type" not in topology:
            raise ValueError("Topology section must have 'type' field")
        topo_type = topology["type"]
        if topo_type not in ("star", "mesh", "custom"):
            raise ValueError(f"Invalid topology type: {topo_type}")

        if topo_type == "custom":
            if "connections" not in topology:
                raise ValueError("Custom topology must have 'connections' field")
            connections = topology["connections"]
            player_ids = set(players.keys())
            for source, targets in connections.items():
                if source not in player_ids:
                    raise ValueError(f"Unknown player in connections: {source}")
                for target in targets:
                    if target not in player_ids:
                        raise ValueError(f"Unknown target player: {target}")


def build_connection_matrix(
    config: Dict[str, Any],
) -> Dict[str, set]:
    """
    Build a connection matrix from topology configuration.

    Connections define who can send messages to whom.
    Only entities with explicit connections can communicate.

    Args:
        config: Full configuration dictionary

    Returns:
        Dictionary mapping source_id to set of allowed target_ids

    Example:
        matrix = build_connection_matrix(cfg)
        # matrix["market"] = {"investor_1", "investor_2", "investor_3"}
        # matrix["investor_1"] = {"market"}
    """
    if "topology" not in config:
        return {}
    topology = config["topology"]
    if "connections" not in topology:
        return {}
    connections_config = topology["connections"]

    # Build connection matrix from explicit config
    connections: Dict[str, set] = {}

    for source, targets in connections_config.items():
        if source not in connections:
            connections[source] = set()
        connections[source].update(targets)

    # Ensure all targets are also keys (even if they have no outbound connections)
    all_entities = set(connections.keys())
    for targets in connections.values():
        all_entities.update(targets)

    for entity in all_entities:
        if entity not in connections:
            connections[entity] = set()

    return connections


# =============================================================================
# Logging Configuration
# =============================================================================


def setup_logging(
    level: int = logging.INFO,
    format_string: str = "%(asctime)s [%(levelname)s] %(message)s",
    datefmt: str = "%H:%M:%S",
) -> None:
    """
    Configure logging with sensible defaults for MASim simulations.

    Call this once at the start of your application before any logging.

    Args:
        level: Logging level (default: logging.INFO)
        format_string: Log message format
        datefmt: Date/time format string

    Example:
        from masim.utils.config import setup_logging
        import logging

        setup_logging()
        logger = logging.getLogger("MyApp")
        logger.info("Application started")
    """
    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt=datefmt,
    )


def load_class(path: str) -> type:
    """
    Load a class from a module path string.

    Args:
        path: Class path in format "module.submodule:ClassName" or
              "module.submodule.ClassName"

    Returns:
        The loaded class

    Raises:
        ImportError: If module cannot be imported
        AttributeError: If class not found in module

    Example:
        PlayerClass = load_class("mypackage.players:MyPlayer")
        PlayerClass = load_class("mypackage.players.MyPlayer")
    """
    if ":" in path:
        module_path, cls_name = path.split(":", 1)
    else:
        module_path, cls_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, cls_name)


__all__ = [
    "load_config",
    "expand_player_instances",
    "validate_config",
    "build_connection_matrix",
    "IncludeLoader",
    "setup_logging",
    "load_class",
]
