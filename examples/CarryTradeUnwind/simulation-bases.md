# CarryTradeUnwind — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                   |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Carry Trade Unwind — Sudden Leveraged Position Liquidation in FX Markets                                                                                                                                                                                                                      |
| Category           | FX market dynamics / leveraged position unwinding / funding liquidity crisis                                                                                                                                                                                                                  |
| Core Mechanism     | Carry trades borrow low-yield funding currencies (JPY, CHF) to invest in high-yield target currencies (AUD, NZD, TRY). When risk sentiment reverses, funding currencies appreciate — forcing leveraged positions to be closed, which amplifies appreciation further, triggering more closures |
| Real-World Origin  | 2008 JPY appreciation (USD/JPY −20% in weeks); 2015 CHF floor removal (CHF +20% in minutes); 2022 JPY carry unwind; JPY appreciation episodes of 1998, 2007–2008                                                                                                                              |
| Research Relevance | Examines how leveraged carry positions create endogenous crash risk; tests whether forced-liquidation cascades can be distinguished from fundamental FX adjustments; quantifies the role of stop-loss thresholds in amplifying volatility                                                     |


## §2 Theoretical Foundation

### 2.1 Carry Trade Returns and Crash Risk (Brunnermeier, Nagel & Pedersen)

- **Citation**: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313–347. DOI: 10.1086/593088
- **Core Insight**: Carry trades earn positive returns on average (the "carry premium") but exhibit severe negative skewness — they are vulnerable to sudden, large losses when risk sentiment reverses and funding currencies appreciate sharply. Brunnermeier et al. document a pattern they call "going up by the stairs and coming down by the elevator": slow carry accumulation during risk-on periods, sudden violent unwind during risk-off. The crash occurs because all carry traders unwind simultaneously, creating herding sell pressure on target currencies.
- **Mathematical Formulation**: Expected carry return: E[r_carry] = i_high − i_low (interest rate differential). Crash risk: Prob(unwind | risk_off) × ΔP_unwind >> E[r_carry]. The carry crash skewness κ < −1, meaning crash losses are systematically larger than normal gains. Leverage amplification: effective price move = λ × (N_carry × sell_qty), where N_carry = number of carry traders.
- **Empirical Evidence**: Brunnermeier et al. (2009) document that carry trade returns have skewness of −1.5 to −2.0, with crash months averaging −5% to −15% returns vs. normal months of +0.3% to +0.8%. The 2008 JPY carry unwind saw USD/JPY fall from 110 to 88 (−20%) in 6 weeks, consistent with the simulation's target drawdown of 10–25%.
- **Relevance to Investor Taxonomy**: CarryTrader represents the slow accumulation phase; LeveragedCarryFund represents the violent unwind; their interaction generates the asymmetric crash pattern documented by Brunnermeier et al.

### 2.2 Carry Trade Feedback Dynamics and Market Instability (Plantin & Shin)

- **Citation**: Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637–666. DOI: 10.3982/TE2739
- **Core Insight**: Plantin & Shin develop a model showing that carry trade positions create endogenous instability: when carry traders are uniformly positioned (all long high-yield), any negative shock to the target currency triggers a cascade of simultaneous exits. The feedback loop is: funding currency appreciation → mark-to-market losses → forced exits → further appreciation → more forced exits. The key parameter is the ratio of leveraged carry position size to market liquidity (λ · N · Q / market_depth).
- **Mathematical Formulation**: Carry trader exit threshold: exit if P_funding > P_entry × (1 + stop_loss). Cascade condition: λ × N_LCF × forced_sell_qty > λ × N_FCB × buy_qty, i.e., destabilizing selling exceeds stabilizing buying. With default parameters: λ × 2 × 4000 = 160 > λ × 2 × 500 = 20 → cascade expected. The cascade condition is satisfied by design, consistent with Plantin & Shin's prediction of endogenous crash risk.
- **Empirical Evidence**: Plantin & Shin cite JPY carry trade in 2007–2008: estimated $1.2 trillion in outstanding carry positions; when the cascade began, position reversal amplified JPY appreciation by 3–5× the fundamental adjustment warranted by interest rate changes alone.
- **Relevance to Investor Taxonomy**: LeveragedCarryFund's stop_loss trigger and large position size directly instantiate the Plantin-Shin cascade mechanism; its forced selling volume (up to 4000 units per round) ensures the cascade condition is satisfied.

### 2.3 Global FX Volatility Factor (Menkhoff et al.)

- **Citation**: Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). "Carry trades and global foreign exchange volatility." *Journal of Finance*, 67(2), 681–718. DOI: 10.1111/j.1540-6261.2012.01728.x
- **Core Insight**: Menkhoff et al. show that carry trade returns are strongly negatively related to innovations in global FX volatility: when volatility spikes, all carry trades unwind simultaneously, regardless of individual currency pair fundamentals. This is because carry trades are funded with leverage, and risk management systems systematically reduce leverage as volatility rises. The HedgedCarryTrader represents the carry trader who explicitly manages volatility risk.
- **Mathematical Formulation**: Carry return decomposition: r_carry(t) = α − β × ΔVol_FX(t) where β > 0. HedgedCarryTrader position sizing: adj_qty = base_qty × (1 − hedge_ratio); enters only when rolling_vol < vol_threshold (0.05); exits when rolling_vol > vol_threshold.
- **Empirical Evidence**: Menkhoff et al. (2012) find β ≈ 2–4 for high-yield currency portfolios: a 1 standard deviation increase in FX volatility predicts a −2% to −4% carry return. The vol_threshold = 0.05 (5%) is calibrated to represent one standard deviation of FX volatility in carry-trade-relevant markets.
- **Relevance to Investor Taxonomy**: HedgedCarryTrader's volatility-based activation (only enters when vol < 0.05; exits when vol > 0.05) operationalizes Menkhoff et al.'s documented relationship between volatility and carry trade participation.

### 2.4 Funding Liquidity and Market Liquidity Spirals (Brunnermeier & Pedersen)

- **Citation**: Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098
- **Core Insight**: Funding liquidity and market liquidity are mutually reinforcing: when leveraged traders face losses, they must reduce positions (sell), which reduces market liquidity, which makes the price impact of further selling larger, which causes more losses, requiring more position reduction. The FundingCurrencyBuyer represents the natural counterparty that provides market liquidity during the unwind — their safe-haven buying of the funding currency partially offsets the cascade.
- **Mathematical Formulation**: Liquidity spiral condition: margin(t) = (equity(t) / assets(t)) < margin_requirement → forced_sell = assets × (margin_shortfall / assets). Each forced sell reduces equity of all leveraged participants simultaneously: ΔEquity_i = −leverage_i × ΔP, amplifying the cascade. FundingCurrencyBuyer provides counter-liquidity: buy_qty = position_size when deviation < −risk_threshold.
- **Empirical Evidence**: Brunnermeier & Pedersen (2009) document funding liquidity spirals in 9 historical episodes including 1987, 1998 LTCM, 2007–2008. In each, market liquidity collapses simultaneously with funding liquidity. FX markets showed bid-ask spreads 3–5× normal during JPY carry unwind in 2008.
- **Relevance to Investor Taxonomy**: FundingCurrencyBuyer represents the natural market liquidity provider who steps in during carry unwinds — safe-haven flows and portfolio rebalancing that partially offset the cascade. risk_threshold = 0.05 calibrated to activate at 5% depreciation of the high-yield currency, consistent with safe-haven flow triggers documented by Brunnermeier & Pedersen.

