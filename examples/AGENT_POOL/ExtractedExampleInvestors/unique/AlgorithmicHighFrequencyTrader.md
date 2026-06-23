# AlgorithmicHighFrequencyTrader

## Summary

| Field                        | Content                                                                                                                                                                                                                                                                               |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Algorithmic, high-frequency, and program-trading agents                                                                                                                                                                                                                               |
| Theory Family                | Microstructure (latency-arbitrage, order-flow imbalance); Trend-Following Systematic; Program-Trading Feedback Loops                                                                                                                                                                  |
| Market Role                  | **Mixed** — `hft_market_maker` (not active here, see [MarketMakerLiquidityAgent](MarketMakerLiquidityAgent.md)) is stabilising; `hft_momentum`, `algo_trender`, and `program_trader` are **destabilising** in stress because they feed positive-feedback loops once volatility spikes |
| Time Horizon                 | ultra-short (1–5 ticks for HFT; 5–30 ticks for algo/program)                                                                                                                                                                                                                          |
| Risk Tolerance               | medium — subject to strict per-tick `inventory_cap` and stop-loss kill rules                                                                                                                                                                                                          |
| Information Asymmetry        | none — all signals are public order-book / price observables, but speed advantage matters                                                                                                                                                                                             |
| Determinism                  | fully deterministic given `(P_t, P_{t−1}, OFI_t, σ̂_t, inventory_t, RNG_seed)` (no Bernoulli draws in the canonical implementation)                                                                                                                                                    |
| Merged profiles              | 3 (Program Trader, Algorithmic Trader, High Frequency Trader — across two scenarios)                                                                                                                                                                                                  |
| Source scenarios             | BlackMonday1987, FlashCrash                                                                                                                                                                                                                                                           |
| Canonical sub-archetype enum | `algo_mode ∈ {program_trader, algo_trender, hft_momentum}`                                                                                                                                                                                                                            |

## Definition and Goals

This agent models the **algorithmic / HFT / program-trading momentum-amplifier** family in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), spanning three merged profiles whose decision input is some combination of recent return, order-flow imbalance, and pre-set price thresholds. The three modes cover the Brady-Commission-1988 program-trading tier-based seller, the Hendershott-Jones-Menkveld (2011) trend-following systematic algorithm, and the Kirilenko-Kyle-Samadi-Tuzun (2017) HFT-momentum-amplifier from the 2010 flash crash.

**Primary goals:**
1. Reproduce the discrete tier-based program-trading cascade (Brady Commission 1988): each successive price threshold triggers a larger sell wave, producing the convex amplification documented during Black Monday.
2. Reproduce the HFT-momentum-amplifier dynamic (Kirilenko et al. 2017): when order-flow imbalance and short-horizon return co-move, the agent emits same-direction flow that further amplifies the move.
3. Reproduce the trend-following systematic-algo positive-feedback channel (Hendershott et al. 2011) at a longer horizon than HFT.
4. Permit ablation of each channel (program tiers vs. HFT momentum vs. trend-follow) to isolate its contribution to flash-crash dynamics, in line with the SEC-CFTC (2010) flash-crash report decomposition.

**Non-goals:**
1. Does NOT model latency arbitrage (co-location, geographic-arbitrage); the simulation is at single-tick resolution.
2. Does NOT model market-making activity — that is the [MarketMakerLiquidityAgent](MarketMakerLiquidityAgent.md) archetype.
3. Does NOT optimise execution-cost (TWAP/VWAP slicing); the agent emits its full per-tick `Q*` as a single market order.
4. Does NOT use `F_t` or any fundamental-value information; the algos are signal-only.

## Theoretical Foundation

### Theory 1 — Brady Commission Program Trading Tiers

