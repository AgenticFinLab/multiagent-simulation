# VolatilityProductTrader

## Summary

| Field                        | Content                                                                                                                                                                                                                                                                                                                                    |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Volatility-product, volatility-management, and equity de-risking agents                                                                                                                                                                                                                                                                    |
| Theory Family                | Volatility Timing (Engle 1982; Bollerslev 1986); Adaptive Expectations (Brock-Hommes 1998); Vol-Targeting / Risk-Parity; Volatility-ETN Mechanical Rebalancing                                                                                                                                                                             |
| Market Role                  | **Mixed** — `vol_etn_manager` is **strongly destabilising** (procyclical rebalancing); `vol_trader` and `equity_de_risker` are **mildly destabilising** in stress (sell into vol-spikes); `long_vol_hedger` is **stabilising** (buys vol when cheap, sells into vol spikes); `slow_adapter` is **mildly stabilising** (delayed correction) |
| Time Horizon                 | medium (10–100 ticks) — vol-regime-conditional                                                                                                                                                                                                                                                                                             |
| Risk Tolerance               | medium — vol-targeting agents have explicit `σ_target`; ETN manager is mandate-driven                                                                                                                                                                                                                                                      |
| Information Asymmetry        | none — uses public realised-volatility / VIX-proxy estimates                                                                                                                                                                                                                                                                               |
| Determinism                  | fully deterministic given `(P_t, P_{t−W}, σ̂_t, vol_proxy_t, position, RNG_seed)` (no Bernoulli draws)                                                                                                                                                                                                                                      |
| Merged profiles              | 5 (Slow Adapter, Volatility Trader, Equity Trader, Long Vol Hedger, Vol ETN Manager — across two scenarios)                                                                                                                                                                                                                                |
| Source scenarios             | VolatilityClustering, Volmageddon                                                                                                                                                                                                                                                                                                          |
| Canonical sub-archetype enum | `vol_mode ∈ {slow_adapter, vol_trader, equity_de_risker, long_vol_hedger, vol_etn_manager}`                                                                                                                                                                                                                                                |

## Definition and Goals

This agent models the **volatility-product / volatility-management / equity-de-risking** family in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), spanning five merged profiles whose decision input is the realised-volatility regime or the level of an exogenous volatility proxy (e.g., VIX). The five modes cover the Brock-Hommes (1998) slow-adapter / adaptive-expectations trader, the Fleming-Kirby-Ostdiek (2001) volatility-timing trader, the vol-targeting equity-de-risker (Moreira-Muir 2017), the long-vol portfolio insurer (Coval-Shumway 2001), and the inverse-VIX-ETN procyclical rebalancer (Carr-Wu 2009; Augustin-Brenner-Subrahmanyam 2020 Volmageddon retrospective).

**Primary goals:**
1. Reproduce the GARCH/ARCH-style volatility-clustering decision (Engle 1982; Bollerslev 1986): exposure declines when `σ̂_t > θ_high · σ̂_avg` and rises when `σ̂_t < θ_low · σ̂_avg`.
2. Reproduce the Volmageddon-2018 procyclical inverse-VIX rebalancing (Augustin et al. 2020): the inverse-vol ETN must buy more vol exposure when vol rises (and sell when it falls), creating a short-vol-feedback amplifier.
3. Reproduce the long-vol-hedger profit-taking after spikes (Coval-Shumway 2001 variance-risk-premium evidence).
4. Permit ablation of each channel (slow-adapter delay, vol-trader threshold, vol-targeting σ_target, ETN-mechanical rebal).

**Non-goals:**
1. Does NOT solve a forward-looking utility-maximisation problem; vol-regime decisions are reactive.
2. Does NOT model option Greeks explicitly; vol exposure is implemented as a synthetic delta-1 vol proxy.
3. Does NOT model the production of `vol_proxy_t` (e.g., VIX); it is exogenous input.
4. Does NOT engage in market-making; trades are directional.

## Theoretical Foundation

### Theory 1 — Engle / Bollerslev GARCH Volatility Clustering

