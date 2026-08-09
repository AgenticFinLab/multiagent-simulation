# Deposit-run coordinator with Diamond-Dybvig first-mover advantage and solvency regime switch

## Summary

| Field                | Content                                                                                                                                                                                                                                                                              |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `deposit` — Bank Deposit / Run Market                                                                                                                                                                                                                                                |
| Coordinator Role     | Central deposit-and-solvency coordinator: tracks cumulative withdrawal fraction, marks the bond portfolio to market, evaluates the solvency ratio, and latches a one-way regime state `solvent` → `stressed` → `failed`                                                             |
| Mechanism Family     | Fraction-of-withdrawals cumulative state with first-mover advantage, mark-to-market bond losses, panic-threshold trigger, and post-failure haircut on remaining claims                                                                                                               |
| Shared State         | `withdrawal_fraction`, `prev_withdrawal_fraction`, `withdrawal_rate_this_round`, `solvency_ratio`, `prev_solvency_ratio`, `bond_mtm_loss`, `regime_status`, `num_withdrawers`, `num_holders`, `num_returners`, `panic_indicator`, `haircut_applied`, `round`                          |
| Broadcast Cadence    | every-tick (one broadcast per round, after all depositor actions drain)                                                                                                                                                                                                            |
| Determinism          | stochastic-given-seed (`ε ~ N(0, σ²)` from a seeded RNG; identical seed + inbound-action sequence + `bond_mtm_loss_trajectory` reproduce byte-equal broadcasts)                                                                                                                     |
| Feedback Direction   | **Regime-dependent** — near-neutral first-mover pressure while `regime_status == "solvent"` and `W < panic_threshold`; common-knowledge cascade amplifies once `W ≥ panic_threshold`; regime latches to `"failed"` and mechanism switches from amplifying to absorbing once `solvency_ratio < solvency_floor` [Ref 1, Ref 2, Ref 3] |
| Scenario Portability | 1 pool scenario bound via `players.yml → market.archetype: deposit-bank-run-diamond-dybvig`. **Full ✅**: (none). **Approximated ⚠**: SVBBankRun — currently uses the stock-standard price-impact code path; the `withdrawal_fraction ∈ [0, 1]` monotone-non-decreasing state, the panic-threshold cascade, and the one-way `solvent → stressed → failed` regime latch are intended but not yet implemented. See also the Scenario Status row below. |
| Scenario Status      | **Full** = coordinator code implements the archetype's mechanism signature verbatim; **Approximated** = archetype bound via `players.yml → market.archetype:` for icon/UI/narrative purposes, but the coordinator code currently uses the standard price-impact formula `P(t+1)=P(t)+λ·NetDemand+γ·(F-P(t))+ε` as a placeholder — the archetype's specialized state and dynamics are intended but not yet realized in code. |

## Definition and Goals

This coordinator models a **single-bank deposit market with a
common-knowledge withdrawal-fraction cascade, an exogenous
mark-to-market bond-portfolio loss trajectory, and a one-way solvency
regime latch** — the workhorse for bank-run scenarios at round
granularity (typically one day; one hour for digital-run studies).
The real-world counterpart is a retail-plus-institutional deposit
book under liquidity stress, in the tradition of Diamond & Dybvig
(1983) [Ref 1] extended with common-knowledge cascades by Goldstein
& Pauzner (2005) [Ref 2] and global-games unique-equilibrium
selection by Rochet & Vives (2004) [Ref 3]. It is fraction-based
rather than order-book matched because Iyer & Puri (2012) [Ref 4]
show peer-observability — not queue position — drives cascades,
making a shared-observable-fraction rule numerically equivalent to
an explicit queue at sufficient aggregation. The empirical anchor is
Silicon Valley Bank's 2023 collapse ($42B outflow in one day), where
Cookson et al. (2023) [Ref 12] documented via Twitter data that
public disclosure of the withdrawal rate was itself the cascade
signal.

Coordination goal: aggregate depositor actions, compute
`W(t+1) = min(1, W(t) + α·NetWithdrawFraction − β·NetReturnFraction
+ ε)`, mark the bond portfolio to market via exogenous
`bond_mtm_loss(t)`, compute
`Solvency(t+1) = (1 − W(t+1)) · (1 − bond_mtm_loss(t))`, evaluate
the solvency floor to determine `regime_status`, apply a haircut at
the moment of failure, and broadcast the 13-field snapshot
identically to every participant (symmetric common-knowledge —
Goldstein-Pauzner [Ref 2] design point).

Non-goals (this coordinator MUST NOT):

- Filter depositor actions by identity, insurance cap, or history —
  first-mover advantage is intrinsic to the state trajectory.
- Inject exogenous rate shocks, news, or guarantees; `bond_mtm_loss`
  is an *input* (see §5 Exogenous Driver Boundary).
- Enforce depositor-side position limits or insurance-cap decisions
  — those are self-imposed per `agent-design-skill.md` §3.6.3.
- Modify the `bond_mtm_loss` trajectory from its own logic.
- Retract a `regime_status = "failed"` latch — one-way per DD
  equilibrium selection.
- Decide the haircut size endogenously; `haircut_fraction` is a
  fixed uniform parameter applied at the moment of failure.

## Theoretical / Mechanistic Foundation

**Coordination-run equilibrium with first-mover advantage (Diamond & Dybvig 1983)**:

- Theory / Study: Sequential-service bank runs with run / no-run
  equilibria selected by depositor beliefs about others.
- Citation: Diamond, D. W., & Dybvig, P. H. (1983). *JPE*, 91(3),
  401–419. DOI: `10.1086/261155`
- Core Insight: Demandable deposits + illiquid assets + sequential
  service ⇒ withdraw if you believe enough others will withdraw
  first; cumulative W is monotone-non-decreasing under normal runs.
- Mathematical Formulation: `ΔW_first_mover = α · NetWithdrawFraction`.
- Empirical Evidence: Iyer & Puri (2012) [Ref 4, Table III]:
  peer-observability raises conditional withdrawal by 3–6 pp ⇒
  `α ∈ [0.5, 1.0]` at round granularity.
- Relevance to This Coordinator: Primary transition term
  `α · NetWithdrawFraction`; anchors invariant #5.
- Calibration Source: Iyer-Puri 2012 [Ref 4, Table III]; DD 1983
  [Ref 1, §III] uses ≈ 1.0.

**Common-knowledge cascade above panic threshold (Goldstein & Pauzner 2005)**:

- Theory / Study: Bank-run equilibrium selection under a
  common-knowledge signal of the withdrawal rate.
- Citation: Goldstein, I., & Pauzner, A. (2005). *JF*, 60(3),
  1293–1327. DOI: `10.1111/j.1540-6261.2005.00762.x`
- Core Insight: A public signal of the current withdrawal fraction
  (statement, Twitter, queue) makes the run self-fulfilling once the
  observed fraction crosses a threshold; further withdrawals confirm
  to others that many are running.
- Mathematical Formulation:
  `panic_indicator(t) = 1 if W(t) ≥ panic_threshold else 0`; default
  keeps `α` constant and broadcasts `panic_indicator`; Ablation Hook
  exposes `α_effective = α · (1 + panic_indicator · gain)`.
- Empirical Evidence: Kelly & Ó Gráda (2000) [Ref 7, Table 4]:
  panic-inflection at `W ≈ 0.15–0.25` in 1854–1857 Irish runs; SVB
  run-rate jumped ≈5%→≈25%/day post-Twitter disclosure (Cookson et
  al. 2023 [Ref 12, §3]).
- Relevance to This Coordinator: Provides `panic_threshold` and the
  `panic_indicator` broadcast field.
- Calibration Source: Kelly-Ó Gráda 2000 [Ref 7, Table 4]; Cookson et
  al. 2023 [Ref 12, §3]; default `panic_threshold = 0.20`.

**Global-games unique-equilibrium selection (Rochet & Vives 2004)**:

- Theory / Study: Bank runs as coordination game with noisy private
  signals yielding a unique threshold equilibrium.
- Citation: Rochet, J.-C., & Vives, X. (2004). *JEEA*, 2(6),
  1116–1147. DOI: `10.1162/1542476042813841`
- Core Insight: Global-games uniquely selects a fundamental-signal
  threshold on `solvency_ratio` distinct from the coordination-signal
  panic threshold; panic = coordination trigger, solvency floor =
  fundamental trigger.
- Mathematical Formulation:
  `regime_switch := "failed" if Solvency(t+1) < solvency_floor
   else regime_status(t)`.
- Empirical Evidence: Rochet-Vives 2004 [Ref 3, §3] simulations put
  the threshold near solvency `0.85–0.95`; FDIC receivership data
  2008–2023 cluster failure marks at `0.90–0.95`.