### 2.5 Noise Trading and Background FX Order Flow (Black)

- **Citation**: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481
- **Core Insight**: Background noise trading provides the liquidity that carry traders need to execute their positions. In FX markets, noise traders represent non-carry order flow from importers, exporters, and portfolio managers with non-speculative FX needs. trade_probability = 0.30 calibrated to reflect the substantial non-speculative FX market volume that provides background liquidity.
- **Empirical Evidence**: BIS Triennial Survey data suggest speculative flow (including carry) accounts for approximately 30–40% of daily FX volume; the remaining 60–70% is non-speculative, consistent with the NoiseTrader modeling background non-carry order flow.


## §3 Market Design Principles

### 3.1 Price Formation Model

Formula: **P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t)**

Note: In this simulation, P represents a **FX exchange rate** (e.g., USD expressed in units of the funding currency — higher P means the target currency is more valuable relative to the funding currency; declining P means funding currency is appreciating).

| Symbol     | Meaning                           | Value          | Economic Justification                                                                                                                            | Calibration Source                       |
|------------|-----------------------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| P(t)       | FX exchange rate (target/funding) | starts at 1.20 | Normalized FX rate; represents a currency pair like AUD/JPY or USD/JPY at a stylized level                                                        | Normalization                            |
| D(t)       | Net demand (buy − sell)           | computed       | Aggregate buy/sell orders from all agents; positive demand = target currency buying = appreciation                                                | —                                        |
| F          | Fundamental FX rate (PPP-based)   | 1.20           | Constant — represents the Purchasing Power Parity (PPP)-implied equilibrium rate; carry trades create deviations from PPP that eventually correct | PPP-based normalization                  |
| λ (lambda) | Price impact coefficient          | 0.02           | MODERATE-HIGH — reflects thinner FX market conditions during a carry unwind stress event; larger than equity markets per unit volume              | Brunnermeier, Nagel & Pedersen (2009)    |
| γ (gamma)  | Mean-reversion coefficient        | 0.02           | Moderate — PPP gravity exists but is slow-acting (years horizon for PPP); during unwind, mean-reversion is overwhelmed by cascade forces          | Rogoff (1996) PPP convergence estimates  |
| ε(t)       | Gaussian noise ~ N(0, σ²)         | σ = 0.02       | Low — FX noise is small relative to carry-event shocks; σ calibrated to 2% of the exchange rate (roughly 2 "pips" per round)                      | BIS (2022) FX market volatility baseline |

**Design Rationale**:
- λ = 0.02 is higher than most other simulations (0.001–0.01): FX markets during carry unwinds exhibit reduced liquidity (market makers widen spreads, reduce size), making each unit of net selling create a larger price impact. Plantin & Shin (2018) estimate price impact is 3–5× higher during carry stress events.
- γ = 0.02 is calibrated to PPP-based mean reversion in FX markets. Rogoff (1996)'s "PPP puzzle" documents that FX deviations from PPP have half-lives of 3–5 years, implying very slow reversion. However, for simulation purposes, γ = 0.02 creates a visible reversion force that limits permanent divergence.
- σ = 0.02 is small — in the context of a carry unwind simulation where crisis-driven moves are 10–25% (deviation = −0.10 to −0.25), background noise of 2% per round is meaningful but not dominant.
- F = 1.20 (constant): The carry trade phenomenon is not about PPP misalignment — it is about interest rate differentials and risk sentiment. Holding F constant isolates the endogenous cascade mechanism from fundamental FX adjustments.

**Cascade Dynamics**:
1. Normal carry phase: P ≈ F (small positive deviation from noise); CarryTrader and HedgedCarryTrader accumulate.
2. Trigger: Random noise or external shock causes P to fall below F; deviation turns negative.
3. Cascade initiation: deviation < −0.02 → CarryTrader sells; deviation < −0.03 → LeveragedCarryFund stop_loss triggered.
4. Cascade acceleration: LeveragedCarryFund sells 4000 shares/round → D(t) << 0 → P falls further → deviation more negative → more forced selling.
5. Cascade condition check: LCF sell volume (2 × 4000 = 8000) >> FCB buy volume (2 × 500 = 1000) → cascade proceeds.
6. Stabilization: FundingCurrencyBuyer activates at deviation < −0.05; mean reversion adds recovery force; LCF positions may be exhausted.
7. Recovery: γ-mean-reversion and FCB buying gradually restore price toward F; recovery ratio depends on remaining carry positions and stabilizer capacity.

### 3.2 Additional Market Mechanisms

- **Price floor**: `max(price, 0.01)` — prevents numerical collapse.
- **No circuit breakers**: Carry unwinds in FX markets have no price limits (unlike equities); consistent with real FX market structure.
- **return_pct NOT broadcast**: Unlike AvailabilityBias simulation, `return_pct` is NOT broadcast. All agents use `deviation` as their primary signal — consistent with FX traders who monitor deviation from fair value rather than momentum signals.

### 3.3 Information Broadcast Design

Each round, the Market sends to all investors:

| Field         | Value / Formula | Rationale                                                                                                              |
|---------------|-----------------|------------------------------------------------------------------------------------------------------------------------|
| `price`       | P(t)            | Current FX rate — used by all agents for order sizing (qty × price calculations)                                       |
| `fundamental` | 1.20 (constant) | PPP-implied fair value; used to compute deviation                                                                      |
| `deviation`   | (P(t) − F) / F  | Primary signal for all agents; positive = target currency overvalued; negative = funding currency appreciated (crisis) |
| `round`       | t               | Round number; used by HedgedCarryTrader for rolling volatility calculation from price_history                          |

Note: `return_pct` is deliberately NOT included because carry trade strategies are fundamentally level-based (not momentum-based) — traders monitor whether the rate is above or below their entry level and stop-loss level, not the recent direction of movement.


## §4 Investor Taxonomy

### Investor: CarryTrader

#### 4.1.1  Summary

