# GFC2008 / Distressed Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GFC2008 |
| Agent type | Distressed Buyer |
| Canonical class | `DistressedBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`DistressedBuyer` represents capital prepared to buy deeply discounted structured-credit assets after forced selling. It is stabilizing but activates only after severe discounts.

## Financial Theory / Theoretical Basis

### Rule / `DistressedBuyer`
- Theory: simulation-bases.md Section 4.4 -- DistressedBuyer
- Theoretical basis: Distressed debt investing (Griffin & Xu, 2009).

### LLM / `LLMDistressedBuyer`
- LLM-driven DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMDistressedBuyer`
- RuleLLM-driven DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMDistressedBuyer`
- RAG-augmented DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| discount_threshold | Rule: `0.2`<br>LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `5000000.0`<br>LLM: `5000000.0`<br>RuleLLM: `5000000.0`<br>Rag: `5000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GFC2008.LLM.prompts:LLM_DISTRESSED_BUYER_SYS', 'user_message': 'examples.GFC2008.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_DISTRESSED_BUYER_SYS', 'user_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GFC2008.Rag.prompts:RAGLLM_DISTRESSED_BUYER_SYS', 'user_message': 'examples.GFC2008.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | distressedbuyer | DistressedBuyer | `DistressedBuyer` | 1 | `examples/GFC2008/Rule/players.py` |
| LLM | distressedbuyer | DistressedBuyer | `LLMDistressedBuyer` | 1 | `examples/GFC2008/LLM/players.py` |
| RuleLLM | distressedbuyer | DistressedBuyer | `RuleLLMDistressedBuyer` | 1 | `examples/GFC2008/RuleLLM/players.py` |
| Rag | distressedbuyer | DistressedBuyer | `RagLLMDistressedBuyer` | 1 | `examples/GFC2008/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 DistressedBuyer

#### Section 4.4.1 Summary

`DistressedBuyer` represents capital prepared to buy deeply discounted structured-credit assets after forced selling. It is stabilizing but activates only after severe discounts.

#### Section 4.4.2 Theoretical and Empirical Foundation

The basis is distressed-investing evidence and crisis-era recovery trading. The agent partially absorbs fire-sale supply, but its cash deployment is capped.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -discount_threshold` | buy with 30% of cash, capped at 1,000 units | stabilizes deep discounts | Section 2 Theory 3 |
| otherwise | hold | waits for margin of safety | Section 2 Theory 3 |

#### Section 4.4.4 Behavioral Framework

```
if deviation < -discount_threshold:
    buy min(1000, int(cash * 0.30 / price))
else:
    hold
```

#### Section 4.4.5 Decision Process Walkthrough

With deviation -25% and `discount_threshold = 0.20`, the buyer deploys capital because the discount is deep enough to compensate for crisis risk.

#### Section 4.4.6 Worked Numerical Example

With cash 5,000,000 and price 75, 30% cash could buy far above 1,000 units, so the cap binds at 1,000.

#### Section 4.4.7 Academic References

Griffin & Xu (2009); Bernanke (2015) for crisis-recovery context.

## Source Docstring Excerpts

### Rule / `DistressedBuyer`

```text
Theory: simulation-bases.md Section 4.4 -- DistressedBuyer

Theoretical basis: Distressed debt investing (Griffin & Xu, 2009).
Buys assets at deep discount during panic selling.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMDistressedBuyer`

```text
LLM-driven DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMDistressedBuyer`

```text
RuleLLM-driven DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMDistressedBuyer`

```text
RAG-augmented DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md Section 4.4.
```
