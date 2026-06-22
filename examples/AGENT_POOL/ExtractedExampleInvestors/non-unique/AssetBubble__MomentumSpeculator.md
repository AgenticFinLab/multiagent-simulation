# AssetBubble / Momentum Speculator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Momentum Speculator |
| Canonical class | `MomentumSpeculator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, RuleLLM, Rag |

## Definition and Goal

MomentumSpeculator represents the archetypal "greater fool" speculative participant. This agent models the retail momentum investor or trend-following fund that ignores fundamental value entirely, buying when prices are rising because past price increases predict short-term future gains. MomentumSpeculator is the primary driver of bubble formation in this simulation -- its positive-feedback demand is what causes prices to diverge from fundamental value. It uses leverage to amplify both positions and losses, making it a significant contributor to the eventual crash when momentum reverses.

## Financial Theory / Theoretical Basis

### Rule / `MomentumSpeculator`
- Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator
- Theory: Greater Fool Theory
- Behavior:
- - Only looks at price momentum, ignores fundamentals
- - Extremely low risk aversion
- - Uses leverage (larger positions)
- - Buys aggressively when price is rising
- Effect: STRONGLY DESTABILIZING - Primary bubble driver
- Formula:
- -> simulation-bases.md Section 4.1 -- MomentumSpeculator (Rule-Based Behavior)

### RuleLLM / `RuleLLMMomentumSpeculator`
- Hybrid momentum rules with LLM reasoning. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.

### Rag / `RagLLMMomentumSpeculator`
- RAG-augmented momentum rules with retrieved knowledge. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| aggressiveness | Rule: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | Rag, Rule, RuleLLM |
| base_position_size | Rule: `50.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>RuleLLM: `3`<br>Rag: `3` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | Rag, Rule, RuleLLM |
| leverage_multiplier | Rule: `1.5`<br>RuleLLM: `2.0`<br>Rag: `2.0` | Rag, Rule, RuleLLM |
| llm | RuleLLM: `{'sys_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_MOMENTUM_SYS', 'user_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_MOMENTUM_SYS', 'user_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | Rag, RuleLLM |
| lookback_short | Rule: `3`<br>RuleLLM: `5`<br>Rag: `5` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentum_speculator | Momentum Speculator | `MomentumSpeculator` | 5 | `examples/AssetBubble/Rule/players.py` |
| RuleLLM | rulellm_momentum | RuleLLM Momentum Speculator | `RuleLLMMomentumSpeculator` | 5 | `examples/AssetBubble/RuleLLM/players.py` |
| Rag | ragllm_momentum | RAG Momentum Speculator | `RagLLMMomentumSpeculator` | 5 | `examples/AssetBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MomentumSpeculator

#### 4.1.1  Summary

MomentumSpeculator represents the archetypal "greater fool" speculative participant. This agent models the retail momentum investor or trend-following fund that ignores fundamental value entirely, buying when prices are rising because past price increases predict short-term future gains. MomentumSpeculator is the primary driver of bubble formation in this simulation -- its positive-feedback demand is what causes prices to diverge from fundamental value. It uses leverage to amplify both positions and losses, making it a significant contributor to the eventual crash when momentum reverses.

#### 4.1.2  Theoretical and Empirical Foundation

**Greater Fool / Momentum Theory**:
- Theory / Study: Greater Fool Theory; Momentum Premium in Equities
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks that have performed well over the past 3-12 months continue to outperform over the next 3-12 months, generating approximately 1% per month excess return. This momentum premium arises because investors underreact to information (slow updating) and positive feedback traders chase trends.
- Mathematical Formulation: `momentum(t) = (P(t) - MA_k(t)) / MA_k(t)` -- deviation of current price from its k-period moving average captures the trend signal.
- Empirical Evidence: Jegadeesh & Titman (1993) find a 12.01% annualised momentum return in US equities (1965-1989). Fama & French (1996) confirm momentum as an anomaly not explained by their three-factor model.
- Relevance to This Investor: MomentumSpeculator's `momentum = (price - MA5) / MA5` formula directly implements the short-horizon momentum signal; buy/sell thresholds (0.01, -0.02) calibrated to produce meaningful but not extreme demand shocks.

**Positive Feedback Trading**:
- Theory / Study: Noise Trader and Positive Feedback Trading
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x
- Core Insight: Positive feedback traders (who buy when prices rise) can destabilise markets when their aggregate demand is large enough relative to corrective arbitrage. Rational speculators may actually front-run positive feedback traders -- buying ahead of expected momentum demand and selling to them later -- which amplifies rather than dampens price movements.
- Mathematical Formulation: `D_feedback(t) = alpha x [P(t) - P(t-1)] / P(t-1)` -- demand proportional to last-period return, alpha > 0 implies positive feedback.
- Empirical Evidence: De Long et al. (1990b) document that momentum-driven demand amplifies price moves by a factor of 2-4x compared to the underlying fundamental change, consistent with MomentumSpeculator's `leverage_multiplier = 2.0` and `aggressiveness = 2.0` (combined 4x amplification).
- Relevance to This Investor: The `aggressiveness x momentum x base_position_size x leverage_multiplier` sizing formula directly implements positive feedback demand proportional to momentum magnitude.