- **Theory/Study**: Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. Bollerslev, T. (1986). Generalized autoregressive conditional heteroscedasticity. *Journal of Econometrics*, 31(3), 307–327.
- **Citation+DOI**: https://doi.org/10.2307/1912773 ; https://doi.org/10.1016/0304-4076(86)90063-1
- **Core Insight**: Volatility clusters: high-volatility periods follow high-volatility periods. A GARCH-style estimate `σ̂_t² = ω + α · ε²_{t−1} + β · σ̂²_{t−1}` is a near-optimal one-step-ahead predictor. A vol-regime-trader can exploit this persistence by reducing exposure in high-vol regimes and increasing it in low-vol regimes.
- **Mathematical Formulation**: When `σ̂_t > θ_high · σ̂_avg`, target exposure `target_pos = base_pos · (σ̂_avg / σ̂_t)`; when `σ̂_t < θ_low · σ̂_avg`, target `target_pos = base_pos · (σ̂_avg / σ̂_t)`. Order: `Q* = (target_pos − position)`.
- **Empirical Evidence**: Engle (1982); Bollerslev (1986); Fleming-Kirby-Ostdiek (2001, JFinEcon DOI 10.1093/jjfinec/nbi002) — vol-timing-evidence; Andersen-Bollerslev-Diebold-Labys (2003, Econometrica DOI 10.1111/1468-0262.00418) — RV-modelling.
- **Relevance to This Agent**: Anchors the `vol_trader` mode; provides the regime-conditional target.
- **Calibration Source**: Fleming et al. (2001); Andersen et al. (2003).
- **Falsification Conditions**: If `θ_high = ∞` and `θ_low = 0`, no regime triggers fire; vol-timing channel silent.
- **Alternative Theories**: Glosten-Jagannathan-Runkle (1993, JF DOI 10.1111/j.1540-6261.1993.tb05128.x) — GJR-GARCH asymmetric; Heston (1993, RFS DOI 10.1093/rfs/6.2.327) — stochastic-vol option-pricing; Carr-Wu (2009, RFS DOI 10.1093/rfs/hhn038) — variance-risk-premium evidence.

### Theory 2 — Brock-Hommes Adaptive Expectations / Slow Adapter

- **Theory/Study**: Brock, W. A. and Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274.
- **Citation+DOI**: https://doi.org/10.1016/S0165-1889(98)00011-6
- **Core Insight**: A trader who updates beliefs about fundamental value with adaptive (rather than rational) expectations under-reacts to fast shocks and contributes to volatility persistence. The trader's perceived value `F̃_t = w · F̃_{t−1} + (1−w) · F_t` lags the true fundamental, generating a multi-tick reaction window.
- **Mathematical Formulation**: `F̃_t = (1 − update_weight) · F̃_{t−1} + update_weight · F_t`. Decision: `Q* = base_pos · sign(F̃_t − P_t) · |F̃_t − P_t|/|F̃_t|` when `|F̃_t − P_t|/|F̃_t| > θ_slow`.
- **Empirical Evidence**: Brock-Hommes (1998); Hommes (2006, *Handbook* chapter); Greenwood-Shleifer (2014, RFS DOI 10.1093/rfs/hht082) — extrapolative-beliefs-evidence in surveys.
- **Relevance to This Agent**: Anchors the `slow_adapter` mode; provides the persistence channel.
- **Calibration Source**: Brock-Hommes (1998); Hommes (2006).
- **Falsification Conditions**: If `update_weight = 1`, `F̃_t = F_t` immediately; the slow-adapter channel collapses to value-investor-style.
- **Alternative Theories**: Cagan (1956 *Studies in the Quantity Theory of Money*) — adaptive-inflation-expectations original; Frankel-Froot (1990, AER DOI 10.2307/2006658) — fundamentalist-vs-chartist alternative; LeBaron-Arthur-Palmer (1999, JEDC DOI 10.1016/S0165-1889(98)00079-7) — Santa Fe artificial-stock-market.

### Theory 3 — Moreira-Muir Volatility-Targeting Strategies

