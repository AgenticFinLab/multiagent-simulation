# MASim Framework Structure

## Code Structure

```
masim/
├── __init__.py              # Public API exports
├── simulator/               # Simulation orchestration
│   ├── base.py              # SimulationConfig, BaseSimulator, ExecutionClock, RoundPhase
│   │                        # update_topology() extension hook (default no-op; override for dynamic topology)
│   └── general.py           # GeneralSimulator: setup, run_round, phase_execute/collect/dispatch
│                            # _setup_topology(), _update_actor_topology_slices()
├── persona/                 # Ray actor wrapper layer
│   ├── base.py              # BasePersona interface (abstract)
│   └── general.py           # PlayerPersona (Ray actor: owns Player + proxies)
│                            # operate() returns (TurnResult, pending_infos) tuple
├── player/                  # Agent logic (USER IMPLEMENTS)
│   ├── base.py              # Data types: Info, Action, Observation, BasePlayer, PlayerState
│   └── general.py           # GeneralPlayer: turn(), prepare_pending_info(), is_received_ready()
├── communication/           # Message encoding/transmission
│   ├── base.py              # SimPacket, CommunicationChannel (abstract)
│   └── general.py           # GeneralCommunicationChannel: JSON encode/decode/deliver
├── proxy/                   # Infrastructure services
│   ├── base.py              # Message, MessageType, MessagePriority, ProxyConfigs, BaseProxy
│   └── general.py           # SendReceiveProxy, StorageProxy, ResourceProxy, MonitoringProxy
│                            # build_message_from_info() — Info→Message conversion (proxy layer helper)
└── utils/                   # Utilities
    ├── config.py            # load_config (!include YAML), setup_logging, validate_config,
    │                        # load_class() — dynamic class loading from module path string
    ├── ray_utils.py         # ensure_ray(), get_actor_name() — Ray cluster init and actor naming
    ├── history.py           # HistoryBuffer: hot deque + cold BlockBasedStoreManager
    ├── topology.py          # TopologyGraph: BFS execution levels, invalidate_levels_cache(), visualize
    └── data_loader.py       # load_simulation_data(), get_investor_* — record directory loading
```

### Module Summary

| Module          | What It Does                                                          | Key Classes                                                                 | User Implements? |
|-----------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------------|------------------|
| `simulator`     | Orchestrates simulation rounds, manages topology, dispatches messages | `GeneralSimulator`, `SimulationConfig`                                      | ❌ No             |
| `persona`       | Ray actor wrapper, bridges Player ↔ Simulator, owns proxy             | `PlayerPersona`                                                             | ❌ No             |
| `player`        | Agent decision logic                                                  | `GeneralPlayer`, `Info`, `Action`, `Observation`                            | ✅ **Yes**        |
| `communication` | Message encoding/decoding, wire protocol                              | `SimPacket`, `GeneralCommunicationChannel`                                  | ❌ No             |
| `proxy`         | Message queue management, routing types                               | `Message`, `SendReceiveProxy`, `StorageProxy`, `MonitoringProxy`            | ❌ No             |
| `utils`         | Config loading, class loading, Ray init, topology graph, history      | `TopologyGraph`, `load_config`, `load_class`, `ensure_ray`, `HistoryBuffer` | ❌ No             |

## Design Architecture

### Component Ownership Map

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  SIMULATOR  (owns CommunicationChannel)                                          │
│    • Drives rounds: phase_execute → phase_collect → phase_dispatch               │
│    • Calls Personas via Ray remote only                                          │
│    • Owns channel: encode Info→Message→SimPacket, dispatch, record              │
└───────────────────────────┬──────────────────────────────────────────────────────┘
                            │  Ray remote calls only
                ┌───────────┴────────────┐
                ▼                        ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│  PERSONA (Ray Actor)      │  │  PERSONA (Ray Actor)      │  ... one per player
