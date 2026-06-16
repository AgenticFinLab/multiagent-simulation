# AssetBubble / Rational Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Rational Arbitrageur |
| Canonical class | `RationalArbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

RationalArbitrageur represents the archetypal rational, fundamental-value investor who seeks to profit from mispricings by shorting overvalued assets or buying undervalued ones. This agent models hedge funds and sophisticated institutions that know asset prices are deviating from fundamentals and attempt to correct the mispricing. However, RationalArbitrageur is deliberately constrained by short-selling costs and position limits -- implementing the Shleifer-Vishny limits to arbitrage -- which means it cannot single-handedly deflate the bubble. Its role in the simulation is to provide a partial, bounded corrective force that keeps the bubble from growing infinitely but fails to prevent it from forming and persisting.

## Financial Theory / Theoretical Basis

### Rule / `RationalArbitrageur`
- Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur
- Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)
- - Arbitrageurs face constraints: short-selling costs, margin requirements
- - Cannot fully correct mispricings due to these limits
- - May be forced to close positions before prices correct
- Behavior:
- - Estimates true value (fundamental)
- - Shorts when price > fundamental (but faces costs)
- - Buys when price < fundamental
- - Limited by capital and short-selling costs
- Effect: WEAKLY STABILIZING - Cannot stop bubbles due to constraints
- Formula:
- -> simulation-bases.md Section 4.2 -- RationalArbitrageur (Rule-Based Behavior)

### LLM / `LLMRationalArbitrageur`
- LLM fundamental analyst. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.

### RuleLLM / `RuleLLMRationalArbitrageur`
- Hybrid deviation rules with LLM reasoning. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.

### Rag / `RagLLMRationalArbitrageur`
- RAG-augmented deviation rules with retrieved knowledge. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `25.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| deviation_threshold | Rule: `0.1`<br>RuleLLM: `0.05`<br>Rag: `0.05` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AssetBubble.LLM.prompts:LLM_ARBITRAGEUR_SYS', 'user_message': 'examples.AssetBubble.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_ARBITRAGEUR_SYS', 'user_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_ARBITRAGEUR_SYS', 'user_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_short_position | Rule: `40.0`<br>RuleLLM: `30.0`<br>Rag: `30.0` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| short_cost_sensitivity | Rule: `0.5`<br>RuleLLM: `2.0`<br>Rag: `2.0` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rational_arbitrageur | Rational Arbitrageur | `RationalArbitrageur` | 3 | `examples/AssetBubble/Rule/players.py` |
| LLM | llm_arbitrageur | LLM Rational Arbitrageur | `LLMRationalArbitrageur` | 3 | `examples/AssetBubble/LLM/players.py` |
| RuleLLM | rulellm_arbitrageur | RuleLLM Rational Arbitrageur | `RuleLLMRationalArbitrageur` | 3 | `examples/AssetBubble/RuleLLM/players.py` |
| Rag | ragllm_arbitrageur | RAG Rational Arbitrageur | `RagLLMRationalArbitrageur` | 3 | `examples/AssetBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 RationalArbitrageur

#### 4.2.1  Summary

RationalArbitrageur represents the archetypal rational, fundamental-value investor who seeks to profit from mispricings by shorting overvalued assets or buying undervalued ones. This agent models hedge funds and sophisticated institutions that know asset prices are deviating from fundamentals and attempt to correct the mispricing. However, RationalArbitrageur is deliberately constrained by short-selling costs and position limits -- implementing the Shleifer-Vishny limits to arbitrage -- which means it cannot single-handedly deflate the bubble. Its role in the simulation is to provide a partial, bounded corrective force that keeps the bubble from growing infinitely but fails to prevent it from forming and persisting.

#### 4.2.2  Theoretical and Empirical Foundation

**Limits to Arbitrage**:
- Theory / Study: Limits of Arbitrage Framework
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Rational arbitrage is limited by (a) short-selling costs that reduce profitability, (b) capital constraints and position limits from risk management, and (c) the risk that mispricings widen before correcting, forcing premature position closure. These frictions explain why large, persistent mispricings exist in real markets despite the presence of rational investors.
- Mathematical Formulation:
  ```
  deviation(t)       = (P(t) - F(t)) / F(t)
  cost_penalty       = max(0.2, 1 - short_cost_sensitivity x short_cost_rate x 10)
  effective_quantity = base_size x deviation(t) x cost_penalty
  max_quantity       = max_short_position - current_short_position
  Q*(t)              = -min(effective_quantity, max_quantity)   [short sell]
  ```
- Empirical Evidence: D'Avolio (2002) documents that average annual stock borrowing costs are 1.1% but can reach 30% for hard-to-borrow stocks; at these costs, many apparent arbitrage opportunities become unprofitable after fees. Lamont & Thaler (2003) show the 3Com/Palm arbitrage persisted 3+ months despite a clear mispricing, confirming that limits to arbitrage prevent rapid convergence.
- Relevance to This Investor: `short_cost_rate = 0.02` and `cost_penalty` formula implement the Shleifer-Vishny friction; `max_short_position = 30` enforces the capital constraint.

**Fundamental Analysis and Value Investing**:
- Theory / Study: Fundamental Analysis and Intrinsic Value
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. https://www.jstor.org/stable/1805228
- Core Insight: Prices can only be informationally efficient if enough informed agents trade on fundamentals. The Grossman-Stiglitz paradox establishes that rational, fundamentals-based agents must earn a return to compensate for their information costs, providing the economic rationale for why `RationalArbitrageur` actively compares price to fundamental and trades when deviation exceeds a threshold.
- Mathematical Formulation: `trade when |deviation(t)| > threshold`, where threshold compensates for the minimum transaction cost and analysis effort.
- Empirical Evidence: Fama & French (1992) find that value stocks (low P/B) outperform growth stocks by ~4.9% per year, consistent with the long-run profitability of fundamental-value strategies despite short-term limits to arbitrage.
- Relevance to This Investor: `deviation_threshold = 0.05` (5% deviation required before action) calibrates the minimum mispricing that justifies RationalArbitrageur entry, consistent with the Grossman-Stiglitz rational cost-benefit framework.

#### 4.2.3  Design Purpose and Activation Scenarios

Purpose: RationalArbitrageur provides the corrective force that prevents the bubble from growing without limit, models the real-world failure of arbitrage to eliminate speculative excess, and validates that the simulation's bubble formation requires both speculative demand AND insufficient arbitrage.

Activation Scenarios:
- Mild overvaluation (deviation > 0.05): Initiates small short positions; provides first line of correction but insufficient to stop bubble.
- Strong overvaluation (deviation > 0.15): Maximum short positions; provides strongest corrective force but still capped at 30 shares.
- Undervaluation (deviation < -0.05): Switches to buying; helps support prices during post-crash recovery.

Market Contribution: **Weakly Stabilising** -- provides meaningful but insufficient corrective pressure during the bubble. The cap at 30 short shares means even at deviation = 0.50, RationalArbitrageur cannot reverse the positive feedback loop created by multiple MomentumSpeculator and NoiseTrader agents.

Interaction with other agents: Directly counteracts MomentumSpeculator and NoiseTrader during bubble phase. Works in the same direction as FundamentalInvestor (both provide corrective force) but is faster-reacting and more aggressive in short sizing.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**

| Signal            | Type           | Rationale                                                                                                                                       |
|-------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| `price`           | Continuous     | Current market price; numerator of deviation calculation                                                                                        |
| `fundamental`     | Continuous     | Intrinsic value F(t); denominator of deviation calculation; agent has access because it performs fundamental analysis                           |
| `short_cost_rate` | Continuous     | Current borrowing cost; required for cost_penalty calculation; consistent with Shleifer-Vishny framing where arbitrageurs track their own costs |
| `short_position`  | State variable | Current short position held; required for position limit enforcement                                                                            |

Does NOT use: `price_history` for momentum, `net_demand`, or sentiment signals. RationalArbitrageur's world-view is entirely fundamental -- it cares only about the gap between price and intrinsic value.

**4.2.4.2  Core Behavioral Mechanism**

1. RationalArbitrageur computes the signed deviation of current price from fundamental value.
2. If deviation > 0.05 (price above fundamental by more than 5%): identifies overvaluation; computes the cost-adjusted short quantity; checks against remaining short capacity; places short sell order.
3. If deviation < -0.05 (price below fundamental by more than 5%): identifies undervaluation; buys to profit from mean reversion; capped at 30 shares.
4. The cost penalty reduces effective short size as borrowing costs rise -- when `short_cost_rate x short_cost_sensitivity` is high enough, the penalty reduces quantity by up to 80%.
5. Hard stop: never exceeds `max_short_position` total short; once at cap, holds regardless of further overvaluation.

**4.2.4.3  Mathematical Model**

- Decision variable: Short quantity Q*(t) (negative = short sell; positive = buy)
- Trigger function:
  ```
  Short: deviation(t) = (P(t) - F(t)) / F(t) > deviation_threshold (0.05)
  Buy:   deviation(t) < -deviation_threshold
  ```
- Sizing function:
  ```
  cost_penalty  = max(0.2, 1 - short_cost_sensitivity x short_cost_rate x 10)
  raw_short     = base_size x deviation(t) x cost_penalty
  remaining_cap = max_short_position - current_short_position
  Q*(t)         = -min(raw_short, remaining_cap)   [short sell]
  Q*(t)         = +min(abs(deviation) x base_size, 30)   [buy -- undervaluation]
  ```
- State variables: `short_position` -- total open short shares; persists across rounds
- Parameter definitions:

| Symbol                       | Meaning                                 | Config Path                       | Source                                                                                         |
|------------------------------|-----------------------------------------|-----------------------------------|------------------------------------------------------------------------------------------------|
| deviation_threshold = 0.05   | Minimum mispricing to justify arbitrage | players.yml -> RationalArbitrageur | Shleifer & Vishny (1997): 5-10% threshold typical before arbitrage entry                       |
| max_short_position = 30      | Hard cap on short shares                | players.yml -> RationalArbitrageur | Capital constraint; D'Avolio (2002): borrow capacity limits                                    |
| short_cost_sensitivity = 2.0 | Scales cost penalty                     | players.yml -> RationalArbitrageur | Shleifer & Vishny (1997): calibrated to produce ~40% effective size reduction at baseline cost |
| base_size = 20.0             | Base trade size                         | players.yml -> RationalArbitrageur | Standardised across agents                                                                     |

**4.2.4.4  Behavioral Properties**

- Time horizon: Medium-term -- waits for deviations to exceed 5% before acting; holds positions until mean reversion
- Risk tolerance: Medium -- bounded by explicit position limits; aware of and responds to borrowing costs
- Information asymmetry: Fundamental-analysis informed -- has access to F(t) (intrinsic value) which most momentum/noise agents ignore
- Psychological profile: Analytically rigorous, patient, frustrated by the irrationality of momentum traders but disciplined enough to stay within position limits. Embodies the Grossman-Stiglitz rational arbitrageur who is "right" about valuation but constrained by capital and timing.

#### 4.2.5  Decision Process Walkthrough

```
Given:  price = 145.0,  fundamental = 106.0,  short_cost_rate = 0.02
        short_position = 15 shares (already short),  max_short_position = 30

