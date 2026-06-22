# EquityPremium / Institutional Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Institutional Investor |
| Canonical class | `InstitutionalInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

LLM-driven institutional investor -- balanced allocation using risk-neutral framework. Theory: simulation-bases.md Section 4.3.

## Financial Theory / Theoretical Basis

### LLM / `LLMInstitutionalInvestor`
- LLM-driven institutional investor -- balanced allocation using risk-neutral framework. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMInstitutionalInvestor`
- RuleLLM risk-neutral institutional allocator. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMInstitutionalInvestor`
- RAG risk-neutral institutional allocator. Theory: simulation-bases.md Section 4.3.

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
| llm | LLM: `{'sys_message': 'examples.EquityPremium.LLM.prompts:LLM_INSTITUTIONAL_SYS', 'user_message': 'examples.EquityPremium.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EquityPremium.RuleLLM.prompts:RULELLM_RISK_NEUTRAL_INVESTOR_SYS', 'user_message': 'examples.EquityPremium.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EquityPremium.Rag.prompts:RAGLLM_RISK_NEUTRAL_INVESTOR_SYS', 'user_message': 'examples.EquityPremium.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_institutional | LLM Institutional Investor | `LLMInstitutionalInvestor` | 1 | `examples/EquityPremium/LLM/players.py` |
| RuleLLM | rulellm_institutional | RuleLLM Institutional Investor | `RuleLLMInstitutionalInvestor` | 1 | `examples/EquityPremium/RuleLLM/players.py` |
| Rag | ragllm_institutional | RAG Institutional Investor | `RagLLMInstitutionalInvestor` | 1 | `examples/EquityPremium/Rag/players.py` |

## Source Docstring Excerpts

### LLM / `LLMInstitutionalInvestor`

```text
LLM-driven institutional investor -- balanced allocation using risk-neutral framework. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMInstitutionalInvestor`

```text
RuleLLM risk-neutral institutional allocator. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMInstitutionalInvestor`

```text
RAG risk-neutral institutional allocator. Theory: simulation-bases.md Section 4.3.
```
