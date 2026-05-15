# Config Repair

## Purpose

This file specifies how to audit and repair YAML configuration files for all four variants of any simulation. It covers:
- `simulation.yml`
- `persona.yml`
- `topology.yml`
- `players.yml`

The authoritative template is `configs/TEMPLATES/full/`. The canonical working example is `configs/AssetBubble/`. Always verify against both.

---

## §1 Config Audit Scope

For each simulation in the revision list, the config scope depends on task type:

| Task Type                  | Config Action                                                               |
|----------------------------|-----------------------------------------------------------------------------|
| Patch-only                 | No config changes needed                                                    |
| Partial-fill / Full-create | Check all 16 YAML files (4 variants × 4 files)                              |
| Rewrite                    | Only repair configs if they are broken; lean configs usually still function |

**Rule of thumb**: If the simulation currently runs (even with wrong documentation), its configs are likely functional. Focus config repair on simulations where code was modified or where configs are clearly broken.

---

## §2 `simulation.yml` Audit

### §2.1 Required structure

→ Template: `configs/TEMPLATES/full/simulation.yml`
→ Example: `configs/AssetBubble/Rule/simulation.yml`

```yaml
setting:
  name: <scenario_name>_<variant>_simulation
  description: "..."
  record_path: "EXPERIMENT/<Scenario>/<Variant>/records"
  total_rounds: 50
  round_history_limit: 10       # REQUIRED — often missing
  save_diagram_interval: 10     # REQUIRED — often missing

environment:
  use_environment: false

ray:
  namespace: <scenario_name>_<variant>
  actor_prefix: <scenario_name>_<variant>
  object_store_memory: <see table below>  # integer bytes

players: !include players.yml
topology: !include topology.yml

communication:
  storage_path: "EXPERIMENT/<Scenario>/<Variant>/records"
  record_messages: false
  message_block_size: 500       # NOT message_timeout_ms or max_retries
```

### §2.2 `object_store_memory` by variant

| Variant | Value (bytes) | Value (human) |
|---------|---------------|---------------|
| Rule    | `134217728`   | 128 MB        |
| LLM     | `536870912`   | 512 MB        |
| RuleLLM | `536870912`   | 512 MB        |
| Rag     | `1073741824`  | 1 GB          |

### §2.3 Common mistakes to fix

| Problem                     | Wrong                                               | Correct                                |
|-----------------------------|-----------------------------------------------------|----------------------------------------|
| Old storage_path location   | `setting:\n  storage_path: ...`                     | Move to `communication:` block         |
| Old Ray fields              | `ignore_reinit_error`, `num_cpus: 4`, `log_level`   | Remove entirely                        |
| Missing required fields     | No `round_history_limit` or `save_diagram_interval` | Add under `setting:`                   |
| Wrong communication block   | `message_timeout_ms`, `max_retries`                 | Replace with `message_block_size: 500` |
| `object_store_memory: null` | null                                                | Integer bytes (see table above)        |

---

## §3 `persona.yml` Audit

### §3.1 Required structure

→ Template: `configs/TEMPLATES/full/simulation.yml` (persona section)
→ Example: `configs/AssetBubble/Rule/persona.yml`

```yaml
auto_checkpoint: false
debug_mode: true
proxy:
  storage:
    storage_path: "EXPERIMENT/<Scenario>/<Variant>/records"
  monitoring:
    metrics_path: "EXPERIMENT/<Scenario>/<Variant>/metrics"
    enable_metrics: false
  communication:
    message_storage_path: "EXPERIMENT/<Scenario>/<Variant>/records"
  resource:
    resource_path: "EXPERIMENT/<Scenario>/<Variant>/resources"
```

### §3.2 Common mistakes to fix

| Problem                | Wrong                                | Correct                                      |
|------------------------|--------------------------------------|----------------------------------------------|
| Old format             | `personas: []`                       | Full `proxy:` block (see template)           |
| Per-agent entries      | `personas:\n  - id: agent1\n    ...` | This is a shared file — no per-agent entries |
| Missing `proxy:` block | `auto_checkpoint: false` only        | Add complete `proxy:` block                  |

