# Step 3: Create Configuration Files

## Purpose

Externalize all parameters into YAML configuration files. No hardcoded values in Python code — every numeric threshold, position size, and parameter must be readable from `players.yml`.

---

## Contract (Inputs / Outputs / Polish Hooks)

This block is the **stable I/O declaration** for Step 3. Both
`masim/skills/create-simulation-pipeline.md` and
`masim/skills/polish-simulation-pipeline.md` anchor to it.

**Inputs (consumed).**

| Source                                                | Used for                                                        |
|-------------------------------------------------------|-----------------------------------------------------------------|
| Target §9 Parameter Seeds                             | authoritative default values for every extras key               |
| Target §10.1 Variants to Build                        | determines which `configs/{ScenarioName}/{V}/` folders are created |
| `simulation-bases.md §4.{N}.7 Parameters` (per agent) | any per-agent override of the target §9 default                 |
| `simulation-bases.md §6 Parameter Table`              | scenario-wide environment-level parameter values (finance appendix: market-level) |

**Outputs (produced).**

| Artefact                                                            | Extent of write                                       |
|---------------------------------------------------------------------|-------------------------------------------------------|
| `configs/{ScenarioName}/{V}/simulation.yml`                          | scenario-level config (rounds, agents, output paths) |
| `configs/{ScenarioName}/{V}/players.yml`                             | one entry per agent; each `extras.*` key echoes target §9 verbatim, with `# Source: target §9 / §4.{N}.7 / §6` comment |
| `configs/{ScenarioName}/{V}/topology.yml`                            | communication topology per §8.2 broadcast fields     |
| `configs/{ScenarioName}/{V}/persona.yml` (LLM-based variants only)  | persona seed — pointer to `{V}/prompts.py` (finance-default LLM-based variants: LLM / RuleLLM / Rag) |

**Polish Hooks (what a polish audit re-verifies against this step).**
When `polish-simulation-pipeline.md` audits Step 3, it MUST re-run
these four checks — no new configs are added:

1. Every YAML file parses cleanly (`python -c "import yaml; yaml.safe_load(open(...))"`).
2. Every `extras.*` key has a `# Source:` comment resolvable to target §9, `simulation-bases.md §4.{N}.7`, or §6.
3. No default value in any config disagrees with target §9 (the target file is authoritative — configs are echoes).
4. Every variant folder marked `Yes` in target §10.1 has all required YAML files present; variants marked `No` MUST NOT have a config folder.

---

## 3.1 Configuration Principles

| Principle                    | Rule                                                     | Rationale                                     |
|------------------------------|----------------------------------------------------------|-----------------------------------------------|
| No hardcoded values          | Every numeric value read from `extras` in `players.yml`  | Enables parameter sweeps without code changes |
| Source citations in comments | Every parameter has a `# Source: ...` YAML comment       | Links config to academic justification        |
| Consistent paths             | `EXPERIMENT/{SimName}/{Variant}/` pattern everywhere     | Enables automated analysis                    |
| Per-variant configs          | Each variant has its own directory with all 4 YAML files | Some parameters differ across variants        |

---

## 3.2 Directory Structure

The variant folder set is declared in target §10.1 Variant Build Matrix. Only variants marked `Yes` receive a config folder. The finance-default four-variant tree is:

```
configs/{SimulationName}/
├── Rule/
│   ├── simulation.yml
│   ├── players.yml
│   ├── topology.yml
│   └── persona.yml
├── LLM/
│   └── [same 4 files]
├── RuleLLM/
│   └── [same 4 files]
└── Rag/
    └── [same 4 files]
```

**Reference**: Copy from a prior scenario's `configs/{PriorScenario}/{V}/` folder in the same domain (finance-default reference: `configs/AssetBubble/Rule/`) and adapt.

---

## 3.3 `simulation.yml` Template