│  ┌─────────────────────┐  │  │  ┌─────────────────────┐  │
│  │  SendReceiveProxy   │  │  │  │  SendReceiveProxy   │  │
│  │  (self.message_proxy│  │  │  │  (self.message_proxy│  │
│  │  send_queue        │  │  │  │  send_queue        │  │
│  │  receive_queue)     │  │  │  │  receive_queue)     │  │
│  └──────────┬──────────┘  │  │  └──────────┬──────────┘  │
│             │             │  │             │             │
│  ┌──────────▼──────────┐  │  │  ┌──────────▼──────────┐  │
│  │  PLAYER (hidden)    │  │  │  │  PLAYER (hidden)    │  │
│  │  perceive→decide→act│  │  │  │  perceive→decide→act│  │
│  └─────────────────────┘  │  │  └─────────────────────┘  │
└───────────────────────────┘  └───────────────────────────┘
```

### Why Player + Persona?

| Layer       | Responsibility                               | User Touches?            |
|-------------|----------------------------------------------|--------------------------|
| **Player**  | Decision logic only                          | ✅ YES - implement this   |
| **Persona** | All infrastructure (Ray, messaging, storage) | ❌ NO - framework handles |

**Benefit**: User focuses purely on agent logic. Framework handles distributed execution, message routing, state management.

### Call Hierarchy

```
Simulator.run()
    │
    └── for round in 1..N:
            │
            └── run_round(round_num)
                    │
                    ├── for level in topology_levels:
                    │       │
                    │       ├── phase_execute(level)  ──────────────────────────────────────────┐
                    │       │       │  [parallel for all nodes in level]                        │
                    │       │       └── persona.operate(round_num)  [Ray remote]               │
                    │       │               │                                                   │
                    │       │               ├── proxy.get_received_senders()  [data]           │
                    │       │               ├── player.is_received_ready()    [decision]       │
                    │       │               ├── proxy.get_received_infos() → Info           │
                    │       │               ├── player.receive_info(info)                   │
                    │       │               └── player.turn(round_num)                        │
                    │       │                       └── for step in 1..N:                     │
                    │       │                               ├── perceive(observation)          │
                    │       │                               ├── decide() → {outbound_messages} │
                    │       │                               └── act(decision) → Action        │
                    │       │                                                                   │
                    │       ├── phase_collect(level)  ◄──────────────────────────────────────────┘
                    │       │       └── ray.get(operate_refs) → TurnResults
                    │       │
                    │       └── phase_dispatch(level)
                    │               ├── [pending_infos bundled into phase_collect result]
                    │               │   (no separate collect_pending_infos() IPC wave)
                    │               ├── build_message_from_info(info) → Message  [proxy.general helper]
                    │               ├── channel.encode_message(Message) → SimPacket
                    │               ├── channel.record_encoded_message(SimPacket)
                    │               ├── channel.decode_message(SimPacket) → Message
                    │               └── target_persona.receive_message(Message)  [Ray remote]
                    │                       └── proxy.handle_incoming(Message) → Info [queued in receive_queue]
                    │
                    └── [next level begins only after dispatch completes]
```

### Persona Responsibilities

```
PlayerPersona (Ray Actor)
    │
    ├── Owns: SendReceiveProxy (self.message_proxy)
    │       │
    │       ├── enqueue_info(info)             # Persona queues Info after Player.turn()
    │       ├── dequeue_infos() → List[Info]   # Collect Info units for dispatch
    │       ├── handle_incoming(Message)        # Proxy converts Message→Info, queues in receive_queue
    │       ├── get_received_senders() → set    # Data for player.is_received_ready()
    │       └── get_received_infos() → List[Info]  # Deliver to Player in operate()
    │
    ├── receive_message(message: Message)   # Called by Simulator via Ray remote
    │       └── Delegates to proxy.handle_incoming(message)
    │           [proxy converts Message → Info, queues in receive_queue]
    │
    ├── operate(round_num) → (TurnResult, List[Dict])   # Called by Simulator each round
    │       ├── proxy.get_received_senders()              [data]
    │       ├── player.is_received_ready()                [player owns this decision]
    │       │       └── if False: log warning, proceed (no busy-wait)
    │       ├── proxy.get_received_infos() → Info
    │       ├── player.receive_info(info)                 [single delivery]
    │       ├── player.turn(round_num) → TurnResult
    │       └── _collect_pending_infos_local() → pending_infos  [bundled into return tuple]
    │               (avoids a separate collect_pending_infos() IPC wave)
    │
    └── collect_pending_infos()   # Legacy public API — still callable externally
            └── proxy.dequeue_infos() → List[Info]
            └── returns [{info, sender_id, target_ids, round_num}]
            (Note: Simulator currently uses operate() return tuple, not this method)
