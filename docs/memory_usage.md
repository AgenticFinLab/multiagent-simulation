# MASim Memory Usage Analysis

This document provides a comprehensive analysis of memory allocation, usage patterns, and optimization strategies in the MASim framework.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Memory Components](#2-core-memory-components)
3. [Memory Growth Classification](#3-memory-growth-classification)
4. [Component-Level Analysis](#4-component-level-analysis)
5. [Memory Estimation Model](#5-memory-estimation-model)
6. [Risk Assessment](#6-risk-assessment)
7. [Optimization Recommendations](#7-optimization-recommendations)

---

## 1. Architecture Overview

### 1.1 Memory Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MEMORY ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Simulator (Single Instance, Driver Process)                                │
│     ├── history: HistoryBuffer              [Round Results]                 │
│     ├── player_persona_handles: Dict        [Ray Actor References]          │
│     ├── topology: TopologyGraph             [Connection Graph]              │
│     └── communication: CommunicationChannel [Message Recording]             │
│                                                                              │
│  PlayerPersona × N (Ray Actors, Separate Processes)                         │
│     ├── storage: StorageProxy               [Turn/Message Recording]        │
│     ├── monitoring: MonitoringProxy         [Metrics/Events]                │
│     ├── communication: SendReceiveProxy     🚨 [Message Queue]              │
│     ├── resource: ResourceProxy             [MCP Cache]                     │
│     └── player: BasePlayer                  [Domain State]                  │
│           ├── inbounds: List[Inbound]       [Received Messages]             │
│           ├── pending_outbounds: List       [Outgoing Messages]             │
│           └── state: PlayerState            [Execution Metrics]             │
│                 └── custom_state: Dict      🚨 [User-Defined Data]          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Storage Strategy: Hot/Cold Architecture

MASim employs a two-tier storage strategy:

| Tier     | Location       | Access Time | Capacity  | Purpose                      |
|----------|----------------|-------------|-----------|------------------------------|
| **Hot**  | Memory (deque) | O(1)        | Bounded   | Recent data, fast access     |
| **Cold** | Disk (JSON)    | O(n)        | Unbounded | Historical data, persistence |

```
┌─────────────────┐  overflow   ┌─────────────────────────────┐
│   Hot (deque)   │ ─────────►  │  Cold (BlockBasedStoreManager) │
│  maxlen=N       │             │  (JSON blocks on disk)      │
└─────────────────┘             └─────────────────────────────┘
```

---

## 2. Core Memory Components

### 2.1 HistoryBuffer

**Source**: `masim/utils/history.py`

The primary memory management utility for bounded in-memory storage with automatic disk persistence.

```python
class HistoryBuffer:
    hot: deque              # maxlen=entry_limit, O(1) access
    cold_store: BlockBasedStoreManager  # Disk-based, unbounded
    _pending_cold: List     # Batch buffer before flush
```

**Memory Characteristics**:
- Hot storage: Fixed size (`entry_limit` items)
- Pending buffer: At most `block_size` items before flush
- Cold storage: Zero memory footprint (disk-only)

**Configuration Parameters**:
| Parameter     | Default | Description            |
|---------------|---------|------------------------|
| `entry_limit` | 100     | Max items in hot deque |
| `block_size`  | 50      | Items per disk block   |

### 2.2 BlockBasedStoreManager

**Source**: `lmbase.utils.tools.BlockBasedStoreManager`

External utility for batched disk persistence.

```python
BlockBasedStoreManager(
    folder: str,          # Storage directory
    file_format: str,     # "json" or "pickle"
    block_size: int       # Items per file
)
```

**Memory Footprint**:
- Internal buffer: Up to `block_size` items
- Flushed on: buffer full OR explicit `flush()` call

### 2.3 Proxy Classes

#### StorageProxy
**Source**: `masim/proxy/general.py`

```python
class StorageProxy:
    _message_stores: Dict[str, BlockBasedStoreManager]  # Per-player
    _turn_stores: Dict[str, BlockBasedStoreManager]     # Per-player
```

**Memory per Player**:
- Message buffer: `block_size` × message_size
- Turn buffer: `block_size` × turn_result_size

#### MonitoringProxy
**Source**: `masim/proxy/general.py`

```python
class MonitoringProxy:
    _metrics: HistoryBuffer   # entry_limit=100
    _events: HistoryBuffer    # entry_limit=100
    _timers: Dict[str, float] # Active timers
```

**Memory Footprint**:
- Metrics hot storage: 100 × ~200 bytes = ~20KB
- Events hot storage: 100 × ~200 bytes = ~20KB
- Timers: Negligible (typically < 10 active)

#### SendReceiveProxy
**Source**: `masim/proxy/general.py`

```python
class SendReceiveProxy:
    pending_messages: Dict[str, List[Message]]  # Per-recipient queue
    subscriptions: Dict[str, Callable]          # Callback registry
```

**Memory Characteristics**:
- 🚨 **UNBOUNDED RISK** if messages not consumed
- Normal operation: Cleared each round via `receive()`

#### ResourceProxy
**Source**: `masim/proxy/general.py`

```python
class ResourceProxy:
    _connections: Dict[str, Any]        # MCP server connections
    _resource_cache: Dict[str, tuple]   # TTL-based cache
```

**Memory Characteristics**:
- Connection metadata: O(servers)
- Cache: Bounded by TTL expiration (`cache_ttl_seconds`)

---

## 3. Memory Growth Classification

### 3.1 Constant Size (O(1))

Components that do not grow with simulation rounds:

| Component                          | Size Factor | Notes                |
|------------------------------------|-------------|----------------------|
| `Simulator.player_persona_handles` | O(N)        | N = player count     |
| `Simulator.topology`               | O(V + E)    | V = nodes, E = edges |
| `PlayerPersona.peer_handles`       | O(degree)   | Topology out-degree  |
| `BasePlayer.expected_senders`      | O(degree)   | Topology in-degree   |
| `PlayerState.last_observation`     | O(1)        | Single reference     |
| `PlayerState.last_action`          | O(1)        | Single reference     |

### 3.2 Bounded Size (O(k))

Components with configurable upper bounds:

| Component                                   | Bound       | Configuration                  |
|---------------------------------------------|-------------|--------------------------------|
| `Simulator.history.hot`                     | entry_limit | `setting.entry_limit`          |
| `MonitoringProxy._metrics.hot`              | 100         | `MonitoringConfig.entry_limit` |
| `MonitoringProxy._events.hot`               | 100         | `MonitoringConfig.entry_limit` |
| `StorageProxy._*_stores` buffer             | block_size  | `StorageConfig.entry_limit`    |
| `CommunicationChannel.message_store` buffer | 500         | Hardcoded                      |

### 3.3 Transient (Cleared Each Round)

Components that are emptied during normal execution:

| Component                               | Clear Point              | Mechanism        |
|-----------------------------------------|--------------------------|------------------|
| `BasePlayer.inbounds`                   | `get_pending_inbounds()` | List clear       |
| `BasePlayer.pending_outbounds`          | `collect_outbounds()`    | List clear       |
| `SendReceiveProxy.pending_messages[id]` | `receive(id)`            | Dict value clear |

### 3.4 🚨 Potentially Unbounded (MEMORY LEAK RISK)

Components that may grow without limit:

| Component                             | Risk Level | Cause                         |
|---------------------------------------|------------|-------------------------------|
| 🚨 `BasePlayer.state.custom_state`    | **HIGH**   | User code accumulation        |
| 🚨 User-defined class attributes      | **HIGH**   | `self.history = []` patterns  |
| ⚠️ `SendReceiveProxy.pending_messages` | Medium     | Unconsumed messages           |
| `ResourceProxy._resource_cache`       | Low        | TTL prevents unbounded growth |

---

## 4. Component-Level Analysis

### 4.1 Simulator (Driver Process)

**File**: `masim/simulator/general.py`, `masim/simulator/base.py`

```python
class BaseSimulator:
    config: SimulationConfig          # ~1KB (static)
    simulation_id: str                # ~50 bytes
    status: SimulatorStatus           # enum
    current_round: int                # 8 bytes
    current_phase: RoundPhase         # enum
    round_clock: ExecutionClock       # ~100 bytes
    player_persona_handles: Dict      # O(N) references
    history: HistoryBuffer            # Bounded by entry_limit
    topology: TopologyGraph           # O(V + E)
    communication: CommunicationChannel  # Includes message buffer
```

**Memory Formula**:
```
Simulator Memory ≈ config + handles(N) + history_hot(L × R) + topology(V, E) + msg_buffer(500 × M)

Where:
  N = player count
  L = entry_limit (default: 10)
  R = sizeof(round_result) ≈ 1KB
  V = topology vertices
  E = topology edges
  M = sizeof(message) ≈ 500 bytes
```

### 4.2 PlayerPersona (Ray Actor)

**File**: `masim/persona/general.py`

```python
class PlayerPersona:
    player_class: type                # Reference only
    player_config: PlayerConfig       # ~500 bytes
    config: Dict                      # Persona config, ~1KB
    player: BasePlayer                # Domain instance
    storage: StorageProxy             # With buffers
    monitoring: MonitoringProxy       # 2 × HistoryBuffer
    communication: SendReceiveProxy   # Message queues
    resource: ResourceProxy           # MCP cache
    topology: TopologyGraph           # Shared reference
    peer_handles: Dict                # O(out-degree)
```

**Memory per Persona**:
```
Persona Memory ≈ player + storage_buffers + monitoring_hot + comm_pending + resource_cache

Typical breakdown:
  - player core: ~5KB
  - storage buffers: ~75KB (50 msgs × 0.5KB + 50 turns × 1KB)
  - monitoring hot: ~40KB (100 metrics + 100 events)
  - comm pending: Variable (should be ~0 after receive)
  - resource cache: ~10KB (depends on MCP usage)
  
Total per Persona: ~130KB (framework overhead)
```

### 4.3 BasePlayer (Domain Logic)

**File**: `masim/player/base.py`

```python
class BasePlayer:
    name: str                         # ~50 bytes
    identity: str                     # ~50 bytes
    group_tags: List[str]             # ~100 bytes
    config: PlayerConfig              # ~500 bytes
    state: PlayerState                # See below
    inbounds: List[Inbound]           # Transient, cleared each round
    pending_outbounds: List[Outbound] # Transient, cleared each round
    expected_senders: Set[str]        # O(in-degree)
    capabilities: List[str]           # ~100 bytes
    topology_targets: List[str]       # O(out-degree)

class PlayerState:
    turn_count: int                   # 8 bytes
    last_observation: Observation     # Reference only
    last_action: Action               # Reference only
    custom_state: Dict[str, Any]      # 🚨 USER CONTROLLED - UNBOUNDED RISK
    # Timing metrics: ~100 bytes total
```

---

## 5. Memory Estimation Model

### 5.1 Framework Baseline

For a simulation with N players over R rounds:

```
Framework Memory = Simulator_Memory + N × Persona_Memory

Simulator_Memory:
  = config(1KB) + handles(N × 100B) + history_hot(L × 1KB) + topology(1KB) + msg_buffer(250KB)
  ≈ 260KB + N × 0.1KB

Persona_Memory (per actor):
  = base(5KB) + storage_buf(75KB) + monitoring_hot(40KB) + comm(~0KB) + resource(10KB)
  ≈ 130KB

Total Framework:
  ≈ 260KB + N × 130KB
  
Example (8 players):
  ≈ 260KB + 8 × 130KB = 1.3MB
```

### 5.2 Scaling Behavior

| Rounds  | Framework Memory | Notes                          |
|---------|------------------|--------------------------------|
| 100     | ~1.3MB           | Baseline                       |
| 1,000   | ~1.3MB           | Hot/cold keeps memory constant |
| 10,000  | ~1.3MB           | Only disk usage grows          |
| 100,000 | ~1.3MB           | Framework memory unchanged     |

**Key Insight**: Framework memory is **O(1)** with respect to rounds due to hot/cold architecture.

### 5.3 User Code Impact

🚨 **WARNING**: User-defined players (`examples/*/players.py`) can break this guarantee:

```python
# 🚨 ANTI-PATTERN: Unbounded growth - MEMORY LEAK!
class BadPlayer(GeneralPlayer):
    def __init__(self):
        self.price_history = []      # 🚨 O(R) - grows with rounds!
        self.all_trades = []         # 🚨 O(R) - grows with rounds!
    
    async def decide(self):
        self.price_history.append(current_price)  # 🚨 Memory leak!

# ✅ CORRECT: Use HistoryBuffer
class GoodPlayer(GeneralPlayer):
    def __init__(self):
        self.price_history = HistoryBuffer(
            folder=f"{record_path}/prices",
            entry_limit=100
        )
    
    async def decide(self):
        self.price_history.append(current_price)  # Bounded!
```

---

## 6. Risk Assessment

### 6.1 🚨 High Risk Components (UNBOUNDED GROWTH)

| Component                | Location                | Risk                | Mitigation                    |
|--------------------------|-------------------------|---------------------|-------------------------------|
| 🚨 `custom_state`        | `PlayerState`           | Unbounded dict      | Document limits, add warnings |
| 🚨 User class attributes | `examples/*/players.py` | Unbounded lists     | Use HistoryBuffer             |
| 🚨 `pending_messages`    | `SendReceiveProxy`      | Unconsumed messages | Ensure receive() called       |

### 6.2 Medium Risk Components

| Component         | Location        | Risk        | Mitigation               |
|-------------------|-----------------|-------------|--------------------------|
| `_resource_cache` | `ResourceProxy` | Cache size  | TTL-based expiration     |
| `_pending_cold`   | `HistoryBuffer` | Flush delay | Call flush() on shutdown |

### 6.3 Low Risk Components

| Component   | Location          | Risk               | Mitigation              |
|-------------|-------------------|--------------------|-------------------------|
| `hot` deque | `HistoryBuffer`   | Fixed by maxlen    | Configuration           |
| `_timers`   | `MonitoringProxy` | Active timer count | Normal operation clears |

---

## 7. Optimization Recommendations

### 7.1 Configuration Guidelines

```yaml
# simulation.yml
setting:
  entry_limit: 10          # Simulator history hot size
                           # Increase for more round access, costs memory

# persona.yml  
proxy:
  storage:
    entry_limit: 50        # Block size for turn/message stores
                           # Larger = fewer disk writes, more memory
  
  monitoring:
    entry_limit: 100       # Metrics/events hot size
                           # Increase for metric analysis, costs memory
```

### 7.2 User Code Best Practices

1. **Use HistoryBuffer for time-series data**:
   ```python
   self.prices = HistoryBuffer(folder=path, entry_limit=100)
   ```

2. **Clear temporary structures each round**:
   ```python
   async def decide(self):
       result = process(self.temp_data)
       self.temp_data.clear()  # Prevent accumulation
       return result
   ```

3. **Avoid storing full observation/action history**:
   ```python
   # 🚨 Bad - UNBOUNDED GROWTH!
   self.all_observations.append(observation)
   
   # ✅ Good - only keep what's needed
   self.last_n_prices = self.last_n_prices[-10:] + [observation.data["price"]]
   ```

### 7.3 Monitoring Memory Usage

Add memory tracking in long-running simulations:

```python
import sys

# In player's decide():
if round_num % 100 == 0:
    custom_size = sys.getsizeof(self.state.custom_state)
    if custom_size > 1_000_000:  # 1MB warning
        logger.warning(f"custom_state size: {custom_size / 1024:.1f}KB")
```

### 7.4 Emergency Memory Recovery

If memory issues occur during simulation:

1. **Force flush all buffers**:
   ```python
   await simulator.history.flush()
   for handle in simulator.player_persona_handles.values():
       ray.get(handle.storage.flush.remote())
   ```

2. **Clear communication pending**:
   ```python
   # In Persona
   self.communication.pending_messages.clear()
   ```

---

## Appendix: File Reference

| File                          | Memory-Related Components                 |
|-------------------------------|-------------------------------------------|
| `masim/utils/history.py`      | `HistoryBuffer`                           |
| `masim/simulator/base.py`     | `BaseSimulator.history`, `ExecutionClock` |
| `masim/simulator/general.py`  | `GeneralSimulator` memory management      |
| `masim/proxy/base.py`         | Proxy config dataclasses                  |
| `masim/proxy/general.py`      | All proxy implementations                 |
| `masim/player/base.py`        | `PlayerState`, `BasePlayer`               |
| `masim/persona/general.py`    | `PlayerPersona` proxy composition         |
| `masim/communication/base.py` | `CommunicationChannel.message_store`      |

---

*Document generated from MASim codebase analysis. Last updated: 2026-03.*
