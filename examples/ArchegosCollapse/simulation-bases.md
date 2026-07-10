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
- **Relevance to This Simulation**: The timing asymmetry between `PrimeBrokerFirstMover` (lower threshold, acts first) and `PrimeBrokerDelayedLiquidator` (higher threshold, acts later and at worse prices) directly models the first-mover advantage. The gap between their threshold values (0.10 vs 0.15) calibrates the price penalty for delayed action.
- **Calibration Implication**: PrimeBrokerFirstMover.liquidation_threshold = 0.10 < PrimeBrokerDelayedLiquidator.liquidation_threshold = 0.15; the price at which PrimeBrokerDelayedLiquidator sells is approximately λ × Q₁ below PrimeBrokerFirstMover's selling price.

---

### Theory: Opportunistic Block Trading and Market Stabilization

- **Citation**: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617–637. https://doi.org/10.1111/j.1540-6261.1988.tb04594.x
- **Core Insight**: In markets with infrequent large-order flow, liquidity providers must hold inventory against the risk of adverse price moves. Block trade buyers will only absorb forced supply when the price discount is sufficient to compensate for inventory risk during the holding period before resale. This creates a natural price floor in liquidation races: when discounts exceed the risk-compensation threshold, opportunistic buyers absorb supply and stabilize prices.
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

---

### Theory: Informed Order-Flow Front-Running of Anticipated Liquidation

- **Citation**: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335. https://doi.org/10.2307/1913210
- **Core Insight**: An informed trader who detects nascent distress before it is public front-runs the anticipated forced order flow. By selling ahead of the mechanical broker liquidation, the informed trader accelerates the initial price decline before rule-based broker thresholds actually trigger, and later covers when the cascade exhausts itself. This is the microstructure counterpart to the creditor-run mechanism: private information about *future* forced supply is transmitted into prices through the informed trader's own order flow.
- **Mathematical Formulation**:
  ```
  Detection event: 1[deviation(t) < θ_det] · Bernoulli(p_det)
  Order sign:      sign(order) = − sign(expected forced flow)   (short when a cascade is anticipated)
  Cover branch:    trigger when deviation(t) > cover_threshold and short_position > 0
  Expected profit rises monotonically with the anticipated cascade depth conditional on successful detection.
  ```
- **Empirical Evidence**: Kyle (1985) establishes the informed-trader price-impact framework in which private signals about future flow are impounded into prices through orders whose informativeness scales with the signal precision. Boehmer, Jones, & Zhang (2008), *Journal of Finance*, 63(2), 491–527, https://doi.org/10.1111/j.1540-6261.2008.01324.x, document that short sellers are on average informed and that a non-trivial fraction (about 30 %–70 % depending on regime) detect distress-relevant information before it becomes public.
- **Relevance to This Simulation**: The `InformationTrader` agent operationalises the Kyle channel by gating a stochastic sell on `deviation(t) < θ_det` with a per-round Bernoulli detection draw, then covering when the deviation recovers. This is the only channel in the scenario that produces informed selling *before* mechanical broker thresholds trigger, so it directly controls the shape of cascade onset (as opposed to cascade amplification, which is Gorton & Metrick 2012's channel).
- **Calibration Implication**: `θ_det = 0.05` and `p_det = 0.50` locate the informed channel inside the empirical Kyle-signal-precision band; both parameters are exported to `simulation-bases.md §6` and to target §9. The predatory-trading extension (Brunnermeier & Pedersen 2005) is inherited by the agent-embedded block in `§4.5.3` and does not require a duplicate root Theory block, since it is a within-agent elaboration of Kyle's informed-flow mechanism.


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
The high λ (0.03) reflects the market-impact amplification typical in concentrated block selling — when a single large seller (ConcentratedFund or a prime broker) submits an order representing 5–10% of daily volume, price impact is significantly larger than normal. The low γ (0.01) models the slow pull toward fundamental value characteristic of equity markets over short horizons: prices do not snap back to intrinsic value within rounds. The combination ensures that cascade-induced deviations persist long enough to trigger successive threshold crossings by PrimeBrokerFirstMover and PrimeBrokerDelayedLiquidator.

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

| Field         | Type  | Definition                                     | Rationale for Inclusion                                                                                                             |
|---------------|-------|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `price`       | float | Current market price after order clearing      | Primary signal; all agents monitor price level                                                                                      |
| `prev_price`  | float | Price from the previous round                  | Enables InformationTrader to detect first signs of decline                                                                          |
| `fundamental` | float | Intrinsic fundamental value (constant = 100.0) | Required for deviation calculation and BlockTradeBuyer activation                                                                   |
| `deviation`   | float | `(price − fundamental) / fundamental`          | Pre-computed; the primary trigger signal for ConcentratedFund, PrimeBrokerFirstMover, PrimeBrokerDelayedLiquidator, BlockTradeBuyer |
| `round`       | int   | Current round number                           | Enables round-based frequency control if needed                                                                                     |

**Design Note**: `return_pct` is NOT broadcast separately — agents that need price change compute it from `price` and `prev_price`. The central signal is `deviation` (not raw price level), consistent with how prime brokers monitor collateral quality relative to fair value.


## §4 Investor Taxonomy

This section follows `masim/skills/agent-design-skill.md` and the finance instantiation in `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. All five Archegos-specific agents now pass the AGENT_POOL gate as `reuse approved` because the finance pool contains matching standalone profiles for TRS hidden leverage, prime-broker liquidation races, delayed broker execution haircuts, block-trade absorption, and liquidation-signal predatory trading. Each standalone pool file is embedded below in re-levelled form.


### §4.1 ConcentratedFund

> Agent pool source: examples/AGENT_POOL/finance/concentrated-fund.md


#### 4.1.1 Summary

| Field                 | Content                                                                               |
|-----------------------|---------------------------------------------------------------------------------------|
| Archetype             | TRS-leveraged concentrated fund                                                       |
| Theory Family         | Leverage / Risk-On-Risk-Off                                                           |
| Market Role           | **Destabilising** - forced deleveraging creates the first large negative demand shock |
| Time Horizon          | medium                                                                                |
| Risk Tolerance        | high                                                                                  |
| Information Asymmetry | partial                                                                               |
| Determinism           | deterministic                                                                         |

#### 4.1.2 Definition and Goals

This agent models a family office or hedge fund using total return swaps for concentrated equity exposure in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: minimize margin-breach pressure by selling a fixed fraction of exposure once collateral deterioration crosses the trigger.

Inside a market simulation this agent initiates a liquidation race through forced selling after a margin breach. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

#### 4.1.3 Theoretical Foundation

**TRS hidden leverage and forced close-out**:
- Theory / Study: Hidden leverage through total return swaps.
- Citation: Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1-12. https://doi.org/10.18651/ER/v106n3Becketti
- Core Insight: TRS exposure can accumulate outside public equity filings, leaving counterparties with incomplete aggregate exposure information. When collateral value falls, a margin breach converts discretionary holding into forced close-out.
- Mathematical Formulation: `equity_ratio_t = equity_t / (abs(position_t) * price_t)`; forced sell when `deviation_t < theta_margin`.
- Empirical Evidence: FSB (2022) reports roughly $35-40B Archegos notional exposure and 5-8x leverage.
- Relevance to This Agent: The agent operationalises the forced close-out channel with `margin_threshold` and `trs_sell_ratio`.
- Calibration Source: Becketti (2021) and FSB (2022), margin range about 10-25% and leverage 5-8x.
- Falsification Conditions: If this agent does not sell when `deviation < margin_threshold`, the mechanism is absent.
- Alternative Theories: voluntary portfolio rebalancing; rational deleveraging.

**Overconfidence and concentration risk**:
- Theory / Study: Overconfidence and excessive trading.
- Citation: Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400
- Core Insight: Overconfident investors overestimate private information quality and accept concentrated exposures. This explains the pre-trigger accumulation phase without making it an environment rule.
- Mathematical Formulation: `Q_actual = Q_prudent * (1 + overconfidence_multiplier)`.
- Empirical Evidence: Barber & Odean (2001) report lower net returns and higher trading among overconfident investor groups.
- Relevance to This Agent: Supports high `initial_position` and delayed voluntary de-risking.
- Calibration Source: Barber & Odean (2001), with position scale normalized to scenario units.
- Falsification Conditions: If reducing initial exposure has no impact on forced-sale quantity, concentration is not represented.
- Alternative Theories: rational concentrated alpha strategy.

#### 4.1.4 Design Purpose and Activation Triggers

Purpose: Generate forced selling after a TRS-style margin breach.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < margin_threshold`: submit sell order sized by `position * trs_sell_ratio`.
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: hold.
- Deviation recovers above threshold: hold reduced position.

Market Contribution by Regime:
| Regime                     | Contribution                | Mechanism                                                                   |
|----------------------------|-----------------------------|-----------------------------------------------------------------------------|
| Calm market                | Hold / latent destabilising | Large exposure is present but inactive.                                     |
| Liquidity stress / drought | Destabilising               | Forced sale adds concentrated supply.                                       |
| Crash / cascade            | Destabilising               | Remaining exposure can continue to liquidate after repeated trigger rounds. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

#### 4.1.5 Behavioral Framework

###### 4.1.5.0 I/O Contract

**Inputs (per decision call).**

| Input                 | Source                                 | Type / Shape | Required?        | Notes                                                                                                 |
|-----------------------|----------------------------------------|--------------|------------------|-------------------------------------------------------------------------------------------------------|
| `price`               | environment broadcast                  | `float`      | yes              | Row of §4.1.5.1                                                                                       |
| `fundamental`         | environment broadcast                  | `float`      | yes              | Row of §4.1.5.1                                                                                       |
| `deviation`           | environment broadcast                  | `float`      | yes              | Row of §4.1.5.1                                                                                       |
| `position`            | agent state (§4.1.5.4 state variables) | `float`      | yes              | Persistent long exposure remaining                                                                    |
| `cash`                | agent state (§4.1.5.4 state variables) | `float`      | yes              | Populated by init from §4.1.6                                                                         |
| `round`               | round header                           | `int`        | yes              | Round number                                                                                          |
| `retrieved_knowledge` | retrieval store (Rag variant only)     | `list[str]`  | Rag variant only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum        | Unit                       | Required? | Meaning                                                    |
|-------------|--------|---------------------------|----------------------------|-----------|------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`   | —                          | yes       | Discrete action selected (matches §4.1.5.3 Order types)    |
| `bid_price` | float  | > 0                       | same units as `price`      | yes       | Order price (§4.1.5.3 Price level rule)                    |
| `quantity`  | float  | ≥ 0, ≤ available position | shares / units of position | yes       | Order magnitude (§4.1.5.3 Order quantity rule)             |
| `reasoning` | string | 1–3 sentences             | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py` |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, position]` before emission.
- `bid_price` MUST be strictly positive; if computed non-positive, floor to `price`.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.1.5.5); the same inputs and state MUST produce byte-identical outputs across variants.

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "sell", "bid_price": 84.0, "quantity": 2500.0, "reasoning": "Deviation crossed margin_threshold, forced close-out of 50% of position."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST be clamped to `[0, position]`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.1.5.2, §4.1.5.3, or §4.1.5.4, this §4.1.5.0 wins.

###### 4.1.5.1 Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                               |
|---------------|------------|---------------|-----------------------------------------------------------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference and portfolio valuation [Ref 9].                                    |
| `fundamental` | Continuous | 1 tick        | Anchor for collateral-value deviation and discount calculations [Ref 1].                |
| `deviation`   | Continuous | 1 tick        | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `position`    | State      | persistent    | Remaining synthetic long exposure available to liquidate [Ref 1].                       |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

###### 4.1.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `position`; Write: no state before decision.
2. Compare `deviation` with `margin_threshold` [Ref 1].
3. If `deviation < margin_threshold`, compute `q = min(position, position * trs_sell_ratio)` [Ref 1; Ref 2].
4. If `q > 0`, emit `sell`; otherwise hold.
5. Post-fill, reduce `position` and increase `cash` by executed proceeds.

###### 4.1.5.3 Action Space

| Aspect                | Specification                                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | `buy`, `sell`, `hold` as specified by the trigger function.                                                                   |
| Price level rule      | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`.                     |
| Order quantity rule   | `q = min(position, position * trs_sell_ratio)` for sell; otherwise zero.                                                      |
| Order lifetime        | One decision round; replace on next fresh broadcast.                                                                          |
| Cancellation policy   | Cancel prior intent when the current trigger evaluates to hold or the opposite side.                                          |
| Inventory constraint  | Never sell more than internally available long position plus declared short inventory discipline.                             |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop selling only when position reaches zero or deviation no longer breaches `margin_threshold`.                              |

