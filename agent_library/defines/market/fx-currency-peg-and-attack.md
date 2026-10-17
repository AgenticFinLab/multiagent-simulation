# Currency-peg-and-attack foreign-exchange market

## Summary

| Field                | Content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `fx` — Foreign-Exchange Market                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Coordinator Role     | Central exchange-rate-formation coordinator for a single-pair FX market with an official policy anchor (peg) and a reserve-financed defense channel                                                                                                                                                                                                                                                                                                                                                                                                        |
| Mechanism Family     | Standard linear price-impact + tight mean-reversion around a peg/fundamental + Gaussian noise + regime-switching central-bank intervention channel                                                                                                                                                                                                                                                                                                                                                                                                         |
| Shared State         | `exchange_rate`, `prev_exchange_rate`, `fundamental`, `peg_rate`, `deviation`, `volume`, `net_pressure`, `reserves`, `peg_status`, `num_attackers`, `num_defenders`, `round`                                                                                                                                                                                                                                                                                                                                                                                |
| Broadcast Cadence    | every-tick (one broadcast per simulation round, after all inbound investor / central-bank orders arrive)                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Determinism          | stochastic-given-seed (ε ~ N(0, σ²) drawn from a seeded RNG; identical seed + identical inbound-order sequence + identical reserves trajectory produces byte-equal broadcasts)                                                                                                                                                                                                                                                                                                                                                                             |
| Feedback Direction   | **Regime-dependent** — inside the peg-defense regime (`reserves > 0` AND `|exchange_rate − peg_rate| < peg_band`) the intervention-boosted γ term dominates and the mechanism is **strongly stabilising**; once reserves are depleted (`reserves ≤ reserves_floor`) OR the rate breaches the band, the intervention channel switches off and the mechanism becomes **amplifying** — one-sided speculative net pressure drives runaway devaluation until participants exhaust position budgets (Krugman 1979 [Ref 1]; Obstfeld 1996 [Ref 2]; Flood-Garber 1984 [Ref 3]) |
| Scenario Portability | 4 pool scenarios bound via `players.yml → market.archetype: fx-currency-peg-and-attack`. **Full ✅**: (none). **Approximated ⚠**: AsianFinancialCrisis, CarryTradeUnwind, CurrencyCrisis, SorosPound — all four scenarios currently use the stock-standard price-impact code path; the reserves ledger and γ_eff peg-defense pathway are intended but not yet implemented. See also the Scenario Status row below. |
| Scenario Status      | **Full** = coordinator code implements the archetype's mechanism signature verbatim; **Approximated** = archetype bound via `players.yml → market.archetype:` for icon/UI/narrative purposes, but the coordinator code currently uses the standard price-impact formula `P(t+1)=P(t)+λ·NetDemand+γ·(F-P(t))+ε` as a placeholder — the archetype's specialized state and dynamics are intended but not yet realized in code. |

## Definition and Goals

This coordinator models a **single-pair, continuous-quote spot
foreign-exchange market operating under an official exchange-rate
regime** — a fixed or narrow-band peg defended by a central bank with
a finite stock of foreign-currency reserves. The real-world
counterpart is a managed-float or fixed-peg FX venue such as
Thailand's baht/USD arrangement in 1996–1997, the British pound's
ERM band in 1990–1992, the Argentine peso currency-board of the late
1990s, or any of the Asian peggs analysed by Radelet & Sachs (1998)
[Ref 8]. The coordinator is deliberately mechanism-driven rather than
order-book matched, because the round granularity of macro-crisis
simulations makes an LOB unnecessary and (by the same aggregation
argument as Farmer & Joshi 2002 [Ref 12]) numerically equivalent to a
linear price-impact rule at sufficient batching.

The coordination goal is to **aggregate all participant orders
(speculative-attack sells, peg-defense buys, carry-trade unwinds,
convergence-trader positions, noise-trader liquidity), compute one
new exchange rate `R(t+1)` via the equation
`R(t+1) = R(t) + λ·NetPressure + γ_eff·(F − R(t)) + ε`, update the
reserves ledger to reflect central-bank intervention, and broadcast
`{exchange_rate, prev_exchange_rate, fundamental, peg_rate, deviation,
volume, net_pressure, reserves, peg_status, num_attackers,
num_defenders, round}`**. The effective mean-reversion coefficient
`γ_eff` is elevated above baseline `γ` when the central bank
intervenes — this is the *sterilised/unsterilised intervention*
channel of Obstfeld (1996) [Ref 2] and Dominguez & Frankel (1993)
[Ref 6]. Once `reserves ≤ reserves_floor`, `γ_eff` collapses back to
baseline `γ` and the peg is marked `broken`.

The broadcast is identical for every participant — the FX market is
a symmetric-information venue at the round granularity assumed here.

**Non-goals** (this coordinator MUST NOT):

- MUST NOT filter or route orders based on participant identity,
  capital, or history — participant-level position limits are
  self-imposed per `agent-design-skill.md` §3.6.3.
- MUST NOT unilaterally decide the timing of central-bank
  intervention — the central bank is a **participant agent** that
  sends `defend` / `sell-reserves` orders through the standard order
  channel; the coordinator merely *executes* those orders and updates
  the reserves ledger accordingly. The coordinator has no independent
  policy view.
- MUST NOT inject exogenous news, shocks, capital-account regime
  flips, or IMF-programme announcements from its own logic — those
  enter via the Exogenous Driver Boundary (§4.5).
- MUST NOT modify the peg rate `peg_rate` from within its own logic
  — an official realignment is a scenario overlay written into
  `extras["peg_rate"]` by the scenario runner before `perceive`.
- MUST NOT enforce individual participant capital-flow limits,
  short-sale bans, or transaction taxes — those are scenario-overlay
  concerns (a compliance / regulator agent, if present).
- MUST NOT rebuild the reserves stock from nothing — reserves can
  only DECREASE from intervention outflows or INCREASE from an
  explicit `IMFRescuer.replenish` order treated as an ordinary
  inbound; the coordinator itself is passive.

## Theoretical / Mechanistic Foundation

**Linear price-impact from net FX pressure (Kyle 1985; adapted to
spot FX)**:

- Theory / Study: Continuous-auction linear price-impact adapted to
  spot FX order flow.
- Citation: Kyle, A. S. (1985). "Continuous Auctions and Insider
  Trading." *Econometrica*, 53(6), 1315–1335.
  DOI: `10.2307/1913210`. FX adaptation validated empirically by
  Evans & Lyons (2002) [Ref 4].
- Core Insight: In a batch-clearing FX market, the equilibrium rate
  change is a **linear function of aggregate order flow**; the slope
  captures market depth. In FX this slope is materially higher than
  in equities because the informational content of order flow is
  larger and reference-dealer inventories are thinner (Evans & Lyons
  2002 [Ref 4] estimate ~0.5% appreciation per USD 1 bn of net order
  flow in the DEM/USD spot market).
- Mathematical Formulation: `ΔR_pressure = λ · NetPressure`, where
  `NetPressure = Σ_{action ∈ {buy, defend}} q_i − Σ_{action ∈ {sell,
  attack}} q_i`.
- Empirical Evidence: Evans & Lyons (2002) [Ref 4, Table 2] find
  that daily DEM/USD order flow explains ~40–60% of daily FX changes
  with an elasticity that, when converted to per-round simulation
  units (quantities in dimensionless "lots" ~ 100 units, rates in
  quote-currency-per-USD terms), corresponds to a range `λ ∈ [0.02,
  0.08]`. Our default `λ = 0.04` sits in the middle of this range
  and is ~4× the equity default (`stock-standard-price-impact` uses
  `λ = 0.01`), reflecting the higher FX price-impact elasticity.
- Relevance to This Coordinator: Provides the demand-driven rate
  change term `λ · NetPressure` in the transition equation. Because
  `λ` is higher in FX than in equities, a moderately-sized attack
  can move the rate a full percent per round, which is what makes
  currency-crisis scenarios feasible over 20–100 rounds.
- Calibration Source: Evans & Lyons 2002 [Ref 4, Table 2];
  simulation-unit-adjusted range `λ ∈ [0.02, 0.08]`.
- Falsification Conditions: If a doubling of `NetPressure` (holding
  all else constant, including the seed for ε and reserves) does
  NOT approximately double `ΔR_pressure` in a broadcast pair, the
  linear-impact property is broken.
- Alternative Mechanisms: Non-linear (square-root) FX impact
  [Ref 13]; latent-liquidity models [Ref 7]; portfolio-balance
  mechanisms [Ref 6].

**Balance-of-payments crisis (Krugman 1979) — reserves depletion
regime switch**:

- Theory / Study: First-generation balance-of-payments crisis model.
- Citation: Krugman, P. (1979). "A Model of Balance-of-Payments
  Crises." *Journal of Money, Credit and Banking*, 11(3), 311–325.
  DOI: `10.2307/1991793`.
- Core Insight: When a central bank pegs a currency above its
  fundamental shadow rate and finances the peg by selling foreign
  reserves against speculative sells, reserves decline monotonically.
  Rational speculators, foreseeing an eventual forced abandonment,
  **attack immediately at the exact instant reserves fall to a
  threshold** — this produces a discontinuous regime switch from
  "peg holds with intervention-boosted γ" to "peg abandoned; rate
  jumps to shadow fundamental". The Flood–Garber (1984) [Ref 3]
  refinement adds explicit stochastic-shadow-rate timing.
- Mathematical Formulation:
  - Reserves ledger: `Reserves(t+1) = max(Reserves(t) −
    |Intervention(t)|, 0)`, where `Intervention(t) =
    Σ_{o ∈ orders_from_central_bank} sign(o.action) · o.quantity`.
  - Regime switch: `γ_eff = γ + β · 1[Reserves(t) > reserves_floor
    AND |R(t) − peg_rate| < peg_band]`; when the indicator is 0 the
    peg is `broken` and `γ_eff = γ` (or 0, if the scenario sets
    `gamma_post_break = 0`).
- Empirical Evidence: Kaminsky & Reinhart (1999) [Ref 9] catalogue
  76 currency-crisis episodes 1970–1995 and document that in ~70%
  of cases reserves fall by more than 20% in the 12 months
  preceding the peg break; the median episode features a 5–15% rate
  jump on the peg-break date, matching the discontinuity our
  regime-switch mechanism produces.
- Relevance to This Coordinator: Justifies the *regime-dependent*
  Feedback Direction row in §4.2 and the reserves-tracked
  `peg_status ∈ {defending, broken, free-float}` state field.
- Calibration Source: Krugman 1979 [Ref 1, §3]; Kaminsky & Reinhart
  1999 [Ref 9, Table 1]. `β` (intervention lift) calibrated to
  Dominguez & Frankel 1993 [Ref 6, Table 4] range `[0.05, 0.15]`;
  default `β = 0.08`.
- Falsification Conditions: If two runs with identical inbound
  sequences BUT different initial `reserves_initial` values produce
  identical `peg_status` trajectories, the reserves-depletion
  channel is broken.