---

## §4 `topology.yml` Audit

### §4.1 Required structure

→ Template: `configs/TEMPLATES/full/topology.yml`
→ Example: `configs/AssetBubble/Rule/topology.yml`

```yaml
type: "star"
sources:
  - market
connections:
  market:
    - agent_key_1
    - agent_key_2
    - agent_key_3
  agent_key_1:
    - market
  agent_key_2:
    - market
  agent_key_3:
    - market
```

### §4.2 Agent key naming by variant

| Variant | Agent Key Pattern      | Example                     |
|---------|------------------------|-----------------------------|
| Rule    | `<agent_type>`         | `momentum_follower`         |
| LLM     | `llm_<agent_type>`     | `llm_momentum_follower`     |
| RuleLLM | `rulellm_<agent_type>` | `rulellm_momentum_follower` |
| Rag     | `ragllm_<agent_type>`  | `ragllm_momentum_follower`  |

### §4.3 Common mistakes to fix

| Problem                        | Wrong                                                  | Correct                                             |
|--------------------------------|--------------------------------------------------------|-----------------------------------------------------|
| Old list-of-dicts format       | `connections:\n  - source: market\n    target: agent1` | Map format: `connections:\n  market:\n    - agent1` |
| Missing `type:` and `sources:` | Only `connections:` block                              | Add `type: "star"` and `sources:\n  - market`       |
| Instance suffixes              | `momentum_follower_1:`                                 | `momentum_follower:` (no suffix)                    |
| Mismatch with players.yml      | Agent key in topology not in players.yml               | Keys must be identical in both files                |
| Class name mismatch with code  | `hedgedfundtrader:` but code class is `HedgedFund`     | Topology key must derive from actual class name     |

> **Historical examples of topology/identity mismatches (fixed 2026-04-29):**
> - CarryTradeUnwind: `cb_intervener` → `hedged_carry_trader` (config referenced non-existent `CentralBankIntervener`)
> - EuropeanDebtCrisis: `hedgedfundtrader` → `hedgedfund` (extra "Trader" suffix)
> - GameStopShortSqueeze: `noisetrader` → `momentumretail` (completely wrong agent name)
> - LTCMCollapse: `noisetrader` → `centralbank` (completely wrong agent name)
> - LossAversion: `dispositiontrader` → `momentumtrader`, `noisetrader` → `marketmaker`

---

## §5 `players.yml` Audit

### §5.1 Market block (all variants)

```yaml
market:
  name: Market
  class: "examples.<Scenario>.<Variant>.players:Market"
  num_instances: 1
  config:
    identity: "market"
    role: coordinator
    steps_per_turn: 1
    group_tags:
      - market
    extras:
      record_path: "EXPERIMENT/<Scenario>/<Variant>/records"
      initial_price: 100.0
      fundamental_value: 100.0
      price_impact: 0.01
      mean_reversion: 0.05
      noise_std: 0.01
      custom_state_hot_limit: 50
  persona: !include persona.yml
```

### §5.2 Rule agent block

```yaml
<agent_type>:
  name: <AgentClassName>
  class: "examples.<Scenario>.Rule.players:<AgentClassName>"
  num_instances: 3
  config:
    identity: "<agent_type>"
    role: player
    steps_per_turn: 1
    group_tags:
      - investors
    extras:
      record_path: "EXPERIMENT/<Scenario>/Rule/records"
      initial_cash: 100000.0
      initial_position: 100
      <scenario_param_1>: <value>
      <scenario_param_2>: <value>
      custom_state_hot_limit: 50
  persona: !include persona.yml
```

### §5.3 LLM / RuleLLM agent block (additions to Rule)

Add `llm:` block inside `extras:`:

```yaml
    extras:
      record_path: "EXPERIMENT/<Scenario>/LLM/records"
      initial_cash: 100000.0
      initial_position: 100
      <scenario_params>: ...
      custom_state_hot_limit: 50
      llm:
        sys_message: "examples.<Scenario>.LLM.prompts:LLM_<TYPE>_SYS"
        user_message: "examples.<Scenario>.LLM.prompts:LLM_USER_TEMPLATE"
        lm_type: "api"
        lm_name: "ark/doubao-seed-1-6-lite-251015"
        generation_config:
          temperature: 0.3
          max_new_tokens: 500
```

Agent key prefix: `llm_<agent_type>` / `rulellm_<agent_type>`
Class prefix: `LLM<Type>` / `RuleLLM<Type>`
Group tags: `[llm_investors]` / `[rulellm_investors]`

### §5.4 Rag agent block (additions to LLM/RuleLLM)

Add `knowledge:` block at file top (before `market:`):

```yaml
knowledge:
  backend: local
  global_uri: "examples/document-sources"
  preprocessing:
    parser: mineru
    output_position: "MinerU_processed"
  rag:
    output_position: "rag_index"
```

Add `private_knowledge:` block inside each agent's `extras:`:

```yaml
    extras:
      ...
      llm:
        ...
        max_new_tokens: 600    # slightly more for RAG context
      private_knowledge:
        from_global_resources:
          - MinerU_processed
        local_resources:
          local_uri: ""
          local_resources: []
        rag:                   # MUST be nested inside private_knowledge, NOT at extras level
          embed_model: "openai/hunyuan-embedding"
          embed_type: "litellm"
          top_k: 3
          chunk_size: 512
          chunk_overlap: 64
          shared_rag_index_dir: "EXPERIMENT/<Scenario>/Rag/rag_index"
```

Agent key prefix: `ragllm_<agent_type>`
Class prefix: `RagLLM<Type>`
Group tags: `[ragllm_investors]`

### §5.5 Common mistakes to fix

| Problem                            | Wrong                                  | Correct                                         |
|------------------------------------|----------------------------------------|-------------------------------------------------|
| Instance suffix in key             | `momentum_follower_1:`                 | `momentum_follower:`                            |
| Missing `steps_per_turn`           | omitted                                | `steps_per_turn: 1`                             |
| Missing `group_tags`               | omitted                                | `group_tags:\n  - investors`                    |
| Missing `custom_state_hot_limit`   | omitted                                | `custom_state_hot_limit: 50`                    |
| Old LLM format                     | `llm: {'model': ..., 'api_key': ...}`  | Full `llm:` block with `sys_message`, `lm_name` |
| Wrong class path                   | `Rule.players:Market` in LLM config    | `LLM.players:Market`                            |
| `rag:` at extras level             | `extras:\n  rag:`                      | `extras:\n  private_knowledge:\n    rag:`       |
| Missing `knowledge:` at top        | Not present in Rag players.yml         | Add `knowledge:` block before `market:`         |
| Wrong prompt module path           | `RuleLLM.prompts:RULELLM_X_SYS` in Rag | `Rag.prompts:RAG_X_SYS`                         |
| Missing `LLM_USER_TEMPLATE` export | Not in Rag/prompts.py                  | Add `LLM_USER_TEMPLATE = RAG_USER_TEMPLATE`     |

---

## §6 Cross-Consistency Check

After repairing configs, verify cross-consistency across **all 4 variants** (Rule, LLM, RuleLLM, Rag):

### §6.1 Automated triple-consistency audit

For each `players.yml`, verify that every `class:` reference resolves to an actual class (defined or imported) in the target `players.py`:

```python
# Extract class: "module.path:ClassName" from players.yml
# Import the module, verify getattr(module, ClassName) exists
# If not: the config is WRONG — fix the class name to match code
```

### §6.2 Automated extras-key audit

For each player in `players.yml`, extract the `extras:` keys. For the corresponding class in `players.py`, extract all `extras["key"]` accesses. Every key accessed in code **must** be present in that player's `extras:` section. Missing keys cause `KeyError` at runtime.

**Per-player check** (not union): verify each player's extras independently. Player A accessing `key_x` is only valid if Player A's yml extras defines `key_x` — not if some other player defines it.