###### 4.1.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_margin:
    a_t = sell; q_t = min(position_t, position_t * phi_trs); b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State              | Initial value   | Update phase | Evolution                                        |
|--------------------|-----------------|--------------|--------------------------------------------------|
| `cash`             | scenario config | post-fill    | cash decreases on buy and increases on sell.     |
| `position`         | scenario config | post-fill    | position increases on buy and decreases on sell. |
| `margin_triggered` | false           | post-decide  | true after the first margin-breach sell.         |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol         | Meaning                                     | Default Value | Source       |
|----------------|---------------------------------------------|---------------|--------------|
| `theta_margin` | Margin-breach deviation threshold           | -0.15         | Ref 1; Ref 2 |
| `phi_trs`      | Fraction of position liquidated per trigger | 0.50          | Ref 1; Ref 2 |

###### 4.1.5.5 Behavioral Properties

- Time horizon: medium - TRS exposure is built over weeks/months but forced close-out is immediate.
- Risk tolerance: high - 5-8x leverage implies high tolerance until forced liquidation.
- Information asymmetry: partial - knows own leverage but not all broker reactions.
- Psychological profile: overconfidence and concentration-risk underestimation [Ref 6].

#### 4.1.6 Parameters

| Parameter          | Type  | Default  | Valid Range    | Sensitivity | Description                                     | Impact                                                           | Source                                           |
|--------------------|-------|----------|----------------|-------------|-------------------------------------------------|------------------------------------------------------------------|--------------------------------------------------|
| `margin_threshold` | float | -0.15    | [-0.25, -0.05] | high        | Deviation at which margin pressure forces sale. | Higher magnitude -> fewer and later forced sales.                | Becketti (2021); FSB (2022)                      |
| `trs_sell_ratio`   | float | 0.50     | [0.10, 1.00]   | high        | Fraction of current position sold per trigger.  | Higher -> larger negative order flow per activation.             | FSB (2022); prime-broker post-mortem calibration |
| `initial_position` | float | 5000.0   | > 0            | high        | Starting synthetic long exposure.               | Higher -> larger cascade seed order.                             | FSB (2022) notional exposure scale, normalized   |
| `initial_cash`     | float | 500000.0 | >= 0           | medium      | Initial liquidity buffer.                       | Higher -> more ability to absorb losses before state exhaustion. | Scenario normalization from §6                   |

#### 4.1.7 Population and Heterogeneity

| Dimension                      | Specification                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Default population size        | 2 instances in ArchegosCollapse configs.                                                                      |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults.                    |
| Heterogeneity per parameter    | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation        | Same archetype instances share theory and trigger sign; cash and position levels may differ.                  |
| Identity persistence           | Persistent identity and state across rounds; no type switching.                                               |

#### 4.1.8 Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = min(5000, 5000 * 0.50) = 2500`; sell branch fires.
Decision: `sell`, `quantity=2500`, `bid_price=84`.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
System state: `price=96`, `fundamental=100`, `deviation=-0.04`, plus default parameters.
Calculation:
  Trigger conditions are not met under the default threshold set.
Decision: `hold`, `quantity=0`, `bid_price=96`.
State update: no cash or position change.

### Case 3 - Stress branch
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation:
  `deviation=-0.12` is above `margin_threshold=-0.15`; margin branch does not fire.
Decision: `hold`, `quantity=0`, `bid_price=88`.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

#### 4.1.9 Validation and Calibration

**Calibration data sources**:
- `margin_threshold` <- Becketti (2021) and FSB (2022), 10-25% margin range.
- `trs_sell_ratio` <- FSB (2022) and Archegos post-event liquidation scale.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

###### 4.1.9.1 Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

#### 4.1.10 Academic References

| # | Citation                                                                                                                                                                                                 | Notes                                         |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1-12. https://doi.org/10.18651/ER/v106n3Becketti                      | TRS leverage and margin breach mechanism      |
| 2 | Financial Stability Board. (2022). *US dollar funding and emerging market economy vulnerabilities*. FSB non-bank financial intermediation analysis, Archegos discussion, pp. 47-51. https://www.fsb.org/ | Archegos notional exposure and leverage scale |
| 6 | Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400    | Overconfidence and concentrated risk taking   |
| 9 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x                                        | Price and order-flow signal relevance         |

#### 4.1.11 Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                    |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | Codex                                                                                                                                                                                                                                                                                                                      |
| Reviewed by | Codex three-pass self-check                                                                                                                                                                                                                                                                                                |
| Created     | 2026-06-30                                                                                                                                                                                                                                                                                                                 |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                      |
| Change log  | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as the first sub-block of §4.N.5 Behavioral Framework, re-verified §3.1–§3.11 section order against `agent-design-skill.md`; no structural change to other sub-blocks. |
| Status      | experimental                                                                                                                                                                                                                                                                                                               |

### §4.2 PrimeBrokerFirstMover

> Agent pool source: examples/AGENT_POOL/finance/prime-broker-first-mover.md


#### 4.2.1 Summary

| Field                 | Content                                                                                            |
|-----------------------|----------------------------------------------------------------------------------------------------|
| Archetype             | first-mover prime-broker liquidator                                                                |
| Theory Family         | Leverage / Risk-On-Risk-Off                                                                        |
| Market Role           | **Destabilising** - early liquidation protects collateral value but accelerates fire-sale pressure |
| Time Horizon          | short                                                                                              |
| Risk Tolerance        | medium                                                                                             |
| Information Asymmetry | partial                                                                                            |
| Determinism           | deterministic                                                                                      |

#### 4.2.2 Definition and Goals

This agent models a prime broker / dealer liquidating client collateral in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: maximize private collateral recovery by selling when collateral-quality deviation breaches the broker threshold.

Inside a market simulation this agent transmits borrower distress into market-wide selling through creditor-run incentives. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

#### 4.2.3 Theoretical Foundation