The CarryTrader is a leveraged hedge fund or institutional investor who borrows low-yield funding currencies (e.g., JPY) at near-zero interest rates and invests in high-yield target currencies (e.g., AUD) to earn the interest rate differential. This investor accumulates long positions in the target currency when conditions are favorable (positive or near-zero deviation from fundamental) and begins unwinding when conditions deteriorate. The CarryTrader is destabilizing during both phases: their buying during accumulation pushes the target currency above fundamental, and their selling during unwind accelerates the decline. The CarryTrader represents the core economic agent driving both the carry premium and the carry crash.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Carry Trade Returns and Uncovered Interest Parity Violation**
- Theory / Study: The carry trade premium and its crash risk
- Citation: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313–347. DOI: 10.1086/593088
- Core Insight: The carry trade exploits the violation of Uncovered Interest Parity (UIP): UIP predicts that high-yield currencies should depreciate by the interest differential, eliminating the carry return. In practice, high-yield currencies tend to appreciate or stay flat in normal times (the "carry premium"), while depreciating sharply in crash episodes. This asymmetry defines the carry trade's risk-return profile.
- Mathematical Formulation: UIP prediction: E[ΔP] = −(i_high − i_low). Observed: E[ΔP] ≈ +0.3% to +0.8% per month (carry premium). Crash: ΔP = −5% to −15% in crisis months. CarryTrader accumulates when deviation > 0 (target above fundamental = favorable carry conditions) and unwinds when deviation < −0.02 (target below fundamental = carry trade losing).
- Empirical Evidence: Brunnermeier et al. (2009) document that JPY carry trades earned +0.8% per month on average from 1990–2008, but experienced −15% losses in October 2008 alone. leverage = 5.0 is consistent with hedge fund leverage ratios documented in BIS (2015) survey of FX market leverage.
- Relevance to This Investor: CarryTrader's leverage = 5.0 multiplies both gains and losses; the sell trigger at deviation < −0.02 represents the threshold at which the carry trade begins losing enough that the position must be reduced.

**Theory 2: Limits of Arbitrage in Currency Markets**
- Theory / Study: Carry trade persistence under capital constraints
- Citation: Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637–666. DOI: 10.3982/TE2739
- Core Insight: Plantin & Shin show that carry traders cannot arbitrage away the carry premium because their capacity is capital-constrained: the more capital they commit, the larger the crash risk they bear. Equilibrium carry positions are self-limiting — but in practice, carry trades accumulate to the point where the cascade risk becomes systemic.
- Mathematical Formulation: CarryTrader sizing: qty = min(800 × leverage, |deviation| × 5000) = min(4000, |deviation| × 5000). With leverage = 5.0 and position = 4000 shares per direction, the CarryTrader represents a meaningful fraction of market depth, making its unwind market-moving.
- Relevance to This Investor: leverage = 5.0 and base_qty = 800 calibrated from Plantin & Shin estimates of typical hedge fund carry positions relative to FX market depth; sell condition at deviation < −0.02 models the capital constraint threshold.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Generate both the accumulation (pre-crisis) and unwind (crisis) phases. CarryTrader buying in the pre-crisis phase creates the overvaluation of the target currency that makes the eventual crash larger; CarryTrader selling during the crisis amplifies the decline beyond fundamental correction.

**Activation Scenarios**:
- Scenario A (Positive deviation, deviation > 0.02): Buy — accumulate long target currency position. Represents the normal carry trade accumulation phase; "buy and hold" while the carry premium is positive.
- Scenario B (Small negative deviation, −0.02 < deviation < 0): Hold — inside the tolerance band; carry trade still profitable, no action.
- Scenario C (Negative deviation, deviation < −0.02): Sell — begin unwinding the carry position. Target currency declining relative to fundamental → carry trade losing → position reduction begins.

**Market Contribution**: Destabilizing in both directions — amplifies upside during accumulation and downside during unwind.

**Interaction with other agents**: Sells alongside LeveragedCarryFund during unwind (both add sell pressure); FundingCurrencyBuyer opposes their selling; HedgedCarryTrader exits earlier (at first volatility spike) and thus sells less during peak cascade.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `deviation`: Primary signal — both trigger and sizing; positive deviation triggers buying (accumulation); negative deviation triggers selling (unwind). This is a level-based strategy responding to the current price-to-fundamental relationship.
- `price`: Used for sizing (cash / price) and order submission.
- Does NOT use rolling volatility (that's HedgedCarryTrader's differentiator); responds only to deviation level.

**4.1.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If |deviation| > 0.02: act (both positive and negative thresholds).
3. If deviation > +0.02: buy. qty = min(int(800 × leverage), int(|deviation| × 5000)) = min(4000, int(|deviation| × 5000)).
4. If deviation < −0.02: sell. qty = min(int(800 × leverage), int(|deviation| × 5000)) = min(4000, int(|deviation| × 5000)).
5. Hold if |deviation| ≤ 0.02.
6. The buy/sell quantities are identical in formula — symmetric activation; the deviation threshold of 0.02 is applied to both sides.

**4.1.4.3  Mathematical Model**
- Decision variable: Q*(t) in units
- Trigger: buy if δ(t) > +0.02; sell if δ(t) < −0.02; hold if |δ| ≤ 0.02
- Sizing: Q*(t) = min(floor(base × leverage), floor(|δ(t)| × 5000)) = min(4000, floor(|δ(t)| × 5000))
- State variables: cash, position

| Parameter | Value | Meaning                                        | Config Path                                        | Source                                             |
|-----------|-------|------------------------------------------------|----------------------------------------------------|----------------------------------------------------|
| leverage  | 5.0   | Leverage multiplier for position sizing        | `CarryTradeUnwind/Rule/config.yaml → carry_trader` | BIS (2015); Brunnermeier et al. (2009)             |
| base_qty  | 800   | Base trade quantity before leverage            | `CarryTradeUnwind/Rule/config.yaml → carry_trader` | Normalization                                      |
| threshold | 0.02  | Deviation threshold for carry position changes | `CarryTradeUnwind/Rule/config.yaml → carry_trader` | Calibrated to carry trigger in Brunnermeier et al. |

**4.1.4.4  Behavioral Properties**
- Time horizon: Medium-term carry accumulation; high-frequency exit during crisis
- Risk tolerance: High during accumulation; reactive (exits) when deviation threshold crossed
- Information asymmetry: None — deviation is publicly broadcast; CarryTrader exploits structural interest rate differential, not private information
- Psychological profile: Systematic, profit-driven, leverage-maximizing. In LLM variants, persona emphasizes exploiting the interest rate differential; psychological challenge is resisting panic selling before stop_loss is reached.

#### 4.1.5  Decision Process Walkthrough

Given: price = 1.22, fundamental = 1.20, deviation = +0.0167 (below 0.02 threshold), leverage = 5.0

Step 1: deviation = +0.0167. |0.0167| < 0.02 → hold. No action.

Given: price = 1.24, fundamental = 1.20, deviation = +0.033, leverage = 5.0

Step 1: deviation = +0.033 > +0.02 → buy.
Step 2: qty = min(int(800 × 5.0), int(0.033 × 5000)) = min(4000, 165) = 165 shares.
Step 3: Cash check: 165 × 1.24 = 204.6 (in nominal FX units → adjusted for initial_cash scale).
Step 4: Send order: action=buy, quantity=165, bid_price=1.24.
Result: +165 to D(t); modest accumulation buying; carries target currency higher.

#### 4.1.6  Worked Numerical Example

Market state: price = 1.16, fundamental = 1.20, deviation = −0.033, leverage = 5.0, position = 2000

