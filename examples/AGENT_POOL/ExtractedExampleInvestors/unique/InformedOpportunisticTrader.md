# InformedOpportunisticTrader

## Summary

| Field                        | Content                                                                                                                                                                                                                                                                                                           |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Informed, insider, block-trade, IPO-flipping, and opportunistic traders                                                                                                                                                                                                                                           |
| Theory Family                | Microstructure (Kyle informed trading); Limits-of-Arbitrage / Fire-Sale Liquidity Provision; IPO Underpricing / Flipping; Front-running                                                                                                                                                                           |
| Market Role                  | **Mixed** — `block_trade_buyer` is **stabilising** (provides discount-floor liquidity); `information_trader` and `insider_advantaged` are **mildly destabilising** (front-run cascades but later cover); `ipo_flipper` and `opportunistic_trader` are **mildly destabilising** (momentum-following participation) |
| Time Horizon                 | short-to-medium (10–200 ticks); patient enough to absorb blocks, fast enough to flip                                                                                                                                                                                                                              |
| Risk Tolerance               | medium-to-high (informed conviction underwrites the position)                                                                                                                                                                                                                                                     |
| Information Asymmetry        | high — defining feature: agents observe a private signal `s_t = F_t + ε_priv_t` with `Var(ε_priv) < Var(ε_public)`                                                                                                                                                                                                |
| Determinism                  | mostly deterministic given `(s_t, P_t, F_t)` (one Bernoulli signal-arrival draw per tick for `information_trader`)                                                                                                                                                                                                |
| Merged profiles              | 5 (Block Trade Buyer, Information Trader, IPO Flipper, Opportunistic Trader, Insider Advantaged — across four scenarios)                                                                                                                                                                                          |
| Source scenarios             | ArchegosCollapse, DotComBubble, SorosPound, SouthSeaBubble                                                                                                                                                                                                                                                        |
| Canonical sub-archetype enum | `info_mode ∈ {block_trade_buyer, information_trader, ipo_flipper, opportunistic_trader, insider_advantaged}`                                                                                                                                                                                                      |

## Definition and Goals

This agent models the **informed / opportunistic / block-trade / IPO-flipping / insider** trader family in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), spanning five merged profiles whose decision input is a privileged signal — a private fundamental observation, an order-flow leak, an awareness of a scheduled forced unwind, or political-economy information about announcements. The five modes cover the Shleifer-Vishny (1992) fire-sale liquidity provider, the Kyle (1985) informed trader, the Ritter (1991) IPO flipper, the momentum-following opportunistic trader, and the historical politically-connected insider.

**Primary goals:**
1. Reproduce the Kyle (1985) informed-trader linear-equilibrium pattern: trade size proportional to `(s_t − P_t)`, with information advantage decaying as price moves to incorporate it.
2. Reproduce the fire-sale liquidity-provision dynamic (Shleifer-Vishny 1992; Brunnermeier-Pedersen 2009): `block_trade_buyer` activates at deep discounts (e.g., `−30 %` from peak) and absorbs forced supply.
3. Reproduce the IPO underpricing / flipping pattern (Ritter 1991; Ofek-Richardson 2003): buy at issuance discount, sell on first-day pop.
4. Permit ablation of the information channel (signal noise variance) and the fire-sale channel (`discount_threshold`) to isolate which channel matters per scenario.

**Non-goals:**
1. Does NOT solve a strategic submission game (Kyle-style optimal lambda); informed trade is a simple proportional rule.
2. Does NOT model the production of the private signal — `s_t` is exogenous input from the simulation environment.
3. Does NOT model the political-economy production of insider information; the `insider_advantaged` mode treats it as an exogenous early-arrival signal.
4. Does NOT engage in market-making (continuous two-sided quoting); trades are directional and patient.

## Theoretical Foundation

### Theory 1 — Kyle Informed Trading