Step 1: Compute deviation
        deviation = (145.0 - 106.0) / 106.0 = 0.368

Step 2: Compare to threshold
        0.368 > 0.05 -> short condition satisfied

Step 3: Compute cost penalty
        cost_penalty = max(0.2, 1 - 2.0 x 0.02 x 10) = max(0.2, 1 - 0.4) = 0.6

Step 4: Compute raw short quantity
        raw_short = 20.0 x 0.368 x 0.6 = 4.42

Step 5: Check position cap
        remaining_cap = 30 - 15 = 15; min(4.42, 15) = 4.42 -> round to 4 shares

Step 6: Send order
        action = sell (short), quantity = 4, bid_price = 145.0

Result: Adds -4 to net demand D(t); contributes lambda x (-4) = -$0.60 downward pressure
        Total short position now = 19 shares (well within cap of 30)
```

#### 4.2.6  Worked Numerical Example

```
Market state:  price = 160.0,  fundamental = 108.0,  short_cost_rate = 0.02
               short_position = 25 shares,  max_short_position = 30

Calculation:
  deviation    = (160.0 - 108.0) / 108.0 = 0.481  (48.1% overvalued)
  cost_penalty = max(0.2, 1 - 2.0 x 0.02 x 10) = 0.6
  raw_short    = 20.0 x 0.481 x 0.6 = 5.77
  remaining    = 30 - 25 = 5
  Q*           = -min(5.77, 5) = -5 shares

