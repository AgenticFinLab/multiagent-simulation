# Limits-to-arbitrage convergence trader

## Summary

| Field                 | Content                                                                                                                                             |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Limits-to-arbitrage convergence trader                                                                                                              |
| Theory Family         | Limits to Arbitrage                                                                                                                                 |
| Market Role           | **Context-dependent** — stabilising in calm regimes (closes mispricings); destabilising in stress regimes (forced unwind amplifies the dislocation) |
| Time Horizon          | medium                                                                                                                                              |
| Risk Tolerance        | medium                                                                                                                                              |
| Information Asymmetry | partial                                                                                                                                             |
| Determinism           | deterministic                                                                                                                                       |

## Definition and Goals

This agent models the **arbitrageur / statistical arbitrageur / hedge fund** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of relative-value traders who profit by closing pricing dislocations but operate under finite capital and noise-trader-risk constraints (Shleifer & Vishny 1997). It encompasses fundamental-convergence trading (LTCM-style swap-Treasury basis trades; LTCM team 1994–98 documented in MacKenzie 2003), index arbitrage (MacKinlay & Ramaswamy 1988), volatility relative value (Bondarenko 2014), leveraged basis trades (Du, Tepper & Verdelhan 2018 covered-interest-parity deviations), and merger-arbitrage (Mitchell & Pulvino 2001).

The decision goal is to compute, on every call, a signed quantity `Q*(t)` that takes a position against a deviation `d(t) = (P(t) − F(t)) / F(t)` between the observed price `P` and a benchmark / fundamental anchor `F`, *but only when* (a) `|d(t)|` exceeds an entry threshold `θ_entry`, (b) the agent has remaining capital under a self-imposed VaR / drawdown cap, and (c) the agent has not been forced to unwind by a stop-loss trigger. The criterion the agent follows is the bounded-rationality version of the convergence trade: open with a sizing that grows with `|d|`, hold until `|d|` falls below an exit threshold `θ_exit < θ_entry`, and **forced-exit** if cumulative drawdown breaches `dd_stop`.

In the simulation, this agent is expected to help produce the **bounded mispricing half-life, fire-sale externality, and limits-to-arbitrage stylized facts** catalogued in [Stylized Facts §5 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), with empirical anchoring to Pontiff (2006) and Mitchell, Pedersen & Pulvino (2007). It is the principal source of *partial corrective flow* in mispricing windows and *destabilising forced unwinds* in funding-stress windows. **Non-goals**: this agent MUST NOT take unbounded positions (Shleifer–Vishny limits are the defining constraint), MUST NOT chase momentum (it is contrarian on `d`), MUST NOT exhibit any psychological bias (it is the rational-but-constrained counterfactual to the bias-driven retail blocks), MUST NOT trade on noise alone (entry threshold prevents this), and MUST NOT include any environment-imposed funding rules per `agent-design-skill.md §3.6.3` — its self-imposed VaR / drawdown cap is the agent's *internal* discipline, not an environment rule.

## Theoretical Foundation

