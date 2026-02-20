"""
General Proxy Implementations for MASim Framework.

This module provides convenience functions and simplified proxy creation.
For detailed proxy implementations and documentation, see base.py.

The proxy system follows the micro-proxy pattern:
    - CommunicationProxy: Message routing (send, broadcast, receive)
    - StorageProxy: State checkpoint/restore
    - ResourceProxy: MCP resource access
    - MonitoringProxy: Metrics and logging

Usage:
------
    # Create all proxies with defaults
    proxies = create_default_proxies()

    # Create proxies for a specific owner
    proxies = create_proxies_for_owner(player)

    # Create a minimal proxy set (just storage and observability)
    proxies = create_minimal_proxies()
"""

from typing import Dict, Optional, TYPE_CHECKING

from masim.proxy.base import (
    # Types
    ProxyType,
    ProxyConfig,
    OwnerType,
    BaseProxy,
    # Proxies and Configs
    CommunicationConfig,
    CommunicationProxy,
    StorageConfig,
    StorageProxy,
    ResourceConfig,
    ResourceProxy,
    MonitoringConfig,
    MonitoringProxy,
)

if TYPE_CHECKING:
    pass


# =============================================================================
#                       CONVENIENCE FUNCTIONS
# =============================================================================


def create_default_proxies(
    owner: Optional[OwnerType] = None,
) -> Dict[ProxyType, BaseProxy]:
    """
    Create a complete set of proxies with default configurations.

    This is the simplest way to get a fully-functional proxy set.
    All proxies use in-memory backends suitable for development/testing.

    Args:
        owner: Optional owner entity to bind proxies to

    Returns:
        Dictionary mapping ProxyType to proxy instance

    Example:
        proxies = create_default_proxies()
        comm_proxy = proxies[ProxyType.COMMUNICATION]
        storage_proxy = proxies[ProxyType.STORAGE]
    """
    return {
        ProxyType.COMMUNICATION: CommunicationProxy(CommunicationConfig(), owner),
        ProxyType.STORAGE: StorageProxy(StorageConfig(), owner),
        ProxyType.RESOURCE: ResourceProxy(ResourceConfig(), owner),
        ProxyType.OBSERVABILITY: MonitoringProxy(MonitoringConfig(), owner),
    }


def create_minimal_proxies(
    owner: Optional[OwnerType] = None,
) -> Dict[ProxyType, BaseProxy]:
    """
    Create a minimal proxy set with just storage and observability.

    Useful for simpler scenarios where communication and external
    resources are not needed.

    Args:
        owner: Optional owner entity to bind proxies to

    Returns:
        Dictionary with STORAGE and OBSERVABILITY proxies
    """
    return {
        ProxyType.STORAGE: StorageProxy(StorageConfig(), owner),
        ProxyType.OBSERVABILITY: MonitoringProxy(MonitoringConfig(), owner),
    }


def create_proxies_for_owner(
    owner: OwnerType,
    include_communication: bool = True,
    include_storage: bool = True,
    include_resource: bool = True,
    include_monitoring: bool = True,
) -> Dict[ProxyType, BaseProxy]:
    """
    Create a customized proxy set for a specific owner.

    Args:
        owner: The owner entity (Player)
        include_communication: Include CommunicationProxy
        include_storage: Include StorageProxy
        include_resource: Include ResourceProxy
        include_monitoring: Include MonitoringProxy

    Returns:
        Dictionary mapping ProxyType to proxy instance
    """
    proxies = {}

    if include_communication:
        proxies[ProxyType.COMMUNICATION] = CommunicationProxy(
            CommunicationConfig(), owner
        )

    if include_storage:
        proxies[ProxyType.STORAGE] = StorageProxy(StorageConfig(), owner)

    if include_resource:
        proxies[ProxyType.RESOURCE] = ResourceProxy(ResourceConfig(), owner)

    if include_monitoring:
        proxies[ProxyType.OBSERVABILITY] = MonitoringProxy(MonitoringConfig(), owner)

    return proxies


# =============================================================================
#                      SIMPLIFIED PROXY WRAPPERS
# =============================================================================


class SimpleStorageProxy(StorageProxy):
    """
    Simplified StorageProxy with sensible defaults.

    Uses in-memory storage with default configuration.
    Ideal for development and testing.
    """

    def __init__(self, owner: Optional[OwnerType] = None):
        """
        Initialize with default in-memory configuration.

        Args:
            owner: Optional owner entity
        """
        config = StorageConfig(
            checkpoint_dir="checkpoints",
            result_path="results",
            record_rounds=True,
        )
        super().__init__(config, owner)


class SimpleMonitoringProxy(MonitoringProxy):
    """
    Simplified MonitoringProxy with sensible defaults.

    Uses in-memory storage for metrics and events.
    Ideal for development and testing.
    """

    def __init__(self, owner: Optional[OwnerType] = None):
        """
        Initialize with default configuration.

        Args:
            owner: Optional owner entity
        """
        config = MonitoringConfig(
            metrics_backend="memory",
            logging_backend="structured",
            enable_tracing=False,
            log_level="INFO",
        )
        super().__init__(config, owner)


# Re-export from base for completeness
__all__ = [
    # Convenience functions
    "create_default_proxies",
    "create_minimal_proxies",
    "create_proxies_for_owner",
    # Simplified wrappers
    "SimpleStorageProxy",
    "SimpleMonitoringProxy",
    # Re-export
    "BaseProxy",
]
