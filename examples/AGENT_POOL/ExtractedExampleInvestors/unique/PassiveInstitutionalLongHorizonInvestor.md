# Passive long-horizon institutional investor

## Summary

| Field                 | Content                                                                                                                           |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Passive long-horizon institutional investor                                                                                       |
| Theory Family         | Quant                                                                                                                             |
| Market Role           | **Stabilising** — provides slow mean-reverting flow toward a strategic target allocation; absent in the noise-trading frequencies |
| Time Horizon          | long                                                                                                                              |
| Risk Tolerance        | low                                                                                                                               |
| Information Asymmetry | none                                                                                                                              |
| Determinism           | deterministic                                                                                                                     |

## Definition and Goals

This agent models the **institutional investor (mutual fund, pension fund, sovereign wealth fund, index fund)** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of long-horizon allocators whose decision rule is portfolio rebalancing toward a strategic target rather than active alpha-seeking. It encompasses the Bogle-style index fund (Bogle 2007), the conservative balanced-allocation holder (Markowitz 1952; Sharpe 1964), the disciplined institutional active manager with symmetric loss/gain thresholds (Shapira & Venezia 2001), and the long-horizon equity investor whose evaluation window is long enough to overcome myopic loss aversion (Benartzi & Thaler 1995, used as the contrast).

The decision goal is to compute, on every call, a target signed quantity that closes a fraction of the gap between current allocation `w(t) = (P · I(t)) / W(t)` and a strategic target `w*`, **but only when the deviation `|w(t) − w*|` exceeds a rebalancing band `θ_band`**. The agent is otherwise inactive — it explicitly does not trade on price changes alone. The criterion the agent follows is the constant-mix / threshold-rebalancing rule of Perold & Sharpe (1988), augmented with a slow-rebalancing speed parameter `rebalance_speed ≪ 1` so that the agent provides gradual mean-reverting demand rather than discontinuous jumps.

In the simulation, this agent is expected to help produce the **slow long-run mean reversion and fundamental anchoring** stylized facts (long-run reversal, sustained fundamental anchoring) catalogued in [Stylized Facts §5 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), with empirical anchoring to Sharpe (1991) and Garleanu & Pedersen (2013). It is the principal **slow stabiliser** in the population — the patient counterweight that buys when the population is selling and sells when the population is buying, but at a rate too slow to oppose short-horizon noise. **Non-goals**: this agent MUST NOT chase momentum (that role belongs to the trend trader), MUST NOT respond to short-horizon volatility shocks (that distinguishes it from the market maker), MUST NOT take fundamental-arbitrage positions (that belongs to the value-fundamental investor and the arbitrageur), MUST NOT exhibit any disposition or loss-aversion asymmetry (that defines the loss-averse retail block), and MUST NOT include any environment-imposed limits per `agent-design-skill.md §3.6.3`.

## Theoretical Foundation