- **Theory/Study**: Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. Washington, DC: U.S. Government Printing Office.
- **Citation+DOI**: ISBN N/A — Brady Report 1988 (US Treasury archival).
- **Core Insight**: During Black Monday 1987, automated portfolio-insurance and index-arbitrage program trades triggered at fixed price thresholds. Each threshold was 0.5–1 % below the prior, and the size of each tier exceeded the previous, generating convex selling pressure that exhausted the bid-side of the order book.
- **Mathematical Formulation**: Tier list `[(threshold_i, size_i)]`. When `(P_t − P_open)/P_open < threshold_i`, emit `Q* = size_i · (1 + |i − 1| · convex_factor)` and advance `tier_idx ← i + 1`.
- **Empirical Evidence**: Brady Commission (1988); Leland (1992, FAJ DOI 10.2469/faj.v48.n6.55) — portfolio-insurance retrospective; Genotte-Leland (1990, AER DOI 10.2307/2006677) — market-crash equilibrium model with program trading.
- **Relevance to This Agent**: Anchors the `program_trader` mode; provides the discrete tier-trigger amplification.
- **Calibration Source**: Brady Commission (1988); Leland (1992).
- **Falsification Conditions**: If `convex_factor = 0` and `size_i ≡ size_0`, all tiers are identical and convex amplification disappears.
- **Alternative Theories**: Grossman (1988, JBus DOI 10.1086/296434) — portfolio-insurance equilibrium-failure alternative; Carlson (2007, FRB Discussion) — Black Monday retrospective; Nofsinger-Sias (1999, JF DOI 10.1111/0022-1082.00188) — institutional-herding alternative.

### Theory 2 — Hendershott-Jones-Menkveld Algorithmic Trend-Following

- **Theory/Study**: Hendershott, T., Jones, C. M. and Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *Journal of Finance*, 66(1), 1–33.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2010.01624.x
- **Core Insight**: Algorithmic trading penetration is associated with improved liquidity in normal markets, but trend-following systematic algorithms generate positive-feedback flow during stress. The systematic algorithm reads short-horizon return signals and emits same-direction flow, amplifying short-horizon momentum.
- **Mathematical Formulation**: `signal_t = w_short · r_short_t + w_long · r_long_t`; emit `Q* = algo_size · sign(signal_t) · |signal_t|` when `|signal_t| > θ_algo`.
- **Empirical Evidence**: Hendershott-Jones-Menkveld (2011); Hendershott-Riordan (2013, JFE DOI 10.1016/j.jfineco.2013.07.005) — algorithmic-execution evidence; Boehmer-Fong-Wu (2021, JFQA DOI 10.1017/S0022109021000168) — international-evidence.
- **Relevance to This Agent**: Anchors the `algo_trender` mode; sets `w_short = 0.7, w_long = 0.3` for systematic-algo typical weighting.
- **Calibration Source**: Hendershott-Jones-Menkveld (2011); Boehmer et al. (2021).
- **Falsification Conditions**: If `algo_size = 0`, no flow; trend-follow channel is silent.
- **Alternative Theories**: Foucault-Hombert-Roşu (2016, JF DOI 10.1111/jofi.12302) — news-driven algo alternative; Brogaard-Hagströmer-Nordén-Riordan (2015, RFS DOI 10.1093/rfs/hhv045) — speed-bump-effects; Menkveld (2013, JFM DOI 10.1016/j.finmar.2013.06.006) — modern-MM survey.

### Theory 3 — Kirilenko-Kyle-Samadi-Tuzun HFT Momentum Cascade