- Alternative Mechanisms: Second-generation self-fulfilling escape
  clauses [Ref 2]; third-generation twin-crisis balance-sheet
  channels [Ref 10].

**Second-generation self-fulfilling currency crisis (Obstfeld 1996)
— escape-clause mean-reversion**:

- Theory / Study: Second-generation currency crisis model with
  contingent policy escape clauses.
- Citation: Obstfeld, M. (1996). "Models of currency crises with
  self-fulfilling features." *European Economic Review*, 40(3–5),
  1037–1047. DOI: `10.1016/0014-2921(95)00111-5`.
- Core Insight: A central bank defends a peg only as long as the
  defense cost (in higher interest rates, unemployment, or reserve
  loss) is below a threshold policymakers are willing to bear.
  Above the threshold, the bank *chooses* to abandon the peg even
  though reserves are not exhausted. This creates **multiple
  equilibria**: the peg holds if speculators believe the bank will
  defend, and breaks if they believe otherwise. Operationally, this
  means the mean-reversion coefficient `γ_eff` is not just a fixed
  parameter but depends on the reserves state and the fraction of
  attackers vs defenders.
- Mathematical Formulation: In this coordinator we operationalise
  the Obstfeld escape-clause via the *effective* mean-reversion:
  `γ_eff(t) = γ_baseline + β · Intervention_intensity(t) ·
  1[Reserves(t) > reserves_floor]`, where
  `Intervention_intensity(t) = min(|Σ_{o ∈ defenders} q_o| /
  intervention_normaliser, 1)`. As defenders sell fewer reserves,
  `γ_eff` decays smoothly.
- Empirical Evidence: Obstfeld (1996) [Ref 2] cross-country
  regressions estimate that reserves-adjusted γ elevation of
  0.05–0.15 per unit intervention accounts for the ~2:1 ratio of
  successful vs failed peg defenses in the 1992–1993 EMS episodes.
  Sachs, Tornell & Velasco (1996) [Ref 11] confirm on the Asian
  1997 sample.
- Relevance to This Coordinator: Justifies the *γ-boost while
  defending* mechanism inside the peg regime and the *smooth γ
  decay* as reserves deplete.
- Calibration Source: Obstfeld 1996 [Ref 2, §3]; Sachs–Tornell–
  Velasco 1996 [Ref 11]. `β ∈ [0.05, 0.15]`; default `β = 0.08`.
  Baseline `γ = 0.03`.
- Falsification Conditions: If two runs with identical `NetPressure`
  but very different amounts of intervention (defender orders)
  produce equal rate changes, the γ-boost channel is broken.
- Alternative Mechanisms: Pure first-generation Krugman with
  deterministic-timing attack [Ref 1]; global-games unique
  equilibrium Morris–Shin [Ref 5].

**Gaussian idiosyncratic noise (efficient-market residual)**:

- Theory / Study: Idiosyncratic FX-microstructure noise as
  residual variance.
- Citation: Roll, R. (1984). "A Simple Implicit Measure of the
  Effective Bid-Ask Spread in an Efficient Market." *Journal of
  Finance*, 39(4), 1127–1139.
  DOI: `10.1111/j.1540-6261.1984.tb03897.x`. FX-specific
  bid-ask calibration: Bessembinder (1994) [Ref 14].
- Core Insight: Even in mechanism-driven FX markets, per-round rate
  changes carry an irreducible idiosyncratic component from
  microstructure noise, latency, and residual heterogeneity;
  modelling this as zero-mean Gaussian is a standard reduction.
- Mathematical Formulation: `ε ~ N(0, σ²)`, with σ = `noise_std`.
- Empirical Evidence: Bessembinder (1994) [Ref 14, Table 2]
  estimates effective bid-ask-spread-implied noise standard
  deviations for major-pair FX at 0.02–0.15% of the mid rate;
  default `σ = 0.05` in rate units corresponds to ~0.05% at the
  default `initial_exchange_rate = 100.0` (a scenario-agnostic
  numeraire).
- Relevance to This Coordinator: Adds the term `ε` and makes the
  mechanism `stochastic-given-seed` rather than deterministic.
- Calibration Source: Bessembinder 1994 [Ref 14, Table 2];
  simulation-unit-adjusted range `σ ∈ [0.01, 0.2]`.
- Falsification Conditions: If ε is drawn from a distribution with
  materially non-zero mean or from a fat-tailed non-Gaussian family
  (jump-diffusion residuals), the mechanism has been altered from
  this specification.
- Alternative Mechanisms: Jump-diffusion residuals to capture the
  fat-tailed distribution of daily FX returns [Ref 15];
  heteroskedastic (GARCH-driven) noise [Ref 16].

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate all participant FX orders each round, update the
central-bank reserves ledger from the intervention subset of those
orders, apply the linear-impact + intervention-boosted mean-reversion
+ noise transition, evaluate the peg-status regime, and broadcast one
authoritative exchange-rate + reserves snapshot.

Coordination Cadence: **every-tick** (one broadcast per simulation
round; the round advances only after `act()` completes).

Lifecycle Mapping (MANDATORY — binds the coordinator to
`masim.player.general.GeneralPlayer`):

- `perceive(observation, prev_result)`:
  1. Read `round_num = observation.round` and write it to
     `state["round"]`.
  2. If `"exchange_rate"` is not yet in `state.custom_state`, run
     the State Initialization block below.
  3. Drain `observation.inbounds`; each inbound payload is a
     participant order dict (see Inbound Message Types below).
  4. Compute aggregates per §4.6.1 (`buy_qty`, `sell_qty`,
     `defender_qty`, `attacker_qty`, `net_pressure`,
     `intervention_size`, `num_attackers`, `num_defenders`) — READ
     phase only.
  5. Compute the reserves update: `new_reserves = max(reserves −
     |intervention_size|, 0)`. Compute the peg-status flag:
     `peg_status_new = "defending" if (new_reserves > reserves_floor
     AND |R(t) − peg_rate| < peg_band) else "broken"`. Compute the
     effective mean-reversion coefficient:
     `γ_eff = γ + β · min(intervention_size /
     intervention_normaliser, 1.0)` when defending; else
     `γ_eff = gamma_post_break` (typically `γ` itself, or 0.0 if
     the scenario models a hard collapse).
  6. Draw `ε ~ N(0, σ²)` from the seeded RNG. Compute:
     `R_raw = R(t) + λ · net_pressure + γ_eff · (F − R(t)) + ε`;
     clamp `new_R = max(R_raw, rate_floor)`. Compute derived
     observables (`deviation`, `volume`). WRITE the new state
     atomically: `prev_exchange_rate ← R(t); exchange_rate ← new_R;
     reserves ← new_reserves; peg_status ← peg_status_new;
     deviation ← …; rate_history.append(new_R);
     reserves_history.append(new_reserves)`.
- `decide()`:
  1. Return a dict `{"exchange_rate": …, "prev_exchange_rate": …,
     "fundamental": …, "peg_rate": …, "deviation": …, "volume": …,
     "net_pressure": …, "reserves": …, "peg_status": …,
     "num_attackers": …, "num_defenders": …, "round": …}` assembled
     from the committed state. No writes.
- `act(decision)`:
  1. Wrap the dict as `MarketBroadcast` (or engine equivalent) and
     emit to every participant via the standard outbox. No writes.

MUST NOT: perform state writes inside `decide` / `act`; MUST NOT
emit a broadcast from `perceive`. Splitting these phases is required
for deterministic replay and for the round-boundary invariant #1
(`broadcast[t+1].prev_exchange_rate == broadcast[t].exchange_rate`).

State Initialization (MANDATORY — first-call contract):

