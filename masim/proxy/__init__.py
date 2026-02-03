"""
MASim Proxy Module.

Exports proxy classes for infrastructure abstraction.
Proxies support weak references to owners and graceful degradation.
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
]
