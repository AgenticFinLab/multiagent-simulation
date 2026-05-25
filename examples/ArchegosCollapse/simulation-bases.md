# ArchegosCollapse — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | **Concentrated Leveraged Liquidation Cascade** — the Archegos Capital Management collapse (March 2021) exemplifies how a single hidden-leverage position can trigger a self-reinforcing prime broker race to liquidate, amplifying losses in rapid sequence                                                                                                                                                                                                                                                                                                           |
| Category           | Forced liquidation / prime broker cascade / leverage unwind / systemic risk                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Core Mechanism     | A highly-leveraged fund holds synthetic equity exposure via Total Return Swaps (TRS), invisible to public filings. When the reference asset declines and margin calls cannot be met, the fund begins forced selling. This initial selling drives prices lower, triggering additional margin calls. Multiple prime brokers, each aware that slower liquidation means worse prices as others sell ahead of them, race to liquidate first — a creditor run that amplifies the initial price decline into a cascade disproportionate to any single actor's position size. |
| Real-World Origin  | Archegos Capital Management, March 24–29, 2021. Losses: Credit Suisse $5.5B, Nomura $2.9B, Morgan Stanley $1B+; ViacomCBS fell ~60% in one week                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Research Relevance | Archegos exposed how TRS-based leverage creates hidden systemic risk invisible to both regulators and counterparties. It illustrates the first-mover advantage incentive in creditor cascades, a mechanism with direct implications for systemic risk regulation, prime broker risk management, and the design of disclosure requirements for synthetic equity instruments.                                                                                                                                                                                           |


## §2 Theoretical Foundation

### Theory: Total Return Swap (TRS) Leverage and Hidden Systemic Risk

- **Citation**: Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1–12. https://doi.org/10.18651/ER/v106n3Becketti
- **Core Insight**: Total Return Swaps allow a fund to gain synthetic equity exposure without the reference assets appearing on the fund's balance sheet or in public SEC 13F filings. This means leverage can accumulate to extreme levels (5x–10x) before any counterparty or regulator observes concentration risk. When the reference asset declines and collateral requirements rise, the fund faces a sudden forced close-out across multiple simultaneous TRS contracts.
- **Mathematical Formulation**:
  ```
  Notional exposure = position_size × P(t)
  Margin requirement = Notional × margin_rate
  Forced close-out triggered when: equity(t) < maintenance_margin × Notional
  where equity(t) = initial_equity + unrealized_PnL(t)
  ```
- **Empirical Evidence**: The Financial Stability Board (2022) estimated Archegos held $35–40B in notional TRS exposure across 5 prime brokers simultaneously, with leverage ratios of 5–8x equity (FSB, 2022, "Non-bank Financial Intermediation" report, pp. 47–51). Individual margin requirements ranged from 10–25% depending on broker and asset volatility.
- **Relevance to This Simulation**: The `ConcentratedFund` agent holds a large initial position representing synthetic TRS exposure. Its forced selling is triggered when price deviation exceeds the maintenance margin threshold, modeling the exact mechanism that initiated the Archegos cascade.
- **Calibration Implication**: leverage_trigger = 0.15 represents a price decline sufficient to breach the maintenance margin; liquidation_fraction = 0.50 reflects typical forced close-out fractions documented in prime broker risk policies.

---

### Theory: Creditor Run and First-Mover Advantage in Liquidation Races

- **Citation**: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016
- **Core Insight**: When multiple creditors each hold collateral against the same distressed borrower, their collective incentive structure mirrors a bank run. Each creditor knows that if they liquidate before others, they receive higher prices (before market impact from mass selling). If they wait, others' liquidation drives down the collateral value, reducing their recovery. This first-mover advantage creates a dominant strategy of immediate liquidation, even when coordinated delay might produce better collective outcomes.
- **Mathematical Formulation**:
  ```
  Payoff(broker i | liquidates at t_i) = Q_i × P(t_i)
  where P(t_i) < P(t_j) for all t_i > t_j (subsequent sellers receive worse prices)

  Expected payoff differential (first vs second mover):
  ΔPayoff = Q × [P(t_1) − P(t_2)] = Q × λ × Q_1 > 0   for Q, Q_1 > 0
  ```
- **Empirical Evidence**: In the Archegos event, Morgan Stanley (acting first, March 25–26) recovered significantly better than Credit Suisse (acting later, March 29), consistent with the first-mover payoff advantage. Gorton & Metrick (2012) document that repo creditors' rollover decisions follow a coordination game with Nash equilibrium in the "run" strategy when collateral quality falls below a threshold.
- **Relevance to This Simulation**: The timing asymmetry between `PrimeBroker1` (lower threshold, acts first) and `PrimeBroker2` (higher threshold, acts later and at worse prices) directly models the first-mover advantage. The gap between their threshold values (0.10 vs 0.15) calibrates the price penalty for delayed action.
- **Calibration Implication**: PrimeBroker1.liquidation_threshold = 0.10 < PrimeBroker2.liquidation_threshold = 0.15; the price at which PrimeBroker2 sells is approximately λ × Q₁ below PrimeBroker1's selling price.

---

### Theory: Opportunistic Block Trading and Market Stabilization

- **Citation**: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617–637. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x
- **Core Insight**: In markets with infrequent large-order flow, liquidity providers must hold inventory against the risk of adverse price moves. Block trade buyers will only absorb forced supply when the price discount is sufficient to compensate for inventory risk during the holding period before resale. This creates a natural price floor in liquidation cascades: when discounts exceed the risk-compensation threshold, opportunistic buyers absorb supply and stabilize prices.
- **Mathematical Formulation**:
  ```
  Buyer activates when: |deviation(t)| > discount_threshold
  where discount_threshold ≥ risk_premium + expected_holding_cost
  Quantity absorbed: Q_buy = α × cash / P(t)
  where α is the capital deployment fraction (typically 0.25–0.40)
  ```
- **Empirical Evidence**: Grossman & Miller (1988) estimate that block trade discounts of 1.5–3.0% are sufficient to attract opportunistic buyers in normal equity markets. In distressed markets (Archegos, LTCM), observed discounts were 5–15% before buyers absorbed supply, consistent with higher inventory risk in stress periods.
- **Relevance to This Simulation**: `BlockTradeBuyer` activates when deviation crosses −0.10 (a 10% discount from fundamental), representing the opportunistic buyer's risk-compensation threshold. Its presence creates the price floor that eventually halts the cascade.
- **Calibration Implication**: discount_threshold = 0.10 based on Grossman & Miller's distressed market estimates; cash_deployment = 0.30 represents conservative capital allocation by institutional buyers.


## §3 Market Design Principles

### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol     | Name                 | Definition                                                       | Role in Cascade                                                       |
|------------|----------------------|------------------------------------------------------------------|-----------------------------------------------------------------------|
| P(t)       | Current price        | Market price at start of round t                                 | State variable; triggers margin calls when it falls                   |
| D(t)       | Net demand           | Σ buy_quantity − Σ sell_quantity across all investors in round t | Negative during cascade (sellers dominate); drives price down         |
| F          | Fundamental value    | Constant intrinsic value = 100.0 (normalization)                 | Mean reversion anchor; determines deviation magnitude                 |
| λ (lambda) | Price impact         | Price change per unit net demand                                 | 0.03 — calibrated to produce 5–8% price moves from block selling      |
| γ (gamma)  | Mean reversion speed | Speed of correction toward F per round                           | 0.01 — slow enough to allow cascade to develop over 10–20 rounds      |
| ε(t)       | Noise                | ~ N(0, σ²), σ = 0.015                                            | Background trading noise; prevents perfectly deterministic thresholds |

**Calibration Rationale**:

| Parameter | Value | Empirical Range | Source                                                                                                        | Sensitivity                                                                            |
|-----------|-------|-----------------|---------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| λ         | 0.03  | 0.01–0.05       | Hasbrouck (1991), *Journal of Finance*, 46(1), 179–207 — intraday price impact of large institutional orders  | High: λ = 0.05 → cascade 67% deeper; λ = 0.01 → cascade too shallow to trigger brokers |
| γ         | 0.01  | 0.005–0.02      | French & Roll (1986), *Journal of Financial Economics*, 17(1), 5–26 — return reversal rates in equity markets | High: γ = 0.05 → rapid recovery prevents cascade; γ = 0.005 → insufficient recovery    |
| σ         | 0.015 | 0.01–0.03       | Roll (1984), *Journal of Finance*, 39(4), 1127–1139 — bid-ask bounce model noise estimate                     | Low: affects variance of threshold crossing timing, not mean behavior                  |

**Economic Rationale**:
The high λ (0.03) reflects the market-impact amplification typical in concentrated block selling — when a single large seller (ConcentratedFund or a prime broker) submits an order representing 5–10% of daily volume, price impact is significantly larger than normal. The low γ (0.01) models the slow fundamental anchoring characteristic of equity markets over short horizons: prices do not snap back to intrinsic value within rounds. The combination ensures that cascade-induced deviations persist long enough to trigger successive threshold crossings by PrimeBroker1 and PrimeBroker2.

**Dynamic Properties**:
- When D(t) < 0 (ConcentratedFund selling): P falls; deviation increases in magnitude → may cross broker thresholds
- When P << F (deep discount): mean reversion provides slow upward pressure; BlockTradeBuyer activates
- When noise adds random positive demand: cascade may temporarily pause before resuming
- Price floor: `P(t+1) = max(calculated_price, 0.01)` — prevents numerical instability in extreme cascades

### 3.2 Additional Market Mechanisms

**Short-Selling**:
- Trigger: InformationTrader decides to short (quantity < 0 beyond current position)
- Action: Allowed; no explicit cost in this simulation (contrast with AssetBubble which charges short costs)
- Economic Rationale: Information-based short selling accelerates the cascade's early development, as informed traders front-run the anticipated forced selling; the absence of borrowing costs reflects that TRS-driven cascades unfold faster than short-borrow markets can respond
- Source: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335. https://doi.org/10.2307/1913210

**Price Floor**:
- Trigger: Computed P(t+1) < 0.01
- Action: `P(t+1) = max(computed_price, 0.01)`
- Economic Rationale: Prevents prices from reaching zero (the firm still has liquidation value); represents minimum asset recovery value

### 3.3 Information Broadcast Design

Each round, the Market broadcasts to all investors:

| Field         | Type  | Definition                                     | Rationale for Inclusion                                                                                    |
|---------------|-------|------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| `price`       | float | Current market price after order clearing      | Primary signal; all agents monitor price level                                                             |
| `prev_price`  | float | Price from the previous round                  | Enables InformationTrader to detect first signs of decline                                                 |
| `fundamental` | float | Intrinsic fundamental value (constant = 100.0) | Required for deviation calculation and BlockTradeBuyer activation                                          |
| `deviation`   | float | `(price − fundamental) / fundamental`          | Pre-computed; the primary trigger signal for ConcentratedFund, PrimeBroker1, PrimeBroker2, BlockTradeBuyer |
| `round`       | int   | Current round number                           | Enables round-based frequency control if needed                                                            |

**Design Note**: `return_pct` is NOT broadcast separately — agents that need price change compute it from `price` and `prev_price`. The central signal is `deviation` (not raw price level), consistent with how prime brokers monitor collateral quality relative to fair value.


## §4 Investor Taxonomy

### §4.1 ConcentratedFund

#### 4.1.1 Summary

The `ConcentratedFund` represents a highly leveraged family office holding large synthetic equity exposure through Total Return Swaps — modeled directly on Archegos Capital Management's operational structure. This investor is the primary cascade initiator: its forced selling, when triggered by a maintenance margin breach, provides the initial large negative demand shock that drives prices below the prime brokers' liquidation thresholds. Without this agent, no cascade occurs — it is the single necessary precondition for the entire phenomenon. Its distinguishing feature compared to other investors is the combination of (1) extreme position size (the largest holder in the market), (2) leverage-forced selling (no discretion once triggered), and (3) sudden, large-block liquidation that no other agent type exhibits.

#### 4.1.2 Theoretical and Empirical Foundation

**Theory/Study 1: TRS Leverage and Hidden Systemic Concentration**

- Citation: Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1–12. https://doi.org/10.18651/ER/v106n3Becketti
- Core Insight: TRS-structured leverage makes extreme concentration invisible to counterparties until the margin breach. The forced close-out mechanism is binary — below the maintenance margin, no partial adjustment is possible; the entire margined position must be wound down rapidly.
- Mathematical Formulation:
  ```
  equity(t) = initial_equity + (P(t) − P(0)) × position
  margin_breach: equity(t) / (P(t) × position) < maintenance_margin_rate
  ```
- Empirical Evidence: FSB (2022) documented Archegos held $35–40B notional exposure with 5–8x leverage. The maintenance margin was approximately 10–15% of notional, implying a margin call is triggered by a price decline of roughly 10–20% from the initial position price. Liquidation fractions of 50–70% in the first round of margin calls are documented in prime broker operational reports.
- Relevance to This Investor: The trigger threshold `leverage_trigger = 0.15` corresponds to a 15% decline from fundamental (approximating the 10–20% empirical range after adjusting for the leverage ratio). The `liquidation_fraction = 0.50` reflects the 50% first-round liquidation documented in post-event analysis.
- Parameter Calibration: leverage_trigger ∈ [0.10, 0.20]; chosen 0.15 as midpoint of empirical range.

**Theory/Study 2: Overconfidence and Concentration Risk**

- Citation: Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261–292. https://doi.org/10.1162/003355301556400
- Core Insight: Overconfident investors hold more concentrated positions and trade more frequently than optimal. They systematically underestimate risk from their own concentration, believing their information edge justifies the risk — until a forced liquidation event reveals the full extent of their exposure.
- Mathematical Formulation: Overconfident position sizing: `Q_overconf = Q_optimal × (1 + overconf_multiplier)`, where `overconf_multiplier ∝ perceived information advantage`.
- Empirical Evidence: Barber & Odean (2001) document that high-confidence traders earn 3.5% lower annual returns net of trading costs, with higher concentration and larger drawdowns. This is consistent with Archegos's known operating style (concentrated bets, high leverage, information-advantage belief).
- Relevance to This Investor: Models the psychological basis for the ConcentratedFund's extreme position size and reluctance to de-risk earlier. The high initial_position reflects overconfident position sizing.

#### 4.1.3 Design Purpose and Activation Scenarios

**Purpose**: Generate the initial large negative demand shock that triggers the cascade. ConcentratedFund is the necessary first-mover in the cascade chain.

| Market Condition                            | ConcentratedFund Response             | Economic Effect                                                                                             | Theory                                               |
|---------------------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| deviation ≥ −0.15 (normal/moderate decline) | Hold position; no action              | No cascade initiation                                                                                       | §4.1.2 Theory 1: below maintenance margin trigger    |
| deviation < −0.15 (margin breach)           | Forced sell: `position × 0.50` shares | Large negative demand shock (−500–1500 shares); price declines further; deviation crosses broker thresholds | §4.1.2 Theory 1: maintenance margin forced close-out |

**Market Contribution**: Strongly Destabilizing. A single forced sell of 50% of position (typically 1000–2000 shares at position_size 2000–4000) generates net demand of −1000 to −2000, producing a price change of `λ × (−1500) = 0.03 × (−1500) = −$4.50` — approximately a 4.5% price decline in one round.

**Interaction Effects**: Must sell BEFORE PrimeBroker1's threshold (−0.10) is crossed, or the cascade ordering does not replicate the Archegos timing. ConcentratedFund's selling is the sole driver of the first threshold crossing; PrimeBroker1 and PrimeBroker2 only act after ConcentratedFund has moved prices into cascade territory.

#### 4.1.4 Behavioral Framework

##### 4.1.4.1 Decision Information Set

