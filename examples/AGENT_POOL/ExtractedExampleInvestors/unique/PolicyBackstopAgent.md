# PolicyBackstopAgent

## Summary

| Field                        | Content                                                                                                                                                      |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Regulators, central banks, policy defenders, and rescue/backstop agents                                                                                      |
| Theory Family                | Macro (lender-of-last-resort, currency-crisis models); Limits to Arbitrage (sovereign-credible-backstop); Microstructure (deep-pocket counter-flow)          |
| Market Role                  | **Stabilising** — credible deep-pocket counter-flow that can extinguish self-fulfilling runs and currency-peg attacks once intervention is announced         |
| Time Horizon                 | event-conditional (only active in stress)                                                                                                                    |
| Risk Tolerance               | n/a (mandate-driven, not P&L-driven)                                                                                                                         |
| Information Asymmetry        | none (uses public price + macro indicators); but commitment / credibility is partial                                                                         |
| Determinism                  | mostly deterministic (one Bernoulli credibility-success draw per intervention attempt)                                                                       |
| Merged profiles              | 7 (PegDefender, CentralBankDefender, ECBIntervenor, IMFRescuer, Regulator (×2), CentralBank-Coordinator — across seven scenarios)                            |
| Source scenarios             | AsianFinancialCrisis, CurrencyCrisis, EuropeanDebtCrisis, GFC2008, LTCMCollapse, SVBBankRun, SorosPound                                                      |
| Canonical sub-archetype enum | `policy_mode ∈ {peg_defender_fx, central_bank_lolr, ecb_whatever_it_takes, imf_rescuer, prudential_regulator, deposit_guarantee, central_bank_coordination}` |

## Definition and Goals

This agent models the **policy backstop / regulator / central-bank / rescue-mechanism** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of public-sector or quasi-public agents whose mandate is to extinguish self-fulfilling runs, defend a currency peg, restore liquidity in a fire-sale episode, or coordinate a private-sector rescue. The seven merged profiles span the FX-peg defender (Krugman 1979; Obstfeld 1996), the lender-of-last-resort central bank (Bagehot 1873; Diamond-Dybvig 1983), the credible "whatever-it-takes" euro-area backstop (Draghi 2012; De Grauwe-Ji 2013), the IMF deep-pocket-but-slow rescuer (Corsetti-Pesenti-Roubini 1999), the macroprudential regulator (Brunnermeier-Crockett-Goodhart-Persaud-Shin 2009), the deposit guarantor (Diamond-Dybvig 1983), and the LTCM-1998-style coordination central bank.

**Primary goals:**
1. Reproduce the mechanism by which a credible public-sector backstop extinguishes a self-fulfilling run (Diamond-Dybvig 1983) or a second-generation currency-crisis attack (Obstfeld 1996; Eichengreen-Rose-Wyplosz 1995).
2. Produce the asymmetric "deep-pockets, slow-trigger" pattern of IMF programs (Corsetti-Pesenti-Roubini 1999): a high deviation threshold and a commensurately large response.
3. Capture the credibility-conditional dimension of central-bank intervention — not all announcements succeed; success is conditional on perceived commitment (Eichengreen-Rose-Wyplosz 1995).
4. Permit ablation of single mechanisms (deep pockets vs. credibility vs. trigger latency) to isolate which channel matters per scenario.

**Non-goals:**
1. Does NOT solve a forward-looking optimal-policy problem; intervention rules are reactive deviation thresholds.
2. Does NOT model fiscal financing of intervention; the agent has finite `firepower_K` capacity.
3. Does NOT model coordinated cross-jurisdictional response beyond the implicit `coordination_intensity` parameter.
4. Does NOT directly produce announcement effects on expectations of OTHER agents; the announcement is implicit in the order flow that other agents observe.

## Theoretical Foundation

### Theory 1 — Bagehot Lender-of-Last-Resort