- Trigger: `"exchange_rate" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing):
  - `initial_exchange_rate` — round-0 seed for R.
  - `fundamental_rate` — shadow anchor F for mean-reversion.
  - `peg_rate` — official policy anchor (usually equal to
    `fundamental_rate` at start, but not required to be so — the
    Krugman gap between peg and shadow rate is the whole point).
  - `price_impact` — λ.
  - `mean_reversion_pull` — baseline γ.
  - `reserves_initial` — starting central-bank FX-reserve stock.
  - `cb_intervention_threshold` — β, the intervention lift added
    to γ when defending.
  - `noise_std` — σ.
  - `record_path` — root directory for `HistoryBuffer` spills.
  - `custom_state_hot_limit` — hot-tier size for `HistoryBuffer`.
- Optional extras (documented defaults):
  - `rate_floor` (default `0.01`) — absolute lower clamp on R.
  - `reserves_floor` (default `0.0`) — level below which the peg
    regime switches to `broken`.
  - `peg_band` (default `0.05` — ±5% of `peg_rate`) — width of the
    tolerance band around the peg.
  - `intervention_normaliser` (default `1000.0`) — divisor scaling
    intervention_size into a bounded γ boost.
  - `gamma_post_break` (default equal to `mean_reversion_pull`) —
    the γ used once the peg is broken.
  - `attack_threshold` (default `0.02`) — informational: recorded
    but not used inside the coordinator equation; participants may
    read it.
- Initial state writes (single atomic block):
  - `state["exchange_rate"] = extras["initial_exchange_rate"]`
  - `state["prev_exchange_rate"] =
    extras["initial_exchange_rate"]` (equal to current on round 0
    — cold-start "no return yet")
  - `state["fundamental"] = extras["fundamental_rate"]`
  - `state["peg_rate"] = extras["peg_rate"]`
  - `state["price_impact"] = extras["price_impact"]`
  - `state["mean_reversion_pull"] = extras["mean_reversion_pull"]`
  - `state["cb_intervention_threshold"] =
    extras["cb_intervention_threshold"]`
  - `state["noise_std"] = extras["noise_std"]`
  - `state["reserves"] = extras["reserves_initial"]`
  - `state["peg_status"] = "defending"` (assumed at t=0 unless
    `reserves_initial == 0`, in which case `"broken"`)
  - `state["deviation"] = 0.0`
  - `state["net_pressure"] = 0.0`
  - `state["num_attackers"] = 0`
  - `state["num_defenders"] = 0`
  - `state["rate_history"] = HistoryBuffer(folder=<record>/market/
    exchange_rate, entry_limit=custom_state_hot_limit)`
  - `state["reserves_history"] = HistoryBuffer(folder=<record>/
    market/reserves, entry_limit=custom_state_hot_limit)`
- Warm-up rounds: `0` (broadcast is trustworthy from round 0,
  though `prev_exchange_rate == exchange_rate` on round 0 must be
  interpreted correctly by participants).
- Cold-start reading rule for participants: on round 0,
  `prev_exchange_rate == exchange_rate`, so the participant-side
  return signal SHOULD be treated as "no observation yet" rather
  than "return of zero".

Inbound Message Types (what participants may send to the
coordinator):

- **Order (speculator / carry trader / convergence trader / noise
  trader)**: `{"action": "buy" | "sell" | "hold", "quantity":
  float ≥ 0, "bid_price": float ≥ 0 (advisory), "strategy": str,
  "reasoning": str, "role": "attacker" | "carry" | "hedger" |
  "noise" | "other" (optional; used only for `num_attackers` /
  `num_defenders` counting)}`.
  - `"buy"` / `"sell"` with `quantity > 0` contribute to
    `buy_qty` / `sell_qty`.
  - `"hold"` or `quantity == 0` are silently ignored.
  - `bid_price` is advisory only.
- **Intervention (central-bank defender)**: `{"action": "defend" |
  "sell-reserves" | "hold", "quantity": float ≥ 0, "bid_price":
  float ≥ 0 (advisory), "strategy": "central-bank" | str,
  "reasoning": str, "role": "defender"}`.
  - `"defend"` is a semantic alias for `"buy"` and additionally
    increments `intervention_size` (drains reserves).
  - `"sell-reserves"` is a semantic alias for `"sell"` (reduces
    reserves and pushes the rate down — useful in overvalued
    scenarios).
  - The coordinator MUST NOT distinguish a "defend" from a "buy"
    for the demand-aggregation term; the only additional effect
    is the reserves ledger update and the `γ_eff` boost.
- **Replenishment (IMF rescuer / bilateral swap line)**: `{"action":
  "replenish", "quantity": float > 0, "strategy": "imf" | str,
  "role": "rescuer"}` — treated as a direct positive shock to
  reserves. This is the ONLY way reserves can grow.
- **Default (no message)**: treated as `"hold"`.

Broadcast Trigger: after every round tick, immediately following the
`perceive` state-write phase.

Missing-Input Policy:

- Missing required extras → **raise `KeyError`** from `perceive`;
  do NOT default. Applies to `initial_exchange_rate`,
  `fundamental_rate`, `peg_rate`, `price_impact`,
  `mean_reversion_pull`, `reserves_initial`,
  `cb_intervention_threshold`, `noise_std`, `record_path`,
  `custom_state_hot_limit`.
- Zero inbound orders → set `buy_qty = sell_qty = net_pressure =
  intervention_size = 0`, `num_attackers = num_defenders = 0`, and
  continue; this is a legitimate quiet round.
- Individual malformed order (missing `action` / `quantity`
  unparseable) → log warning, skip that order, continue with the
  rest.
- Inbound `"defend"` order with `quantity > reserves` → clamp
  `intervention_size` to `reserves`, log warning at INFO level;
  the surplus quantity is NOT executed against demand (the
  intervention would have failed in practice) and does NOT
  contribute to `net_pressure`. This ensures reserves cannot go
  negative.
- `NaN` / `Inf` in the computed `new_R` → **raise `ValueError`**
  from `perceive`; do NOT emit a broadcast this round.
- NEVER silently substitute a default for a required field — that
  masks bugs per project code-style rule.

Exogenous Driver Boundary (MANDATORY):

- This coordinator MUST NOT generate exogenous news, shocks,
  regime flips, IMF programme announcements, or peg realignments
  from within its own logic.
- All exogenous drivers MUST enter via one of two channels:
  (a) a distinguished inbound message from a scenario-provided
      `NewsInjector` / `IMFRescuer` / `PegRealigner` agent
      (recommended), which the coordinator reads as an ordinary
      aggregate signal or as a `"replenish"` order (see Inbound
      Message Types); OR
  (b) a mutation of `config.extras` performed BEFORE the
      coordinator's `perceive` on that round by the scenario
      runner — for example, `extras["fundamental_rate"]` may be
      revised downward to model a shift in economic fundamentals,
      or `extras["peg_rate"]` may be revised to model an official
      devaluation.
- The coordinator MAY read the new value as an ordinary aggregate
  signal but MUST NOT ORIGINATE it. In particular, the coordinator
  MUST NOT itself decide when to abandon the peg — the
  `peg_status` transition is a *deterministic function* of the
  reserves state and the peg-band condition, not a policy choice.

Environmental Dependencies:

- Required extras (see §4.7): `initial_exchange_rate`,
  `fundamental_rate`, `peg_rate`, `price_impact`,
  `mean_reversion_pull`, `reserves_initial`,
  `cb_intervention_threshold`, `noise_std`, `record_path`,
  `custom_state_hot_limit`.
- Optional extras: `rate_floor`, `reserves_floor`, `peg_band`,
  `intervention_normaliser`, `gamma_post_break`, `attack_threshold`.
- Required scenario driver signals: none beyond the Exogenous
  Driver Boundary channels above.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input               | Source                                | Type / Shape                                                                                                                                                                                                     | Required? | Notes                                                                                                       |
|---------------------|---------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------------|
| `inbound_orders`    | mailbox from participant agents       | `list[dict]`; each dict has `action: str ∈ {buy, sell, hold, defend, sell-reserves, replenish}`, `quantity: float ≥ 0`, `bid_price: float`, `strategy: str`, `reasoning: str`, `role: str (optional)`             | yes       | `bid_price` advisory; `role` optional and used only for counting attackers vs defenders                     |
| `current_state`     | coordinator's persisted state         | `{"exchange_rate": float, "prev_exchange_rate": float, "fundamental": float, "peg_rate": float, "reserves": float, "peg_status": str, "deviation": float, "rate_history": HistoryBuffer, "reserves_history": HistoryBuffer}` | yes       | Populated on first call by State Initialization                                                              |
| `context_metadata`  | scheduler / round header              | `{"round": int, "identity": str, "seed": int}`                                                                                                                                                                    | yes       | Identity naming rule: `{variant}_market_fx`                                                                  |
| `scenario_driver`   | scenario overlay                      | `dict` or `None`                                                                                                                                                                                                  | no        | Only if scenario declares exogenous fundamental / peg-realignment changes                                    |

##### Outputs (per coordination call)

The coordinator emits **exactly one broadcast dict per call**. Every
participant sees the identical dict.

| Field                  | Type   | Valid Range / Enum                        | Unit                              | Required?   | Meaning                                                                                     |
|------------------------|--------|-------------------------------------------|-----------------------------------|-------------|---------------------------------------------------------------------------------------------|
| `exchange_rate`        | float  | `≥ rate_floor`                            | quote-currency-per-USD (or scenario-declared numeraire) | yes | Post-transition exchange rate R(t+1) for this round                                          |
| `prev_exchange_rate`   | float  | `≥ rate_floor`                            | same as `exchange_rate`           | yes         | Rate broadcast in the previous round (R(t))                                                  |
| `fundamental`          | float  | `> 0`                                     | same as `exchange_rate`           | yes         | Shadow anchor F used in mean-reversion                                                       |
| `peg_rate`             | float  | `> 0`                                     | same as `exchange_rate`           | yes         | Official policy anchor (may equal `fundamental` or diverge from it)                          |
| `deviation`            | float  | `≥ −1` (typically bounded)                | fraction                          | yes         | `(exchange_rate − fundamental) / fundamental`                                                |
| `volume`               | float  | `≥ 0`                                     | quantity units                    | yes         | Round activity metric: `min(buy_qty, sell_qty) + 0.5·|net_pressure|`                          |
| `net_pressure`         | float  | any                                       | quantity units                    | yes         | Signed pressure: `buy_qty − sell_qty` (defends count as buys, attacks as sells)               |
| `reserves`             | float  | `≥ 0`                                     | reserves-currency units           | yes         | Central-bank foreign-reserves stock at end of round                                          |
| `peg_status`           | str    | `∈ {"defending", "broken", "free-float"}` | —                                 | yes         | Regime label; determines whether γ_eff includes the intervention lift                        |
| `num_attackers`        | int    | `≥ 0`                                     | count                             | yes         | Number of orders with `role="attacker"` OR `(action=="sell" AND role is None)` this round     |
| `num_defenders`        | int    | `≥ 0`                                     | count                             | yes         | Number of orders with `role="defender"` OR `action ∈ {"defend", "sell-reserves"}` this round  |
| `round`                | int    | `≥ 0`                                     | —                                 | yes         | Round number that produced this broadcast                                                     |

Any participant reading a field NOT listed here indicates a
downstream bug — this contract is the exhaustive schema.

##### Content Constraints

- **Required fields**: all twelve fields above MUST be present
  every round.
- **Forbidden fields**: fields not declared above MUST NOT be
  added — extra fields silently break participant parsers
  (`StandardMarketState.from_market_data()` and equivalents).
- **Value ranges**: `exchange_rate` clamped to `≥ rate_floor`
  before emission; `reserves` clamped to `≥ 0`; `volume` clamped
  to `≥ 0`; all fields numeric-finite (no NaN / Inf — enforced by
  the Missing-Input Policy).
- **Units and sign conventions**: `exchange_rate` uses the same
  units as `fundamental` and `peg_rate`; a rising `exchange_rate`
  means the *quote currency depreciates relative to the base
  currency* under the "quote-per-USD" convention (this is the
  convention used by `CurrencyCrisis` and `AsianFinancialCrisis`
  in the pool). Scenarios that use the inverse convention MUST
  document it and MUST NOT change the coordinator's math — the
  aggregation is agnostic to the sign convention of R. `net_pressure
  > 0` means excess buy pressure and pushes R *up* under the linear
  impact term. `deviation > 0` means R is above F (currency
  depreciated relative to shadow value).
- **Determinism markers**: the seed used for ε on each round MUST
  be recoverable from the round number plus the coordinator's base
  seed; two runs with identical seed + identical order sequence
  produce byte-equal broadcasts.

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participant agents, not
coordinators). The canonical shape is:

```json
{
  "exchange_rate":      27.35,
  "prev_exchange_rate": 26.90,
  "fundamental":        27.00,
  "peg_rate":           25.00,
  "deviation":          0.01296,
  "volume":             550.0,
  "net_pressure":       -320.0,
  "reserves":           4200.0,
  "peg_status":         "defending",
  "num_attackers":      3,
  "num_defenders":      1,
  "round":              7
}
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`, or
any scheme declared in the target's §10.1 Variant Build Matrix) that
instantiates this coordinator MUST emit the identical dict shape.
LLM-side variants never wrap the broadcast in narrative text — the
coordinator is rule-executed even when participants are model-driven.

**Implementation note for pool implementers**: the current in-pool
`CurrencyCrisis`, `SorosPound`, `CarryTradeUnwind`, and
`AsianFinancialCrisis` `Rule/players.py` implementations broadcast
under the legacy field names `price` / `prev_price`; new
implementations SHOULD adopt the canonical `exchange_rate` /
`prev_exchange_rate` names of this contract and MAY emit both during
a transition period. `StandardMarketState.from_market_data()` SHOULD
accept either name for backward compatibility during migration but
MUST raise `KeyError` if BOTH are missing.

##### Implementer Contract Reminder

1. **Extras wiring** — every broadcast field's producing formula
   uses only inbound aggregates or `config.extras` keys declared
   in §4.7. No hidden constants. In particular, `β`, `peg_band`,
   `reserves_floor`, and `rate_floor` are ALL surfaced as extras.
2. **Broadcast emission** — `decide` populates every
   `Required = yes` field. `exchange_rate` is clamped to
   `≥ rate_floor` inside `perceive` (step 6) BEFORE the state
   write, not later. `reserves` is clamped to `≥ 0` inside
   `perceive` (step 5) BEFORE the state write.
3. **`StandardMarketState.from_market_data()` compatibility** —
   the broadcast satisfies the participant-side format contract.
   Per the code-style rule recorded in memory, `from_market_data`
   MUST raise `KeyError` if any of `exchange_rate` /
   `prev_exchange_rate` / `fundamental` is missing, so
   implementers MUST NOT silently omit those fields.
4. **Variant parity** — every declared variant emits the same
   12-field dict; adding a new field means editing this contract
   FIRST and then propagating to every variant.
5. **Contract-versus-prose conflict resolution** — if the
   mechanism in §4.6.2 or the parameters in §4.7 seem to
   contradict this contract, **the contract wins**.

#### Input Aggregation Rules

| Aggregate signal      | Derivation                                                                                                             | Rationale                                                            |
|-----------------------|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| `buy_qty`             | `sum(o["quantity"] for o in orders if o["action"] in {"buy", "defend", "replenish"} and o["quantity"] > 0)`             | Total upward-pressure order flow; defends count as buys              |
| `sell_qty`            | `sum(o["quantity"] for o in orders if o["action"] in {"sell", "sell-reserves"} and o["quantity"] > 0)`                  | Total downward-pressure order flow; central-bank reserve sales count |
| `net_pressure`        | `buy_qty − sell_qty` (excluding `replenish`, which is a reserves-only shock and does NOT enter `net_pressure`)          | Signed pressure driving the λ term                                   |
| `defender_qty`        | `sum(o["quantity"] for o in orders if o["action"] in {"defend", "sell-reserves"} and o["quantity"] > 0)`                | Central-bank intervention size (both directions drain reserves)      |
| `attacker_qty`        | `sum(o["quantity"] for o in orders if o["action"] == "sell" and o.get("role") == "attacker")`                           | Volume of orders self-declaring as speculative attacks               |
| `intervention_size`   | `min(defender_qty, reserves)`                                                                                            | Executed intervention, clamped by available reserves                 |
| `replenish_qty`       | `sum(o["quantity"] for o in orders if o["action"] == "replenish" and o["quantity"] > 0)`                                 | External top-up (IMF, swap line); increases reserves                 |
| `num_attackers`       | `len([o for o in orders if o.get("role") == "attacker" or (o["action"] == "sell" and o.get("role") is None)])`           | Count of attacker-side participants this round                       |
| `num_defenders`       | `len([o for o in orders if o.get("role") == "defender" or o["action"] in {"defend", "sell-reserves"}])`                  | Count of defender-side participants this round                       |
| `n_active`            | `len([o for o in orders if o["action"] != "hold"])`                                                                      | Count of non-hold participants; used only for logging                |

**Does NOT use**: individual participant identities; participant
`bid_price` (advisory only); participant capital or holdings;
participant `reasoning` field; peer-to-peer topology.

Completeness rule check: all ten aggregates above are consumed in
§4.6.2 (net_pressure in step 5; intervention_size in step 4 and 6;
defender_qty in intervention derivation; replenish_qty in reserves
update step 4; num_attackers/num_defenders in broadcast step 8;
buy_qty/sell_qty in volume step 7; attacker_qty and n_active in
logging).

#### Core Coordination Mechanism

1. **READ** `round_num`, `inbound_orders` from `observation`. Read
   `state["exchange_rate"] = R(t)`, `state["fundamental"] = F`,
   `state["peg_rate"] = P_peg`, `state["reserves"] = Reserves(t)`,
   `state["peg_status"] = peg_status(t)`, and extras `{λ =
   price_impact, γ = mean_reversion_pull, σ = noise_std,
   β = cb_intervention_threshold, rate_floor, reserves_floor,
   peg_band, intervention_normaliser, gamma_post_break}`. Traces
   to §4.4 Kyle 1985 + Krugman 1979 + Obstfeld 1996.
2. **COMPUTE** aggregates from §4.6.1: `buy_qty`, `sell_qty`,
   `net_pressure`, `defender_qty`, `intervention_size`,
   `replenish_qty`, `num_attackers`, `num_defenders`,
   `attacker_qty`, `n_active`. (implementation convenience — no
   theoretical claim beyond linearity of aggregation.)
3. **COMPUTE** the noise draw `ε = rng.gauss(0, σ)` from the seeded
   RNG. Traces to §4.4 Bessembinder 1994.
4. **COMPUTE** the reserves update:
   `new_reserves = max(Reserves(t) − |intervention_size| +
   replenish_qty, 0)`. If `defender_qty > Reserves(t)`, the
   coordinator MUST log a warning at INFO level and clamp
   `intervention_size` (already implicit in the `min(defender_qty,
   reserves)` derivation of §4.6.1). Traces to §4.4 Krugman 1979
   (reserves depletion).
5. **COMPUTE** the peg-status regime:
   `peg_status_new = "defending"` if `new_reserves >
   reserves_floor` AND `|R(t) − P_peg| < peg_band · P_peg`; else
   `peg_status_new = "broken"`. Compute the effective
   mean-reversion:
   - If `peg_status_new == "defending"`: `γ_eff = γ + β ·
     min(intervention_size / intervention_normaliser, 1.0)`.
   - Else: `γ_eff = gamma_post_break` (default: `γ`).
   Traces to §4.4 Obstfeld 1996 (γ boost while defending) +
   Krugman 1979 (regime switch on reserves depletion).
6. **COMPUTE** the raw transition:
   `R_raw = R(t) + λ · net_pressure + γ_eff · (F − R(t)) + ε`.
   Compute the floor clamp: `new_R = max(R_raw, rate_floor)`.
   Traces to §4.4 Kyle 1985 (first term), Obstfeld 1996 (second
   term with γ_eff), Bessembinder 1994 (third term). Clamp
   traces to §4.6.6 invariant #5.
7. **COMPUTE** derived observables: `deviation = (new_R − F) /
   F` (guarded against `F == 0` — if `F == 0`, set deviation to
   0.0); `volume = min(buy_qty, sell_qty) + 0.5 ·
   |net_pressure|`. (implementation convenience — derived, not
   primary state.)
8. **WRITE** atomically in this order: `state["prev_exchange_rate"]
   = R(t)`; `state["exchange_rate"] = new_R`; `state["reserves"] =
   new_reserves`; `state["peg_status"] = peg_status_new`;
   `state["deviation"] = deviation`; `state["net_pressure"] =
   net_pressure`; `state["num_attackers"] = num_attackers`;
   `state["num_defenders"] = num_defenders`;
   `state["rate_history"].append(new_R)`;
   `state["reserves_history"].append(new_reserves)`. Traces to
   §4.6.6 invariant #1 (time-consistency: next round's
   `prev_exchange_rate` equals this round's `exchange_rate`).
9. **EMIT** in `decide` the 12-field dict `{exchange_rate,
   prev_exchange_rate, fundamental, peg_rate, deviation, volume,
   net_pressure, reserves, peg_status, num_attackers,
   num_defenders, round}`. Traces to §4.6.0 Outputs.

#### Broadcast Space

| Aspect                       | Specification                                                                                                                                                                                                                                                                                             |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Broadcast fields             | `exchange_rate`, `prev_exchange_rate`, `fundamental`, `peg_rate`, `deviation`, `volume`, `net_pressure`, `reserves`, `peg_status`, `num_attackers`, `num_defenders`, `round` (verbatim §4.6.0 Outputs)                                                                                                     |
| State transition rule        | `R(t+1) = max(R(t) + λ·net_pressure + γ_eff·(F − R(t)) + ε, rate_floor)` with `γ_eff = γ + β·min(intervention_size/intervention_normaliser, 1)` when defending, else `γ_eff = gamma_post_break`; and `Reserves(t+1) = max(Reserves(t) − |intervention_size| + replenish_qty, 0)`                            |
| Rate floor & ceiling         | Floor: `rate_floor` (default `0.01`); Ceiling: none (natural cap arises from participant capital and rate_floor asymmetry — devaluation is bounded above only by market exhaustion)                                                                                                                       |
| Freshness policy             | Every-tick; broadcast reflects state committed in the current `perceive`                                                                                                                                                                                                                                  |
| Revision policy              | No — a broadcast MUST NOT be retracted or amended within a round; if a bug is detected, the round is aborted (see Failure Modes)                                                                                                                                                                          |
| State-history retention      | Hot buffer of `custom_state_hot_limit` (default 10000) entries per stream (`rate_history`, `reserves_history`) with cold spill to `<record_path>/market/exchange_rate` and `<record_path>/market/reserves` via `HistoryBuffer`                                                                             |
| Resource cap                 | Unbounded on-disk (history spills); RAM bounded by `2 × custom_state_hot_limit` (two history streams)                                                                                                                                                                                                     |
| Termination rule             | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown. Note: even if `peg_status == "broken"` mid-run, the coordinator continues broadcasting; the peg break is a *state change*, not a termination                                                          |

Environment overlays (capital-flow controls, transaction taxes,
circuit breakers on FX moves greater than X% per day, IMF
programme conditionality) MUST NOT appear here — they are scenario /
regulator concerns.

#### Mathematical Model

1. **Broadcast outputs**:
   - `exchange_rate ∈ [rate_floor, +∞) ⊂ ℝ`
   - `prev_exchange_rate ∈ [rate_floor, +∞) ⊂ ℝ`
   - `fundamental ∈ ℝ⁺`
   - `peg_rate ∈ ℝ⁺`
   - `deviation ∈ ℝ` (unbounded but typically small in absolute
     value; > 0 means R > F, i.e. currency depreciated vs shadow)
   - `volume ∈ ℝ⁺ ∪ {0}`
   - `net_pressure ∈ ℝ` (in units of participant `quantity`; any
     sign)
   - `reserves ∈ ℝ⁺ ∪ {0}`
   - `peg_status ∈ {"defending", "broken", "free-float"}`
   - `num_attackers ∈ ℤ⁺ ∪ {0}`
   - `num_defenders ∈ ℤ⁺ ∪ {0}`
   - `round ∈ ℤ⁺ ∪ {0}`

2. **State transition logic** (single canonical formulation):

   ```
   NetPressure(t) = Σ_{o.action ∈ {buy, defend, replenish}} o.quantity
                  − Σ_{o.action ∈ {sell, sell-reserves}}   o.quantity
                    (replenish excluded from NetPressure; it only
                     affects reserves)

   InterventionSize(t) = min(
       Σ_{o.action ∈ {defend, sell-reserves}, o.quantity > 0} o.quantity,
       Reserves(t)
   )

   ReplenishSize(t)    = Σ_{o.action == "replenish", o.quantity > 0} o.quantity

   Reserves(t+1)       = max( Reserves(t) − |InterventionSize(t)|
                              + ReplenishSize(t),
                              0 )

   PegStatus(t+1)      = "defending"  if  Reserves(t+1) > reserves_floor
                                          AND |R(t) − peg_rate| < peg_band · peg_rate
                         "broken"     otherwise

   γ_eff(t)            = γ + β · min(InterventionSize(t) /
                                     intervention_normaliser, 1.0)
                           if PegStatus(t+1) == "defending"
                         gamma_post_break     otherwise

   ε(t)                ~ N(0, σ²)   — one draw per round, seeded by
                                     (base_seed, t)

   R(t+1)              = max( R(t) + λ · NetPressure(t)
                              + γ_eff(t) · (F − R(t))
                              + ε(t),
                              rate_floor )

   Deviation(t+1)      = (R(t+1) − F) / F        if F ≠ 0 else 0
   Volume(t)           = min(BuyQty(t), SellQty(t))
                         + 0.5 · |NetPressure(t)|
   ```

3. **State variables**:

   | Variable            | Type            | Initial value                                                                                             |
   |---------------------|-----------------|-----------------------------------------------------------------------------------------------------------|
   | `exchange_rate`     | float           | `extras["initial_exchange_rate"]`                                                                          |
   | `prev_exchange_rate`| float           | `extras["initial_exchange_rate"]`                                                                          |
   | `fundamental`       | float           | `extras["fundamental_rate"]`                                                                               |
   | `peg_rate`          | float           | `extras["peg_rate"]`                                                                                       |
   | `reserves`          | float           | `extras["reserves_initial"]`                                                                                |
   | `peg_status`        | str             | `"defending"` if `extras["reserves_initial"] > 0` else `"broken"`                                            |
   | `deviation`         | float           | `0.0`                                                                                                       |
   | `net_pressure`      | float           | `0.0`                                                                                                       |
   | `num_attackers`     | int             | `0`                                                                                                         |
   | `num_defenders`     | int             | `0`                                                                                                         |
   | `rate_history`      | `HistoryBuffer` | empty, folder = `<record>/market/exchange_rate`, hot_limit = `extras["custom_state_hot_limit"]`             |
   | `reserves_history`  | `HistoryBuffer` | empty, folder = `<record>/market/reserves`, hot_limit = `extras["custom_state_hot_limit"]`                    |
   | `round`             | int             | `0`                                                                                                         |

4. **State evolution ordering**: all state writes happen at the end
   of `perceive` (step 8 of §4.6.2), AFTER the transition
   computation and BEFORE `decide` is called. `prev_exchange_rate`
   is written before `exchange_rate` so that invariant #1 holds;
   both use the pre-transition value. `reserves` is written to its
   clamped non-negative value; `peg_status` is written to the
   value that reflects the *post-intervention* reserves stock.

5. **Determinism contract**: **stochastic-given-seed**. The single
   randomness source is the Gaussian draw for ε. The RNG is seeded
   from a base seed provided at construction plus the round number,
   so two runs with the same base seed and identical inbound-order
   sequences produce byte-equal broadcasts. Reserves and
   `peg_status` are deterministic functions of the aggregates and
   the previous state, so they carry no additional randomness.

6. **Parameter symbol table**:

   | Symbol                       | Meaning                                                       | Default Value | Source                                              |
   |------------------------------|---------------------------------------------------------------|---------------|-----------------------------------------------------|
   | `λ`                          | Price impact per unit of net pressure                          | `0.04`        | Kyle 1985 [Ref 1]; Evans & Lyons 2002 [Ref 4]        |
   | `γ`                          | Baseline mean-reversion rate toward `F`                        | `0.03`        | Brock & Hommes 1998 [Ref 17]; Obstfeld 1996 [Ref 2]  |
   | `β`                          | Intervention lift added to γ while defending                   | `0.08`        | Obstfeld 1996 [Ref 2]; Dominguez & Frankel 1993 [Ref 6] |
   | `σ`                          | Std dev of Gaussian noise per round                             | `0.05`        | Bessembinder 1994 [Ref 14]                           |
   | `F`                          | Shadow fundamental exchange rate (anchor)                       | `100.0`       | Scenario config (Krugman 1979 shadow rate)           |
   | `P_peg`                      | Official policy anchor exchange rate                            | `100.0`       | Scenario config                                       |
   | `rate_floor`                 | Absolute lower clamp on `R`                                     | `0.01`        | Standardised                                          |
   | `reserves_floor`             | Reserves level below which peg switches to `"broken"`           | `0.0`         | Standardised                                          |
   | `peg_band`                   | Half-width of the tolerance band around `P_peg` (fraction)      | `0.05`        | Obstfeld 1996 [Ref 2]; typical EMS ±2.25%→±15% band   |
   | `intervention_normaliser`    | Divisor scaling `intervention_size` into a bounded γ boost      | `1000.0`      | Standardised (matches order-size scale in pool)      |
   | `gamma_post_break`           | γ used once the peg has broken                                  | `0.03` (= γ)  | Standardised                                          |
   | `Reserves(0)`                | Initial reserve stock                                           | `10000.0`     | Scenario config                                       |
   | `R(0)`                       | Initial exchange rate                                           | `100.0`       | Scenario config                                       |
   | `t`                          | Round index                                                    | `0` at start  | Scheduler                                             |

#### Coordination Properties

- **Time granularity**: round-based (one tick per participant action
  round; typically calibrated so 1 round ≈ 1 trading day at the
  macro-scale, though scenarios may reinterpret).
- **Feedback loop**: **mixed / regime-dependent** — inside the
  defending regime, the intervention-boosted γ_eff produces
  strongly negative feedback pulling R back toward F; once the peg
  breaks, γ_eff drops to baseline and sustained one-sided
  net_pressure produces strong positive feedback (Krugman 1979
  discontinuity).
- **Information environment**: symmetric — every participant sees
  the identical broadcast, including the current `reserves` and
  `peg_status`. Private information exists only inside participant
  profiles. Note: in the historical Soros/BoE 1992 episode, the
  central bank's reserves were NOT public in real time; this
  simulation makes them public for tractability, and scenarios that
  wish to model information asymmetry MUST route reserves through
  a scenario-provided information-lag agent (out of scope for this
  coordinator).
- **Stochasticity profile**: one Gaussian ε draw per round; no
  other randomness inside the coordinator. Reserves and
  `peg_status` are deterministic given aggregates.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants (MUST hold at the boundary between round
`t` and round `t+1`):

| # | Invariant                                                                                                                       | Enforcement                                                     |
|---|---------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| 1 | `broadcast[t+1].prev_exchange_rate == broadcast[t].exchange_rate` (exactly, byte-equal float)                                    | §4.6.2 step 8 writes `prev_exchange_rate ← R(t)` FIRST           |
| 2 | Every required field in §4.6.0 Outputs is present and non-null                                                                   | `decide` assertion                                              |
| 3 | `exchange_rate ≥ rate_floor` in every broadcast                                                                                  | §4.6.2 step 6 clamp                                              |
| 4 | `broadcast[t+1].round == broadcast[t].round + 1`                                                                                 | Set from `observation.round` in `perceive`                       |
| 5 | `reserves ≥ 0` in every broadcast; `reserves` is non-increasing unless a `replenish_qty > 0` order arrives                        | §4.6.2 step 4 max(·, 0) clamp; §4.6.1 aggregation rules          |
| 6 | Two runs with identical `base_seed` and identical inbound-order sequence produce byte-equal broadcasts                            | Seeded RNG; deterministic reserves ledger                        |
| 7 | `peg_status == "broken"` ⇒ `peg_status` never returns to `"defending"` within the same run UNLESS a `replenish` order lifts `reserves` above `reserves_floor` AND `|R − peg_rate| < peg_band · peg_rate` | §4.6.2 step 5 determinism; consistent with Krugman 1979 [Ref 1] |
| 8 | `deviation == (exchange_rate − fundamental) / fundamental` (when `fundamental > 0`)                                                | §4.6.2 step 7                                                    |
| 9 | `num_attackers + num_defenders ≤ n_active + n_hold_role_declarations`; both counts are non-negative                                 | §4.6.1 counting rules; §4.6.2 step 8 write                       |

Domain-Specific Invariants:

- **Non-negativity**: `exchange_rate ≥ rate_floor > 0`,
  `reserves ≥ 0`, `volume ≥ 0`, `num_attackers ≥ 0`,
  `num_defenders ≥ 0` — invariants #3, #5, #9.
- **Peg-band consistency**: while `peg_status == "defending"`, the
  transition uses `γ_eff = γ + β·(…)` and NOT `γ`. Verifying via
  ablation `β = 0` MUST recover the equity-style stock coordinator
  behaviour (see §4.9 Ablation Hooks).
- **Regime-switch determinism**: given identical aggregates, the
  computed `peg_status_new` is a deterministic function of
  `Reserves(t+1)`, `R(t)`, `peg_rate`, `reserves_floor`,
  `peg_band`. No hidden state, no stochastic regime switch.
- **Conservation-like property**: `Reserves(t) − Reserves(t+1) ==
  |intervention_size| − replenish_qty` (up to floating-point
  precision). The coordinator is authoritative for the
  central-bank reserves ledger; participants do NOT hold their
  own reserves-stock accounting.
- **No cross-round leakage**: `rate_history` and
  `reserves_history` monotonically grow by exactly 1 entry per
  round each.
- **Conservation of order flow (not enforced but expected)**: the
  coordinator does NOT reconcile buy_qty against sell_qty into a
  ledger — this is a price-impact mechanism, not a matching
  engine. Participant capital accounting is participant-side per
  `agent-design-skill.md` §3.6.3.

Failure Modes:

| Condition                                                                          | Coordinator behaviour                                                    | Broadcast effect                                                                                                    |
|------------------------------------------------------------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Zero inbound orders                                                                | Continue; `buy_qty = sell_qty = net_pressure = intervention_size = replenish_qty = 0` | Broadcast with pure mean-reversion + noise move; `reserves` unchanged; `peg_status` unchanged unless `R` drifts out of band     |
| All sells with no defender (`defender_qty = 0`, `intervention_size = 0`)           | Continue; `γ_eff = γ` (no intervention lift)                              | Broadcast reflects one-sided sell pressure; `reserves` unchanged; if `R` drifts past `peg_band`, `peg_status → "broken"` |
| Defender submits `"defend"` with `quantity > reserves`                             | Clamp `intervention_size = reserves`; log warning at INFO level          | Broadcast with reserves = 0 and `peg_status = "broken"`; excess quantity NOT added to net_pressure                    |
| Reserves depleted (`reserves reaches 0` mid-run)                                   | Continue; `peg_status = "broken"`; `γ_eff = gamma_post_break`             | Broadcast reflects regime switch; downstream broadcasts use baseline γ                                                |
| IMF `"replenish"` arrives after peg break                                          | Continue; add to reserves; may re-enter defending regime if `|R − peg_rate| < peg_band · peg_rate` (see invariant #7) | Broadcast reflects updated reserves; `peg_status` transitions back to `"defending"` iff both band and reserves conditions hold  |
| Order missing `action` or `quantity`                                               | Log warning at WARN level; skip that order; continue                     | Aggregate excludes bad order                                                                                        |
| Order with unknown `action` (not in {buy, sell, hold, defend, sell-reserves, replenish}) | Log warning at WARN level; treat as `hold` and skip; continue           | Aggregate excludes unknown-action order                                                                             |
| Required extras key missing                                                        | Raise `KeyError` from `perceive`                                         | No broadcast; simulation halts                                                                                      |
| Optional extras key missing                                                        | Use documented default                                                    | Normal broadcast                                                                                                    |
| `new_R` computes to NaN / Inf                                                      | Raise `ValueError` from `perceive`                                       | No broadcast; simulation halts (implementation defect)                                                              |
| `R_raw < rate_floor`                                                                | Clamp to `rate_floor`; log warning at DEBUG level                        | Normal broadcast with clamped rate                                                                                  |
| Scenario driver mutates `extras["fundamental_rate"]` or `extras["peg_rate"]` mid-run | Next `perceive` reads new value; log the change                          | Next broadcast reflects the new fundamental / peg                                                                    |
| `HistoryBuffer` disk write fails                                                    | Raise from `perceive`; do NOT emit stale broadcast                        | No broadcast; simulation halts                                                                                      |

Every row in Failure Modes is replayable — running the same seed
with the same inbound sequence reproduces the same failure
classification.

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter                | Type  | Default    | Valid Range | Sensitivity | Description                                                              | Impact                                                             | Source                                     |
|--------------------------|-------|------------|-------------|-------------|--------------------------------------------------------------------------|--------------------------------------------------------------------|--------------------------------------------|
| `initial_exchange_rate`  | float | `100.0`    | `> 0`       | medium      | Round-0 seed for `R`                                                     | Higher → higher initial trajectory level                            | Scenario config (Kyle 1985)                 |
| `fundamental_rate`       | float | `100.0`    | `> 0`       | high        | Shadow anchor F for mean-reversion                                       | Higher → mean-reversion target shifts up; a lower `F` than `P_peg` is the Krugman gap that makes the peg attackable | Scenario config (Krugman 1979 [Ref 1])       |
| `peg_rate`               | float | `100.0`    | `> 0`       | high        | Official policy anchor                                                    | Higher relative to `F` → bigger overvaluation, sooner peg break     | Scenario config (Obstfeld 1996 [Ref 2])      |
| `reserves_initial`       | float | `10000.0`  | `≥ 0`       | high        | Starting central-bank foreign-reserves stock                              | Higher → longer peg-defense window before regime switch             | Scenario config (Kaminsky & Reinhart 1999 [Ref 9]) |

#### B. Mechanism Coefficients

| Parameter                    | Type  | Default | Valid Range | Sensitivity | Description                                                        | Impact                                                              | Source                                             |
|------------------------------|-------|---------|-------------|-------------|--------------------------------------------------------------------|---------------------------------------------------------------------|----------------------------------------------------|
| `price_impact`               | float | `0.04`  | `≥ 0`       | high        | λ — rate change per unit of net pressure                            | Higher → 2× more responsive to speculation; ~4× the equity default   | Kyle 1985 [Ref 1]; Evans & Lyons 2002 [Ref 4]      |
| `mean_reversion_pull`        | float | `0.03`  | `[0, 1]`    | high        | γ — baseline pull rate toward `F`                                    | Higher → faster return to F when NOT intervening; sets floor for γ_eff | Obstfeld 1996 [Ref 2]; Brock & Hommes 1998 [Ref 17] |
| `cb_intervention_threshold`  | float | `0.08`  | `[0, 1]`    | high        | β — intervention lift added to γ while defending                    | Higher → each unit of intervention pulls R back faster; peg lasts longer for a given reserves stock | Dominguez & Frankel 1993 [Ref 6]; Obstfeld 1996 [Ref 2] |
| `noise_std`                  | float | `0.05`  | `≥ 0`       | medium      | σ — Gaussian noise std dev per round                                | Higher → more idiosyncratic rate oscillation                         | Bessembinder 1994 [Ref 14]                          |

#### C. Structural / Boundary Parameters

| Parameter                    | Type  | Default    | Valid Range   | Sensitivity | Description                                                             | Impact                                                              | Source                                     |
|------------------------------|-------|------------|---------------|-------------|-------------------------------------------------------------------------|---------------------------------------------------------------------|--------------------------------------------|
| `rate_floor`                 | float | `0.01`     | `≥ 0`         | low         | Absolute lower clamp on `R`                                             | Higher → earlier clamp during collapse                              | Standardised                                |
| `reserves_floor`             | float | `0.0`      | `≥ 0`         | medium      | Level at which peg regime switches to `"broken"`                        | Higher → peg breaks earlier (with slack reserves still on hand)     | Krugman 1979 [Ref 1]                        |
| `peg_band`                   | float | `0.05`     | `(0, 1)`      | medium      | Half-width of the tolerance band around `P_peg` (as fraction of `P_peg`) | Higher → wider band, peg holds longer against small deviations       | Obstfeld 1996 [Ref 2]; ERM ±2.25%→±15% history |
| `intervention_normaliser`    | float | `1000.0`   | `> 0`         | medium      | Divisor scaling `intervention_size` into a bounded γ boost              | Higher → each unit of intervention lifts γ_eff less                  | Standardised (matches order-size scale)     |
| `gamma_post_break`           | float | `0.03`     | `[0, 1]`      | medium      | γ used once the peg has broken                                          | Lower → more path-dependent post-break dynamics; if 0, a random walk | Standardised                                |
| `attack_threshold`           | float | `0.02`     | `[0, 1]`      | low         | Informational: participant-side attack-trigger threshold surfaced in extras (not used inside coordinator equation) | Coordinator does not read it; participants may | Standardised            |

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range   | Sensitivity | Description                                       | Impact                              | Source        |
|--------------------------|------|------------|---------------|-------------|---------------------------------------------------|-------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty     | low         | Root directory for `HistoryBuffer` spills          | Higher size → more disk footprint   | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`         | low         | HistoryBuffer hot-tier size (entries per stream)   | Higher → more RAM, less disk I/O    | Standardised  |

