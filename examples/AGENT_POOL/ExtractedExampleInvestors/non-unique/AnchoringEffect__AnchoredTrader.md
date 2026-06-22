# AnchoringEffect / Anchored Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Anchored Trader |
| Canonical class | `AnchoredTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

AnchoredTrader represents the archetypal retail investor or buy-side analyst who anchors strongly to the first price they observed and adjusts toward fundamental value by only a fraction of the necessary amount. This agent directly models the Tversky-Kahneman anchoring-and-adjustment heuristic: it knows the fundamental value but cannot bring itself to use it fully, believing its biased "perceived target" to be the true fair value. AnchoredTrader is the primary driver of persistent mispricing in the simulation -- its refusal to trade at the true fundamental price is what keeps prices elevated above F for extended periods.

## Financial Theory / Theoretical Basis

### Rule / `AnchoredTrader`
- Theoretical basis: simulation-bases.md Section 2.1 (Tversky & Kahneman, 1974).
- Decision rule (simulation-bases.md Section 4.1 -- Rule-Based Behavior):

### LLM / `LLMAnchoredTrader`
- LLM-driven anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.

### RuleLLM / `RuleLLMAnchoredTrader`
- RuleLLM anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.

### Rag / `RagLLMAnchoredTrader`
- RAG-augmented anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| adjustment_factor | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| base_position_size | Rule: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AnchoringEffect.LLM.prompts:LLM_ANCHORED_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_ANCHORED_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AnchoringEffect.Rag.prompts:RAG_ANCHORED_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_threshold | Rag: `0.03` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | anchored_trader | Anchored Trader | `AnchoredTrader` | 2 | `examples/AnchoringEffect/Rule/players.py` |
| LLM | anchored_trader | Anchored Trader | `LLMAnchoredTrader` | 2 | `examples/AnchoringEffect/LLM/players.py` |
| RuleLLM | rulellm_anchored | RuleLLM Anchored Trader | `RuleLLMAnchoredTrader` | 2 | `examples/AnchoringEffect/RuleLLM/players.py` |
| Rag | ragllm_anchored | RAG Anchored Trader | `RagLLMAnchoredTrader` | 2 | `examples/AnchoringEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 AnchoredTrader

#### 4.1.1  Summary

AnchoredTrader represents the archetypal retail investor or buy-side analyst who anchors strongly to the first price they observed and adjusts toward fundamental value by only a fraction of the necessary amount. This agent directly models the Tversky-Kahneman anchoring-and-adjustment heuristic: it knows the fundamental value but cannot bring itself to use it fully, believing its biased "perceived target" to be the true fair value. AnchoredTrader is the primary driver of persistent mispricing in the simulation -- its refusal to trade at the true fundamental price is what keeps prices elevated above F for extended periods.

#### 4.1.2  Theoretical and Empirical Foundation

**Anchoring and Insufficient Adjustment**:
- Theory / Study: Anchoring Heuristic in Numerical Estimation
- Citation: Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124
- Core Insight: Estimates insufficiently adjust from initial anchor values even when the anchor is arbitrary. The resulting bias toward the anchor is systematic and persistent, not reducible with expertise or incentives.
- Mathematical Formulation: `perceived_target = anchor + (F - anchor) x alpha`, where alpha = 0.3 from experimental calibration.
- Empirical Evidence: Tversky & Kahneman (1974) median estimates in the "spin the wheel" experiment shifted 10-15% toward the anchor value; Chapman & Johnson (1999, *Organizational Behavior and Human Decision Processes*) confirm alpha ≈ 0.25-0.40 across diverse estimation tasks.
- Relevance to This Investor: With anchor = 105.0 and F = 100.0, `perceived_target = 105.0 + (100.0 - 105.0) x 0.3 = 103.5`. AnchoredTrader treats 103.5 as "fair value" rather than the true 100.0, causing it to buy too aggressively at prices near 103-104 and sell too cautiously.

