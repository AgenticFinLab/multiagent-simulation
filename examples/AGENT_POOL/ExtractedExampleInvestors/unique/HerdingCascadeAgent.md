# HerdingCascadeAgent

## Summary

| Field                        | Content                                                                                                                                                                                                                     |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Herding, contagion, cascade, reputation, and social-proof agents                                                                                                                                                            |
| Theory Family                | Information Cascades; Career-Concern / Reputation Herding; Financial Contagion; Crowd / Social-Proof Psychology                                                                                                             |
| Market Role                  | **Destabilising** — once activated, all four sub-modes amplify the prevailing direction and ignore (or under-weight) private signals; cascades create runaway price dynamics until the cascade is broken by external shocks |
| Time Horizon                 | very short to short (1–20 ticks) — herd reaction is reactive to recent public flow                                                                                                                                          |
| Risk Tolerance               | high (career-concern modes are risk-averse only in *deviating* from peers, not in absolute terms)                                                                                                                           |
| Information Asymmetry        | none — agents observe public price flow + cascade-state signal `cascade_count`                                                                                                                                              |
| Determinism                  | mostly deterministic (one Bernoulli engagement draw per tick for `social_proof_follower`)                                                                                                                                   |
| Merged profiles              | 4 (Cascade Follower, Reputation Herder, Contagion Trader, Social Proof Follower — across three scenarios)                                                                                                                   |
| Source scenarios             | AsianFinancialCrisis, HerdingInformation, TulipMania                                                                                                                                                                        |
| Canonical sub-archetype enum | `herd_mode ∈ {cascade_follower, reputation_herder, contagion_trader, social_proof_follower}`                                                                                                                                |

## Definition and Goals

This agent models the **herding / contagion / social-proof / reputation-driven follower** family in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), spanning four merged profiles whose decision input is the *direction of the crowd* rather than private information. The sub-archetypes cover the canonical Bikhchandani-Hirshleifer-Welch (1992) information cascade, the Scharfstein-Stein (1990) reputation-driven career-concern herder, the cross-border contagion trader (Kaminsky-Reinhart 1999), and the historical social-proof / crowd-psychology buyer (Mackay 1841; Shiller 2000).

**Primary goals:**
1. Reproduce the discrete cascade-lock-in dynamic (Bikhchandani et al. 1992): when `cascade_count > θ_cascade`, the agent abandons its private signal and follows the public direction.
2. Reproduce the reputation-herding asymmetry (Scharfstein-Stein 1990): the agent prefers to be "wrong with the consensus" rather than "right alone" — it activates earlier than the cascade lock-in.
3. Reproduce the cross-border contagion channel (Kaminsky-Reinhart 1999): combined deviation + momentum signal that propagates a regional shock.
4. Permit ablation of each channel (cascade vs. reputation vs. contagion vs. social-proof) to isolate which mechanism drives the empirical herding pattern in each scenario.

**Non-goals:**
1. Does NOT solve a forward-looking utility-maximisation problem; herding is reactive, not strategic.
2. Does NOT attempt to distinguish "informed cascade" from "uninformed cascade" — both produce identical order flow given identical observables.
3. Does NOT model the production of `cascade_count` or `peer_position_consensus`; these are exogenous state inputs computed by the simulation environment.
4. Does NOT independently form fundamental views; only the `contagion_trader` mode references the deviation `(P_t − F_t)/F_t` directly.

## Theoretical Foundation

### Theory 1 — Bikhchandani-Hirshleifer-Welch Information Cascades

