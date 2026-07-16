# Tax-aware investor

## Summary

| Field                 | Content                                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------------------|
| Archetype             | Tax-aware investor                                                                                        |
| Theory Family         | Tax-Optimal Portfolio Management / Neoclassical Finance                                                   |
| Behavioral Tendency   | **Converging** — realizes losses quickly and defers gains, acting as a stabilising counterweight to disposition-effect traders |
| Time Horizon          | medium                                                                                                    |
| Risk Tolerance        | medium                                                                                                    |
| Information Asymmetry | none                                                                                                      |
| Determinism           | deterministic                                                                                             |

## Definition and Goals

This agent models a tax-conscious investor who exploits the asymmetric tax treatment of realized gains versus losses by implementing a tax-loss harvesting strategy. The real-world counterpart is the high-net-worth individual or taxable account manager documented by Constantinides (1983) and implemented by modern direct-indexing platforms (Wealthfront, Betterment, Aperio). These investors constitute a significant portion of taxable equity accounts, particularly in the US where short-term/long-term capital gains tax differentials create harvesting incentives.

The decision goal is to realize losses quickly (harvesting the tax deduction) while deferring gains as long as possible (postponing capital gains tax liability). The agent emits sell orders when unrealized losses exceed the tax-loss threshold and only sells winners when gains exceed a high capital-gains-hold threshold. The optimization criterion is after-tax wealth maximization through optimal timing of loss realization and gain deferral.

Inside the simulation this agent generates the mirror-image of disposition-effect behaviour — selling losers (providing sell-side pressure during drawdowns) and holding winners (reducing sell pressure during rallies). It acts as a stabilising counterweight to disposition populations. **Non-goals:** (1) The agent must NOT hold losing positions to avoid realization — this is the opposite of its mandate. (2) The agent must NOT use momentum, fundamental value, or technical signals — it trades purely on unrealized gain/loss relative to cost basis. (3) The agent must NOT engage in wash-sale violations (it does not repurchase within 30 days of a tax-loss sale in the same security).

## Theoretical Foundation

**Optimal Tax-Loss Harvesting**:
- Theory / Study: Capital market equilibrium with personal tax.
- Citation: Constantinides, G. M. (1983). Capital market equilibrium with personal tax. *Econometrica*, 51(3), 611-636. https://doi.org/10.2307/1912153
- Core Insight: In the presence of asymmetric tax treatment (losses deductible against income, gains taxed only upon realization), the optimal policy is to realize losses immediately upon occurrence and defer gains as long as possible. This creates an after-tax value advantage equivalent to an interest-free loan from the government.
- Mathematical Formulation: `harvest_signal = 1 if (price - cost_basis) / cost_basis < tax_loss_threshold else 0`; `defer_signal = 1 if (price - cost_basis) / cost_basis < capital_gains_hold else 0`
- Empirical Evidence: Constantinides (1983) proves the optimal policy analytically. Arnott et al. (2001) estimate tax-loss harvesting adds 0.5-1.5% annually after tax for typical US taxable accounts with turnover rate of 5-15%. Chaudhuri et al. (2020) find direct-indexing with harvesting generates alpha of 1.08% annually (n=10,000 Monte Carlo paths, 95% CI [0.82%, 1.34%]).
- Relevance to This Agent: The agent directly implements the Constantinides optimal policy — immediate loss realization and gain deferral — with thresholds calibrated to balance transaction costs against tax benefit.
- Calibration Source: Constantinides (1983) — optimal loss realization at any loss exceeding transaction costs (~1-5%); gain deferral until very large gains (15-25%). Arnott et al. (2001) Table 2 — threshold ranges for 28% tax bracket.
- Falsification Conditions: If the agent holds a position with unrealized loss > 2x tax_loss_threshold for more than 5 ticks without harvesting, its tax-optimal mandate is falsified.
- Alternative Theories: Disposition effect (opposite: holds losers, sells winners); passive buy-and-hold (no tax-aware trading); continuous-time optimal trading (Davis & Norman 1990).

