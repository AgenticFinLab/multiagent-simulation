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
│   └── general.py           # PlayerPersona, ConductorPersona
├── player/                  # L3: Autonomous agent domain logic
│   ├── base.py              # Abstract BasePlayer, Action, Observation, PlayerConfig, PlayerState
│   └── general.py           # GeneralPlayer, EchoPlayer, NoOpPlayer, ReactivePlayer
├── conductor/               # L3: Coordination domain logic
│   ├── base.py              # Abstract BaseConductor, CoordinationDecision, ConductorConfig
│   └── general.py           # GeneralConductor, PassThroughConductor, BroadcastConductor
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
│  Layer 1: Player / Conductor  (WHAT)                               │
│  Pure domain logic — perceive → decide → act                       │
│  ZERO infrastructure knowledge, ZERO proxy references              │
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
| **Why does Persona own proxy_config?**       | Centralized configuration. Player/Conductor don't need to know proxy details. Changing storage backend only affects Persona config.     |

### Layer Responsibilities

| Layer                | Responsibility             | Knows About          | Hidden From                       |
|----------------------|----------------------------|----------------------|-----------------------------------|
| **Player/Conductor** | Domain logic (WHAT to do)  | Only `self._persona` | Proxies, Ray, configs             |
| **Persona**          | Coordination (WHEN to do)  | All 4 proxies, Ray   | Implementation details of proxies |
| **Proxy**            | Infrastructure (HOW to do) | Specific backend     | Domain logic                      |

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
└── conductor: (same structure)
```

**Key Rule**: `proxy_config` is EXCLUSIVELY owned by Persona. Player/Conductor never see it.

## Hierarchical Execution Model

```
┌──────────┬────────────────────┬───────────┬──────────────────────────────┐
│  Level   │  Entity            │  Term     │  Description                 │
├──────────┼────────────────────┼───────────┼──────────────────────────────┤
│  L1      │  Simulator         │  round    │  Orchestrates all Personas   │
│  L2      │  PlayerPersona     │  operate  │  Calls Player.turn()         │
│  L3      │  Player            │  turn     │  Loop of step() calls        │
│  L4      │  Player            │  step     │  perceive → decide → act     │
│  L2      │  ConductorPersona  │  cycle    │  receive → analyze →         │
│          │                    │           │  coordinate                  │
└──────────┴────────────────────┴───────────┴──────────────────────────────┘
```

A single **round** progresses through three phases:

1. **NOTIFICATION** — Conductor notifies all Players of round state.
2. **PLAYER_DECISION** — All PlayerPersonas execute `operate()` in parallel (Ray).
3. **COORDINATION** — ConductorPersona collects response_pool and executes `cycle()`, broadcasts decision.

## Execution Granularity

The framework uses a strict hierarchical time model where each level has its own clock for traceability. The nesting relationship is:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ROUND (Simulator)                                                       ║
║  • One complete simulation cycle across ALL entities                     ║
║  • Progresses through phases: NOTIFICATION → PLAYER_DECISION → COORDINATION ║
║  • Tracked by: round_clock (ExecutionClock)                              ║
╠═════════════════════════════════════╣═════════════════════════════════════╣
║  OPERATE (PlayerPersona)            ║  CYCLE (ConductorPersona)          ║
║  • Simulator-facing interface       ║  • Simulator-facing interface       ║
║  • Invokes Player.turn()            ║  • notify → collect → analyze      ║
║  • Returns: TurnResult              ║    → coordinate                    ║
║                                     ║  • Returns: CycleResult             ║
╠═════════════════════════════════════╩═════════════════════════════════════╣
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

| Term        | Owner            | Description                                                                | Output      | Clock         |
|-------------|------------------|----------------------------------------------------------------------------|-------------|---------------|
| **round**   | Simulator        | One complete simulation cycle; all players act, then conductor coordinates | RoundResult | `round_clock` |
| **operate** | PlayerPersona    | Facade method called by Simulator; invokes `turn()` internally             | TurnResult  | (delegates)   |
| **turn**    | Player           | Batch of `step()` calls; iterates with `prev_result` chaining              | TurnResult  | `turn_clock`  |
| **step**    | Player           | Atomic unit: `perceive() → decide() → act()`                               | StepResult  | `step_clock`  |
| **cycle**   | ConductorPersona | Conductor's coordination unit: `analyze(responses) → coordinate`           | CycleResult | `cycle_clock` |

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
├── Phase: NOTIFICATION
│   └── conductor.notify() → {player_id: notification_dict}
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
├── Phase: COORDINATION
│   └── ConductorPersona.cycle()
│       ├── collect_census(all_actions)
│       ├── analyze() → analysis_result
│       └── coordinate(analysis) → CoordinationDecision
│       → CycleResult
│
└── Phase: COMPLETE
    └── Broadcast decision to all players

Round 2 ...
```