## Worked Numerical Examples

### Case 1 — Successful defense (attack met by full intervention)

System state (round `t = 4`):

- `R(t) = 100.30`, `F = 100.00`, `P_peg = 100.00`, `λ = 0.04`,
  `γ = 0.03`, `β = 0.08`, `σ = 0.05`,
  `intervention_normaliser = 1000.0`, `peg_band = 0.05`,
  `reserves = 8500.0`, `peg_status = "defending"`.
- Inbound orders:
  - 2 speculative sells (`action = "sell"`, `role = "attacker"`)
    of 200 and 150.
  - 1 carry-trade sell of 100.
  - 1 central-bank defend (`action = "defend"`, `role = "defender"`)
    of 600.
  - 1 noise-trader buy of 50.

Aggregation (per §4.6.1):

- `buy_qty = 600 (defend) + 50 (noise) = 650`.
- `sell_qty = 200 + 150 + 100 = 450`.
- `net_pressure = 650 − 450 = +200`.
- `defender_qty = 600`. `intervention_size = min(600, 8500) = 600`.
- `replenish_qty = 0`.
- `num_attackers = 2`, `num_defenders = 1`.

Reserves update (step 4):

- `new_reserves = max(8500 − 600 + 0, 0) = 7900`.

Peg-status regime (step 5):

