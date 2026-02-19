# MASim Code Structure and Architecture

## Overview

MASim (Multi-Agent Simulation) is a domain-agnostic, behavior-semantics-driven multi-agent framework built on Ray for distributed execution. The framework separates *what* agents do (domain logic) from *how* infrastructure operates (proxies) through a three-layer abstraction model.

## Directory Layout

```
masim/
├── __init__.py              # Package root: re-exports all public symbols
├── simulator/               # L1: Simulation orchestration
│   ├── base.py              # Abstract BaseSimulator, SimulationConfig, ExecutionClock
│   └── general.py           # GeneralSimulator with Ray actor management
├── persona/                 # L2: Infrastructure coordination facade
│   ├── base.py              # Abstract BasePersona, PersonaConfig
│   └── general.py           # PlayerPersona (for all players including coordinators)
├── player/                  # L3: Autonomous agent domain logic
│   ├── base.py              # Abstract BasePlayer, Action, Observation, PlayerConfig, PlayerState
│   └── general.py           # GeneralPlayer, EchoPlayer, NoOpPlayer, ReactivePlayer
├── proxy/                   # Infrastructure primitives (micro-proxy pattern)
│   ├── base.py              # Four proxy types + ProxyFactory
│   └── general.py           # Convenience constructors, simplified wrappers
├── communication/           # Message routing and protocols
│   └── base.py              # Message, MessageRouter, JsonProtocol
└── utils/                   # Configuration and helpers
    └── config.py            # load_config with !include, env interpolation
```

Every module follows the **base.py / general.py** convention:
- `base.py` — Abstract classes, data types, enums, and architectural documentation.
- `general.py` — Concrete, ready-to-use implementations.

## Three-Layer Architecture

MASim employs a strict three-layer separation to isolate domain logic from infrastructure concerns:

```
┌───────────────────────────────────────────────────────────────────────┐
│  Layer 1: Player  (WHAT)                                          │
│  Pure domain logic — perceive → decide → act                       │
│  ZERO infrastructure knowledge, ZERO proxy references              │
│  Coordinators are Players with role='coordinator'                  │
└───────────────────────┬───────────────────────────────────────────────┘
                        │  self._persona.xxx()
┌───────────────────────▼───────────────────────────────────────────────┐
│  Layer 2: Persona  (WHEN)                                          │
│  Infrastructure coordination facade                                │
│  - Proxy aggregation (owns all 4 proxy types)                      │
│  - Lifecycle management (init/shutdown)                            │
│  - Timing policies (auto-checkpoint, retry, timeout)               │
│  - Ray Actor interface (Simulator only sees Persona)               │
└───────────────────────┬───────────────────────────────────────────────┘
                        │  self._storage.checkpoint(), self._communication.send(), ...
┌───────────────────────▼───────────────────────────────────────────────┐
│  Layer 3: Proxy  (HOW)                                             │
│  Single-responsibility infrastructure primitives                   │
│  - CommunicationProxy: send, broadcast, subscribe                  │
│  - StorageProxy: checkpoint, restore, list_checkpoints             │
│  - ResourceProxy: fetch_resource, invoke_tool (MCP)                │
│  - ObservabilityProxy: log_event, record_metric, get_metrics       │
└───────────────────────────────────────────────────────────────────────┘
```

### Why Three Layers? (Design Rationale)

| Question                                     | Answer                                                                                                                                  |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| **Why not let Player use Proxies directly?** | Violates separation of concerns. Player would be polluted with infrastructure logic (when to checkpoint, how to retry, error handling). |
| **Why not merge Persona into Player?**       | Player should be pure domain logic, easily testable without infrastructure. Persona handles Ray integration, lifecycle, and policies.   |
| **Why not merge Proxy into Persona?**        | Different proxies have different implementations (storage backends, message protocols). Single-responsibility principle.                |
| **Why does Persona own proxy_config?**       | Centralized configuration. Player doesn't need to know proxy details. Changing storage backend only affects Persona config.             |

### Layer Responsibilities

| Layer       | Responsibility             | Knows About          | Hidden From                       |
|-------------|----------------------------|----------------------|-----------------------------------|
| **Player**  | Domain logic (WHAT to do)  | Only `self._persona` | Proxies, Ray, configs             |
| **Persona** | Coordination (WHEN to do)  | All 4 proxies, Ray   | Implementation details of proxies |
| **Proxy**   | Infrastructure (HOW to do) | Specific backend     | Domain logic                      |