**Tax-Deferred Investing and Optimal Asset Location**:
- Theory / Study: Optimal asset location and allocation with taxable and tax-deferred investing.
- Citation: Dammon, R. M., Spatt, C. S., & Zhang, H. H. (2004). Optimal asset location and allocation with taxable and tax-deferred investing. *Journal of Finance*, 59(3), 999-1037. https://doi.org/10.1111/j.1540-6261.2004.00655.x
- Core Insight: In a taxable account, the investor should actively manage tax lots to minimize lifetime tax burden. The marginal benefit of harvesting a loss is the tax rate times the loss amount, discounted at the after-tax rate. This creates a clear threshold: harvest when the tax benefit exceeds the transaction cost.
- Mathematical Formulation: `net_benefit = tax_rate * abs(unrealized_loss) - transaction_cost`; harvest when `net_benefit > 0`, equivalently when `abs(loss_pct) > transaction_cost / (tax_rate * cost_basis)`.
- Empirical Evidence: Dammon et al. (2004) find optimal harvesting increases certainty-equivalent wealth by 5-20 basis points per year depending on volatility and tax rate, using dynamic programming with 20-year horizons (Table III).
- Relevance to This Agent: Provides the theoretical justification for the high capital_gains_hold threshold — gains should only be realized when the benefit of portfolio adjustment exceeds the tax cost of realization.
- Calibration Source: Dammon et al. (2004) Table III — optimal gain realization threshold 15-25% for 20% capital gains tax rate; Arnott et al. (2001) — 0.5-1.5% annual alpha from systematic harvesting.
- Falsification Conditions: If the agent realizes gains below capital_gains_hold threshold without an overriding constraint (e.g. cash need), the deferral logic is falsified.
- Alternative Theories: Tax-neutral index rebalancing; mark-to-market taxation (eliminates deferral value); consumption-based optimal taxation.

## Design Purpose and Activation Triggers

Purpose: Realize tax losses immediately when unrealized loss exceeds threshold, and defer gains until they become very large, implementing the tax-optimal strategy that is the mirror-image of disposition-effect behaviour.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `cost_basis` available (own state)
- `position` available (own state)
- `cash` available (own state)

Missing-Signal Policy: hold when any required signal is unavailable or stale.

Activation Triggers:
- `gain_pct < tax_loss_threshold` (-0.05): sell `tax_harvest_fraction * position` (harvest tax loss).
- `gain_pct > capital_gains_hold` (0.20): sell `gain_sell_fraction * position` (realize large deferred gain).
- `<Default>`: hold (defer — either small loss not worth harvesting, or gain being deferred).

Deactivation Conditions:
- Position reaches zero: no further harvesting possible.
- All losses already harvested and gains below capital_gains_hold: hold indefinitely.

Behavioral Adaptation by Condition:
| Condition                       | Behavioral change                    | Mechanism                                |
|---------------------------------|--------------------------------------|------------------------------------------|
| Market drawdown (losses mount)  | Active selling to harvest losses     | Tax-loss threshold breached              |
| Sustained rally (gains grow)    | Hold until very high gain threshold  | Gain deferral maximizes tax benefit      |
| Flat market                     | Extended hold                        | Neither threshold breached               |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input        | Source      | Type / Shape | Required? | Notes                              |
|--------------|-------------|--------------|-----------|------------------------------------|
| `price`      | environment | float        | yes       | current market price               |
| `cost_basis` | own state   | float        | yes       | average purchase price (tax lot basis) |
| `position`   | own state   | float        | yes       | current shares held                |
| `cash`       | own state   | float        | yes       | available capital                  |
| `round`      | scheduler   | int          | yes       | current simulation round           |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                      |
|-------------|--------|---------------------------------|--------|-----------|------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | trade direction              |
| `quantity`  | float  | `>= 0`                         | shares | yes       | number of shares to trade    |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | audit trail for the decision |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` must be present on every call.
- Forbidden fields: no fields beyond the three declared.
- Value ranges: `quantity` clamped to `[0, position]` for sells.
- Units: quantity in shares; price in environment currency units.
- Sign conventions: positive quantity always; direction conveyed by `action` field.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning, 1-3 sentences...</analysis>
<decision>{"action": "buy|sell|hold", "quantity": 0.0, "reasoning": "..."}</decision>
```

Rules: (1) Tags are literal ASCII, not optional. (2) Decision block contains valid JSON matching Outputs table. (3) Rule-driven variants generate analysis from deterministic template. (4) Model-driven variants must include tag+JSON requirement in prompt.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth.** On conflict with prose elsewhere, this section wins. (1) Signal wiring: every input row maps to a real read. (2) Decision emission: populate all required fields, clamp out-of-range values. (3) Prompt drafting: spell out tag pattern and JSON schema literally. (4) Parser tests: verify tags, parse JSON, assert fields in range. (5) Variant parity: all variants produce same field set. (6) Contract wins on conflict.