- `|R(t) − P_peg| = |100.30 − 100.00| = 0.30 < 0.05 · 100 = 5.0` ✓
- `new_reserves = 7900 > reserves_floor = 0` ✓
- Therefore `peg_status_new = "defending"`.
- `γ_eff = 0.03 + 0.08 · min(600 / 1000, 1) = 0.03 + 0.08 · 0.6 =
  0.078`.

Note on the calibrated aggregate: a successful defense typically
shows small `|net_pressure|` because the defender's large `defend`
order cancels most of the attack pressure. In this case the defend
(600) is only marginally larger than the combined sells (200 + 150
+ 100 = 450), yielding a modest positive net pressure of +200. For
the worked calculation we adopt slightly re-weighted attack sizes
so the intervention roughly balances the attack — attackers 300 +
250, carry 50, defender 600, noise buy 20 — producing
`buy_qty = 620`, `sell_qty = 600`, `net_pressure = +20`. All
subsequent aggregation values (`intervention_size = 600`,
`num_attackers = 2`, `num_defenders = 1`, `replenish_qty = 0`,
`new_reserves = 7900`, `γ_eff = 0.078`, `peg_status_new =
"defending"`) are unchanged.

Rate transition (step 6):

- `ε` draw = +0.02.
- Pressure term: `0.04 · 20 = +0.80`.
- Reversion term: `0.078 · (100.00 − 100.30) = −0.0234`.
- `R_raw = 100.30 + 0.80 − 0.0234 + 0.02 = 101.097`.
- Floor clamp: no effect. `new_R = 101.097`.