> **Extras key mismatch inventory (fixed 2026-02-03):**
>
> **Category B — Rule investor parameter name mismatches (13 fixes):**
> - CarryTradeUnwind/Rule: `CarryTrader` needed `leverage` (added); `FundingCurrencyBuyer` needed `position_size` (renamed from `risk_buy_size`)
> - EndowmentEffect/Rule: `EndowedHolder` needed `sell_reluctance` (added); `StatusQuoSeller` needed `status_quo_threshold` (renamed from `status_quo_premium`)
> - EuropeanDebtCrisis/Rule: 5 investors had wrong key names (`panic_threshold`→`sell_threshold`, `stress_threshold`→`panic_threshold`, `value_threshold`→`flight_threshold`, `ecb_threshold`→`intervention_threshold`, `spread_buy_threshold`→`entry_threshold`)
> - FlashCrash2010/Rule: `MomentumChaser` needed `lookback_window` (added)
> - GameStopShortSqueeze/Rule: `MomentumRetail` needed `fomo_threshold` (added)
> - LossAversion/Rule: `MomentumTrader` `profit_trigger`→`entry_threshold`; `MarketMaker` needed `inventory_limit` (added)
>
> **Category A — Rag/RuleLLM Market liquidity-model config gaps (15 fixes):**
> - 8 scenarios × Rag+RuleLLM: Market code used generic liquidity model keys (`base_liquidity`, `base_price_impact`, `high_impact_multiplier`, `low_liquidity_threshold`) but configs lacked them
> - Affected: EquityPremium, HerdEffect, LiquidityDryup, MarketCrash, MomentumEffect, ReversalEffect, ShortSqueeze, VolatilityClustering
> - Also fixed: `price_impact`→`base_price_impact`, `initial_fundamental`→`fundamental_value`, `initial_stock_price`→`initial_price` renames
>
> **Audit t3 — LLM sub-config key mismatches and forbidden `.get()` elimination (2026-04-29):**
>
> **LLM init pattern fix (46 code files):**
> - All LLM/Rag/RuleLLM `players.py` using `llm_cfg["model"]` → fixed to `llm_cfg["lm_name"]`
> - All manually-constructed `generation_config` dicts → fixed to `llm_cfg["generation_config"]`
> - All `llm_cfg.get("generation_config", {})` → fixed to `llm_cfg["generation_config"]`
> - All `extras.get("llm", {})` → fixed to `extras["llm"]`
> - Affected: 46 `players.py` files + 11 `run_*.py` scripts across all LLM-bearing variants
>
> **Forbidden `.get()` elimination (73 code files, 295 occurrences):**
> - All `extras.get("key", default)` → `extras["key"]` across 73 `players.py` files
> - All `self.config.extras.get("key", default)` → `self.config.extras["key"]`
> - Chained fallbacks `private_knowledge.get("rag", extras["rag"])` → `private_knowledge["rag"]`
>
> **Config YAML keys added (53 keys across 11 Rule variant configs):**
> - ConfirmationBias/Rule: 4 investors needed `order_size`, plus `initial_belief`, `confirmation_strength`, `scan_threshold`, `analysis_threshold`
> - CreditCycle/Rule: 4 investors needed `order_size`, plus `credit_multiplier`, `crisis_threshold`, `initial_leverage`, `max_leverage`, `boom_sell_threshold`, `crisis_buy_threshold`
> - CurrencyCrisis/Rule: 4 investors needed `order_size`
> - DotComBubble/Rule: 5 investors needed `order_size`, plus `flip_threshold`, `momentum_threshold`, `value_buy_threshold`, `value_sell_threshold`
> - GFC2008/Rule: `margin_call_trigger`; HindsightBias/Rule: `prediction_overweight`, `failure_discount`, `outcome_weight`, `position_size`
> - LTCMCollapse/Rule: `var_limit`, `intervention_threshold`, `rescue_probability`; LUNACollapse/Rule: `yield_threshold`
> - OverconfidenceBias/Rule: `signal_precision`; RepresentativenessBias/Rule: `base_rate_ignore`, `pattern_sensitivity`, `category_weight`, `sample_bias`, `evidence_weight`, `position_size`
> - Volmageddon/Rule: 5 investors needed `stop_loss`, `rebalance_size`, `rebalance_threshold`, `hedge_ratio`, `entry_threshold`, `risk_limit`

