# SunkCostFallacy / Opportunity Cost Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SunkCostFallacy |
| Agent type | Opportunity Cost Trader |
| Canonical class | `OpportunityCostTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor compares current exposure with the best available use of capital.

## Financial Theory / Theoretical Basis

### Rule / `OpportunityCostTrader`
- Theory: simulation-bases.md Section 4.4 -- OpportunityCostTrader
- Theoretical basis: opportunity cost analysis.

### LLM / `LLMOpportunityCostTrader`
- LLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMOpportunityCostTrader`
- RuleLLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMOpportunityCostTrader`
- RagLLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1300000.0`<br>LLM: `1300000.0`<br>RuleLLM: `1300000.0`<br>Rag: `1300000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_OPPORTUNITY_COST_TRADER_SYS', 'user_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_OPPORTUNITY_COST_TRADER_SYS', 'user_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SunkCostFallacy.Rag.prompts:RAGLLM_OPPORTUNITY_COST_TRADER_SYS', 'user_message': 'examples.SunkCostFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| realloc_threshold | Rule: `0.08`<br>LLM: `0.08`<br>RuleLLM: `0.08`<br>Rag: `0.08` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | opportunitycosttrader | OpportunityCostTrader | `OpportunityCostTrader` | 2 | `examples/SunkCostFallacy/Rule/players.py` |
| LLM | opportunitycosttrader | OpportunityCostTrader | `LLMOpportunityCostTrader` | 2 | `examples/SunkCostFallacy/LLM/players.py` |
| RuleLLM | opportunitycosttrader | OpportunityCostTrader | `RuleLLMOpportunityCostTrader` | 2 | `examples/SunkCostFallacy/RuleLLM/players.py` |
| Rag | opportunitycosttrader | OpportunityCostTrader | `RagLLMOpportunityCostTrader` | 2 | `examples/SunkCostFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 OpportunityCostTrader

#### Section 4.4.1 Summary

This investor compares current exposure with the best available use of capital.

Its role is to counter sunk-cost attachment through explicit opportunity-cost
reasoning.

#### Section 4.4.2 Theoretical and Empirical Foundation

Buchanan (1969) formalizes opportunity cost as the value of the best foregone
alternative. Portfolio theory applies this principle to capital allocation.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -realloc_threshold` | Buy | Reallocate into undervalued capital use | Section 2.5 |
| `deviation > realloc_threshold` | Sell | Reallocate away from overvalued exposure | Section 2.5 |
| Small deviation | Hold | Opportunity cost is not large enough | Section 2.5 |

#### Section 4.4.4 Behavioral Framework

The agent uses `realloc_threshold` and `position_size`. It is more selective
than `RationalCutter` because it waits for a larger opportunity-cost signal.

#### Section 4.4.5 Decision Process Walkthrough

At an 8% threshold, a 6% deviation is ignored, but a 10% deviation triggers
capital reallocation.

#### Section 4.4.6 Worked Numerical Example

```text
P=110, F=100, deviation=0.10, realloc_threshold=0.08
Q = 300 * 0.10 / 0.08 = 375 shares sold, capped by inventory
```

#### Section 4.4.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Buchanan (1969), *Cost and Choice* | Opportunity-cost principle. |
| 2 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x | Capital-allocation benchmark. |

## Source Docstring Excerpts

### Rule / `OpportunityCostTrader`

```text
Evaluates positions by opportunity cost, reallocates capital from underperformers.

Theory: simulation-bases.md Section 4.4 -- OpportunityCostTrader
Theoretical basis: opportunity cost analysis.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMOpportunityCostTrader`

```text
LLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMOpportunityCostTrader`

```text
RuleLLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMOpportunityCostTrader`

```text
RagLLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.
```
