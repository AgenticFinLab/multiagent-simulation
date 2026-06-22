# StatusQuoBias / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | StatusQuoBias |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents uninformed background flow from liquidity needs, mistakes, or idiosyncratic portfolio changes.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: noise-trader model.

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.

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
| llm | LLM: `{'sys_message': 'examples.StatusQuoBias.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.StatusQuoBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.StatusQuoBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.StatusQuoBias.Rag.prompts:RAGLLM_NOISE_TRADER_SYS', 'user_message': 'examples.StatusQuoBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.95, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| noise_size | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noisetrader | NoiseTrader | `NoiseTrader` | 2 | `examples/StatusQuoBias/Rule/players.py` |
| LLM | noisetrader | NoiseTrader | `LLMNoiseTrader` | 2 | `examples/StatusQuoBias/LLM/players.py` |
| RuleLLM | noisetrader | NoiseTrader | `RuleLLMNoiseTrader` | 2 | `examples/StatusQuoBias/RuleLLM/players.py` |
| Rag | noisetrader | NoiseTrader | `RagLLMNoiseTrader` | 2 | `examples/StatusQuoBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### Section 4.5.1 Summary

This investor represents uninformed background flow from liquidity needs,
mistakes, or idiosyncratic portfolio changes.

It prevents the market from being fully deterministic and supplies baseline
orders for volume and price-path variation.

#### Section 4.5.2 Theoretical and Empirical Foundation

Black (1986) defines noise as information-free trading that makes markets
possible but imperfect. De Long et al. (1990) show that noise-trader risk can
affect prices.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| Random draw below `trade_probability` | Buy or sell random size | Background liquidity | Section 2.5 |
| Random draw above threshold | Hold | No informational content | Section 2.5 |

#### Section 4.5.4 Behavioral Framework

The agent uses `trade_probability` and `noise_size`. Action direction is random;
quantity is bounded by affordability and inventory.

#### Section 4.5.5 Decision Process Walkthrough

If the random draw activates and direction is buy, the order size is sampled
between 1 and `noise_size` shares, then capped by cash.

#### Section 4.5.6 Worked Numerical Example

```text
trade_probability=0.30, noise_size=100
draw=0.21 -> active; sampled quantity=64; action=random buy/sell
```

#### Section 4.5.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Noise-trader concept. |
| 2 | De Long et al. (1990), *Journal of Political Economy*, https://doi.org/10.1086/261703 | Noise-trader risk and price effects. |

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: noise-trader model.
See simulation-bases.md Section 4.5 for mathematical model.

Parameters from config extras:
    - trade_probability
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RagLLM noise trader providing random baseline liquidity. Theory: simulation-bases.md Section 4.5.
```