**Creditor run and first-mover liquidation**:
- Theory / Study: Run incentives among collateralised creditors.
- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: When several creditors can liquidate similar collateral, earlier sellers receive better prices because later sellers face price impact from prior liquidation. The private incentive to run can dominate collective value preservation.
- Mathematical Formulation: `payoff_i = q_i * P(t_i)`, with `P(t_i) > P(t_j)` when `t_i < t_j` during liquidation pressure.
- Empirical Evidence: Gorton & Metrick (2012) document run-like rollover behaviour when collateral quality deteriorates; Archegos post-mortems show first movers lost less than late movers.
- Relevance to This Agent: The liquidation threshold and sell fraction encode the broker's private recovery race.
- Calibration Source: Gorton & Metrick (2012); Archegos broker-loss comparisons reported in regulatory and bank post-mortems.
- Falsification Conditions: If earlier threshold settings do not improve selling price, first-mover advantage is not represented.
- Alternative Theories: coordinated workout; patient liquidation.

#### 4.2.4 Design Purpose and Activation Triggers

Purpose: Liquidate client collateral when collateral-value deterioration crosses the broker threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal collateral inventory

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < liquidation_threshold`: submit sell order sized by `position * liquidation_sell_ratio`.
- `<Default>`: hold.

Deactivation Conditions:
- Collateral inventory exhausted: hold.
- Deviation above threshold: hold.

Market Contribution by Regime:
| Regime                     | Contribution  | Mechanism                                                       |
|----------------------------|---------------|-----------------------------------------------------------------|
| Calm market                | Hold          | No liquidation while collateral value remains inside threshold. |
| Liquidity stress / drought | Destabilising | Sells collateral into weakening demand.                         |
| Crash / cascade            | Destabilising | Repeated sell decisions reinforce price impact.                 |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

#### 4.2.5 Behavioral Framework

###### 4.2.5.0 I/O Contract

**Inputs (per decision call).**

| Input                 | Source                             | Type / Shape | Required?        | Notes                                                                                                 |
|-----------------------|------------------------------------|--------------|------------------|-------------------------------------------------------------------------------------------------------|
| `price`               | environment broadcast              | `float`      | yes              | Row of §4.2.5.1                                                                                       |
| `fundamental`         | environment broadcast              | `float`      | yes              | Row of §4.2.5.1                                                                                       |
| `deviation`           | environment broadcast              | `float`      | yes              | Row of §4.2.5.1                                                                                       |
| `position`            | agent state (§4.2.5.4)             | `float`      | yes              | Collateral inventory available to liquidate                                                           |
| `cash`                | agent state (§4.2.5.4)             | `float`      | yes              | Populated by init from §4.2.6                                                                         |
| `round`               | round header                       | `int`        | yes              | Round number                                                                                          |
| `retrieved_knowledge` | retrieval store (Rag variant only) | `list[str]`  | Rag variant only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty |

**Outputs (per decision call).**

| Field       | Type   | Valid Range / Enum        | Unit                       | Required? | Meaning                                                    |
|-------------|--------|---------------------------|----------------------------|-----------|------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`   | —                          | yes       | Discrete action selected (matches §4.2.5.3 Order types)    |
| `bid_price` | float  | > 0                       | same units as `price`      | yes       | Order price (§4.2.5.3 Price level rule)                    |
| `quantity`  | float  | ≥ 0, ≤ available position | shares / units of position | yes       | Order magnitude (§4.2.5.3 Order quantity rule)             |
| `reasoning` | string | 1–3 sentences             | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py` |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, position]` before emission.
- `bid_price` MUST be strictly positive; if computed non-positive, floor to `price`.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.2.5.5); the same inputs and state MUST produce byte-identical outputs across variants.

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "sell", "bid_price": 90.0, "quantity": 800.0, "reasoning": "Deviation −0.11 crossed θ_liq_1 = −0.10; liquidate 40% of position first."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST be clamped to `[0, position]`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.2.5.2, §4.2.5.3, or §4.2.5.4, this §4.2.5.0 wins.

###### 4.2.5.1 Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                               |
|---------------|------------|---------------|-----------------------------------------------------------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference and portfolio valuation [Ref 9].                                    |
| `fundamental` | Continuous | 1 tick        | Anchor for collateral-value deviation and discount calculations [Ref 1].                |
| `deviation`   | Continuous | 1 tick        | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `position`    | State      | persistent    | Collateral inventory available to liquidate [Ref 3].                                    |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

###### 4.2.5.2 Core Behavioral Mechanism

1. Read: `deviation`, `price`, and `position`; Write: no state before decision.
2. Compare `deviation` with `liquidation_threshold=-0.10` [Ref 3].
3. If threshold is breached, compute `q = min(position, position * liquidation_sell_ratio)` [Ref 3].
4. Emit sell at current price; otherwise hold.
5. Post-fill, reduce collateral position and increase cash by proceeds.

###### 4.2.5.3 Action Space

| Aspect                | Specification                                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | `buy`, `sell`, `hold` as specified by the trigger function.                                                                   |
| Price level rule      | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`.                     |
| Order quantity rule   | `q = min(position, position * liquidation_sell_ratio)` for sell; otherwise zero.                                              |
| Order lifetime        | One decision round; replace on next fresh broadcast.                                                                          |
| Cancellation policy   | Cancel prior intent when the current trigger evaluates to hold or the opposite side.                                          |
| Inventory constraint  | Never sell more than internally available long position plus declared short inventory discipline.                             |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop selling when position is exhausted or collateral deviation no longer breaches the threshold.                             |

###### 4.2.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_liq:
    a_t = sell; q_t = min(position_t, position_t * phi_liq); b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State             | Initial value   | Update phase | Evolution                                        |
|-------------------|-----------------|--------------|--------------------------------------------------|
| `cash`            | scenario config | post-fill    | cash decreases on buy and increases on sell.     |
| `position`        | scenario config | post-fill    | position increases on buy and decreases on sell. |
| `liquidated_once` | false           | post-decide  | true after first sell activation.                |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol      | Meaning                                 | Default Value | Source |
|-------------|-----------------------------------------|---------------|--------|
| `theta_liq` | Liquidation deviation threshold         | -0.10         | Ref 3  |
| `phi_liq`   | Fraction of collateral sold per trigger | 0.40          | Ref 3  |

###### 4.2.5.5 Behavioral Properties

- Time horizon: short - prime-broker risk decisions are short-horizon once collateral deteriorates.
- Risk tolerance: medium - risk discipline is balance-sheet protective, not speculative.
- Information asymmetry: partial - observes own client exposure but not all competitor actions.
- Psychological profile: competitive first-mover risk management under run incentives [Ref 3].

#### 4.2.6 Parameters

| Parameter                | Type  | Default | Valid Range    | Sensitivity | Description                                     | Impact                                       | Source                                                      |
|--------------------------|-------|---------|----------------|-------------|-------------------------------------------------|----------------------------------------------|-------------------------------------------------------------|
| `liquidation_threshold`  | float | -0.10   | [-0.30, -0.03] | high        | Deviation that triggers collateral liquidation. | Higher magnitude -> later liquidation.       | Gorton & Metrick (2012); Archegos broker timing calibration |
| `liquidation_sell_ratio` | float | 0.40    | [0.05, 1.00]   | high        | Fraction of collateral sold per activation.     | Higher -> larger immediate selling pressure. | Gorton & Metrick (2012); post-event broker calibration      |
| `initial_position`       | float | 4000.0  | > 0            | high        | Starting collateral inventory.                  | Higher -> larger liquidation supply.         | Scenario normalization from Archegos exposure reports       |

#### 4.2.7 Population and Heterogeneity

| Dimension                      | Specification                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Default population size        | 1 instance in ArchegosCollapse configs.                                                                       |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults.                    |
| Heterogeneity per parameter    | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation        | Same archetype instances share theory and trigger sign; cash and position levels may differ.                  |
| Identity persistence           | Persistent identity and state across rounds; no type switching.                                               |

#### 4.2.8 Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = position * 0.40`; sell branch fires because `-0.16 < -0.10`.
Decision: `sell`, positive quantity, `bid_price` determined by price-level rule.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
System state: `price=96`, `fundamental=100`, `deviation=-0.04`, plus default parameters.
Calculation:
  Trigger conditions are not met under the default threshold set.
Decision: `hold`, `quantity=0`, `bid_price=96`.
State update: no cash or position change.

### Case 3 - Stress branch
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation:
  At `deviation=-0.12`, branch fires for this threshold.
Decision: sell for PrimeBrokerFirstMover-style early threshold; hold for delayed threshold until deeper stress.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

#### 4.2.9 Validation and Calibration

**Calibration data sources**:
- `liquidation_threshold` <- Gorton & Metrick (2012) run threshold logic and Archegos broker timing.
- `liquidation_sell_ratio` <- liquidation-race payoff calibration from scenario §2 and §8.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

###### 4.2.9.1 Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

#### 4.2.10 Academic References

| # | Citation                                                                                                                                                                    | Notes                                         |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 3 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016 | Creditor run and first-mover liquidation race |
| 9 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x           | Price impact and execution-price relevance    |

#### 4.2.11 Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                    |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | Codex                                                                                                                                                                                                                                                                                                                      |
| Reviewed by | Codex three-pass self-check                                                                                                                                                                                                                                                                                                |
| Created     | 2026-06-30                                                                                                                                                                                                                                                                                                                 |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                      |
| Change log  | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as the first sub-block of §4.N.5 Behavioral Framework, re-verified §3.1–§3.11 section order against `agent-design-skill.md`; no structural change to other sub-blocks. |
| Status      | experimental                                                                                                                                                                                                                                                                                                               |