```

### Three-Layer Message Model

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  THREE-LAYER MESSAGE MODEL                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layer         Type          Where Defined       Description                 │
│  ─────────     ──────────    ───────────────     ──────────────────────────  │
│  Player        Info          player/base.py      Pure payload, no routing    │
│                                                  payload, content_type,      │
│                                                  extras, sender_id*,         │
│                                                  time_received*              │
│                                                  (* populated on receive)    │
│                                                                              │
│  Proxy         Message       proxy/base.py       Adds routing metadata       │
│                                                  sender_id, recipient_id,    │
│                                                  timestamp, priority,        │
│                                                  message_type                │
│                                                                              │
│  Channel       SimPacket     communication/      Wire envelope               │
│                              base.py             encoded (JSON str),         │
│                                                  sender_id, recipient_id,    │
│                                                  timestamp                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Full Message Flow (Send + Receive)

```
 PLAYER A                 PERSONA A                    SIMULATOR                     PERSONA B                 PLAYER B
    │                        │                             │                              │                        │
    │  decide():             │                             │                              │                        │
    │  {"outbound_messages" :│                             │                              │                        │
    │  [Info(payload={...})]}│                             │                              │                        │
    │──────────────────────►│                             │                              │                        │
    │                        │  proxy.enqueue_info(info)   │                             │                        │
    │                        │  [info in send_queue]        │                             │                        │
    │                        │                             │                              │                        │
    │                        │◄────────────────────────────│  collect_pending_infos()     │                        │
    │                        │  proxy.dequeue_infos()      │                             │                        │
    │                        │  → [info]                   │                             │                        │
    │                        │                             │                              │                        │
    │                        │                             │  build_message_from_info(Info)                       │
    │                        │                             │  → Message(sender, recipient, payload)               │
    │                        │                             │                              │                        │
    │                        │                             │  encode_message(Message)     │                        │
    │                        │                             │  → SimPacket(encoded=JSON)   │                        │
    │                        │                             │                              │                        │
    │                        │                             │  record_encoded_message(SimPacket)
    │                        │                             │                              │                        │
    │                        │                             │  decode_message(SimPacket)   │                        │
    │                        │                             │  → Message (restored)        │                        │
    │                        │                             │                              │                        │
    │                        │                             │  receive_message(Message) ──►│                        │
    │                        │                             │  [Ray remote]                │                        │
    │                        │                             │                              │  proxy.handle_incoming(│
    │                        │                             │                              │  Message)→Info queued  │
    │                        │                             │                              │  in receive_queue      │
    │                        │                             │                              │                        │
    │             [next round: operate() called]           │              operate() ─────►│                        │
    │                        │                             │                              │                        │
    │                        │                             │                              │  get_received_senders()│
    │                        │                             │                              │  is_received_ready()   │
    │                        │                             │                              │  get_received_infos()│
    │                        │                             │                              │  → Info                │
    │                        │                             │                              │──────────────────────►│
    │                        │                             │                              │  receive_info(info)    │
    │                        │                             │                              │  player.turn()         │
