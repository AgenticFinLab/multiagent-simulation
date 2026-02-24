"""MASim Utilities Package

Provides utility modules:
- config: YAML configuration loading with !include support
- topology: NetworkX-based topology graph for message routing
- history: Memory-efficient history buffer with disk persistence
"""

from masim.utils.config import (
    load_config,
    validate_config,
    build_connection_matrix,
    ConnectionValidator,
    IncludeLoader,
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
    "ConnectionValidator",
    "IncludeLoader",
    # History utilities
    "HistoryBuffer",
    "create_history_buffer",
]