| Signal        | Used?    | Rationale                                                                                                         |
|---------------|----------|-------------------------------------------------------------------------------------------------------------------|
| `deviation`   | Yes      | The primary trigger signal; directly measures the equity loss relative to fundamental, proxying for margin status |
| `price`       | Yes      | Used for portfolio valuation and order pricing                                                                    |
| `fundamental` | Implicit | Used only through `deviation`; ConcentratedFund does not independently compute fundamental analysis               |
| `prev_price`  | No       | Trigger is level-based (deviation threshold), not change-based                                                    |
| `round`       | No       | No frequency control; triggers immediately when margin breached                                                   |

**Information asymmetry note**: ConcentratedFund knows its leverage ratio but is modeled as NOT knowing when other prime brokers will liquidate. This asymmetry — not knowing competitors' thresholds — is historically accurate: Archegos held TRS positions with multiple prime brokers simultaneously, and no single broker had full visibility into the others' exposure.

##### 4.1.4.2 Core Behavioral Mechanism

ConcentratedFund starts the simulation with a very large long equity position funded through TRS leverage. In normal rounds (deviation above −0.15), it holds passively — the leveraged fund has no incentive to trade; it is waiting for the position to appreciate.

When price decline brings deviation below the leverage_trigger threshold (−0.15), this signals a maintenance margin breach. At this point, the fund loses discretion: it must sell to meet margin calls from its prime brokers. The forced close-out is large and abrupt — the fund does not sell gradually; it liquidates a fixed fraction of its position immediately in the triggered round.

The sizing reflects TRS margin call mechanics: the fund does not sell the entire position (which would close out all synthetic exposure), but a substantial fraction sufficient to restore the equity ratio above maintenance margin. In practice, 40–60% of position is sold in the initial margin call response.

ConcentratedFund has no persistent state beyond its current position size. Once it has sold in response to a margin call, it cannot re-enter (no cash available; position reduced). If deviation recovers, the fund simply holds the reduced position.

##### 4.1.4.3 Mathematical Model

**Decision Variable**: Q_sell = forced sell quantity (shares)

**Trigger Function**:
```
Trigger when: δ(t) < −θ_leverage
where δ(t) = (P(t) − F) / F   [deviation from fundamental]
      θ_leverage = leverage_trigger = 0.15  [maintenance margin approximation]
```

**Sizing Function**:
```
Q_sell(t) = position(t) × φ_liquidation
where φ_liquidation = liquidation_fraction = 0.50
Constraint: Q_sell ≤ position(t)   [cannot sell more than held]
Result: action = "sell", quantity = Q_sell
```

**State Variables**:
| Variable | Type  | Initial Value | Update Rule                         | Economic Meaning                          |
|----------|-------|---------------|-------------------------------------|-------------------------------------------|
| position | int   | 2000 shares   | position -= Q_sell each sell round  | Remaining synthetic long exposure         |
| cash     | float | 10000.0       | cash += Q_sell × price when selling | Available cash (small; fund is leveraged) |

**Parameter Definitions**:
| Symbol        | Plain-Language Meaning                     | Config Path                 | Value | Source                                     |
|---------------|--------------------------------------------|-----------------------------|-------|--------------------------------------------|
| θ_leverage    | Deviation threshold triggering margin call | extras.leverage_trigger     | 0.15  | Becketti (2021); FSB (2022)                |
| φ_liquidation | Fraction of position sold at margin call   | extras.liquidation_fraction | 0.50  | Archegos post-mortem; prime broker reports |

**Model Limitations**: The model uses a single static threshold for the margin call, whereas real TRS agreements use dynamic margin schedules (margin increases as losses deepen). This simplification is consistent with agent-based modeling conventions (LeBaron, 2006; *Handbook of Computational Economics*, Vol. 2).

##### 4.1.4.4 Behavioral Properties

| Property               | Value                                                                                                | Rationale                                                                             |
|------------------------|------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Time Horizon           | Position trader (months), forced to liquidate instantly                                              | TRS positions are designed for medium-term holding; forced close-out is instantaneous |
| Risk Tolerance         | Extreme (leverage ratio 5–8x)                                                                        | Empirically documented in FSB (2022); Archegos operational profile                    |
| Decision Frequency     | Condition-triggered only (not every round)                                                           | Only acts when leverage_trigger is crossed; holds in all other rounds                 |
| Information Processing | Partially rational (holds based on information edge belief); forced action ignores market conditions | Barber & Odean (2001) overconfidence model                                            |
| Psychological Profile  | Overconfident in position; denial-resistant to early signs of loss; abrupt capitulation at threshold | Archegos post-mortem accounts; Barber & Odean (2001)                                  |

#### 4.1.5 Decision Process Walkthrough

**Example Market State**:
- Round: 12
- Price: 84.5 — declining from initial 100.0
- Fundamental: 100.0
- Deviation: (84.5 − 100.0) / 100.0 = −0.155 — BELOW the −0.15 trigger
- Position: 2000 shares
- Cash: 10,000

**Decision Trace**:

Step 1 — Perception:
  ConcentratedFund observes deviation = −0.155.
  This is below the leverage_trigger threshold of −0.15.
  In real terms: the TRS mark-to-market loss on 2000 shares × ($100 − $84.50) = $31,000 has depleted the margin account.

Step 2 — Trigger Check:
  Check: −0.155 < −0.15? → YES
  Margin call triggered. The prime broker demands immediate collateral posting or position close-out.

Step 3 — Sizing:
  Q_sell = position × liquidation_fraction = 2000 × 0.50 = 1000 shares
  Constraint: Q_sell = 1000 ≤ position = 2000 ✓

Step 4 — Action:
  Decision: action = "sell", quantity = 1000, bid_price = 84.5 (market order at current price)

Step 5 — Market Impact:
  This order contributes −1000 to net demand D(t).
  Price effect: ΔP ≈ λ × (−1000) = 0.03 × (−1000) = −$30.00
  New price (before mean reversion and noise): P ≈ 84.5 − 30 = ~54.5
  New deviation: (54.5 − 100) / 100 = −0.455 → well below PrimeBroker1 threshold (−0.10)

#### 4.1.6 Worked Numerical Example

**Inputs**:
| Variable                 | Value       |
|--------------------------|-------------|
| P(t)                     | 84.5        |
| F                        | 100.0       |
| δ(t) = (84.5−100)/100    | −0.155      |
| position                 | 2000 shares |
| cash                     | $10,000     |
| leverage_trigger (θ)     | 0.15        |
| liquidation_fraction (φ) | 0.50        |

**Calculation**:
```
Step 1: Check trigger: δ = −0.155 < −θ = −0.15 → True
Step 2: Q_sell = 2000 × 0.50 = 1000 shares
Step 3: Constraint: 1000 ≤ 2000 ✓
Step 4: Submit order: sell 1000 shares at $84.50
```

**Expected Market Impact** (assuming no other orders this round):
```
D(t) = 0 − 1000 = −1000 (only this order)
ΔP_demand = λ × D = 0.03 × (−1000) = −$30.00
ΔP_mean_rev = γ × (F − P) = 0.01 × (100 − 84.5) = +$0.155
ΔP_noise ≈ 0 (expected value)
P(t+1) ≈ 84.5 − 30.0 + 0.155 = $54.66
New deviation ≈ (54.66 − 100) / 100 = −0.453
```
This −45.3% deviation far exceeds both PrimeBroker thresholds (−0.10, −0.15), triggering the cascade in the following rounds.

#### 4.1.7 Academic References

| # | Full Citation                                                                                                                                                                                                      | Contribution                                                             |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1–12. https://doi.org/10.18651/ER/v106n3Becketti                                | TRS leverage mechanics; margin call thresholds; liquidation fractions    |
| 2 | Financial Stability Board. (2022). *Non-bank Financial Intermediation: Global Monitoring Report 2022*, pp. 47–54. https://www.fsb.org/2022/12/global-monitoring-report-on-non-bank-financial-intermediation-2022/  | Empirical leverage ratios and concentration data for Archegos-type funds |
| 3 | Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261–292. https://doi.org/10.1162/003355301556400              | Overconfidence as basis for extreme position sizing and concentration    |
| 4 | LeBaron, B. (2006). Agent-based computational finance. In L. Tesfatsion & K. L. Judd (Eds.), *Handbook of Computational Economics*, Vol. 2, pp. 1187–1233. Elsevier. https://doi.org/10.1016/S1574-0021(05)02024-1 | Justification for single-threshold margin call simplification            |