### Concrete Example: Checkpoint Flow

```
1. Simulator calls: player_persona.operate()
2. Persona decides: "After this step, I should auto-checkpoint"
3. Persona calls: self._storage.checkpoint(player.save_state())
4. StorageProxy executes: Write to disk/S3/Redis (configurable)
5. Player is UNAWARE that checkpoint happened
```

**Without Persona (BAD design):**
```python
class MyPlayer(BasePlayer):
    async def decide(self):
        # Player polluted with infrastructure concerns
        await self._storage.checkpoint(...)  # WHEN to checkpoint? Error handling?
        return {"action": "buy"}
```

**With Persona (GOOD design):**
```python
class MyPlayer(BasePlayer):
    async def decide(self):
        # Pure domain logic only
        return {"action": "buy"}

# Persona handles checkpoint automatically based on PersonaConfig.auto_checkpoint
```

### Configuration Ownership

```
SimulationConfig
│
├── setting: {total_rounds, steps_per_turn, ...}
├── ray: {address, namespace, ...}
│
├── players:
│   └── agent_1:
│       ├── class: "module:PlayerClass"     # Player knows nothing about infra
│       ├── config: {identity, extras}       # PlayerConfig (domain only)
│       └── persona_config:                  # PersonaConfig (infra policies)
│           ├── auto_checkpoint: true
│           ├── proxy_config:                # Proxy configs (HOW)
│           │   ├── storage: {backend: "file", path: "./data"}
│           │   ├── communication: {protocol: "json"}
│           │   └── observability: {log_level: "INFO"}
│           └── env_overrides: {...}
│
└── ... (more players with role='coordinator' or role='player')
```

**Key Rule**: `proxy_config` is EXCLUSIVELY owned by Persona. Players never see it.

## Hierarchical Execution Model

```
┌──────────┬────────────────────┬───────────┬──────────────────────────────┐
│  Level   │  Entity            │  Term     │  Description                 │
├──────────┼────────────────────┼───────────┼──────────────────────────────┤
│  L1      │  Simulator         │  round    │  Orchestrates all Personas   │
│  L2      │  PlayerPersona     │  operate  │  Calls Player.turn()         │
│  L3      │  Player            │  turn     │  Loop of step() calls        │
│  L4      │  Player            │  step     │  perceive → decide → act     │
└──────────┴────────────────────┴───────────┴──────────────────────────────┘
```

Note: Coordinators are Players with `role='coordinator'` in their config.
They execute first in each round, then regular players execute.

A single **round** progresses through these phases:

1. **COORDINATION** (if coordinators exist) — Coordinators execute first.
2. **PLAYER_DECISION** — All regular PlayerPersonas execute `operate()` in parallel (Ray).
3. **COMPLETE** — Collect results and record history.

## Execution Granularity

The framework uses a strict hierarchical time model where each level has its own clock for traceability. The nesting relationship is:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ROUND (Simulator)                                                       ║
║  • One complete simulation cycle across ALL entities                     ║
║  • Phases: COORDINATION (if coordinators) → PLAYER_DECISION → COMPLETE   ║
║  • Tracked by: round_clock (ExecutionClock)                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  OPERATE (PlayerPersona)                                                 ║
║  • Simulator-facing interface for ALL players (coordinators & regular)   ║
║  • Invokes Player.turn() internally                                      ║
║  • Returns: TurnResult                                                   ║
║  TURN (Player)                                                           ║
║  • A batch of steps within one operate() call                           ║
║  • Iterative loop: step(prev_result) × num_steps                        ║
║  • prev_result feeds into next step (stateful chaining)                 ║
║  • Tracked by: turn_clock                                               ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  STEP (Player)                                                           ║
║  • Atomic behavioral unit: perceive → decide → act                      ║
║  • Produces one Action and one StepResult                               ║
║  • Tracked by: step_clock                                               ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Granularity Definitions

| Term        | Owner         | Description                                                             | Output      | Clock         |
|-------------|---------------|-------------------------------------------------------------------------|-------------|---------------|
| **round**   | Simulator     | One complete simulation cycle; coordinators first, then regular players | RoundResult | `round_clock` |
| **operate** | PlayerPersona | Facade method called by Simulator; invokes `turn()` internally          | TurnResult  | (delegates)   |
| **turn**    | Player        | Batch of `step()` calls; iterates with `prev_result` chaining           | TurnResult  | `turn_clock`  |
| **step**    | Player        | Atomic unit: `perceive() → decide() → act()`                            | StepResult  | `step_clock`  |

