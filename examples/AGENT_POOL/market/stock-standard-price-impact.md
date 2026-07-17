# Standard price-impact stock market

## Summary

| Field                | Content                                                                                                                                                                                                                                                                        |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `stock` — Stock / Equity Market                                                                                                                                                                                                                                                |
| Coordinator Role     | Central price-formation coordinator for a single-asset equity market                                                                                                                                                                                                           |
| Mechanism Family     | Standard linear price-impact with mean-reversion and Gaussian noise                                                                                                                                                                                                            |
| Shared State         | `price`, `prev_price`, `fundamental`, `deviation`, `volume`, `net_demand`, `round`                                                                                                                                                                                             |
| Broadcast Cadence    | every-tick (one broadcast per simulation round, after all participants submit orders)                                                                                                                                                                                          |
| Determinism          | stochastic-given-seed (ε ~ N(0, σ²) drawn from a seeded RNG; identical seed + identical inbound order sequence reproduces byte-equal broadcasts)                                                                                                                               |
| Feedback Direction   | **Regime-dependent** — inside the band `|price − fundamental| < 0.5·fundamental`, the mean-reversion term dominates and the mechanism is stabilising; outside that band, linear price-impact from one-sided net demand can dominate mean-reversion and become amplifying [Ref 1, Ref 2] |
| Scenario Portability | Used by ≥ 30 pool scenarios: AnchoringEffect, AssetBubble, AvailabilityBias, BlackMonday1987, ConfirmationBias, DispositionEffect, DotComBubble, EndowmentEffect, FramingEffect, GamblerFallacy, HerdEffect, HerdingInformation, HindsightBias, LiquidityDryup, LossAversion, MarketCrash, MentalAccounting, MomentumEffect, OverconfidenceBias, RepresentativenessBias, ReversalEffect, SouthSeaBubble, StatusQuoBias, SunkCostFallacy, TulipMania, VolatilityClustering, Volmageddon and others |

## Definition and Goals

This coordinator models a **single-asset, continuous-price equity
market with a designated price-formation mechanism** — the workhorse
market microstructure used to study behavioural finance phenomena in
a controlled setting. The real-world counterpart is a centralised
call-auction or continuous-limit-order-book equity venue
approximated at the round (bar) granularity, similar in spirit to the
setup analysed by Kyle (1985) [Ref 1] and adopted as a standard
building block in agent-based financial simulations by Brock &
Hommes (1998) [Ref 2] and Farmer & Joshi (2002) [Ref 3]. The
coordinator is deliberately mechanism-driven rather than order-book
matched, because the round granularity of the enclosing simulation
makes a full LOB matching engine both unnecessary and (per Farmer &
Joshi) numerically equivalent to a linear price-impact rule at
sufficient aggregation.

The coordination goal is to **aggregate all participant buy/sell
orders submitted this round, produce exactly one new price `P(t+1)`
via the equation `P(t+1) = P(t) + λ·NetDemand + γ·(F − P(t)) + ε`,
and broadcast `{price, prev_price, fundamental, deviation, volume,
net_demand, round}` to every participant.** The broadcast is
identical for every participant (symmetric information environment).

Non-goals (this coordinator MUST NOT):

- MUST NOT filter or route orders based on participant identity,
  capital, or history — that is the job of scenario-specific
  compliance / regulation agents if any exist.
- MUST NOT inject exogenous news, shocks, or regime flips from
  within its own logic — such drivers enter via the Exogenous Driver
  Boundary declared in §5.
- MUST NOT enforce individual participant position limits, margin
  calls, or short-sale constraints — those are self-imposed
  disciplines declared in each participant profile per
  `agent-design-skill.md` §3.6.3.
- MUST NOT modify the fundamental value `F` from its own logic;
  fundamental drift, if any, is a scenario overlay written into
  `extras` by the scenario runner before `perceive` (see §5).

## Theoretical / Mechanistic Foundation

**Linear price-impact from net demand (Kyle 1985)**:

- Theory / Study: Continuous auction equilibrium with a strategic
  informed trader
- Citation: Kyle, A. S. (1985). "Continuous Auctions and Insider
  Trading." *Econometrica*, 53(6), 1315–1335.
  DOI: `10.2307/1913210`
