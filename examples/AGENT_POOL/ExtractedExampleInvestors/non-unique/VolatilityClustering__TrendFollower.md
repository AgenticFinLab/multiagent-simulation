# VolatilityClustering / Trend Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | VolatilityClustering |
| Agent type | Trend Follower |
| Canonical class | `TrendFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades with recent price trends and sizes by volatility. **Theoretical and Empirical Basis**: Chartist and managed-futures trend following. **Design Purpose**: Amplify shocks and help create clustered large returns. **Behavioral Framework**: Uses `lookback_window`, `trend_threshold`, `baseline_volatility`, `volatility_sensitivity`, and `base_position_size`. **Decision Process**: Compare current price with recent average; trade in the trend direction if the signal exceeds threshold; increase size in high volatility. **Worked Numerical Example**: A price above its lookback average with volatility twice baseline creates a larger buy order. **Academic References**: Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x; Moskowitz, Ooi, and Pedersen (2012), DOI: 10.1016/j.jfineco.2011.11.003.

## Financial Theory / Theoretical Basis

### Rule / `TrendFollower`
- Theory: simulation-bases.md Section 4.2.

### LLM / `LLMTrendFollower`
- LLM TrendFollower. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMTrendFollower`
- Hybrid TrendFollower. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMTrendFollower`
- RAG TrendFollower. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `30.0` | Rule |
| baseline_volatility | Rule: `1.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.VolatilityClustering.LLM.prompts:LLM_TREND_FOLLOWER_SYS', 'user_message': 'examples.VolatilityClustering.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_TREND_FOLLOWER_SYS', 'user_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_TREND_FOLLOWER_SYS', 'user_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback_window | Rule: `3` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trend_threshold | Rule: `0.005` | Rule |
| volatility_sensitivity | Rule: `0.8` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | trend_follower | Trend Follower | `TrendFollower` | 3 | `examples/VolatilityClustering/Rule/players.py` |
| LLM | llm_trend_follower | LLM Trend Follower | `LLMTrendFollower` | 3 | `examples/VolatilityClustering/LLM/players.py` |
| RuleLLM | rulellm_trend_follower | RuleLLM Trend Follower | `RuleLLMTrendFollower` | 3 | `examples/VolatilityClustering/RuleLLM/players.py` |
| Rag | ragllm_trend_follower | RAG Trend Follower | `RagLLMTrendFollower` | 3 | `examples/VolatilityClustering/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 TrendFollower

**Summary**: Trades with recent price trends and sizes by volatility.
**Theoretical and Empirical Basis**: Chartist and managed-futures trend
following.
**Design Purpose**: Amplify shocks and help create clustered large returns.
**Behavioral Framework**: Uses `lookback_window`, `trend_threshold`,
`baseline_volatility`, `volatility_sensitivity`, and `base_position_size`.
**Decision Process**: Compare current price with recent average; trade in the
trend direction if the signal exceeds threshold; increase size in high
volatility.
**Worked Numerical Example**: A price above its lookback average with volatility
twice baseline creates a larger buy order.
**Academic References**: Jegadeesh and Titman (1993), DOI:
10.1111/j.1540-6261.1993.tb04702.x; Moskowitz, Ooi, and Pedersen (2012), DOI:
10.1016/j.jfineco.2011.11.003.

## Source Docstring Excerpts

### Rule / `TrendFollower`

```text
Trend-following investor with high volatility sensitivity.

Theory: simulation-bases.md Section 4.2.

Parameters from config extras:
    - lookback_window, base_position_size, volatility_sensitivity
    - baseline_volatility, trend_threshold
```

### LLM / `LLMTrendFollower`

```text
LLM TrendFollower. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMTrendFollower`

```text
Hybrid TrendFollower. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMTrendFollower`

```text
RAG TrendFollower. Theory: simulation-bases.md Section 4.2.
```
