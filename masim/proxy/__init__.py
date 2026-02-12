"""MASim Proxy Module.

This module provides infrastructure abstraction through the micro-proxy pattern.
Proxies support weak references to owners and graceful degradation.

Base Classes and Types (base.py):
    - ObservableEntity: Protocol for proxy owners
    - BaseProxy: Abstract base class for all proxy types
    - ProxyType: Enum of proxy types
    - ProxyConfig: Base configuration for proxies
    - ProxyResult: Result wrapper for graceful degradation
    - Error types: ProxyError, ProxyNotInitializedError, ProxyOperationError

Proxy Implementations (base.py):
    - CommunicationProxy: Message routing and transmission
    - StorageProxy: State checkpoint and rollback
    - ResourceProxy: MCP resource access
    - ObservabilityProxy: Metrics and structured logging

Convenience Functions (general.py):
    - create_default_proxies(): Create all proxies with defaults
    - create_minimal_proxies(): Create just storage and observability
    - create_proxies_for_owner(): Create customized proxy set
    - SimpleStorageProxy: Simplified storage with defaults
    - SimpleObservabilityProxy: Simplified observability with defaults
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
    # Communication
    CommunicationConfig,
    CommunicationProxy,
    # Storage
    StorageConfig,
    Checkpoint,
    StorageProxy,
    # Resource
    ResourceConfig,
    ResourceProxy,
    # Observability
    ObservabilityConfig,
    ObservabilityProxy,
    # Factory
    ProxyFactory,
)

from masim.proxy.general import (
    # Convenience functions
    create_default_proxies,
    create_minimal_proxies,
    create_proxies_for_owner,
    # Simplified wrappers
    SimpleStorageProxy,
    SimpleObservabilityProxy,
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
    "Checkpoint",
    "StorageProxy",
    # Resource
    "ResourceConfig",
    "ResourceProxy",
    # Observability
    "ObservabilityConfig",
    "ObservabilityProxy",
    # Factory
    "ProxyFactory",
    # Convenience functions
    "create_default_proxies",
    "create_minimal_proxies",
    "create_proxies_for_owner",
    # Simplified wrappers
    "SimpleStorageProxy",
    "SimpleObservabilityProxy",
]
