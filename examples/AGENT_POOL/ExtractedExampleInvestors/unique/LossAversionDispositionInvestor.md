# Loss-averse and disposition-effect retail investor

## Summary

| Field                 | Content                                                                                                                     |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Loss-averse and disposition-effect retail investor                                                                          |
| Theory Family         | Behavioral Finance                                                                                                          |
| Market Role           | **Context-dependent** — stabilising on rallies (early profit-taking), destabilising on selloffs (refusal to realise losses) |
| Time Horizon          | medium                                                                                                                      |
| Risk Tolerance        | low (in the gain region) / high (in the loss region, by reflection)                                                         |
| Information Asymmetry | none                                                                                                                        |
| Determinism           | deterministic                                                                                                               |

## Definition and Goals

This agent models a **retail trader / individual investor** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of retail investors whose buy/sell decisions are governed by Prospect Theory (Kahneman & Tversky 1979) reasoning around a personal cost-basis reference point. It encompasses the disposition-effect trader (Shefrin & Statman 1985) who sells winners early and holds losers too long, the high-λ loss-averse investor (Kahneman & Tversky 1979), the endowment-affected holder (Kahneman, Knetsch & Thaler 1990), the status-quo-biased non-seller (Samuelson & Zeckhauser 1988), the myopic loss-averse equity-premium investor (Benartzi & Thaler 1995), and the convex-region break-even gambler whose loss position drives risk-seeking escalation.

The decision goal is to compute, on every call for each held position, a binary action `{sell, hold}` for that position (and possibly `buy` to add at entry-price for the break-even-gambler variant), driven by the *perceived* prospect-theory value of the current paper P&L versus the reference point. Concretely the agent computes the relative gain `g(t) = (P(t) − R) / R` where `R` is the reference point (cost basis for `disposition / loss_averse / break_even_gambler`; an *endowment-premium-shifted* basis for `endowment / status_quo`); applies the asymmetric value function `V(g) = g^α` for `g ≥ 0` and `V(g) = −λ · |g|^β` for `g < 0`; and uses a kinked decision rule with a small gain threshold `θ_g` and a much larger loss threshold `θ_l`. The criterion the agent follows is "sell when paper-gain crosses `θ_g`, hold (or escalate) when paper-loss is shallower than `θ_l`".

In the simulation, this agent is expected to help produce the **disposition-effect skew, momentum-then-reversal pattern, and equity-premium-puzzle behaviour** stylized facts catalogued in [Stylized Facts §5 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), with empirical anchoring to Odean (1998) and Frazzini (2006). It is the principal source of *asymmetric supply* in rallies and *withheld supply* in drawdowns. **Non-goals**: this agent MUST NOT take fundamental-value bets (that role belongs to the value-fundamental investor), MUST NOT chase momentum (that belongs to the trend trader), MUST NOT trade at the second-by-second microstructure horizon (that belongs to the HFT and market maker), MUST NOT exhibit symmetric gain/loss thresholds (that defines the rational-analyst counterfactual), and MUST NOT include any environment-imposed circuit-breaker, fee schedule, or matching-engine rule per `agent-design-skill.md §3.6.3`.

## Theoretical Foundation