### §6.3 Manual cross-file checks

```bash
# 1. All agent keys in topology.yml match keys in players.yml
# Extract agent keys from players.yml (non-market blocks)
grep "^[a-z_]*:" configs/<Scenario>/Rule/players.yml | grep -v "^market:" | grep -v "^knowledge:"

# Compare with topology.yml connections
grep "^  [a-z_]*:" configs/<Scenario>/Rule/topology.yml

# 2. Class paths in players.yml match class definitions in players.py
grep "class:" configs/<Scenario>/Rule/players.yml

# 3. Prompt paths in players.yml match constants in prompts.py
grep "sys_message:" configs/<Scenario>/LLM/players.yml
grep "^LLM_\|^RULELLM_\|^RAG_" examples/<Scenario>/LLM/prompts.py

# 4. record_path in extras matches setting.record_path in simulation.yml
grep "record_path" configs/<Scenario>/Rule/players.yml
grep "record_path" configs/<Scenario>/Rule/simulation.yml
```

---

## §7 Quick Reference: Path Naming Conventions

| Purpose                | Pattern                                               | Example                                                         |
|------------------------|-------------------------------------------------------|-----------------------------------------------------------------|
| EXPERIMENT record path | `EXPERIMENT/<Scenario>/<Variant>/records`             | `EXPERIMENT/DotComBubble/LLM/records`                           |
| Ray namespace          | `<scenario_name>_<variant>`                           | `dot_com_bubble_llm`                                            |
| Simulation name        | `<scenario_name>_<variant>_simulation`                | `dot_com_bubble_llm_simulation`                                 |
| Player key (Rule)      | `<agent_type>`                                        | `momentum_follower`                                             |
| Player key (LLM)       | `llm_<agent_type>`                                    | `llm_momentum_follower`                                         |
| Player key (RuleLLM)   | `rulellm_<agent_type>`                                | `rulellm_momentum_follower`                                     |
| Player key (Rag)       | `ragllm_<agent_type>`                                 | `ragllm_momentum_follower`                                      |
| Class path             | `"examples.<Scenario>.<Variant>.players:<ClassName>"` | `"examples.DotComBubble.LLM.players:LLMMomentumFollower"`       |
| Prompt path            | `"examples.<Scenario>.<Variant>.prompts:<CONSTANT>"`  | `"examples.DotComBubble.LLM.prompts:LLM_MOMENTUM_FOLLOWER_SYS"` |

---

## §8 Variant-Specific Config Rules

### §8.1 Rule Variant

- `players.yml`: no `llm:` block anywhere, no `knowledge:` block
- `topology.yml`: uses base agent keys without prefix (e.g., `momentum_follower`)
- Market class path: `"examples.<Scenario>.Rule.players:Market"`
- All agent keys use plain underscore names

### §8.2 LLM Variant

- `players.yml`: has `llm:` block, no `knowledge:`, no `private_knowledge:`
- Market class path: `"examples.<Scenario>.LLM.players:Market"`
- Agent keys: `llm_<agent_type>`
- Class names: `LLM<Type>`
- `group_tags: [llm_investors]`

### §8.3 RuleLLM Variant

- Identical structure to LLM variant
- Market class path: `"examples.<Scenario>.RuleLLM.players:Market"`
- Agent keys: `rulellm_<agent_type>`
- Class names: `RuleLLM<Type>`
- `group_tags: [rulellm_investors]`

### §8.4 Rag Variant

- `players.yml`: has `knowledge:` at top before `market:`, `private_knowledge:` in each agent's extras
- Agent keys: `ragllm_<agent_type>`
- Class names: `RagLLM<Type>`
- `group_tags: [ragllm_investors]`
- `max_new_tokens: 600` (slightly more due to RAG context)

