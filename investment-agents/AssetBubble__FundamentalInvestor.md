# AssetBubble / Fundamental Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Fundamental Investor |
| Canonical class | `FundamentalInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

FundamentalInvestor represents the patient, value-oriented long-term investor who anchors decisions to intrinsic value and acts infrequently, modelling the discipline of institutional value managers (Graham, Buffett tradition). This agent is intentionally slow-reacting -- it trades only every 5 rounds -- which means it cannot prevent bubble formation in the short term but provides a persistent, low-frequency anchoring force. In the long run, FundamentalInvestor is the agent most likely to outperform if the simulation is run long enough for prices to revert to fundamental.

## Financial Theory / Theoretical Basis

### Rule / `FundamentalInvestor`
- Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor
- Theory: Traditional value investing
- Behavior:
- - Compares price to fundamental value
- - Buys undervalued, sells overvalued
- - Very patient, trades slowly
- - Provides weak anchoring force
- Effect: WEAKLY STABILIZING - Too slow to prevent bubbles
- Formula:
- -> simulation-bases.md Section 4.4 -- FundamentalInvestor (Rule-Based Behavior)

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `15.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| trade_frequency | Rule: `5` | Rule |
| value_sensitivity | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamental_investor | Fundamental Investor | `FundamentalInvestor` | 4 | `examples/AssetBubble/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 FundamentalInvestor

#### 4.4.1  Summary

FundamentalInvestor represents the patient, value-oriented long-term investor who anchors decisions to intrinsic value and acts infrequently, modelling the discipline of institutional value managers (Graham, Buffett tradition). This agent is intentionally slow-reacting -- it trades only every 5 rounds -- which means it cannot prevent bubble formation in the short term but provides a persistent, low-frequency anchoring force. In the long run, FundamentalInvestor is the agent most likely to outperform if the simulation is run long enough for prices to revert to fundamental.

#### 4.4.2  Theoretical and Empirical Foundation

**Value Investing and Fundamental Analysis**:
- Theory / Study: Value Investing and Mean Reversion
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. (The seminal exposition of intrinsic-value investing; establishes the principle that price must eventually revert to intrinsic value.)
- Core Insight: Every security has an intrinsic value determinable from its earnings capacity, assets, and future cash flows. When market price deviates substantially from intrinsic value (Graham's "margin of safety"), the rational investor buys or sells. The key discipline is patience -- the market may remain irrational longer than expected, but intrinsic value is the ultimate anchor.
- Mathematical Formulation: `trade_signal = (F(t) - P(t)) / P(t)` -- buy when price is below fundamental; sell when above.
- Empirical Evidence: Fama & French (1992) find that value stocks (low price-to-book, analogous to low P/F in this simulation) outperform growth stocks by 4.9% per year (1963-1990), confirming the long-run mean reversion that FundamentalInvestor exploits.
- Relevance to This Investor: FundamentalInvestor computes `deviation = (fundamental - price) / price` and sizes trades proportionally -- buying when undervalued, selling when overvalued. The `trade_frequency = 5` constraint implements the "patient" dimension of Graham's framework.

**Patience as Strategy -- Infrequent Trading**:
- Theory / Study: Cost of Overtrading and Benefits of Patience
- Citation: Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth: The common stock investment performance of individual investors. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226
- Core Insight: Individual investors who trade more frequently earn lower returns net of transaction costs (Barber & Odean find that the most active quintile of investors underperforms the market by 6.5% per year). Patient investors who trade infrequently outperform because they avoid noise-driven errors. This grounds FundamentalInvestor's `trade_frequency = 5` as a deliberate feature, not a limitation.
- Mathematical Formulation: Trading only when `round_number mod trade_frequency == 0` reduces the number of decisions from T to T/5, eliminating 80% of rounds where the investor might react to noise rather than signal.
- Empirical Evidence: Fama & French (1992) long-run value premium; Graham & Dodd (1934) case studies of patient value investors consistently outperforming active traders across economic cycles.
- Relevance to This Investor: `trade_frequency = 5` is the key distinguishing behavioural feature; it means FundamentalInvestor misses short-term opportunities but avoids noise-driven errors.

#### 4.4.3  Design Purpose and Activation Scenarios

Purpose: FundamentalInvestor provides the weak gravitational anchor that prevents the simulation from producing an ever-growing bubble with no corrective force. Together with RationalArbitrageur and gamma-term mean reversion, it ensures the simulation has a realistic mix of stabilising and destabilising forces.

Activation Scenarios:
- Every 5 rounds, unconditional: Computes deviation and places proportional order regardless of market conditions.
- Significant overvaluation (price >> fundamental): Places modest sell orders; provides very slow but persistent downward pressure.
- Post-crash undervaluation (price << fundamental): Places buy orders; helps stabilise prices during resolution phase.

Market Contribution: **Weakly Stabilising** -- too slow and too small to prevent bubble formation but provides a persistent, low-frequency corrective signal that contributes to eventual mean reversion.

Interaction with other agents: Works in the same direction as RationalArbitrageur (both sell when overvalued) but slower and smaller. Provides buying support during recovery when MomentumSpeculator and NoiseTrader may still be selling.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**

| Signal        | Type       | Rationale                                                                                    |
|---------------|------------|----------------------------------------------------------------------------------------------|
| `price`       | Continuous | Observed market price; denominator of deviation formula                                      |
| `fundamental` | Continuous | Intrinsic value F(t); FundamentalInvestor is defined by its access to and use of this signal |
| `round`       | Integer    | Required for frequency gate (act only every 5 rounds)                                        |

Does NOT use: `price_history`, `momentum`, `net_demand`, `short_cost_rate`. FundamentalInvestor's world-view is purely valuation-based; it ignores market dynamics signals entirely.

**4.4.4.2  Core Behavioral Mechanism**

1. Each round, FundamentalInvestor first checks the frequency gate: if `round mod trade_frequency ≠ 0`, it holds unconditionally.
2. On active rounds, it computes deviation = (fundamental - price) / price. Positive deviation means price is below fundamental (undervalued); negative deviation means price is above fundamental (overvalued).
3. Sizes trade proportionally: `quantity = value_sensitivity x deviation x base_position_size`.
4. Positive deviation (undervalued) -> buy; negative deviation (overvalued) -> sell.
5. Bounded at ±15 shares per trade, reflecting the investor's patience and conservative sizing.

**4.4.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t) (positive = buy, negative = sell)
- Trigger function:
  ```
  Active round: round_number mod trade_frequency == 0
  deviation(t) = (F(t) - P(t)) / P(t)
  ```
- Sizing function:
  ```
  Q*(t) = value_sensitivity x deviation(t) x base_position_size
  Bounds: Q*(t) ∈ [-15, +15]
  ```
- State variables: None; each active-round decision is independent
- Parameter definitions:

| Symbol                    | Meaning                 | Config Path                       | Source                                                                                |
|---------------------------|-------------------------|-----------------------------------|---------------------------------------------------------------------------------------|
| trade_frequency = 5       | Act every 5 rounds      | players.yml -> FundamentalInvestor | Barber & Odean (2000): patient investors outperform; 5-round = once-per-week analogue |
| value_sensitivity = 1.5   | Position scaling factor | players.yml -> FundamentalInvestor | Fama & French (1992): value tilt proportional to P/B gap; 1.5x moderate activist      |
| base_position_size = 20.0 | Reference lot           | players.yml -> FundamentalInvestor | Standardised                                                                          |

**4.4.4.4  Behavioral Properties**

- Time horizon: Long-term -- 5-round frequency gate means FundamentalInvestor is focused on multi-round value, not short-term price movements
- Risk tolerance: Low -- small maximum trade size (15 shares); no leverage; waits for clear deviation before acting
- Information asymmetry: Fundamental-analysis informed -- uses F(t) which most other agents ignore
- Psychological profile: Patient, disciplined (Graham & Dodd, 1934); immune to short-term noise; comfortable holding positions that may worsen before reversing; the "long-term is always right" mindset that occasionally leads to being early during bubbles

#### 4.4.5  Decision Process Walkthrough

```
Given:  round = 35 (active: 35 mod 5 == 0),  price = 148.0,  fundamental = 107.0
        base_position_size = 20.0,  value_sensitivity = 1.5

