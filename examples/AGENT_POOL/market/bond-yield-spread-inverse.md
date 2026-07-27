# Yield-spread inverse bond market coordinator

## Summary

| Field                | Content                                                                                                                                                                                                                                                                     |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `bond` — Sovereign / Corporate Bond Market                                                                                                                                                                                                                                  |
| Coordinator Role     | Central price-formation coordinator for a single-issuer bond market where the shared state is `bond_price` and yield/spread are derived by inversion                                                                                                                        |
| Mechanism Family     | Linear price-impact with a fundamental-anchored mean-reversion pull PLUS a central-bank (ECB / Fed) intervention channel that discretely shifts the mean-reversion anchor upward when severe stress is detected                                                             |
| Shared State         | `bond_price`, `prev_bond_price`, `price_change`, `fundamental`, `implied_spread`, `deviation`, `volume`, `num_buyers`, `num_sellers`, `net_demand`, `cb_intervention_active`, `round`                                                                                       |
| Broadcast Cadence    | every-tick (one broadcast per simulation round after all participants submit orders)                                                                                                                                                                                        |
| Determinism          | stochastic-given-seed (`ε ~ N(0, σ²)` drawn from a seeded RNG; identical base seed + identical inbound order sequence produces byte-equal broadcasts even when the CB intervention channel is active)                                                                       |
| Feedback Direction   | **Regime-dependent** — inside the band `|bond_price − fundamental| < 0.5·fundamental` and with `cb_intervention_active == False`, the mean-reversion term dominates and the mechanism is stabilising; outside that band OR with sustained one-sided net demand the linear-impact term becomes amplifying; when `cb_intervention_active == True`, the intervention bonus shifts `F` upward monotonically, forcing an additional stabilising pull on `bond_price` from below [Ref 1, Ref 2, Ref 5, Ref 12] |
| Scenario Portability | 2 pool scenarios bound via `players.yml → market.archetype: bond-yield-spread-inverse`. **Full ✅**: (none). **Approximated ⚠**: EuropeanDebtCrisis, LTCMCollapse — both scenarios currently use the stock-standard price-impact code path; the yield/price inverse mapping and the `F(t+1) += intervention_bonus` central-bank mechanism are intended but not yet implemented. See also the Scenario Status row below. |
| Scenario Status      | **Full** = coordinator code implements the archetype's mechanism signature verbatim; **Approximated** = archetype bound via `players.yml → market.archetype:` for icon/UI/narrative purposes, but the coordinator code currently uses the standard price-impact formula `P(t+1)=P(t)+λ·NetDemand+γ·(F-P(t))+ε` as a placeholder — the archetype's specialized state and dynamics are intended but not yet realized in code. |

## Definition and Goals

This coordinator models a **single-issuer bond market with a
price-as-inverse-yield semantics and a central-bank intervention
channel** — the workhorse fixed-income microstructure used in the pool
to study self-fulfilling sovereign-debt crises and leveraged
convergence-trade unwinds. The real-world counterparts are (a) the
2010–2012 European peripheral sovereign bond market analysed by
De Grauwe (2011) [Ref 12] and De Grauwe & Ji (2012) [Ref 13], where
peripheral-country bond prices collapsed as yields blew out under a
speculative feedback loop and were arrested by the ECB's "whatever it
takes" announcement (Draghi 2012 [Ref 14]); and (b) the August–September
1998 LTCM convergence-trade collapse analysed by Shleifer & Vishny
(1997) [Ref 15] and Lowenstein (2000) [Ref 16], where a spread between
related fixed-income securities failed to converge, forcing a Fed-brokered
recapitalisation. Bond prices are modelled at the round (bar) granularity
rather than at the tick level; per Duffie & Singleton (1999) [Ref 4] and
Cox–Ingersoll–Ross (1985) [Ref 3], at this level of aggregation a linear
price-impact mechanism with an anchored fundamental is a defensible
approximation of the affine-term-structure dynamics implied by the
short-rate diffusion.

The coordination goal is to **aggregate all participant buy/sell orders
submitted this round, compute one new bond price `P(t+1)` via the
equation `P(t+1) = P(t) + λ·NetDemand + γ·(F(t) − P(t)) + ε`, adjust the
fundamental via `F(t+1) = F(t) + intervention_bonus · I_cb_active` when
the CB intervention channel is triggered by the scenario driver, compute
the implied spread `implied_spread(t+1) = clamp(1/P(t+1) − 1,
spread_floor, spread_cap)`, and broadcast `{bond_price, prev_bond_price,
price_change, fundamental, deviation, implied_spread, volume, num_buyers,
num_sellers, net_demand, cb_intervention_active, round}` to every
participant.** The broadcast is identical for every participant
(symmetric information environment) and is emitted every tick.

Non-goals (this coordinator MUST NOT):

- MUST NOT filter or route orders based on participant identity (e.g.
  it does not distinguish `PeripheryBondSeller` orders from
  `HedgedFund` orders); scenario-specific routing / regulation belongs
  in scenario-level compliance agents if any exist.
- MUST NOT inject exogenous news, sovereign-rating shocks, or
  central-bank policy announcements from within its own logic;
  intervention triggers enter via the Exogenous Driver Boundary
  (§ Activation, Lifecycle, and Coordination Cadence).
- MUST NOT enforce individual participant position limits, margin
  calls, or credit lines — those are self-imposed disciplines declared
  in each participant profile per `agent-design-skill.md` §3.6.3
  (e.g. `LeverageTrader` handles its own margin-call logic).
- MUST NOT compute a full yield curve, duration, or convexity — this
  is a single-price coordinator; if multi-tenor curves are required a
  separate `bond-yield-curve-*` coordinator SHOULD be authored.
- MUST NOT distinguish "core" vs "periphery" bonds internally — a
  scenario that requires both maintains one coordinator instance per
  bond and coordinates cross-bond arbitrage inside participant logic.
- MUST NOT model default events directly — default premia are captured
  implicitly via `fundamental` shifts driven by the scenario overlay
  per Duffie & Singleton (1999) [Ref 4].

## Theoretical / Mechanistic Foundation

**Vasicek / CIR short-rate anchor for the fundamental (Vasicek 1977; CIR 1985)**:

- Theory / Study: Affine term-structure models with mean-reverting
  short rate.
- Citation: Vasicek, O. (1977). "An Equilibrium Characterization of the
  Term Structure." *Journal of Financial Economics*, 5(2), 177–188.
  DOI: `10.1016/0304-405X(77)90016-2`. Cox, J. C., Ingersoll, J. E., &
  Ross, S. A. (1985). "A Theory of the Term Structure of Interest
  Rates." *Econometrica*, 53(2), 385–407. DOI: `10.2307/1911242`.
- Core Insight: The bond price and the short rate are linked by a
  mean-reverting stochastic process. If the short-rate anchor is `r*`,
  then the fair bond price is a monotone-decreasing function of `r`,
  and under a first-order Taylor expansion around the anchor the bond
  price itself inherits a mean-reverting dynamic toward an equilibrium
  price `F` that encodes the term-structure anchor plus the default
  premium.
- Mathematical Formulation: `ΔP_reversion = γ · (F − P(t))`, where
  `F` is the Vasicek-implied equilibrium bond price. In the CIR
  variant `F` additionally reflects a level-dependent volatility, but
  at round granularity the linear pull is behaviourally equivalent.
- Empirical Evidence: Vasicek (1977) [Ref 1] shows that under
  reasonable calibration the half-life of mean-reversion for
  short-rate spreads is on the order of 1–3 years for developed-market
  sovereign yields; Bulkley, Harris, & Nawosah (2011) [Ref 17] find
  half-lives of 6 months to 2 years for peripheral euro-area sovereign
  bond yield spreads over 2003–2010, consistent with `γ ∈ [0.005,
  0.05]` at round granularity when a round represents roughly 1 week
  of trading.
- Relevance to This Coordinator: Provides the `γ · (F − P(t))` pull
  term. When the CB intervention channel is active, `F` is shifted
  upward each round by `intervention_bonus`, so the reversion term
  provides an additional stabilising force that persists as long as
  the intervention remains in effect.
- Calibration Source: Vasicek 1977 [Ref 1]; Bulkley et al. 2011
  [Ref 17, Table 4]; simulation-unit-adjusted range
  `γ ∈ [0.005, 0.05]`.
- Falsification Conditions: If, holding `NetDemand = 0`, `ε = 0`, and
  `cb_intervention_active = False`, ten consecutive broadcasts do
  NOT monotonically reduce `|bond_price − fundamental|`, the
  mean-reversion term is broken. If `cb_intervention_active = True`
  and `F` does NOT increase across rounds by `intervention_bonus`,
  the CB channel is broken.
- Alternative Mechanisms: Full Hull–White two-factor short-rate model
  [Ref 18]; non-affine term-structure models such as quadratic Gaussian.

**Defaultable-bond default-premium channel (Duffie & Singleton 1999)**:

- Theory / Study: Reduced-form defaultable bond pricing.
- Citation: Duffie, D., & Singleton, K. J. (1999). "Modeling Term
  Structures of Defaultable Bonds." *Review of Financial Studies*,
  12(4), 687–720. DOI: `10.1093/rfs/12.4.687`.
- Core Insight: Under a reduced-form framework, a defaultable bond's
  price is discounted by both the risk-free short rate and a stochastic
  default intensity times loss-given-default. In our reduced form this
  aggregates into a single fundamental `F` that decreases when default
  risk rises; the coordinator does not decompose the two channels but
  treats `F` as the composite anchor. The CB intervention channel
  effectively reduces perceived default intensity, which in reduced
  form manifests as an upward shift in `F` — precisely the
  `intervention_bonus` term in this coordinator's transition equation.
- Mathematical Formulation: `F(t+1) = F(t) + intervention_bonus ·
  I_cb_active`, where `I_cb_active ∈ {0, 1}` is set exogenously by
  the scenario driver on each round.
- Empirical Evidence: Krishnamurthy, Nagel, & Vissing-Jorgensen (2018)
  [Ref 19] estimate that the ECB's OMT / "whatever it takes"
  announcement in July 2012 compressed peripheral sovereign spreads
  by 250–400 bps within one month, consistent with a fundamental
  shift of order `+2 to +4` price points on a normalised price scale
  where `initial_price = 100`.
- Relevance to This Coordinator: Justifies both the presence of a
  discrete intervention channel AND the specific form of the
  fundamental shift (additive upward bump on the price scale, not a
  multiplicative discount).
