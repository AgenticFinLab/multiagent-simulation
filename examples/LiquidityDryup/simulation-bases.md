# LiquidityDryup Simulation — Theoretical Bases

## §1 Phenomenon Overview

Liquidity dry-up describes episodes in which market makers simultaneously withdraw from providing bid-ask quotes, causing a self-reinforcing cascade of rising price impact, forced selling, further volatility, and further withdrawal. The phenomenon is distinct from a simple price decline: it is a collapse in the *ability* to trade at any reasonable price. Liquidity dry-ups have been documented in the 1987 stock market crash, LTCM crisis (1998), the 2007–08 financial crisis, and the March 2020 COVID shock.

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Grossman & Miller (1988) formalised the market maker as an "immediacy provider" who absorbs temporary order imbalances in exchange for the bid-ask spread. Amihud & Mendelson (1986) showed that illiquidity is priced — assets with higher bid-ask spreads must offer higher expected returns. The modern micro-foundations of liquidity dry-up come from Brunnermeier & Pedersen (2009), who identified the feedback loop between *funding liquidity* (access to leverage) and *market liquidity* (ability to transact): when funding liquidity tightens, leveraged market makers are forced to cut positions, widening spreads and reducing market liquidity, which in turn further tightens funding liquidity. Kyle (1985) provided the original model of price impact proportional to order size, showing that illiquidity amplifies informed-trader price impact.

#### §1.1.2 Real-World Event Catalogue

| Event                     | Period                 | Liquidity Signature                                                                                         | Price Impact                                                                                                 |
|---------------------------|------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Black Monday              | October 19, 1987       | Specialists failed to maintain orderly markets; portfolio insurance selling overwhelmed order books         | DJIA –22.6% in one day; bid-ask spreads widened 10×                                                          |
| LTCM Crisis               | August–October 1998    | Hedge fund forced selling triggered market maker withdrawal across bond and equity markets                  | Russian default caused correlated liquidity dry-up in multiple asset classes; Fed-orchestrated rescue        |
| Global Financial Crisis   | September–October 2008 | Interbank funding market freeze; money market funds "broke the buck"; primary dealer market makers withdrew | TED spread peaked at 465 bps; CDS markets became illiquid; bid-ask spreads in corporate bonds widened 20–50× |
| Flash Crash               | May 6, 2010            | High-frequency market makers withdrew simultaneously, creating a 1,000-point Dow intraday drop              | Nearly $1 trillion in market value evaporated in minutes; prices recovered within 36 minutes                 |
| COVID-19 Liquidity Crisis | March 2020             | Even US Treasury bonds became illiquid; hedge funds faced margin calls; ETF spreads widened dramatically    | 10-year Treasury bid-ask spread reached 10× normal; Fed emergency purchases required                         |

#### §1.1.3 Book Literature

| Title                                            | Author(s)                    | Year | Relevance                                                      |
|--------------------------------------------------|------------------------------|------|----------------------------------------------------------------|
| *Market Liquidity: Theory, Evidence, and Policy* | Foucault, Pagano & Röell     | 2013 | Comprehensive treatment of market microstructure and liquidity |
| *When Genius Failed*                             | Roger Lowenstein             | 2000 | Narrative account of LTCM and liquidity spiral mechanisms      |
| *The Big Short*                                  | Michael Lewis                | 2010 | Credit market illiquidity during GFC; market maker withdrawal  |
| *Firefighting*                                   | Bernanke, Geithner & Paulson | 2019 | Policy response to GFC liquidity dry-up; lender-of-last-resort |
| *Advances in Financial Machine Learning*         | Marcos López de Prado        | 2018 | Quantitative methods for measuring market impact and liquidity |

---

## §2 Theoretical Framework

### §T1 Grossman–Miller Immediacy Model (Grossman & Miller 1988)

#### §T1.1 Citation
Grossman, S. J., & Miller, M. H. (1988). Liquidity and Market Structure. *Journal of Finance*, 43(3), 617–633. doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)

#### §T1.2 Core Claim
Market makers earn the bid-ask spread as compensation for providing immediacy. Their inventory risk determines the spread; when inventory risk becomes unbearable (extreme volatility, forced positions), they withdraw, making the spread theoretically infinite.

