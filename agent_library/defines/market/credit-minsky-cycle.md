# Minsky-cycle credit market with endogenous leverage-regime state

## Summary

| Field                | Content                                                                                                                                                                                                                                                                                                                                             |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `credit` — Credit / Lending Market                                                                                                                                                                                                                                                                                                                  |
| Coordinator Role     | Central price-formation coordinator for a credit / lending market with an endogenous **Minsky financing regime** state that gates the strength of the fundamental anchor                                                                                                                                                                             |
| Mechanism Family     | Standard linear price-impact + mean-reversion + Gaussian noise, extended with a categorical **Minsky regime** state `{hedge, speculative, ponzi}` whose transitions are a deterministic function of aggregate leverage `L(t)`; optionally a second co-broadcast asset (MBS) for the GFC2008 mode                                                     |
| Shared State         | `credit_price`, `prev_credit_price`, `price_change`, `aggregate_leverage`, `prev_aggregate_leverage`, `minsky_regime`, `prev_minsky_regime`, `regime_transition_this_round`, `num_borrowers`, `num_lenders`, `num_extenders`, `num_contractors`, `net_credit_demand`, `mbs_price` (only if `mbs_enabled = true`), `round`                              |
| Broadcast Cadence    | every-tick (one broadcast per simulation round, after all participants submit orders)                                                                                                                                                                                                                                                               |
| Determinism          | stochastic-given-seed (a single Gaussian noise draw `ε ~ N(0, σ²)` per broadcast per asset from a seeded RNG; regime transitions themselves are deterministic given `L(t)`; identical base seed + identical inbound-order sequence reproduces byte-equal broadcasts)                                                                                 |
| Feedback Direction   | **Regime-dependent** — in the `hedge` regime (`L < L_spec_threshold`) mean-reversion is full-strength (`γ = γ_base`) and the mechanism is **stabilising**; in the `speculative` regime (`L_spec_threshold ≤ L < L_ponzi_threshold`) mean-reversion is halved (`γ = 0.5·γ_base`) and the mechanism is **weakly stabilising / mildly amplifying**; in the `ponzi` regime (`L ≥ L_ponzi_threshold`) mean-reversion collapses (`γ ≈ 0`) and net-demand price-impact dominates, making the mechanism **amplifying** — the classic Minsky moment [Ref 1, Ref 2, Ref 3] |
| Scenario Portability | 2 pool scenarios bound via `players.yml → market.archetype: credit-minsky-cycle`. **Full ✅**: (none). **Approximated ⚠**: CreditCycle, GFC2008 — both scenarios currently use the stock-standard price-impact code path; the Market-side regime state `{hedge, speculative, ponzi}` and the γ(regime) monotone-tightening pathway are intended but not yet implemented. Note: the `MinskyBorrower` player already carries a regime-state variable, but the Market coordinator does not yet consume it. See also the Scenario Status row below. |
| Scenario Status      | **Full** = coordinator code implements the archetype's mechanism signature verbatim; **Approximated** = archetype bound via `players.yml → market.archetype:` for icon/UI/narrative purposes, but the coordinator code currently uses the standard price-impact formula `P(t+1)=P(t)+λ·NetDemand+γ·(F-P(t))+ε` as a placeholder — the archetype's specialized state and dynamics are intended but not yet realized in code. |

## Definition and Goals

This coordinator models a **credit / lending market at a business-cycle
granularity** — a stylised representation of the aggregate credit
market in which the price of credit (or, equivalently, the inverse
of the credit spread over a risk-free rate) is jointly determined by
(a) participant demand for and supply of credit and (b) an
endogenously evolving **Minsky financing regime** that governs how
tightly the fundamental value anchors the observed price. The
real-world counterparts are the **U.S. corporate-credit and shadow-
banking markets during 2003–2009** — the leveraged-loan boom, the
subprime-mortgage originate-to-distribute expansion, and the
subsequent Global Financial Crisis (Brunnermeier 2009 [Ref 8];
Gorton & Metrick 2012 [Ref 9]; Reinhart & Rogoff 2011 [Ref 7]) —
and, more generally, any credit boom-bust episode documented in the
Reinhart & Rogoff (2011) [Ref 7] cross-country credit-boom sample.
Following Minsky (1986/1992) [Ref 1, Ref 2] and Geanakoplos (2010)
[Ref 3], the coordinator treats the aggregate leverage of the
economy as a state variable whose *level* deterministically induces
one of three qualitatively distinct financing regimes — hedge,
speculative, and Ponzi — each of which changes the effective
elasticity of the market's response to shocks.

The coordination goal is to **aggregate all participant credit
orders each round (buy / sell of the credit asset, borrow / repay
of debt, and extend / contract of credit lines), produce one new
credit price `P(t+1)` via the equation `P(t+1) = P(t) + λ·NetDemand
+ γ(regime(t))·(F − P(t)) + ε`, update aggregate leverage `L(t+1)
= max(L(t) + η·NetBorrowing(t) − ζ·NetRepayment(t), 0)`, run the
deterministic regime-transition function `regime(t+1) =
f(L(t+1))`, and broadcast the complete state dict to every
participant.** In the GFC2008 mode (`mbs_enabled = true`) the
coordinator ALSO clears an MBS asset with an independent
`buy_mbs` / `sell_mbs` order stream using the SAME λ, γ(regime), σ
coefficients (so the MBS price shares the same Minsky regime state
as the underlying credit price — this is the key mechanism through
which the housing-credit shock propagates to the securitised layer
per Gorton–Metrick 2012 [Ref 9]).

Non-goals (this coordinator MUST NOT):

- MUST NOT filter or route orders based on participant identity or
  credit rating — differential treatment of borrowers is the job of
  scenario-specific participant profiles.
- MUST NOT inject exogenous news, macro-shocks, policy-rate changes,
  or regime flips from within its own logic — such drivers enter
  only via the Exogenous Driver Boundary (§4.5).
- MUST NOT enforce participant-level leverage or capital-ratio
  limits — those are self-imposed disciplines declared in each
  participant profile per `agent-design-skill.md` §3.6.3.
- MUST NOT compute credit-default losses, mark-to-market write-downs
  on individual balance sheets, or intra-firm insolvency events —
  the coordinator broadcasts market-level state only.
- MUST NOT modify the fundamental credit value `F` from its own
  logic; fundamental drift, if any, enters via the Exogenous Driver
  Boundary.

## Theoretical / Mechanistic Foundation

**Linear price-impact from net credit demand (Kyle 1985; adapted to credit markets)**:

- Theory / Study: Continuous auction equilibrium with a strategic
  informed trader, applied to a credit-asset market.
- Citation: Kyle, A. S. (1985). "Continuous Auctions and Insider
  Trading." *Econometrica*, 53(6), 1315–1335.
  DOI: `10.2307/1913210`
- Core Insight: In a batch-clearing market, the equilibrium price
  change is a **linear function of aggregate order flow**; Kyle's λ
  captures market depth. The credit-market interpretation is that
  net demand for credit assets moves the credit price (or,
  equivalently, tightens/widens the credit spread) linearly at
  round granularity.
- Mathematical Formulation: `ΔP_demand = λ · NetDemand`, where
  `NetDemand = BuyCredit − SellCredit` (contract-extension and
  contract-contraction contributions are folded into net demand via
  §4.6.1).
- Empirical Evidence: Chen, Lookman, Schürhoff & Seppi (2014)
  [Ref 10, Table III] estimate price-impact elasticities for
  corporate-bond block trades in the 4–8 bp per $1M range;
  translated to simulation units (`quantity` = single credit
  contracts, `price` = index units) our default `λ = 0.01`
  reproduces a per-round move of ≈ 1% at `|NetDemand| = 1`.
- Relevance to This Coordinator: Provides the demand-driven credit-
  price change term `λ · NetDemand` in the transition equation.
- Calibration Source: Chen et al. 2014 [Ref 10, Table III];
  simulation-unit-adjusted range `λ ∈ [0.001, 0.05]`.
- Falsification Conditions: If a doubling of `NetDemand` (holding
  regime, seed, and all else constant) does NOT approximately
  double `ΔP_demand`, the linear-impact property is broken.
- Alternative Mechanisms: Non-linear (square-root) price impact for
  credit assets [Ref 11]; latent-liquidity models [Ref 12].

**Minsky financing regime as an endogenous state variable (Minsky 1986/1992)**:

- Theory / Study: Financial Instability Hypothesis — periods of
  stability breed instability because agents progress from hedge
  (able to service debt from operating cash flow) → speculative
  (able to service interest but must roll principal) → Ponzi
  (must borrow to pay interest itself).
- Citation: Minsky, H. P. (1992). "The Financial Instability
  Hypothesis." *Levy Economics Institute Working Paper No. 74*.
  URL: `https://www.levyinstitute.org/pubs/wp74.pdf`. See also
  Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale
  University Press. ISBN: 978-0300041521.
- Core Insight: The aggregate financing regime of the economy is
  categorical (three phases) and its transitions are driven by
  the accumulation of leverage during tranquil periods. Once
  Ponzi financing dominates, the market has "lost its anchor" —
  small negative shocks cannot be absorbed by cash flow and
  trigger a cascade of fire-sales. This coordinator
  operationalises the categorical regime as a state variable
  `minsky_regime ∈ {"hedge", "speculative", "ponzi"}` whose
  transitions are deterministic threshold-crossings of aggregate
  leverage `L(t)`.
- Mathematical Formulation:
  ```
  regime(t+1) = "hedge"        if L(t+1) < L_spec_threshold
              = "speculative"  if L_spec_threshold ≤ L(t+1) < L_ponzi_threshold
              = "ponzi"        if L(t+1) ≥ L_ponzi_threshold
  γ(regime)   = γ_base          if regime = "hedge"
              = 0.5 · γ_base    if regime = "speculative"
              = ε_γ · γ_base    if regime = "ponzi"       (default ε_γ = 0.05)
  ```
- Empirical Evidence: Reinhart & Rogoff (2011) [Ref 7, Table 1]
  identify 66 credit-boom episodes across advanced economies in
  which private-credit / GDP rose by ≥ 15 pp over 3–5 years and
  the boom was followed by a systemic banking crisis with
  probability ≈ 0.50; Schularick & Taylor (2012) [Ref 13,
  Figure 4] find that credit-growth in the top decile of the
  historical distribution predicts financial crises within 5
  years at ≈ 3× the base rate. The threshold crossings in this
  coordinator are calibrated so `L_spec_threshold ≈ 1.5·L(0)`
  and `L_ponzi_threshold ≈ 2.5·L(0)`, consistent with the
  Reinhart–Rogoff pre-crisis credit-to-baseline ratios.
- Relevance to This Coordinator: Provides the regime state that
  gates mean-reversion strength — the mechanism by which
  "stability breeds instability" in a computable form.
- Calibration Source: Reinhart & Rogoff 2011 [Ref 7, Table 1];
  Schularick & Taylor 2012 [Ref 13, §3].
- Falsification Conditions: If `L(t)` crosses `L_ponzi_threshold`
  from below but the broadcast still reports `regime = "hedge"`,
  the regime-transition function is broken. If `L(t)` exceeds
  `L_ponzi_threshold` for K consecutive rounds and yet a
  `net_demand = 0, ε = 0` broadcast still reverts `price` toward
  `F` at rate `γ_base`, the regime-γ coupling is broken.
- Alternative Mechanisms: Continuous-γ dependence on L (smooth
  logistic instead of stepwise) [Ref 14]; Geanakoplos leverage-
  cycle regimes indexed by collateral haircuts [Ref 3].

**Regime-gated mean-reversion toward fundamental credit value (Brock & Hommes 1998; regime-gated variant)**:

- Theory / Study: Heterogeneous adaptive belief systems, with
  the fundamentalist-weight modulated by the Minsky regime.
- Citation: Brock, W. A., & Hommes, C. H. (1998). "Heterogeneous
  beliefs and routes to chaos in a simple asset pricing model."
  *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274.
  DOI: `10.1016/S0165-1889(98)00011-6`
- Core Insight: The rate at which prices revert to fundamentals
  is proportional to the effective weight of fundamentalist
  traders in the market. In a credit market, that weight collapses
  as leverage rises and Ponzi financing dominates (fundamentalists
  cannot arbitrage against Ponzi rollovers with limited capital,
  per Shleifer & Vishny 1997 [Ref 15]). This coordinator
  operationalises the collapsing fundamentalist weight as the
  regime-dependent γ multiplier.