### Design Rationale

1. **Stateful Step Chaining**: Each `step()` receives `prev_result` from the previous step, enabling iterative refinement (e.g., multi-round negotiation, progressive reasoning).

2. **Isolation Boundaries**: Simulator only sees `operate()` / `cycle()`; it has no knowledge of the internal `turn` / `step` structure. This preserves encapsulation.

3. **Parallel Execution**: All `PlayerPersona.operate()` calls within a round execute in parallel via Ray; the Conductor waits for all to complete before coordination.

4. **Clock Hierarchy**: Each level tracks its own timing independently, enabling fine-grained performance analysis and debugging.

## Simulator (`masim/simulator/`)

The Simulator is a **pure orchestrator**. It does not generate observations, execute actions, or interpret domain semantics.

| Symbol             | Role                                                                                                               |
|--------------------|--------------------------------------------------------------------------------------------------------------------|
| `SimulatorStatus`  | Enum: `INITIALIZING → READY → RUNNING → PAUSED → TERMINATED → ERROR`                                               |
| `RoundPhase`       | Enum: `NOTIFICATION → PLAYER_DECISION → COORDINATION → COMPLETE`                                                   |
| `ExecutionClock`   | Hierarchical time tracking (`tick_start` / `tick_end`)                                                             |
| `SimulationConfig` | Dataclass whose fields match `simulation.yml` top-level keys: `setting`, `ray`, `players`, `conductor`, `topology` |
| `BaseSimulator`    | Abstract — subclasses implement `create_player_personas()` and `create_conductor_persona()`                        |
| `GeneralSimulator` | Concrete — Ray cluster init, actor launching, round loop                                                           |

Configuration loading:

```python
yaml_config = load_config("configs/Demo/simulation.yml")
sim_config = SimulationConfig(**yaml_config)
```

## Persona (`masim/persona/`)

Persona is the **primary external interface** that the Simulator interacts with. Player and Conductor are completely hidden behind their respective Personas as internal implementation details.

| Symbol             | Role                                                                                                |
|--------------------|-----------------------------------------------------------------------------------------------------|
| `BasePersona`      | Abstract — proxy aggregation, `fetch_resource()`, `log_event()`                                     |
| `PersonaConfig`    | `auto_checkpoint`, `debug_mode`, `env_overrides`                                                    |
| `PlayerPersona`    | Wraps `BasePlayer`, exposes `operate()` / `initialize()` / `shutdown()` / `get_state_snapshot()`    |
| `ConductorPersona` | Wraps `BaseConductor`, exposes `cycle()` / `notify()` / `receive_responses()` / `register_player()` |

At runtime, both Persona types are deployed as **Ray actors** with detached lifetime.

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

- **Information Asymmetry**: Player state is private and invisible to Conductor and other Players.
- **Capability Parity**: Player and Conductor have equal infrastructure access (same proxy set via Persona); they differ only in output type.

### Built-in Implementations

| Class            | Behavior                                       |
|------------------|------------------------------------------------|
| `GeneralPlayer`  | Configurable via `extras["strategy"]`          |
| `EchoPlayer`     | Echoes observations as actions                 |
| `NoOpPlayer`     | Always produces no-op actions                  |
| `ReactivePlayer` | Triggers actions based on `extras["triggers"]` |

## Conductor (`masim/conductor/`)

A Conductor is defined by its behavioral contract: it produces `CoordinationDecision` objects that **indirectly influence** Players. It cannot directly act on the environment.

### Core Data Types

| Type                   | Description                                                                        |
|------------------------|------------------------------------------------------------------------------------|
| `CoordinationDecision` | `decision_type`, `scope` (GLOBAL/GROUP/INDIVIDUAL), `parameters`, `source_id`      |
| `CycleResult`          | Result of one `analyze(responses) → coordinate` cycle                              |
| `DecisionScope`        | Enum: `GLOBAL`, `GROUP`, `INDIVIDUAL`                                              |
| `ConductorConfig`      | `identity`, `coordination_mode`, `extras`                                          |
| `ConductorState`       | Globally visible — cycle counter, player registry, response_pool, decision history |

### Abstract Contract

Subclasses of `BaseConductor` implement:

```
notify(round_num, player_ids)      → Dict[str, Dict]      # Conductor → Players
analyze(responses)                 → Dict[str, Any]       # Process responses
coordinate(analysis_result)        → CoordinationDecision
```

The framework composes `analyze(responses) → coordinate` into `cycle()` automatically.

Note: `notify()` is called BEFORE players act; responses are collected via streaming.

### Key Design Properties

- **Global Visibility**: Conductor state is transparent (unlike Player's private state).
- **Notification Ownership**: The Conductor notifies Players because it has global visibility and controls information asymmetry.
- **Response-based Coordination**: Conductor collects "response_pool" (aggregated responses from Players) before analysis.
- **Contract Enforcement**: `_validate_decision()` rejects decision types that would directly act on the environment.

### Built-in Implementations

| Class                  | Behavior                             |
|------------------------|--------------------------------------|
| `GeneralConductor`     | Configurable coordination logic      |
| `PassThroughConductor` | No coordination, passes through      |
| `ThrottlingConductor`  | Applies throttling based on activity |
| `BroadcastConductor`   | Broadcasts decisions to all players  |

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
| `validate_config()`         | Validate required sections, player/conductor structure, topology constraints                   |
| `build_connection_matrix()` | Build `source_id → {target_ids}` adjacency from topology config                                |
| `ConnectionValidator`       | Enforce topology at runtime: `can_send()`, `can_broadcast()`, `validate_send()`                |
| `setup_logging()`           | Configure Python logging with MASim defaults                                                   |
| `IncludeLoader`             | Custom YAML loader resolving `!include` paths relative to the including file                   |

## Configuration (`configs/`)

Configuration uses a modular `!include` pattern:

```
configs/Demo/
├── simulation.yml    # Top-level: setting, ray, environment, logging
├── players.yml       # Player definitions (class path + config)
├── conductor.yml     # Conductor definition (class path + config)
└── topology.yml      # Communication topology (star/mesh/custom + connections)
```

`simulation.yml` top-level keys map directly to `SimulationConfig` fields:

```yaml
setting:     # name, total_rounds, entry_limit, steps_per_turn, etc.
ray:         # address, namespace, num_cpus, dashboard, actor_options, etc.
players:     !include players.yml
conductor:   !include conductor.yml
topology:    !include topology.yml
```

## Ray Integration

MASim is **natively Ray-based** — there is no runtime-agnostic abstraction layer.

- `ensure_ray()` initializes the Ray cluster from the `ray` config dict.
- `get_actor_name()` produces deterministic actor names: `{simulation_name}::{entity_id}`.
- `load_class()` dynamically imports player/conductor classes from `"module.path:ClassName"` strings.
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
│   ├─ create_player_personas()     # load_class → PlayerPersona
│   ├─ _launch_player_personas()    # ray.remote → detached actors
│   ├─ create_conductor_persona()   # load_class → ConductorPersona
│   ├─ _launch_conductor_persona()  # ray.remote → detached actor
│   ├─ register all players with conductor
│   └─ initialize all actors
│
├─ simulator.run()
│   └─ for round in 1..total_rounds:
│       ├─ Phase 1: conductor.notify()           # Conductor → Players
│       ├─ Phase 2: player_persona.operate() [parallel via Ray]
│       │   └─ Player.turn() → step() × num_steps
│       │       └─ perceive → decide → act → StepResult
│       ├─ Phase 3: conductor.receive_responses() → cycle()  # Players → Conductor
│       │   └─ analyze(responses) → coordinate → CycleResult
│       └─ broadcast coordination decision to all players
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

**2. Custom Conductor** — subclass `BaseConductor`:

```python
class MyMarket(BaseConductor):
    def notify(self, round_num, player_ids):
        """Notify players of round state (Conductor → Players)."""
        return {pid: {"data": {...}, "source_id": self.identity, "num_steps": 1}
                for pid in player_ids}

    async def analyze(self, responses):
        """Analyze responses from players."""
        return {"summary": ..., "count": len(responses)}

    async def coordinate(self, analysis):
        """Produce CoordinationDecision."""
        return CoordinationDecision(
            decision_type="price_update", scope=DecisionScope.GLOBAL,
            parameters=analysis, source_id=self.identity)
```

**3. YAML Configuration** — reference the classes via module path:

```yaml
# players.yml
agent_1:
  class: "my_module.players:MyPlayer"
  name: "Agent 1"
  config:
    identity: "agent_1"

# conductor.yml
class: "my_module.conductor:MyMarket"
name: "My Market"
config:
  identity: "market"
```