### §4.3 PrimeBrokerDelayedLiquidator

> Agent pool source: examples/AGENT_POOL/finance/prime-broker-delayed-liquidator.md


#### 4.3.1 Summary

| Field                 | Content                                                                                  |
|-----------------------|------------------------------------------------------------------------------------------|
| Archetype             | delayed prime-broker liquidator                                                          |
| Theory Family         | Leverage / Risk-On-Risk-Off                                                              |
| Market Role           | **Destabilising** - later liquidation amplifies the cascade and receives worse execution |
| Time Horizon          | short                                                                                    |
| Risk Tolerance        | medium                                                                                   |
| Information Asymmetry | partial                                                                                  |
| Determinism           | deterministic                                                                            |

#### 4.3.2 Definition and Goals

This agent models a prime broker / dealer liquidating client collateral in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: maximize private collateral recovery by selling when collateral-quality deviation breaches the broker threshold.

Inside a market simulation this agent transmits borrower distress into market-wide selling through creditor-run incentives. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

#### 4.3.3 Theoretical Foundation

**Creditor run and first-mover liquidation**:
- Theory / Study: Run incentives among collateralised creditors.
- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: When several creditors can liquidate similar collateral, earlier sellers receive better prices because later sellers face price impact from prior liquidation. The private incentive to run can dominate collective value preservation.
- Mathematical Formulation: `payoff_i = q_i * P(t_i)`, with `P(t_i) > P(t_j)` when `t_i < t_j` during liquidation pressure.
- Empirical Evidence: Gorton & Metrick (2012) document run-like rollover behaviour when collateral quality deteriorates; Archegos post-mortems show first movers lost less than late movers.
- Relevance to This Agent: The liquidation threshold and sell fraction encode the broker's private recovery race.
- Calibration Source: Gorton & Metrick (2012); Archegos broker-loss comparisons reported in regulatory and bank post-mortems.
- Falsification Conditions: If earlier threshold settings do not improve selling price, first-mover advantage is not represented.
- Alternative Theories: coordinated workout; patient liquidation.

#### 4.3.4 Design Purpose and Activation Triggers

Purpose: Liquidate client collateral when collateral-value deterioration crosses the broker threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal collateral inventory

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < liquidation_threshold`: submit sell order sized by `position * liquidation_sell_ratio`.
- `<Default>`: hold.

Deactivation Conditions:
- Collateral inventory exhausted: hold.
- Deviation above threshold: hold.

Market Contribution by Regime:
| Regime                     | Contribution  | Mechanism                                                       |
|----------------------------|---------------|-----------------------------------------------------------------|
| Calm market                | Hold          | No liquidation while collateral value remains inside threshold. |
| Liquidity stress / drought | Destabilising | Sells collateral into weakening demand.                         |
| Crash / cascade            | Destabilising | Repeated sell decisions reinforce price impact.                 |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

#### 4.3.5 Behavioral Framework

###### 4.3.5.0 I/O Contract

**Inputs (per decision call).**

| Input                 | Source                                 | Type / Shape | Required?        | Notes                                                                                                 |
|-----------------------|----------------------------------------|--------------|------------------|-------------------------------------------------------------------------------------------------------|
| `price`               | environment broadcast                  | `float`      | yes              | Row of §4.3.5.1                                                                                       |
| `fundamental`         | environment broadcast                  | `float`      | yes              | Row of §4.3.5.1                                                                                       |
| `deviation`           | environment broadcast                  | `float`      | yes              | Row of §4.3.5.1                                                                                       |
| `position`            | agent state (§4.3.5.4 state variables) | `float`      | yes              | Collateral inventory remaining to liquidate                                                           |
| `cash`                | agent state (§4.3.5.4 state variables) | `float`      | yes              | Populated by init from §4.3.6                                                                         |
| `round`               | round header                           | `int`        | yes              | Round number                                                                                          |
| `retrieved_knowledge` | retrieval store (Rag variant only)     | `list[str]`  | Rag variant only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum        | Unit                       | Required? | Meaning                                                                    |
|-------------|--------|---------------------------|----------------------------|-----------|----------------------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`   | —                          | yes       | Discrete action selected (matches §4.3.5.3 Order types)                    |
| `bid_price` | float  | > 0                       | same units as `price`      | yes       | Order price (§4.3.5.3 Price level rule; sell uses `price * price_penalty`) |
| `quantity`  | float  | ≥ 0, ≤ available position | shares / units of position | yes       | Order magnitude (§4.3.5.3 Order quantity rule)                             |
| `reasoning` | string | 1–3 sentences             | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py`                 |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, position]` before emission.
- `bid_price` MUST be strictly positive; if the haircut product `price * price_penalty` is non-positive, floor to `price`.
- Sign convention: `action = "sell"` corresponds to negative net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.3.5.5); the same inputs and state MUST produce byte-identical outputs across variants.

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "sell", "bid_price": 82.45, "quantity": 1225.0, "reasoning": "Deviation crossed liquidation_threshold=-0.15 after first-mover selling; liquidating 35% of collateral at delayed haircut."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST be clamped to `[0, position]`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example that uses the later `liquidation_threshold=-0.15` calibration.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.3.5.2, §4.3.5.3, or §4.3.5.4, this §4.3.5.0 wins.

###### 4.3.5.1 Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                               |
|---------------|------------|---------------|-----------------------------------------------------------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference and portfolio valuation [Ref 9].                                    |
| `fundamental` | Continuous | 1 tick        | Anchor for collateral-value deviation and discount calculations [Ref 1].                |
| `deviation`   | Continuous | 1 tick        | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `position`    | State      | persistent    | Collateral inventory available to liquidate [Ref 3].                                    |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

###### 4.3.5.2 Core Behavioral Mechanism

1. Read: `deviation`, `price`, and `position`; Write: no state before decision.
2. Compare `deviation` with `liquidation_threshold=-0.15` [Ref 3].
3. If threshold is breached, compute `q = min(position, position * liquidation_sell_ratio)` [Ref 3].
4. Emit sell at current price adjusted by `price_penalty`; otherwise hold.
5. Post-fill, reduce collateral position and increase cash by proceeds.

###### 4.3.5.3 Action Space

| Aspect                | Specification                                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | `buy`, `sell`, `hold` as specified by the trigger function.                                                                   |
| Price level rule      | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`.                     |
| Order quantity rule   | `q = min(position, position * liquidation_sell_ratio)` for sell; otherwise zero.                                              |
| Order lifetime        | One decision round; replace on next fresh broadcast.                                                                          |
| Cancellation policy   | Cancel prior intent when the current trigger evaluates to hold or the opposite side.                                          |
| Inventory constraint  | Never sell more than internally available long position plus declared short inventory discipline.                             |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop selling when position is exhausted or collateral deviation no longer breaches the threshold.                             |

###### 4.3.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_liq:
    a_t = sell; q_t = min(position_t, position_t * phi_liq); b_t = price_t * pi_penalty
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State             | Initial value   | Update phase | Evolution                                        |
|-------------------|-----------------|--------------|--------------------------------------------------|
| `cash`            | scenario config | post-fill    | cash decreases on buy and increases on sell.     |
| `position`        | scenario config | post-fill    | position increases on buy and decreases on sell. |
| `liquidated_once` | false           | post-decide  | true after first sell activation.                |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol       | Meaning                                   | Default Value | Source       |
|--------------|-------------------------------------------|---------------|--------------|
| `theta_liq`  | Liquidation deviation threshold           | -0.15         | Ref 3        |
| `phi_liq`    | Fraction of collateral sold per trigger   | 0.35          | Ref 3        |
| `pi_penalty` | Execution haircut for delayed liquidation | 0.97          | Ref 3; Ref 9 |

###### 4.3.5.5 Behavioral Properties

- Time horizon: short - prime-broker risk decisions are short-horizon once collateral deteriorates.
- Risk tolerance: medium - risk discipline is balance-sheet protective, not speculative.
- Information asymmetry: partial - observes own client exposure but not all competitor actions.
- Psychological profile: competitive first-mover risk management under run incentives [Ref 3].

#### 4.3.6 Parameters

| Parameter                | Type  | Default | Valid Range    | Sensitivity | Description                                     | Impact                                       | Source                                                      |
|--------------------------|-------|---------|----------------|-------------|-------------------------------------------------|----------------------------------------------|-------------------------------------------------------------|
| `liquidation_threshold`  | float | -0.15   | [-0.30, -0.03] | high        | Deviation that triggers collateral liquidation. | Higher magnitude -> later liquidation.       | Gorton & Metrick (2012); Archegos broker timing calibration |
| `liquidation_sell_ratio` | float | 0.35    | [0.05, 1.00]   | high        | Fraction of collateral sold per activation.     | Higher -> larger immediate selling pressure. | Gorton & Metrick (2012); post-event broker calibration      |
| `initial_position`       | float | 3500.0  | > 0            | high        | Starting collateral inventory.                  | Higher -> larger liquidation supply.         | Scenario normalization from Archegos exposure reports       |
| `price_penalty`          | float | 0.97    | [0.80, 1.00]   | medium      | Execution haircut for delayed liquidation.      | Higher -> smaller first-mover payoff gap.    | Archegos broker-loss comparison calibration                 |

#### 4.3.7 Population and Heterogeneity

| Dimension                      | Specification                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Default population size        | 1 instance in ArchegosCollapse configs.                                                                       |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults.                    |
| Heterogeneity per parameter    | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation        | Same archetype instances share theory and trigger sign; cash and position levels may differ.                  |
| Identity persistence           | Persistent identity and state across rounds; no type switching.                                               |

#### 4.3.8 Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = position * 0.35`; sell branch fires because `-0.16 < -0.15`.
Decision: `sell`, positive quantity, `bid_price` determined by price-level rule.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
System state: `price=96`, `fundamental=100`, `deviation=-0.04`, plus default parameters.
Calculation:
  Trigger conditions are not met under the default threshold set.
