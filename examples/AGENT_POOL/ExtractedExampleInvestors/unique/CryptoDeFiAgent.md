# Stablecoin, DeFi, and Crypto-Market Participants

## Summary

| Field              | Content                                                                                                                                                                                                         |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype          | Stablecoin, DeFi, and Crypto-Market Participants                                                                                                                                                                |
| Sub-archetype enum | `crypto_mode ∈ {algo_stablecoin_holder, fiat_backed_holder, defi_yield_farmer, liquidity_provider_amm, run_redeemer}`                                                                                           |
| Market Role        | Crypto / DeFi liquidity and redemption participant — supplies AMM and yield-farming liquidity in calm regimes; converts to forced redemption / depeg-driven seller in crisis (LUNA / Terra-style death spiral). |
| Merged profiles    | 1 (extended with adjacent crypto roles for completeness)                                                                                                                                                        |
| Scenarios          | LUNACollapse                                                                                                                                                                                                    |
| Observed names     | Stablecoin Holder                                                                                                                                                                                               |
| Decision target    | Redemption / hold ratio for stablecoin; LP-share / yield-farming allocation; spot order on depeg threshold breach.                                                                                              |
| Time horizon       | Hours-to-days; in run mode collapses to single-tick.                                                                                                                                                            |
| Information access | Stablecoin price (P_t), peg target (=1), yield rate, perceived backing ratio / collateralisation; no order-book depth, no peer counter-party identity.                                                          |
| Risk profile       | Tail-risk dominated: bounded gains (yield), unbounded loss on depeg / death spiral.                                                                                                                             |

## Definition and Goals

This archetype models holders of crypto-asset and stablecoin instruments whose primary decision is whether to remain in the protocol or redeem to fiat / safe haven. Algorithmic stablecoins (Terra UST / LUNA) are particularly vulnerable to confidence-driven runs, because the redemption mechanism is reflexive: redemption pressure mints supply of the volatile sister-token, dilutes its price, undermining the peg, accelerating redemption — the **death spiral** (Liu, Makarov, & Schoar 2023).

**Goals.**
1. Reproduce stablecoin holding-vs-redemption decisions under depeg pressure.
2. Model DeFi yield-farming flows that respond to APR opportunities and impermanent-loss risk.
3. Generate run-equilibrium dynamics consistent with Diamond-Dybvig (1983) extended to crypto (Liu et al. 2023; Gorton & Zhang 2022).

**Non-goals.**
- Modelling on-chain transaction-fee market.
- Smart-contract execution semantics.
- MEV / sandwich-attack micro-mechanics.

## Theoretical Foundation

### Theory 1 — Diamond-Dybvig Bank Runs (1983)

| Field                    | Content                                                                                                                                            |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Bank Runs, Deposit Insurance, and Liquidity                                                                                                        |
| Citation                 | Diamond, D. W., & Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy*, 91(3), 401–419.               |
| DOI                      | 10.1086/261155                                                                                                                                     |
| Core Insight             | Two equilibria: depositors hold (good) or run (bad); runs are self-fulfilling once a critical mass redeems. Maps directly to algo-stablecoin runs. |
| Mathematical Formulation | If `redemption_share_t > θ_run`, expected payoff to holders falls below par → cascade.                                                             |
| Empirical Evidence       | Northern Rock 2007, SVB 2023, Terra UST May 2022.                                                                                                  |
| Relevance to This Agent  | Defines the run-trigger logic in `run_redeemer` and `algo_stablecoin_holder` modes.                                                                |
| Calibration Source       | Diamond-Dybvig (1983); Liu et al. (2023).                                                                                                          |
| Falsification Conditions | If holders never run despite arbitrarily large depeg, the theory is wrong.                                                                         |
| Alternative Theories     | Frictionless market clearing — predicts no run; rejected by Terra evidence.                                                                        |

### Theory 2 — Algorithmic Stablecoin Reflexivity (Liu, Makarov, Schoar 2023)

