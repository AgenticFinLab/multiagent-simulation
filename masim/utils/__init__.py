"""MASim Utilities Package

Provides utility modules:
- config:        YAML configuration loading with !include support; load_class(); expand_player_instances()
- ray_utils:     Ray cluster initialization and actor naming helpers
- topology:      NetworkX-based topology graph for message routing
- history:       Memory-efficient history buffer with disk persistence
- result_loader: Generic simulation result loading from record directories
"""

from masim.utils.config import (
    load_config,
    expand_player_instances,
    validate_config,
    build_connection_matrix,
    IncludeLoader,
    load_class,
)
from masim.utils.ray_utils import (
    ensure_ray,
    get_actor_name,
)
from masim.utils.result_loader import (
    SimulationResults,
    PlayerResults,
    TurnStore,
    MessageStore,
    BatchStore,
    TopologyView,
    load_results,
    load_simulation_data,  # deprecated alias
)
from masim.utils.history import (
    HistoryBuffer,
    create_history_buffer,
)

__all__ = [
    # Config utilities
    "load_config",
    "expand_player_instances",
    "validate_config",
    "build_connection_matrix",
    "IncludeLoader",
    "load_class",
    # Ray utilities
    "ensure_ray",
    "get_actor_name",
    # Result loader utilities
    "SimulationResults",
    "PlayerResults",
    "TurnStore",
    "MessageStore",
    "BatchStore",
    "TopologyView",
    "load_results",
    "load_simulation_data",
    # History utilities
    "HistoryBuffer",
    "create_history_buffer",
]