- Mathematical Formulation: `ΔP_reversion = γ(regime) · (F − P(t))`.
- Empirical Evidence: Adrian & Shin (2010) [Ref 4, Figure 2]
  document that intermediary leverage is strongly procyclical and
  that during 2007–2008 the effective anchoring of asset prices to
  fundamentals collapsed as broker-dealer leverage peaked. Fama &
  French (1988) [Ref 16] mean-reversion half-lives (3–5 years)
  provide the `γ_base ≈ 0.01` calibration at round granularity.
- Relevance to This Coordinator: Provides the anchor-pull term
  whose strength is state-dependent.
- Calibration Source: Brock & Hommes 1998 [Ref 6, §4]; Fama &
  French 1988 [Ref 16].
- Falsification Conditions: If, holding `NetDemand = 0`,
  `ε = 0`, and `regime = "ponzi"`, ten consecutive broadcasts
  reduce `|price − fundamental|` at a rate ≥ 0.5·γ_base, the
  regime-γ collapse is broken.
- Alternative Mechanisms: Constant-γ (regime-independent, i.e. a
  pure BH98 model — this is the ablation `no-regime-gate`);
  no-reversion pure random walk when in Ponzi regime [Ref 17].

**Aggregate leverage accumulation from borrowing / repayment flows (Adrian & Shin 2010; Kiyotaki & Moore 1997)**:

- Theory / Study: Procyclical intermediary leverage; collateral-
  constrained leverage cycle.
- Citation: Adrian, T., & Shin, H. S. (2010). "Liquidity and
  leverage." *Journal of Financial Intermediation*, 19(3),
  418–437. DOI: `10.1016/j.jfi.2008.12.002`. See also Kiyotaki,
  N., & Moore, J. (1997). "Credit Cycles." *Journal of Political
  Economy*, 105(2), 211–248. DOI: `10.1086/262072`.
- Core Insight: Aggregate leverage in the financial system evolves
  procyclically — new borrowing (during booms) adds to the
  aggregate leverage stock at rate `η`, and net repayment (during
  contractions) subtracts at rate `ζ`. When rising asset prices
  loosen collateral constraints, borrowing accelerates, which is
  precisely the mechanism through which leverage crosses the
  Minsky-regime thresholds endogenously.
- Mathematical Formulation:
  `L(t+1) = max(L(t) + η · NetBorrowing(t) − ζ · NetRepayment(t), 0)`
  where `NetBorrowing = Σ (borrow_size) + Σ (extend_size)` and
  `NetRepayment = Σ (repay_size) + Σ (contract_size)` from the
  round's inbound orders.
- Empirical Evidence: Adrian & Shin (2010) [Ref 4, Figure 3, Table
  2] estimate that a 1% rise in total assets of U.S. broker-dealers
  is associated with a ≈ 0.7% rise in leverage during 2001–2007,
  and the ratio collapses symmetrically during 2008–2009. Our
  defaults `η = 0.005`, `ζ = 0.004` reproduce a comparable
  aggregate-leverage half-life to the Adrian–Shin sample when
  scaled to round granularity.
- Relevance to This Coordinator: Provides the state-evolution law
  for `aggregate_leverage`, which drives the regime state.
- Calibration Source: Adrian & Shin 2010 [Ref 4, Table 2];
  Kiyotaki & Moore 1997 [Ref 5, §4] collateral multipliers.
- Falsification Conditions: If `NetBorrowing = 0`,
  `NetRepayment = 0`, and yet `L(t+1) ≠ L(t)`, the leverage
  evolution equation has a spurious drift. If `NetBorrowing > 0`
  and `NetRepayment = 0` yet `L(t+1) < L(t)`, the sign is wrong.
- Alternative Mechanisms: Bernanke–Gertler (1989) [Ref 18]
  agency-cost formulation with an external-finance premium
  linking L to price; Rajan (2010) [Ref 19] systemic-risk-
  linked leverage caps.

**Gaussian idiosyncratic noise (efficient-market residual)**:

- Theory / Study: Idiosyncratic microstructure noise.
- Citation: Roll, R. (1984). "A Simple Implicit Measure of the
  Effective Bid-Ask Spread in an Efficient Market." *Journal of
  Finance*, 39(4), 1127–1139. DOI: `10.1111/j.1540-6261.1984.tb03897.x`
- Core Insight: An irreducible zero-mean Gaussian residual is
  standard practice for round-granularity price processes.
- Mathematical Formulation: `ε ~ N(0, σ²)`, one draw per asset
  per round, seeded by `(base_seed, round, asset_index)`.
- Empirical Evidence: Roll (1984) [Ref 20, Table I] estimates
  0.1–1% of price for NYSE stocks; our default `σ = 0.1`
  corresponds to ≈ 0.1% at `initial_credit_price = 100`.
- Relevance to This Coordinator: Adds the `ε` term to `P(t+1)`.
- Calibration Source: Roll 1984 [Ref 20, Table I]; range
  `[0.01, 0.5]` in price units.
- Falsification Conditions: If `ε` is drawn from a distribution
  with materially non-zero mean or a non-Gaussian family, the
  mechanism has been altered.
- Alternative Mechanisms: Heteroskedastic (GARCH) residuals
  [Ref 21]; jump-diffusion residuals for crisis-period MBS
  price paths [Ref 22].

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate all participant credit orders and financing flows
each round, apply the linear-impact + regime-gated mean-reversion +
noise transition to the credit price, evolve aggregate leverage,
compute the deterministic Minsky-regime transition, and broadcast a
single authoritative credit-market state snapshot (plus MBS price if
`mbs_enabled = true`).

Coordination Cadence: **every-tick** (one broadcast per simulation
round; the round advances only after `act()` completes).

Lifecycle Mapping (MANDATORY):

- `perceive(observation, prev_result)`:
  1. Read `round_num = observation.round` and write it to
     `state["round"]`.
  2. If `"credit_price"` is not yet in `state.custom_state`, run
     the State Initialization block below.
  3. Drain `observation.inbounds`; each inbound payload is a
     participant order dict.
  4. Compute aggregates per §4.6.1 — `buy_credit_qty`,
     `sell_credit_qty`, `borrow_qty`, `repay_qty`, `extend_qty`,
     `contract_qty`, `net_credit_demand`, `net_borrowing`,
     `net_repayment`, `buy_mbs_qty`, `sell_mbs_qty`,
     `net_mbs_demand`, `num_borrowers`, `num_lenders`,
     `num_extenders`, `num_contractors` — READ phase only, no
     writes yet.
- `decide()`:
  1. **Deviation from standard skeleton — state-writes happen in
     `decide`, not `perceive`.** Because the regime transition
     depends on the *post-update* aggregate leverage `L(t+1)`, and
     because `γ(regime)` on the RHS of `P(t+1)` must use the
     *current-round* regime (i.e. the regime derived from `L(t+1)`
     to avoid a one-round staleness that would let a Ponzi-regime
     price still get pulled at hedge-regime γ), the coordinator
     performs its full compute-then-write block inside `decide()`
     rather than `perceive()`. This deviates from the reference
     `stock-standard-price-impact` profile (which writes in
     `perceive` step 5) and is deliberate: it keeps the
     leverage-to-regime-to-γ chain within one atomic block.
     `perceive` remains write-free for aggregates (they are
     stored in ephemeral round-local state, not `custom_state`).
     The lifecycle-invariant "`perceive` reads, `decide` returns
     the payload, `act` emits" is preserved because writes here
     are internal state updates that happen *before* the payload
     is assembled and returned; no external observers see state
     changes between `perceive` and `decide`. See §4.6.6
     invariants #1 and #8 for the round-boundary guarantees this
     preserves. **Implementers MUST NOT move these writes back to
     `perceive` — doing so decouples γ from the same-round
     regime and violates §4.6.6 invariant #8.**
  2. Draw `ε_credit ~ N(0, σ²)` from the seeded RNG; if
     `mbs_enabled = true` draw `ε_mbs ~ N(0, σ²)` from an
     independently-seeded stream (seed = `(base_seed, round,
     asset_index=1)`).
  3. Compute `L_raw = L(t) + η·net_borrowing − ζ·net_repayment`;
     `L(t+1) = max(L_raw, 0)`.
  4. Compute `regime(t+1) = f(L(t+1))` per §4.4 Minsky block;
     compute `γ(regime(t+1))`; compute `regime_transition_this_round
     = (regime(t+1) != regime(t))`.
  5. Compute `P_raw = P(t) + λ·net_credit_demand +
     γ(regime(t+1))·(F − P(t)) + ε_credit`; compute
     `credit_price(t+1) = max(P_raw, price_floor)`; compute
     `price_change = credit_price(t+1) − P(t)`.
  6. (If `mbs_enabled`) compute `MBS_raw = M(t) + λ·net_mbs_demand
     + γ(regime(t+1))·(F_mbs − M(t)) + ε_mbs`; `mbs_price(t+1)
     = max(MBS_raw, price_floor)`. Note: the *same* regime state
     gates both assets — this is the Gorton–Metrick 2012 [Ref 9]
     securitised-banking co-movement mechanism.
  7. WRITE atomically in this order: `state["prev_credit_price"] =
     P(t)`; `state["credit_price"] = credit_price(t+1)`;
     `state["prev_aggregate_leverage"] = L(t)`;
     `state["aggregate_leverage"] = L(t+1)`;
     `state["prev_minsky_regime"] = regime(t)`;
     `state["minsky_regime"] = regime(t+1)`;
     `state["regime_transition_this_round"] =
     regime_transition_this_round`; (if `mbs_enabled`)
     `state["prev_mbs_price"] = M(t)`; `state["mbs_price"] =
     mbs_price(t+1)`; append to `credit_price_history`,
     `leverage_history`, `regime_history` history buffers.
  8. Return a dict conforming to §4.6.0 Outputs assembled from
     committed state. No further writes after this line.
- `act(decision)`:
  1. Wrap the dict as `MarketBroadcast` (or engine equivalent) and
     emit to every participant via the standard outbox. No writes.

MUST NOT emit a broadcast from `perceive`, and MUST NOT perform
additional state writes inside `act`. `decide` writes are
permitted (and required) per the deviation documented above.

State Initialization (MANDATORY):