| Field                    | Content                                                                                                                                            |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | The Anatomy of a Stablecoin                                                                                                                        |
| Citation                 | Liu, J., Makarov, I., & Schoar, A. (2023). Anatomy of a run: The Terra Luna crash. *NBER Working Paper 31160*.                                     |
| DOI                      | 10.3386/w31160                                                                                                                                     |
| Core Insight             | UST → LUNA mint mechanism creates reflexive feedback: redemption mints LUNA → LUNA price falls → backing weakens → more redemption (death spiral). |
| Mathematical Formulation | LUNA supply growth `dS_LUNA = redemption_UST / P_LUNA`; price `P_LUNA ∝ Marketcap / Supply`; depeg threshold `P_UST < 0.95`.                       |
| Empirical Evidence       | Terra UST 8–13 May 2022: $40B mcap → $0 in 5 days.                                                                                                 |
| Relevance to This Agent  | Provides the death-spiral reflexivity for `algo_stablecoin_holder`.                                                                                |
| Calibration Source       | Liu et al. (2023); on-chain data from CoinMarketCap / Glassnode.                                                                                   |
| Falsification Conditions | If LUNA mint pressure does not depress LUNA price empirically, the theory is wrong.                                                                |
| Alternative Theories     | Frictionless arbitrage stabilises algo pegs — rejected by UST collapse.                                                                            |

### Theory 3 — Stablecoin Backing and Confidence (Gorton & Zhang 2022)

| Field                    | Content                                                                                                                                       |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Taming Wildcat Stablecoins                                                                                                                    |
| Citation                 | Gorton, G. B., & Zhang, J. (2022). Taming wildcat stablecoins. *University of Chicago Law Review*, 90(3), 909–971.                            |
| DOI                      | 10.2139/ssrn.3888752                                                                                                                          |
| Core Insight             | Fiat-backed stablecoins (USDC, USDT) face only confidence runs (no reflexive minting); algo-stablecoins face both confidence and reflexivity. |
| Mathematical Formulation | Backing ratio `b_t = collateral_t / supply_t`; depeg risk `∝ 1 − b_t` with non-linear amplification when `b_t < b_critical`.                  |
| Empirical Evidence       | USDC depeg 11 Mar 2023 ($0.87) on SVB exposure; UST 8 May 2022.                                                                               |
| Relevance to This Agent  | Differentiates `fiat_backed_holder` (slower run) from `algo_stablecoin_holder` (reflexive).                                                   |
| Calibration Source       | Gorton & Zhang (2022).                                                                                                                        |
| Falsification Conditions | If fiat-backed pegs never break, the model can ignore confidence channel.                                                                     |
| Alternative Theories     | Perfect-collateralisation theories — rejected by USDC March 2023.                                                                             |

### Theory 4 — Automated Market Maker (AMM) and Impermanent Loss

| Field                    | Content                                                                                                                       |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Constant-Product Market Making (Uniswap v2)                                                                                   |
| Citation                 | Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D. (2021). Uniswap v3 core whitepaper. *Uniswap Labs*.         |
| DOI                      | 10.5281/zenodo.5701018                                                                                                        |
| Core Insight             | LPs face impermanent loss when token-pair price diverges; rational LPs withdraw when realised IL exceeds expected fee income. |
| Mathematical Formulation | IL(r) = `2·sqrt(r)/(1+r) − 1`, where r = P_t / P_0; LP withdraws if IL · liquidity > fee_income · horizon.                    |
| Empirical Evidence       | UST/3Crv pool drained in hours during May 2022 depeg.                                                                         |
| Relevance to This Agent  | Justifies `liquidity_provider_amm` mode and IL-driven withdrawal trigger.                                                     |
| Calibration Source       | Adams et al. (2021); Heimbach, Wang, & Wattenhofer (2022).                                                                    |
| Falsification Conditions | If LPs never withdraw despite large IL, the model fails.                                                                      |
| Alternative Theories     | Static LP positions — rejected by 3Crv evidence.                                                                              |