### Time Tracking (ExecutionClock)

Each level maintains its own `ExecutionClock` for precise temporal traceability:

```python
@dataclass
class ExecutionClock:
    tick_start: Optional[float] = None   # Start timestamp
    tick_end: Optional[float] = None     # End timestamp
    iteration: int = 0                   # Current iteration count
```

### Nesting Example

```
Round 1
├── Phase: COORDINATION (if coordinators exist)
│   └── PlayerPersona[coordinator].operate()
│       └── Player.turn(num_steps=1)
│           └── step: perceive → decide → act → StepResult
│           → TurnResult (coordinator's action/broadcast)
│
├── Phase: PLAYER_DECISION (parallel)
│   ├── PlayerPersona[agent_1].operate()
│   │   └── Player.turn(num_steps=3)
│   │       ├── step(1): perceive → decide → act → StepResult_1
│   │       ├── step(2, prev=StepResult_1) → StepResult_2
│   │       └── step(3, prev=StepResult_2) → StepResult_3 (final)
│   │       → TurnResult(final_action, all_step_results)
│   │
│   └── PlayerPersona[agent_2].operate() ... (parallel)
│
└── Phase: COMPLETE
    └── Collect all results, record history

Round 2 ...
```

### Design Rationale

1. **Stateful Step Chaining**: Each `step()` receives `prev_result` from the previous step, enabling iterative refinement (e.g., multi-round negotiation, progressive reasoning).

2. **Isolation Boundaries**: Simulator only sees `operate()`; it has no knowledge of the internal `turn` / `step` structure. This preserves encapsulation.

3. **Parallel Execution**: All `PlayerPersona.operate()` calls within a round execute in parallel via Ray; coordinators execute first if present.

4. **Clock Hierarchy**: Each level tracks its own timing independently, enabling fine-grained performance analysis and debugging.

## Simulator (`masim/simulator/`)

The Simulator is a **pure orchestrator**. It does not generate observations, execute actions, or interpret domain semantics.

| Symbol             | Role                                                                                |
|--------------------|-------------------------------------------------------------------------------------|
| `SimulatorStatus`  | Enum: `INITIALIZING → READY → RUNNING → PAUSED → TERMINATED → ERROR`                |
| `RoundPhase`       | Enum: `NOTIFICATION → PLAYER_DECISION → COORDINATION → COMPLETE`                    |
| `ExecutionClock`   | Hierarchical time tracking (`tick_start` / `tick_end`)                              |
| `SimulationConfig` | Dataclass: `setting`, `ray`, `players` (includes coordinators via role), `topology` |
| `BaseSimulator`    | Abstract — subclasses implement `_launch_player_personas()`                         |
| `GeneralSimulator` | Concrete — Ray cluster init, actor launching, round loop                            |

Configuration loading:

```python
yaml_config = load_config("configs/Demo/simulation.yml")
sim_config = SimulationConfig(**yaml_config)
```

## Persona (`masim/persona/`)

Persona is the **primary external interface** that the Simulator interacts with. Player is completely hidden behind Persona as internal implementation detail.

| Symbol          | Role                                                                                             |
|-----------------|--------------------------------------------------------------------------------------------------|
| `BasePersona`   | Abstract — proxy aggregation, `fetch_resource()`, `log_event()`                                  |
| `PersonaConfig` | `auto_checkpoint`, `debug_mode`, `env_overrides`                                                 |
| `PlayerPersona` | Wraps `BasePlayer`, exposes `operate()` / `initialize()` / `shutdown()` / `get_state_snapshot()` |

All Personas (including coordinators) are deployed as **Ray actors** with detached lifetime.
Coordinators are simply Players with `role='coordinator'` in their config.

## Player (`masim/player/`)

A Player is defined by its behavioral contract: it produces `Action` objects that are **directly interpreted** by the environment.

### Core Data Types

| Type           | Description                                                                                          |
|----------------|------------------------------------------------------------------------------------------------------|
| `Action`       | Behavioral output — `action_type`, `payload`, `source_id`, with UUID, timestamp, and status tracking |
| `Observation`  | Structured input from environment — `data`, `source_id`, optional `target_id` and `step`             |
| `StepResult`   | Result of one atomic `perceive → decide → act` cycle                                                 |
| `TurnResult`   | Result of a turn containing multiple `StepResult` entries                                            |
| `PlayerConfig` | `name`, `identity`, `group_tags`, `extras`                                                           |
| `PlayerState`  | Private state container — turn/step counters, timing, `custom_state` dict, message inbox             |