- **Theory/Study**: Kirilenko, A., Kyle, A. S., Samadi, M. and Tuzun, T. (2017). The flash crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998.
- **Citation+DOI**: https://doi.org/10.1111/jofi.12498
- **Core Insight**: During the 2010 flash crash, HFT firms initially provided liquidity but then switched to momentum-following ("hot-potato") trading, passing inventory among themselves and amplifying the price move. The discrete switch occurs when realised volatility breaches a threshold and inventory risk-aversion dominates.
- **Mathematical Formulation**: When `σ̂_t > σ̂_threshold` AND `OFI_t · r_t > 0`, switch to momentum mode: `Q* = hft_size · sign(OFI_t) · |OFI_t|/OFI_norm`. In quiet markets `σ̂_t < σ̂_threshold` the agent is inactive.
- **Empirical Evidence**: Kirilenko et al. (2017) Tables 4–6 — hot-potato evidence; SEC-CFTC (2010) flash-crash report; Hagströmer-Nordén (2013, JFM DOI 10.1016/j.finmar.2013.06.006) — HFT-strategy decomposition.
- **Relevance to This Agent**: Anchors the `hft_momentum` mode; provides the volatility-conditional switch.
- **Calibration Source**: Kirilenko et al. (2017); SEC-CFTC (2010).
- **Falsification Conditions**: If `σ̂_threshold = ∞`, the agent never switches to momentum; its flow is silent.
- **Alternative Theories**: Easley-López de Prado-O'Hara (2012, RFS DOI 10.1093/rfs/hhs053) — VPIN-toxicity alternative; Biais-Foucault-Moinas (2015, JFE DOI 10.1016/j.jfineco.2015.03.004) — equilibrium-HFT model; Madhavan (2012, FAJ DOI 10.2469/faj.v68.n4.6) — flash-crash retrospective.

### Theory 4 — Order-Flow Imbalance Price Impact

- **Theory/Study**: Cont, R., Kukanov, A. and Stoikov, S. (2014). The price impact of order book events. *Journal of Financial Econometrics*, 12(1), 47–88.
- **Citation+DOI**: https://doi.org/10.1093/jjfinec/nbt003
- **Core Insight**: Short-horizon price moves are linearly explained by order-flow imbalance `OFI_t = Σ(buy_volume) − Σ(sell_volume)` rather than trade-volume per se. The HFT-momentum trader monitors `OFI_t` and trades in its direction.
- **Mathematical Formulation**: `r_t ≈ λ · OFI_t / depth_t`. Decision rule incorporates `OFI_t` directly.
- **Empirical Evidence**: Cont-Kukanov-Stoikov (2014); Brogaard-Hendershott-Riordan (2014, RFS DOI 10.1093/rfs/hhu032) — HFT-OFI-trading evidence; Kissell (2013, *Algorithmic Trading Methods*).
- **Relevance to This Agent**: Provides the `OFI_t` signal used in `hft_momentum` and feeds the magnitude scaling in `algo_trender`.
- **Calibration Source**: Brogaard-Hendershott-Riordan (2014).
- **Falsification Conditions**: If `OFI_norm = ∞`, the OFI scaling collapses; agent reverts to plain trend-follow.
- **Alternative Theories**: Almgren-Chriss (2001, RoF) — execution-cost-optimal alternative; Bouchaud-Bonart-Donier-Gould (2018, *Trades, Quotes and Prices*) — propagator-model alternative; Glosten-Harris (1988, JFE DOI 10.1016/0304-405X(88)90034-7) — adverse-selection-component decomposition.

### Theory 5 — Menkveld HFT Market Making and Adverse-Selection Costs

- **Theory/Study**: Menkveld, A. J. (2013). High frequency trading and the new market makers. *Journal of Financial Markets*, 16(4), 712–740.
- **Citation+DOI**: 10.1016/j.finmar.2013.06.006
- **Core Insight**: HFT firms act as the dominant new market makers; their market-making activity earns the bid-ask-spread but can suddenly withdraw or invert into directional momentum trading when adverse-selection costs spike, amplifying liquidity gaps in stress.
- **Mathematical Formulation**: HFT inventory `I_t` mean-reverts under ∂²spread/∂t < 0; once `adverse_selection_t > θ_AS`, agent flips from spread-capture to OFI-momentum mode within sub-second horizon.
- **Empirical Evidence**: Menkveld (2013); Hagströmer-Nordén (2013, JFM DOI 10.1016/j.finmar.2013.05.005); Brogaard-Garriott-Pomeranets (2014, JFM) Flash Crash 6 May 2010 inventory withdrawal evidence.
- **Relevance to This Agent**: Justifies the `hft_momentum` mode flip and the adverse-selection-driven liquidity withdrawal embedded in the cancellation-policy rule.
- **Calibration Source**: Menkveld (2013) inventory half-life; Hagströmer-Nordén (2013) for spread-capture vs. directional split.
- **Falsification Conditions**: If HFTs maintain market-making inventory through adverse-selection spikes, the regime-switch is rejected.
- **Alternative Theories**: Pure-rent-extraction view (Budish-Cramton-Shim 2015, QJE DOI 10.1093/qje/qjv027) — alternative explanation for HFT activity.