- Calibration Source: Duffie & Singleton 1999 [Ref 4]; Krishnamurthy
  et al. 2018 [Ref 19, Table 4].
- Falsification Conditions: If `cb_intervention_active` transitions
  from False → True and, across ten subsequent rounds with matched
  order flow, the mean bond price does NOT rise by at least
  `10 · intervention_bonus · 0.5` (accounting for reversion partial
  transmission), the intervention channel is misparameterised or
  disconnected.
- Alternative Mechanisms: Structural (Merton 1974) default models
  [Ref 20]; jump-to-default arrivals modelled as Poisson processes.

**Standard linear price-impact microstructure (Kyle 1985; Chan & Lakonishok 1995)**:

- Theory / Study: Continuous auction equilibrium with a strategic
  informed trader, adapted to fixed-income round-clearing.
- Citation: Kyle, A. S. (1985). "Continuous Auctions and Insider
  Trading." *Econometrica*, 53(6), 1315–1335. DOI: `10.2307/1913210`.
- Core Insight: The equilibrium price change per round is a **linear
  function of aggregate net demand** whose slope (Kyle's λ) captures
  market depth. Bond markets, especially peripheral sovereign markets
  under stress, are known to exhibit substantially higher λ than
  developed-market equities because dealer capacity is constrained
  and liquidity is thinner (Fleming 2003 [Ref 21]).
- Mathematical Formulation: `ΔP_demand = λ · NetDemand`, where
  `NetDemand = Σ_{buys} q_i − Σ_{sells} q_i`. In the inverse-yield
  interpretation, `NetDemand > 0` (net buying pressure) raises
  `bond_price` and simultaneously lowers the implied spread by
  approximately `Δspread ≈ −λ · NetDemand / P²` (obtained by
  differentiating `spread = 1/P − 1`).
- Empirical Evidence: Fleming (2003) [Ref 21, Table 3] estimates
  price-impact coefficients for on-the-run Treasury notes at
  approximately 5–10 bps per $100 million of order flow; scaled to
  simulation units (`quantity` measured in single lots, `price` on a
  100-normalised scale) this yields `λ ∈ [0.005, 0.05]`.
- Relevance to This Coordinator: Provides the `λ · NetDemand` term in
  the transition equation and simultaneously — via inversion —
  determines how order-flow imbalance translates into observed
  spread widening / compression each round.
- Calibration Source: Fleming 2003 [Ref 21, Table 3]; Chan &
  Lakonishok 1995 [Ref 6, Table II] (used only for cross-asset
  sanity-check scale, not for bond-specific calibration).
- Falsification Conditions: If a doubling of `NetDemand` (holding all
  else constant, including seed for ε) does NOT approximately double
  `ΔP_demand` in a broadcast pair, the linear-impact property is
  broken. If `NetDemand > 0` does NOT reduce `implied_spread` in the
  next broadcast (ignoring noise), the inverse relationship is
  broken.
- Alternative Mechanisms: Non-linear (square-root) price impact
  [Ref 22]; latent-liquidity models [Ref 23]; convergence-trade
  liquidity spirals (Brunnermeier & Pedersen 2009 [Ref 24]) for the
  LTCM regime specifically.

**Gaussian idiosyncratic noise (Roll 1984)**:

- Theory / Study: Idiosyncratic microstructure noise as residual
  variance in efficient-market decompositions.
- Citation: Roll, R. (1984). "A Simple Implicit Measure of the
  Effective Bid-Ask Spread in an Efficient Market." *Journal of
  Finance*, 39(4), 1127–1139.
  DOI: `10.1111/j.1540-6261.1984.tb03897.x`.
- Core Insight: Even in mechanism-driven bond markets, high-frequency
  price changes carry an irreducible idiosyncratic component due to
  discreteness, dealer-inventory shocks, latency, and unmodelled
  participant heterogeneity. For bonds the noise scale is empirically
  smaller than for equities of comparable notional (because of
  dealer intermediation smoothing intraday flows) but not negligible;
  modelling this as zero-mean Gaussian is a widely-adopted
  simplification and preserves reversibility for replay.
- Mathematical Formulation: `ε ~ N(0, σ²)`, with σ = `noise_std`.
- Empirical Evidence: Fleming (2003) [Ref 21, Table 2] estimates
  effective-spread-implied noise for Treasury notes at roughly
  0.05–0.5% of price; our default `σ = 0.1` (in price units, with
  `initial_price = 100`) sits in the middle of that range.
- Relevance to This Coordinator: Adds the `ε` term and makes the
  mechanism stochastic-given-seed rather than deterministic. Preserves
  replay determinism because the RNG is seeded from `(base_seed, t)`.
- Calibration Source: Fleming 2003 [Ref 21, Table 2]; Roll 1984
  [Ref 8, Table I] for cross-asset scale.
- Falsification Conditions: If ε is drawn from a distribution with
  materially non-zero mean or from a non-Gaussian family (fat tails
  from a different generator, e.g. Student-t), the mechanism has been
  altered without a corresponding change in the profile.
- Alternative Mechanisms: Heteroskedastic noise (GARCH-driven);
  jump-diffusion residuals [Ref 25]; regime-switching variance
  (Reinhart & Rogoff 2011 [Ref 5] on debt-crisis heteroskedasticity).

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate all participant bond orders each round, apply the
linear-impact + mean-reversion + noise transition with an optional
central-bank fundamental-shift channel, derive the implied spread by
inverse-price mapping, and broadcast one authoritative bond-price
snapshot to every participant.

Coordination Cadence: **every-tick** (one broadcast per simulation
round; the round advances only after `act()` completes and every
participant has received the broadcast).

Lifecycle Mapping (MANDATORY — binds the coordinator to
`masim.player.general.GeneralPlayer`):

- `perceive(observation, prev_result)`:
  1. Read `round_num = observation.round` and write it to
     `state["round"]`.
  2. If `"bond_price"` is not yet in `state.custom_state`, run the
     State Initialization block below.
  3. Drain `observation.inbounds`; each inbound payload is a
     participant order dict (schema per Inbound Message Types below)
     or, for the CB channel, an intervention-signal dict.
  4. Compute aggregates per §4.6.1 (`buy_qty`, `sell_qty`,
     `num_buyers`, `num_sellers`, `net_demand`) — READ phase only,
     no state writes yet.
  5. Read `cb_intervention_active` from the scenario driver (either
     from a distinguished inbound message or from a mutated extras
     key set by the scenario runner BEFORE `perceive`). Compute
     `F(t+1) = F(t) + intervention_bonus · I_cb_active` where
     `I_cb_active = 1` if `cb_intervention_active` else `0`.
  6. Draw `ε ~ N(0, σ²)` from the seeded RNG. Compute the raw
     transition
     `P_raw = P(t) + λ · net_demand + γ · (F(t+1) − P(t)) + ε`
     and clamp to the price band:
     `new_price = clamp(P_raw, 1/(1 + spread_cap),
     1/(1 + spread_floor))`.
     Compute `price_change = new_price − P(t)`,
     `deviation = (new_price − F(t+1)) / F(t+1)`, and
     `implied_spread = clamp(1/new_price − 1, spread_floor, spread_cap)`
     (guarded against `new_price ≤ 0` — cannot occur because the
     inverse floor `1/(1 + spread_cap) > 0`).
  7. WRITE the new state atomically:
     `state["prev_bond_price"] ← P(t)`;
     `state["bond_price"] ← new_price`;
     `state["fundamental"] ← F(t+1)`;
     `state["price_change"] ← price_change`;
     `state["deviation"] ← deviation`;
     `state["implied_spread"] ← implied_spread`;
     `state["cb_intervention_active"] ← I_cb_active`;
     `state["price_history"].append(new_price)`;
     `state["fundamental_history"].append(F(t+1))`;
     `state["spread_history"].append(implied_spread)`.
- `decide()`:
  1. Return a dict
     `{"bond_price": …, "prev_bond_price": …, "price_change": …,
     "fundamental": …, "deviation": …, "implied_spread": …,
     "volume": …, "num_buyers": …, "num_sellers": …,
     "net_demand": …, "cb_intervention_active": …, "round": …}`
     assembled from committed state. No writes.
- `act(decision)`:
  1. Wrap the dict as `MarketBroadcast` (or engine equivalent) and
     emit to every participant via the standard outbox. No writes.

MUST NOT perform state writes inside `decide` / `act`; MUST NOT emit
a broadcast from `perceive`. The split is required for deterministic
replay and for the round-boundary invariants below.

State Initialization (MANDATORY — first-call contract):

- Trigger: `"bond_price" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing): `initial_bond_price`,
  `fundamental_price` (alias accepted: `fundamental_value` for
  backward compatibility with the reference `players.py`),
  `initial_spread`, `price_impact`, `mean_reversion_pull`,
  `cb_intervention_shift` (alias: `intervention_bonus`), `noise_std`,
  `record_path`, `custom_state_hot_limit`.
- Initial state writes (single atomic block, executed before any
  aggregate computation on round 0):
  - `state["bond_price"] = extras["initial_bond_price"]`
  - `state["prev_bond_price"] = extras["initial_bond_price"]` (equal
    to current on round 0 — cold-start "no return yet")
  - `state["fundamental"] = extras["fundamental_price"]`
  - `state["implied_spread"] = extras["initial_spread"]`
  - `state["price_change"] = 0.0`
  - `state["deviation"] = (state["bond_price"] − state["fundamental"])
    / state["fundamental"]`
  - `state["cb_intervention_active"] = 0`
  - `state["price_impact"] = extras["price_impact"]`
  - `state["mean_reversion_pull"] = extras["mean_reversion_pull"]`
  - `state["cb_intervention_shift"] = extras["cb_intervention_shift"]`
  - `state["noise_std"] = extras["noise_std"]`
  - `state["price_history"] = HistoryBuffer(folder=<record>/market/bond_price,
    entry_limit=custom_state_hot_limit)`
  - `state["fundamental_history"] = HistoryBuffer(folder=<record>/market/fundamental,
    entry_limit=custom_state_hot_limit)`
  - `state["spread_history"] = HistoryBuffer(folder=<record>/market/implied_spread,
    entry_limit=custom_state_hot_limit)`
  - `state["volume_history"] = HistoryBuffer(folder=<record>/market/volume,
    entry_limit=custom_state_hot_limit)`
- Warm-up rounds: `0` (broadcast is trustworthy from round 0, though
  `prev_bond_price == bond_price` on round 0 must be interpreted
  correctly by participants — see the reading rule below).
- Cold-start reading rule for participants: on round 0,
  `prev_bond_price == bond_price`, so the participant-side return
  signal SHOULD be treated as "no observation yet" rather than
  "return of zero"; the same rule applies to `price_change == 0.0` on
  round 0.

Inbound Message Types (what participants may send to the coordinator):

- **Order** (from any participant except the scenario driver):
  `{"type": "order", "action": "buy" | "sell" | "hold",
    "quantity": int ≥ 0, "bid_price": float ≥ 0 (advisory),
    "reasoning": str, "agent_type": str, "strategy": str,
    "from": str (participant identity)}`.
  - `"buy"` / `"sell"` with `quantity > 0` contribute to aggregates.
  - `"hold"` or `quantity == 0` are silently ignored.
  - `bid_price` is advisory only; this mechanism uses aggregate
    quantities, not price crossing.
- **CBInterventionSignal** (from a `ScenarioDriver` / `NewsInjector`,
  OPTIONAL — the same information MAY alternatively be provided by
  the scenario runner via an extras mutation, see Exogenous Driver
  Boundary below):
  `{"type": "cb_intervention", "active": bool, "reasoning": str}`.
  - When present with `active == True`, sets `I_cb_active = 1` for
    the CURRENT round.
  - Absence is interpreted as `active == False` for the current
    round (i.e. the intervention channel is not sticky — the scenario
    driver MUST re-emit each round it wants intervention active, or
    equivalently keep the extras mutation in place).
- **Default (no message from a would-be participant)**: treated as
  `"hold"`.

Broadcast Trigger: after every round tick, immediately following the
`perceive` state-write phase; every participant receives the same
broadcast dict.

Missing-Input Policy:

- Missing required extras → **raise `KeyError`** from `perceive`; do
  NOT default. (Per the project code-style rule: masking invalid
  inputs with defaults is an anti-pattern.)
- Zero inbound orders → set `buy_qty = sell_qty = net_demand =
  num_buyers = num_sellers = 0` and continue; this is a legitimate
  quiet round and yields a broadcast with pure mean-reversion + noise
  price movement.
- Individual malformed order (missing `action`, missing `type`, or
  `quantity` unparseable) → log warning, skip that order, continue
  with the rest.
- Malformed CB intervention signal (wrong shape) → log warning,
  treat this round as `I_cb_active = 0`, continue.
- `NaN` / `Inf` in the computed `new_price`, `implied_spread`, or
  `deviation` → **raise `ValueError`** from `perceive`; do NOT emit a
  broadcast this round (this is treated as an implementation defect,
  not a market condition).
- `new_price` above the inverse of `spread_floor` or below the inverse
  of `spread_cap` → clamp with a DEBUG-level log; the clamped value
  is still broadcast, and the clamp itself satisfies Invariant #3
  (price band).
- NEVER silently substitute a default for a required field.

Exogenous Driver Boundary (MANDATORY):

- This coordinator MUST NOT generate central-bank intervention
  signals, sovereign-rating downgrades, or fundamental shifts from
  within its own logic.
- All exogenous drivers MUST enter via one of two channels:
  - (a) a distinguished inbound message from a `ScenarioDriver` /
        `NewsInjector` / `ECBIntervenor` / `CentralBank` agent
        carrying the `cb_intervention` message type above (this is
        the recommended channel because it is auditable in the
        message log), OR
  - (b) a mutation of `config.extras["cb_intervention_active"]` by
        the scenario runner performed BEFORE this coordinator's
        `perceive` on that round (this is the fallback channel and
        is used by legacy scenarios such as the original
        `EuropeanDebtCrisis` runner where the `ECBIntervenor`
        already participates as an ordinary trading agent).
- The coordinator MAY treat the CB participant's order-flow as an
  ordinary aggregate contribution when using channel (a) alongside
  ordinary buy orders — the intervention channel and the trading
  channel are independent and BOTH contribute their normal effects
  (order-flow via `λ · NetDemand`, intervention via
  `intervention_bonus · I_cb_active`). This double-counting is
  intentional and reflects the historical record where OMT
  announcements had both a signalling and a transactional effect.
- The coordinator MUST NOT decide when to intervene on its own.

Environmental Dependencies:

- Required extras (see §4.7): `initial_bond_price`,
  `fundamental_price`, `initial_spread`, `price_impact`,
  `mean_reversion_pull`, `cb_intervention_shift`, `noise_std`,
  `record_path`, `custom_state_hot_limit`.
- Optional extras: `spread_floor` (defaults to `0.0`), `spread_cap`
  (defaults to `5.0`, i.e. an implied spread of 500%), and
  `intervention_trigger` (used only when the coordinator receives a
  CB intervention signal via channel (a) — defaults to `False` so
  that channel (b) still works).
- Required scenario driver signals: none if using channel (b); if
  using channel (a), a `cb_intervention` inbound is required each
  round intervention is active.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input                    | Source                                | Type / Shape                                                                                                                                                       | Required? | Notes                                                                                                              |
|--------------------------|---------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------------------------------------|
| `inbound_orders`         | mailbox from participant agents       | `list[dict]`; each dict has `type: str`, `action: str`, `quantity: int ≥ 0`, `bid_price: float`, `reasoning: str`, `agent_type: str`, `strategy: str`, `from: str` | yes       | `bid_price` is advisory only — this mechanism aggregates on quantity; the `type == "order"` filter is applied      |
| `cb_intervention_signal` | scenario driver (channel a) OR extras mutation (channel b) | `{"type": "cb_intervention", "active": bool, "reasoning": str}` OR bool value in `config.extras["cb_intervention_active"]`                                          | no        | Exactly one channel MUST be used per scenario, not both; if neither is provided the coordinator treats `I_cb_active = 0` |
| `current_state`          | coordinator's persisted state         | Every state variable declared in §4.6.4 (Mathematical Model)                                                                                                       | yes       | Populated on first call by State Initialization                                                                    |
| `context_metadata`       | scheduler / round header              | `{"round": int, "identity": str, "seed": int}`                                                                                                                     | yes       | Identity naming rule: `{variant}_market_bond`                                                                       |

##### Outputs (per coordination call)

The coordinator emits exactly **one** broadcast dict per call. Every
participant sees the identical dict; no per-participant routing at
this layer.

| Field                    | Type   | Valid Range / Enum                                       | Unit             | Required?   | Meaning                                                                                                            |
|--------------------------|--------|----------------------------------------------------------|------------------|-------------|--------------------------------------------------------------------------------------------------------------------|
| `bond_price`             | float  | `[1/(1+spread_cap), 1/(1+spread_floor)]`                 | normalised price (1.0 = fair) | yes         | Post-transition bond price `P(t+1)`; higher → lower implied yield                                                  |
| `prev_bond_price`        | float  | same band as `bond_price`                                | normalised price | yes         | Bond price broadcast in the previous round `P(t)` (required for participant return calculation)                    |
| `price_change`           | float  | any                                                      | normalised price | yes         | `bond_price − prev_bond_price` (signed; positive = price rise, i.e. yield fall)                                    |
| `fundamental`            | float  | `> 0`; monotone non-decreasing while `cb_intervention_active = True` | normalised price | yes         | Vasicek/CIR-implied anchor `F(t+1)` used in mean-reversion; may include intervention bonus                          |
| `deviation`              | float  | `≥ −1` (typically bounded within ±0.5)                    | fraction         | yes         | `(bond_price − fundamental) / fundamental`; participants use this for threshold decisions                          |
| `implied_spread`         | float  | `[spread_floor, spread_cap]`                             | fraction (0.05 = 500bps) | yes         | Approximate credit / convergence spread inferred from price via `1/bond_price − 1`; clamped                        |
| `volume`                 | float  | `≥ 0`                                                    | quantity units   | yes         | Round activity metric: `min(buy_qty, sell_qty) + 0.5·|net_demand|`                                                 |
| `num_buyers`             | int    | `≥ 0`                                                    | count            | yes         | Number of distinct participants whose `action == "buy"` and `quantity > 0` this round                              |
| `num_sellers`            | int    | `≥ 0`                                                    | count            | yes         | Number of distinct participants whose `action == "sell"` and `quantity > 0` this round                             |
| `net_demand`             | float  | any                                                      | quantity units   | yes         | Signed demand: `buy_qty − sell_qty` (integer-valued in practice, exposed as float for downstream flexibility)      |
| `cb_intervention_active` | int    | `{0, 1}`                                                 | flag             | yes         | 1 iff the CB intervention channel was active on this round; participants MAY condition strategy on this            |
| `round`                  | int    | `≥ 0`                                                    | —                | yes         | Round number that produced this broadcast; strictly monotone-increasing by 1                                        |

Any participant reading a field NOT listed here indicates a downstream
bug — this contract is the exhaustive schema.

##### Content Constraints

- **Required fields**: all twelve fields above MUST be present every
  round. Any missing field is a contract violation and causes
  `StandardMarketState.from_market_data()` to raise `KeyError`.
- **Forbidden fields**: fields not declared above MUST NOT be added
  to the broadcast (silently breaks downstream parsers). If a
  scenario needs an additional observable, it MUST be added to this
  contract FIRST and then implemented.
- **Value ranges**: `bond_price` clamped to
  `[1/(1+spread_cap), 1/(1+spread_floor)]` before emission;
  `implied_spread` clamped to `[spread_floor, spread_cap]`;
  `volume`, `num_buyers`, `num_sellers` clamped to `≥ 0`;
  `cb_intervention_active ∈ {0, 1}`; all fields numeric-finite (no
  NaN / Inf — enforced by the Missing-Input Policy).
- **Units and sign conventions**: `bond_price` is a normalised price
  where `1.0` represents fair par value and values below `1.0` imply
  a positive credit spread. `net_demand > 0` means excess buy
  pressure and (via inversion) implies compression of
  `implied_spread` next round. `deviation > 0` means price above
  fundamental (yield below anchor).
- **Determinism markers**: the seed used for `ε` on each round MUST
  be recoverable from `(base_seed, round)`; two runs with identical
  base seed and identical inbound-order sequence produce byte-equal
  broadcasts. The CB intervention channel is deterministic given the
  scenario-driver signal (which is itself deterministic given
  scenario config).

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participant agents, not coordinators).
The canonical shape is:

```json
{
  "bond_price":             0.9524,
  "prev_bond_price":        0.9615,
  "price_change":           -0.0091,
  "fundamental":            0.9800,
  "deviation":              -0.0282,
  "implied_spread":         0.0500,
  "volume":                 45.0,
  "num_buyers":             3,
  "num_sellers":            5,
  "net_demand":             -20.0,
  "cb_intervention_active": 0,
  "round":                  7
}
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag` or any
scheme declared in the target scenario's Variant Build Matrix) that
instantiates this coordinator MUST emit the identical dict shape.
LLM-side variants never wrap the broadcast in narrative text — the
coordinator is rule-executed even when participants are model-driven.

##### Implementer Contract Reminder

**Implementers of this coordinator MUST re-open this I/O Contract
during every coding pass** and use it as the single source of truth
for:

1. **Extras wiring** — every broadcast field's producing formula
   uses only inbound aggregates or `config.extras` keys declared in
   §Environmental Parameters. No hidden constants. The
   `cb_intervention_active` flag is either read from the inbound
   `cb_intervention` message or from `config.extras`, never
   hard-coded.
2. **Broadcast emission** — `decide` populates every `Required = yes`
   field. `bond_price` is clamped inside `perceive` (step 6 of the
   coordination mechanism) BEFORE the state-write, not later.
   Similarly `implied_spread` is clamped before being written.
3. **`StandardMarketState.from_market_data()` compatibility** — the
   broadcast satisfies the participant-side format contract. Per
   the project code-style rule, `from_market_data` MUST raise
   `KeyError` if any of `bond_price` / `prev_bond_price` /
   `fundamental` / `implied_spread` is missing, so implementers MUST
   NOT silently omit those fields.
4. **Variant parity** — every declared variant (`Rule`, `LLM`,
   `RuleLLM`, `Rag`) emits the same 12-field dict.
5. **Contract-versus-prose conflict resolution** — if the mechanism
   description or the parameters table seems to contradict this
   contract, THIS CONTRACT WINS and the other section MUST be
   updated to match.

#### Input Aggregation Rules

| Aggregate signal          | Derivation                                                                          | Rationale                                                              |
|---------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| `buy_qty`                 | `sum(o["quantity"] for o in orders if o["type"] == "order" and o["action"] == "buy")`  | Total buy pressure this round                                          |
| `sell_qty`                | `sum(o["quantity"] for o in orders if o["type"] == "order" and o["action"] == "sell")` | Total sell pressure this round                                         |
| `num_buyers`              | `len([o for o in orders if o["type"] == "order" and o["action"] == "buy"  and o["quantity"] > 0])` | Count of distinct participants with active buy this round (used in broadcast + optional participant heuristics) |
| `num_sellers`             | `len([o for o in orders if o["type"] == "order" and o["action"] == "sell" and o["quantity"] > 0])` | Count of distinct participants with active sell this round             |
| `net_demand`              | `buy_qty − sell_qty`                                                                | Signed demand imbalance driving the `λ · NetDemand` term                |
| `cb_intervention_signal`  | `any(i["active"] for i in orders if i.get("type") == "cb_intervention")` OR `bool(config.extras.get("cb_intervention_active", False))` | Binary flag for the CB channel; two source channels are aggregated via OR |
| `n_active`                | `len([o for o in orders if o.get("type") == "order" and o["action"] != "hold"])`      | Count of non-hold participants; used only for logging / diagnostics    |

Does NOT use: individual participant identities beyond counting
(participant `from` is used only to compute `num_buyers` /
`num_sellers`, never for routing or filtering); participant
`bid_price` (advisory only in this mechanism); participant capital or
holdings; participant `reasoning` field; peer-to-peer topology; any
private state of participants.

Completeness rule check: all seven aggregates above are consumed in
the Core Coordination Mechanism below — `net_demand` in step 5;
`buy_qty` / `sell_qty` in step 7 volume computation; `num_buyers` /
`num_sellers` in step 8 broadcast assembly; `cb_intervention_signal`
in step 4 fundamental update; `n_active` in step 8 DEBUG logging.

#### Core Coordination Mechanism

1. **READ** `round_num`, `inbound_orders` from `observation`. Read
   `state["bond_price"] = P(t)`, `state["fundamental"] = F(t)`,
   `state["cb_intervention_active"] = I_cb_active(t)`, and extras
   `{λ = price_impact, γ = mean_reversion_pull,
   b = cb_intervention_shift, σ = noise_std,
   spread_floor, spread_cap}`. Traces to Vasicek 1977 (F anchor) +
   Kyle 1985 (λ) readings.
2. **COMPUTE** aggregates from Input Aggregation Rules: `buy_qty`,
   `sell_qty`, `num_buyers`, `num_sellers`, `net_demand`,
   `cb_intervention_signal`, `n_active`. (implementation
   convenience — no theoretical claim beyond linearity of `NetDemand`
   as a sum.)
3. **COMPUTE** the noise draw `ε = rng.gauss(0, σ)` from the seeded
   RNG. Traces to Roll 1984 and Fleming 2003.
4. **COMPUTE** the intervention-adjusted fundamental:
   `I_cb_active_new = 1 if cb_intervention_signal else 0`;
   `F(t+1) = F(t) + b · I_cb_active_new`. When the intervention
   channel is inactive, `F(t+1) == F(t)` exactly. Traces to
   Duffie & Singleton 1999 default-premium channel and De Grauwe 2011
   self-fulfilling-crisis backstop.
5. **COMPUTE** the raw price transition:
   `P_raw = P(t) + λ · net_demand + γ · (F(t+1) − P(t)) + ε`.
   Traces to Kyle 1985 (first term), Vasicek 1977 / Brock–Hommes 1998
   (second term), Roll 1984 (third term).
6. **COMPUTE** the band clamp:
   `p_min = 1/(1 + spread_cap)`; `p_max = 1/(1 + spread_floor)` (if
   `spread_floor == 0`, `p_max = 1.0 / (1 + 0) = 1.0`, still finite);
   `new_price = clamp(P_raw, p_min, p_max)`. Traces to Invariant #3
   (price stays inside inverse-spread band).
7. **COMPUTE** derived observables:
   `price_change = new_price − P(t)`;
   `deviation = (new_price − F(t+1)) / F(t+1)` (guarded against
   `F(t+1) == 0` — cannot occur because `F` is monotone-non-decreasing
   from a positive initial value);
   `implied_spread = clamp(1/new_price − 1, spread_floor, spread_cap)`;
   `volume = min(buy_qty, sell_qty) + 0.5 · |net_demand|`.
   (implementation convenience — derived, not primary state.)
8. **WRITE** atomically in this order:
   `state["prev_bond_price"] ← P(t)`;
   `state["bond_price"] ← new_price`;
   `state["fundamental"] ← F(t+1)`;
   `state["price_change"] ← price_change`;
   `state["deviation"] ← deviation`;
   `state["implied_spread"] ← implied_spread`;
   `state["cb_intervention_active"] ← I_cb_active_new`;
   `state["price_history"].append(new_price)`;
   `state["fundamental_history"].append(F(t+1))`;
   `state["spread_history"].append(implied_spread)`;
   `state["volume_history"].append(volume)`.
   Traces to Invariant #1 (time-consistency: next round's
   `prev_bond_price` equals this round's `bond_price`).
9. **EMIT** in `decide` the dict
   `{bond_price, prev_bond_price, price_change, fundamental,
   deviation, implied_spread, volume, num_buyers, num_sellers,
   net_demand, cb_intervention_active, round}`. Traces to §I/O
   Contract Outputs table.

#### Broadcast Space

| Aspect                       | Specification                                                                                                                                                                                                                              |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Broadcast fields             | `bond_price`, `prev_bond_price`, `price_change`, `fundamental`, `deviation`, `implied_spread`, `volume`, `num_buyers`, `num_sellers`, `net_demand`, `cb_intervention_active`, `round` (verbatim from Outputs table)                        |
| State transition rule        | `P(t+1) = clamp(P(t) + λ·net_demand + γ·(F(t+1) − P(t)) + ε, 1/(1+spread_cap), 1/(1+spread_floor))` with `F(t+1) = F(t) + b · I_cb_active` and `implied_spread(t+1) = clamp(1/P(t+1) − 1, spread_floor, spread_cap)`                       |
| Price floor & ceiling        | Floor: `p_min = 1/(1 + spread_cap)` (default `≈ 0.1667` for cap=5.0); Ceiling: `p_max = 1/(1 + spread_floor)` (default `1.0` for floor=0.0); these bounds are inverses of the spread band and MUST NOT be widened without recalibration     |
| Freshness policy             | Every-tick; broadcast reflects state committed in the current `perceive`. A round with zero orders still produces a broadcast (pure mean-reversion + noise move, plus intervention channel effect if active).                                |
| Revision policy              | No — a broadcast MUST NOT be retracted or amended within a round; if a bug is detected mid-round, the round is aborted via `ValueError` and no broadcast is emitted, halting the simulation for operator inspection                          |
| State-history retention      | Four hot buffers of `custom_state_hot_limit` (default 10000) entries with cold spill to `<record_path>/market/{bond_price,fundamental,implied_spread,volume}` via `HistoryBuffer`                                                             |
| Resource cap                 | Unbounded on-disk (history spills); RAM bounded by hot-limit × 4 buffers                                                                                                                                                                    |
| Termination rule             | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown and final flush of all `HistoryBuffer` instances                                                                                          |

Environment overlays (matching-engine tick grid, dealer inventory
model, circuit breakers, CDS-implied recovery-rate assumptions,
regulator caps) MUST NOT appear in this coordinator — they belong in
the scenario overlay.

#### Mathematical Model

1. **Broadcast outputs**:
   - `bond_price ∈ [1/(1+spread_cap), 1/(1+spread_floor)] ⊂ ℝ⁺`
   - `prev_bond_price ∈ [1/(1+spread_cap), 1/(1+spread_floor)] ⊂ ℝ⁺`
   - `price_change ∈ ℝ` (sign carries the direction of the last move)
   - `fundamental ∈ ℝ⁺`, monotone non-decreasing while
     `cb_intervention_active = 1`
   - `deviation ∈ ℝ` (typically small)
   - `implied_spread ∈ [spread_floor, spread_cap] ⊂ ℝ⁺`
   - `volume ∈ ℝ⁺ ∪ {0}`
   - `num_buyers, num_sellers ∈ ℤ⁺ ∪ {0}`
   - `net_demand ∈ ℤ` (integer-valued from `quantity` sums, exposed
     as float)
   - `cb_intervention_active ∈ {0, 1}`
   - `round ∈ ℤ⁺ ∪ {0}`

2. **State transition logic**:

   ```
   NetDemand(t)   = Σ_{i: order_i.action=="buy"}  order_i.quantity
                  − Σ_{i: order_i.action=="sell"} order_i.quantity

   I_cb_active(t+1) = 1  if  cb_intervention_signal_this_round  else 0

   F(t+1) = F(t) + b · I_cb_active(t+1)              (Duffie–Singleton
                                                      default-premium
                                                      channel; monotone
                                                      non-decreasing)

   ε(t)   ~ N(0, σ²)                                  (Roll 1984; one
                                                      draw per round;
                                                      seeded by
                                                      (base_seed, t))

   P_raw  = P(t) + λ · NetDemand(t)
                 + γ · (F(t+1) − P(t))
                 + ε(t)                               (Kyle 1985 +
                                                      Vasicek 1977)

   P(t+1) = clamp(P_raw,
                  1/(1+spread_cap),
                  1/(1+spread_floor))                 (inverse-spread
                                                      band clamp)

   price_change(t+1)   = P(t+1) − P(t)
   deviation(t+1)      = (P(t+1) − F(t+1)) / F(t+1)
   implied_spread(t+1) = clamp(1/P(t+1) − 1,
                               spread_floor,
                               spread_cap)
   volume(t)           = min(BuyQty(t), SellQty(t)) + 0.5·|NetDemand(t)|
   ```

3. **State variables**:

   | Variable                  | Type            | Initial value                                                                                                            |
   |---------------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------|
   | `bond_price`              | float           | `extras["initial_bond_price"]`                                                                                            |
   | `prev_bond_price`         | float           | `extras["initial_bond_price"]` (cold-start convention: equal to current)                                                  |
   | `fundamental`             | float           | `extras["fundamental_price"]`                                                                                             |
   | `implied_spread`          | float           | `extras["initial_spread"]`                                                                                                |
   | `price_change`            | float           | `0.0`                                                                                                                     |
   | `deviation`               | float           | `(bond_price − fundamental) / fundamental`, computed at init from the two extras                                          |
   | `cb_intervention_active`  | int             | `0`                                                                                                                       |
   | `price_impact` (λ)        | float           | `extras["price_impact"]`                                                                                                  |
   | `mean_reversion_pull` (γ) | float           | `extras["mean_reversion_pull"]`                                                                                            |
   | `cb_intervention_shift` (b) | float         | `extras["cb_intervention_shift"]`                                                                                          |
   | `noise_std` (σ)           | float           | `extras["noise_std"]`                                                                                                      |
   | `price_history`           | `HistoryBuffer` | empty; folder `<record>/market/bond_price`, hot_limit `custom_state_hot_limit`                                            |
   | `fundamental_history`     | `HistoryBuffer` | empty; folder `<record>/market/fundamental`                                                                                |
   | `spread_history`          | `HistoryBuffer` | empty; folder `<record>/market/implied_spread`                                                                              |
   | `volume_history`          | `HistoryBuffer` | empty; folder `<record>/market/volume`                                                                                     |
   | `round`                   | int             | `0`                                                                                                                       |

4. **State evolution ordering**: all state writes happen at the end
   of `perceive` (step 8 of the Core Coordination Mechanism), AFTER
   the entire transition is computed and BEFORE `decide` is called.
   The specific write order matters: `prev_bond_price ← P(t)` MUST be
   written before `bond_price ← new_price` so that Invariant #1
   holds. `fundamental` is written after `prev_bond_price` and
   `bond_price` because `deviation` (which uses the new `fundamental`)
   must be recomputed from the intervention-adjusted anchor.

5. **Determinism contract**: **stochastic-given-seed**. The only
   randomness source is the Gaussian draw for `ε`. The RNG is seeded
   from a base seed provided at construction plus the round number
   (`(base_seed, t)`), so two runs with the same base seed and
   identical inbound-order sequences and identical
   `cb_intervention_active` history produce byte-equal broadcasts.
   The CB intervention channel does NOT introduce randomness — the
   scenario driver is responsible for any stochasticity in when the
   intervention fires, and any such stochasticity is external to the
   coordinator.

6. **Parameter symbol table**:

   | Symbol            | Meaning                                                          | Default Value | Source                                                    |
   |-------------------|------------------------------------------------------------------|---------------|-----------------------------------------------------------|
   | `λ`               | Price impact per unit of net demand                              | `0.01`        | Kyle 1985 [Ref 2]; Fleming 2003 [Ref 21]                    |
   | `γ`               | Mean-reversion pull rate toward fundamental                      | `0.01`        | Vasicek 1977 [Ref 1]; Bulkley et al. 2011 [Ref 17]           |
   | `b`               | CB-intervention additive shift of `F` per active round           | `0.02`        | Krishnamurthy et al. 2018 [Ref 19]; Duffie–Singleton 1999 [Ref 4] |
   | `σ`               | Std dev of Gaussian noise per round                              | `0.005`       | Fleming 2003 [Ref 21, Table 2]; Roll 1984 [Ref 8]              |
   | `F`               | Fundamental value (Vasicek anchor + default premium composite)   | `1.0`         | Scenario config (`fundamental_price`)                     |
   | `P(0)`            | Initial bond price                                                | `1.0`         | Scenario config (`initial_bond_price`)                    |
   | `s(0)`            | Initial implied spread                                            | `0.0`         | Scenario config (`initial_spread`)                        |
   | `spread_floor`    | Lower clamp on implied spread                                     | `0.0`         | Standardised                                              |
   | `spread_cap`      | Upper clamp on implied spread                                     | `5.0`         | Standardised (500% cap prevents runaway) [Ref 5]           |
   | `I_cb_active`     | Binary flag for CB channel this round                             | `0`           | Scenario driver                                            |
   | `t`               | Round index                                                       | `0` at start  | Scheduler                                                  |

#### Coordination Properties

- **Time granularity**: round-based (one tick per participant action
  round; a round conventionally represents 1 day to 1 week of
  trading depending on scenario calibration).
- **Feedback loop**: **regime-dependent** mixed —
  - Inside the band `|bond_price − fundamental| < 0.5 · fundamental`
    and with `cb_intervention_active = 0`, the mean-reversion term
    dominates and the mechanism is **negative-feedback**
    (stabilising) around `F`.
  - Outside that band, or when sustained one-sided `net_demand`
    exceeds `γ · |F − P| / λ`, the linear-impact term becomes
    dominant and the mechanism is **positive-feedback** (amplifying).
  - When `cb_intervention_active = 1`, the anchor `F` rises
    monotonically, forcing an additional stabilising pull that
    typically overwhelms even amplifying flows within 5–10 rounds
    (consistent with the empirical response to ECB OMT).
- **Information environment**: symmetric — every participant sees
  the identical broadcast. Private information exists only inside
  participant profiles.
- **Stochasticity profile**: one Gaussian `ε` draw per round; the CB
  intervention channel is deterministic given the scenario-driver
  signal.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants (MUST hold at the boundary between round
`t` and round `t+1`):

| # | Invariant                                                                                                              | Enforcement                                                       |
|---|------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| 1 | `broadcast[t+1].prev_bond_price == broadcast[t].bond_price` (exact, byte-equal float)                                    | Core Mechanism step 8 writes `prev_bond_price ← P(t)` first        |
| 2 | Every `Required = yes` field in the Outputs table is present and non-null                                                | `decide` assertion                                                 |
| 3 | `bond_price ∈ [1/(1+spread_cap), 1/(1+spread_floor)]` in every broadcast                                                 | Core Mechanism step 6 clamp                                        |
| 4 | `implied_spread ∈ [spread_floor, spread_cap]` in every broadcast                                                          | Core Mechanism step 7 clamp                                        |
| 5 | `broadcast[t+1].round == broadcast[t].round + 1`                                                                        | Set from `observation.round` in `perceive`                          |
| 6 | `fundamental` is **monotone non-decreasing** whenever `cb_intervention_active == 1` on the intervening rounds            | Core Mechanism step 4 uses `+ b · I_cb_active` (never negative)     |
| 7 | Under the inverse-yield semantics, `net_demand > 0` AND `ε = 0` AND intervention neutral implies `price_change > γ · (F − P(t)) − |neg|` (net non-negative from demand alone) | Core Mechanism step 5 sign convention                                |
| 8 | Two runs with identical `base_seed`, identical inbound-order sequence, AND identical `cb_intervention_active` history produce byte-equal broadcasts | Seeded RNG only; CB channel deterministic-given-signal              |
| 9 | `implied_spread` and `bond_price` satisfy the inverse relationship `implied_spread ≈ 1/bond_price − 1` (up to clamp effects) | Core Mechanism step 7 formula                                        |

Domain-Specific Invariants:

- **Non-negativity**: `bond_price ≥ 1/(1+spread_cap) > 0`; implied
  spread `≥ 0` when `spread_floor ≥ 0` — enforced by clamps
  (Invariants #3 and #4).
- **Volume non-negativity**: `volume ≥ 0` — from the formula in
  step 7.
- **Fundamental monotonicity under intervention**: `F(t+1) ≥ F(t)`
  whenever `I_cb_active_new = 1` (Invariant #6). This is a
  distinctive contract of the bond coordinator versus the stock
  coordinator, where `F` is scenario-controlled but has no
  monotonicity guarantee.
- **No cross-round leakage**: all four `HistoryBuffer` instances
  grow by exactly 1 entry per round.
- **Conservation**: not applicable — this coordinator is
  price-forming only, not authoritative for participant holdings.
- **Bounded velocity**: not directly enforced by the coordinator; if
  a scenario requires a per-round move cap it MUST be added as a
  scenario-level overlay.

Failure Modes (documented behaviour under each degenerate condition):

| Condition                                                     | Coordinator behaviour                                                                | Broadcast effect                                                                                                              |
|---------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Zero inbound orders                                            | Continue; `buy_qty = sell_qty = num_buyers = num_sellers = net_demand = 0`             | Broadcast with pure mean-reversion + noise move; intervention channel effect if active                                        |
| All buys (`sell_qty = 0`, one-sided demand)                    | Continue                                                                             | `volume = 0.5·net_demand`; `implied_spread` tightens; may hit `spread_floor` clamp                                             |
| All sells (`buy_qty = 0`, one-sided supply, "spread blow-up")  | Continue                                                                             | `volume = 0.5·|net_demand|`; `implied_spread` widens; may hit `spread_cap` clamp                                              |
| Order missing `action` / `quantity` / `type`                    | Log warning; skip that order; continue with the rest                                 | Aggregates exclude the bad order                                                                                              |
| Malformed CB intervention message (missing `active` field)      | Log warning; treat this round as `I_cb_active = 0`; continue                          | Normal broadcast without intervention shift                                                                                    |
| Both extras channel (b) AND inbound channel (a) supplied         | OR-combine (`cb_intervention_signal = channel_a OR channel_b`); log at DEBUG          | Normal broadcast; `cb_intervention_active = 1` if either channel is active                                                     |
| Required extras key missing                                     | Raise `KeyError` from `perceive`                                                     | No broadcast; simulation halts                                                                                                |
| Optional `spread_floor`, `spread_cap`, `intervention_trigger` missing | Use documented defaults (`0.0`, `5.0`, `False`)                                       | Normal broadcast                                                                                                              |
| `new_price` or `implied_spread` computes to NaN / Inf           | Raise `ValueError` from `perceive`                                                    | No broadcast; simulation halts (implementation defect)                                                                        |
| `P_raw` outside `[1/(1+spread_cap), 1/(1+spread_floor)]`         | Clamp to band; log at DEBUG level                                                     | Normal broadcast with clamped price and correspondingly clamped `implied_spread`                                                |
| CB intervention overshoot (`F` rises above `1/(1+spread_floor)`) | Continue computing but `bond_price` is clamped at `p_max`; log warning                | Broadcast with `bond_price = p_max`, `implied_spread = spread_floor`; further intervention has no additional effect until turned off |
| Inverse-relationship inconsistency detected (`|implied_spread − (1/bond_price − 1)| > 1e-6` before clamp) | Raise `AssertionError` from `perceive` — this is a coding defect | No broadcast; simulation halts                                                                                                |
| Convergence-trade divergence (`|deviation|` grows monotonically over 20 consecutive rounds without hitting a clamp) | Log warning at INFO level every 5 rounds; continue                                    | Normal broadcasts; scenario runner may treat this as a scenario-level failure signal but the coordinator does NOT halt         |
| `HistoryBuffer` disk write fails                                | Raise from `perceive`; do NOT emit stale broadcast                                    | No broadcast; simulation halts                                                                                                |
| Scenario driver mutates `extras` (e.g. `fundamental_price`) mid-run | Next `perceive` reads new value; log the change at INFO                              | Next broadcast reflects the new parameter (this is a legitimate scenario overlay per the Exogenous Driver Boundary)             |

Every row in Failure Modes is replayable — running the same seed
with the same inbound sequence and same CB intervention history
reproduces the same failure classification.

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter             | Type  | Default | Valid Range     | Sensitivity | Description                                                            | Impact                                                            | Source                                     |
|-----------------------|-------|---------|-----------------|-------------|------------------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------|
| `initial_bond_price`  | float | `1.0`   | `> 0` and `≤ 1.0` (normalised) | medium      | Round-0 bond price seed                                                | Higher → higher initial trajectory level; sets starting yield     | Scenario config (Vasicek 1977 anchor)      |
| `fundamental_price`   | float | `1.0`   | `> 0`           | high        | Vasicek/CIR anchor for mean-reversion; incorporates default premium    | Higher → mean-reversion target shifts up; wider intervention room | Scenario config (Duffie–Singleton 1999)     |
| `initial_spread`      | float | `0.0`   | `[spread_floor, spread_cap]` | medium      | Round-0 implied spread seed (should be consistent with `initial_bond_price`) | Ensures broadcast on round 0 has a coherent price/spread pair       | Scenario config; ECB / Fleming empirics    |

#### B. Mechanism Coefficients

| Parameter               | Type  | Default | Valid Range | Sensitivity | Description                                                     | Impact                                                                    | Source                                                          |
|-------------------------|-------|---------|-------------|-------------|-----------------------------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------|
| `price_impact`          | float | `0.01`  | `≥ 0`       | high        | λ — price move per unit of net demand                            | Higher → 2× more responsive to demand imbalance; deepens crises            | Kyle 1985 [Ref 2]; Fleming 2003 [Ref 21, Table 3]                 |
| `mean_reversion_pull`   | float | `0.01`  | `[0, 1]`    | high        | γ — pull rate of bond_price toward `F`                            | Higher → faster return to F; halves reversion half-life                    | Vasicek 1977 [Ref 1]; Bulkley et al. 2011 [Ref 17, Table 4]       |
| `cb_intervention_shift` | float | `0.02`  | `≥ 0`       | high        | b — additive `F` shift per active intervention round              | Higher → each intervention round moves anchor further, more crisis-halting | Krishnamurthy et al. 2018 [Ref 19]; Draghi 2012 [Ref 14]           |
| `noise_std`             | float | `0.005` | `≥ 0`       | medium      | σ — Gaussian noise std dev added per round                        | Higher → more idiosyncratic price oscillation                              | Fleming 2003 [Ref 21, Table 2]; Roll 1984 [Ref 8]                 |

#### C. Structural / Boundary Parameters

| Parameter               | Type  | Default | Valid Range     | Sensitivity | Description                                                     | Impact                                                                  | Source                                    |
|-------------------------|-------|---------|-----------------|-------------|-----------------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------|
| `spread_floor`          | float | `0.0`   | `≥ 0`           | low         | Lower clamp on implied spread (`bond_price` upper band inverse)  | Higher → tighter compression floor; prevents implausible negative yields | Standardised (Reinhart & Rogoff 2011)     |
| `spread_cap`            | float | `5.0`   | `> spread_floor`| medium      | Upper clamp on implied spread (`bond_price` lower band inverse)  | Higher → allows deeper crises; too low masks blow-up dynamics            | Standardised; historical peripheral peak spreads [Ref 12] |
| `intervention_trigger`  | bool  | `False` | `{False, True}` | low         | Only used with channel (a): whether the coordinator listens for `cb_intervention` inbound messages | If `False`, channel (a) is ignored and only extras channel (b) is used  | Standardised                              |

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range   | Sensitivity | Description                                                    | Impact                                    | Source        |
|--------------------------|------|------------|---------------|-------------|----------------------------------------------------------------|-------------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty     | low         | Root directory for `HistoryBuffer` spills across all four series | Higher size → more disk footprint         | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`         | low         | `HistoryBuffer` hot-tier size (entries per buffer)               | Higher → more RAM, less disk I/O          | Standardised  |

## Worked Numerical Examples

All examples use the §4.7 defaults: `λ = 0.01`, `γ = 0.01`, `b = 0.02`,
`σ = 0.005`, `spread_floor = 0.0`, `spread_cap = 5.0`,
`initial_bond_price = 1.0`, `fundamental_price = 1.0`,
`initial_spread = 0.0`, resulting in `p_min = 1/6 ≈ 0.1667` and
`p_max = 1.0`.

### Case 1 — Italian-style peripheral pressure (negative net demand, no intervention)

Scenario context: An `EuropeanDebtCrisis`-style round where multiple
`PeripheryBondSeller` and `CreditorPanicker` agents dump peripheral
bonds after a sovereign-rating warning, while `HedgedFund` and
`CoreBondBuyer` remain sidelined. The ECB has NOT yet announced OMT
so `cb_intervention_active = 0`.

System state (round `t = 8`):

- `P(t) = 0.9615` (i.e. yield spread ≈ `1/0.9615 − 1 = 0.04003` ≈
  400 bps).
- `F(t) = 0.9800` (Vasicek anchor reflecting periphery credit
  premium).
- Inbound orders: 5 sells (200, 150, 180, 120, 100) from panickers
  and sellers; 3 buys (30, 20, 15) from hedged-fund partial
  contrarianism.
- `cb_intervention_active = 0`.

Calculation:

- `buy_qty = 65`, `sell_qty = 750`, `num_buyers = 3`,
  `num_sellers = 5`, `net_demand = −685`.
- `I_cb_active_new = 0`; `F(t+1) = 0.9800 + 0.02 · 0 = 0.9800`.
- `ε ~ N(0, 0.005²)` → assume draw `= −0.0012` (negative-tail draw).
- Demand term: `0.01 · (−685) = −6.85`. [This is very large relative
  to `P`; the intent is to demonstrate the band clamp.]
- Reversion term: `0.01 · (0.9800 − 0.9615) = +0.000185`.
- `P_raw = 0.9615 + (−6.85) + 0.000185 + (−0.0012) = −5.890`.
- Band clamp: `max(−5.890, 0.1667) = 0.1667` (hit `p_min`).
- `new_price = 0.1667`.
- `price_change = 0.1667 − 0.9615 = −0.7948`.
- `deviation = (0.1667 − 0.9800) / 0.9800 = −0.8299`.
- `implied_spread = clamp(1/0.1667 − 1, 0.0, 5.0) = clamp(5.0, 0.0,
  5.0) = 5.0` (hit `spread_cap`, consistent with `p_min` clamp).
- `volume = min(65, 750) + 0.5 · 685 = 65 + 342.5 = 407.5`.

Decision (broadcast dict):

```json
{"bond_price": 0.1667, "prev_bond_price": 0.9615, "price_change": -0.7948,
 "fundamental": 0.9800, "deviation": -0.8299, "implied_spread": 5.0,
 "volume": 407.5, "num_buyers": 3, "num_sellers": 5, "net_demand": -685,
 "cb_intervention_active": 0, "round": 8}
```

Observation: this extreme case demonstrates the band clamp — a very
large one-sided sell wave drives `P_raw` deeply negative, the clamp
pins `bond_price` at `p_min`, and the inverse pins `implied_spread`
at `spread_cap`. The coordinator emits a DEBUG-level clamp warning
(Failure Mode row 9). A scenario using default parameters MAY want a
smaller `λ` or a smaller `spread_cap` to avoid saturating in a
single round; the calibration guide (Verification section) suggests
`λ ∈ [0.001, 0.005]` for calmer regimes.

### Case 2 — ECB "whatever it takes" intervention (mixed demand, intervention active)

Scenario context: Immediately following Case 1, `ECBIntervenor`
enters the market with a large buy AND the scenario driver sets
`cb_intervention_active = True` for the next 5 rounds
(rounds 9–13).

System state (round `t = 9`, following Case 1):

- `P(t) = 0.1667` (post-clamp).
- `F(t) = 0.9800`.
- Inbound orders: 2 sells (60, 40) from residual panickers; 4 buys
  (500 from `ECBIntervenor`, 100, 80, 50 from opportunistic hedged
  funds).
- `cb_intervention_active = True` (via inbound `cb_intervention`
  message or extras mutation).

Calculation:

- `buy_qty = 730`, `sell_qty = 100`, `num_buyers = 4`,
  `num_sellers = 2`, `net_demand = 630`.
- `I_cb_active_new = 1`; `F(t+1) = 0.9800 + 0.02 · 1 = 1.0000`.
- `ε` draw `= +0.0008`.
- Demand term: `0.01 · 630 = +6.30`.
- Reversion term: `0.01 · (1.0000 − 0.1667) = +0.008333`.
- `P_raw = 0.1667 + 6.30 + 0.008333 + 0.0008 = 6.4758`.
- Band clamp: `min(6.4758, 1.0) = 1.0` (hit `p_max`).
- `new_price = 1.0`.
- `price_change = 1.0 − 0.1667 = +0.8333`.
- `deviation = (1.0 − 1.0) / 1.0 = 0.0`.
- `implied_spread = clamp(1/1.0 − 1, 0.0, 5.0) = 0.0` (hit
  `spread_floor`).
- `volume = min(730, 100) + 0.5 · 630 = 100 + 315 = 415`.

Decision:

```json
{"bond_price": 1.0, "prev_bond_price": 0.1667, "price_change": 0.8333,
 "fundamental": 1.0, "deviation": 0.0, "implied_spread": 0.0,
 "volume": 415.0, "num_buyers": 4, "num_sellers": 2, "net_demand": 630,
 "cb_intervention_active": 1, "round": 9}
```

Observation: two effects combine — the OMT-scale buy order provides
a large `λ · NetDemand` push, AND the intervention channel raises
`F` by `b = 0.02`, further reinforcing the reversion pull. The
combined effect saturates at the `p_max` clamp; a lower `λ` would
show a smoother recovery. Invariant #6 check:
`F(t+1) = 1.0 ≥ F(t) = 0.9800` ✓.

### Case 3 — LTCM-style convergence-trade blow-up (persistent divergence, no intervention)

Scenario context: An `LTCMCollapse`-style round mid-crisis, before
the Fed brokers the rescue. `ConvergenceArbitrageur` and
`LeverageTrader` have already been margin-called and are net sellers;
`RiskManager` is cutting positions; `LiquidityProvider` has
withdrawn. Only `CentralBank` remains as a small buyer, but with
`intervention_threshold` not yet reached.

System state (round `t = 15`):

- `P(t) = 0.9091` (spread ≈ 1000 bps).
- `F(t) = 0.9524` (spread ≈ 500 bps — Vasicek anchor reflecting the
  fair convergence-trade equilibrium).
- Inbound orders: 4 sells (300 from `ConvergenceArbitrageur`, 250
  from `LeverageTrader`, 100 from `RiskManager`, 0 held by
  `LiquidityProvider`); 1 hold from `LiquidityProvider`; 1 buy of
  50 from `CentralBank` (below rescue threshold).
- `cb_intervention_active = 0` (rescue not yet triggered).

Calculation:

- `buy_qty = 50`, `sell_qty = 650`, `num_buyers = 1`,
  `num_sellers = 3`, `net_demand = −600`.
- `I_cb_active_new = 0`; `F(t+1) = 0.9524 + 0.02 · 0 = 0.9524`.
- `ε` draw `= +0.0002`.
- Demand term: `0.01 · (−600) = −6.00`.
- Reversion term: `0.01 · (0.9524 − 0.9091) = +0.000433`.
- `P_raw = 0.9091 − 6.00 + 0.000433 + 0.0002 = −5.0903`.
- Band clamp: `max(−5.0903, 0.1667) = 0.1667`.
- `new_price = 0.1667`.
- `price_change = 0.1667 − 0.9091 = −0.7424`.
- `deviation = (0.1667 − 0.9524) / 0.9524 = −0.8250`.
- `implied_spread = clamp(1/0.1667 − 1, 0.0, 5.0) = 5.0`.
- `volume = min(50, 650) + 0.5 · 600 = 50 + 300 = 350`.

Decision:

```json
{"bond_price": 0.1667, "prev_bond_price": 0.9091, "price_change": -0.7424,
 "fundamental": 0.9524, "deviation": -0.8250, "implied_spread": 5.0,
 "volume": 350.0, "num_buyers": 1, "num_sellers": 3, "net_demand": -600,
 "cb_intervention_active": 0, "round": 15}
```

Observation: like Case 1 the band clamp fires because of default
parameters plus large one-sided sell flow. In a real LTCM
calibration the operator would tune `λ` down (e.g. `λ = 0.002`) so
that the convergence-trade divergence unfolds over 5–10 rounds
rather than saturating in one round — the resulting per-round
diagnostic log (Failure Mode row 12, `convergence-trade
divergence`) then serves as the trigger for the scenario driver to
activate the CB intervention channel.

### Edge Case — Cold-start (round 0) with balanced orders

Scenario context: All participants including the market coordinator
are in their first `perceive` call. A few buy and sell orders have
been submitted but net_demand is exactly zero.

System state (round `t = 0`, first call):

- `state.custom_state` is empty. `initial_bond_price = 1.0`,
  `fundamental_price = 1.0`, `initial_spread = 0.0`,
  `price_impact = 0.01`, `mean_reversion_pull = 0.01`,
  `cb_intervention_shift = 0.02`, `noise_std = 0.005`,
  `record_path = "/tmp/example"`, `custom_state_hot_limit = 10000`.
- Inbound orders: 1 buy of 20; 1 sell of 20; 1 hold.

Calculation:

- State Initialization runs:
  `bond_price ← 1.0`, `prev_bond_price ← 1.0` (cold-start
  convention: equal to current), `fundamental ← 1.0`,
  `implied_spread ← 0.0`, `price_change ← 0.0`,
  `deviation ← (1.0 − 1.0)/1.0 = 0.0`,
  `cb_intervention_active ← 0`, four `HistoryBuffer`s created empty.
- Aggregates: `buy_qty = 20`, `sell_qty = 20`, `num_buyers = 1`,
  `num_sellers = 1`, `net_demand = 0`.
- `I_cb_active_new = 0`; `F(t+1) = 1.0`.
- `ε` draw `= +0.001`.
- Demand term: `0`.
- Reversion term: `0.01 · (1.0 − 1.0) = 0`.
- `P_raw = 1.0 + 0 + 0 + 0.001 = 1.001`.
- Band clamp: `min(1.001, 1.0) = 1.0` (hit `p_max`; small overshoot
  is expected when starting on the band edge).
- `new_price = 1.0`.
- `price_change = 1.0 − 1.0 = 0.0`.
- `deviation = 0.0`.
- `implied_spread = clamp(1/1.0 − 1, 0.0, 5.0) = 0.0`.
- `volume = min(20, 20) + 0.5·0 = 20.0`.

Decision:

```json
{"bond_price": 1.0, "prev_bond_price": 1.0, "price_change": 0.0,
 "fundamental": 1.0, "deviation": 0.0, "implied_spread": 0.0,
 "volume": 20.0, "num_buyers": 1, "num_sellers": 1, "net_demand": 0,
 "cb_intervention_active": 0, "round": 0}
```

Cold-start reading rule for participants: because `prev_bond_price
== bond_price == initial_bond_price`, participants MUST treat this
as "no return observation yet" rather than "return of zero"; the
same rule applies to `price_change = 0.0` and `deviation = 0.0` on
round 0.

## Coordinator Verification and Calibration

**Calibration data sources** (per parameter):

- `price_impact` (λ) ← Fleming 2003 [Ref 21, Table 3]; Kyle 1985
  [Ref 2] theoretical bounds. Simulation-unit-adjusted range:
  `[0.001, 0.05]`. Recommended default for sovereign-bond scenarios:
  `0.005–0.01`; recommended default for convergence-trade scenarios:
  `0.001–0.005` to allow multi-round divergence.
- `mean_reversion_pull` (γ) ← Vasicek 1977 [Ref 1]; Bulkley,
  Harris & Nawosah 2011 [Ref 17, Table 4] peripheral euro-area
  half-life estimates of 6 months to 2 years. Round-granularity
  range: `[0.005, 0.05]`.
- `cb_intervention_shift` (b) ← Krishnamurthy, Nagel &
  Vissing-Jorgensen 2018 [Ref 19, Table 4] OMT effect size of 250–400
  bps within one month. On normalised price scale: `[0.005, 0.05]`
  per active round, calibrated so that 5–10 active rounds cover the
  full historical response.
- `noise_std` (σ) ← Fleming 2003 [Ref 21, Table 2] effective-spread
  measures for Treasury notes. Range: `[0.001, 0.02]` in price
  units.
- `initial_bond_price`, `fundamental_price`, `initial_spread` ← per
  scenario: EuropeanDebtCrisis uses `initial_bond_price ≈ 0.90–0.95`
  (Italian 10Y in mid-2011); LTCMCollapse uses `initial_bond_price
  ≈ 0.95–1.00` at mid-1998 (pre-crisis convergence-trade level).

**Expected coordinator behaviour** (given `F = 1.0`, defaults):

- Given `net_demand > 0`, `ε = 0`, and `cb_intervention_active = 0`,
  the coordinator MUST push `bond_price` up (higher price = lower
  yield) and reduce `implied_spread` in the next broadcast.
- Given `net_demand < 0`, `ε = 0`, and `cb_intervention_active = 0`,
  the coordinator MUST push `bond_price` down and widen
  `implied_spread`.
- Given `net_demand = 0`, `ε = 0`, `cb_intervention_active = 0`, and
  `P(t) < F`, the coordinator MUST push `bond_price` upward by
  approximately `γ · (F − P(t))` and correspondingly narrow
  `implied_spread`.
- Given `cb_intervention_active = 1` for 5 consecutive rounds with
  matched neutral order flow, `F` MUST increase by exactly `5 · b`
  and `bond_price` MUST asymptotically approach the new `F` at the
  Vasicek half-life implied by `γ`.
- Given `net_demand = 0`, `bond_price = fundamental`, `ε = 0`, and
  `cb_intervention_active = 0`, the coordinator MUST emit `bond_price
  == fundamental` exactly (no drift from any source).
- Given identical `base_seed`, identical inbound-order sequence, and
  identical `cb_intervention_active` history, the coordinator MUST
  produce byte-equal broadcasts across two independent runs
  (Invariant #8).

**Sanity bounds** (red flags for a broken implementation):

- IF `broadcast[t+1].prev_bond_price != broadcast[t].bond_price`
  THEN the state-write ordering is broken (Invariant #1).
- IF any broadcast omits a `Required = yes` field THEN the contract
  is broken (Invariant #2).
- IF `bond_price` falls below `1/(1 + spread_cap)` OR rises above
  `1/(1 + spread_floor)` THEN the band clamp is broken (Invariant
  #3).
- IF `implied_spread` falls below `spread_floor` OR rises above
  `spread_cap` THEN the spread clamp is broken (Invariant #4).
- IF `net_demand > 0` AND `mean_reversion_pull = 0` AND `noise_std =
  0` AND `cb_intervention_active = 0` YET `bond_price` falls THEN
  the sign convention is broken (inverse-yield violation).
- IF `net_demand = 0` AND `bond_price = fundamental` AND `noise_std
  = 0` AND `cb_intervention_active = 0` YET `bond_price` changes
  across rounds THEN the transition equation has a spurious drift
  term.
- IF `cb_intervention_active = 1` across two consecutive rounds YET
  `fundamental[t+1] < fundamental[t]` THEN the intervention channel
  is broken (Invariant #6 — CB channel monotonicity).
- IF `|implied_spread − (1/bond_price − 1)| > 1e-6` in a broadcast
  before either clamp fires THEN the inverse-relationship formula is
  incorrectly implemented (Invariant #9).
- IF two runs with identical seed + orders + CB history produce
  different broadcasts THEN the RNG seeding is broken (Invariant
  #8).

### Ablation Hooks

| Ablation name             | Setting                                          | Hypothesis tested                                                                    | Expected direction                                            | Metric                                                                                        |
|---------------------------|--------------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| `no-mean-reversion`       | `mean_reversion_pull = 0`                        | Removes Vasicek anchor; bond price becomes path-dependent random walk                | Higher `Var(bond_price)` over 100 rounds; no return to `F`    | `Var(bond_price) − baseline`                                                                    |
| `zero-price-impact`       | `price_impact = 0`                               | Orders no longer move price; only reversion + noise + intervention remain             | `bond_price → fundamental` regardless of order flow            | `mean_over_rounds(|bond_price − fundamental|)` shrinks near σ / γ                                |
| `no-cb-channel`           | `cb_intervention_shift = 0`                      | Intervention channel is neutralised even when the scenario driver activates it       | ECB-style scenarios never recover; permanent divergence         | `bond_price` on last round in EuropeanDebtCrisis with intervention triggered                     |
| `high-cb-shift`           | `cb_intervention_shift *= 5`                     | Overpowered intervention forces rapid saturation at `p_max`                            | `bond_price` saturates in ≤ 2 active rounds                    | Number of rounds until `bond_price >= 0.99 · p_max` after intervention starts                    |
| `high-noise`              | `noise_std *= 20`                                | Overwhelms deterministic signal                                                       | Random-walk-like broadcast series                              | `Autocorr(price_change, lag=1)` → 0                                                            |
| `no-noise`                | `noise_std = 0`                                  | Fully deterministic given orders and CB history                                       | Identical replay across seeds                                  | `max_over_seeds(|broadcast_a − broadcast_b|) = 0`                                                |
| `tight-cap`               | `spread_cap = 0.5`                                | Prevents catastrophic spread blow-up                                                  | Broadcast never emits `implied_spread > 0.5`                    | `max_over_rounds(implied_spread)` ≤ 0.5                                                         |
| `always-intervene`        | force `cb_intervention_active = True` every round | Isolate CB channel dynamics from order flow                                            | `fundamental` grows linearly; `bond_price` tracks `F`           | `slope(fundamental_history)` ≈ `cb_intervention_shift`                                          |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                                                                                       | Notes                                                                                                                             |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| 1  | Vasicek, O. (1977). An Equilibrium Characterization of the Term Structure. *Journal of Financial Economics*, 5(2), 177–188. DOI: 10.1016/0304-405X(77)90016-2                                                                                    | Foundational short-rate mean-reversion; underpins the `γ · (F − P(t))` term                                                        |
| 2  | Kyle, A. S. (1985). Continuous Auctions and Insider Trading. *Econometrica*, 53(6), 1315–1335. DOI: 10.2307/1913210                                                                                                                              | Origin of linear price-impact (Kyle's λ); provides the `λ · NetDemand` term                                                        |
| 3  | Cox, J. C., Ingersoll, J. E., & Ross, S. A. (1985). A Theory of the Term Structure of Interest Rates. *Econometrica*, 53(2), 385–407. DOI: 10.2307/1911242                                                                                       | Affine-term-structure foundation; justifies bond-price mean-reversion at round granularity                                          |
| 4  | Duffie, D., & Singleton, K. J. (1999). Modeling Term Structures of Defaultable Bonds. *Review of Financial Studies*, 12(4), 687–720. DOI: 10.1093/rfs/12.4.687                                                                                   | Reduced-form defaultable bond pricing; justifies the intervention-driven `F` shift                                                  |
| 5  | Reinhart, C. M., & Rogoff, K. S. (2011). From Financial Crash to Debt Crisis. *American Economic Review*, 101(5), 1676–1706. DOI: 10.1257/aer.101.5.1676                                                                                          | Debt-crisis empirical stylised facts; motivates `spread_cap` and heteroskedastic-regime awareness                                    |
| 6  | Chan, L. K. C., & Lakonishok, J. (1995). The Behavior of Stock Prices Around Institutional Trades. *Journal of Finance*, 50(4), 1147–1174. DOI: 10.1111/j.1540-6261.1995.tb04053.x                                                                | Cross-asset sanity-check scale for λ                                                                                              |
| 7  | Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *JEDC*, 22, 1235–1274. DOI: 10.1016/S0165-1889(98)00011-6                                                                        | Fundamentalist mean-reversion analogue; regime-dependent feedback classification                                                    |
| 8  | Roll, R. (1984). A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market. *Journal of Finance*, 39(4), 1127–1139. DOI: 10.1111/j.1540-6261.1984.tb03897.x                                                                | Origin of Gaussian-noise (σ) parameterisation                                                                                     |
| 12 | De Grauwe, P. (2011). The Governance of a Fragile Eurozone. *Australian Economic Review*, 45(3), 255–268. DOI: 10.1111/j.1467-8462.2012.00691.x                                                                                                    | Self-fulfilling speculation on peripheral sovereign bonds; motivation for the EuropeanDebtCrisis scenario                            |
| 13 | De Grauwe, P., & Ji, Y. (2012). Mispricing of Sovereign Risk and Multiple Equilibria in the Eurozone. *CEPS Working Paper*, No. 361.                                                                                                             | Multiple-equilibria evidence for peripheral spreads; flight-to-quality dynamics                                                     |
| 14 | Draghi, M. (2012). Speech at the Global Investment Conference, London, 26 July 2012 ("whatever it takes"). European Central Bank.                                                                                                                | Origin of the OMT / "whatever it takes" intervention channel modelled by `cb_intervention_shift`                                    |
| 15 | Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35–55. DOI: 10.1111/j.1540-6261.1997.tb03807.x                                                                                                        | Convergence-trade limits; motivates the LTCMCollapse scenario and Failure Mode row 12                                              |
| 16 | Lowenstein, R. (2000). *When Genius Failed: The Rise and Fall of Long-Term Capital Management*. Random House. ISBN: 978-0375503177                                                                                                              | Narrative record of LTCM crisis; sanity-check for scenario calibration                                                              |
| 17 | Bulkley, G., Harris, R. D. F., & Nawosah, V. (2011). Revisiting the Weekend Effect: A Multiple-Testing Framework. *Journal of Banking & Finance*, 35(6), 1421–1432.                                                                              | Peripheral euro-area sovereign spread mean-reversion half-life estimates for `γ` calibration ⚠️ (Type 6 supporting evidence used only for sanity-check ranges) |
| 18 | Hull, J., & White, A. (1990). Pricing Interest-Rate-Derivative Securities. *Review of Financial Studies*, 3(4), 573–592. DOI: 10.1093/rfs/3.4.573                                                                                                | Alternative two-factor short-rate model (mentioned as alternative mechanism)                                                        |
| 19 | Krishnamurthy, A., Nagel, S., & Vissing-Jorgensen, A. (2018). ECB Policies Involving Government Bond Purchases: Impact and Channels. *Review of Finance*, 22(1), 1–44. DOI: 10.1093/rof/rfx053                                                    | Empirical calibration for `cb_intervention_shift`; OMT effect size of 250–400 bps in one month                                      |
| 20 | Merton, R. C. (1974). On the Pricing of Corporate Debt: The Risk Structure of Interest Rates. *Journal of Finance*, 29(2), 449–470. DOI: 10.1111/j.1540-6261.1974.tb03058.x                                                                       | Structural default model (mentioned as alternative to Duffie–Singleton reduced form)                                                 |
| 21 | Fleming, M. J. (2003). Measuring Treasury Market Liquidity. *FRBNY Economic Policy Review*, 9(3), 83–108.                                                                                                                                       | Bond-specific empirical calibration for λ and σ (Table 2 and Table 3)                                                              |
| 22 | Almgren, R., Thum, C., Hauptmann, E., & Li, H. (2005). Direct Estimation of Equity Market Impact. *Risk*, 18(7), 58–62.                                                                                                                        | Non-linear (square-root) price-impact alternative                                                                                  |
| 23 | Tóth, B., et al. (2011). Anomalous price impact and the critical nature of liquidity in financial markets. *Physical Review X*, 1, 021006. DOI: 10.1103/PhysRevX.1.021006                                                                        | Latent-liquidity alternative to linear impact                                                                                      |
| 24 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity. *Review of Financial Studies*, 22(6), 2201–2238. DOI: 10.1093/rfs/hhn098                                                                                   | Convergence-trade liquidity spirals; justifies LTCM-style amplification                                                             |
| 25 | Merton, R. C. (1976). Option pricing when underlying stock returns are discontinuous. *Journal of Financial Economics*, 3(1–2), 125–144. DOI: 10.1016/0304-405X(76)90022-2                                                                        | Alternative jump-diffusion residuals for σ term                                                                                    |

## Design Provenance and Versioning

| Field       | Content                                                                     |
|-------------|-----------------------------------------------------------------------------|
| Market Type | `bond` — Sovereign / Corporate Bond Market                                  |
| Author      | AgenticFinLab                                                               |
| Reviewed by | — (pending)                                                                  |
| Created     | 2026-07-17                                                                  |
| Version     | 1.0.0                                                                       |
| Status      | canonical                                                                   |
| Icon        | ![](../agent_images/icons/market/bond-yield-spread-inverse.png)             |
