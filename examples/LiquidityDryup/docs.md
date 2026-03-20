# LiquidityDryup Simulation - Market Maker Inventory Model

## What is This?

| Item               | Description                                                                |
|--------------------|----------------------------------------------------------------------------|
| **Phenomenon**     | **Liquidity Dry-up** - Market makers withdraw, creating illiquidity spiral |
| **Model**          | Inventory-based market making with stress-induced withdrawal               |
| **Key Feature**    | Liquidity begets liquidity; illiquidity begets illiquidity                 |
| **Academic Value** | Tests Grossman-Miller (1988) market maker inventory model                  |

## Financial Background

| Theory                 | Application                                   | Reference                                      |
|------------------------|-----------------------------------------------|------------------------------------------------|
| **Market Maker Model** | Inventory risk drives bid-ask spread          | Grossman & Miller (1988). *Journal of Finance* |
| **Liquidity Premium**  | Illiquid assets require higher returns        | Amihud & Mendelson (1986). *JFE*               |
| **Illiquidity Spiral** | Selling → lower liquidity → more price impact | Brunnermeier & Pedersen (2009). *RFS*          |
| **Flight to Quality**  | Stress → investors flee to liquid assets      | Beber, Brandt & Kavajecz (2009). *RFS*         |

## Liquidity Dry-up Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │     Liquidity Dry-up Mechanism           │
                    │     (Inventory Risk + Withdrawal)        │
                    └──────────────────────────────────────────┘

  Normal State: ABUNDANT LIQUIDITY
  ─────────────────────────────────────
  MarketMakers actively quote bid/ask
  Tight spreads, low price impact
                 │
                 ▼
  Phase 1: STRESS EVENT
  ─────────────────────────
  Volatility spike or large sell order
  MarketMaker inventory becomes imbalanced
                 │
                 ▼
  Phase 2: INVENTORY PRESSURE
  ─────────────────────────────
  MM holds unwanted inventory → risk
  Cost of holding = Inventory × Volatility
                 │
                 ▼
  Phase 3: SPREAD WIDENING
  ───────────────────────────
  MM widens bid-ask to compensate for risk
  Or REDUCES quote size
                 │
                 ▼
  Phase 4: LIQUIDITY WITHDRAWAL
  ─────────────────────────────────
  If volatility too high → MM withdraws entirely
  "Not worth the risk"
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   ILLIQUIDITY SPIRAL            │
         │   Less liquidity → More impact  │
         │   More impact → More withdrawal │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: EXTREME PRICE IMPACT
  ─────────────────────────────────
  Small orders cause large price moves
  LiquiditySeekers suffer poor execution