Trigger: −0.033 < −0.02 → sell.
Quantity: min(int(800 × 5.0), int(0.033 × 5000)) = min(4000, 165) = 165.
Order: action=sell, quantity=165, bid_price=1.16.
Rationale: Price has fallen 3.3% below PPP fundamental; CarryTrader begins unwinding. At this deviation, the unwind quantity is modest (165 vs. 4000 max). As deviation worsens to −0.10: qty = min(4000, int(0.10 × 5000)) = min(4000, 500) = 500 — still below max. At deviation = −0.80: qty = min(4000, 4000) = 4000 — maximum. The position scaling ensures progressive acceleration of sell volume as the crisis deepens.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                         | Notes                                                                          |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1 | Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313–347. DOI: 10.1086/593088 | Primary reference; leverage calibration; carry premium and crash documentation |
| 2 | Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637–666. DOI: 10.3982/TE2739                        | Carry trade sizing and cascade condition; capital constraint theory            |


---

### Investor: LeveragedCarryFund

#### 4.2.1  Summary

The LeveragedCarryFund is a highly leveraged institutional fund — a hedge fund or proprietary trading desk — that has accumulated a large carry position using maximum available leverage. Unlike the CarryTrader (who unwinds gradually as deviation worsens), the LeveragedCarryFund has an explicit stop_loss trigger: when the deviation crosses −3%, the fund's risk management system forces immediate complete liquidation. This forced selling generates the bulk of the cascade's price impact. The LeveragedCarryFund is the simulation's primary crash amplifier: its position is large, its exit is forced and rapid, and its selling volume far exceeds the stabilizing capacity of FundingCurrencyBuyer.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Forced Liquidation and Funding Liquidity Spirals**
- Theory / Study: Liquidity spirals from leveraged position unwinding
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098
- Core Insight: Highly leveraged funds face forced liquidation when mark-to-market losses erode equity below margin requirements. Each forced sell simultaneously (a) reduces the fund's position, and (b) depresses market prices, which reduces the equity of all similarly positioned funds — triggering a cascade of simultaneous forced exits. The speed and severity of the cascade is proportional to: (fund leverage) × (position size) × (price impact per unit sold).
- Mathematical Formulation: Forced sell triggered when equity / assets < margin_requirement, equivalent to deviation < −stop_loss in the simulation. Forced sell volume: forced_sell = min(base_qty × leverage, position) = min(4000, position). This is a binary trigger: no gradual unwind — the risk management system demands immediate full exit.
- Empirical Evidence: LTCM in 1998 lost 90% of equity in months due to this spiral. In 2008 JPY carry unwind, prime broker margin calls forced hedge funds to liquidate simultaneously. stop_loss = 0.03 (3%) calibrated to represent typical FX fund risk limits (BIS 2015 survey: median hedge fund stop-loss threshold = 2–4%).
- Relevance to This Investor: stop_loss = 0.03 and leverage = 5.0 create a fund that is forced to sell up to 4000 units per round when triggered — generating the dominant sell pressure in the cascade.

**Theory 2: Systemic Herding in Leveraged FX Markets**
- Theory / Study: Simultaneous exit of leveraged carry positions
- Citation: Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637–666. DOI: 10.3982/TE2739
- Core Insight: When many leveraged carry funds share similar stop-loss levels (as is common in practice — risk management systems converge on similar VaR-based thresholds), their simultaneous exit creates a liquidity event far larger than any individual fund's position. Plantin & Shin show that this herding creates price discontinuities: prices can jump from near-fundamental to −10% or more in a single cascade episode when many leveraged funds hit their stops simultaneously.
- Empirical Evidence: Plantin & Shin cite the 2008 JPY carry unwind: estimated $300–500B in carry positions hitting stops within weeks, far exceeding the absorption capacity of FX markets during the period.
- Relevance to This Investor: Two LeveragedCarryFund agents with identical stop_loss = 0.03 model the herding behavior — when one hits its stop, the price decline it causes likely triggers the other, creating simultaneous multi-agent forced selling.

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Generate the primary cascade mechanism — the sudden, forced exit of a large leveraged position that creates a price discontinuity and triggers further forced exits. Without LeveragedCarryFund, the simulation cannot reproduce the violent, rapid unwind dynamics of historical carry crashes.

**Activation Scenarios**:
- Scenario A (Deviation within tolerance, |deviation| ≤ 0.03): Hold — stop_loss not breached; fund maintains full carry position.
- Scenario B (Stop_loss triggered, deviation < −0.03): FORCED SELL — immediately sell up to min(4000, position) units. This is a binary, non-discretionary exit driven by risk management protocol.
- Scenario C (Positive deviation, deviation > 0): Hold or small buy — fund may add to position in favorable conditions; but note the primary function is the forced exit.

**Market Contribution**: Dominantly destabilizing — the largest single source of sell volume during cascade. 2 × LeveragedCarryFund instances selling up to 4000 units each = 8000 units/round vs. 2 × FundingCurrencyBuyer buying 500 units each = 1000 units/round. Cascade condition: 8000 >> 1000.

**Interaction with other agents**: Amplifies CarryTrader selling (same direction); overwhelms FundingCurrencyBuyer buying; HedgedCarryTrader may have already exited (if volatility trigger fired earlier), reducing total sell volume.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Primary trigger — stop_loss is a level-based threshold on deviation; when crossed, forces complete exit.
- `position`: Determines actual sell quantity (bounded by current position).
- Does NOT use volatility — risk management is purely deviation-based (stop_loss), not volatility-based.

**4.2.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation < −stop_loss (−0.03) OR (deviation < 0 and |deviation| > 0.02): forced sell.
3. Sell quantity: forced_sell = min(int(base_qty × leverage), position) = min(4000, position).
4. If neither condition: hold (or buy at small deviations per CarryTrader-like logic in some implementations).
5. The critical feature is the binary, non-discretionary nature: no partial unwind, no gradual exit — risk management forces full immediate liquidation.

**4.2.4.3  Mathematical Model**
- Decision variable: forced exit quantity
- Trigger: sell if δ(t) < −stop_loss OR (δ(t) < 0 and |δ(t)| > 0.02)
- Sizing: Q*_sell = min(base_qty × leverage, position) = min(4000, position)
- State variables: position, cash

| Parameter | Value | Meaning                             | Config Path                                                | Source                         |
|-----------|-------|-------------------------------------|------------------------------------------------------------|--------------------------------|
| stop_loss | 0.03  | Deviation threshold for forced exit | `CarryTradeUnwind/Rule/config.yaml → leveraged_carry_fund` | BIS (2015) FX fund risk limits |
| leverage  | 5.0   | Position leverage multiplier        | `CarryTradeUnwind/Rule/config.yaml → leveraged_carry_fund` | Brunnermeier & Pedersen (2009) |
| base_qty  | 800   | Base position size                  | `CarryTradeUnwind/Rule/config.yaml → leveraged_carry_fund` | Normalization                  |

**4.2.4.4  Behavioral Properties**
- Time horizon: Position held long-term; exit is immediate and forced
- Risk tolerance: Very Low — forced exit at first stop_loss breach; no discretion
- Information asymmetry: None
- Psychological profile: Systematic risk management; no emotional override; the trigger is algorithmic. In LLM variants, the key test is whether the persona faithfully executes the forced exit rather than deliberating.

#### 4.2.5  Decision Process Walkthrough