```

**Key Ownership Rules:**
1. **Simulator owns CommunicationChannel** — only Simulator calls `encode_message`, `decode_message`, `encode_and_deliver`
2. **Persona owns SendReceiveProxy** — proxy is never shared, never accessed by Simulator directly
3. **Player owns readiness decision** — `player.is_received_ready()` decides when to proceed; proxy only provides data
4. **Single delivery** — Info units delivered to Player ONCE, inside `operate()` after readiness confirmed
5. **Topology targets come from edges** — `topology.get_targets(sender_id)` returns successors; `topology.get_senders(receiver_id)` returns predecessors used for `expected_senders`
6. **operate() returns bundled tuple** — `(TurnResult, pending_infos)` in a single `ray.get()`, eliminating a separate `collect_pending_infos()` IPC round-trip

## Execution Model

## Round Phases

Each round iterates over topology levels (Level 0 → Level 1 → ... → Level N). **All three phases complete for one level before the next level begins.** This guarantees messages from Level N arrive at Level N+1 before Level N+1 starts executing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Round N  (for each level)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: EXECUTE  (status → EXECUTING)                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Submit persona.operate(round_num, level=N) for all nodes in level     │  │
│  │   in parallel via Ray .remote()                                       │  │
│  │                                                                       │  │
│  │ Inside operate():                                                     │  │
│  │   ① Readiness check: player.is_received_ready() — if False, log      │  │
│  │       warning and proceed (no busy-wait; level-ordered dispatch       │  │
│  │       guarantees messages arrive before operate() is called)          │  │
│  │   ② Drain: proxy.get_received_infos() → player.receive_info()        │  │
│  │   ③ Execute: player.turn(round_num) → TurnResult                     │  │
│  │      turn() = for step in N: perceive→decide→act                     │  │
│  │      prepare_pending_info() extracts outbound_messages into pending  │  │
│  │   ④ Collect: _collect_pending_infos_local() bundles pending Info     │  │
│  │   ⑤ Return: (TurnResult, pending_infos) tuple — no extra IPC wave   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  Phase 2: COLLECT                                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ ray.wait() loop until all operate() futures done                     │  │
│  │ Returns {player_id → TurnResult}                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  Phase 3: DISPATCH                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ ① pending_infos already collected from operate() return value         │  │
│  │   (no separate ray.get call — bundled in phase_collect result)        │  │
│  │ ② build_message_from_info(info) → Message                            │  │
│  │   (wraps payload in {"content":…,"content_type":…,"extras":…})      │  │
│  │ ③ channel.encode_and_deliver(messages, handles)                      │  │
│  │   encode → record → decode → target.receive_message.remote()        │  │
│  │ ④ ray.get(dispatch_refs) — block until all deliveries confirmed      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  [then proceed to next level or next round]                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                                 Round N+1
```

### Topology-Based Execution Order

Topology is a directed graph where an edge `A → B` means A can send to B. Execution levels are computed via BFS from the configured `sources`.

```yaml
# topology.yml
sources:
  - coordinator          # These are Level 0 (execute first)

connections:
  coordinator:           # coordinator can send to player_1, player_2
    - player_1
    - player_2
  player_1:              # player_1 can send back to coordinator
    - coordinator
  player_2:              # player_2 can send back to coordinator
    - coordinator
```

**Derived Execution Levels (BFS from sources):**

| Level | Nodes                  | When They Execute | `expected_senders` (predecessors)             |
|-------|------------------------|-------------------|-----------------------------------------------|
| 0     | `coordinator`          | First             | `{player_1, player_2}` — wait Round 2+ only   |
| 1     | `player_1`, `player_2` | After Level 0     | `{coordinator}` — wait for coordinator always |

**No `sources` configured:** All players placed in a single Level 0 (all run in parallel).

**`expected_senders` derivation:** Each Persona calls `topology.get_senders(self.identity)` (graph predecessors) after topology is set. This set is assigned to `player.expected_senders` and checked in `is_received_ready()`.

### Round Numbering

