# FlashCrash / High Frequency Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash |
| Agent type | High Frequency Trader |
| Canonical class | `HighFrequencyTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Ultra-fast momentum trader; primary crash trigger.

## Financial Theory / Theoretical Basis

### Rule / `HighFrequencyTrader`
- Theory: simulation-bases.md Section 4.1 -- HighFrequencyTrader
- Theoretical basis: Kirilenko et al. (2017) HFT flash crash role; momentum

### LLM / `LLMHighFrequencyTrader`
- LLM-driven high-frequency trader -- momentum detection and rapid bets via LLM reasoning. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMHighFrequencyTrader`
- Hybrid: HFT momentum rules + LLM rapid reasoning. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMHighFrequencyTrader`
- RAG-augmented HFT -- momentum rules + LLM rapid reasoning + retrieved knowledge. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash.LLM.prompts:LLM_HFT_SYS', 'user_message': 'examples.FlashCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_HFT_SYS', 'user_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_HFT_SYS', 'user_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback | Rule: `2`<br>RuleLLM: `2`<br>Rag: `2` | Rag, Rule, RuleLLM |
| momentum_sensitivity | Rule: `3.0`<br>RuleLLM: `3.0`<br>Rag: `3.0` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| speed_advantage | Rule: `1.5`<br>RuleLLM: `1.5`<br>Rag: `1.5` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hft | HFT | `HighFrequencyTrader` | 3 | `examples/FlashCrash/Rule/players.py` |
| LLM | llm_hft | LLM High-Frequency Trader | `LLMHighFrequencyTrader` | 3 | `examples/FlashCrash/LLM/players.py` |
| RuleLLM | rulellm_hft | RuleLLM HFT | `RuleLLMHighFrequencyTrader` | 3 | `examples/FlashCrash/RuleLLM/players.py` |
| Rag | ragllm_hft | RAG HFT | `RagLLMHighFrequencyTrader` | 3 | `examples/FlashCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 HighFrequencyTrader

**Role:** Ultra-fast momentum trader; primary crash trigger.

**Behavioural model:**
```python
short_momentum = price_history[-1] / price_history[-short_window] - 1
signal = short_momentum * momentum_sensitivity
quantity = signal * base_position_size * speed_advantage  # clamped ±60
provides_liquidity: False
```

**Parameters:** `momentum_sensitivity`, `base_position_size`, `speed_advantage`, `short_window`

**Decision rule:** Buys (sells) proportionally to short-term positive (negative) momentum. Never provides liquidity.

**Market effect:** Amplifies initial directional move; executes before slower agents.

**Theory:** Kirilenko et al. (2017) Section 4.1; positive-feedback momentum trading.

**Diversity:** Varied `momentum_sensitivity` (0.5-2.0) and `speed_advantage` (1.2-2.0) across instances.

**Distinguishing feature:** Fastest agent; drives the initial crash phase.

---

## Source Docstring Excerpts

### Rule / `HighFrequencyTrader`

```text
High-frequency trader with rapid momentum detection.

Theory: simulation-bases.md Section 4.1 -- HighFrequencyTrader
Theoretical basis: Kirilenko et al. (2017) HFT flash crash role; momentum
detection triggers rapid directional bets, amplifying price moves.
See simulation-bases.md Section 4.1 for mathematical model.

Parameters from config extras:
    - lookback, momentum_sensitivity, base_position_size, speed_advantage
```

### LLM / `LLMHighFrequencyTrader`

```text
LLM-driven high-frequency trader -- momentum detection and rapid bets via LLM reasoning. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMHighFrequencyTrader`

```text
Hybrid: HFT momentum rules + LLM rapid reasoning. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMHighFrequencyTrader`

```text
RAG-augmented HFT -- momentum rules + LLM rapid reasoning + retrieved knowledge. Theory: simulation-bases.md Section 4.1.
```