### Theory 5 — Yield Farming and Capital Flight (Aramonte, Huang, Schrimpf 2021)

| Field                    | Content                                                                                                                                     |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | DeFi Risks and the Decentralisation Illusion                                                                                                |
| Citation                 | Aramonte, S., Huang, W., & Schrimpf, A. (2021). DeFi risks and the decentralisation illusion. *BIS Quarterly Review*, December 2021, 21–36. |
| DOI                      | 10.2139/ssrn.4022702                                                                                                                        |
| Core Insight             | Yield-farming flows respond elastically to APR differentials and shrink dramatically on adverse signals (rug-pull, hack, depeg).            |
| Mathematical Formulation | Allocation `w_i = exp(β·APR_i) / Σ exp(β·APR_j)` (logit); β collapses to 0 in stress.                                                       |
| Empirical Evidence       | TVL of Anchor protocol fell from $14B to $0 in May 2022.                                                                                    |
| Relevance to This Agent  | Provides `defi_yield_farmer` mode logic.                                                                                                    |
| Calibration Source       | Aramonte et al. (2021); DeFiLlama TVL series.                                                                                               |
| Falsification Conditions | If yield farmers do not respond to APR spreads, the model fails.                                                                            |
| Alternative Theories     | Sticky DeFi capital — rejected by post-2022 evidence.                                                                                       |

## Design Purpose and Activation Triggers

This agent fulfils three roles:
1. **Crypto liquidity in calm regimes** — `defi_yield_farmer`, `liquidity_provider_amm`, fiat-backed holding.
2. **Confidence-run / depeg seller** — `run_redeemer`, `algo_stablecoin_holder` under depeg pressure.
3. **Death-spiral amplifier** — algo-stablecoin redemption flow that triggers minting cascade.

**Activation triggers (per mode):**
- `algo_stablecoin_holder`: P_t < 1 − θ_depeg or backing_ratio_t < b_critical → redeem.
- `fiat_backed_holder`: P_t < 1 − θ_depeg_fiat (slower threshold) or `audit_signal` adverse.
- `defi_yield_farmer`: APR change > θ_apr or rug-pull signal → reallocate / exit.
- `liquidity_provider_amm`: |IL_t| > θ_IL → withdraw.
- `run_redeemer`: redemption_share_t > θ_run AND P_t < 1 − θ_depeg → forced redeem.

**Deactivation conditions:** holdings exhausted, peg restored, withdrawal cooldown active.

### Market Contribution by Regime

| Regime         | Contribution                                                       |
|----------------|--------------------------------------------------------------------|
| Calm           | Provides AMM liquidity; harvests yield; mildly stabilising.        |
| Trending boom  | Increases TVL on rising APRs; weakly destabilising in fee markets. |
| Trending crash | Yield farmers exit; LP withdrawals widen spreads; destabilising.   |
| Depeg event    | Forced redemption + reflexive minting → death spiral (LUNA-style). |
| Stress         | Fiat-backed runs slower but not absent (USDC March 2023).          |

**Interaction with other agents:** Run-redeemers act as forced sellers vs. crypto market makers; AMM-LP withdrawal compounds spread widening and reduces market-maker quoted depth.

## Behavioural Framework

### 3.6.1 State Variables

| Symbol               | Type        | Description                                     |
|----------------------|-------------|-------------------------------------------------|
| `crypto_mode`        | Categorical | One of the 5 enum values.                       |
| `holdings`           | Float       | Current stablecoin / LP / farm balance.         |
| `P_t`                | Float       | Price of the stablecoin / token.                |
| `b_t`                | Float       | Backing ratio (or perceived collateralisation). |
| `APR_t`              | Float       | Annualised yield offered by the protocol.       |
| `redemption_share_t` | Float       | Share of supply redeemed in trailing window.    |
| `IL_t`               | Float       | Realised impermanent loss for AMM LPs.          |
| `cooldown_t`         | Int         | Withdrawal-cooldown counter.                    |
| `confidence_t`       | Float       | Holder confidence proxy (e.g., audit signal).   |