| Round | Type             | Description                                                                  |
|-------|------------------|------------------------------------------------------------------------------|
| 0     | Setup            | Topology initialization, actor creation, diagram saved                       |
| 1     | First simulation | Level 0 nodes (`round==1 and level==0`) execute without waiting for messages |
| 2+    | Subsequent       | All nodes wait for `expected_senders` before proceeding                      |

**Readiness Logic (`is_received_ready`):**
```python
# Level 0 in Round 1 = initiators, don't wait
if round_num == 1 and level == 0:
    return True
# No expected senders → always ready
if not self.expected_senders:
    return True
# Otherwise wait for all predecessors to have sent
return self.expected_senders.issubset(received_senders)
```
This means in a star topology with `coordinator` at Level 0: coordinator fires first in Round 1 without waiting; from Round 2 onward, coordinator waits for player responses before running.

## Extension Points

### Dynamic Topology (`update_topology`)

Override `update_topology(round_num)` in a `GeneralSimulator` subclass to rewire the topology before each round:

```python
class MySimulator(GeneralSimulator):
    def update_topology(self, round_num: int) -> None:
        if round_num == 10:
            self.topology.graph.add_edge("player_1", "player_2")
            self.topology.invalidate_levels_cache()   # Force BFS recompute
            self._update_actor_topology_slices(["player_1", "player_2"])
            # Pass both affected players: player_1's targets grew,
            # player_2's senders grew — and player_1 needs player_2's handle.
```

`_update_actor_topology_slices(player_ids)` does two things atomically:
1. Pushes new `{targets, senders}` slices via `set_topology.remote()`
2. Pushes updated peer handle subsets via `set_peer_handles.remote()`

Both steps must complete before the next round's phase_execute starts.

### Custom Readiness Logic (`is_received_ready`)

Override `is_received_ready(round_num, received_senders, **kwargs)` in your `Player` subclass for non-standard scenarios:
- **Same-level peers**: relax readiness condition for optional/lagged senders
- **Feedback edges**: check `info.extras["round_num"]` to distinguish which round's message arrived
- **Quorum-based**: proceed when a minimum subset of expected senders have sent
- **Timeout-based**: proceed after N rounds regardless of readiness

Default implementation (in `GeneralPlayer`):
```python
def is_received_ready(self, round_num, received_senders, **kwargs) -> bool:
    level = kwargs.get("level", 0)
    if round_num == 1 and level == 0:   # Initiators fire unconditionally
        return True
    if not self.expected_senders:        # Isolated node — always ready
        return True
    return self.expected_senders.issubset(received_senders)
```

## Memory Management

The framework is designed to avoid unbounded memory growth over long simulations:

| Component                        | What it stores                     | Bound                                                  |
|----------------------------------|------------------------------------|--------------------------------------------------------|
| `HistoryBuffer` (simulator)      | Round results                      | `setting.round_history_limit` hot; rest on disk        |
| `MonitoringProxy`                | Metrics + events                   | `MonitoringConfig.monitor_hot_limit` hot; rest on disk |
| `StorageProxy`                   | Turn results + messages per player | BlockBasedStoreManager (disk, flushed on shutdown)     |
| `SendReceiveProxy.send_queue`    | Pending Info to dispatch           | Cleared every round in `collect_pending_infos()`       |
| `SendReceiveProxy.receive_queue` | Received Info to deliver           | Cleared every round in `get_received_infos()`          |
| `Player.received_infos`          | Infos before delivery              | Cleared in `get_received_infos()`                      |
| `Player.pending_info`            | Infos after decide()               | Cleared in `operate()` after enqueue                   |

**In example players:** Use `HistoryBuffer` or `deque(maxlen=N)` for any list that grows each round (e.g., price history, returns). Never use a plain `list.append()` without a bound.

## Data Types Reference

### Player-Layer: Info (direction-agnostic content carrier)