**Anchoring in Financial Forecast Revisions**:
- Theory / Study: Consensus Forecast Anchoring
- Citation: Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127
- Core Insight: Professional forecasters revise their estimates by only 30-70% of what the new information implies. The under-revision is directly proportional to the distance from the prior anchor, and it is persistent across many revision cycles.
- Mathematical Formulation: `revision = theta x (new_info - prior_forecast)`, where theta ≈ 0.3-0.5 empirically.
- Empirical Evidence: Campbell & Sharpe (2009) document mean forecast error autocorrelation r ≈ 0.4 in Bloomberg consensus data (1992-2006), confirming that under-revision is predictable and persistent -- not random.
- Relevance to This Investor: `adjustment_factor = 0.3` calibrated directly from Campbell & Sharpe's theta estimates; the persistent mispricing in the simulation replicates the predictable forecast errors they document.

#### 4.1.3  Design Purpose and Activation Scenarios

Purpose: AnchoredTrader generates the persistent price stickiness that is the core phenomenon. It buys when price dips below its biased perceived target (103.5), providing upward price support that prevents the market from efficiently correcting to fundamental (100.0).

Activation Scenarios:
- Price below perceived target by > 3% (price < 100.4): Buys; interprets as undervaluation relative to biased reference; provides upward price support.
- Price above perceived target by > 3% (price > 106.6): Sells; interprets as overvaluation; provides downward correction relative to biased reference.
- Price within ±3% of perceived target: Holds; consistent with the "close enough" behaviour documented when deviations are near threshold.

Market Contribution: **Destabilising** -- sustains mispricings by refusing to correct to the true fundamental. When F = 100 and anchor = 105, AnchoredTrader's buying support keeps prices elevated above fundamental, preventing efficient price discovery.

Interaction with other agents: Directly opposes RationalUpdater (who tries to correct deviation); is reinforced by MomentumTrader (who amplifies the upward drift); partially overlaps with HistoricalAnchor (both resist correction, but from different anchors).

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**

| Signal         | Type             | Rationale                                                                                                          |
|----------------|------------------|--------------------------------------------------------------------------------------------------------------------|
| `price`        | Continuous       | Current market price; compared to perceived_target                                                                 |
| `fundamental`  | Continuous       | True F; used in perceived_target calculation with alpha < 1; agent knows F but does not act on it directly             |
| Anchor (state) | Persistent state | Set once on first round to initial_price = 105.0; never updated; embodies the "first observation" anchoring effect |

Does NOT use: `prev_price`, `momentum`, `net_demand`. AnchoredTrader makes decisions based on its biased valuation estimate, not market dynamics signals.

**4.1.4.2  Core Behavioral Mechanism**

1. On first round: records `anchor = initial_price = 105.0` (the first price observed).
2. Each round: computes `perceived_target = anchor + (fundamental - anchor) x adjustment_factor` = 105.0 + (100.0 - 105.0) x 0.3 = 103.5.
3. Computes `perceived_dev = (price - perceived_target) / perceived_target`.
4. If `perceived_dev < -0.03` (price more than 3% below perceived target): buys -- it looks cheap from the biased perspective.
5. If `perceived_dev > +0.03` (price more than 3% above perceived target): sells -- it looks expensive.
6. Sizes trade proportionally to perceived deviation magnitude, bounded at base_position_size.
7. Note: AnchoredTrader will never aggressively correct price to F = 100 because its perceived target is already at 103.5, not 100.0.

**4.1.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  perceived_target = anchor + (F - anchor) x adjustment_factor   [computed once; anchor = 105.0 fixed]
  perceived_dev(t) = (P(t) - perceived_target) / perceived_target
  Buy:  perceived_dev(t) < -0.03
  Sell: perceived_dev(t) > +0.03
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(perceived_dev(t)) x 1000)
  Constrained by cash (buy) or position (sell)
  ```
- State variables: `anchor` -- set once on first round to initial_price; never updated
- Parameter definitions:

| Symbol                    | Meaning                                               | Config Path                  | Source                                                      |
|---------------------------|-------------------------------------------------------|------------------------------|-------------------------------------------------------------|
| adjustment_factor = 0.3   | Fraction of gap to anchor that agent adjusts toward F | players.yml -> AnchoredTrader | Tversky & Kahneman (1974): alpha ≈ 0.3 from experimental data   |
| base_position_size = 20.0 | Maximum trade size                                    | players.yml -> AnchoredTrader | Standardised across agents                                  |
| threshold = 0.03          | Minimum perceived deviation before trading            | players.yml -> AnchoredTrader | Consistent with 3% "noise band" in Campbell & Sharpe (2009) |

**4.1.4.4  Behavioral Properties**

- Time horizon: Medium-term -- adjusts slowly; anchor is permanent (set once and never updated)
- Risk tolerance: Medium -- trades only when perceived deviation exceeds 3%; positions bounded at 20 shares
- Information asymmetry: None -- has access to true F but cognitively discounts it through alpha < 1 adjustment
- Psychological profile: Anchoring bias (Tversky & Kahneman, 1974); conservatism bias (Barberis, Shleifer, & Vishny, 1998 -- investors underreact to new information); the "reference point" psychology of Kahneman & Tversky (1979) Prospect Theory

#### 4.1.5  Decision Process Walkthrough

```
Given:  price = 101.5,  fundamental = 100.0,  anchor = 105.0 (set on round 1)
        adjustment_factor = 0.3,  base_position_size = 20.0