- **Theory/Study**: Moreira, A. and Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644.
- **Citation+DOI**: https://doi.org/10.1111/jofi.12513
- **Core Insight**: A vol-target strategy `position_t = σ_target / σ̂_t · benchmark_position` produces robust risk-adjusted returns: it scales down exposure exactly when volatility rises, avoiding fat tails. Empirically, this generates positive Sharpe-ratio improvement across multiple asset classes.
- **Mathematical Formulation**: `target_pos = (σ_target / σ̂_t) · base_pos`. When `|target_pos − position| > θ_rebal`, `Q* = ε · (target_pos − position)`.
- **Empirical Evidence**: Moreira-Muir (2017) Tables 1–3 — multi-asset evidence; Barroso-Santa-Clara (2015, JFE DOI 10.1016/j.jfineco.2014.07.012) — momentum-vol-targeting; Asness-Frazzini-Pedersen (2012, *Quality Minus Junk*) — risk-parity evidence.
- **Relevance to This Agent**: Anchors the `equity_de_risker` mode; provides the explicit `σ_target` rebalancing.
- **Calibration Source**: Moreira-Muir (2017); Barroso-Santa-Clara (2015).
- **Falsification Conditions**: If `σ_target = ∞`, the agent never de-risks; the vol-target channel is silent.
- **Alternative Theories**: Daniel-Moskowitz (2016, JFE DOI 10.1016/j.jfineco.2015.12.002) — momentum-crash-management alternative; Harvey-Hoyle-Korgaonkar-Rattray-Sargaison-Van Hemert (2018, JPM DOI 10.3905/jpm.2018.45.1.014) — vol-target meta-analysis; Cederburg-O'Doherty (2016, *JFM*) — vol-target retrospective.

### Theory 4 — Coval-Shumway Variance-Risk Premium / Long-Vol Hedger

- **Theory/Study**: Coval, J. D. and Shumway, T. (2001). Expected option returns. *Journal of Finance*, 56(3), 983–1009.
- **Citation+DOI**: https://doi.org/10.1111/0022-1082.00352
- **Core Insight**: Implied volatility consistently exceeds realised volatility — the variance-risk premium is empirically negative. A long-vol position therefore loses on average but pays out during stress. A long-vol-hedger uses this asymmetry: hold long-vol as a hedge in calm times, take profit on spikes.
- **Mathematical Formulation**: When `vol_proxy_t < θ_cheap_vol · long_run_vol`, BUY vol exposure. When `vol_proxy_t > θ_spike · long_run_vol`, SELL vol exposure (take profit on spike).
- **Empirical Evidence**: Coval-Shumway (2001); Bakshi-Kapadia-Madan (2003, RFS DOI 10.1093/rfs/16.1.0101) — risk-neutral-vs-physical moments; Carr-Wu (2009, RFS DOI 10.1093/rfs/hhn038) — variance-risk-premium evidence.
- **Relevance to This Agent**: Anchors the `long_vol_hedger` mode; provides the take-profit-on-spike rule.
- **Calibration Source**: Carr-Wu (2009); Bakshi-Kapadia-Madan (2003).
- **Falsification Conditions**: If `θ_cheap_vol = 0`, never buys vol; channel silent.
- **Alternative Theories**: Bondarenko (2004 *RFS-WP*) — variance-swap-pricing; Bollerslev-Tauchen-Zhou (2009, RFS DOI 10.1093/rfs/hhp008) — VRP-and-stock-returns; Cremers-Halling-Weinbaum (2015, *JF*) — aggregate-jump-tail-risk.

### Theory 5 — Augustin-Brenner-Subrahmanyam Volmageddon Inverse-VIX Cascade