---

### §4.2 PrimeBroker1

#### 4.2.1 Summary

`PrimeBroker1` represents the first-acting prime broker — the counterparty that liquidates ahead of competitors, obtaining better prices. In the Archegos event, Morgan Stanley acted earliest (March 25–26) among the major prime brokers. PrimeBroker1 models the financially rational response to a creditor run: first-mover advantage means acting at threshold −0.10 (a less severe decline) rather than waiting for the more conservative threshold. This investor is the second link in the cascade chain: its large sell order, coming at prices still above PrimeBroker2's eventual selling price, amplifies the initial ConcentratedFund shock and pushes prices toward PrimeBroker2's trigger.

#### 4.2.2 Theoretical and Empirical Foundation

**Theory/Study 1: Creditor Run and First-Mover Advantage**

- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: The first creditor to liquidate collateral captures the highest price (before mass liquidation depresses value). This creates a dominant strategy equilibrium: all creditors prefer to liquidate first, producing a coordination failure that amplifies the borrower's distress into a system-wide run.
- Mathematical Formulation: First-mover payoff premium = `Q × [P(t₁) − P(t₂)] = Q × λ × Q₁ > 0`, where Q₁ is first-mover sell volume and t₂ > t₁. This premium is always positive, making early liquidation dominant regardless of Q₁.
- Empirical Evidence: Gorton & Metrick (2012) document that repo creditors begin running when haircuts rise above 5–10%, well before borrower insolvency. In Archegos, Morgan Stanley's early action allowed it to limit losses to ~$1B versus Credit Suisse's $5.5B (Financial Times, April 2021 analysis).
- Relevance to This Investor: PrimeBroker1's threshold (−0.10) is set lower than PrimeBroker2's (−0.15) to capture the first-mover decision: it accepts acting at moderate distress rather than waiting for confirmed crisis.
- Parameter Calibration: liquidation_threshold = 0.10 reflects the 10% decline that typically prompts prime broker risk committees to initiate forced close-out; liquidation_fraction = 0.40 (slightly less than ConcentratedFund) reflects broker position size constraints.

**Theory/Study 2: Risk-Averse Institutional Decision-Making Under Uncertainty**

- Citation: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185
- Core Insight: Loss aversion causes decision-makers to weight potential losses more heavily than equivalent gains. Institutional risk managers exhibit strong loss aversion: a 15% recovery in prices is valued far less than avoiding an additional 15% decline. This asymmetry explains why prime brokers act decisively to cut losses rather than waiting for recovery.
- Mathematical Formulation: Loss aversion utility: `U(x) = x^α for x > 0; −λ × (−x)^β for x < 0`, with λ ≈ 2.25, α = β ≈ 0.88 (Tversky & Kahneman, 1992).
- Empirical Evidence: Loss aversion coefficient λ ≈ 2.25 is documented across multiple experimental studies (Tversky & Kahneman, 1992, *Journal of Risk and Uncertainty*, 5(4), 297–323). In institutional settings, risk management guidelines typically enforce stop-loss rules at 10–15% loss thresholds.
- Relevance to This Investor: The low threshold (−0.10) reflects institutional risk management stop-loss rules grounded in loss aversion; PrimeBroker1 would rather realize a certain 10% loss than risk a worse outcome by waiting.

#### 4.2.3 Design Purpose and Activation Scenarios

**Purpose**: Amplify the initial ConcentratedFund shock by adding a second large sell order at relatively good prices, driving prices further down toward PrimeBroker2's trigger.

| Market Condition                       | PrimeBroker1 Response   | Economic Effect                                                              | Theory                                           |
|----------------------------------------|-------------------------|------------------------------------------------------------------------------|--------------------------------------------------|
| deviation ≥ −0.10                      | Hold; monitoring        | No amplification; creditor run has not started                               | §4.2.2 below risk threshold                      |
| deviation < −0.10 (first-mover window) | Sell: `position × 0.40` | Second large sell order at moderate price; pushes deviation well below −0.15 | §4.2.2 Theory 1: first-mover advantage dominates |

**Market Contribution**: Strongly Destabilizing. PrimeBroker1's 0.40 × position sell order (typically 400–800 shares) adds −400 to −800 net demand. Combined with ConcentratedFund's prior selling, this depresses prices into PrimeBroker2's threshold range.

**Interaction Effects**: PrimeBroker1 acts AFTER ConcentratedFund's selling (which creates the −0.10 deviation crossing) but BEFORE PrimeBroker2 (whose threshold is −0.15). PrimeBroker1 and ConcentratedFund are the key cascade initiators; PrimeBroker2 deepens the trough.

#### 4.2.4 Behavioral Framework

##### 4.2.4.1 Decision Information Set

| Signal        | Used?    | Rationale                                                                                  |
|---------------|----------|--------------------------------------------------------------------------------------------|
| `deviation`   | Yes      | Primary risk signal: monitors loss relative to fundamental as margin quality proxy         |
| `price`       | Yes      | Used for order pricing                                                                     |
| `prev_price`  | No       | Threshold-based decision, not change-based                                                 |
| `fundamental` | Implicit | Via deviation only; PrimeBroker1 monitors counterparty collateral quality, not asset value |

##### 4.2.4.2 Core Behavioral Mechanism

PrimeBroker1 is the institutional risk manager who decided to act early rather than risk a worse outcome from waiting. In normal rounds (deviation above −0.10), it holds its collateral and monitors. Once deviation crosses −0.10, its risk management protocol triggers an automatic liquidation order.

The sell size (40% of position) is chosen to significantly reduce exposure in one action while not creating a catastrophic position mismatch. The prime broker's position is held as collateral against the fund's TRS exposure — it is not a directional bet, but a risk management tool.

After selling, PrimeBroker1 does not re-enter; its holding represents collateral that has been liquidated to close the TRS contracts.

##### 4.2.4.3 Mathematical Model

**Trigger Function**:
```
Trigger when: δ(t) < −θ₁  where θ₁ = liquidation_threshold = 0.10
```

**Sizing Function**:
```
Q_sell = position(t) × φ₁  where φ₁ = liquidation_fraction = 0.40
Constraint: Q_sell ≤ position(t)
```

**Parameter Definitions**:
| Symbol | Meaning                              | Config Path                  | Value | Source                                                            |
|--------|--------------------------------------|------------------------------|-------|-------------------------------------------------------------------|
| θ₁     | First-mover liquidation threshold    | extras.liquidation_threshold | 0.10  | Gorton & Metrick (2012); prime broker risk management conventions |
| φ₁     | Fraction of collateral position sold | extras.liquidation_fraction  | 0.40  | Standard prime broker collateral liquidation protocol             |

#### 4.2.5 Decision Process Walkthrough