### Abstract Contract

Subclasses of `BasePlayer` implement three methods:

```
perceive(observation, prev_result) → None       # Update internal state
decide()                          → PayloadType # Core decision logic
act(decision_payload)             → Action      # Produce Action
```

The framework composes these into `step()` and `turn()` automatically.

### Key Design Properties

- **Information Asymmetry**: Player state is private and invisible to other Players.
- **Role-Based Coordination**: Players with `role='coordinator'` execute first and can coordinate other players.
- **Unified Interface**: All agents use the same `perceive → decide → act` pattern.

### Built-in Implementations

| Class            | Behavior                                       |
|------------------|------------------------------------------------|
| `GeneralPlayer`  | Configurable via `extras["strategy"]`          |
| `EchoPlayer`     | Echoes observations as actions                 |
| `NoOpPlayer`     | Always produces no-op actions                  |
| `ReactivePlayer` | Triggers actions based on `extras["triggers"]` |

## Coordination (Unified Player Architecture)

In MASim, **coordinators are Players** with `role='coordinator'` in their config. There is no separate Conductor class.

### How Coordination Works

1. **Config-Based Role**: Players with `role='coordinator'` are distinguished at config level:
   ```yaml
   players:
     market_coordinator:
       role: coordinator  # <-- Executes first in each round
       class: examples.Demo.coordinator:SimpleMarketCoordinator
     player_1:
       role: player       # <-- Executes after coordinators (default)
   ```

2. **Execution Order**: Coordinators execute first, then regular players.

3. **Same Interface**: Coordinators use the same `perceive → decide → act` pattern.

### Supported Coordination Modes

| Mode                      | Description                                        |
|---------------------------|----------------------------------------------------|
| **No Coordinator**        | Peer-to-peer mode, all players execute in parallel |
| **Single Coordinator**    | Traditional hierarchical coordination              |
| **Multiple Coordinators** | Multi-level coordination hierarchy (future)        |

### Design Properties

- **Information Asymmetry**: Coordinators can see aggregated player responses.
- **Coordinator-First Execution**: Coordinators run first to prepare state for regular players.
- **Same Infrastructure**: Coordinators use the same Persona/Proxy infrastructure as regular players.

## Proxy (`masim/proxy/`)

Four micro-proxies provide single-responsibility infrastructure primitives:

| Proxy                | Responsibility           | Key Operations                                    |
|----------------------|--------------------------|---------------------------------------------------|
| `CommunicationProxy` | Message routing          | `send()`, `broadcast()`, `subscribe()`            |
| `StorageProxy`       | State persistence        | `checkpoint()`, `restore()`, `list_checkpoints()` |
| `ResourceProxy`      | MCP protocol integration | `fetch_resource()`, `invoke_tool()`               |
| `ObservabilityProxy` | Metrics and logging      | `log_event()`, `record_metric()`, `get_metrics()` |

Each proxy follows a common pattern:

- **`ProxyConfig`** subclass for typed configuration.
- **`ProxyResult`** wrapper enabling `result.success` / `result.data` / `result.error_code` for graceful degradation.
- **`ObservableEntity`** protocol — the minimal interface a proxy owner must expose (`identity`, `on_message()`, `save_state()`, `load_state()`, `get_capabilities()`).
- **`ProxyFactory`** for batch creation from configuration.

## Communication (`masim/communication/`)

| Symbol                          | Role                                                                                                            |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `Message`                       | Standard format: `message_type`, `sender_id`, `payload`, `recipient_id`, `priority`, `correlation_id`           |
| `MessageType`                   | `OBSERVATION`, `ACTION`, `COORDINATION`, `PEER`, `SYSTEM`, `BROADCAST`                                          |
| `MessagePriority`               | `LOW`, `NORMAL`, `HIGH`, `CRITICAL`                                                                             |
| `BaseProtocol` / `JsonProtocol` | Serialization layer for encoding/decoding messages                                                              |
| `MessageRouter`                 | Routes messages to registered handlers by entity ID                                                             |
| Builder functions               | `build_observation_message()`, `build_action_message()`, `build_coordination_message()`, `build_peer_message()` |

All cross-component messages conform to the `Message` format. Custom objects, closures, and mixed formats are prohibited.

