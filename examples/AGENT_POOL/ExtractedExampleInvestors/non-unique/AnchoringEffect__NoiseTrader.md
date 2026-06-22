# AnchoringEffect / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

NoiseTrader represents the uninformed retail participant who trades on impulse, rumour, and random sentiment rather than any systematic signal. In the AnchoringEffect simulation, NoiseTrader serves a specific design purpose: it prevents anchoring-induced mispricings from being too "clean" (perfect exponential decay), adds realistic background volatility, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its high trade volume (100-500 shares vs. 20 shares for other agents) means it has disproportionate short-term price impact.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theoretical basis: simulation-bases.md Section 2.6 (Black, 1986 -- Noise Trader Risk).
- Decision rule (simulation-bases.md Section 4.5 -- Rule-Based Behavior):

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AnchoringEffect.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AnchoringEffect.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500.0`<br>RuleLLM: `500.0`<br>Rag: `500.0` | Rag, Rule, RuleLLM |
| min_order | Rule: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 2 | `examples/AnchoringEffect/Rule/players.py` |
| LLM | noise_trader | Noise Trader | `LLMNoiseTrader` | 2 | `examples/AnchoringEffect/LLM/players.py` |
| RuleLLM | rulellm_noise | RuleLLM Noise Trader | `RuleLLMNoiseTrader` | 2 | `examples/AnchoringEffect/RuleLLM/players.py` |
| Rag | ragllm_noise | RAG Noise Trader | `RagLLMNoiseTrader` | 2 | `examples/AnchoringEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### 4.5.1  Summary

NoiseTrader represents the uninformed retail participant who trades on impulse, rumour, and random sentiment rather than any systematic signal. In the AnchoringEffect simulation, NoiseTrader serves a specific design purpose: it prevents anchoring-induced mispricings from being too "clean" (perfect exponential decay), adds realistic background volatility, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its high trade volume (100-500 shares vs. 20 shares for other agents) means it has disproportionate short-term price impact.

#### 4.5.2  Theoretical and Empirical Foundation

**Noise Trading and Market Microstructure**:
- Theory / Study: Noise Trading and Its Market Effects
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Noise traders (those who trade on noise rather than information) create liquidity and price volatility. Without noise traders, markets would be too thin -- only information-based trades would occur. Noise traders make markets more active but also more volatile; their presence is necessary for market function.
- Mathematical Formulation: `Q_noise ~ Uniform(min_order, max_order)` with random direction (buy/sell each with probability 0.5); `P(trade) = 0.05` per round.
- Empirical Evidence: Glosten & Milgrom (1985) estimate that uninformed (noise) trading accounts for 30-60% of total order flow in liquid equity markets. In the 9-investor simulation, 2 NoiseTrader instances with trade_probability = 0.05 provide sparse background liquidity without dominating systematic anchoring and rational-updating flows.
- Relevance to This Investor: Large order size (100-500 shares vs. 20 for anchoring agents) means even occasional trades create significant price volatility, adding realistic noise to the clean anchoring signal.

#### 4.5.3  Design Purpose and Activation Scenarios

Purpose: Add background noise that prevents the simulation from being too mechanistic; provide liquidity; model the realistic presence of uninformed order flow in all markets.

Activation Scenarios:
- With probability 0.05 per round: trades (95% chance of holding each round).
- Random direction (buy or sell with equal probability).
- Random quantity drawn from Uniform(100, 500).

Market Contribution: **Neutral** -- expected net demand = 0 over many rounds; but provides large random demand shocks that prevent prices from following a smooth path.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**: None -- NoiseTrader does not use any market signals systematically.

**4.5.4.2  Core Behavioral Mechanism**: Probabilistic random trading: trade with probability 0.05, otherwise hold. Trade direction and size are uniformly random.

**4.5.4.3  Mathematical Model**

- Trigger: `random() < trade_probability = 0.05`
- Direction: `random() > 0.5 -> buy; else sell`
- Sizing: `Q ~ Uniform(min_order = 100, max_order = 500)`
- Constrained by cash (buy) or position (sell)

**4.5.4.4  Behavioral Properties**

- Time horizon: Random -- no consistent horizon
- Risk tolerance: Not applicable -- no risk model
- Information asymmetry: None -- actively ignores all information
- Psychological profile: Pure noise; no systematic bias; models impulse trading, random sentiment, and order flow noise

#### 4.5.5  Decision Process Walkthrough

```
Round 47:
  Step 1: random() = 0.03 < 0.05 -> active this round
  Step 2: random() = 0.72 > 0.5 -> buy
  Step 3: quantity = Uniform(100, 500) -> 247 shares (constrained by cash)
  Action: buy 247 shares at current price

Round 48:
  Step 1: random() = 0.71 > 0.05 -> inactive; hold
```

#### 4.5.6  Worked Numerical Example

```
Market state:  price = 101.0; NoiseTrader cash = 5,000

Trade fires (probability 0.05 rolls 0.03):
  direction: random = 0.2 < 0.5 -> sell
  quantity:  Uniform(100, 500) -> 183 shares
  position check: current_position = 100 -> sell min(183, 100) = 100 shares (limited by position)

Decision: action = sell, quantity = 100, bid_price = 101.0
Market impact: adds -100 to net demand D(t); contributes lambda x (-100) = -$1.00 to price
Rationale: A large random sell creates a temporary downward price shock that may trigger
RationalUpdater to hold (price closer to F after shock) or MomentumTrader to sell (following the drop).
```

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                                                                                             | Notes                                                                           |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                                                                                                    | Foundational rationale for noise trading; establishes trade_probability concept |
| 2 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Establishes informed vs. uninformed order flow fractions                        |

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader providing background market liquidity.

Implements simulation-bases.md Section 4.5 -- NoiseTrader.
Theoretical basis: simulation-bases.md Section 2.6 (Black, 1986 -- Noise Trader Risk).

Decision rule (simulation-bases.md Section 4.5 -- Rule-Based Behavior):
    trade with probability trade_probability (0.05) each round
    direction: buy or sell with equal probability (0.5 each)
    quantity: random.uniform(min_order, max_order)

Parameters (simulation-bases.md Section 6):
    trade_probability: 0.05 (5% chance of trading per round)
    min_order: 100; max_order: 500 (quantity bounds)
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.
```