- **Theory/Study**: Augustin, P., Brenner, M. and Subrahmanyam, M. G. (2020). Why is the volatility of volatility so high? *Journal of Financial Stability*, 51, 100793. (Volmageddon-2018 retrospective.)
- **Citation+DOI**: https://doi.org/10.1016/j.jfs.2020.100793
- **Core Insight**: Inverse-VIX-ETNs (e.g., XIV, SVXY) maintain a fixed `−1×` daily exposure to the VIX-future-front-month. When realised vol rises, the ETN must *buy* vol-futures to maintain the −1× exposure (procyclical demand). On 5 Feb 2018, this mechanical rebalance generated >$1bn of vol-buying flow within 30 minutes, killing several ETNs.
- **Mathematical Formulation**: `aum_t · (−1) = position_vol_t · vol_future_price_t`. When `vol_future_price_t` jumps, `position_vol` must be re-set to `−aum_t / vol_future_price_t`. Required adjustment: `Q* = (target_position_vol − current_position_vol)`.
- **Empirical Evidence**: Augustin-Brenner-Subrahmanyam (2020); SEC report on Volmageddon (2019); Eraker-Wu (2017, JFQA DOI 10.1017/S0022109017000370) — VIX-ETN-pricing.
- **Relevance to This Agent**: Anchors the `vol_etn_manager` mode; provides the procyclical mechanical-rebalance flow.
- **Calibration Source**: Augustin et al. (2020); Eraker-Wu (2017).
- **Falsification Conditions**: If `etn_leverage = 0`, no rebalance flow; channel silent.
- **Alternative Theories**: Whaley (2013 *JPM*) — VIX-product survey; Alexander-Korovilas (2013, *JPM*) — VIX-ETN-roll-yield; Bollerslev-Todorov (2011, JF DOI 10.1111/j.1540-6261.2011.01666.x) — tail-risk-and-jumps.

## Design Purpose and Activation Triggers

| Trigger condition                          | Activated mode                  | Effect                                    |
|--------------------------------------------|---------------------------------|-------------------------------------------|
| `                                          | F̃_t − P_t                       | /                                         |
| `σ̂_t > θ_high · σ̂_avg`                     | `vol_trader`                    | SELL — reduce exposure in high-vol regime |
| `σ̂_t < θ_low · σ̂_avg`                      | `vol_trader`                    | BUY — increase exposure in low-vol regime |
| `                                          | target_pos(σ_target) − position | > θ_rebal`                                |
| `vol_proxy_t < θ_cheap_vol · long_run_vol` | `long_vol_hedger`               | BUY vol                                   |
| `vol_proxy_t > θ_spike · long_run_vol`     | `long_vol_hedger`               | SELL vol (take profit)                    |
| `vol_future_price_t` jump                  | `vol_etn_manager`               | Mechanical rebalance to `−1×` exposure    |
| `<Default>`                                | any mode                        | NO action                                 |

**Prerequisite Signals:** price `P_t`, fundamental `F_t` (only `slow_adapter`), realised vol `σ̂_t`, long-run vol `σ̂_avg`, vol proxy `vol_proxy_t` (e.g., VIX), vol-future price `vol_future_price_t` (only `vol_etn_manager`).

**Missing-Signal Policy:** If `σ̂_t` missing, use 20-tick rolling std fallback. If `vol_proxy_t` missing, use `σ̂_t` as substitute. If `F_t` missing, deactivate `slow_adapter`. If `vol_future_price_t` missing, deactivate `vol_etn_manager`.

**Deactivation Conditions:** Wealth-based — `cash + position · P_t < W_min`. `vol_etn_manager` deactivates if `aum_t < aum_min` (ETN-termination event, as happened to XIV on 5 Feb 2018).

Market Contribution by Regime:

| Regime         | Contribution           | Mechanism                                                                                               |
|----------------|------------------------|---------------------------------------------------------------------------------------------------------|
| Calm           | Mildly stabilising     | `vol_trader` accumulates exposure in low-vol; `long_vol_hedger` buys cheap vol                          |
| Trending boom  | Mildly stabilising     | `slow_adapter` lagged sell into rising prices                                                           |
| Trending crash | Mixed                  | `equity_de_risker` and `vol_trader` sell into rising vol; `long_vol_hedger` takes profit                |
| Reversal phase | Mildly destabilising   | `slow_adapter` continues to react to old level; `vol_etn_manager` rebalance amplifies                   |
| Stress / Panic | Strongly destabilising | `vol_etn_manager` mechanical procyclical buy of vol-futures dominates; equity sell-flow from de-riskers |

Interaction with other agents: `vol_etn_manager` flow interacts with `MarketMakerLiquidityAgent` who absorbs only at widened spreads; `equity_de_risker` co-fires with `LeveragedFundInvestor.forced_unwind`; `long_vol_hedger` is a counter-flow to `ShortSellerAndShortVolTrader.short_vol_trader`; `slow_adapter` is the natural counter-party for fast-momentum agents.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: float (+ long, − short equity exposure)
- `position_vol`: float (only `long_vol_hedger`, `vol_etn_manager`)
- `cash`: float
- `F̃_t`: float (slow-adapter perceived fundamental)
- `σ̂_avg`: float (long-run vol average)
- `aum_t`: float (only `vol_etn_manager`)
- `tick_index`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    σ̂_t = realized_vol(t, W_vol)
    σ̂_avg_t = ema(σ̂, half_life=W_avg)

    if vol_mode == slow_adapter:
        F̃_t = (1 − update_weight) · F̃_{t−1} + update_weight · F_t
        dev = (F̃_t − P_t) / |F̃_t|
        if abs(dev) > θ_slow:
            Q* = base_pos · sign(dev) · abs(dev)
            emit MARKET sign(dev) of Q*

    if vol_mode == vol_trader:
        if σ̂_t > θ_high · σ̂_avg_t:
            target_pos = base_pos · (σ̂_avg_t / σ̂_t)
            Q* = ε · (target_pos − position)
            emit MARKET sign(Q*) of |Q*|
        elif σ̂_t < θ_low · σ̂_avg_t:
            target_pos = base_pos · (σ̂_avg_t / σ̂_t)
            Q* = ε · (target_pos − position)
            emit MARKET sign(Q*) of |Q*|

    if vol_mode == equity_de_risker:
        target_pos = (σ_target / σ̂_t) · base_pos
        if abs(target_pos − position) > θ_rebal:
            Q* = ε · (target_pos − position)
            emit MARKET sign(Q*) of |Q*|

    if vol_mode == long_vol_hedger:
        if vol_proxy_t < θ_cheap_vol · long_run_vol:
            emit MARKET buy vol of vol_size
        elif vol_proxy_t > θ_spike · long_run_vol:
            emit MARKET sell vol of vol_size · take_profit_frac · position_vol

    if vol_mode == vol_etn_manager:
        target_position_vol = − etn_leverage · aum_t / vol_future_price_t
        Q* = target_position_vol − position_vol
        if abs(Q*) > 0:
            emit MARKET sign(Q*) of |Q*|              # mechanical procyclical
```