## Utils (`masim/utils/`)

| Symbol                      | Role                                                                                           |
|-----------------------------|------------------------------------------------------------------------------------------------|
| `load_config()`             | Load YAML with `!include` tag support and `${VAR:-default}` environment variable interpolation |
| `validate_config()`         | Validate required sections, player structure, topology constraints                             |
| `build_connection_matrix()` | Build `source_id → {target_ids}` adjacency from topology config                                |
| `ConnectionValidator`       | Enforce topology at runtime: `can_send()`, `can_broadcast()`, `validate_send()`                |
| `setup_logging()`           | Configure Python logging with MASim defaults                                                   |
| `IncludeLoader`             | Custom YAML loader resolving `!include` paths relative to the including file                   |

## Configuration (`configs/`)

Configuration uses a modular `!include` pattern:

```
configs/Demo/
├── simulation.yml    # Top-level: setting, ray, environment, logging
├── players.yml       # Player definitions (class path + config), includes coordinators
└── topology.yml      # Communication topology (star/mesh/custom + connections)
```

`simulation.yml` top-level keys map directly to `SimulationConfig` fields:

```yaml
setting:     # name, total_rounds, entry_limit, steps_per_turn, etc.
ray:         # address, namespace, num_cpus, dashboard, actor_options, etc.
players:     !include players.yml  # Includes coordinators with role='coordinator'
topology:    !include topology.yml
```

## Ray Integration

MASim is **natively Ray-based** — there is no runtime-agnostic abstraction layer.

- `ensure_ray()` initializes the Ray cluster from the `ray` config dict.
- `get_actor_name()` produces deterministic actor names: `{simulation_name}::{entity_id}`.
- `load_class()` dynamically imports player classes from `"module.path:ClassName"` strings.
- All Personas are launched as **detached Ray actors** within a shared namespace.
- `ray.get()` is used for synchronous result collection; `ray.remote()` for parallel dispatch.

## Execution Flow

```
run_simple_simulation.py
│
├─ load_config("simulation.yml")
├─ SimulationConfig(**yaml_config)
├─ GeneralSimulator(sim_config)
│
├─ simulator.setup()
│   ├─ ensure_ray(config.ray)
│   ├─ _launch_player_personas()    # ray.remote → detached actors
│   │   └─ Separates coordinators from regular players
│   └─ initialize all actors
│
├─ simulator.run()
│   └─ for round in 1..total_rounds:
│       ├─ Phase 1: coordinator_persona.operate() (if coordinators exist)
│       │   └─ Player.turn() → step() × num_steps
│       ├─ Phase 2: player_persona.operate() [parallel via Ray]
│       │   └─ Player.turn() → step() × num_steps
│       │       └─ perceive → decide → act → StepResult
│       └─ Phase 3: Collect results, record history
│
└─ simulator.shutdown()
    └─ shutdown all actor handles
```

## Extending the Framework

To create a new simulation, implement two classes and provide YAML configuration:

**1. Custom Player** — subclass `BasePlayer`:

```python
class MyPlayer(BasePlayer):
    async def perceive(self, observation, prev_result=None):
        self._state.set_custom("data", observation.data)

    async def decide(self):
        return {"action": "buy", "qty": 100}

    async def act(self, decision):
        return Action(action_type="trade", payload=decision, source_id=self.identity)
```

**2. Custom Coordinator** — subclass `BasePlayer` with `role='coordinator'`:

```python
class MyCoordinator(BasePlayer):
    async def perceive(self, observation, prev_result=None):
        """Process observations from simulator."""
        self.state.set_custom("round", observation.step)

    async def decide(self):
        """Prepare coordination message for players."""
        return {"market_state": ..., "round": self.state.get_custom("round")}

    async def act(self, decision):
        """Broadcast coordination decision."""
        return Action(
            action_type="coordinate", 
            payload=decision, 
            source_id=self.identity,
            metadata={"role": "coordinator"}
        )
```

**3. YAML Configuration** — reference the classes via module path:

```yaml
# players.yml
market_coordinator:
  class: "my_module.coordinator:MyCoordinator"
  name: "Market Coordinator"
  config:
    identity: "coordinator"
    role: coordinator  # <-- Executes first in each round

agent_1:
  class: "my_module.players:MyPlayer"
  name: "Agent 1"
  config:
    identity: "agent_1"
    role: player  # <-- Default, executes after coordinators
```
