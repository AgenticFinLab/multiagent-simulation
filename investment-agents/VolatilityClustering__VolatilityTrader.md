# VolatilityClustering / Volatility Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | VolatilityClustering |
| Agent type | Volatility Trader |
| Canonical class | `VolatilityTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Changes exposure based on volatility regime. **Theoretical and Empirical Basis**: Volatility timing and volatility mean-reversion strategies. **Design Purpose**: Make volatility state directly affect order flow. **Behavioral Framework**: Uses `vol_lookback`, `high_vol_threshold`, `low_vol_threshold`, and `base_position_size`. **Decision Process**: Sell or reduce exposure when volatility is high relative to its moving average; buy or increase exposure in low-volatility regimes. **Worked Numerical Example**: If current volatility is 1.8 times its recent average and the high threshold is 1.5, the trader sells. **Academic References**: Engle (1982), DOI: 10.2307/1912773; Bollerslev (1986), DOI: 10.1016/0304-4076(86)90063-1; volatility timing literature.

## Financial Theory / Theoretical Basis

### Rule / `VolatilityTrader`
- Theory: simulation-bases.md Section 4.5.

### LLM / `LLMVolatilityTrader`
- LLM VolatilityTrader. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMVolatilityTrader`
- Hybrid VolatilityTrader. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMVolatilityTrader`
- RAG VolatilityTrader. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `15.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| high_vol_threshold | Rule: `1.5` | Rule |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.VolatilityClustering.LLM.prompts:LLM_VOLATILITY_TRADER_SYS', 'user_message': 'examples.VolatilityClustering.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_VOLATILITY_TRADER_SYS', 'user_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_VOLATILITY_TRADER_SYS', 'user_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| low_vol_threshold | Rule: `0.7` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| vol_lookback | Rule: `5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | volatility_trader | Volatility Trader | `VolatilityTrader` | 1 | `examples/VolatilityClustering/Rule/players.py` |
| LLM | llm_volatility_trader | LLM Volatility Trader | `LLMVolatilityTrader` | 1 | `examples/VolatilityClustering/LLM/players.py` |
| RuleLLM | rulellm_volatility_trader | RuleLLM Volatility Trader | `RuleLLMVolatilityTrader` | 1 | `examples/VolatilityClustering/RuleLLM/players.py` |
| Rag | ragllm_volatility_trader | RAG Volatility Trader | `RagLLMVolatilityTrader` | 1 | `examples/VolatilityClustering/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 VolatilityTrader

**Summary**: Changes exposure based on volatility regime.
**Theoretical and Empirical Basis**: Volatility timing and volatility
mean-reversion strategies.
**Design Purpose**: Make volatility state directly affect order flow.
**Behavioral Framework**: Uses `vol_lookback`, `high_vol_threshold`,
`low_vol_threshold`, and `base_position_size`.
**Decision Process**: Sell or reduce exposure when volatility is high relative
to its moving average; buy or increase exposure in low-volatility regimes.
**Worked Numerical Example**: If current volatility is 1.8 times its recent
average and the high threshold is 1.5, the trader sells.
**Academic References**: Engle (1982), DOI: 10.2307/1912773; Bollerslev (1986),
DOI: 10.1016/0304-4076(86)90063-1; volatility timing literature.

## Source Docstring Excerpts

### Rule / `VolatilityTrader`

```text
Volatility regime trader - sells in high vol, buys in low vol.

Theory: simulation-bases.md Section 4.5.

Parameters from config extras:
    - vol_lookback, high_vol_threshold, low_vol_threshold, base_position_size
```

### LLM / `LLMVolatilityTrader`

```text
LLM VolatilityTrader. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMVolatilityTrader`

```text
Hybrid VolatilityTrader. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMVolatilityTrader`

```text
RAG VolatilityTrader. Theory: simulation-bases.md Section 4.5.
```