- **Theory/Study**: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335.
- **Citation+DOI**: https://doi.org/10.2307/1913210
- **Core Insight**: An informed trader with private signal `s` about terminal value `v` submits orders proportional to `(s − P_t)`. The market maker sets price `P_t = E[v | order flow]` linearly in `flow`. The informed trader's profit is `(v − P_t) · q*` and decays as the price incorporates the signal.
- **Mathematical Formulation**: `Q* = β · (s_t − P_t)` with `β = 1 / (2 · λ)` where `λ` is the price-impact slope. In simplified rule form: `Q* = info_size · sign(s_t − P_t) · |s_t − P_t| / σ_s`.
- **Empirical Evidence**: Kyle (1985); Easley-O'Hara (1992, JF DOI 10.1111/j.1540-6261.1992.tb04402.x) — PIN measure; Glosten-Milgrom (1985, JFE DOI 10.1016/0304-405X(85)90044-3) — sequential informed-trade model; Bhattacharya-Spiegel (1991, RFS DOI 10.1093/rfs/4.2.255) — informed-trade-size evidence.
- **Relevance to This Agent**: Anchors the `information_trader` and `insider_advantaged` modes; provides the linear `(s_t − P_t)` decision rule.
- **Calibration Source**: Easley-O'Hara (1992); Bhattacharya-Spiegel (1991).
- **Falsification Conditions**: If `s_t = P_t` (i.e., signal matches price), no order; informed channel is silent.
- **Alternative Theories**: Holden-Subrahmanyam (1992, JF DOI 10.1111/j.1540-6261.1992.tb04652.x) — multi-period strategic informed; Foster-Viswanathan (1996, JF DOI 10.1111/j.1540-6261.1996.tb05206.x) — heterogeneous informed; Back (1992, RFS DOI 10.1093/rfs/5.3.387) — continuous-time Kyle.

### Theory 2 — Shleifer-Vishny Fire-Sale Liquidity Provision

- **Theory/Study**: Shleifer, A. and Vishny, R. W. (1992). Liquidation values and debt capacity: A market equilibrium approach. *Journal of Finance*, 47(4), 1343–1366.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1992.tb04661.x
- **Core Insight**: When natural buyers (industry peers) are themselves financially distressed, asset prices in fire-sale auctions fall below fundamental value. Outside opportunistic buyers with cash and patience can earn excess returns by absorbing supply. The discount level is determined by the gap between forced-supply and outside-buyer capital.
- **Mathematical Formulation**: When `(P_t − F_t)/F_t < −discount_threshold` AND `cash > min_cash`, emit `Q* = absorption_size · |d_t| · cash / P_t`.
- **Empirical Evidence**: Shleifer-Vishny (1992); Pulvino (1998, JF DOI 10.1111/0022-1082.00050) — aircraft fire-sale evidence; Coval-Stafford (2007, JFE DOI 10.1016/j.jfineco.2006.05.005) — mutual-fund fire-sale evidence; Mitchell-Pulvino (2012, JF DOI 10.1111/j.1540-6261.2012.01740.x) — convertible-arbitrage forced-unwind.
- **Relevance to This Agent**: Anchors the `block_trade_buyer` mode; sets `discount_threshold = 0.20` (20 % discount typical of forced-block evidence).
- **Calibration Source**: Pulvino (1998); Coval-Stafford (2007).
- **Falsification Conditions**: If `discount_threshold = 0`, the agent buys at any price; there is no fire-sale channel. If `cash = 0`, no flow.
- **Alternative Theories**: Brunnermeier-Pedersen (2009, RFS DOI 10.1093/rfs/hhn098) — funding-liquidity-cascade alternative; Acharya-Pedersen (2005, JFE DOI 10.1016/j.jfineco.2004.06.007) — liquidity-CAPM; Allen-Gale (1994, AER DOI 10.2307/2117986) — cash-in-the-market-pricing.

### Theory 3 — Ritter / Ofek-Richardson IPO Flipping

