# VolatilityClustering / Fundamentalist

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | VolatilityClustering |
| Agent type | Fundamentalist |
| Canonical class | `Fundamentalist` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trades toward fundamental value at a low frequency. **Theoretical and Empirical Basis**: Fundamental anchoring and stabilizing value demand. **Design Purpose**: Damp excessive deviation and prevent unbounded price drift. **Behavioral Framework**: Uses `trade_frequency`, `value_sensitivity`, `base_position_size`, and `value_noise_std`. **Decision Process**: Trade only on configured rounds; estimate value with noise; buy undervaluation and sell overvaluation. **Worked Numerical Example**: If price is 95 and noisy estimated value is 100, the positive deviation creates a buy order scaled by value sensitivity. **Academic References**: Graham (1949); Brock and Hommes (1998), DOI: 10.1016/S0165-1889(98)00011-6.

## Financial Theory / Theoretical Basis

### Rule / `Fundamentalist`
- Fundamentalist investor with slow mean reversion behavior.
- Theory: simulation-bases.md Section 4.1.

### LLM / `LLMFundamentalist`
- LLM Fundamentalist. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMFundamentalist`
- Hybrid Fundamentalist. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMFundamentalist`
- RAG Fundamentalist. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `20.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.VolatilityClustering.LLM.prompts:LLM_FUNDAMENTALIST_SYS', 'user_message': 'examples.VolatilityClustering.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_FUNDAMENTALIST_SYS', 'user_message': 'examples.VolatilityClustering.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_FUNDAMENTALIST_SYS', 'user_message': 'examples.VolatilityClustering.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_frequency | Rule: `3` | Rule |
| value_noise_std | Rule: `2.0` | Rule |
| value_sensitivity | Rule: `0.5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamentalist | Fundamentalist Investor | `Fundamentalist` | 2 | `examples/VolatilityClustering/Rule/players.py` |
| LLM | llm_fundamentalist | LLM Fundamentalist | `LLMFundamentalist` | 2 | `examples/VolatilityClustering/LLM/players.py` |
| RuleLLM | rulellm_fundamentalist | RuleLLM Fundamentalist | `RuleLLMFundamentalist` | 2 | `examples/VolatilityClustering/RuleLLM/players.py` |
| Rag | ragllm_fundamentalist | RAG Fundamentalist | `RagLLMFundamentalist` | 2 | `examples/VolatilityClustering/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 Fundamentalist

**Summary**: Trades toward fundamental value at a low frequency.
**Theoretical and Empirical Basis**: Fundamental anchoring and stabilizing value
demand.
**Design Purpose**: Damp excessive deviation and prevent unbounded price drift.
**Behavioral Framework**: Uses `trade_frequency`, `value_sensitivity`,
`base_position_size`, and `value_noise_std`.
**Decision Process**: Trade only on configured rounds; estimate value with
noise; buy undervaluation and sell overvaluation.
**Worked Numerical Example**: If price is 95 and noisy estimated value is 100,
the positive deviation creates a buy order scaled by value sensitivity.
**Academic References**: Graham (1949); Brock and Hommes (1998), DOI:
10.1016/S0165-1889(98)00011-6.

## Source Docstring Excerpts

### Rule / `Fundamentalist`

```text
Fundamentalist investor with slow mean reversion behavior.

Theory: simulation-bases.md Section 4.1.

Parameters from config extras:
    - trade_frequency, value_sensitivity, base_position_size, value_noise_std
```

### LLM / `LLMFundamentalist`

```text
LLM Fundamentalist. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMFundamentalist`

```text
Hybrid Fundamentalist. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMFundamentalist`

```text
RAG Fundamentalist. Theory: simulation-bases.md Section 4.1.
```