#### 3.6.3 Slow-Adapter Belief Update (state input for slow_adapter)

```
on tick t:
    F̃_{t+1} = (1 − update_weight) · F̃_t + update_weight · F_t
    σ̂_avg_{t+1} = (1 − 1/W_avg) · σ̂_avg_t + (1/W_avg) · σ̂_t
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, F_t, σ̂_t, vol_proxy_t, vol_future_price_t, position, position_vol, cash, F̃_t, σ̂_avg_t, aum_t, vol_mode, RNG_seed)` the output `(action, Q*, T_life)` is a fully deterministic pure function — no Bernoulli draws. Heterogeneity comes from instantiation-time draws on `update_weight, θ_*, σ_target, etn_leverage, base_pos`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume, peer counter-party identity, news content, sentiment, narrative-strength, options chain individual contracts, or own forward P&L. The decision is taken from `(P_t, F_t, σ̂_t, vol_proxy_t, vol_future_price_t)` and the agent's own `(position, position_vol, F̃_t, σ̂_avg_t, aum_t)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t` (only `slow_adapter`), `σ̂_t`, `vol_proxy_t`, `vol_future_price_t` (only `vol_etn_manager`).
- Internal: `position`, `position_vol`, `cash`, `F̃_t`, `σ̂_avg_t`, `aum_t`, `tick_index`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty` (signed, equity).
2. `position_vol_{t+1} = position_vol_t + filled_qty_vol` (signed, vol).
3. `cash_{t+1}` adjusted for both legs.
4. `F̃` and `σ̂_avg` per 3.6.3.
5. `aum_{t+1} = cash_{t+1} + position_vol_{t+1} · vol_future_price_{t+1}` (vol_etn).
6. `tick_index += 1`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                            |
|----------------------|-----------------------------------------------------------------|
| Order types allowed  | MARKET (vol-regime decisions are decisive, not patient)         |
| Price level rule     | Cross the spread; no limit price                                |
| Order quantity rule  | Per-mode (see 3.6.2); `(target_pos − position)` for rebalancers |
| Order lifetime       | One tick (immediate-or-cancel)                                  |
| Cancellation policy  | Cancel-on-fill                                                  |
| Inventory constraint | Soft cap `                                                      |
| Wealth/leverage cap  | `cash + position · P_t ≥ W_min`; `aum_t ≥ aum_min` (vol_etn)    |
| Stop-loss/kill rule  | `vol_etn_manager`: `aum < aum_min` ⇒ permanent termination      |