- **Theory/Study**: Bikhchandani, S., Hirshleifer, D. and Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026.
- **Citation+DOI**: https://doi.org/10.1086/261849
- **Core Insight**: When agents act sequentially and observe predecessors' actions, a cascade can form in which agents rationally ignore their own private signal. Once `cascade_count` of consecutive same-direction actions is observed, the public history outweighs any single private signal, and all subsequent agents follow regardless of their own information.
- **Mathematical Formulation**: If `cascade_count_t > θ_cascade` and `consensus_direction_t = sign(d_t)` (or `sign(r_t)`), emit `Q* = base_size · |signal_t|` in `consensus_direction`. Once locked-in, the agent does not reverse until cascade breaks (i.e., `|cascade_count_t| < θ_cascade_break`).
- **Empirical Evidence**: Bikhchandani-Hirshleifer-Welch (1992); Anderson-Holt (1997, AER DOI 10.1257/aer.87.5.847) — laboratory cascade experiments; Cipriani-Guarino (2014, AEJ-Micro DOI 10.1257/mic.6.4.180) — cascade-fragility experimental evidence.
- **Relevance to This Agent**: Anchors the `cascade_follower` mode; provides the lock-in threshold `θ_cascade`.
- **Calibration Source**: Anderson-Holt (1997); Cipriani-Guarino (2014).
- **Falsification Conditions**: If `θ_cascade = ∞`, no cascade ever forms; agent reduces to private-signal trading (or no trading) — the cascade pattern is silent.
- **Alternative Theories**: Banerjee (1992, QJE DOI 10.2307/2118364) — simple-Bayesian herd model; Avery-Zemsky (1998, AER DOI 10.1257/aer.88.4.724) — multi-dimensional uncertainty cascade-fragility; Park-Sabourian (2011, Econometrica DOI 10.3982/ECTA8602) — herding-with-public-information equilibrium.

### Theory 2 — Scharfstein-Stein Reputation Herding

- **Theory/Study**: Scharfstein, D. S. and Stein, J. C. (1990). Herd behavior and investment. *American Economic Review*, 80(3), 465–479.
- **Citation+DOI**: https://doi.org/10.2307/2006678
- **Core Insight**: When fund-manager compensation is based on relative performance, a manager prefers to fail conventionally rather than succeed unconventionally, because the latter risks being labelled "incompetent" if isolated. This produces herding even when the manager has a strong private contrary signal — a low activation threshold relative to information cascades.
- **Mathematical Formulation**: When `|peer_position_consensus_t| > θ_reputation` (where `θ_reputation < θ_cascade`), emit `Q* = base_size · sign(peer_consensus) · |peer_consensus|`. The agent activates *before* cascade lock-in.
- **Empirical Evidence**: Scharfstein-Stein (1990); Lakonishok-Shleifer-Vishny (1992, JFE DOI 10.1016/0304-405X(92)90023-Q) — pension-fund herd evidence; Wermers (1999, JF DOI 10.1111/0022-1082.00118) — mutual-fund herding; Hirshleifer-Teoh (2003, EFM DOI 10.1111/1468-036X.00207) — herding survey.
- **Relevance to This Agent**: Anchors the `reputation_herder` mode; sets `θ_reputation = 0.5 · θ_cascade` for early activation.
- **Calibration Source**: Lakonishok-Shleifer-Vishny (1992); Wermers (1999).
- **Falsification Conditions**: If `θ_reputation = θ_cascade`, the reputation-herding distinction collapses into pure cascade-following.
- **Alternative Theories**: Trueman (1994, JFI DOI 10.1006/jfin.1994.1004) — analyst-forecast career-concern model; Effinger-Polborn (2001, EER DOI 10.1016/S0014-2921(00)00036-8) — anti-herding for differentiation; Brunnermeier (2001, OUP) — herding survey.

### Theory 3 — Kaminsky-Reinhart Cross-Border Contagion

- **Theory/Study**: Kaminsky, G. L. and Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473–500.
- **Citation+DOI**: https://doi.org/10.1257/aer.89.3.473
- **Core Insight**: Crises propagate across borders through two channels simultaneously: (i) fundamental linkages (trade, finance) and (ii) investor panic / portfolio rebalancing. The composite signal `α · d_t + (1−α) · r_t` captures both: the fundamental gap component and the momentum component of cross-border outflow.
- **Mathematical Formulation**: `signal_t = α_contag · d_t + (1 − α_contag) · r_t`; emit `Q* = base_size · sign(signal) · |signal|` when `|signal| > θ_contag`.
- **Empirical Evidence**: Kaminsky-Reinhart (1999); Forbes-Rigobon (2002, JF DOI 10.1111/0022-1082.00494) — "no contagion, only interdependence" critical re-examination; Bekaert-Harvey-Ng (2005, JBus DOI 10.1086/426519) — emerging-market spillovers; Bae-Karolyi-Stulz (2003, RFS DOI 10.1093/rfs/hhg012) — extreme-return propagation.
- **Relevance to This Agent**: Anchors the `contagion_trader` mode; the `α_contag` parameter controls the deviation-vs-momentum mix.
- **Calibration Source**: Kaminsky-Reinhart (1999); Forbes-Rigobon (2002).
- **Falsification Conditions**: If `α_contag = 0`, agent collapses to pure momentum trader; if `α_contag = 1`, agent collapses to pure value trader. The contagion channel requires both components.
- **Alternative Theories**: Calvo-Mendoza (2000, JIE DOI 10.1016/S0022-1996(99)00040-X) — wake-up-call alternative; Pavlova-Rigobon (2008, RFS DOI 10.1093/rfs/hhm042) — portfolio-rebalancing-channel general-equilibrium; Allen-Gale (2000, JPE DOI 10.1086/262109) — financial-contagion network alternative.

