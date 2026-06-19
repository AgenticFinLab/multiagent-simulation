# DotComBubble / Short Seller

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DotComBubble |
| Agent type | Short Seller |
| Canonical class | `ShortSeller` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

Investor betting against overvaluation while exposed to squeeze risk. It is stabilizing in theory but limited by timing and inventory constraints.

## Financial Theory / Theoretical Basis

### Rule / `ShortSeller`
- Theory: simulation-bases.md Section 4.5 -- ShortSeller
- Theoretical basis: Abreu & Brunnermeier (2003) limits to arbitrage; short sellers face synchronization risk.

### LLM / `LLMShortSeller`
- LLM-driven short seller -- bets against overvaluation, faces squeeze risk. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMShortSeller`
- RuleLLM-driven short seller -- short/cover threshold rules embedded. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMShortSeller`
- RAG-augmented short seller -- bets against bubble with historical limits-to-arbitrage knowledge. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| cover_threshold | Rule: `2.5`<br>LLM: `2.5`<br>RuleLLM: `2.5`<br>Rag: `2.5` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DotComBubble.LLM.prompts:LLM_SHORT_SELLER_SYS', 'user_message': 'examples.DotComBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_SHORT_SELLER_SYS', 'user_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.DotComBubble.Rag.prompts:RAG_SHORT_SELLER_SYS', 'user_message': 'examples.DotComBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `400` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| short_threshold | Rule: `5.0`<br>LLM: `5.0`<br>RuleLLM: `5.0`<br>Rag: `5.0` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | shortseller | ShortSeller | `ShortSeller` | 1 | `examples/DotComBubble/Rule/players.py` |
| LLM | shortseller | ShortSeller | `LLMShortSeller` | 1 | `examples/DotComBubble/LLM/players.py` |
| RuleLLM | shortseller | ShortSeller | `RuleLLMShortSeller` | 1 | `examples/DotComBubble/RuleLLM/players.py` |
| Rag | shortseller | ShortSeller | `RagLLMShortSeller` | 1 | `examples/DotComBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 ShortSeller

#### Section 4.5.1 Summary

Investor betting against overvaluation while exposed to squeeze risk. It is stabilizing in theory but limited by timing and inventory constraints.

#### Section 4.5.2 Theoretical and Empirical Foundation

The basis is synchronization risk (Section 2.5). Short sellers may be right about valuation and still lose money if the bubble keeps rising.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > short_threshold` | sell | pushes against overvaluation | Section 2.5 |
| `deviation < cover_threshold` | buy | covers after correction | Section 2.5 |

#### Section 4.5.4 Behavioral Framework

```
if deviation > short_threshold: sell min(order_size, position)
elif deviation < cover_threshold: buy min(order_size, cash / price)
else: hold
```

#### Section 4.5.5 Decision Process Walkthrough

At price 120 and fundamental 100 with `short_threshold = 0.15`, the short seller sells because overvaluation exceeds 15%.

#### Section 4.5.6 Worked Numerical Example

With position 400 and `order_size = 400`, sell quantity is 400.

#### Section 4.5.7 Academic References

Abreu & Brunnermeier (2003); Ofek & Richardson (2003).

## Source Docstring Excerpts

### Rule / `ShortSeller`

```text
Bets against overvalued stocks -- faces squeeze risk during bubble.

Theory: simulation-bases.md Section 4.5 -- ShortSeller
Theoretical basis: Abreu & Brunnermeier (2003) limits to arbitrage; short sellers face synchronization risk.
See simulation-bases.md Section 4.5 for mathematical model.
Role: stabilizing.
```

### LLM / `LLMShortSeller`

```text
LLM-driven short seller -- bets against overvaluation, faces squeeze risk. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMShortSeller`

```text
RuleLLM-driven short seller -- short/cover threshold rules embedded. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMShortSeller`

```text
RAG-augmented short seller -- bets against bubble with historical limits-to-arbitrage knowledge. Theory: simulation-bases.md Section 4.5.
```
