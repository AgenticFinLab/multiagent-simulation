# AsianFinancialCrisis / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AsianFinancialCrisis |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

NoiseTrader represents uninformed retail FX speculators and random order flow participants who trade on impulse, rumour, and random sentiment rather than any systematic signal. In the AsianFinancialCrisis simulation, NoiseTrader serves a specific design purpose: it prevents crisis-driven mispricings from following overly smooth paths, adds realistic background volatility consistent with emerging-market FX noise, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its activity rate (`trade_probability = 0.30`) is higher than in developed-market scenarios, reflecting the elevated noise in crisis-era EM currency markets.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical Basis: Noise trader model (Black, 1986)

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM noise trader with explicit trade probability rules. Theory: simulation-bases.md Section 4.5.

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
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `200000.0`<br>LLM: `200000.0`<br>RuleLLM: `200000.0`<br>Rag: `200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1000.0`<br>LLM: `1000.0`<br>RuleLLM: `1000.0`<br>Rag: `1000.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 3 | `examples/AsianFinancialCrisis/Rule/players.py` |
| LLM | noise_trader | Noise Trader | `LLMNoiseTrader` | 3 | `examples/AsianFinancialCrisis/LLM/players.py` |
| RuleLLM | noise_trader | Noise Trader | `RuleLLMNoiseTrader` | 3 | `examples/AsianFinancialCrisis/RuleLLM/players.py` |
| Rag | ragllm_noise_trader | RAG Noise Trader | `RagLLMNoiseTrader` | 3 | `examples/AsianFinancialCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### 4.5.1  Summary

NoiseTrader represents uninformed retail FX speculators and random order flow participants who trade on impulse, rumour, and random sentiment rather than any systematic signal. In the AsianFinancialCrisis simulation, NoiseTrader serves a specific design purpose: it prevents crisis-driven mispricings from following overly smooth paths, adds realistic background volatility consistent with emerging-market FX noise, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its activity rate (`trade_probability = 0.30`) is higher than in developed-market scenarios, reflecting the elevated noise in crisis-era EM currency markets.

#### 4.5.2  Theoretical and Empirical Foundation

**Noise Trading and Market Microstructure**:
- Theory / Study: Noise Trading and Its Market Effects
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Noise traders (those who trade on noise rather than information) create liquidity and price volatility. Without noise traders, markets would be too thin -- only information-based trades would occur. Noise traders make markets more active but also more volatile; their presence is necessary for market function.
- Mathematical Formulation: `Q_noise ~ Uniform(min_order, max_order)` with random direction (buy/sell each with probability 0.5); `P(trade) = 0.30` per round.
- Empirical Evidence: Black (1986) estimates that uninformed trading accounts for 30-60% of total order flow in liquid markets. In crisis-era EM FX markets, the proportion of noise-driven flow increases as institutional participants withdraw and retail speculators increase activity.
- Relevance to This Investor: `trade_probability = 0.30` (higher than the 0.05 in developed-market simulations) reflects the elevated noise documented in 1997 Asian FX markets; 3 instances produce realistic background volatility.

#### 4.5.3  Design Purpose and Activation Scenarios

Purpose: Add background noise that prevents the simulation from being too mechanistic; provide liquidity; model the realistic presence of uninformed order flow in crisis-era EM FX markets.

Activation Scenarios:
- With probability 0.30 per round: trades (70% chance of holding each round).
- Random direction (buy or sell with equal probability).
- Random quantity drawn from Uniform(min_order, max_order).

Market Contribution: **Neutral** -- expected net demand = 0 over many rounds; but provides random demand shocks that add realistic noise to crisis price dynamics.

#### 4.5.4  Behavioral Framework

- Trigger: `random() < trade_probability = 0.30`
- Direction: `random() > 0.5 -> buy; else sell`
- Sizing: `Q ~ Uniform(min_order, max_order)`
- Constrained by cash (buy) or position (sell)

#### 4.5.5  Decision Process Walkthrough

```
Round 15 (mid-crisis):
  Step 1: random() = 0.22 < 0.30 -> active this round
  Step 2: random() = 0.38 < 0.5 -> sell
  Step 3: quantity = Uniform(min_order, max_order) -> drawn quantity (constrained by position)
  Action: sell at current price

Round 16:
  Step 1: random() = 0.85 > 0.30 -> inactive; hold
```

#### 4.5.6  Worked Numerical Example

```
Market state:  price = 88.0 (deviation = -0.12),  NoiseTrader position = 200 shares

Trade fires (probability 0.30 rolls 0.22):
  direction: random = 0.65 > 0.5 -> buy
  quantity:  drawn from Uniform range -> 150 shares (constrained by cash)

Decision: action = buy, quantity = 150
Market impact: adds +150 to net demand D(t); contributes lambda x 150 = +$6.0 to price
Note: A random buy during a deep crisis slightly slows the cascade -- realistic noise that
prevents the crisis path from being a smooth monotonic decline.
```

#### 4.5.7  Academic References

| # | Citation                                                                                                                                     | Notes                                                                           |
|---|----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                            | Foundational rationale for noise trading; establishes trade_probability concept |
| 2 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices. *JFE*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Establishes informed vs. uninformed order flow fractions                        |

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical Basis: Noise trader model (Black, 1986)
Market Role: neutral

Strategy:
    - With probability trade_probability: randomly buy or sell a random quantity
See simulation-bases.md Section 4.5.4.3 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader with explicit trade probability rules. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
```
