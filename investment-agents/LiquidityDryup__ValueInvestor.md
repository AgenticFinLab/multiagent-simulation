# LiquidityDryup / Value Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LiquidityDryup |
| Agent type | Value Investor |
| Canonical class | `ValueInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

Momentum-style LLM investor using the legacy class name. Theory: simulation-bases.md Section 4.4

## Financial Theory / Theoretical Basis

### LLM / `LLMValueInvestor`
- Momentum-style LLM investor using the legacy class name. Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMValueInvestor`
- Hybrid: MomentumTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMValueInvestor`
- RAG-augmented: ValueInvestor rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.4

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
| llm | LLM: `{'sys_message': 'examples.LiquidityDryup.LLM.prompts:LLM_VALUE_SYS', 'user_message': 'examples.LiquidityDryup.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.LiquidityDryup.RuleLLM.prompts:RULELLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.LiquidityDryup.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.LiquidityDryup.Rag.prompts:RAGLLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.LiquidityDryup.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_value | LLM Value Investor | `LLMValueInvestor` | 2 | `examples/LiquidityDryup/LLM/players.py` |
| RuleLLM | rulellm_value | RuleLLM Value Investor | `RuleLLMValueInvestor` | 2 | `examples/LiquidityDryup/RuleLLM/players.py` |
| Rag | ragllm_value | RAG Value Investor | `RagLLMValueInvestor` | 2 | `examples/LiquidityDryup/Rag/players.py` |

## Source Docstring Excerpts

### LLM / `LLMValueInvestor`

```text
Momentum-style LLM investor using the legacy class name. Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMValueInvestor`

```text
Hybrid: MomentumTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMValueInvestor`

```text
RAG-augmented: ValueInvestor rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.4
```
