# BankingCreditAgent

## Summary

| Field                        | Content                                                                                                                                                                                  |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Banking, Credit, Lending, Depositor, Broker, and Rating Agent                                                                                                                            |
| Family                       | Intermediary / Funding-supply (financial domain)                                                                                                                                         |
| Market Role                  | Provides or withdraws funding/credit-equivalent risk capital, directly determining leverage capacity and balance-sheet liquidity available to other agents.                              |
| Theory Family                | Banking and Credit-Cycle Theory; Financial Accelerator; Leverage Cycle; Coordination-Run Theory; Rating-Inflation Theory                                                                 |
| Merged profiles              | 12 (PrimeBroker1, PrimeBroker2, CounterCyclicalLender, MinskyBorrower, ProCyclicalLender, CreditorPanicker, MBSOriginator, RatingAgency, DeFiLender, BankManager, BondTrader, Depositor) |
| Source scenarios             | ArchegosCollapse, CreditCycle, EuropeanDebtCrisis, GFC2008, LUNACollapse, SVBBankRun                                                                                                     |
| Canonical sub-archetype enum | `bank_mode ∈ {procyclical_lender, countercyclical_lender, minsky_borrower, depositor_run, prime_broker_first, prime_broker_late, mbs_originator, rating_agency}`                         |

## Definition and Goals

`BankingCreditAgent` represents the heterogeneous family of credit-supplying, funding-providing, and rating-issuing intermediaries that collectively determine the leverage and liquidity environment of the simulated market. Its trading behaviour is a proxy for credit extension (buying risk units = expanding balance sheet, selling = deleveraging or run-driven liquidation). Across modes it spans the full pro-cyclical-to-counter-cyclical spectrum, the lender-borrower duality of the Minsky cycle, the first-mover-vs-late-mover liquidation race in prime-broker cascades, the coordination logic of depositor runs, the fee-driven origination pipeline, and the equilibrium rating-inflation behaviour of issuer-paid rating agencies.

**Primary goals:**
1. Reproduce stylised credit-cycle facts: pro-cyclical leverage build-up in booms, sharp deleveraging in busts, hoarding by counter-cyclical lenders, and the Minsky transition from hedge → speculative → Ponzi finance.
2. Produce realistic stress propagation: depositor coordination runs, prime-broker liquidation cascades with first-mover advantage, and sovereign-bank doom-loop dynamics.
3. Carry the credit channel of the financial accelerator (Bernanke-Gertler 1989) by allowing balance-sheet shocks to feed back into asset-price dynamics.
4. Permit ablation of single mechanisms (run, accelerator, leverage cycle, rating inflation) for causal inference.

**Non-goals:**
1. Does NOT model individual loan-level cash flows or term structure; positions in a single risk asset proxy aggregate credit exposure.
2. Does NOT solve a forward-looking Bellman equation; the agent is rule-based with regime-conditioned thresholds, not utility-maximising.
3. Does NOT simulate the central-bank reaction function; macro-prudential responses are exogenous.
4. Does NOT model deposit-insurance equilibria; the depositor-run mode is a coordination heuristic, not a Bayesian-Nash equilibrium.

## Theoretical Foundation

### Theory 1 — Diamond-Dybvig Bank Run

- **Theory/Study**: Diamond, D. W. and Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401–419.
- **Citation+DOI**: https://doi.org/10.1086/261155
- **Core Insight**: Demand-deposit contracts admit two equilibria — a good equilibrium with normal liquidity provision and a bad run equilibrium in which depositors withdraw because they expect others to withdraw, even when the bank is solvent. Runs are coordination failures, not solvency failures.
- **Mathematical Formulation**: Withdraw if expected fraction of depositors running `π_e ≥ π*` where `π*` solves the bank's sequential-service constraint; in the simulation we approximate `π_e` by observed price drawdown and sentiment, triggering full withdrawal when `drawdown < −θ_run`.
- **Empirical Evidence**: Iyer & Puri (2012, AER) document depositor runs at an Indian commercial bank in 2001 conditional on observable distress signals; Goldstein & Pauzner (2005, JF) provide the global-games refinement matching these patterns.
- **Relevance to This Agent**: The `depositor_run` mode encodes the run threshold and the consequent step-function selling of all proxy units.
- **Calibration Source**: Iyer-Puri (2012) withdrawal rates; SVB run telemetry (March 2023, FDIC report).
- **Falsification Conditions**: Threshold-triggered runs are not observed in the data; the depositor-run mode then reduces to a slow drift parameter and the model produces no panic spike.
- **Alternative Theories**: Calomiris-Kahn (1991, AER) — runs as informed monitoring; Goldstein-Pauzner (2005, JF) — global-games unique equilibrium; Allen-Gale (2000, JPE) — contagion through interbank network.

### Theory 2 — Bernanke-Gertler Financial Accelerator

