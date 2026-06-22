# MarketCrash / Bottom Fisher

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Bottom Fisher |
| Canonical class | `BottomFisher` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A contrarian buyer that enters after large discounts. **Theoretical and Empirical Basis**: Contrarian and value demand can absorb forced sales after large deviations. **Design Purpose**: Test whether opportunistic capital stabilizes the crash. **Behavioral Framework**: Uses crash-buy threshold, discount threshold, buy size, and lookback window. **Decision Process**: Wait until price is sufficiently discounted or recent returns indicate a crash; then submit buy orders subject to cash constraints. **Worked Numerical Example**: If price is 15% below fundamental and the discount threshold is 10%, the agent submits a buy order of the configured size. **Academic References**: Lakonishok, Shleifer, and Vishny (1994, DOI: 10.1111/j.1540-6261.1994.tb04772.x).

## Financial Theory / Theoretical Basis

### Rule / `BottomFisher`
- Theory: simulation-bases.md Section 4.6.

### LLM / `LLMBottomFisher`
- LLM BottomFisher. Theory: simulation-bases.md Section 4.6.

### RuleLLM / `RuleLLMBottomFisher`
- Hybrid BottomFisher. Theory: simulation-bases.md Section 4.6.

### Rag / `RagLLMBottomFisher`
- RAG BottomFisher. Theory: simulation-bases.md Section 4.6.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_size | Rule: `15.0` | Rule |
| crash_buy_threshold | Rule: `-0.03` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| discount_threshold | Rule: `0.1` | Rule |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `10.0`<br>RuleLLM: `10.0`<br>Rag: `10.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MarketCrash.LLM.prompts:LLM_BOTTOM_FISHER_SYS', 'user_message': 'examples.MarketCrash.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_BOTTOM_FISHER_SYS', 'user_message': 'examples.MarketCrash.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_BOTTOM_FISHER_SYS', 'user_message': 'examples.MarketCrash.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback | Rule: `10` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | bottom_fisher | Bottom Fisher | `BottomFisher` | 1 | `examples/MarketCrash/Rule/players.py` |
| LLM | llm_bottom_fisher | LLM Bottom Fisher | `LLMBottomFisher` | 1 | `examples/MarketCrash/LLM/players.py` |
| RuleLLM | rulellm_bottom_fisher | RuleLLM Bottom Fisher | `RuleLLMBottomFisher` | 1 | `examples/MarketCrash/RuleLLM/players.py` |
| Rag | ragllm_bottom_fisher | RAG Bottom Fisher | `RagLLMBottomFisher` | 1 | `examples/MarketCrash/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 BottomFisher

**Summary**: A contrarian buyer that enters after large discounts.
**Theoretical and Empirical Basis**: Contrarian and value demand can absorb
forced sales after large deviations.
**Design Purpose**: Test whether opportunistic capital stabilizes the crash.
**Behavioral Framework**: Uses crash-buy threshold, discount threshold, buy
size, and lookback window.
**Decision Process**: Wait until price is sufficiently discounted or recent
returns indicate a crash; then submit buy orders subject to cash constraints.
**Worked Numerical Example**: If price is 15% below fundamental and the
discount threshold is 10%, the agent submits a buy order of the configured size.
**Academic References**: Lakonishok, Shleifer, and Vishny (1994, DOI:
10.1111/j.1540-6261.1994.tb04772.x).

## Source Docstring Excerpts

### Rule / `BottomFisher`

```text
Bottom fisher buying during crashes.

Theory: simulation-bases.md Section 4.6.

Parameters from config extras:
    - crash_buy_threshold, discount_threshold, buy_size, lookback
```

### LLM / `LLMBottomFisher`

```text
LLM BottomFisher. Theory: simulation-bases.md Section 4.6.
```

### RuleLLM / `RuleLLMBottomFisher`

```text
Hybrid BottomFisher. Theory: simulation-bases.md Section 4.6.
```

### Rag / `RagLLMBottomFisher`

```text
RAG BottomFisher. Theory: simulation-bases.md Section 4.6.
```