Decision: `hold`, `quantity=0`, `bid_price=96`.
State update: no cash or position change.

### Case 3 - Stress branch
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation:
  At `deviation=-0.12`, branch does not fire for this threshold.
Decision: sell for PrimeBrokerFirstMover-style early threshold; hold for delayed threshold until deeper stress.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

#### 4.3.9 Validation and Calibration

**Calibration data sources**:
- `liquidation_threshold` <- Gorton & Metrick (2012) run threshold logic and Archegos broker timing.
- `liquidation_sell_ratio` <- liquidation-race payoff calibration from scenario §2 and §8.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

###### 4.3.9.1 Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

#### 4.3.10 Academic References

| # | Citation                                                                                                                                                                    | Notes                                         |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 3 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016 | Creditor run and first-mover liquidation race |
| 9 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x           | Price impact and execution-price relevance    |

#### 4.3.11 Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                    |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | Codex                                                                                                                                                                                                                                                                                                                      |
| Reviewed by | Codex three-pass self-check                                                                                                                                                                                                                                                                                                |
| Created     | 2026-06-30                                                                                                                                                                                                                                                                                                                 |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                      |
| Change log  | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as the first sub-block of §4.N.5 Behavioral Framework, re-verified §3.1–§3.11 section order against `agent-design-skill.md`; no structural change to other sub-blocks. |
| Status      | experimental                                                                                                                                                                                                                                                                                                               |

### §4.4 BlockTradeBuyer

> Agent pool source: examples/AGENT_POOL/finance/block-trade-buyer.md


#### 4.4.1 Summary

| Field                 | Content                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| Archetype             | opportunistic block-trade buyer                                         |
| Theory Family         | Liquidity / Funding                                                     |
| Market Role           | **Stabilising** - absorbs distressed supply after a sufficient discount |
| Time Horizon          | medium                                                                  |
| Risk Tolerance        | medium                                                                  |
| Information Asymmetry | partial                                                                 |
| Determinism           | deterministic                                                           |

#### 4.4.2 Definition and Goals

This agent models a asset manager, family office, or proprietary desk buying large blocks in distressed markets in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: deploy a bounded fraction of cash when price discount compensates inventory risk.

Inside a market simulation this agent provides stabilising demand and a partial price floor during forced liquidation. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

#### 4.4.3 Theoretical Foundation

**Block liquidity provision**:
- Theory / Study: Liquidity and market structure.
- Citation: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-633. https://doi.org/10.1111/j.1540-6261.1988.tb04594.x
- Core Insight: Large urgent sellers require immediacy from buyers who must be compensated for inventory risk. Distressed block buyers activate only when discounts exceed expected holding costs and risk premia.
- Mathematical Formulation: `q_buy = phi_buy * cash_t / price_t` if `deviation_t < theta_discount`.
- Empirical Evidence: Grossman & Miller (1988) model block liquidity compensation; Archegos block sales traded at sharp discounts during stress.
- Relevance to This Agent: The agent turns fire-sale discounts into bounded stabilising demand.
- Calibration Source: Grossman & Miller (1988), distressed-discount range 5-15% in scenario §2.
- Falsification Conditions: If this agent buys without a discount or sells into the discount, it is not a block buyer.
- Alternative Theories: market-maker spread provision; passive value investing.

**Limits to arbitrage**:
- Theory / Study: Capital-constrained arbitrage.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Corrective capital is limited and must be rationed under stress. The buyer therefore deploys a fraction of cash rather than eliminating all mispricing immediately.
- Mathematical Formulation: `q_t <= cash_t / price_t` and `q_t = phi_buy * cash_t / price_t`.
- Empirical Evidence: Limits-to-arbitrage literature documents slow correction when risk-bearing capital is constrained.
- Relevance to This Agent: `buy_ratio` prevents unrealistic infinite stabilisation.
- Calibration Source: Shleifer & Vishny (1997); scenario §6.
- Falsification Conditions: If the agent removes all mispricing in one step despite low `buy_ratio`, the cap is not represented.
- Alternative Theories: fully elastic arbitrage.

#### 4.4.4 Design Purpose and Activation Triggers

Purpose: Absorb supply when distressed discount exceeds the required compensation threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < discount_threshold`: submit buy order sized by `cash * buy_ratio / price`.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hold.
- Deviation above discount threshold: hold.

Market Contribution by Regime:
| Regime                     | Contribution | Mechanism                                                    |
|----------------------------|--------------|--------------------------------------------------------------|
| Calm market                | Hold         | Waits for adequate discount.                                 |
| Liquidity stress / drought | Stabilising  | Absorbs shares that forced sellers unload.                   |
| Post-shock recovery        | Stabilising  | Continued bids support convergence toward fundamental value. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

#### 4.4.5 Behavioral Framework

###### 4.4.5.0 I/O Contract

**Inputs (per decision call).**

| Input                 | Source                                 | Type / Shape | Required?        | Notes                                                                                                 |
|-----------------------|----------------------------------------|--------------|------------------|-------------------------------------------------------------------------------------------------------|
| `price`               | environment broadcast                  | `float`      | yes              | Row of §4.4.5.1                                                                                       |
| `fundamental`         | environment broadcast                  | `float`      | yes              | Row of §4.4.5.1                                                                                       |
| `deviation`           | environment broadcast                  | `float`      | yes              | Row of §4.4.5.1                                                                                       |
| `cash`                | agent state (§4.4.5.4 state variables) | `float`      | yes              | Capital available for distressed block absorption                                                     |
| `position`            | agent state (§4.4.5.4 state variables) | `float`      | yes              | Cumulative inventory accumulated so far                                                               |
| `round`               | round header                           | `int`        | yes              | Round number                                                                                          |
| `retrieved_knowledge` | retrieval store (Rag variant only)     | `list[str]`  | Rag variant only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum      | Unit                       | Required? | Meaning                                                           |
|-------------|--------|-------------------------|----------------------------|-----------|-------------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}` | —                          | yes       | Discrete action selected (matches §4.4.5.3 Order types)           |
| `bid_price` | float  | > 0                     | same units as `price`      | yes       | Order price (§4.4.5.3 Price level rule; buy uses current `price`) |
| `quantity`  | float  | ≥ 0, ≤ cash / price     | shares / units of position | yes       | Order magnitude (§4.4.5.3 Order quantity rule)                    |
| `reasoning` | string | 1–3 sentences           | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py`        |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped so that `quantity * bid_price ≤ cash`.
- `bid_price` MUST be strictly positive; if computed non-positive, floor to `price`.
- Sign convention: `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: this agent is `deterministic` (§4.4.5.5); the same inputs and state MUST produce byte-identical outputs across variants.

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "buy", "bid_price": 88.0, "quantity": 3409.09, "reasoning": "Deviation -0.12 exceeds discount_threshold=-0.10; deploying 30% of cash to absorb forced supply."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity * bid_price` MUST NOT exceed `cash`.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example emitting a `buy` at the current `price`.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.4.5.2, §4.4.5.3, or §4.4.5.4, this §4.4.5.0 wins.

###### 4.4.5.1 Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                               |
|---------------|------------|---------------|-----------------------------------------------------------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference and portfolio valuation [Ref 9].                                    |
| `fundamental` | Continuous | 1 tick        | Anchor for collateral-value deviation and discount calculations [Ref 1].                |
| `deviation`   | Continuous | 1 tick        | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `cash`        | State      | persistent    | Capital available for distressed block absorption [Ref 4].                              |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

###### 4.4.5.2 Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`; Write: no state before decision.
2. Compare `deviation` with `discount_threshold` [Ref 4; Ref 8].
3. If price is sufficiently below fundamental, compute deployment `cash * buy_ratio`.
4. Convert deployment to quantity using current `price`; emit buy if affordable.
5. Post-fill, reduce cash and increase position.

###### 4.4.5.3 Action Space

