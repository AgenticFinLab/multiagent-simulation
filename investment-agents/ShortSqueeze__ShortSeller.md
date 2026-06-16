# ShortSqueeze / Short Seller

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ShortSqueeze |
| Agent type | Short Seller |
| Canonical class | `ShortSeller` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Holds short exposure and buys to cover when losses exceed a threshold. **Theoretical and Empirical Basis**: Short-sale constraints, borrow scarcity, and margin pressure from Section 2.1. **Design Purpose**: Generate forced buy demand during price spikes. **Behavioral Framework**: Uses `short_entry_price`, `short_initial_position`, `cover_threshold`, and current price. **Decision Process**: If current price is above entry by more than `cover_threshold`, buy enough shares to close part of the short position; otherwise hold. **Worked Numerical Example**: With `short_entry_price=30`, `cover_threshold=0.20`, and price at 39, the 30% loss exceeds the trigger, so a short position of -50 covers 25 shares. **Academic References**: Miller (1977), DOI: 10.1111/j.1540-6261.1977.tb03317.x; Duffie, Garleanu, and Pedersen (2002), DOI: 10.1111/1540-6261.00461.

## Financial Theory / Theoretical Basis

### Rule / `ShortSeller`
- Theory: simulation-bases.md Section 4.1

### LLM / `LLMShortSeller`
- Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMShortSeller`
- Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMShortSeller`
- Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| cover_threshold | Rule: `0.2` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `-50.0`<br>RuleLLM: `-50.0`<br>Rag: `-50.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ShortSqueeze.LLM.prompts:LLM_SHORT_SELLER_SYS', 'user_message': 'examples.ShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_SHORT_SELLER_SYS', 'user_message': 'examples.ShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_SHORT_SELLER_SYS', 'user_message': 'examples.ShortSqueeze.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| short_entry_price | Rule: `30.0` | Rule |
| short_initial_position | Rule: `-50.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | short_seller | Short Seller | `ShortSeller` | 3 | `examples/ShortSqueeze/Rule/players.py` |
| LLM | llm_short_seller | LLM Short Seller | `LLMShortSeller` | 3 | `examples/ShortSqueeze/LLM/players.py` |
| RuleLLM | rulellm_short_seller | RuleLLM Short Seller | `RuleLLMShortSeller` | 3 | `examples/ShortSqueeze/RuleLLM/players.py` |
| Rag | ragllm_short_seller | RAG Short Seller | `RagLLMShortSeller` | 3 | `examples/ShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 ShortSeller

**Summary**: Holds short exposure and buys to cover when losses exceed a
threshold.
**Theoretical and Empirical Basis**: Short-sale constraints, borrow scarcity,
and margin pressure from Section 2.1.
**Design Purpose**: Generate forced buy demand during price spikes.
**Behavioral Framework**: Uses `short_entry_price`,
`short_initial_position`, `cover_threshold`, and current price.
**Decision Process**: If current price is above entry by more than
`cover_threshold`, buy enough shares to close part of the short position;
otherwise hold.
**Worked Numerical Example**: With `short_entry_price=30`,
`cover_threshold=0.20`, and price at 39, the 30% loss exceeds the trigger, so a
short position of -50 covers 25 shares.
**Academic References**: Miller (1977), DOI:
10.1111/j.1540-6261.1977.tb03317.x; Duffie, Garleanu, and Pedersen (2002),
DOI: 10.1111/1540-6261.00461.

## Source Docstring Excerpts

### Rule / `ShortSeller`

```text
Short seller who must cover when losses mount.
Theory: simulation-bases.md Section 4.1

Parameters from config extras:
    - short_initial_position, short_entry_price, cover_threshold
```

### LLM / `LLMShortSeller`

```text
Short seller - manages short position risk.

Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMShortSeller`

```text
Hybrid: ShortSeller rules + LLM reasoning.

Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMShortSeller`

```text
RAG-augmented short seller.

Theory: simulation-bases.md Section 4.1
```
