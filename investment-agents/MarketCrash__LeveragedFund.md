# MarketCrash / Leveraged Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Leveraged Fund |
| Canonical class | `LeveragedFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

LLM LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.

## Financial Theory / Theoretical Basis

### LLM / `LLMLeveragedFund`
- LLM LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMLeveragedFund`
- Hybrid LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMLeveragedFund`
- RAG LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, RuleLLM |
| initial_position | LLM: `80.0`<br>RuleLLM: `80.0`<br>Rag: `80.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MarketCrash.LLM.prompts:LLM_LEVERAGED_FUND_SYS', 'user_message': 'examples.MarketCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_LEVERAGED_HEDGE_FUND_SYS', 'user_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_LEVERAGED_HEDGE_FUND_SYS', 'user_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_leveraged_fund | LLM Leveraged Fund | `LLMLeveragedFund` | 3 | `examples/MarketCrash/LLM/players.py` |
| RuleLLM | rulellm_leveraged_fund | RuleLLM Leveraged Fund | `RuleLLMLeveragedFund` | 3 | `examples/MarketCrash/RuleLLM/players.py` |
| Rag | ragllm_leveraged_fund | RAG Leveraged Fund | `RagLLMLeveragedFund` | 3 | `examples/MarketCrash/Rag/players.py` |

## Source Docstring Excerpts

### LLM / `LLMLeveragedFund`

```text
LLM LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMLeveragedFund`

```text
Hybrid LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMLeveragedFund`

```text
RAG LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.
```