- Trigger: `"credit_price" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing):
  - `initial_credit_price` — float, round-0 credit-price seed
  - `fundamental_credit_price` — float, anchor F
  - `initial_leverage` — float, round-0 aggregate leverage
  - `price_impact` — float λ
  - `mean_reversion_pull_base` — float γ_base
  - `borrowing_impact_on_leverage` — float η
  - `repayment_impact_on_leverage` — float ζ
  - `leverage_speculative_threshold` — float L_spec_threshold
  - `leverage_ponzi_threshold` — float L_ponzi_threshold
  - `noise_std` — float σ
  - `mbs_enabled` — bool (controls two-asset mode)
  - `record_path` — str, root for HistoryBuffer spills
  - `custom_state_hot_limit` — int, hot-buffer capacity
- Conditionally required extras (raise `KeyError` if
  `mbs_enabled = true` and missing):
  - `initial_mbs_price` — float, round-0 MBS-price seed
  - `fundamental_mbs_price` — float, anchor F_mbs
- Optional extras (documented defaults apply if missing):
  - `price_floor` (default `0.01`)
  - `ponzi_gamma_multiplier` (default `0.05` — the ε_γ
    multiplier that scales γ_base in the Ponzi regime; must be
    in `[0, 0.5]`)
  - `speculative_gamma_multiplier` (default `0.5`)
- Initial state writes (single atomic block on first call):
  - `state["credit_price"] = extras["initial_credit_price"]`
  - `state["prev_credit_price"] = extras["initial_credit_price"]`
    (equal to current on round 0 — cold-start "no return yet")
  - `state["fundamental_credit_price"] =
    extras["fundamental_credit_price"]`
  - `state["aggregate_leverage"] = extras["initial_leverage"]`
  - `state["prev_aggregate_leverage"] = extras["initial_leverage"]`
  - `state["minsky_regime"] = f(extras["initial_leverage"])`
    (deterministic; usually `"hedge"` at a properly seeded start)
  - `state["prev_minsky_regime"] = state["minsky_regime"]`
  - `state["regime_transition_this_round"] = False`
  - `state["price_change"] = 0.0`
  - Coefficients cached: `state["price_impact"] = λ`,
    `state["mean_reversion_pull_base"] = γ_base`,
    `state["noise_std"] = σ`, `state["borrowing_impact_on_leverage"]
    = η`, `state["repayment_impact_on_leverage"] = ζ`,
    `state["leverage_speculative_threshold"]`,
    `state["leverage_ponzi_threshold"]`,
    `state["ponzi_gamma_multiplier"]`,
    `state["speculative_gamma_multiplier"]`,
    `state["mbs_enabled"]`.
  - `state["credit_price_history"] = HistoryBuffer(folder=
    <record>/market/credit_price, entry_limit=hot_limit)`
  - `state["leverage_history"] = HistoryBuffer(folder=
    <record>/market/leverage, entry_limit=hot_limit)`
  - `state["regime_history"] = HistoryBuffer(folder=
    <record>/market/regime, entry_limit=hot_limit)`
  - If `mbs_enabled = true`: also
    `state["mbs_price"] = extras["initial_mbs_price"]`,
    `state["prev_mbs_price"] = extras["initial_mbs_price"]`,
    `state["fundamental_mbs_price"] =
    extras["fundamental_mbs_price"]`,
    `state["mbs_price_history"] = HistoryBuffer(folder=
    <record>/market/mbs_price, entry_limit=hot_limit)`.
- Warm-up rounds: `0` (broadcast is trustworthy from round 0;
  cold-start `prev_* == current_*` convention holds).
- Cold-start reading rule for participants: on round 0,
  `prev_credit_price == credit_price` and
  `prev_aggregate_leverage == aggregate_leverage`, so the
  participant-side change signals SHOULD be treated as "no
  observation yet" rather than "change of zero".

Inbound Message Types:

- **Order** (`action_type ∈ {"buy_credit", "sell_credit", "borrow",
  "repay", "extend_credit", "contract_credit"}`):
  ```
  {
    "action_type": str (one of the 6 above),
    "intensity": float ∈ [0, 1]  (advisory, drives quantity for
                                  narrative-driven variants),
    "size":      int ≥ 0         (the aggregated quantity used
                                  for pricing / leverage)
  }
  ```
  - `"buy_credit"` / `"sell_credit"` with `size > 0` feed into
    `net_credit_demand` per §4.6.1.
  - `"borrow"` / `"extend_credit"` with `size > 0` feed into
    `net_borrowing`.
  - `"repay"` / `"contract_credit"` with `size > 0` feed into
    `net_repayment`.
- **MBS-Order** (only accepted when `mbs_enabled = true`;
  `action_type ∈ {"buy_mbs", "sell_mbs"}`, same `intensity` /
  `size` fields):
  - `"buy_mbs"` / `"sell_mbs"` feed into `net_mbs_demand`.
- **Default (no message / any other action_type)**: treated as a
  no-op ("hold"), silently ignored, does not contribute to any
  aggregate.

Broadcast Trigger: after every round tick, immediately following
`decide`'s state-write phase; `act` performs the emission.

Missing-Input Policy:

- Missing required extras → **raise `KeyError`** from `perceive`
  (or from `decide` for the conditionally-required MBS extras if
  `mbs_enabled = true`); do NOT default.
- Zero inbound orders → set every aggregate to `0` and continue;
  this is a legitimate quiet round. `L(t+1) = L(t)`,
  `regime(t+1) = regime(t)`, and the credit-price update is
  pure mean-reversion + noise.
- Individual malformed order (missing `action_type` / `size`
  unparseable / `size < 0` / `intensity` outside `[0, 1]`) → log
  warning at WARN level, skip that order, continue with the
  rest.
- `NaN` / `Inf` in `L(t+1)`, `credit_price(t+1)`, or (if
  applicable) `mbs_price(t+1)` → **raise `ValueError`** from
  `decide`; do NOT emit a broadcast.
- Regime function receives `L(t+1) < 0` → this can only occur if
  the `max(·, 0)` clamp is disabled; raise `ValueError`.
- NEVER silently substitute a default for a required field — that
  masks bugs.

Exogenous Driver Boundary (MANDATORY):

- This coordinator MUST NOT generate exogenous news, macro-shocks,
  policy-rate shifts, or regime flips from within its own logic.
  Regime transitions ARE generated internally, but ONLY as a
  deterministic function of the endogenously accumulated
  aggregate leverage `L(t)` — they are not exogenous drivers.
- Exogenous fundamental changes (e.g. macro-shock to
  `fundamental_credit_price`, subprime-write-down news to
  `fundamental_mbs_price`) enter via either
  (a) a distinguished inbound message from a scenario-provided
      `NewsInjector` / `ScenarioDriver` agent, which
      `perceive` reads and writes to `state["fundamental_*"]`, OR
  (b) a mutation of `config.extras["fundamental_credit_price"]`
      (or `["fundamental_mbs_price"]`) performed BEFORE the
      coordinator's `perceive` on that round by the scenario
      runner.
- Regime-threshold parameters (`L_spec_threshold`,
  `L_ponzi_threshold`) MAY be mutated by the scenario runner
  between rounds (this represents policy tightening); such
  mutations are read at the top of `decide` and are logged.

Environmental Dependencies:

- Required extras: as listed in State Initialization above
  (12 unconditional + 2 conditional-on-`mbs_enabled` = up to 14).
- Optional extras: `price_floor`, `ponzi_gamma_multiplier`,
  `speculative_gamma_multiplier`.
- No scenario driver signals are required beyond the Exogenous
  Driver Boundary channels.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input               | Source                          | Type / Shape                                                                                                                                                                                                    | Required? | Notes                                                                                          |
|---------------------|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|------------------------------------------------------------------------------------------------|
| `inbound_orders`    | mailbox from participant agents | `list[dict]`; each dict has `action_type: str ∈ {"buy_credit","sell_credit","borrow","repay","extend_credit","contract_credit","buy_mbs","sell_mbs"}`, `intensity: float ∈ [0,1]`, `size: int ≥ 0`             | yes       | MBS actions accepted only if `mbs_enabled = true`; unknown `action_type` is silently ignored    |
| `current_state`     | coordinator's persisted state   | `{"credit_price": float, "prev_credit_price": float, "fundamental_credit_price": float, "aggregate_leverage": float, "minsky_regime": str, "prev_minsky_regime": str, ..., history buffers}`                    | yes       | Populated on first call by State Initialization                                                 |
| `context_metadata`  | scheduler / round header        | `{"round": int, "identity": str, "seed": int}`                                                                                                                                                                  | yes       | Identity naming: `{variant}_market_credit`                                                      |
| `scenario_driver`   | scenario overlay                | `dict` or `None`                                                                                                                                                                                                | no        | Only if scenario declares exogenous fundamental / regime-threshold changes                      |
| `mbs_enabled_flag`  | `config.extras["mbs_enabled"]`  | `bool`                                                                                                                                                                                                          | yes       | Read once at State Initialization; determines single-asset vs two-asset mode                    |

##### Outputs (per coordination call)

The coordinator emits exactly one broadcast dict per call. Every
participant receives the identical dict.

| Field                            | Type   | Valid Range / Enum                        | Unit                     | Required?          | Meaning                                                                                                             |
|----------------------------------|--------|-------------------------------------------|--------------------------|--------------------|---------------------------------------------------------------------------------------------------------------------|
| `credit_price`                   | float  | `≥ price_floor`                           | credit-index units       | yes                | Post-transition credit price `P(t+1)`                                                                                |
| `prev_credit_price`              | float  | `≥ price_floor`                           | credit-index units       | yes                | Credit price broadcast in the previous round                                                                         |
| `price_change`                   | float  | any                                       | credit-index units       | yes                | `credit_price(t+1) − prev_credit_price` (this-round change)                                                          |
| `fundamental_credit_price`       | float  | `> 0`                                     | credit-index units       | yes                | Anchor F used in mean-reversion for credit                                                                           |
| `aggregate_leverage`             | float  | `≥ 0`                                     | leverage units           | yes                | Post-update aggregate leverage `L(t+1)`                                                                              |
| `prev_aggregate_leverage`        | float  | `≥ 0`                                     | leverage units           | yes                | Aggregate leverage broadcast in the previous round                                                                   |
| `minsky_regime`                  | str    | `{"hedge","speculative","ponzi"}`         | categorical              | yes                | Current-round Minsky financing regime (deterministic function of `L(t+1)`)                                          |
| `prev_minsky_regime`             | str    | `{"hedge","speculative","ponzi"}`         | categorical              | yes                | Regime broadcast in the previous round                                                                               |
| `regime_transition_this_round`   | bool   | `{true, false}`                           | —                        | yes                | True iff `minsky_regime != prev_minsky_regime` (participants use this as a change signal)                            |
| `num_borrowers`                  | int    | `≥ 0`                                     | count                    | yes                | Number of distinct participants who submitted `action_type = "borrow"` this round                                    |
| `num_lenders`                    | int    | `≥ 0`                                     | count                    | yes                | Number who submitted `"buy_credit"` this round                                                                       |
| `num_extenders`                  | int    | `≥ 0`                                     | count                    | yes                | Number who submitted `"extend_credit"` this round                                                                    |
| `num_contractors`                | int    | `≥ 0`                                     | count                    | yes                | Number who submitted `"contract_credit"` this round                                                                  |
| `net_credit_demand`              | float  | any                                       | quantity units           | yes                | `buy_credit_qty − sell_credit_qty` (drives λ term for credit)                                                        |
| `mbs_price`                      | float  | `≥ price_floor`                           | MBS-index units          | conditional        | Post-transition MBS price `M(t+1)`. **Required if and only if `mbs_enabled = true`**; MUST NOT be broadcast otherwise |
| `round`                          | int    | `≥ 0`                                     | —                        | yes                | Round number that produced this broadcast                                                                            |

Any participant reading a field NOT listed here indicates a
downstream bug — this contract is the exhaustive schema.
`mbs_price` is a conditional field: implementers MUST include it
exactly when `mbs_enabled = true` and MUST NOT include it
otherwise (silent inclusion would break single-asset variants).

##### Content Constraints

- **Required fields**: all `yes`-flagged fields MUST be present
  every round. `mbs_price` MUST be present iff `mbs_enabled = true`.
- **Forbidden fields**: fields not declared above MUST NOT be
  broadcast (silently breaks `StandardMarketState.from_market_data`
  and downstream credit-cycle participant parsers).
- **Value ranges**: `credit_price` clamped to `≥ price_floor`
  before emission; `mbs_price` clamped to `≥ price_floor`;
  `aggregate_leverage` clamped to `≥ 0`; all numeric fields
  finite (no NaN / Inf — enforced by Missing-Input Policy).
- **Categorical domain**: `minsky_regime` and `prev_minsky_regime`
  MUST both be members of `{"hedge", "speculative", "ponzi"}` — the
  three-value support is closed and MUST NOT be extended without a
  new profile version.
- **Units and sign conventions**: `size` fields on the inbound side
  are non-negative integer quantities; `net_credit_demand > 0`
  means excess buy pressure on credit; `net_borrowing > 0` means
  the round expanded aggregate credit; `price_change` sign matches
  `credit_price(t+1) − prev_credit_price`.
- **Determinism markers**: the seeds used for `ε_credit` and (if
  applicable) `ε_mbs` on each round MUST be recoverable from the
  round number plus the coordinator's base seed
  (`(base_seed, round, asset_index)`); two runs with identical
  seed + identical order sequence produce byte-equal broadcasts.

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participant agents, not
coordinators). The canonical shape in two-asset mode is:

```json
{
  "credit_price":                 102.34,
  "prev_credit_price":            101.10,
  "price_change":                 1.24,
  "fundamental_credit_price":     100.00,
  "aggregate_leverage":           1.87,
  "prev_aggregate_leverage":      1.75,
  "minsky_regime":                "speculative",
  "prev_minsky_regime":           "hedge",
  "regime_transition_this_round": true,
  "num_borrowers":                4,
  "num_lenders":                  6,
  "num_extenders":                2,
  "num_contractors":              1,
  "net_credit_demand":            35.0,
  "mbs_price":                    97.55,
  "round":                        12
}
```

Single-asset mode (`mbs_enabled = false`) omits the `mbs_price`
key. Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag`
or any scheme declared in the target's §10.1) that instantiates
this coordinator MUST emit the identical dict shape for its mode.
LLM-side variants never wrap the broadcast in narrative text — the
coordinator is rule-executed even when participants are
model-driven.

##### Implementer Contract Reminder

1. **Extras wiring** — every broadcast field's producing formula
   uses only inbound aggregates or `config.extras` keys declared
   in §4.7. No hidden constants.
2. **Broadcast emission** — `decide` writes state atomically per
   the deviation documented in §4.5, then assembles the dict;
   `credit_price` (and, if applicable, `mbs_price`) are clamped
   to `≥ price_floor` inside `decide` (step 5/6) before the
   state-write, not later. `aggregate_leverage` is clamped to
   `≥ 0` in step 3.