## Parameters

| Symbol             | Name                     | Default | Range         | Units      | Source                 | Sensitivity | Notes              |
|--------------------|--------------------------|---------|---------------|------------|------------------------|-------------|--------------------|
| `update_weight`    | Slow-adapter speed       | 0.10    | [0.01, 0.50]  | weight     | Brock-Hommes (1998)    | High        | 1=immediate        |
| `θ_slow`           | Slow-adapter act trigger | 0.02    | [0.005, 0.10] | return     | Hommes (2006)          | Med         | Min `              |
| `θ_high`           | Vol-trader high cut      | 1.5     | [1.1, 3.0]    | mult       | Fleming et al. (2001)  | High        | High-vol switch    |
| `θ_low`            | Vol-trader low cut       | 0.7     | [0.3, 0.95]   | mult       | Fleming et al. (2001)  | High        | Low-vol switch     |
| `σ_target`         | Vol-target level         | 0.12    | [0.05, 0.30]  | annualised | Moreira-Muir (2017)    | High        | De-risker target   |
| `θ_rebal`          | Rebal threshold          | 100     | [10, 1000]    | shares     | implementation         | Med         | Min trade          |
| `ε`                | Rebalance speed          | 0.30    | [0.05, 1.00]  | frac       | Constantinides (1983)  | Med         | Per-tick frac      |
| `θ_cheap_vol`      | Cheap-vol threshold      | 0.7     | [0.3, 0.95]   | mult       | Carr-Wu (2009)         | High        | Buy-vol trigger    |
| `θ_spike`          | Spike-take-profit        | 1.8     | [1.2, 3.0]    | mult       | Bakshi et al. (2003)   | High        | Sell-vol trigger   |
| `take_profit_frac` | Take-profit fraction     | 0.50    | [0.10, 1.00]  | frac       | implementation         | Med         | Per-spike sell     |
| `etn_leverage`     | ETN target leverage      | 1.0     | [0.5, 3.0]    | mult       | Augustin et al. (2020) | High        | `−1×` typical      |
| `vol_size`         | Vol-hedger trade size    | 100     | [20, 1000]    | vol-shares | implementation         | High        | Per-tick scale     |
| `base_pos`         | Base position level      | 1000    | [100, 10000]  | shares     | implementation         | High        | Reference exposure |
| `W_vol`            | Vol window               | 20      | [5, 100]      | ticks      | Andersen et al. (2003) | Med         | Realised-vol       |
| `W_avg`            | Long-run-vol window      | 250     | [50, 1000]    | ticks      | Engle (1982)           | Med         | EMA half-life      |
| `long_run_vol`     | Long-run vol level       | 0.20    | [0.05, 0.50]  | annualised | Carr-Wu (2009)         | Med         | Reference vol      |
| `position_cap`     | Inventory cap            | 5000    | [1000, 50000] | shares     | implementation         | Med         | Soft constraint    |
| `W_min`            | Min wealth               | 0       | [−5e4, +5e4]  | currency   | implementation         | Low         | Stop-trading floor |
| `aum_min`          | ETN min AUM              | 1e5     | [1e3, 1e8]    | currency   | Augustin et al. (2020) | High        | Termination floor  |

## Population and Heterogeneity

```yaml
vol_mode_mixture:
  slow_adapter: 0.20
  vol_trader: 0.25
  equity_de_risker: 0.25
  long_vol_hedger: 0.15
  vol_etn_manager: 0.15
