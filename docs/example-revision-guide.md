# Example Revision Guide

A comprehensive reference for auditing, correcting, and extending scenario implementations in `examples/` and `configs/`. This guide covers the complete pipeline from theory to configuration to code, using `examples/AssetBubble` as the canonical working reference.

---

## Table of Contents

1. [Overview and Reference Architecture](#1-overview-and-reference-architecture)
2. [Directory Structure Contract](#2-directory-structure-contract)
3. [Theory-to-Agent Mapping (explain.md Audit)](#3-theory-to-agent-mapping)
4. [Python Code Standards](#4-python-code-standards)
5. [Configuration File Standards](#5-configuration-file-standards)
6. [Variant-Specific Rules](#6-variant-specific-rules)
7. [Common Errors and Fixes](#7-common-errors-and-fixes)
8. [Step-by-Step Audit Checklist](#8-step-by-step-audit-checklist)
9. [Scenario Creation Workflow](#9-scenario-creation-workflow)
10. [Code Compliance Audit and Repair Workflow](#10-code-compliance-audit-and-repair-workflow)

---

## 1. Overview and Reference Architecture

### Canonical Reference

Every scenario must be audited and validated against two sources:

| Source                                           | Purpose                                              |
|--------------------------------------------------|------------------------------------------------------|
| `configs/TEMPLATES/full/`                        | The authoritative template for all four config files |
| `configs/AssetBubble/` + `examples/AssetBubble/` | A concrete, verified working implementation          |

**Rule**: AssetBubble is a concrete worked example showing how to apply the template — how configs are structured, how code is organized, and what a complete implementation looks like. It is a reference for *form*, not for *content*. Every scenario has its own distinct financial phenomenon, theoretical mechanisms, and agent designs. Any resemblance between your scenario and AssetBubble in terms of agents, parameters, or dynamics is coincidental — each scenario must be independently designed from its own theory.

### Four Variant System

Every scenario has exactly four variants. Each has its own `configs/<Scenario>/<Variant>/` and `examples/<Scenario>/<Variant>/` directory:

| Variant   | Code logic                                     | LLM | RAG |
|-----------|------------------------------------------------|-----|-----|
| `Rule`    | Deterministic formulas                         | No  | No  |
| `LLM`     | LLM decisions + rich persona prompts           | Yes | No  |
| `RuleLLM` | LLM decisions + rules embedded in prompts      | Yes | No  |
| `Rag`     | LLM + rules + per-decision knowledge retrieval | Yes | Yes |

### Execution Flow (All Variants)

```
Round N:
  Level 0 — Market executes (rule-based always):
    perceive()  ← reads inbounds (investor orders from round N-1)
    decide()    ← computes new price, returns market_data + outbound_messages
    act()       ← constructs and returns Action object

  Level 1 — All investors execute IN PARALLEL:
    perceive()  ← reads inbounds (market data broadcast)
    decide()    ← computes trading decision (or calls LLM)
    act()       ← constructs and returns Action object

Round N+1 begins.
```

---

## 2. Directory Structure Contract

### Files Required Per Scenario

```
examples/<Scenario>/
├── __init__.py              ← package root (empty or re-exports)
├── Rule/
│   ├── __init__.py          ← imports all public classes
│   └── players.py           ← Market + all rule-based agent classes
├── LLM/
│   ├── __init__.py
│   ├── players.py           ← Market (re-imported) + LLM agent classes
│   └── prompts.py           ← all LLM system prompt constants + LLM_USER_TEMPLATE
├── RuleLLM/
│   ├── __init__.py
│   ├── players.py           ← Market (re-imported) + RuleLLM agent classes
│   └── prompts.py           ← rule-embedded system prompts + RULELLM_USER_TEMPLATE
└── Rag/
    ├── __init__.py
    ├── players.py           ← Market (re-imported) + RagLLM agent classes
    └── prompts.py           ← RAG-aware system prompts + RAG_USER_TEMPLATE

configs/<Scenario>/
├── Rule/
│   ├── players.yml
│   ├── topology.yml
│   ├── persona.yml
│   └── simulation.yml
├── LLM/         (same 4 files)
├── RuleLLM/     (same 4 files)
└── Rag/         (same 4 files)
```

### `__init__.py` Requirements

Every variant `__init__.py` must use **exact class names** from its `players.py` in a clean multi-line import block, followed by a matching `__all__` list of separate strings.
→ See `examples/AssetBubble/Rule/__init__.py` for the canonical pattern

**Critical**: `__all__` must be a list of separate strings — NOT a single string with commas inside. The class names in imports must exactly match what is defined in `players.py`.

---

## 3. Theory-to-Agent Mapping

### Read explain.md First

Before touching any code or config, read `examples/<Scenario>/explain.md` (or equivalent). It defines:
- The financial phenomenon being simulated
- The theoretical literature it draws from
- The named agent types and their behavioral roles

The code must match the theory. Each agent class corresponds to a named behavioral type.

### Agent Role Taxonomy

| Role                            | Market effect        | Typical parameters                        |
|---------------------------------|----------------------|-------------------------------------------|
| Destabilizing (trend-followers) | Amplify price swings | High aggressiveness/weight, low threshold |
| Stabilizing (correctors)        | Dampen deviations    | Deviation threshold, fixed position size  |
| Neutral (noise)                 | Provide liquidity    | Trade probability, random quantity        |

### Parameter Derivation

All agent parameters must come from theory, not arbitrary values:

1. Read the theoretical mechanism (e.g., availability heuristic gives 70% recency weight)
2. Encode the formula in `Rule/players.py` using the exact parameter name
3. Use the same parameter name and value in `players.yml` under `extras:`
4. Embed the same rule (with its numerical value) in `RuleLLM/prompts.py` system prompts

**Example** — AvailabilityBias RecentEventOverweighter:
- Theory: recency weight = 0.70 (recent events feel 70% more available)
- `players.py`: `effective_signal = deviation_pct * recency_weight + return_pct * (1 - recency_weight)`
- `players.yml`: `recency_weight: 0.70`
- `RuleLLM/prompts.py`: "Weight recent return 70% and fundamental deviation 30%..."

---

## 4. Python Code Standards

### 4.1 Module Docstring Rule

The module docstring MUST be the first statement in the file, before all imports:

```python
"""<Scenario> <Variant> - <description>

Theoretical Foundation:
    - Author (Year): Key insight
    ...
"""

import logging
import os
...
```

Never put imports above the docstring.

### 4.2 Import Structure

Canonical import order (Rule / LLM variants respectively):
→ `examples/AssetBubble/Rule/players.py` (top section)
→ `examples/AssetBubble/LLM/players.py` (top section)

Key rules:
- Standard library first, then third-party, then `lmbase`, then `masim`, then `examples.*`
- **Never use `masim.utils.llm_client.LLMClient`** — that module does not exist. Always use `LangChainAPIInference` + `InferInput` from `lmbase`
- LLM/RuleLLM/Rag must add `sys.path.insert(0, ...)` before importing from `examples.*`
- Market is always re-imported from `examples.<Scenario>.Rule.players` in LLM/RuleLLM/Rag

### 4.2a lmbase API Contract

The exact public API for the inference classes used in every LLM/RuleLLM/Rag variant is defined in `lmbase.inference`. Always verify against the source before writing any inference call.

**`LangChainAPIInference` constructor** (`lmbase.inference.api_call`):
```python
LangChainAPIInference(
    lm_name="ark/doubao-seed-1-6-lite-251015",  # required: "<provider>/<model>"
    generation_config={"temperature": 0.3, "max_new_tokens": 500},  # optional
)
```
- Only two constructor parameters: `lm_name` and `generation_config`
- API key is **automatically read** from `os.getenv("<PROVIDER>_API_KEY")` — never pass `api_key=` or `base_url=` explicitly
- Provider is inferred from the prefix before `/` in `lm_name` (e.g., `"ark"` → reads `ARK_API_KEY`)

**`InferInput` dataclass** (`lmbase.inference.base`):
```python
InferInput(
    system_msg="...",   # required kwarg — NOT system=, NOT sys_message=
    user_msg="...",     # required kwarg — NOT user=, NOT user_message=
)
```

**`BaseLMAPIInference.run()`** (synchronous — no `await`):
```python
infer_output = llm_client.run([infer_input])       # returns InferBatchOutput
response_text = infer_output.outputs[0].response   # str — NOT .text, NOT .content
```

Full correct call sequence:
```python
infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
infer_output = llm_client.run([infer_input])
raw = infer_output.outputs[0].response
result = parse_llm_response_with_thinking(raw)
```

### 4.3 Three-Method Player Contract

Every player class must implement exactly three async methods: `perceive → decide → act`.
→ See `examples/AssetBubble/Rule/players.py` for the Market and investor implementations
→ See `examples/AssetBubble/LLM/players.py` for the LLM base class pattern

Key rules:
- `perceive`: reads `observation.round` + `observation.inbounds`, initializes state on first call
- `decide`: ALL logic goes here (formulas, LLM calls, RAG retrieval); returns dict with `outbound_messages` key
- `act`: constructs and returns `Action(action_type=..., payload=..., source_id=self.identity)` only
- **Never put LLM calls in `act()`**

### 4.4 Observation API

```python
# CORRECT
if observation.inbounds:
    for inb in observation.inbounds:
        data = inb.payload      # the message content dict
        sender = inb.sender_id  # identity string of the sender

# WRONG — this field does not exist
observation.messages            # AttributeError
observation.outbounds           # AttributeError
```

### 4.5 State Initialization Pattern

Initialize all custom state in `perceive()` on first call, guarded by a key-existence check (e.g., `if "cash" not in self.state.custom_state`).
→ See `examples/AssetBubble/Rule/players.py` — `perceive()` in the investor base class
→ See `examples/AssetBubble/LLM/players.py` — `perceive()` showing LLM client initialization

Key points: all state (cash, position, HistoryBuffer, llm_client) is created on round 0 only; all values come from `self.config.extras`; `HistoryBuffer` takes `folder=` and `entry_limit=`; LLM client creation also stores `lm_name` and `generation_config` separately for Ray `__setstate__` reconstruction.

### 4.6 Ray Serialization (LLM/RuleLLM/Rag)

`LangChainAPIInference` cannot be pickled by Ray. Always add `__getstate__`/`__setstate__` to the LLM investor base class.
→ See `examples/AssetBubble/LLM/players.py` — `LLMInvestor.__getstate__` and `__setstate__`

Pattern: `__getstate__` pops `llm_client` from `custom_state` before pickling; `__setstate__` recreates it from the stored `lm_name` + `generation_config`.

### 4.7 LLM Call Pattern

→ See `examples/AssetBubble/LLM/players.py` — `LLMInvestor.decide()` for the full pattern

Key steps: load system prompt via `load_prompt(self.config.extras["llm"]["sys_message"])`, build user prompt, call `llm_client.run([InferInput(system_msg=..., user_msg=...)])`, parse with `parse_llm_response_with_thinking(infer_output.outputs[0].response)`, retry up to 3 times, fallback to `hold` on persistent failure.

### 4.8 Prompt Loading

`load_prompt(path)` splits `"module.path:VARIABLE_NAME"` at `:`, calls `importlib.import_module`, returns `getattr(module, var_name)`.
→ See `examples/AssetBubble/LLM/players.py` — `load_prompt` helper function

Prompt paths in `players.yml` always use: `"examples.<Scenario>.<Variant>.prompts:PROMPT_CONSTANT_NAME"`

### 4.9 No Hardcoded Constants

All parameters come from `self.config.extras` (populated from `players.yml`). Never hardcode values directly in `players.py`:

```python
# CORRECT
threshold = self.config.extras["deviation_threshold"]

# WRONG
threshold = 0.05    # hardcoded — breaks configurability
```

### 4.10 Outbound Messages Format

`decide()` must return a dict containing an `outbound_messages` list. Each item is `{"payload": <dict>, "content_type": <str>}`; the `payload` is exactly what the recipient sees in `inb.payload`.
→ See `examples/AssetBubble/Rule/players.py` — investor `decide()` return value for the canonical structure

### 4.11 Canonical LLM Output Format

All system prompts (LLM, RuleLLM, Rag variants) must instruct the LLM to produce output in the following **canonical two-tag format**:

```
<analysis>
... reasoning about current market conditions, portfolio state, strategy logic ...
</analysis>

<decision>
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
</decision>
```

**Tag semantics:**

| Tag                        | Purpose                                                                            | Required |
|----------------------------|------------------------------------------------------------------------------------|----------|
| `<analysis>...</analysis>` | Chain-of-thought reasoning — step-by-step market analysis and strategy application | Yes      |
| `<decision>...</decision>` | JSON trading decision — must be parseable by `parse_llm_response_with_thinking()`  | Yes      |

**Rules:**
- Use `<analysis>` not `<think>` — `<think>` is a deprecated legacy tag (parser accepts it as fallback only)
- The `<decision>` block must contain valid JSON with the required fields: `action`, `bid_price`, `quantity`, `reasoning`
- `bid_price` and `quantity` must be **numeric literals** — not expressions, not strings, not formulas
- The `reasoning` field is a short string summary (< 150 chars) for logging
- No text outside the two tag pairs is parsed — do not place JSON before or after `<decision>`

**How to embed in prompts:**

```python
# At the end of every LLM/RuleLLM system prompt constant:
OUTPUT_FORMAT_INSTRUCTION = """OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags, then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas."""
```

**Example:**

```
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
```

**Parser (`llm_utils.parse_llm_response_with_thinking`):**
- Primary: reads `<analysis>...</analysis>`
- Legacy fallback: reads `<think>...</think>` (deprecated — do not use in new prompts)
- Primary: reads `<decision>...</decision>` for the JSON payload
- Fallback: tries code block JSON, then bare JSON object scan

**Common mistake:**
```python
# WRONG — uses deprecated <think> tag
"Output your reasoning in <think>...</think> tags"

# CORRECT — uses canonical <analysis> tag
"Output your reasoning in <analysis>...</analysis> tags"
```

---

## 5. Configuration File Standards

### 5.1 simulation.yml

→ Authoritative template: `configs/TEMPLATES/full/simulation.yml`
→ Concrete working example: `configs/AssetBubble/Rule/simulation.yml`

Required top-level blocks: `setting:`, `environment:`, `ray:`, `players: !include players.yml`, `topology: !include topology.yml`, `communication:`.

Key field notes:
- `setting.name`: `<scenario_name>_<variant>_simulation` (snake_case)
- `setting.round_history_limit` and `setting.save_diagram_interval` are required (often missing)
- `ray.object_store_memory`: integer bytes — Rule: 128MB (`134217728`), LLM/RuleLLM: 512MB (`536870912`), Rag: 1GB (`1073741824`)
- `communication:` contains only `storage_path`, `record_messages`, `message_block_size: 500`

**Common mistakes**:
- Old `storage_path` inside `setting:` — remove it
- `ignore_reinit_error`, `num_cpus: 4`, `log_level` — old fields, remove them
- Missing `round_history_limit`, `save_diagram_interval` — add them
- `message_timeout_ms`, `max_retries` in `communication:` — old fields, replace with `message_block_size: 500`

### 5.2 persona.yml

→ Authoritative template: `configs/TEMPLATES/full/simulation.yml` (persona section)
→ Concrete working example: `configs/AssetBubble/Rule/persona.yml`

Top-level keys: `auto_checkpoint: false`, `debug_mode: true`, and a `proxy:` block with four sub-blocks: `storage:`, `monitoring:`, `communication:`, `resource:`.
This is a **shared file** for all agents in the variant — no per-agent entries.

**Common mistakes**:
- `personas: []` — wrong, that is the old format
- Missing `proxy:` block entirely
- Per-agent persona entries — wrong, this is a shared file

### 5.3 topology.yml

→ Authoritative template: `configs/TEMPLATES/full/topology.yml`
→ Concrete working example: `configs/AssetBubble/Rule/topology.yml`

Required structure: `type: "star"`, `sources: [market]`, `connections:` as a YAML map (`key: [list]`).
Every agent key from `players.yml` must appear once in `connections:`, with bidirectional entries (market→agents and agents→market).

**Common mistakes**:
- Old list-of-dicts format: `connections: [{source: x, target: y}]` — wrong
- Missing `type: "star"` and `sources:` block
- Using expanded instance names like `agent_type_1` — always use base key
- Missing `connections:` map format (must be `key: [list]` not `- source/target` pairs)

### 5.4 players.yml — Market Block

→ Authoritative template: `configs/TEMPLATES/full/players.yml`
→ Concrete working example: `configs/AssetBubble/Rule/players.yml` (market block)

Required fields: `name`, `class`, `num_instances: 1`, `config.identity: "market"`, `config.role: coordinator`, `config.steps_per_turn: 1`, `config.group_tags: [market]`, `config.extras` (with `record_path`, market dynamics params, `custom_state_hot_limit`), `persona: !include persona.yml`.

**Common mistakes**:
- Missing `steps_per_turn: 1` and `group_tags:`
- Missing `record_path` and `custom_state_hot_limit` in extras
- Market class path pointing to wrong variant (e.g., `LLM.players:Market` in Rule config)
- Identity using capital letter `"Market"` instead of `"market"`

### 5.5 players.yml — Agent Block (Rule variant)

→ Authoritative template: `configs/TEMPLATES/full/players.yml` (investor block)
→ Concrete working example: `configs/AssetBubble/Rule/players.yml` (any investor block)

Required fields: same as market block except `role: player`, `group_tags: [investors]`, `num_instances: N`. The `extras:` block must include `record_path`, `initial_cash`, `initial_position`, `custom_state_hot_limit`, plus all scenario-specific formula parameters.

**Common mistakes**:
- Agent key with trailing `_1` suffix (e.g., `agenttype_1:`) — never add instance suffixes to YAML keys
- Missing `steps_per_turn`, `group_tags`, `custom_state_hot_limit`
- No scenario-specific parameters in extras (agents can't work without their formula inputs)
- Wrong `class:` path (pointing to different variant)

### 5.6 players.yml — Agent Block (LLM/RuleLLM variant)

→ Concrete working example: `configs/AssetBubble/LLM/players.yml` (any investor block)

Same as Rule agent block, plus an `llm:` sub-block inside `extras:` containing: `sys_message` (module path to prompt constant), `user_message`, `lm_type: "api"`, `lm_name: "ark/doubao-seed-1-6-lite-251015"`, `generation_config: {temperature: 0.3, max_new_tokens: 500}`.

Agent keys use `llm_` / `rulellm_` prefix. Class names use `LLM<Type>` / `RuleLLM<Type>`. Group tags: `[llm_investors]` / `[rulellm_investors]`.

**Common mistakes**:
- `llm: {'model': ..., 'api_key': ..., 'base_url': ...}` — wrong old format with inline dict and hardcoded API keys
- Class path missing prefix (e.g., `LLM.players:RecentEventOverweighter` instead of `LLM.players:LLMRecentEventOverweighter`)
- Prompt path referencing wrong variant module

### 5.7 players.yml — Agent Block (Rag variant)

→ Concrete working example: `configs/AssetBubble/Rag/players.yml`

Two additions on top of the LLM/RuleLLM pattern:
1. A `knowledge:` block at the **top of the file** (before `market:`) — the config loader promotes it to top-level
2. A `private_knowledge:` sub-block inside each agent's `extras:`, containing `from_global_resources:`, `local_resources:`, and — critically — a `rag:` block **nested inside `private_knowledge:`**

Agent keys use `ragllm_` prefix. Class names use `RagLLM<Type>`. Group tags: `[ragllm_investors]`. `max_new_tokens: 600` (slightly more due to RAG context).

**Critical rules**:
- `rag:` MUST be nested inside `private_knowledge:` — NOT at the same level as `private_knowledge:`
- `knowledge:` block goes at file top, before `market:`
- Rag agent keys must use `ragllm_` prefix

---

## 6. Variant-Specific Rules

### 6.1 Rule Variant

- `players.py`: Market + N agent classes, no imports of `LangChainAPIInference` or `dotenv`
- `players.yml`: No `llm:` block anywhere, no `knowledge:` block
- `topology.yml`: Uses base agent keys without prefix (e.g., `recent_event_overweighter`)
- Market class path: `"examples.<Scenario>.Rule.players:Market"`

### 6.2 LLM Variant

- `players.py`: Market re-imported from Rule, `LLMInvestor` base + `LLM<Type>` subclasses
- `prompts.py`: Rich behavioral persona ONLY — no quantitative rules, no scenario name
- `players.yml`: Has `llm:` block, no `knowledge:`, no `private_knowledge:`
- Market class path: `"examples.<Scenario>.LLM.players:Market"`
- Agent keys: `llm_<agent_type>` (e.g., `llm_recent_event_overweighter`)
- `group_tags: [llm_investors]`

**Prompt design rule**: LLM system prompts describe ONLY the investor's personality and trading style. They must NOT reveal the simulation scenario name or target outcome. Say "I am a trader who gives extra weight to recently observed price movements" — never say "I am simulating availability bias."

### 6.3 RuleLLM Variant

- `players.py`: Identical structure to LLM variant but class prefix `RuleLLM<Type>`
- `prompts.py`: System prompts embed BOTH the behavioral persona AND explicit quantitative rules
- Market class path: `"examples.<Scenario>.RuleLLM.players:Market"`
- Agent keys: `rulellm_<agent_type>`

**Prompt design rule**: RuleLLM prompts must include the exact numerical thresholds and formulas from the Rule variant. Example: "When effective_signal = deviation_pct × 0.70 + return_pct × 0.30 exceeds 2%, buy proportionally..."

### 6.4 Rag Variant

- `players.py`: `RagLLMInvestor` base with `_get_rag_context()` method
- `prompts.py`: Defines own `RAG_*_SYS` constants (may re-export from RuleLLM), defines `RAG_USER_TEMPLATE` with `{rag_context}` placeholder, and exports `LLM_USER_TEMPLATE = RAG_USER_TEMPLATE` as an alias (required by `players.yml`)
- `players.yml`: Has `knowledge:` at top, `private_knowledge:` in each agent's extras
- Agent keys: `ragllm_<agent_type>`
- `group_tags: [ragllm_investors]`

**Critical `prompts.py` rules for Rag variant**:
- `RAG_USER_TEMPLATE` MUST include a `{rag_context}` placeholder — the context is injected via `.format()`, NOT appended manually after formatting
- All prompt constants referenced in `players.yml` must be importable from `Rag/prompts.py` — if `players.yml` uses `LLM_USER_TEMPLATE`, that name must be exported (add `LLM_USER_TEMPLATE = RAG_USER_TEMPLATE`)
- Never import `LLM_USER_TEMPLATE` from `RuleLLM/prompts.py` — it does not exist there (only `RULELLM_USER_TEMPLATE` exists)
- Correct pattern for re-using RuleLLM system prompts:
```python
from examples.<Scenario>.RuleLLM.prompts import (
    RULELLM_<TYPE>_SYS,
    RULELLM_USER_TEMPLATE,   # NOT LLM_USER_TEMPLATE
)
RAG_<TYPE>_SYS = RULELLM_<TYPE>_SYS    # re-export with RAG_ prefix
RAG_USER_TEMPLATE = """...{rag_context}..."""
LLM_USER_TEMPLATE = RAG_USER_TEMPLATE  # alias for players.yml compatibility
```

**RAG context pattern**:
→ See `examples/AssetBubble/Rag/players.py` — `RagLLMInvestor._get_rag_context()` for the canonical implementation

Key points: wrapped in `try/except`; checks `self.knowledge is not None`; builds a domain-specific query from current market state; returns `""` on failure or empty results; uses `self.knowledge.retrieve(query)` and joins top-k results.

---

## 7. Common Errors and Fixes

### 7.1 Code Errors

| Error                             | Wrong                                           | Correct                                                                  |
|-----------------------------------|-------------------------------------------------|--------------------------------------------------------------------------|
| Wrong observation field           | `observation.messages`                          | `observation.inbounds`                                                   |
| Wrong LLM client class            | `from masim.utils.llm_client import LLMClient`  | `from lmbase.inference.api_call import LangChainAPIInference`            |
| Wrong LLM import module           | `from masim.interface.inference import ...`     | `from lmbase.inference.api_call import LangChainAPIInference`            |
| Wrong `LangChainAPIInference` arg | `LangChainAPIInference(model=..., api_key=...)` | `LangChainAPIInference(lm_name=..., generation_config=...)`              |
| Wrong `InferInput` kwarg names    | `InferInput(system=..., user=...)`              | `InferInput(system_msg=..., user_msg=...)`                               |
| Wrong `InferInput` kwarg names    | `InferInput(sys_message=..., user_message=...)` | `InferInput(system_msg=..., user_msg=...)`                               |
| Wrong LLM call method             | `await self._llm_client.ainfer(infer_input)`    | `self._llm_client.run([infer_input]).outputs[0].response`                |
| Wrong LLM call method             | `await self._llm_client.infer(infer_input)`     | `self._llm_client.run([infer_input]).outputs[0].response`                |
| Wrong response field              | `infer_output.outputs[0].text`                  | `infer_output.outputs[0].response`                                       |
| Wrong prompt utility import       | `from masim.utils.prompt import load_prompt`    | Local `load_prompt` function using `importlib`                           |
| Wrong utils import path           | `from masim.utils.llm_utils import ...`         | `from examples.llm_utils import ...`                                     |
| Calling non-existent method       | `rag_store.save(persist_dir)`                   | Remove — `build()` auto-persists to `persist_dir`                        |
| Dict access with default          | `payload.get("action", "hold")`                 | `payload["action"]`                                                      |
| Inline comment                    | `threshold = 0.05  # from theory`               | Comment on separate line above the code                                  |
| LLM logic in wrong method         | LLM call inside `act()`                         | LLM call inside `decide()`                                               |
| Docstring not first               | imports before docstring                        | module docstring must precede all imports                                |
| Hardcoded parameters              | `threshold = 0.05` in code                      | `threshold = self.config.extras["threshold"]`                            |
| No Ray serialization              | no `__getstate__`/`__setstate__`                | required for all LLM/RuleLLM/Rag players                                 |
| Wrong Action constructor          | `Action(outbounds=[...])`                       | `Action(action_type=..., payload=..., source_id=...)`                    |
| Wrong import for Market           | each variant re-defines Market                  | `from examples.<Scenario>.Rule.players import Market`                    |
| Character-split `__all__`         | `__all__ = ["M, a, r, k, e, t"]`                | `__all__ = ["Market"]`                                                   |
| Wrong `Rag/prompts.py` import     | `from RuleLLM.prompts import LLM_USER_TEMPLATE` | Import `RULELLM_USER_TEMPLATE`; define `RAG_USER_TEMPLATE` locally       |
| RAG context injected manually     | `user_prompt += rag_context` after `.format()`  | Include `{rag_context}` in template; pass via `.format(rag_context=...)` |
| Wrong analysis tag in prompt      | `<think>...</think>` in OUTPUT FORMAT section   | Use `<analysis>...</analysis>` (canonical tag; `<think>` is deprecated)  |
| Wrong HistoryBuffer args          | `HistoryBuffer(maxlen=100)`                     | `HistoryBuffer(folder=path, entry_limit=N)`                              |

### 7.2 Config Errors

| Error                         | Wrong                                   | Correct                                    |
|-------------------------------|-----------------------------------------|--------------------------------------------|
| Old topology format           | `connections: [{source: x, target: y}]` | `connections: {x: [y], y: [x]}`            |
| Missing topology header       | No `type:` or `sources:`                | `type: "star"\nsources:\n  - market`       |
| Old persona format            | `personas: []`                          | Full `proxy:` block structure              |
| Old simulation format         | `num_cpus: 4`, `log_level: INFO`        | Remove; use template structure             |
| Wrong `communication:` fields | `message_timeout_ms`, `max_retries`     | Use `message_block_size: 500`              |
| Old LLM config format         | `llm: {'model': ..., 'api_key': ...}`   | `llm:\n  sys_message: ...\n  lm_name: ...` |
| Instance suffix in key        | `agent_type_1:` as YAML key             | `agent_type:` (no suffix in players.yml)   |
| `rag:` at wrong nesting       | `extras:\n  rag:`                       | `extras:\n  private_knowledge:\n    rag:`  |
| Missing `num_instances`       | omitted                                 | Required for every player                  |
| Wrong class path              | `Rule.players:Market` in LLM config     | `LLM.players:Market`                       |

### 7.3 __init__.py Errors

| Error                   | Wrong                                     | Correct                               |
|-------------------------|-------------------------------------------|---------------------------------------|
| Character-split import  | `from x import M, a, r, k, e, t`          | `from x import Market`                |
| All names in one string | `__all__ = ["Market, Agent"]`             | `__all__ = ["Market", "Agent"]`       |
| Wrong class names       | `from x import HotMoneyFunder` in RuleLLM | `from x import RuleLLMHotMoneyFunder` |

---

## 8. Step-by-Step Audit Checklist

Use this checklist when auditing any existing scenario. Work through it in order.

### Phase 1 — Theory Review

- [ ] Read `explain.md` (or the scenario docstring in `Rule/players.py`)
- [ ] List the named agent types and their theoretical roles
- [ ] Verify each agent class in code matches an agent in the theory
- [ ] Check all parameter values are grounded in theory or empirical data

### Phase 2 — Python Code Audit

For each of the 7 Python files (Rule/players.py, LLM/players.py, LLM/prompts.py, RuleLLM/players.py, RuleLLM/prompts.py, Rag/players.py, Rag/prompts.py):

- [ ] Module docstring is the first statement (before all imports)
- [ ] All imports are at file top (no function-level imports)
- [ ] No inline (end-of-line) comments — comments must appear on the line above the code
- [ ] Correct imports: `LangChainAPIInference` from `lmbase.inference.api_call`, not `LLMClient` and not `masim.interface.inference`
- [ ] Correct imports: `InferInput` from `lmbase.inference.base`, not from `masim.interface.inference`
- [ ] No import from `masim.utils.prompt` or `masim.utils.llm_utils` — use local `load_prompt` / `from examples.llm_utils import ...`
- [ ] `observation.inbounds` used, not `observation.messages`
- [ ] LLM call is in `decide()`, not `act()`
- [ ] `act()` only constructs and returns `Action(action_type=..., payload=..., source_id=...)`
- [ ] State initialized on first call in `perceive()`, not at class level
- [ ] `__getstate__`/`__setstate__` present in all LLM/RuleLLM/Rag base classes
- [ ] No hardcoded constants — all params from `self.config.extras["key"]` (direct `[]` access, never `.get(key, default)`)
- [ ] No `.get(key, default)` on any dict — use `dict["key"]` directly (fail-fast principle §2.4)
- [ ] `KnowledgeStore.save()` is never called — `build()` auto-persists
- [ ] `LangChainAPIInference` uses only `lm_name=` and `generation_config=` — no `api_key=`, `model=`, `base_url=`
- [ ] `InferInput` uses `system_msg=` and `user_msg=` — not `system=`, `user=`, `sys_message=`, `user_message=`
- [ ] LLM call uses `.run([infer_input])` (synchronous) — not `.ainfer()`, `.infer()`, or `await .run()`
- [ ] Response extracted as `.outputs[0].response` — not `.text`, `.content`, `.response` on the batch object
- [ ] `HistoryBuffer` uses `folder=` and `entry_limit=`, not `maxlen=`
- [ ] `_get_rag_context()` present in Rag base class with graceful fallback
- [ ] Prompt constants use correct naming: `LLM_<TYPE>_SYS`, `RULELLM_<TYPE>_SYS`, `RAG_<TYPE>_SYS`
- [ ] All prompts use `<analysis>...</analysis>` output tag (NOT `<think>...</think>`)
- [ ] All prompts use `<decision>...</decision>` for the JSON decision block
- [ ] `LLM_USER_TEMPLATE` / `RULELLM_USER_TEMPLATE` / `RAG_USER_TEMPLATE` present
- [ ] Run `python3 -m py_compile <file>` — no syntax errors

### Phase 3 — `__init__.py` Audit

For each of the 4 `__init__.py` files:

- [ ] Imports all public classes from `players.py`
- [ ] Class names match exactly (including prefix: `LLM`, `RuleLLM`, `RagLLM`)
- [ ] `__all__` is a list of separate strings, not one comma-separated string
- [ ] Run `python3 -m py_compile <file>` — no syntax errors

### Phase 4 — Config Audit

For each of the 16 YAML files (4 variants × 4 files):

**simulation.yml**:
- [ ] Uses `namespace`, `actor_prefix`, proper Ray fields
- [ ] Has `round_history_limit` and `save_diagram_interval` in `setting:`
- [ ] `communication:` has only `storage_path`, `record_messages`, `message_block_size`
- [ ] `object_store_memory` is integer, not null

**persona.yml**:
- [ ] Has `auto_checkpoint: false` + full `proxy:` block
- [ ] No `personas: []` or per-agent entries

**topology.yml**:
- [ ] Has `type: "star"`, `sources: [market]`, `connections: {key: [list]}` map format
- [ ] Every agent key from `players.yml` appears in connections
- [ ] No instance suffixes (`_1`, `_2`) in any key

**players.yml**:
- [ ] Market block has `steps_per_turn`, `group_tags`, `record_path`, `custom_state_hot_limit`
- [ ] All agent keys use underscore naming, no trailing `_1` suffix
- [ ] Rule variant: no `llm:` block anywhere
- [ ] LLM/RuleLLM: `llm:` block with `sys_message`, `user_message`, `lm_name`, `generation_config`
- [ ] LLM format: `lm_name: "ark/doubao-seed-1-6-lite-251015"` not inline dict
- [ ] Rag: `knowledge:` at top before `market:`
- [ ] Rag: `rag:` nested inside `private_knowledge:` for each agent
- [ ] Class paths correct per variant (`Rule.players:X`, `LLM.players:LLMX`, etc.)

### Phase 5 — Cross-Consistency Check

- [ ] Agent key names in `players.yml` exactly match agent keys in `topology.yml`
- [ ] Class names in `players.yml` class paths exactly match class definitions in `players.py`
- [ ] Parameter names in `players.yml` extras match `self.config.extras["param"]` accesses in code
- [ ] Prompt constant names in `players.yml` sys_message/user_message match constants in `prompts.py`
- [ ] `record_path` in all extras matches `setting.record_path` in `simulation.yml`
- [ ] `record_path` in `persona.yml` proxy paths matches the other paths

---

## 9. Scenario Creation Workflow

When creating a new scenario from scratch, follow this order:

### Step 1 — Theory Foundation

1. Define the financial phenomenon and research question
2. Identify 2-3 key theoretical papers/mechanisms
3. Name 4-6 distinct agent types based on the theory
4. For each agent, write out: behavioral rule formula, key parameters, market role (stabilizing/destabilizing/neutral)

### Step 2 — File Setup

```
mkdir -p examples/<Scenario>/{Rule,LLM,RuleLLM,Rag}
mkdir -p configs/<Scenario>/{Rule,LLM,RuleLLM,Rag}
touch examples/<Scenario>/__init__.py
touch examples/<Scenario>/{Rule,LLM,RuleLLM,Rag}/__init__.py
```

### Step 3 — Rule/players.py

Write in this order:
1. Module docstring with theory section
2. Imports (standard library, masim only — no LLM imports)
3. `Market` class with `perceive/decide/act`
4. Base agent class (if shared logic exists)
5. One class per agent type, each with its own `decide()` implementing the formula
6. `__all__` list

### Step 4 — Rule configs

1. `persona.yml` — copy from AssetBubble/Rule/persona.yml, change all paths
2. `topology.yml` — list all agent keys under `connections:`
3. `players.yml` — one block per agent with scenario-specific parameters in extras
4. `simulation.yml` — copy from AssetBubble/Rule/simulation.yml, change name/description/paths

### Step 5 — LLM/prompts.py

Write one system prompt constant per agent type. Each prompt must:
- Describe the investor's personality and trading philosophy
- NOT mention the scenario name or simulation target
- NOT contain quantitative rules (those go in RuleLLM)

Then write `LLM_USER_TEMPLATE` with all relevant market data fields.

### Step 6 — LLM/players.py + configs

1. `players.py`: Re-import Market from Rule, write `LLMInvestor` base, one `LLM<Type>` subclass per agent
2. Configs: copy Rule configs, change all paths to `LLM/`, update class paths, add `llm:` blocks

### Step 7 — RuleLLM/prompts.py + players.py + configs

1. `prompts.py`: Rewrite system prompts to embed quantitative rules (thresholds, weights, formulas)
2. `players.py`: Copy from LLM, change class prefix to `RuleLLM<Type>`
3. Configs: copy LLM configs, change all paths to `RuleLLM/`, update class paths and prompt references

### Step 8 — Rag/prompts.py + players.py + configs

1. `prompts.py`: Add `{rag_context}` placeholder to system prompts and user template
2. `players.py`: Copy from RuleLLM, add `_get_rag_context()`, change prefix to `RagLLM<Type>`
3. Configs: copy RuleLLM configs, change paths to `Rag/`, add `knowledge:` block, add `private_knowledge:` to each agent, prefix agent keys with `ragllm_`

### Step 9 — Validation

```bash
# Syntax check all Python files
python3 -m py_compile examples/<Scenario>/Rule/players.py
python3 -m py_compile examples/<Scenario>/LLM/players.py
python3 -m py_compile examples/<Scenario>/LLM/prompts.py
python3 -m py_compile examples/<Scenario>/RuleLLM/players.py
python3 -m py_compile examples/<Scenario>/RuleLLM/prompts.py
python3 -m py_compile examples/<Scenario>/Rag/players.py
python3 -m py_compile examples/<Scenario>/Rag/prompts.py
python3 -m py_compile examples/<Scenario>/Rule/__init__.py
python3 -m py_compile examples/<Scenario>/LLM/__init__.py
python3 -m py_compile examples/<Scenario>/RuleLLM/__init__.py
python3 -m py_compile examples/<Scenario>/Rag/__init__.py
```

Then run the Phase 4 and Phase 5 config audit checklist above.

---

## Quick Reference: Path Naming Conventions

| Purpose                       | Pattern                                               | Example                                                                     |
|-------------------------------|-------------------------------------------------------|-----------------------------------------------------------------------------|
| EXPERIMENT record path        | `EXPERIMENT/<Scenario>/<Variant>/records`             | `EXPERIMENT/AvailabilityBias/LLM/records`                                   |
| Ray namespace                 | `<scenario_name>_<variant>`                           | `availability_bias_llm`                                                     |
| Simulation name               | `<scenario_name>_<variant>_simulation`                | `availability_bias_llm_simulation`                                          |
| Player key (Rule)             | `<agent_type>`                                        | `recent_event_overweighter`                                                 |
| Player key (LLM)              | `llm_<agent_type>`                                    | `llm_recent_event_overweighter`                                             |
| Player key (RuleLLM)          | `rulellm_<agent_type>`                                | `rulellm_recent_event_overweighter`                                         |
| Player key (Rag)              | `ragllm_<agent_type>`                                 | `ragllm_recent_event_overweighter`                                          |
| Class name (Rule)             | `<TypeName>`                                          | `RecentEventOverweighter`                                                   |
| Class name (LLM)              | `LLM<TypeName>`                                       | `LLMRecentEventOverweighter`                                                |
| Class name (RuleLLM)          | `RuleLLM<TypeName>`                                   | `RuleLLMRecentEventOverweighter`                                            |
| Class name (Rag)              | `RagLLM<TypeName>`                                    | `RagLLMRecentEventOverweighter`                                             |
| class path in YAML            | `"examples.<Scenario>.<Variant>.players:<ClassName>"` | `"examples.AvailabilityBias.LLM.players:LLMRecentEventOverweighter"`        |
| Prompt constant (LLM sys)     | `LLM_<TYPE>_SYS`                                      | `LLM_RECENT_EVENT_OVERWEIGHTER_SYS`                                         |
| Prompt constant (RuleLLM sys) | `RULELLM_<TYPE>_SYS`                                  | `RULELLM_RECENT_EVENT_OVERWEIGHTER_SYS`                                     |
| Prompt constant (Rag sys)     | `RAG_<TYPE>_SYS`                                      | `RAG_RECENT_EVENT_OVERWEIGHTER_SYS`                                         |
| Prompt path in YAML           | `"examples.<Scenario>.<Variant>.prompts:<CONSTANT>"`  | `"examples.AvailabilityBias.LLM.prompts:LLM_RECENT_EVENT_OVERWEIGHTER_SYS"` |

---

## Quick Reference: object_store_memory by Variant

| Variant | Value (bytes)        | Explanation                              |
|---------|----------------------|------------------------------------------|
| Rule    | `134217728` (128 MB) | No LLM strings in store                  |
| LLM     | `536870912` (512 MB) | Prompt/response strings per TurnResult   |
| RuleLLM | `536870912` (512 MB) | Same as LLM                              |
| Rag     | `1073741824` (1 GB)  | RAG context adds ~8-16 KB per TurnResult |

---

## 10. Code Compliance Audit and Repair Workflow

This section documents the systematic audit and repair process applied across all `examples/` scenarios to bring every file into full compliance with the project coding standards. Use this as a repeatable playbook whenever new scenarios are added or an existing scenario is suspected of non-compliance.

### 10.1 Overview

The audit covers four categories, applied in this priority order:

| Priority | Category                       | Standard                     | Tool                        |
|----------|--------------------------------|------------------------------|-----------------------------|
| 1        | Syntax correctness             | Python parse-ability         | `py_compile`                |
| 2        | Import correctness             | Correct module paths         | `grep` + manual inspection  |
| 3        | API usage correctness          | Real class/method names only | `grep` + API source reading |
| 4        | llm-coding-rules.md compliance | §1.1 §1.2 §2.1 §2.4          | tokenize + regex audit      |

Always fix in this order — syntax errors block everything else; wrong imports produce runtime failures; API misuse produces `AttributeError`; coding rule violations produce silent degradation.

### 10.2 Step 1 — Baseline Syntax Check

Before any audit, establish a clean baseline:

```bash
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/**/*.py', recursive=True))
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
if errors:
    for e in errors: print('ERROR:', e)
    sys.exit(1)
else:
    print(f'ALL OK: {len(files)} files')
"
```

Expected: zero errors. If any exist, fix syntax before proceeding.

### 10.3 Step 2 — Import Correctness Audit

Three categories of wrong imports have been observed in practice. Scan for all three:

#### Category A — Wrong inference module path

```bash
grep -rn "masim.interface.inference" examples/ --include="players.py"
```

`masim.interface` is the UI dashboard module. It has **no** `inference` submodule.

Correct replacement:
```python
# WRONG
from masim.interface.inference import LangChainAPIInference, InferInput

# CORRECT
from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
```

#### Category B — Non-existent prompt utility module

```bash
grep -rn "masim.utils.prompt" examples/ --include="players.py"
```

`masim.utils.prompt` does not exist. `load_prompt` is a local helper using `importlib`.

Correct replacement — inject this function after the imports:
```python
import importlib

def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)
```

#### Category C — Wrong utils path

```bash
grep -rn "masim.utils.llm_utils" examples/ --include="players.py"
```

Correct replacement:
```python
# WRONG
from masim.utils.llm_utils import load_prompt, parse_llm_response_with_thinking

# CORRECT
from examples.llm_utils import load_prompt, parse_llm_response_with_thinking
```

**After fixing all imports, re-run the baseline syntax check.**

### 10.4 Step 3 — API Usage Audit

Verify that all calls on framework objects use only real public API methods. This applies to both the `masim` framework and third-party libraries like `lmbase`. Before writing any call against a third-party class, read its source to confirm the exact constructor signature, method names, and return types.

#### lmbase Inference API

The `lmbase` package (`lmbase.inference`) is the LLM inference backend for all LLM/RuleLLM/Rag variants. Three classes are involved:

**`LangChainAPIInference`** (`lmbase.inference.api_call.LangChainAPIInference`):
- Constructor: `__init__(self, lm_name=None, generation_config=None)` — exactly two parameters
- Reads the API key automatically: `os.getenv(f"{provider.upper()}_API_KEY")` where `provider` is the prefix of `lm_name` before `/`
- **Never pass** `api_key=`, `model=`, or `base_url=` — they do not exist as constructor parameters
- `.run([InferInput(...)])` — synchronous method (no `await`), returns `InferBatchOutput`
- No `.ainfer()`, `.infer()`, `.async_run()` methods exist

**`InferInput`** (`lmbase.inference.base.InferInput`):
- Fields: `system_msg` (str, required), `user_msg` (str or list, required), `messages` (optional), `extras` (optional)
- **Exact kwarg names**: `system_msg=` and `user_msg=` — NOT `system=`, `user=`, `sys_message=`, `user_message=`, `prompt=`

**`InferBatchOutput`** (returned by `.run()`):
- Fields: `outputs` (list of `InferOutput`), `total_time_used` (float)
- To get the response text: `infer_output.outputs[0].response` — NOT `.text`, NOT `.content`

Detection commands:
```bash
# Wrong constructor kwargs
grep -rn "LangChainAPIInference" examples/ --include="players.py" | grep -E "api_key=|model=|base_url="

# Wrong InferInput kwarg names
grep -rn "InferInput(" examples/ --include="players.py" | grep -E "sys_message=|user_message=|\bsystem=|\buser="

# Wrong method calls
grep -rn "\.ainfer\|\.infer(" examples/ --include="players.py"

# Wrong response field
grep -rn "\.outputs\[0\]\.text\|\.outputs\[0\]\.content" examples/ --include="players.py"
```

Fix pattern:
```python
# WRONG — three different wrong patterns observed in practice
InferInput(system=sys_msg, user=user_msg)
InferInput(sys_message=sys_msg, user_message=user_msg)
response = await self._llm_client.ainfer(infer_input)
raw = await self._llm_client.infer(infer_input)

# CORRECT
infer_input = InferInput(system_msg=sys_msg, user_msg=user_msg)
infer_output = self._llm_client.run([infer_input])      # synchronous, no await
raw = infer_output.outputs[0].response
result = parse_llm_response_with_thinking(raw)
```

**Automated bulk fix** for InferInput kwargs:
```python
import re, glob
for f in glob.glob("examples/**/*.py", recursive=True):
    content = open(f).read()
    original = content
    content = re.sub(r'\bsys_message\s*=', 'system_msg=', content)
    content = re.sub(r'\buser_message\s*=', 'user_msg=', content)
    content = re.sub(r'(?<!\w)system\s*=\s*(?=[^\s=])', 'system_msg=', content)
    content = re.sub(r'(?<!\w)user\s*=\s*(?=[^\s=])', 'user_msg=', content)
    if content != original:
        open(f, 'w').write(content)
```

**Automated bulk fix** for `.ainfer()`/`.infer()` → `.run()`:
```python
import re, glob
for f in glob.glob("examples/**/*.py", recursive=True):
    content = open(f).read()
    original = content
    for attr in ['_llm_client', '_llm']:
        content = re.sub(
            rf'await\s+(self\.{attr})\.(ainfer|infer)\s*\(\s*(\w+)\s*\)',
            rf'\1.run([\3]).outputs[0].response',
            content
        )
    if content != original:
        open(f, 'w').write(content)
```

#### KnowledgeStore API

The real public methods are: `build()`, `load()`, `query()`, `is_built()`, `is_initialized()`.

**`save()` does not exist.** `build()` automatically persists to `persist_dir` if configured.

```bash
grep -rn "rag_store\.save\|knowledge_store\.save" examples/ --include="players.py"
```

Fix: remove the `.save(persist_dir)` call entirely:
```python
# WRONG
rag_store.build(docs)
rag_store.save(local_rag_dir)   # AttributeError — method does not exist

# CORRECT
rag_store.build(docs)           # auto-persists to persist_dir from constructor
```

#### KnowledgeResult API

The real properties/attributes are: `chunks` (list), `query` (KnowledgeQuery), `is_empty` (bool), `formatted_text` (str).

Do not confuse `KnowledgeResult` objects with regular Python dicts. The variable name `result` may refer to either — inspect the assignment context.

#### KnowledgeLoader API

The real public methods are: `load_from_dir()`, `load_from_urls()`, `load_from_url_csv()`, `suggest_and_download()`, `load_for_agent()`.

#### Broad API validity check

Run a script that scans for method calls on known objects and cross-references against the real API:

```python
import re, glob

VALID_METHODS = {
    "KnowledgeStore": {"build", "load", "query", "is_built", "is_initialized"},
    "KnowledgeLoader": {"load_from_dir", "load_from_url_csv", "load_from_urls",
                        "suggest_and_download", "load_for_agent"},
}

for f in glob.glob("examples/**/*.py", recursive=True):
    if not f.endswith("players.py"):
        continue
    for i, line in enumerate(open(f).readlines(), 1):
        for m in re.finditer(r'\b(rag_store|knowledge_store)\s*\.\s*(\w+)\s*\(', line):
            method = m.group(2)
            if method not in VALID_METHODS["KnowledgeStore"]:
                print(f"{f}:{i}: .{method}() — NOT in KnowledgeStore API")
```

### 10.5 Step 4 — llm-coding-rules.md Compliance

All code must comply with `docs/research-plan/llm-coding-rules.md`. The four most commonly violated rules are:

#### §1.1 — No Inline (End-of-Line) Comments

Comments must be on a separate line **above** the code they describe. Inline comments are prohibited.

```python
# WRONG
threshold = self.config.extras["threshold"]  # deviation threshold

# CORRECT
# Deviation threshold from config
threshold = self.config.extras["threshold"]
```

Detection using Python's `tokenize` module is more accurate than regex (avoids false matches inside strings):

```python
import tokenize, io

def has_inline_comment(source_line: str) -> bool:
    """Return True if the line has a real inline comment (not standalone)."""
    stripped = source_line.rstrip()
    if stripped.lstrip().startswith("#"):
        return False  # Standalone comment line — not inline
    tokens = list(tokenize.generate_tokens(io.StringIO(stripped).readline))
    comment_tokens = [t for t in tokens if t.type == tokenize.COMMENT]
    return len(comment_tokens) > 0
```

#### §1.2 — All Imports at File Top

No function-level, conditional, or lazy imports. All `import` / `from ... import` statements must be at module top-level.

```python
# WRONG — import inside a method
def perceive(self, observation):
    import json
    ...

# CORRECT — import at file top
import json
```

Detection:
```bash
grep -rn "^    import \|^        import \|^    from " examples/ --include="players.py"
```

**Exception**: `from __future__ import annotations` may appear inside class bodies if required by type hints — though this is unusual.

#### §2.1 / §2.4 — No `.get()` with Default Values

Do not use `dict.get(key, default)` for any **known** dictionary key. Use direct `dict[key]` access and let `KeyError` surface immediately. This is the "fail-fast" principle.

```python
# WRONG — silently uses wrong data if key is missing
action = decision_payload.get("action", "hold")
value  = config.get("threshold", 0.05)

# CORRECT — fails loudly if key is unexpectedly absent
action = decision_payload["action"]
value  = config["threshold"]
```

This applies to ALL dicts in `players.py`:
- Config dicts: `extras`, `cs`, `llm_cfg`, `rag_cfg`, `gen_cfg`
- Message payload dicts: `payload`, `decision_payload`
- LLM response dicts: `result` (from `parse_llm_response_with_thinking`)
- Internal state dicts: `decision`

Detection:
```bash
python3 -c "
import re, glob
for f in glob.glob('examples/**/*.py', recursive=True):
    if not f.endswith('players.py'): continue
    for i, line in enumerate(open(f).readlines(), 1):
        if re.search(r'\.get\s*\(\s*[\"\'][^\"\']+[\"\'\]\s*,', line):
            print(f'{f}:{i}: {line.rstrip()}')
"
```

**Important caveat for automated repair**: The regex `.get("key", default)` → `["key"]` script must NOT match inside string literals or `%`-format expressions. Validate with `py_compile` after every bulk replacement.

### 10.6 Step 5 — HistoryBuffer Constructor Audit

`HistoryBuffer` takes exactly two arguments: `folder` (str) and `entry_limit` (int). The old keyword argument `maxlen=` is incorrect.

```python
# WRONG
buffer = HistoryBuffer(maxlen=100)
buffer = HistoryBuffer(record_path=path, maxlen=100)

# CORRECT
record_dir = os.path.join(self.config.extras["record_path"], self.identity)
buffer = HistoryBuffer(
    folder=record_dir,
    entry_limit=self.config.extras["history_limit"],
)
```

Note: `record_path` must be assigned **before** the `HistoryBuffer(...)` call, not passed as a constructor argument. Automated scripts that insert `record_path = ...` must ensure the assignment appears on a separate line above the constructor call.

Detection:
```bash
grep -rn "HistoryBuffer(" examples/ --include="players.py" | grep -v "folder="
```

### 10.7 Step 6 — Final Validation

After all fixes, run the full suite:

```bash
# 1. Syntax check all Python files
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/**/*.py', recursive=True))
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
if errors:
    for e in errors: print('ERROR:', e); sys.exit(1)
else:
    print(f'ALL OK: {len(files)} files')
"

# 2. Confirm no invalid lmbase API usage
grep -rn "LangChainAPIInference" examples/ --include="players.py" | grep -E "api_key=|model=|base_url="
grep -rn "\.ainfer\|self\._llm\.infer\|self\._llm_client\.infer" examples/ --include="players.py"
grep -rn "outputs\[0\]\.text\|outputs\[0\]\.content" examples/ --include="players.py"

# 3. Confirm no invalid KnowledgeStore methods
grep -rn "\.save(\|rag_store\.\|knowledge_store\." examples/ --include="players.py"

# 4. Confirm no .get(key, default) in players.py
python3 -c "
import re, glob
count = 0
for f in glob.glob('examples/**/players.py', recursive=True):
    for line in open(f):
        if re.search(r'\.get\s*\(\s*[\"\']+[^\"\']+[\"\']+\s*,', line):
            count += 1
print(f'Remaining .get(key,default): {count}')
"

# 5. Confirm no wrong import paths
grep -rn "masim.interface.inference\|masim.utils.prompt\|masim.utils.llm_utils" examples/ --include="players.py"
```

All checks must return zero findings.

### 10.8 Edge Cases and Pitfalls

The following edge cases have been encountered in practice:

#### Multiline `.get()` leaves stray parenthesis

When a `.get()` call spans multiple lines (e.g., inside a `float(\n    extras.get(...)\n)` wrapper), a single-line regex replacement leaves the outer closing `)` as a syntax error:

```python
# Before
cs["peg_rate"] = float(
    extras.get("peg_rate", 1.2)
)

# After naive regex — WRONG (stray closing paren)
cs["peg_rate"] = float(
    extras["peg_rate"]
)  # <-- this ) is now unmatched

# CORRECT manual fix
cs["peg_rate"] = float(extras["peg_rate"])
```

Always run `py_compile` after automated fixes to catch these.

#### Docstring lines starting with `from`

A `fix_function_imports()` routine that matches lines starting with `from ` can incorrectly move docstring prose into the imports section if the docstring contains text like:

```
from narrative-driven buying. Mean reversion is suppressed...
```

Guard the import detector against lines inside triple-quoted strings.

#### `system=` regex over-matching

A regex replacing `(?<!\w)system\s*=` with `system_msg=` will correctly fix `InferInput(system=...)` but may over-match in other contexts such as:

```python
# A variable assignment — DO NOT transform this
operating_system = "linux"
```

Because the lookbehind `(?<!\w)` guards against word characters, assignments like `operating_system =` are safe. But always verify with `py_compile` after any bulk regex pass.

#### `%`-format strings with `.get()`

A regex that replaces `.get("key", default)` → `["key"]` inside a format expression like:

```python
print("Rounds: %s" % config.setting.get("total_rounds", 0))
```

will produce:

```python
print("Rounds: %%s" %% config.setting["total_rounds"])  # WRONG
```

because the `%` character after the closing `"` triggers the regex. Apply the replacement only to `players.py` files, not `run_*.py` files, or add negative lookbehind for `%`.

#### `analysis.py` and `run_*.py` exemption

The `.get(key, default)` prohibition applies strictly to `players.py`. Analysis scripts (`analysis.py`) and runner scripts (`run_*.py`) work with potentially incomplete or partial records and may legitimately use `.get()` for safe data extraction. Do not apply automated fixes to those files.

### 10.9 Repair Script Pattern

The canonical structure for a bulk repair script:

```python
import re, glob, py_compile, sys

files = sorted(glob.glob("examples/**/players.py", recursive=True))
fixed = 0

for f in files:
    with open(f) as fh:
        content = fh.read()
    original = content

    # Apply targeted, well-scoped transformations here
    # ...

    if content != original:
        with open(f, "w") as fh:
            fh.write(content)
        fixed += 1
        print(f"[FIXED] {f}")

print(f"\nFixed: {fixed} files")

# Always verify syntax after bulk edits
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))

if errors:
    print(f"\nSYNTAX ERRORS ({len(errors)}):")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"py_compile: ALL OK ({len(files)} files)")
```

Key principles:
- Always read → transform → compare before writing
- Always run `py_compile` after every bulk edit pass
- Fix one category per script; do not batch unrelated transformations
- Test on a single file first before running on all files at scale