3. **`StandardMarketState.from_market_data()` compatibility** — the
   broadcast satisfies the participant-side format contract. Per
   the code-style rule, `from_market_data` MUST raise `KeyError`
   if any of `credit_price` / `prev_credit_price` /
   `fundamental_credit_price` / `minsky_regime` is missing, so
   implementers MUST NOT silently omit those fields.
4. **Variant parity** — every declared variant emits the same
   15-field dict (single-asset mode) or 16-field dict
   (two-asset mode).
5. **`mbs_enabled` conditional handling** — implementers MUST
   read `mbs_enabled` at State Initialization only and cache the
   value in `state["mbs_enabled"]`; MUST NOT re-read from
   `config.extras` mid-run (this prevents accidental mode-switch).
6. **Contract-versus-prose conflict resolution** — if the
   mechanism in §4.6.2 or the parameters in §4.7 seem to
   contradict this contract, the contract wins.

#### Input Aggregation Rules

| Aggregate signal        | Derivation                                                                                                        | Rationale                                                            |
|-------------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| `buy_credit_qty`        | `sum(o["size"] for o in orders if o["action_type"]=="buy_credit")`                                                | Total buy-side credit-asset pressure                                 |
| `sell_credit_qty`       | `sum(o["size"] for o in orders if o["action_type"]=="sell_credit")`                                               | Total sell-side credit-asset pressure                                |
| `net_credit_demand`     | `buy_credit_qty − sell_credit_qty`                                                                                | Signed credit demand — drives λ term in the credit-price equation    |
| `borrow_qty`            | `sum(o["size"] for o in orders if o["action_type"]=="borrow")`                                                    | Aggregate new borrowing this round                                   |
| `extend_qty`            | `sum(o["size"] for o in orders if o["action_type"]=="extend_credit")`                                             | Aggregate new credit-line extensions this round                      |
| `repay_qty`             | `sum(o["size"] for o in orders if o["action_type"]=="repay")`                                                     | Aggregate repayments this round                                      |
| `contract_qty`          | `sum(o["size"] for o in orders if o["action_type"]=="contract_credit")`                                           | Aggregate credit-line contractions this round                        |
| `net_borrowing`         | `borrow_qty + extend_qty`                                                                                         | Total flow that increases aggregate leverage — drives η term in L    |
| `net_repayment`         | `repay_qty + contract_qty`                                                                                        | Total flow that decreases aggregate leverage — drives ζ term in L    |
| `buy_mbs_qty`           | `sum(o["size"] for o in orders if o["action_type"]=="buy_mbs")` (only if `mbs_enabled`)                          | Total buy-side MBS pressure                                          |
| `sell_mbs_qty`          | `sum(o["size"] for o in orders if o["action_type"]=="sell_mbs")` (only if `mbs_enabled`)                         | Total sell-side MBS pressure                                         |
| `net_mbs_demand`        | `buy_mbs_qty − sell_mbs_qty` (only if `mbs_enabled`)                                                              | Signed MBS demand — drives λ term in the MBS-price equation          |
| `num_borrowers`         | `len({o["source_id"] for o in orders if o["action_type"]=="borrow"})` OR `len([o ... == "borrow"])` if source_ids absent | Count of distinct borrower participants this round                    |
| `num_lenders`           | `len([o for o in orders if o["action_type"]=="buy_credit"])`                                                       | Count of participants adding to the buy-side credit book              |
| `num_extenders`         | `len([o for o in orders if o["action_type"]=="extend_credit"])`                                                    | Count of participants extending credit lines                          |
| `num_contractors`       | `len([o for o in orders if o["action_type"]=="contract_credit"])`                                                  | Count of participants contracting credit lines                        |

Does NOT use: individual participant capital / balance sheet;
`intensity` field (advisory only in this mechanism — used only for
narrative-driven LLM variants at the participant side); peer-to-
peer topology; participant credit ratings; participant `reasoning`
field.

Completeness rule check: every aggregate above is consumed by at
least one step in §4.6.2 (`net_credit_demand` → step 5;
`net_borrowing`, `net_repayment` → step 3; `net_mbs_demand` →
step 6 [conditional]; `num_*` → step 8 broadcast assembly).

#### Core Coordination Mechanism

1. **READ** `round_num` and `inbound_orders` from `observation`.
   Read `state["credit_price"] = P(t)`,
   `state["fundamental_credit_price"] = F`,
   `state["aggregate_leverage"] = L(t)`,
   `state["minsky_regime"] = regime(t)`, and extras `{λ, γ_base,
   σ, η, ζ, L_spec, L_ponzi, ε_γ, spec_mult, price_floor}`.
   (If `mbs_enabled`: also read `state["mbs_price"] = M(t)` and
   `state["fundamental_mbs_price"] = F_mbs`.) Traces to §4.4
   Kyle, Minsky, Adrian–Shin readings.

2. **COMPUTE** aggregates per §4.6.1: `buy_credit_qty`,
   `sell_credit_qty`, `net_credit_demand`; `borrow_qty`,
   `extend_qty`, `repay_qty`, `contract_qty`, `net_borrowing`,
   `net_repayment`; (if `mbs_enabled`) `buy_mbs_qty`,
   `sell_mbs_qty`, `net_mbs_demand`; counts `num_borrowers`,
   `num_lenders`, `num_extenders`, `num_contractors`.
   (implementation convenience — no theoretical claim beyond
   linearity.)

3. **COMPUTE** the leverage update:
   `L_raw = L(t) + η · net_borrowing − ζ · net_repayment`;
   `L(t+1) = max(L_raw, 0)`. Traces to §4.4 Adrian–Shin 2010 /
   Kiyotaki–Moore 1997. The `max(·, 0)` clamp is the sole
   enforcement of invariant #4 (non-negative leverage).

4. **COMPUTE** the regime transition (deterministic function of
   `L(t+1)`):
   ```
   if   L(t+1) < L_spec_threshold:   regime(t+1) = "hedge"
   elif L(t+1) < L_ponzi_threshold:  regime(t+1) = "speculative"
   else:                             regime(t+1) = "ponzi"
   ```
   Then compute
   ```
   γ(regime(t+1)) = γ_base                   if regime(t+1) = "hedge"
                  = spec_mult · γ_base       if regime(t+1) = "speculative"
                  = ε_γ · γ_base             if regime(t+1) = "ponzi"
   regime_transition_this_round = (regime(t+1) != regime(t))
   ```
   Traces to §4.4 Minsky 1986/1992 block. Note: the same
   `γ(regime(t+1))` gates BOTH the credit-price and (if
   `mbs_enabled`) MBS-price transitions — this shared γ is the
   Gorton–Metrick 2012 [Ref 9] cross-asset co-movement channel.

5. **COMPUTE** the credit-price transition. Draw
   `ε_credit = rng.gauss(0, σ)` from the seeded RNG with seed
   `(base_seed, round, asset_index=0)`. Then:
   ```
   P_raw = P(t) + λ · net_credit_demand
                 + γ(regime(t+1)) · (F − P(t))
                 + ε_credit
   credit_price(t+1) = max(P_raw, price_floor)
   price_change      = credit_price(t+1) − P(t)
   ```
   Traces to §4.4 Kyle 1985 (first term), Brock–Hommes 1998 with
   regime-gated γ (second term), Roll 1984 (third term).

6. **COMPUTE** the MBS-price transition (only if
   `mbs_enabled = true`; otherwise SKIP this step). Draw
   `ε_mbs = rng.gauss(0, σ)` from an independently seeded stream
   `(base_seed, round, asset_index=1)`. Then:
   ```
   MBS_raw = M(t) + λ · net_mbs_demand
                    + γ(regime(t+1)) · (F_mbs − M(t))
                    + ε_mbs
   mbs_price(t+1) = max(MBS_raw, price_floor)
   ```
   Uses the SAME λ, γ(regime(t+1)), σ as credit — the shared
   parameter set is the securitised-banking co-movement
   mechanism. Traces to §4.4 Kyle 1985, Minsky 1986/1992,
   Gorton–Metrick 2012.

7. **WRITE** atomically inside `decide` (see §4.5 lifecycle
   deviation) in this order:
   ```
   state["prev_credit_price"]           = P(t)
   state["credit_price"]                = credit_price(t+1)
   state["price_change"]                = price_change
   state["prev_aggregate_leverage"]     = L(t)
   state["aggregate_leverage"]          = L(t+1)
   state["prev_minsky_regime"]          = regime(t)
   state["minsky_regime"]               = regime(t+1)
   state["regime_transition_this_round"]= regime_transition_this_round
   if mbs_enabled:
       state["prev_mbs_price"]          = M(t)
       state["mbs_price"]               = mbs_price(t+1)
   state["credit_price_history"].append(credit_price(t+1))
   state["leverage_history"].append(L(t+1))
   state["regime_history"].append(regime(t+1))
   if mbs_enabled:
       state["mbs_price_history"].append(mbs_price(t+1))
   ```
   Traces to §4.6.6 invariants #1, #7, #8 (round-boundary time-
   consistency for credit_price, aggregate_leverage, regime).

8. **EMIT** in the return dict from `decide`:
   `{credit_price, prev_credit_price, price_change,
   fundamental_credit_price, aggregate_leverage,
   prev_aggregate_leverage, minsky_regime, prev_minsky_regime,
   regime_transition_this_round, num_borrowers, num_lenders,
   num_extenders, num_contractors, net_credit_demand,
   [mbs_price if mbs_enabled], round}`. `act` then wraps and
   emits. Traces to §4.6.0 Outputs.

#### Broadcast Space

| Aspect                    | Specification                                                                                                                                                                                                                                                                                                                                                                                        |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Broadcast fields          | `credit_price`, `prev_credit_price`, `price_change`, `fundamental_credit_price`, `aggregate_leverage`, `prev_aggregate_leverage`, `minsky_regime`, `prev_minsky_regime`, `regime_transition_this_round`, `num_borrowers`, `num_lenders`, `num_extenders`, `num_contractors`, `net_credit_demand`, `mbs_price` (only if `mbs_enabled = true`), `round` — verbatim §4.6.0 Outputs                             |
| State transition rule     | `P(t+1) = max(P(t) + λ·net_credit_demand + γ(regime(t+1))·(F−P(t)) + ε_credit, price_floor)`; `L(t+1) = max(L(t) + η·net_borrowing − ζ·net_repayment, 0)`; `regime(t+1) = f(L(t+1))`; `γ(regime)` per §4.4; if `mbs_enabled`, `M(t+1) = max(M(t) + λ·net_mbs_demand + γ(regime(t+1))·(F_mbs−M(t)) + ε_mbs, price_floor)`                                                                                    |
| Price/state floor & ceiling | `credit_price` floor: `price_floor` (default `0.01`), no ceiling; `mbs_price` floor: `price_floor`, no ceiling; `aggregate_leverage` floor: `0`, no explicit ceiling (natural cap arises from `net_repayment ≥ 0`); `minsky_regime` support: closed 3-element categorical set                                                                                                                             |
| Freshness policy          | Every-tick; broadcast reflects state committed in the current `decide` (deviation from standard perceive-writes — see §4.5)                                                                                                                                                                                                                                                                            |
| Revision policy           | No — a broadcast MUST NOT be retracted or amended within a round; if a bug is detected, the round is aborted (see Failure Modes)                                                                                                                                                                                                                                                                       |
| State-history retention   | Hot buffer of `custom_state_hot_limit` (default 10000) entries with cold spill to disk via `HistoryBuffer`, one buffer per state variable (`credit_price_history`, `leverage_history`, `regime_history`, and — if `mbs_enabled` — `mbs_price_history`), rooted at `<record_path>/market/{state_var}`                                                                                                       |
| Resource cap              | Unbounded on-disk (history spills); RAM bounded by `4 × hot_limit` slots for two-asset mode, `3 × hot_limit` for single-asset mode                                                                                                                                                                                                                                                                     |
| Termination rule          | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown. No self-termination on regime = "ponzi" — the coordinator continues broadcasting even during a Minsky-moment cascade, because the scenario driver is responsible for defining end-of-simulation conditions                                                                                          |

Environment overlays (capital-adequacy caps, macroprudential
haircut rules, discount-window facilities, deposit insurance)
MUST NOT appear here — they belong to scenario-specific
regulator / policy agents.

#### Mathematical Model