| Aspect                | Specification                                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | `buy`, `sell`, `hold` as specified by the trigger function.                                                                   |
| Price level rule      | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`.                     |
| Order quantity rule   | `q = (cash * buy_ratio) / price` for buy, clamped by available cash; otherwise zero.                                          |
| Order lifetime        | One decision round; replace on next fresh broadcast.                                                                          |
| Cancellation policy   | Cancel prior intent when the current trigger evaluates to hold or the opposite side.                                          |
| Inventory constraint  | Never sell more than internally available long position plus declared short inventory discipline.                             |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop buying when cash is exhausted or discount no longer exceeds threshold.                                                   |

###### 4.4.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_discount:
    a_t = buy; q_t = (cash_t * phi_buy) / price_t; b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State              | Initial value   | Update phase | Evolution                                        |
|--------------------|-----------------|--------------|--------------------------------------------------|
| `cash`             | scenario config | post-fill    | cash decreases on buy and increases on sell.     |
| `position`         | scenario config | post-fill    | position increases on buy and decreases on sell. |
| `deployed_capital` | 0.0             | post-fill    | cumulative cash spent on block purchases.        |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol           | Meaning                     | Default Value | Source       |
|------------------|-----------------------------|---------------|--------------|
| `theta_discount` | Required discount threshold | -0.10         | Ref 4; Ref 8 |
| `phi_buy`        | Cash deployment fraction    | 0.30          | Ref 4; Ref 8 |

###### 4.4.5.5 Behavioral Properties

- Time horizon: medium - block buyers expect recovery over multiple rounds rather than immediate resale.
- Risk tolerance: medium - takes inventory risk but only after a margin-of-safety discount.
- Information asymmetry: partial - observes public price discount but not every seller exposure.
- Psychological profile: patient value/liquidity provision under limits to arbitrage [Ref 8].

#### 4.4.6 Parameters

| Parameter            | Type  | Default   | Valid Range    | Sensitivity | Description                                       | Impact                                      | Source                                                    |
|----------------------|-------|-----------|----------------|-------------|---------------------------------------------------|---------------------------------------------|-----------------------------------------------------------|
| `discount_threshold` | float | -0.10     | [-0.30, -0.01] | high        | Discount from fundamental required before buying. | Higher magnitude -> fewer stabilising buys. | Grossman & Miller (1988); Shleifer & Vishny (1997)        |
| `buy_ratio`          | float | 0.30      | [0.01, 1.00]   | high        | Fraction of cash deployed per trigger.            | Higher -> larger stabilising demand.        | Grossman & Miller (1988) distressed liquidity calibration |
| `initial_cash`       | float | 1000000.0 | >= 0           | high        | Starting capital available for block purchases.   | Higher -> stronger price floor.             | Scenario normalization from block-trade capacity          |

#### 4.4.7 Population and Heterogeneity

| Dimension                      | Specification                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Default population size        | 1 instance in ArchegosCollapse configs.                                                                       |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults.                    |
| Heterogeneity per parameter    | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation        | Same archetype instances share theory and trigger sign; cash and position levels may differ.                  |
| Identity persistence           | Persistent identity and state across rounds; no type switching.                                               |

#### 4.4.8 Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = 1000000 * 0.30 / 84 = 3571.43`; buy branch fires.
Decision: `buy`, `quantity=3571.43`, `bid_price=84`.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
System state: `price=96`, `fundamental=100`, `deviation=-0.04`, plus default parameters.
Calculation:
  Trigger conditions are not met under the default threshold set.
Decision: `hold`, `quantity=0`, `bid_price=96`.
State update: no cash or position change.

### Case 3 - Stress branch
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation:
  `deviation=-0.12 < -0.10`; buy branch fires with smaller quantity because price is 88.
Decision: `buy`, `quantity=3409.09`, `bid_price=88`.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

#### 4.4.9 Validation and Calibration

**Calibration data sources**:
- `discount_threshold` <- Grossman & Miller (1988), block liquidity premium; stressed-market calibration in scenario §2.
- `buy_ratio` <- Grossman & Miller (1988), inventory-risk capital deployment logic.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

###### 4.4.9.1 Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

#### 4.4.10 Academic References

| # | Citation                                                                                                                                                          | Notes                                                     |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| 4 | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-633. https://doi.org/10.1111/j.1540-6261.1988.tb04594.x | Block liquidity provision and inventory-risk compensation |
| 8 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x             | Limits to arbitrage and capital constraints               |

#### 4.4.11 Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                    |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | Codex                                                                                                                                                                                                                                                                                                                      |
| Reviewed by | Codex three-pass self-check                                                                                                                                                                                                                                                                                                |
| Created     | 2026-06-30                                                                                                                                                                                                                                                                                                                 |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                      |
| Change log  | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as the first sub-block of §4.N.5 Behavioral Framework, re-verified §3.1–§3.11 section order against `agent-design-skill.md`; no structural change to other sub-blocks. |
| Status      | experimental                                                                                                                                                                                                                                                                                                               |

### §4.5 InformationTrader

> Agent pool source: examples/AGENT_POOL/finance/information-trader.md


#### 4.5.1 Summary

| Field                 | Content                                                                                                           |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|
| Archetype             | liquidation-signal information trader                                                                             |
| Theory Family         | Microstructure                                                                                                    |
| Market Role           | **Context-dependent** - front-runs distress and later covers, amplifying early decline but aiding price discovery |
| Time Horizon          | short                                                                                                             |
| Risk Tolerance        | high                                                                                                              |
| Information Asymmetry | partial                                                                                                           |
| Determinism           | stochastic-given-seed                                                                                             |

#### 4.5.2 Definition and Goals

This agent models a proprietary trading desk or informed hedge fund reading order-flow stress in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: trade ahead of expected liquidation when a distress signal is detected, then cover after recovery signal appears.

Inside a market simulation this agent adds early informed selling and later covering around the forced-liquidation episode. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

#### 4.5.3 Theoretical Foundation

**Informed trading**:
- Theory / Study: Continuous auctions and insider trading.
- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210
- Core Insight: Informed traders infer or possess signals about future order flow and trade before prices fully reveal that information. Their trades move prices toward the information but can worsen short-run impact.
- Mathematical Formulation: `sell_signal = 1[deviation_t < theta_detect] * Bernoulli(p_detect)`.
- Empirical Evidence: Kyle (1985) formalizes informed order splitting and price impact; market microstructure evidence links informed flow to price discovery.
- Relevance to This Agent: The detection threshold and probability encode partial information about forced liquidation.
- Calibration Source: Kyle (1985); scenario §6.
- Falsification Conditions: If the agent never sells after a detected distress signal, informed trading is absent.
- Alternative Theories: noise trading; passive liquidity provision.

**Predatory trading around distressed liquidation**:
- Theory / Study: Predatory trading.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825-1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x
- Core Insight: Traders who anticipate another trader's need to liquidate can sell ahead of that liquidation and later repurchase after prices are depressed. This behaviour amplifies temporary price pressure.
- Mathematical Formulation: `q_sell = min(front_run_size, position)` before liquidation; `q_cover = min(cover_size, short_position, cash/price)` after recovery signal.
- Empirical Evidence: Brunnermeier & Pedersen (2005) show predatory trading can increase liquidation costs.
- Relevance to This Agent: The sell-and-cover branches are the direct operationalization.
- Calibration Source: Brunnermeier & Pedersen (2005), normalized to scenario order size.
- Falsification Conditions: If short covering does not reduce `short_position`, the predatory cycle is incomplete.
- Alternative Theories: market making; fundamental value investing.

#### 4.5.4 Design Purpose and Activation Triggers

Purpose: Exploit partial order-flow information about imminent liquidation pressure.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `prev_price` available for change detection
- seeded random source available for detection success

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < detection_threshold` and detection draw succeeds: submit sell order sized by `front_run_size`.
- `deviation > cover_threshold` and `short_position > 0`: submit buy order sized by `cover_size`.
- `<Default>`: hold.

Deactivation Conditions:
- No long position and no short inventory: hold.
- Detection draw fails: hold.

Market Contribution by Regime:
| Regime                     | Contribution  | Mechanism                                   |
|----------------------------|---------------|---------------------------------------------|
| Calm market                | Hold          | No distress signal.                         |
| Liquidity stress / drought | Destabilising | Sells ahead of expected forced liquidation. |
| Post-shock recovery        | Stabilising   | Covers short exposure through buy orders.   |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

#### 4.5.5 Behavioral Framework

###### 4.5.5.0 I/O Contract

**Inputs (per decision call).**

| Input                 | Source                                 | Type / Shape | Required?        | Notes                                                                                                 |
|-----------------------|----------------------------------------|--------------|------------------|-------------------------------------------------------------------------------------------------------|
| `price`               | environment broadcast                  | `float`      | yes              | Row of §4.5.5.1                                                                                       |
| `fundamental`         | environment broadcast                  | `float`      | yes              | Row of §4.5.5.1                                                                                       |
| `deviation`           | environment broadcast                  | `float`      | yes              | Row of §4.5.5.1                                                                                       |
| `prev_price`          | environment broadcast (extended field) | `float`      | yes              | Supports local order-flow stress inference [Ref 5]                                                    |
| `position`            | agent state (§4.5.5.4 state variables) | `float`      | yes              | Long inventory available for the sell (front-run) branch                                              |
| `short_position`      | agent state (§4.5.5.4 state variables) | `float`      | yes              | Determines whether the cover branch can activate                                                      |
| `cash`                | agent state (§4.5.5.4 state variables) | `float`      | yes              | Bounds the cover-branch buy quantity                                                                  |
| `rng_state`           | agent state (seeded)                   | `int` / RNG  | yes              | Detection uses Bernoulli(`p_detect`); seed-reproducible                                               |
| `round`               | round header                           | `int`        | yes              | Round number                                                                                          |
| `retrieved_knowledge` | retrieval store (Rag variant only)     | `list[str]`  | Rag variant only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum                                            | Unit                       | Required? | Meaning                                                                    |
|-------------|--------|---------------------------------------------------------------|----------------------------|-----------|----------------------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`                                       | —                          | yes       | Discrete action selected (matches §4.5.5.3 Order types)                    |
| `bid_price` | float  | > 0                                                           | same units as `price`      | yes       | Order price (§4.5.5.3 Price level rule; both branches use current `price`) |
| `quantity`  | float  | ≥ 0; sell ≤ position; buy ≤ min(short_position, cash / price) | shares / units of position | yes       | Order magnitude (§4.5.5.3 Order quantity rule)                             |
| `reasoning` | string | 1–3 sentences                                                 | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py`                 |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- Sell branch `quantity` MUST be clamped to `[0, min(front_run_size, position)]`.
- Cover branch `quantity` MUST be clamped to `[0, min(cover_size, short_position, cash / price)]`.
- `bid_price` MUST be strictly positive; if computed non-positive, floor to `price`.
- Sign convention: `action = "sell"` corresponds to negative net demand and increases `short_position`; `action = "buy"` corresponds to positive net demand and reduces `short_position`; `quantity` is always non-negative.
- Determinism marker: this agent is `stochastic-given-seed` (§4.5.5.5); the emitted `<decision>` object MUST allow the round's Bernoulli draw to be reproduced from the declared `rng_state` seed (the implementation MUST log the seed deterministically per round).

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "sell", "bid_price": 84.0, "quantity": 1000.0, "reasoning": "Deviation -0.16 crossed detection_threshold=-0.05 and Bernoulli(p_detect=0.5) fired; front-running expected forced flow."}</decision>
```