## Design Purpose and Activation Triggers

| Trigger condition                         | Activated mode                      | Effect                            |
|-------------------------------------------|-------------------------------------|-----------------------------------|
| `(P_t − P_open)/P_open < threshold_i`     | `program_trader`                    | Tier-i sell wave (convex)         |
| `                                         | w_short · r_short + w_long · r_long | > θ_algo`                         |
| `σ̂_t > σ̂_threshold` AND `OFI_t · r_t > 0` | `hft_momentum`                      | Same-direction OFI-momentum trade |
| `<Default>`                               | any mode                            | NO action                         |

**Prerequisite Signals:** price `P_t`, opening price `P_open`, recent returns `r_short_t = (P_t − P_{t−k_s})/P_{t−k_s}` and `r_long_t` (longer window), realised volatility `σ̂_t`, order-flow imbalance `OFI_t = Σ(buy_qty) − Σ(sell_qty)` over rolling window.

**Missing-Signal Policy:** If `OFI_t` missing, deactivate `hft_momentum`. If `P_open` missing, use `P_{t-W_open}` (rolling-window open) for `program_trader`. If `σ̂_t` missing, use 20-tick rolling std fallback.

**Deactivation Conditions:** Hard stop on inventory: `|inventory_t| > inventory_cap`. Stop-loss-kill on intraday-P&L: `pnl_intraday < kill_pnl_threshold`. Program-trader deactivates after all tiers exhausted.

Market Contribution by Regime:

| Regime         | Contribution           | Mechanism                                                                                                  |
|----------------|------------------------|------------------------------------------------------------------------------------------------------------|
| Calm           | Inactive               | All thresholds far from triggering; HFT-momentum mode requires `σ̂_t > σ̂_threshold`                         |
| Trending boom  | Mildly destabilising   | `algo_trender` and `hft_momentum` add same-direction flow                                                  |
| Trending crash | Strongly destabilising | `program_trader` cascades through tiers; `algo_trender` adds same-direction sell flow                      |
| Reversal phase | Destabilising          | `hft_momentum` may flip direction with the reversal, adding noise                                          |
| Stress / Panic | Strongly destabilising | All three modes co-fire; `program_trader` exhausts bid-side liquidity (Brady 1988 / SEC-CFTC 2010 dynamic) |

Interaction with other agents: amplifies `MomentumTrendTrader` flow at higher frequency; depletes the inventory budget of `MarketMakerLiquidityAgent` (who then widens spreads); feeds `LeveragedFundInvestor.forced_unwind` by increasing realised volatility and triggering margin calls; counter-acted by `Arbitrageur` and `BlockTradeBuyer` at deep discounts.

## Behavioural Framework

#### 3.6.1 State Variables