1. **Broadcast outputs**:
   - `credit_price ∈ [price_floor, +∞) ⊂ ℝ`
   - `prev_credit_price ∈ [price_floor, +∞) ⊂ ℝ`
   - `price_change ∈ ℝ`
   - `fundamental_credit_price ∈ ℝ⁺`
   - `aggregate_leverage ∈ [0, +∞) ⊂ ℝ`
   - `prev_aggregate_leverage ∈ [0, +∞) ⊂ ℝ`
   - `minsky_regime ∈ {"hedge", "speculative", "ponzi"}`
   - `prev_minsky_regime ∈ {"hedge", "speculative", "ponzi"}`
   - `regime_transition_this_round ∈ {true, false}`
   - `num_borrowers`, `num_lenders`, `num_extenders`,
     `num_contractors` ∈ ℤ⁺ ∪ {0}
   - `net_credit_demand ∈ ℝ` (in participant `size` units)
   - `mbs_price ∈ [price_floor, +∞) ⊂ ℝ` (only if `mbs_enabled`)
   - `round ∈ ℤ⁺ ∪ {0}`

2. **State transition logic**:
   ```
   NetCreditDemand(t) = BuyCreditQty(t) − SellCreditQty(t)
   NetBorrowing(t)    = BorrowQty(t)    + ExtendQty(t)
   NetRepayment(t)    = RepayQty(t)     + ContractQty(t)
   NetMBSDemand(t)    = BuyMBSQty(t)    − SellMBSQty(t)     (only if mbs_enabled)

   L(t+1)        = max(L(t) + η · NetBorrowing(t)
                              − ζ · NetRepayment(t), 0)

   regime(t+1)   = "hedge"        if L(t+1) < L_spec_threshold
                 = "speculative"  if L_spec_threshold ≤ L(t+1) < L_ponzi_threshold
                 = "ponzi"        if L(t+1) ≥ L_ponzi_threshold

   γ(regime)     = γ_base          if regime = "hedge"
                 = spec_mult · γ_base if regime = "speculative"
                 = ε_γ    · γ_base if regime = "ponzi"

   ε_credit(t)   ~ N(0, σ²)   seeded by (base_seed, t, 0)
   P(t+1)        = max( P(t) + λ · NetCreditDemand(t)
                             + γ(regime(t+1)) · (F − P(t))
                             + ε_credit(t), price_floor )
   price_change(t+1) = P(t+1) − P(t)

   (if mbs_enabled:)
   ε_mbs(t)      ~ N(0, σ²)   seeded by (base_seed, t, 1)
   M(t+1)        = max( M(t) + λ · NetMBSDemand(t)
                             + γ(regime(t+1)) · (F_mbs − M(t))
                             + ε_mbs(t), price_floor )
   ```

3. **State variables**:

   | Variable                          | Type                    | Initial value                                                                                    |
   |-----------------------------------|-------------------------|--------------------------------------------------------------------------------------------------|
   | `credit_price`                    | float                   | `extras["initial_credit_price"]`                                                                 |
   | `prev_credit_price`               | float                   | `extras["initial_credit_price"]`                                                                 |
   | `price_change`                    | float                   | `0.0`                                                                                            |
   | `fundamental_credit_price`        | float                   | `extras["fundamental_credit_price"]`                                                             |
   | `aggregate_leverage`              | float                   | `extras["initial_leverage"]`                                                                     |
   | `prev_aggregate_leverage`         | float                   | `extras["initial_leverage"]`                                                                     |
   | `minsky_regime`                   | str (categorical)       | `f(extras["initial_leverage"])` — deterministic; usually `"hedge"` at a properly seeded start    |
   | `prev_minsky_regime`              | str (categorical)       | same as `minsky_regime` at round 0                                                               |
   | `regime_transition_this_round`    | bool                    | `False`                                                                                          |
   | `credit_price_history`            | `HistoryBuffer`         | empty; folder = `<record>/market/credit_price`; hot_limit = `extras["custom_state_hot_limit"]`   |
   | `leverage_history`                | `HistoryBuffer`         | empty; folder = `<record>/market/leverage`                                                       |
   | `regime_history`                  | `HistoryBuffer`         | empty; folder = `<record>/market/regime`                                                         |
   | `mbs_price` (if `mbs_enabled`)    | float                   | `extras["initial_mbs_price"]`                                                                    |
   | `prev_mbs_price`                  | float                   | `extras["initial_mbs_price"]`                                                                    |
   | `fundamental_mbs_price`           | float                   | `extras["fundamental_mbs_price"]`                                                                |
   | `mbs_price_history`               | `HistoryBuffer`         | empty; folder = `<record>/market/mbs_price`                                                      |
   | `round`                           | int                     | `0`                                                                                              |