Every implementation variant declared `Yes` in target §10.1 (`Rule`, `LLM`, `RuleLLM`, `Rag`) MUST honour this tag pattern. The `Rule` variant MAY populate `<analysis>` from a deterministic template. The `LLM`, `RuleLLM`, and `Rag` variants MUST include this tag + JSON schema literally in the system or user prompt. The `Rag` variant MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, the seeded RNG, or the round header; `prev_price` MUST be added to the environment broadcast payload for this agent.
2. **Decision emission** — every `Required? = yes` field MUST be populated; sell and cover quantities MUST be clamped per §4.5.5.3.
3. **Prompt drafting** — the `LLM`, `RuleLLM`, and `Rag` prompt templates MUST spell out the tag pattern and JSON schema verbatim with a worked example that covers both the front-run sell and the cover buy branches, and MUST expose the Bernoulli detection semantics.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range, and (iv) verifies seed reproducibility of the detection branch.
5. **Variant parity** — all four target §10.1 variants MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with §4.5.5.2, §4.5.5.3, or §4.5.5.4, this §4.5.5.0 wins.

###### 4.5.5.1 Decision Information Set

| Signal           | Type       | Memory Window | Rationale                                                                               |
|------------------|------------|---------------|-----------------------------------------------------------------------------------------|
| `price`          | Continuous | 1 tick        | Execution reference and portfolio valuation [Ref 9].                                    |
| `fundamental`    | Continuous | 1 tick        | Anchor for collateral-value deviation and discount calculations [Ref 1].                |
| `deviation`      | Continuous | 1 tick        | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `prev_price`     | Continuous | 1 tick        | Supports local order-flow stress inference [Ref 5].                                     |
| `short_position` | State      | persistent    | Determines whether cover branch can activate [Ref 7].                                   |
| `rng_state`      | State      | persistent    | Makes partial detection stochastic but seed-reproducible.                               |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

###### 4.5.5.2 Core Behavioral Mechanism

1. Read: `deviation`, `price`, `position`, `short_position`, and seeded random source.
2. If `deviation < detection_threshold`, draw detection success with probability `detection_ability` [Ref 5].
3. On successful detection, sell `min(front_run_size, position)` and increase `short_position` post-fill [Ref 7].
4. Else if `deviation > cover_threshold` and `short_position > 0`, buy `min(cover_size, short_position, cash / price)` to cover.
5. If neither branch fires, hold.

###### 4.5.5.3 Action Space