- **Theory/Study**: Bernanke, B. and Gertler, M. (1989). Agency costs, net worth, and business fluctuations. *American Economic Review*, 79(1), 14–31.
- **Citation+DOI**: https://www.jstor.org/stable/1804770
- **Core Insight**: Costly state verification implies that a borrower's external finance premium is a decreasing function of net worth. Adverse shocks to net worth therefore amplify and propagate real shocks: lower net worth → higher cost of credit → less investment → lower asset prices → still lower net worth.
- **Mathematical Formulation**: Lending capacity `L = κ · N`, where `N` is net worth and `κ` is the leverage cap; an asset-price shock `−Δp` reduces `N` by `position · Δp` and forces a quantity adjustment `ΔL = −κ · position · Δp` in the same direction as the shock.
- **Empirical Evidence**: Bernanke-Gertler-Gilchrist (1999, *Handbook of Macroeconomics*) calibrate accelerator strength; Adrian-Shin (2010) document the empirical leverage-asset comovement at investment banks.
- **Relevance to This Agent**: The shared `leverage_max` parameter and net-worth-linked sizing rule mechanise the accelerator across all modes.
- **Calibration Source**: Bernanke-Gertler-Gilchrist (1999) net-worth elasticities; Adrian-Shin (2010) leverage-to-asset slope.
- **Falsification Conditions**: Removing the net-worth-linked sizing yields a model in which adverse shocks do not amplify; comparison with crisis episodes shows excess kurtosis cannot then be reproduced.
- **Alternative Theories**: Kiyotaki-Moore (1997, JPE) — collateral constraints; Holmstrom-Tirole (1997, QJE) — moral-hazard rationing; He-Krishnamurthy (2013, AER) — intermediary asset pricing.

### Theory 3 — Adrian-Shin Pro-cyclical Leverage

- **Theory/Study**: Adrian, T. and Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437.
- **Citation+DOI**: https://doi.org/10.1016/j.jfi.2008.12.002
- **Core Insight**: For market-based intermediaries, leverage is pro-cyclical: balance sheets expand when asset prices rise (because mark-to-market net worth grows faster than the borrowing constraint binds) and contract sharply when prices fall.
- **Mathematical Formulation**: `Δleverage_t = β · Δlog(asset_value_t)` with `β > 0` for broker-dealers; in our model `procyclical_lender` buys `q ∝ +max(r̄, 0)` and sells `q ∝ −max(−r̄, 0)` where `r̄` is the rolling return.
- **Empirical Evidence**: Adrian-Shin (2010) find positive comovement of leverage and total assets at U.S. broker-dealers, 1963–2006; Geanakoplos (2010) extends to housing.
- **Relevance to This Agent**: Drives `procyclical_lender` sizing; opposite sign drives `countercyclical_lender`.
- **Calibration Source**: Adrian-Shin (2010) Figure 4 (leverage-asset slope ≈ 0.6–0.8 for broker-dealers).
- **Falsification Conditions**: If empirical leverage is independent of asset values, pro-cyclical sizing produces no extra volatility above noise.
- **Alternative Theories**: Geanakoplos (2010) — leverage cycle with disagreement; Brunnermeier-Pedersen (2009, RFS) — funding-liquidity spiral; Acharya-Viswanathan (2011, JF) — debt rollover and runs.

### Theory 4 — Minsky Financial Instability Hypothesis

- **Theory/Study**: Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale University Press.
- **Citation+DOI**: https://doi.org/10.12987/9780300188042
- **Core Insight**: Financial structures evolve endogenously through three regimes — hedge finance (cash flows cover principal+interest), speculative finance (cash flows cover interest only), Ponzi finance (cash flows insufficient even for interest). Long stability incentivises greater leverage and migration toward Ponzi finance, sowing the seeds of crisis.
- **Mathematical Formulation**: `target_leverage_t = L₀ + α · t_stable_t`, where `t_stable` is consecutive ticks with `|r_t| < σ_calm`; the borrower buys until `current_leverage = target_leverage` and is forced to delever when calm ends.
- **Empirical Evidence**: Schularick-Taylor (2012, AER) document credit-driven boom-bust cycles in 14 advanced economies, 1870–2008; Jorda-Schularick-Taylor (2013, JMCB) find credit growth predicts crises.
- **Relevance to This Agent**: Drives the `minsky_borrower` mode's monotonic leverage build-up during calm regimes and forced unwind on volatility shock.
- **Calibration Source**: Schularick-Taylor (2012) credit-to-GDP elasticities; Minsky (1986) typology.
- **Falsification Conditions**: If long calm periods do not raise system leverage in the data, the Minsky channel collapses to a noise term.
- **Alternative Theories**: Brunnermeier-Sannikov (2014, AER) — endogenous-risk macroeconomic model; Geanakoplos (2010) — leverage cycle; Bordo-Eichengreen-Klingebiel-Martinez-Peria (2001) — empirical crisis taxonomy.

### Theory 5 — Geanakoplos Leverage Cycle