**Shleifer–Vishny limits to arbitrage**:
- Theory / Study: Shleifer & Vishny (1997).
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. [https://doi.org/10.1111/j.1540-6261.1997.tb03807.x](https://doi.org/10.1111/j.1540-6261.1997.tb03807.x)
- Core Insight: Real-world arbitrage is conducted by specialised intermediaries (hedge funds, prop desks) with finite capital and outside investors who withdraw capital after losses. As a result, arbitrageurs face the perverse situation that mispricings can widen further before they converge, forcing a *forced unwind* at the worst possible time (the "noise-trader risk" mechanism). Arbitrage capacity is therefore *concave* in mispricing depth: large deviations attract less capital than small ones, exactly when more capital would be most useful.
- Mathematical Formulation: arbitrageur capital `K(t+1) = K(t) · (1 − a · max(0, −r_arb(t)))` where `a ≥ 1` is the outside-investor withdrawal multiplier; arbitrage capacity `Q_max(t) = κ · K(t)` with `κ` a leverage coefficient.
- Empirical Evidence: LTCM 1998 unwind (Lowenstein 2001); Mitchell, Pedersen & Pulvino (2007) document arbitrage-capacity contraction in 1987, 1998, and 2001.
- Relevance to This Agent: The agent's `dd_stop` parameter is the forced-unwind trigger; the `capital` state variable shrinks linearly with realised drawdown (no outside-investor withdrawal modelled at the agent level — that is a population-level scenario input).
- Calibration Source: Mitchell, Pedersen & Pulvino (2007) Figure 4.
- Falsification Conditions: Arbitrageur survives unbounded drawdown without forced unwind; arbitrage capacity grows with mispricing depth.
- Alternative Theories: De Long, Shleifer, Summers & Waldmann (1990) noise-trader risk in a CARA-Gaussian setup; Gromb & Vayanos (2002) equilibrium with margin constraints.

**Index arbitrage (futures-spot basis)**:
- Theory / Study: MacKinlay & Ramaswamy (1988); Brennan & Schwartz (1990).
- Citation: MacKinlay, A. C., & Ramaswamy, K. (1988). Index-futures arbitrage and the behavior of stock index futures prices. *Review of Financial Studies*, 1(2), 137–158. [https://doi.org/10.1093/rfs/1.2.137](https://doi.org/10.1093/rfs/1.2.137)
- Core Insight: When the futures-spot basis `b(t) = F_fut − P_spot · (1 + r·τ − div·τ)` deviates from the cost-of-carry no-arbitrage value, mechanical buy-spot/sell-futures or sell-spot/buy-futures trades produce a (near-)riskless profit. The agent's only risk is execution slippage and basis convergence timing.
- Mathematical Formulation: enter when `|b(t)| > θ_entry`, sized by `Q* = sign(−b) · κ · |b|`; close when `|b| < θ_exit`.
- Empirical Evidence: MacKinlay & Ramaswamy (1988) document basis-convergence half-life of 30–60 minutes in S&P 500 futures.
- Relevance to This Agent: The `index_pair_arb` variant operates on a synthetic basis input rather than a single-asset deviation.
- Calibration Source: MacKinlay & Ramaswamy (1988) Table III.
- Falsification Conditions: Basis stays open without convergence under stationary-`F` scenarios.
- Alternative Theories: Pure cost-of-carry models (Cornell & French 1983) ignoring counterparty / funding risk.

**Pontiff arbitrage costs**:
- Theory / Study: Pontiff (1996, 2006) — empirical study of closed-end-fund discounts as a measure of arbitrage frictions.
- Citation: Pontiff, J. (2006). Costly arbitrage and the myth of idiosyncratic risk. *Journal of Accounting and Economics*, 42(1–2), 35–52. [https://doi.org/10.1016/j.jacceco.2006.04.002](https://doi.org/10.1016/j.jacceco.2006.04.002)
- Core Insight: Arbitrage cost rises in idiosyncratic volatility of the mispriced asset (a noise-trader-risk proxy), holding cost (margin and short-fees), and required holding period. Empirical mispricings are persistent precisely in assets with high arbitrage cost.
- Mathematical Formulation: implied arbitrage capacity `Q_max ∝ 1 / (idio_vol² · holding_cost)`.
- Empirical Evidence: Pontiff (2006) on CEF discounts: idio-vol explains ~30% of cross-sectional discount variation.
- Relevance to This Agent: The `idio_vol_penalty` parameter modulates `θ_entry` upward when realised idio-vol is high — the agent demands a wider spread to enter when convergence risk is higher.
- Calibration Source: Pontiff (2006), Table 4.
- Falsification Conditions: Agent enters at the same threshold regardless of realised idio-vol.
- Alternative Theories: Mitchell, Pulvino & Stafford (2002) — focus on holding-period uncertainty alone.

**Merger-arbitrage non-Gaussian risk profile**:
- Theory / Study: Mitchell & Pulvino (2001).
- Citation: Mitchell, M., & Pulvino, T. (2001). Characteristics of risk and return in risk arbitrage. *Journal of Finance*, 56(6), 2135–2175. [https://doi.org/10.1111/0022-1082.00401](https://doi.org/10.1111/0022-1082.00401)
- Core Insight: Merger-arbitrage returns are nearly riskless in normal markets but exhibit large left-tail losses precisely when the broader market falls (deal break correlation with market stress). The risk-return profile resembles a short put on the market.
- Mathematical Formulation: `r_merger_arb ≈ premium − P_break · loss_on_break` with `Cov(P_break, r_market) < 0`.
- Empirical Evidence: Mitchell & Pulvino (2001) on 4,750 mergers 1963–1998: average return 4% over 3 months in normal markets; −7% in market-stress months.
- Relevance to This Agent: The `merger_event` variant is gated on a `deal_announced` exogenous flag and exits on `deal_closed` or `deal_broken`; the `dd_stop` rule is critical for survival.
- Calibration Source: Mitchell & Pulvino (2001) Table III.
- Falsification Conditions: Merger-arbitrage P&L is uncorrelated with market stress.
- Alternative Theories: Baker & Savaşoglu (2002) — regulatory-jurisdiction risk pricing.

## Design Purpose and Activation Triggers

Purpose: provide partial corrective flow against mispricings within the agent's capacity, then forced-unwind when drawdown breaches the agent's self-imposed cap — producing the empirically observed bounded mispricing half-life and the destabilising-unwind crisis-amplification mechanism.

Call Frequency: every-N-ticks (`evaluation_period`, default 1 — the agent evaluates as fast as the deviation signal arrives).

Prerequisite Signals:
- `price` (P) available
- `fundamental` (F) or `benchmark` (e.g. futures, paired ETF) available — the agent does not infer F itself
- `idio_vol` (σ_idio) over the last `vol_window` ticks available
- For `merger_event` variant: `deal_announced`, `deal_closed`, `deal_broken` flags available

Missing-Signal Policy: hold — the agent never opens a new position against a missing benchmark or unknown idio-vol. If `F` becomes unavailable while a position is open, the agent holds the existing position but does not adjust sizing.

Activation Triggers:
- `d(t) = (P − F)/F`, deviation in absolute value `|d(t)| > θ_entry · (1 + idio_vol_penalty · σ_idio)`: open or scale position toward `Q* = sign(−d) · κ · |d| · K / P`.
- `|d(t)| < θ_exit` while position is open: close position toward zero at `unwind_speed`.
- `Q* > 0` (long-mispriced): submit BUY; `Q* < 0` (short-mispriced): submit SHORT-equivalent SELL (long-only ablations are configurable).
- `<Default>`: hold.

Deactivation Conditions:
- Cumulative drawdown on the agent's mark-to-market P&L over `dd_window` ticks falls below `dd_stop` (e.g. −20% of `K`): **forced unwind** — the agent submits market orders to close 100% of position over the next `unwind_horizon` ticks, regardless of `d(t)`. Capital is then locked out for `cooldown` ticks (model of post-unwind investor withdrawal).
- `K(t) < K_min`: hard kill (insolvency).
- For `merger_event`: on `deal_closed` (close at announced price) or `deal_broken` (close at market with realised loss).

Market Contribution by Regime:

| Regime          | Contribution  | Mechanism                                                                                                                              |
|-----------------|---------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Calm            | Stabilising   | Convergence trades close mispricings within capacity; bounded mispricing half-life                                                     |
| Stress / Crisis | Destabilising | Forced-unwind rule produces same-signed flow as the original dislocation; exits at the worst possible time (Shleifer–Vishny mechanism) |
| Liquidity-rich  | Stabilising   | Larger `K`, tighter `θ_entry`, faster convergence                                                                                      |
| Liquidity-poor  | Destabilising | Smaller `K`, wider `θ_entry`, larger residual mispricing                                                                               |

Interaction with other agents: opposes the noise trader and the loss-averse retail block (these create the deviations the agent profits from); is consumed by the leveraged-fund and panic-forced-seller (their forced unwinds drive the deviations the agent exploits — and, when severe, trigger this agent's own unwind); reinforces the value-fundamental investor in calm regimes.

## Behavioral Framework

#### Decision Information Set

| Signal         | Type       | Memory Window                  | Rationale                                                    |
|----------------|------------|--------------------------------|--------------------------------------------------------------|
| `price`        | Continuous | 1 tick                         | Current observed price                                       |
| `fundamental`  | Continuous | 1 tick                         | Benchmark / fundamental anchor `F`; required to compute `d`  |
| `deviation`    | Derived    | per call                       | `d = (P − F) / F`                                            |
| `idio_vol`     | Continuous | `vol_window` ticks             | Realised idiosyncratic volatility, drives `θ_entry` widening |
| `position`     | State      | persistent                     | Net long / short exposure                                    |
| `capital`      | State      | persistent                     | Mark-to-market capital `K`                                   |
| `cum_drawdown` | State      | persistent                     | Rolling P&L drawdown over `dd_window`                        |
| `deal_flags`   | Discrete   | per call (`merger_event` only) | `deal_announced / closed / broken`                           |
| `mode`         | State      | persistent                     | Active variant                                               |

Does NOT use: peer trade flow, social sentiment, news beyond the explicit deal flags, or any momentum / trend signal. The agent is contrarian by construction on `d`.

#### Core Behavioral Mechanism

1. Compute `d(t) = (P(t) − F(t)) / F(t)`. Update `idio_vol(t)` over `vol_window`.
2. Compute drawdown-aware capital `K(t)` from cumulative mark-to-market P&L.
3. **Drawdown stop**: if `cum_drawdown(t) < dd_stop`, transition to `forced_unwind` mode (closes 100% of position over `unwind_horizon` ticks); skip steps 4–7.
4. **Insolvency**: if `K(t) < K_min`, kill the agent.
5. **Effective entry threshold**: `θ_eff = θ_entry · (1 + idio_vol_penalty · idio_vol(t))`.
6. **Entry / scale**: if `|d(t)| > θ_eff` and current position has the same sign as `−d` (or is zero), increase `|position|` toward `Q* = sign(−d) · κ · |d| · K / P`, capped by remaining capacity `Q_max = κ · K / P − |position|`.
7. **Exit**: if `|d(t)| < θ_exit` and position is open, reduce `|position|` toward zero by `unwind_speed · |position|`.
8. **Merger-event override** (`merger_event` only): on `deal_closed`, close at announced settlement price; on `deal_broken`, close at market.
9. **Post-fill state update**: realised P&L credited to `cum_pnl`; mark-to-market P&L computed against unfilled position; `K` updated.

#### Action Space

| Aspect               | Specification                                                                                                                                                           |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | market (entries, exits, forced unwind); limit (entries only when `                                                                                                      |
| Price level rule     | market price for forced-unwind and merger settlement; `P · (1 − sign(Q*) · 0.001)` limit price for non-aggressive entries                                               |
| Order quantity rule  | entry: `Q* = sign(−d) · κ ·                                                                                                                                             |
| Order lifetime       | 1 tick (re-decided every cycle)                                                                                                                                         |
| Cancellation policy  | unfilled limit orders cancelled at end-of-tick; replaced next tick if `d` still above threshold; on forced-unwind transition, all open limit orders converted to market |
| Inventory constraint | `                                                                                                                                                                       |
| Wealth/leverage cap  | `K ≥ K_min`; `position notional ≤ leverage_max · K`; for `leveraged_basis` variant `leverage_max` up to 30× (LTCM-style); for `fundamental_convergence` typically 2–4×  |
| Stop-loss/kill rule  | forced unwind on `cum_drawdown < dd_stop`; full kill on `K < K_min`; merger-event-specific exits on deal-closed / deal-broken flags                                     |

#### Mathematical Model

- **Decision variable**: signed scalar `Q*(t)`.
- **Trigger function**:
  ```
  d = (P − F) / F
  θ_eff = θ_entry · (1 + idio_vol_penalty · idio_vol)
  if cum_drawdown < dd_stop:
      mode <- forced_unwind
  if mode == forced_unwind:
      Q* = -position / unwind_horizon (signed to close)
  elif |d| > θ_eff and (position == 0 or sign(position) == -sign(d)):
      Q_target = sign(−d) · κ · |d| · K / P
      Q* = clip(Q_target − position, −Q_max, +Q_max)
  elif |d| < θ_exit and position != 0:
      Q* = -unwind_speed · position
  else:
      Q* = 0
  ```
- **Sizing function**: as in trigger; entry size linear in `|d|` and `K`; exit size linear in current position.
- **State variables**:

| Symbol          | Meaning                                 | Initial value     | Updated when            |
|-----------------|-----------------------------------------|-------------------|-------------------------|
| `position`      | Net signed exposure                     | 0                 | post-fill               |
| `K`             | Mark-to-market capital                  | initial endowment | every call (pre-decide) |
| `cum_pnl`       | Realised cumulative P&L                 | 0                 | post-fill               |
| `cum_drawdown`  | Rolling P&L drawdown over `dd_window`   | 0                 | every call (pre-decide) |
| `idio_vol`      | Realised idiosyncratic volatility       | 0                 | every call (pre-decide) |
| `mode_state`    | `normal` / `forced_unwind` / `cooldown` | `normal`          | on threshold breach     |
| `cooldown_left` | Ticks remaining in cooldown             | 0                 | every call (pre-decide) |
| `deal_status`   | `merger_event` only                     | `none`            | scenario-driven         |
| `arb_mode`      | Active variant                          | configured        | never                   |

- **State-update rule**: `K`, `cum_drawdown`, `idio_vol`, `cooldown_left`, `mode_state` updated **pre-decide**; `position`, `cum_pnl` updated **post-fill**. The forced-unwind transition is one-way until cooldown expires.
- **Determinism contract**: deterministic given `(P, F, idio_vol, position, K, cum_drawdown, mode_state, cooldown_left, deal_status, arb_mode)` and parameters; all stochasticity (variant assignment, parameter draw) resolved at instantiation and seed-reproducible.

| Symbol             | Meaning                              | Default Value | Source                              |
|--------------------|--------------------------------------|---------------|-------------------------------------|
| `θ_entry`          | Entry deviation threshold            | 0.05          | Pontiff (2006)                      |
| `θ_exit`           | Exit deviation threshold             | 0.01          | Standardised (`< θ_entry`)          |
| `κ`                | Sizing coefficient                   | 5.0           | Calibration                         |
| `idio_vol_penalty` | Threshold widening per unit idio-vol | 2.0           | Pontiff (2006) Table 4              |
| `unwind_speed`     | Fractional exit per tick             | 0.30          | Standardised                        |
| `dd_stop`          | Drawdown trigger for forced unwind   | −0.20         | Mitchell, Pedersen & Pulvino (2007) |
| `unwind_horizon`   | Forced-unwind length (ticks)         | 5             | Calibration                         |
| `cooldown`         | Post-unwind capital lockout (ticks)  | 100           | Calibration                         |
| `leverage_max`     | Self-imposed leverage cap            | 4.0           | Standardised                        |

#### Behavioral Properties

- Time horizon: medium — entries held until convergence (`θ_exit` crossed) or forced unwind; typical horizon 10–100 ticks.
- Risk tolerance: medium — leveraged but with a hard drawdown stop; the agent accepts noise-trader risk but caps it.
- Information asymmetry: partial — has access to the benchmark `F` (which the noise trader does not), but the same `F` is also visible to the value-fundamental investor and the rational-analyst investor.
- Psychological profile: none in the bias sense; the agent is the rational-but-constrained counterfactual to the bias-driven blocks. The destabilising forced-unwind behaviour is *structural* (Shleifer–Vishny), not psychological.

## Parameters

| Parameter          | Type                                                                                         | Default                 | Valid Range      | Sensitivity | Description                                        | Impact                                                                               | Source                              |
|--------------------|----------------------------------------------------------------------------------------------|-------------------------|------------------|-------------|----------------------------------------------------|--------------------------------------------------------------------------------------|-------------------------------------|
| `arb_mode`         | enum<fundamental_convergence,index_pair_arb,vol_relative_value,leveraged_basis,merger_event> | fundamental_convergence | enum             | high        | Active sub-archetype variant                       | `leveraged_basis` → 10–30× leverage, much larger contribution / drawdown             | Standardised (synthesis)            |
| `theta_entry`      | float                                                                                        | 0.05                    | (0, 1]           | high        | Entry deviation threshold                          | Higher → fewer entries, wider mispricing tolerance, smaller stabilising contribution | Pontiff (2006)                      |
| `theta_exit`       | float                                                                                        | 0.01                    | [0, theta_entry) | high        | Exit deviation threshold                           | Lower → holds positions longer, larger inventory drawdown risk                       | Standardised                        |
| `kappa`            | float                                                                                        | 5.0                     | (0, 100]         | high        | Sizing coefficient                                 | Higher → larger position per unit `                                                  | d                                   |
| `idio_vol_penalty` | float                                                                                        | 2.0                     | [0, 10]          | medium      | Threshold widening per unit idio-vol               | Higher → more cautious entries in volatile regimes                                   | Pontiff (2006)                      |
| `unwind_speed`     | float                                                                                        | 0.30                    | (0, 1]           | medium      | Fractional position exit per tick                  | Higher → faster exit, less holding-period risk, larger exit-impact                   | Standardised                        |
| `dd_stop`          | float                                                                                        | −0.20                   | (−1, 0]          | high        | Drawdown trigger for forced unwind                 | More negative (closer to −1) → less likely to forced-unwind, larger destabilisation  | Mitchell, Pedersen & Pulvino (2007) |
| `unwind_horizon`   | int                                                                                          | 5                       | [1, 100]         | medium      | Forced-unwind spread length                        | Lower → faster unwind, larger price impact                                           | Calibration                         |
| `cooldown`         | int                                                                                          | 100                     | [0, 10000]       | low         | Post-unwind lockout length                         | Higher → slower recovery, more persistent corrective-capacity collapse               | Calibration                         |
| `leverage_max`     | float                                                                                        | 4.0                     | [1, 50]          | high        | Self-imposed leverage cap                          | Higher → larger possible position, larger drawdown, more LTCM-style risk             | Standardised                        |
| `K_min`            | float                                                                                        | 0.05                    | (0, 1]           | low         | Insolvency threshold (fraction of initial capital) | Higher → easier kill, fewer surviving instances                                      | Standardised                        |
| `vol_window`       | int                                                                                          | 20                      | [1, 500]         | low         | Trailing window for idio-vol                       | Higher → smoother penalty, slower threshold response                                 | Standardised                        |
| `dd_window`        | int                                                                                          | 50                      | [1, 1000]        | medium      | Drawdown rolling window                            | Higher → smoother drawdown signal, slower forced-unwind trigger                      | Calibration                         |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                                                                            |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | scenario-dependent — typical small `N` (3–20) since arbitrage is concentrated in specialised intermediaries                                                                                                                                                                                                                                              |
| Parameter heterogeneity policy | iid LogNormal on `theta_entry`, `kappa`, `leverage_max`; **shared `dd_stop`** across all instances of the same `arb_mode` so that a single drawdown episode triggers correlated unwinds (the empirical Shleifer–Vishny mechanism)                                                                                                                        |
| Heterogeneity per parameter    | `arb_mode` ← Categorical{fundamental_convergence: 0.40, index_pair_arb: 0.20, vol_relative_value: 0.20, leveraged_basis: 0.10, merger_event: 0.10}; `theta_entry` ← LogNormal(ln 0.05, 0.4); `kappa` ← LogNormal(ln 5, 0.5); `leverage_max` ← LogNormal(ln 4, 0.5); `dd_stop` ← Uniform(−0.25, −0.15) per scenario, shared across same-`arb_mode` cohort |
| Cross-agent correlation        | shared `dd_stop` within `arb_mode` cohort → correlated forced-unwind episodes (LTCM-1998 stylised fact); independent draws otherwise                                                                                                                                                                                                                     |
| Identity persistence           | identical across episodes; capital `K` and `position` reset between episodes                                                                                                                                                                                                                                                                             |

## Worked Numerical Examples

Common parameters: `θ_entry = 0.05`, `θ_exit = 0.01`, `κ = 5.0`, `idio_vol_penalty = 2.0`, `dd_stop = −0.20`, `leverage_max = 4.0`. Initial state: `K = 1,000`, `position = 0`, `cum_drawdown = 0`, `mode_state = normal`.

### Case 1 — Open long-mispriced position
Market state: `P = 100`, `F = 110` ⇒ `d = (100 − 110)/110 = −0.0909`. `idio_vol = 0.02`. `θ_eff = 0.05 · (1 + 2.0 · 0.02) = 0.052`.
Calculation:
  `|d| = 0.091 > 0.052` → entry triggered. Sign: `−d = +0.091` → BUY.
  `Q_target = +5.0 · 0.091 · 1000 / 100 = +4.55` → 4 shares (round down).
  capacity `Q_max = 4.0 · 1000 / 100 − 0 = 40` → not binding.
Decision: emit `BUY 4 @ market` (or `LIMIT 99.90 ×4`).
State update: `position = +4`. `K` unchanged (open position not yet closed).

### Case 2 — Scale into deepening mispricing
Market state (next eval cycle): `P = 95`, `F = 110` ⇒ `d = −0.136`. `idio_vol = 0.025`. `θ_eff = 0.055`. Currently `position = +4`, `K_mtm = 1000 + 4·(95 − 100) = 980`, `cum_drawdown = (980 − 1000)/1000 = −0.02`.
Calculation:
  `|d| = 0.136 > θ_eff = 0.055` → scale.
  `Q_target = +5.0 · 0.136 · 980 / 95 = +7.01` → target 7. Already at +4; add `+3`.
  capacity: `Q_max = 4.0 · 980 / 95 − 4 = 41.3 − 4 = 37.3` → not binding.
  cum_drawdown −0.02 > dd_stop −0.20 → no forced unwind.
Decision: emit `BUY 3`.
State update: `position = +7`, `K_mtm = 980` (open position; no realised P&L yet).

### Case 3 — Convergence exit
Market state (later): `P = 109.5`, `F = 110` ⇒ `d = −0.0045`. `position = +7`. K_mtm = `1000 + 7·(109.5 − avg_entry_98.6) = 1000 + 7·10.9 = 1076.3`.
Calculation:
  `|d| = 0.0045 < θ_exit = 0.01` → exit branch.
  `Q* = -unwind_speed · position = -0.30 · 7 = -2.1` → SELL 2.
Decision: emit `SELL 2 @ market`.
State update: realised P&L = `2 · (109.5 − 98.6) = +21.8`. `position = +5`. `cum_pnl += 21.8`. Continue exit on subsequent ticks until `position → 0`.

### Case 4 — Forced unwind on drawdown breach (Shleifer–Vishny)
Market state (alternative branch from Case 2): `P = 80`, `F = 110` ⇒ `d = −0.273`. `position = +7`, `K_mtm = 1000 + 7·(80 − 98.6) = 1000 + 7·(−18.6) = 870`. `cum_drawdown = (870 − 1000)/1000 = −0.13`. Two ticks later, `P = 75`, `K_mtm = 1000 + 7·(75 − 98.6) = 835`, `cum_drawdown = −0.165`. One more tick, `P = 70`, `K_mtm = 800`, `cum_drawdown = −0.20` → **breach**.
Calculation:
  `cum_drawdown ≤ dd_stop` → transition `mode_state ← forced_unwind`.
  Despite `|d| = 0.364` >> `θ_eff` (which would normally trigger MORE entry), the agent is now in forced-exit mode. `Q* = -7 / unwind_horizon = -7/5 = -1.4` → SELL 1 this tick, repeated for `unwind_horizon=5` ticks.
Decision: emit `SELL 1 @ market` (forced).
State update: position decremented by 1. The forced sell at `P = 70` (well below convergence target `F = 110`) realises a large loss, exactly matching the Shleifer–Vishny "wrong-time exit" mechanism. After 5 ticks, `position = 0`, `cooldown_left = 100`, and the agent is locked out for 100 ticks regardless of how the deviation evolves.

### Edge Case — Merger-event broken deal
Market state: `arb_mode = merger_event`. At `tick = 50`, `deal_announced` flag flips to True, announced settlement `F = 110`. `P = 105`. Agent enters `BUY` toward target. At `tick = 200`, `deal_broken` flag fires. `P = 92`.
Calculation:
  Override: regardless of `d`, close position at market.
  `position = +5` → `SELL 5 @ market` at `P = 92`.
Decision: emit `SELL 5 @ market`.
State update: realised P&L = `5 · (92 − 105) = −65`. `position = 0`. `cum_pnl += −65`. The negative P&L correlates with broader market stress (Mitchell & Pulvino 2001 short-put profile), and may push `cum_drawdown < dd_stop`, in which case the forced-unwind cooldown applies — but since position is already zero, it just locks out new entries for `cooldown` ticks.

## Validation and Calibration

**Calibration data sources**:
- `theta_entry` ← Pontiff (2006), Table 4 — implied entry threshold ≈ 5% on closed-end-fund discount panels.
- `idio_vol_penalty` ← Pontiff (2006); idio-vol explains ~30% of cross-sectional discount variance.
- `dd_stop` ← Mitchell, Pedersen & Pulvino (2007), Figure 4 — implied −20% drawdown trigger across LTCM-1998, equity-arb-2007.
- `leverage_max` ← LTCM disclosed leverage 25–30× pre-collapse (MacKenzie 2003); typical hedge-fund leverage 2–6×.
- `kappa` ← Calibrated to match empirical mispricing half-life of 30–60 minutes (MacKinlay & Ramaswamy 1988) for the index-arb variant.
- `merger_event` parameters ← Mitchell & Pulvino (2001); P_break ≈ 0.10, loss_on_break ≈ 12%.

**Expected stylized facts** when this agent dominates the population:
- Bounded mispricing half-life: deviations relative to `F` decay with half-life 5–50 ticks in calm regimes (matching Pontiff 2006 long-run averages).
- Forced-unwind clusters: same-signed sell flow concentrated in stress-window tails (Mitchell, Pedersen & Pulvino 2007).
- Capital-recovery slowness: post-unwind cooldown produces ~100-tick window where mispricing can widen unopposed.
- For `merger_event` cohort: realised P&L correlates negatively with market stress (Mitchell & Pulvino 2001 short-put profile).

**Sanity bounds (red flags during simulation)**:
- Agent enters in the same direction as the deviation — sign error in trigger function.
- Agent survives drawdown deeper than `dd_stop` — forced-unwind logic broken.
- Agent maintains positions during cooldown — lockout broken.
- Agent's mark-to-market P&L over an episode dwarfs `K · leverage_max` — leverage cap not enforced.
- For `merger_event`: deal-broken realised loss is positive — sign error.

#### Ablation Hooks

| Ablation name     | Setting                             | Hypothesis tested                                                                                                                           |
|-------------------|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `disable_dd_stop` | `dd_stop = −∞`                      | Removes the Shleifer–Vishny forced-unwind mechanism; expected to eliminate crisis-amplification, with implausible survival in deep drawdown |
| `flat_threshold`  | `idio_vol_penalty = 0`              | Tests Pontiff (2006) — does idio-vol-aware entry threshold materially change mispricing persistence?                                        |
| `low_leverage`    | `leverage_max = 1.5`                | Tests how much of the destabilisation comes from leverage versus the unwind-rule alone                                                      |
| `merger_only`     | `arb_mode = merger_event` exclusive | Isolates the short-put-on-market profile                                                                                                    |
| `arb_off`         | population fraction = 0             | Removes corrective flow entirely; measures the agent's marginal contribution to mispricing half-life                                        |

## Academic References

| #  | Citation                                                                                                                                                                              | Notes                                        |
|----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| 1  | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *JF*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                                 | Defining theory                              |
| 2  | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise-trader risk in financial markets. *JPE*, 98(4), 703–738. https://doi.org/10.1086/261703                 | Noise-trader-risk foundation                 |
| 3  | Gromb, D., & Vayanos, D. (2002). Equilibrium and welfare in markets with financially constrained arbitrageurs. *JFE*, 66(2–3), 361–407. https://doi.org/10.1016/S0304-405X(02)00228-3 | Equilibrium with margin constraints          |
| 4  | MacKinlay, A. C., & Ramaswamy, K. (1988). Index-futures arbitrage. *RFS*, 1(2), 137–158. https://doi.org/10.1093/rfs/1.2.137                                                          | Index-arb empirical foundation               |
| 5  | Brennan, M. J., & Schwartz, E. S. (1990). Arbitrage in stock index futures. *J. Business*, 63(1), S7–S31. https://doi.org/10.1086/296491                                              | Cost-of-carry alternative                    |
| 6  | Pontiff, J. (1996). Costly arbitrage: Evidence from closed-end funds. *QJE*, 111(4), 1135–1151. https://doi.org/10.2307/2946710                                                       | Earlier arbitrage-cost evidence              |
| 7  | Pontiff, J. (2006). Costly arbitrage and the myth of idiosyncratic risk. *JAE*, 42(1–2), 35–52. https://doi.org/10.1016/j.jacceco.2006.04.002                                         | Idio-vol-aware threshold calibration         |
| 8  | Mitchell, M., & Pulvino, T. (2001). Characteristics of risk and return in risk arbitrage. *JF*, 56(6), 2135–2175. https://doi.org/10.1111/0022-1082.00401                             | Merger-arb short-put profile                 |
| 9  | Mitchell, M., Pedersen, L. H., & Pulvino, T. (2007). Slow-moving capital. *AER P&P*, 97(2), 215–220. https://doi.org/10.1257/aer.97.2.215                                             | Crisis-window arbitrage-capacity contraction |
| 10 | MacKenzie, D. (2003). Long-Term Capital Management and the sociology of arbitrage. *Economy and Society*, 32(3), 349–380. https://doi.org/10.1080/03085140303130                      | LTCM case study                              |
| 11 | Lowenstein, R. (2001). *When Genius Failed: The Rise and Fall of Long-Term Capital Management*. Random House. ISBN 978-0-375-50317-7                                                  | LTCM narrative reference                     |
| 12 | Du, W., Tepper, A., & Verdelhan, A. (2018). Deviations from covered interest rate parity. *JF*, 73(3), 915–957. https://doi.org/10.1111/jofi.12620                                    | Leveraged-basis empirical evidence           |
| 13 | Bondarenko, O. (2014). Why are put options so expensive? *Quarterly J. Finance*, 4(3), 1450015. https://doi.org/10.1142/S2010139214500153                                             | Vol-relative-value foundation                |
| 14 | Mitchell, M., Pulvino, T., & Stafford, E. (2002). Limited arbitrage in equity markets. *JF*, 57(2), 551–584. https://doi.org/10.1111/1540-6261.00434                                  | Holding-period risk evidence                 |
| 15 | Cornell, B., & French, K. R. (1983). The pricing of stock index futures. *J. Futures Markets*, 3(1), 1–14. https://doi.org/10.1002/fut.3990030102                                     | Pure cost-of-carry alternative               |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                                                |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curation team                                                                                                                                                                                                                                                                                                                         |
| Reviewed by | _pending_                                                                                                                                                                                                                                                                                                                                              |
| Created     | 2026-06-11                                                                                                                                                                                                                                                                                                                                             |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                                                  |
| Change log  | 1.0.0 (2026-06-11): Initial pilot-depth specification synthesising the 11 merged profiles in `DEDUPLICATION_REPORT.md`. Conforms to `masim/format/agent-design-skill.md` v1 + `masim/format/agent-design-finance.md` v1. Variants `fundamental_convergence / index_pair_arb / vol_relative_value / leveraged_basis / merger_event` (5-mode synthesis). |
| Status      | canonical                                                                                                                                                                                                                                                                                                                                              |
