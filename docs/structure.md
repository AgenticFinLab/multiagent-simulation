# MASim Framework Structure

## Code Structure

```
masim/
├── __init__.py              # Public API exports
├── simulator/               # Simulation orchestration
│   ├── base.py              # SimulationConfig, BaseSimulator
│   └── general.py           # GeneralSimulator implementation
├── persona/                 # Ray actor wrapper layer
│   ├── base.py              # BasePersona interface
│   └── general.py           # PlayerPersona (handles all I/O)
├── player/                  # Agent logic (USER IMPLEMENTS)
│   ├── base.py              # Data types: Action, Observation, Inbound, Outbound
│   └── general.py           # GeneralPlayer base class
├── communication/           # Message encoding/transmission
│   ├── base.py              # Message, CommunicationChannel
│   └── general.py           # GeneralCommunicationChannel
├── proxy/                   # Infrastructure services
│   ├── base.py              # ProxyConfig, BaseProxy
│   └── general.py           # StorageProxy, MonitoringProxy, etc.
└── utils/                   # Utilities
    ├── config.py            # load_config, setup_logging
    └── topology.py          # TopologyGraph
```

### Module Summary

| Module          | What It Does                                                          | Key Classes                              | User Implements? |
|-----------------|-----------------------------------------------------------------------|------------------------------------------|------------------|
| `simulator`     | Orchestrates simulation rounds, manages topology, dispatches messages | `GeneralSimulator`, `SimulationConfig`   | ❌ No             |
| `persona`       | Ray actor wrapper, handles receive/send, calls Player                 | `PlayerPersona`                          | ❌ No             |
| `player`        | Agent decision logic                                                  | `GeneralPlayer`, `Action`, `Observation` | ✅ **Yes**        |
| `communication` | Message encoding/decoding, wire protocol                              | `Message`, `GeneralCommunicationChannel` | ❌ No             |
| `proxy`         | Storage, monitoring, resource management                              | `StorageProxy`, `MonitoringProxy`        | ❌ No             |
| `utils`         | Config loading, topology graph                                        | `TopologyGraph`, `load_config`           | ❌ No             |

## Design Architecture

### Three-Layer Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Simulator                                      │
│  Controls: rounds, topology, message dispatch                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Persona (Ray Actor)                                 │
│  Handles: message receive, message send, state persistence                  │
│  User does NOT touch this layer                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Player (Your Code)                                 │
│  Implements: perceive() → decide() → act()                                  │
│  User ONLY writes this layer                                                │
└─────────────────────────────────────────────────────────────────────────────┘
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
                    ├── phase_execute()  ─────────────────────────────────────┐
                    │       │                                                 │
                    │       └── for level in topology_levels:                 │
                    │               │                                         │
                    │               └── Persona.operate(round_num)            │
                    │                       │                                 │
                    │                       ├── wait for expected messages    │
                    │                       │                                 │
                    │                       └── Player.turn(round_num)        │
                    │                               │                         │
                    │                               └── for step in 1..N:     │
                    │                                       │                 │
                    │                                       └── step()        │
                    │                                           ├── perceive()│
                    │                                           ├── decide()  │
                    │                                           └── act()     │
                    │                                                         │
                    ├── phase_collect()  ◄────────────────────────────────────┘
                    │       └── gather TurnResults from all Personas
                    │
                    └── phase_dispatch()
                            └── collect outbounds, route via topology
```

### Persona Responsibilities

```
PlayerPersona (Ray Actor)
    │
    ├── receive_message(message)      # Receive from other agents
    │       └── convert to Inbound
    │       └── store in player.inbounds
    │
    ├── operate(round_num)            # Called by Simulator each round
    │       └── wait for expected messages
    │       └── call player.turn()
    │       └── return TurnResult
    │
    ├── collect_outbounds()           # Called by Simulator after execution
    │       └── get pending outbounds from player
    │
    └── send via Simulator            # Simulator dispatches messages
            └── encode_and_deliver() to target Personas
```

### Message Flow Detail

```
Player A                    Framework                    Player B
    │                          │                            │
    │  decide() returns:       │                            │
    │  {"outbound_messages":   │                            │
    │    [{"payload": data}]}  │                            │
    │          │               │                            │
    │          ▼               │                            │
    │    Outbound object       │                            │
    │          │               │                            │
    └──────────┼───────────────┘                            │
               │                                            │
               ▼                                            │
    ┌─────────────────────┐                                 │
    │ Simulator collects  │                                 │
    │ all outbounds       │                                 │
    └─────────┬───────────┘                                 │
              │                                             │
              ▼                                             │
    ┌─────────────────────┐                                 │
    │ Channel.prepare_    │                                 │
    │ message(outbound)   │──► Message object               │
    └─────────┬───────────┘                                 │
              │                                             │
              ▼                                             │
    ┌─────────────────────┐                                 │
    │ encode_and_deliver  │                                 │
    │ to target Persona B │─────────────────────────────────┤
    └─────────────────────┘                                 │
                                                            │
                                            ┌───────────────┘
                                            ▼
                                 ┌─────────────────────┐
                                 │ Persona B receives  │
                                 │ converts to Inbound │
                                 └─────────┬───────────┘
                                           │
                                           ▼
                                 ┌─────────────────────┐
                                 │ Next round:         │
                                 │ observation.inbounds│
                                 │ contains the data   │
                                 └─────────────────────┘