- **Theory/Study**: Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65.
- **Citation+DOI**: https://doi.org/10.1086/648285
- **Core Insight**: Endogenous collateral haircuts cycle pro-cyclically; in good times haircuts shrink, leverage rises, optimists buy at high prices; in bad times haircuts spike, leverage collapses, prices overshoot downward as optimists are forced out.
- **Mathematical Formulation**: Margin constraint `position · P · h_t ≤ N_t` with haircut `h_t = h_min + φ · 𝟙{regime=stress}`; the counter-cyclical lender accumulates reserves when `r̄ > +θ_boom` and deploys when `r̄ < −θ_bust`.
- **Empirical Evidence**: Geanakoplos (2010) shows margin haircuts on AAA mortgage tranches went from 3% (2006) to 40% (2008); Gorton-Metrick (2012, JFE) document the same in repo.
- **Relevance to This Agent**: Anchors `countercyclical_lender` mode and the `prime_broker_*` haircut-driven liquidation logic.
- **Calibration Source**: Geanakoplos (2010) margin-cycle data; Gorton-Metrick (2012) repo haircuts.
- **Falsification Conditions**: If haircuts are constant across regimes, the leverage cycle is muted and the model must explain crisis amplification through a different channel.
- **Alternative Theories**: Brunnermeier-Pedersen (2009, RFS) — funding-liquidity spiral; Adrian-Shin (2010) — pro-cyclical leverage; He-Krishnamurthy (2013, AER) — intermediary asset pricing.

### Theory 6 — Bolton-Freixas-Shapiro Rating Inflation

- **Theory/Study**: Bolton, P., Freixas, X. and Shapiro, J. (2012). The credit ratings game. *Journal of Finance*, 67(1), 85–111.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2011.01708.x
- **Core Insight**: Under the issuer-pays model, rating agencies have an equilibrium incentive to inflate ratings during booms when investor scrutiny is low, then revise downward sharply when stress reveals errors.
- **Mathematical Formulation**: Rating signal `s_t = θ_true + ε_t + b_t`, where the bias `b_t = b̄ · 𝟙{regime=boom}`; the agent's proxy trade is `q_t = κ · sign(s_t)` with size shrinking in stress.
- **Empirical Evidence**: Griffin-Tang (2012, JF) document AAA-CDO rating inflation 2003–2007; Becker-Milbourn (2011, JFE) link issuer-pays to lower rating quality.
- **Relevance to This Agent**: Drives the `rating_agency` mode's amplification of inflows during the boom and abrupt downgrade-driven outflow during stress.
- **Calibration Source**: Griffin-Tang (2012) AAA-CDO bias estimates; Becker-Milbourn (2011) rating-quality wedge.
- **Falsification Conditions**: If rating bias is zero across regimes, the rating-agency mode collapses to a passive sentiment relay.
- **Alternative Theories**: Skreta-Veldkamp (2009, JME) — ratings shopping; Mathis-McAndrews-Rochet (2009, JME) — reputation cycles; Sangiorgi-Spatt (2017, AERIns) — rating shopping with selective disclosure.

### Theory 7 — Gorton-Metrick Securitised-Banking Run

- **Theory/Study**: Gorton, G. and Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451.
- **Citation+DOI**: https://doi.org/10.1016/j.jfineco.2011.03.016
- **Core Insight**: The 2007–2008 crisis was a wholesale-funding run: repo haircuts on previously safe collateral spiked, forcing dealers to dump assets — a first-mover advantage drives sequential liquidation by counterparties.
- **Mathematical Formulation**: First broker liquidates at threshold `−θ₁` with `θ₁ < θ₂`; second broker liquidates at `−θ₂` after prices have already fallen, suffering greater impact `MS_PB1 < MS_PB2`.
- **Empirical Evidence**: Gorton-Metrick (2012) document repo haircut spikes; Krishnamurthy-Nagel-Orlov (2014, JF) extend to MMF runs; Archegos 2021 (Morgan Stanley vs Credit Suisse loss differential ≈ $4–5 B) is the canonical first-vs-late example.
- **Relevance to This Agent**: Anchors `prime_broker_first` (early threshold ≈ −0.10) and `prime_broker_late` (delayed threshold ≈ −0.15) modes.
- **Calibration Source**: Archegos public filings (2021); Gorton-Metrick (2012) repo-haircut data.
- **Falsification Conditions**: If first-mover advantage is absent in the data, the two prime-broker modes collapse to a single threshold.
- **Alternative Theories**: Brunnermeier-Pedersen (2009, RFS) — funding-liquidity spiral; Diamond-Rajan (2011, QJE) — fear of fire sales; Acharya-Gale-Yorulmazer (2011, JF) — rollover risk.

## Design Purpose and Activation Triggers