- **Theory/Study**: Ritter, J. R. (1991). The long-run performance of initial public offerings. *Journal of Finance*, 46(1), 3–27. Ofek, E. and Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113–1138.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.1991.tb03743.x ; https://doi.org/10.1111/1540-6261.00560
- **Core Insight**: IPOs are systematically underpriced (~15–20 % first-day pop), and a population of "flippers" buys at issuance and sells immediately into the first-day pop. The trade is short-horizon, mechanical, and has high turnover — flippers do not hold for the long-run drift documented in Ritter (1991).
- **Mathematical Formulation**: When `tick_since_IPO < W_flip` AND `(P_t − P_IPO)/P_IPO > θ_flip`, emit `Q* = flip_fraction · position`.
- **Empirical Evidence**: Ritter (1991); Ofek-Richardson (2003) — dot-com IPO evidence; Aggarwal (2003, JF DOI 10.1111/1540-6261.00543) — institutional flipping; Lowry-Schwert (2002, JF DOI 10.1111/1540-6261.00485) — IPO cycles.
- **Relevance to This Agent**: Anchors the `ipo_flipper` mode; sets `θ_flip = 0.10` (10 % pop) typical first-day flip threshold.
- **Calibration Source**: Aggarwal (2003); Ofek-Richardson (2003).
- **Falsification Conditions**: If `θ_flip = ∞`, no flips; the IPO-flipping channel is silent.
- **Alternative Theories**: Loughran-Ritter (2002, RFS DOI 10.1093/rfs/15.2.413) — prospect-theory IPO-issuer alternative; Benveniste-Spindt (1989, JFE DOI 10.1016/0304-405X(89)90051-2) — book-building IPO alternative; Cornelli-Goldreich-Ljungqvist (2006, JF DOI 10.1111/j.1540-6261.2006.00876.x) — investor-sentiment-IPO.

### Theory 4 — Brunnermeier-Pedersen Front-Running of Forced Trades

- **Theory/Study**: Brunnermeier, M. K. and Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825–1863.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2005.00781.x
- **Core Insight**: When a leveraged trader is known to be facing a forced unwind (e.g., a margin call), informed predators can profit by selling first and buying back at the cascade-low. This is a refinement of the Kyle (1985) informed-trader model where the "private signal" is knowledge of impending forced supply.
- **Mathematical Formulation**: When `forced_unwind_signal_t = 1`, emit `Q* = front_run_fraction · expected_unwind_size · sign(forced_direction)`. Cover at the cascade-low: when `cum_drawdown < −θ_cover`, emit reverse `Q*`.
- **Empirical Evidence**: Brunnermeier-Pedersen (2005); Carlin-Lobo-Viswanathan (2007, JF DOI 10.1111/j.1540-6261.2007.01254.x) — episodic-liquidity-evidence; Christophe-Ferri-Hsieh (2010, JFE DOI 10.1016/j.jfineco.2010.01.001) — pre-announcement short-selling evidence.
- **Relevance to This Agent**: Anchors the `information_trader` mode (front-running of `LeveragedFundInvestor.forced_unwind` flow).
- **Calibration Source**: Carlin et al. (2007); Christophe et al. (2010).
- **Falsification Conditions**: If `front_run_fraction = 0`, no predatory flow; channel silent.
- **Alternative Theories**: Attari-Mello-Ruckes (2005, JF DOI 10.1111/j.1540-6261.2005.00808.x) — predator-prey alternative; Hirshleifer-Subrahmanyam-Titman (1994, JF DOI 10.1111/j.1540-6261.1994.tb00071.x) — information-hierarchies; Cespa-Foucault (2014, RFS DOI 10.1093/rfs/hhu030) — cross-asset informed-learning.

### Theory 5 — Allen-Gorton Politically-Connected Insider