4. **State evolution ordering**: all state writes happen inside
   `decide` step 7 (per the §4.5 lifecycle deviation), AFTER the
   full transition computation and BEFORE the payload dict is
   returned. Writes are ordered: leverage update → regime
   transition → credit price → MBS price (if enabled) → history
   buffers → prev_* fields set from pre-update values. `prev_*`
   fields are written from the pre-transition values before the
   corresponding current-round fields are overwritten, so
   invariant #1 (`broadcast[t+1].prev_credit_price ==
   broadcast[t].credit_price`) holds.

5. **Determinism contract**: **stochastic-given-seed**. The
   randomness sources are one Gaussian draw per asset per round
   (`ε_credit` always, `ε_mbs` only if `mbs_enabled`). Both are
   drawn from streams seeded by `(base_seed, round, asset_index)`
   so two runs with the same base seed and identical inbound-
   order sequences produce byte-equal broadcasts. Regime
   transitions and the leverage update are deterministic given
   `L(t)` and the round's aggregates — they contribute no
   additional randomness.

6. **Parameter symbol table**:

   | Symbol                            | Meaning                                                              | Default Value | Source                                                        |
   |-----------------------------------|----------------------------------------------------------------------|---------------|---------------------------------------------------------------|
   | `λ`                               | Price impact per unit of net demand (both credit and MBS)            | `0.01`        | Kyle 1985 [Ref 4]; Chen et al. 2014 [Ref 10]                   |
   | `γ_base`                          | Base mean-reversion rate toward fundamental (hedge-regime γ)         | `0.01`        | Brock & Hommes 1998 [Ref 6]; Fama & French 1988 [Ref 16]       |
   | `spec_mult`                       | Multiplier for γ in the speculative regime                            | `0.5`         | Minsky 1986/1992 [Ref 1, Ref 2] — qualitative anchor            |
   | `ε_γ`                             | Multiplier for γ in the Ponzi regime (near-collapse of anchor)        | `0.05`        | Minsky 1986/1992 [Ref 1, Ref 2]; Shleifer & Vishny 1997 [Ref 15]|
   | `σ`                               | Std dev of Gaussian noise per asset per round                          | `0.1`         | Roll 1984 [Ref 20]                                             |
   | `η`                               | Impact of NetBorrowing on aggregate leverage                          | `0.005`       | Adrian & Shin 2010 [Ref 4, Table 2]                            |
   | `ζ`                               | Impact of NetRepayment on aggregate leverage                          | `0.004`       | Adrian & Shin 2010 [Ref 4, Table 2]                            |
   | `L_spec_threshold`                | Leverage above which the regime is `"speculative"` (or higher)        | `1.5`         | Reinhart & Rogoff 2011 [Ref 7, Table 1] — pre-crisis L/GDP ratio |
   | `L_ponzi_threshold`               | Leverage above which the regime is `"ponzi"`                          | `2.5`         | Reinhart & Rogoff 2011 [Ref 7, Table 1]; Schularick–Taylor 2012 [Ref 13] |
   | `F`                               | Fundamental credit price (anchor)                                     | `100.0`       | Scenario config                                                |
   | `F_mbs`                           | Fundamental MBS price (anchor, only if `mbs_enabled`)                 | `100.0`       | Scenario config                                                |
   | `price_floor`                     | Absolute lower clamp on both credit and MBS prices                    | `0.01`        | Standardised                                                   |
   | `P(0)`                            | Initial credit price                                                  | `100.0`       | Scenario config                                                |
   | `M(0)`                            | Initial MBS price (only if `mbs_enabled`)                             | `100.0`       | Scenario config                                                |
   | `L(0)`                            | Initial aggregate leverage                                            | `1.0`         | Scenario config                                                |
   | `t`                               | Round index                                                           | `0` at start  | Scheduler                                                      |

#### Coordination Properties

- **Time granularity**: round-based (one tick per participant
  action round; typical scenario horizon 20–100 rounds representing
  a business-cycle window).
- **Feedback loop**: **regime-dependent mixed** — in the hedge
  regime the mean-reversion term dominates and feedback is
  negative (stabilising); in the speculative regime feedback is
  weakly negative; in the Ponzi regime the anchor is nearly gone
  and net-credit-demand feedback becomes positive (amplifying).
  Additionally, the leverage-to-regime feedback is a slow
  positive loop: sustained net_borrowing raises L, which
  eventually crosses `L_ponzi_threshold`, which then weakens the
  price anchor, which typically raises net-demand imbalance
  further — the endogenous Minsky-moment mechanism.
- **Information environment**: symmetric — every participant sees
  the identical broadcast. The regime state is public.
- **Stochasticity profile**: one Gaussian ε draw per asset per
  round (1 draw single-asset mode; 2 draws two-asset mode). No
  other randomness inside the coordinator.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants:

| # | Invariant                                                                                                                       | Enforcement                                                                                                        |
|---|---------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| 1 | `broadcast[t+1].prev_credit_price == broadcast[t].credit_price` (byte-equal float)                                              | §4.6.2 step 7 writes `prev_credit_price ← P(t)` before overwriting `credit_price`                                  |
| 2 | Every required field in §4.6.0 Outputs is present and non-null; `mbs_price` present iff `mbs_enabled = true`                    | `decide` assertion + conditional inclusion at payload assembly (step 8)                                            |
| 3 | `credit_price ≥ price_floor` and (if `mbs_enabled`) `mbs_price ≥ price_floor` in every broadcast                                | §4.6.2 step 5 / step 6 clamp                                                                                       |
| 4 | `aggregate_leverage ≥ 0` in every broadcast                                                                                     | §4.6.2 step 3 `max(·, 0)` clamp                                                                                    |
| 5 | `minsky_regime ∈ {"hedge","speculative","ponzi"}` and `prev_minsky_regime ∈ {"hedge","speculative","ponzi"}`                    | §4.6.2 step 4 deterministic branch; three-branch coverage is exhaustive                                            |
| 6 | `broadcast[t+1].round == broadcast[t].round + 1`                                                                                | Set from `observation.round` in `perceive` step 1                                                                  |
| 7 | `broadcast[t+1].prev_aggregate_leverage == broadcast[t].aggregate_leverage` (byte-equal float)                                  | §4.6.2 step 7 writes `prev_aggregate_leverage ← L(t)` before overwriting `aggregate_leverage`                       |
| 8 | `broadcast[t+1].prev_minsky_regime == broadcast[t].minsky_regime` (string equality)                                             | §4.6.2 step 7 writes `prev_minsky_regime ← regime(t)` before overwriting `minsky_regime`                            |
| 9 | Regime is a deterministic function of `L(t+1)`: identical `L(t+1)` values ALWAYS yield identical `regime(t+1)`                    | §4.6.2 step 4 branch has no stochasticity                                                                          |
| 10| γ ordering: `γ("hedge") ≥ γ("speculative") ≥ γ("ponzi") ≥ 0` (monotonically non-increasing along hedge → speculative → Ponzi)   | Enforced by config validation at State Initialization: assert `1 ≥ spec_mult ≥ ε_γ ≥ 0`                             |
| 11| Two runs with identical `base_seed` and identical inbound-order sequence produce byte-equal broadcasts (all fields, all rounds) | Seeded RNG per `(base_seed, round, asset_index)`; regime and leverage updates are deterministic                     |
| 12| `regime_transition_this_round == (minsky_regime != prev_minsky_regime)` (exactly)                                                | §4.6.2 step 4 explicit comparison                                                                                  |

Domain-Specific Invariants:

- **Non-negativity**: `credit_price ≥ 0`, `mbs_price ≥ 0`
  (implied by `price_floor > 0`), `aggregate_leverage ≥ 0` —
  invariants #3, #4.
- **Regime support**: the categorical domain of `minsky_regime`
  is exactly `{"hedge", "speculative", "ponzi"}` (3 values) and
  MUST NOT be extended without a new profile version (invariant
  #5).
- **Regime determinism**: identical aggregate leverage produces
  identical regime — no hysteresis, no stochastic transitions
  (invariant #9). The Minsky cycle IS an endogenous feedback
  loop, but the L→regime map is a pure function.
- **γ monotonicity along hedge → speculative → Ponzi**:
  `γ_base ≥ spec_mult · γ_base ≥ ε_γ · γ_base ≥ 0` (invariant
  #10). Violations correspond to Ponzi financing having a
  *stronger* anchor than hedge — this would be a semantic
  inversion of the Minsky hypothesis.
- **No cross-round leakage**: each of `credit_price_history`,
  `leverage_history`, `regime_history`, and (if `mbs_enabled`)
  `mbs_price_history` grows by exactly 1 entry per round.
- **Conservation**: not applicable — this coordinator is
  price/state-forming only, not authoritative for participant
  cash / positions.

Failure Modes:

| Condition                                                                            | Coordinator behaviour                                                          | Broadcast effect                                                                                                    |
|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Zero inbound orders                                                                  | Continue; all aggregates = 0; `L(t+1) = L(t)`, `regime(t+1) = regime(t)`       | Broadcast reflects pure mean-reversion + noise on price; leverage and regime unchanged                              |
| All orders same side (e.g. all `buy_credit`)                                         | Continue                                                                       | Large positive `net_credit_demand`; strong upward price move (magnitude depends on regime)                          |
| Order missing `action_type`, `size < 0`, or `intensity` outside `[0, 1]`             | Log warning at WARN; skip that order; continue with remaining                  | Aggregates exclude the malformed order                                                                              |
| Unknown `action_type` (e.g. `"buy_stock"` in a credit market)                        | Silently ignore that order (do not raise — future action-types may be added)   | Aggregates exclude that order                                                                                       |
| MBS order (`buy_mbs` / `sell_mbs`) received when `mbs_enabled = false`               | Log warning at WARN; skip that order; continue                                 | MBS aggregates remain 0; no `mbs_price` field emitted                                                               |
| Required extras key missing                                                          | Raise `KeyError` from `perceive` (or from `decide` for MBS-conditional extras) | No broadcast; simulation halts                                                                                      |
| Optional extras key missing                                                          | Use documented default (`price_floor = 0.01`, `spec_mult = 0.5`, `ε_γ = 0.05`)  | Normal broadcast                                                                                                    |
| `L(t+1)` computes to NaN / Inf                                                       | Raise `ValueError` from `decide`                                               | No broadcast; simulation halts (implementation defect)                                                              |
| `credit_price(t+1)` or `mbs_price(t+1)` computes to NaN / Inf                        | Raise `ValueError` from `decide`                                               | No broadcast; simulation halts (implementation defect)                                                              |
| `L(t+1) < 0` before clamping (e.g. repayment > η/ζ * borrowing surplus)              | Clamp to `0` via `max(·, 0)`; log warning at DEBUG                             | Normal broadcast with `aggregate_leverage = 0` (fully deleveraged)                                                  |
| Regime-transition-thrashing (`L(t)` oscillates across `L_spec_threshold` every round)| Continue emitting broadcasts; log an INFO-level "thrashing detected" if ≥ 3 transitions in 5 rounds | Broadcast is correct; participants are responsible for smoothing on their side                                     |
| `P_raw < price_floor` (crash below the clamp)                                         | Clamp to `price_floor`; log warning at DEBUG                                   | Broadcast reflects clamped price; participants observe a floor event                                                |
| `regime_transition_this_round = true` but no aggregate change (impossible under §4.6.2 step 4) | This is a contradiction; raise `AssertionError` from `decide`         | No broadcast; simulation halts (implementation defect indicating a broken deterministic step 4)                     |
| Scenario driver mutates `L_spec_threshold` or `L_ponzi_threshold` mid-run             | Next `decide` reads new value; log the change at INFO                          | Next broadcast reflects new thresholds — regime may transition immediately if new threshold falls below current L    |
| Scenario driver mutates `fundamental_credit_price` (or `fundamental_mbs_price`)       | Next `perceive` reads new value; log the change at INFO                        | Next broadcast reflects new fundamental                                                                             |
| `HistoryBuffer` disk write fails                                                     | Raise from `decide`; do NOT emit stale broadcast                               | No broadcast; simulation halts                                                                                      |

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter                    | Type  | Default   | Valid Range     | Sensitivity | Description                                                     | Impact                                                                          | Source                                             |
|------------------------------|-------|-----------|-----------------|-------------|-----------------------------------------------------------------|---------------------------------------------------------------------------------|----------------------------------------------------|
| `initial_credit_price`       | float | `100.0`   | `> 0`           | medium      | Round-0 credit-price seed `P(0)`                                | Higher → higher initial trajectory level                                        | Scenario config (Kyle 1985 [Ref 4])                 |
| `fundamental_credit_price`   | float | `100.0`   | `> 0`           | high        | Anchor `F` for credit-price mean-reversion                       | Higher → mean-reversion target shifts up                                        | Scenario config (Brock & Hommes 1998 [Ref 6])       |
| `initial_leverage`           | float | `1.0`     | `≥ 0`           | high        | Round-0 aggregate leverage `L(0)`                                | Higher → closer to `L_spec_threshold` at start → earlier speculative onset      | Scenario config (Adrian & Shin 2010 [Ref 4])        |
| `initial_mbs_price` (cond.)  | float | `100.0`   | `> 0`           | medium      | Round-0 MBS-price seed `M(0)` (only if `mbs_enabled = true`)      | Higher → higher initial MBS trajectory                                          | Scenario config (Gorton & Metrick 2012 [Ref 9])     |
| `fundamental_mbs_price` (cond.) | float | `100.0` | `> 0`           | high        | Anchor `F_mbs` for MBS-price mean-reversion                       | Higher → MBS mean-reversion target shifts up                                    | Scenario config (Gorton & Metrick 2012 [Ref 9])     |

#### B. Mechanism Coefficients

| Parameter                       | Type  | Default   | Valid Range   | Sensitivity | Description                                                                                          | Impact                                                                                                | Source                                                     |
|---------------------------------|-------|-----------|---------------|-------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| `price_impact`                  | float | `0.01`    | `≥ 0`         | high        | λ — price move per unit of net demand (applied to both credit and MBS in two-asset mode)              | Higher → 2× more responsive to demand imbalance                                                       | Kyle 1985 [Ref 4]; Chen et al. 2014 [Ref 10]                |
| `mean_reversion_pull_base`      | float | `0.01`    | `[0, 1]`      | high        | γ_base — pull rate toward fundamental in the hedge regime                                            | Higher → faster return to F in hedge / speculative regimes                                            | Brock & Hommes 1998 [Ref 6]; Fama & French 1988 [Ref 16]    |
| `speculative_gamma_multiplier`  | float | `0.5`     | `[0, 1]`      | high        | Multiplier that scales γ_base when `regime = "speculative"`                                          | Higher → speculative regime is more like hedge; lower → speculative regime is more like Ponzi         | Minsky 1986/1992 [Ref 1, Ref 2]; qualitative anchor         |
| `ponzi_gamma_multiplier`        | float | `0.05`    | `[0, 0.5]`    | high        | ε_γ — multiplier that scales γ_base when `regime = "ponzi"` (the "lost anchor")                        | Higher → Ponzi still partially anchored (weaker Minsky moment); lower → sharper crisis cascade         | Minsky 1986/1992 [Ref 1, Ref 2]; Shleifer & Vishny 1997 [Ref 15] |
| `noise_std`                     | float | `0.1`     | `≥ 0`         | medium      | σ — Gaussian noise std dev per asset per round                                                        | Higher → more idiosyncratic price oscillation on both assets                                          | Roll 1984 [Ref 20, Table I]                                 |
| `borrowing_impact_on_leverage`  | float | `0.005`   | `≥ 0`         | high        | η — impact of NetBorrowing on `L`                                                                     | Higher → leverage builds faster during booms → earlier Minsky moment                                  | Adrian & Shin 2010 [Ref 4, Table 2]                         |
| `repayment_impact_on_leverage`  | float | `0.004`   | `≥ 0`         | high        | ζ — impact of NetRepayment on `L`                                                                     | Higher → leverage falls faster during contractions → faster regime downshift                          | Adrian & Shin 2010 [Ref 4, Table 2]                         |
| `leverage_speculative_threshold`| float | `1.5`     | `> 0`         | high        | `L_spec_threshold` — L above which regime is `"speculative"` (or higher)                              | Higher → speculative regime harder to reach → longer stable phase                                     | Reinhart & Rogoff 2011 [Ref 7, Table 1]                     |
| `leverage_ponzi_threshold`      | float | `2.5`     | `> L_spec_threshold` | high | `L_ponzi_threshold` — L above which regime is `"ponzi"`                                                | Higher → Ponzi regime harder to reach → later/less-severe Minsky moment                              | Reinhart & Rogoff 2011 [Ref 7]; Schularick & Taylor 2012 [Ref 13] |

#### C. Structural / Boundary Parameters

| Parameter       | Type  | Default   | Valid Range   | Sensitivity | Description                                                    | Impact                                                                     | Source        |
|-----------------|-------|-----------|---------------|-------------|----------------------------------------------------------------|----------------------------------------------------------------------------|---------------|
| `price_floor`   | float | `0.01`    | `≥ 0`         | low         | Absolute lower clamp on both credit and MBS prices              | Higher → earlier clamp during crash                                        | Standardised  |
| `mbs_enabled`   | bool  | `false`   | `{true, false}` | high      | Whether the coordinator operates in single-asset (credit-only) or two-asset (credit + MBS) mode | Toggles the `mbs_price` output field and MBS-order acceptance; single-asset mode reduces broadcast size | Scenario config (GFC2008: `true`; CreditCycle: `false`) |

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range   | Sensitivity | Description                                                       | Impact                                     | Source        |
|--------------------------|------|------------|---------------|-------------|-------------------------------------------------------------------|--------------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty     | low         | Root directory for HistoryBuffer spills                            | Higher size → more disk footprint          | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`         | low         | HistoryBuffer hot-tier size (entries)                             | Higher → more RAM, less disk I/O           | Standardised  |

## Worked Numerical Examples

All examples use the §4.7 Defaults unless overridden:
`λ = 0.01`, `γ_base = 0.01`, `spec_mult = 0.5`, `ε_γ = 0.05`,
`σ = 0.1`, `η = 0.005`, `ζ = 0.004`, `L_spec = 1.5`,
`L_ponzi = 2.5`, `F = 100.0`, `initial_credit_price = 100.0`,
`initial_leverage = 1.0`, `price_floor = 0.01`. Unless
otherwise stated, `mbs_enabled = false`.

### Case 1 — Stable hedge regime (moderate net-buy pressure, regime unchanged)

System state (round `t = 3`):

- `P(t) = 101.10`, `F = 100.00`, `L(t) = 1.20`, `regime(t) =
  "hedge"` (since `1.20 < 1.5`).
- Inbound orders: 5 `buy_credit` totalling 30, 3 `sell_credit`
  totalling 12; 4 `borrow` totalling 20, 2 `repay` totalling 15;
  1 `extend_credit` of 5; 1 `contract_credit` of 3.

Aggregate computation (§4.6.1):

- `buy_credit_qty = 30`, `sell_credit_qty = 12`;
  `net_credit_demand = 18`.
- `borrow_qty = 20`, `extend_qty = 5`, `net_borrowing = 25`.
- `repay_qty = 15`, `contract_qty = 3`, `net_repayment = 18`.
- Counts: `num_borrowers = 4`, `num_lenders = 5`,
  `num_extenders = 1`, `num_contractors = 1`.

Transition (§4.6.2 steps 3–5):

- `L_raw = 1.20 + 0.005 · 25 − 0.004 · 18 = 1.20 + 0.125 − 0.072
  = 1.253`; `L(t+1) = max(1.253, 0) = 1.253`.
- Regime: `1.253 < 1.5` → `regime(t+1) = "hedge"`; γ =
  `0.01`; `regime_transition_this_round = false` (same as
  `hedge`).
- `ε_credit` draw `= +0.03`.
- Demand term: `0.01 · 18 = +0.18`.
- Reversion term: `0.01 · (100.00 − 101.10) = −0.011`.
- `P_raw = 101.10 + 0.18 − 0.011 + 0.03 = 101.299`.
- Floor clamp: no effect (still ≫ 0.01).
- `credit_price(t+1) = 101.299`; `price_change = +0.199`.

Broadcast (single-asset mode):

```json
{"credit_price": 101.299, "prev_credit_price": 101.10,
 "price_change": 0.199, "fundamental_credit_price": 100.00,
 "aggregate_leverage": 1.253, "prev_aggregate_leverage": 1.20,
 "minsky_regime": "hedge", "prev_minsky_regime": "hedge",
 "regime_transition_this_round": false,
 "num_borrowers": 4, "num_lenders": 5,
 "num_extenders": 1, "num_contractors": 1,
 "net_credit_demand": 18.0, "round": 3}
```