#### 4.1.3  Design Purpose and Activation Scenarios

Purpose: MomentumSpeculator generates the positive feedback loop that is the core mechanism of bubble formation. Without this agent, prices would hover near fundamental value since other agents are either corrective (RationalArbitrageur, FundamentalInvestor) or noise-driven without strong trend-following (NoiseTrader).

Activation Scenarios:
- Early bubble (momentum > 0.01): Begins buying, producing positive net demand D(t) > 0, which pushes prices higher, which increases momentum further -- the positive feedback loop.
- Bubble escalation (momentum > 0.05): Large positions (50-100 shares) amplify price moves; leverage_multiplier doubles effective demand.
- Momentum reversal (momentum < -0.02): Panic-sells, contributing to crash onset; panic selling accelerates the downward momentum.

Market Contribution: **Strongly Destabilising** -- MomentumSpeculator's buying pushes prices above fundamental, while its eventual panic selling amplifies the crash. The leverage multiplier means its effective market impact is 4x larger than a passive investor of the same base size.

Interaction with other agents: MomentumSpeculator's buying is directly counteracted by RationalArbitrageur (who shorts as deviation grows). However, because MomentumSpeculator's demand grows with momentum while RationalArbitrageur's corrective capacity is capped at `max_short_position = 30`, MomentumSpeculator dominates during the bubble phase.

#### 4.1.4  Behavioral Framework

This section defines MomentumSpeculator's decision logic at the archetype level -- independent of any specific variant implementation. It describes WHAT the investor does and WHY, not HOW any particular variant encodes it.

**4.1.4.1  Decision Information Set**

| Signal                          | Type       | Rationale                                                                              |
|---------------------------------|------------|----------------------------------------------------------------------------------------|
| `price`                         | Continuous | Current market price; numerator of momentum formula                                    |
| `price_history` (last k rounds) | Series     | Required to compute MA_k moving average; embodiment of backward-looking momentum logic |

Does NOT use: `fundamental`, `bubble_ratio`, `short_cost_rate`. These would require fundamentals-based reasoning inconsistent with pure greater-fool motivation. MomentumSpeculator's information set is deliberately restricted to price history -- consistent with the Keynes beauty contest framing where the agent focuses on what others will pay next, not what the asset is worth.

**4.1.4.2  Core Behavioral Mechanism**

1. MomentumSpeculator observes the current price and maintains a rolling price history (k = 5 rounds).
2. It computes momentum as the percentage deviation of current price from its 5-period moving average. A positive momentum value signals that the market is trending upward above recent averages.
3. If momentum > buy_threshold (0.01): the trend is confirmed as upward. The agent sizes a buy order proportional to momentum magnitude, amplified by aggressiveness and leverage_multiplier. Larger momentum -> larger position, reflecting the greater-fool expectation that the trend will persist and attract more buyers.
4. If momentum < sell_threshold (-0.02): the trend has reversed. The agent sells proportionally to momentum magnitude -- a panic response to preserve capital. The sell threshold is set larger in magnitude than the buy threshold, reflecting asymmetric psychological response (fear stronger than greed for reversals).
5. If momentum is between the two thresholds: the agent holds, consistent with "no clear signal" behaviour.
6. Action is bounded: maximum buy = 100 shares (capital constraint); minimum sell = -80 shares (position limit).

**4.1.4.3  Mathematical Model**

- Decision variable: Buy/sell quantity Q*(t)
- Trigger functions:
  ```
  momentum(t) = (P(t) - MA_5(t)) / MA_5(t)
  Buy  condition: momentum(t) > 0.01
  Sell condition: momentum(t) < -0.02
  ```
- Sizing function:
  ```
  Q*(t) = aggressiveness x momentum(t) x base_position_size x leverage_multiplier   [buy]
  Q*(t) = aggressiveness x momentum(t) x base_position_size                           [sell]
  Bounds: Q*(t) ∈ [-80, +100]
  ```
- State variables: `price_history` -- rolling window of last 5 prices; updated each round
- Parameter definitions:

| Symbol                    | Meaning                           | Config Path                      | Source                                                                     |
|---------------------------|-----------------------------------|----------------------------------|----------------------------------------------------------------------------|
| aggressiveness = 2.0      | Position scaling factor           | players.yml -> MomentumSpeculator | De Long et al. (1990b): typical momentum demand is 2-4x fundamental demand |
| leverage_multiplier = 2.0 | Additional leverage on buy orders | players.yml -> MomentumSpeculator | Adrian & Shin (2010): typical retail margin leverage 2-3x                  |
| base_position_size = 20.0 | Reference lot size (shares)       | players.yml -> MomentumSpeculator | Standardised across all agent types                                        |
| MA window k = 5           | Lookback for moving average       | players.yml (lookback_short)     | Jegadeesh & Titman (1993): 5-period window captures short-horizon momentum |

**4.1.4.4  Behavioral Properties**

- Time horizon: Very short-term -- 5-round moving average horizon; cares only about short-term price trends
- Risk tolerance: Extreme -- uses leverage; does not limit position by fundamental valuation; no stop-loss logic
- Information asymmetry: No unique information; purely reactive to public price history
- Psychological profile: FOMO (Fear of Missing Out) bias -- buys aggressively when trend confirms; loss aversion asymmetry -- sell threshold magnitude (0.02) > buy threshold (0.01), reflecting stronger panic response to downtrends than greed response to uptrends (Kahneman & Tversky, 1979)

#### 4.1.5  Decision Process Walkthrough

```
Given:  price = 125.0,  MA_5 = 120.0,  base_position_size = 20,  aggressiveness = 2.0,  leverage_multiplier = 2.0

Step 1: Compute momentum
        momentum = (125.0 - 120.0) / 120.0 = 0.0417

Step 2: Compare to buy threshold
        0.0417 > 0.01 -> buy condition satisfied

Step 3: Compute raw quantity
        Q_raw = 2.0 x 0.0417 x 20.0 x 2.0 = 3.33

Step 4: Apply bounds
        Q*(t) = min(max(3.33, 0), 100) = 3.33 -> rounds to 3 shares

Step 5: Send order
        action = buy, quantity = 3, bid_price = 125.0

Result: Adds +3 to net demand D(t); contributes lambda x 3 = 0.15 x 3 = +$0.45 to price increase
```

#### 4.1.6  Worked Numerical Example

```
Market state:  price = 140.0,  MA_5 = 128.0,  fundamental = 105.0
               cash = 8,000,  position = 45 shares

Calculation:
  momentum     = (140.0 - 128.0) / 128.0 = 0.0938
  Q_raw        = 2.0 x 0.0938 x 20.0 x 2.0 = 7.50 -> 7 shares
  buy condition confirmed (0.0938 > 0.01)

Decision: action = buy, quantity = 7, bid_price = 140.0
Cash cost: 7 x 140.0 = $980; cash remaining = $7,020

Rationale: Price is 9.4% above its 5-period average, signalling a strong upward trend.
MomentumSpeculator buys aggressively, contributing to the positive feedback loop even though
the asset is already 33% above fundamental value -- a pure "greater fool" decision.
```

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                                                                                          | Notes                                                                           |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                                                          | Establishes momentum premium; calibrates MA window and momentum magnitude       |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990b). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x | Establishes positive feedback demand model; calibrates aggressiveness parameter |
| 3 | Keynes, J. M. (1936). *The General Theory of Employment, Interest and Money*. Macmillan. Ch. 12.                                                                                                                                                  | Foundational "beauty contest" / greater fool framing                            |
| 4 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185                                                                                          | Grounds asymmetric buy/sell thresholds in loss-aversion psychology              |

---

## Source Docstring Excerpts

### Rule / `MomentumSpeculator`

```text
Momentum speculator that drives bubble formation.
Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator

Theory: Greater Fool Theory
    Buy even if overvalued, expecting to sell to a "greater fool."
    -> simulation-bases.md Section 2.1

Behavior:
    - Only looks at price momentum, ignores fundamentals
    - Extremely low risk aversion
    - Uses leverage (larger positions)
    - Buys aggressively when price is rising

Effect: STRONGLY DESTABILIZING - Primary bubble driver

Formula:
    momentum = (price - MA_short) / MA_short
    quantity = aggressiveness x momentum x base_size
    -> simulation-bases.md Section 4.1 -- MomentumSpeculator (Rule-Based Behavior)

Parameters from config extras:
    - lookback_short, aggressiveness, base_position_size, leverage_multiplier
    -> simulation-bases.md Section 6
```

### RuleLLM / `RuleLLMMomentumSpeculator`

```text
Hybrid momentum rules with LLM reasoning. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
```

### Rag / `RagLLMMomentumSpeculator`

```text
RAG-augmented momentum rules with retrieved knowledge. Theory: simulation-bases.md Section 4.1 -- MomentumSpeculator.
```