| Trigger condition                                      | Activated mode                                          | Effect                                          |
|--------------------------------------------------------|---------------------------------------------------------|-------------------------------------------------|
| `regime ∈ {boom}` AND `rolling_return r̄ > +θ_boom`     | `procyclical_lender`, `mbs_originator`, `rating_agency` | Expand balance sheet / sustain origination flow |
| `regime ∈ {boom}` AND `t_stable > τ_minsky`            | `minsky_borrower`                                       | Build leverage toward `target_leverage`         |
| `regime ∈ {boom}` AND `r̄ > +θ_boom`                    | `countercyclical_lender`                                | Hoard reserves: net SELL pressure               |
| `regime ∈ {stress, panic}` AND `drawdown ∈ (−0.10, 0]` | `prime_broker_first`                                    | Pre-emptive liquidation                         |
| `regime ∈ {stress, panic}` AND `drawdown < −0.15`      | `prime_broker_late`                                     | Forced liquidation at worse prices              |
| `regime ∈ {panic}` AND `drawdown < −θ_run`             | `depositor_run`                                         | Full position unwind (all-or-nothing)           |
| `regime ∈ {stress, panic}` AND `r̄ < −θ_bust`           | `countercyclical_lender`                                | Deploy reserves: net BUY pressure               |
| `<Default>`                                            | `procyclical_lender` (mild boom) or hold                | No change                                       |

**Prerequisite Signals:** Rolling return `r̄` (window `W_r = 20`), drawdown `d_t = (P_t − max_{s≤t} P_s) / max_{s≤t} P_s`, calm-streak counter `t_stable`, regime classifier output `regime ∈ {boom, normal, stress, panic}`.

**Missing-Signal Policy:** If `r̄` or `d_t` is unavailable, default to mode `procyclical_lender` with zero quantity (i.e., hold). If regime classifier is unavailable, derive a fallback regime by binning `d_t`: `boom` if `d_t > −0.02`, `stress` if `d_t ∈ [−0.10, −0.02]`, `panic` if `d_t < −0.10`.

**Deactivation Conditions:** Cooldown `T_cool = 100` ticks after any forced unwind (depositor-run completion or prime-broker liquidation). During cooldown, the agent only emits hold orders. Deactivation also occurs on `equity ≤ 0.10 · equity_init` (insolvency).

Market Contribution by Regime:

| Regime         | Contribution             | Mechanism                                                                                                                                                    |
|----------------|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Boom / Calm    | Destabilising (long-run) | `procyclical_lender`, `mbs_originator`, `rating_agency`, and `minsky_borrower` jointly inflate leverage and supply, planting the seed of the subsequent bust |
| Boom / Calm    | Stabilising (short-run)  | `countercyclical_lender` accumulates reserves; `bank_manager` (low-`κ_cc` variant) absorbs small mispricings                                                 |
| Stress         | Destabilising            | `prime_broker_first` triggers liquidation; `mbs_originator` accelerates dump; `rating_agency` revises ratings down sharply                                   |
| Panic / Crisis | Strongly Destabilising   | `prime_broker_late` forced sells at depressed prices; `depositor_run` mode liquidates entire positions in one tick (Diamond-Dybvig coordination failure)     |
| Recovery       | Stabilising              | `countercyclical_lender` deploys reserves into oversold market; `procyclical_lender` cohort still in cooldown so amplification is muted                      |

Interaction with other agents: supplies the leverage that all leveraged-fund / momentum / arbitrageur agents depend on; the prime-broker liquidation cascade is the principal forced-seller cohort feeding the panic-amplifier loop; the depositor-run cohort transmits sentiment shocks into immediate quantity flows; the rating-agency mode injects pro-cyclical sentiment that amplifies herding agents.

## Behavioral Framework

#### Action Space

| Aspect               | Specification                                                                                          |
|----------------------|--------------------------------------------------------------------------------------------------------|
| Order types allowed  | LIMIT (default), MARKET (forced unwind, depositor run, prime-broker liquidation)                       |
| Price level rule     | LIMIT placed at `mid ± δ_price · σ`; MARKET used when `mode_state ∈ {forced_unwind, run}`              |
| Order quantity rule  | `Q* = sign · κ_mode ·                                                                                  |
| Order lifetime       | `T_life = 1` tick for normal lending flow; `T_life = ∞` (until filled) for forced-unwind market orders |
| Cancellation policy  | Cancel on regime transition that switches the active mode; cancel on cooldown entry                    |
| Inventory constraint | `                                                                                                      |
| Wealth/leverage cap  | `leverage = position · P / equity ≤ leverage_max`; on breach, force unwind 100% over `T_unwind` ticks  |
| Stop-loss/kill rule  | `cum_drawdown < dd_kill = −0.30` ⇒ permanent deactivation; insolvency at `equity ≤ 0.10 · equity_init` |

The agent does NOT use: stop-limit, iceberg, hidden, peg, conditional, or pair-trade order types.

#### Decision Process

1. Observe `(P_t, r̄_t, d_t, t_stable_t, regime_t, equity_t, position_t)`.
2. Determine the active sub-mode via the §3.5 trigger table; ties broken by the `bank_mode` enum default.
3. Compute the mode-specific signal and target quantity (formulas in §3.6.3).
4. Apply leverage and cooldown caps; clip quantity to `[Q_min, Q_max_mode]`.
5. Submit the order with the mode-determined order type (LIMIT or MARKET).
6. Update internal state at end of tick (post-fill update rule in §3.6.4).

#### Mathematical Model