**Example Market State** (round after ConcentratedFund sells):
- Price: 54.7 (after ConcentratedFund's selling)
- Fundamental: 100.0
- Deviation: (54.7 − 100) / 100 = −0.453 — well below −0.10 threshold
- Position: 1000 shares (collateral held against ConcentratedFund TRS)

Step 1: Observe δ = −0.453 < −0.10 → trigger
Step 2: Q_sell = 1000 × 0.40 = 400 shares
Step 3: Submit order: sell 400 shares at $54.70
Step 4: Market impact: ΔP ≈ 0.03 × (−400) = −$12.00; New P ≈ $42.70; New δ ≈ −0.573

#### 4.2.6 Worked Numerical Example

```
P(t) = 54.7, δ = −0.453, position = 1000, θ₁ = 0.10, φ₁ = 0.40
Step 1: −0.453 < −0.10 → True
Step 2: Q_sell = 1000 × 0.40 = 400 shares
Step 3: Sell 400 @ $54.70
Market impact: D = −400; ΔP_demand = 0.03 × (−400) = −$12.00
P(t+1) ≈ 54.7 − 12.0 + 0.01×(100−54.7) = 54.7 − 12.0 + 0.453 = $43.15
δ(t+1) ≈ (43.15 − 100) / 100 = −0.569
```
This deepens deviation well beyond PrimeBroker2's threshold (−0.15), ensuring cascade continuation.

#### 4.2.7 Academic References

| # | Full Citation                                                                                                                                                                                   | Contribution                                            |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016                     | Creditor run theory; first-mover liquidation advantage  |
| 2 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185                                        | Loss aversion basis for early risk management threshold |
| 3 | Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. https://doi.org/10.1007/BF00122574 | Quantitative loss aversion coefficient λ ≈ 2.25         |

---

### §4.3 PrimeBroker2

#### 4.3.1 Summary

`PrimeBroker2` represents the second-acting prime broker — the counterparty who acted later and received worse prices. In the Archegos event, Credit Suisse and Nomura delayed action (March 29), incurring losses of $5.5B and $2.9B respectively versus Morgan Stanley's ~$1B. PrimeBroker2 models the cost of second-mover disadvantage in a creditor cascade: it has a higher threshold (−0.15) reflecting greater loss tolerance or slower risk management processes, but this conservatism backfires — by the time it acts, prices have already been depressed by ConcentratedFund and PrimeBroker1, and its sell orders occur at substantially worse prices.

#### 4.3.2 Theoretical and Empirical Foundation

**Theory/Study 1: Second-Mover Disadvantage in Creditor Runs**

- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: In a creditor run, later-moving creditors face a coordination disadvantage: earlier liquidators have already depressed collateral prices, reducing the recovery value of later liquidations. The second mover's payoff is `Q × P(t₂) = Q × [P(t₁) − λ × Q₁]`, which is strictly less than the first mover's payoff for any positive first-mover sell volume Q₁.
- Mathematical Formulation: `PnL_loss(second mover) = Q₂ × λ × Q₁` — the loss from late action is proportional to first mover's volume times price impact.
- Empirical Evidence: Credit Suisse's $5.5B loss vs. Morgan Stanley's ~$1B loss in the Archegos event is consistent with a 3–5x penalty for delayed action when $35B in positions were being simultaneously unwound (Financial Times, April 6, 2021).
- Relevance to This Investor: PrimeBroker2's higher threshold (−0.15) vs PrimeBroker1 (−0.10) models the delayed reaction. The price at which PrimeBroker2 sells is already depressed by both ConcentratedFund's and PrimeBroker1's selling, replicating the empirical payoff differential.
- Parameter Calibration: liquidation_threshold = 0.15 (vs PrimeBroker1's 0.10); the 0.05 differential represents a 5% additional loss tolerance before action.

**Theory/Study 2: Institutional Inertia and Slow Risk Management Response**

- Citation: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Core Insight: The disposition effect — the tendency to hold losers too long — is documented in both individual and institutional investors. Risk managers at slower-acting institutions may exhibit disposition-like reluctance to crystallize losses, delaying forced selling beyond the risk-optimal threshold.
- Mathematical Formulation: Disposition-adjusted threshold: `θ₂_effective = θ₂_optimal × (1 + d)`, where `d > 0` is the disposition effect delay factor.
- Empirical Evidence: Shefrin & Statman (1985) document the disposition effect across multiple asset classes; institutional manifestations include delayed margin call enforcement documented in post-crisis analyses.
- Relevance to This Investor: The higher threshold (−0.15 vs PrimeBroker1's −0.10) models institutional hesitation and slower response, even at greater financial cost.

#### 4.3.3 Design Purpose and Activation Scenarios

**Purpose**: Deepen the cascade trough by selling at worse prices than PrimeBroker1, completing the wave of prime broker liquidations and driving prices to their minimum before recovery.

| Market Condition  | PrimeBroker2 Response                            | Economic Effect                                                                    | Theory                                     |
|-------------------|--------------------------------------------------|------------------------------------------------------------------------------------|--------------------------------------------|
| deviation ≥ −0.15 | Hold (monitors situation)                        | Cascade not yet reached PrimeBroker2's trigger                                     | Second-mover waiting strategy              |
| deviation < −0.15 | Sell: `position × 0.35` (accepting worse prices) | Third large sell order at deeply discounted prices; pushes price to cascade trough | §4.3.2 Theory 1: second-mover disadvantage |

**Market Contribution**: Strongly Destabilizing. Deepens the cascade trough. Sells at prices 30–50% below initial levels (after ConcentratedFund and PrimeBroker1 have already sold), realizing the worst outcomes of the three liquidating agents.

#### 4.3.4 Behavioral Framework

##### 4.3.4.1 Mathematical Model

**Trigger Function**:
```
Trigger when: δ(t) < −θ₂  where θ₂ = 0.15
```

**Sizing Function**:
```
Q_sell = position(t) × φ₂  where φ₂ = 0.35 (slightly smaller than PrimeBroker1's 0.40 — accepts partial liquidation)
Constraint: Q_sell ≤ position(t)
```

PrimeBroker2 accepts a price penalty representing the worse execution prices from delayed action. In the model, this is captured naturally through the price dynamics — by the time PrimeBroker2 triggers, prices are already significantly lower.

#### 4.3.5 Decision Process Walkthrough

After PrimeBroker1's selling:
- Price: ~43.2 (from worked example above)
- Deviation: −0.568 — far below both thresholds
- PrimeBroker2 triggers immediately in the same or next round

Q_sell = position × 0.35 = 1000 × 0.35 = 350 shares at ~$43.20
Market impact: ΔP ≈ 0.03 × (−350) = −$10.50; P drops to ~$32.70
This represents a 67% decline from initial $100 — consistent with Archegos-scale events (ViacomCBS fell 60%).

#### 4.3.6 Worked Numerical Example

```
P(t) = 43.15, δ = −0.569, position = 1000, θ₂ = 0.15, φ₂ = 0.35
Step 1: −0.569 < −0.15 → True (triggered immediately after PrimeBroker1)
Step 2: Q_sell = 1000 × 0.35 = 350 shares
Step 3: Sell 350 @ $43.15
Market impact: ΔP ≈ 0.03 × (−350) = −$10.50
P(t+1) ≈ 43.15 − 10.50 + 0.01×(100−43.15) = 43.15 − 10.50 + 0.569 = $33.22
δ(t+1) ≈ −0.668  → minimum cascade point; triggers BlockTradeBuyer
```

#### 4.3.7 Academic References

| # | Full Citation                                                                                                                                                                                   | Contribution                                              |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| 1 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016                     | Second-mover payoff disadvantage; cascade amplification   |
| 2 | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x | Institutional hesitation and delayed loss crystallization |

---

### §4.4 BlockTradeBuyer

#### 4.4.1 Summary

`BlockTradeBuyer` represents the opportunistic institutional buyer who absorbs forced supply at fire-sale discounts. In the Archegos event, several hedge funds and asset managers purchased blocks of ViacomCBS and Discovery at 50–60% discounts from peak prices. This investor is the primary stabilizing force: once prices fall far enough below fundamental value (beyond the discount_threshold), it deploys cash to buy. Its presence creates a price floor — without it, prices could cascade to near-zero in extreme scenarios. BlockTradeBuyer is distinguished by large cash reserves, patient capital, and willingness to absorb illiquid supply when others are forced to sell.

#### 4.4.2 Theoretical and Empirical Foundation

**Theory/Study 1: Block Trading and Liquidity Provision in Stressed Markets**

- Citation: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617–637. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x
- Core Insight: Block trade buyers provide liquidity by holding inventory at a discount. They only absorb supply when prices are low enough to compensate for the risk of further price decline (inventory risk). The minimum discount required equals the expected holding cost plus a risk premium for uncertainty about when prices will recover.
- Mathematical Formulation: `Activation condition: (F − P(t)) / F > discount_threshold`, equivalent to `deviation(t) < −discount_threshold`. `Purchase quantity: Q_buy = α × cash / P(t)` where α is the capital deployment fraction.
- Empirical Evidence: Grossman & Miller (1988) estimate normal block trade discounts of 1.5–3.0%. In distressed markets, block trade discounts of 5–15% are documented (Mitchell & Pulvino, 2012, *Review of Financial Studies*, 25(7), 2235–2274). The 10% threshold (discount_threshold = 0.10) is calibrated to this distressed range.
- Relevance to This Investor: BlockTradeBuyer's 10% discount threshold models institutional buyers who require compensation for holding risk during the Archegos-scale cascade.
- Parameter Calibration: discount_threshold = 0.10; cash_deployment = 0.30 (30% of available cash per activation round).

**Theory/Study 2: Value Investing and Margin of Safety**

- Citation: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. (Revised edition 2006, Collins Business.)
- Core Insight: Value investors require a "margin of safety" — a sufficient discount to fundamental value — before committing capital. This provides protection against estimation error and further price decline. The margin of safety principle produces natural price-floor behavior: value capital is deployed when discounts exceed the safety threshold.
- Empirical Evidence: Academic research on value investing documents that deep-value purchases (at discounts of 30%+ to book value or intrinsic value) have historically generated 5–10% annual alpha (Lakonishok, Shleifer & Vishny, 1994, *Journal of Finance*, 49(5), 1541–1578), consistent with the block trade buying strategy.
- Relevance to This Investor: BlockTradeBuyer's activation at −10% deviation represents a conservative margin of safety, deployed by patient capital willing to accept short-term mark-to-market losses in exchange for long-term value recovery.

#### 4.4.3 Design Purpose and Activation Scenarios

**Purpose**: Provide a price floor that eventually halts the cascade and begins the recovery phase.

| Market Condition  | BlockTradeBuyer Response          | Economic Effect                                                              | Theory                                           |
|-------------------|-----------------------------------|------------------------------------------------------------------------------|--------------------------------------------------|
| deviation ≥ −0.10 | Hold; no action                   | No stabilization needed at normal prices                                     | Below discount threshold                         |
| deviation < −0.10 | Buy: `0.30 × cash / price` shares | Positive demand shock; partially offsets broker selling; creates price floor | §4.4.2 Theory 1: block trade liquidity provision |

**Market Contribution**: Stabilizing. Provides positive demand offset during and after cascade. The recovery phase begins when BlockTradeBuyer's purchases (combined with mean reversion) exceed the remaining selling pressure from brokers.

#### 4.4.4 Behavioral Framework

##### 4.4.4.1 Mathematical Model

**Trigger Function**:
```
Trigger when: δ(t) < −θ_discount   where θ_discount = 0.10
```

**Sizing Function**:
```
Q_buy = floor(α × cash / P(t))
where α = cash_deployment = 0.30
Constraint: Q_buy × P(t) ≤ cash   [cannot spend more than available]
```

**State Variables**:
| Variable | Type  | Update Rule                         |
|----------|-------|-------------------------------------|
| cash     | float | cash -= Q_buy × P(t) each buy round |
| position | int   | position += Q_buy each buy round    |

#### 4.4.5 Decision Process Walkthrough

At cascade trough (price ≈ $33, deviation ≈ −0.67):
- BlockTradeBuyer observes deviation = −0.67 < −0.10 → trigger
- Q_buy = floor(0.30 × 100,000 / 33.0) = floor(909) = 909 shares
- Submit: buy 909 shares at $33.00
- Market impact: ΔP ≈ 0.03 × 909 = +$27.27; P rises toward $60.27
- Cascade begins to reverse as BlockTradeBuyer continues buying in subsequent rounds

#### 4.4.6 Worked Numerical Example

```
P(t) = 33.20, δ = −0.668, cash = 100,000, α = 0.30, θ = 0.10
Step 1: −0.668 < −0.10 → True
Step 2: Q_buy = floor(0.30 × 100,000 / 33.20) = floor(30,000 / 33.20) = 903 shares
Step 3: Buy 903 @ $33.20; cash → 100,000 − 903×33.20 = $70,020
Market impact: ΔP ≈ 0.03 × 903 = $27.09; P(t+1) ≈ 33.20 + 27.09 + 0.668 = $60.96
Recovery begins.
```

#### 4.4.7 Academic References

| # | Full Citation                                                                                                                                                                                    | Contribution                                                         |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| 1 | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617–637. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x                                | Block trade discount threshold; liquidity provision mechanism        |
| 2 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers (rev. ed. 2006, Collins Business).                                                                                              | Margin of safety principle; value buyer activation at deep discounts |
| 3 | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | Empirical returns to deep-value block buying strategy                |

---

### §4.5 InformationTrader

#### 4.5.1 Summary

`InformationTrader` represents informed short sellers who detect the onset of forced institutional selling — front-runners who pick up signals of impending cascade and establish short positions before the main wave. In the Archegos event, several well-positioned traders reportedly detected unusual block trade flows and large single-name option activity before the public cascade began. This investor adds early price pressure at moderate deviations, contributing to cascade speed but also covering short positions and providing buying support when the cascade reverses. It is the most sophisticated participant in the simulation.

#### 4.5.2 Theoretical and Empirical Foundation

**Theory/Study 1: Information-Based Trading and Price Discovery**

- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335. https://doi.org/10.2307/1913210
- Core Insight: Informed traders with private information strategically trade to extract profits while hiding their information from market makers. Their trading accelerates price discovery — prices move toward true value faster than with uninformed trading alone. In the context of liquidation cascades, informed traders front-run anticipated forced selling.
- Mathematical Formulation: Kyle's lambda (λ_kyle) measures price impact per unit of informed order flow: `ΔP = λ_kyle × (informed_order + noise_order)`. Informed traders size their orders to maximize expected profit given price impact: `Q_opt = (V − P) / (2 × λ_kyle)`, where V is the informed trader's private value estimate.
- Empirical Evidence: Empirical estimates of Kyle's lambda for individual stocks range from 0.01–0.05 per unit of normalized order flow (Glosten & Harris, 1988, *Journal of Finance*, 43(1), 123–142). Information traders in distressed scenarios appear to act on signals 2–5 rounds before public events materialize.
- Relevance to This Investor: InformationTrader acts at deviation = −0.05 (earlier than any other agent), reflecting early detection of cascade signals. The `detection_ability = 0.50` models partial information — it only detects the signal 50% of the time, consistent with the noisy nature of pre-cascade information.
- Parameter Calibration: detection_threshold = 0.05; detection_ability = 0.50 (coin-flip detection rate reflecting noisy signals).

**Theory/Study 2: Short Selling and Market Efficiency**

- Citation: Boehmer, E., Jones, C. M., & Zhang, X. (2008). Which shorts are informed? *Journal of Finance*, 63(2), 491–527. https://doi.org/10.1111/j.1540-6261.2008.01324.x
- Core Insight: Institutional short sellers are significantly more informed than retail short sellers. Stocks with high institutional short interest subsequently underperform by 1–2% per month, confirming that informed shorting accelerates price adjustment toward fundamental value.
- Empirical Evidence: Boehmer et al. (2008) find that institutional short sellers earn 20-day raw returns of −9.4% on their short positions (mean), consistent with exploiting anticipated price declines of 5–15%.
- Relevance to This Investor: InformationTrader's front-running behavior and short covering represent the empirically documented institutional short-selling cycle: establish short ahead of cascade, cover on stabilization.

#### 4.5.3 Design Purpose and Activation Scenarios

**Purpose**: Provide early downward price pressure, accelerating cascade onset, then provide stabilizing buying when short positions are covered during recovery.

| Market Condition                            | InformationTrader Response                       | Economic Effect                                                             | Theory                                        |
|---------------------------------------------|--------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------|
| deviation < −0.05 AND random() < 0.50       | Short (sell): up to `min(1000, position)` shares | Adds to early downward pressure; accelerates threshold crossing             | §4.5.2 Theory 1: front-running informed trade |
| deviation > −0.03 AND short position exists | Buy to cover: up to 200 shares                   | Positive demand shock during recovery; partially offsets long recovery time | Short covering creates buying pressure        |
| All other conditions                        | Hold                                             | Neutral impact                                                              | No signal                                     |

**Market Contribution**: Neutral to Amplifying early; Stabilizing on recovery. Net effect on cascade depth is approximately neutral: short establishment amplifies the decline, but short covering amplifies the recovery.

#### 4.5.4 Behavioral Framework

##### 4.5.4.1 Mathematical Model

**Short Entry Trigger**:
```
Trigger when: δ(t) < −θ_detect  AND  U(0,1) < p_detect
where θ_detect = 0.05, p_detect = 0.50
Q_sell = min(front_run_size, position(t))  where front_run_size = 1000
```

**Short Cover Trigger**:
```
Trigger when: δ(t) > −θ_recovery  AND  short_position(t) > 0
where θ_recovery = 0.03
Q_buy = min(200, short_position)
```

**State Variables**:
| Variable       | Update Rule                                   |
|----------------|-----------------------------------------------|
| short_position | increments on each short; decrements on cover |

#### 4.5.5 Decision Process Walkthrough

Early cascade detection (round 3–5):
- deviation = −0.07 (below detection threshold of −0.05)
- random() = 0.38 < 0.50 → signal detected
- Q_sell = min(1000, position) = min(1000, 2000) = 1000 shares
- Submit: sell 1000 @ current price → accelerates cascade onset

Recovery phase:
- deviation rises to −0.025 (above −0.03 recovery threshold)
- short_position > 0 → cover
- Q_buy = min(200, short_position) → adds positive demand during recovery

#### 4.5.6 Worked Numerical Example

```
Round 4: P = 95.0, δ = −0.05, position = 2000, p_detect = 0.50
Trigger: −0.05 < −0.05 (border case; use strict <) → use δ = −0.06 for illustration
random() = 0.42 < 0.50 → detect
Q_sell = min(1000, 2000) = 1000 shares
Sell 1000 @ $95.00
ΔP ≈ 0.03 × (−1000) = −$30; P → $65.00 (before mean reversion)
This accelerates the cascade by pushing price below PrimeBroker1 threshold sooner.
```

#### 4.5.7 Academic References

| # | Full Citation                                                                                                                                                                     | Contribution                                                     |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| 1 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335. https://doi.org/10.2307/1913210                                                    | Information-based trading theory; front-running model            |
| 2 | Boehmer, E., Jones, C. M., & Zhang, X. (2008). Which shorts are informed? *Journal of Finance*, 63(2), 491–527. https://doi.org/10.1111/j.1540-6261.2008.01324.x                  | Empirical evidence for institutional short selling effectiveness |
| 3 | Glosten, L. R., & Harris, L. E. (1988). Estimating the components of the bid/ask spread. *Journal of Finance*, 43(1), 123–142. https://doi.org/10.1111/j.1540-6261.1988.tb02591.x | Kyle lambda empirical estimates for individual stocks            |


## §5 Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                                                                                                                                                |
|----------------------------------|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | ConcentratedFund: medium-term position holder (months); PrimeBrokers: immediate responders (same round as threshold); BlockTradeBuyer: patient capital (holds for recovery); InformationTrader: high-frequency (front-runs then covers) |
| Different information processing | Yes  | ConcentratedFund: level-threshold (absolute loss); PrimeBroker1/2: level-threshold at different levels; BlockTradeBuyer: discount-seeking; InformationTrader: stochastic detection with probability                                     |
| Conflicting incentives           | Yes  | BlockTradeBuyer BUYS when all three liquidating agents are SELLING; InformationTrader COVERS when all forced sellers are exhausted                                                                                                      |
| Mix of stabilizing/destabilizing | Yes  | 3 destabilizing (ConcentratedFund, PrimeBroker1, PrimeBroker2), 1 stabilizing (BlockTradeBuyer), 1 neutral-then-stabilizing (InformationTrader)                                                                                         |
| Different risk tolerances        | Yes  | ConcentratedFund: Extreme (5–8x leverage); BlockTradeBuyer: High (willingness to buy distressed assets); InformationTrader: Medium; PrimeBroker1: Low (early stop-loss); PrimeBroker2: Low-Medium (delayed stop-loss)                   |
| Different decision frequencies   | Yes  | ConcentratedFund: once (triggered once typically); PrimeBroker1: once at −10%; PrimeBroker2: once at −15%; BlockTradeBuyer: every round below −10%; InformationTrader: every round with stochastic detection                            |

**Critical mass check**: The cascade requires: (1) ConcentratedFund to initiate, (2) at least one broker to amplify, (3) BlockTradeBuyer to eventually halt the decline. Removing ConcentratedFund → no cascade (no initiator). Removing BlockTradeBuyer → prices may collapse to floor without recovery. The 2-broker asymmetry (different thresholds) is essential to model the timing spread observed in Archegos.


## §6 Parameter Table

| Parameter                   | Symbol | Value | Typical Range | Source Citation                                                                                                                                                                               | Description                                 | Sensitivity                                                 |
|-----------------------------|--------|-------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|-------------------------------------------------------------|
| initial_price               | P(0)   | 100.0 | —             | Normalization                                                                                                                                                                                 | Starting stock price                        | Low — scale only                                            |
| fundamental_value           | F      | 100.0 | —             | Normalization                                                                                                                                                                                 | Intrinsic fair value                        | Medium — determines deviation scale                         |
| price_impact                | λ      | 0.03  | 0.01–0.05     | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179–207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x                             | Price change per unit net demand            | High — λ=0.05 → 67% deeper cascade                          |
| mean_reversion              | γ      | 0.01  | 0.005–0.02    | French, K. R., & Roll, R. (1986). Stock return variances. *Journal of Financial Economics*, 17(1), 5–26. https://doi.org/10.1016/0304-405X(86)90004-8                                         | Pull strength toward fundamental value      | High — γ=0.05 → too-fast recovery                           |
| noise_std                   | σ      | 0.015 | 0.01–0.03     | Roll, R. (1984). A simple implicit measure of the effective bid-ask spread in an efficient market. *Journal of Finance*, 39(4), 1127–1139. https://doi.org/10.1111/j.1540-6261.1984.tb03897.x | Noise term standard deviation               | Low — affects timing variance only                          |
| leverage_trigger            | θ_lev  | 0.15  | 0.10–0.20     | Becketti (2021); FSB (2022) non-bank intermediation report                                                                                                                                    | ConcentratedFund margin call threshold      | High — controls when cascade begins                         |
| liquidation_fraction (CF)   | φ_CF   | 0.50  | 0.40–0.70     | Archegos Capital Management post-mortem; FSB (2022), p. 51                                                                                                                                    | Fraction of CF position sold at margin call | High — determines initial shock magnitude                   |
| liquidation_threshold (PB1) | θ₁     | 0.10  | 0.08–0.15     | Gorton & Metrick (2012); prime broker risk management conventions                                                                                                                             | PrimeBroker1 stop-loss threshold            | High — controls first-mover timing                          |
| liquidation_fraction (PB1)  | φ₁     | 0.40  | 0.30–0.50     | Standard prime broker protocol                                                                                                                                                                | PrimeBroker1 sell fraction                  | Medium                                                      |
| liquidation_threshold (PB2) | θ₂     | 0.15  | 0.12–0.20     | Gorton & Metrick (2012); Credit Suisse post-mortem accounts                                                                                                                                   | PrimeBroker2 stop-loss threshold            | High — controls second-mover timing and payoff differential |
| liquidation_fraction (PB2)  | φ₂     | 0.35  | 0.25–0.45     | Standard protocol                                                                                                                                                                             | PrimeBroker2 sell fraction                  | Medium                                                      |
| discount_threshold (BT)     | θ_disc | 0.10  | 0.05–0.15     | Grossman & Miller (1988), distressed market estimate                                                                                                                                          | BlockTradeBuyer activation discount         | Medium — determines price floor level                       |
| cash_deployment (BT)        | α      | 0.30  | 0.20–0.40     | Conservative institutional capital deployment standard                                                                                                                                        | Fraction of cash deployed per activation    | Medium                                                      |
| detection_threshold (IT)    | θ_det  | 0.05  | 0.03–0.08     | Kyle (1985) informed trading model                                                                                                                                                            | InformationTrader early signal threshold    | Medium — controls cascade acceleration                      |
| detection_ability (IT)      | p_det  | 0.50  | 0.30–0.70     | Boehmer et al. (2008) informed short seller frequency                                                                                                                                         | Probability of detecting cascade signal     | Low — affects variance of onset timing                      |


## §7 Communication and Round Structure

```
Round N (t = 1, 2, ..., 200):

  Phase 1 — Market Broadcast:
    Market → all 5 investor instances: {price, prev_price, fundamental, deviation, round}
    All agents receive identical public information simultaneously.

  Phase 2 — Investor Decisions:
    ConcentratedFund: perceive() → check δ < −0.15 → act (sell if triggered)
    PrimeBroker1:     perceive() → check δ < −0.10 → act (sell if triggered)
    PrimeBroker2:     perceive() → check δ < −0.15 → act (sell if triggered, typically rounds after CF)
    BlockTradeBuyer:  perceive() → check δ < −0.10 → act (buy if triggered and cash available)
    InformationTrader: perceive() → stochastic detection → act (short or cover)

  Phase 3 — Order Submission:
    All investors → Market: {action: buy/sell/hold, quantity: Q, bid_price: P}

  Phase 4 — Market Clearing:
    Market.perceive(): collect all orders
    Market.decide():   D(t) = Σ buy_qty − Σ sell_qty
                       P(t+1) = max(P(t) + λ·D(t) + γ·[F−P(t)] + ε(t), 0.01)
    Market.act():      broadcast updated {price, prev_price, fundamental, deviation, round}

  Phase 5 — Logging:
    Records written to EXPERIMENT/ArchegosCollapse/{Variant}/records/
```

**Round duration interpretation**: Each round approximates one trading day in the cascade context. The 200-round simulation covers approximately 40 trading weeks, providing enough time for cascade onset (~rounds 10–25), trough (~rounds 15–30), and recovery (~rounds 30–80).


## §8 Historical Case Studies

### Event: Archegos Capital Management Collapse

| Item      | Detail                                                                                                                                                      |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Date      | March 22–29, 2021 (primary cascade March 25–29)                                                                                                             |
| Market    | US equities: ViacomCBS (VIAC), Discovery (DISCA), GSX Techedu (GOTU), Farfetch, others                                                                      |
| Trigger   | ViacomCBS $3B equity offering (March 22) caused share price decline → triggered TRS margin calls at Archegos across multiple prime brokers simultaneously   |
| Duration  | Cascade phase: 5 trading days; recognition phase: 3–4 months                                                                                                |
| Magnitude | ViacomCBS fell from $100 to ~$40 (−60%) in one week; total Archegos losses: ~$20B; Credit Suisse loss: $5.5B; Nomura loss: $2.9B; Morgan Stanley loss: ~$1B |

**Key Dynamics Timeline**:

| Date        | Event                                                           | Market Effect                               |
|-------------|-----------------------------------------------------------------|---------------------------------------------|
| March 22    | ViacomCBS announces $3B equity offering                         | VIAC falls ~12% in one day                  |
| March 23–24 | Archegos fails to meet margin calls; notifies prime brokers     | No public disclosure (TRS not required)     |
| March 25    | Morgan Stanley organizes block trade; sells first at ~$92/share | First public cascade signal                 |
| March 26    | Multiple prime brokers begin simultaneous block trades          | VIAC falls to ~$48 (−50% from week start)   |
| March 29    | Credit Suisse, Nomura acknowledge large losses                  | VIAC at ~$40; market recognizes full extent |

**Quantitative Evidence**:
- ViacomCBS price: $100 (March 22 open) → $40 (March 29 close); −60% (Bloomberg, 2021)
- Archegos notional exposure: $35–40B across 5 prime brokers (FSB, 2022, p. 49)
- Leverage ratio: 5–8x equity (Becketti, 2021)
- Morgan Stanley total loss: ~$1B (Q2 2021 earnings disclosure)
- Credit Suisse total loss: $5.5B (Credit Suisse Annual Report 2021, supplementary disclosures)

**Agent Mappings**:

| Simulation Agent  | Real-World Counterpart                                    | Mapping Justification                                                             |
|-------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| ConcentratedFund  | Archegos Capital Management (Bill Hwang)                  | TRS leverage; hidden concentration; forced liquidation initiator                  |
| PrimeBroker1      | Morgan Stanley                                            | First to organize block trades (March 25–26); incurred smallest loss (~$1B)       |
| PrimeBroker2      | Credit Suisse / Nomura                                    | Later to act (March 29); incurred largest losses ($5.5B + $2.9B)                  |
| BlockTradeBuyer   | Institutional buyers of discounted blocks                 | Various asset managers who purchased VIAC/DISCA at fire-sale prices in late March |
| InformationTrader | Hedge funds that detected unusual TRS-related block flows | Traders who reportedly shorted these names before the public cascade              |

**Simulation Calibration Lessons**:
- The 0.05 difference between PrimeBroker1 threshold (0.10) and PrimeBroker2 threshold (0.15) should produce a loss differential of approximately 3–5x, consistent with the Morgan Stanley vs. Credit Suisse outcome
- Cascade should develop over 3–5 rounds from trigger to trough, consistent with the 5 trading days in the actual event
- Recovery should be partial, not full, within 200 rounds — ViacomCBS had not fully recovered 6 months later

**Primary Sources**:
- Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, FRB Kansas City, 2021-Q3.
- Financial Stability Board. (2022). *Global Monitoring Report on Non-Bank Financial Intermediation 2022*, pp. 47–54.
- SEC Staff Report on Archegos Capital Management. (2022). U.S. Securities and Exchange Commission.
- Credit Suisse Group AG. (2021). *Annual Report 2021*. Zurich.


## §9 Variant Comparison Preview

| Aspect                    | Rule                                            | LLM                                                                                                      | RuleLLM                                                           | Rag                                                                                              |
|---------------------------|-------------------------------------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| Decision Logic            | Fixed thresholds + formulas                     | Persona-driven LLM reasoning                                                                             | Formula-anchored hybrid LLM                                       | RAG-augmented hybrid LLM                                                                         |
| Determinism               | Fully deterministic                             | Stochastic (LLM variability)                                                                             | Semi-deterministic (±20% quantity noise)                          | Stochastic + knowledge-dependent                                                                 |
| Expected Cascade Depth    | Consistent ~60% drawdown (calibration target)   | Variable: LLM may hesitate or over-sell; expected 40–70%                                                 | Near-Rule (±15%) — rules constrain behavior                       | Modified by historical case recall; expected similar or slightly moderated                       |
| Expected Cascade Timing   | Predictable: onset rounds 10–20                 | Variable onset: ±5–10 rounds due to LLM persona effects                                                  | Near-Rule timing (±3–5 rounds)                                    | May onset earlier or later depending on historical context retrieved                             |
| Key Behavioral Difference | Baseline reference                              | ConcentratedFund may "rationalize" delayed selling (LLM denial effect); PrimeBrokers may show hesitation | Rules ensure threshold adherence; LLM adjusts quantity ±20% only  | Retrieved Archegos/LTCM knowledge may cause earlier pre-emptive action or more calibrated sizing |
| Research Question         | Does cascade emerge from threshold rules alone? | Do LLM personas reproduce denial-then-panic psychology without knowing the scenario name?                | Does quantitative rule anchoring suppress LLM hesitation effects? | Does historical knowledge of TRS cascades change prime broker timing or severity?                |

**Predicted ordering**: Cascade depth: Rule ≈ RuleLLM > LLM ≈ Rag (LLM personas may introduce more hesitation; RAG provides historical calibration)
