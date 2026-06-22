# FlashCrash2010 / Stop Loss Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash2010 |
| Agent type | Stop Loss Trader |
| Canonical class | `StopLossTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Stop-loss cascade generator; forced seller at pre-set level.

## Financial Theory / Theoretical Basis

### Rule / `StopLossTrader`
- Theory: simulation-bases.md Section 4.4 -- StopLossTrader
- Theoretical basis: Stop-loss cascade mechanism; fixed stop levels trigger

### LLM / `LLMStopLossTrader`
- LLM-driven stop-loss trader -- cascade selling via LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMStopLossTrader`
- Hybrid: Stop-loss trigger rules + LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMStopLossTrader`
- RAG-augmented stop-loss trader -- trigger rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_price | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1000`<br>LLM: `1000`<br>RuleLLM: `1000`<br>Rag: `1000` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash2010.LLM.prompts:LLM_STOP_LOSS_SYS', 'user_message': 'examples.FlashCrash2010.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_STOP_LOSS_SYS', 'user_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FlashCrash2010.Rag.prompts:RAGLLM_STOP_LOSS_SYS', 'user_message': 'examples.FlashCrash2010.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `1000`<br>LLM: `1000`<br>RuleLLM: `1000`<br>Rag: `1000` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stop_percentage | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | stoplosstrader | StopLossTrader | `StopLossTrader` | 3 | `examples/FlashCrash2010/Rule/players.py` |
| LLM | stoplosstrader | StopLossTrader | `LLMStopLossTrader` | 3 | `examples/FlashCrash2010/LLM/players.py` |
| RuleLLM | stoplosstrader | StopLossTrader | `RuleLLMStopLossTrader` | 3 | `examples/FlashCrash2010/RuleLLM/players.py` |
| Rag | stoplosstrader | StopLossTrader | `RagLLMStopLossTrader` | 3 | `examples/FlashCrash2010/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 StopLossTrader

**Role:** Stop-loss cascade generator; forced seller at pre-set level.

**Behavioural model:**
```python
stop_level = entry_price * (1 - stop_percentage)
if price <= stop_level and position > 0 and not stopped:
    quantity = -position              # sell entire position
    stopped = True
else:
    quantity = 0
provides_liquidity: False
agent_type: "stoploss"
```

**Parameters:** `stop_percentage`, `initial_position`, `entry_price`

**Decision rule:** Holds position until price touches `stop_level`; then sells the entire position in one round (one-shot exit).

**Market effect:** Large, sudden sell orders that deplete `Depth` and trigger further price drops, setting off the next wave of stop-losses.

**Theory:** Brunnermeier & Pedersen (2005) -- stop-level predatory targeting.

**Diversity:** Varied `stop_percentage` (0.02-0.08) -> multi-wave cascade as successive levels are hit.

**Distinguishing feature:** Fires once and permanently exits (`stopped = True`); `agent_type = "stoploss"`.

---

## Source Docstring Excerpts

### Rule / `StopLossTrader`

```text
Trader with stop-loss orders - creates cascade selling.

Theory: simulation-bases.md Section 4.4 -- StopLossTrader
Theoretical basis: Stop-loss cascade mechanism; fixed stop levels trigger
correlated market sells that accelerate the crash once momentum begins.
See simulation-bases.md Section 4.4 for mathematical model.

Parameters from config extras:
    - initial_cash, initial_position, stop_percentage, position_size, entry_price,
      custom_state_hot_limit, record_path
```

### LLM / `LLMStopLossTrader`

```text
LLM-driven stop-loss trader -- cascade selling via LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMStopLossTrader`

```text
Hybrid: Stop-loss trigger rules + LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMStopLossTrader`

```text
RAG-augmented stop-loss trader -- trigger rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md Section 4.4.
```