#### §T1.3 Simulation Mapping
`MarketMaker` provides `base_liquidity` in normal conditions and sets `provides_liquidity = 0` when `volatility > volatility_threshold`. The threshold triggers the withdrawal described in Grossman–Miller: when inventory risk exceeds the market maker's risk tolerance, they stop quoting.

#### §T1.4 Key Parameters
`volatility_threshold`, `base_liquidity`, `withdraw_rebalance` (inventory offload ratio), `normal_rebalance`

#### §T1.5 Limitations
A single volatility threshold replaces the continuous spread-widening of the Grossman–Miller model; partial withdrawal and graduated spread widening are not implemented.

---

### §T2 Brunnermeier–Pedersen Liquidity Spiral (Brunnermeier & Pedersen 2009)

#### §T2.1 Citation
Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity. *Review of Financial Studies*, 22(6), 2201–2238. doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)

#### §T2.2 Core Claim
Market liquidity and funding liquidity are mutually reinforcing. When speculators face funding constraints, they cut positions → prices fall → margins rise → more cutting (margin spiral). Simultaneously, higher volatility → wider margins → less capacity to absorb order flow (loss spiral). The combination creates a discontinuous "dry-up" equilibrium.

#### §T2.3 Simulation Mapping
The spiral is encoded through the price impact formula `liquidity_factor = 100 / max(total_liquidity, 10)`: as `MarketMaker` withdraws (provides_liquidity drops), `total_liquidity` falls, `liquidity_factor` rises, and price impact for the same net demand increases, generating larger price moves that trigger further withdrawal. `LiquiditySeeker` amplifies this by reducing order size proportional to `liquidity / liquidity_base`.

#### §T2.4 Key Parameters
`base_liquidity`, `price_impact` (λ), `liquidity_factor = 100 / max(total_liquidity, 10)`

#### §T2.5 Limitations
Funding liquidity (leverage constraints, margin calls) is not modelled directly; only market liquidity (bid-ask / price impact) is simulated. The two-spiral structure collapses into a single price-impact spiral.

---

### §T3 Kyle Market Impact Model (Kyle 1985)