**Modern portfolio theory and the strategic-target allocation**:
- Theory / Study: Markowitz (1952); Sharpe (1964) — mean-variance and CAPM origins of strategic asset allocation.
- Citation: Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77–91. [https://doi.org/10.1111/j.1540-6261.1952.tb01525.x](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x); Sharpe, W. F. (1964). Capital asset prices: A theory of market equilibrium under conditions of risk. *Journal of Finance*, 19(3), 425–442. [https://doi.org/10.1111/j.1540-6261.1964.tb02865.x](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x)
- Core Insight: An investor's optimal portfolio is the tangency portfolio, scaled by risk aversion; in a CAPM equilibrium the tangency is the market portfolio. A long-horizon institutional investor whose objective is mean-variance utility holds a fixed allocation `w*` and rebalances any drift back to it.
- Mathematical Formulation: `w* = argmax_w μ(w) − γ_inv/2 · σ²(w)` subject to `Σ w_i = 1`; for our single-asset abstraction `w*` is a scenario-given scalar.
- Empirical Evidence: Brinson, Hood & Beebower (1986) attribute >90% of pension-fund return variation to strategic asset allocation rather than active selection.
- Relevance to This Agent: The agent's `target_allocation` parameter is the strategic target `w*`; it is exogenous (set at scenario instantiation) and not optimised inside the agent.
- Calibration Source: Brinson, Hood & Beebower (1986); typical pension-fund strategic equity allocations 50–70%.
- Falsification Conditions: The agent's mean allocation drifts away from `target_allocation` over long simulation horizons.
- Alternative Theories: Black-Litterman (1992) reverse-optimised allocation; risk-parity (Qian 2005).

**Threshold rebalancing and constant-mix dynamic strategies**:
- Theory / Study: Perold & Sharpe (1988); Garleanu & Pedersen (2013).
- Citation: Perold, A. F., & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*, 44(1), 16–27. [https://doi.org/10.2469/faj.v44.n1.16](https://doi.org/10.2469/faj.v44.n1.16); Garleanu, N., & Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *Journal of Finance*, 68(6), 2309–2340. [https://doi.org/10.1111/jofi.12080](https://doi.org/10.1111/jofi.12080)
- Core Insight: With transaction costs, the optimal rebalancing rule is to trade only when the allocation breaches a no-trade band around the target, and to rebalance partially (not all the way back) when triggered. This produces a contrarian buy-the-dip / sell-the-rally pattern that is concave in the deviation.
- Mathematical Formulation: trade iff `|w − w*| > θ_band`; quantity `Q* = rebalance_speed · (w* − w) · W / P`.
- Empirical Evidence: Garleanu & Pedersen (2013) show that the optimal trade is a fraction of the unconstrained gap, with the fraction decreasing in transaction-cost intensity; calibrated to 5–25% per period for institutional desks.
- Relevance to This Agent: The agent's `rebalance_band` parameter is `θ_band`; the agent's `rebalance_speed` is the partial-rebalance fraction.
- Calibration Source: Garleanu & Pedersen (2013) Table II.
- Falsification Conditions: The agent rebalances inside the band, or fully closes the gap in a single trade.
- Alternative Theories: Constant-proportion portfolio insurance (CPPI; Black & Jones 1987) — *concave-allocation* rebalancing; option-replication strategies.

**Bogle indexing and zero-sum active management**:
- Theory / Study: Bogle (2007); Sharpe (1991) — arithmetic of active management.
- Citation: Bogle, J. C. (2007). *The Little Book of Common Sense Investing*. John Wiley & Sons. ISBN 978-0-470-10210-7. (Operational reference for the indexing thesis.); Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal*, 47(1), 7–9. [https://doi.org/10.2469/faj.v47.n1.7](https://doi.org/10.2469/faj.v47.n1.7)
- Core Insight: Active managers in aggregate hold the market portfolio gross of fees; therefore the average active-manager return must underperform a low-cost index by the gap in fees. This is a tautological identity, not an empirical claim, and it is the single strongest argument for passive long-horizon investing.
- Mathematical Formulation: `r_active_avg = r_market − fees_active`; `r_passive = r_market − fees_passive`; `r_active_avg − r_passive = fees_passive − fees_active < 0`.
- Empirical Evidence: French (2008) estimates the deadweight loss from active management at ~67 bps/year on US equities; SPIVA (2010–2024) shows ~80% of US large-cap active funds underperform their benchmark over 10-year windows.
- Relevance to This Agent: The `index_fund` variant has `target_allocation = 1.0` (full equity) and `rebalance_band` deliberately wide (only react to large deviations from a fixed index weight) — it does not attempt any timing.
- Calibration Source: French (2008); SPIVA reports.
- Falsification Conditions: The `index_fund` variant exhibits active timing (entering / exiting based on price level).
- Alternative Theories: Smart-beta / factor-tilted indexing (Asness, Frazzini & Pedersen 2013) — non-zero deviations from market weights based on factor signals.

**Long-horizon investing as immunisation against myopic loss aversion**:
- Theory / Study: Benartzi & Thaler (1995) used as a *contrast* / motivation; Campbell & Viceira (2002) long-horizon allocation.
- Citation: Campbell, J. Y., & Viceira, L. M. (2002). *Strategic Asset Allocation: Portfolio Choice for Long-Term Investors*. Oxford University Press. [https://doi.org/10.1093/0198296940.001.0001](https://doi.org/10.1093/0198296940.001.0001); Benartzi & Thaler (1995) — see [LossAversionDispositionInvestor.md](LossAversionDispositionInvestor.md) for full treatment.
- Core Insight: When evaluation windows are long (years rather than months), even a moderately loss-averse investor finds the equity premium attractive enough to hold a high stock allocation. The `long_horizon_equity` variant captures this — the agent uses an evaluation window so long (e.g. multi-year) that it ignores short-horizon drawdowns.
- Mathematical Formulation: implied equity premium `EP(λ, T_eval) → r_market − r_f` as `T_eval → ∞`; the long-horizon agent prices in long-run mean reversion of equity returns.
- Empirical Evidence: Campbell & Viceira (2002) calibrate long-horizon stock allocation under mean-reversion at 60–80% for 20-year horizons.
- Relevance to This Agent: The `long_horizon_equity` variant uses `target_allocation ≥ 0.7` and a wide `rebalance_band` to ignore intra-window noise.
- Calibration Source: Campbell & Viceira (2002), Tables 4.1 and 5.1.
- Falsification Conditions: `long_horizon_equity` agents trade more frequently than `index_fund` in calm regimes.
- Alternative Theories: Strategic withdrawal under predictability (Wachter 2002).

## Design Purpose and Activation Triggers

Purpose: provide slow, threshold-triggered, contrarian flow that anchors the long-run mean of price near the strategic target without opposing short-horizon noise.

Call Frequency: every-N-ticks (`rebalance_check_period`, default 20). Some variants use `event-driven` on calendar boundaries (e.g. once per "month" in scenarios with calendar metadata).

Prerequisite Signals:
- `price` (P) available
- `inventory` (I) available
- `wealth` (W = cash + P · I) available
- `target_allocation` (w*) configured at instantiation

Missing-Signal Policy: hold — the agent never rebalances against a missing wealth or price reading; if any prerequisite is unavailable, skip this evaluation and resume next cycle.

Activation Triggers:
- `(w(t) − w*) > +θ_band` (over-allocated): submit `SELL Q*` with `Q* = rebalance_speed · (w(t) − w*) · W / P` (positive rebalance toward target).
- `(w(t) − w*) < −θ_band` (under-allocated): submit `BUY Q*` symmetrically.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted (`cash < 0`) on the buy branch — the agent abstains until cash is replenished by exogenous inflow (scenario-driven).
- `|w(t) − w*| > θ_panic` (panic band, e.g. 3 × `θ_band`): the agent suspends rebalancing on the assumption that the market regime has shifted; resumes only when within `θ_band` again. This prevents the agent from being whipsawed in a crisis (consistent with empirical institutional behaviour during 2008–2009; Anand, Jotikasthira, & Venkataraman 2013).

Market Contribution by Regime:

| Regime         | Contribution | Mechanism                                                                     |
|----------------|--------------|-------------------------------------------------------------------------------|
| Calm           | Stabilising  | Threshold-rebalancing absorbs small deviations; provides patient counter-flow |
| Bull           | Stabilising  | Sells into rallies as `w(t)` rises above `w*`                                 |
| Bear           | Stabilising  | Buys into selloffs as `w(t)` falls below `w*`                                 |
| Stress / Panic | Suspended    | `                                                                             |

Interaction with other agents: opposes the noise trader in the long-horizon mean (absorbs cumulative noise); opposes the momentum trader by definition (sells what the momentum trader buys); does not interact with the market maker at the microstructure horizon (different time scale); is consumed by the panic-forced seller in crisis windows (which is exactly when this agent suspends rebalancing).

## Behavioral Framework

#### Decision Information Set

| Signal              | Type       | Memory Window              | Rationale                              |
|---------------------|------------|----------------------------|----------------------------------------|
| `price`             | Continuous | 1 tick                     | Required to compute current allocation |
| `inventory`         | State      | persistent                 | Net position                           |
| `cash`              | State      | persistent                 | Cash balance for buy-side capacity     |
| `wealth`            | Derived    | per call                   | `W = cash + P · I`                     |
| `allocation`        | Derived    | per call                   | `w(t) = P · I / W`                     |
| `target_allocation` | Static     | persistent (configuration) | Strategic target `w*`                  |
| `tick_index`        | Discrete   | persistent                 | Drives `rebalance_check_period` gate   |

Does NOT use: `fundamental` (the agent has no fundamental view; `w*` is a scenario input), momentum, peer flow, sentiment, news, or any signal at finer than `rebalance_check_period`-tick resolution.

#### Core Behavioral Mechanism

1. **Cycle gate**: if `tick mod rebalance_check_period ≠ 0`, hold and return.
2. Compute `W(t) = cash + P(t) · I(t)`.
3. If `W(t) ≤ 0` (insolvent), kill the agent.
4. Compute `w(t) = (P(t) · I(t)) / W(t)`.
5. Compute deviation `Δ(t) = w(t) − w*`.
6. **Panic-band check**: if `|Δ(t)| > θ_panic`, hold (regime-shift suspension); skip steps 7–8.
7. **Band check**: if `|Δ(t)| ≤ θ_band`, hold (within tolerance); skip step 8.
8. **Rebalance**: signed quantity `Q*(t) = −sign(Δ(t)) · rebalance_speed · |Δ(t)| · W(t) / P(t)`. Cap by available cash on the buy side and by `inventory` on the sell side. Submit market order.
9. **Post-fill state update**: `cash`, `inventory`, `W` updated; `target_allocation` is invariant by design (changing it is a scenario-level event, not an agent-level decision).

#### Action Space

| Aspect               | Specification                                                                                                                                                       |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | market (rebalance trades only); hold-no-op                                                                                                                          |
| Price level rule     | market price (no limit); the agent does not chase, but takes the touch                                                                                              |
| Order quantity rule  | `Q* = rebalance_speed · (w* − w) · W / P`, signed; clipped by `cash / P` (buys) and `inventory` (sells)                                                             |
| Order lifetime       | 1 tick (immediate; cancelled if not filled)                                                                                                                         |
| Cancellation policy  | unfilled orders are cancelled at end-of-tick; the agent re-decides next cycle (`rebalance_check_period` ticks later)                                                |
| Inventory constraint | `inventory ≥ 0` (the agent does not short; the index-fund / conservative variants are long-only by definition); aggregate inventory cap `inventory ≤ inventory_max` |
| Wealth/leverage cap  | `cash ≥ 0` hard; no margin used; aggregate `W ≤ wealth_cap` (scenario-set, prevents the agent from absorbing the entire market)                                     |
| Stop-loss/kill rule  | full kill if `W ≤ 0` (insolvent — drawdown so deep that strategic allocation is mathematically infeasible); otherwise none                                          |

#### Mathematical Model

- **Decision variable**: signed scalar quantity `Q*(t)` (positive = buy, negative = sell).
- **Trigger function**:
  ```
  if tick mod rebalance_check_period != 0:
      hold
  W = cash + P · I
  w = (P · I) / W
  Δ = w − w*
  if |Δ| > θ_panic:
      hold (panic-band suspension)
  elif |Δ| <= θ_band:
      hold (within band)
  else:
      Q* = −sign(Δ) · rebalance_speed · |Δ| · W / P
      submit market order Q*
  ```
- **Sizing function**: `Q* = clip(−sign(Δ) · rebalance_speed · |Δ| · W / P, cash/P (buys), inventory (sells))`.
- **State variables**:

| Symbol              | Meaning               | Initial value                         | Updated when            |
|---------------------|-----------------------|---------------------------------------|-------------------------|
| `cash`              | Cash balance          | initial endowment                     | post-fill               |
| `I`                 | Inventory             | initial allocation `w*` × `W₀` / `P₀` | post-fill               |
| `target_allocation` | Strategic target `w*` | scenario-set                          | never (within episode)  |
| `tick_index`        | Tick counter          | 0                                     | every call (pre-decide) |
| `mode`              | Active variant        | configured at instantiation           | never                   |

- **State-update rule**: `tick_index` updated **pre-decide**; `cash`, `I` updated **post-fill**. `target_allocation` is invariant; ablations that vary `w*` over time are scenario-level events.
- **Determinism contract**: deterministic given `(P, I, cash, target_allocation, tick_index, mode)` and parameters; population-level stochasticity (variant assignment, parameter draw) resolved at instantiation and seed-reproducible.

| Symbol                   | Meaning                     | Default Value | Source                          |
|--------------------------|-----------------------------|---------------|---------------------------------|
| `w*`                     | Strategic target allocation | 0.60          | Brinson, Hood & Beebower (1986) |
| `θ_band`                 | Rebalance no-trade band     | 0.05          | Garleanu & Pedersen (2013)      |
| `θ_panic`                | Panic-band suspension       | 0.20          | Anand et al. (2013)             |
| `rebalance_speed`        | Partial-rebalance fraction  | 0.20          | Garleanu & Pedersen (2013)      |
| `rebalance_check_period` | Cycle gate length (ticks)   | 20            | Standardised                    |
| `inventory_max`          | Hard inventory cap          | 10000         | Calibration                     |
| `wealth_cap`             | Hard wealth cap             | 1.0e8         | Standardised                    |

#### Behavioral Properties

- Time horizon: long — the agent's natural frequency is `rebalance_check_period` (~20 ticks ≈ 1 trading "month" in many scenarios) or longer; it ignores all signals at finer resolution.
- Risk tolerance: low — `rebalance_speed = 0.2` means at most 20% of the gap is closed per cycle; the agent accepts long-run deviation in return for low transaction-cost / impact footprint.
- Information asymmetry: none — uses only public price and its own state.
- Psychological profile: none in the bias sense; the agent is the *rational long-horizon counterfactual*. By construction it embodies *no* disposition effect, *no* momentum chasing, *no* loss-aversion asymmetry. It is the population's slow-stabilising baseline.

## Parameters

| Parameter                | Type                                                                            | Default                | Valid Range | Sensitivity | Description                        | Impact                                                                           | Source                          |
|--------------------------|---------------------------------------------------------------------------------|------------------------|-------------|-------------|------------------------------------|----------------------------------------------------------------------------------|---------------------------------|
| `passive_mode`           | enum<index_fund,conservative_holder,institutional_balanced,long_horizon_equity> | institutional_balanced | enum        | medium      | Active sub-archetype variant       | `index_fund` → highest `w*`, widest band; `conservative_holder` → lowest `w*`    | Standardised (synthesis)        |
| `target_allocation`      | float                                                                           | 0.60                   | [0, 1]      | high        | Strategic target `w*`              | Higher → larger long-run equity demand, higher floor on price                    | Brinson, Hood & Beebower (1986) |
| `rebalance_band`         | float                                                                           | 0.05                   | (0, 0.5]    | high        | No-trade band `θ_band`             | Higher → fewer trades, slower mean reversion contribution                        | Garleanu & Pedersen (2013)      |
| `panic_band`             | float                                                                           | 0.20                   | (0, 1]      | medium      | Panic-suspension band `θ_panic`    | Higher → less likely to suspend, more contribution in crisis (and more drawdown) | Anand et al. (2013)             |
| `rebalance_speed`        | float                                                                           | 0.20                   | (0, 1]      | high        | Fraction of gap closed per trigger | Higher → faster convergence, larger price impact, more trades                    | Garleanu & Pedersen (2013)      |
| `rebalance_check_period` | int                                                                             | 20                     | [1, 1000]   | medium      | Cycle-gate length in ticks         | Higher → less frequent evaluation, slower stabiliser                             | Standardised                    |
| `inventory_max`          | int                                                                             | 10000                  | [1, 1.0e8]  | low         | Hard inventory cap                 | Higher → larger possible position, larger equilibrium demand                     | Calibration                     |
| `wealth_cap`             | float                                                                           | 1.0e8                  | (0, ∞)      | low         | Hard wealth cap                    | Higher → larger possible footprint                                               | Standardised                    |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                                                                                                                     |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | scenario-dependent — typical small `N` (1–20) since this archetype represents large-balance-sheet institutional holders                                                                                                                                                                                                                                                                           |
| Parameter heterogeneity policy | iid Beta on `target_allocation`, iid LogNormal on `rebalance_band` and `rebalance_speed`; correlated `rebalance_check_period` across all `index_fund` instances (calendar-synchronised rebalance dates)                                                                                                                                                                                           |
| Heterogeneity per parameter    | `passive_mode` ← Categorical{index_fund: 0.30, conservative_holder: 0.20, institutional_balanced: 0.40, long_horizon_equity: 0.10}; `target_allocation` ← Beta(6, 4) for `institutional_balanced` (mean ≈ 0.60); `rebalance_band` ← LogNormal(ln 0.05, 0.4); `rebalance_speed` ← LogNormal(ln 0.20, 0.3); `rebalance_check_period` shared across `index_fund` (calendar) and per-agent for others |
| Cross-agent correlation        | calendar-correlated rebalance dates among `index_fund` instances (synchronised end-of-month rebalancing → known stylised-fact trading-flow concentration); independent otherwise                                                                                                                                                                                                                  |
| Identity persistence           | identical across episodes; cash and inventory carry over within an episode and reset between episodes                                                                                                                                                                                                                                                                                             |

## Worked Numerical Examples

Common parameters: `w* = 0.60`, `θ_band = 0.05`, `θ_panic = 0.20`, `rebalance_speed = 0.20`, `rebalance_check_period = 20`. Initial state: `cash = 4,000`, `I = 60`, `P = 100` ⇒ `W = 4000 + 6000 = 10,000`, `w = 0.60` (perfectly on target).

### Case 1 — Within-band hold
Market state: tick index 20 (cycle-gate fires), `P = 102`, `I = 60`, `cash = 4000`. `W = 4000 + 6120 = 10,120`. `w = 6120 / 10120 = 0.6047`. `Δ = +0.0047`.
Calculation:
  `|Δ| = 0.0047 < θ_band = 0.05` → within band.
Decision: HOLD.
State update: no change.

### Case 2 — Sell rebalance after rally
Market state: tick index 40, `P = 130`, `I = 60`, `cash = 4000`. `W = 4000 + 7800 = 11,800`. `w = 7800 / 11800 = 0.661`. `Δ = +0.061`.
Calculation:
  `|Δ| = 0.061 > θ_band = 0.05` and `|Δ| ≤ θ_panic = 0.20` → rebalance.
  `Q* = −sign(+0.061) · 0.20 · 0.061 · 11800 / 130 = −0.20 · 0.061 · 90.77 = −1.107` ⇒ round to `−1`.
  cap by `inventory = 60` (more than enough on sell side).
Decision: emit `SELL 1 @ market`.
State update: `I = 59`, `cash = 4000 + 130 = 4,130`. `W = 4130 + 7670 = 11,800` (unchanged on a paper basis; the rebalance does not change wealth, only allocation). New `w = 7670 / 11800 = 0.650` (closer to 0.60). Next cycle gate at tick 60.

### Case 3 — Buy rebalance after drawdown
Market state: tick index 60, `P = 80`, `I = 59`, `cash = 4130`. `W = 4130 + 4720 = 8,850`. `w = 4720 / 8850 = 0.533`. `Δ = −0.067`.
Calculation:
  `|Δ| = 0.067 > θ_band = 0.05` and `|Δ| ≤ θ_panic = 0.20` → rebalance.
  `Q* = +0.20 · 0.067 · 8850 / 80 = +1.484` ⇒ round to `+1`.
  cap by `cash / P = 4130 / 80 = 51.6` (more than enough on buy side).
Decision: emit `BUY 1 @ market`.
State update: `I = 60`, `cash = 4050`. `W = 4050 + 4800 = 8,850`. New `w = 4800 / 8850 = 0.542` (closer to 0.60). The agent is patient — it does not close the gap fully in one trade.

### Case 4 — Panic-band suspension
Market state: tick index 80, `P = 50` (severe drawdown), `I = 60`, `cash = 4050`. `W = 4050 + 3000 = 7,050`. `w = 3000 / 7050 = 0.426`. `Δ = −0.174`.
Calculation:
  `|Δ| = 0.174 ≤ θ_panic = 0.20`, but very close. `Q* = +0.20 · 0.174 · 7050 / 50 = +4.91` → emit BUY 4.
  Compare with `θ_panic = 0.20`: not yet breached, so the agent still trades.
  Suppose at tick 100, `P = 30`, `I = 64`, `cash = 3850`. `W = 3850 + 1920 = 5,770`. `w = 1920 / 5770 = 0.333`. `Δ = −0.267`. Now `|Δ| > θ_panic = 0.20` → suspend.
Decision (tick 100): HOLD (panic-suspension).
State update: no trade. Resumes only when `|w − w*| ≤ θ_panic` again, i.e. when `P` recovers enough that allocation falls within the panic band.

### Edge Case — Cash-exhausted buy with calendar-correlated index_fund cohort
Market state: tick index 200 (month-end rebalance day for the cohort). `P = 80`, `I = 59`, `cash = 50` (low). `W = 50 + 4720 = 4,770`. `w = 0.989`. `Δ = +0.389` — actually over-allocated due to drift since last rebalance; but assume different scenario: `cash = 50`, target `w* = 0.60`, current `w = 0.30`, `Δ = −0.30`.
Calculation:
  `|Δ| = 0.30 > θ_panic = 0.20` → suspend (panic).
  Even if not suspended, hypothetical buy quantity `Q* = +0.20 · 0.30 · W / P` → would require ~0.20·0.30·W of cash; only `50` available, capped.
Decision: HOLD (panic-band).
State update: no trade. The calendar-correlated cohort *all* simultaneously suspend on the same severe-drawdown tick — producing the empirical stylised fact that institutional rebalancing flow vanishes during crises (Anand et al. 2013).

## Validation and Calibration

**Calibration data sources**:
- `target_allocation` ← Brinson, Hood & Beebower (1986); typical pension-fund equity allocation 50–70%.
- `rebalance_band`, `rebalance_speed` ← Garleanu & Pedersen (2013), Table II — institutional-desk-implied no-trade band ≈ 5%, partial-rebalance fraction 10–25%.
- `panic_band` ← Anand, Jotikasthira & Venkataraman (2013); institutional flow suppression during 2008–2009 crisis windows.
- `rebalance_check_period` ← Standardised default; calendar-correlated for `index_fund` cohort.

**Expected stylized facts** when this agent dominates the population:
- Long-run mean reversion toward fundamental anchor: half-life of mispricing relative to `w*`-implied price > 50 ticks.
- Negligible short-horizon return autocorrelation contribution (the agent is silent at fine timescales).
- End-of-period rebalancing flow cluster (calendar-synchronised `index_fund` cohort).
- Crisis-window flow suppression: trading volume by this agent class drops 50–80% when `|Δ| > θ_panic`.

**Sanity bounds (red flags during simulation)**:
- Mean realised allocation `w` drifts permanently away from `w*` — rebalance rule broken.
- Agent trades inside the band — `θ_band` not enforced.
- Agent rebalances during a crisis when `|Δ| > θ_panic` — panic-suspension broken.
- `index_fund` instances de-synchronise — calendar correlation broken.
- Rebalance trade closes the gap fully in one tick — `rebalance_speed` set to 1.0 inadvertently.

#### Ablation Hooks

| Ablation name         | Setting                               | Hypothesis tested                                                                                                           |
|-----------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `disable_rebalance`   | `rebalance_speed = 0`                 | Removes the slow stabiliser; expected to lengthen mispricing half-life and increase long-run reversal                       |
| `tight_band`          | `rebalance_band = 0.005`              | Close to continuous rebalancing; tests whether the no-trade band is the source of the discrete-flow stylized fact           |
| `no_panic_suspension` | `panic_band = ∞`                      | Forces rebalancing during crises; expected to amplify drawdowns from this agent class (counterfactual to Anand et al. 2013) |
| `index_fund_only`     | `passive_mode = index_fund` exclusive | Isolates the calendar-synchronised flow channel                                                                             |
| `passive_off`         | population fraction = 0               | Removes the slow stabiliser entirely; measures the floor it provides on long-run price                                      |

## Academic References

| #  | Citation                                                                                                                                                                           | Notes                                     |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1  | Markowitz, H. (1952). Portfolio selection. *JF*, 7(1), 77–91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x                                                                   | Strategic-allocation foundation           |
| 2  | Sharpe, W. F. (1964). Capital asset prices. *JF*, 19(3), 425–442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x                                                               | CAPM equilibrium target                   |
| 3  | Sharpe, W. F. (1991). The arithmetic of active management. *FAJ*, 47(1), 7–9. https://doi.org/10.2469/faj.v47.n1.7                                                                 | Indexing tautology                        |
| 4  | Bogle, J. C. (2007). *The Little Book of Common Sense Investing*. Wiley. ISBN 978-0-470-10210-7                                                                                    | Indexing thesis                           |
| 5  | Brinson, G. P., Hood, L. R., & Beebower, G. L. (1986). Determinants of portfolio performance. *FAJ*, 42(4), 39–44. https://doi.org/10.2469/faj.v42.n4.39                           | Strategic-allocation empirical importance |
| 6  | Perold, A. F., & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *FAJ*, 44(1), 16–27. https://doi.org/10.2469/faj.v44.n1.16                                         | Threshold-rebalancing theory              |
| 7  | Garleanu, N., & Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *JF*, 68(6), 2309–2340. https://doi.org/10.1111/jofi.12080                 | Partial-rebalance speed calibration       |
| 8  | French, K. R. (2008). Presidential address: The cost of active investing. *JF*, 63(4), 1537–1573. https://doi.org/10.1111/j.1540-6261.2008.01368.x                                 | Active-management deadweight loss         |
| 9  | Asness, C. S., Frazzini, A., & Pedersen, L. H. (2013). Quality minus junk. *Working Paper*. https://doi.org/10.2139/ssrn.2312432                                                   | Smart-beta alternative                    |
| 10 | Black, F., & Jones, R. (1987). Simplifying portfolio insurance. *J. Portfolio Management*, 14(1), 48–51. https://doi.org/10.3905/jpm.1987.409131                                   | CPPI alternative theory                   |
| 11 | Campbell, J. Y., & Viceira, L. M. (2002). *Strategic Asset Allocation*. Oxford University Press. https://doi.org/10.1093/0198296940.001.0001                                       | Long-horizon allocation theory            |
| 12 | Anand, A., Jotikasthira, C., & Venkataraman, K. (2013). Do institutional investors stabilize equity markets? *JFE*, 109(2), 357–374. https://doi.org/10.1016/j.jfineco.2013.04.002 | Crisis-window flow-suppression evidence   |
| 13 | Black, F., & Litterman, R. (1992). Global portfolio optimization. *FAJ*, 48(5), 28–43. https://doi.org/10.2469/faj.v48.n5.28                                                       | Reverse-optimisation alternative          |
| 14 | Qian, E. (2005). On the financial interpretation of risk contribution. *J. Investment Management*, 4(4), 41–51                                                                     | Risk-parity alternative                   |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                                 |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curation team                                                                                                                                                                                                                                                                                                          |
| Reviewed by | _pending_                                                                                                                                                                                                                                                                                                                               |
| Created     | 2026-06-11                                                                                                                                                                                                                                                                                                                              |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                                   |
| Change log  | 1.0.0 (2026-06-11): Initial pilot-depth specification synthesising the 12 merged profiles in `DEDUPLICATION_REPORT.md`. Conforms to `masim/format/agent-design-skill.md` v1 + `masim/format/agent-design-finance.md` v1. Variants `index_fund / conservative_holder / institutional_balanced / long_horizon_equity` (4-mode synthesis). |
| Status      | canonical                                                                                                                                                                                                                                                                                                                               |