```

## Why These 5 Investor Types?

### Liquidity Providers

| Investor        | Role               | Behavior                                                        |
|-----------------|--------------------|-----------------------------------------------------------------|
| **MarketMaker** | ⭐ Liquidity Source | Provides bid/ask quotes. WITHDRAWS when volatility > threshold. |

### Liquidity Demanders

| Investor            | Role                 | Behavior                                            |
|---------------------|----------------------|-----------------------------------------------------|
| **LiquiditySeeker** | ⭐ Liquidity Consumer | Needs to trade, pays the spread. Suffers in dry-up. |
| **MomentumTrader**  | Trend Follower       | Trades on price trends, can worsen dry-up.          |

### Neutral/Stabilizing

| Investor        | Role        | Behavior                                            |
|-----------------|-------------|-----------------------------------------------------|
| **ValueTrader** | Fundamental | Buys when P << F. Patient, provides some stability. |
| **NoiseTrader** | Random      | Random trades, background liquidity.                |

## Market Model

### Notations

| Symbol                   | Meaning                                                                  |
|--------------------------|--------------------------------------------------------------------------|
| $P(t)$                   | Market price at round $t$                                                |
| $D(t)$                   | Net aggregate demand                                                     |
| $\lambda$                | Base price-impact coefficient (0.08)                                     |
| $L(t)$                   | Total available liquidity: $L_{\text{base}}+L_{\text{MM}}(t)$            |
| $L_{\text{base}}$        | Minimum market liquidity (base_liquidity config)                         |
| $L_{\text{MM}}(t)$       | Market-maker–provided liquidity                                          |
| $\gamma$                 | Mean-reversion speed (0.015)                                             |
| $F$                      | Fundamental value                                                        |
| $\varepsilon(t)$         | Microstructure noise                                                     |
| $\sigma(t)$              | Rolling return volatility $=                                             |
| $\sigma_{\text{thresh}}$ | MM withdrawal threshold (`volatility_threshold` config)                  |
| $d(t)$                   | Fundamental deviation $(F-P)/F$ for ValueTrader                          |
| $v_{\text{mult}}$        | ValueTrader size multiplier (`value_multiplier` config)                  |
| $\theta_v$               | ValueTrader trade threshold (`trade_threshold` config)                   |
| $\theta_L$               | ValueTrader liquidity provision threshold (`liquidity_threshold` config) |
| $\sigma_{\text{tgt}}$    | LiquiditySeeker target volatility (`target_volatility` config)           |
| $m_{\text{mult}}$        | MomentumTrader size multiplier (`momentum_multiplier` config)            |
| $m_{\text{thresh}}$      | MomentumTrader return threshold (`momentum_threshold` config)            |
| $\mathrm{ILLIQ}(t)$      | Amihud illiquidity ratio: $                                              |
| $\mathrm{DDI}$           | Dry-up Duration Index: fraction of rounds with $L<0.3\,L_{\max}$         |
| $\mathrm{EC}(t)$         | Execution cost for forced trader                                         |
| $\mathrm{Spread}^*(t)$   | Optimal MM bid-ask spread                                                |

Liquidity-adjusted price impact (Amihud & Mendelson 1986 [2]; Amihud 2002 [5]):

$$P(t+1) = P(t) + \frac{\lambda}{L(t)/100}\cdot D(t) + \gamma\cdot[F-P(t)] + \varepsilon(t)$$

When MarketMakers withdraw, $L_{\text{MM}}\to 0$ $\Rightarrow$ $L\downarrow$ $\Rightarrow$ price impact spikes.

| Parameter      | Value | Financial Meaning                      |
|----------------|-------|----------------------------------------|
| Base Liquidity | 50    | Minimum market liquidity               |
| Price Impact   | 0.08  | Normal impact coefficient              |
| Mean Reversion | 0.015 | Speed to fundamental                   |
| MM Threshold   | 3.0   | Volatility level at which MM withdraws |

## Investor Strategy Formulas

*See implementation*: `examples/LiquidityDryup/players.py`.

| Agent           | Key parameters                                                                                                                                                      | File reference             |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| MarketMaker     | provides `base_liquidity` when $\sigma(t)<\sigma_{\text{thresh}}$; **withdraws** ($L_{\text{MM}}=0$) when $\sigma(t)\ge\sigma_{\text{thresh}}$; rebalances position | `MarketMaker.decide()`     |
| LiquiditySeeker | exogenous need $q_{\text{raw}}\sim\mathcal{N}(0,\sigma_{\text{tgt}}^2)$; actual order scaled down by liquidity: $q=q_{\text{raw}}\cdot\min(1,L/L_{\text{base}})$    | `LiquiditySeeker.decide()` |
| MomentumTrader  | $q=r(t)\cdot m_{\text{mult}}$ when $                                                                                                                                | r(t)                       |
| ValueTrader     | $q = d\cdot v_{\text{mult}}$ when $                                                                                                                                 | d                          |
| NoiseTrader     | random orders $\sim\mathcal{N}(0,\sigma_{\text{noise}}^2)$                                                                                                          | `NoiseTrader.decide()`     |

## Mathematical Foundations

### Grossman-Miller Market Maker Model

Grossman & Miller (1988) [1]: market makers provide immediacy at a cost — they are willing to take the other side of trades only if compensated for the inventory risk they bear (*Implementation*: `MarketMaker.decide()`).

MM profit/loss from providing liquidity:

> **Source**: Grossman, S.J. & Miller, M.H. (1988) [1] — *Liquidity and Market Structure*. Journal of Finance, 43(3), 617–637. The P&L decomposition into spread income minus inventory risk is the core of their immediacy model: market makers are compensated for absorbing order imbalances, but only up to the point where inventory risk becomes prohibitive. *Implementation*: `examples/LiquidityDryup/players.py`, `MarketMaker.decide()`.

$$\text{P\&L}_{\text{MM}} = \text{Spread income} - \text{Inventory risk}$$

> **What it does**: States the fundamental economic condition that determines whether a market maker remains active. Spread income is earned by quoting a bid below and ask above the mid-price — every round-trip trade earns the spread. Inventory risk is the cost of holding an imbalanced position when prices move adversely. When inventory risk grows large enough to exceed expected spread income, the market maker's rational response is to **withdraw** — triggering the liquidity dry-up. **Simulates**: the intermediary's optimization problem documented by Grossman & Miller (1988) [1]: market makers are not infinitely deep liquidity pools; they face capital constraints and risk limits.

Inventory risk cost:

> **Source**: Grossman & Miller (1988) [1] — inventory risk is proportional to position size and squared volatility (variance), a standard result from inventory-theoretic market-making models (also Ho & Stoll 1981). *Implementation*: `MarketMaker.decide()`, computed each round to determine withdrawal decision.

$$\mathrm{Cost}(t) = \gamma_{\text{MM}}\cdot|\mathrm{Inventory}(t)|\cdot\sigma(t)^2$$

> **What it does**: Quantifies exactly how much it costs the market maker to hold its current position in a volatile market. $|\mathrm{Inventory}(t)|$ is the absolute share imbalance — the more one-sided the book, the higher the directional risk. $\sigma(t)^2$ is realized variance — the more prices are moving, the more that imbalanced inventory can lose. $\gamma_{\text{MM}}$ is the risk-aversion coefficient. **Simulates**: the internal risk calculation that a real market maker (e.g., an options market maker, a HFT firm) performs on every tick to decide whether to stay in the market. **Effect**: when $\sigma(t)$ spikes (e.g., a news shock hits), Cost$(t)$ rises quadratically, potentially crossing the withdrawal threshold in a single round.

Optimal spread to break even:

> **Source**: Grossman & Miller (1988) [1] — the break-even spread condition equates spread revenue per unit volume $Q$ to inventory risk cost. *Implementation*: `MarketMaker.decide()`, diagnostic computation of effective spread.

$$\mathrm{Spread}^*(t) = \frac{2\,\gamma_{\text{MM}}\cdot|\mathrm{Inventory}(t)|\cdot\sigma(t)^2}{Q}$$

> **What it does**: Derives the minimum bid-ask spread the market maker must quote to break even on each round of liquidity provision, given the current inventory imbalance and volatility. The factor of 2 comes from the full round-trip spread (bid below mid + ask above mid). When $\sigma(t)$ is high or $|\mathrm{Inventory}(t)|$ is large, Spread$^*(t)$ becomes very wide — effectively making the market maker's quotes unattractive or infeasible. **Simulates**: how liquidity-providing costs translate directly into quoted spreads that investors pay. **Effect**: rising Spread$^*(t)$ is the precursor to withdrawal; in the simulation this manifests as the liquidity dry-up sequence.

Withdrawal condition: if $\sigma(t)\ge\sigma_{\text{thresh}}$ then $L_{\text{MM}}(t)=0$ (inventory risk exceeds maximum tolerable). In the active state, $L_{\text{MM}}=\text{base\_liquidity}$ (from config) and the MM rebalances inventory at `normal_rebalance` rate; when withdrawing it flattens inventory at `withdraw_rebalance` rate.

### Liquidity-Adjusted Price Impact

Amihud & Mendelson (1986) [2] — assets with lower liquidity trade at a discount (yield higher returns) to compensate investors for the higher trading costs; total liquidity and impact coefficient:

> **Source**: Amihud, Y. & Mendelson, H. (1986) [2] — *Asset Pricing and the Bid-Ask Spread*. Journal of Financial Economics, 17(2), 223–249. The liquidity-adjusted price impact formula directly implements their insight that effective price impact is inversely proportional to market depth/liquidity. *Implementation*: `examples/LiquidityDryup/players.py`, `Market.clear()`.

$$L(t) = L_{\text{base}} + L_{\text{MM}}(t)$$

> **What it does**: Total available liquidity $L(t)$ is the sum of the permanent market floor $L_{\text{base}}$ (e.g., noise traders, passive participants) and the endogenous market-maker contribution $L_{\text{MM}}(t)$ which can drop to zero. When the MM withdraws, $L(t)$ falls from its normal level (e.g., 150) to just $L_{\text{base}}$ (e.g., 50) — a 67% reduction in liquidity in a single round. **Simulates**: the structure of market depth as documented by Grossman & Miller (1988) [1]: the market has a stable floor of liquidity plus a volatile top layer provided by active intermediaries.

> **Source**: Kyle (1985) linear impact model; Amihud & Mendelson (1986) [2] liquidity premium framework. The $\lambda/L$ structure captures how price impact rises when liquidity falls. *Implementation*: `Market.clear()`, `price_impact` parameter.

$$\lambda(t) = \frac{\lambda_{\text{base}}\cdot 100}{L(t)}$$

> **What it does**: The effective price-impact coefficient is inversely proportional to total liquidity — this is the central mechanism of the liquidity dry-up simulation. When $L(t)=100$ (normal), $\lambda(t)=\lambda_{\text{base}}=0.08$ (mild impact). When $L(t)=20$ (crisis), $\lambda(t)=0.08\times100/20=0.40$ — five times larger. A sell order of 10 units that would move price by 0.8 in normal conditions now moves it by 4.0. **Simulates**: the empirical fact that markets become dramatically more price-sensitive during crises — documented by Amihud & Mendelson (1986) [2] and confirmed in every major liquidity crisis from 1987 to 2020. **Effect**: amplifies all price moves during dry-up, increasing volatility, triggering further MM withdrawal, and creating the feedback spiral.

Amihud (2002) [5] ILLIQ measure — the ratio of absolute return to dollar volume, capturing how much a unit of trading volume moves prices:

> **Source**: Amihud, Y. (2002) [5] — *Illiquidity and Stock Returns: Cross-Section and Time-Series Effects*. Journal of Financial Markets, 5(1), 31–56. The ILLIQ ratio is one of the most widely-used empirical liquidity measures, computed from daily return and volume data. *Implementation*: `examples/LiquidityDryup/players.py`, tracked in `Market.metrics`.

$$\mathrm{ILLIQ}(t) = \frac{|r(t)|}{\mathrm{Volume}(t)}$$

> **What it does**: Measures price impact per unit of volume — how many cents prices move per dollar traded. In normal conditions with ample liquidity, a large volume of trades produces only a small price move (low ILLIQ). During a liquidity dry-up, the same volume moves prices dramatically more (high ILLIQ). **Simulates**: the empirically measurable illiquidity that Amihud (2002) [5] documented across stocks and over time. **Effect**: expected to rise 3–10× during the dry-up phase; ILLIQ$_{\text{peak}}$/ILLIQ$_{\text{normal}}>5$ is the validation threshold for this simulation.

### LiquiditySeeker — Forced Trader

Exogenous trade need, scaled by current market liquidity (*Implementation*: `LiquiditySeeker.decide()`):

> **Source**: Grossman & Miller (1988) [1] — the concept of "impatient" or forced traders who need immediacy regardless of market conditions, and whose execution cost rises during dry-ups. *Implementation*: `examples/LiquidityDryup/players.py`, `LiquiditySeeker.decide()`.

$$q_{\text{raw}}(t) \sim \mathcal{N}(0,\,\sigma_{\text{tgt}}^2)$$

> **What it does**: Generates an exogenous, noise-driven trade need each round — the LiquiditySeeker has a genuine, non-discretionary reason to trade (e.g., portfolio rebalancing, margin call, redemption) drawn from a Gaussian with zero mean and target-volatility standard deviation. The trade is random in direction and size, independent of price signals. **Simulates**: the class of investors — pension funds, insurance companies, individuals facing margin calls — who **must** trade at any given moment regardless of market conditions, as modeled in Grossman & Miller (1988) [1].

> **Source**: Grossman & Miller (1988) [1] — the scaling of executed order size by available liquidity, capturing partial fills and slippage during dry-ups. *Implementation*: `LiquiditySeeker.decide()`.

$$q_{\text{LS}}(t) = q_{\text{raw}}(t)\cdot\min\!\left(1,\,\frac{L(t)}{L_{\text{base}}}\right)$$

> **What it does**: Scales the intended order down by the liquidity ratio. When $L(t)=L_{\text{base}}$ (normal), the ratio is 1 and the full order executes. When $L(t)<L_{\text{base}}$ (dry-up), the ratio drops below 1 and the LiquiditySeeker can only execute a fraction of its intended trade. **Simulates**: the real-world experience of being unable to find counterparties during a crisis — orders go partially or wholly unfilled, or must be broken up over many rounds at increasingly bad prices. **Effect**: forced traders suffer two compounding costs: (1) reduced execution size (they cannot complete their trade), (2) elevated price impact on the portion they do execute.

When $L$ drops, `LiquiditySeeker` cannot execute its full intended size — capturing the slippage and partial-fill costs of a dry-up. Execution cost at crisis ($L=20$):

> **Source**: Amihud & Mendelson (1986) [2] — total execution cost decomposition into spread cost and market impact cost. *Implementation*: `LiquidityDryup/analysis.py`, execution cost calculation.

$$\mathrm{EC}(t) = |q_{\text{LS}}|\cdot\left[\frac{\mathrm{Spread}(t)}{2} + \lambda(t)\cdot|q_{\text{LS}}|\right]$$

> **What it does**: The total cost of executing a trade of size $|q_{\text{LS}}|$ has two components: (1) $\mathrm{Spread}(t)/2$ per share — the half-spread paid to cross the bid-ask; this is the fixed cost of immediacy. (2) $\lambda(t)\cdot|q_{\text{LS}}|$ per share — the market impact cost, which rises linearly with order size; in a dry-up ($\lambda(t)$ large) this term dominates. At $L=20$: $\lambda=0.40$, a 50-unit intended trade is reduced and each executed unit costs $0.40\times|q_{\text{LS}}|$ in price impact — representing 4–5× normal execution costs. **Simulates**: the concrete financial damage suffered by forced traders during a liquidity crisis, consistent with the liquidity premium theory of Amihud & Mendelson (1986) [2].

### Illiquidity Spiral — Fixed-Point Analysis

Brunnermeier & Pedersen (2009) [3] feedback loop — when funding liquidity tightens, traders must liquidate positions, depressing market liquidity, which raises margins, further tightening funding (*Implementation*: `LiquidityDryup/players.py`):

> **Source**: Brunnermeier, M.K. & Pedersen, L.H. (2009) [3] — *Market Liquidity and Funding Liquidity*. Review of Financial Studies, 22(6), 2201–2238. The feedback loop equation is the verbal summary of their Proposition 3 (liquidity spiral), which shows that market liquidity and funding liquidity are mutually reinforcing in a self-fulfilling loop. *Implementation*: `LiquidityDryup/players.py`, `MarketMaker.decide()` withdrawal decision.

$$\sigma\uparrow \;\Rightarrow\; \mathrm{Cost}_{\text{MM}}\uparrow \;\Rightarrow\; L_{\text{MM}}\downarrow \;\Rightarrow\; \lambda\uparrow \;\Rightarrow\; |\Delta P|\uparrow \;\Rightarrow\; \sigma\uparrow$$

> **What it does**: Describes the complete self-reinforcing cycle — each arrow represents a causal mechanism implemented in the simulation. Step 1 ($\sigma\uparrow\Rightarrow\mathrm{Cost}_{\text{MM}}\uparrow$): higher volatility raises market-maker inventory risk (Cost formula above). Step 2 ($\mathrm{Cost}_{\text{MM}}\uparrow\Rightarrow L_{\text{MM}}\downarrow$): when the cost crosses the threshold $\sigma_{\text{thresh}}=3.0$, the MM withdraws. Step 3 ($L_{\text{MM}}\downarrow\Rightarrow\lambda\uparrow$): reduced total liquidity raises price impact ($\lambda=\lambda_{\text{base}}\times100/L$). Step 4 ($\lambda\uparrow\Rightarrow|\Delta P|\uparrow$): each trade now moves prices more. Step 5 ($|\Delta P|\uparrow\Rightarrow\sigma\uparrow$): larger price moves mean higher realized volatility, restarting the cycle. **Simulates**: the March 2020 COVID bond market crisis, the 2008 repo market freeze, and the 2010 Flash Crash — events where initial volatility spikes triggered institutional market-maker withdrawal, causing runaway price impact. **Effect**: once initiated, the spiral is self-sustaining until ValueTraders step in at extreme mispricings.

Feedback multiplier near spiral basin ($\partial f/\partial\sigma>0$):

> **Source**: Brunnermeier & Pedersen (2009) [3] — the feedback multiplier formula is the discrete-time analog of their continuous-time spiral condition (Proposition 3, equation for equilibrium multiplicity). *Implementation*: diagnostic analysis in `LiquidityDryup/analysis.py`.

$$M = \frac{1}{1 - \dfrac{\partial\lambda}{\partial L}\cdot\dfrac{\partial L}{\partial\sigma}\cdot\dfrac{\partial\sigma}{\partial\lambda}}$$

> **What it does**: The feedback multiplier $M$ quantifies how much the initial $\sigma$ shock is amplified by one trip around the spiral loop. The denominator $1-\frac{\partial\lambda}{\partial L}\cdot\frac{\partial L}{\partial\sigma}\cdot\frac{\partial\sigma}{\partial\lambda}$ is a product of three partial derivatives around the loop: (1) how sensitive price impact is to liquidity changes; (2) how sensitive MM liquidity is to volatility; (3) how sensitive volatility is to price impact. When this product approaches 1 — near the tipping point — $M\to\infty$ and the spiral is explosive. Below 1, it is self-stabilizing. **Simulates**: the critical threshold behavior of liquidity crises: small shocks before the threshold are absorbed; shocks above it amplify into full-blown crises. **Effect**: in the simulation, the threshold occurs near $\sigma\approx\sigma_{\text{thresh}}=3.0$ — the market-maker withdrawal threshold.

Stable fixed points: $(\text{low }\sigma,\,\text{high }L)$ and $(\text{very high }\sigma,\,L=L_{\min})$. Unstable transition at $\sigma\approx 2.5$ (withdrawal threshold) — once the MM withdraws, the system snaps to the high-$\sigma$ low-$L$ equilibrium.

### ValueTrader — Fundamental-Based Stabiliser

Conditional trade on fundamental deviation (*Implementation*: `ValueTrader.decide()`):

> **Source**: Grossman & Miller (1988) [1] — the role of "patient" fundamental traders who provide liquidity of last resort when prices deviate from value; Beber, Brandt & Kavajecz (2009) [4] for empirical evidence of such stabilizing behavior during stress. *Implementation*: `examples/LiquidityDryup/players.py`, `ValueTrader.decide()`.

$$d(t) = \frac{F - P(t)}{F}$$

> **What it does**: Computes the fractional deviation of the current market price from fundamental value $F$. When $d(t)>0$ (price below fundamental), the stock is undervalued — a buy signal. When $d(t)<0$ (price above fundamental), it is overvalued — a sell signal. This ratio is dimensionless and threshold-comparable regardless of the price level. **Simulates**: the value investor's first calculation — how far is price from intrinsic worth? In a liquidity crisis, prices deviate massively from fundamentals, making $|d(t)|$ large and activating the ValueTrader.

> **Source**: Grossman & Miller (1988) [1] — value investors as the "outside" liquidity providers who step in when spread widens enough; threshold $\theta_v$ represents the minimum mispricing required to attract their capital. *Implementation*: `ValueTrader.decide()`, `trade_threshold` and `value_multiplier` config parameters.

$$q_{\text{VT}}(t) = \begin{cases} d(t)\cdot v_{\text{mult}} & |d(t)| > \theta_v \\ 0 & \text{otherwise} \end{cases}$$

> **What it does**: The ValueTrader only acts when mispricing exceeds a minimum threshold $\theta_v$ — representing the minimum return premium required to justify the execution risk and spread costs of entering during a volatile, illiquid market. When they do act, position size scales linearly with deviation $d(t)$: a 10% undervaluation generates twice the order of a 5% undervaluation, creating proportional price support. **Simulates**: the empirical behavior documented by Beber, Brandt & Kavajecz (2009) [4] in Euro-area bond markets during stress — fundamental investors eventually step in, but only after mispricings become large enough. **Effect**: acts as a nonlinear stabilizer — absent during mild dry-ups, increasingly active during extreme crises, preventing $P\to 0$ and setting the floor of the liquidity spiral.

where $v_{\text{mult}}=\text{value\_multiplier}$ is a config parameter controlling position size, and $\theta_v=\text{trade\_threshold}$. ValueTrader also posts `base_liquidity_provision` units of liquidity when $|d|>\theta_L$ (`liquidity_threshold`).

Acts as liquidity of last resort: limits the spiral to finite depth (prevents $P\to 0$). Beber, Brandt & Kavajecz (2009) [4] document similar flight-to-quality behavior in sovereign bond markets during stress.

### Liquidity Metrics

Amihud ratio:

> **Source**: Amihud (2002) [5] — ILLIQ ratio, the primary empirical liquidity measure used in the simulation validation. *Implementation*: computed in `Market.metrics` each round.

$$\mathrm{ILLIQ}(t) = \frac{|r(t)|}{\mathrm{Volume}(t)}$$

> **What it does**: Same as above — price move per unit volume. Used here as the real-time monitoring metric during the simulation to detect when a dry-up is occurring and to validate its severity (ILLIQ$_{\text{peak}}$/ILLIQ$_{\text{normal}}>5$).

Liquidity ratio:

> **Source**: Defined for this simulation — normalizes total liquidity to the historical maximum to provide a [0,1] scale for the dry-up indicator. *Implementation*: `Market.metrics`, DDI computation.

$$\mathrm{LR}(t) = \frac{L(t)}{L_{\max}} \qquad (\mathrm{LR}<0.3\Rightarrow\text{ severe dry-up})$$

> **What it does**: Tracks the fraction of maximum liquidity currently available. LR $= 1.0$ is fully normal; LR $< 0.3$ means over 70% of peak liquidity has been withdrawn — the definition of a severe dry-up in this simulation. **Effect**: the threshold LR $< 0.3$ triggers the dry-up alert in the validation logic.

Dry-up Duration Index:

> **Source**: Defined for this simulation, inspired by the "fraction of days in illiquidity" metric in Amihud (2002) [5]. *Implementation*: `validate_liquidity_dryup()` in `masim/evaluation/finance/validation.py`.

$$\mathrm{DDI} = \frac{|\{t:\mathrm{LR}(t)<0.3\}|}{T} \qquad (\mathrm{DDI}>0.3\Rightarrow\text{ 30\% of simulation in dry-up})$$

> **What it does**: Measures **persistence** of the dry-up, not just its peak severity. DDI $= 0.3$ means 30% of all simulation rounds had liquidity below 30% of normal — a prolonged crisis, not a brief flash. A spike to low liquidity that immediately recovers would have DDI near 0. **Simulates**: the multi-day or multi-week nature of real liquidity crises (e.g., the 2008 credit crisis lasted months, not hours). **Effect**: DDI is a key validation criterion alongside ILLIQ ratio — the simulation must demonstrate both depth (ILLIQ spike) and duration (DDI $> 0.2$) to score as a genuine dry-up.

## Strategy Comparison

| Strategy            | Liquidity Role  | Stress Behavior         | Market Effect         |
|---------------------|-----------------|-------------------------|-----------------------|
| **MarketMaker**     | Provider        | WITHDRAWS when vol high | ⭐ Causes dry-up       |
| **LiquiditySeeker** | Consumer        | Must trade anyway       | ⭐ Suffers from dry-up |
| MomentumTrader      | Consumer        | May amplify volatility  | Worsens situation     |
| ValueTrader         | Provider (slow) | Steps in at extremes    | Stabilizes eventually |
| NoiseTrader         | Neutral         | Random                  | Background noise      |

## Liquidity Metrics

| Metric              | Formula                              | Dry-up Signal               |
|---------------------|--------------------------------------|-----------------------------|
| **Total Liquidity** | $L_{\text{base}} + L_{\text{MM}}(t)$ | $< 30$ = severe dry-up      |
| **Bid-Ask Spread**  | $P_{\text{ask}} - P_{\text{bid}}$    | $> 2\%$ = liquidity problem |
| **Price Impact**    | $\Delta P / \Delta Q$                | High = low liquidity        |
| **Volume**          | Total trading volume                 | Low = dry-up                |
| **Depth**           | Quoted size at bid/ask               | Low = dry-up                |

## Liquidity States

| State       | Liquidity | Spread   | Impact Factor | MM Behavior        |
|-------------|-----------|----------|---------------|--------------------|
| **Normal**  | > 100     | < 0.5%   | 1.0x          | Full provision     |
| **Reduced** | 50-100    | 0.5-1.5% | 1.5-2x        | Partial withdrawal |
| **Dry-up**  | < 50      | > 2%     | 3-5x          | Full withdrawal    |
| **Crisis**  | < 20      | > 5%     | 5-10x         | No quotes          |

## Topology

```
                         ┌───────────────────┐
                         │      market       │ ◄── Liquidity-adjusted pricing
                         └─────────┬─────────┘
                                   │
     ┌───────────┬─────────────────┼─────────────────┬───────────┐
     ▼           ▼                 ▼                 ▼           ▼