- **Theory/Study**: Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. London: Henry S. King. Diamond, D. W. and Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401–419.
- **Citation+DOI**: ISBN N/A (1873) ; https://doi.org/10.1086/261155
- **Core Insight**: In a banking panic, lend freely against good collateral at a penalty rate (Bagehot's dictum). The credible commitment to provide unlimited liquidity is itself sufficient to extinguish a self-fulfilling run, because investors who would otherwise withdraw stay put once they observe the backstop.
- **Mathematical Formulation**: When deviation `d_t = (P_t − F_t)/F_t < − θ_lolr`, intervene with `Q* = + κ_lolr · |d_t| · firepower_K / P_t`. Firepower is depleted: `K_{t+1} = K_t − |Q* · P_t|`.
- **Empirical Evidence**: Friedman-Schwartz (1963) US monetary history; Bordo (1990, FRB-StL) cross-country LOLR effectiveness; Reinhart-Rogoff (2009, AER DOI 10.1257/aer.98.2.339) — banking crises history.
- **Relevance to This Agent**: Anchors the `central_bank_lolr` and `central_bank_coordination` modes; defines the "lend freely" rule.
- **Calibration Source**: Friedman-Schwartz (1963); Bordo (1990); Reinhart-Rogoff (2009).
- **Falsification Conditions**: If `firepower_K = 0`, intervention is impossible and the LOLR mechanism is mute; runs proceed unchecked.
- **Alternative Theories**: Goodfriend-King (1988, FRB-Richmond) — open-market operations as substitute for direct LOLR; Allen-Gale (2000, JPE DOI 10.1086/262109) — financial-contagion network alternative; Rochet-Vives (2004, JEEA) — coordination-failure interpretation.

### Theory 2 — Obstfeld Self-Fulfilling Currency Crises

- **Theory/Study**: Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3–5), 1037–1047. Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311–325.
- **Citation+DOI**: https://doi.org/10.1016/0014-2921(95)00111-5 ; https://doi.org/10.2307/1991793
- **Core Insight**: A currency peg can collapse for two distinct reasons. In the Krugman first-generation model, exhaustion of reserves produces an inevitable attack as fundamentals deteriorate. In the Obstfeld second-generation model, the peg is sustainable but multiple equilibria exist: a coordinated attack can break the peg even when fundamentals are sound. Credible defence — large reserves and a high-cost reaction function — can shift the equilibrium back to the no-attack state.
- **Mathematical Formulation**: Defender intervenes when `s_t < (1 − θ_peg) · s_central`, buying domestic currency: `Q* = κ_def · (s_central − s_t) · firepower_FX_K`. Reserve depletion: `K_FX_{t+1} = K_FX_t − |Q* · s_t|`. Credibility success: `Bernoulli(p_credibility)`.
- **Empirical Evidence**: Eichengreen-Rose-Wyplosz (1995, EP DOI 10.1111/j.1468-0327.1995.tb00038.x) ERM episode; Kaminsky-Reinhart (1999, AER DOI 10.1257/aer.89.3.473) twin-crisis evidence; 1992 ERM exit and 1997-98 Asian crisis case studies.
- **Relevance to This Agent**: Anchors the `peg_defender_fx` mode; provides the credibility-conditional intervention.
- **Calibration Source**: Eichengreen-Rose-Wyplosz (1995); Kaminsky-Reinhart (1999).
- **Falsification Conditions**: If `p_credibility = 0`, defender's flow is consumed but yields no equilibrium-shifting effect; the peg breaks regardless.
- **Alternative Theories**: Morris-Shin (1998, AER DOI 10.1257/aer.88.3.587) — global-games refinement that selects unique equilibrium; Jeanne (2000) — escape-clause model; Drazen (2000) — political-economy interpretation.

### Theory 3 — Draghi / De Grauwe-Ji Whatever-It-Takes Backstop

- **Theory/Study**: De Grauwe, P. and Ji, Y. (2013). Self-fulfilling crises in the Eurozone: An empirical test. *Journal of International Money and Finance*, 34, 15–36. (Draghi, M. (2012). London speech, "whatever it takes", *not journal-published*.)
- **Citation+DOI**: https://doi.org/10.1016/j.jimonfin.2012.11.003
- **Core Insight**: A credible commitment by a deep-pocketed central bank to backstop sovereign bonds removes the multiple-equilibria region in spreads. Draghi's July 2012 speech was followed by a sharp compression of peripheral spreads even though no actual purchases were initially required, demonstrating the announcement-effect channel.
- **Mathematical Formulation**: Trigger when `bond_spread_t > θ_spread`; intervention `Q* = κ_ecb · (spread − θ_spread) · firepower_BOND_K / P_t`. Announcement effect: spreads compress immediately by `Δ_announce` independent of realised purchases (modelled as flow modifier).
- **Empirical Evidence**: De Grauwe-Ji (2013) Tables 1–4 — sovereign-spread regressions before/after Draghi speech; Krishnamurthy-Nagel-Vissing-Jorgensen (2018, JF) — ECB program evidence; Altavilla-Carboni-Motto (2021, JME) — ECB-asset-purchase pricing.
- **Relevance to This Agent**: Anchors the `ecb_whatever_it_takes` mode; provides the credibility-induced spread compression.
- **Calibration Source**: De Grauwe-Ji (2013); Krishnamurthy et al. (2018).
- **Falsification Conditions**: If `θ_spread = ∞`, mode is inactive; spreads should not show structural compression in the simulation.
- **Alternative Theories**: Eser-Schwaab (2016, JFinEcon) — flow channel of ECB asset purchases; Ghysels-Idier-Manganelli-Vergote (2017, MS) — high-frequency identification; Christensen-Krogstrup (2019, EJ) — reserve-effect channel.

