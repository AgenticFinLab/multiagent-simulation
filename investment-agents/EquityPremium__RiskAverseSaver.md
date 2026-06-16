# EquityPremium / Risk Averse Saver

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Risk Averse Saver |
| Canonical class | `RiskAverseSaver` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

LLM-driven risk-averse saver -- strong bond preference with prospect theory reasoning. Theory: simulation-bases.md Section 4.4.

## Financial Theory / Theoretical Basis

### LLM / `LLMRiskAverseSaver`
- LLM-driven risk-averse saver -- strong bond preference with prospect theory reasoning. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMRiskAverseSaver`
- RuleLLM conservative saver allocator. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMRiskAverseSaver`
- RAG conservative saver allocator. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, RuleLLM |
| initial_bond_ratio | LLM: `0.25`<br>RuleLLM: `0.25`<br>Rag: `0.25` | LLM, Rag, RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, RuleLLM |
| initial_cash_ratio | LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, RuleLLM |
| initial_stock_shares | LLM: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EquityPremium.LLM.prompts:LLM_RISK_AVERSE_SYS', 'user_message': 'examples.EquityPremium.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EquityPremium.RuleLLM.prompts:RULELLM_CONSERVATIVE_INVESTOR_SYS', 'user_message': 'examples.EquityPremium.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EquityPremium.Rag.prompts:RAGLLM_CONSERVATIVE_INVESTOR_SYS', 'user_message': 'examples.EquityPremium.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_risk_averse | LLM Risk-Averse Saver | `LLMRiskAverseSaver` | 3 | `examples/EquityPremium/LLM/players.py` |
| RuleLLM | rulellm_risk_averse | RuleLLM Risk-Averse Saver | `RuleLLMRiskAverseSaver` | 3 | `examples/EquityPremium/RuleLLM/players.py` |
| Rag | ragllm_risk_averse | RAG Risk-Averse Saver | `RagLLMRiskAverseSaver` | 3 | `examples/EquityPremium/Rag/players.py` |

## Source Docstring Excerpts

### LLM / `LLMRiskAverseSaver`

```text
LLM-driven risk-averse saver -- strong bond preference with prospect theory reasoning. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMRiskAverseSaver`

```text
RuleLLM conservative saver allocator. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMRiskAverseSaver`

```text
RAG conservative saver allocator. Theory: simulation-bases.md Section 4.4.
```
