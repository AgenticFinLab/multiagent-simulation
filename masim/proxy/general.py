"""General Proxy Implementations for MASim Framework.

This module provides concrete proxy implementations:
    - SendReceiveProxy: Info send/receive queue management for Persona
    - StorageProxy: State checkpoint/restore using BlockBasedStoreManager
    - ResourceProxy: MCP resource access
    - MonitoringProxy: Metrics and logging

Base classes and configs are in base.py; implementations are here.

Architecture (SendReceiveProxy):
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  Proxy strictly owned by Persona - manages Info send/receive queues   │
    │  Proxy CANNOT access Channel (owned by Simulator)                      │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  SEND FLOW (Player → Simulator):                                        │
    │    Player.decide() → outbound_messages                                 │
    │    Persona extracts → proxy.enqueue_info(info)                         │
    │    Simulator → persona.message_proxy.dequeue_infos()                   │
    │    Simulator → channel.encode() → dispatch via ray.remote              │
    │                                                                         │
    │  RECEIVE FLOW (Simulator → Player):                                     │
    │    Simulator → persona.message_proxy.handle_incoming(message)          │
    │    Proxy converts Message → Info and queues in receive_queue           │
    │    Persona → proxy.get_received_senders() → player.is_received_ready() │
    │    Persona → proxy.get_received_infos() → player.receive_info()        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
"""

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from masim.proxy.base import (
    # Types
    ProxyType,
    OwnerType,
    BaseProxy,
    ProxyResult,
    # Message types
    Message,
    MessageType,
    # Configs
    SendReceiveConfig,
    StorageConfig,
    ResourceConfig,
    MonitoringConfig,
)
from masim.player.base import Info
from masim.utils.history import HistoryBuffer
from lmbase.utils.tools import BlockBasedStoreManager

if TYPE_CHECKING:
    pass


# =============================================================================
#                     BUILD MESSAGE HELPER
# =============================================================================


def build_message_from_info(
    info: "Info",
    sender_id: str,
    target_id: str,
    round_num: int = 0,
) -> Message:
    """
    Convert a player-layer Info unit to a proxy-layer Message.

    This is the ONLY place where Info → Message conversion happens.
    Called by Simulator in phase_dispatch after collecting outbounds.

    The Info payload is wrapped in a content envelope so the proxy-layer
    Message carries structured metadata alongside the raw content:
        payload = {"content": info.payload,
                   "content_type": info.content_type,
                   "extras": info.extras}

    On the receive side, SendReceiveProxy.handle_incoming() unpacks this
    envelope back into an Info unit for the target player.

    Args:
        info:       The Info unit produced by the sending Player
        sender_id:  Identity of the sending Persona
        target_id:  Identity of the receiving Persona
        round_num:  Current simulation round (stored in extras)

    Returns:
        Message ready for CommunicationChannel.encode_and_deliver()
    """
    payload = {
        "content": info.payload,
        "content_type": info.content_type,
        "extras": info.extras,
    }
    return Message(
        message_type=MessageType.PEER,
        sender_id=sender_id,
        recipient_id=target_id,
        payload=payload,
        timestamp=datetime.now().isoformat(),
        extras={"round_num": round_num},
    )


# =============================================================================
#                       COMMUNICATION PROXY
# =============================================================================