- **Theory/Study**: Allen, F. and Gorton, G. (1993). Churning bubbles. *Review of Economic Studies*, 60(4), 813–836.
- **Citation+DOI**: https://doi.org/10.2307/2298101
- **Core Insight**: Politically connected investors (or any agent with privileged-timing information about announcements) systematically trade in advance of public-information arrival. In historical bubbles (South Sea, Mississippi), insiders profited from the bubble inflation while late entrants suffered. The agent's flow is correlated with the announcement direction but precedes it.
- **Mathematical Formulation**: When `narrative_event_t` (or `announcement_imminent_t`), trigger early. Trade size `Q* = insider_size · sign(announcement_direction)`.
- **Empirical Evidence**: Allen-Gorton (1993); Temin-Voth (2004, JFE DOI 10.1016/j.jfineco.2003.07.001) — South-Sea bank-of-Hoare insider-trading evidence; Velikonja (2014, MLR) — insider-trading retrospective; Bhattacharya (2014, JF Survey).
- **Relevance to This Agent**: Anchors the `insider_advantaged` mode.
- **Calibration Source**: Temin-Voth (2004).
- **Falsification Conditions**: If `insider_size = 0` or `announcement_signal` always missing, the channel is silent.
- **Alternative Theories**: Manove (1989, QJE DOI 10.2307/2937928) — risk-bearing insider-tax model; Fishman-Hagerty (1992, RAND DOI 10.2307/2555867) — insider-trade welfare; Ausubel (1990, AER DOI 10.2307/2006669) — insider-trade equilibrium.

## Design Purpose and Activation Triggers

| Trigger condition                                             | Activated mode                   | Effect                              |
|---------------------------------------------------------------|----------------------------------|-------------------------------------|
| `(P_t − F_t)/F_t < −discount_threshold` AND `cash > min_cash` | `block_trade_buyer`              | Large MARKET buy at discount        |
| `                                                             | s_t − P_t                        | > θ_info`                           |
| `forced_unwind_signal_t = 1`                                  | `information_trader` (front-run) | Sell ahead of cascade; cover at low |
| `tick_since_IPO < W_flip` AND `(P_t − P_IPO)/P_IPO > θ_flip`  | `ipo_flipper`                    | Sell `flip_fraction · position`     |
| `r_t > θ_opp` (momentum participation)                        | `opportunistic_trader`           | Same-direction MARKET trade         |
| `announcement_imminent_t = 1`                                 | `insider_advantaged`             | Pre-announcement directional trade  |
| `<Default>`                                                   | any mode                         | NO action                           |

**Prerequisite Signals:** price `P_t`, fundamental `F_t`, recent return `r_t`, private signal `s_t = F_t + ε_priv_t` (modes 2,5), `forced_unwind_signal_t ∈ {0,1}`, `announcement_imminent_t ∈ {0,1}`, `tick_since_IPO ∈ ℕ`, `P_IPO`.

**Missing-Signal Policy:** If `s_t` missing, deactivate `information_trader` (Kyle channel). If `forced_unwind_signal` missing, treat as 0. If `announcement_imminent` missing, treat as 0. If `P_IPO` missing, deactivate `ipo_flipper`. If `F_t` missing, fall back to 200-tick rolling-mean (`block_trade_buyer` only).

**Deactivation Conditions:** Wealth-based — `cash + position · P_t < W_min`. `ipo_flipper` deactivates after `tick_since_IPO > W_flip`. `insider_advantaged` deactivates after announcement is made (information no longer private).

Market Contribution by Regime:

| Regime         | Contribution         | Mechanism                                                                                                |
|----------------|----------------------|----------------------------------------------------------------------------------------------------------|
| Calm           | Mildly stabilising   | `information_trader` Kyle-style trades push price toward `s_t ≈ F_t`                                     |
| Trending boom  | Mixed                | `ipo_flipper` and `insider_advantaged` extract gains; `block_trade_buyer` inactive                       |
| Trending crash | Strongly stabilising | `block_trade_buyer` activates at `−discount_threshold`; absorbs forced supply                            |
| Reversal phase | Mildly stabilising   | `information_trader` covers; `block_trade_buyer` continues to support price                              |
| Stress / Panic | Strongly stabilising | `block_trade_buyer` provides discount-floor liquidity; `information_trader` covers shorts on cascade-low |