### Theory 4 — Corsetti-Pesenti-Roubini IMF Rescue

- **Theory/Study**: Corsetti, G., Pesenti, P. and Roubini, N. (1999). What caused the Asian currency and financial crisis? *Japan and the World Economy*, 11(3), 305–373.
- **Citation+DOI**: https://doi.org/10.1016/S0922-1425(99)00019-5
- **Core Insight**: IMF programs in 1997–98 displayed a "deep pockets, slow trigger" pattern: very large support packages were eventually deployed, but only after substantial currency depreciation, leading to widespread criticism that intervention was too late to prevent macroeconomic damage. The slow-trigger reflects political-economy constraints and conditionality requirements rather than absence of resources.
- **Mathematical Formulation**: Trigger `if d_t < −θ_imf` (where `θ_imf > θ_lolr` — slow trigger); intervention size `Q* = κ_imf · |d_t| · firepower_IMF_K / P_t` with very large `κ_imf`.
- **Empirical Evidence**: Corsetti-Pesenti-Roubini (1999); Bordo-Schwartz (2000) US Treasury Blueprint; Ghosh et al. (2002, IMF) review of Asian-crisis programs.
- **Relevance to This Agent**: Anchors the `imf_rescuer` mode; sets `θ_imf = 0.05` (vs. `θ_lolr = 0.02` for fast-trigger LOLR).
- **Calibration Source**: Corsetti et al. (1999); IMF program-size historical data.
- **Falsification Conditions**: If `θ_imf = θ_lolr`, slow-trigger pattern disappears; cross-section of intervention magnitudes should match the IMF historical scale.
- **Alternative Theories**: Sachs (1995, FAJ) — Mexican peso crisis early-intervention; Mussa (2002) — IMF self-critique; Eichengreen-Mody-Nedeljkovic-Sarno (2012, JIMF) — IMF program effectiveness.

### Theory 5 — Brunnermeier-Crockett-Goodhart-Persaud-Shin Macroprudential Regulation

- **Theory/Study**: Brunnermeier, M. K., Crockett, A., Goodhart, C. A. E., Persaud, A. and Shin, H. S. (2009). *The fundamental principles of financial regulation*. Geneva Reports on the World Economy 11. ICMB / CEPR.
- **Citation+DOI**: ISBN 978-1-907142-04-5 ; companion paper Goodhart (2008) FMG-LSE Working Paper.
- **Core Insight**: Microprudential regulation focused on individual-firm risk fails to internalise systemic externalities. Macroprudential tools (countercyclical capital buffers, leverage caps, position limits) are required to address fire-sale, contagion, and procyclicality channels. The regulator's role is to apply system-wide constraints when systemic risk indicators spike.
- **Mathematical Formulation**: When `systemic_stress_t > θ_macropru`, intervene to relieve fire-sale pressure: `Q* = κ_pru · stress · firepower_MP_K / P_t`. Probabilistic activation `Bernoulli(p_intervention)` reflecting political-economy decision lag.
- **Empirical Evidence**: Goodhart (2008); Cerutti-Claessens-Laeven (2017, JFS) on macroprudential-tool effectiveness; Kashyap-Stein (2004, NBER) on countercyclical capital.
- **Relevance to This Agent**: Anchors the `prudential_regulator` and `deposit_guarantee` modes; provides the systemic-stress-conditional activation.
- **Calibration Source**: Goodhart (2008); Cerutti et al. (2017).
- **Falsification Conditions**: If `p_intervention = 0` or `θ_macropru = ∞`, the regulator is silent and the systemic-stress channel is unaddressed.
- **Alternative Theories**: Borio (2014, JBF) — alternative cyclical-versus-structural frame; Acharya-Pedersen-Philippon-Richardson (2017, RFS) — systemic-risk contributions framework; Adrian-Brunnermeier (2016, AER DOI 10.1257/aer.20120555) — CoVaR.

