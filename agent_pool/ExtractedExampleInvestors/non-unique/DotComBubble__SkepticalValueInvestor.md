# DotComBubble / Skeptical Value Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DotComBubble |
| Agent type | Skeptical Value Investor |
| Canonical class | `SkepticalValueInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

Fundamental investor that sells extreme overvaluation and buys post-crash undervaluation. It is stabilizing but can be early.

## Financial Theory / Theoretical Basis

### Rule / `SkepticalValueInvestor`
- Theory: simulation-bases.md Section 4.4 -- SkepticalValueInvestor
- Theoretical basis: Graham (1949) value investing; Abreu & Brunnermeier (2003) rational arbitrageurs too early.

### LLM / `LLMSkepticalValueInvestor`
- LLM-driven skeptical value investor -- avoids overvalued tech, waits for crash. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMSkepticalValueInvestor`
- RuleLLM-driven skeptical value investor -- value threshold rules embedded. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMSkepticalValueInvestor`
- RAG-augmented skeptical value investor -- fundamental anchor with historical crash knowledge. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| buy_pf | Rule: `1.2`<br>LLM: `1.2`<br>RuleLLM: `1.2`<br>Rag: `1.2` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DotComBubble.LLM.prompts:LLM_SKEPTICAL_VALUE_INVESTOR_SYS', 'user_message': 'examples.DotComBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_SKEPTICAL_VALUE_INVESTOR_SYS', 'user_message': 'examples.DotComBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.DotComBubble.Rag.prompts:RAG_SKEPTICAL_VALUE_INVESTOR_SYS', 'user_message': 'examples.DotComBubble.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| max_pf | Rule: `3.0`<br>LLM: `3.0`<br>RuleLLM: `3.0`<br>Rag: `3.0` | LLM, Rag, Rule, RuleLLM |
| order_size | Rule: `400` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_buy_threshold | Rule: `-0.1` | Rule |
| value_sell_threshold | Rule: `0.2` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | skepticalvalueinvestor | SkepticalValueInvestor | `SkepticalValueInvestor` | 1 | `examples/DotComBubble/Rule/players.py` |
| LLM | skepticalvalueinvestor | SkepticalValueInvestor | `LLMSkepticalValueInvestor` | 1 | `examples/DotComBubble/LLM/players.py` |
| RuleLLM | skepticalvalueinvestor | SkepticalValueInvestor | `RuleLLMSkepticalValueInvestor` | 1 | `examples/DotComBubble/RuleLLM/players.py` |
| Rag | skepticalvalueinvestor | SkepticalValueInvestor | `RagLLMSkepticalValueInvestor` | 1 | `examples/DotComBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 SkepticalValueInvestor

#### Section 4.4.1 Summary

Fundamental investor that sells extreme overvaluation and buys post-crash undervaluation. It is stabilizing but can be early.

#### Section 4.4.2 Theoretical and Empirical Foundation

The basis is value investing (Section 2.4) combined with limits to arbitrage (Section 2.5). Fundamental investors can identify overvaluation while still underperforming before the peak.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < value_buy_threshold` | buy | supports price after crash | Section 2.4 |
| `deviation > value_sell_threshold` | sell | restrains overvaluation | Section 2.4 |

#### Section 4.4.4 Behavioral Framework

```
if deviation < value_buy_threshold: buy min(order_size, cash / price)
elif deviation > value_sell_threshold: sell min(order_size, position)
else: hold
```

#### Section 4.4.5 Decision Process Walkthrough

At price 125 and fundamental 100 with sell threshold 20%, the investor sells because the asset is overvalued.

#### Section 4.4.6 Worked Numerical Example

With position 300 and `order_size = 400`, sell quantity is `min(400, 300) = 300`.

#### Section 4.4.7 Academic References

Graham (1949); Shiller (2000); Abreu & Brunnermeier (2003).

## Source Docstring Excerpts

### Rule / `SkepticalValueInvestor`

```text
Avoids overvalued tech stocks -- waits for correction, then buys.

Theory: simulation-bases.md Section 4.4 -- SkepticalValueInvestor
Theoretical basis: Graham (1949) value investing; Abreu & Brunnermeier (2003) rational arbitrageurs too early.
See simulation-bases.md Section 4.4 for mathematical model.
Role: stabilizing.
```

### LLM / `LLMSkepticalValueInvestor`

```text
LLM-driven skeptical value investor -- avoids overvalued tech, waits for crash. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMSkepticalValueInvestor`

```text
RuleLLM-driven skeptical value investor -- value threshold rules embedded. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMSkepticalValueInvestor`

```text
RAG-augmented skeptical value investor -- fundamental anchor with historical crash knowledge. Theory: simulation-bases.md Section 4.4.
```