Invariant checks: #1 `prev_credit_price = 101.10 = broadcast[t].credit_price` ✓
(assuming broadcast[t] emitted 101.10); #4 `1.253 ≥ 0` ✓;
#5 both regimes in support ✓; #10 γ ordering trivially satisfied
(only hedge γ used).

### Case 2 — Speculative build-up (leverage crosses `L_spec_threshold`, regime transitions hedge → speculative)

System state (round `t = 12`, following an extended boom):

- `P(t) = 108.40`, `F = 100.00`, `L(t) = 1.48`, `regime(t) =
  "hedge"` (`1.48 < 1.5`).
- Inbound orders: heavy borrowing pressure — 6 `borrow` totalling
  90, 4 `extend_credit` totalling 40, 0 `repay`, 1
  `contract_credit` of 5; 8 `buy_credit` totalling 55, 2
  `sell_credit` totalling 10.

Aggregate:

- `net_credit_demand = 45`.
- `net_borrowing = 90 + 40 = 130`; `net_repayment = 0 + 5 = 5`.
- Counts: `num_borrowers = 6`, `num_lenders = 8`,
  `num_extenders = 4`, `num_contractors = 1`.

Transition:

- `L_raw = 1.48 + 0.005 · 130 − 0.004 · 5 = 1.48 + 0.65 − 0.02
  = 2.11`; `L(t+1) = 2.11`.
- Regime: `1.5 ≤ 2.11 < 2.5` → `regime(t+1) = "speculative"`;
  γ = `0.5 · 0.01 = 0.005`;
  `regime_transition_this_round = true` (hedge → speculative).
- `ε_credit` draw `= +0.04`.
- Demand term: `0.01 · 45 = +0.45`.
- Reversion term: `0.005 · (100.00 − 108.40) = −0.042`. (γ has
  been halved because the regime just transitioned to
  speculative; the anchor is weakening.)
- `P_raw = 108.40 + 0.45 − 0.042 + 0.04 = 108.848`.
- Floor clamp: no effect.
- `credit_price(t+1) = 108.848`; `price_change = +0.448`.

Broadcast:

```json
{"credit_price": 108.848, "prev_credit_price": 108.40,
 "price_change": 0.448, "fundamental_credit_price": 100.00,
 "aggregate_leverage": 2.11, "prev_aggregate_leverage": 1.48,
 "minsky_regime": "speculative", "prev_minsky_regime": "hedge",
 "regime_transition_this_round": true,
 "num_borrowers": 6, "num_lenders": 8,
 "num_extenders": 4, "num_contractors": 1,
 "net_credit_demand": 45.0, "round": 12}
```

Observation: because γ was halved, the reversion pull (`−0.042`)
is much weaker than it would have been under `γ_base` (`−0.084`).
The price now drifts further from `F` than it would have in the
hedge regime, illustrating the endogenous instability build-up.
Invariant #8 `prev_minsky_regime = "hedge" = broadcast[t].regime` ✓;
invariant #12 `regime_transition_this_round = true` matches the
regime string inequality ✓.

### Case 3 — Minsky moment cascade (Ponzi regime with a small negative shock, two-asset GFC2008 mode)

System state (round `t = 25`, following a Ponzi build-up).
**Override**: `mbs_enabled = true`, `M(t) = 105.20`,
`F_mbs = 100.0`.

- `P(t) = 118.00`, `F = 100.00`, `L(t) = 2.58`, `regime(t) =
  "ponzi"` (`2.58 ≥ 2.5`).
- Inbound orders: forced-selling cascade begins — 2 `buy_credit`
  totalling 8, 9 `sell_credit` totalling 120; 1 `borrow` of 5,
  7 `repay` totalling 95, 0 `extend_credit`, 5
  `contract_credit` totalling 60; on MBS side, 1 `buy_mbs` of
  10, 6 `sell_mbs` totalling 85.

Aggregate:

- `net_credit_demand = 8 − 120 = −112`.
- `net_borrowing = 5 + 0 = 5`; `net_repayment = 95 + 60 = 155`.
- `net_mbs_demand = 10 − 85 = −75`.
- Counts: `num_borrowers = 1`, `num_lenders = 2`,
  `num_extenders = 0`, `num_contractors = 5`.

Transition:

- `L_raw = 2.58 + 0.005 · 5 − 0.004 · 155 = 2.58 + 0.025 − 0.620
  = 1.985`; `L(t+1) = 1.985`.
- Regime: `1.5 ≤ 1.985 < 2.5` → `regime(t+1) = "speculative"`;
  γ = `0.5 · 0.01 = 0.005`; `regime_transition_this_round =
  true` (ponzi → speculative — regime cascade in the
  contraction direction).
- Credit branch: `ε_credit` draw `= −0.05`.
- Demand term: `0.01 · (−112) = −1.12`.
- Reversion term (using new γ 0.005, since regime transitions
  are applied same-round per §4.6.2 step 4):
  `0.005 · (100.00 − 118.00) = −0.09`.
- `P_raw = 118.00 − 1.12 − 0.09 − 0.05 = 116.74`.
- `credit_price(t+1) = 116.74`; `price_change = −1.26`.
- MBS branch: `ε_mbs` draw (independent stream) `= −0.02`.
- Demand term: `0.01 · (−75) = −0.75`.
- Reversion term: `0.005 · (100.00 − 105.20) = −0.026`.
- `MBS_raw = 105.20 − 0.75 − 0.026 − 0.02 = 104.404`;
  `mbs_price(t+1) = 104.404`.

Broadcast (two-asset mode — includes `mbs_price`):

```json
{"credit_price": 116.74, "prev_credit_price": 118.00,
 "price_change": -1.26, "fundamental_credit_price": 100.00,
 "aggregate_leverage": 1.985, "prev_aggregate_leverage": 2.58,
 "minsky_regime": "speculative", "prev_minsky_regime": "ponzi",
 "regime_transition_this_round": true,
 "num_borrowers": 1, "num_lenders": 2,
 "num_extenders": 0, "num_contractors": 5,
 "net_credit_demand": -112.0, "mbs_price": 104.404,
 "round": 25}
```

Observation: this round captures the initial phase of the Minsky
moment — mass repayment / contraction pulls `L` below
`L_ponzi_threshold`, the regime downshifts to speculative, and
γ jumps *up* from `0.05·γ_base` to `0.5·γ_base`. The anchor is
partially restored, but the immediate price collapse is driven
primarily by the very large negative `net_credit_demand` under
still-modest γ. If the sell-off continues in subsequent rounds,
`L` will fall further, γ will fully recover to `γ_base` on the
hedge-transition, and the mean-reversion term will begin to pull
credit_price back toward `F = 100`. Note also: the MBS price
tracks credit qualitatively (both fall, both governed by the same
γ) — the shared-γ channel is the Gorton–Metrick 2012 [Ref 9]
securitised-banking co-movement mechanism in action.

Invariants: #4 `L = 1.985 ≥ 0` ✓; #5 both regimes in support ✓;
#7 `prev_aggregate_leverage = 2.58 = broadcast[t].aggregate_leverage` ✓;
#8 `prev_minsky_regime = "ponzi" = broadcast[t].minsky_regime` ✓;
#9 regime deterministic in L ✓; #10 γ ordering respected across
the three regime settings (`0.01 ≥ 0.005 ≥ 0.0005 ≥ 0`) ✓.

### Edge Case — Leverage exactly at the Ponzi threshold

System state (round `t = 20`):

- `P(t) = 112.50`, `F = 100.00`, `L(t) = 2.4990`, `regime(t) =
  "speculative"`.
- Inbound orders: 0 `buy_credit`, 0 `sell_credit`, 1 `borrow` of
  2, 0 others.

Aggregate:

- `net_credit_demand = 0`, `net_borrowing = 2`,
  `net_repayment = 0`, all counts small.

Transition:

- `L_raw = 2.4990 + 0.005 · 2 − 0 = 2.5090`; `L(t+1) = 2.5090`.
- Regime branch: `L(t+1) = 2.5090 ≥ L_ponzi_threshold = 2.5` →
  `regime(t+1) = "ponzi"`. (The branch is closed on the right:
  the `≥` in the `"ponzi"` clause means the exact-boundary case
  belongs to the Ponzi regime, NOT the speculative regime. This
  is a design decision — the profile explicitly resolves the
  boundary in the direction of instability, so that a leverage
  tick that touches the threshold triggers the Minsky moment
  rather than being absorbed silently.) γ = `0.05 · 0.01 =
  0.0005`; `regime_transition_this_round = true`.
- `ε_credit` draw `= +0.02`.
- Demand term: `0`.
- Reversion term: `0.0005 · (100.00 − 112.50) = −0.00625`.
- `P_raw = 112.50 + 0 − 0.00625 + 0.02 = 112.514`;
  `credit_price(t+1) = 112.514`; `price_change = +0.014`.

Broadcast (single-asset mode):

```json
{"credit_price": 112.514, "prev_credit_price": 112.50,
 "price_change": 0.014, "fundamental_credit_price": 100.00,
 "aggregate_leverage": 2.509,
 "prev_aggregate_leverage": 2.499,
 "minsky_regime": "ponzi", "prev_minsky_regime": "speculative",
 "regime_transition_this_round": true,
 "num_borrowers": 1, "num_lenders": 0,
 "num_extenders": 0, "num_contractors": 0,
 "net_credit_demand": 0.0, "round": 20}
```

Observation: this edge case exercises the exact-threshold branch.
Two implementers of §4.6.2 step 4 who disagree about whether the
right endpoint is `<` or `≤` would produce DIFFERENT regime
broadcasts here — the profile is unambiguous: the Ponzi clause
uses `≥`, so `L = 2.5090 ≥ 2.5` yields Ponzi. The anchor pull
has now collapsed to `0.0005`; even though the price is 12.5%
above fundamental, the reversion term is nearly nil, and the
noise draw alone determines this round's direction. This is the
classical "market has lost its anchor" state — a small positive
noise draw can now push price further from `F`, and subsequent
Ponzi-regime rounds are structurally vulnerable to any sell-side
shock (as demonstrated in Case 3).

Invariants: #5 support respected (regime transitioned from
`speculative` to `ponzi`, both in support) ✓; #9 determinism —
the exact `L = 2.5090` yields `"ponzi"` deterministically ✓;
#12 `regime_transition_this_round = true` matches the regime
inequality ✓.

## Coordinator Verification and Calibration

**Calibration data sources**:

- `price_impact` (λ) ← Kyle 1985 [Ref 4]; Chen et al. 2014
  [Ref 10, Table III]. Simulation-unit-adjusted range:
  `[0.001, 0.05]`.
- `mean_reversion_pull_base` (γ_base) ← Brock & Hommes 1998
  [Ref 6, §4]; Fama & French 1988 [Ref 16] half-life
  reinterpretation. Range: `[0.005, 0.05]`.
- `speculative_gamma_multiplier` (spec_mult) ← qualitative from
  Minsky 1986/1992 [Ref 1, Ref 2] — speculative firms roll
  principal but still service interest, i.e. the anchor is
  weakened but not lost. Reasonable range: `[0.3, 0.7]`.
- `ponzi_gamma_multiplier` (ε_γ) ← Minsky 1986/1992 [Ref 1, Ref 2]
  + Shleifer & Vishny 1997 [Ref 15] limits-to-arbitrage. Ponzi
  units cannot even service interest, so fundamentalists cannot
  profitably counter them. Reasonable range: `[0.01, 0.15]`.
- `noise_std` (σ) ← Roll 1984 [Ref 20, Table I]. Range:
  `[0.01, 0.5]`.
- `borrowing_impact_on_leverage` (η) and
  `repayment_impact_on_leverage` (ζ) ← Adrian & Shin 2010
  [Ref 4, Table 2] procyclical broker-dealer leverage
  elasticities; typical `η/ζ ratio ≈ 1.2–1.5` during the
  2001–2007 boom half-cycle.
- `leverage_speculative_threshold` (`L_spec_threshold`) and
  `leverage_ponzi_threshold` (`L_ponzi_threshold`) ← Reinhart &
  Rogoff 2011 [Ref 7, Table 1] pre-crisis credit-to-baseline
  ratios; Schularick & Taylor 2012 [Ref 13, §3] top-decile
  credit-growth episodes. Suggested calibration: `L_spec = 1.5 ·
  L(0)`, `L_ponzi = 2.5 · L(0)`.

**Expected coordinator behaviour** (given defaults):