- `inventory`: float (+ long, − short)
- `cash`: float
- `tier_idx`: integer (only `program_trader`)
- `pnl_intraday`: float
- `last_OFI`: float
- `tick_index`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    r_short = (P_t − P_{t−k_s}) / P_{t−k_s}
    r_long  = (P_t − P_{t−k_l}) / P_{t−k_l}
    open_dev = (P_t − P_open) / P_open
    OFI = order_flow_imbalance(t)
    sigma_hat = realized_vol(t, W_vol)

    if abs(inventory) > inventory_cap or pnl_intraday < kill_pnl_threshold:
        # Kill-switch: forced flatten
        emit MARKET sign(-inventory) of |inventory|
        return

    if algo_mode == program_trader:
        while tier_idx < n_tiers and open_dev < tiers[tier_idx].threshold:
            size = tiers[tier_idx].size · (1 + tier_idx · convex_factor)
            emit MARKET sell of size
            tier_idx += 1

    if algo_mode == algo_trender:
        signal = w_short · r_short + w_long · r_long
        if abs(signal) > θ_algo:
            Q* = algo_size · sign(signal) · min(|signal| / θ_algo, q_cap)
            emit MARKET sign(signal) of Q*

    if algo_mode == hft_momentum:
        if sigma_hat > σ̂_threshold and OFI · r_short > 0:
            Q* = hft_size · sign(OFI) · min(|OFI| / OFI_norm, q_cap)
            emit MARKET sign(OFI) of Q*
```

#### 3.6.3 OFI / Volatility-State Update

```
on tick t (computed by environment):
    OFI_{t+1} = sum(buy_qty − sell_qty over window W_OFI)
    σ̂_{t+1} = std(returns over window W_vol)
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, P_{t−k_s}, P_{t−k_l}, P_open, OFI_t, σ̂_t, inventory_t, pnl_intraday_t, tier_idx, algo_mode, RNG_seed)` the output `(action, Q*, T_life)` is a fully deterministic pure function — no Bernoulli draws. Heterogeneity comes from instantiation-time draws on `θ_algo, σ̂_threshold, w_short, w_long, hft_size, algo_size, tier list`.

Does NOT use: fundamental value `F_t`, news content, sentiment, narrative-strength, peer counter-party identity, options chain, individual order-book level beyond aggregate `OFI_t`, traded-volume directly, or own forward P&L. The decision is taken from `(P_t, P_{t−k_s}, P_{t−k_l}, P_open, OFI_t, σ̂_t)` and the agent's own `(inventory, pnl_intraday, tier_idx)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `P_{t−k_s}`, `P_{t−k_l}`, `P_open`, `OFI_t`, `σ̂_t`.
- Internal: `inventory`, `cash`, `pnl_intraday`, `tier_idx`, `last_OFI`, `tick_index`.