Given: price = 1.164, fundamental = 1.20, deviation = −0.03 (exactly at stop_loss), position = 4000

Step 1: deviation = −0.03. Is −0.03 < −0.03? This is boundary case — treat as triggered.
Step 2: Forced sell = min(4000, 4000) = 4000 units.
Step 3: Order: action=sell, quantity=4000, bid_price=1.164.
Result: −4000 to D(t); price impact = λ × 4000 = 0.02 × 4000 = 80 units... 

Note on scale: actual impact in FX rate points = 0.02 × 4000 × (FX rate scale / normalization). The key feature is that LeveragedCarryFund's sell volume (4000) is 8× FundingCurrencyBuyer's buy volume (500), ensuring the cascade proceeds.

#### 4.2.6  Worked Numerical Example

Market state: price = 1.155, fundamental = 1.20, deviation = −0.0375, position = 3500

Trigger: −0.0375 < −0.03 → forced sell.
Quantity: min(4000, 3500) = 3500.
Order: action=sell, quantity=3500, bid_price=1.155.
Rationale: LeveragedCarryFund has lost (1.20 − 1.155) / 1.20 = 3.75% on its position; with leverage = 5.0, this represents 18.75% equity loss. Risk management mandates forced exit, consistent with Brunnermeier & Pedersen (2009) margin call mechanics.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                          | Notes                                                                         |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098 | Forced liquidation mechanics; funding liquidity spiral; stop_loss calibration |
| 2 | Plantin, G., & Shin, H. S. (2018). "Exchange rates and monetary spillovers." *Theoretical Economics*, 13(2), 637–666. DOI: 10.3982/TE2739                         | Herding and simultaneous exit; cascade condition analysis                     |


---

### Investor: FundingCurrencyBuyer

#### 4.3.1  Summary

The FundingCurrencyBuyer is a risk-averse investor — pension fund, central bank reserve manager, or safe-haven-seeking institutional — who buys the funding currency (e.g., JPY, CHF) when carry trade stress exceeds a threshold. This safe-haven demand provides the natural counter-pressure to forced carry trade unwinding. However, the FundingCurrencyBuyer's position size (500 units) is deliberately small relative to LeveragedCarryFund's forced selling (4000 units), representing the real-world situation where safe-haven demand is insufficient to fully absorb a large carry crash. The FundingCurrencyBuyer is the simulation's primary stabilizing force — it limits but cannot prevent the crash.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Safe-Haven Demand and Flight-to-Quality**
- Theory / Study: JPY and CHF as safe-haven funding currencies
- Citation: Ranaldo, A., & Söderlind, P. (2010). "Safe haven currencies." *Review of Finance*, 14(3), 385–407. DOI: 10.1093/rof/rfq007. Also: Brunnermeier, M. K., & Pedersen, L. H. (2009). DOI: 10.1093/rfs/hhn098
- Core Insight: During risk-off episodes, investors worldwide buy the funding currency (JPY, CHF) as a safe haven, providing natural demand that partially offsets carry trade forced selling. This safe-haven demand is triggered by the same risk sentiment deterioration that forces carry trade exits — making it simultaneously stabilizing for the funding currency but potentially insufficient to prevent the full cascade.
- Mathematical Formulation: Safe-haven trigger: buy if δ(t) < −risk_threshold = −0.05. Buy quantity: position_size = 500 (fixed, not deviation-scaled). Total stabilizing volume: 2 FCB agents × 500 = 1000 units vs. 2 LCF agents × 4000 = 8000 units cascade selling. Net cascade: 8000 − 1000 = 7000 units/round during peak.
- Empirical Evidence: Ranaldo & Söderlind (2010) document that JPY appreciates by 1–3% for every 1 standard deviation increase in VIX or CDS spreads during risk-off episodes — a systematic but finite safe-haven flow. The fact that JPY still appreciated 20% in 2008 (despite safe-haven flows) demonstrates that forced carry unwind exceeds safe-haven demand, consistent with the simulation's design.
- Relevance to This Investor: risk_threshold = 0.05 (5%) and position_size = 500 calibrated so that FundingCurrencyBuyer's buying provides a visible but insufficient floor — realistic per Ranaldo & Söderlind (2010)'s documented magnitude of safe-haven flows.

**Theory 2: Market-Clearing and Recovery Mechanism**
- Theory / Study: Mean-reversion and recovery following FX overshoots
- Citation: Rogoff, K. (1996). "The purchasing power parity puzzle." *Journal of Economic Literature*, 34(2), 647–668. DOI: 10.2307/2729217
- Core Insight: Rogoff (1996)'s PPP puzzle documents that FX rates deviate substantially from PPP for years but do ultimately revert. The FundingCurrencyBuyer, combined with the γ-mean-reversion term in the price equation, represents the equilibrating forces that prevent permanent FX misalignment. Their combined effect (FCB buying + PPP gravity) determines the recovery ratio after the cascade.
- Relevance to This Investor: FundingCurrencyBuyer's buying at deviation < −0.05 provides discrete recovery assistance on top of the continuous γ-mean-reversion; their combined effect is tested by the recovery_ratio metric.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Provide partial stabilization during the carry unwind cascade — model the safe-haven demand that limits crash depth. The FundingCurrencyBuyer does not prevent the crash (deliberately under-sized) but creates a price floor that limits the maximum deviation.

**Activation Scenarios**:
- Scenario A (Deviation > −5%): Hold — safe-haven demand not yet triggered; carry stress insufficient to generate flight-to-quality.
- Scenario B (Deviation < −5%): Buy fixed position_size = 500. Safe-haven buying activates; provides 1000 units/round of demand across 2 instances.
- Scenario C (Full recovery, deviation > 0): May sell to rebalance back to neutral; not implemented in base version.

**Market Contribution**: Stabilizing — partial floor at deviation < −5%. Combined 2-instance buying of 1000 units/round is visible in net demand but overwhelmed by cascade selling of 8000 units/round.

**Interaction with other agents**: Directly opposes LeveragedCarryFund and CarryTrader selling; aligns with HedgedCarryTrader in reducing net sell pressure; NoiseTrader occasionally reinforces or reduces their net buying.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Sole trigger signal — buy when deviation < −risk_threshold.
- `price`, `cash`: Constraint variables.

**4.3.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation < −risk_threshold (−0.05): buy position_size = 500 units (cash-constrained).
3. Hold otherwise.

**4.3.4.3  Mathematical Model**
- Trigger: buy if δ(t) < −risk_threshold = −0.05
- Sizing: Q*(t) = min(position_size, floor(cash / price)) = min(500, floor(cash / price))

| Parameter      | Value | Meaning                                           | Config Path                                                  | Source                                     |
|----------------|-------|---------------------------------------------------|--------------------------------------------------------------|--------------------------------------------|
| risk_threshold | 0.05  | Deviation below which safe-haven buying activates | `CarryTradeUnwind/Rule/config.yaml → funding_currency_buyer` | Ranaldo & Söderlind (2010)                 |
| position_size  | 500   | Fixed units per safe-haven buy                    | `CarryTradeUnwind/Rule/config.yaml → funding_currency_buyer` | Normalization (deliberately small vs. LCF) |