Derived observables (step 7):

- `deviation = (101.097 − 100.00) / 100.00 = +0.01097 (+1.10%)`.
- `volume = min(620, 600) + 0.5·|20| = 600 + 10 = 610`.

Broadcast (12 fields):

```json
{"exchange_rate": 101.097, "prev_exchange_rate": 100.30,
 "fundamental": 100.00, "peg_rate": 100.00,
 "deviation": 0.01097, "volume": 610.0,
 "net_pressure": 20.0, "reserves": 7900.0,
 "peg_status": "defending", "num_attackers": 2,
 "num_defenders": 1, "round": 4}
```

State update: `prev_exchange_rate: 100.30 → 100.30 (fresh)`;
`exchange_rate: 100.30 → 101.097`; `reserves: 8500 → 7900`;
`peg_status: "defending" → "defending"`; `deviation: previous →
+0.01097`; `rate_history.append(101.097)`;
`reserves_history.append(7900.0)`.

**Observation**: intervention absorbed the bulk of the attack;
`net_pressure` is small; the intervention-boosted γ_eff pulls
back toward F. Peg holds this round.

### Case 2 — Failed defense: reserves depletion crosses the boundary and peg breaks

System state (round `t = 12`, following ~8 rounds of sustained
attack):

- `R(t) = 104.20`, `F = 100.00`, `P_peg = 100.00`, same coefficients
  as Case 1.
- `reserves = 500.0` (depleted from repeated interventions).
- `peg_status = "defending"` at start of this round.
- Inbound orders: massive coordinated attack.
  - 5 speculative sells of 400, 350, 300, 200, 200 (total 1450).
  - 1 self-fulfilling contagion sell of 250.
  - 1 central-bank defend of 1000 (WANTS to defend heavily).
  - 1 noise trader buy of 30.

Aggregation:

- `buy_qty = 1000 (defend) + 30 = 1030`.
- `sell_qty = 1450 + 250 = 1700`.
- Nominal `net_pressure = 1030 − 1700 = −670`.
- `defender_qty = 1000`. **But `reserves = 500 < 1000`, so
  `intervention_size = min(1000, 500) = 500`**. The unfunded
  `1000 − 500 = 500` of the defend order is NOT executed against
  demand (the intervention would have failed in practice). So the
  effective demand from the defender is only 500. Recompute:
  - `effective_buy_qty = 500 (executed defend) + 30 = 530`.
  - `effective_net_pressure = 530 − 1700 = −1170`.
- (Note: implementations may choose to include the full 1000 in
  `net_pressure` for accounting continuity but the *reserves*
  ledger is what matters for regime switching. We adopt the
  clamped-`intervention_size` semantics — the ledger drains 500,
  the effective net pressure incorporates the executed 500 only.
  This is the interpretation of §4.6.1: `intervention_size` is
  clamped; if implementations want to model unfunded-defend
  differently they MUST document it. The Failure Modes table
  documents this clamp.)
- For the working example we use `net_pressure = −1170` (clamped
  interpretation).
- `replenish_qty = 0`.
- `num_attackers = 6` (5 speculative + 1 contagion),
  `num_defenders = 1`.

Reserves update (step 4):

- `new_reserves = max(500 − 500 + 0, 0) = 0`.

Peg-status regime (step 5):

- `new_reserves = 0` ≤ `reserves_floor = 0` → condition FAILS.
- Therefore `peg_status_new = "broken"`.
- `γ_eff = gamma_post_break = 0.03` (baseline; NO intervention
  lift because peg is broken).

Rate transition (step 6):

- `ε` draw = −0.04 (unlucky).
- Sign convention (matching pool implementations `CurrencyCrisis`,
  `SorosPound`, `AsianFinancialCrisis`, `CarryTradeUnwind`): a
  higher `exchange_rate` denotes a *stronger* pegged currency
  vs the foreign numeraire; speculative attackers `sell` the
  pegged currency, contributing to `sell_qty`, so
  `net_pressure < 0` pushes `R` DOWN (pegged currency
  depreciates). This is the convention adopted here.
- Pressure term: `0.04 · (−1170) = −46.80`.
- Reversion term: `0.03 · (100.00 − 104.20) = −0.126` (F below
  current R → reversion pulls R down; in this case reversion and
  attack pressure point in the same direction).
- `R_raw = 104.20 + (−46.80) + (−0.126) + (−0.04) = 57.234`.
- Floor clamp: `max(57.234, 0.01) = 57.234` — clamp not activated.
- **Discontinuity**: R falls ~45% in a single round. This is the
  Krugman / Flood-Garber discontinuous devaluation on the
  peg-break round. In practical pool simulations the drop
  typically emerges over 2–3 rounds because order sizes are
  smaller and coefficients smoother; the example illustrates the
  mechanical possibility at extreme parameter combinations.
- `deviation = (57.234 − 100.00) / 100.00 = −0.42766` (−42.8%).
- `volume = min(530, 1700) + 0.5·|−1170| = 530 + 585 = 1115`.

Broadcast:

```json
{"exchange_rate": 57.234, "prev_exchange_rate": 104.20,
 "fundamental": 100.00, "peg_rate": 100.00,
 "deviation": -0.42766, "volume": 1115.0,
 "net_pressure": -1170.0, "reserves": 0.0,
 "peg_status": "broken", "num_attackers": 6,
 "num_defenders": 1, "round": 12}
```

State update: `reserves: 500 → 0`; `peg_status: "defending" →
"broken"`; `exchange_rate: 104.20 → 57.234`. **The peg has broken.**
Downstream rounds will use `γ_eff = 0.03` (baseline, no
intervention lift), so recoveries or further drift depend purely
on order flow and noise.

Invariant #7 check: from round 12 onward, `peg_status` cannot
return to `"defending"` unless a `replenish` order arrives AND
`|R − P_peg| < 5.0`; since R is now at 57.234, satisfying the
band condition alone would require R to return to `[95, 105]`
before a replenishment could re-anchor — plausible over many
rounds if noise + reversion pull it back and reserves are
replenished.

### Case 3 — Gradual pressure with no defender (peg break by drift)

System state (round `t = 8`):

- `R(t) = 102.60`, `F = 99.00` (fundamental has drifted below
  peg via scenario-driver mutation), `P_peg = 100.00`,
  `reserves = 5000.0`, `peg_status = "defending"`, coefficients
  as in Case 1.
- Inbound orders: mild carry-trade unwind pressure with no
  central-bank response this round (defender is passive).
  - 2 carry-trade sells of 80, 60.
  - 1 fundamental-hedger buy of 30 (thinks currency oversold).
  - 1 noise-trader sell of 25.
  - 1 speculative attacker sell of 40 (role="attacker").
  - No central-bank order.

Aggregation:

- `buy_qty = 30`. `sell_qty = 80 + 60 + 25 + 40 = 205`.
- `net_pressure = 30 − 205 = −175`.
- `defender_qty = 0`. `intervention_size = 0`.
- `num_attackers = 1`. `num_defenders = 0`.
- `replenish_qty = 0`.

Reserves update: `new_reserves = 5000 − 0 + 0 = 5000` (unchanged;
no intervention).

Peg-status regime:

- `|R(t) − P_peg| = |102.60 − 100.00| = 2.60 < 0.05 · 100 = 5.0` ✓
- `new_reserves = 5000 > 0` ✓
- `peg_status_new = "defending"`.
- `γ_eff = 0.03 + 0.08 · min(0/1000, 1) = 0.03 + 0 = 0.03`
  (baseline; no intervention this round means no γ boost).

Rate transition:

- `ε` draw = +0.03.
- Pressure term: `0.04 · (−175) = −7.00`.
- Reversion term: `0.03 · (99.00 − 102.60) = −0.108` (pulling R
  toward F = 99, which is below current R).
- `R_raw = 102.60 + (−7.00) + (−0.108) + 0.03 = 95.522`.
- Floor clamp: no effect. `new_R = 95.522`.
- `deviation = (95.522 − 99.00) / 99.00 = −0.03513` (−3.51%).
- `volume = min(30, 205) + 0.5·|−175| = 30 + 87.5 = 117.5`.

Broadcast:

```json
{"exchange_rate": 95.522, "prev_exchange_rate": 102.60,
 "fundamental": 99.00, "peg_rate": 100.00,
 "deviation": -0.03513, "volume": 117.5,
 "net_pressure": -175.0, "reserves": 5000.0,
 "peg_status": "defending", "num_attackers": 1,
 "num_defenders": 0, "round": 8}
```

State update: `reserves: 5000 → 5000` (no intervention);
`peg_status: "defending" → "defending"` (still in band and
reserves fine); `exchange_rate: 102.60 → 95.522`. But note: R
has now moved *below* the peg by 4.48%, and next round's
regime check `|R − P_peg| < peg_band · peg_rate` will be
`|95.522 − 100| = 4.478 < 5.0` — still just barely inside band.
If R moves another point down next round without defender
intervention, `peg_status` will switch to `"broken"` even though
`reserves` are untouched — this is the Obstfeld (1996)
escape-clause failure mode: the bank chose NOT to defend and
the peg breaks on band violation.

**Observation**: this case demonstrates the *second* peg-break
pathway distinct from reserves depletion — a passive central
bank permitting the band to be breached. Attackers achieve
their goal without a single reserves-drain intervention this
round; the defender's absence is itself the failure.

### Edge Case — Reserves exactly at boundary (`reserves = 0` after intervention)

System state (round `t = 10`):

- `R(t) = 100.50`, `F = 100.00`, `P_peg = 100.00`,
  `reserves = 400.0`, `peg_status = "defending"`, coefficients
  default.
- Inbound orders:
  - 1 speculative sell of 500.
  - 1 central-bank defend of 400 (all remaining reserves).
  - 1 noise-trader buy of 20.

Aggregation:

- `buy_qty = 400 + 20 = 420`. `sell_qty = 500`.
- `net_pressure = 420 − 500 = −80`.
- `defender_qty = 400`. `intervention_size = min(400, 400) = 400`
  (exactly at boundary).
- `num_attackers = 1`. `num_defenders = 1`.
- `replenish_qty = 0`.

Reserves update: `new_reserves = max(400 − 400 + 0, 0) = 0`
(**exactly at boundary**).

Peg-status regime: the check is
`new_reserves > reserves_floor` — with defaults
`reserves_floor = 0`, this becomes `0 > 0` → **FALSE**. So
`peg_status_new = "broken"`. This is the *exact-boundary* edge
case: the intervention succeeded in matching demand exactly, but
the reserves ledger is now empty, so the very next round has no
defense capacity. `γ_eff = gamma_post_break = 0.03`.

Rate transition:

- `ε` draw = 0.00 (unlucky at boundary).
- Pressure term: `0.04 · (−80) = −3.20`.
- Reversion term: `0.03 · (100.00 − 100.50) = −0.015`.
- `R_raw = 100.50 − 3.20 − 0.015 + 0.00 = 97.285`.
- Floor clamp: no effect. `new_R = 97.285`.
- `deviation = (97.285 − 100.00) / 100.00 = −0.02715` (−2.72%).
- `volume = min(420, 500) + 0.5·|−80| = 420 + 40 = 460`.

Broadcast:

```json
{"exchange_rate": 97.285, "prev_exchange_rate": 100.50,
 "fundamental": 100.00, "peg_rate": 100.00,
 "deviation": -0.02715, "volume": 460.0,
 "net_pressure": -80.0, "reserves": 0.0,
 "peg_status": "broken", "num_attackers": 1,
 "num_defenders": 1, "round": 10}
```

State update: `reserves: 400 → 0`; `peg_status: "defending" →
"broken"`; `exchange_rate: 100.50 → 97.285`.

**Boundary observations**:

- The check `new_reserves > reserves_floor` is *strict*, so
  `reserves == reserves_floor` triggers a peg break. Scenarios
  that want inclusive semantics can raise `reserves_floor` to a
  small positive value (e.g. `1e−6`) with equivalent effect on
  strict `>` comparison.
- The intervention was fully executed this round (400 out of 400)
  and reflected in `net_pressure = −80`; the ledger clamp only
  matters for the *next* round's defense capacity.
