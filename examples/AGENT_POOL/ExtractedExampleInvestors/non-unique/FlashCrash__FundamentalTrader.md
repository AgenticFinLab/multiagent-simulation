# FlashCrash / Fundamental Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash |
| Agent type | Fundamental Trader |
| Canonical class | `FundamentalTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Value buyer; provides the recovery force.

## Financial Theory / Theoretical Basis

### Rule / `FundamentalTrader`
- Theory: simulation-bases.md Section 4.5 -- FundamentalTrader
- Theoretical basis: Value investing contrarianism; aggressive buying when price

### LLM / `LLMFundamentalTrader`
- LLM-driven fundamental trader -- value-based recovery buying via LLM analytical reasoning. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMFundamentalTrader`
- Hybrid: Value deviation rules + LLM analytical reasoning. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMFundamentalTrader`
- RAG-augmented fundamental trader -- value deviation rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `30.0`<br>RuleLLM: `30.0`<br>Rag: `30.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash.LLM.prompts:LLM_FUNDAMENTAL_SYS', 'user_message': 'examples.FlashCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_FUNDAMENTAL_SYS', 'user_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_FUNDAMENTAL_SYS', 'user_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_multiplier | Rule: `10`<br>RuleLLM: `10`<br>Rag: `10` | Rag, Rule, RuleLLM |
| value_sensitivity | Rule: `1.0`<br>RuleLLM: `1.0`<br>Rag: `1.0` | Rag, Rule, RuleLLM |
| value_threshold | Rule: `0.1`<br>RuleLLM: `0.1`<br>Rag: `0.1` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamental_trader | Fundamental Trader | `FundamentalTrader` | 2 | `examples/FlashCrash/Rule/players.py` |
| LLM | llm_fundamental | LLM Fundamental Trader | `LLMFundamentalTrader` | 2 | `examples/FlashCrash/LLM/players.py` |
| RuleLLM | rulellm_fundamental | RuleLLM Fundamental Trader | `RuleLLMFundamentalTrader` | 2 | `examples/FlashCrash/RuleLLM/players.py` |
| Rag | ragllm_fundamental | RAG Fundamental Trader | `RagLLMFundamentalTrader` | 2 | `examples/FlashCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 FundamentalTrader

**Role:** Value buyer; provides the recovery force.

**Behavioural model:**
```python
deviation = (fundamental - price) / fundamental
if deviation > value_threshold:
    quantity = deviation * base_position_size * value_sensitivity * value_multiplier
elif deviation < -value_threshold:
    quantity = deviation * base_position_size * value_sensitivity * value_multiplier  # sell
quantity = clamp(quantity, -50, 50)
provides_liquidity: True
```

**Parameters:** `value_threshold`, `base_position_size`, `value_sensitivity`, `value_multiplier`

**Decision rule:** Buys when market price is sufficiently below fundamental; sells when it is above. Always provides liquidity.

**Market effect:** Absorbs selling pressure during the crash trough; supplies stabilising net demand for recovery.

**Theory:** Shiller (1981) -- fundamental value as gravity.

**Diversity:** Varied `value_threshold` (0.03-0.10) -- more aggressive traders provide earlier stabilisation.

**Distinguishing feature:** Only consistently pro-cyclical liquidity provider; drives recovery phase.

---

## Source Docstring Excerpts

### Rule / `FundamentalTrader`

```text
Fundamental value trader - provides recovery force.

Theory: simulation-bases.md Section 4.5 -- FundamentalTrader
Theoretical basis: Value investing contrarianism; aggressive buying when price
deviates below fundamental provides the stabilizing recovery force.
See simulation-bases.md Section 4.5 for mathematical model.

Parameters from config extras:
    - value_threshold, base_position_size, value_sensitivity, value_multiplier
```

### LLM / `LLMFundamentalTrader`

```text
LLM-driven fundamental trader -- value-based recovery buying via LLM analytical reasoning. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMFundamentalTrader`

```text
Hybrid: Value deviation rules + LLM analytical reasoning. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMFundamentalTrader`

```text
RAG-augmented fundamental trader -- value deviation rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.5.
```