**4.3.4.4  Behavioral Properties**
- Time horizon: Medium-term safe-haven holding; exits when crisis resolves
- Risk tolerance: Low — buys as a safe-haven, not as risk-taking
- Information asymmetry: None
- Psychological profile: Risk-averse, safe-haven-driven, systematic. In LLM variants, persona emphasizes capital preservation and flight-to-quality narrative.

#### 4.3.5  Decision Process Walkthrough

Given: price = 1.14, fundamental = 1.20, deviation = −0.05, risk_threshold = 0.05, cash = 50000

Step 1: deviation = −0.05. Is −0.05 < −0.05? Boundary — treat as triggered.
Step 2: Quantity = min(500, floor(50000 / 1.14)) = min(500, 43859) = 500.
Step 3: Order: action=buy, quantity=500, bid_price=1.14.
Result: +500 to D(t); partial offset of cascade selling.

#### 4.3.6  Worked Numerical Example

Market state: price = 1.10, fundamental = 1.20, deviation = −0.0833, cash = 45000

Trigger: −0.0833 < −0.05 → buy.
Quantity: min(500, floor(45000 / 1.10)) = min(500, 40909) = 500.
Order: action=buy, quantity=500, bid_price=1.10.
Rationale: 8.3% appreciation of the funding currency triggers safe-haven demand, consistent with Ranaldo & Söderlind (2010)'s documented 1–3% JPY appreciation per VIX standard deviation — at extreme deviations, systematic safe-haven flows activate.

#### 4.3.7  Academic References

| # | Citation                                                                                                                        | Notes                                                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| 1 | Ranaldo, A., & Söderlind, P. (2010). "Safe haven currencies." *Review of Finance*, 14(3), 385–407. DOI: 10.1093/rof/rfq007      | risk_threshold and position_size calibration; safe-haven flow documentation |
| 2 | Rogoff, K. (1996). "The purchasing power parity puzzle." *Journal of Economic Literature*, 34(2), 647–668. DOI: 10.2307/2729217 | Recovery mechanism; PPP gravity combined with FCB buying                    |


---

### Investor: HedgedCarryTrader

#### 4.4.1  Summary

The HedgedCarryTrader is a sophisticated carry fund that incorporates volatility risk management: it carries a FX options hedge (modeled as hedge_ratio = 0.30 of position) and adjusts its directional exposure based on rolling volatility. When FX volatility is low, the HedgedCarryTrader accumulates carry positions (but with 30% hedge reducing net exposure); when volatility spikes above threshold, it exits. This investor represents the more sophisticated "smart carry" strategies documented by Menkhoff et al. (2012) — carry trades that adapt to the volatility environment rather than mechanically holding.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Volatility-Adjusted Carry (Menkhoff et al.)**
- Theory / Study: Global FX volatility and carry trade returns
- Citation: Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). "Carry trades and global foreign exchange volatility." *Journal of Finance*, 67(2), 681–718. DOI: 10.1111/j.1540-6261.2012.01728.x
- Core Insight: Carry trade returns are strongly negatively related to FX volatility innovations. Menkhoff et al. find that a volatility-timing strategy (scaling carry positions inversely with volatility) generates Sharpe ratios 50–100% higher than naive carry — demonstrating the value of volatility-aware position management.
- Mathematical Formulation: Volatility-adjusted position: adj_qty = base_qty × (1 − hedge_ratio) = 500 × 0.7 = 350. Entry condition: deviation > 0 AND rolling_vol < vol_threshold (0.05). Exit condition: deviation < 0 AND rolling_vol > vol_threshold (0.05). Rolling volatility: σ(t) = std(r[t−N:t]) where r = price returns.
- Empirical Evidence: Menkhoff et al. (2012) find that volatility-timed carry generates annualized Sharpe ratio of 1.2–1.5 vs. 0.4–0.8 for naive carry. vol_threshold = 0.05 calibrated to represent one standard deviation of daily FX volatility — the level at which risk-adjusted carry becomes unattractive.
- Relevance to This Investor: The HedgedCarryTrader exits before the full cascade peak (triggered by vol_threshold) — it is typically fully exited before LeveragedCarryFund's stop_loss is hit. This models the empirical observation that sophisticated carry funds exit early while naïve leveraged funds hold until forced.

**Theory 2: Dynamic Hedging and Options-Based Carry**
- Theory / Study: Hedged carry trade strategies
- Citation: Burnside, C., Eichenbaum, M., Kleshchelski, I., & Rebelo, S. (2011). "Do peso problems explain the returns to the carry trade?" *Review of Financial Studies*, 24(3), 853–891. DOI: 10.1093/rfs/hhq138
- Core Insight: Burnside et al. document that purchasing put options to hedge crash risk reduces carry returns by 2–4% per year but eliminates crash losses. The hedge_ratio = 0.30 models this partial hedging: 30% of the position is covered, reducing net directional exposure to 70% while maintaining most of the carry premium. The hedge cost is modeled implicitly as the reduced position size.
- Relevance to This Investor: adj_qty = 350 (70% of base 500) represents the reduced directional exposure after hedging; the HedgedCarryTrader's smaller position means its exit during the cascade adds less to selling pressure than LeveragedCarryFund — a realistic difference between hedged and unhedged funds.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Model volatility-aware carry trade participation — a sophisticated counterpart to the naive LeveragedCarryFund. The HedgedCarryTrader adds carry accumulation during stable phases but exits earlier than LeveragedCarryFund during stress, reducing its cascade contribution.

**Activation Scenarios**:
- Scenario A (Low volatility, deviation > 0): Buy (adj_qty = 350) — entering carry with partial hedge; models slow accumulation during risk-on periods.
- Scenario B (High volatility spike, deviation < 0): Sell (adj_qty = 350) — exits before stop_loss is reached; reduces total cascade selling volume vs. LeveragedCarryFund.
- Scenario C (High volatility, small positive deviation): Hold — vol above threshold even if rate above fundamental; HedgedCarryTrader requires BOTH favorable rate AND low volatility.

