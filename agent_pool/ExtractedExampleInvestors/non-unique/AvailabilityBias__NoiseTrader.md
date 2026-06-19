# AvailabilityBias / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AvailabilityBias |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The NoiseTrader is a random, uninformed participant whose trades are unconnected to any market signal -- fundamental or cognitive bias. In the availability bias context, the NoiseTrader models background retail investors who trade based on personal liquidity needs, random news interpretation, or behavioral impulses unrelated to either fundamentals or the specific availability heuristic being studied. Its primary role is to ensure the simulation does not converge to a perfectly deterministic price path, enabling meaningful statistical analysis across runs.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Black (1986) -- Noise traders.

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AvailabilityBias.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AvailabilityBias.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500.0` | Rule |
| min_order | Rule: `100.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 3 | `examples/AvailabilityBias/Rule/players.py` |
| LLM | llm_noise_trader | LLM Noise Trader | `LLMNoiseTrader` | 3 | `examples/AvailabilityBias/LLM/players.py` |
| RuleLLM | rulellm_noise_trader | RuleLLM Noise Trader | `RuleLLMNoiseTrader` | 3 | `examples/AvailabilityBias/RuleLLM/players.py` |
| Rag | ragllm_noise_trader | RAG Noise Trader | `RagLLMNoiseTrader` | 3 | `examples/AvailabilityBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Investor: NoiseTrader

#### 4.5.1  Summary

The NoiseTrader is a random, uninformed participant whose trades are unconnected to any market signal -- fundamental or cognitive bias. In the availability bias context, the NoiseTrader models background retail investors who trade based on personal liquidity needs, random news interpretation, or behavioral impulses unrelated to either fundamentals or the specific availability heuristic being studied. Its primary role is to ensure the simulation does not converge to a perfectly deterministic price path, enabling meaningful statistical analysis across runs.

#### 4.5.2  Theoretical and Empirical Foundation

**Theory 1: Noise Trading Theory (Black)**
- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.2307/2328481
- Core Insight: Noise traders provide liquidity without which informed and systematic traders could not execute. Their stochastic behavior ensures market prices are not perfectly determined by the modeled agents, adding realistic variance. trade_probability = 0.30 (30% per round) is higher than the BlackMonday1987 simulation (5%) because availability bias episodes are subtler and require more background noise to prevent the simulation from being too mechanically predictable.
- Empirical Evidence: Black (1986) estimates noise traders account for 20-40% of daily volume. trade_probability = 0.30 consistent with a higher retail participation rate typical of behavioral-bias-driven episodes (vs. institutional-dominated crisis simulations).

**Theory 2: Retail Investor Behavior (Odean)**
- Citation: Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773-806. DOI: 10.1111/j.1540-6261.2000.tb04002.x
- Core Insight: Retail investors trade excessively and in directions uncorrelated with fundamental value, consistent with the noise trader model. Barber & Odean find retail trading volume negatively predicts subsequent returns, consistent with uninformed noise trading.
- Empirical Evidence: Average retail investor trades approximately 75% of portfolio per year -- equivalent to trading probability of ~0.3% per day. In simulation rounds of longer time horizon, 30% per round is calibrated to match retail turnover.

#### 4.5.3  Design Purpose and Activation Scenarios

**Purpose**: Add stochastic variation -- ensure that each simulation run produces a unique price path, enabling statistical comparison of bias effects across runs. Also models the genuine background retail order flow in availability-bias-driven markets.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**
- No signals used -- purely random. Does not observe any market data.

**4.5.4.2  Core Behavioral Mechanism**
1. Draw r ~ Uniform(0, 1). If r < 0.30: trade.
2. If trading: draw direction (buy/sell, 50/50); draw quantity ~ Uniform(100, 500).
3. Execute. Hold otherwise.

**4.5.4.3  Mathematical Model**
- Trade probability: P(trade) = 0.30 per round
- Direction: P(buy | trade) = P(sell | trade) = 0.5
- Sizing: Q ~ Uniform(100, 500)

| Parameter         | Value | Meaning                                 | Config Path                                        | Source          |
|-------------------|-------|-----------------------------------------|----------------------------------------------------|-----------------|
| trade_probability | 0.30  | Probability of trading in a given round | `configs/AvailabilityBias/Rule/players.yml -> noise_trader` | Black (1986)    |
| min_order         | 100   | Minimum random trade quantity           | `configs/AvailabilityBias/Rule/players.yml -> noise_trader` | Retail lot size |
| max_order         | 500   | Maximum random trade quantity           | `configs/AvailabilityBias/Rule/players.yml -> noise_trader` | Retail lot size |

**4.5.4.4  Behavioral Properties**
- Time horizon: Random
- Risk tolerance: Medium (unoptimized)
- Information asymmetry: None
- Psychological profile: Random, uninformed. In LLM variants, the persona uses varied language with no systematic strategy -- "I trade based on gut feeling and personal circumstances."

#### 4.5.5  Decision Process Walkthrough

Random draw r = 0.18 < 0.30 -> trade. Direction: sell. Quantity: 250. Order: sell 250 at current price.

#### 4.5.6  Worked Numerical Example

r = 0.42 >= 0.30 -> hold. No order sent this round.

r = 0.07 < 0.30 -> trade. Direction: buy. Quantity: 180. Order: buy 180 at current price. Net contribution: +180 to D(t); partially offsets any bias-driven selling in the same round by coincidence.

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                | Notes                                            |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| 1 | Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.2307/2328481                                                                   | Theoretical basis; trade_probability calibration |
| 2 | Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773-806. DOI: 10.1111/j.1540-6261.2000.tb04002.x | Retail overtrading; trade frequency calibration  |

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Black (1986) -- Noise traders.
Trades randomly with probability trade_probability each round.
See simulation-bases.md Section 4.5.4.3 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
```
