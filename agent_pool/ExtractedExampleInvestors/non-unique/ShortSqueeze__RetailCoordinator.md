# ShortSqueeze / Retail Coordinator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ShortSqueeze |
| Agent type | Retail Coordinator |
| Canonical class | `RetailCoordinator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | LLM, RuleLLM, Rag |

## Definition and Goal

Retail trader - aggressive bullish buyer.

## Financial Theory / Theoretical Basis

### LLM / `LLMRetailCoordinator`
- Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMRetailCoordinator`
- Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMRetailCoordinator`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, RuleLLM |
| initial_cash | LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, RuleLLM |
| initial_position | LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ShortSqueeze.LLM.prompts:LLM_RETAIL_COORD_SYS', 'user_message': 'examples.ShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_RETAIL_TRADER_SYS', 'user_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_RETAIL_TRADER_SYS', 'user_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| LLM | llm_retail_coord | LLM Retail Coordinator | `LLMRetailCoordinator` | 3 | `examples/ShortSqueeze/LLM/players.py` |
| RuleLLM | rulellm_retail_coord | RuleLLM Retail Coordinator | `RuleLLMRetailCoordinator` | 3 | `examples/ShortSqueeze/RuleLLM/players.py` |
| Rag | ragllm_retail_coord | RAG Retail Coordinator | `RagLLMRetailCoordinator` | 3 | `examples/ShortSqueeze/Rag/players.py` |

## Source Docstring Excerpts

### LLM / `LLMRetailCoordinator`

```text
Retail trader - aggressive bullish buyer.

Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMRetailCoordinator`

```text
Hybrid: RetailTrader rules + LLM reasoning.

Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMRetailCoordinator`

```text
RAG-augmented retail coordinator.

Theory: simulation-bases.md Section 4.3
```
