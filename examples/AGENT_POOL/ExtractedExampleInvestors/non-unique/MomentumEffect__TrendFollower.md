# MomentumEffect / Trend Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Trend Follower |
| Canonical class | `TrendFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: An API-variant aggressive trend follower. **Theoretical and Empirical Basis**: Trend-following and crowded momentum strategies. **Design Purpose**: Increase API-variant continuation pressure without adding a passive rebalancer. **Behavioral Framework**: LLM, RuleLLM, and Rag variants use prompt rules based on medium-horizon momentum direction. **Decision Process**: Buy when the trend is positive, sell when it is negative, and size more aggressively than a baseline momentum trader when conviction is high. **Worked Numerical Example**: Positive 10-period momentum supports a larger buy than a moderate 5-period signal. **Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI: 10.1016/j.jfineco.2011.11.003.

## Financial Theory / Theoretical Basis

### LLM / `LLMTrendFollower`
- LLM TrendFollower. Theory: simulation-bases.md Section 4.7.

### RuleLLM / `RuleLLMTrendFollower`
- Hybrid TrendFollower. Theory: simulation-bases.md Section 4.7.

### Rag / `RagLLMTrendFollower`
- RAG TrendFollower. Theory: simulation-bases.md Section 4.7.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, RuleLLM |
| initial_position | LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MomentumEffect.LLM.prompts:LLM_TREND_FOLLOWER_SYS', 'user_message': 'examples.MomentumEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_TREND_FOLLOWER_SYS', 'user_message': 'examples.MomentumEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_TREND_FOLLOWER_SYS', 'user_message': 'examples.MomentumEffect.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_trend_follower | LLM Trend Follower | `LLMTrendFollower` | 2 | `examples/MomentumEffect/LLM/players.py` |
| RuleLLM | rulellm_trend_follower | RuleLLM Trend Follower | `RuleLLMTrendFollower` | 2 | `examples/MomentumEffect/RuleLLM/players.py` |
| Rag | ragllm_trend_follower | RAG Trend Follower | `RagLLMTrendFollower` | 2 | `examples/MomentumEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.7 TrendFollower

**Summary**: An API-variant aggressive trend follower.  
**Theoretical and Empirical Basis**: Trend-following and crowded momentum
strategies.  
**Design Purpose**: Increase API-variant continuation pressure without adding a
passive rebalancer.  
**Behavioral Framework**: LLM, RuleLLM, and Rag variants use prompt rules based
on medium-horizon momentum direction.  
**Decision Process**: Buy when the trend is positive, sell when it is negative,
and size more aggressively than a baseline momentum trader when conviction is
high.  
**Worked Numerical Example**: Positive 10-period momentum supports a larger
buy than a moderate 5-period signal.  
**Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI:
10.1016/j.jfineco.2011.11.003.

## Source Docstring Excerpts

### LLM / `LLMTrendFollower`

```text
LLM TrendFollower. Theory: simulation-bases.md Section 4.7.
```

### RuleLLM / `RuleLLMTrendFollower`

```text
Hybrid TrendFollower. Theory: simulation-bases.md Section 4.7.
```

### Rag / `RagLLMTrendFollower`

```text
RAG TrendFollower. Theory: simulation-bases.md Section 4.7.
```
