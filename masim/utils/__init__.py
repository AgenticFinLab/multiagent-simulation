"""MASim Utilities Package

Provides utility modules:
- config: YAML configuration loading with !include support
- topology: NetworkX-based topology graph for message routing
- history: Memory-efficient history buffer with disk persistence
- data_loader: Generic simulation data loading from record directories
"""

from masim.utils.config import (
    load_config,
    validate_config,
    build_connection_matrix,
    IncludeLoader,
)
from masim.utils.data_loader import (
    load_simulation_data,
    get_investor_quantities,
    get_investor_orders,
    get_investor_bids,
)
from masim.utils.history import (
    HistoryBuffer,
    create_history_buffer,
)

__all__ = [
    # Config utilities
    "load_config",
    "validate_config",
    "build_connection_matrix",
    "IncludeLoader",
    # Data loader utilities
    "load_simulation_data",
    "get_investor_quantities",
    "get_investor_orders",
    "get_investor_bids",
    # History utilities
    "HistoryBuffer",
    "create_history_buffer",
]