#### Decision Information Set

| Signal       | Type       | Memory Window | Rationale                                          |
|--------------|------------|---------------|----------------------------------------------------|
| `price`      | Continuous | 1 tick        | Needed to compute unrealized gain/loss             |
| `cost_basis` | State      | persistent    | Tax lot basis — reference for gain/loss computation |
| `position`   | State      | persistent    | Determines harvest capacity                        |
| `cash`       | State      | persistent    | Tracks proceeds from harvesting                    |

Does NOT use: fundamental value, momentum signals, technical indicators, peer positions, volume, volatility, news, or tax-calendar signals. Decision is purely based on unrealized gain/loss relative to cost basis.

#### Core Behavioral Mechanism

1. **Read inputs.** Read `price`, `cost_basis`, `position`, `cash` from environment and own state. (Implementation convenience — no theoretical claim.)
2. **Compute gain percentage.** Calculate `gain_pct = (price - cost_basis) / cost_basis`. Read: price, cost_basis. Write: gain_pct (transient). [Traces to Constantinides (1983) — unrealized gain/loss evaluation.]
3. **Evaluate tax-loss harvest branch.** If `gain_pct < tax_loss_threshold`, compute `sell_qty = tax_harvest_fraction * position`, clamped to `[0, position]`. Read: gain_pct, tax_loss_threshold, tax_harvest_fraction, position. Write: action = sell, quantity = sell_qty. [Traces to Constantinides (1983) — immediate loss realization is optimal.]
4. **Evaluate gain realization branch.** If `gain_pct > capital_gains_hold`, compute `sell_qty = gain_sell_fraction * position`, clamped to `[0, position]`. Read: gain_pct, capital_gains_hold, gain_sell_fraction, position. Write: action = sell, quantity = sell_qty. [Traces to Dammon et al. (2004) — realize only very large gains.]
5. **Default hold (deferral).** If neither threshold breached, set action = hold, quantity = 0. Read: gain_pct, thresholds. Write: action, quantity. [Traces to Constantinides (1983) — gain deferral is optimal.]
6. **Update cost basis (post-execution).** After sell: cost_basis unchanged for remaining shares. After repurchase (if reinvestment enabled): weighted average update. Read: execution result. Write: cost_basis if applicable. [Traces to tax-lot accounting.]
7. **Emit decision object.** Serialize in canonical format. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                                |
|-----------------------|------------------------------------------------------------------------------|
| Action types allowed  | buy, sell, hold                                                              |
| Action parameter rule | market order at current price                                                |
| Sizing rule           | Loss harvest: `tax_harvest_fraction * position`. Gain realize: `gain_sell_fraction * position` |
| Action lifetime       | one decision call (immediate execution)                                      |
| Revision policy       | previous intent replaced each tick                                           |
| State constraint      | position >= 0 (no short selling)                                             |
| Resource cap          | sell quantity <= position                                                     |
| Exit rule             | none — agent continues to monitor for harvest opportunities indefinitely     |

#### Mathematical Model

**Decision output:** Action `a` in {buy, sell, hold} and quantity `q >= 0` per tick.

**Decision logic formalization:**

```
gain_pct = (price - cost_basis) / cost_basis

If gain_pct < tax_loss_threshold:
    a = sell
    q = min(tax_harvest_fraction * position, position)
Else if gain_pct > capital_gains_hold:
    a = sell
    q = min(gain_sell_fraction * position, position)
Else:
    a = hold
    q = 0
```

**State variables:**

| Variable    | Type  | Initial Value          |
|-------------|-------|------------------------|
| `position`  | float | scenario-defined       |
| `cash`      | float | scenario-defined       |
| `cost_basis`| float | initial purchase price |

**State evolution:**
- Post-execution:
  - Sell (harvest or gain realize): `position -= q_filled`; `cash += q_filled * fill_price`; `cost_basis` unchanged for remaining lot.
  - Buy (reinvestment): `position += q_filled`; `cash -= q_filled * fill_price`; `cost_basis = (old_cost * old_pos + fill_price * q_filled) / (old_pos + q_filled)`.
  - Hold: no state change.
- Update phase: post-execution only.

**Determinism contract:** Fully deterministic. No stochastic component.

