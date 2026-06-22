# AssetBubble / Conservative Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Conservative Holder |
| Canonical class | `ConservativeHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

ConservativeHolder is the stabilizing allocation agent. It does not chase momentum, does not short mispricing, and does not use leverage. Instead, it maintains a strategic target position and rebalances slowly when its holdings drift away from that target. This provides a weak but persistent stabilizing flow that prevents the simulated market from being composed only of aggressive speculators and arbitrageurs.

## Financial Theory / Theoretical Basis

### Rule / `ConservativeHolder`
- Theory: simulation-bases.md Section 4.6 -- ConservativeHolder
- Behavior:
- - Holds steady position
- - Rarely trades
- - Provides small stabilizing force
- - Rebalances slowly
- Effect: VERY WEAKLY STABILIZING
- Formula:
- -> simulation-bases.md Section 4.6 -- ConservativeHolder (Rule-Based Behavior)

### LLM / `LLMConservativeHolder`
- LLM conservative holder. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.

### RuleLLM / `RuleLLMConservativeHolder`
- Hybrid rebalancing rules with LLM reasoning. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.

### Rag / `RagLLMConservativeHolder`
- RAG-augmented rebalancing rules with retrieved knowledge. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AssetBubble.LLM.prompts:LLM_CONSERVATIVE_SYS', 'user_message': 'examples.AssetBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_CONSERVATIVE_SYS', 'user_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_CONSERVATIVE_SYS', 'user_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rebalance_frequency | Rule: `10`<br>LLM: `10`<br>RuleLLM: `10`<br>Rag: `10` | LLM, Rag, Rule, RuleLLM |
| rebalance_rate | Rule: `0.2`<br>LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, Rule, RuleLLM |
| target_position | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | conservative_holder | Conservative Holder | `ConservativeHolder` | 2 | `examples/AssetBubble/Rule/players.py` |
| LLM | llm_conservative | LLM Conservative Holder | `LLMConservativeHolder` | 2 | `examples/AssetBubble/LLM/players.py` |
| RuleLLM | rulellm_conservative | RuleLLM Conservative Holder | `RuleLLMConservativeHolder` | 2 | `examples/AssetBubble/RuleLLM/players.py` |
| Rag | ragllm_conservative | RAG Conservative Holder | `RagLLMConservativeHolder` | 2 | `examples/AssetBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 ConservativeHolder

ConservativeHolder is the stabilizing allocation agent. It does not chase
momentum, does not short mispricing, and does not use leverage. Instead, it
maintains a strategic target position and rebalances slowly when its holdings
drift away from that target. This provides a weak but persistent stabilizing
flow that prevents the simulated market from being composed only of aggressive
speculators and arbitrageurs.

Behavioral rule:

```text
if round % rebalance_frequency != 0:
    quantity = 0
else:
    gap = target_position - current_position
    quantity = clamp(gap * rebalance_rate, -10, +10)
```

Parameters are loaded from `configs/AssetBubble/{Variant}/players.yml` under
`conservative_holder`, `llm_conservative`, `rulellm_conservative`, or
`ragllm_conservative`.

## Source Docstring Excerpts

### Rule / `ConservativeHolder`

```text
Conservative long-term holder providing stability.
Theory: simulation-bases.md Section 4.6 -- ConservativeHolder

Behavior:
    - Holds steady position
    - Rarely trades
    - Provides small stabilizing force
    - Rebalances slowly

Effect: VERY WEAKLY STABILIZING

Formula:
    gap = target_position - position
    quantity = gap x rebalance_rate  (every N rounds, capped at ±10)
    -> simulation-bases.md Section 4.6 -- ConservativeHolder (Rule-Based Behavior)

Parameters from config extras:
    - target_position, rebalance_frequency, rebalance_rate
    -> simulation-bases.md Section 6
```

### LLM / `LLMConservativeHolder`

```text
LLM conservative holder. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.
```

### RuleLLM / `RuleLLMConservativeHolder`

```text
Hybrid rebalancing rules with LLM reasoning. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.
```

### Rag / `RagLLMConservativeHolder`

```text
RAG-augmented rebalancing rules with retrieved knowledge. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.
```