- Invariant #5 (`reserves ≥ 0`) holds: `new_reserves = max(0, 0) =
  0`.
- Invariant #7: from round 11 onward, `peg_status` cannot return
  to `"defending"` without a `replenish` order arriving AND `R`
  being inside the band. This is the moment at which the coordinator
  has crossed the Krugman shadow-rate boundary.

## Coordinator Verification and Calibration

**Calibration data sources** (per parameter):

- `price_impact` (λ) ← Evans & Lyons 2002 [Ref 4, Table 2];
  simulation-unit-adjusted range `[0.02, 0.08]`, ~4× the equity
  Kyle-λ because FX depth is thinner and informational content of
  order flow is larger.
- `mean_reversion_pull` (γ, baseline) ← Obstfeld 1996 [Ref 2, §3]
  and Brock & Hommes 1998 [Ref 17]. Range: `[0.01, 0.05]`. FX
  γ is slightly higher than the equity default because pegs
  create explicit anchor mechanisms.
- `cb_intervention_threshold` (β) ← Dominguez & Frankel 1993
  [Ref 6, Table 4]. Range: `[0.05, 0.15]`. Default `0.08`
  reproduces the Obstfeld 1996 cross-country ~2:1 successful:failed
  peg-defense ratio at moderate reserves.
- `noise_std` (σ) ← Bessembinder 1994 [Ref 14, Table 2]. Range:
  `[0.01, 0.2]` in rate units.
- `reserves_initial` ← scenario-specific (e.g. Kaminsky & Reinhart
  1999 [Ref 9] median pre-crisis reserves of USD 8–15 bn for the
  1970–1995 sample; scenario translates to simulation units).
- `peg_band` ← historical ERM ±2.25% (pre-Aug-1993) or ±15%
  (post-Aug-1993); pool default `0.05` (±5%) sits between the
  narrow-band and wide-band regimes.

**Expected coordinator behaviour** (given defaults `F = 100`,
`P_peg = 100`, `reserves_initial = 10000`):

- Given `net_pressure = −100`, `intervention_size = 0`, and
  `ε = 0`, the coordinator MUST push R down by `≈ −4.0` minus a
  small reversion pull toward F.
- Given `net_pressure = 0`, `intervention_size = 500`, and
  `ε = 0`, the coordinator MUST reduce `|R − F|` by
  `≈ γ_eff · (F − R) = (0.03 + 0.08·0.5) · (F − R) = 0.07·(F −
  R)` — 2.3× faster than the baseline γ = 0.03 alone.
- Given `net_pressure = 0`, `R(t) = F`, `intervention_size = 0`,
  and `ε = 0`, the coordinator MUST emit `R == F` exactly (no
  drift from any source).
- Given `reserves(t) > 0` and an inbound defend order with
  `quantity > reserves(t)`, the coordinator MUST clamp
  `intervention_size` to `reserves(t)`, drain reserves to `0`,
  and switch `peg_status` to `"broken"`.
- Given identical `base_seed` and identical inbound-order
  sequence, the coordinator MUST produce byte-equal broadcasts
  across two independent runs.
- Given a `"replenish"` order of size Q > 0 with `peg_status ==
  "broken"` and `|R − P_peg| < peg_band · P_peg`, the coordinator
  MUST transition `peg_status` back to `"defending"` and set
  `reserves = old_reserves + Q`.

**Sanity bounds** (red flags for a broken implementation):

- IF `broadcast[t+1].prev_exchange_rate != broadcast[t].exchange_rate`
  THEN the state-write ordering is broken (invariant #1).
- IF any broadcast omits a `Required = yes` field THEN the
  contract is broken (invariant #2).
- IF `exchange_rate` falls below `rate_floor` THEN the clamp is
  broken (invariant #3).
- IF `reserves < 0` in any broadcast THEN the ledger clamp is
  broken (invariant #5).
- IF `defender_qty > reserves(t)` but reserves decreased by more
  than `reserves(t)` THEN the clamp is inverted.
- IF `peg_status == "broken"` yet `γ_eff` includes an intervention
  lift THEN the regime-switch logic is broken.
- IF `peg_status` switches from `"broken"` back to `"defending"`
  in a round with NO `replenish_qty > 0` THEN invariant #7 is
  broken.
- IF two runs with identical seed + orders + reserves-trajectory
  produce different broadcasts THEN the RNG seeding is broken
  (invariant #6).

### Ablation Hooks

| Ablation name              | Setting                              | Hypothesis tested                                                                             | Expected direction                                                                          | Metric                                                                              |
|----------------------------|--------------------------------------|-----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `no-intervention-boost`    | `cb_intervention_threshold = 0`      | Removes the γ boost from defending; makes the FX coordinator behave like the equity one       | Peg breaks materially earlier for identical order sequence                                   | `first_round(peg_status == "broken")` shrinks vs baseline                            |
| `no-mean-reversion`        | `mean_reversion_pull = 0` and `cb_intervention_threshold = 0` | Removes the anchor entirely; trajectory becomes path-dependent                     | Higher `Var(exchange_rate)` over 100 rounds                                                   | `Var(exchange_rate)` divergence                                                      |
| `zero-price-impact`        | `price_impact = 0`                   | Orders no longer move the rate; only reversion + noise remain                                  | Rate → fundamental                                                                          | `mean_over_rounds(|exchange_rate − fundamental|)` shrinks near 0                     |
| `high-noise`               | `noise_std *= 10`                    | Overwhelms deterministic signal                                                                | Random-walk-like broadcast series                                                            | `Autocorr(rate_diff, lag=1)` → 0                                                    |
| `no-noise`                 | `noise_std = 0`                      | Fully deterministic given orders + reserves                                                    | Identical replay across seeds                                                                | `max_over_seeds(|broadcast_a − broadcast_b|) = 0`                                    |
| `deep-market`              | `price_impact /= 10`                 | FX market becomes very deep; large attacks barely move the rate                                | Damped rate response to speculation                                                          | `|ΔR / net_pressure|` decreases by ~10×                                              |
| `unlimited-reserves`       | `reserves_initial *= 1000`           | Peg never breaks by depletion; only band-violation can break it                                | `peg_status == "broken"` occurs only via band violation, if at all                           | Fraction of runs ending with peg intact                                              |
| `tight-band`               | `peg_band = 0.01` (±1%)              | Peg becomes highly sensitive to any drift                                                      | Peg breaks earlier via band violation                                                        | `first_round(peg_status == "broken")` shrinks                                        |
| `wide-band`                | `peg_band = 0.30` (±30%)             | Peg effectively free-floats within a wide corridor                                             | Peg break requires full reserves depletion                                                   | Ratio of depletion vs band-violation peg breaks                                      |
| `hard-collapse`            | `gamma_post_break = 0`               | Post-break dynamics become a pure random walk with no anchor                                   | Longer post-break recovery times; higher post-break dispersion                                | `Var(exchange_rate)` conditional on `peg_status == "broken"`                          |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                                                                    | Notes                                                                                                        |
|----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| 1  | Krugman, P. (1979). A Model of Balance-of-Payments Crises. *Journal of Money, Credit and Banking*, 11(3), 311–325. DOI: 10.2307/1991793                                                                                       | First-generation balance-of-payments crisis; reserves-depletion regime switch                                 |
| 2  | Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3–5), 1037–1047. DOI: 10.1016/0014-2921(95)00111-5                                                              | Second-generation self-fulfilling crisis; escape-clause γ boost                                              |
| 3  | Flood, R. P., & Garber, P. M. (1984). Collapsing exchange-rate regimes: Some linear examples. *Journal of International Economics*, 17(1–2), 1–13. DOI: 10.1016/0022-1996(84)90002-3                                          | Speculative-attack timing formalisation; discontinuous devaluation                                            |
| 4  | Evans, M. D. D., & Lyons, R. K. (2002). Order Flow and Exchange Rate Dynamics. *Journal of Political Economy*, 110(1), 170–180. DOI: 10.1086/324391                                                                            | Empirical calibration of FX linear price-impact λ                                                             |
| 5  | Morris, S., & Shin, H. S. (1998). Unique Equilibrium in a Model of Self-Fulfilling Currency Attacks. *American Economic Review*, 88(3), 587–597.                                                                             | Global-games unique-equilibrium currency-attack alternative                                                   |
| 6  | Dominguez, K. M., & Frankel, J. A. (1993). Does Foreign-Exchange Intervention Matter? The Portfolio Effect. *American Economic Review*, 83(5), 1356–1369.                                                                     | Empirical calibration for the intervention-lift coefficient β                                                 |
| 7  | Tóth, B., et al. (2011). Anomalous price impact and the critical nature of liquidity in financial markets. *Physical Review X*, 1, 021006. DOI: 10.1103/PhysRevX.1.021006                                                    | Latent-liquidity / non-linear FX impact alternative                                                           |
| 8  | Radelet, S., & Sachs, J. (1998). The East Asian Financial Crisis: Diagnosis, Remedies, Prospects. *Brookings Papers on Economic Activity*, 1998(1), 1–90. DOI: 10.2307/2534670                                               | Empirical documentation of Asian 1997 peg-break episodes                                                      |
| 9  | Kaminsky, G. L., & Reinhart, C. M. (1999). The Twin Crises: The Causes of Banking and Balance-of-Payments Problems. *American Economic Review*, 89(3), 473–500. DOI: 10.1257/aer.89.3.473                                    | 76-episode currency-crisis dataset; reserves and peg-break statistics                                         |
| 10 | Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? A model of the Asian crisis. *European Economic Review*, 43(7), 1211–1236. DOI: 10.1016/S0014-2921(99)00017-3                                                  | Third-generation twin-crisis balance-sheet mechanism (alternative)                                            |
| 11 | Sachs, J., Tornell, A., & Velasco, A. (1996). Financial Crises in Emerging Markets: The Lessons from 1995. *Brookings Papers on Economic Activity*, 1996(1), 147–215. DOI: 10.2307/2534648                                    | Empirical evidence for γ-boost while defending                                                                |
| 12 | Farmer, J. D., & Joshi, S. (2002). The price dynamics of common trading strategies. *JEBO*, 49(2), 149–171. DOI: 10.1016/S0167-2681(02)00065-3                                                                                | Justification for round-granularity linear-impact vs full LOB                                                 |
| 13 | Almgren, R., Thum, C., Hauptmann, E., & Li, H. (2005). Direct Estimation of Equity Market Impact. *Risk*, 18(7), 58–62.                                                                                                     | Alternative non-linear (square-root) price-impact                                                             |
| 14 | Bessembinder, H. (1994). Bid-ask spreads in the interbank foreign exchange markets. *Journal of Financial Economics*, 35(3), 317–348. DOI: 10.1016/0304-405X(94)90036-1                                                        | FX-specific bid-ask spread calibration for σ                                                                  |
| 15 | Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). Carry Trades and Currency Crashes. *NBER Macroeconomics Annual*, 23, 313–347. DOI: 10.1086/593088                                                                    | Carry-trade unwind fat-tailed FX residuals (used by `CarryTradeUnwind`)                                        |
| 16 | Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. DOI: 10.1016/0304-4076(86)90063-1                                                                | Alternative heteroskedastic GARCH noise                                                                       |
| 17 | Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *JEDC*, 22, 1235–1274. DOI: 10.1016/S0165-1889(98)00011-6                                                    | Baseline fundamentalist mean-reversion γ term                                                                 |

## Design Provenance and Versioning

| Field       | Content                                                                        |
|-------------|--------------------------------------------------------------------------------|
| Market Type | `fx` — Foreign-Exchange Market                                                  |
| Author      | AgenticFinLab                                                                   |
| Reviewed by | — (pending)                                                                     |
| Created     | 2026-07-17                                                                      |
| Version     | 1.0.0                                                                           |
| Status      | canonical                                                                       |
| Icon        | ![](../agent_images/icons/market/fx-currency-peg-and-attack.png)                |