- Core Insight: In a batch-clearing market with a competitive
  market-maker, the equilibrium price change is a **linear function
  of aggregate order flow** whose slope (Kyle's λ) captures market
  depth. Higher λ means demand imbalance moves the price more; lower
  λ means the market absorbs demand more elastically.
- Mathematical Formulation: `ΔP_demand = λ · NetDemand`, where
  `NetDemand = Σ_buys q_i − Σ_sells q_i`.
- Empirical Evidence: Hasbrouck (1991) [Ref 4] estimates λ for
  large-cap NYSE stocks in the range `1e−7` to `1e−5` per dollar of
  aggregate order flow; our default `λ = 0.01` operates at simulation
  units (`quantity` in single units, `price` in currency units) and
  reproduces the target price-impact-per-round of ≈ 1% at
  `|NetDemand| = 1`, consistent with the elasticity range reported by
  Chan & Lakonishok (1995) [Ref 5, Table II] for institutional
  trading.
- Relevance to This Coordinator: Provides the demand-driven price
  change term `λ · NetDemand` in the transition equation.
- Calibration Source: Hasbrouck 1991 [Ref 4, Table 3] and Chan &
  Lakonishok 1995 [Ref 5, Table II]; simulation-unit-adjusted range
  `λ ∈ [0.001, 0.05]`.
- Falsification Conditions: If a doubling of `NetDemand` (holding all
  else constant, including seed for ε) does NOT approximately double
  `ΔP_demand` in a broadcast pair, the linear-impact property is
  broken.
- Alternative Mechanisms: Non-linear (square-root) price impact
  [Ref 6]; latent-liquidity models [Ref 7].

**Mean-reversion toward fundamental value (Brock & Hommes 1998)**:

- Theory / Study: Heterogeneous adaptive belief systems with
  fundamentalist / chartist mixtures
- Citation: Brock, W. A., & Hommes, C. H. (1998). "Heterogeneous
  beliefs and routes to chaos in a simple asset pricing model."
  *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274.
  DOI: `10.1016/S0165-1889(98)00011-6`
- Core Insight: In markets populated by both fundamentalist and
  trend-following traders, the price is systematically pulled back
  toward an anchor fundamental value at a rate that depends on the
  effective weight of fundamentalists, capturing the empirically
  observed slow reversion of prices to intrinsic value.
- Mathematical Formulation: `ΔP_reversion = γ · (F − P(t))`.
- Empirical Evidence: Fama & French (1988) [Ref 8] document
  half-lives of 3–5 years for stock-price mean-reversion in long-run
  U.S. data; De Bondt & Thaler (1985) [Ref 9] report a 3-year loser
  portfolio reverses ≈ 25 percentage points versus winners. On a
  round-granularity simulation with 20–100 rounds, `γ ∈ [0.005,
  0.05]` reproduces comparable relative reversion rates.
- Relevance to This Coordinator: Provides the anchoring pull term
  `γ · (F − P(t))` that is required to prevent scenarios from
  drifting indefinitely.
- Calibration Source: Brock & Hommes 1998 [Ref 2, §4] simulations
  use γ ≈ 0.01; consistent with Fama–French half-life when
  reinterpreted at round granularity.
- Falsification Conditions: If, holding `NetDemand = 0` and `ε = 0`,
  ten consecutive broadcasts do NOT monotonically reduce
  `|price − fundamental|`, the mean-reversion term is broken.
- Alternative Mechanisms: Adaptive-expectation drift [Ref 10];
  no-reversion pure random walk [Ref 11].

**Gaussian idiosyncratic noise (efficient-market residual)**:

- Theory / Study: Idiosyncratic microstructure noise as residual
  variance in efficient-market decompositions
- Citation: Roll, R. (1984). "A Simple Implicit Measure of the
  Effective Bid-Ask Spread in an Efficient Market." *Journal of
  Finance*, 39(4), 1127–1139. DOI: `10.1111/j.1540-6261.1984.tb03897.x`
- Core Insight: Even in mechanism-driven markets, high-frequency
  price changes carry an irreducible idiosyncratic component due to
  discreteness, latency, and unmodelled participant heterogeneity;
  modelling this as zero-mean Gaussian is a widely-adopted
  simplification.
- Mathematical Formulation: `ε ~ N(0, σ²)`, with σ = `noise_std`.
- Empirical Evidence: Roll (1984) [Ref 12, Table I] estimates
  effective bid-ask-spread-implied noise standard deviations of
  0.1–1% of price for NYSE stocks; our default `σ = 0.1` (in price
  units) corresponds to ≈ 0.1% at the default `initial_price = 100`.
- Relevance to This Coordinator: Adds the term `ε` and makes the
  mechanism stochastic-given-seed rather than deterministic.
- Calibration Source: Roll 1984 [Ref 12, Table I].
- Falsification Conditions: If ε is drawn from a distribution with
  materially non-zero mean or from a non-Gaussian family (fat tails
  from a different generator), the mechanism has been altered.
- Alternative Mechanisms: Heteroskedastic noise (GARCH-driven — see
  the sibling `stock-garch-volatility` profile [pool-only, not yet
  written]); jump-diffusion residuals [Ref 13].

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate all participant orders each round, apply the
linear-impact + mean-reversion + noise transition, and broadcast one
authoritative price snapshot.

Coordination Cadence: **every-tick** (one broadcast per simulation
round; the round advances only after `act()` completes).

Lifecycle Mapping (MANDATORY):

- `perceive(observation, prev_result)`:
  1. Read `round_num = observation.round` and write it to
     `state["round"]`.
  2. If `"price"` is not yet in `state.custom_state`, run the State
     Initialization block below.
  3. Drain `observation.inbounds`; each inbound payload is a
     participant order dict.
  4. Compute aggregates per §4.6.1 (`buy_qty`, `sell_qty`,
     `net_demand`) — READ phase only.
  5. Draw `ε ~ N(0, σ²)` from the seeded RNG; compute
     `new_price = clamp(P(t) + λ·NetDemand + γ·(F − P(t)) + ε,
     price_floor, +∞)`; compute `deviation` and `volume`. WRITE the
     new state atomically: `prev_price ← P(t); price ← new_price;
     deviation ← …; price_history.append(new_price)`.
- `decide()`:
  1. Return a dict `{"price": …, "prev_price": …, "fundamental": …,
     "deviation": …, "volume": …, "net_demand": …, "round": …}`
     assembled from committed state. No writes.
- `act(decision)`:
  1. Wrap the dict as `MarketBroadcast` (or engine equivalent) and
     emit to every participant via the standard outbox. No writes.

MUST NOT perform state writes inside `decide` / `act`; MUST NOT emit
a broadcast from `perceive`.

State Initialization (MANDATORY):

- Trigger: `"price" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing): `initial_price`,
  `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`,
  `record_path`, `custom_state_hot_limit`.
- Initial state writes (single atomic block):
  - `state["price"] = extras["initial_price"]`
  - `state["prev_price"] = extras["initial_price"]` (equal to
    current on round 0 — cold-start "no return yet")
  - `state["fundamental"] = extras["fundamental_value"]`
  - `state["price_impact"] = extras["price_impact"]`
  - `state["mean_reversion"] = extras["mean_reversion"]`
  - `state["noise_std"] = extras["noise_std"]`
  - `state["deviation"] = 0.0`
  - `state["price_history"] = HistoryBuffer(folder=<record>/market/price,
    entry_limit=custom_state_hot_limit)`
- Warm-up rounds: `0` (broadcast is trustworthy from round 0, though
  `prev_price == price` on round 0 must be interpreted correctly by
  participants).
- Cold-start reading rule for participants: on round 0, `prev_price
  == price`, so the participant-side return signal SHOULD be treated
  as "no observation yet" rather than "return of zero".

Inbound Message Types:

- **Order**: `{"action": "buy" | "sell" | "hold", "quantity": int ≥ 0,
  "bid_price": float ≥ 0 (advisory), "strategy": str, "reasoning":
  str}`.
  - `"buy"` / `"sell"` with `quantity > 0` contribute to aggregates.
  - `"hold"` or `quantity == 0` are silently ignored.
  - `bid_price` is advisory only; this mechanism uses aggregate
    quantities, not price crossing.
- **Default (no message)**: treated as `"hold"`.

Broadcast Trigger: after every round tick, immediately following the
`perceive` state-write phase.

Missing-Input Policy:

- Missing required extras → **raise `KeyError`** from `perceive`; do
  NOT default.
- Zero inbound orders → set `buy_qty = sell_qty = net_demand = 0` and
  continue; this is a legitimate quiet round.
- Individual malformed order (missing `action` / `quantity`
  unparseable) → log warning, skip that order, continue with the
  rest.
- `NaN` / `Inf` in the computed `new_price` → **raise `ValueError`**
  from `perceive`; do NOT emit a broadcast this round.
- NEVER silently substitute a default for a required field.

Exogenous Driver Boundary (MANDATORY):

- This coordinator MUST NOT generate exogenous news, shocks, or
  regime flips from within its own logic.
- Fundamental changes (e.g. positive news, dividend announcements)
  enter via either (a) a distinguished inbound message from a
  scenario-provided `NewsInjector` agent, in which case `perceive`
  reads it as an ordinary aggregate signal that shifts `state[
  "fundamental"]`, OR (b) a mutation of `config.extras[
  "fundamental_value"]` by the scenario runner performed BEFORE this
  coordinator's `perceive`. The coordinator itself remains passive.

Environmental Dependencies:

- Required extras (see §4.7): `initial_price`, `fundamental_value`,
  `price_impact`, `mean_reversion`, `noise_std`, `record_path`,
  `custom_state_hot_limit`.
- Optional extras: `price_floor` (defaults to `0.01`).
- No scenario driver signals are required beyond what enters via
  the Exogenous Driver Boundary.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input               | Source                          | Type / Shape                                                                                     | Required? | Notes                                                                          |
|---------------------|---------------------------------|--------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------|
| `inbound_orders`    | mailbox from participant agents | `list[dict]`; each dict has `action: str`, `quantity: int ≥ 0`, `bid_price: float`, `strategy: str`, `reasoning: str` | yes       | `bid_price` is advisory only — this mechanism aggregates on quantity            |
| `current_state`     | coordinator's persisted state   | `{"price": float, "prev_price": float, "fundamental": float, "deviation": float, "price_history": HistoryBuffer}` | yes       | Populated on first call by State Initialization                                |
| `context_metadata`  | scheduler / round header        | `{"round": int, "identity": str, "seed": int}`                                                    | yes       | Identity naming: `{variant}_market_stock`                                       |
| `scenario_driver`   | scenario overlay                | `dict` or `None`                                                                                  | no        | Only if scenario declares exogenous fundamental / regime changes                |

##### Outputs (per coordination call)

The coordinator emits exactly one broadcast dict per call. Every
participant sees the identical dict.

| Field           | Type   | Valid Range / Enum          | Unit                 | Required?   | Meaning                                                       |
|-----------------|--------|-----------------------------|----------------------|-------------|---------------------------------------------------------------|
| `price`         | float  | `≥ price_floor`             | currency units       | yes         | Post-transition price P(t+1) for this round                    |
| `prev_price`    | float  | `≥ price_floor`             | currency units       | yes         | Price broadcast in the previous round (P(t))                   |
| `fundamental`   | float  | `> 0`                       | currency units       | yes         | Anchor value F used in mean-reversion                          |
| `deviation`     | float  | `≥ −1` (typically bounded)  | fraction             | yes         | `(price − fundamental) / fundamental`                          |
| `volume`        | float  | `≥ 0`                       | quantity units       | yes         | Round activity metric: `min(buy_qty, sell_qty) + 0.5·|net_demand|` |
| `net_demand`    | float  | any                         | quantity units       | yes         | Signed demand: `buy_qty − sell_qty`                            |
| `round`         | int    | `≥ 0`                       | —                    | yes         | Round number that produced this broadcast                       |

Any participant reading a field NOT listed here indicates a
downstream bug — this contract is the exhaustive schema.

##### Content Constraints

- **Required fields**: all seven fields above MUST be present every
  round.
- **Forbidden fields**: fields not declared above MUST NOT be added
  (silently breaks downstream parsers, notably
  `StandardMarketState.from_market_data`).
- **Value ranges**: `price` clamped to `≥ price_floor` before
  emission; `volume` clamped to `≥ 0`; all fields numeric-finite (no
  NaN / Inf — enforced by the Missing-Input Policy above).
- **Units and sign conventions**: quantity units are dimensionless
  integers on the participant side; `net_demand > 0` means excess
  buy pressure; deviation sign matches price minus fundamental.
- **Determinism markers**: the seed used for ε on each round MUST
  be recoverable from the round number plus the coordinator's
  base seed; two runs with identical seed + identical order
  sequence produce byte-equal broadcasts.

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participant agents, not coordinators).
The canonical shape is:

```json
{
  "price":       102.34,
  "prev_price":  101.10,
  "fundamental": 100.00,
  "deviation":   0.0234,
  "volume":      120.0,
  "net_demand":  40.0,
  "round":       5
}
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag` or any
scheme declared in the target's §10.1) that instantiates this
coordinator MUST emit the identical dict shape. LLM-side variants
never wrap the broadcast in narrative text — the coordinator is
rule-executed even when participants are model-driven.

##### Implementer Contract Reminder

1. **Extras wiring** — every broadcast field's producing formula
   uses only inbound aggregates or `config.extras` keys declared
   in §4.7. No hidden constants.
2. **Broadcast emission** — `decide` populates every `Required = yes`
   field; `price` is clamped to `≥ price_floor` inside `perceive`
   (step 5) before the state-write, not later.
3. **`StandardMarketState.from_market_data()` compatibility** — the
   broadcast satisfies the participant-side format contract. Per
   the code-style rule, `from_market_data` MUST raise `KeyError` if
   any of `price` / `prev_price` / `fundamental` is missing, so
   implementers MUST NOT silently omit those fields.
4. **Variant parity** — every declared variant emits the same
   7-field dict.
5. **Contract-versus-prose conflict resolution** — if the mechanism
   in §4.6.2 or the parameters in §4.7 seem to contradict this
   contract, the contract wins.

#### Input Aggregation Rules

| Aggregate signal | Derivation                                              | Rationale                                            |
|------------------|---------------------------------------------------------|------------------------------------------------------|
| `buy_qty`        | `sum(o["quantity"] for o in orders if o["action"]=="buy")`  | Total buy pressure this round                        |
| `sell_qty`       | `sum(o["quantity"] for o in orders if o["action"]=="sell")` | Total sell pressure this round                       |
| `net_demand`     | `buy_qty − sell_qty`                                        | Signed demand imbalance driving λ term                |
| `n_active`       | `len([o for o in orders if o["action"] != "hold"])`         | Count of non-hold participants; used only for logging |

Does NOT use: individual participant identities; participant
`bid_price` (advisory only in this mechanism); participant capital
or holdings; participant `reasoning` field; peer-to-peer topology.

Completeness rule check: all four aggregates above are consumed in
§4.6.2 (net_demand in step 4; buy_qty/sell_qty in step 6 volume
computation; n_active in step 7 logging).

#### Core Coordination Mechanism

1. **READ** `round_num`, `inbound_orders` from `observation`. Read
   `state["price"] = P(t)`, `state["fundamental"] = F`, and extras
   `{λ = price_impact, γ = mean_reversion, σ = noise_std,
   price_floor}`. Traces to §4.4 Kyle 1985 + Brock–Hommes 1998
   readings.
2. **COMPUTE** aggregates from §4.6.1: `buy_qty`, `sell_qty`,
   `net_demand`. (implementation convenience — no theoretical claim
   beyond linearity.)
3. **COMPUTE** the noise draw `ε = rng.gauss(0, σ)` from the seeded
   RNG. Traces to §4.4 Roll 1984.
4. **COMPUTE** the raw transition:
   `P_raw = P(t) + λ · net_demand + γ · (F − P(t)) + ε`. Traces to
   §4.4 Kyle 1985 (first term), Brock–Hommes 1998 (second term),
   Roll 1984 (third term).
5. **COMPUTE** the floor clamp: `new_price = max(P_raw,
   price_floor)`. Traces to §4.6.6 invariant #5 (state stays
   non-negative / above floor).
6. **COMPUTE** derived observables: `deviation = (new_price − F) / F`
   (guarded against `F == 0` — if `F == 0` set deviation to 0.0);
   `volume = min(buy_qty, sell_qty) + 0.5 · |net_demand|`.
   (implementation convenience — derived, not primary state.)
7. **WRITE** atomically in this order: `state["prev_price"] = P(t)`;
   `state["price"] = new_price`; `state["deviation"] = deviation`;
   `state["price_history"].append(new_price)`. Traces to §4.6.6
   invariant #1 (time-consistency: next round's `prev_price` equals
   this round's `price`).
8. **EMIT** in `decide` the dict `{price, prev_price, fundamental,
   deviation, volume, net_demand, round}`. Traces to §4.6.0 Outputs.

#### Broadcast Space

| Aspect                       | Specification                                                                                          |
|------------------------------|--------------------------------------------------------------------------------------------------------|
| Broadcast fields             | `price`, `prev_price`, `fundamental`, `deviation`, `volume`, `net_demand`, `round` (verbatim §4.6.0 Outputs) |
| State transition rule        | `P(t+1) = max(P(t) + λ·net_demand + γ·(F − P(t)) + ε, price_floor)`                                    |
| Price floor & ceiling        | Floor: `price_floor` (default `0.01`); Ceiling: none (natural cap arises from participant capital)     |
| Freshness policy             | Every-tick; broadcast reflects state committed in the current `perceive`                                |
| Revision policy              | No — a broadcast MUST NOT be retracted or amended within a round; if a bug is detected, the round is aborted (see Failure Modes) |
| State-history retention      | Hot buffer of `custom_state_hot_limit` (default 10000) entries with cold spill to `<record_path>/market/price` via `HistoryBuffer` |
| Resource cap                 | Unbounded on-disk (history spills); RAM bounded by hot-limit                                            |
| Termination rule             | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown     |

#### Mathematical Model

1. **Broadcast outputs**:
   - `price ∈ [price_floor, +∞) ⊂ ℝ`
   - `prev_price ∈ [price_floor, +∞) ⊂ ℝ`
   - `fundamental ∈ ℝ⁺`
   - `deviation ∈ ℝ` (unbounded but typically small)
   - `volume ∈ ℝ⁺ ∪ {0}`
   - `net_demand ∈ ℤ` (in units of participant `quantity`; may be
     any sign)
   - `round ∈ ℤ⁺ ∪ {0}`

2. **State transition logic**:
   ```
   P(t+1) = max( P(t) + λ · NetDemand(t) + γ · (F − P(t)) + ε(t),
                 price_floor )
   ε(t)   ~ N(0, σ²)   — one draw per round, seeded by (base_seed, t)
   NetDemand(t) = Σ_{i: order_i.action == "buy"}  order_i.quantity
                − Σ_{i: order_i.action == "sell"} order_i.quantity
   deviation(t+1) = (P(t+1) − F) / F   if F ≠ 0 else 0
   volume(t)      = min(BuyQty(t), SellQty(t)) + 0.5·|NetDemand(t)|
   ```

3. **State variables**:

   | Variable         | Type            | Initial value                                                   |
   |------------------|-----------------|-----------------------------------------------------------------|
   | `price`          | float           | `extras["initial_price"]`                                       |
   | `prev_price`     | float           | `extras["initial_price"]`                                       |
   | `fundamental`    | float           | `extras["fundamental_value"]`                                    |
   | `deviation`      | float           | `0.0`                                                            |
   | `price_history`  | `HistoryBuffer` | empty, folder = `<record>/market/price`, hot_limit = `extras["custom_state_hot_limit"]` |
   | `round`          | int             | `0`                                                              |

4. **State evolution ordering**: all state writes happen at the end
   of `perceive` (step 7 of §4.6.2), AFTER the transition computation
   and BEFORE `decide` is called. `prev_price` is written before
   `price` so that invariant #1 holds; both use the pre-transition
   value.

5. **Determinism contract**: **stochastic-given-seed**. The single
   randomness source is the Gaussian draw for ε. The RNG is seeded
   from a base seed provided at construction plus the round number,
   so two runs with the same base seed and identical inbound-order
   sequences produce byte-equal broadcasts.

6. **Parameter symbol table**:

   | Symbol         | Meaning                                            | Default Value | Source                                    |
   |----------------|----------------------------------------------------|---------------|-------------------------------------------|
   | `λ`            | Price impact per unit of net demand                | `0.01`        | Kyle 1985 [Ref 1]; Hasbrouck 1991 [Ref 4] |
   | `γ`            | Mean-reversion rate toward fundamental             | `0.01`        | Brock & Hommes 1998 [Ref 2]                |
   | `σ`            | Std dev of Gaussian noise per round                | `0.1`         | Roll 1984 [Ref 12]                         |
   | `F`            | Fundamental value (anchor)                          | `100.0`       | Scenario config                            |
   | `price_floor`  | Absolute lower clamp on price                       | `0.01`        | Standardised                               |
   | `P(0)`         | Initial price                                       | `100.0`       | Scenario config                            |
   | `t`            | Round index                                         | `0` at start  | Scheduler                                  |

#### Coordination Properties

- **Time granularity**: round-based (one tick per participant action
  round).
- **Feedback loop**: mixed — mean-reversion produces negative
  feedback around `F`; sustained one-sided net demand produces
  positive-feedback price drift; the crossover depends on
  parameter ratio `λ/γ` and the persistence of `net_demand`.
- **Information environment**: symmetric — every participant sees
  the identical broadcast. Private information exists only inside
  participant profiles.
- **Stochasticity profile**: one Gaussian ε draw per round; no
  other randomness inside the coordinator.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants:

| # | Invariant                                                                                | Enforcement                                    |
|---|------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | `broadcast[t+1].prev_price == broadcast[t].price` (exactly, byte-equal float)             | §4.6.2 step 7 writes `prev_price ← P(t)` first  |
| 2 | Every required field in §4.6.0 Outputs is present and non-null                            | `decide` assertion                              |
| 3 | `price ≥ price_floor` in every broadcast                                                  | §4.6.2 step 5 clamp                             |
| 4 | `broadcast[t+1].round == broadcast[t].round + 1`                                          | Set from `observation.round` in `perceive`      |
| 5 | `fundamental` unchanged across rounds UNLESS Exogenous Driver Boundary is invoked         | §4.5 boundary rule                              |
| 6 | Two runs with identical `base_seed` and identical inbound-order sequence produce byte-equal broadcasts | Seeded RNG only                        |
| 7 | `deviation == (price − fundamental) / fundamental` (when `fundamental > 0`)               | §4.6.2 step 6                                   |

Domain-Specific Invariants:

- **Non-negativity**: `price ≥ 0` (implied by `price_floor > 0`) —
  invariant #3.
- **Volume non-negativity**: `volume ≥ 0` — from formula in step 6.
- **No cross-round leakage**: `price_history` monotonically grows
  by exactly 1 entry per round.
- **Conservation**: not applicable — this coordinator is
  price-forming only, not authoritative for participant holdings.

Failure Modes:

| Condition                                     | Coordinator behaviour                                  | Broadcast effect                                                    |
|-----------------------------------------------|--------------------------------------------------------|---------------------------------------------------------------------|
| Zero inbound orders                           | Continue; `buy_qty = sell_qty = net_demand = 0`         | Broadcast with pure mean-reversion + noise move                     |
| All buys (`sell_qty = 0`)                     | Continue                                                | `volume = 0.5·net_demand` (min term is 0)                            |
| All sells (`buy_qty = 0`)                     | Continue                                                | `volume = 0.5·|net_demand|` with negative sign in `net_demand`       |
| Order missing `action` or `quantity`          | Log warning; skip that order; continue                  | Aggregate excludes bad order                                        |
| Required extras key missing                   | Raise `KeyError` from `perceive`                        | No broadcast; simulation halts                                      |
| Optional `price_floor` missing                | Use default `0.01`                                      | Normal broadcast                                                    |
| `new_price` computes to NaN / Inf             | Raise `ValueError` from `perceive`                      | No broadcast; simulation halts (implementation defect)              |
| `P_raw < price_floor`                         | Clamp to `price_floor`; log warning at DEBUG level      | Normal broadcast with clamped price                                 |
| Scenario driver mutates `extras["fundamental_value"]` mid-run | Next `perceive` reads new value; log the change | Next broadcast reflects the new fundamental                          |
| `HistoryBuffer` disk write fails              | Raise from `perceive`; do NOT emit stale broadcast      | No broadcast; simulation halts                                      |

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter           | Type  | Default | Valid Range | Sensitivity | Description                        | Impact                                     | Source                        |
|---------------------|-------|---------|-------------|-------------|------------------------------------|--------------------------------------------|-------------------------------|
| `initial_price`     | float | `100.0` | `> 0`       | medium      | Round-0 price seed                 | Higher → higher initial trajectory level    | Scenario config (Kyle 1985)   |
| `fundamental_value` | float | `100.0` | `> 0`       | high        | Anchor F for mean-reversion         | Higher → mean-reversion target shifts up    | Scenario config (BH 1998)     |

#### B. Mechanism Coefficients

| Parameter        | Type  | Default | Valid Range | Sensitivity | Description                                        | Impact                                                   | Source                              |
|------------------|-------|---------|-------------|-------------|----------------------------------------------------|----------------------------------------------------------|-------------------------------------|
| `price_impact`   | float | `0.01`  | `≥ 0`       | high        | λ — price move per unit of net demand              | Higher → 2× more responsive to demand imbalance          | Kyle 1985 [Ref 1]; Hasbrouck 1991 [Ref 4] |
| `mean_reversion` | float | `0.01`  | `[0, 1]`    | high        | γ — pull rate toward fundamental                    | Higher → faster return to F; halves reversion half-life  | Brock & Hommes 1998 [Ref 2]         |
| `noise_std`      | float | `0.1`   | `≥ 0`       | medium      | σ — Gaussian noise std dev added per round          | Higher → more idiosyncratic price oscillation            | Roll 1984 [Ref 12, Table I]         |

#### C. Structural / Boundary Parameters

| Parameter     | Type  | Default | Valid Range | Sensitivity | Description                       | Impact                                  | Source        |
|---------------|-------|---------|-------------|-------------|-----------------------------------|-----------------------------------------|---------------|
| `price_floor` | float | `0.01`  | `≥ 0`       | low         | Absolute lower clamp on price     | Higher → earlier clamp during crash     | Standardised  |

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range   | Sensitivity | Description                              | Impact                              | Source        |
|--------------------------|------|------------|---------------|-------------|------------------------------------------|-------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty     | low         | Root directory for HistoryBuffer spills  | Higher size → more disk footprint   | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`         | low         | HistoryBuffer hot-tier size (entries)    | Higher → more RAM, less disk I/O    | Standardised  |

## Worked Numerical Examples

### Case 1 — Buy-pressure round (positive net demand, inside mean-reversion band)

System state (round `t = 3`):

- `P(t) = 101.10`, `F = 100.00`, `λ = 0.01`, `γ = 0.01`, `σ = 0.1`,
  `price_floor = 0.01`.
- Inbound orders: 3 buys of 20, 15, 10 shares; 2 sells of 8, 12
  shares.

Calculation:

- `buy_qty = 45`, `sell_qty = 20`, `net_demand = 25`.
- `ε ~ N(0, 0.01)` → assume draw `= +0.05`.
- Demand term: `0.01 · 25 = +0.25`.
- Reversion term: `0.01 · (100.00 − 101.10) = −0.011`.
- `P_raw = 101.10 + 0.25 − 0.011 + 0.05 = 101.389`.
- Floor clamp: `max(101.389, 0.01) = 101.389`.
- Deviation: `(101.389 − 100.00) / 100.00 = +0.01389 (+1.39%)`.
- Volume: `min(45, 20) + 0.5·|25| = 20 + 12.5 = 32.5`.

Decision (broadcast dict):

```json
{"price": 101.389, "prev_price": 101.10, "fundamental": 100.00,
 "deviation": 0.01389, "volume": 32.5, "net_demand": 25, "round": 3}
```

State update: `prev_price: 101.10 → 101.10 (unchanged in dict but
stored fresh)`; `price: 101.10 → 101.389`; `deviation: previous →
0.01389`; `price_history.append(101.389)`.

### Case 2 — Sell-pressure round (negative net demand)

System state (round `t = 4`, following Case 1):

- `P(t) = 101.389`, `F = 100.00`, same coefficients.
- Inbound orders: 1 buy of 5; 4 sells of 10, 10, 15, 20.

Calculation:

- `buy_qty = 5`, `sell_qty = 55`, `net_demand = −50`.
- `ε` draw `= −0.03`.
- Demand term: `0.01 · (−50) = −0.50`.
- Reversion term: `0.01 · (100.00 − 101.389) = −0.01389`.
- `P_raw = 101.389 − 0.50 − 0.01389 − 0.03 = 100.845`.
- Floor clamp: no effect (still above 0.01).
- Deviation: `(100.845 − 100.00) / 100.00 = +0.00845 (+0.85%)`.
- Volume: `min(5, 55) + 0.5·50 = 5 + 25 = 30.0`.

Decision:

```json
{"price": 100.845, "prev_price": 101.389, "fundamental": 100.00,
 "deviation": 0.00845, "volume": 30.0, "net_demand": -50, "round": 4}
```

Invariant #1 check: `broadcast[4].prev_price == broadcast[3].price ==
101.389` ✓.

### Case 3 — Balanced round (zero net demand, mean-reversion dominates)

System state (round `t = 5`, following Case 2):

- `P(t) = 100.845`, `F = 100.00`, same coefficients.
- Inbound orders: 2 buys of 20, 20; 2 sells of 20, 20; 1 hold.

Calculation:

- `buy_qty = 40`, `sell_qty = 40`, `net_demand = 0`.
- `ε` draw `= +0.01`.
- Demand term: `0`.
- Reversion term: `0.01 · (100.00 − 100.845) = −0.00845`.
- `P_raw = 100.845 + 0 − 0.00845 + 0.01 = 100.847`.
- Deviation: `+0.00847`.
- Volume: `min(40, 40) + 0.5·0 = 40.0`.

Decision:

```json
{"price": 100.847, "prev_price": 100.845, "fundamental": 100.00,
 "deviation": 0.00847, "volume": 40.0, "net_demand": 0, "round": 5}
```

Observation: with zero net demand, the price moves almost entirely
due to the reversion term (small pull toward F) plus noise.

### Edge Case — Cold-start (round 0) + zero orders

System state (round `t = 0`, first call):

- `state.custom_state` is empty. `initial_price = 100.0`,
  `fundamental_value = 100.0`, `λ = 0.01`, `γ = 0.01`, `σ = 0.1`.
- Inbound orders: none (all participants also in cold-start
  `perceive` and produced no orders yet).

Calculation:

- State Initialization runs: `price ← 100.0`, `prev_price ← 100.0`
  (cold-start convention: equal to current), `fundamental ← 100.0`,
  `deviation ← 0.0`, `price_history ← <empty buffer>`.
- Aggregates: `buy_qty = sell_qty = net_demand = 0`.
- `ε` draw `= +0.02`.
- `P_raw = 100.0 + 0 + 0.01·(100.00 − 100.0) + 0.02 = 100.02`.
- Deviation: `+0.0002`.
- Volume: `0`.

Decision:

```json
{"price": 100.02, "prev_price": 100.0, "fundamental": 100.0,
 "deviation": 0.0002, "volume": 0.0, "net_demand": 0, "round": 0}
```

Cold-start reading rule for participants: because `prev_price == 100.0
== initial_price`, participants MUST treat this as "no return
observation yet" rather than "return of +0.02%".

## Coordinator Verification and Calibration

**Calibration data sources**:

- `price_impact` (λ) ← Hasbrouck 1991 [Ref 4, Table 3]; Chan &
  Lakonishok 1995 [Ref 5, Table II]. Simulation-unit-adjusted
  range: `[0.001, 0.05]`.
- `mean_reversion` (γ) ← Brock & Hommes 1998 [Ref 2, §4] and
  Fama–French 1988 [Ref 8] half-life reinterpretation. Range:
  `[0.005, 0.05]`.
- `noise_std` (σ) ← Roll 1984 [Ref 12, Table I]. Range: `[0.01,
  0.5]` in price units.

**Expected coordinator behaviour** (given `F = 100`, defaults):

- Given `net_demand = +25` and `ε = 0`, the coordinator MUST push
  price up by `≈ +0.25` minus any small reversion pull.
- Given `net_demand = 0`, `P(t) = 105`, and `ε = 0`, the
  coordinator MUST push price toward `F`, producing a broadcast with
  `deviation` strictly smaller in magnitude than the previous round.
- Given `net_demand = 0`, `P(t) = 100`, and `ε = 0`, the coordinator
  MUST emit `price == 100.0` exactly (no drift from any source).
- Given identical `base_seed` and identical inbound-order sequence,
  the coordinator MUST produce byte-equal broadcasts across two
  independent runs.

**Sanity bounds** (red flags for a broken implementation):

- IF `broadcast[t+1].prev_price != broadcast[t].price` THEN the
  state-write ordering is broken (invariant #1).
- IF any broadcast omits a `Required = yes` field THEN the
  contract is broken (invariant #2).
- IF `price` falls below `price_floor` THEN the clamp is broken
  (invariant #3).
- IF `net_demand > 0` AND `mean_reversion == 0` AND `noise_std == 0`
  YET `price` falls THEN the sign convention is broken.
- IF `net_demand == 0` AND `price == fundamental` YET `noise_std ==
  0` YET `price` changes across rounds THEN the transition equation
  has a spurious drift term.
- IF two runs with identical seed + orders produce different
  broadcasts THEN the RNG seeding is broken (invariant #6).

### Ablation Hooks

| Ablation name       | Setting          | Hypothesis tested                                       | Expected direction              | Metric                                                     |
|---------------------|------------------|---------------------------------------------------------|---------------------------------|------------------------------------------------------------|
| `no-mean-reversion` | `γ = 0`          | Removes fundamental anchor; trajectory becomes path-dependent | Higher var(price) over 100 rounds | `Var(price) - baseline`                                    |
| `zero-price-impact` | `λ = 0`          | Orders no longer move price; only reversion + noise remain | Price → fundamental              | `mean_over_rounds(|price - fundamental|)` shrinks near 0    |
| `high-noise`        | `σ *= 10`        | Overwhelms deterministic signal                          | Random-walk-like broadcast series | `Autocorr(price_diff, lag=1)` → 0                          |
| `no-noise`          | `σ = 0`          | Fully deterministic given orders                        | Identical replay across seeds    | `max_over_seeds(|broadcast_a - broadcast_b|) = 0`           |
| `deep-market`       | `λ /= 10`        | Market becomes very deep; large orders barely move price | Damped price-impact response     | `|Δprice / net_demand|` decreases by ~10×                    |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                                                                    | Notes                                                                                          |
|----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1  | Kyle, A. S. (1985). Continuous Auctions and Insider Trading. *Econometrica*, 53(6), 1315–1335. DOI: 10.2307/1913210                                                                                                          | Origin of linear price-impact (Kyle's λ); mechanism basis                                       |
| 2  | Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *JEDC*, 22, 1235–1274. DOI: 10.1016/S0165-1889(98)00011-6                                                    | Fundamentalist mean-reversion (γ term); regime-dependent feedback                              |
| 3  | Farmer, J. D., & Joshi, S. (2002). The price dynamics of common trading strategies. *JEBO*, 49(2), 149–171. DOI: 10.1016/S0167-2681(02)00065-3                                                                              | Justification for round-granularity linear-impact vs full LOB                                  |
| 4  | Hasbrouck, J. (1991). Measuring the Information Content of Stock Trades. *Journal of Finance*, 46(1), 179–207. DOI: 10.1111/j.1540-6261.1991.tb03749.x                                                                       | Empirical calibration range for λ                                                              |
| 5  | Chan, L. K. C., & Lakonishok, J. (1995). The Behavior of Stock Prices Around Institutional Trades. *Journal of Finance*, 50(4), 1147–1174. DOI: 10.1111/j.1540-6261.1995.tb04053.x                                            | Institutional trade price impact; λ calibration                                                |
| 6  | Almgren, R., Thum, C., Hauptmann, E., & Li, H. (2005). Direct Estimation of Equity Market Impact. *Risk*, 18(7), 58–62.                                                                                                    | Alternative non-linear (square-root) price-impact                                              |
| 7  | Tóth, B., et al. (2011). Anomalous price impact and the critical nature of liquidity in financial markets. *Physical Review X*, 1, 021006. DOI: 10.1103/PhysRevX.1.021006                                                    | Latent-liquidity alternative to linear impact                                                  |
| 8  | Fama, E. F., & French, K. R. (1988). Permanent and Temporary Components of Stock Prices. *Journal of Political Economy*, 96(2), 246–273. DOI: 10.1086/261535                                                                | Empirical mean-reversion half-lives (γ calibration)                                             |
| 9  | De Bondt, W. F. M., & Thaler, R. (1985). Does the Stock Market Overreact? *Journal of Finance*, 40(3), 793–805. DOI: 10.1111/j.1540-6261.1985.tb05004.x                                                                     | Long-horizon mean-reversion effect size                                                        |
| 10 | Cutler, D. M., Poterba, J. M., & Summers, L. H. (1991). Speculative Dynamics. *Review of Economic Studies*, 58(3), 529–546. DOI: 10.2307/2298010                                                                            | Alternative adaptive-expectation drift                                                          |
| 11 | Fama, E. F. (1970). Efficient Capital Markets: A Review of Theory and Empirical Work. *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486                                                                             | Alternative: pure random-walk baseline                                                          |
| 12 | Roll, R. (1984). A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market. *Journal of Finance*, 39(4), 1127–1139. DOI: 10.1111/j.1540-6261.1984.tb03897.x                                            | Origin of Gaussian-noise (σ) parameterisation                                                   |
| 13 | Merton, R. C. (1976). Option pricing when underlying stock returns are discontinuous. *Journal of Financial Economics*, 3(1–2), 125–144. DOI: 10.1016/0304-405X(76)90022-2                                                    | Alternative: jump-diffusion residuals                                                          |

## Design Provenance and Versioning

| Field       | Content                                                             |
|-------------|---------------------------------------------------------------------|
| Market Type | `stock` — Stock / Equity Market                                     |
| Author      | AgenticFinLab                                                       |
| Reviewed by | — (pending)                                                          |
| Created     | 2026-07-16                                                          |
| Version     | 1.0.0                                                               |
| Status      | canonical                                                           |
| Icon        | ![](../agent_images/icons/market/stock-standard-price-impact.png)   |