**Critical rules**:
- `rag:` MUST be nested inside `private_knowledge:` — NOT at the same level as `private_knowledge:`, NOT at the `extras:` level
- `knowledge:` block goes at file top, before `market:`

---

## §9 Common Config Errors — Quick Reference

| Error                               | Wrong                                                                      | Correct                                                            |
|-------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------|
| Old topology format                 | `connections: [{source: x, target: y}]`                                    | `connections: {x: [y], y: [x]}`                                    |
| Missing topology header             | No `type:` or `sources:`                                                   | `type: "star"\nsources:\n  - market`                               |
| Old persona format                  | `personas: []`                                                             | Full `proxy:` block structure                                      |
| Old simulation format               | `num_cpus: 4`, `log_level: INFO`                                           | Remove; use template structure                                     |
| Wrong `communication:` fields       | `message_timeout_ms`, `max_retries`                                        | Use `message_block_size: 500`                                      |
| Old LLM config format               | `llm: {'model': ..., 'api_key': ...}`                                      | `llm:\n  sys_message: ...\n  lm_name: ...`                         |
| Wrong llm sub-config key in code    | `llm_cfg["model"]` or manual `{"temperature": ...}`                        | `llm_cfg["lm_name"]` and `llm_cfg["generation_config"]`            |
| Forbidden `.get()` on config extras | `extras.get("key", default)` masks missing config keys                     | `extras["key"]` — fail-fast, config MUST provide the key           |
| Instance suffix in key              | `agent_type_1:` as YAML key                                                | `agent_type:` (no suffix in players.yml)                           |
| `rag:` at wrong nesting             | `extras:\n  rag:`                                                          | `extras:\n  private_knowledge:\n    rag:`                          |
| Missing `num_instances`             | omitted                                                                    | Required for every player                                          |
| Wrong class path                    | `Rule.players:Market` in LLM config                                        | `LLM.players:Market`                                               |
| Wrong topology key                  | `momentum_follower_1` (with suffix)                                        | `momentum_follower` (no suffix)                                    |
| Class name mismatch with code       | `class: "...players:NoiseTrader"` but code has `MomentumRetail`            | `class: "...players:MomentumRetail"` — match `simulation-bases.md` |
| Config extras key mismatch          | `extras: {sell_size: 60}` but code reads `extras["base_size"]`             | Key names must exactly match code accesses                         |
| Extras key rename without updating  | `profit_trigger:` in yml but code reads `extras["entry_threshold"]`        | Rename yml key to match `simulation-bases.md` → code               |
| Rag/RuleLLM Market missing keys     | Rag Market uses liquidity model but config has Rule-style keys             | Add `base_liquidity`, `low_liquidity_threshold` etc. to config     |
| Wrong variant class prefix          | `LLMFoo` class in Rag config                                               | `RagLLMFoo` — Rag uses `RagLLM` prefix, RuleLLM uses `RuleLLM`     |
| Identity/topology mismatch          | `identity: "cb_intervener"` but topology uses `hedged_carry_trader`        | Identical names in players.yml identity AND topology.yml           |
| Stale comments after rename         | `# CentralBankIntervener parameters` after renaming to `HedgedCarryTrader` | Update ALL comments when renaming agents                           |
| Missing `steps_per_turn`            | omitted from any player block                                              | `steps_per_turn: 1`                                                |
| Missing `group_tags`                | omitted from any player block                                              | `group_tags:\n  - investors`                                       |
| Missing `custom_state_hot_limit`    | omitted from extras                                                        | `custom_state_hot_limit: 50`                                       |
| Old storage_path location           | `setting:\n  storage_path: ...`                                            | Move to `communication:` block                                     |
| `object_store_memory: null`         | null                                                                       | Integer bytes per §2.2 table                                       |
| Wrong prompt module path            | `RuleLLM.prompts:RULELLM_X_SYS` in Rag config                              | `Rag.prompts:RAG_X_SYS`                                            |
| Missing `LLM_USER_TEMPLATE` export  | Not in `Rag/prompts.py`                                                    | Add `LLM_USER_TEMPLATE = RAG_USER_TEMPLATE`                        |
