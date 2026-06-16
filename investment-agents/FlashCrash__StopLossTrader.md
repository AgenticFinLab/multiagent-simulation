# FlashCrash / Stop Loss Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash |
| Agent type | Stop Loss Trader |
| Canonical class | `StopLossTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Stop-loss cascade generator; forced seller at predetermined levels.

## Financial Theory / Theoretical Basis

### Rule / `StopLossTrader`
- Theory: simulation-bases.md Section 4.4 -- StopLossTrader
- Theoretical basis: Stop-loss cascade mechanism; pre-set exit triggers create

### LLM / `LLMStopLossTrader`
- LLM-driven stop-loss trader -- cascade selling triggers via LLM position management. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMStopLossTrader`
- Hybrid: Stop-loss cascade rules + LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMStopLossTrader`
- RAG-augmented stop-loss trader -- cascade rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_buy_price | Rule: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `50.0`<br>LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash.LLM.prompts:LLM_STOP_LOSS_SYS', 'user_message': 'examples.FlashCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_STOP_LOSS_SYS', 'user_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_STOP_LOSS_SYS', 'user_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stop_loss_percent | Rule: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | stop_loss | Stop Loss Trader | `StopLossTrader` | 3 | `examples/FlashCrash/Rule/players.py` |
| LLM | llm_stop_loss | LLM Stop-Loss Trader | `LLMStopLossTrader` | 3 | `examples/FlashCrash/LLM/players.py` |
| RuleLLM | rulellm_stop_loss | RuleLLM Stop-Loss Trader | `RuleLLMStopLossTrader` | 3 | `examples/FlashCrash/RuleLLM/players.py` |
| Rag | ragllm_stop_loss | RAG Stop-Loss Trader | `RagLLMStopLossTrader` | 3 | `examples/FlashCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 StopLossTrader

**Role:** Stop-loss cascade generator; forced seller at predetermined levels.

**Behavioural model:**
```python
stop_price = recent_high * (1 - stop_loss_percent)
if price < stop_price and position > 0:
    quantity = -position    # sell entire position
    stop_triggered = True
provides_liquidity: False
```

**Parameters:** `stop_loss_percent`, `base_position_size`

**Decision rule:** Holds until price breaches `stop_price`; then sells all shares in a single round.

**Market effect:** Lumpy cascade selling that arrives in waves as successive stop levels are hit.

**Theory:** Brunnermeier & Pedersen (2005) -- predatory stop-level targeting.

**Diversity:** Varied `stop_loss_percent` (0.02-0.10) -> different agents trigger at different price levels, creating multi-wave cascade.

**Distinguishing feature:** One-shot seller; once triggered, exits completely and stays out.

---

## Source Docstring Excerpts

### Rule / `StopLossTrader`

```text
Trader with stop-loss orders - creates cascade selling.

Theory: simulation-bases.md Section 4.4 -- StopLossTrader
Theoretical basis: Stop-loss cascade mechanism; pre-set exit triggers create
correlated sell orders that amplify the price decline in a feedback loop.
See simulation-bases.md Section 4.4 for mathematical model.

Parameters from config extras:
    - stop_loss_percent, initial_buy_price
```

### LLM / `LLMStopLossTrader`

```text
LLM-driven stop-loss trader -- cascade selling triggers via LLM position management. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMStopLossTrader`

```text
Hybrid: Stop-loss cascade rules + LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMStopLossTrader`

```text
RAG-augmented stop-loss trader -- cascade rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md Section 4.4.
```
