# Liquidity-providing market maker

## Summary

| Field                 | Content                                                                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Liquidity-providing market maker                                                                                                                |
| Theory Family         | Market Microstructure                                                                                                                           |
| Market Role           | **Context-dependent** — stabilising in calm regimes, destabilising in stress regimes when stress-withdrawing or gamma-hedging variants dominate |
| Time Horizon          | short                                                                                                                                           |
| Risk Tolerance        | low                                                                                                                                             |
| Information Asymmetry | partial                                                                                                                                         |
| Determinism           | deterministic                                                                                                                                   |

## Definition and Goals

This agent models a **market maker / dealer** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md). It captures the family of liquidity-providing intermediaries that quote two-sided around a fair-quote estimate and earn the bid–ask spread as compensation for inventory and adverse-selection risk: the passive electronic dealer (Glosten & Milgrom 1985), the inventory-controlling specialist (Ho & Stoll 1981), the stress-sensitive immediacy provider (Grossman & Miller 1988; Brunnermeier & Pedersen 2009), and the options market maker who delta- and gamma-hedges its derivative book (Jarrow & Li 2021). The agent does **not** form a directional view; its only directional flow is the involuntary residue of asymmetric order arrival.

The decision goal is to compute, on every call, a pair of quotes `(bid(t), ask(t))` and a quoted size `q(t)` for each side, given a fair-quote estimate `m(t)` (an EMA over recent mid-prices), realised volatility `σ(t)`, current inventory `I(t)`, and (in the gamma-hedging variant) accumulated short-call gamma `Γ(t)`. The agent adjusts the spread `s(t) = ask − bid` to compensate for inventory imbalance and volatility, withdraws (sets `q(t) = 0`) when `σ(t)` exceeds a withdrawal threshold, and emits a hedging market order when `|Γ(t) · ΔP|` exceeds a hedge-trigger threshold. The criterion the agent follows is the inventory-control rule of Ho & Stoll (1981) augmented with a volatility-withdrawal switch from Grossman & Miller (1988).

In the simulation, the market maker is expected to help produce the **time-varying bid–ask spread, depth, and liquidity dry-up** stylized facts catalogued in [Stylized Facts §5 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), with empirical anchoring to Hendershott et al. (2011) and Brunnermeier & Pedersen (2009). It is the principal source of the *liquidity-spiral / margin-spiral* mechanism that turns moderate volatility shocks into flash-crash-style depth collapses. **Non-goals**: this agent MUST NOT take directional bets on fundamental value (that role belongs to the value-fundamental investor), MUST NOT chase momentum (that belongs to the trend trader), MUST NOT override its own withdrawal rule with a discretionary "lean against the wind" stance (that role belongs to the policy backstop agent), and MUST NOT assume any environment-imposed circuit breakers, fee schedule, latency model, or matching-engine priority — those are scenario-layer concerns per `agent-design-skill.md §3.6.3`.

## Theoretical Foundation