### Theory 6 — He-Krishnamurthy Intermediary Asset Pricing

- **Theory/Study**: He, Z. and Krishnamurthy, A. (2013). Intermediary asset pricing. *American Economic Review*, 103(2), 732–770.
- **Citation+DOI**: https://doi.org/10.1257/aer.103.2.732
- **Core Insight**: Asset prices in stress are determined by the equity capital of leveraged intermediaries rather than by household marginal utility. A central-bank intervention that re-capitalises intermediaries (via direct asset purchases or LOLR) restores risk-bearing capacity and re-anchors prices to fundamentals.
- **Mathematical Formulation**: Re-capitalisation pulse: `K_intermediary_{t+1} = K_intermediary_t + transfer_size`; equilibrium price `P_t = F_t · g(K_intermediary_t)` with `g` increasing.
- **Empirical Evidence**: He-Krishnamurthy (2013); Adrian-Boyarchenko (2018, RoF); Haddad-Muir (2021, JF) — intermediary capital and risk premia.
- **Relevance to This Agent**: Provides the theoretical justification for why backstop flow re-prices assets even at modest size: the agent's flow is targeted at intermediaries (or proxied by direct purchases that reduce intermediary balance-sheet stress).
- **Calibration Source**: He-Krishnamurthy (2013); Haddad-Muir (2021).
- **Falsification Conditions**: If the simulation's price impact does not respond to backstop flow magnitude in a non-linear fashion in stress, the intermediary-amplification channel is inactive.
- **Alternative Theories**: Brunnermeier-Sannikov (2014, AER) — financial accelerator continuous-time model; Garleanu-Pedersen (2011, RFS) — margin-CAPM; Caballero-Krishnamurthy (2008, JF DOI 10.1111/j.1540-6261.2008.01390.x) — flight-to-quality.

## Design Purpose and Activation Triggers

| Trigger condition                                                | Activated mode              | Effect                           |
|------------------------------------------------------------------|-----------------------------|----------------------------------|
| `s_t < (1 − θ_peg) · s_central`                                  | `peg_defender_fx`           | BUY domestic currency            |
| Banking-sector run AND `d_t < −θ_lolr`                           | `central_bank_lolr`         | BUY against good collateral      |
| Sovereign-spread `> θ_spread`                                    | `ecb_whatever_it_takes`     | BUY peripheral bonds             |
| `d_t < −θ_imf` (high threshold)                                  | `imf_rescuer`               | Large support package            |
| `systemic_stress_t > θ_macropru` AND `Bernoulli(p_intervention)` | `prudential_regulator`      | Targeted relief flow             |
| Deposit run flag                                                 | `deposit_guarantee`         | BUY backstop, freeze withdrawals |
| LTCM-style coordination event                                    | `central_bank_coordination` | Coordinated counterparty rescue  |
| `<Default>`                                                      | any mode                    | NO action (idle)                 |

**Prerequisite Signals:** price `P_t`, fundamental `F_t`, FX rate `s_t`, sovereign spread `bond_spread_t`, systemic-stress indicator `stress_t` (e.g., aggregate `cum_drawdown`, VaR breach count, deposit-flow proxy), banking-run flag.

**Missing-Signal Policy:** If `F_t` missing, fall back to long-run mean (e.g., 200-tick rolling). If FX or spread missing, deactivate the corresponding mode. If `stress_t` missing, set to 0 (no intervention).

**Deactivation Conditions:** Permanent deactivation when `firepower_K_remaining = 0`. Cooldown `T_cool = 50` ticks after each intervention pulse to model decision-lag and political-economy friction.

Market Contribution by Regime:

| Regime          | Contribution              | Mechanism                                                                       |
|-----------------|---------------------------|---------------------------------------------------------------------------------|
| Calm            | Inactive                  | All thresholds far from triggering; no flow                                     |
| Trending boom   | Inactive                  | Intervention strictly conditional on stress; booms are not stressed             |
| Trending crash  | Stabilising               | LOLR / regulator activate; counter-flow magnitude proportional to `firepower_K` |
| Stress / Panic  | Strongly stabilising      | Coordinated activation across multiple modes (LOLR + macroprudential + ECB)     |
| Currency-attack | Stabilising (conditional) | Peg defender; success conditional on `Bernoulli(p_credibility)`                 |