Common signals:
- `r̄_t = (1/W_r) Σ_{i=t−W_r+1..t} r_i`, with `W_r = 20`.
- `d_t = (P_t − P_peak_t) / P_peak_t`, where `P_peak_t = max_{s ≤ t} P_s`.
- `t_stable_t = t_stable_{t−1} + 1` if `|r_t| < σ_calm` else `0`.
- `equity_t = cash_t + position_t · P_t`.
- `leverage_t = position_t · P_t / equity_t`.

Mode-specific decision rules (`κ_mode` is the mode sizing scalar):

`procyclical_lender`:
```
if r̄_t > +θ_boom:  Q* = +κ_pc · r̄_t · equity / P
elif r̄_t < −θ_bust: Q* = −κ_pc · |r̄_t| · |position|
else: Q* = 0
```

`countercyclical_lender`:
```
if r̄_t > +θ_boom:  Q* = −κ_cc · r̄_t · |position|     (hoard: sell)
elif r̄_t < −θ_bust: Q* = +κ_cc · |r̄_t| · cash / P    (deploy: buy)
else: Q* = 0
```

`minsky_borrower`:
```
target_leverage_t = L₀ + α_minsky · min(t_stable_t, τ_max)
if leverage_t < target_leverage_t and regime ∈ {boom, normal}:
    Q* = (target_leverage_t − leverage_t) · equity / P
elif regime ∈ {stress, panic}:
    Q* = −unwind_speed · position    (forced delever)
else: Q* = 0
```

`depositor_run`:
```
if d_t < −θ_run OR sentiment_t < −θ_panic:
    mode_state ← run
    Q* = −position    (sell ALL, single tick MARKET)
else: Q* = 0
```

`prime_broker_first`:
```
if d_t < −0.10:
    Q* = −min(liquidation_speed_pb1 · |position|, |position|)    (MARKET)
else: Q* = 0
```

`prime_broker_late`:
```
if d_t < −0.15:
    Q* = −min(liquidation_speed_pb2 · |position|, |position|)    (MARKET, larger size)
else: Q* = 0
```

`mbs_originator`:
```
if regime ∈ {boom, normal}:
    Q* = −ρ_origination · inventory_t    (steady distribution: net SELL)
elif regime ∈ {stress, panic}:
    Q* = −min(2 · ρ_origination · inventory_t, inventory_t)    (accelerated dump)
```

`rating_agency`:
```
bias_t = b̄ · 𝟙{regime ∈ {boom}} − b_revise · 𝟙{regime ∈ {stress, panic}}
Q* = κ_ra · bias_t · capacity        (proxy: sentiment-amplifying flow)
```

#### Determinism, State, and Update Rule

**Determinism contract:** Given `(P_t, r̄_t, d_t, t_stable_t, regime_t, equity_t, position_t, mode_state_t, RNG_seed)` the output `(action, Q*, T_life)` is a pure function. The only stochastic element is the `Categorical(p_mode)` mixture sampling at agent instantiation; once `bank_mode` is drawn it is fixed for the agent's lifetime.

**State variables:**
- Pre-decide observables: `P_t`, `r̄_t`, `d_t`, `t_stable_t`, `regime_t`, `sentiment_t`.
- Internal: `equity_t`, `position_t`, `cash_t`, `mode_state_t ∈ {active, run, forced_unwind, cooldown, deactivated}`, `cooldown_left_t`, `peak_equity_t`.