Interaction with other agents: counter-flow against `PanicForcedSeller` and `LeveragedFundInvestor.forced_unwind` (the `block_trade_buyer` absorbs their supply); complement `Arbitrageur` whose convergence trade benefits from the same `(s_t − P_t)` signal; `information_trader` front-runs the same flows that `MarketMakerLiquidityAgent` is unable to absorb during stress.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: float (+ long, − short)
- `cash`: float
- `tick_since_IPO`: integer (only `ipo_flipper`)
- `is_short_front_run`: bool (only `information_trader`)
- `entry_price_short`: float (only `information_trader` cover)
- `tick_index`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    d_t = (P_t − F_t) / F_t
    r_t = (P_t − P_{t−1}) / P_{t−1}

    if info_mode == block_trade_buyer:
        if d_t < −discount_threshold and cash > min_cash:
            Q* = absorption_size · |d_t| · cash / P_t
            Q* = min(Q*, cash / P_t · max_buy_frac)
            emit MARKET buy of Q*

    if info_mode == information_trader:
        if forced_unwind_signal_t and not is_short_front_run:
            Q* = front_run_fraction · expected_unwind_size
            emit MARKET sell of Q*
            is_short_front_run ← True
            entry_price_short ← P_t
        elif is_short_front_run and cum_drawdown_t < −θ_cover:
            emit MARKET buy of |Q*_outstanding|             # cover
            is_short_front_run ← False
        else:
            # Kyle-channel
            if abs(s_t − P_t) > θ_info:
                Q* = info_size · sign(s_t − P_t) · |s_t − P_t| / σ_s
                emit MARKET sign(s_t − P_t) of Q*

    if info_mode == ipo_flipper:
        if tick_since_IPO < W_flip:
            pop = (P_t − P_IPO) / P_IPO
            if pop > θ_flip and position > 0:
                Q* = flip_fraction · position
                emit MARKET sell of Q*
            elif pop < −θ_flip_buy and tick_since_IPO < W_buy_window:
                Q* = entry_size                              # IPO-day buy
                emit MARKET buy of Q*

    if info_mode == opportunistic_trader:
        if abs(r_t) > θ_opp:
            Q* = opp_size · sign(r_t) · |r_t|
            emit MARKET sign(r_t) of Q*

    if info_mode == insider_advantaged:
        if announcement_imminent_t:
            Q* = insider_size
            emit MARKET sign(announcement_direction_t) of Q*