Interaction with other agents: counter-flow against `MacroCurrencySovereignTrader.peg_attacker` and `LeveragedFundInvestor.forced_unwind` flows; restores risk-bearing capacity that `MarketMakerLiquidityAgent` had withdrawn during stress; complements `Arbitrageur` whose convergence trade benefits from announcement-induced spread compression.

## Behavioural Framework

#### 3.6.1 State Variables

- `firepower_K`: float, remaining intervention capacity
- `firepower_K_initial`: float, starting capacity
- `last_intervention_tick`: integer
- `cooldown_ticks`: integer
- `mode_state`: enum `{idle, intervening, cooldown, exhausted}`
- `cumulative_intervention`: float
- `credibility_score`: float ∈ [0, 1] (updated post-intervention)

#### 3.6.2 Decision Rule

```
on tick t:
    if mode_state == exhausted: return
    if cooldown_ticks > 0: cooldown_ticks -= 1; return

    if policy_mode == peg_defender_fx:
        if s_t < (1 − θ_peg) · s_central:
            credible = Bernoulli(p_credibility)
            if credible:
                Q* = κ_def · (s_central − s_t) · firepower_K / s_t
                emit MARKET buy of domestic currency
                firepower_K -= Q* · s_t
                cooldown_ticks ← T_cool
            return

    if policy_mode == central_bank_lolr:
        if banking_run_flag and d_t < −θ_lolr:
            Q* = κ_lolr · |d_t| · firepower_K / P_t
            emit MARKET buy
            firepower_K -= Q* · P_t
            cooldown_ticks ← T_cool

    if policy_mode == ecb_whatever_it_takes:
        if bond_spread_t > θ_spread:
            Q* = κ_ecb · (spread − θ_spread) · firepower_K / P_t
            emit MARKET buy
            firepower_K -= Q* · P_t
            cooldown_ticks ← T_cool

    if policy_mode == imf_rescuer:
        if d_t < −θ_imf:                              # slow / high threshold
            Q* = κ_imf · |d_t| · firepower_K / P_t
            emit MARKET buy
            firepower_K -= Q* · P_t
            cooldown_ticks ← T_cool_imf               # longer cool-down

    if policy_mode == prudential_regulator:
        if systemic_stress_t > θ_macropru and Bernoulli(p_intervention):
            Q* = κ_pru · systemic_stress_t · firepower_K / P_t
            emit MARKET buy
            firepower_K -= Q* · P_t
            cooldown_ticks ← T_cool

    if policy_mode == deposit_guarantee:
        if deposit_run_flag:
            emit support_signal (no order, but flag for downstream agents)
            cooldown_ticks ← T_cool

    if policy_mode == central_bank_coordination:
        if coordination_event_flag and d_t < −θ_lolr:
            Q* = κ_coord · |d_t| · firepower_K / P_t
            emit MARKET buy (coordinated)
            firepower_K -= Q* · P_t
            cooldown_ticks ← T_cool

    if firepower_K ≤ 0: mode_state ← exhausted
```

#### 3.6.3 Credibility Update

```
after each intervention:
    if intervention_succeeded (price reverts within T_eval ticks by ≥ ε):
        credibility_score ← min(1.0, credibility_score + δ_credit)
    else:
        credibility_score ← max(0.0, credibility_score − δ_credit)
    p_credibility ← credibility_score   # state-dependent for next tick
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, F_t, s_t, bond_spread_t, systemic_stress_t, banking_run_flag, deposit_run_flag, firepower_K, credibility_score, mode_state, RNG_seed)` the output `(action, Q*, T_life)` is a pure function modulo a single `Bernoulli(p_credibility)` draw per intervention attempt for `peg_defender_fx` and a single `Bernoulli(p_intervention)` draw per tick for `prudential_regulator`. Heterogeneity comes from instantiation-time draws on `θ_*, κ_*, p_credibility_initial, firepower_K_initial`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume, peer counter-party identity, news content, sentiment, social-graph signals, options chain, or own P&L. The decision is taken from `(P_t, F_t, s_t, bond_spread_t, systemic_stress_t, run-flags)` plus internal capacity state alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `s_t`, `bond_spread_t`, `systemic_stress_t`, `banking_run_flag`, `deposit_run_flag`, `coordination_event_flag`.
- Internal: `firepower_K`, `credibility_score`, `cumulative_intervention`, `mode_state`, `cooldown_ticks`, `last_intervention_tick`.

