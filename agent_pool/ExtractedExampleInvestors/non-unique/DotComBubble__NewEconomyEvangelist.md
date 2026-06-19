# DotComBubble / New Economy Evangelist

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DotComBubble |
| Agent type | New Economy Evangelist |
| Canonical class | `NewEconomyEvangelist` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

Narrative-driven buyer who treats internet adoption as a reason to keep buying even under overvaluation. This investor is destabilizing because persistent demand lifts the market above fundamental value.

## Financial Theory / Theoretical Basis

### Rule / `NewEconomyEvangelist`
- Theory: simulation-bases.md Section 4.1 -- NewEconomyEvangelist
- Theoretical basis: Shiller (2000) narrative economics; tech evangelists dismiss P/E ratios as irrelevant.

### LLM / `LLMNewEconomyEvangelist`
- LLM-driven new economy evangelist -- ignores valuation, buys internet narrative. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMNewEconomyEvangelist`
- RuleLLM-driven new economy evangelist -- narrative rules embedded. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMNewEconomyEvangelist`
- RAG-augmented new economy evangelist -- narrative-driven buyer with historical bubble context. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_buy_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DotComBubble.LLM.prompts:LLM_NEW_ECONOMY_EVANGELIST_SYS', 'user_message': 'examples.DotComBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_NEW_ECONOMY_EVANGELIST_SYS', 'user_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.DotComBubble.Rag.prompts:RAG_NEW_ECONOMY_EVANGELIST_SYS', 'user_message': 'examples.DotComBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_pf_ratio | Rule: `10.0`<br>LLM: `10.0`<br>RuleLLM: `10.0`<br>Rag: `10.0` | LLM, Rag, Rule, RuleLLM |
| narrative_strength | Rule: `0.8`<br>LLM: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | LLM, Rag, Rule, RuleLLM |
| order_size | Rule: `600` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | neweconomyevangelist | NewEconomyEvangelist | `NewEconomyEvangelist` | 2 | `examples/DotComBubble/Rule/players.py` |
| LLM | neweconomyevangelist | NewEconomyEvangelist | `LLMNewEconomyEvangelist` | 2 | `examples/DotComBubble/LLM/players.py` |
| RuleLLM | neweconomyevangelist | NewEconomyEvangelist | `RuleLLMNewEconomyEvangelist` | 2 | `examples/DotComBubble/RuleLLM/players.py` |
| Rag | neweconomyevangelist | NewEconomyEvangelist | `RagLLMNewEconomyEvangelist` | 2 | `examples/DotComBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 NewEconomyEvangelist

#### Section 4.1.1 Summary

Narrative-driven buyer who treats internet adoption as a reason to keep buying even under overvaluation. This investor is destabilizing because persistent demand lifts the market above fundamental value.

#### Section 4.1.2 Theoretical and Empirical Foundation

The basis is narrative economics (Section 2.1). The agent maps dot-com-era claims that valuation multiples no longer applied into a buy-unless-crash rule.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > -0.20` | buy up to `order_size` | persistent bubble demand | Section 2.1 |
| `deviation < -0.30` | sell half-sized order if holding | late capitulation | Section 2.1 |

#### Section 4.1.4 Behavioral Framework

Information set: `price`, `fundamental`, `deviation`, `cash`, `position`. The agent does not estimate value independently; it accepts the new-economy narrative unless the crash is extreme.

```
if deviation > -0.20: buy min(order_size, cash / price)
elif deviation < -0.30: sell min(order_size / 2, position)
else: hold
```

#### Section 4.1.5 Decision Process Walkthrough

At price 130 and fundamental 100, deviation is +30%. The agent still buys because the market has not crashed below the capitulation threshold.

#### Section 4.1.6 Worked Numerical Example

With cash 100,000, price 130, and `order_size = 600`, the agent buys `min(600, floor(100000/130)) = 600` shares.

#### Section 4.1.7 Academic References

Shiller (2000); Shiller (2017).

## Source Docstring Excerpts

### Rule / `NewEconomyEvangelist`

```text
Believes in new paradigm -- ignores traditional valuation metrics during internet bubble.

Theory: simulation-bases.md Section 4.1 -- NewEconomyEvangelist
Theoretical basis: Shiller (2000) narrative economics; tech evangelists dismiss P/E ratios as irrelevant.
See simulation-bases.md Section 4.1 for mathematical model.
Role: destabilizing.
```

### LLM / `LLMNewEconomyEvangelist`

```text
LLM-driven new economy evangelist -- ignores valuation, buys internet narrative. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMNewEconomyEvangelist`

```text
RuleLLM-driven new economy evangelist -- narrative rules embedded. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMNewEconomyEvangelist`

```text
RAG-augmented new economy evangelist -- narrative-driven buyer with historical bubble context. Theory: simulation-bases.md Section 4.1.
```