**Update rule (post-fill, end of tick t):**
1. `inventory_{t+1} = inventory_t + filled_qty` (signed).
2. `cash_{t+1} = cash_t − filled_qty · fill_price`.
3. `pnl_intraday_{t+1} = cash_{t+1} + inventory_{t+1} · P_{t+1} − initial_equity`.
4. `tier_idx` advanced if `program_trader` fired.
5. `tick_index += 1`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                             |
|----------------------|------------------------------------------------------------------|
| Order types allowed  | MARKET (algo / HFT prioritises certainty-of-execution)           |
| Price level rule     | Cross the spread; no limit price                                 |
| Order quantity rule  | Per-mode (see 3.6.2); convex tier-amplified for `program_trader` |
| Order lifetime       | One tick (immediate-or-cancel)                                   |
| Cancellation policy  | Cancel-on-fill                                                   |
| Inventory constraint | Hard cap `                                                       |
| Wealth/leverage cap  | `pnl_intraday > kill_pnl_threshold` required                     |
| Stop-loss/kill rule  | `inventory` cap or `pnl` floor breach ⇒ flatten and deactivate   |

## Parameters

| Symbol               | Name                     | Default                             | Range         | Units    | Source                     | Sensitivity | Notes                  |
|----------------------|--------------------------|-------------------------------------|---------------|----------|----------------------------|-------------|------------------------|
| `tiers[i].threshold` | Program-trader trigger i | [-0.01, -0.02, -0.04, -0.07, -0.10] | per-i         | return   | Brady (1988)               | High        | Discrete cascade tiers |
| `tiers[i].size`      | Program-trader size i    | [200, 400, 800, 1600, 3200]         | per-i         | shares   | Brady (1988)               | High        | Convex doubling        |
| `convex_factor`      | Tier convex amplifier    | 0.50                                | [0.0, 2.0]    | mult     | Genotte-Leland (1990)      | High        | Per-tier extra         |
| `n_tiers`            | Number of program tiers  | 5                                   | [2, 10]       | count    | Brady (1988)               | Med         | Cascade depth          |
| `θ_algo`             | Algo-trender activation  | 0.005                               | [0.001, 0.05] | return   | Hendershott et al. (2011)  | High        | Min `                  |
| `algo_size`          | Algo-trender size scale  | 300                                 | [50, 2000]    | shares   | Boehmer et al. (2021)      | High        | Per-tick scale         |
| `w_short`            | Short-window weight      | 0.70                                | [0.30, 1.00]  | weight   | Hendershott et al. (2011)  | High        | Trend short            |
| `w_long`             | Long-window weight       | 0.30                                | [0.00, 0.70]  | weight   | Hendershott et al. (2011)  | High        | Trend long             |
| `k_s`                | Short window length      | 3                                   | [1, 10]       | ticks    | Boehmer et al. (2021)      | Med         | Short return           |
| `k_l`                | Long window length       | 20                                  | [10, 100]     | ticks    | Boehmer et al. (2021)      | Med         | Long return            |
| `σ̂_threshold`        | HFT volatility cut       | 0.02                                | [0.005, 0.10] | return   | Kirilenko et al. (2017)    | High        | Hot-potato switch      |
| `hft_size`           | HFT momentum size        | 100                                 | [20, 1000]    | shares   | Kirilenko et al. (2017)    | High        | Per-tick scale         |
| `OFI_norm`           | OFI normalisation        | 1000                                | [100, 100000] | shares   | Cont et al. (2014)         | Med         | Signal scale           |
| `W_OFI`              | OFI window               | 5                                   | [1, 50]       | ticks    | Cont et al. (2014)         | Med         | Imbalance look-back    |
| `W_vol`              | Vol window               | 20                                  | [5, 100]      | ticks    | Kirilenko et al. (2017)    | Med         | Realised-vol window    |
| `q_cap`              | Per-tick cap mult        | 5.0                                 | [1.0, 50.0]   | mult     | implementation             | Med         | Limits explosion       |
| `inventory_cap`      | Inventory hard cap       | 5000                                | [500, 50000]  | shares   | Hendershott-Riordan (2013) | High        | Kill-switch trigger    |
| `kill_pnl_threshold` | Daily P&L kill           | -1e4                                | [-1e6, -1e3]  | currency | implementation             | Med         | Drawdown stop          |
| `W_open`             | Rolling open window      | 100                                 | [1, 1000]     | ticks    | implementation             | Low         | Fallback               |

## Population and Heterogeneity

```yaml
algo_mode_mixture:
  program_trader: 0.30
  algo_trender: 0.40
  hft_momentum: 0.30
heterogeneity:
  theta_algo: Lognormal(ln 0.005, 0.40)
  algo_size: Lognormal(ln 300, 0.50)
  w_short: Beta(7, 3)                       # mean ≈ 0.70
  hft_size: Lognormal(ln 100, 0.50)
  sigma_hat_threshold: Lognormal(ln 0.02, 0.30)
  convex_factor: Beta(3, 7)                 # mean ≈ 0.30
  inventory_cap: Lognormal(ln 5000, 0.50)
```

The 0.40 fraction for `algo_trender` and 0.30 for `hft_momentum` matches Hendershott-Jones-Menkveld (2011) algorithm-trading-share evidence (≈ 70 % of US-equity volume by 2010). The 0.30 program-trader fraction matches portfolio-insurance-share at peak Brady-1988 deployment.

## Worked Numerical Examples