- Given `net_credit_demand > 0`, `net_borrowing = net_repayment
  = 0`, and `regime = "hedge"`, the coordinator MUST push
  `credit_price` up and leave `aggregate_leverage` and
  `minsky_regime` unchanged.
- Given `net_credit_demand = 0`, `net_borrowing > 0`,
  `net_repayment = 0`, the coordinator MUST leave
  `credit_price` unchanged apart from mean-reversion + noise,
  and MUST strictly increase `aggregate_leverage`.
- Given `net_borrowing = 0`, `net_repayment > 0`, and
  `L(t) > 0`, the coordinator MUST strictly decrease
  `aggregate_leverage` (until the `max(·, 0)` clamp binds).
- Given `L(t+1) = L(t) = 1.0` and no exogenous threshold
  mutation, the coordinator MUST emit `minsky_regime =
  prev_minsky_regime = "hedge"` and `regime_transition_this_round
  = false`.
- Given identical `base_seed`, identical inbound-order sequence,
  and identical `mbs_enabled`, the coordinator MUST produce
  byte-equal broadcasts across two independent runs (all rounds,
  all fields).
- Given a scenario driver that raises `L_ponzi_threshold` from
  `2.5` to `3.0` between rounds while `L(t) = 2.6`, the next
  broadcast MUST downshift `minsky_regime` from `"ponzi"` back
  to `"speculative"` — the regime is a pure function of the
  current threshold values.
- Given `mbs_enabled = false`, the broadcast MUST NOT contain
  the `mbs_price` key.
- Given `mbs_enabled = true`, the broadcast MUST contain
  `mbs_price` in every round.

**Sanity bounds** (red flags for a broken implementation):

- IF `broadcast[t+1].prev_credit_price != broadcast[t].credit_price`
  THEN the state-write ordering is broken (invariant #1).
- IF `broadcast[t+1].prev_aggregate_leverage !=
  broadcast[t].aggregate_leverage` THEN the leverage-prev write
  is broken (invariant #7).
- IF `broadcast[t+1].prev_minsky_regime != broadcast[t].minsky_regime`
  THEN the regime-prev write is broken (invariant #8).
- IF any broadcast reports `minsky_regime ∉ {"hedge",
  "speculative", "ponzi"}` THEN the regime domain is broken
  (invariant #5).
- IF `aggregate_leverage < 0` in any broadcast THEN the
  `max(·, 0)` clamp is broken (invariant #4).
- IF `credit_price < price_floor` in any broadcast THEN the
  price clamp is broken (invariant #3).
- IF two consecutive broadcasts have identical `L` but
  different `minsky_regime` (without threshold mutation) THEN
  the regime function has non-determinism (invariant #9).
- IF `γ("ponzi") > γ("hedge")` — i.e. the anchor pull is
  *stronger* in Ponzi than in hedge — THEN the γ ordering is
  inverted (invariant #10).
- IF `regime_transition_this_round = true` while
  `minsky_regime == prev_minsky_regime` THEN the transition-
  flag logic is broken (invariant #12).
- IF `mbs_enabled = true` and any broadcast omits `mbs_price`
  THEN the conditional-field logic is broken (invariant #2).
- IF `mbs_enabled = false` and any broadcast includes
  `mbs_price` THEN the forbidden-field discipline is broken
  (§4.6.0 Content Constraints).
- IF two runs with identical `base_seed` and identical
  inbound-order sequence produce different broadcasts THEN the
  RNG seeding is broken (invariant #11).

### Ablation Hooks

| Ablation name              | Setting                                                                 | Hypothesis tested                                                             | Expected direction                                                                | Metric                                                     |
|----------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|------------------------------------------------------------|
| `no-regime-gate`           | `spec_mult = 1.0`, `ε_γ = 1.0` (γ constant across regimes)             | Removes the Minsky endogenous instability mechanism                            | No Ponzi-price-blow-up; trajectory stays bounded                                   | `max_over_rounds(|credit_price − F|)` shrinks              |
| `hard-anchor`              | `γ_base = 0.05`                                                          | Stronger anchor in all regimes                                                 | Faster mean-reversion; smaller peak-to-trough swing                                | Peak-trough range on a Case-3-style shock                  |
| `no-mean-reversion`        | `γ_base = 0`                                                             | Removes the anchor entirely                                                    | Trajectory becomes path-dependent; regime state still evolves                      | `Var(credit_price)` over 100 rounds                        |
| `zero-price-impact`        | `λ = 0`                                                                  | Orders no longer move price; leverage still evolves                            | Credit-price → fundamental; leverage cycle continues on borrowing/repayment flows | `mean(|credit_price − F|)` → near 0                        |
| `high-noise`               | `σ *= 10`                                                                | Overwhelms deterministic signal                                                | Random-walk-like broadcast series                                                 | `Autocorr(price_diff, lag=1)` → 0                          |
| `fast-leverage-buildup`    | `η = 0.05` (10×)                                                         | Booms accelerate leverage buildup                                              | Earlier speculative and Ponzi transitions                                          | Round at which `regime = "ponzi"` first                    |
| `low-ponzi-threshold`      | `L_ponzi_threshold = 1.75`                                               | Regime cascade triggers earlier                                                | Minsky moment appears in earlier rounds                                            | Round of first `"ponzi"` broadcast                          |
| `symmetric-η-ζ`            | `η = ζ`                                                                  | Leverage builds and unwinds at the same rate                                    | Cycle symmetric; no persistent Ponzi if borrowing/repayment balanced               | Mean `L` over 200 rounds                                    |
| `mbs-only-shock`           | `mbs_enabled = true`; scenario driver drops `F_mbs` by 30%                | Test MBS-vs-credit propagation via shared γ(regime) channel                    | Both prices should co-move given a Ponzi regime                                    | Correlation of `Δmbs_price` and `Δcredit_price` during shock |
| `ponzi-collapse-severity`  | `ε_γ = 0.005` (10× weaker Ponzi anchor)                                  | Extreme Minsky moment                                                          | Larger price collapse magnitude when regime = "ponzi"                              | Max `|credit_price − F|` during Ponzi                       |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                                                                                                                                     | Notes                                                                                                                    |
|----|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| 1  | Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale University Press. ISBN: 978-0300041521.                                                                                                                                                                                        | Financial Instability Hypothesis; origin of hedge/speculative/Ponzi regime taxonomy                                       |
| 2  | Minsky, H. P. (1992). The Financial Instability Hypothesis. *Levy Economics Institute Working Paper No. 74*. URL: https://www.levyinstitute.org/pubs/wp74.pdf                                                                                                                                | Compact statement of the regime-transition mechanism used in this coordinator                                            |
| 3  | Geanakoplos, J. (2010). The Leverage Cycle. *NBER Macroeconomics Annual*, 24(1), 1–65. DOI: 10.1086/648285                                                                                                                                                                                    | Collateral-haircut-indexed leverage cycles; alternative regime formulation                                                |
| 4  | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. DOI: 10.1016/j.jfi.2008.12.002                                                                                                                                              | Procyclical intermediary leverage; empirical basis for η, ζ (also cites Kyle 1985 replica for λ)                          |
| 5  | Kiyotaki, N., & Moore, J. (1997). Credit Cycles. *Journal of Political Economy*, 105(2), 211–248. DOI: 10.1086/262072                                                                                                                                                                        | Collateral-constrained leverage cycle; theoretical grounding for L evolution                                              |
| 6  | Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274. DOI: 10.1016/S0165-1889(98)00011-6                                                                            | Fundamentalist-weighted mean-reversion γ; basis for regime-gated γ variant                                                |
| 7  | Reinhart, C. M., & Rogoff, K. S. (2011). From Financial Crash to Debt Crisis. *American Economic Review*, 101(5), 1676–1706. DOI: 10.1257/aer.101.5.1676                                                                                                                                     | Cross-country credit-boom empirics; calibration source for L_spec_threshold, L_ponzi_threshold                            |
| 8  | Brunnermeier, M. K. (2009). Deciphering the Liquidity and Credit Crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. DOI: 10.1257/jep.23.1.77                                                                                                                               | GFC2008 mechanics; margin-call spiral and loss-spiral feedback                                                            |
| 9  | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. DOI: 10.1016/j.jfineco.2011.03.016                                                                                                                             | Shared-shock propagation from underlying credit market to MBS; basis for two-asset mode with shared γ(regime)             |
| 10 | Chen, Z., Lookman, A., Schürhoff, N., & Seppi, D. (2014). Rating-Based Investment Practices and Bond Market Segmentation. *Review of Asset Pricing Studies*, 4(2), 162–205. DOI: 10.1093/rapstu/rau003                                                                                       | Credit-market price-impact elasticities; empirical λ calibration                                                          |
| 11 | Almgren, R., Thum, C., Hauptmann, E., & Li, H. (2005). Direct Estimation of Equity Market Impact. *Risk*, 18(7), 58–62.                                                                                                                                                                     | Alternative non-linear (square-root) price-impact                                                                          |
| 12 | Tóth, B., et al. (2011). Anomalous price impact and the critical nature of liquidity in financial markets. *Physical Review X*, 1, 021006. DOI: 10.1103/PhysRevX.1.021006                                                                                                                    | Latent-liquidity alternative to linear impact                                                                              |
| 13 | Schularick, M., & Taylor, A. M. (2012). Credit Booms Gone Bust: Monetary Policy, Leverage Cycles, and Financial Crises, 1870–2008. *American Economic Review*, 102(2), 1029–1061. DOI: 10.1257/aer.102.2.1029                                                                                | Long-run credit-boom-then-bust empirics; supports L_ponzi_threshold calibration                                            |
| 14 | Bhattacharya, S., Goodhart, C., Tsomocos, D., & Vardoulakis, A. (2015). A Reconsideration of Minsky's Financial Instability Hypothesis. *Journal of Money, Credit and Banking*, 47(5), 931–973. DOI: 10.1111/jmcb.12229                                                                       | Alternative: continuous / smooth-logistic regime formulation                                                              |
| 15 | Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35–55. DOI: 10.1111/j.1540-6261.1997.tb03807.x                                                                                                                                                    | Why fundamentalists cannot restore anchoring in Ponzi regime; supports ε_γ ≪ γ_base                                        |
| 16 | Fama, E. F., & French, K. R. (1988). Permanent and Temporary Components of Stock Prices. *Journal of Political Economy*, 96(2), 246–273. DOI: 10.1086/261535                                                                                                                                 | Empirical mean-reversion half-lives; γ_base calibration                                                                    |
| 17 | Fama, E. F. (1970). Efficient Capital Markets: A Review of Theory and Empirical Work. *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486                                                                                                                                             | Random-walk baseline (γ = 0 ablation reference)                                                                            |
| 18 | Bernanke, B., & Gertler, M. (1989). Agency Costs, Net Worth, and Business Fluctuations. *American Economic Review*, 79(1), 14–31. URL: https://www.jstor.org/stable/1804770                                                                                                                  | Agency-cost / external-finance premium; alternative price-leverage coupling                                               |
| 19 | Rajan, R. G. (2010). *Fault Lines: How Hidden Fractures Still Threaten the World Economy*. Princeton University Press. ISBN: 978-0691146836. See also Rajan, R. G. (2005). Has Financial Development Made the World Riskier? *Proceedings of the Jackson Hole Symposium*.                    | Systemic risk from procyclical leverage; policy-implications context                                                       |
| 20 | Roll, R. (1984). A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market. *Journal of Finance*, 39(4), 1127–1139. DOI: 10.1111/j.1540-6261.1984.tb03897.x                                                                                                            | Gaussian-noise (σ) parameterisation                                                                                        |
| 21 | Engle, R. F. (1982). Autoregressive Conditional Heteroskedasticity with Estimates of the Variance of United Kingdom Inflation. *Econometrica*, 50(4), 987–1007. DOI: 10.2307/1912773                                                                                                          | Alternative: heteroskedastic (GARCH) residuals                                                                             |
| 22 | Merton, R. C. (1976). Option pricing when underlying stock returns are discontinuous. *Journal of Financial Economics*, 3(1–2), 125–144. DOI: 10.1016/0304-405X(76)90022-2                                                                                                                    | Alternative: jump-diffusion residuals for crisis-period MBS paths                                                          |

## Design Provenance and Versioning

| Field       | Content                                                        |
|-------------|----------------------------------------------------------------|
| Market Type | `credit` — Credit / Lending Market                             |
| Author      | AgenticFinLab                                                  |
| Reviewed by | — (pending)                                                    |
| Created     | 2026-07-16                                                     |
| Version     | 1.0.0                                                          |
| Status      | canonical                                                      |
| Icon        | ![](../agent_images/icons/market/credit-minsky-cycle.png)      |