- Relevance to This Coordinator: Provides `solvency_floor`; motivates
  the one-way `regime_status` latch (invariant #4).
- Calibration Source: Rochet-Vives 2004 [Ref 3, §3]; FDIC failed-bank
  list; default `solvency_floor = 0.90`.

**Mark-to-market bond-portfolio losses (Jiang, Matvos, Piskorski, Seru 2023 SVB analysis)**:

- Theory / Study: SVB 2023 failure as rate-driven MTM losses +
  loss-crystallisation-triggered run + sequential-service depletion.
- Citation: Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A.
  (2023). *NBER WP 31048*. DOI: `10.3386/w31048`
- Core Insight: Solvency in a run depends on the marked-to-market
  value of the whole asset book (not just liquid reserves); MTM
  channel enters solvency multiplicatively on the asset side.
- Mathematical Formulation:
  `Solvency(t+1) = (1 − W(t+1)) · (1 − bond_mtm_loss(t))`.
- Empirical Evidence: Jiang et al. (2023) [Ref 8, Table 3]: ≈$2.2T
  unrealised MTM losses across U.S. banks in Q1 2023, ≈10% of assets
  on average and 15–20% at fragile banks including SVB ⇒
  `bond_mtm_loss ∈ [0.10, 0.20]`.
- Relevance to This Coordinator: Motivates the second term of the
  solvency formula and the exogenous-input treatment.
- Calibration Source: Jiang et al. 2023 [Ref 8, Table 3]; default
  scalar `bond_mtm_loss = 0.10`, optional
  `bond_mtm_loss_trajectory`.

**Post-failure uniform haircut on remaining claims**:

- Theory / Study: Sequential-service tail behaviour at insolvency —
  remaining depositors receive a pro-rata haircut.
- Citation: Diamond & Dybvig 1983 [Ref 1, §II]; Rochet-Vives 2004
  [Ref 3, §4]; Bennett & Unal (2015) [Ref 14].
- Core Insight: At the moment the regime latch to `"failed"` fires,
  remaining claims suffer a uniform `haircut_fraction`; the haircut
  is one-shot and never reverts.
- Mathematical Formulation: at `t*` where `regime(t*) = "failed"`
  first: `haircut_applied ← haircut_fraction`; residual claim value
  `= (1 − W(t*)) · (1 − haircut_fraction)`.
- Empirical Evidence: Bennett & Unal (2015) [Ref 14, Table 2]:
  average FDIC uninsured-depositor recovery ≈72% in 2008–2013
  (haircut ≈28%); default `haircut_fraction = 0.20` is the low end.
- Relevance to This Coordinator: Provides `haircut_fraction` and the
  `haircut_applied` broadcast field.
- Calibration Source: Bennett-Unal 2015 [Ref 14, Table 2]; default
  `haircut_fraction = 0.20`.

**Depositor-return channel (optional; Farhi & Tirole–style reversal)**:

- Theory / Study: DD extension where credible guarantees allow
  panicked depositors to partially reverse withdrawals.
- Citation: Farhi, E., & Tirole, J. (2012). *AER*, 102(1), 60–93.
  DOI: `10.1257/aer.102.1.60`
- Core Insight: Strict DD has irreversible withdrawals; in practice
  (Continental Illinois 1984, SVB post-guarantee) a credible reset
  returns a fraction of deposits. Modelled as an optional path gated
  by `allow_returns` (default `false`).
- Mathematical Formulation: `ΔW_return = −β · NetReturnFraction ·
  allow_returns_flag`; only active while `regime_status != "failed"`.
- Empirical Evidence: Federal Reserve (1984) [Ref 16]: ≈40% of
  Continental Illinois uninsured deposits returned within 30 days of
  the FDIC no-loss guarantee; SVB stabilised within 48 hours of the
  2023-03-12 systemic-risk exception (FDIC 2023 [Ref 17]).
- Relevance to This Coordinator: Provides `return_impact` (β) and
  the optional negative transition term.
- Calibration Source: Federal Reserve 1984 [Ref 16]; default
  `return_impact = 0.5`, `allow_returns = false`.

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate depositor actions, apply the first-mover +
optional-return + noise transition to `withdrawal_fraction`, evaluate
exogenous `bond_mtm_loss(t)` and derive `solvency_ratio`, latch
`regime_status` on the solvency floor, and broadcast one authoritative
deposit-market snapshot including `panic_indicator`.

Coordination Cadence: **every-tick** (one broadcast per round). Once
`regime_status == "failed"`, the coordinator keeps broadcasting each
round (for post-failure analytics) but rejects all further withdrawal/
return actions — `num_withdrawers` and `num_returners` are forced to
`0` and state is held constant apart from the frozen
`haircut_applied` flag.

Lifecycle Mapping (MANDATORY):

- `perceive(observation, prev_result)`:
  1. Set `state["round"] = observation.round`.
  2. If `"withdrawal_fraction"` is not in `state.custom_state`, run
     State Initialization below.
  3. Drain `observation.inbounds`; each payload is
     `{action_type ∈ {withdraw, hold, return, panic_withdraw},
     intensity ∈ [0,1], share ∈ [0,1], agent_role}`.
  4. Validate each action per §4.6.6 (raise `ValueError` on
     out-of-range); store in `state["actions"]` — READ only, no
     derived-state writes.
  5. Read exogenous MTM:
     `state["bond_mtm_loss_current"] =
     bond_mtm_loss_trajectory[round_num]` if trajectory provided,
     else scalar `bond_mtm_loss`.
- `decide()`: execute §4.6.2 Core Coordination Mechanism (aggregate →
  branch on `regime_status(t) == "failed"` short-circuit → noise draw
  → transition with monotone guard → solvency identity → panic
  indicator → latch → atomic WRITE of all 13 broadcast fields in the
  order `prev_withdrawal_fraction ← W(t)`, `prev_solvency_ratio ←
  Solvency(t)` first, then current-round fields; append to each of
  the five `HistoryBuffer` instances). Returns the 13-field broadcast
  dict. See §4.6.2 for the full step-by-step.
- `act(decision)`: wrap as `EnvironmentBroadcast`
  (`action_type="deposit_market_broadcast"`) and emit to every
  participant. No writes.

Deviation from the stock-market lifecycle: because `solvency_ratio`,
`regime_status`, `panic_indicator`, and `haircut_applied` are all
**derived from aggregated actions plus the exogenous MTM input**, and
because the regime latch requires the *post-transition* solvency
before committing state, the state-write step lives inside `decide`,
not `perceive`. `perceive` only validates/stores raw actions and
reads the current MTM value; `decide` performs the transition, latch,
and write; `act` remains write-free. Mirrors the
opinion-echo-chamber coordinator's lifecycle deviation and is
observable via invariant #1. Any implementation that writes state in
`perceive` will evaluate the latch on stale aggregates and violate
invariant #4.

State Initialization (MANDATORY):

- Trigger: `"withdrawal_fraction" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing): `initial_deposits`,
  `initial_bond_portfolio_value`, `initial_withdrawal_fraction`,
  `withdrawal_impact` α, `return_impact` β, `panic_threshold`
  τ_panic, `solvency_floor` τ_solv, `stressed_floor` τ_stress
  (must satisfy `solvency_floor < stressed_floor < 1`),
  `haircut_fraction` h, `bond_mtm_loss` (scalar fallback, required
  if trajectory absent), `noise_std` σ, `allow_returns` (bool,
  default `false`), `record_path`, `custom_state_hot_limit`.
- Optional: `bond_mtm_loss_trajectory` (`list[float]`, length ≥
  `total_rounds`; overrides the scalar).
- Initial writes (single atomic block): set `W_0 =
  initial_withdrawal_fraction`; `withdrawal_fraction = W_0`;
  `prev_withdrawal_fraction = W_0`; `withdrawal_rate_this_round = 0`;
  `bond_mtm_loss = trajectory[0]` if provided else scalar;
  `solvency_ratio = (1 − W_0)·(1 − bond_mtm_loss)`;
  `prev_solvency_ratio = solvency_ratio`; `regime_status = "solvent"`
  at t=0 regardless (latch fires only on transitions);
  `panic_indicator = 1 if W_0 ≥ panic_threshold else 0`;
  `haircut_applied = 0.0`; `num_withdrawers = num_holders =
  num_returners = 0`; instantiate five `HistoryBuffer`s
  (`withdrawal_history`, `solvency_history`, `regime_history`,
  `bond_mtm_loss_history`, `withdrawer_count_history`) rooted at
  `<record>/<identity>/…`, `entry_limit=hot_limit`.
- Warm-up rounds: `0` (round-0 broadcast is trustworthy, but
  `prev_withdrawal_fraction == withdrawal_fraction` at t=0 SHOULD be
  read as "no observation yet", not "run rate of zero").

Inbound Message Types:

- **DepositorAction**: `{"action_type": "withdraw" | "hold" |
  "return" | "panic_withdraw", "intensity": float ∈ [0,1], "share":
  float ∈ [0,1], "agent_role": str}`. `withdraw` and
  `panic_withdraw` are treated identically (label variant only);
  `return` contributes iff `allow_returns == true` else counted only
  in `num_returners`; `hold` or `intensity == 0` counted only in
  `num_holders`. `share` is the fraction of the depositor's own
  still-remaining balance to move this round. Aggregation is
  count-mean-normalised (see §4.6.1).
- Default (no message): treated as `hold` with `intensity = 0`.

Broadcast Trigger: end of `decide`, after the state-write.

Missing-Input Policy: missing required extras → `KeyError` from
`perceive`; invalid `action_type` or out-of-range `intensity`/`share`
→ `ValueError` from `perceive`; `bond_mtm_loss_trajectory` shorter
than run length → `IndexError` from `perceive`; `NaN`/`Inf` in
`new_W`/`new_solvency` → `ValueError` from `decide`; zero inbound
actions is legitimate (noise + MTM move still runs). NEVER silently
substitute a default for a required field.

Exogenous Driver Boundary (MANDATORY): coordinator MUST NOT generate
exogenous rate shocks, MTM jumps, government guarantees, or news
events. `bond_mtm_loss` enters via a pre-computed
`bond_mtm_loss_trajectory` in `extras`, or via mutation of
`config.extras["bond_mtm_loss"]` (or a trajectory entry) by a
scenario `RateEnvironment` agent BEFORE this coordinator's
`perceive` for that round. `allow_returns` MAY be flipped mid-run by
a scenario `RegulatorAgent` (representing FDIC's systemic-risk
exception on 2023-03-12); the coordinator itself is passive.

Environmental Dependencies: see §4.7 for the full extras list; the
optional scenario driver signals are `RateEnvironment` (per-round
mutation of `bond_mtm_loss`) and `RegulatorAgent` (mid-run flip of
`allow_returns`). Neither is required for baseline runs.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input               | Source                          | Type / Shape                                                                                                                          | Required? | Notes                                                                                    |
|---------------------|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|-----------|------------------------------------------------------------------------------------------|
| `inbound_actions`   | mailbox from depositor agents   | `list[dict]`; each dict has `action_type: str`, `intensity: float`, `share: float`, `agent_role: str`                                  | yes       | `share` is a fraction of the depositor's own still-remaining balance                     |
| `current_state`     | coordinator's persisted state   | `{"withdrawal_fraction": float, "prev_withdrawal_fraction": float, "solvency_ratio": float, "regime_status": str, ...}`                | yes       | Populated on first call by State Initialization                                          |
| `context_metadata`  | scheduler / round header        | `{"round": int, "identity": str, "seed": int}`                                                                                        | yes       | Identity naming: `{variant}_market_deposit`                                              |
| `scenario_driver`   | scenario overlay                | `dict` or `None` — may carry updated `bond_mtm_loss` value and/or `allow_returns` toggle                                              | no        | Only if scenario declares a `RateEnvironment` or `RegulatorAgent`                        |

##### Outputs (per coordination call)

The coordinator emits exactly one broadcast dict per call. Every
participant sees the identical dict.

| Field                          | Type   | Valid Range / Enum                       | Unit                       | Required? | Meaning                                                                                    |
|--------------------------------|--------|------------------------------------------|----------------------------|-----------|--------------------------------------------------------------------------------------------|
| `withdrawal_fraction`          | float  | `[0, 1]`                                 | fraction of initial deposits | yes       | Post-transition cumulative withdrawal fraction W(t+1) for this round                        |
| `prev_withdrawal_fraction`     | float  | `[0, 1]`                                 | fraction of initial deposits | yes       | Withdrawal fraction broadcast in the previous round (W(t))                                  |
| `withdrawal_rate_this_round`   | float  | `[-1, 1]`                                | fraction per round         | yes       | `withdrawal_fraction − prev_withdrawal_fraction` (may be negative if `allow_returns`)       |
| `solvency_ratio`               | float  | `[0, 1]`                                 | ratio                      | yes       | `(1 − withdrawal_fraction) · (1 − bond_mtm_loss)`                                          |
| `prev_solvency_ratio`          | float  | `[0, 1]`                                 | ratio                      | yes       | Solvency ratio broadcast in the previous round                                              |
| `bond_mtm_loss`                | float  | `[0, 1]`                                 | fraction of asset value    | yes       | Current-round mark-to-market loss on the bond portfolio (exogenous input value)             |
| `regime_status`                | str    | `{"solvent", "stressed", "failed"}`      | enum                       | yes       | One-way-latch regime label; `"failed"` once set never reverts                              |
| `num_withdrawers`              | int    | `≥ 0`                                    | count                      | yes       | Number of `withdraw` or `panic_withdraw` actions this round                                 |
| `num_holders`                  | int    | `≥ 0`                                    | count                      | yes       | Number of `hold` actions this round                                                         |
| `num_returners`                | int    | `≥ 0`                                    | count                      | yes       | Number of `return` actions this round (0 unless `allow_returns`)                            |
| `panic_indicator`              | int    | `{0, 1}`                                 | Boolean                    | yes       | `1` iff `withdrawal_fraction ≥ panic_threshold` in the current broadcast                    |
| `haircut_applied`              | float  | `[0, 1]`                                 | fraction of remaining claim | yes       | `0.0` while `regime_status != "failed"`; latches to `haircut_fraction` at the moment of failure |
| `round`                        | int    | `≥ 0`                                    | —                          | yes       | Round number that produced this broadcast                                                   |

Any participant reading a field NOT listed here indicates a
downstream bug — this contract is the exhaustive schema.

##### Content Constraints

- **Required fields**: all thirteen fields present every round,
  including post-failure rounds (coordinator keeps broadcasting so
  analytics can observe frozen state).
- **Forbidden fields**: fields not declared above MUST NOT be added.
- **Value ranges**: `withdrawal_fraction`, `solvency_ratio`,
  `bond_mtm_loss`, `haircut_applied` clipped to `[0, 1]`;
  `regime_status` in the three-element enum; `panic_indicator ∈
  {0, 1}`; all numeric fields finite.
- **Units / sign**: `withdrawal_fraction` is a fraction of *initial*
  deposits (does NOT renormalise as base shrinks). `solvency_ratio`
  is initial-deposit-backed fraction. `withdrawal_rate_this_round`
  is signed (negative only under `allow_returns == true`).
- **Determinism**: ε seed recoverable from `(base_seed, round)`;
  identical seed + actions + `bond_mtm_loss_trajectory` yield
  byte-equal broadcasts.

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participants). Retrieval fallback
sentinel: if a downstream reader loses a field, it MUST raise
`KeyError`, not substitute a default (see Missing-Input Policy).
Canonical shape:

```json
{
  "withdrawal_fraction":         0.28,
  "prev_withdrawal_fraction":    0.19,
  "withdrawal_rate_this_round":  0.09,
  "solvency_ratio":              0.648,
  "prev_solvency_ratio":         0.729,
  "bond_mtm_loss":               0.10,
  "regime_status":               "stressed",
  "num_withdrawers":             42,
  "num_holders":                 8,
  "num_returners":               0,
  "panic_indicator":             1,
  "haircut_applied":             0.0,
  "round":                       6
}
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag` or any
scheme declared in the target's §10.1) that instantiates this
coordinator MUST emit the identical dict shape. LLM-side variants
never wrap the broadcast in narrative text — the coordinator is
rule-executed even when participants are model-driven.

##### Implementer Contract Reminder

1. **Extras wiring** — every broadcast field uses only inbound
   aggregates, `bond_mtm_loss_current` loaded in `perceive`, or
   `config.extras` keys declared in §4.7; no hidden constants. The
   broadcast `bond_mtm_loss` MUST equal the trajectory value read
   in `perceive` — not smoothed, not imputed.
2. **Broadcast emission** — `decide` populates every required field;
   clips `withdrawal_fraction`, `solvency_ratio`, `bond_mtm_loss`,
   `haircut_applied` to `[0, 1]`; enforces the `regime_status` enum;
   applies the monotone guard when `allow_returns == false`; all
   BEFORE state-write.
3. **Format-layer compatibility** — participant-side
   `StandardDepositState` (or engine-equivalent) MUST raise
   `KeyError` on missing `withdrawal_fraction`, `solvency_ratio`, or
   `regime_status`.
4. **Variant parity** — every declared variant emits the same
   13-field dict.
5. **One-way-latch enforcement** — transitioning `regime_status`
   from `"failed"` back to any other value is a contract violation;
   short-circuit inside `decide` when `regime_status(t) == "failed"`.
6. **Conflict resolution** — if §4.6.2, §4.7, or §4.8 seem to
   contradict this contract, the contract wins.

#### Input Aggregation Rules

| Aggregate signal            | Derivation                                                                                                                       | Rationale                                                              |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| `total_withdraw_share`      | `sum(a["intensity"] · a["share"] for a in actions if a["action_type"] ∈ {"withdraw", "panic_withdraw"}) / max(1, len(actions))`   | Total intensity-weighted withdrawal share, normalised by depositor count |
| `total_return_share`        | `sum(a["intensity"] · a["share"] for a in actions if a["action_type"] == "return") / max(1, len(actions))`                       | Total intensity-weighted return share, same normalisation                |
| `net_withdraw_fraction`     | `total_withdraw_share`                                                                                                            | Feeds the α term of the transition                                       |
| `net_return_fraction`       | `total_return_share · allow_returns_flag`                                                                                         | Feeds the β term of the transition; gated by the flag                    |
| `num_withdrawers`           | `sum(1 for a in actions if a["action_type"] ∈ {"withdraw", "panic_withdraw"})`                                                    | Count of withdrawers this round                                          |
| `num_holders`               | `sum(1 for a in actions if a["action_type"] == "hold")`                                                                           | Count of holders this round                                              |
| `num_returners`             | `sum(1 for a in actions if a["action_type"] == "return")`                                                                         | Count of returners this round (logged even if `allow_returns == false`)   |
| `n_active`                  | `len([a for a in actions if a["action_type"] != "hold"])`                                                                         | Count of non-hold participants; used only for logging                    |

Does NOT use: individual participant identities; participant
`agent_role` (label is stored but not aggregated); participant
deposit-insurance-cap status; participant capital or wealth; peer-to-peer
topology.

Completeness rule check: all eight aggregates above are consumed in
§4.6.2 (net_withdraw_fraction in step 5; net_return_fraction in step
5; num_withdrawers / num_holders / num_returners in step 8 (WRITE);
n_active in step 9 logging; total_withdraw_share and
total_return_share are the raw signals that feed the two net_ signals
and are written into logs as diagnostics).

#### Core Coordination Mechanism

1. **READ** `round_num`, `inbound_actions` from `observation`; read
   `state["withdrawal_fraction"] = W(t)`, `state["solvency_ratio"] =
   Solvency(t)`, `state["regime_status"] = R(t)`; and extras
   `{α, β, σ, τ_panic, τ_solv, τ_stress, h, allow_returns_flag}`.
2. **READ** exogenous MTM: `bond_mtm_loss_current =
   bond_mtm_loss_trajectory[round_num]` if provided, else scalar.
3. **VALIDATE** each action against valid types (`withdraw`, `hold`,
   `return`, `panic_withdraw`), `intensity, share ∈ [0, 1]`; raise
   `ValueError` on violation.
4. **COMPUTE** aggregates per §4.6.1: `total_withdraw_share`,
   `total_return_share`, `net_withdraw_fraction`,
   `net_return_fraction`, `num_withdrawers`, `num_holders`,
   `num_returners`.
5. **BRANCH** on `R(t)`: if `R(t) == "failed"`, skip transition
   (`new_W = W(t)`, `new_solvency = Solvency(t)`, `new_regime =
   "failed"`, carry prior `panic_indicator`/`haircut_applied`, force
   `num_withdrawers = num_returners = 0` in the broadcast) and jump
   to step 8; else continue.
6. **COMPUTE** noise `ε = rng.gauss(0, σ)`.
7. **COMPUTE** transition:
   `W_raw = W(t) + α·net_withdraw_fraction − β·net_return_fraction·allow_returns_flag + ε`;
   monotone guard when `allow_returns_flag == false`:
   `W_guarded = max(W_raw, W(t))`;
   clip `new_W = min(1, max(0, W_guarded))`;
   `new_solvency = (1 − new_W)·(1 − bond_mtm_loss_current)`;
   `panic_indicator = 1 if new_W ≥ τ_panic else 0`.
8. **EVALUATE LATCH**: if `new_solvency < τ_solv` AND `R(t) !=
   "failed"` → `new_regime = "failed"`, `haircut_applied = h`
   (one-shot flip from `0.0`); else if `new_W ≥ τ_panic OR
   new_solvency < τ_stress` → `new_regime = "stressed"`,
   `haircut_applied = 0.0`; else → `new_regime = "solvent"`,
   `haircut_applied = 0.0`.
9. **WRITE** atomically in order: `prev_withdrawal_fraction ← W(t)`,
   `prev_solvency_ratio ← Solvency(t)`, then `withdrawal_fraction`,
   `withdrawal_rate_this_round`, `solvency_ratio`, `bond_mtm_loss`,
   `regime_status`, `panic_indicator`, `haircut_applied`,
   `num_withdrawers`, `num_holders`, `num_returners`; append to each
   `HistoryBuffer`.
10. **EMIT** the 13-field broadcast dict per §4.6.0 Outputs.

#### Broadcast Space

| Aspect                       | Specification                                                                                                                                                                                              |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Broadcast fields             | `withdrawal_fraction`, `prev_withdrawal_fraction`, `withdrawal_rate_this_round`, `solvency_ratio`, `prev_solvency_ratio`, `bond_mtm_loss`, `regime_status`, `num_withdrawers`, `num_holders`, `num_returners`, `panic_indicator`, `haircut_applied`, `round` (verbatim §4.6.0 Outputs) |
| State transition rule        | `W(t+1) = clip(max(W(t) + α·net_withdraw_fraction − β·net_return_fraction·allow_returns_flag + ε, W(t) if not allow_returns else −1), 0, 1)`; `Solvency(t+1) = (1 − W(t+1))·(1 − bond_mtm_loss(t))`; one-way regime latch |
| Value bounds                 | `withdrawal_fraction, solvency_ratio, bond_mtm_loss, haircut_applied ∈ [0, 1]`; `regime_status ∈ {"solvent", "stressed", "failed"}`; `panic_indicator ∈ {0, 1}`                                             |
| Freshness policy             | Every-tick; broadcast reflects state committed in the current `decide`. Post-failure broadcasts continue every round with frozen state values (except `round` and the `prev_*` fields).                    |
| Revision policy              | No — a broadcast MUST NOT be retracted or amended within a round; the `regime_status = "failed"` latch is IRREVOCABLE across rounds. If a bug is detected mid-round the round is aborted (see Failure Modes). |
| State-history retention      | Hot buffer of `custom_state_hot_limit` (default 10000) entries with cold spill to `<record_path>/<identity>/…` via `HistoryBuffer`. Five parallel history buffers are maintained.                          |
| Resource cap                 | Unbounded on-disk (history spills); RAM bounded by hot-limit.                                                                                                                                              |
| Termination rule             | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown. Even after `regime_status = "failed"` latches, broadcasts continue until `total_rounds`.              |

#### Mathematical Model

1. **Broadcast outputs (types)**: `withdrawal_fraction`,
   `prev_withdrawal_fraction`, `solvency_ratio`, `prev_solvency_ratio`,
   `bond_mtm_loss`, `haircut_applied` ∈ `[0, 1] ⊂ ℝ`;
   `withdrawal_rate_this_round ∈ [-1, 1] ⊂ ℝ` (negative only under
   `allow_returns == true`); `regime_status ∈ {"solvent", "stressed",
   "failed"}`; `panic_indicator ∈ {0, 1}`; `num_withdrawers,
   num_holders, num_returners, round ∈ ℤ⁺ ∪ {0}`. Full field
   descriptions in §4.6.0 Outputs.

2. **State transition logic**:
   ```
   ε(t)   ~ N(0, σ²)   — one draw per round, seeded by (base_seed, t)

   NetWithdrawFraction(t) =
       Σ_{i: action_i.type ∈ {"withdraw","panic_withdraw"}}
           (intensity_i · share_i) / max(1, len(actions))

   NetReturnFraction(t) =
       Σ_{i: action_i.type == "return"}
           (intensity_i · share_i) / max(1, len(actions))

   W_raw(t+1) = W(t) + α · NetWithdrawFraction(t)
                     − β · NetReturnFraction(t) · allow_returns_flag
                     + ε(t)

   W_guarded(t+1) = max(W_raw(t+1), W(t))   if allow_returns_flag == 0
                  = W_raw(t+1)              otherwise

   W(t+1)      = clip(W_guarded(t+1), 0, 1)

   Solvency(t+1) = (1 − W(t+1)) · (1 − bond_mtm_loss(t))

   panic_indicator(t+1) = 1 if W(t+1) ≥ τ_panic else 0

   regime(t+1) =
     "failed"    if regime(t) == "failed" OR Solvency(t+1) < τ_solv
     "stressed"  else if W(t+1) ≥ τ_panic OR Solvency(t+1) < τ_stress
     "solvent"   otherwise

   haircut_applied(t+1) =
     haircut_applied(t)   if regime(t) == "failed"           (frozen)
     h                    if regime(t) != "failed" AND regime(t+1) == "failed"
     0.0                  otherwise
   ```

3. **State variables** (initial values set in §4.5 State
   Initialization): scalar floats `withdrawal_fraction`,
   `prev_withdrawal_fraction`, `withdrawal_rate_this_round`,
   `solvency_ratio`, `prev_solvency_ratio`, `bond_mtm_loss`,
   `haircut_applied`; scalar strings `regime_status`; scalar ints
   `panic_indicator`, `num_withdrawers`, `num_holders`,
   `num_returners`, `round`; five `HistoryBuffer` instances
   (`withdrawal_history`, `solvency_history`, `regime_history`,
   `bond_mtm_loss_history`, `withdrawer_count_history`), each
   rooted at `<record>/<identity>/…` with `entry_limit=hot_limit`.

4. **State evolution ordering**: all writes happen at the end of
   `decide` (§4.6.2 step 9), AFTER transition + latch and BEFORE the
   broadcast is returned. `prev_*` fields are written before the
   corresponding current values (invariant #1); `regime_status` and
   `haircut_applied` update in the same atomic block so no reader
   ever sees a `"failed"` regime paired with `haircut = 0.0`.

5. **Determinism contract**: **stochastic-given-seed**. The single
   randomness source is ε; the RNG is seeded by
   `(base_seed, round)`. Identical base seed + inbound actions +
   `bond_mtm_loss_trajectory` ⇒ byte-equal broadcasts; the latch is
   a deterministic function of seed-reproducible quantities.

6. **Parameter symbol table**: symbols `α`, `β`, `σ`, `τ_panic`,
   `τ_solv`, `τ_stress`, `h`, `bond_mtm_loss(t)`, `allow_returns_flag`,
   `W(0)`, `t`; defaults, valid ranges, and sources listed in §4.7
   (Mechanism Coefficients + Initial Conditions).

#### Coordination Properties

- **Time granularity**: round-based (one tick per depositor action
  round; typically one day in SVB-style scenarios, one hour for
  high-frequency digital-run studies).
- **Feedback loop**: mixed — the α term is a **first-mover
  amplifying** feedback (each withdrawal permanently raises W and
  lowers Solvency); `panic_indicator` is a **regime-crossing
  amplifier** (participant profiles typically weight withdrawals
  higher once W ≥ τ_panic); the `"failed"` latch is an **absorbing
  attractor**; the optional return channel is a **stabilising**
  negative feedback.
- **Information environment**: symmetric common-knowledge — every
  participant sees the identical broadcast including
  `withdrawal_rate_this_round`, which is itself the coordination
  signal (Goldstein-Pauzner design point). Private information lives
  only in participant profiles (e.g., own insurance status).
- **Stochasticity profile**: one Gaussian ε draw per round; no other
  coordinator-side randomness. Latch is deterministic on
  post-transition state. `bond_mtm_loss_trajectory` is an exogenous
  fixed sequence; any stochastic `RateEnvironment` variation is
  external.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants:

| # | Invariant                                                                                                                                            | Enforcement                                                                        |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 1 | `broadcast[t+1].prev_withdrawal_fraction == broadcast[t].withdrawal_fraction` (byte-equal float) AND `broadcast[t+1].prev_solvency_ratio == broadcast[t].solvency_ratio` | §4.6.2 step 9 writes `prev_*` before the corresponding current values          |
| 2 | Every required field in §4.6.0 Outputs is present and non-null                                                                                       | `decide` assertion at emit                                                          |
| 3 | `withdrawal_fraction, solvency_ratio, bond_mtm_loss, haircut_applied ∈ [0, 1]` in every broadcast                                                     | §4.6.2 step 7 clip + step 8 latch                                                   |
| 4 | **One-way regime latch**: once any broadcast has `regime_status == "failed"`, every subsequent broadcast MUST also have `regime_status == "failed"`   | §4.6.2 step 5 short-circuit branch                                                  |
| 5 | **Monotone-non-decreasing W (under normal runs)**: when `allow_returns_flag == false`, `withdrawal_fraction(t+1) ≥ withdrawal_fraction(t)` for every t | §4.6.2 step 7 monotone guard `W_guarded = max(W_raw, W(t))`                        |
| 6 | **Solvency identity**: `solvency_ratio == (1 − withdrawal_fraction) · (1 − bond_mtm_loss)` in every broadcast (to numerical precision)                | §4.6.2 step 7 explicit formula                                                      |
| 7 | **Haircut only post-failure**: `haircut_applied > 0` ⟹ `regime_status == "failed"` in the same broadcast                                              | §4.6.2 step 8 sets `haircut_applied` only in the same atomic write as `regime_status = "failed"` |
| 8 | **Panic-indicator consistency**: `panic_indicator == 1 ⟺ withdrawal_fraction ≥ panic_threshold` in every broadcast                                    | §4.6.2 step 7 explicit indicator computation                                        |
| 9 | `broadcast[t+1].round == broadcast[t].round + 1`                                                                                                     | Set from `observation.round` in `perceive`                                          |
| 10 | Two runs with identical `base_seed`, identical inbound-action sequence, and identical `bond_mtm_loss_trajectory` produce byte-equal broadcasts       | Seeded RNG only + deterministic latch                                               |
| 11 | `regime_status ∈ {"solvent", "stressed", "failed"}` in every broadcast (no other string)                                                              | §4.6.2 step 8 explicit enum branch                                                  |
| 12 | `withdrawal_rate_this_round == withdrawal_fraction − prev_withdrawal_fraction`                                                                       | §4.6.2 step 9 explicit derivation                                                    |

Domain-Specific Invariants:

- **W monotone-non-decreasing (invariant #5)**: distinguishes a
  deposit-run coordinator from price/opinion coordinators. Enforced
  *inside* the coordinator via the `max(W_raw, W(t))` guard (not
  left emergent) because a spurious noise-driven or FP-rounding
  negative move would silently break DD semantics. Guard is disabled
  ONLY when `allow_returns_flag == true`, weakening #5 to
  `withdrawal_fraction ∈ [0, 1]`.
- **Regime latch one-way (invariant #4)**: second distinguishing
  property. `decide` short-circuits when `regime_status(t) ==
  "failed"`; only `prev_*` fields and `round` update.
- **Solvency identity (invariant #6)**: enforced by construction —
  `solvency_ratio` is computed from `W` and `bond_mtm_loss` every
  round; no independent state kept.
- **Haircut fairness (invariant #7)**: single, uniform, one-shot
  application at the moment of failure — never partial, never
  re-applied, never reverted. Post-failure rounds keep
  `haircut_applied == h` (frozen) for analytics.
- **No cross-round leakage**: each history buffer grows by exactly 1
  entry per round.
- **Conservation**: N/A — this coordinator tracks a *fraction* of
  initial deposits, not individual claims. Participant-side balance
  conservation is the profiles' responsibility.

Failure Modes:

| Condition                                                             | Coordinator behaviour                                                            | Broadcast effect                                       |
|-----------------------------------------------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------|
| Zero inbound actions                                                  | Continue; `net_withdraw = net_return = 0`; still evaluate MTM + latch            | Pure noise + MTM move                                  |
| All withdrawers                                                       | Continue                                                                         | Amplifying pressure on W                               |
| All `hold` actions                                                    | Continue; `net_withdraw = 0`                                                     | Pure MTM + noise move                                  |
| `return` action while `allow_returns == false`                        | Count in `num_returners`; do NOT feed `net_return`; do NOT modify W              | Returners logged, W unchanged                          |
| **Panic-cascade coordination failure** (`panic_withdraw` above τ_panic drives solvency below τ_solv in one round) | Continue; latch `regime = "failed"`; apply `haircut = h`                         | `regime = "failed"`, `haircut = h`                     |
| **Solvency-boundary rounding** (`new_solvency` numerically equal to `τ_solv`) | Strict `< τ_solv` compare (equal → still `"stressed"`)                          | Regime remains `"stressed"` at exact boundary          |
| **One-way-latch violation attempt** (`return` after `"failed"`)       | Short-circuit step 5; regime stays `"failed"`; W unchanged                       | Frozen `"failed"` broadcast                            |
| **Bond-MTM-loss non-monotone** (trajectory decreases)                 | Accept as-is (coordinator does NOT enforce MTM monotonicity)                     | Solvency may rise while W remains monotone             |
| **Haircut-fairness violation attempt** (bug applies haircut pre-latch) | Defect; invariant #7 replay test catches it                                     | Correct impls never emit `haircut > 0` outside `"failed"` |
| Invalid `action_type`                                                 | `ValueError` from `perceive`                                                     | Simulation halts, no broadcast                         |
| `intensity` or `share` outside `[0, 1]`                               | `ValueError` from `perceive`                                                     | Simulation halts, no broadcast                         |
| Required extras key missing                                           | `KeyError` from `perceive`                                                       | Simulation halts, no broadcast                         |
| `bond_mtm_loss_trajectory` shorter than run length                    | `IndexError` from `perceive` on first out-of-range round                         | Simulation halts, no broadcast                         |
| `new_W` / `new_solvency` / `haircut` NaN / Inf                        | `ValueError` from `decide`                                                       | Simulation halts (implementation defect)               |
| Scenario driver mutates `bond_mtm_loss` or `allow_returns` mid-run    | Next `perceive` reads new value; log change; current-round transition uses new  | Next broadcast reflects new MTM / return-flag          |
| `HistoryBuffer` disk write fails                                      | Raise from `decide`; do NOT emit stale broadcast                                 | Simulation halts, no broadcast                         |

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter                          | Type  | Default   | Valid Range | Sensitivity | Description                                                    | Impact                                                        | Source                              |
|------------------------------------|-------|-----------|-------------|-------------|----------------------------------------------------------------|---------------------------------------------------------------|-------------------------------------|
| `initial_deposits`                 | float | `173e9`   | `> 0`       | low         | Total deposit stock at round 0 (currency units)                | Scaling only — the transition operates on fractions            | SVB 10-K 2022 (approx. $173B) [Ref 8] |
| `initial_bond_portfolio_value`     | float | `120e9`   | `> 0`       | low         | Book value of the bond portfolio at round 0                    | Scaling only — the transition operates on fractions            | SVB 10-K 2022 [Ref 8]                |
| `initial_withdrawal_fraction`      | float | `0.0`     | `[0, 1]`    | high        | Round-0 withdrawal fraction seed                               | Higher → starting closer to the panic threshold                | Diamond-Dybvig 1983 [Ref 1]          |

#### B. Mechanism Coefficients

| Parameter                    | Type  | Default | Valid Range | Sensitivity | Description                                                    | Impact                                                              | Source                                              |
|------------------------------|-------|---------|-------------|-------------|----------------------------------------------------------------|---------------------------------------------------------------------|-----------------------------------------------------|
| `withdrawal_impact`          | float | `1.0`   | `≥ 0`       | high        | α — withdrawal-fraction move per unit of net withdraw share    | Higher → run rate accelerates faster given the same net withdrawal  | Diamond-Dybvig 1983 [Ref 1]; Iyer-Puri 2012 [Ref 4] |
| `return_impact`              | float | `0.5`   | `≥ 0`       | high        | β — withdrawal-fraction move per unit of net return share       | Higher → reset events reverse more of the run per round             | Farhi-Tirole 2012 [Ref 13]; Fed 1984 [Ref 16]      |
| `noise_std`                  | float | `0.01`  | `≥ 0`       | medium      | σ — Gaussian noise std dev added per round                     | Higher → more idiosyncratic run/hold jitter                        | Depositor-heterogeneity residual                    |
| `panic_threshold`            | float | `0.20`  | `[0, 1]`    | high        | τ_panic — coordination-signal cutoff on W                       | Higher → panic indicator turns on later                             | Goldstein-Pauzner 2005 [Ref 2]; Kelly-Ó Gráda [Ref 7] |
| `solvency_floor`             | float | `0.90`  | `[0, 1]`    | high        | τ_solv — fundamental-signal cutoff on solvency for failure     | Higher → bank fails earlier; lower → bank more resilient           | Rochet-Vives 2004 [Ref 3]; FDIC empirical           |
| `stressed_floor`             | float | `0.95`  | `[0, 1]`    | medium      | τ_stress — intermediate cutoff between solvent and stressed     | Higher → more time in `"stressed"` before failure                   | Scenario config                                     |
| `haircut_fraction`           | float | `0.20`  | `[0, 1]`    | high        | h — pro-rata haircut applied to remaining claims at failure     | Higher → uninsured depositors lose more if they held               | Bennett-Unal 2015 [Ref 14]                          |
| `bond_mtm_loss`              | float | `0.10`  | `[0, 1]`    | high        | Scalar fallback for the exogenous MTM-loss trajectory          | Higher → solvency starts lower; interacts multiplicatively with W  | Jiang et al. 2023 [Ref 8]                            |
| `allow_returns`              | bool  | `false` | `{true, false}` | high    | Gate on the return channel                                     | If `true`, W can decrease (weakens invariant #5); if `false`, monotone | Farhi-Tirole 2012 [Ref 13]                          |

#### C. Structural / Boundary Parameters

| Parameter                       | Type       | Default      | Valid Range | Sensitivity | Description                                                              | Impact                                        | Source        |
|---------------------------------|------------|--------------|-------------|-------------|--------------------------------------------------------------------------|-----------------------------------------------|---------------|
| `bond_mtm_loss_trajectory`      | list[float] or `None` | `None`       | each entry `[0, 1]`; length `≥ total_rounds` | medium | Optional exogenous MTM trajectory; overrides the scalar `bond_mtm_loss` | Higher-value entries push solvency down faster | Scenario config (Jiang et al. 2023 [Ref 8]) |

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range | Sensitivity | Description                              | Impact                              | Source        |
|--------------------------|------|------------|-------------|-------------|------------------------------------------|-------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty   | low         | Root directory for HistoryBuffer spills  | Higher size → more disk footprint   | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`       | low         | HistoryBuffer hot-tier size (entries)    | Higher → more RAM, less disk I/O    | Standardised  |

## Worked Numerical Examples

### Case 1 — Stable-solvent round (small NetWithdraw, W and Solvency both far from thresholds)

System state (round `t = 2`):

- `W(t) = 0.03`, `Solvency(t) = 0.97·0.90 = 0.873`,
  `regime(t) = "solvent"`, `panic_indicator(t) = 0`,
  `haircut_applied(t) = 0.0`.
- Extras: `α = 1.0`, `β = 0.5`, `σ = 0.01`, `τ_panic = 0.20`,
  `τ_solv = 0.90`, `τ_stress = 0.95`, `h = 0.20`,
  `bond_mtm_loss(2) = 0.10`, `allow_returns = false`.
- Inbound (50 depositors): 3 withdrawers (intensity 0.6/0.5/0.4,
  share 0.5/0.4/0.3); 45 holders; 2 returners (ignored because
  `allow_returns == false`).

Calculation:

- `total_withdraw_share = (0.30 + 0.20 + 0.12)/50 = 0.0124`;
  `net_withdraw_fraction = 0.0124`; `net_return = 0` (gated).
- `ε = +0.002`;
  `W_raw = 0.03 + 1.0·0.0124 + 0.002 = 0.0444`;
  monotone guard: `max(0.0444, 0.03) = 0.0444`; clip: `0.0444`.
- `new_solvency = 0.9556·0.90 = 0.86004`;
  `panic_indicator = 0` (0.0444 < 0.20).
- Latch: `0.86004 < τ_stress = 0.95` → `new_regime = "stressed"`
  (with `bond_mtm_loss = 0.10` max solvency is `0.90` so `τ_stress =
  0.95` forces `"stressed"` at t=0 — intentional per Jiang et al.
  2023 SVB Q1 2023 posture).
- `haircut_applied = 0.0` (regime `"stressed"`, not `"failed"`).

Decision:

```json
{"withdrawal_fraction": 0.0444, "prev_withdrawal_fraction": 0.03,
 "withdrawal_rate_this_round": 0.0144, "solvency_ratio": 0.86004,
 "prev_solvency_ratio": 0.873, "bond_mtm_loss": 0.10,
 "regime_status": "stressed", "num_withdrawers": 3, "num_holders": 45,
 "num_returners": 2, "panic_indicator": 0, "haircut_applied": 0.0,
 "round": 2}
```

Invariant checks: #1 `prev == 0.03`; #5 monotone (0.0444 ≥ 0.03);
#6 solvency identity `(1−0.0444)·(1−0.10) = 0.86004`; #7 haircut = 0
while regime `"stressed"`; #8 `panic_indicator = 0` and W < 0.20.

### Case 2 — Partial-run-with-recovery-via-central-bank (returns turned on)

System state (round `t = 5`, prior W = 0.15, MTM = 0.10):

- `W(t) = 0.15`, `Solvency(t) = 0.85·0.90 = 0.765`,
  `regime(t) = "stressed"`, `panic_indicator(t) = 0`,
  `haircut_applied(t) = 0.0`.
- Extras: as Case 1 but `allow_returns = true` (scenario
  `RegulatorAgent` just flipped the flag — Continental-Illinois-style
  FDIC no-loss guarantee).
- Inbound (50 depositors): 5 withdrawers (intensity
  0.3/0.3/0.2/0.2/0.2, share 0.4); 20 holders; 25 returners
  (intensity 0.6, share 0.5).

Calculation:

- `total_withdraw_share = 1.2·0.4/50 = 0.0096`;
  `total_return_share = 25·0.6·0.5/50 = 0.15`;
  `net_withdraw = 0.0096`; `net_return = 0.15` (gate open).
- `ε = −0.003`;
  `W_raw = 0.15 + 0.0096 − 0.075 − 0.003 = 0.0816`;
  monotone guard SKIPPED (`allow_returns == true`); clip: `0.0816`.
- `new_solvency = 0.9184·0.90 = 0.82656`; `panic_indicator = 0`.
- Latch: `0.82656 < τ_stress = 0.95` → `new_regime = "stressed"`
  (run reversed but MTM keeps ratio below stress cutoff);
  `haircut_applied = 0.0`.

Decision:

```json
{"withdrawal_fraction": 0.0816, "prev_withdrawal_fraction": 0.15,
 "withdrawal_rate_this_round": -0.0684, "solvency_ratio": 0.82656,
 "prev_solvency_ratio": 0.765, "bond_mtm_loss": 0.10,
 "regime_status": "stressed", "num_withdrawers": 5, "num_holders": 20,
 "num_returners": 25, "panic_indicator": 0, "haircut_applied": 0.0,
 "round": 5}
```

Observation: `allow_returns == true` deliberately weakens invariant
#5; `withdrawal_rate_this_round` is negative, showing a Farhi-Tirole
reversal. Under the default `allow_returns = false` this scenario is
impossible.

### Case 3 — SVB-style failure with haircut (accelerating run + high MTM)

System state (round `t = 8`, `bond_mtm_loss_trajectory[8] = 0.18`
following a rate shock; W has been climbing but not yet crossed
panic):

- `W(t) = 0.18` (just below τ_panic), `bond_mtm_loss(t) = 0.18`,
  `Solvency(t) = 0.82·0.82 = 0.6724`, `regime(t) = "stressed"`,
  `panic_indicator(t) = 0`, `haircut_applied(t) = 0.0`.
- Extras: as Case 1 defaults but `bond_mtm_loss_trajectory[8] =
  0.18`; `allow_returns = false`.
- Inbound (50 depositors, cascade round): 32 panic_withdrawers
  (intensity 1.0, share 1.0); 12 withdrawers (intensity 0.8, share
  0.9); 6 holders.

Calculation:

- `total_withdraw_share = (32·1.0·1.0 + 12·0.8·0.9)/50 =
  (32 + 8.64)/50 = 0.8128`.
- `ε = +0.005`;
  `W_raw = 0.18 + 1.0·0.8128 + 0.005 = 0.9978`;
  monotone guard: `max(0.9978, 0.18) = 0.9978`; clip: `0.9978`.
- `new_solvency = 0.0022·0.82 = 0.001804`;
  `panic_indicator = 1` (0.9978 ≥ 0.20).
- Latch: `0.001804 < τ_solv = 0.90` AND `R(t) != "failed"` →
  `new_regime = "failed"`; `haircut_applied = 0.20`.

Decision:

```json
{"withdrawal_fraction": 0.9978, "prev_withdrawal_fraction": 0.18,
 "withdrawal_rate_this_round": 0.8178, "solvency_ratio": 0.001804,
 "prev_solvency_ratio": 0.6724, "bond_mtm_loss": 0.18,
 "regime_status": "failed", "num_withdrawers": 44, "num_holders": 6,
 "num_returners": 0, "panic_indicator": 1, "haircut_applied": 0.20,
 "round": 8}
```

Invariant checks: #1 `prev == 0.18` ✓; #4 tested in round 9; #5
monotone ✓; #7 `haircut = 0.20` alongside `regime = "failed"` ✓;
#8 `panic_indicator = 1` and W ≥ 0.20 ✓.

Round 9 post-failure broadcast (regardless of submitted actions —
short-circuit):

```json
{"withdrawal_fraction": 0.9978, "prev_withdrawal_fraction": 0.9978,
 "withdrawal_rate_this_round": 0.0, "solvency_ratio": 0.001804,
 "prev_solvency_ratio": 0.001804, "bond_mtm_loss": 0.18,
 "regime_status": "failed", "num_withdrawers": 0, "num_holders": 0,
 "num_returners": 0, "panic_indicator": 1, "haircut_applied": 0.20,
 "round": 9}
```

Invariant #4 holds — regime remains `"failed"` in every subsequent
round.

### Edge Case — Solvency exactly at floor (τ_solv boundary tie-break)

System state (round `t = 6`):

- `W(t) = 0.09`, `bond_mtm_loss(t) = 0.0110` (contrived to hit the
  tie), `Solvency(t) ≈ 0.91·0.989 ≈ 0.90000` at floor;
  `regime(t) = "stressed"`.
- Extras: `τ_solv = 0.90`, `τ_stress = 0.95`, `allow_returns =
  false`.
- Inbound: none this round (all `hold`).

Calculation:

- `net_withdraw_fraction = 0`; `ε = 0.0` (chosen for the
  illustration).
- `W_raw = 0.09`; monotone guard: `0.09`; clip: `0.09`.
- `new_solvency = 0.91·0.989 = 0.89999` (slightly below the exact
  tie due to double-precision rounding).
- Tie-break: `0.89999 < 0.90` TRUE → `new_regime = "failed"`;
  `haircut_applied = 0.20`.

Decision:

```json
{"withdrawal_fraction": 0.09, "prev_withdrawal_fraction": 0.09,
 "withdrawal_rate_this_round": 0.0, "solvency_ratio": 0.89999,
 "prev_solvency_ratio": 0.90000, "bond_mtm_loss": 0.0110,
 "regime_status": "failed", "num_withdrawers": 0, "num_holders": 50,
 "num_returners": 0, "panic_indicator": 0, "haircut_applied": 0.20,
 "round": 6}
```

Observations: (a) The latch is **strict `<`** — an exact tie at
`τ_solv` keeps regime `"stressed"`; only a strict undershoot
triggers `"failed"`. Implementers MUST use `<`, not `≤`, so
identical-seed replay is deterministic across math libraries with
different FP rounding. (b) The bank can fail even with
`panic_indicator == 0` — low W combined with a large exogenous MTM
loss is sufficient (Rochet-Vives fundamental channel operating
independently of the Goldstein-Pauzner coordination channel).

## Coordinator Verification and Calibration

**Calibration data sources**:

| Symbol             | Source                                                                                                    | Default | Range        |
|--------------------|-----------------------------------------------------------------------------------------------------------|---------|--------------|
| `α`                | Diamond-Dybvig 1983 [Ref 1, §III]; Iyer-Puri 2012 [Ref 4, Table III]                                      | `1.0`   | `[0.5, 1.2]` |
| `β`                | Farhi-Tirole 2012 [Ref 13]; Fed 1984 [Ref 16] on Continental Illinois recovery                            | `0.5`   | `[0.2, 1.0]` |
| `σ`                | Idiosyncratic depositor-heterogeneity residual (default mechanism-dominated)                              | `0.01`  | `[0.0, 0.05]`|
| `τ_panic`          | Goldstein-Pauzner 2005 [Ref 2]; Kelly-Ó Gráda 2000 [Ref 7, Table 4]; Cookson et al. 2023 [Ref 12] (SVB)   | `0.20`  | `[0.15, 0.25]`|
| `τ_solv`           | Rochet-Vives 2004 [Ref 3, §3]; FDIC receivership cluster                                                  | `0.90`  | `[0.90, 0.95]`|
| `τ_stress`         | Scenario-level convention                                                                                 | `0.95`  | `> τ_solv`   |
| `h`                | Bennett-Unal 2015 [Ref 14, Table 2]; FDIC uninsured recovery ≈72%                                         | `0.20`  | `[0.20, 0.40]`|
| `bond_mtm_loss`    | Jiang et al. 2023 [Ref 8, Table 3]; SVB-specific ≈15–20%                                                  | `0.10`  | `[0.05, 0.20]`|

**Expected coordinator behaviour** (defaults, no returns):
`net_withdraw = +0.05`, ε = 0, `W(t) = 0.05`, `bond_mtm_loss = 0.10`
→ W(t+1) = 0.10, solvency = 0.81. `net_withdraw = 0`, ε = 0 →
W(t+1) = W(t) (monotone guard + zero net + zero noise). Any
broadcast with `regime = "failed"` → every subsequent broadcast
retains `regime = "failed"`. Identical `base_seed` + actions +
trajectory → byte-equal broadcasts. `allow_returns == false` +
submitted `return` → W MUST NOT decrease.

**Sanity bounds** (red flags for a broken implementation): any
observed violation of invariants #1–#12 in §4.6.6 flags the
corresponding defect (state-write order, missing field, clip,
regime latch, monotone guard, solvency identity, haircut fairness,
panic-indicator logic, round counter, seed determinism, enum, rate
identity).

### Ablation Hooks

| Ablation name              | Setting                                                 | Hypothesis tested                                                                          | Expected direction                             | Metric                                                                 |
|----------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------|------------------------------------------------------------------------|
| `no-panic-signal`          | `panic_threshold = 1.01`                                | Panic indicator can never fire; cascade dynamics disabled                                  | Slower run trajectories                        | `mean(withdrawal_fraction) at round T` decreases                        |
| `zero-mtm-loss`            | `bond_mtm_loss = 0.0`                                    | Solvency depends only on W; SVB-style dual-channel failure disabled                        | Later regime failure                          | `first_round(regime == "failed")` increases                             |
| `low-solvency-floor`       | `solvency_floor = 0.5`                                   | Bank more resilient; failure requires larger cumulative run                                 | Later regime failure                          | `first_round(regime == "failed")` increases                             |
| `high-noise`               | `noise_std = 0.10`                                       | Idiosyncratic jitter dominates deterministic mechanism                                     | Random-walk-like W trajectory                  | `Var(W(t+1) − W(t))` up an order of magnitude                          |
| `returns-on`               | `allow_returns = true`; feed a `RegulatorAgent`          | Test the Farhi-Tirole reversal channel                                                     | W can decrease post-guarantee                  | `min_over_rounds(withdrawal_rate_this_round) < 0`                       |
| `high-haircut`             | `haircut_fraction = 0.5`                                 | Regulator-cost dominant failure regime                                                     | Uninsured depositor loss doubles at failure    | `haircut_applied` post-failure                                          |
| `mtm-trajectory-shock`     | `bond_mtm_loss_trajectory` step-up at round `t*`         | Test Jiang-style fundamentals shock independent of coordination signal                     | Fail without panic_indicator having fired      | `first_round(regime == "failed") with panic_indicator(t*) == 0`         |
| `cascade-gain`             | Enable coordinator-side `α_effective = α · (1 + p)`      | Move Goldstein-Pauzner cascade from participant side to coordinator side                    | Sharper panic-driven acceleration              | `W(t+1) − W(t)` at panic-latch round                                    |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                                                                          | Notes                                                                                          |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1  | Diamond, D. W., & Dybvig, P. H. (1983). Bank Runs, Deposit Insurance, and Liquidity. *Journal of Political Economy*, 91(3), 401–419. DOI: 10.1086/261155                                                                            | Foundational sequential-service bank-run model (α-term basis; first-mover advantage)            |
| 2  | Goldstein, I., & Pauzner, A. (2005). Demand-Deposit Contracts and the Probability of Bank Runs. *Journal of Finance*, 60(3), 1293–1327. DOI: 10.1111/j.1540-6261.2005.00762.x                                                       | Common-knowledge cascade above panic threshold (τ_panic basis; panic_indicator)                 |
| 3  | Rochet, J.-C., & Vives, X. (2004). Coordination Failures and the Lender of Last Resort: Was Bagehot Right After All? *Journal of the European Economic Association*, 2(6), 1116–1147. DOI: 10.1162/1542476042813841                 | Global-games unique-equilibrium selection (τ_solv basis; one-way regime latch)                  |
| 4  | Iyer, R., & Puri, M. (2012). Understanding Bank Runs: The Importance of Depositor-Bank Relationships and Networks. *American Economic Review*, 102(4), 1414–1445. DOI: 10.1257/aer.102.4.1414                                        | Micro-level bank-run panel data; empirical α calibration                                        |
| 5  | Ennis, H. M., & Keister, T. (2009). Bank Runs and Institutions: The Perils of Intervention. *American Economic Review*, 99(4), 1588–1607. DOI: 10.1257/aer.99.4.1588                                                                | Alternative sunspot-equilibrium multiplicity                                                    |
| 6  | Anderson, R. G., et al. (2018). Bank Panics and Scale Economies. *European Economic Review*, 102, 300–318. DOI: 10.1016/j.euroecorev.2017.12.007                                                                                    | Alternative bounded-rationality depositor-learning model                                        |
| 7  | Kelly, M., & Ó Gráda, C. (2000). Market Contagion: Evidence from the Panics of 1854 and 1857. *American Economic Review*, 90(5), 1110–1124. DOI: 10.1257/aer.90.5.1110                                                              | Empirical panic-threshold calibration (`0.15–0.25`) from 19th-century Irish bank runs           |
| 8  | Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A. (2023). Monetary Tightening and U.S. Bank Fragility in 2023: Mark-to-Market Losses and Uninsured Depositor Runs? *NBER Working Paper 31048*. DOI: 10.3386/w31048                | Empirical bond_mtm_loss calibration; SVB-specific solvency decomposition                        |
| 9  | Diamond, D. W., & Rajan, R. G. (2001). Liquidity Risk, Liquidity Creation, and Financial Fragility: A Theory of Banking. *Journal of Political Economy*, 109(2), 287–327. DOI: 10.1086/319552                                        | Alternative additive solvency decomposition                                                     |
| 10 | Shleifer, A., & Vishny, R. W. (1992). Liquidation Values and Debt Capacity: A Market Equilibrium Approach. *Journal of Finance*, 47(4), 1343–1366. DOI: 10.1111/j.1540-6261.1992.tb04661.x                                          | Alternative fire-sale-price feedback mechanism                                                  |
| 11 | Gorton, G. (1988). Banking Panics and Business Cycles. *Oxford Economic Papers*, 40(4), 751–781. DOI: 10.1093/oxfordjournals.oep.a041885                                                                                            | Alternative announcement-effect regime-switch                                                   |
| 12 | Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2023). Social Media as a Bank Run Catalyst. *Available at SSRN 4422754*. DOI: 10.2139/ssrn.4422754                                                             | Empirical evidence that Twitter-driven common-knowledge disclosure accelerated SVB run          |
| 13 | Farhi, E., & Tirole, J. (2012). Collective Moral Hazard, Maturity Mismatch, and Systemic Bailouts. *American Economic Review*, 102(1), 60–93. DOI: 10.1257/aer.102.1.60                                                             | Return-channel extension (β-term basis)                                                         |
| 14 | Bennett, R. L., & Unal, H. (2015). Understanding the Components of Bank Failure Resolution Costs. *Financial Markets, Institutions & Instruments*, 24(5), 349–389. DOI: 10.1111/fmii.12034                                          | Empirical FDIC uninsured-depositor haircut fraction calibration                                 |
| 15 | Cochrane, J. H. (2023). Silicon Valley Bank Blew Up. Regulators Have Some Explaining to Do. *The Wall Street Journal*, March 12 2023. (Op-ed, cited for policy commentary only ⚠️)                                                   | ⚠️ Type-6 policy commentary on the systemic-risk exception invoked for SVB                     |
| 16 | Board of Governors of the Federal Reserve System (1984). *Annual Report 1984*. Chapter on Continental Illinois Assistance Program.                                                                                                | Empirical evidence for post-guarantee deposit-return magnitudes                                 |
| 17 | Federal Deposit Insurance Corporation (2023). Joint Statement on Silicon Valley Bank and Signature Bank. Press Release PR-19-2023, March 12 2023.                                                                                  | Primary source for the SVB systemic-risk exception                                              |
| 18 | Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. Henry S. King.                                                                                                                                            | Classical lender-of-last-resort doctrine (background for the guarantee-put alternative)         |

## Design Provenance and Versioning

| Field       | Content                                                                              |
|-------------|--------------------------------------------------------------------------------------|
| Market Type | `deposit` — Bank Deposit / Run Market                                                |
| Author      | AgenticFinLab                                                                        |
| Reviewed by | — (pending)                                                                          |
| Created     | 2026-07-16                                                                           |
| Version     | 1.0.0                                                                                |
| Status      | canonical                                                                            |
| Icon        | ![](../agent_images/icons/market/deposit-bank-run-diamond-dybvig.png)                |