```python
@dataclass
class Info:
    payload: PayloadType         # The actual content (sent or received)
    content_type: Optional[str]  # Optional label (e.g., "broadcast", "result")
    extras: Dict                 # Flexible additional fields
    sender_id: Optional[str]     # Populated on RECEIVE — who sent this (None if sending)
    time_received: Optional[str] # Populated on RECEIVE — ISO timestamp (None if sending)
```
```

### Proxy-Layer: Message (routing metadata)

```python
@dataclass
class Message:
    message_type: MessageType    # PEER, BROADCAST, OBSERVATION, ACTION, ...
    sender_id: str               # Who sent this
    payload: Dict                # {"content": ..., "content_type": ..., "extras": ...}
    recipient_id: Optional[str]  # Target recipient (None = broadcast)
    timestamp: str               # ISO format
    priority: MessagePriority    # LOW, NORMAL, HIGH, CRITICAL
    extras: Dict                 # Additional context (e.g., round_num)
```

### Channel-Layer: SimPacket (wire envelope)

```python
@dataclass
class SimPacket:
    encoded: str              # JSON-serialized Message content
    sender_id: str            # For routing without full decode
    recipient_id: Optional[str]
    timestamp: str            # Encoding timestamp (ISO format)
```

### Input: Observation

```python
@dataclass
class Observation:
    local: LocalObservation   # Player's own perception
    inbounds: List[Info]      # Received Info units from other players (sender_id populated)
    round: int                # Current round number
```

### Output: Action

```python
@dataclass
class Action:
    action_type: str          # Category (e.g., "trade", "move")
    payload: Dict             # Action parameters
    source_id: str            # Player identity
    timestamp: str            # Auto-generated
    extras: Dict              # Additional context
```

## How to Implement a Player

### Required Methods

| Method     | Signature                                 | Purpose                                                 |
|------------|-------------------------------------------|---------------------------------------------------------|
| `perceive` | `async (observation, prev_result) → None` | Process received messages, update internal state        |
| `decide`   | `async () → Dict`                         | Make decision, return dict with `outbound_messages` key |
| `act`      | `async (decision_payload) → Action`       | Create Action object for logging/environment            |

### Template

```python
from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, Info, StepResult
from typing import Dict, Any, Optional