### 3.6.2 Decision Rule

```
observe P_t, b_t, APR_t, redemption_share_t, IL_t, confidence_t

if crypto_mode == algo_stablecoin_holder:
    if P_t < 1 − θ_depeg or b_t < b_critical:
        Q* = − redemption_size · holdings        # mint LUNA, sell into market
    else:
        Q* = 0

elif crypto_mode == fiat_backed_holder:
    if P_t < 1 − θ_depeg_fiat or confidence_t < c_critical:
        Q* = − ρ_redeem · holdings               # slower partial redemption
    else:
        Q* = 0

elif crypto_mode == defi_yield_farmer:
    if APR_change_t > θ_apr or rug_signal_t:
        Q* = − holdings_in_pool                  # exit
    elif APR_t > APR_target:
        Q* = + new_capital_inflow                # enter pool
    else:
        Q* = 0

elif crypto_mode == liquidity_provider_amm:
    if |IL_t| > θ_IL:
        Q* = − LP_share                          # withdraw LP
    else:
        Q* = 0

elif crypto_mode == run_redeemer:
    if redemption_share_t > θ_run and P_t < 1 − θ_depeg:
        Q* = − full_holdings                     # full forced redemption
    else:
        Q* = 0
```

### 3.6.3 Mode-specific update rules

- `algo_stablecoin_holder`: redemption mints LUNA → upstream `S_LUNA` increases → next-tick price feedback (death spiral closure handled at the protocol level).
- `fiat_backed_holder`: redemption is partial; cooldown_t imposes minimum delay between subsequent redemptions.
- `defi_yield_farmer`: tracks APR_change_t as `(APR_t − APR_{t−k}) / APR_{t−k}`; rug_signal toggles modes.
- `liquidity_provider_amm`: continuously updates IL_t based on token-price ratio; withdrawal frees Q* for LP fee accounting.
- `run_redeemer`: deterministic once trigger crosses; no partial.

### 3.6.4 Determinism Contract and State Update

- Deterministic given (`P_t`, `b_t`, `APR_t`, `redemption_share_t`, `IL_t`, `confidence_t`, parameters, mode-specific state).
- After each tick: `holdings += Q*`; if `Q* < 0` reset relevant pool / LP share state; increment cooldown if applicable.

**Does NOT use:** order-book depth, on-chain mempool data, MEV-bot identity, sentiment scores, social-media volume, options-implied vol. Uses only own holdings state, peg / backing signals, APR, redemption-share aggregate, and IL ratio.

### 3.6.5 Action Space

| Property             | Specification                                                                                                            |
|----------------------|--------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | MARKET (predominant in run / depeg modes); LIMIT for AMM swaps; protocol-redemption transactions for stablecoin holders. |
| Price level rule     | MARKET at best bid (sell into depeg); LIMIT at peg ± ε in calm modes.                                                    |
| Order quantity rule  | `Q* = ratio · holdings`, ratio mode-specific; capped by `single_redeem_cap`.                                             |
| Order lifetime       | MARKET: immediate; LIMIT: 10 ticks.                                                                                      |
| Cancellation policy  | Cancel pending swaps on regime flip (peg restore / break).                                                               |
| Inventory constraint | `holdings ≥ 0`; `LP_share ∈ [0, total_share]`.                                                                           |
| Wealth-leverage cap  | No leverage on holders; LP modes face IL-implied implicit leverage.                                                      |
| Stop-loss-kill rule  | Force full exit when `P_t < kill_floor` (default 0.50) — death-spiral terminal exit.                                     |

## Parameters

