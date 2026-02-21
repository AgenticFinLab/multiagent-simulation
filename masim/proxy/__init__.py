"""MASim Proxy Module.

This module provides infrastructure abstraction through the micro-proxy pattern.
Proxies support weak references to owners and graceful degradation.

Base Classes and Types (base.py):
    - ObservableEntity: Protocol for proxy owners
    - BaseProxy: Abstract base class for all proxy types
    - ProxyType: Enum of proxy types
    - ProxyConfig: Base configuration for proxies
    - ProxyResult: Result wrapper for graceful degradation
    - Config dataclasses: CommunicationConfig, StorageConfig, ResourceConfig, MonitoringConfig
    - Error types: ProxyError, ProxyNotInitializedError, ProxyOperationError

Proxy Implementations (general.py):
    - CommunicationProxy: Message routing and transmission
    - StorageProxy: State checkpoint and rollback
    - ResourceProxy: MCP resource access
    - MonitoringProxy: Metrics and structured logging

Convenience Functions (general.py):
    - create_default_proxies(): Create all proxies with defaults
    - create_minimal_proxies(): Create just storage and monitoring
    - create_proxies_for_owner(): Create customized proxy set
    - SimpleStorageProxy: Simplified storage with defaults
    - SimpleMonitoringProxy: Simplified monitoring with defaults
"""

from masim.proxy.base import (
    # Observable Entity Protocol
    ObservableEntity,
    # Error types
    ProxyError,
    ProxyNotInitializedError,
    ProxyOperationError,
    ProxyResult,
    # Base proxy types
    ProxyType,
    ProxyConfig,
    BaseProxy,
    OwnerType,
    # Config dataclasses
    CommunicationConfig,
    StorageConfig,
    ResourceConfig,
    MonitoringConfig,
)

from masim.proxy.general import (
    # Proxy implementations
    CommunicationProxy,
    StorageProxy,
    ResourceProxy,
    MonitoringProxy,
    # Convenience functions
    create_default_proxies,
    create_minimal_proxies,
    create_proxies_for_owner,
    # Simplified wrappers
    SimpleStorageProxy,
    SimpleMonitoringProxy,
)

__all__ = [
    # Observable Entity Protocol
    "ObservableEntity",
    # Error types
    "ProxyError",
    "ProxyNotInitializedError",
    "ProxyOperationError",
    "ProxyResult",
    # Base proxy types
    "ProxyType",
    "ProxyConfig",
    "BaseProxy",
    "OwnerType",
    # Communication
    "CommunicationConfig",
    "CommunicationProxy",
    # Storage
    "StorageConfig",
    "StorageProxy",
    # Resource
    "ResourceConfig",
    "ResourceProxy",
    # Monitoring
    "MonitoringConfig",
    "MonitoringProxy",
    # Convenience functions
    "create_default_proxies",
    "create_minimal_proxies",
    "create_proxies_for_owner",
    # Simplified wrappers
    "SimpleStorageProxy",
    "SimpleMonitoringProxy",
]