#### §T3.1 Citation
Kyle, A. S. (1985). Continuous Auctions and Insider Trading. *Econometrica*, 53(6), 1315–1335. doi:[10.2307/1913210](https://doi.org/10.2307/1913210)

#### §T3.2 Core Claim
Price impact is proportional to net order flow: `ΔP = λ × NetDemand`. The coefficient λ (Kyle's lambda) reflects the informativeness of order flow. In liquid markets, λ is small; in illiquid markets, λ is large.

#### §T3.3 Simulation Mapping
The Market agent uses `P(t+1) = P(t) + (price_impact × NetDemand × liquidity_factor) + mean_reversion + ε`. The effective Kyle lambda becomes `price_impact × liquidity_factor`, which rises endogenously as liquidity providers withdraw — replicating the illiquidity amplification in Kyle.

#### §T3.4 Key Parameters
`price_impact` (base λ), `liquidity_factor` (endogenous amplifier), `noise_std`

#### §T3.5 Limitations
Kyle's model assumes a competitive market maker who sets price as a function of total order flow; here the market maker is a strategic agent whose withdrawal changes the price-setting function.

---

### §T4 Amihud Illiquidity Measure (Amihud 2002)

#### §T4.1 Citation
Amihud, Y. (2002). Illiquidity and Stock Returns: Cross-Section and Time-Series Effects. *Journal of Financial Markets*, 5(1), 31–56. doi:[10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6)

Amihud, Y., & Mendelson, H. (1986). Asset Pricing and the Bid-Ask Spread. *Journal of Financial Economics*, 17(2), 223–249. doi:[10.1016/0304-405X(86)90065-6](https://doi.org/10.1016/0304-405X(86)90065-6)

#### §T4.2 Core Claim
The Amihud illiquidity ratio `ILLIQ = |return| / volume` measures price impact per unit of trading volume. High ILLIQ indicates a market where small trades move prices significantly — the hallmark of a liquidity dry-up episode.

#### §T4.3 Simulation Mapping
The `LiquidityRatioIndex` metric (§4 of analysis-bases.md) implements an Amihud-style measure computed from the simulation's price history and total volume. Rising LRI across rounds signals an ongoing dry-up episode.

#### §T4.4 Key Parameters
`price_history`, `volume_history`; computed as `mean(|return(t)| / volume(t))`

#### §T4.5 Limitations
Volume is approximated as total absolute order quantity; the simulation does not distinguish between informed and uninformed volume as in Amihud (2002).

---

### §T5 Momentum and Cascade Dynamics (De Long et al. 1990)

#### §T5.1 Citation
De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive Feedback Investment Strategies and Destabilizing Rational Speculation. *Journal of Finance*, 45(2), 379–395. doi:[10.1111/j.1540-6261.1990.tb03695.x](https://doi.org/10.1111/j.1540-6261.1990.tb03695.x)

#### §T5.2 Core Claim
Momentum traders follow recent returns; this positive-feedback trading can destabilise prices and amplify liquidity dry-ups. Even rational speculators may engage in destabilising momentum if they anticipate that noise traders will continue driving prices in the same direction.

#### §T5.3 Simulation Mapping
`MomentumTrader` implements `quantity = return × momentum_multiplier if |return| > momentum_threshold`. During a liquidity dry-up, large price moves triggered by reduced liquidity activate momentum traders, who amplify the move, reduce liquidity further, and contribute to the cascade spiral.

#### §T5.4 Key Parameters
`momentum_threshold`, `momentum_multiplier`; max quantity ±35

#### §T5.5 Limitations
Momentum is conditioned only on the single-period return; multi-period trend following and stop-loss dynamics are not implemented.

---

## §3 Agent Architecture

| Class             | §4 Reference | Role                                            | Liquidity Provision                             | Market Impact                           |
|-------------------|--------------|-------------------------------------------------|-------------------------------------------------|-----------------------------------------|
| `MarketMaker`     | §4.1         | Immediacy provider; withdraws in stress         | `base_liquidity` when calm; 0 when volatile     | Stabilising (normal); absent (stress)   |
| `LiquiditySeeker` | §4.2         | Needs to trade; constrained by low liquidity    | None                                            | Random; scales with available liquidity |
| `ValueTrader`     | §4.3         | Fundamental-anchored; provides crisis liquidity | `base_liquidity_provision` when deviation large | Stabilising                             |
| `MomentumTrader`  | §4.4         | Trend follower; cascade amplifier               | None                                            | Destabilising                           |
| `NoiseTrader`     | §4.5         | Random order flow                               | None                                            | Random (Gaussian)                       |

---

## §4 Investor Taxonomy

### §4.1 MarketMaker

**Summary**: Implements the Grossman–Miller (1988) immediacy provider who earns the bid-ask spread in normal conditions but withdraws when inventory risk from high volatility exceeds their risk tolerance. Withdrawal triggers the liquidity spiral by reducing `total_liquidity` and amplifying price impact.

**Foundation**: Grossman, S. J., & Miller, M. H. (1988). doi:10.1111/j.1540-6261.1988.tb04594.x; Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:10.1093/rfs/hhn098

**Design Purpose**: Model the endogenous withdrawal of liquidity providers under stress. The critical threshold `volatility_threshold` represents the point where inventory risk dominates the spread revenue, replicating the empirically observed "liquidity vacuum" in stress episodes.

**Behavioral Framework**:

| Decision Variable | Logic                         | Formula                                                                        |
|-------------------|-------------------------------|--------------------------------------------------------------------------------|
| `volatility`      | Single-period absolute return | `                                                                              |
| Stress condition  | Exceed volatility threshold   | `volatility > volatility_threshold`                                            |
| Stress response   | Withdraw + offload inventory  | `provides_liquidity = 0; quantity = −position × withdraw_rebalance`            |
| Normal response   | Provide liquidity + rebalance | `provides_liquidity = base_liquidity; quantity = −position × normal_rebalance` |
| Quantity cap      | Risk management               | `max(−25, min(25, quantity))`                                                  |

**Decision Walkthrough**:
1. Receive market data: `{price, return, liquidity}`.
2. Compute `volatility = |return|`.
3. If `volatility > volatility_threshold`: set `provides_liquidity = 0`; sell/buy `position × withdraw_rebalance` shares to reduce inventory.
4. Else: set `provides_liquidity = base_liquidity`; rebalance inventory by `position × normal_rebalance`.
5. Cap quantity at ±25.

**Worked Example**: `position = 10`, `|return| = 0.04 > volatility_threshold = 0.03`. Withdraw: `provides_liquidity = 0`, `quantity = −10 × 0.5 = −5` (sell 5 to reduce inventory). Effective liquidity in market drops by `base_liquidity`, amplifying next-round price impact.

**References**: simulation-bases.md §2 Theory 1 (Grossman–Miller); doi:10.1111/j.1540-6261.1988.tb04594.x; doi:10.1093/rfs/hhn098

---

### §4.2 LiquiditySeeker

**Summary**: Represents institutional investors or fund managers who need to transact (rebalancing, redemptions) regardless of market conditions, but whose execution is constrained by available liquidity. When liquidity is low, they reduce order size — representing the demand-side of the liquidity spiral.

**Foundation**: Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:10.1093/rfs/hhn098; Coval, J., & Stafford, E. (2007). Asset fire sales (and purchases) in equity markets. *Journal of Financial Economics*, 86(2), 479–512. doi:[10.1016/j.jfineco.2006.09.007](https://doi.org/10.1016/j.jfineco.2006.09.007)

**Design Purpose**: Capture the demand-side of the liquidity dry-up: investors who would normally trade at their desired size but are forced to scale back when liquidity disappears. This creates a "missing demand" that prevents prices from recovering.

**Behavioral Framework**:

| Decision Variable    | Logic                       | Formula                                  |
|----------------------|-----------------------------|------------------------------------------|
| `target_quantity`    | Random trade size           | `N(0, target_volatility)`                |
| Liquidity adjustment | Scale down in low liquidity | `min(1.0, liquidity / liquidity_base)`   |
| Actual quantity      | Adjusted order              | `target_quantity × liquidity_adjustment` |
| Quantity cap         | Risk management             | `max(−20, min(20, quantity))`            |

**Decision Walkthrough**:
1. Sample target quantity from `N(0, target_volatility)`.
2. Compute `liquidity_adjustment = min(1.0, liquidity / liquidity_base)`.
3. `quantity = target_quantity × liquidity_adjustment` — reduces order when liquidity is scarce.
4. Cap at ±20 and apply cash/position constraints.

**Worked Example**: `target_quantity = 15`, `liquidity = 40`, `liquidity_base = 100`. `adjustment = 0.4`. Actual quantity = `15 × 0.4 = 6`. In normal conditions (`liquidity = 100`), would trade 15; in dry-up, trades only 6.

**References**: simulation-bases.md §2 Theory 2 (Brunnermeier–Pedersen); doi:10.1093/rfs/hhn098

---

### §4.3 ValueTrader

**Summary**: Fundamental-anchored investor who buys when price is below fundamental and sells when above, providing stabilising liquidity when market prices deviate significantly. During a dry-up, `ValueTrader` acts as the last line of defence against extreme price dislocation.

**Foundation**: Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35–55. doi:[10.1111/j.1540-6261.1997.tb03807.x](https://doi.org/10.1111/j.1540-6261.1997.tb03807.x); Amihud, Y., & Mendelson, H. (1986). doi:10.1016/0304-405X(86)90065-6

**Design Purpose**: Model the patient capital that eventually halts a liquidity dry-up. When `|deviation| > trade_threshold`, `ValueTrader` provides both liquidity (`base_liquidity_provision`) and a corrective price signal. Their limited size (cap ±25) reflects limits-to-arbitrage constraints.

**Behavioral Framework**:

| Decision Variable   | Logic                            | Formula                               |
|---------------------|----------------------------------|---------------------------------------|
| `deviation`         | Price deviation from fundamental | `(fundamental − price) / fundamental` |
| Liquidity provision | Active when large deviation      | `base_liquidity_provision if          |
| Quantity            | Value-corrective trade           | `deviation × value_multiplier if      |
| Quantity cap        | Limits to arbitrage              | `max(−25, min(25, quantity))`         |

**Decision Walkthrough**:
1. Compute `deviation = (fundamental − price) / fundamental`.
2. If `|deviation| > liquidity_threshold`: provide `base_liquidity_provision` to market.
3. If `|deviation| > trade_threshold`: trade `deviation × value_multiplier` (buy if underpriced, sell if overpriced).
4. Cap at ±25.

**Worked Example**: `fundamental = 100`, `price = 85`, `deviation = 0.15 > trade_threshold = 0.05`. `quantity = 0.15 × 100 = 15`. Buy 15 shares + provide `base_liquidity_provision = 20` liquidity units.

**References**: simulation-bases.md §2 Theory 3 (Kyle Impact); doi:10.1111/j.1540-6261.1997.tb03807.x

---

### §4.4 MomentumTrader

**Summary**: Trend follower that amplifies price moves — a critical accelerant in the liquidity spiral. By buying into rising prices and selling into falling prices, `MomentumTrader` intensifies the market maker's stress trigger, causing more withdrawal and less liquidity.

**Foundation**: De Long, J. B., et al. (1990). doi:10.1111/j.1540-6261.1990.tb03695.x; Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:10.1093/rfs/hhn098

**Design Purpose**: Model the positive-feedback traders who transform an initial liquidity shock into a self-reinforcing cascade. Momentum trading in the simulation acts as the coupling mechanism between price impact and market maker withdrawal: large returns trigger momentum buys/sells → amplified price impact → higher `|return|` → market maker withdrawal → further amplification.

**Behavioral Framework**:

| Decision Variable | Logic                 | Formula                       |
|-------------------|-----------------------|-------------------------------|
| `ret`             | Single-period return  | `market_data["return"]`       |
| Activation        | Significant trend     | `                             |
| Quantity          | Proportional to trend | `ret × momentum_multiplier`   |
| Quantity cap      | Position risk limit   | `max(−35, min(35, quantity))` |

**Decision Walkthrough**:
1. Receive `return` from market.
2. If `|return| ≤ momentum_threshold`: hold.
3. Else: `quantity = return × momentum_multiplier` (positive return → buy; negative → sell).
4. Cap at ±35 (larger than other agents to reflect momentum trader aggression).

**Worked Example**: `return = −0.04`, `momentum_threshold = 0.02`, `momentum_multiplier = 500`. `quantity = −0.04 × 500 = −20`. Sell 20 shares, amplifying the decline, further stressing market makers.

**References**: simulation-bases.md §2 Theory 5 (Momentum Cascades); doi:10.1111/j.1540-6261.1990.tb03695.x

---

### §4.5 NoiseTrader

**Summary**: Submits random Gaussian order flow that provides baseline liquidity and masks informed trading signals. During a dry-up, noise trading is the only source of trading volume when market makers withdraw, but its random direction provides no stabilising force.

**Foundation**: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. doi:[10.1111/j.1540-6261.1986.tb04513.x](https://doi.org/10.1111/j.1540-6261.1986.tb04513.x); De Long, J. B., et al. (1990). doi:10.1111/j.1540-6261.1990.tb03695.x

**Design Purpose**: Represent uninformed trading that provides market depth in normal conditions but cannot substitute for market makers during a stress event. High noise volatility relative to market maker liquidity can trigger dry-up even without a fundamental shock.

**Behavioral Framework**:

| Decision Variable  | Logic           | Formula                       |
|--------------------|-----------------|-------------------------------|
| Quantity           | Random Gaussian | `N(0, noise_volatility)`      |
| Quantity cap       | Risk management | `max(−15, min(15, quantity))` |
| Provides liquidity | Never           | Always 0                      |

**Decision Walkthrough**:
1. Sample `quantity ~ N(0, noise_volatility)`.
2. Cap at ±15.
3. Submit order; `provides_liquidity = 0` always.

**Worked Example**: `noise_volatility = 5`. Sample `quantity = 8.3`. Buy 8 shares at current price. No contribution to `total_liquidity` — market maker withdrawal is not offset.

**References**: simulation-bases.md §2 Theory 5; doi:10.1111/j.1540-6261.1986.tb04513.x

---

## §5 Market Mechanism

Price formation with endogenous liquidity amplification:

```
P(t+1) = P(t) + (λ × NetDemand × liquidity_factor) + γ × (F − P(t)) + ε(t)
```

Where:
```
total_liquidity(t) = base_liquidity + Σ provides_liquidity_i(t)
liquidity_factor(t) = 100 / max(total_liquidity(t), 10)
```

| Parameter                | Symbol | Typical Value   | Role                  |
|--------------------------|--------|-----------------|-----------------------|
| Price impact coefficient | λ      | 0.001           | Base Kyle lambda      |
| Liquidity factor         | 100/L  | 1.0–10.0        | Endogenous amplifier  |
| Mean reversion           | γ      | 0.05            | Fundamental anchor    |
| Noise                    | ε      | N(0, noise_std) | Exogenous uncertainty |

The key insight: `effective_lambda = price_impact × liquidity_factor`. As `total_liquidity → 10` (minimum floor), `liquidity_factor → 10`, and price impact is 10× the base level. This endogenous amplification is the core of the liquidity spiral.

---

## §6 Configuration Schema

Key `extras` fields:

| Field                      | Used By         | Description                                         |
|----------------------------|-----------------|-----------------------------------------------------|
| `volatility_threshold`     | MarketMaker     | Return level triggering withdrawal                  |
| `base_liquidity`           | MarketMaker     | Liquidity provided in normal conditions             |
| `withdraw_rebalance`       | MarketMaker     | Inventory reduction fraction during stress          |
| `normal_rebalance`         | MarketMaker     | Inventory rebalancing fraction in normal conditions |
| `target_volatility`        | LiquiditySeeker | σ of target order size distribution                 |
| `liquidity_base`           | LiquiditySeeker | Normalisation for liquidity scaling                 |
| `liquidity_threshold`      | ValueTrader     | Deviation threshold for liquidity provision         |
| `trade_threshold`          | ValueTrader     | Deviation threshold for value trading               |
| `base_liquidity_provision` | ValueTrader     | Liquidity units provided during crises              |
| `value_multiplier`         | ValueTrader     | Trade size scaling                                  |
| `momentum_threshold`       | MomentumTrader  | Minimum return to follow trend                      |
| `momentum_multiplier`      | MomentumTrader  | Trend-following intensity                           |
| `noise_volatility`         | NoiseTrader     | σ of noise order distribution                       |
| `fundamental_value`        | Market          | Fundamental anchor F                                |
| `price_impact`             | Market          | Base λ coefficient                                  |
| `mean_reversion`           | Market          | γ coefficient                                       |
| `noise_std`                | Market          | Market-level noise                                  |

---

## §7 Simulation Dynamics

### §7.1 Normal Regime
Market makers active → `total_liquidity` ≈ `base_liquidity × n_makers`. Price impact low. `ValueTrader` and noise trader provide additional order flow. Market prices close to fundamental.

### §7.2 Spiral Onset
A noise or momentum shock produces a large `|return|`. Market makers' `volatility > threshold` → withdraw. `total_liquidity` drops sharply. `liquidity_factor` rises. Next period's price impact amplified. Momentum traders sell into the drop. Value traders limited by size caps.

### §7.3 Dry-Up Regime
All market makers withdrawn. `total_liquidity = base_liquidity_value_traders_only`. `liquidity_factor ≈ 100/10 = 10`. Every unit of net demand moves price 10× the base lambda. LiquiditySeeker order sizes shrink. Only `ValueTrader` and `NoiseTrader` remain.

### §7.4 Recovery
`ValueTrader` provides corrective liquidity when `|deviation| > trade_threshold`. Large enough deviation → market makers re-enter as `|return|` normalises → liquidity returns → spiral unwinds.

---

## §8 Historical Case Studies

### Case 1 — 1987 Black Monday

**Event Profile**:

| Attribute | Value                                                               |
|-----------|---------------------------------------------------------------------|
| Event     | US stock market crash                                               |
| Date      | October 19, 1987                                                    |
| Asset     | DJIA, S&P 500                                                       |
| Decline   | –22.6% in a single session (DJIA)                                   |
| Trigger   | Portfolio insurance program selling overwhelmed specialist capacity |

**Chronological Dynamics**:

| Time     | Market Condition                           | Mechanism                                          | Outcome              |
|----------|--------------------------------------------|----------------------------------------------------|----------------------|
| Opening  | Normal liquidity                           | Specialists provide bids                           | Orderly trading      |
| 10:00 AM | Portfolio insurance sell programs activate | Automated sell orders exceed specialist capacity   | Spreads widen 3×     |
| 12:00 PM | Specialists withdraw bids                  | `volatility > threshold` → market maker withdrawal | Liquidity vacuum     |
| 2:00 PM  | No market makers quoting                   | Pure momentum selling with no bid support          | DJIA –10% in 2 hours |
| 4:00 PM  | NYSE closes                                | Forced close prevents further decline              | Day ends –22.6%      |

**Agent Mappings**: `MarketMaker` models specialists who withdrew bids; `MomentumTrader` models portfolio insurance selling; `ValueTrader` models Warren Buffett / bottom-fishing buyers.

**Calibration Lessons**: Set `volatility_threshold = 0.02` (strict) for early withdrawal; `momentum_multiplier = 500` for aggressive portfolio insurance; `noise_std = 0.02` for normal; 2 MarketMakers needed for spiral to self-extinguish after ~30 rounds.

---

### Case 2 — LTCM / Russian Default 1998

**Event Profile**:

| Attribute | Value                                                 |
|-----------|-------------------------------------------------------|
| Event     | Long-Term Capital Management near-collapse            |
| Period    | August–October 1998                                   |
| Asset     | Global bond spreads, equity vol, emerging market debt |
| Trigger   | Russian sovereign default (August 17, 1998)           |
| Outcome   | Fed-orchestrated $3.6B rescue by 14 banks             |

**Chronological Dynamics**:

| Month    | Condition           | Mechanism                                      | Outcome                         |
|----------|---------------------|------------------------------------------------|---------------------------------|
| Aug 1998 | Russian default     | Forced LTCM selling across all positions       | Liquidity dry-up in EM bonds    |
| Sep 1998 | LTCM forced selling | Market makers withdraw from illiquid positions | Corporate bond spreads widen 5× |
| Sep 23   | Near-default        | All counterparties pull credit                 | Funding liquidity zero          |
| Oct 1998 | Fed intervention    | Coordinated rescue                             | Spiral arrested                 |

**Agent Mappings**: `LiquiditySeeker` models LTCM forced selling; `MarketMaker` models dealer withdrawal from corporate and EM bonds; `ValueTrader` models rescue-package buyers.

**Calibration Lessons**: `target_volatility = 15` (large LiquiditySeeker orders); `volatility_threshold = 0.015` (hair-trigger market maker withdrawal); `value_multiplier = 200` for aggressive value entry near bottom.

---

### Case 3 — Global Financial Crisis 2008

**Event Profile**:

| Attribute        | Value                                                         |
|------------------|---------------------------------------------------------------|
| Event            | Lehman Brothers bankruptcy and credit market freeze           |
| Date             | September 15, 2008 onwards                                    |
| Assets           | Interbank market, commercial paper, corporate bonds, equities |
| Peak Illiquidity | TED spread 465 bps; Libor-OIS 364 bps                         |
| Duration         | ~6 months of elevated illiquidity                             |

**Chronological Dynamics**:

| Period   | Condition                        | Mechanism                                 | Outcome                                   |
|----------|----------------------------------|-------------------------------------------|-------------------------------------------|
| Sep 15   | Lehman files Chapter 11          | Primary dealers withdraw from repo market | Overnight funding market seizes           |
| Sep 16   | Reserve Primary Fund breaks buck | Money market runs begin                   | Commercial paper market freezes           |
| Sep–Oct  | Mark-to-market losses            | Bank capital erosion → deleveraging       | Liquidity spiral across all asset classes |
| Oct 2008 | Government interventions         | TARP, Fed facilities                      | Partial liquidity restoration             |

**Agent Mappings**: `MarketMaker` models primary dealer withdrawal; `LiquiditySeeker` models fund redemptions and margin calls; `MomentumTrader` models CDS spread wideners; `ValueTrader` models Warren Buffett investments.

**Calibration Lessons**: Multiple simultaneous MarketMaker withdrawals required (`n_market_makers ≥ 3`); `momentum_threshold = 0.01` for aggressive cascade; `fundamental_value` should slowly decline to model solvency concerns alongside liquidity concerns.

---

## §9 Variant Comparison

| Dimension               | Rule                             | LLM                                          | RuleLLM                                        | Rag                                              |
|-------------------------|----------------------------------|----------------------------------------------|------------------------------------------------|--------------------------------------------------|
| Market maker withdrawal | Volatility threshold formula     | LLM perceives stress and decides to withdraw | Rule triggers; LLM determines withdrawal speed | Rule triggers; KB confirms crisis precedent      |
| Liquidity spiral        | Automatic via `liquidity_factor` | Emergent from LLM coordination               | Rule-anchored spiral + LLM modulation          | RAG may moderate spiral via historical precedent |
| Cascade trigger         | Deterministic `                  | return                                       | > threshold`                                   | LLM observes others withdrawing                  |
| Value trader entry      | Fixed deviation formula          | LLM judges "crisis opportunity"              | Rule threshold + LLM confirmation              | KB retrieves post-crisis recovery data           |
| Key diagnostic          | LRI, MWF                         | LRI, LPI                                     | LRI, MWF                                       | NCE, LRI                                         |