**Parameter symbol table:**

| Symbol                 | Meaning                                   | Default Value | Source                       |
|------------------------|-------------------------------------------|---------------|------------------------------|
| `tax_loss_threshold`   | Loss fraction triggering harvest          | -0.05         | Constantinides (1983)        |
| `capital_gains_hold`   | Gain fraction below which agent defers    | 0.20          | Dammon et al. (2004)         |
| `tax_harvest_fraction` | Fraction of position sold on loss harvest | 0.50          | Arnott et al. (2001)         |
| `gain_sell_fraction`   | Fraction of position sold on gain realize | 0.30          | Expert judgment ⚠️           |
| `tax_rate`             | Applicable capital gains tax rate         | 0.20          | US long-term CG rate         |

#### Behavioral Properties

- Time horizon: medium — holds positions to defer gains but actively harvests losses; no ultra-short-term trading.
- Risk tolerance: medium — willing to realize losses (accept crystallised loss) to gain tax benefit.
- Information asymmetry: none — uses only own cost basis and public price.
- Psychological profile: fully rational from tax perspective; no behavioral biases; deliberately counter-dispositional. Embodies Constantinides (1983) optimal tax-trading policy.

## Parameters

| Parameter              | Type  | Default | Valid Range     | Sensitivity | Description                                | Impact                                           | Source                       |
|------------------------|-------|---------|-----------------|-------------|--------------------------------------------|--------------------------------------------------|------------------------------|
| `tax_loss_threshold`   | float | -0.05   | [-0.15, -0.01]  | high        | Loss fraction that triggers harvest sell   | More negative -> fewer harvests, only large losses | Constantinides (1983)       |
| `capital_gains_hold`   | float | 0.20    | [0.10, 0.50]    | high        | Gain fraction below which agent defers sell | Higher -> longer gain deferral, less selling     | Dammon et al. (2004)         |
| `tax_harvest_fraction` | float | 0.50    | [0.20, 1.00]    | medium      | Fraction of position sold on loss harvest  | Higher -> more aggressive harvesting per event   | Arnott et al. (2001)         |
| `gain_sell_fraction`   | float | 0.30    | [0.10, 1.00]    | medium      | Fraction of position sold on gain realize  | Higher -> faster gain realization when threshold hit | Expert judgment ⚠️         |
| `tax_rate`             | float | 0.20    | [0.10, 0.40]    | low         | Capital gains tax rate                     | Higher -> more valuable to harvest losses        | US federal long-term CG rate |

## Worked Numerical Examples

### Case 1 — Tax-loss harvest (sell loser)

System state: price = 94.0, cost_basis = 100.0, position = 100, cash = 5000, tax_loss_threshold = -0.05, tax_harvest_fraction = 0.50.
Calculation:
  gain_pct = (94.0 - 100.0) / 100.0 = -0.06
  -0.06 < -0.05 (tax_loss_threshold) -> harvest branch activated
  sell_qty = 0.50 * 100 = 50.0
  clamp: min(50.0, 100) = 50.0
Decision: sell 50 shares at 94.0 (crystallise loss for tax offset).
State update: position: 100 -> 50; cash: 5000 -> 9700; cost_basis: 100.0 (unchanged for remaining shares).

### Case 2 — Gain realization (very large gain)

System state: price = 125.0, cost_basis = 100.0, position = 80, cash = 3000, capital_gains_hold = 0.20, gain_sell_fraction = 0.30.
Calculation:
  gain_pct = (125.0 - 100.0) / 100.0 = 0.25
  0.25 > 0.20 (capital_gains_hold) -> gain realization branch activated
  sell_qty = 0.30 * 80 = 24.0
  clamp: min(24.0, 80) = 24.0
Decision: sell 24 shares at 125.0 (accept capital gains tax on large gain).
State update: position: 80 -> 56; cash: 3000 -> 6000; cost_basis: 100.0 (unchanged).

### Case 3 — Hold (gain deferred)

System state: price = 112.0, cost_basis = 100.0, position = 100, cash = 5000, tax_loss_threshold = -0.05, capital_gains_hold = 0.20.
Calculation:
  gain_pct = (112.0 - 100.0) / 100.0 = 0.12
  0.12 > -0.05 -> loss harvest not triggered
  0.12 < 0.20 -> gain realization not triggered
Decision: hold (defer gain — tax-optimal to wait).
State update: no change.