**Prospect Theory value function**:
- Theory / Study: Kahneman & Tversky (1979); refined in Tversky & Kahneman (1992).
- Citation: Kahneman, D., & Tversky, A. (1979). Prospect Theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. [https://doi.org/10.2307/1914185](https://doi.org/10.2307/1914185); Tversky, A., & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. [https://doi.org/10.1007/BF00122574](https://doi.org/10.1007/BF00122574)
- Core Insight: Decision-makers evaluate outcomes relative to a reference point, not in terms of absolute wealth; the value function is concave for gains, convex for losses, and steeper in the loss domain by a factor `λ ≈ 2.25`. This single asymmetry generates loss aversion, the disposition effect, the endowment effect, and the equity-premium puzzle as corollaries.
- Mathematical Formulation: `V(x) = x^α` for `x ≥ 0`; `V(x) = −λ · |x|^β` for `x < 0`, with `α = β ≈ 0.88` and `λ ≈ 2.25`.
- Empirical Evidence: Tversky & Kahneman (1992) elicit `α = 0.88, β = 0.88, λ = 2.25` from a 25-subject lottery experiment. Booij, van Praag & van de Kuilen (2010) replicate with `λ = 1.6–2.6` across 1,930 Dutch respondents.
- Relevance to This Agent: The agent's `loss_aversion_lambda` parameter is the Prospect-Theory `λ`; the agent's gain/loss curvatures are the `α, β` exponents.
- Calibration Source: Tversky & Kahneman (1992) Table 4.
- Falsification Conditions: Realised sell rate is the same in the gain and loss regions, or the gain–loss asymmetry has the wrong sign.
- Alternative Theories: Expected-utility CRRA (no kink, no reference point); Köszegi-Rabin (2006) reference-dependent preferences with stochastic reference point.

**Disposition effect**:
- Theory / Study: Shefrin & Statman (1985); empirically documented in Odean (1998) and extended in Frazzini (2006).
- Citation: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777–790. [https://doi.org/10.1111/j.1540-6261.1985.tb05002.x](https://doi.org/10.1111/j.1540-6261.1985.tb05002.x); Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775–1798. [https://doi.org/10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Core Insight: Investors realise gains substantially faster than losses. The Proportion of Gains Realised (PGR) exceeds the Proportion of Losses Realised (PLR) by 50–100% in retail brokerage data. The mechanism is a combination of Prospect-Theory loss aversion plus mental accounting that closes a position only at a "win" outcome.
- Mathematical Formulation: `PGR = realised_gains / (realised_gains + paper_gains)`; `PLR = realised_losses / (realised_losses + paper_losses)`; disposition effect ⇔ `PGR > PLR`.
- Empirical Evidence: Odean (1998) finds `PGR = 0.148`, `PLR = 0.098` on 10,000 retail accounts (1987–1993) — `PGR / PLR ≈ 1.51`. Frazzini (2006) extends to mutual funds.
- Relevance to This Agent: The `disposition` variant uses a small gain threshold (`θ_g ≈ 0.10`) and a large loss threshold (`θ_l ≈ 0.30`), reproducing the asymmetric realisation pattern.
- Calibration Source: Odean (1998), Table I.
- Falsification Conditions: PGR ≤ PLR in the simulated population.
- Alternative Theories: Tax-loss-harvesting (rational deferral of loss realisation for tax benefit); Lakonishok & Smidt (1986) trading-cost explanation.

**Endowment effect**:
- Theory / Study: Kahneman, Knetsch & Thaler (1990).
- Citation: Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. *Journal of Political Economy*, 98(6), 1325–1348. [https://doi.org/10.1086/261737](https://doi.org/10.1086/261737)
- Core Insight: Owning an asset induces a willingness-to-accept (WTA) that exceeds willingness-to-pay (WTP) by a factor of 2–7×, even after controlling for income and tax effects. The implied valuation gap suppresses voluntary selling.
- Mathematical Formulation: WTA / WTP ≈ 2 − 7; reservation sell price `R_endow = (1 + π_endow) · cost_basis` with `π_endow ≈ 0.5 − 1.0`.
- Empirical Evidence: Kahneman et al. (1990) coffee-mug experiment, WTA / WTP ≈ 2.2; Plott & Zeiler (2005) report sensitivity to procedure.
- Relevance to This Agent: The `endowment` variant inflates the reference point by `endowment_premium ∈ [0.3, 1.0]` so that the gain threshold becomes effectively unreachable until prices rise far above cost.
- Calibration Source: Kahneman, Knetsch & Thaler (1990) Tables 1–3.
- Falsification Conditions: Endowment-variant agents sell at the same price level as cost-basis-only variants.
- Alternative Theories: Plott & Zeiler (2005) — endowment effect is a procedural artefact; Heffetz & List (2014) — depends on subject pool.

**Status-quo bias**:
- Theory / Study: Samuelson & Zeckhauser (1988).
- Citation: Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7–59. [https://doi.org/10.1007/BF00055564](https://doi.org/10.1007/BF00055564)
- Core Insight: Decision-makers exhibit a systematic bias toward keeping the current arrangement, beyond what loss aversion predicts. Switching costs are largely psychological; the bias persists even in zero-cost choice settings.
- Mathematical Formulation: indifference threshold expanded by `δ_status_quo` so that switching is chosen only if `|ΔU| > δ_status_quo`.
- Empirical Evidence: Samuelson & Zeckhauser (1988) find ~40% choose default in TIAA-CREF-style retirement-allocation experiment.
- Relevance to This Agent: The `status_quo` variant adds an inertia gate `tick mod inertia_period == 0` that blocks any sell decision unless triggered on a rare evaluation tick.
- Calibration Source: Samuelson & Zeckhauser (1988), Table III.
- Falsification Conditions: Status-quo-variant agents revise positions as frequently as `disposition`-variant agents.
- Alternative Theories: Switching-cost models (Klemperer 1995); rational inattention (Sims 2003).

**Myopic loss aversion / equity-premium puzzle**:
- Theory / Study: Benartzi & Thaler (1995).
- Citation: Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73–92. [https://doi.org/10.2307/2118511](https://doi.org/10.2307/2118511)
- Core Insight: Loss-averse investors who evaluate their portfolios over short windows demand a much higher equity premium than infrequent evaluators do; an evaluation window of 1 year matches the historical equity-premium magnitude given `λ ≈ 2.25`.
- Mathematical Formulation: implied equity premium `EP(λ, T_eval)` is increasing in `λ` and decreasing in `T_eval`.
- Empirical Evidence: Benartzi & Thaler (1995) match 6.5% historical US equity premium with `T_eval = 12 months` and `λ = 2.25`.
- Relevance to This Agent: The `loss_averse` variant evaluates rolling P&L over `evaluation_window` ticks (default 20) so that short-horizon return drawdowns trigger sales even when long-run unrealised gains remain positive.
- Calibration Source: Benartzi & Thaler (1995), Table II.
- Falsification Conditions: Equity premium produced by a loss-averse-dominated population is independent of `evaluation_window`.
- Alternative Theories: Habit-formation utility (Campbell & Cochrane 1999); rare-disasters (Barro 2006).

## Design Purpose and Activation Triggers

Purpose: produce asymmetric retail order flow — early profit-taking on rallies, withheld supply on drawdowns, occasional break-even escalation — that recreates the disposition effect, the endowment-effect supply suppression, and the equity-premium volatility profile.

Call Frequency: every tick (with inertia gate for `status_quo` variant: every `inertia_period` ticks).

Prerequisite Signals:
- `price` (P) available
- `cost_basis` (R) per held position available — set at entry, persistent across ticks
- For `loss_averse` variant: `evaluation_window`-length rolling return available

Missing-Signal Policy: if `cost_basis` is unavailable for a held position, hold (the agent never sells without a reference point); if `price` is unavailable, hold all positions.

Activation Triggers:
- `g(t) = (P − R) / R ≥ +θ_g` (gain region beyond gain threshold): submit sell of `sell_fraction · position_size`.
- `g(t) ≤ −θ_l` (deep-loss region beyond loss threshold): submit sell of `sell_fraction · position_size` (capitulation).
- `−θ_l < g(t) < 0` and variant ∈ {`break_even_gambler`}: submit *additional buy* of `escalation_size · |g(t)|`, scaled by remaining cash.
- `<Default>`: hold.

Deactivation Conditions:
- All positions closed and cash exhausted: hibernate until next entry signal (scenario-driven).
- Cumulative drawdown on closed positions exceeds `kill_drawdown`: hard kill — agent ceases trading for the remainder of the episode (the trader has been "shaken out").

Market Contribution by Regime:

| Regime | Contribution  | Mechanism                                                                                     |
|--------|---------------|-----------------------------------------------------------------------------------------------|
| Bull   | Stabilising   | Early profit-taking provides supply that damps rally; mitigates pure noise overshoot          |
| Bear   | Destabilising | Refusal to realise losses removes liquidity; price impact of any forced selling is amplified  |
| Calm   | Stabilising   | Modest profit-taking on small `θ_g` crossings provides steady-state supply                    |
| Stress | Destabilising | Capitulation at `θ_l` produces clustered selling; break-even-gambler escalation amplifies bid |

Interaction with other agents: opposes the momentum trader (sells early into rallies the momentum trader is buying); is consumed by the market maker on profit-taking; amplifies the panic-forced seller's signal in deep-loss regions; counterfactual benchmark is the rational-analyst investor (which has symmetric thresholds).

## Behavioral Framework

#### Decision Information Set

| Signal              | Type       | Memory Window                                  | Rationale                                             |
|---------------------|------------|------------------------------------------------|-------------------------------------------------------|
| `price`             | Continuous | 1 tick                                         | Current market price                                  |
| `cost_basis`        | State      | persistent (per position)                      | Reference point for the value function                |
| `position_size`     | State      | persistent (per position)                      | Quantity available to sell                            |
| `evaluation_return` | Continuous | `evaluation_window` ticks (`loss_averse` only) | Short-horizon rolling return for myopic-LA evaluation |
| `tick_index`        | Discrete   | persistent (`status_quo` only)                 | Drives the inertia gate                               |
| `cash`              | State      | persistent                                     | Constrains escalation buys (`break_even_gambler`)     |

Does NOT use: `fundamental`, momentum, peer flow, sentiment, news, social-graph signals, or any liquidity / depth indicator. The agent is deliberately blind to fundamentals — its mental accounting is private and based purely on its own cost basis.

#### Core Behavioral Mechanism

1. For each held position, compute relative gain `g(t) = (P(t) − R) / R` where `R = cost_basis · (1 + endowment_premium)` (premium is 0 except in `endowment / status_quo` variants).
2. Compute prospect-theory value: `V(g) = g^α` if `g ≥ 0`, else `V(g) = −λ · |g|^β`.
3. **Inertia gate** (`status_quo` variant): if `tick mod inertia_period ≠ 0`, hold and skip steps 4–8.
4. **Gain branch**: if `g ≥ θ_g`, submit `SELL sell_fraction · position_size` at price `P`. The `disposition` variant uses a small `θ_g` (~0.10).
5. **Loss capitulation branch**: if `g ≤ −θ_l`, submit `SELL sell_fraction · position_size` at price `P`. The `loss_averse` variant uses a large `θ_l` (~0.30).
6. **Hold-loss branch** (default loss behaviour): if `−θ_l < g < 0`, hold (refuse to realise the loss).
7. **Break-even escalation** (`break_even_gambler` variant only): if `−θ_l < g < 0`, submit additionally `BUY size = escalation_size · |g| · cash_fraction` at price `P` to dollar-cost-average toward break-even.
8. **Myopic-LA gate** (`loss_averse` variant): if rolling `evaluation_return` over the last `evaluation_window` ticks is below `−theta_eval`, force-sell `panic_fraction · position_size` regardless of long-run paper P&L.
9. **Post-fill state update**: realised P&L credited; for partial sells, `position_size` reduced and `cost_basis` left unchanged (per-share cost is invariant under partial liquidation under the standard mental-accounting model). For escalation buys, new shares added at the *current* price as a separate position with its own `cost_basis = P(t)`.

#### Action Space

| Aspect               | Specification                                                                                                                             |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | market (sell on `θ_g` or `θ_l` cross); market BUY only for `break_even_gambler` variant escalation; hold-no-op                            |
| Price level rule     | market price (P) for both sell and escalation-buy; the agent does not place limit orders                                                  |
| Order quantity rule  | sell: `Q = sell_fraction · position_size` clipped by `position_size`; escalation buy: `Q = escalation_size ·                              |
| Order lifetime       | 1 tick (immediate execution if filled; otherwise discarded — mental accounting does not carry stale orders)                               |
| Cancellation policy  | unfilled orders are cancelled at end-of-tick; never replaced — the agent re-decides next tick                                             |
| Inventory constraint | per-position `position_size ≥ 0` (no shorting); aggregate `position_count ≤ position_max`; on hard cap breach, sell oldest position first |
| Wealth/leverage cap  | cash ≥ 0 hard; no margin in any variant; escalation buys (`break_even_gambler`) clipped by `escalation_cash_fraction · cash`              |
| Stop-loss/kill rule  | hard kill the agent for the rest of the episode if cumulative realised P&L falls below `kill_drawdown` (e.g. −50% of initial capital)     |

#### Mathematical Model

- **Decision variable**: per held position, signed quantity `Q_i*(t) ∈ {−position_size_i, 0, +escalation_buy_size}`.
- **Trigger function**:
  ```
  R_i = cost_basis_i · (1 + endowment_premium)
  g_i = (P − R_i) / R_i
  if (variant == status_quo) and (tick mod inertia_period ≠ 0):
      hold all positions
  elif g_i >= θ_g:
      sell sell_fraction · position_size_i
  elif g_i <= −θ_l:
      sell sell_fraction · position_size_i
  elif (variant == break_even_gambler) and (−θ_l < g_i < 0):
      buy escalation_size · |g_i| · cash_fraction
  elif (variant == loss_averse) and (rolling_return(eval_window) < −theta_eval):
      sell panic_fraction · position_size_i
  else:
      hold
  ```
- **Sizing function**: as in the trigger; sell sizes are fractions of current position, escalation sizes scale linearly with depth-of-loss `|g|`.
- **State variables**:

| Symbol            | Meaning                                                           | Initial value                       | Updated when                       |
|-------------------|-------------------------------------------------------------------|-------------------------------------|------------------------------------|
| `R_i`             | Reference point for position `i` (cost basis ± endowment premium) | entry price · (1+endowment_premium) | at entry; never updated thereafter |
| `position_size_i` | Quantity remaining in position `i`                                | size at entry                       | post-fill (decreases on sell)      |
| `cash`            | Cash available                                                    | initial endowment                   | post-fill                          |
| `roll_ret`        | Rolling `evaluation_window` return (`loss_averse`)                | 0                                   | every call, pre-decide             |
| `cum_pnl`         | Cumulative realised P&L                                           | 0                                   | post-fill                          |
| `mode`            | Active variant                                                    | configured at instantiation         | never                              |

- **State-update rule**: `roll_ret` updated **pre-decide**; `position_size_i`, `cash`, `cum_pnl` updated **post-fill**. `R_i` is **never** updated after entry — this is the mental-accounting invariant that drives the disposition effect; relaxing this assumption (e.g. exponentially-fading reference point, Köszegi-Rabin) is an ablation hook.
- **Determinism contract**: deterministic given `(P, R_i, position_size_i, cash, roll_ret, mode)` and parameters; population-level stochasticity (variant assignment, parameter draw, cost-basis draw at entry) is resolved at instantiation and seed-reproducible.

| Symbol              | Meaning                        | Default Value                                          | Source                            |
|---------------------|--------------------------------|--------------------------------------------------------|-----------------------------------|
| `α`                 | Gain-region curvature          | 0.88                                                   | Tversky & Kahneman (1992)         |
| `β`                 | Loss-region curvature          | 0.88                                                   | Tversky & Kahneman (1992)         |
| `λ`                 | Loss-aversion coefficient      | 2.25                                                   | Tversky & Kahneman (1992)         |
| `θ_g`               | Gain threshold (`disposition`) | 0.10                                                   | Odean (1998)                      |
| `θ_l`               | Loss threshold                 | 0.30                                                   | Odean (1998); Frazzini (2006)     |
| `endowment_premium` | Reference-point inflator       | 0.0 (default) / 0.5 (`endowment`) / 0.3 (`status_quo`) | Kahneman, Knetsch & Thaler (1990) |
| `inertia_period`    | Status-quo inertia gate        | 5 ticks                                                | Samuelson & Zeckhauser (1988)     |
| `evaluation_window` | Myopic-LA window               | 20 ticks                                               | Benartzi & Thaler (1995)          |
| `escalation_size`   | Break-even gambler scale       | 2.0                                                    | Calibration                       |

#### Behavioral Properties

- Time horizon: medium — positions are typically held until `θ_g` or `θ_l` is crossed, which can take many ticks; not high-frequency.
- Risk tolerance: low in the gain region (early profit-taking), high in the loss region (refusal to realise, escalation in `break_even_gambler`) — this is exactly the Prospect-Theory reflection effect.
- Information asymmetry: none — the agent uses only its own cost basis and the public price.
- Psychological profile: loss aversion (Kahneman–Tversky), disposition effect (Shefrin–Statman), endowment effect (Kahneman–Knetsch–Thaler), status-quo bias (Samuelson–Zeckhauser), myopic loss aversion (Benartzi–Thaler), reflection effect.

## Parameters

| Parameter                  | Type                                                                  | Default     | Valid Range | Sensitivity | Description                                              | Impact                                                                      | Source                            |
|----------------------------|-----------------------------------------------------------------------|-------------|-------------|-------------|----------------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------|
| `lossav_mode`              | enum<disposition,loss_averse,endowment,status_quo,break_even_gambler> | disposition | enum        | high        | Active sub-archetype variant                             | `endowment` → suppresses sells; `break_even_gambler` → escalation in losses | Standardised (synthesis)          |
| `loss_aversion_lambda`     | float                                                                 | 2.25        | [1.0, 5.0]  | high        | Prospect-theory `λ`                                      | Higher → wider asymmetry, larger PGR/PLR ratio, larger equity premium       | Tversky & Kahneman (1992)         |
| `gain_curvature_alpha`     | float                                                                 | 0.88        | (0, 1]      | medium      | Concavity of gain branch                                 | Lower → faster diminishing gain perception → earlier profit-taking          | Tversky & Kahneman (1992)         |
| `loss_curvature_beta`      | float                                                                 | 0.88        | (0, 1]      | medium      | Convexity of loss branch                                 | Lower → loss-region risk-seeking strengthens → more escalation              | Tversky & Kahneman (1992)         |
| `gain_threshold`           | float                                                                 | 0.10        | [0, 1]      | high        | `θ_g` for sell                                           | Lower → faster profit-taking, stronger PGR                                  | Odean (1998)                      |
| `loss_threshold`           | float                                                                 | 0.30        | [0, 1]      | high        | `θ_l` for capitulation                                   | Higher → losers held longer, weaker PLR, larger drawdown contribution       | Odean (1998); Frazzini (2006)     |
| `sell_fraction`            | float                                                                 | 1.0         | (0, 1]      | medium      | Fraction of position sold on trigger                     | Lower → smoother liquidation, less price impact                             | Standardised                      |
| `endowment_premium`        | float                                                                 | 0.0         | [0, 2]      | high        | Reference-point inflator (only `endowment / status_quo`) | Higher → stronger refusal-to-sell, larger floor under price                 | Kahneman, Knetsch & Thaler (1990) |
| `inertia_period`           | int                                                                   | 5           | [1, 100]    | medium      | Status-quo inertia gate                                  | Higher → fewer evaluation ticks, larger float-suppression effect            | Samuelson & Zeckhauser (1988)     |
| `evaluation_window`        | int                                                                   | 20          | [1, 250]    | medium      | Myopic-LA window (`loss_averse` only)                    | Lower → more myopic, larger implied equity premium                          | Benartzi & Thaler (1995)          |
| `theta_eval`               | float                                                                 | 0.10        | [0, 1]      | medium      | Rolling-return panic threshold (`loss_averse`)           | Lower → easier panic-trigger, more contribution to drawdown selling         | Benartzi & Thaler (1995)          |
| `panic_fraction`           | float                                                                 | 0.5         | (0, 1]      | medium      | Fraction sold on myopic-LA panic                         | Higher → larger drawdown amplification                                      | Calibration                       |
| `escalation_size`          | float                                                                 | 2.0         | [0, 10]     | high        | Coefficient on break-even gambler buys                   | Higher → larger doubling-down flow, larger price impact in losses           | Calibration                       |
| `escalation_cash_fraction` | float                                                                 | 0.20        | [0, 1]      | medium      | Cap on escalation buys per tick                          | Higher → faster cash exhaustion → harder kill-rule                          | Calibration                       |
| `position_max`             | int                                                                   | 10          | [1, 1000]   | low         | Max simultaneous positions                               | Higher → more dispersed mental accounting, smoother per-position triggers   | Calibration                       |
| `kill_drawdown`            | float                                                                 | −0.50       | (−1, 0]     | low         | Cumulative-P&L kill threshold                            | Less negative (closer to 0) → easier kill, fewer surviving instances        | Standardised                      |

## Population and Heterogeneity

| Aspect                         | Specification                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default population size        | scenario-dependent — typical large `N` (50–500) since retail loss-averse traders are a high-cardinality population in real markets                                                                                                                                                                                                                                                                              |
| Parameter heterogeneity policy | iid per-agent draw on `loss_aversion_lambda`, `gain_threshold`, `loss_threshold`, `endowment_premium`; shared (population-level) `evaluation_window` so that myopic-LA panics align temporally                                                                                                                                                                                                                  |
| Heterogeneity per parameter    | `lossav_mode` ← Categorical{disposition: 0.45, loss_averse: 0.25, endowment: 0.15, status_quo: 0.10, break_even_gambler: 0.05}; `loss_aversion_lambda` ← TruncatedNormal(2.25, 0.5, [1.0, 5.0]); `gain_threshold` ← LogNormal(ln 0.10, 0.4); `loss_threshold` ← LogNormal(ln 0.30, 0.4); `endowment_premium` ← Beta(2, 5) · 1.0 (only `endowment / status_quo`); `evaluation_window` shared at population level |
| Cross-agent correlation        | shared `evaluation_window` → temporally correlated panics; otherwise independent                                                                                                                                                                                                                                                                                                                                |
| Identity persistence           | identical across episodes; cost-basis per position re-drawn at scenario entry                                                                                                                                                                                                                                                                                                                                   |

## Worked Numerical Examples

Common parameters: `λ = 2.25`, `α = β = 0.88`, `θ_g = 0.10`, `θ_l = 0.30`, `sell_fraction = 1.0`, `position_size = 100`, `cost_basis R = 100.00`.

### Case 1 — Gain-region trigger (disposition variant)
Market state: `P(t) = 110.50`, `position_size = 100`, `R = 100`, `mode = disposition`.
Calculation:
  `g = (110.50 − 100) / 100 = +0.105`. `g ≥ θ_g = 0.10` → sell branch.
  `V(g) = 0.105^0.88 = 0.135` — perceived gain value modest but above threshold.
  Quantity = `1.0 · 100 = 100` shares.
Decision: emit `SELL 100 @ market`.
State update: position closed; realised P&L = `100 · (110.50 − 100) = +1,050`. `cum_pnl += 1050`. Cash credited.

### Case 2 — Deep-loss capitulation (loss_averse variant)
Market state: `P(t) = 65.00`, `R = 100`, `mode = loss_averse`, `evaluation_window = 20`, rolling 20-tick return = −0.18.
Calculation:
  `g = (65 − 100) / 100 = −0.35`. `g ≤ −θ_l = −0.30` → loss capitulation.
  `V(g) = −2.25 · 0.35^0.88 = −2.25 · 0.402 = −0.905` — large perceived loss.
  Quantity = `1.0 · 100 = 100`.
Decision: emit `SELL 100 @ market`.
State update: position closed; realised P&L = `−3,500`. `cum_pnl += −3500`. If `cum_pnl ≤ kill_drawdown · initial_capital`, hard-kill.

### Case 3 — Hold in shallow-loss region (default disposition behaviour)
Market state: `P(t) = 88.00`, `R = 100`, `mode = disposition`. Loss `g = −0.12`, between `−θ_l = −0.30` and `0`.
Calculation:
  `g` falls in the hold-loss region. `V(g) = −2.25 · 0.12^0.88 = −0.346` — perceived loss is painful but not catastrophic.
  No trigger crossed → hold.
Decision: HOLD.
State update: position unchanged; `R` unchanged.

### Case 4 — Endowment-premium suppression
Market state: `P(t) = 110.50`, `cost_basis = 100`, `mode = endowment`, `endowment_premium = 0.5` → effective `R = 100 · 1.5 = 150`.
Calculation:
  `g = (110.50 − 150) / 150 = −0.263`. Falls between `−θ_l = −0.30` and `0` (hold-loss region).
  Even though raw P&L vs cost basis is +10.5%, the endowment-inflated reference point makes this look like a *loss* relative to the agent's perceived "ownership" value.
Decision: HOLD.
State update: no change. The agent will not sell until `P > 165` (`g ≥ +θ_g = 0.10` against the inflated reference).

### Edge Case — Break-even-gambler escalation
Market state: `P(t) = 80.00`, `R = 100`, `mode = break_even_gambler`, `position_size = 100`, `cash = 5,000`, `escalation_size = 2.0`, `escalation_cash_fraction = 0.20`.
Calculation:
  `g = −0.20`. In hold-loss region for other variants; for `break_even_gambler`, escalation triggered.
  raw escalation `Q = escalation_size · |g| · cash / P = 2.0 · 0.20 · 5000 / 80 = 25` shares.
  cash cap `Q ≤ escalation_cash_fraction · cash / P = 0.20 · 5000 / 80 = 12.5` → `Q = 12`.
Decision: emit `BUY 12 @ market`. *Adds* a new position at `P = 80` with its own `cost_basis = 80` (the original position's `R = 100` is unchanged).
State update: new position appended (position_count++); `cash -= 12·80 = 960`. Original position's `g` unchanged. If `P` continues falling and original position's `g ≤ −θ_l`, capitulation triggers on it; the new (lower-cost-basis) position requires a much shallower fall to enter capitulation, creating two layered exit triggers.

## Validation and Calibration

**Calibration data sources**:
- `loss_aversion_lambda` ← Tversky & Kahneman (1992), Table 4: λ̂ = 2.25, σ ≈ 0.5.
- `gain_threshold`, `loss_threshold` ← Odean (1998), Table I: PGR ≈ 0.148, PLR ≈ 0.098 → ratio 1.51.
- `endowment_premium` ← Kahneman, Knetsch & Thaler (1990): WTA / WTP ≈ 2.2 → premium ≈ 1.0; conservative default 0.5.
- `evaluation_window`, `theta_eval` ← Benartzi & Thaler (1995): T_eval = 12 months matches 6.5% historical equity premium.
- `inertia_period` ← Samuelson & Zeckhauser (1988): default-stickiness ≈ 40% of decisions.

**Expected stylized facts** when this agent dominates the population:
- Disposition ratio `PGR / PLR > 1.3` (Odean 1998, Frazzini 2006).
- Asymmetric volume distribution: volume concentrated above cost basis, sparse below — observable as kink in price-volume hexbin.
- Long-run reversal of momentum — losers get held until forced exit, then released en masse (DeBondt & Thaler 1985 reversal).
- Equity-premium-puzzle elevated implied premium consistent with Benartzi & Thaler (1995).
- Endowment-premium scenarios: realised volume drops 30–60% compared to symmetric-threshold benchmark.

**Sanity bounds (red flags during simulation)**:
- PGR ≤ PLR — disposition mechanism inverted; check threshold parameters.
- Sell rate identical above and below cost basis — asymmetry not implemented.
- Endowment-variant agents trade at the same volume as `disposition` variant — endowment premium not biting.
- `break_even_gambler` cash never exhausts despite repeated escalation — `escalation_cash_fraction` cap not applied.
- Cumulative population P&L grows without bound — likely missing `kill_drawdown` rule.

#### Ablation Hooks

| Ablation name          | Setting                                              | Hypothesis tested                                                                                      |
|------------------------|------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `lambda_unity`         | `loss_aversion_lambda = 1.0`                         | Disposition effect requires `λ > 1`; setting to 1 should collapse PGR/PLR to ~1.0                      |
| `symmetric_thresholds` | `gain_threshold = loss_threshold`                    | Tests whether asymmetric thresholds (not just λ) are needed for the disposition effect                 |
| `disable_endowment`    | `endowment_premium = 0` for all                      | Endowment effect contribution to volume suppression                                                    |
| `force_inertia_off`    | `inertia_period = 1`                                 | Status-quo bias contribution to volume                                                                 |
| `gambler_only`         | `lossav_mode = break_even_gambler` exclusive         | Isolates the convex-region risk-seeking channel                                                        |
| `evaluation_long`      | `evaluation_window = 250` (~1 trading year of ticks) | Tests Benartzi–Thaler prediction that long evaluation windows attenuate the equity-premium implication |

## Academic References

| #  | Citation                                                                                                                                                                                                                             | Notes                                         |
|----|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1  | Kahneman, D., & Tversky, A. (1979). Prospect Theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185                                                                             | Foundational value-function theory            |
| 2  | Tversky, A., & Kahneman, D. (1992). Advances in Prospect Theory. *J. Risk and Uncertainty*, 5(4), 297–323. https://doi.org/10.1007/BF00122574                                                                                        | Calibrated `α, β, λ` parameter estimates      |
| 3  | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *JF*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x                                                      | Disposition-effect theory                     |
| 4  | Odean, T. (1998). Are investors reluctant to realize their losses? *JF*, 53(5), 1775–1798. https://doi.org/10.1111/0022-1082.00072                                                                                                   | PGR/PLR empirical calibration                 |
| 5  | Frazzini, A. (2006). The disposition effect and underreaction to news. *JF*, 61(4), 2017–2046. https://doi.org/10.1111/j.1540-6261.2006.00896.x                                                                                      | Mutual-fund disposition extension             |
| 6  | Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. *JPE*, 98(6), 1325–1348. https://doi.org/10.1086/261737                                                      | Endowment-effect calibration                  |
| 7  | Plott, C. R., & Zeiler, K. (2005). The willingness to pay–willingness to accept gap. *AER*, 95(3), 530–545. https://doi.org/10.1257/0002828054201387                                                                                 | Endowment-effect alternative theory           |
| 8  | Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. *JRU*, 1(1), 7–59. https://doi.org/10.1007/BF00055564                                                                                                    | Status-quo-bias theory                        |
| 9  | Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *QJE*, 110(1), 73–92. https://doi.org/10.2307/2118511                                                                                      | Myopic-LA evaluation-window calibration       |
| 10 | DeBondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *JF*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                                                                                 | Long-run reversal stylized fact               |
| 11 | Köszegi, B., & Rabin, M. (2006). A model of reference-dependent preferences. *QJE*, 121(4), 1133–1165. https://doi.org/10.1093/qje/121.4.1133                                                                                        | Stochastic-reference-point alternative theory |
| 12 | Booij, A. S., van Praag, B. M. S., & van de Kuilen, G. (2010). A parametric analysis of prospect theory's functionals for the general population. *Theory and Decision*, 68(1–2), 115–148. https://doi.org/10.1007/s11238-009-9144-4 | Population-level parameter range              |
| 13 | Heffetz, O., & List, J. A. (2014). Is the endowment effect an expectations effect? *J. European Economic Association*, 12(5), 1396–1422. https://doi.org/10.1111/jeea.12091                                                          | Endowment-effect robustness                   |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | masim agent-pool curation team                                                                                                                                                                                                                                                                                                  |
| Reviewed by | _pending_                                                                                                                                                                                                                                                                                                                       |
| Created     | 2026-06-11                                                                                                                                                                                                                                                                                                                      |
| Version     | 1.0.0                                                                                                                                                                                                                                                                                                                           |
| Change log  | 1.0.0 (2026-06-11): Initial pilot-depth specification synthesising the 12 merged profiles in `DEDUPLICATION_REPORT.md`. Conforms to `masim/format/agent-design-skill.md` v1 + `masim/format/agent-design-finance.md` v1. Variants `disposition / loss_averse / endowment / status_quo / break_even_gambler` (5-mode synthesis). |
| Status      | canonical                                                                                                                                                                                                                                                                                                                       |