Decision: action = sell (short), quantity = 5, bid_price = 160.0
New short position: 30 shares (at cap)

Rationale: Even at 48% overvaluation, RationalArbitrageur is now at the short cap.
It cannot add more corrective pressure. The bubble can continue to grow despite the arbitrageur
knowing prices are extreme -- this is the Shleifer-Vishny limits to arbitrage in action.
```

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                                                     | Notes                                                                    |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                        | Core theoretical foundation; calibrates cost_penalty and position limits |
| 2 | D'Avolio, G. (2002). The market for borrowing stock. *Journal of Financial Economics*, 66(2-3), 271-306. https://doi.org/10.1016/S0304-405X(02)00206-4                                       | Empirical calibration of short-selling costs (1-30% annually)            |
| 3 | Lamont, O. A., & Thaler, R. H. (2003). Can the market add and subtracttheta Mispricing in tech stock carve-outs. *Journal of Political Economy*, 111(2), 227-268. https://doi.org/10.1086/367683 | Empirical evidence that limits to arbitrage allow mispricings to persist |
| 4 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408.                                            | Grounds the economic rationale for fundamental-based trading             |

---

## Source Docstring Excerpts

### Rule / `RationalArbitrageur`

```text
Rational arbitrageur attempting to correct mispricings.
Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur

Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)
    - Arbitrageurs face constraints: short-selling costs, margin requirements
    - Cannot fully correct mispricings due to these limits
    - May be forced to close positions before prices correct
    -> simulation-bases.md Section 2.2

Behavior:
    - Estimates true value (fundamental)
    - Shorts when price > fundamental (but faces costs)
    - Buys when price < fundamental
    - Limited by capital and short-selling costs

Effect: WEAKLY STABILIZING - Cannot stop bubbles due to constraints

Formula:
    deviation = (price - fundamental) / fundamental
    If deviation > threshold: short (with cost penalty)
    If deviation < -threshold: buy
    -> simulation-bases.md Section 4.2 -- RationalArbitrageur (Rule-Based Behavior)

Parameters from config extras:
    - deviation_threshold, base_position_size, max_short_position, short_cost_sensitivity
    -> simulation-bases.md Section 6
```

### LLM / `LLMRationalArbitrageur`

```text
LLM fundamental analyst. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.
```

### RuleLLM / `RuleLLMRationalArbitrageur`

```text
Hybrid deviation rules with LLM reasoning. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.
```

### Rag / `RagLLMRationalArbitrageur`

```text
RAG-augmented deviation rules with retrieved knowledge. Theory: simulation-bases.md Section 4.2 -- RationalArbitrageur.
```
