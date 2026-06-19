# FlashCrash / Algorithmic Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash |
| Agent type | Algorithmic Trader |
| Canonical class | `AlgorithmicTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** Trend-following algorithm; mid-speed amplifier.

## Financial Theory / Theoretical Basis

### Rule / `AlgorithmicTrader`
- Theory: simulation-bases.md Section 4.3 -- AlgorithmicTrader
- Theoretical basis: Trend-following algorithm as positive-feedback mechanism;

### LLM / `LLMAlgorithmicTrader`
- LLM-driven algorithmic trader -- trend-following momentum via LLM systematic reasoning. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMAlgorithmicTrader`
- Hybrid: Trend-following algorithm rules + LLM systematic reasoning. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMAlgorithmicTrader`
- RAG-augmented algorithmic trader -- trend-following rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `25.0`<br>RuleLLM: `25.0`<br>Rag: `25.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash.LLM.prompts:LLM_ALGO_SYS', 'user_message': 'examples.FlashCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_ALGO_SYS', 'user_message': 'examples.FlashCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_ALGO_SYS', 'user_message': 'examples.FlashCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback | Rule: `3`<br>RuleLLM: `3`<br>Rag: `3` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trend_multiplier | Rule: `10`<br>RuleLLM: `10`<br>Rag: `10` | Rag, Rule, RuleLLM |
| trend_sensitivity | Rule: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | algo_trader | Algorithmic Trader | `AlgorithmicTrader` | 2 | `examples/FlashCrash/Rule/players.py` |
| LLM | llm_algo | LLM Algorithmic Trader | `LLMAlgorithmicTrader` | 2 | `examples/FlashCrash/LLM/players.py` |
| RuleLLM | rulellm_algo | RuleLLM Algorithmic Trader | `RuleLLMAlgorithmicTrader` | 2 | `examples/FlashCrash/RuleLLM/players.py` |
| Rag | ragllm_algo | RAG Algorithmic Trader | `RagLLMAlgorithmicTrader` | 2 | `examples/FlashCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 AlgorithmicTrader

**Role:** Trend-following algorithm; mid-speed amplifier.

**Behavioural model:**
```python
trend = price_history[-1] / price_history[-trend_window] - 1
quantity = trend * trend_sensitivity * base_position_size * trend_multiplier
quantity = clamp(quantity, -40, 40)
provides_liquidity: False
```

**Parameters:** `trend_sensitivity`, `base_position_size`, `trend_multiplier`, `trend_window`

**Decision rule:** Buys (sells) in proportion to the return over a medium lookback window.

**Market effect:** Reinforces trend after HFT initiates it; sustains selling pressure during crash.

**Theory:** De Long et al. (1990) -- positive-feedback speculation.

**Diversity:** Varied `trend_sensitivity` (0.5-2.0) and `trend_window` (3-10 rounds).

**Distinguishing feature:** Medium lookback window; bridges HFT and slower stop-loss agents.

---

## Source Docstring Excerpts

### Rule / `AlgorithmicTrader`

```text
Algorithmic trend-following trader.

Theory: simulation-bases.md Section 4.3 -- AlgorithmicTrader
Theoretical basis: Trend-following algorithm as positive-feedback mechanism;
amplifies price moves during crash by following momentum signals.
See simulation-bases.md Section 4.3 for mathematical model.

Parameters from config extras:
    - lookback, trend_sensitivity, base_position_size, trend_multiplier
```

### LLM / `LLMAlgorithmicTrader`

```text
LLM-driven algorithmic trader -- trend-following momentum via LLM systematic reasoning. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMAlgorithmicTrader`

```text
Hybrid: Trend-following algorithm rules + LLM systematic reasoning. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMAlgorithmicTrader`

```text
RAG-augmented algorithmic trader -- trend-following rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3.
```