### Edge Case — Small loss below harvest threshold

System state: price = 97.0, cost_basis = 100.0, position = 100, cash = 5000, tax_loss_threshold = -0.05.
Calculation:
  gain_pct = (97.0 - 100.0) / 100.0 = -0.03
  -0.03 > -0.05 -> loss too small to harvest (transaction cost would exceed tax benefit)
Decision: hold (loss not sufficient to trigger harvest).
State update: no change.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `tax_loss_threshold` <- Constantinides (1983) optimal policy; Arnott et al. (2001) Table 2 — harvest at -3% to -7% depending on transaction costs and tax rate
- `capital_gains_hold` <- Dammon et al. (2004) Table III — defer until gain exceeds 15-25% for 20% tax rate
- `tax_harvest_fraction` <- Arnott et al. (2001) — partial harvest of 40-60% balances tax benefit against tracking error

**Expected individual behaviour:**
- Given price 6% below cost basis with tax_loss_threshold = -0.05, agent MUST sell to harvest the loss.
- Given price 25% above cost basis with capital_gains_hold = 0.20, agent MUST sell (realize large gain).
- Given price 12% above cost basis (below capital_gains_hold), agent MUST hold (defer gain).
- Given price 3% below cost basis (above tax_loss_threshold), agent MUST hold (loss too small to harvest).

**Sanity bounds (red flags indicating broken implementation):**
- IF agent holds a loss exceeding 2x tax_loss_threshold for > 5 ticks THEN broken: harvest mandate violated.
- IF agent sells a gain smaller than capital_gains_hold THEN broken: premature gain realization (disposition-like, not tax-optimal).
- IF agent's sell quantity exceeds current position THEN broken: violates position >= 0 constraint.
- IF agent exhibits PGR > PLR (sells winners more than losers) at small gain levels THEN broken: behaving like disposition effect, not tax-optimal.

#### Ablation Hooks

| Ablation name        | Setting                           | Hypothesis tested                             | Expected direction | Metric                        |
|----------------------|-----------------------------------|-----------------------------------------------|--------------------|-------------------------------|
| no-harvest           | `tax_loss_threshold = -1.0`       | Loss harvesting drives counter-dispositional flow | decrease       | Loss realization rate (PLR)   |
| early-gain-sell      | `capital_gains_hold = 0.05`       | Gain deferral differentiates from disposition  | increase           | Gain realization rate (PGR)   |
| full-harvest         | `tax_harvest_fraction = 1.0`      | Partial harvesting controls tracking error     | increase           | Position turnover per harvest |

## Academic References

| # | Citation                                                                                                                                           | Notes                                     |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | Constantinides, G. M. (1983). Capital market equilibrium with personal tax. *Econometrica*, 51(3), 611-636. https://doi.org/10.2307/1912153       | Optimal tax-loss harvesting theory        |
| 2 | Dammon, R. M., Spatt, C. S., & Zhang, H. H. (2004). Optimal asset location and allocation with taxable and tax-deferred investing. *Journal of Finance*, 59(3), 999-1037. https://doi.org/10.1111/j.1540-6261.2004.00655.x | Gain deferral and asset location |
| 3 | Arnott, R. D., Berkin, A. L., & Ye, J. (2001). Loss harvesting: What's it worth to the taxable investor? *Journal of Wealth Management*, 3(4), 10-18. https://doi.org/10.3905/jwm.2001.320396 | Empirical harvesting value (0.5-1.5% pa) |
| 4 | Chaudhuri, S. E., Burnham, T. C., & Lo, A. W. (2020). An empirical evaluation of tax-loss-harvesting alpha. *Financial Analysts Journal*, 76(3), 99-108. https://doi.org/10.1080/0015198X.2020.1760064 | Modern direct-indexing harvesting alpha   |
| 5 | Davis, M. H. A. & Norman, A. R. (1990). Portfolio selection with transaction costs. *Mathematics of Operations Research*, 15(4), 676-713. https://doi.org/10.1287/moor.15.4.676 | Continuous-time optimal trading with costs |

## Design Provenance and Versioning

| Field   | Content                                                   |
|---------|-----------------------------------------------------------|
| Author  | Codex                                                     |
| Created | 2026-07-16                                                |
| Version | 1.0.0                                                     |
| Icon    | ![](../agent_images/icons/finance-tax-aware-investor.png) |
| Status  | draft                                                     |