**Update rule (post-fill, end of tick t):**
1. Apply fill: `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. Mark to market: `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`.
3. Update peak and drawdown: `peak_equity_{t+1} = max(peak_equity_t, equity_{t+1})`; `cum_drawdown_{t+1} = (equity_{t+1} − peak_equity_{t+1}) / peak_equity_{t+1}`.
4. Update calm streak: `t_stable_{t+1} = t_stable_t + 1` if `|r_{t+1}| < σ_calm` else `0`.
5. Mode-state transitions: `run`/`forced_unwind` → `cooldown` once `position = 0`; `cooldown` → `active` once `cooldown_left = 0`; any state → `deactivated` if `cum_drawdown_{t+1} < dd_kill` or `equity_{t+1} < 0.10 · equity_init`.

## Parameters

| Symbol                  | Name                            | Default     | Range           | Units         | Source                        | Sensitivity | Notes                         |
|-------------------------|---------------------------------|-------------|-----------------|---------------|-------------------------------|-------------|-------------------------------|
| `bank_mode`             | Sub-archetype                   | Categorical | enum (8 modes)  | —             | §3.8 mixture                  | High        | Fixed at instantiation        |
| `θ_boom`                | Boom return threshold           | 0.02        | [0.005, 0.05]   | per tick      | Adrian-Shin (2010)            | Medium      | Triggers pro/counter-cyclical |
| `θ_bust`                | Bust return threshold           | 0.02        | [0.005, 0.05]   | per tick      | Adrian-Shin (2010)            | Medium      | Symmetric default             |
| `θ_run`                 | Depositor-run drawdown          | 0.15        | [0.05, 0.30]    | fraction      | Iyer-Puri (2012); SVB         | High        | Critical for run mode         |
| `θ_panic`               | Sentiment panic threshold       | −0.5        | [−0.8, −0.3]    | std-units     | Goldstein-Pauzner (2005)      | High        | Run mode trigger              |
| `α_minsky`              | Leverage-build slope            | 0.001       | [0.0002, 0.005] | per tick      | Schularick-Taylor (2012)      | High        | Per-tick increment            |
| `L₀`                    | Initial target leverage         | 1.0         | [1.0, 2.0]      | ×             | Calibration                   | Low         | Minsky baseline               |
| `τ_max`                 | Calm-streak cap                 | 500         | [200, 2000]     | ticks         | Minsky (1986)                 | Medium      | Saturation point              |
| `σ_calm`                | Calm-volatility cutoff          | 0.005       | [0.002, 0.015]  | per tick      | Calibration                   | Medium      | Defines `t_stable`            |
| `κ_pc`                  | Pro-cyclical sizing             | 5.0         | [1, 20]         | dimensionless | Adrian-Shin (2010)            | Medium      | Gain on `r̄`                   |
| `κ_cc`                  | Counter-cyclical sizing         | 3.0         | [1, 10]         | dimensionless | Geanakoplos (2010)            | Medium      | Reserve deployment gain       |
| `κ_ra`                  | Rating-agency sizing            | 2.0         | [0.5, 5]        | dimensionless | Bolton-Freixas-Shapiro (2012) | Low         | Bias amplification            |
| `b̄`                     | Boom rating bias                | 0.5         | [0.1, 1.0]      | std-units     | Griffin-Tang (2012)           | Medium      | Inflation magnitude           |
| `b_revise`              | Stress downgrade swing          | 1.0         | [0.5, 2.0]      | std-units     | Griffin-Tang (2012)           | Medium      | Cliff-edge revision           |
| `ρ_origination`         | MBS distribution rate           | 0.02        | [0.005, 0.10]   | per tick      | GFC2008 stylised              | Medium      | Inventory turnover            |
| `liquidation_speed_pb1` | First-mover unwind rate         | 0.50        | [0.20, 1.00]    | fraction/tick | Archegos (2021)               | High        | Faster unwind                 |
| `liquidation_speed_pb2` | Late-mover unwind rate          | 0.30        | [0.10, 0.80]    | fraction/tick | Archegos (2021)               | High        | Slower → worse fills          |
| `unwind_speed`          | Minsky stress unwind            | 0.30        | [0.10, 0.80]    | fraction/tick | Brunnermeier-Pedersen (2009)  | High        | Forced delever                |
| `leverage_max`          | Maximum leverage                | 5.0         | [1.0, 15.0]     | ×             | Adrian-Shin (2010)            | High        | Hard cap                      |
| `dd_kill`               | Permanent-deactivation drawdown | −0.30       | [−0.50, −0.15]  | fraction      | Risk policy                   | High        | Insolvency proxy              |
| `T_cool`                | Cooldown after forced unwind    | 100         | [50, 500]       | ticks         | Calibration                   | Low         | Re-entry delay                |
| `δ_price`               | Limit-price offset              | 0.5         | [0.1, 2.0]      | std-units     | Microstructure                | Low         | LIMIT placement               |

All parameters are deterministic functions of mode + observables once the seed is fixed.

## Population and Heterogeneity

The realised intermediary cohort is drawn from a Categorical mixture over the eight sub-modes. Default mixture (calibrated to match credit-cycle stylised facts and the Archegos 2021 sequence):

`p_mode = {procyclical_lender: 0.20, countercyclical_lender: 0.10, minsky_borrower: 0.15, depositor_run: 0.15, prime_broker_first: 0.05, prime_broker_late: 0.05, mbs_originator: 0.10, rating_agency: 0.05, bank_manager: 0.15}` — note: `bank_manager` is a synonym for a small-`κ_cc` `countercyclical_lender` (SVB Bank Manager profile) absorbed into that mode for parsimony. The published sum is over the 8 canonical modes plus this synonym.

Within each mode, agent-level heterogeneity is introduced via:
- Truncated-Normal draws on `θ_boom`, `θ_bust`, `θ_run` (cv ≈ 20%).
- LogNormal draws on `α_minsky`, `κ_pc`, `κ_cc` (σ_log ≈ 0.30).
- Uniform draws on `liquidation_speed_*` within published ranges.

Population-level invariants:
1. Mean leverage ≤ `leverage_max` × 0.7 in calm regimes.
2. Run-mode cohort size ≥ 5 to avoid degenerate single-agent panic.
3. At least one `prime_broker_first` AND one `prime_broker_late` in any prime-broker scenario to preserve the cascade ordering.

## Worked Numerical Examples

**Example 1 — Pro-cyclical lender in boom.** State: `bank_mode=procyclical_lender, P=110, equity=1,000,000, r̄=+0.025, regime=boom`.
Step 1: `r̄ > θ_boom (0.02)` → expansionary signal.
Step 2: `Q* = +κ_pc · r̄ · equity / P = 5.0 · 0.025 · 1,000,000 / 110 ≈ +1,136 units (LIMIT BUY)`.
Step 3: Cap by `leverage_max · equity / P − |position| = 5 · 1,000,000 / 110 − 0 ≈ 45,454`. Not binding.
Outcome: Submit LIMIT BUY 1,136 @ `mid + 0.5σ`. Net: balance-sheet expansion, pro-cyclical.

**Example 2 — Minsky borrower late in calm.** State: `bank_mode=minsky_borrower, t_stable=400, leverage=2.5, equity=500,000, P=100, regime=normal`.
Step 1: `target_leverage = L₀ + α_minsky · min(t_stable, τ_max) = 1.0 + 0.001 · 400 = 1.4`. Wait — `target=1.4 < leverage=2.5` → no buy; agent holds.
Step 2: revise example with `target=L₀ + α · 400 = 1.0 + 0.005 · 400 = 3.0` (using `α=0.005`). Now `target=3.0 > leverage=2.5` → `Q* = (3.0 − 2.5) · 500,000 / 100 = +2,500 units`.
Outcome: Submit LIMIT BUY 2,500. Net: leverage builds toward Ponzi phase; small volatility shock subsequently triggers `unwind_speed · position` forced sell.

**Example 3 — Depositor run.** State: `bank_mode=depositor_run, P=80, P_peak=100, position=600, sentiment=−0.7`.
Step 1: `d_t = (80 − 100)/100 = −0.20 < −0.15 = −θ_run` AND `sentiment < −θ_panic = −0.5` → both conditions met.
Step 2: `mode_state ← run`; `Q* = −position = −600 (MARKET SELL)`.
Outcome: Full liquidation at MARKET; entire 600 units sold within one tick. Subsequent ticks: cooldown 100 ticks of holds.

**Example 4 — Prime-broker cascade.** Scenario: drawdown deepens from `−0.05 → −0.12 → −0.18` over three ticks.
Tick 1 (`d=−0.05`): both PB1 and PB2 hold (above thresholds).
Tick 2 (`d=−0.12 < −0.10`): PB1 active; `Q*_PB1 = −0.50 · 1,000 = −500 (MARKET)`. PB2 still holds.
Tick 3 (`d=−0.18 < −0.15`): PB2 active; `Q*_PB2 = −0.30 · 1,000 = −300 (MARKET)`, but executes at depressed prices because PB1 has already sold. PB2's average fill price ≈ 4–5% lower than PB1's, reproducing the Archegos loss differential.

**Example 5 — Edge case: counter-cyclical exhaustion.** State: `bank_mode=countercyclical_lender, regime=panic, r̄=−0.05, cash=0, position=200, equity=200·P`.
Step 1: `r̄ < −θ_bust` → deploy reserves: `Q* = +κ_cc · |r̄| · cash / P = 3.0 · 0.05 · 0 / P = 0`.
Outcome: No buy possible — reserves exhausted. Mode is *latent*: even though the trigger fires, capacity is zero. This is the documented failure mode of counter-cyclical buffers when scaled too aggressively in advance of crisis (Geanakoplos 2010 §6).

## Validation and Calibration

**Calibration objective:** Match credit-cycle stylised facts:
1. Pro-cyclical leverage (Adrian-Shin 2010 slope ≈ 0.6–0.8 between leverage and asset value).
2. Run-mode discontinuity (full-position liquidation within ≤ 5 ticks of breach, Iyer-Puri 2012).
3. Prime-broker cost differential (`avg_fill_PB2 − avg_fill_PB1 ≤ −0.04 · P`, Archegos 2021).
4. Minsky leverage build-up (`leverage_T / leverage_0 ≥ 1.5` after `t_stable ≥ 300` ticks, Schularick-Taylor 2012).

**Stylised facts the population must reproduce:**
- Credit-driven boom-bust cycles (Schularick-Taylor 2012).
- Leverage pro-cyclicality at broker-dealers (Adrian-Shin 2010).
- Run-induced drawdown spikes with fast-decay autocorrelation (Diamond-Dybvig 1983).
- Sequential broker liquidation with first-mover advantage (Gorton-Metrick 2012; Archegos 2021).
- Boom rating inflation followed by abrupt downgrade in stress (Griffin-Tang 2012).

**Ablation hooks:**
1. Set `α_minsky = 0` → no Minsky build-up; expected effect: reduced crisis amplitude.
2. Set `θ_run = ∞` → no run mode; expected effect: smoother drawdowns, no panic spike.
3. Set `liquidation_speed_pb2 = liquidation_speed_pb1` → eliminate first-mover advantage; expected effect: equalised broker losses, no cascade timing.
4. Set `b̄ = b_revise = 0` → eliminate rating cycle; expected effect: removed boom-stress sentiment swing.
5. Force `bank_mode ≡ procyclical_lender` → eliminate counter-cyclical buffer; expected effect: more severe drawdown in panic.

**Sensitivity bounds:** `θ_run ∈ [0.05, 0.30]`, `α_minsky ∈ [0.0002, 0.005]`, `liquidation_speed_pb1 − liquidation_speed_pb2 ∈ [0.05, 0.40]` (must be positive to preserve first-mover ordering).

## Academic References

1. Diamond, D. W. & Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401–419. https://doi.org/10.1086/261155
2. Bernanke, B. & Gertler, M. (1989). Agency costs, net worth, and business fluctuations. *American Economic Review*, 79(1), 14–31.
3. Calomiris, C. W. & Kahn, C. M. (1991). The role of demandable debt in structuring optimal banking arrangements. *American Economic Review*, 81(3), 497–513.
4. Kiyotaki, N. & Moore, J. (1997). Credit cycles. *Journal of Political Economy*, 105(2), 211–248. https://doi.org/10.1086/262072
5. Holmstrom, B. & Tirole, J. (1997). Financial intermediation, loanable funds, and the real sector. *Quarterly Journal of Economics*, 112(3), 663–691. https://doi.org/10.1162/003355397555316
6. Allen, F. & Gale, D. (2000). Financial contagion. *Journal of Political Economy*, 108(1), 1–33. https://doi.org/10.1086/262109
7. Bordo, M., Eichengreen, B., Klingebiel, D. & Martinez-Peria, M. S. (2001). Is the crisis problem growing more severe? *Economic Policy*, 16(32), 51–82.
8. Goldstein, I. & Pauzner, A. (2005). Demand-deposit contracts and the probability of bank runs. *Journal of Finance*, 60(3), 1293–1327. https://doi.org/10.1111/j.1540-6261.2005.00762.x
9. Skreta, V. & Veldkamp, L. (2009). Ratings shopping and asset complexity: A theory of ratings inflation. *Journal of Monetary Economics*, 56(5), 678–695. https://doi.org/10.1016/j.jmoneco.2009.04.006
10. Brunnermeier, M. K. & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
11. Adrian, T. & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
12. Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65. https://doi.org/10.1086/648285
13. Acharya, V. V. & Viswanathan, S. (2011). Leverage, moral hazard, and liquidity. *Journal of Finance*, 66(1), 99–138. https://doi.org/10.1111/j.1540-6261.2010.01627.x
14. Diamond, D. W. & Rajan, R. G. (2011). Fear of fire sales, illiquidity seeking, and credit freezes. *Quarterly Journal of Economics*, 126(2), 557–591. https://doi.org/10.1093/qje/qjr012
15. Becker, B. & Milbourn, T. (2011). How did increased competition affect credit ratings? *Journal of Financial Economics*, 101(3), 493–514. https://doi.org/10.1016/j.jfineco.2011.03.012
16. Bolton, P., Freixas, X. & Shapiro, J. (2012). The credit ratings game. *Journal of Finance*, 67(1), 85–111. https://doi.org/10.1111/j.1540-6261.2011.01708.x
17. Iyer, R. & Puri, M. (2012). Understanding bank runs: The importance of depositor-bank relationships and networks. *American Economic Review*, 102(4), 1414–1445. https://doi.org/10.1257/aer.102.4.1414
18. Gorton, G. & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016
19. Schularick, M. & Taylor, A. M. (2012). Credit booms gone bust: Monetary policy, leverage cycles, and financial crises, 1870–2008. *American Economic Review*, 102(2), 1029–1061. https://doi.org/10.1257/aer.102.2.1029
20. Griffin, J. M. & Tang, D. Y. (2012). Did subjectivity play a role in CDO credit ratings? *Journal of Finance*, 67(4), 1293–1328. https://doi.org/10.1111/j.1540-6261.2012.01748.x
21. He, Z. & Krishnamurthy, A. (2013). Intermediary asset pricing. *American Economic Review*, 103(2), 732–770. https://doi.org/10.1257/aer.103.2.732
22. Brunnermeier, M. K. & Sannikov, Y. (2014). A macroeconomic model with a financial sector. *American Economic Review*, 104(2), 379–421. https://doi.org/10.1257/aer.104.2.379
23. Krishnamurthy, A., Nagel, S. & Orlov, D. (2014). Sizing up repo. *Journal of Finance*, 69(6), 2381–2417. https://doi.org/10.1111/jofi.12168
24. Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale University Press. https://doi.org/10.12987/9780300188042

## Design Provenance and Versioning

- **Source skeleton:** [BankingCreditAgent.md (skeleton, v0)](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/examples/AGENT_POOL/ExtractedExampleInvestors/unique/BankingCreditAgent.md) — derived from 12 scenario profiles spanning ArchegosCollapse, CreditCycle, EuropeanDebtCrisis, GFC2008, LUNACollapse, SVBBankRun.
- **Standardisation references:** [agent-design-skill.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-skill.md) (canonical 12-section handbook) and [agent-design-finance.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-finance.md) (finance-domain addendum).
- **Authored:** Batch 2.5 of unique/ standardisation pass.
- **Version:** v1.0 (pilot-depth).
- **Change log:** v1.0 — initial 11-section pilot-depth authoring; eight `bank_mode` sub-archetypes; seven theory blocks with full nine-field structure; Categorical mixture aligned with crisis-scenario stylised facts.