**Case 1 — Program trader cascade (`algo_mode = program_trader`)**: `P_t = 95, P_open = 100, open_dev = −0.05, tiers = [(-0.01, 200), (-0.02, 400), (-0.04, 800), (-0.07, 1600), (-0.10, 3200)], convex_factor = 0.5, tier_idx = 0`.
- Iter: `open_dev = −0.05 < −0.01`. Sell `200 · (1 + 0 · 0.5) = 200`. Idx → 1.
- Iter: `−0.05 < −0.02`. Sell `400 · 1.5 = 600`. Idx → 2.
- Iter: `−0.05 < −0.04`. Sell `800 · 2.0 = 1600`. Idx → 3.
- Iter: `−0.05 ≥ −0.07`. Halt. Total this tick: 200 + 600 + 1600 = 2400 shares sold via three tier waves.
- Reproduces the convex-cascade Brady-1988 dynamic.

**Case 2 — Algorithmic trend-follower (`algo_mode = algo_trender`)**: `r_short = 0.005, r_long = 0.003, w_short = 0.7, w_long = 0.3, θ_algo = 0.005, algo_size = 300, q_cap = 5.0`.
- `signal = 0.7 · 0.005 + 0.3 · 0.003 = 0.0035 + 0.0009 = 0.0044`. `|signal| = 0.0044 < 0.005 = θ_algo`. No trade.

**Case 3 — Algorithmic trend-follower with stronger signal**: same parameters, `r_short = 0.012`. 
- `signal = 0.7 · 0.012 + 0.3 · 0.003 = 0.0084 + 0.0009 = 0.0093`. `|signal| > 0.005`.
- `Q* = 300 · 1 · min(0.0093 / 0.005, 5.0) = 300 · 1.86 = 558`.
- Action: MARKET buy 558.

**Case 4 — HFT momentum cascade (`algo_mode = hft_momentum`)**: `σ̂_t = 0.05, σ̂_threshold = 0.02, OFI_t = -800, r_short = -0.008, hft_size = 100, OFI_norm = 1000, q_cap = 5.0`.
- `σ̂_t > σ̂_threshold`. `OFI · r_short = (−800) · (−0.008) = +6.4 > 0` ⇒ they co-move (both negative).
- `Q* = 100 · sign(−800) · min(800/1000, 5.0) = 100 · (−1) · 0.8 = −80`.
- Action: MARKET sell 80 (HFT joins the down move).

**Edge case — Inventory kill-switch**: `inventory = +5500`, `inventory_cap = 5000`. Kill-switch fires: emit MARKET sell 5500 (flatten). Mode deactivates. This reproduces the canonical HFT inventory-circuit-breaker behaviour observed during the 2010 flash crash (Kirilenko et al. 2017).

## Validation and Calibration