**Update rule (post-fill, end of tick t):**
1. `firepower_K_{t+1} = firepower_K_t − |filled_qty · fill_price|`.
2. `cumulative_intervention_{t+1} += |filled_qty · fill_price|`.
3. After `T_eval` ticks, update `credibility_score` per 3.6.3.
4. Mode-state transitions: `intervening → cooldown` after pulse; `cooldown → idle` when `cooldown_ticks = 0`; `idle → exhausted` if `firepower_K ≤ 0`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                         |
|----------------------|--------------------------------------------------------------|
| Order types allowed  | MARKET (intervention is decisive, not patient)               |
| Price level rule     | Cross the spread; no limit price                             |
| Order quantity rule  | Per-mode (see 3.6.2), capped by `firepower_K_remaining`      |
| Order lifetime       | One tick (immediate-or-cancel)                               |
| Cancellation policy  | Cancel-on-fill                                               |
| Inventory constraint | Position can grow without bound; constraint is `firepower_K` |
| Wealth/leverage cap  | n/a (sovereign / public-sector balance sheet)                |
| Stop-loss/kill rule  | `firepower_K ≤ 0` ⇒ permanent deactivation (mode=exhausted)  |

## Parameters

| Symbol                  | Name                     | Default  | Range         | Units    | Source                      | Sensitivity | Notes                      |
|-------------------------|--------------------------|----------|---------------|----------|-----------------------------|-------------|----------------------------|
| `θ_peg`                 | Peg-deviation trigger    | 0.02     | [0.005, 0.10] | FX-frac  | Obstfeld (1996)             | High        | FX defender activation     |
| `θ_lolr`                | LOLR trigger             | 0.02     | [0.005, 0.10] | return   | Bagehot (1873)              | High        | Fast-trigger LOLR          |
| `θ_imf`                 | IMF trigger              | 0.05     | [0.02, 0.20]  | return   | Corsetti et al. (1999)      | High        | Slow-trigger IMF           |
| `θ_spread`              | Sovereign-spread trigger | 0.05     | [0.02, 0.15]  | bps frac | De Grauwe-Ji (2013)         | High        | "Whatever it takes"        |
| `θ_macropru`            | Systemic-stress trigger  | 0.50     | [0.20, 0.90]  | unitless | Goodhart (2008)             | Med         | Macroprudential activation |
| `κ_def`                 | FX-defender flow scale   | 1.0      | [0.5, 5.0]    | none     | Eichengreen et al. (1995)   | Med         | Per-tick flow magnitude    |
| `κ_lolr`                | LOLR flow scale          | 1.5      | [0.5, 5.0]    | none     | Bordo (1990)                | Med         | Lend-freely scale          |
| `κ_ecb`                 | ECB flow scale           | 1.0      | [0.5, 5.0]    | none     | Krishnamurthy et al. (2018) | Med         | OMT pace                   |
| `κ_imf`                 | IMF flow scale           | 5.0      | [1.0, 20.0]   | none     | Corsetti et al. (1999)      | High        | Large package              |
| `κ_pru`                 | Macroprudential scale    | 0.5      | [0.1, 2.0]    | none     | Cerutti et al. (2017)       | Med         | Targeted flow              |
| `κ_coord`               | Coordination scale       | 2.0      | [0.5, 10.0]   | none     | LTCM-1998 case              | Med         | Coordinated rescue         |
| `firepower_K_initial`   | Initial capacity         | 1e6      | [1e4, 1e10]   | currency | Brady (1988) sizes          | High        | Sovereign balance sheet    |
| `p_credibility_initial` | Initial credibility      | 0.7      | [0.0, 1.0]    | prob     | De Grauwe-Ji (2013)         | High        | Defender success rate      |
| `p_intervention`        | Macropru engagement prob | 0.4      | [0.05, 0.95]  | prob     | Goodhart (2008)             | Med         | Decision-lag proxy         |
| `δ_credit`              | Credibility update step  | 0.05     | [0.01, 0.20]  | prob     | implementation              | Low         | Per-success update         |
| `T_cool`                | Cooldown ticks           | 50       | [10, 200]     | ticks    | political-economy lag       | Med         | Standard pulses            |
| `T_cool_imf`            | IMF cooldown             | 200      | [50, 500]     | ticks    | Corsetti et al. (1999)      | Med         | Slow-trigger longer pause  |
| `T_eval`                | Credibility eval window  | 20       | [5, 100]      | ticks    | implementation              | Low         | Outcome look-back          |
| `s_central`             | FX-peg central rate      | 1.0      | calibrated    | rate     | Krugman (1979)              | n/a         | Scenario-specific          |
| `ε`                     | Reversion threshold      | 0.50 · θ | [0.10·θ, θ]   | return   | implementation              | Low         | Success criterion          |

