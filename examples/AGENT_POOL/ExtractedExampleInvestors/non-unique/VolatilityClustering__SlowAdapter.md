# VolatilityClustering / Slow Adapter

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | VolatilityClustering |
| Agent type | Slow Adapter |
| Canonical class | `SlowAdapter` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Updates perceived value gradually after market moves. **Theoretical and Empirical Basis**: Adaptive expectations and delayed information processing. **Design Purpose**: Extend the effect of shocks over several rounds. **Behavioral Framework**: Uses `lookback_window`, `update_weight`, and `base_position_size`. **Decision Process**: Blend fundamental value with a long moving average; trade only when the deviation is material. **Worked Numerical Example**: After a price shock, the moving average remains away from fundamental and influences orders for multiple rounds. **Academic References**: Hommes (2006); Brock and Hommes (1998), DOI: 10.1016/S0165-1889(98)00011-6.

## Financial Theory / Theoretical Basis

### Rule / `SlowAdapter`
- Theory: simulation-bases.md Section 4.4.

### LLM / `LLMSlowAdapter`
- LLM SlowAdapter. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMSlowAdapter`
- Hybrid SlowAdapter. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMSlowAdapter`
- RAG SlowAdapter. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `10.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.VolatilityClustering.LLM.prompts:LLM_SLOW_ADAPTER_SYS', 'user_message': 'examples.VolatilityClustering.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_SLOW_ADAPTER_SYS', 'user_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_SLOW_ADAPTER_SYS', 'user_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback_window | Rule: `10` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| update_weight | Rule: `0.1` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | slow_adapter | Slow Adapter | `SlowAdapter` | 1 | `examples/VolatilityClustering/Rule/players.py` |
| LLM | llm_slow_adapter | LLM Slow Adapter | `LLMSlowAdapter` | 1 | `examples/VolatilityClustering/LLM/players.py` |
| RuleLLM | rulellm_slow_adapter | RuleLLM Slow Adapter | `RuleLLMSlowAdapter` | 1 | `examples/VolatilityClustering/RuleLLM/players.py` |
| Rag | ragllm_slow_adapter | RAG Slow Adapter | `RagLLMSlowAdapter` | 1 | `examples/VolatilityClustering/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 SlowAdapter

**Summary**: Updates perceived value gradually after market moves.
**Theoretical and Empirical Basis**: Adaptive expectations and delayed
information processing.
**Design Purpose**: Extend the effect of shocks over several rounds.
**Behavioral Framework**: Uses `lookback_window`, `update_weight`, and
`base_position_size`.
**Decision Process**: Blend fundamental value with a long moving average; trade
only when the deviation is material.
**Worked Numerical Example**: After a price shock, the moving average remains
away from fundamental and influences orders for multiple rounds.
**Academic References**: Hommes (2006); Brock and Hommes (1998), DOI:
10.1016/S0165-1889(98)00011-6.

## Source Docstring Excerpts

### Rule / `SlowAdapter`

```text
Conservative investor with slow information processing.

Theory: simulation-bases.md Section 4.4.

Parameters from config extras:
    - lookback_window, update_weight, base_position_size
```

### LLM / `LLMSlowAdapter`

```text
LLM SlowAdapter. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMSlowAdapter`

```text
Hybrid SlowAdapter. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMSlowAdapter`

```text
RAG SlowAdapter. Theory: simulation-bases.md Section 4.4.
```