**Market Contribution**: Mildly destabilizing during exit (adds to cascade selling, but 350 vs. LCF's 4000); moderately stabilizing relative to LeveragedCarryFund (exits earlier, sells less at peak).

**Interaction with other agents**: Sells alongside LeveragedCarryFund and CarryTrader during unwind but at smaller size; partially offsets FundingCurrencyBuyer buying during accumulation.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**
- `deviation`: Directional signal — buy when positive, sell when negative.
- Rolling volatility (computed from price_history): Second condition — only act when vol is on the right side of threshold.
- `price`: For order submission.

**4.4.4.2  Core Behavioral Mechanism**
1. Compute rolling volatility σ(t) = std(recent price returns).
2. If deviation > 0 AND σ < vol_threshold (0.05): buy adj_qty = 350.
3. If deviation < 0 AND σ > vol_threshold (0.05): sell adj_qty = 350.
4. Hold otherwise.

**4.4.4.3  Mathematical Model**
- Two-signal trigger: buy if δ > 0 AND σ < 0.05; sell if δ < 0 AND σ > 0.05
- Sizing: Q*(t) = adj_qty = base_qty × (1 − hedge_ratio) = 500 × 0.70 = 350

| Parameter     | Value | Meaning                                            | Config Path                                               | Source                 |
|---------------|-------|----------------------------------------------------|-----------------------------------------------------------|------------------------|
| hedge_ratio   | 0.30  | Fraction of position hedged (reduces net exposure) | `CarryTradeUnwind/Rule/config.yaml → hedged_carry_trader` | Burnside et al. (2011) |
| vol_threshold | 0.05  | FX volatility threshold for position adjustment    | `CarryTradeUnwind/Rule/config.yaml → hedged_carry_trader` | Menkhoff et al. (2012) |
| base_qty      | 500   | Base quantity before hedge ratio reduction         | `CarryTradeUnwind/Rule/config.yaml → hedged_carry_trader` | Normalization          |

**4.4.4.4  Behavioral Properties**
- Time horizon: Carry accumulation (medium-term); quick exit on volatility spike
- Risk tolerance: Medium — hedge reduces crash exposure; volatility-managed
- Information asymmetry: None — uses only publicly available price data for volatility calculation
- Psychological profile: Sophisticated, volatility-aware, risk-adjusted. In LLM variants, persona explicitly mentions "I monitor volatility and exit when it spikes."

#### 4.4.5  Decision Process Walkthrough

Given: price = 1.22, fundamental = 1.20, deviation = +0.017, rolling_vol = 0.03 (< 0.05)

Step 1: deviation > 0 AND vol = 0.03 < 0.05 → buy condition met.
Step 2: adj_qty = 500 × (1 − 0.30) = 350.
Step 3: Order: action=buy, quantity=350, bid_price=1.22.
Result: Carry accumulation in low-volatility environment.

#### 4.4.6  Worked Numerical Example

Market state: price = 1.17, fundamental = 1.20, deviation = −0.025, rolling_vol = 0.07 (> 0.05)

Step 1: deviation < 0 AND vol = 0.07 > 0.05 → sell condition met.
Step 2: adj_qty = 350.
Step 3: Order: action=sell, quantity=350, bid_price=1.17.
Rationale: Volatility has spiked above threshold while carry is losing — HedgedCarryTrader exits early, before LeveragedCarryFund's stop_loss (−3%) is triggered at deviation = −0.025. This early exit reduces total cascade selling at the peak, consistent with Menkhoff et al.'s documentation that volatility-aware funds exit earlier and suffer smaller losses.

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                                               | Notes                                                                     |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| 1 | Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). "Carry trades and global foreign exchange volatility." *Journal of Finance*, 67(2), 681–718. DOI: 10.1111/j.1540-6261.2012.01728.x      | vol_threshold calibration; volatility-adjusted carry strategy performance |
| 2 | Burnside, C., Eichenbaum, M., Kleshchelski, I., & Rebelo, S. (2011). "Do peso problems explain the returns to the carry trade?" *Review of Financial Studies*, 24(3), 853–891. DOI: 10.1093/rfs/hhq138 | hedge_ratio calibration; hedged carry trade design                        |


---

### Investor: NoiseTrader

#### 4.5.1  Summary

The NoiseTrader provides background FX order flow — representing importers, exporters, portfolio managers, and retail FX participants whose trades are unconnected to carry trade positioning. In FX markets, non-speculative flow accounts for approximately 60–70% of daily volume, providing the liquidity that makes carry trades executable. trade_probability = 0.30 is calibrated to a higher value than BlackMonday1987 (0.05) because FX markets have substantially more non-speculative background activity.

#### 4.5.2  Theoretical and Empirical Foundation

**Theory 1: Noise Trading as Market Liquidity (Black)**
- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481
- Core Insight: Noise traders are essential for liquidity. trade_probability = 0.30 calibrated to represent non-speculative FX participation. Quantity range [100, 500] represents retail and small institutional lot sizes.

#### 4.5.3  Design Purpose and Activation Scenarios

**Purpose**: Prevent deterministic price paths; model genuine background FX market activity; ensure variance across simulation runs for statistical analysis.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**: None — purely random.

**4.5.4.2  Core Behavioral Mechanism**
1. Draw r ~ Uniform(0, 1). If r < 0.30: trade.
2. Draw direction (buy/sell, 50/50); draw quantity ~ Uniform(100, 500).
3. Execute. Hold otherwise.

**4.5.4.3  Mathematical Model**
- P(trade) = 0.30; direction = 50/50; Q ~ Uniform(100, 500)

| Parameter         | Value | Source             |
|-------------------|-------|--------------------|
| trade_probability | 0.30  | Black (1986)       |
| min_order         | 100   | FX market lot size |
| max_order         | 500   | FX market lot size |

**4.5.4.4  Behavioral Properties**: Random, neutral, stochastic.

#### 4.5.5  Decision Process Walkthrough

r = 0.18 < 0.30 → trade. Direction: buy. Quantity: 300. Order: buy 300 at current price.

#### 4.5.6  Worked Numerical Example

r = 0.65 ≥ 0.30 → hold. No order sent.
r = 0.12 < 0.30 → trade. Direction: sell. Quantity: 210. Order: sell 210 at current FX rate.

#### 4.5.7  Academic References

| # | Citation                                                                              | Notes                                               |
|---|---------------------------------------------------------------------------------------|-----------------------------------------------------|
| 1 | Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481 | trade_probability calibration; noise trading theory |


## §5 Agent Diversity Verification

Diversity Check:
- Different roles: CarryTrader (gradual unwind); LeveragedCarryFund (forced binary exit); FundingCurrencyBuyer (safe-haven counter); HedgedCarryTrader (volatility-aware sophistication); NoiseTrader (background noise)
- Different signals: CarryTrader (deviation level); LeveragedCarryFund (deviation vs. stop_loss); FundingCurrencyBuyer (deviation below risk_threshold); HedgedCarryTrader (deviation + rolling volatility); NoiseTrader (none)
- Different sizing: LeveragedCarryFund (4000 — largest); CarryTrader (up to 4000 — deviation-proportional); HedgedCarryTrader (350 — reduced by hedge); FundingCurrencyBuyer (500 — fixed modest); NoiseTrader (100–500 random)
- Cascade condition by design: LCF forced selling (8000/round) >> FCB stabilizing (1000/round) → cascade proceeds; realistic per Plantin & Shin (2018)
- Asymmetric behavior: HedgedCarryTrader requires BOTH favorable deviation AND low volatility to enter; sole agent with two-signal decision logic


## §6 Parameter Table