| Symbol              | Name                   | Default | Range         | Units      | Source              | Sensitivity | Notes                  |
|---------------------|------------------------|---------|---------------|------------|---------------------|-------------|------------------------|
| `θ_depeg`           | Algo depeg trigger     | 0.05    | [0.01, 0.20]  | fraction   | Liu et al. (2023)   | High        | UST tripped at 0.95    |
| `θ_depeg_fiat`      | Fiat depeg trigger     | 0.02    | [0.005, 0.05] | fraction   | USDC March 2023     | High        | Slower but real        |
| `b_critical`        | Critical backing ratio | 0.80    | [0.6, 1.0]    | fraction   | Gorton-Zhang (2022) | High        | Confidence break       |
| `c_critical`        | Confidence threshold   | 0.50    | [0.2, 0.8]    | normalised | Calibrated          | Medium      | Audit-signal gate      |
| `θ_run`             | Run-share trigger      | 0.10    | [0.03, 0.30]  | fraction   | Diamond-Dybvig      | High        | Coordination threshold |
| `θ_apr`             | APR-change trigger     | 0.30    | [0.10, 0.80]  | fraction   | Aramonte (2021)     | Medium      | Capital flight         |
| `APR_target`        | Min entry APR          | 0.05    | [0.01, 0.30]  | annual     | Calibrated          | Medium      | Yield seeking          |
| `θ_IL`              | IL withdrawal trigger  | 0.05    | [0.02, 0.20]  | fraction   | Heimbach et al.     | Medium      | LP exit                |
| `redemption_size`   | Algo redeem ratio      | 1.0     | [0.5, 1.0]    | fraction   | Run-eq logic        | High        | Full mint              |
| `ρ_redeem`          | Fiat redeem ratio      | 0.50    | [0.10, 1.0]   | fraction   | Calibrated          | Medium      | Partial                |
| `kill_floor`        | Hard exit price        | 0.50    | [0.30, 0.80]  | peg unit   | Manual              | High        | Terminal trigger       |
| `single_redeem_cap` | Per-tick cap           | 1e5     | [1e4, 1e7]    | $          | Liquidity logic     | Low         | Smoothing              |
| `cooldown_ticks`    | Withdrawal cooldown    | 1       | [0, 24]       | ticks      | Manual              | Low         | Anti-spam              |

## Population and Heterogeneity

Categorical mixture per scenario:
- LUNACollapse: `algo_stablecoin_holder` 0.55, `defi_yield_farmer` 0.20, `liquidity_provider_amm` 0.10, `run_redeemer` 0.15.
- Generic Stablecoin scenario: `fiat_backed_holder` 0.50, `defi_yield_farmer` 0.30, `liquidity_provider_amm` 0.20.

Heterogeneity per agent:
- `holdings` ~ LogNormal(μ=ln(1e4), σ=1.0).
- `θ_depeg` ~ Normal(0.05, 0.02), truncated [0.01, 0.20].
- `c_critical` ~ Beta(2, 2) scaled to [0.3, 0.8].

## Worked Numerical Examples

**Example 1 — Algo stablecoin holding in calm regime.**
P_t = 0.998, b_t = 0.95 → no trigger; Q* = 0.

**Example 2 — Algo depeg trigger (Terra-style).**
P_t = 0.92 < 1 − θ_depeg (=0.95), holdings = $50,000 → Q* = − redemption_size · 50,000 = −$50,000 redeemed in one tick → mints proportional LUNA on protocol side.

**Example 3 — Fiat-backed slower partial redemption (USDC March 2023).**
P_t = 0.87, θ_depeg_fiat = 0.02 (P_t below 0.98) → ρ_redeem = 0.50; holdings = $100,000 → Q* = −$50,000; cooldown_ticks = 1 before next.

**Example 4 — AMM LP withdrawal on impermanent loss.**
Token-pair price ratio r = 0.5 → IL = 2·sqrt(0.5)/(1+0.5) − 1 = −0.057 (5.7% loss); θ_IL = 0.05 → withdraw full LP.