heterogeneity:
  update_weight: Beta(2, 18)              # mean ≈ 0.10
  theta_high: Lognormal(ln 1.5, 0.20)
  sigma_target: Lognormal(ln 0.12, 0.30)
  etn_leverage: Lognormal(ln 1.0, 0.10)
  base_pos: Lognormal(ln 1000, 0.50)
```

The 0.25 fraction for `equity_de_risker` matches risk-parity AUM share (≈ 20–25 % of systematic AUM per Asness-Frazzini-Pedersen 2012). The 0.15 `vol_etn_manager` fraction reflects pre-Volmageddon inverse-VIX-ETN AUM share of total VIX-ETN universe (~$3bn / ~$20bn in early 2018).

## Worked Numerical Examples

**Case 1 — Slow-adapter lag (`vol_mode = slow_adapter`)**: `F_{t} = 110, F̃_{t-1} = 100, P_t = 105, update_weight = 0.10, θ_slow = 0.02, base_pos = 1000`.
- `F̃_t = 0.9 · 100 + 0.1 · 110 = 101`. `dev = (101 − 105) / 101 = −0.0396`. `|dev| > 0.02`.
- `Q* = 1000 · (−1) · 0.0396 = −39.6 ≈ −40`.
- Action: MARKET sell 40 (slow-adapter still sees value < price, sells slowly).

**Case 2 — Vol-trader high regime (`vol_mode = vol_trader`)**: `σ̂_t = 0.30, σ̂_avg = 0.15, θ_high = 1.5, base_pos = 1000, position = 1000, ε = 0.30`.
- `σ̂_t / σ̂_avg = 2.0 > θ_high`. `target_pos = 1000 · 0.15 / 0.30 = 500`.
- `Q* = 0.30 · (500 − 1000) = −150`.
- Action: MARKET sell 150 (de-risk in high-vol regime).

**Case 3 — Equity de-risker (`vol_mode = equity_de_risker`)**: `σ_target = 0.12, σ̂_t = 0.20, base_pos = 1000, position = 1000, θ_rebal = 100, ε = 0.30`.
- `target_pos = (0.12/0.20) · 1000 = 600`. `|target − pos| = 400 > 100`.
- `Q* = 0.30 · (600 − 1000) = −120`.
- Action: MARKET sell 120 (vol-target rebalance).

**Case 4 — Vol-ETN procyclical rebalance (`vol_mode = vol_etn_manager`, Volmageddon-style)**: `aum_t = 1e6, etn_leverage = 1.0, vol_future_price_t = 20 (was 12 yesterday), position_vol = −83333` (set by yesterday's `−1·1e6/12`).
- `target_position_vol = −1.0 · 1e6 / 20 = −50,000`.
- `Q* = −50,000 − (−83333) = +33,333`. (Must BUY vol-futures to reduce negative exposure.)
- Action: MARKET buy 33,333 vol-futures — procyclical demand at the worst possible time.
- This reproduces the canonical Volmageddon-2018 dynamic where rising vol forced inverse-VIX-ETNs to buy vol-futures, driving vol higher.

**Edge case — ETN termination**: After several ticks of further vol-spike, `aum_t` may fall below `aum_min` (e.g., $100k). The mode permanently terminates and stops emitting flow — analogous to the XIV termination event of 5 Feb 2018.

## Validation and Calibration

- **V1 — GARCH vol-clustering response (Theory 1)**: Conditional on `σ̂_t > 1.5 · σ̂_avg`, observed `vol_trader` exposure should drop to ≈ `σ̂_avg / σ̂_t ≈ 0.67 · base_pos` (Fleming et al. 2001 magnitude). Ablation: `θ_high = ∞`.
- **V2 — Slow-adapter belief lag (Theory 2)**: After a fundamental shock, `F̃_t` should converge to `F_t` with half-life `≈ ln 2 / update_weight ≈ 7` ticks (Brock-Hommes 1998 prediction). Ablation: `update_weight = 1`.
- **V3 — Vol-target Sharpe improvement (Theory 3)**: Sharpe ratio of `equity_de_risker` should exceed the Sharpe of plain buy-and-hold by ≈ 30 % (Moreira-Muir 2017 magnitude). Ablation: `σ_target = ∞`.
- **V4 — Variance-risk-premium take-profit (Theory 4)**: Cross-section of `long_vol_hedger` returns should match Carr-Wu (2009) variance-swap excess return ≈ −5 % per month with positive skew. Ablation: `θ_cheap_vol = 0`.
- **V5 — Volmageddon procyclical demand (Theory 5)**: Conditional on `Δ vol_future_price > 50 %`, `vol_etn_manager` flow should exceed daily ETN-AUM-fraction of vol-future-OI (Augustin et al. 2020 magnitude — in 2018, ~10 % of front-month VIX-future-OI). Ablation: `etn_leverage = 0`.

**Ablation Hooks**:
- `update_weight = 1` → disables Theory 2 (slow-adapter delay).
- `θ_high = ∞` → disables Theory 1 (vol-clustering trade).
- `σ_target = ∞` → disables Theory 3 (vol-target rebalance).
- `θ_cheap_vol = 0` → disables Theory 4 (long-vol hedger).
- `etn_leverage = 0` → disables Theory 5 (Volmageddon channel).

## Academic References

1. Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773
2. Bollerslev, T. (1986). Generalized autoregressive conditional heteroscedasticity. *Journal of Econometrics*, 31(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1
3. Fleming, J., Kirby, C. and Ostdiek, B. (2001). The economic value of volatility timing. *Journal of Finance*, 56(1), 329–352. https://doi.org/10.1111/0022-1082.00327
4. Andersen, T. G., Bollerslev, T., Diebold, F. X. and Labys, P. (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), 579–625. https://doi.org/10.1111/1468-0262.00418
5. Brock, W. A. and Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274. https://doi.org/10.1016/S0165-1889(98)00011-6
6. Hommes, C. H. (2006). Heterogeneous agent models in economics and finance. In *Handbook of Computational Economics*, Vol. 2, 1109–1186. https://doi.org/10.1016/S1574-0021(05)02023-X
7. Greenwood, R. and Shleifer, A. (2014). Expectations of returns and expected returns. *Review of Financial Studies*, 27(3), 714–746. https://doi.org/10.1093/rfs/hht082
8. Moreira, A. and Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. https://doi.org/10.1111/jofi.12513
9. Barroso, P. and Santa-Clara, P. (2015). Momentum has its moments. *Journal of Financial Economics*, 116(1), 111–120. https://doi.org/10.1016/j.jfineco.2014.07.012
10. Coval, J. D. and Shumway, T. (2001). Expected option returns. *Journal of Finance*, 56(3), 983–1009. https://doi.org/10.1111/0022-1082.00352
11. Bakshi, G., Kapadia, N. and Madan, D. (2003). Stock return characteristics, skew laws, and the differential pricing of individual equity options. *Review of Financial Studies*, 16(1), 101–143. https://doi.org/10.1093/rfs/16.1.0101
12. Carr, P. and Wu, L. (2009). Variance risk premiums. *Review of Financial Studies*, 22(3), 1311–1341. https://doi.org/10.1093/rfs/hhn038
13. Bollerslev, T., Tauchen, G. and Zhou, H. (2009). Expected stock returns and variance risk premia. *Review of Financial Studies*, 22(11), 4463–4492. https://doi.org/10.1093/rfs/hhp008
14. Augustin, P., Brenner, M. and Subrahmanyam, M. G. (2020). Why is the volatility of volatility so high? *Journal of Financial Stability*, 51, 100793. https://doi.org/10.1016/j.jfs.2020.100793
15. Eraker, B. and Wu, Y. (2017). Explaining the negative returns to volatility claims: An equilibrium approach. *Journal of Financial and Quantitative Analysis*, 52(6), 2503–2534. https://doi.org/10.1017/S0022109017000370

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/VolatilityProductTrader.md` (legacy); five merged scenario profiles from `VolatilityClustering` (×2), `Volmageddon` (×3).
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 5.5 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