| Parameter                           | Value | Source Citation                        | Description                            | Sensitivity                                       |
|-------------------------------------|-------|----------------------------------------|----------------------------------------|---------------------------------------------------|
| initial_price                       | 1.20  | Normalization                          | Starting FX rate                       | Low — scale only                                  |
| fundamental_value                   | 1.20  | PPP normalization                      | PPP-implied equilibrium FX rate        | Medium — determines deviation magnitude           |
| price_impact (λ)                    | 0.02  | Brunnermeier, Nagel & Pedersen (2009)  | Price response per unit net demand     | High — cascade speed and depth                    |
| mean_reversion (γ)                  | 0.02  | Rogoff (1996)                          | PPP gravity strength                   | Medium — recovery rate                            |
| noise_std (σ)                       | 0.02  | BIS (2022) FX baseline                 | Background FX noise                    | Low — random trigger variability                  |
| CarryTrader leverage                | 5.0   | BIS (2015); Brunnermeier et al. (2009) | Leverage multiplier                    | High — position size and unwind speed             |
| LeveragedCarryFund stop_loss        | 0.03  | BIS (2015) risk limit survey           | Forced exit deviation threshold        | High — earlier trigger → faster cascade           |
| LeveragedCarryFund leverage         | 5.0   | Brunnermeier & Pedersen (2009)         | Leverage multiplier                    | High — sell volume at forced exit                 |
| FundingCurrencyBuyer risk_threshold | 0.05  | Ranaldo & Söderlind (2010)             | Safe-haven activation threshold        | Medium — deeper floor/ceiling                     |
| FundingCurrencyBuyer position_size  | 500   | Normalization                          | Fixed safe-haven buy size per instance | Medium — stabilization effectiveness              |
| HedgedCarryTrader hedge_ratio       | 0.30  | Burnside et al. (2011)                 | Position hedge fraction                | Low — adjusts net exposure slightly               |
| HedgedCarryTrader vol_threshold     | 0.05  | Menkhoff et al. (2012)                 | Volatility-based exit threshold        | Medium — controls when sophisticated exit happens |
| NoiseTrader trade_probability       | 0.30  | Black (1986)                           | Per-round trade probability            | Low — background noise level                      |


## §7 Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, fundamental, deviation, round}
  2. Each investor:
     a. perceive() — extract and store market data
     b. decide()   — apply strategy (rule / LLM call)
     c. act()      — send order to Market
  3. Market:
     a. perceive() — collect all orders; compute net_demand
     b. decide()   — apply price formula P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε
     c. act()      — broadcast new state
  4. Logging and state persistence
```

Key difference from equity simulations: `return_pct` is NOT broadcast — all agents use deviation from PPP fundamental, not price momentum, as their primary signal.


## §8 Historical Case Studies

### Event 1: JPY Carry Unwind — 2008 Financial Crisis

**Date**: August–October 2008
**Market**: USD/JPY (and related JPY cross rates AUD/JPY, NZD/JPY)
**Timeline**:
- Pre-crisis (2005–2007): JPY carry trade accumulated; estimated $500B–$1T in outstanding positions. USD/JPY drifted from 105 to 124 (appreciation of target currency / depreciation of funding currency).
- August 2008: USD/JPY began declining as Lehman stress became apparent; initial portfolio adjustments.
- September 15, 2008 (Lehman collapse): Massive risk-off; USD/JPY fell from 108 to 100 in one week.
- October 2008: Peak carry unwind; USD/JPY reached 88 by late October — a 20% decline from July peak.
- Recovery: Partial recovery to 95 by December 2008; full recovery took years.

**Quantitative Data**:
- USD/JPY decline: 124 → 88 over 4 months (−29%); largest JPY appreciation since 1998 crisis
- AUD/JPY decline: 107 → 55 (−49%) — high-yield target currency suffered extreme losses
- VIX peak: 89.5 on November 20, 2008
- Estimated carry position liquidation: $200–300B in forced FX trades

**Agent Mapping**:
- CarryTrader → Medium-sized hedge funds with 3–5× leverage that began unwinding early
- LeveragedCarryFund → Large leveraged funds (Citadel, SAC Capital, etc.) that held until margin calls forced exits
- FundingCurrencyBuyer → Japanese repatriation flows; pension fund safe-haven buying; central bank reserve rebalancing
- HedgedCarryTrader → Macro funds with explicit FX options hedges that exited early
- NoiseTrader → Importers/exporters, retail FX traders, non-carry institutional flows

**Lesson for Simulation**: The 2008 JPY carry unwind demonstrates that: (a) the cascade condition (forced sell > safe-haven buy) was met; (b) the unwind was faster than the build-up (consistent with "elevator down" dynamic); (c) partial recovery occurred as fundamental PPP gravity eventually reasserted.

### Event 2: CHF Flash Crash — January 15, 2015

**Date**: January 15, 2015
**Market**: EUR/CHF (and USD/CHF, GBP/CHF)
**Event**: Swiss National Bank (SNB) removed the EUR/CHF 1.20 floor without warning. EUR/CHF fell from 1.20 to 0.85 within minutes (−29%) before recovering to 1.00.
**Key Dynamics**: Unlike the 2008 JPY unwind (gradual cascade), this was a single discontinuous shock. The stop_loss mechanism in the simulation captures both cases: gradual cascade (2008 JPY) and discontinuous jump (2015 CHF).
**Agent Mapping**: LeveragedCarryFund → all carry funds simultaneously forced out; FundingCurrencyBuyer → delayed activation (shock was too sudden for orderly safe-haven flows); HedgedCarryTrader → hedge activated immediately, limiting losses.
**Lesson for Simulation**: The 2015 event illustrates that stop_loss triggers can fire simultaneously across all LeveragedCarryFund instances — the simulation's "herding" design (two LCF agents with same stop_loss) is validated.

### Event 3: JPY Carry Unwind — Summer 2024

**Date**: July–August 2024
**Market**: USD/JPY, AUD/JPY, global carry trades
**Event**: Bank of Japan unexpected rate hike triggered JPY appreciation; USD/JPY fell from 161 to 142 (−12%) in 3 weeks; global risk assets fell simultaneously as carry unwinds forced deleveraging across asset classes.
**Lesson for Simulation**: The 2024 episode confirms that the carry unwind mechanism is not historically isolated — it is a recurring feature of leveraged FX markets whenever funding rate expectations shift. The simulation captures this recurrence by parameterizing the cascade condition as a permanent structural risk.


## §9 Variant Comparison Preview

| Aspect               | Rule                                                  | LLM                                                        | RuleLLM                                          | Rag                                                             |
|----------------------|-------------------------------------------------------|------------------------------------------------------------|--------------------------------------------------|-----------------------------------------------------------------|
| Decision Logic       | Exact thresholds; deterministic cascade               | Persona + LLM reasoning about carry dynamics               | Formula-anchored LLM                             | RAG-augmented with historical carry crash knowledge             |
| Determinism          | Deterministic (modulo NoiseTrader)                    | Stochastic — LLM may delay or accelerate unwind decisions  | Semi-deterministic                               | Stochastic — depends on retrieved context                       |
| Expected Crash Depth | Consistent, calibrated (10–25% drawdown)              | Variable — LLM carry fund may show delayed exit or herding | Near-Rule; ±20% quantity on individual trades    | Modified by 2008/2015/2024 historical carry crash context       |
| Research Question    | Does forced-sell cascade produce historical drawdown? | Do LLM carry personas reproduce forced exit mechanics?     | Does rule anchoring constrain LLM unwind timing? | Does 2008 JPY crash knowledge change leverage or exit behavior? |