Step 1: Frequency gate check
        35 mod 5 == 0 -> active round, proceed

Step 2: Compute deviation
        deviation = (107.0 - 148.0) / 148.0 = -0.277  (price 27.7% above fundamental)

Step 3: Compute quantity
        Q_raw = 1.5 x (-0.277) x 20.0 = -8.31

Step 4: Apply bounds
        Q*(t) = max(-15, -8.31) = -8 shares

Step 5: Send order
        action = sell, quantity = 8, bid_price = 148.0

Result: Adds -8 to net demand; contributes lambda x (-8) = -$1.20 downward pressure
```

#### 4.4.6  Worked Numerical Example

```
Market state:  round = 85 (post-crash),  price = 82.0,  fundamental = 111.0

Calculation:
  deviation = (111.0 - 82.0) / 82.0 = 0.354  (price 35.4% below fundamental -- post-crash undervaluation)
  Q_raw     = 1.5 x 0.354 x 20.0 = 10.62 -> 10 shares (within ±15 bound)

Decision: action = buy, quantity = 10, bid_price = 82.0

Rationale: Post-crash undervaluation. FundamentalInvestor provides recovery-phase buying support,
consistent with the long-run mean reversion documented by Fama & French (1992).
While momentum traders have already sold, FundamentalInvestor steps in to absorb supply and push
prices back toward fundamental -- the "patient value investor buys the crash" pattern.
```

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                   | Notes                                                                                   |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                                           | Foundational intrinsic-value framework; establishes the buy/sell-on-deviation principle |
| 2 | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427-465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x | Empirical validation of value premium (4.9%/year); calibrates value_sensitivity         |
| 3 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226                      | Grounds trade_frequency = 5 as a deliberate patience strategy                           |

---

## Source Docstring Excerpts

### Rule / `FundamentalInvestor`

```text
Fundamental investor anchoring to intrinsic value.
Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor

Theory: Traditional value investing
    -> simulation-bases.md Section 2 (context: slow correction vs momentum forces)

Behavior:
    - Compares price to fundamental value
    - Buys undervalued, sells overvalued
    - Very patient, trades slowly
    - Provides weak anchoring force

Effect: WEAKLY STABILIZING - Too slow to prevent bubbles

Formula:
    deviation = (fundamental - price) / price
    quantity = value_sensitivity x deviation x base_position_size  (every N rounds)
    -> simulation-bases.md Section 4.4 -- FundamentalInvestor (Rule-Based Behavior)

Parameters from config extras:
    - trade_frequency, value_sensitivity, base_position_size
    -> simulation-bases.md Section 6
```
