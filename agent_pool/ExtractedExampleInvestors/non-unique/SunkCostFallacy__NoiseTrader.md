# SunkCostFallacy / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SunkCostFallacy |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents uninformed liquidity and idiosyncratic retail flow.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: noise-trader model.

### LLM / `LLMNoiseTrader`
- LLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RagLLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `200`<br>LLM: `200`<br>RuleLLM: `200`<br>Rag: `200` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SunkCostFallacy.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.SunkCostFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/SunkCostFallacy/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/SunkCostFallacy/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/SunkCostFallacy/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/SunkCostFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### Section 4.5.1 Summary

This investor represents uninformed liquidity and idiosyncratic retail flow.

It adds background volume without systematically encoding the sunk-cost
mechanism.

#### Section 4.5.2 Theoretical and Empirical Foundation

Black (1986) defines noise trading as non-informational order flow that remains
essential to market functioning.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| Random draw below `trade_probability` | Random buy or sell | Baseline liquidity | Section 2.5 |
| Otherwise | Hold | No informational action | Section 2.5 |

#### Section 4.5.4 Behavioral Framework

The agent uses `trade_probability` and `noise_size`. Direction is random and
quantity is bounded by cash or inventory.

#### Section 4.5.5 Decision Process Walkthrough

If the random draw activates, the order direction is sampled and quantity is
drawn from `1..noise_size`.

#### Section 4.5.6 Worked Numerical Example

```text
trade_probability=0.30, noise_size=100
draw=0.12 -> active; quantity=64; direction=random
```

#### Section 4.5.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Noise-trader baseline. |

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: noise-trader model.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RagLLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.
```