class MyPlayer(GeneralPlayer):

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """
        Called first in each step.
        - observation.round: current round number
        - observation.inbounds: List[Info] from other players
          - info.sender_id: who sent it
          - info.payload: the actual content
        """
        self.state.custom_state["round"] = observation.round
        
        for info in observation.inbounds:
            sender = info.sender_id
            data = info.payload      # Direct access to content
            # Process data...

    async def decide(self) -> Dict[str, Any]:
        """
        Called after perceive().
        
        To send messages, include "outbound_messages" key as List[Dict]:
          - payload: content to send (routed by topology)
          - content_type: optional label
        """
        return {
            "my_result": 42,
            "outbound_messages": [
                {
                    "payload": {"value": 42},
                    "content_type": "result",
                }
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Called after decide()."""
        return Action(
            action_type="my_action",
            payload=decision_payload,
            source_id=self.identity,
        )
```

## Configuration

### File Structure

```
configs/MySimulation/
├── simulation.yml      # Main config
├── players.yml         # Player definitions  
├── topology.yml        # Communication graph
└── persona.yml         # Shared persona settings
```

### simulation.yml

```yaml
setting:
  name: "my_simulation"
  total_rounds: 5
  record_path: "EXPERIMENT/MySimulation/records"

environment:
  dotenv_path: .env

ray:
  namespace: "my_simulation"
  num_cpus: 4

players: !include players.yml
topology: !include topology.yml

communication:
  storage_path: "EXPERIMENT/MySimulation/communication"
```

### players.yml

```yaml
player_id:                                    # Unique identifier
  name: "Display Name"
  class: "module.path:ClassName"              # Import path
  num_instances: 1                            # REQUIRED — no default; omitting raises KeyError
  config:
    identity: "player_id"                     # Must match key
    role: coordinator | player                # Role hint
    steps_per_turn: 1                         # Steps per round
  persona: !include persona.yml
```

### topology.yml

```yaml
sources:
  - node_that_starts_first

connections:
  sender_id:
    - target_1
    - target_2
```

## Running a Simulation

```python
import asyncio
from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config

async def main():
    config = SimulationConfig(**load_config("configs/MySimulation/simulation.yml"))
    simulator = GeneralSimulator(config)
    
    await simulator.setup()      # Create Ray actors
    results = await simulator.run()  # Run all rounds
    await simulator.shutdown()   # Cleanup

asyncio.run(main())
```

## Quick Reference

### Sending a Message

```python
async def decide(self) -> Dict[str, Any]:
    return {
        "outbound_messages": [
            {"payload": {"key": "value"}, "content_type": "my_type"}
        ]
    }
```

### Receiving a Message

```python
async def perceive(self, observation: Observation, ...) -> None:
    for info in observation.inbounds:      # List[Info]
        sender = info.sender_id            # who sent it
        value = info.payload["key"]        # the actual content
        label = info.content_type          # optional type label
```

### Storing State Between Rounds

```python
async def perceive(self, observation, ...) -> None:
    self.state.custom_state["my_data"] = computed_value

async def decide(self) -> Dict[str, Any]:
    data = self.state.custom_state["my_data"]
```

## Output Artifacts

```
EXPERIMENT/MySimulation/
├── records/                         # config.setting.record_path
│   ├── diagrams/
│   │   ├── topology_r000000.png     # Round 0 (setup)
│   │   ├── topology_r000001.png     # Round 1 (if save_diagram_interval matches)
│   │   └── ...
│   └── history/
│       └── batch_*.json             # HistoryBuffer cold storage (round results)
├── communication/                   # config.communication.storage_path
│   └── *.json                       # SimPacket records (one per message)
└── <player_id>/                     # StorageProxy per-player storage
    ├── messages/
    │   └── *.json                   # Per-round message records (StorageProxy)
    └── turns/
        └── turn_r*.json             # TurnResult records per round (StorageProxy)
```

**Key config fields controlling artifacts:**
- `setting.record_path`: base for diagrams, history, player storage
- `setting.save_diagram_interval`: how often topology diagrams are saved (0 = never)
- `setting.round_history_limit`: HistoryBuffer hot deque size for round results
- `communication.storage_path`: where channel SimPacket records go
- `proxy.storage.record_path` in persona.yml: per-player turn/message storage root

## Complete Data Types

| Dataclass          | Layer   | Purpose                        | Key Fields                                                          |
|--------------------|---------|--------------------------------|---------------------------------------------------------------------|
| `Info`             | Player  | Send/receive content           | `payload`, `content_type`, `extras`, `sender_id*`, `time_received*` |
| `Observation`      | Player  | Input to perceive()            | `local`, `inbounds: List[Info]`, `round`                            |
| `LocalObservation` | Player  | Player's own perception        | `data`, `timestamp`, `extras`                                       |
| `Action`           | Player  | Output of act()                | `action_type`, `payload`, `source_id`                               |
| `StepResult`       | Player  | Single step output             | `action`, `decision_payload`                                        |
| `TurnResult`       | Player  | Full turn output               | `step_results`, `final_action`                                      |
| `Message`          | Proxy   | Routed message (proxy/base.py) | `message_type`, `sender_id`, `recipient_id`, `payload`              |
| `SimPacket`        | Channel | Wire envelope                  | `encoded`, `sender_id`, `recipient_id`, `timestamp`                 |
| `PlayerState`      | Player  | Mutable player state           | `custom_state`, `turn_count`                                        |
| `PlayerConfig`     | Player  | Immutable player config        | `identity`, `role`, `steps_per_turn`                                |

`*` populated only on receive (Info sent outgoing has these as None)