```

## Execution Model

### Round Phases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Round N                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: EXECUTE                                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ For each level (0, 1, 2, ...):                                        │  │
│  │   • All nodes in level execute in parallel                            │  │
│  │   • Each node: Persona.operate() → Player.turn() → step() × N         │  │
│  │   • step() = perceive() → decide() → act()                            │  │
│  │   • Wait for level to complete before next level                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  Phase 2: COLLECT                                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Gather TurnResult from all players                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  Phase 3: DISPATCH                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Collect all outbounds from all Personas                             │  │
│  │ • For each outbound:                                                  │  │
│  │   - Look up topology targets for sender                               │  │
│  │   - Route message to each target Persona                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                                 Round N+1
```

### Topology-Based Execution Order

```yaml
# topology.yml
sources:
  - coordinator          # These are Level 0

connections:
  coordinator:           # coordinator can send to player_1, player_2
    - player_1
    - player_2
  player_1:              # player_1 can send to coordinator
    - coordinator
  player_2:              # player_2 can send to coordinator
    - coordinator
```

**Derived Execution Levels:**

| Level | Nodes                  | When They Execute | Message Waiting                                 |
|-------|------------------------|-------------------|-------------------------------------------------|
| 0     | `coordinator`          | First             | Round 1: No waiting. Round 2+: Wait for senders |
| 1     | `player_1`, `player_2` | After Level 0     | Wait for all expected senders                   |

### Round Numbering

| Round | Type             | Description                                            |
|-------|------------------|--------------------------------------------------------|
| 0     | Setup            | Topology initialization, actor creation, diagram saved |
| 1     | First simulation | Level 0 nodes execute without waiting for messages     |
| 2+    | Subsequent       | All nodes wait for expected senders before proceeding  |

## Data Types Reference

### Input: Observation

```python
@dataclass
class Observation:
    local: LocalObservation    # Player's own perception
    inbounds: List[Inbound]    # Messages from other players
    round: int                 # Current round number
```

### Input: Inbound

```python
@dataclass
class Inbound:
    message: Message
    time_received: str
    
    @property
    def sender_id(self) -> str       # Who sent this
    
    @property
    def payload(self) -> Dict        # The actual content (auto-unwrapped)
```

### Output: Outbound

```python
@dataclass
class Outbound:
    payload: Dict               # Content to send
    content_type: Optional[str] # Label (e.g., "broadcast", "response")
    extras: Dict                # Additional metadata
```

### Output: Action

```python
@dataclass
class Action:
    action_type: str           # Category (e.g., "trade", "move")
    payload: Dict              # Action parameters
    source_id: str             # Player identity
    timestamp: str             # Auto-generated
    extras: Dict               # Additional context
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
from masim.player.base import Action, Observation, StepResult
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
        - observation.inbounds: list of received messages
        - observation.local: local observation data
        
        Store relevant data in self.state.custom_state for use in decide()
        """
        self.state.custom_state["round"] = observation.round
        
        for inb in observation.inbounds:
            sender = inb.sender_id
            data = inb.payload  # Direct access to content
            # Process data...

    async def decide(self) -> Dict[str, Any]:
        """
        Called after perceive().
        
        Must return a dict. To send messages, include "outbound_messages" key:
        - outbound_messages: List[Dict] with "payload" and optional "content_type"
        
        Messages are routed based on topology connections.
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
        """
        Called after decide().
        - decision_payload: the dict returned by decide()
        
        Create and return an Action object.
        """
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
    for inb in observation.inbounds:
        sender = inb.sender_id
        value = inb.payload["key"]  # Direct access
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
├── records/
│   └── diagrams/
│       ├── topology_r000000.png    # Round 0 (setup)
│       ├── topology_r000001.png    # Round 1
│       └── ...
└── communication/
    └── messages/
        └── *.json                   # Encoded message records
```

## Complete Data Types

| Dataclass          | Purpose                  | Key Fields                                             |
|--------------------|--------------------------|--------------------------------------------------------|
| `Observation`      | Input to perceive()      | `local`, `inbounds`, `round`                           |
| `LocalObservation` | Player's own perception  | `data`, `timestamp`, `extras`                          |
| `Inbound`          | Received message wrapper | `sender_id`, `payload` (properties)                    |
| `Outbound`         | Message to send          | `payload`, `content_type`, `extras`                    |
| `Action`           | Output of act()          | `action_type`, `payload`, `source_id`                  |
| `StepResult`       | Single step output       | `action`, `outbounds`, `decision_payload`              |
| `TurnResult`       | Full turn output         | `step_results`, `action`, `outbounds`                  |
| `Message`          | Wire format              | `message_type`, `sender_id`, `recipient_id`, `payload` |
| `PlayerState`      | Mutable player state     | `custom_state`, `last_observation`                     |
| `PlayerConfig`     | Immutable player config  | `identity`, `role`, `steps_per_turn`                   |