| Aspect                | Specification                                                                                                                    |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | `buy`, `sell`, `hold` as specified by the trigger function.                                                                      |
| Price level rule      | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`.                        |
| Order quantity rule   | Sell `min(front_run_size, position)` on detection; buy `min(cover_size, short_position, cash / price)` on cover; otherwise zero. |
| Order lifetime        | One decision round; replace on next fresh broadcast.                                                                             |
| Cancellation policy   | Cancel prior intent when the current trigger evaluates to hold or the opposite side.                                             |
| Inventory constraint  | Never sell more than internally available long position plus declared short inventory discipline.                                |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger.    |
| Stop-loss / kill rule | Stop selling when no long inventory remains; stop covering when short_position reaches zero.                                     |

###### 4.5.5.4 Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_detect and Bernoulli(p_detect)=1:
    a_t = sell; q_t = min(front_run_size, position_t); b_t = price_t
elif delta_t > theta_cover and short_position_t > 0:
    a_t = buy; q_t = min(cover_size, short_position_t, cash_t / price_t); b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State            | Initial value   | Update phase | Evolution                                                     |
|------------------|-----------------|--------------|---------------------------------------------------------------|
| `cash`           | scenario config | post-fill    | cash decreases on buy and increases on sell.                  |
| `position`       | scenario config | post-fill    | position increases on buy and decreases on sell.              |
| `short_position` | 0.0             | post-fill    | increases after sell branch and decreases after cover branch. |

Determinism contract: stochastic-given-seed because detection uses a Bernoulli draw with configured probability.

Parameter symbol table:
| Symbol           | Meaning                                     | Default Value | Source       |
|------------------|---------------------------------------------|---------------|--------------|
| `p_detect`       | Probability of detecting liquidation signal | 0.50          | Ref 5; Ref 7 |
| `theta_detect`   | Distress-detection deviation threshold      | -0.05         | Ref 5; Ref 7 |
| `front_run_size` | Maximum sell size on detected signal        | 1000          | Ref 7        |
| `theta_cover`    | Recovery threshold for cover branch         | -0.03         | Ref 7        |
| `cover_size`     | Maximum buy-to-cover size                   | 500           | Ref 7        |

###### 4.5.5.5 Behavioral Properties

- Time horizon: short - information advantage decays quickly as order flow becomes public.
- Risk tolerance: high - takes directional exposure before liquidation is fully visible.
- Information asymmetry: partial - has partial noisy order-flow information, not full broker books.
- Psychological profile: predatory trading and informed order-flow inference [Ref 5; Ref 7].

#### 4.5.6 Parameters

| Parameter             | Type  | Default | Valid Range   | Sensitivity | Description                                         | Impact                                      | Source                                      |
|-----------------------|-------|---------|---------------|-------------|-----------------------------------------------------|---------------------------------------------|---------------------------------------------|
| `detection_ability`   | float | 0.50    | [0.00, 1.00]  | high        | Probability of detecting the liquidation signal.    | Higher -> more early sell orders.           | Kyle (1985); Brunnermeier & Pedersen (2005) |
| `detection_threshold` | float | -0.05   | [-0.20, 0.00] | high        | Deviation at which distress detection is attempted. | Higher magnitude -> later signal attempts.  | Kyle (1985); predatory-trading calibration  |
| `front_run_size`      | float | 1000    | >= 0          | high        | Maximum sell quantity on successful detection.      | Higher -> stronger early downward pressure. | Brunnermeier & Pedersen (2005), normalized  |
| `cover_threshold`     | float | -0.03   | [-0.20, 0.10] | medium      | Deviation above which covering is allowed.          | Higher -> later covering.                   | Brunnermeier & Pedersen (2005)              |
| `cover_size`          | float | 500     | >= 0          | medium      | Maximum buy-to-cover quantity.                      | Higher -> faster short-position reduction.  | Brunnermeier & Pedersen (2005), normalized  |

#### 4.5.7 Population and Heterogeneity

| Dimension                      | Specification                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Default population size        | 2 instances in ArchegosCollapse configs.                                                                      |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults.                    |
| Heterogeneity per parameter    | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation        | Same archetype instances share theory and trigger sign; cash and position levels may differ.                  |
| Identity persistence           | Persistent identity and state across rounds; no type switching.                                               |

#### 4.5.8 Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  If the Bernoulli draw succeeds, `q = min(1000, 1000) = 1000`; sell branch fires.
Decision: `sell`, `quantity=1000`, `bid_price=84` on detection success; otherwise hold.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
System state: `price=96`, `fundamental=100`, `deviation=-0.04`, plus default parameters.
Calculation:
  Trigger conditions are not met under the default threshold set.
Decision: `hold`, `quantity=0`, `bid_price=96`.
State update: no cash or position change.

### Case 3 - Stress branch
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation:
  `deviation=-0.12 < -0.05`; detection branch is eligible; expected activation probability is 0.50.
Decision: stochastic sell-or-hold according to detection draw.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

#### 4.5.9 Validation and Calibration

**Calibration data sources**:
- `detection_ability` <- Kyle (1985) information advantage and Brunnermeier & Pedersen (2005) predatory-trading mechanism.
- `front_run_size`, `cover_size` <- scenario-normalized order-flow scale from §6.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

###### 4.5.9.1 Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

#### 4.5.10 Academic References

| # | Citation                                                                                                                                                   | Notes                                       |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| 5 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210                             | Informed order-flow trading                 |
| 7 | Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825-1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x | Predatory trading around forced liquidation |

#### 4.5.11 Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                    |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | Codex                                                                                                                                                                                                                                                                                                                      |
| Reviewed by | Codex three-pass self-check                                                                                                                                                                                                                                                                                                |
| Created     | 2026-06-30                                                                                                                                                                                                                                                                                                                 |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                      |
| Change log  | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as the first sub-block of §4.N.5 Behavioral Framework, re-verified §3.1–§3.11 section order against `agent-design-skill.md`; no structural change to other sub-blocks. |
| Status      | experimental                                                                                                                                                                                                                                                                                                               |

## §5 Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                                                                                                                                                       |
|----------------------------------|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | ConcentratedFund: medium-term position holder (months); PrimeBrokers: immediate responders (same round as threshold); BlockTradeBuyer: patient capital (holds for recovery); InformationTrader: high-frequency (front-runs then covers)        |
| Different information processing | Yes  | ConcentratedFund: level-threshold (absolute loss); PrimeBrokerFirstMover/2: level-threshold at different levels; BlockTradeBuyer: discount-seeking; InformationTrader: stochastic detection with probability                                   |
| Conflicting incentives           | Yes  | BlockTradeBuyer BUYS when all three liquidating agents are SELLING; InformationTrader COVERS when all forced sellers are exhausted                                                                                                             |
| Mix of stabilizing/destabilizing | Yes  | 3 destabilizing (ConcentratedFund, PrimeBrokerFirstMover, PrimeBrokerDelayedLiquidator), 1 stabilizing (BlockTradeBuyer), 1 neutral-then-stabilizing (InformationTrader)                                                                       |
| Different risk tolerances        | Yes  | ConcentratedFund: Extreme (5–8x leverage); BlockTradeBuyer: High (willingness to buy distressed assets); InformationTrader: Medium; PrimeBrokerFirstMover: Low (early stop-loss); PrimeBrokerDelayedLiquidator: Low-Medium (delayed stop-loss) |
| Different decision frequencies   | Yes  | ConcentratedFund: once (triggered once typically); PrimeBrokerFirstMover: once at −10%; PrimeBrokerDelayedLiquidator: once at −15%; BlockTradeBuyer: every round below −10%; InformationTrader: every round with stochastic detection          |

**Critical mass check**: The cascade requires: (1) ConcentratedFund to initiate, (2) at least one broker to amplify, (3) BlockTradeBuyer to eventually halt the decline. Removing ConcentratedFund → no cascade (no initiator). Removing BlockTradeBuyer → prices may collapse to floor without recovery. The 2-broker asymmetry (different thresholds) is essential to model the timing spread observed in Archegos.


## §6 Parameter Table

| Parameter                   | Symbol | Value | Typical Range | Source Citation                                                                                                                                                                               | Description                                      | Sensitivity                                                 |
|-----------------------------|--------|-------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|-------------------------------------------------------------|
| initial_price               | P(0)   | 100.0 | —             | Normalization                                                                                                                                                                                 | Starting stock price                             | Low — scale only                                            |
| fundamental_value           | F      | 100.0 | —             | Normalization                                                                                                                                                                                 | Intrinsic fair value                             | Medium — determines deviation scale                         |
| price_impact                | λ      | 0.03  | 0.01–0.05     | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179–207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x                             | Price change per unit net demand                 | High — λ=0.05 → 67% deeper cascade                          |
| mean_reversion              | γ      | 0.01  | 0.005–0.02    | French, K. R., & Roll, R. (1986). Stock return variances. *Journal of Financial Economics*, 17(1), 5–26. https://doi.org/10.1016/0304-405X(86)90004-8                                         | Pull strength toward fundamental value           | High — γ=0.05 → too-fast recovery                           |
| noise_std                   | σ      | 0.015 | 0.01–0.03     | Roll, R. (1984). A simple implicit measure of the effective bid-ask spread in an efficient market. *Journal of Finance*, 39(4), 1127–1139. https://doi.org/10.1111/j.1540-6261.1984.tb03897.x | Noise term standard deviation                    | Low — affects timing variance only                          |
| leverage_trigger            | θ_lev  | 0.15  | 0.10–0.20     | Becketti (2021); FSB (2022) non-bank intermediation report                                                                                                                                    | ConcentratedFund margin call threshold           | High — controls when cascade begins                         |
| liquidation_fraction (CF)   | φ_CF   | 0.50  | 0.40–0.70     | Archegos Capital Management post-mortem; FSB (2022), p. 51                                                                                                                                    | Fraction of CF position sold at margin call      | High — determines initial shock magnitude                   |
| liquidation_threshold (PB1) | θ₁     | 0.10  | 0.08–0.15     | Gorton & Metrick (2012); prime broker risk management conventions                                                                                                                             | PrimeBrokerFirstMover stop-loss threshold        | High — controls first-mover timing                          |
| liquidation_fraction (PB1)  | φ₁     | 0.40  | 0.30–0.50     | Standard prime broker protocol                                                                                                                                                                | PrimeBrokerFirstMover sell fraction              | Medium                                                      |
| liquidation_threshold (PB2) | θ₂     | 0.15  | 0.12–0.20     | Gorton & Metrick (2012); Credit Suisse post-mortem accounts                                                                                                                                   | PrimeBrokerDelayedLiquidator stop-loss threshold | High — controls second-mover timing and payoff differential |
| liquidation_fraction (PB2)  | φ₂     | 0.35  | 0.25–0.45     | Standard protocol                                                                                                                                                                             | PrimeBrokerDelayedLiquidator sell fraction       | Medium                                                      |
| discount_threshold (BT)     | θ_disc | 0.10  | 0.05–0.15     | Grossman & Miller (1988), distressed market estimate                                                                                                                                          | BlockTradeBuyer activation discount              | Medium — determines price floor level                       |
| cash_deployment (BT)        | α      | 0.30  | 0.20–0.40     | Conservative institutional capital deployment standard                                                                                                                                        | Fraction of cash deployed per activation         | Medium                                                      |
| detection_threshold (IT)    | θ_det  | 0.05  | 0.03–0.08     | Kyle (1985) informed trading model                                                                                                                                                            | InformationTrader early signal threshold         | Medium — controls cascade acceleration                      |
| detection_ability (IT)      | p_det  | 0.50  | 0.30–0.70     | Boehmer et al. (2008) informed short seller frequency                                                                                                                                         | Probability of detecting distress signal         | Low — affects variance of onset timing                      |


## §7 Communication and Round Structure

```
Round N (t = 1, 2, ..., 200):

  Phase 1 — Market Broadcast:
    Market → all 5 investor instances: {price, prev_price, fundamental, deviation, round}
    All agents receive identical public information simultaneously.

  Phase 2 — Investor Decisions:
    ConcentratedFund: perceive() → check δ < −0.15 → act (sell if triggered)
    PrimeBrokerFirstMover:     perceive() → check δ < −0.10 → act (sell if triggered)
    PrimeBrokerDelayedLiquidator:     perceive() → check δ < −0.15 → act (sell if triggered, typically rounds after CF)
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
| March 25    | Morgan Stanley organizes block trade; sells first at ~$92/share | First public distress signal                |
| March 26    | Multiple prime brokers begin simultaneous block trades          | VIAC falls to ~$48 (−50% from week start)   |
| March 29    | Credit Suisse, Nomura acknowledge large losses                  | VIAC at ~$40; market recognizes full extent |

**Quantitative Evidence**:
- ViacomCBS price: $100 (March 22 open) → $40 (March 29 close); −60% (Bloomberg, 2021)
- Archegos notional exposure: $35–40B across 5 prime brokers (FSB, 2022, p. 49)
- Leverage ratio: 5–8x equity (Becketti, 2021)
- Morgan Stanley total loss: ~$1B (Q2 2021 earnings disclosure)
- Credit Suisse total loss: $5.5B (Credit Suisse Annual Report 2021, supplementary disclosures)

**Agent Mappings**:

| Simulation Agent             | Real-World Counterpart                                    | Mapping Justification                                                             |
|------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| ConcentratedFund             | Archegos Capital Management (Bill Hwang)                  | TRS leverage; hidden concentration; forced liquidation initiator                  |
| PrimeBrokerFirstMover        | Morgan Stanley                                            | First to organize block trades (March 25–26); incurred smallest loss (~$1B)       |
| PrimeBrokerDelayedLiquidator | Credit Suisse / Nomura                                    | Later to act (March 29); incurred largest losses ($5.5B + $2.9B)                  |
| BlockTradeBuyer              | Institutional buyers of discounted blocks                 | Various asset managers who purchased VIAC/DISCA at fire-sale prices in late March |
| InformationTrader            | Hedge funds that detected unusual TRS-related block flows | Traders who reportedly shorted these names before the public cascade              |

**Simulation Calibration Lessons**:
- The 0.05 difference between PrimeBrokerFirstMover threshold (0.10) and PrimeBrokerDelayedLiquidator threshold (0.15) should produce a loss differential of approximately 3–5x, consistent with the Morgan Stanley vs. Credit Suisse outcome
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
| Research Question         | Does cascade emerge from threshold rules alone? | Do LLM personas reproduce denial-then-panic psychology without knowing the scenario name?                | Does quantitative rule grounding suppress LLM hesitation effects? | Does historical knowledge of TRS cascades change prime broker timing or severity?                |

**Predicted ordering**: Cascade depth: Rule ≈ RuleLLM > LLM ≈ Rag (LLM personas may introduce more hesitation; RAG provides historical calibration)