**Example 5 — Edge case: cooldown blocks redemption.**
Fiat-backed holder redeemed last tick; cooldown_ticks=1 active → Q* = 0 even though peg still broken; redemption deferred to next tick.

## Validation and Calibration

**Validation targets:**
- Death-spiral reproduction: mode `algo_stablecoin_holder` with redemption_share crossing θ_run produces a price decay matching UST May 2022 trajectory within 30% MSE.
- USDC depeg recovery: fiat_backed_holder mode with cooldown produces a slower run that recovers within 5 days.
- AMM-LP elasticity: 50% of LP capital exits within 24h when IL > 5% (3Crv pattern).

**Ablation Hooks:**
- Disable reflexivity (no LUNA mint feedback) → no death spiral; tests Liu et al. (2023) channel.
- Set `θ_run = ∞` → no run; tests Diamond-Dybvig coordination.
- Disable `θ_apr` trigger → no yield-farm capital flight; tests Aramonte (2021) channel.

**Calibration sources:**
- Glassnode / CoinMarketCap on-chain Terra UST / LUNA data (May 2022).
- DeFiLlama TVL series for Anchor / Curve.
- Coinbase / Kraken USDC trading data (March 2023).

## Academic References

1. Diamond, D. W., & Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *JPE*, 91(3), 401–419. DOI: 10.1086/261155
2. Liu, J., Makarov, I., & Schoar, A. (2023). Anatomy of a run: The Terra Luna crash. *NBER WP 31160*. DOI: 10.3386/w31160
3. Gorton, G. B., & Zhang, J. (2022). Taming wildcat stablecoins. *U. Chi. L. Rev.*, 90(3), 909–971. DOI: 10.2139/ssrn.3888752
4. Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D. (2021). Uniswap v3 core whitepaper. *Uniswap Labs*. DOI: 10.5281/zenodo.5701018
5. Aramonte, S., Huang, W., & Schrimpf, A. (2021). DeFi risks and the decentralisation illusion. *BIS Q. Rev.*, December 2021, 21–36. DOI: 10.2139/ssrn.4022702
6. Heimbach, L., Wang, Y., & Wattenhofer, R. (2022). Behavior of liquidity providers in decentralized exchanges. *FC '22*. DOI: 10.48550/arXiv.2105.13822
7. Catalini, C., de Gortari, A., & Shah, N. (2022). Some simple economics of stablecoins. *Annual Review of Financial Economics*, 14, 117–135. DOI: 10.1146/annurev-financial-111621-101151
8. Makarov, I., & Schoar, A. (2020). Trading and arbitrage in cryptocurrency markets. *JFE*, 135(2), 293–319. DOI: 10.1016/j.jfineco.2019.07.001
9. Foley, S., Karlsen, J. R., & Putniņš, T. J. (2019). Sex, drugs, and bitcoin: How much illegal activity is financed through cryptocurrencies? *RFS*, 32(5), 1798–1853. DOI: 10.1093/rfs/hhz015

## Design Provenance and Versioning

- **Version:** 1.0 (pilot pass, 2026-Q2)
- **Source skeleton:** examples/AGENT_POOL/ExtractedExampleInvestors/unique/CryptoDeFiAgent.md (skeleton, 33 lines)
- **Merged scenarios:** LUNACollapse (extended with adjacent crypto roles)
- **Sub-archetype synthesis:** original Stablecoin Holder profile expanded to a 5-level `crypto_mode` enum covering algo / fiat-backed holders, yield-farmers, AMM LPs, and run-redeemers — preserving LUNA's reflexive death-spiral as the primary calibration anchor.
- **Authoring rubric:** agent-design-skill.md (12-section pilot depth) + agent-design-finance.md addendum.
- **Audit fields:** Market Role, Market Contribution by Regime, 8-row Action Space, observation `Does NOT use:` declaration, ablation hooks — all present.
- **Open issues:** on-chain transaction-cost / mempool dynamics not modelled; MEV-bot interactions deferred to v2; cross-chain bridge runs (Wormhole-style) deferred.