## Population and Heterogeneity

```yaml
policy_mode_mixture:
  peg_defender_fx: 0.15
  central_bank_lolr: 0.15
  ecb_whatever_it_takes: 0.10
  imf_rescuer: 0.15
  prudential_regulator: 0.20
  deposit_guarantee: 0.10
  central_bank_coordination: 0.15
heterogeneity:
  firepower_K_initial: Lognormal(ln 1e6, 1.0)
  p_credibility_initial: Beta(7, 3)
  theta_imf: Lognormal(ln 0.05, 0.30)
  theta_lolr: Lognormal(ln 0.02, 0.30)
  kappa_imf: Lognormal(ln 5.0, 0.50)
```

The population fractions reflect typical multi-jurisdiction crisis-resolution composition: 1 peg defender + 1 LOLR + 1 ECB-style + 1 IMF + 1–2 prudential per scenario, matching Reinhart-Rogoff (2009) cross-country sample composition.

## Worked Numerical Examples

**Case 1 — Peg defender successful intervention (`policy_mode = peg_defender_fx`)**: `s_central = 1.0, s_t = 0.95, θ_peg = 0.02, κ_def = 1.0, firepower_K = 1e6, p_credibility = 0.70`.
- Trigger: `s_t = 0.95 < 0.98`. Bernoulli(0.70) = 1 (success this draw).
- `Q* = 1.0 · (1.0 − 0.95) · 1,000,000 / 0.95 = 52,632` units.
- Emit MARKET buy. `firepower_K ← 1e6 − 50,000 = 950,000`. Cooldown 50 ticks.
- Action: MARKET buy 52,632 currency units; subsequent credibility update if `s_t` reverts by 0.025 within 20 ticks.

**Case 2 — IMF slow-trigger rescue (`policy_mode = imf_rescuer`)**: `d_t = −0.06 < −θ_imf = −0.05, κ_imf = 5.0, firepower_K = 5e6, P_t = 80`.
- Trigger fires. `Q* = 5.0 · 0.06 · 5,000,000 / 80 = 18,750` shares.
- MARKET buy 18,750 shares. `firepower_K ← 5e6 − 1,500,000 = 3.5e6`. Cooldown `T_cool_imf = 200` ticks.
- Action: massive buy; long pause until next pulse.

**Case 3 — ECB-style backstop (`policy_mode = ecb_whatever_it_takes`)**: `bond_spread_t = 0.08, θ_spread = 0.05, κ_ecb = 1.0, firepower_K = 2e6, P_t = 90`.
- Trigger: `0.08 > 0.05`. `Q* = 1.0 · 0.03 · 2,000,000 / 90 = 667` shares.
- MARKET buy 667. Spreads should compress within `T_eval = 20` ticks for credibility update.
- Action: MARKET buy 667 bonds.

**Case 4 — Macroprudential regulator (`policy_mode = prudential_regulator`)**: `systemic_stress_t = 0.65, θ_macropru = 0.50, p_intervention = 0.4, κ_pru = 0.5, firepower_K = 1e6, P_t = 100`.
- Trigger: `0.65 > 0.50`. Bernoulli(0.4) = 1. `Q* = 0.5 · 0.65 · 1,000,000 / 100 = 3,250`.
- MARKET buy 3,250. Cooldown 50 ticks.
- Action: MARKET buy 3,250.

**Edge case — Firepower exhaustion**: `firepower_K = 50,000` remaining. Trigger fires; `Q* = 0.5 · 1.0 · 50,000 / 100 = 250` capped flow only because of remaining capacity. After fill, `firepower_K = 25,000`. Next trigger: `Q* = 0.5 · 1.0 · 25,000 / 100 = 125`. Capacity halves each pulse until `firepower_K ≤ 0`; mode becomes `exhausted` and agent permanently deactivates.

## Validation and Calibration