```

#### 3.6.3 Information-Decay Update (Kyle channel)

```
on tick t (after fill):
    # private signal becomes public after horizon W_priv
    if tick_index > tick_signal_acquired + W_priv:
        s_t ← P_t   # signal value collapses to price
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, F_t, r_t, s_t, forced_unwind_signal_t, announcement_imminent_t, tick_since_IPO, P_IPO, position, cash, info_mode, RNG_seed)` the output `(action, Q*, T_life)` is a pure function modulo a single `Bernoulli(p_signal_arrival)` draw per tick for `information_trader` and `insider_advantaged` (signal-arrival noise). Heterogeneity comes from instantiation-time draws on `discount_threshold, info_size, θ_*, flip_fraction, t_aware_imminent`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume directly, peer counter-party identity (only the aggregate `forced_unwind_signal`), narrative-strength, sentiment, options chain, or own forward P&L. The decision is taken from `(P_t, F_t, r_t, s_t, forced_unwind_signal, announcement_imminent_t, tick_since_IPO, P_IPO)` and the agent's own `(position, cash, is_short_front_run)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `r_t`, `s_t`, `forced_unwind_signal_t`, `announcement_imminent_t`, `tick_since_IPO`, `P_IPO`.
- Internal: `position`, `cash`, `is_short_front_run`, `entry_price_short`, `tick_signal_acquired`, `tick_index`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty` (signed).
2. `cash_{t+1} = cash_t − filled_qty · fill_price`.
3. If `ipo_flipper`: `tick_since_IPO += 1`.
4. If signal expired: `s_t ← P_t` per 3.6.3.
5. `tick_index += 1`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                         |
|----------------------|--------------------------------------------------------------|
| Order types allowed  | MARKET (informed conviction is decisive, no patient quoting) |
| Price level rule     | Cross the spread; no limit price                             |
| Order quantity rule  | Per-mode (see 3.6.2); proportional to `(s_t − P_t)` or `     |
| Order lifetime       | One tick (immediate-or-cancel)                               |
| Cancellation policy  | Cancel-on-fill                                               |
| Inventory constraint | Soft cap `                                                   |
| Wealth/leverage cap  | `cash + position · P_t ≥ W_min`                              |
| Stop-loss/kill rule  | `ipo_flipper`: `tick_since_IPO > W_flip` ⇒ deactivate        |

## Parameters

| Symbol               | Name                       | Default | Range         | Units    | Source                       | Sensitivity | Notes                   |
|----------------------|----------------------------|---------|---------------|----------|------------------------------|-------------|-------------------------|
| `discount_threshold` | Fire-sale buy trigger      | 0.20    | [0.05, 0.50]  | return   | Pulvino (1998)               | High        | Block-buyer activation  |
| `min_cash`           | Min cash for buy           | 1e4     | [1e3, 1e6]    | currency | implementation               | Med         | Capital floor           |
| `absorption_size`    | Block buyer scale          | 0.50    | [0.10, 1.0]   | frac     | Coval-Stafford (2007)        | High        | Per-tick absorption     |
| `max_buy_frac`       | Max cash deployed          | 0.50    | [0.10, 1.0]   | frac     | implementation               | Med         | Conservatism            |
| `θ_info`             | Kyle info trigger          | 0.005   | [0.001, 0.05] | return   | Easley-O'Hara (1992)         | High        | `                       |
| `info_size`          | Kyle informed size         | 200     | [50, 1000]    | shares   | implementation               | High        | Per-tick scale          |
| `σ_s`                | Signal-noise std           | 0.02    | [0.005, 0.10] | return   | Bhattacharya-Spiegel (1991)  | High        | Signal precision        |
| `W_priv`             | Signal horizon             | 50      | [10, 500]     | ticks    | Kyle (1985)                  | Med         | Information half-life   |
| `front_run_fraction` | Front-run scale            | 0.30    | [0.05, 1.0]   | frac     | Brunnermeier-Pedersen (2005) | High        | Predator size           |
| `θ_cover`            | Cover threshold            | 0.10    | [0.03, 0.30]  | return   | implementation               | Med         | Front-run cover trigger |
| `θ_flip`             | IPO flip threshold         | 0.10    | [0.02, 0.50]  | return   | Aggarwal (2003)              | High        | First-day pop trigger   |
| `θ_flip_buy`         | IPO buy-dip threshold      | 0.05    | [0.01, 0.20]  | return   | implementation               | Med         | IPO-day discount        |
| `flip_fraction`      | Flip sell fraction         | 0.80    | [0.30, 1.0]   | frac     | Ofek-Richardson (2003)       | High        | Per-flip exit           |
| `entry_size`         | IPO-day buy size           | 100     | [10, 1000]    | shares   | implementation               | Med         | Per-IPO entry           |
| `W_flip`             | Flip window                | 5       | [1, 30]       | ticks    | Aggarwal (2003)              | Med         | First-week-only         |
| `W_buy_window`       | IPO-buy window             | 1       | [1, 5]        | ticks    | Ofek-Richardson (2003)       | Low         | First-day-only          |
| `θ_opp`              | Opportunistic momentum cut | 0.01    | [0.003, 0.05] | return   | implementation               | Med         | Momentum trigger        |
| `opp_size`           | Opportunistic size         | 200     | [50, 1000]    | shares   | implementation               | Med         | Per-tick scale          |
| `insider_size`       | Insider trade size         | 400     | [100, 2000]   | shares   | Temin-Voth (2004)            | High        | Per-announcement        |
| `position_cap`       | Inventory cap              | 5000    | [1000, 50000] | shares   | implementation               | Med         | Soft constraint         |
| `W_min`              | Min wealth                 | 0       | [−5e4, +5e4]  | currency | implementation               | Low         | Stop-trading floor      |