```yaml
# {SimulationName} {Variant} Simulation Configuration
# Phenomenon: [Description from simulation-bases.md §1]
# Theories: [List from simulation-bases.md §2]
# Usage: python examples/{Sim}/{Variant}/run_{name}[_suffix].py -c configs/{Sim}/{Variant}/simulation.yml

setting:
  name: "{sim_name}_{variant}"
  description: "[phenomenon description]"
  total_rounds: 200
  record_path: "EXPERIMENT/{SimulationName}/{Variant}/records"
  storage_path: "EXPERIMENT/{SimulationName}/{Variant}/communication"

environment:
  dotenv_path: ".env"
  workspace: "."

ray:
  namespace: "{sim_name}_{variant}"
  object_store_memory: 268435456  # 256MB for Rule; 536870912 (512MB) for LLM/RuleLLM/Rag

players: !include players.yml
topology: !include topology.yml

communication:
  storage_path: "EXPERIMENT/{SimulationName}/{Variant}/communication"
  record_messages: false  # true for debugging only
```

**Notes**:
- `total_rounds: 200` is standard. Use 500 for research-quality runs.
- `object_store_memory`: Rule variant needs less (no LLM context); LLM/RuleLLM/Rag need ≥512MB.
- `record_messages: false` in production; enable only for debugging message flow.

---

## 3.4 `players.yml` Template

```yaml
# {SimulationName} {Variant} Agent Configuration
# Agent architecture: [brief description]
# Theory basis: [list theories from simulation-bases.md §2]

# NOTE: The top-level coordinator key is `environment:` (domain-neutral).
#       Finance appendix (§4.1.F) relabels this key to `market:` and the class to `players:Market`.
environment:
  name: "{Environment Display Name}"
  class: "examples.{SimulationName}.{Variant}.players:{CoordinatorClass}"
  num_instances: 1
  config:
    identity: "environment"
    role: coordinator
    extras:
      # Environment parameters — see simulation-bases.md §3.1 (state update law) and §6
      # Every coefficient must have a `# Source:` citation traceable to target §9.
      # <Finance appendix (§4.1.F) instantiation — Market parameters:
      #   fundamental_value: 100.0    # Normalization — starting intrinsic value
      #   initial_price: 100.0        # Normalization — starting market price
      #   price_impact: 0.03          # λ — Source: Hasbrouck (1991), J. Finance, typical 0.01-0.05
      #   mean_reversion: 0.01        # γ — Source: French & Roll (1986), J. Fin. Econ., typical 0.005-0.02
      #   noise_std: 0.015            # σ — Source: Roll (1984), J. Finance, bid-ask bounce
      # >

{agent_type_1}:
  name: "{Agent Type 1 Display Name}"
  class: "examples.{SimulationName}.{Variant}.players:{ClassName1}"
  num_instances: 2
  config:
    identity: "{agent_identity_1}"
    role: player
    extras:
      # Agent parameters — see simulation-bases.md §4.{N} and §6
      # (finance appendix relabels this comment as "Investor parameters")
      initial_cash: 100000.0
      initial_position: 1000
      {threshold_param}: 0.15     # Source: [Author, Year] — [why this value]
      {size_param}: 0.50          # Source: [Author, Year] — [why this value]

{agent_type_2}:
  name: "{Agent Type 2 Display Name}"
  class: "examples.{SimulationName}.{Variant}.players:{ClassName2}"
  num_instances: 2
  config:
    identity: "{agent_identity_2}"
    role: player
    extras:
      initial_cash: 50000.0
      initial_position: 500
      {threshold_param}: 0.10     # Source: [Author, Year]
      {size_param}: 0.40          # Source: [Author, Year]

# ... repeat for each agent type
```

**Critical requirements**:
- Every numeric `extras` value must have a `# Source: ...` comment linking to simulation-bases.md §6
- `num_instances` controls how many copies of each agent run; typically 1-3 per type
- `identity` is used in records to identify agent type; keep it consistent