**Glosten–Milgrom adverse-selection spread**:
- Theory / Study: Glosten & Milgrom (1985) — sequential trade model with informed and uninformed traders.
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. [https://doi.org/10.1016/0304-405X(85)90044-3](https://doi.org/10.1016/0304-405X(85)90044-3)
- Core Insight: A risk-neutral dealer facing a mix of informed and noise traders must set a positive spread to break even on the adverse-selection cost of trading against informed counterparties; the equilibrium spread widens in the share of informed traders and the variance of the asset value.
- Mathematical Formulation: `ask(t) = E[V | order = buy](t)`; `bid(t) = E[V | order = sell](t)`; spread `s = ask − bid > 0` whenever the proportion of informed traders is positive.
- Empirical Evidence: Hasbrouck (1988) decomposes NYSE trades and finds the implied adverse-selection component accounts for roughly 30–60% of the effective spread.
- Relevance to This Agent: The agent's `base_spread_bps` parameter is the residual quote-edge after inventory and volatility adjustments — the closest analogue to the Glosten–Milgrom adverse-selection spread.
- Calibration Source: Hendershott, Jones & Menkveld (2011) — algorithmic-liquidity NYSE Hybrid panel.
- Falsification Conditions: Quoted spread is zero or negative on average, or the spread does not widen in realised volatility.
- Alternative Theories: Kyle (1985) batch-auction microstructure, in which the dealer absorbs all flow at a single price.

**Ho–Stoll inventory-control market making**:
- Theory / Study: Ho & Stoll (1981) — optimal dealer pricing with inventory aversion.
- Citation: Ho, T., & Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty. *Journal of Financial Economics*, 9(1), 47–73. [https://doi.org/10.1016/0304-405X(81)90020-5](https://doi.org/10.1016/0304-405X(81)90020-5)
- Core Insight: A risk-averse dealer facing inventory-shock uncertainty quotes asymmetrically around the mid: when inventory is long, both bid and ask are *shifted down* to attract sells and discourage buys, and vice versa. The shift magnitude is increasing in inventory and in volatility.
- Mathematical Formulation: `bid(t) = m(t) − s/2 − γ · σ²(t) · I(t)`; `ask(t) = m(t) + s/2 − γ · σ²(t) · I(t)` where `γ` is dealer risk aversion and `I(t)` is inventory.
- Empirical Evidence: Madhavan & Smidt (1991) confirm the inventory-skew prediction in NYSE specialist data.
- Relevance to This Agent: The `inventory_reverting` variant implements exactly this skew, and the parameter `inventory_aversion` is the agent's `γ`.
- Calibration Source: Hansch, Naik & Viswanathan (1998), London Stock Exchange dealer panel.
- Falsification Conditions: Quotes do not skew with inventory, or skew has the wrong sign.
- Alternative Theories: Stoll (1978) without volatility scaling; Avellaneda & Stoikov (2008) with terminal time horizon.

**Grossman–Miller stress withdrawal**:
- Theory / Study: Grossman & Miller (1988); Brunnermeier & Pedersen (2009) — funding-liquidity-driven dealer withdrawal.
- Citation: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617–633. [https://doi.org/10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x); Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. [https://doi.org/10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Core Insight: Dealer immediacy is a finite resource constrained by funding capital; when realised volatility (and therefore margin requirements on inventory) rises above a critical level, the dealer rationally withdraws quotes, producing a discontinuous depth collapse.
- Mathematical Formulation: emit quotes only if `σ(t) ≤ σ_withdraw`; else `q(t) = 0`.
- Empirical Evidence: Kirilenko, Kyle, Samadi & Tuzun (2017) document HFT dealers withdrawing ~50% of quoted depth during the May 6, 2010 Flash Crash within 30 seconds of the volatility spike.
- Relevance to This Agent: The `stress_withdrawing` variant adds a volatility threshold above which the agent emits no quotes; this is the principal liquidity-spiral driver in the population.
- Calibration Source: Kirilenko et al. (2017) Table 4 — withdrawal latency and depth collapse statistics.
- Falsification Conditions: Realised volatility doubles but the agent does not change its quoted depth.
- Alternative Theories: Morris & Shin (2004) liquidity black holes — withdrawal is driven by VaR-binding stop-loss, not raw volatility.

**Gamma-hedging delta-replication**:
- Theory / Study: Jarrow & Li (2021); Black & Scholes (1973) implied-hedging mechanics.
- Citation: Jarrow, R. A., & Li, S. (2021). The impact of a hedge fund's gamma exposure on the underlying asset price. *Review of Derivatives Research*, 24, 233–263. [https://doi.org/10.1007/s11147-021-09176-6](https://doi.org/10.1007/s11147-021-09176-6); Black, F., & Scholes, M. (1973). The pricing of options and corporate liabilities. *Journal of Political Economy*, 81(3), 637–654. [https://doi.org/10.1086/260062](https://doi.org/10.1086/260062)
- Core Insight: An options dealer who is short gamma must buy the underlying after a price rise and sell after a price fall to keep its delta-hedge intact. This converts a price move of ΔP into a same-signed underlying-market order of size `|Γ| · ΔP`, mechanically amplifying the original move.
- Mathematical Formulation: hedge order quantity `Q_hedge = Γ · ΔP`, signed to neutralise the new delta from the price move.
- Empirical Evidence: Barbon, Beckmeyer, Buraschi & Moerke (2024) document a 0.1–0.4 standard-deviation amplification of intraday return autocorrelation from concentrated short-gamma dealer positions.
- Relevance to This Agent: The `gamma_hedging` variant adds a `gamma_exposure` state and a hedge order rule that mechanically buys into rallies and sells into selloffs — the only directional behaviour any market-maker variant exhibits, and it is *involuntary*.
- Calibration Source: Jarrow & Li (2021) Table 2 — gamma-amplification coefficients calibrated to GameStop January 2021.
- Falsification Conditions: Net hedge flow is uncorrelated with price changes.
- Alternative Theories: Static hedging (Carr & Wu 2014) — the dealer does not rehedge intraday and absorbs gamma P&L.

## Design Purpose and Activation Triggers

Purpose: provide continuous two-sided liquidity around a short-horizon fair quote, charge a spread for immediacy, and withdraw under stress so that the population can produce realistic intraday liquidity dry-ups.

Call Frequency: every tick.

Prerequisite Signals:
- `price` (P) available
- `mid_quote_ema` (m) available — short-window EMA over recent mids
- `realised_vol` (σ) over the last `vol_window` ticks available
- `inventory` (I) available
- For `gamma_hedging` variant: `gamma_exposure` (Γ) and `Δprice` over the last tick available

Missing-Signal Policy: if `m`, `σ`, or `I` is unavailable / NaN / stale, hold (emit zero-size quotes) — the agent never quotes against a missing fair-quote estimate.

Activation Triggers:
- `σ(t) ≤ σ_withdraw` and `|I(t)| < inventory_max`: emit two-sided limit quotes at `(m − s/2 − γ·σ²·I, m + s/2 − γ·σ²·I)` with size `quote_size`.
- `|I(t)| ≥ inventory_max`: emit one-sided quote on the inventory-reducing side only.
- `gamma_hedging` variant and `|Γ · ΔP| > hedge_trigger`: additionally emit a same-signed market order of size `|Γ · ΔP|`.
- `<Default>`: hold (no quotes).

Deactivation Conditions:
- `σ(t) > σ_withdraw` (`stress_withdrawing` variant): withdraw both quotes — emit zero-size; this is the principal stress-driver.
- Cumulative drawdown on quoted-spread P&L exceeds `pnl_floor`: hibernate for `cooldown` ticks, then resume only if `σ` has fallen below the threshold.
- `|I(t)| > 2 · inventory_max` (hard cap): emit only inventory-reducing market orders until breach is cured.

Market Contribution by Regime:

| Regime         | Contribution  | Mechanism                                                                                                          |
|----------------|---------------|--------------------------------------------------------------------------------------------------------------------|
| Calm           | Stabilising   | Two-sided quotes around `m` damp short-horizon noise; inventory skew mean-reverts price toward fair-quote estimate |
| Stress         | Destabilising | Withdrawal rule removes depth precisely when other agents need to trade out; depth collapse propagates volatility  |
| Liquidity-rich | Stabilising   | Tight spread, high quoted size, narrow inventory band                                                              |
| Liquidity-poor | Destabilising | Wide spread, reduced size, frequent withdrawal — immediacy becomes scarce                                          |

Interaction with other agents: opposes the noise trader and momentum trader (absorbs their flow at a spread), is consumed by the panic-forced seller (whose inelastic supply triggers the volatility breach that withdraws the dealer), and complements the policy-backstop agent (which can resupply liquidity precisely when this agent withdraws).

## Behavioral Framework

#### Decision Information Set

| Signal           | Type       | Memory Window                             | Rationale                                                    |
|------------------|------------|-------------------------------------------|--------------------------------------------------------------|
| `price`          | Continuous | 1 tick                                    | Current market price, only used to update the EMA            |
| `mid_quote_ema`  | Continuous | EMA half-life `ema_halflife` ticks        | Fair-quote estimate `m(t)` around which quotes are anchored  |
| `realised_vol`   | Continuous | `vol_window` ticks                        | Trailing realised volatility, drives spread + withdrawal     |
| `inventory`      | State      | persistent                                | Current net position, drives Ho–Stoll skew and inventory cap |
| `gamma_exposure` | State      | persistent (`gamma_hedging` variant only) | Short-gamma book size, drives hedge-flow rule                |
| `Δprice`         | Continuous | 1 tick (`gamma_hedging` variant only)     | Last-tick price change, drives hedge order size              |

Does NOT use: `fundamental` (the agent has no fundamental view by design), peer-trade flow, news, sentiment, longer-window momentum signals, or any social-graph / peer-network signal.

#### Core Behavioral Mechanism

1. Update fair-quote EMA: `m(t) = (1 − α) · m(t−1) + α · P(t)` with `α = 1 − exp(−ln 2 / ema_halflife)`.
2. Update realised volatility: rolling stdev of returns over `vol_window`.
3. **Stress check** (`stress_withdrawing` variant): if `σ(t) > σ_withdraw`, set `q(t) = 0` for both sides and skip steps 4–7.
4. Compute inventory-skewed quotes: `bid = m − s/2 − γ·σ²·I`, `ask = m + s/2 − γ·σ²·I` with `s = base_spread_bps · m / 10000`.
5. Compute quoted size: `q_bid = q_ask = quote_size`. If `|I| ≥ inventory_max`, set `q_bid = 0` (already long) or `q_ask = 0` (already short).
6. **Gamma hedge** (`gamma_hedging` variant): if `|Γ · ΔP| > hedge_trigger`, emit a same-signed market order of size `|Γ · ΔP|` *in addition to* the limit quotes.
7. Submit the limit quotes; cancel any prior unfilled quotes; wait for fills.
8. **Post-fill state update**: increment `I(t+1) = I(t) + filled_buys − filled_sells`. Update `gamma_exposure` from any options-side fills (modeled as scenario input in `gamma_hedging` variant).
9. **Drawdown check**: if cumulative quote-spread P&L over `pnl_window` ticks falls below `pnl_floor`, hibernate for `cooldown` ticks.

#### Action Space

| Aspect               | Specification                                                                                                                                                 |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | limit (always); market (only `gamma_hedging` variant, only for hedge flow); hold-no-op                                                                        |
| Price level rule     | `bid = m − s/2 − γ·σ²·I`; `ask = m + s/2 − γ·σ²·I`. Quotes never cross. The hedge order (`gamma_hedging`) is a market order at touch                          |
| Order quantity rule  | `q_bid = q_ask = quote_size` if `                                                                                                                             |
| Order lifetime       | 1 tick (cancel-replace each call)                                                                                                                             |
| Cancellation policy  | unfilled prior quotes are cancelled at the start of every call before new quotes are emitted; on stress withdrawal, all open quotes are cancelled             |
| Inventory constraint | soft cap `                                                                                                                                                    |
| Wealth/leverage cap  | cash floor `cash ≥ cash_floor`; no margin used by the limit-quote variants. The `gamma_hedging` variant respects a notional cap `                             |
| Stop-loss/kill rule  | hibernate for `cooldown` ticks if cumulative spread P&L < `pnl_floor`; full kill (no further quotes for the episode) if cumulative drawdown < `2 · pnl_floor` |

#### Mathematical Model

- **Decision variable**: quote tuple `(bid(t), ask(t), q_bid(t), q_ask(t))`, plus optional hedge order `Q_hedge(t)` for the `gamma_hedging` variant.
- **Trigger function**:
  ```
  if σ(t) > σ_withdraw and variant == stress_withdrawing:
      emit nothing
  else:
      bid = m(t) − s/2 − γ · σ²(t) · I(t)
      ask = m(t) + s/2 − γ · σ²(t) · I(t)
      emit (bid, ask, q_bid, q_ask)
      if variant == gamma_hedging and |Γ(t) · ΔP(t)| > hedge_trigger:
          emit market order sign(ΔP) · |Γ(t) · ΔP(t)|
  ```
- **Sizing function**:
  ```
  q_bid = quote_size if I < +inventory_max else 0
  q_ask = quote_size if I > −inventory_max else 0
  Q_hedge = clip(Γ · ΔP, −hedge_max, +hedge_max)
  ```
- **State variables**:

| Symbol | Meaning                              | Initial value               | Updated when              |
|--------|--------------------------------------|-----------------------------|---------------------------|
| `m`    | Fair-quote EMA                       | first observed price        | every call (pre-decide)   |
| `σ`    | Realised volatility (rolling stdev)  | 0                           | every call (pre-decide)   |
| `I`    | Net inventory                        | 0                           | post-fill                 |
| `Γ`    | Net short-gamma exposure             | scenario input              | post-fill / scenario tick |
| `pnl`  | Rolling spread-P&L over `pnl_window` | 0                           | post-fill                 |
| `mode` | Active variant                       | configured at instantiation | never                     |

- **State-update rule**: `m`, `σ` updated **pre-decide**; `I`, `Γ`, `pnl` updated **post-fill**. The hibernation flag is checked **pre-decide** and cleared `cooldown` ticks after entry.
- **Determinism contract**: deterministic given `(m, σ, I, Γ, ΔP)` and the configured parameters; all stochasticity (which variant a given dealer instance is, its parameter draw) is resolved at population-instantiation time and is reproducible given a seed.

| Symbol          | Meaning                             | Default Value | Source                           |
|-----------------|-------------------------------------|---------------|----------------------------------|
| `s`             | Spread (bps of mid)                 | 10            | Hendershott et al. (2011) median |
| `γ`             | Inventory aversion coefficient      | 0.001         | Ho & Stoll (1981)                |
| `quote_size`    | Quoted size each side               | 20            | Calibration                      |
| `inventory_max` | Soft inventory cap                  | 100           | Madhavan & Smidt (1991)          |
| `σ_withdraw`    | Volatility threshold for withdrawal | 0.03          | Kirilenko et al. (2017)          |
| `hedge_trigger` | Min hedge flow to act on            | 5             | Jarrow & Li (2021)               |
| `ema_halflife`  | Fair-quote EMA half-life            | 5             | Standardised                     |
| `vol_window`    | Realised-vol rolling window         | 20            | Standardised                     |
| `pnl_floor`     | Hibernation drawdown threshold      | −1000         | Calibration                      |

#### Behavioral Properties

- Time horizon: short — every-tick quote refresh; no view longer than `ema_halflife` ticks.
- Risk tolerance: low — inventory cap, hard cap, drawdown kill, stress withdrawal; the agent is by construction reluctant to carry overnight risk.
- Information asymmetry: partial — sees the order-book imbalance via inventory but never the fundamental.
- Psychological profile: none in the behavioural-bias sense; the agent is rational under a constrained inventory-and-funding objective. The destabilising behaviour is *structural* (Brunnermeier–Pedersen funding constraint), not psychological.

## Parameters

| Parameter            | Type                                                                         | Default             | Valid Range | Sensitivity | Description                              | Impact                                                                              | Source                             |
|----------------------|------------------------------------------------------------------------------|---------------------|-------------|-------------|------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------|
| `mm_mode`            | enum<passive_two_sided,inventory_reverting,stress_withdrawing,gamma_hedging> | inventory_reverting | enum        | high        | Active sub-archetype variant             | passive_two_sided → flat skew; stress_withdrawing → step withdrawal at σ_withdraw   | Standardised (synthesis)           |
| `base_spread_bps`    | float                                                                        | 10.0                | (0, 100]    | high        | Base bid–ask spread in bps of mid        | Higher → lower fill rate, higher per-trade margin, lower contribution to liquidity  | Hendershott et al. (2011)          |
| `inventory_aversion` | float                                                                        | 0.001               | [0, 0.1]    | high        | Ho–Stoll γ coefficient                   | Higher → larger inventory skew, faster mean reversion of `I`                        | Ho & Stoll (1981)                  |
| `quote_size`         | int                                                                          | 20                  | [1, 1000]   | medium      | Quoted size per side                     | Higher → more depth provided in calm regime, more inventory risk in stress          | Calibration                        |
| `inventory_max`      | int                                                                          | 100                 | [1, 10000]  | medium      | Soft inventory cap                       | Higher → wider tolerance, lower withdrawal frequency, larger inventory P&L variance | Madhavan & Smidt (1991)            |
| `vol_window`         | int                                                                          | 20                  | [1, 500]    | medium      | Trailing window for realised volatility  | Higher → smoother σ, slower withdrawal response                                     | Standardised                       |
| `sigma_withdraw`     | float                                                                        | 0.03                | [0, 1]      | high        | Withdrawal volatility threshold          | Higher → less withdrawal, lower contribution to liquidity spirals                   | Kirilenko et al. (2017)            |
| `ema_halflife`       | int                                                                          | 5                   | [1, 200]    | low         | Half-life of the fair-quote EMA          | Higher → smoother quote anchor, slower response to genuine repricing                | Standardised                       |
| `hedge_trigger`      | float                                                                        | 5.0                 | [0, 1000]   | medium      | Min `                                    | Γ·ΔP                                                                                | ` to act on (`gamma_hedging` only) |
| `gamma_notional_max` | float                                                                        | 1.0e6               | (0, ∞)      | medium      | Notional cap on hedge book               | Higher → larger amplification per ΔP, larger crash potential                        | Jarrow & Li (2021)                 |
| `cooldown`           | int                                                                          | 50                  | [0, 5000]   | low         | Hibernation length after drawdown breach | Higher → slower recovery, more persistent depth collapse                            | Standardised                       |
| `pnl_floor`          | float                                                                        | −1000               | (−∞, 0]     | low         | Drawdown threshold for hibernation       | Lower (more negative) → less likely to hibernate, more risk-tolerant                | Calibration                        |
| `cash_floor`         | float                                                                        | 0                   | [0, ∞)      | low         | Minimum cash balance                     | Higher → tighter capital constraint, earlier withdrawal                             | Standardised                       |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                                  |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | scenario-dependent — typical small `N` (1–8) since dealers are concentrated in real markets                                                                                                                                                                                                                    |
| Parameter heterogeneity policy | iid lognormal on `base_spread_bps` (μ=ln 10, σ=0.5) and `inventory_max` (μ=ln 100, σ=0.4); shared `sigma_withdraw` across stress variant for coherent withdrawal episodes                                                                                                                                      |
| Heterogeneity per parameter    | `mm_mode` ← Categorical{passive_two_sided: 0.20, inventory_reverting: 0.50, stress_withdrawing: 0.20, gamma_hedging: 0.10}; `base_spread_bps` ← LogNormal(ln 10, 0.5); `inventory_max` ← LogNormal(ln 100, 0.4); `sigma_withdraw` ← Uniform(0.025, 0.040) per draw, shared across stress variant; others point |
| Cross-agent correlation        | shared `sigma_withdraw` across all `stress_withdrawing` instances (coherent withdrawal episode); independent draws otherwise                                                                                                                                                                                   |
| Identity persistence           | identical across episodes within a scenario; re-drawn between scenarios                                                                                                                                                                                                                                        |

## Worked Numerical Examples

Common parameters: `base_spread_bps = 10`, `inventory_aversion γ = 0.001`, `quote_size = 20`, `inventory_max = 100`, `sigma_withdraw = 0.03`, `ema_halflife = 5`.

### Case 1 — Calm-regime two-sided quoting (inventory_reverting variant)
Market state: `P(t) = 100.00`, `m(t) = 100.00`, `σ(t) = 0.012`, `I(t) = 0`.
Calculation:
  spread `s = 10 / 10000 · 100 = 0.10`.
  bid = 100.00 − 0.05 − 0.001 · 0.012² · 0 = 99.95.
  ask = 100.00 + 0.05 − 0.001 · 0.012² · 0 = 100.05.
  no withdrawal (`σ < σ_withdraw`); both sides quoted at size 20.
Decision: emit `(BID 99.95 ×20, ASK 100.05 ×20)`.
State update: `I` unchanged (no fill yet). `m` updated next tick.

### Case 2 — Inventory-skewed quoting after asymmetric fills
Market state: `P(t) = 100.00`, `m(t) = 100.00`, `σ(t) = 0.020`, `I(t) = +60` (long after a series of sells absorbed).
Calculation:
  inventory-skew term `γ · σ² · I = 0.001 · 0.020² · 60 = 0.000024 · 60 = 0.00144 ≈ 0.0014`. (small in absolute terms; model uses bps-scaled `γ`)
  Using a calibrated `γ' = 0.05` for visibility (illustrative): skew = 0.05 · 0.020² · 60 = 0.0012; skew over price = 0.0012 → bid = 100.00 − 0.05 − 0.0012 = 99.9488; ask = 100.00 + 0.05 − 0.0012 = 100.0488.
  Quotes shift down → makes sells less attractive, buys more attractive → inventory mean-reverts toward 0.
  Both sides quoted; `|I| < inventory_max`.
Decision: emit `(BID 99.95 ×20, ASK 100.05 ×20)` with downward skew.
State update: as fills arrive, `I` decreases; rolling spread P&L credited.

### Case 3 — Stress withdrawal (stress_withdrawing variant)
Market state: `P(t) = 100.00`, `m(t) = 100.20`, `σ(t) = 0.045` (above `σ_withdraw = 0.030`), `I(t) = +30`.
Calculation:
  stress check: `σ(t) > σ_withdraw` → withdraw.
  Cancel any prior open quotes; emit no new quotes.
Decision: HOLD (no quotes).
State update: `I` unchanged this tick (no fills); `m`, `σ` updated for next tick. If `σ` falls back below threshold within `cooldown` ticks, normal quoting resumes; otherwise hibernation persists.

### Case 4 — Gamma-hedging amplification (gamma_hedging variant)
Market state: `P(t−1) = 100.00`, `P(t) = 102.00`, so `ΔP = +2.00`. `Γ(t) = +50` (short 50 calls' worth of gamma; positive sign = short gamma). `hedge_trigger = 5`.
Calculation:
  hedge flow `Γ · ΔP = 50 · 2.00 = 100.00`. `|100| > 5` → hedge.
  emit market BUY of size 100 (sign(+2) = +). The dealer is forced to chase the rally.
  In parallel, the limit quotes still get emitted at the new `m`.
Decision: emit market `BUY 100 @ market` plus refreshed two-sided limit quotes around `m(t)`.
State update: `I(t+1) = I(t) + 100`; `Γ(t+1) ≈ Γ(t) − Γ_decay` (scenario-driven). The market move is amplified by the hedge flow.

### Edge Case — Hard inventory-cap breach
Market state: `I(t) = +205`, `inventory_max = 100`, so `|I| > 2·inventory_max`.
Calculation:
  Hard cap breached → suppress both limit quotes; emit market SELL at touch of size `min(quote_size · 5, |I| − inventory_max) = min(100, 105) = 100`.
Decision: emit aggressive `SELL 100 @ market` to cure breach; no limit quotes this tick.
State update: `I(t+1) = I(t) − 100 = 105`. Still above soft cap; on next tick, one-sided ask-only quoting resumes until breach is fully cured.

## Validation and Calibration

**Calibration data sources**:
- `base_spread_bps` ← Hendershott et al. (2011), Table 3 — median NYSE Hybrid quoted spread ≈ 10 bps for liquid names.
- `inventory_aversion` ← Ho & Stoll (1981) parameter range; refined by Madhavan & Smidt (1991) NYSE specialist panel.
- `sigma_withdraw` ← Kirilenko et al. (2017), Section 5 — empirical realised-volatility threshold above which HFT depth fell by ≥50% during the May 6, 2010 Flash Crash.
- `quote_size`, `inventory_max` ← matched to the median LSE dealer panel summary statistics in Hansch, Naik & Viswanathan (1998).
- `gamma_notional_max` ← Jarrow & Li (2021) GameStop-event-implied gamma exposure.

**Expected stylized facts** when this agent dominates the population:
- Time-varying bid–ask spread: positive correlation with realised volatility (Hendershott et al. 2011).
- Volume-volatility co-movement (Brunnermeier & Pedersen 2009).
- Liquidity dry-ups: depth drops by ≥50% during periods when `σ` exceeds the withdrawal threshold (Kirilenko et al. 2017).
- Inventory mean-reversion: autocorrelation of `I` decays with half-life ≈ 5–20 ticks (Madhavan & Smidt 1991).

**Sanity bounds (red flags during simulation)**:
- Average quoted spread ≤ 0 bps — adverse-selection protection failed; investigate.
- Inventory `I` drifts unbounded with no skew correction — Ho–Stoll skew not applied; check `inventory_aversion`.
- `stress_withdrawing` instances quote continuously throughout a stress period — withdrawal logic broken.
- `gamma_hedging` instance hedge flow uncorrelated with ΔP — gamma rule broken.
- Cumulative dealer P&L grows without bound at sub-second timescales — likely arbitrage against own quotes; check that quotes never cross.

#### Ablation Hooks

| Ablation name         | Setting                             | Hypothesis tested                                                                                          |
|-----------------------|-------------------------------------|------------------------------------------------------------------------------------------------------------|
| `disable_withdrawal`  | `sigma_withdraw = ∞`                | Stress withdrawal is the principal liquidity-spiral mechanism: removing it should attenuate flash crashes  |
| `flat_inventory_skew` | `inventory_aversion = 0`            | Without inventory skew, dealer P&L variance and inventory-cap-breach frequency rise sharply                |
| `tight_quote_size`    | `quote_size = 1`                    | Reducing quoted depth should widen realised volatility and increase price-impact coefficients              |
| `gamma_only`          | `mm_mode = gamma_hedging` exclusive | Isolates the gamma-amplification channel from passive market making                                        |
| `mm_off`              | population fraction = 0             | Removes the dealer entirely — measures the marginal contribution of the dealer block to all stylized facts |

## Academic References

| #  | Citation                                                                                                                                                                                                  | Notes                                               |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| 1  | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *JFE*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3 | Adverse-selection spread foundation                 |
| 2  | Ho, T., & Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty. *JFE*, 9(1), 47–73. https://doi.org/10.1016/0304-405X(81)90020-5                                         | Inventory-control quote skew                        |
| 3  | Stoll, H. R. (1978). The supply of dealer services in securities markets. *JF*, 33(4), 1133–1151. https://doi.org/10.1111/j.1540-6261.1978.tb02053.x                                                      | Earlier dealer-supply model (alternative theory)    |
| 4  | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *JF*, 43(3), 617–633. https://doi.org/10.1111/j.1540-6261.1988.tb04594.x                                                         | Immediacy provider; foundation of stress withdrawal |
| 5  | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *RFS*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098                                                        | Liquidity-spiral / margin-spiral mechanism          |
| 6  | Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *JF*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498                     | Empirical withdrawal evidence; calibration source   |
| 7  | Hasbrouck, J. (1988). Trades, quotes, inventories, and information. *JFE*, 22(2), 229–252. https://doi.org/10.1016/0304-405X(88)90070-0                                                                   | Adverse-selection decomposition of spreads          |
| 8  | Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *JF*, 66(1), 1–33. https://doi.org/10.1111/j.1540-6261.2010.01624.x                                  | Algorithmic-liquidity calibration                   |
| 9  | Madhavan, A., & Smidt, S. (1991). A Bayesian model of intraday specialist pricing. *JFE*, 30(1), 99–134. https://doi.org/10.1016/0304-405X(91)90023-D                                                     | Inventory-skew empirical evidence                   |
| 10 | Hansch, O., Naik, N. Y., & Viswanathan, S. (1998). Do inventories matter in dealership markets? Evidence from the LSE. *JF*, 53(5), 1623–1656. https://doi.org/10.1111/0022-1082.00067                    | Dealer-panel calibration                            |
| 11 | Avellaneda, M., & Stoikov, S. (2008). High-frequency trading in a limit order book. *Quantitative Finance*, 8(3), 217–224. https://doi.org/10.1080/14697680701381228                                      | Alternative formulation with finite horizon         |
| 12 | Morris, S., & Shin, H. S. (2004). Liquidity black holes. *Review of Finance*, 8(1), 1–18. https://doi.org/10.1023/B:EUFI.0000022155.98681.25                                                              | VaR-binding withdrawal alternative                  |
| 13 | Jarrow, R. A., & Li, S. (2021). The impact of a hedge fund's gamma exposure on the underlying asset price. *RDR*, 24, 233–263. https://doi.org/10.1007/s11147-021-09176-6                                 | Gamma-amplification calibration                     |
| 14 | Black, F., & Scholes, M. (1973). The pricing of options and corporate liabilities. *JPE*, 81(3), 637–654. https://doi.org/10.1086/260062                                                                  | Delta-hedging foundation                            |
| 15 | Barbon, A., Beckmeyer, H., Buraschi, A., & Moerke, M. (2024). The role of intermediaries' gamma exposure on intraday autocorrelation. *Working Paper, SSRN 4501316*. https://doi.org/10.2139/ssrn.4501316 | Empirical gamma-amplification effect size           |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                           |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curation team                                                                                                                                                                                                                                                                                    |
| Reviewed by | _pending_                                                                                                                                                                                                                                                                                                         |
| Created     | 2026-06-11                                                                                                                                                                                                                                                                                                        |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                             |
| Change log  | 1.0.0 (2026-06-11): Initial pilot-depth specification synthesising the 12 merged profiles in `DEDUPLICATION_REPORT.md`. Conforms to `masim/format/agent-design-skill.md` v1 + `masim/format/agent-design-finance.md` v1. Variants `passive_two_sided / inventory_reverting / stress_withdrawing / gamma_hedging`. |
| Status      | canonical                                                                                                                                                                                                                                                                                                         |