## Population and Heterogeneity

```yaml
info_mode_mixture:
  block_trade_buyer: 0.20
  information_trader: 0.25
  ipo_flipper: 0.20
  opportunistic_trader: 0.20
  insider_advantaged: 0.15
heterogeneity:
  discount_threshold: Lognormal(ln 0.20, 0.30)
  info_size: Lognormal(ln 200, 0.50)
  sigma_s: Lognormal(ln 0.02, 0.40)
  flip_fraction: Beta(8, 2)                 # mean ≈ 0.80
  W_priv: Uniform(20, 100)
  insider_size: Lognormal(ln 400, 0.50)
```

The 0.25 fraction for `information_trader` matches the Easley-O'Hara (1992) PIN-distribution-evidence that ~ 20–25 % of order flow is informed in liquid markets. The 0.20 IPO-flipper fraction matches Aggarwal (2003) institutional-flipping rates.

## Worked Numerical Examples

**Case 1 — Block trade buyer at discount (`info_mode = block_trade_buyer`)**: `P_t = 50, F_t = 100, d_t = −0.50, discount_threshold = 0.20, cash = 1e6, absorption_size = 0.50, max_buy_frac = 0.50`.
- `d_t < −0.20 = −discount_threshold`, `cash > min_cash`. Activate.
- Raw `Q* = 0.50 · 0.50 · 1,000,000 / 50 = 5,000`.
- Cap: `0.50 · 1,000,000 / 50 = 10,000`. Use raw `5,000`.
- Action: MARKET buy 5,000 at $50.

**Case 2 — Kyle informed trader (`info_mode = information_trader`, no forced unwind)**: `P_t = 100, s_t = 102, |s_t − P_t| = 2, info_size = 200, σ_s = 0.02 · 100 = 2`.
- `(s_t − P_t) > 0`. `Q* = 200 · 1 · 2 / 2 = 200`.
- Action: MARKET buy 200 (informed-Kyle linear-equilibrium).

**Case 3 — Information trader front-run (`info_mode = information_trader`, forced unwind known)**: `forced_unwind_signal_t = 1, expected_unwind_size = 1000, front_run_fraction = 0.30`.
- `Q* = 0.30 · 1000 = 300`. Sell direction.
- Action: MARKET sell 300; set `is_short_front_run = True`, `entry_price_short = 100`. Cover when `cum_drawdown < −0.10`.

**Case 4 — IPO flipper (`info_mode = ipo_flipper`)**: `tick_since_IPO = 1, P_t = 115, P_IPO = 100, pop = 0.15, θ_flip = 0.10, position = 100, flip_fraction = 0.80`.
- `pop > θ_flip`, `position > 0`. `Q* = 0.80 · 100 = 80`.
- Action: MARKET sell 80 (first-day pop flip).

**Edge case — Information decay**: Agent acquires `s_t = 102` at tick 50 with `P_t = 100`. Trades `Q* = 200`. By tick 100, `tick_index = 100 > tick_signal_acquired + W_priv = 100`, so `s_t ← P_t` (signal collapses to price). All subsequent ticks have `|s_t − P_t| = 0` and the agent is silent until next signal arrives. This reproduces the Kyle (1985) information-decay pattern.

## Validation and Calibration

- **V1 — Kyle linear-equilibrium fit (Theory 1)**: Cross-section regression of `Q*` on `(s_t − P_t)` should yield slope ≈ `info_size / σ_s` with R² > 0.9 for the `information_trader` sub-population (Kyle 1985 prediction). Ablation: `info_size = 0`.
- **V2 — Fire-sale liquidity provision (Theory 2)**: Conditional on `d_t < −0.20`, observed `block_trade_buyer` flow ≥ `absorption_size · |d_t| · aggregate_cash / P_t` (Coval-Stafford 2007 magnitude). Ablation: `discount_threshold = 0`.
- **V3 — IPO first-day pop and flip (Theory 3)**: For population fraction `ipo_flipper ≥ 0.20`, observed first-tick sell flow after IPO should match `flip_fraction · sum(positions) · 1{pop > θ_flip}` (Aggarwal 2003 magnitude ≈ 0.80 · 0.50 = 0.40 of issuance). Ablation: `θ_flip = ∞`.
- **V4 — Front-running profit (Theory 4)**: `information_trader` front-run cycle profit (sell-low, cover-low) should average `front_run_fraction · expected_unwind_size · θ_cover` per cycle (Brunnermeier-Pedersen 2005 prediction). Ablation: `front_run_fraction = 0`.
- **V5 — Insider directional accuracy (Theory 5)**: Conditional on `announcement_imminent_t = 1`, observed flow direction matches `announcement_direction_t` ≥ 90 % of the time (Temin-Voth 2004 South-Sea evidence). Ablation: `insider_size = 0`.