class SendReceiveProxy(BaseProxy):
    """
    Proxy for Info send/receive queue management - strictly owned by Persona.

    Architecture:
        Proxy owns Info queues but CANNOT access Channel (Simulator-owned).
        Simulator accesses proxy via persona.message_proxy.xxx().

    Core Methods:
        1. enqueue_info(info)        - Called by Persona to queue Info for dispatch
        2. dequeue_infos()           - Called by Simulator to collect all queued Info units
        3. handle_incoming(message)  - Called by Simulator to deliver incoming Message
        4. get_received_senders()    - Called by Persona to pass data to Player.is_received_ready()
        5. get_received_infos()      - Called by Persona to deliver Info units to Player

    Flow:
        SEND:    Player.decide() → Persona.enqueue_info() → Simulator.dequeue_infos()
        RECEIVE: Simulator.handle_incoming() → Persona checks player.is_received_ready()
                 → Persona.get_received_infos() → Player.receive_info()
    """

    def __init__(
        self,
        config: Optional[SendReceiveConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config or SendReceiveConfig(), owner)
        self.config: SendReceiveConfig = config or SendReceiveConfig()
        # Send queue: Info units waiting to be dispatched by Simulator
        self.send_queue: List[Info] = []
        # Receive queue: Info units waiting to be delivered to Player
        self.receive_queue: List[Info] = []

    async def initialize(self) -> None:
        self.is_initialized = True

    async def shutdown(self) -> None:
        self.send_queue.clear()
        self.receive_queue.clear()
        self.is_initialized = False

    # =========================================================================
    #                    SEND METHODS (Persona → Simulator)
    # =========================================================================

    def enqueue_info(self, info: "Info") -> None:
        """
        Queue an Info unit for later dispatch by Simulator.

        Called by Persona after extracting Info units from Player.

        Args:
            info: The Info unit (player-layer content) to queue for sending
        """
        self.send_queue.append(info)

    def dequeue_infos(self) -> List["Info"]:
        """
        Dequeue all Info units queued for dispatch.

        Called by Simulator via persona.message_proxy.dequeue_infos().
        Returns all queued Info units and clears the send queue.

        Returns:
            List of all queued Info units ready for channel encoding
        """
        result = self.send_queue.copy()
        self.send_queue.clear()
        return result

    # =========================================================================
    #                    RECEIVE METHODS (Simulator → Player)
    # =========================================================================

    def handle_incoming(self, message: Message) -> None:
        """
        Handle an incoming Message from Simulator.

        Called by Simulator via persona.message_proxy.handle_incoming().
        Converts Message → Info (populates sender_id + time_received) and queues.

        Args:
            message: The proxy-layer Message received from another player
        """
        info = Info(
            payload=message.payload["content"],
            content_type=message.payload["content_type"],
            extras=message.payload["extras"],
            sender_id=message.sender_id,
            time_received=datetime.now().isoformat(),
        )
        self.receive_queue.append(info)

    def get_received_infos(self) -> List["Info"]:
        """
        Get all received Info units for Player.

        Called by Persona to retrieve Info units and deliver to Player.
        Returns all queued Info units and clears the receive queue.

        Returns:
            List of all received Info units (sender_id populated)
        """
        result = self.receive_queue.copy()
        self.receive_queue.clear()
        return result

    def has_received_infos(self) -> bool:
        """
        Check if there are Info units waiting to be delivered to Player.

        Returns:
            True if receive_queue is not empty
        """
        return len(self.receive_queue) > 0

    def get_received_senders(self) -> set:
        """
        Get the set of sender IDs currently in the inbound queue.

        Called by Persona to pass inbound state to Player.is_received_ready().
        Proxy owns the DATA; Player owns the DECISION of whether that's enough.

        Returns:
            Set of sender_id strings for all queued inbound messages
        """
        return {info.sender_id for info in self.receive_queue}


# =============================================================================
#                          STORAGE PROXY
# =============================================================================


class StorageProxy(BaseProxy):
    """Proxy for state persistence using BlockBasedStoreManager."""

    def __init__(
        self,
        config: StorageConfig,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config, owner)
        self.config: StorageConfig = config
        self._message_stores: Dict[str, BlockBasedStoreManager] = {}
        self._turn_stores: Dict[str, BlockBasedStoreManager] = {}

    def _get_base_path(self, player_id: str) -> str:
        """Get base path for player storage: {record_path}/{player_id}"""
        return os.path.join(self.config.record_path, player_id)

    def _get_message_store(self, player_id: str) -> BlockBasedStoreManager:
        """Get or create message store for player."""
        if player_id not in self._message_stores:
            msg_dir = os.path.join(self._get_base_path(player_id), "messages")
            os.makedirs(msg_dir, exist_ok=True)
            self._message_stores[player_id] = BlockBasedStoreManager(
                folder=msg_dir,
                file_format="json",
                block_size=self.config.turn_block_size,
            )
        return self._message_stores[player_id]

    def _get_turn_store(self, player_id: str) -> BlockBasedStoreManager:
        """Get or create turn store for player."""
        if player_id not in self._turn_stores:
            turn_dir = os.path.join(self._get_base_path(player_id), "turns")
            os.makedirs(turn_dir, exist_ok=True)
            self._turn_stores[player_id] = BlockBasedStoreManager(
                folder=turn_dir,
                file_format="json",
                block_size=self.config.turn_block_size,
            )
        return self._turn_stores[player_id]

    def record_message(
        self, player_id: str, round_num: int, message: Any, direction: str
    ) -> None:
        """Record a message using BlockBasedStoreManager."""
        if not self.config.record_rounds:
            return

        serialized_message = (
            message.to_dict() if hasattr(message, "to_dict") else message
        )

        timestamp = datetime.now()
        record = {
            "round_num": round_num,
            "direction": direction,
            "timestamp": timestamp.isoformat(),
            "message": serialized_message,
        }
        # Format: msg_r{round}_{MMDDHHMMSS}
        # e.g., msg_r000001_0221143052
        savename = f"msg_r{round_num:06d}_{timestamp.strftime('%m%d%H%M%S')}"
        self._get_message_store(player_id).save(savename=savename, data=record)

    def record_turn_result(
        self, player_id: str, round_num: int, turn_result: Any
    ) -> None:
        """Record turn result using BlockBasedStoreManager."""
        if not self.config.record_rounds:
            return
        serialized_result = (
            turn_result.to_dict() if hasattr(turn_result, "to_dict") else turn_result
        )
        timestamp = datetime.now()
        record = {
            "round_num": round_num,
            "timestamp": timestamp.isoformat(),
            "turn_result": serialized_result,
        }
        # Format: turn_r{round}_{MMDDHHMMSS}
        # e.g., turn_r000001_0221143052
        savename = f"turn_r{round_num:06d}_{timestamp.strftime('%m%d%H%M%S')}"
        self._get_turn_store(player_id).save(savename=savename, data=record)

    async def initialize(self) -> None:
        self.is_initialized = True

    async def shutdown(self) -> None:
        for store in self._message_stores.values():
            store.flush()
        for store in self._turn_stores.values():
            store.flush()
        self.is_initialized = False


# =============================================================================
#                          RESOURCE PROXY
# =============================================================================


class ResourceProxy(BaseProxy):
    """Proxy for MCP connection management and resource access."""

    def __init__(
        self,
        config: Optional[ResourceConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config or ResourceConfig(), owner)
        self.config: ResourceConfig = config or ResourceConfig()
        self._connections: Dict[str, Any] = {}
        self._resource_cache: Dict[str, tuple] = {}

    async def initialize(self) -> None:
        for server_config in self.config.mcp_servers:
            server_name = server_config["name"]
            self._connections[server_name] = {
                "config": server_config,
                "connected": True,
            }
        self.is_initialized = True

    async def shutdown(self) -> None:
        self._connections.clear()
        self._resource_cache.clear()
        self.is_initialized = False

    async def fetch_resource(self, resource_uri: str) -> ProxyResult:
        """Fetch a resource via MCP protocol."""
        if self.config.enable_caching:
            cached = self._check_cache(resource_uri)
            if cached is not None:
                return ProxyResult.ok(cached)

        server_name, _ = self._parse_uri(resource_uri)

        if server_name not in self._connections:
            return ProxyResult.fail(
                "NOT_CONNECTED", f"Not connected to MCP server: {server_name}"
            )

        result = {
            "uri": resource_uri,
            "data": {},
            "timestamp": datetime.now().isoformat(),
        }

        if self.config.enable_caching:
            self._cache_result(resource_uri, result)

        return ProxyResult.ok(result)

    async def invoke_tool(
        self, tool_name: str, args: Dict[str, Any], server: Optional[str] = None
    ) -> ProxyResult:
        """Invoke an external tool via MCP."""
        target_server = server or (
            list(self._connections.keys())[0] if self._connections else None
        )
        if not target_server or target_server not in self._connections:
            return ProxyResult.fail("NO_SERVER", "No connected MCP server")

        result = {
            "tool": tool_name,
            "args": args,
            "result": {},
            "timestamp": datetime.now().isoformat(),
        }
        return ProxyResult.ok(result)

    async def list_available_resources(
        self, server: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available resources from connected servers."""
        servers = [server] if server else list(self._connections.keys())
        return [
            {"server": srv, "resources": []}
            for srv in servers
            if srv in self._connections
        ]

    async def connect(self, server_config: Dict[str, Any]) -> bool:
        """Connect to an MCP server."""
        server_name = server_config["name"]
        self._connections[server_name] = {"config": server_config, "connected": True}
        return True

    async def disconnect(self, server_name: str) -> bool:
        """Disconnect from an MCP server."""
        if server_name not in self._connections:
            return False
        del self._connections[server_name]
        return True

    def _parse_uri(self, uri: str) -> tuple:
        """Parse MCP URI into (server_name, resource_path)."""
        if not uri.startswith("mcp://"):
            raise ValueError(f"Invalid MCP URI format: {uri}")
        path = uri[6:]
        parts = path.split("/", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    def _check_cache(self, uri: str) -> Optional[Any]:
        """Check cache for a resource."""
        if uri in self._resource_cache:
            data, ts = self._resource_cache[uri]
            if time.time() - ts < self.config.cache_ttl_seconds:
                return data
            del self._resource_cache[uri]
        return None

    def _cache_result(self, uri: str, data: Any) -> None:
        """Cache a resource result."""
        self._resource_cache[uri] = (data, time.time())


# =============================================================================
#                        MONITORING PROXY
# =============================================================================


class MonitoringProxy(BaseProxy):
    """
    Proxy for metrics collection and structured logging.

    Uses HistoryBuffer for memory-efficient hot/cold storage:
    - Hot: Recent entries in memory (deque, fast access)
    - Cold: Historical entries on disk (BlockBasedStoreManager)

    ┌─────────────────────────────────────────────────────────────────────┐
    │  ┌─────────────────┐           ┌─────────────────────────────────┐  │
    │  │  Hot (deque)    │  overflow │   Cold (BlockBasedStoreManager) │  │
    │  │  maxlen=N       │ ───────►  │   (JSON blocks on disk)         │  │
    │  └─────────────────┘           └─────────────────────────────────┘  │
    │                                                                      │
    │  API:                                                                │
    │  - get_metrics()     → recent (hot only, fast)                      │
    │  - get_all_metrics() → complete history (hot + cold)                │
    └─────────────────────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        config: Optional[MonitoringConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config or MonitoringConfig(), owner)
        self.config: MonitoringConfig = config or MonitoringConfig()

        # Initialize HistoryBuffer storage (record_path must be set in config)
        entry_limit = self.config.monitor_hot_limit
        record_path = self.config.record_path

        metrics_dir = os.path.join(record_path, "metrics")
        events_dir = os.path.join(record_path, "events")
        self._metrics: HistoryBuffer = HistoryBuffer(
            folder=metrics_dir, entry_limit=entry_limit
        )
        self._events: HistoryBuffer = HistoryBuffer(
            folder=events_dir, entry_limit=entry_limit
        )

        self._timers: Dict[str, float] = {}

    async def initialize(self) -> None:
        self.is_initialized = True

    async def shutdown(self) -> None:
        self._metrics.flush()
        self._events.flush()
        self.is_initialized = False

    async def record_metric(
        self, name: str, value: Any, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric (fire-and-forget, never fails)."""
        self._metrics.append(
            {
                "name": name,
                "value": value,
                "tags": tags or {},
                "entity_id": self.owner_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def log_event(
        self, event_type: str, data: Dict[str, Any], level: str = "INFO"
    ) -> None:
        """Log a structured event (fire-and-forget, never fails)."""
        self._events.append(
            {
                "event_type": event_type,
                "data": data,
                "level": level,
                "entity_id": self.owner_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def start_timer(self, name: str) -> None:
        """Start a named timer for measuring operation duration."""
        self._timers[name] = time.time()

    async def stop_timer(self, name: str) -> float:
        """Stop a timer and return duration in milliseconds."""
        if name not in self._timers:
            return 0.0

        duration_ms = (time.time() - self._timers.pop(name)) * 1000
        await self.record_metric(f"timer_{name}", duration_ms, {"unit": "ms"})
        return duration_ms

    async def get_metrics(
        self, name_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recorded metrics (recent, from hot storage)."""
        result = list(self._metrics.hot)
        if name_filter:
            result = [m for m in result if m["name"].startswith(name_filter)]
        return result

    async def get_events(
        self, event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recorded events (recent, from hot storage)."""
        result = list(self._events.hot)
        if event_type:
            result = [e for e in result if e["event_type"] == event_type]
        return result

    async def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get ALL recorded metrics (hot + cold). Use sparingly."""
        return self._metrics.get_all()

    async def get_all_events(self) -> List[Dict[str, Any]]:
        """Get ALL recorded events (hot + cold). Use sparingly."""
        return self._events.get_all()


# =============================================================================
#                       CONVENIENCE FUNCTIONS
# =============================================================================


def create_default_proxies(
    owner: Optional[OwnerType] = None,
) -> Dict[ProxyType, BaseProxy]:
    """Create a complete set of proxies with default configurations."""
    return {
        ProxyType.COMMUNICATION: SendReceiveProxy(SendReceiveConfig(), owner),
        ProxyType.STORAGE: StorageProxy(StorageConfig(), owner),
        ProxyType.RESOURCE: ResourceProxy(ResourceConfig(), owner),
        ProxyType.OBSERVABILITY: MonitoringProxy(MonitoringConfig(), owner),
    }


def create_minimal_proxies(
    owner: Optional[OwnerType] = None,
) -> Dict[ProxyType, BaseProxy]:
    """Create a minimal proxy set with just storage and observability."""
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
    """Create a customized proxy set for a specific owner."""
    proxies = {}

    if include_communication:
        proxies[ProxyType.COMMUNICATION] = SendReceiveProxy(SendReceiveConfig(), owner)

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
    """Simplified StorageProxy with sensible defaults."""

    def __init__(self, owner: Optional[OwnerType] = None):
        config = StorageConfig(
            checkpoint_dir="checkpoints",
            record_path="records",
            record_rounds=True,
        )
        super().__init__(config, owner)


class SimpleMonitoringProxy(MonitoringProxy):
    """Simplified MonitoringProxy with sensible defaults."""

    def __init__(
        self,
        record_path: str = "EXPERIMENT/default/monitoring",
        owner: Optional[OwnerType] = None,
    ):
        config = MonitoringConfig(
            record_path=record_path,
            monitor_hot_limit=3,
        )
        super().__init__(config, owner)


# Re-export
__all__ = [
    # Proxy implementations
    "SendReceiveProxy",
    "StorageProxy",
    "ResourceProxy",
    "MonitoringProxy",
    # Convenience functions
    "create_default_proxies",
    "create_minimal_proxies",
    "create_proxies_for_owner",
    # Simplified wrappers
    "SimpleStorageProxy",
    "SimpleMonitoringProxy",
]