---

## 3.5 `topology.yml` Template

```yaml
# {SimulationName} {Variant} Communication Topology
# Star topology: environment coordinator ↔ all agents bidirectional
# (finance appendix: Market ↔ investors)

graph:
  type: star
  center: environment  # finance appendix relabels this identity to `market`

connections:
  - from: environment  # finance appendix: `market`
    to:
      - {agent_identity_1}_0
      - {agent_identity_1}_1
      - {agent_identity_2}_0
      - {agent_identity_2}_1
      # ... all agent instances
    bidirectional: true

broadcast:
  enabled: true
  from: environment  # finance appendix: `market`
  to: all_players
```

**Notes**:
- Instance names follow the pattern `{identity}_{index}` (0-based)
- Must list every instance explicitly
- `bidirectional: true` enables both broadcast (coordinator→agents) and actions (agents→coordinator); finance-appendix instantiation: broadcast (market→investors) and orders (investors→market)

---

## 3.6 `persona.yml` Template

```yaml
# {SimulationName} {Variant} Persistence Configuration
# NOTE: The top-level coordinator key is `environment:` (domain-neutral).
#       Finance appendix (§4.1.F) relabels this key and its record-path stem to `market`.

environment:
  type: proxy
  checkpoint_dir: "EXPERIMENT/{SimulationName}/{Variant}/checkpoints/environment"
  record_path: "EXPERIMENT/{SimulationName}/{Variant}/records/environment"
  monitoring:
    record_path: "EXPERIMENT/{SimulationName}/{Variant}/records/environment/monitor"

{agent_identity_1}:
  type: player
  checkpoint_dir: "EXPERIMENT/{SimulationName}/{Variant}/checkpoints/{agent_identity_1}"
  record_path: "EXPERIMENT/{SimulationName}/{Variant}/records/{agent_identity_1}"
  monitoring:
    record_path: "EXPERIMENT/{SimulationName}/{Variant}/records/{agent_identity_1}/monitor"

# ... repeat for each agent identity
```

---

## 3.7 Rag Variant Additional Configuration

For Rag variant, each agent in `players.yml` needs a `rag` block:

```yaml
{agent_type_rag}:
  name: "{Agent Display Name}"
  class: "examples.{SimulationName}.Rag.players:{ClassName}"
  num_instances: 2
  config:
    identity: "{agent_identity}"
    role: player
    extras:
      # ... all standard parameters
      rag:
        docs_dir: "configs/{SimulationName}/Rag/docs/{agent_identity}/"
        docs_save_dir: "configs/{SimulationName}/Rag/docs_saved/{agent_identity}/"
        rag_persist_dir: "configs/{SimulationName}/Rag/rag_index/{agent_identity}/"
        embed_model: "text-embedding-3-small"
        top_k: 3
```

RAG documents are placed in `configs/{SimulationName}/Rag/docs/{agent_identity}/`. Each agent type should have 2-5 documents:
- Relevant academic papers (PDFs or text excerpts)
- Historical case study summaries (from simulation-bases.md §8)
- Agent type behavior descriptions (finance appendix: investor-type behavior descriptions)

---

## 3.8 Configuration Validation Checklist

After creating all configs:

- [ ] All YAML files parse without errors: `python -c "import yaml; yaml.safe_load(open('configs/.../simulation.yml'))"` 
- [ ] All paths in `simulation.yml` and `persona.yml` are consistent (same base EXPERIMENT path)
- [ ] Every `extras` parameter in `players.yml` has a source citation comment
- [ ] All agent instances are listed in `topology.yml` connections
- [ ] `players.yml` class paths match the actual Python class names in `players.py`
- [ ] LLM-based variants have appropriate `object_store_memory` (≥512MB) — finance-default LLM-based variants: LLM / RuleLLM / Rag
- [ ] If a Rag variant is declared in target §10.1, every agent's `extras` has a `rag:` block