- **V1 — LOLR run-extinction (Theory 1)**: Conditional on activation, run-driven price decline reverses within `T_eval = 20` ticks in `≥ 70%` of episodes (Diamond-Dybvig 1983 prediction). Ablation: set `firepower_K = 0`.
- **V2 — Peg-defence credibility-conditional success (Theory 2)**: Success rate empirically equals `p_credibility`. Ablation: set `p_credibility = 0` ⇒ all defenders fail; peg breaks 100% of attacks.
- **V3 — Whatever-it-takes spread compression (Theory 3)**: Sovereign spread declines on average by `Δ_announce ≥ 30%` after first ECB pulse (Krishnamurthy et al. 2018 magnitude). Ablation: deactivate `ecb_whatever_it_takes`.
- **V4 — IMF slow-trigger pattern (Theory 4)**: Conditional on stress depth `d_t ∈ [−0.10, −0.03]`, IMF intervention rate is `< 20%`; conditional on `d_t < −0.05`, rate is `> 80%`. Ablation: `θ_imf = θ_lolr` ⇒ pattern collapses.
- **V5 — Macroprudential probabilistic activation (Theory 5)**: Long-run intervention frequency matches `p_intervention · Pr(stress_t > θ_macropru)`. Ablation: `p_intervention = 0` or `θ_macropru = ∞`.
- **V6 — Intermediary-channel non-linearity (Theory 6)**: Price impact of `K_intervention` flow is super-linear in stress (e.g., `2× flow → 3× price recovery`). Ablation: deactivate `LeveragedFundInvestor.forced_unwind` to remove intermediary channel.

**Ablation Hooks**:
- `firepower_K = 0` → disables LOLR (Theory 1).
- `p_credibility = 0` → disables peg defence (Theory 2).
- `θ_spread = ∞` → disables ECB whatever-it-takes (Theory 3).
- `θ_imf = θ_lolr` → collapses slow-trigger to fast-trigger (Theory 4).
- `θ_macropru = ∞` → disables macroprudential (Theory 5).

## Academic References

1. Diamond, D. W. and Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401–419. https://doi.org/10.1086/261155
2. Reinhart, C. M. and Rogoff, K. S. (2008). Is the 2007 US sub-prime financial crisis so different? An international historical comparison. *American Economic Review*, 98(2), 339–344. https://doi.org/10.1257/aer.98.2.339
3. Allen, F. and Gale, D. (2000). Financial contagion. *Journal of Political Economy*, 108(1), 1–33. https://doi.org/10.1086/262109
4. Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311–325. https://doi.org/10.2307/1991793
5. Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3–5), 1037–1047. https://doi.org/10.1016/0014-2921(95)00111-5
6. Eichengreen, B., Rose, A. K. and Wyplosz, C. (1995). Exchange market mayhem: The antecedents and aftermath of speculative attacks. *Economic Policy*, 10(21), 249–312. https://doi.org/10.2307/1344591
7. Morris, S. and Shin, H. S. (1998). Unique equilibrium in a model of self-fulfilling currency attacks. *American Economic Review*, 88(3), 587–597. https://doi.org/10.1257/aer.88.3.587
8. De Grauwe, P. and Ji, Y. (2013). Self-fulfilling crises in the Eurozone: An empirical test. *Journal of International Money and Finance*, 34, 15–36. https://doi.org/10.1016/j.jimonfin.2012.11.003
9. Corsetti, G., Pesenti, P. and Roubini, N. (1999). What caused the Asian currency and financial crisis? Part I. *Japan and the World Economy*, 11(3), 305–373. https://doi.org/10.1016/S0922-1425(99)00019-5
10. Kaminsky, G. L. and Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473
11. Cerutti, E., Claessens, S. and Laeven, L. (2017). The use and effectiveness of macroprudential policies: New evidence. *Journal of Financial Stability*, 28, 203–224. https://doi.org/10.1016/j.jfs.2015.10.004
12. He, Z. and Krishnamurthy, A. (2013). Intermediary asset pricing. *American Economic Review*, 103(2), 732–770. https://doi.org/10.1257/aer.103.2.732
13. Caballero, R. J. and Krishnamurthy, A. (2008). Collective risk management in a flight to quality episode. *Journal of Finance*, 63(5), 2195–2230. https://doi.org/10.1111/j.1540-6261.2008.01390.x
14. Adrian, T. and Brunnermeier, M. K. (2016). CoVaR. *American Economic Review*, 106(7), 1705–1741. https://doi.org/10.1257/aer.20120555
15. Krishnamurthy, A., Nagel, S. and Vissing-Jorgensen, A. (2018). ECB policies involving government bond purchases: Impact and channels. *Review of Finance*, 22(1), 1–44. https://doi.org/10.1093/rof/rfx053

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/PolicyBackstopAgent.md` (legacy); seven merged scenario profiles from `AsianFinancialCrisis`, `CurrencyCrisis`, `EuropeanDebtCrisis`, `GFC2008`, `LTCMCollapse`, `SVBBankRun`, `SorosPound`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 4.4 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