- **V1 — Program-trader cascade convexity (Theory 1)**: Per-tier sell flow ratio matches `(1 + i · convex_factor)`; cumulative-sell at tier 5 ≈ `Σ size_i · (1 + i · convex_factor) ≈ 6,200` for the canonical `[200..3200]` tier list with `convex_factor = 0.5`. Ablation: `convex_factor = 0`.
- **V2 — Algo trend-follow R² (Theory 2)**: Cross-section regression of `Q*` on `signal` for `algo_trender` should yield slope ≈ `algo_size / θ_algo` with R² > 0.85 (Hendershott et al. 2011 prediction). Ablation: `algo_size = 0`.
- **V3 — HFT momentum-switch (Theory 3)**: Conditional on `σ̂_t > σ̂_threshold`, `hft_momentum` participation rate ≈ 1.0; conditional on `σ̂_t < σ̂_threshold`, participation rate ≈ 0 (Kirilenko et al. 2017 hot-potato switch). Ablation: `σ̂_threshold = ∞`.
- **V4 — OFI price-impact slope (Theory 4)**: Aggregated `r_t` regression on `OFI_t` should yield slope `λ ≈ 1 / depth_t` with R² > 0.5 (Cont-Kukanov-Stoikov 2014 prediction). Ablation: `OFI_norm = ∞`.
- **V5 — Inventory kill-switch (cross)**: `|inventory|` distribution should be capped at `inventory_cap`; flush events should produce ≥ `inventory_cap` of one-tick flow (cross-validates V3 with V1's cascade).

**Ablation Hooks**:
- `convex_factor = 0` → disables Theory 1 (tier convex amplification).
- `algo_size = 0` → disables Theory 2 (trend-follow channel).
- `σ̂_threshold = ∞` → disables Theory 3 (HFT momentum switch).
- `OFI_norm = ∞` → degrades Theory 4 (collapses OFI signal).

## Academic References

1. Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. Washington, DC: U.S. Government Printing Office.
2. Leland, H. E. (1992). Insurance, hedging, and crash dynamics. *Financial Analysts Journal*, 48(6), 55–62. https://doi.org/10.2469/faj.v48.n6.55
3. Genotte, G. and Leland, H. E. (1990). Market liquidity, hedging, and crashes. *American Economic Review*, 80(5), 999–1021. https://doi.org/10.2307/2006677
4. Grossman, S. J. (1988). An analysis of the implications for stock and futures price volatility of program trading and dynamic hedging strategies. *Journal of Business*, 61(3), 275–298. https://doi.org/10.1086/296434
5. Hendershott, T., Jones, C. M. and Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *Journal of Finance*, 66(1), 1–33. https://doi.org/10.1111/j.1540-6261.2010.01624.x
6. Hendershott, T. and Riordan, R. (2013). Algorithmic trading and the market for liquidity. *Journal of Financial Economics*, 110(2), 396–411. https://doi.org/10.1016/j.jfineco.2013.07.005
7. Boehmer, E., Fong, K. Y. L. and Wu, J. J. (2021). Algorithmic trading and market quality: International evidence. *Journal of Financial and Quantitative Analysis*, 56(8), 2659–2688. https://doi.org/10.1017/S0022109021000168
8. Kirilenko, A., Kyle, A. S., Samadi, M. and Tuzun, T. (2017). The flash crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498
9. Easley, D., López de Prado, M. M. and O'Hara, M. (2012). Flow toxicity and liquidity in a high-frequency world. *Review of Financial Studies*, 25(5), 1457–1493. https://doi.org/10.1093/rfs/hhs053
10. Biais, B., Foucault, T. and Moinas, S. (2015). Equilibrium fast trading. *Journal of Financial Economics*, 116(2), 292–313. https://doi.org/10.1016/j.jfineco.2015.03.004
11. Madhavan, A. (2012). Exchange-traded funds, market structure, and the flash crash. *Financial Analysts Journal*, 68(4), 20–35. https://doi.org/10.2469/faj.v68.n4.6
12. Cont, R., Kukanov, A. and Stoikov, S. (2014). The price impact of order book events. *Journal of Financial Econometrics*, 12(1), 47–88. https://doi.org/10.1093/jjfinec/nbt003
13. Brogaard, J., Hendershott, T. and Riordan, R. (2014). High-frequency trading and price discovery. *Review of Financial Studies*, 27(8), 2267–2306. https://doi.org/10.1093/rfs/hhu032
14. Brogaard, J., Hagströmer, B., Nordén, L. and Riordan, R. (2015). Trading fast and slow: Colocation and liquidity. *Review of Financial Studies*, 28(12), 3407–3443. https://doi.org/10.1093/rfs/hhv045
15. Foucault, T., Hombert, J. and Roşu, I. (2016). News trading and speed. *Journal of Finance*, 71(1), 335–382. https://doi.org/10.1111/jofi.12302

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/AlgorithmicHighFrequencyTrader.md` (legacy); three merged scenario profiles from `BlackMonday1987`, `FlashCrash` (×2).
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 5.4 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