### Theory 4 — Mackay / Shiller Social Proof and Crowd Psychology

- **Theory/Study**: Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. Mackay, C. (1841). *Memoirs of Extraordinary Popular Delusions and the Madness of Crowds*. London: Richard Bentley.
- **Citation+DOI**: ISBN 978-0691050621 (Shiller 2000); ISBN 978-0486432236 (Mackay reprint).
- **Core Insight**: Participation in a speculative trade is itself a signal that "many others believe", and the validity of that signal scales with the *visibility* of the crowd. In a bubble (TulipMania, South-Sea Bubble, dot-com), this produces additional buying pressure beyond what fundamental or trend signals alone would predict.
- **Mathematical Formulation**: `signal_t = γ_proof · social_proof_intensity_t · sign(d_t)`; emit `Q* = base_size · |signal_t|` when `|d_t| > θ_proof_act`. The `social_proof_intensity_t` is exogenous in [0, 1].
- **Empirical Evidence**: Shiller (2000); Hong-Kubik-Stein (2004, JF DOI 10.1111/j.1540-6261.2004.00629.x) — social-interaction and stock participation; Han-Hirshleifer-Walden (2022, RFS DOI 10.1093/rfs/hhac015) — social-transmission bias evidence; Pedersen (2022, JFE DOI 10.1016/j.jfineco.2021.09.005) — game-of-trends.
- **Relevance to This Agent**: Anchors the `social_proof_follower` mode; `γ_proof` scales the crowd-visibility multiplier.
- **Calibration Source**: Hong-Kubik-Stein (2004); Han-Hirshleifer-Walden (2022).
- **Falsification Conditions**: If `γ_proof = 0`, social-proof channel disappears; agent silent in this mode.
- **Alternative Theories**: Akerlof-Shiller (2009 *Animal Spirits*) — narrative-momentum alternative; Pedersen (2022) — game-of-trends self-reinforcing alternative; Bursztyn-Ederer-Ferman-Yuchtman (2014, Econometrica DOI 10.3982/ECTA11991) — peer-effects experimental evidence.

### Theory 5 — Banerjee Simple Model of Herd Behaviour

- **Theory/Study**: Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of Economics*, 107(3), 797–817.
- **Citation+DOI**: 10.2307/2118364
- **Core Insight**: Sequential decision-makers observe predecessors' choices but not their private signals; once early-mover decisions establish a direction, later movers ignore their own signal and follow — generating fragile consensus that can flip on a single contrarian signal.
- **Mathematical Formulation**: Posterior `P(state | history) > P(state | own signal)` once `cascade_count_t > θ_cascade`; agent emits `Q* = sign(consensus_direction) · base_size`.
- **Empirical Evidence**: Anderson & Holt (1997, AER DOI 10.1257/aer.87.5.847) — laboratory cascade experiments; Çelen & Kariv (2004, AER DOI 10.1257/0002828041464461) — distinguishing cascade-vs-conformity.
- **Relevance to This Agent**: Provides the micro-foundation for the `cascade_follower` mode's signal-suppression behaviour.
- **Calibration Source**: Anderson & Holt (1997); Çelen & Kariv (2004) experimental cascade-rate parameters.
- **Falsification Conditions**: If agents maintain own signal even after long predecessor sequences, the cascade prediction fails (no observed conformity).
- **Alternative Theories**: Bayesian aggregation (Aumann 1976) — predicts no cascade if signals fully revealed; rejected by Anderson-Holt evidence.