market_maker  liq_seeker      momentum          value        noise
(⭐ withdraw)  (⭐ suffer)     (worsen)       (stabilize)  (neutral)
```

## Files

| File                                       | Purpose                     |
|--------------------------------------------|-----------------------------|
| `examples/LiquidityDryup/players.py`       | Market + 5 investor classes |
| `examples/LiquidityDryup/run_liquidity.py` | Entry point                 |
| `configs/LiquidityDryup/simulation.yml`    | Main config                 |
| `configs/LiquidityDryup/players.yml`       | Player definitions          |
| `configs/LiquidityDryup/topology.yml`      | Star topology               |

## Running

```bash
python examples/LiquidityDryup/run_liquidity.py -c configs/LiquidityDryup/simulation.yml
```

## Expected Behavior

| Phase    | Rounds  | Liquidity | Observation               |
|----------|---------|-----------|---------------------------|
| Normal   | 1-50    | > 100     | Tight spreads, low impact |
| Stress   | 51-100  | 50-100    | MM reduces provision      |
| Dry-up   | 101-150 | < 50      | High impact, MM withdraws |
| Crisis   | 151-170 | < 20      | Extreme price moves       |
| Recovery | 171-200 | Rising    | Value traders step in     |

## Real-World Mapping

| Simulation        | Real-World Example               |
|-------------------|----------------------------------|
| MM withdrawal     | 2010 Flash Crash liquidity gap   |
| Spread widening   | 2008 Credit Crisis bond markets  |
| Liquidity spiral  | August 2015 ETF liquidity crisis |
| Flight to quality | March 2020 COVID dash for cash   |

## References

\[1\] Grossman, S.J. & Miller, M.H. (1988). *Liquidity and Market Structure*. Journal of Finance, 43(3), 617–637.

\[2\] Amihud, Y. & Mendelson, H. (1986). *Asset Pricing and the Bid-Ask Spread*. Journal of Financial Economics, 17(2), 223–249.

\[3\] Brunnermeier, M.K. & Pedersen, L.H. (2009). *Market Liquidity and Funding Liquidity*. Review of Financial Studies, 22(6), 2201–2238.

\[4\] Beber, A., Brandt, M.W. & Kavajecz, K.A. (2009). *Flight-to-Quality or Flight-to-Liquidity? Evidence from the Euro-Area Bond Market*. Review of Financial Studies, 22(3), 925–957.

\[5\] Amihud, Y. (2002). *Illiquidity and Stock Returns: Cross-Section and Time-Series Effects*. Journal of Financial Markets, 5(1), 31–56.