Step 1: Compute perceived_target
        perceived_target = 105.0 + (100.0 - 105.0) x 0.3 = 105.0 - 1.5 = 103.5

Step 2: Compute perceived deviation
        perceived_dev = (101.5 - 103.5) / 103.5 = -0.0193

Step 3: Compare to threshold
        |-0.0193| < 0.03 -> below threshold; HOLD

Result: Despite price being 1.5% above true fundamental, AnchoredTrader holds
        because relative to its biased perceived target (103.5), the price looks
        only 1.9% undervalued -- below its 3% action threshold.
        This illustrates how anchoring sustains mispricings.
```

#### 4.1.6  Worked Numerical Example

```
Market state:  price = 98.0,  fundamental = 100.0,  anchor = 105.0 (permanent)

Calculation:
  perceived_target = 105.0 + (100.0 - 105.0) x 0.3 = 103.5
  perceived_dev    = (98.0 - 103.5) / 103.5 = -0.0531   (price 5.3% below biased target)
  -0.0531 < -0.03 -> buy condition satisfied
  Q* = min(20.0, 0.0531 x 1000) = min(20.0, 53.1) = 20 shares (capped at base_position_size)

Decision: action = buy, quantity = 20, bid_price = 98.0

Rationale: Price at 98 is actually 2% BELOW true fundamental (100), so a rational agent would hold or sell.
But AnchoredTrader perceives it as 5.3% below its biased target (103.5) and buys aggressively.
This buying creates upward price pressure at levels that rational agents would not support,
directly producing and maintaining the anchoring-driven mispricing.
```

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                        | Notes                                                                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 1 | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124           | Core theoretical foundation; calibrates alpha = 0.3                                             |
| 2 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts. *JFQA*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127                               | Financial market application; calibrates MAD target [3%, 10%] and half-life [20, 60 rounds] |
| 3 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185                        | Grounds reference-point psychology underlying anchor as subjective "fair value"             |
| 4 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Connects anchoring to conservatism bias and underreaction in financial markets              |

---

## Source Docstring Excerpts

### Rule / `AnchoredTrader`

```text
Anchors to initial price, adjusts insufficiently toward fundamental.

Implements simulation-bases.md Section 4.1 -- AnchoredTrader.
Theoretical basis: simulation-bases.md Section 2.1 (Tversky & Kahneman, 1974).

Decision rule (simulation-bases.md Section 4.1 -- Rule-Based Behavior):
    anchor_price = first market price observed (set on first perceive call)
    perceived_target = anchor_price + (fundamental - anchor_price) * adjustment_factor
    perceived_dev = (price - perceived_target) / perceived_target
    if abs(perceived_dev) > 0.03: trade in corrective direction
    quantity = min(base_position_size, abs(perceived_dev) * 1000)

Parameters (simulation-bases.md Section 6):
    adjustment_factor: 0.3 (calibrated from Tversky & Kahneman 1974 experimental data)
    base_position_size: loaded from extras["base_position_size"]
```

### LLM / `LLMAnchoredTrader`

```text
LLM-driven anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.
```

### RuleLLM / `RuleLLMAnchoredTrader`

```text
RuleLLM anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.
```

### Rag / `RagLLMAnchoredTrader`

```text
RAG-augmented anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.
```