## Design Purpose and Activation Triggers

| Trigger condition                                    | Activated mode                      | Effect                                                |
|------------------------------------------------------|-------------------------------------|-------------------------------------------------------|
| `cascade_count_t > θ_cascade`                        | `cascade_follower`                  | Trade in `consensus_direction`, ignore private signal |
| `                                                    | peer_position_consensus_t           | > θ_reputation`                                       |
| `                                                    | α_contag · d_t + (1−α_contag) · r_t | > θ_contag`                                           |
| `social_proof_intensity_t > θ_proof_intensity` AND ` | d_t                                 | > θ_proof_act`                                        |
| `<Default>`                                          | any mode                            | NO action                                             |

**Prerequisite Signals:** price `P_t`, fundamental `F_t`, recent return `r_t = (P_t − P_{t−1})/P_{t−1}`, exogenous `cascade_count_t ∈ ℤ`, `peer_position_consensus_t ∈ [−1, +1]`, `social_proof_intensity_t ∈ [0, 1]`.

**Missing-Signal Policy:** If `cascade_count_t` missing, treat as 0. If `peer_position_consensus_t` missing, treat as 0. If `social_proof_intensity_t` missing, treat as 0. If `F_t` missing, fall back to a 200-tick rolling-mean (consistent with NoiseTrader policy).

**Deactivation Conditions:** Wealth-based — if `cash + position · P_t < W_min`, agent stops new entries. Cascade-mode also deactivates when `|cascade_count_t| < θ_cascade_break` (cascade explicitly broken).

Market Contribution by Regime:

| Regime         | Contribution           | Mechanism                                                                                                            |
|----------------|------------------------|----------------------------------------------------------------------------------------------------------------------|
| Calm           | Inactive               | None of the cascade/reputation/contagion thresholds are crossed; agents quiet                                        |
| Trending boom  | Strongly destabilising | Reputation herders activate first; cascade follower locks in once `cascade_count` is reached; social proof amplifies |
| Trending crash | Strongly destabilising | Cascade and reputation modes feed sell flow; contagion mode propagates across markets                                |
| Reversal phase | Mildly destabilising   | Cascade may break (`                                                                                                 |
| Stress / Panic | Strongly destabilising | All four modes co-fire; contagion mode adds cross-market correlation                                                 |

Interaction with other agents: amplifies the `MomentumTrendTrader` flow (consumes their liquidity), counter-acted by `ContrarianReversalInvestor` and `Arbitrageur`, fed by `SocialInformationAgents` cascade-events; `PolicyBackstopAgent` interventions can break the cascade by re-pricing `(P_t, F_t)` so that `cascade_count` resets.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: float (+ long, − short)
- `cash`: float
- `last_consensus_direction`: enum `{−1, 0, +1}`
- `tick_index`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    d_t = (P_t − F_t) / F_t
    r_t = (P_t − P_{t−1}) / P_{t−1}
    cc_t = cascade_count_t
    pc_t = peer_position_consensus_t
    sp_t = social_proof_intensity_t

    if herd_mode == cascade_follower:
        if abs(cc_t) > θ_cascade:
            dir = sign(cc_t)
            Q* = base_size · min(|cc_t| / θ_cascade, q_cap)
            emit MARKET dir of Q*

    if herd_mode == reputation_herder:
        if abs(pc_t) > θ_reputation:
            dir = sign(pc_t)
            Q* = base_size · |pc_t|
            emit MARKET dir of Q*

    if herd_mode == contagion_trader:
        signal = α_contag · d_t + (1 − α_contag) · r_t
        if abs(signal) > θ_contag:
            dir = sign(signal)
            Q* = base_size · |signal|
            emit MARKET dir of Q*

    if herd_mode == social_proof_follower:
        if sp_t > θ_proof_intensity and abs(d_t) > θ_proof_act:
            if Bernoulli(p_engage) == 0: return
            dir = sign(d_t)                              # follow direction of deviation
            Q* = base_size · γ_proof · sp_t
            emit MARKET dir of Q*
```

#### 3.6.3 Cascade-State Update (state input from environment)

```
on tick t (computed by environment, not agent):
    if action_count_in_direction(t, W_cascade) > 0.7 · W_cascade:
        cascade_count_{t+1} = cascade_count_t + 1
    elif action_count_in_direction(t, W_cascade) < −0.7 · W_cascade:
        cascade_count_{t+1} = cascade_count_t − 1
    else:
        cascade_count_{t+1} = cascade_count_t · ρ_decay
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, F_t, r_t, cascade_count_t, peer_position_consensus_t, social_proof_intensity_t, position, cash, herd_mode, RNG_seed)` the output `(action, Q*, T_life)` is a pure function modulo a single `Bernoulli(p_engage)` draw per tick for `social_proof_follower`. Heterogeneity comes from instantiation-time draws on `θ_*, α_contag, γ_proof, base_size`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume, peer counter-party identity, news content, sentiment, narrative-strength, options chain, or own forward P&L. The decision is taken from `(P_t, F_t, r_t, cascade_count_t, peer_position_consensus_t, social_proof_intensity_t)` and the agent's own `(position, cash)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `r_t`, `cascade_count_t`, `peer_position_consensus_t`, `social_proof_intensity_t`.
- Internal: `position`, `cash`, `last_consensus_direction`, `tick_index`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty` (signed).
2. `cash_{t+1} = cash_t − filled_qty · fill_price`.
3. `last_consensus_direction_{t+1} = sign(filled_qty)` (if action taken).
4. `tick_index += 1`.
5. `cascade_count` is updated by the environment per 3.6.3.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                           |
|----------------------|----------------------------------------------------------------|
| Order types allowed  | MARKET (herd reaction is decisive, not patient)                |
| Price level rule     | Cross the spread; no limit price                               |
| Order quantity rule  | Per-mode (see 3.6.2); proportional to signal magnitude         |
| Order lifetime       | One tick (immediate-or-cancel)                                 |
| Cancellation policy  | Cancel-on-fill                                                 |
| Inventory constraint | Soft cap `                                                     |
| Wealth/leverage cap  | `cash + position · P_t ≥ W_min`; agent stops new entries below |
| Stop-loss/kill rule  | Cascade-break (`                                               |

## Parameters

| Symbol              | Name                         | Default | Range         | Units    | Source                     | Sensitivity | Notes                              |
|---------------------|------------------------------|---------|---------------|----------|----------------------------|-------------|------------------------------------|
| `θ_cascade`         | Cascade lock-in threshold    | 5       | [2, 20]       | count    | Bikhchandani et al. (1992) | High        | Min consecutive same-dir actions   |
| `θ_cascade_break`   | Cascade-break threshold      | 2       | [1, 5]        | count    | Cipriani-Guarino (2014)    | Med         | Reset trigger                      |
| `θ_reputation`      | Reputation activation        | 0.30    | [0.10, 0.70]  | unitless | Scharfstein-Stein (1990)   | High        | `< θ_cascade` for early activation |
| `θ_contag`          | Contagion activation         | 0.02    | [0.005, 0.10] | return   | Kaminsky-Reinhart (1999)   | High        | Composite-signal trigger           |
| `α_contag`          | Contagion fundamental weight | 0.50    | [0.0, 1.0]    | weight   | Forbes-Rigobon (2002)      | High        | 0=pure momentum, 1=pure value      |
| `θ_proof_intensity` | Social-proof activation      | 0.50    | [0.20, 0.90]  | unitless | Hong-Kubik-Stein (2004)    | High        | Crowd-visibility cut               |
| `θ_proof_act`       | Social-proof deviation cut   | 0.02    | [0.005, 0.10] | return   | implementation             | Med         | Min `                              |
| `γ_proof`           | Social-proof multiplier      | 1.5     | [0.5, 5.0]    | mult     | Han et al. (2022)          | High        | Crowd-visibility scale             |
| `ρ_decay`           | Cascade-count decay          | 0.95    | [0.80, 0.99]  | rate     | implementation             | Med         | AR(1) decay if no consensus        |
| `W_cascade`         | Cascade-count window         | 10      | [3, 50]       | ticks    | implementation             | Low         | Look-back                          |
| `q_cap`             | Per-tick cap mult            | 3.0     | [1.0, 10.0]   | mult     | implementation             | Med         | Limits cascade explosion           |
| `base_size`         | Per-trade scale              | 400     | [100, 2000]   | shares   | implementation             | High        | Order size unit                    |
| `position_cap`      | Inventory cap                | 5000    | [1000, 50000] | shares   | implementation             | Med         | Soft constraint                    |
| `W_min`             | Min wealth                   | 0       | [−5e4, +5e4]  | currency | implementation             | Low         | Stop-trading floor                 |
| `p_engage`          | Per-tick engagement prob     | 0.80    | [0.10, 1.00]  | prob     | implementation             | Low         | Attention proxy                    |

## Population and Heterogeneity

```yaml
herd_mode_mixture:
  cascade_follower: 0.30
  reputation_herder: 0.30
  contagion_trader: 0.20
  social_proof_follower: 0.20
heterogeneity:
  theta_cascade: Lognormal(ln 5, 0.50)
  theta_reputation: Beta(3, 7)              # mean ≈ 0.30
  alpha_contag: Beta(5, 5)                  # mean ≈ 0.50
  gamma_proof: Lognormal(ln 1.5, 0.50)
  base_size: Lognormal(ln 400, 0.50)
  rho_decay: Beta(95, 5)                    # mean ≈ 0.95
```

The 0.30 fraction for cascade and reputation modes matches Wermers (1999) Table V evidence that ~30 % of mutual-fund managers display detectable career-concern herding. The 0.20 contagion-trader fraction reflects the cross-border-investor share documented in Bekaert-Harvey-Ng (2005).

## Worked Numerical Examples

**Case 1 — Cascade follower locked in (`herd_mode = cascade_follower`)**: `cascade_count_t = +7, θ_cascade = 5, base_size = 400, q_cap = 3.0`.
- `|cc_t| = 7 > 5 = θ_cascade`. `dir = +1`.
- `Q* = 400 · min(7/5, 3.0) = 400 · 1.4 = 560`.
- Action: MARKET buy 560 (locked into upward cascade).

**Case 2 — Reputation herder early activation (`herd_mode = reputation_herder`)**: `peer_position_consensus_t = +0.45, θ_reputation = 0.30, base_size = 400`.
- `|pc_t| = 0.45 > 0.30`. `dir = +1`.
- `Q* = 400 · 0.45 = 180`.
- Action: MARKET buy 180 (activates *before* cascade lock-in).

**Case 3 — Contagion trader composite signal (`herd_mode = contagion_trader`)**: `d_t = −0.04, r_t = −0.02, α_contag = 0.50, base_size = 400, θ_contag = 0.02`.
- `signal = 0.5 · (−0.04) + 0.5 · (−0.02) = −0.030`. `|signal| = 0.030 > 0.020`.
- `Q* = 400 · 0.030 = 12`.
- Action: MARKET sell 12 (cross-border contagion sell).

**Case 4 — Social proof follower in bubble (`herd_mode = social_proof_follower`)**: `social_proof_intensity_t = 0.85, θ_proof_intensity = 0.50, d_t = +0.10, θ_proof_act = 0.02, γ_proof = 1.5, base_size = 400`.
- Both thresholds passed. Bernoulli(0.80) = 1.
- `Q* = 400 · 1.5 · 0.85 = 510`. `dir = +1`.
- Action: MARKET buy 510 (canonical bubble-driving social-proof buy).

**Edge case — Cascade break**: cascade_count_t = +6 (above θ_cascade), but environment reports `cascade_count_{t+1} = +1` because consensus broke. Now `|cc_{t+1}| = 1 < θ_cascade_break = 2`, so the cascade_follower deactivates this tick. No order. This reproduces the known cascade-fragility result of Cipriani-Guarino (2014).

## Validation and Calibration

- **V1 — Cascade lock-in (Theory 1)**: Conditional on `cascade_count_t > θ_cascade`, agent action probability in consensus direction = 1.0; cross-section of cascade durations should match Anderson-Holt (1997) experimental distribution. Ablation: `θ_cascade = ∞`.
- **V2 — Reputation early-activation (Theory 2)**: Mean activation tick of `reputation_herder` should *precede* mean activation tick of `cascade_follower` by a factor of `θ_reputation / θ_cascade ≈ 1/16` (in the population sense). Ablation: `θ_reputation = θ_cascade`.
- **V3 — Contagion correlation (Theory 3)**: Cross-market return correlation rises by 30–50 % during stress with `contagion_trader` active (Bae-Karolyi-Stulz 2003 magnitude). Ablation: deactivate the `contagion_trader` mode.
- **V4 — Social-proof bubble persistence (Theory 4)**: For `social_proof_intensity > 0.50` populations, mean overshoot duration > 50 ticks (Shiller 2000 dot-com magnitude). Ablation: `γ_proof = 0`.
- **V5 — Cascade-fragility (Theory 1, secondary)**: Under perturbation that resets `cascade_count → 0`, all `cascade_follower` agents deactivate within 1 tick; subsequent flow direction reverses (Cipriani-Guarino 2014 cascade-fragility experimental result).

**Ablation Hooks**:
- `θ_cascade = ∞` → disables Theory 1 (cascade channel).
- `θ_reputation = θ_cascade` → disables Theory 2 (reputation early-activation).
- `α_contag = 0` or 1 → degrades Theory 3 (collapses composite signal).
- `γ_proof = 0` → disables Theory 4 (social-proof channel).

## Academic References

1. Bikhchandani, S., Hirshleifer, D. and Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849
2. Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of Economics*, 107(3), 797–817. https://doi.org/10.2307/2118364
3. Anderson, L. R. and Holt, C. A. (1997). Information cascades in the laboratory. *American Economic Review*, 87(5), 847–862. https://doi.org/10.1257/aer.87.5.847
4. Cipriani, M. and Guarino, A. (2014). Estimating a structural model of herd behavior in financial markets. *AEJ: Microeconomics*, 6(4), 180–209. https://doi.org/10.1257/mic.6.4.180
5. Scharfstein, D. S. and Stein, J. C. (1990). Herd behavior and investment. *American Economic Review*, 80(3), 465–479. https://doi.org/10.2307/2006678
6. Lakonishok, J., Shleifer, A. and Vishny, R. W. (1992). The impact of institutional trading on stock prices. *Journal of Financial Economics*, 32(1), 23–43. https://doi.org/10.1016/0304-405X(92)90023-Q
7. Wermers, R. (1999). Mutual fund herding and the impact on stock prices. *Journal of Finance*, 54(2), 581–622. https://doi.org/10.1111/0022-1082.00118
8. Hirshleifer, D. and Teoh, S. H. (2003). Herd behaviour and cascading in capital markets: A review and synthesis. *European Financial Management*, 9(1), 25–66. https://doi.org/10.1111/1468-036X.00207
9. Kaminsky, G. L. and Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473
10. Forbes, K. J. and Rigobon, R. (2002). No contagion, only interdependence: Measuring stock market comovements. *Journal of Finance*, 57(5), 2223–2261. https://doi.org/10.1111/0022-1082.00494
11. Bae, K.-H., Karolyi, G. A. and Stulz, R. M. (2003). A new approach to measuring financial contagion. *Review of Financial Studies*, 16(3), 717–763. https://doi.org/10.1093/rfs/hhg012
12. Pavlova, A. and Rigobon, R. (2008). The role of portfolio constraints in the international propagation of shocks. *Review of Financial Studies*, 21(3), 1139–1180. https://doi.org/10.1093/rfs/hhm042
13. Hong, H., Kubik, J. D. and Stein, J. C. (2004). Social interaction and stock-market participation. *Journal of Finance*, 59(1), 137–163. https://doi.org/10.1111/j.1540-6261.2004.00629.x
14. Han, B., Hirshleifer, D. and Walden, J. (2022). Social transmission bias and investor behavior. *Review of Financial Studies*, 35(5), 2093–2138. https://doi.org/10.1093/rfs/hhac015
15. Avery, C. and Zemsky, P. (1998). Multidimensional uncertainty and herd behavior in financial markets. *American Economic Review*, 88(4), 724–748. https://doi.org/10.1257/aer.88.4.724

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/HerdingCascadeAgent.md` (legacy); four merged scenario profiles from `AsianFinancialCrisis`, `HerdingInformation` (×2), `TulipMania`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 5.1 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