**Ablation Hooks**:
- `info_size = 0` → disables Theory 1 (Kyle channel).
- `discount_threshold = 0` → disables Theory 2 (fire-sale channel).
- `θ_flip = ∞` → disables Theory 3 (IPO-flipping channel).
- `front_run_fraction = 0` → disables Theory 4 (predatory channel).
- `insider_size = 0` → disables Theory 5 (insider channel).

## Academic References

1. Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315–1335. https://doi.org/10.2307/1913210
2. Easley, D. and O'Hara, M. (1992). Time and the process of security price adjustment. *Journal of Finance*, 47(2), 577–605. https://doi.org/10.1111/j.1540-6261.1992.tb04402.x
3. Glosten, L. R. and Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3
4. Holden, C. W. and Subrahmanyam, A. (1992). Long-lived private information and imperfect competition. *Journal of Finance*, 47(1), 247–270. https://doi.org/10.1111/j.1540-6261.1992.tb04652.x
5. Shleifer, A. and Vishny, R. W. (1992). Liquidation values and debt capacity: A market equilibrium approach. *Journal of Finance*, 47(4), 1343–1366. https://doi.org/10.1111/j.1540-6261.1992.tb04661.x
6. Pulvino, T. C. (1998). Do asset fire sales exist? An empirical investigation of commercial aircraft transactions. *Journal of Finance*, 53(3), 939–978. https://doi.org/10.1111/0022-1082.00050
7. Coval, J. and Stafford, E. (2007). Asset fire sales (and purchases) in equity markets. *Journal of Financial Economics*, 86(2), 479–512. https://doi.org/10.1016/j.jfineco.2006.05.005
8. Mitchell, M. and Pulvino, T. (2012). Arbitrage crashes and the speed of capital. *Journal of Finance*, 67(5), 1799–1834. https://doi.org/10.1111/j.1540-6261.2012.01740.x
9. Ritter, J. R. (1991). The long-run performance of initial public offerings. *Journal of Finance*, 46(1), 3–27. https://doi.org/10.1111/j.1540-6261.1991.tb03743.x
10. Ofek, E. and Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113–1138. https://doi.org/10.1111/1540-6261.00560
11. Aggarwal, R. (2003). Allocation of initial public offerings and flipping activity. *Journal of Financial Economics*, 68(1), 111–135. https://doi.org/10.1016/S0304-405X(02)00248-6
12. Brunnermeier, M. K. and Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825–1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x
13. Carlin, B. I., Lobo, M. S. and Viswanathan, S. (2007). Episodic liquidity crises: Cooperative and predatory trading. *Journal of Finance*, 62(5), 2235–2274. https://doi.org/10.1111/j.1540-6261.2007.01254.x
14. Allen, F. and Gorton, G. (1993). Churning bubbles. *Review of Economic Studies*, 60(4), 813–836. https://doi.org/10.2307/2298101
15. Temin, P. and Voth, H.-J. (2004). Riding the South Sea Bubble. *American Economic Review*, 94(5), 1654–1668. https://doi.org/10.1257/0002828043052268

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/InformedOpportunisticTrader.md` (legacy); five merged scenario profiles from `ArchegosCollapse` (×2), `DotComBubble`, `SorosPound`, `SouthSeaBubble`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 5.3 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
