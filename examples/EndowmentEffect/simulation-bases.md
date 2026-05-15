# EndowmentEffect — Simulation Design Basis

## §1 Phenomenon

**Endowment Effect**: Once individuals own an asset, they value it more than an identical asset they do not own. This ownership premium creates a persistent gap between willingness-to-accept (WTA) and willingness-to-pay (WTP), suppresses trading volume, and holds prices above fundamental value. First documented in controlled experiments by Kahneman, Knetsch & Thaler (1990), the endowment effect is one of the most replicated findings in behavioral economics and has significant implications for asset pricing, portfolio rebalancing, and market microstructure.

In financial markets the endowment effect manifests as excess holding of loss positions, reluctance to rebalance portfolios, abnormal volume suppression around ownership-change events, and price stickiness. It interacts with loss aversion (Kahneman & Tversky, 1979) because selling frames the transaction as losing the owned asset — a loss that looms approximately 2.25× larger than the equivalent gain from holding cash.

**Core stylized facts**:
- WTA/WTP ratios of 2:1 to 7:1 documented across multiple experimental designs (Kahneman et al., 1990; Plott & Zeiler, 2005)
- Trading volume in endowment-effect markets is 40–60% of rational benchmark volume (Plott & Zeiler, 2005)
- Endowment-effect-driven price premiums of 5–20% above fundamental value (Genesove & Mayer, 2001)
- Housing markets show loss-averse sellers demanding 25–35% higher list prices than rational valuation (Genesove & Mayer, 2001)

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

The endowment effect has its roots in the observation that standard economic theory — which assumes preferences are independent of initial allocation — systematically fails to predict observed trading behavior. Early evidence came from experimental economics: Vernon Smith's (1962) induced-value experiments showed that subjects do trade rationally when valuations are explicitly assigned, but naturally occurring preferences deviate sharply. This established the baseline against which the endowment effect would be measured.

The theoretical foundation was laid by Kahneman and Tversky's (1979) Prospect Theory, which replaced the smooth utility function of expected utility theory with a value function that is concave for gains, convex for losses, and kinked at the reference point. Losses loom approximately 2.25× larger than equivalent gains. The reference point for an owned asset is the ownership state itself — selling registers as a loss, not merely a reduction in wealth. This loss aversion coefficient directly generates the WTA > WTP gap.

Kahneman, Knetsch & Thaler (1990) translated this theoretical prediction into direct market-level evidence using Cornell University students and coffee mugs. Their experimental markets demonstrated that endowed subjects demanded a median of $7.12 to sell, while non-endowed subjects offered only $2.87 — a 2.5× gap — and that trading volume was approximately 20% of the competitive equilibrium prediction. This paper is the canonical demonstration of the endowment effect in a market setting.

Plott & Zeiler (2005) subsequently challenged the interpretation, arguing that the gap could be explained by procedural factors rather than true preferences. Their controlled replications showed that when ownership priming was eliminated, the WTA/WTP gap largely disappeared. This debate established an important design constraint for agent-based simulations: the endowment effect requires explicit ownership representation, not just wealth accounting.

The simulation design in this repository operationalizes Kahneman et al.'s (1990) model with explicit ownership attachment parameters, following the agent-based financial market framework developed by Tesfatsion & Judd (2006) and the behavioral heterogeneous-agent models of Chiarella & He (2002).

#### §1.1.2 Real-World Event Catalogue

| Event                                           | Period       | Geography | Magnitude                                                                                   | Agent Correspondence                                                  |
|-------------------------------------------------|--------------|-----------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| Cornell mug experiment                          | 1990         | USA (lab) | WTA/WTP ratio = 2.5×; volume = 20% of equilibrium                                           | EndowedHolder (high attachment), NewBuyer (no attachment)             |
| Boston housing market post-peak                 | 1989–1992    | USA       | Loss-averse sellers listed 25–35% above market; time-to-sale 3–5× longer                    | StatusQuoSeller (inertia), RationalArbitrageur (corrective)           |
| Japanese equity portfolio rebalancing 2000–2002 | 2000–2002    | Japan     | Tech-bubble losers held 18 months longer than winners by retail investors                   | EndowedHolder (loss-reluctance), NoiseTrader (random rebalancing)     |
| US mutual fund flows during COVID-19 crash      | Feb–Apr 2020 | USA       | Equity fund outflows 60% below expected given price declines                                | StatusQuoSeller (status quo bias), RationalArbitrageur (sold quickly) |
| Chinese A-share holding patterns                | 2015–2016    | China     | Retail investors held losing positions 2.3× longer than gaining positions during correction | EndowedHolder, NoiseTrader                                            |

#### §1.1.3 Book and Practitioner Literature

- Thaler, R. H. (1980). *Toward a Positive Theory of Consumer Choice*. Journal of Economic Behavior & Organization, 1(1), 39–60. Thaler's original formulation of mental accounting and the endowment effect as a cognitive phenomenon, predating and motivating the experimental demonstrations.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux. Chapter 27 ("The Endowment Effect") provides the authoritative accessible account of the phenomenon, its experimental foundation, and its implications for market design.
- Shiller, R. J. (2015). *Irrational Exuberance* (3rd ed.). Princeton University Press. Chapter 3 documents endowment-like behavior in US housing and equity markets at scale.

---

## §2 Theory

### §2.1 Endowment Effect and Loss Aversion (Kahneman, Knetsch & Thaler, 1990)

**Citation**: Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. *Journal of Political Economy*, 98(6), 1325–1348. DOI: https://doi.org/10.1086/261737

**Core Theoretical Mechanism**: Ownership of an object increases its subjective value above the market price. The seller frames a sale as losing the object; the buyer frames a purchase as gaining it. Because losses are weighted approximately 2.25× more heavily than equivalent gains in the prospect theory value function, the minimum acceptable sale price (WTA) systematically exceeds the maximum willingness to pay (WTP) for the same object. This creates a persistent bid-ask gap that cannot be closed by equilibrating trade, suppressing volume to 20–40% of the rational benchmark and holding transaction prices above fundamental value.

**Mathematical Formulation**:

Let V(x; r) = x^α if x ≥ 0 (gain from reference point r), −λ(−x)^β if x < 0 (loss from reference point r), where α, β ≈ 0.88, λ ≈ 2.25 (Tversky & Kahneman, 1992).

For an endowed owner, the reference point is "owns the asset." Selling at market price P yields perceived loss = −V(−P; own) = λ × P^β. The minimum acceptable price is WTA = P × λ^(1/α) ≈ 2.25P for linear approximation.

| Symbol  | Meaning                            |
|---------|------------------------------------|
| V(x; r) | Prospect theory value function     |
| x       | Deviation from reference point r   |
| λ       | Loss aversion coefficient (≈ 2.25) |
| α, β    | Curvature parameters (≈ 0.88)      |
| WTA     | Minimum acceptable sale price      |
| WTP     | Maximum willingness to pay         |

**Empirical Evidence**:

| Study                   | Finding                             | Quantitative Magnitude                         |
|-------------------------|-------------------------------------|------------------------------------------------|
| Kahneman et al. (1990)  | Cornell mug experiment              | WTA/WTP = 2.5×; volume = 20% of equilibrium    |
| Plott & Zeiler (2005)   | Replication with ownership controls | Gap disappears without ownership framing       |
| Genesove & Mayer (2001) | Housing market                      | 25–35% price premium for loss-averse sellers   |
| Odean (1998)            | Stock market                        | Investors hold losers 1.7× longer than winners |

**Relevance**: Directly motivates §4.1 EndowedHolder (maximum ownership attachment) and §4.2 StatusQuoSeller (inertia-based resistance). The loss aversion coefficient λ = 2.25 sets the endowment_premium parameter range.

### §2.2 Status Quo Bias (Samuelson & Zeckhauser, 1988)

**Citation**: Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7–59. DOI: https://doi.org/10.1007/BF00055564

**Core Theoretical Mechanism**: Individuals exhibit a systematic tendency to prefer the current state of affairs over alternatives, even when switching would be objectively beneficial. Status quo bias goes beyond loss aversion: it incorporates omission bias (inaction is less culpable than action), familiarity, and effort avoidance. In financial markets, status quo bias causes investors to maintain existing portfolio allocations too long, resist rebalancing even at substantial overvaluation, and anchor selling thresholds high above current prices.

**Mathematical Formulation**:

Status quo utility premium: U(SQ) = U(alternative) + δ, where δ > 0 captures the cognitive cost of switching. An agent switches from holding to selling only when expected utility from selling exceeds δ:

E[U(sell)] − δ > E[U(hold)] ⟹ sell; else hold

The threshold deviation τ_sq in the simulation implements δ: agents sell only when price deviation > τ_sq.

| Symbol | Meaning                                                        |
|--------|----------------------------------------------------------------|
| δ      | Status quo premium (cognitive switching cost)                  |
| τ_sq   | Status quo threshold (`status_quo_threshold` config parameter) |
| SQ     | Status quo (hold) alternative                                  |

**Empirical Evidence**:

| Study                         | Finding                            | Quantitative Magnitude                                      |
|-------------------------------|------------------------------------|-------------------------------------------------------------|
| Samuelson & Zeckhauser (1988) | Retirement plan allocation inertia | 60–80% maintained default allocations                       |
| Madrian & Shea (2001)         | 401(k) default participation       | Participation rate 86% vs 49% without defaults              |
| Ameriks & Zeldes (2004)       | Equity share rebalancing           | 50% of households made zero portfolio changes over 10 years |

**Relevance**: Directly motivates §4.2 StatusQuoSeller. The parameter `status_quo_threshold` is calibrated from Samuelson & Zeckhauser's experiments and Genesove & Mayer's housing market evidence.

### §2.3 Rational Expectations and Arbitrage Limits (Muth, 1961; Shleifer & Vishny, 1997)

**Citation**: Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. DOI: https://doi.org/10.2307/1905537. Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. DOI: https://doi.org/10.1111/j.1540-6261.1997.tb03807.x

**Core Theoretical Mechanism**: Under rational expectations, prices fully incorporate available information and trade at fundamental value. Rational arbitrageurs exploit endowment-effect overvaluation by selling overpriced shares. However, Shleifer & Vishny (1997) demonstrate that arbitrage is limited in practice — capital constraints, noise trader risk, and short-horizon pressures prevent full correction. In the simulation, RationalArbitrageur provides a corrective force but cannot overcome the combined resistance of EndowedHolder and StatusQuoSeller.

**Mathematical Formulation**:

Rational sell signal: sell if (P − F) / F > τ_r; buy if (P − F) / F < −τ_r; else hold.

Order size: Q = order_size × |(P − F) / F|, capped by position and cash constraints.

| Symbol | Meaning                                             |
|--------|-----------------------------------------------------|
| F      | Fundamental value                                   |
| τ_r    | Rational arbitrage threshold (`rational_threshold`) |
| Q      | Order quantity                                      |

**Empirical Evidence**:

| Study                    | Finding           | Quantitative Magnitude                                |
|--------------------------|-------------------|-------------------------------------------------------|
| Fama (1970)              | Semi-strong EMH   | Arbitrage eliminates most mispricings within days     |
| Shleifer & Vishny (1997) | Arbitrage limits  | Long-short funds underperform during liquidity stress |
| De Long et al. (1990)    | Noise trader risk | Rational arbitrageurs may be driven out by noise      |

**Relevance**: Directly motivates §4.3 RationalArbitrageur. The corrective force is intentionally incomplete to sustain the endowment-effect overvaluation.

---

## §3 Market Design

### §3.1 Price Formation Model

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

| Symbol       | Meaning                                      | Config Key          |
|--------------|----------------------------------------------|---------------------|
| P(t)         | Market price at round t                      | `initial_price`     |
| λ            | Price impact coefficient                     | `price_impact`      |
| NetDemand(t) | Sum of signed order quantities (buy+, sell−) | derived             |
| γ            | Mean-reversion rate                          | `mean_reversion`    |
| F            | Fundamental value                            | `fundamental_value` |
| ε(t)         | Gaussian noise: ε ~ N(0, σ²)                 | `noise_std`         |

### §3.2 Market Role

The `Market` class is the sole price-setter. It collects orders from all investors in `perceive()`, computes net demand, applies the price formation formula, and broadcasts `market_data` (price, fundamental, deviation, round) to all investors via `outbound_messages`. There is no explicit order book — all orders are aggregated into net demand.

### §3.3 Deviation Metric

`deviation = (price − fundamental) / fundamental`. Positive deviation indicates overvaluation; negative indicates undervaluation. All investor decision thresholds reference this metric.

---

## §4 Investor Taxonomy

### §4.1 EndowedHolder

#### 4.1.1 Summary

A heavily endowed investor who values owned shares far above market price due to maximum ownership attachment. Sells only when price exceeds a large endowment premium threshold; creates persistent upward price pressure and suppresses trading volume. Embodies the strongest form of the endowment effect.

#### 4.1.2 Theoretical and Empirical Foundation

- **Kahneman, Knetsch & Thaler (1990)**: Endowment effect; WTA/WTP ratio of 2–7 for identical objects. DOI: `10.1086/261737`. Mechanism: ownership frames selling as a loss; loss aversion coefficient λ ≈ 2.25 drives WTA > market price.
- **Shefrin & Statman (1985)**: Disposition effect; extreme reluctance to realize losses combines with endowment attachment to suppress selling. DOI: `10.1111/j.1540-6261.1985.tb05002.x`.

#### 4.1.3 Design Purpose and Activation Scenarios

- **Activates when**: Price exceeds `fundamental × (1 + endowment_premium)` → sells; price falls below `fundamental × (1 − 0.05)` → buys
- **Role in phenomenon**: Destabilizing — suppresses selling below the endowment threshold, keeping prices above fundamental
- **Interaction effects**: Resists RationalArbitrageur sell pressure; amplifies StatusQuoSeller resistance layer

#### 4.1.4 Behavioral Framework

**Information set**: current price, fundamental value, deviation, personal `endowment_premium` and `sell_reluctance` parameters

**Mechanism narrative**: EndowedHolder adds a large ownership premium to their minimum acceptable sale price. They will only sell if price exceeds `fundamental × (1 + endowment_premium)`. Below this threshold they hold regardless of market conditions, creating a persistent volume suppression. When selling, they sell only `position × sell_reluctance` shares, reflecting reluctance to liquidate fully.

**Mathematical model**:
```
threshold = fundamental × (1 + endowment_premium)
if price > threshold:
    sell_q = min(int(position × sell_reluctance), position)
    sell(sell_q)
elif deviation < −0.05:
    buy_q = min(500, int(cash / price))
    buy(buy_q)
else: hold()
```

**Behavioral properties**: Strong loss aversion (λ ≈ 2.25), high ownership attachment, low trading frequency, asymmetric buy/sell thresholds

#### 4.1.5 Decision Process Walkthrough

1. Receive market broadcast: extract price, fundamental, deviation
2. Compute endowment threshold = fundamental × (1 + endowment_premium)
3. If price > threshold → sell `position × sell_reluctance` shares (reluctant partial sell)
4. Else if deviation < −0.05 → buy up to 500 shares (buys undervalued)
5. Otherwise → hold

#### 4.1.6 Worked Numerical Example

Given: price = 112, fundamental = 100, endowment_premium = 0.15, position = 1000, sell_reluctance = 0.30

- Endowment threshold = 100 × 1.15 = 115; price (112) < 115 → do NOT sell
- deviation = (112 − 100)/100 = 0.12 > −0.05 → do NOT buy
- Decision: **hold**

Given: price = 120, fundamental = 100, endowment_premium = 0.15, position = 1000, sell_reluctance = 0.30

- Endowment threshold = 115; price (120) > 115 → sell 1000 × 0.30 = **300 shares**

#### 4.1.7 Academic References

- Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect. *Journal of Political Economy*, 98(6), 1325–1348. DOI: 10.1086/261737
- Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early. *Journal of Finance*, 40(3), 777–790. DOI: 10.1111/j.1540-6261.1985.tb05002.x

---

### §4.2 StatusQuoSeller

#### 4.2.1 Summary

A status-quo-biased seller who holds positions long due to inertia, demanding a premium significantly above fundamental before selling. Creates a secondary resistance layer below EndowedHolder, reflecting cognitive switching costs rather than pure ownership attachment.

#### 4.2.2 Theoretical and Empirical Foundation

- **Samuelson & Zeckhauser (1988)**: Status quo bias; strong preference for current state even when switching is rational. DOI: `10.1007/BF00055564`.
- **Kahneman, Knetsch & Thaler (1990)**: Endowment effect extends to the broader status quo framing — ownership makes "not selling" the default. DOI: `10.1086/261737`.

#### 4.2.3 Design Purpose and Activation Scenarios

- **Activates when**: `deviation > status_quo_threshold` → sells 400 units; `deviation < −0.08` → buys 300 units
- **Role in phenomenon**: Destabilizing — creates a second price floor; rarely sells, reinforces overvaluation
- **Interaction effects**: Complements EndowedHolder; forms a two-layer resistance structure that sustains price above fundamental

#### 4.2.4 Behavioral Framework

**Information set**: price, fundamental, deviation

**Mechanism narrative**: StatusQuoSeller holds unless deviation exceeds a large threshold (`status_quo_threshold`), reflecting inertia bias — they need a compelling reason to trade. This creates intermediate-level resistance below EndowedHolder's threshold. Buys on significant undervaluation to exploit perceived safety.

**Mathematical model**:
```
if deviation > status_quo_threshold: sell(400)
elif deviation < −0.08: buy(300)
else: hold()
```

**Behavioral properties**: High inertia (δ large), moderate loss aversion, infrequent trading, asymmetric sell threshold

#### 4.2.5 Decision Process Walkthrough

1. Receive deviation from market broadcast
2. If deviation > status_quo_threshold → sell 400 units
3. If deviation < −0.08 → buy 300 units
4. Otherwise → hold

#### 4.2.6 Worked Numerical Example

Given: deviation = 0.10, status_quo_threshold = 0.12

- 0.10 < 0.12 → do NOT sell; 0.10 > −0.08 → do NOT buy → **hold**

Given: deviation = 0.15, status_quo_threshold = 0.12

- 0.15 > 0.12 → **sell 400 units**

#### 4.2.7 Academic References

- Samuelson, W., & Zeckhauser, R. (1988). Status quo bias. *Journal of Risk and Uncertainty*, 1(1), 7–59. DOI: 10.1007/BF00055564
- Kahneman, D. et al. (1990). *Journal of Political Economy*, 98(6). DOI: 10.1086/261737

---

### §4.3 RationalArbitrageur

#### 4.3.1 Summary

A fully rational investor who trades at fundamental value with no ownership bias, providing the corrective force that drives prices back toward fair value. Embodies the rational expectations benchmark.

#### 4.3.2 Theoretical and Empirical Foundation

- **Muth (1961)**: Rational expectations — agents incorporate all available information into price. DOI: `10.2307/1905537`.
- **Fama (1970)**: Efficient market hypothesis — rational arbitrage eliminates systematic mispricings. DOI: `10.2307/2325486`.

#### 4.3.3 Design Purpose and Activation Scenarios

- **Activates when**: `|deviation| > rational_threshold`
- **Role in phenomenon**: Stabilizing — corrects overvaluation by selling overpriced assets; partially offsets endowment resistance
- **Interaction effects**: Provides downward pressure against EndowedHolder and StatusQuoSeller; insufficient alone to fully correct due to numerical resistance

#### 4.3.4 Behavioral Framework

**Information set**: price, fundamental, deviation

**Mechanism narrative**: RationalArbitrageur computes the pure deviation from fundamental and acts proportionally. No ownership premium — applies symmetric buy/sell logic.

**Mathematical model**:
```
deviation = (price − fundamental) / fundamental
if deviation > rational_threshold:
    sell(min(order_size × deviation, position))
elif deviation < −rational_threshold:
    buy(min(order_size × |deviation|, affordable))
else: hold()
```

**Behavioral properties**: Fully rational, no cognitive bias, symmetric response, proportional order sizing

#### 4.3.5 Decision Process Walkthrough

1. Compute deviation from fundamental
2. Compare magnitude to rational_threshold
3. Submit proportional sell or buy order

#### 4.3.6 Worked Numerical Example

Given: price = 105, fundamental = 100, rational_threshold = 0.02, order_size = 1000

- deviation = 0.05 > 0.02 → **sell** min(1000 × 0.05, position) = 50 shares

#### 4.3.7 Academic References

- Muth, J. F. (1961). Rational expectations. *Econometrica*, 29(3), 315–335. DOI: 10.2307/1905537
- Fama, E. F. (1970). Efficient capital markets. *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486

---

### §4.4 NewBuyer

#### 4.4.1 Summary

A new entrant who evaluates assets purely at market value with no ownership bias, representing the rational WTP side of the endowment gap. Provides corrective buying when prices are below or at fundamental.

#### 4.4.2 Theoretical and Empirical Foundation

- **Kahneman, Knetsch & Thaler (1990)**: Buyers unaffected by endowment effect — WTP equals rational valuation. DOI: `10.1086/261737`.
- **Plott & Zeiler (2005)**: Without ownership priming, subjects exhibit no WTA/WTP gap. DOI: `10.1257/aer.95.3.530`.

#### 4.4.3 Design Purpose and Activation Scenarios

- **Activates when**: `deviation < buy_threshold` (buys at or below fundamental); `deviation > 0.10` (sells overvalued)
- **Role in phenomenon**: Stabilizing — buys when EndowedHolder refuses to sell; partially fills volume gap
- **Interaction effects**: Provides demand-side correction; acts as the rational WTP counterpart to EndowedHolder's inflated WTA

#### 4.4.4 Behavioral Framework

**Information set**: price, fundamental, deviation

**Mechanism narrative**: NewBuyer has no ownership attachment and applies pure value-investing logic. Buys at or below fundamental; sells above 10% premium.

**Mathematical model**:
```
if deviation < buy_threshold:
    buy(min(500, int(cash / price)))
elif deviation > 0.10:
    sell(min(400, position))
else: hold()
```

**Behavioral properties**: Rational WTP, unbiased, contrarian relative to endowed sellers

#### 4.4.5 Decision Process Walkthrough

1. Observe deviation from market broadcast
2. If deviation < buy_threshold → buy up to 500 shares
3. If deviation > 0.10 → sell up to 400 shares
4. Otherwise → hold

#### 4.4.6 Worked Numerical Example

Given: deviation = −0.03, buy_threshold = 0.0

- −0.03 < 0.0 → **buy** min(500, int(cash / price)) shares

#### 4.4.7 Academic References

- Kahneman, D. et al. (1990). *Journal of Political Economy*, 98(6). DOI: 10.1086/261737
- Plott, C. R., & Zeiler, K. (2005). *American Economic Review*, 95(3). DOI: 10.1257/aer.95.3.530

---

### §4.5 NoiseTrader

#### 4.5.1 Summary

An uninformed random trader who provides background volume and prevents the market from being trivially predictable. Embodies noise trading theory.

#### 4.5.2 Theoretical and Empirical Foundation

- **Black (1986)**: Noise trading; uninformed traders are essential for liquid markets. DOI: `10.1111/j.1540-6261.1986.tb04513.x`.
- **De Long, Shleifer, Summers & Waldmann (1990)**: Noise trader risk — noise traders can move prices systematically and earn returns that persist. DOI: `10.1086/261703`.

#### 4.5.3 Design Purpose and Activation Scenarios

- **Activates when**: `random() < trade_probability` each round
- **Role in phenomenon**: Neutral — provides background volume, prevents degenerate equilibria
- **Interaction effects**: Dilutes clean endowment signals; occasional spurious buys can temporarily amplify overvaluation

#### 4.5.4 Behavioral Framework

**Information set**: none (random)

**Mechanism narrative**: Trades with fixed probability each round; direction and size randomly determined from a uniform distribution.

**Mathematical model**:
```
if random() < trade_probability:
    direction = buy if random() > 0.5 else sell
    quantity = uniform(min_order, max_order)
    submit(direction, quantity)
else: hold()
```

**Behavioral properties**: Uninformed, random, bounded position

#### 4.5.5 Decision Process Walkthrough

1. Random draw vs. trade_probability
2. If trading: random direction (buy/sell) and size (uniform)
3. Submit order or hold

#### 4.5.6 Worked Numerical Example

Given: trade_probability = 0.30, random draw = 0.22 < 0.30 → trades; direction = buy; size = 10 → **buy 10 shares**

#### 4.5.7 Academic References

- Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528–543. DOI: 10.1111/j.1540-6261.1986.tb04513.x
- De Long, J. B. et al. (1990). Noise trader risk. *Journal of Political Economy*, 98(4), 703–738. DOI: 10.1086/261703

---

## §5 Agent Diversity

The five-agent mix produces the endowment effect phenomenon through three interacting forces:

1. **Resistance layer** (EndowedHolder + StatusQuoSeller): Suppress selling by demanding supra-fundamental prices. EndowedHolder requires price > fundamental × 1.15; StatusQuoSeller requires deviation > 0.12. Both agents hold unless their respective threshold is exceeded, creating a powerful ownership-premium floor that sustains price above fundamental.

2. **Correction layer** (RationalArbitrageur + NewBuyer): RationalArbitrageur sells overvalued shares proportionally to deviation; NewBuyer buys at-or-below fundamental. Together they provide the restoring force, but are numerically outweighed by the resistance layer.

3. **Background noise** (NoiseTrader): Provides random volume and prevents trivial equilibria.

The key emergent property is **persistent overvaluation** — prices held 5–20% above fundamental for extended periods — and **suppressed trading volume** — because the resistance layer rarely trades.

---

## §6 Parameter Table

| Parameter              | Default Value | Source                        | Justification                                              |
|------------------------|---------------|-------------------------------|------------------------------------------------------------|
| `initial_price`        | 105.0         | Kahneman et al. (1990)        | 5% above fundamental; typical initial endowment premium    |
| `fundamental_value`    | 100.0         | Muth (1961)                   | Normalized fundamental for ratio interpretability          |
| `price_impact`         | 0.001         | Calibration                   | Standard market-impact coefficient for mid-cap stock       |
| `mean_reversion`       | 0.01          | Calibration                   | Slow reversion consistent with persistent endowment effect |
| `noise_std`            | 0.5           | Calibration                   | Realistic price noise standard deviation                   |
| `endowment_premium`    | 0.15          | Kahneman et al. (1990)        | WTA/WTP gap; median 15% above market from experiments      |
| `sell_reluctance`      | 0.30          | Shefrin & Statman (1985)      | Partial sell only; disposition effect reluctance           |
| `status_quo_threshold` | 0.12          | Samuelson & Zeckhauser (1988) | Threshold for status quo bias to be overcome               |
| `rational_threshold`   | 0.02          | Muth (1961)                   | 2% minimum deviation for profitable arbitrage              |
| `trade_probability`    | 0.30          | Black (1986)                  | 30% per-round trade probability for noise traders          |
| `buy_threshold`        | 0.0           | Kahneman et al. (1990)        | NewBuyer buys at or below fundamental (WTP = fair value)   |

---

## §7 Round Structure

Each simulation round executes in this order:

1. **Market.perceive()**: Collect investor orders from `observation.inbounds`; store in `custom_state["orders"]`
2. **Market.decide()**: Apply price formation formula; compute new price; return `market_data` with `outbound_messages`
3. **Investor.perceive()**: Receive `market_data` from `observation.inbounds`; update `custom_state["market_data"]`
4. **Investor.decide()**: Evaluate thresholds; submit order or hold
5. **Investor.act()**: Package decision as `Action`

**Initialization** (first perceive): Each investor's `if "cash" not in` guard sets cash, position from `config.extras`. Market sets price from `extras["initial_price"]`.

---

## §8 Historical Cases

### §8.1 Case 1: Cornell Mug Experiment (Kahneman, Knetsch & Thaler, 1990)

#### Event Profile

| Field      | Detail                                      |
|------------|---------------------------------------------|
| Event Name | Endowment Effect Experimental Market        |
| Period     | 1984–1990 (multiple replications)           |
| Geography  | Cornell University, USA                     |
| Asset Type | Coffee mugs, chocolate bars                 |
| Resolution | Persistent WTA/WTP gap; sub-optimal volume  |
| Sources    | Kahneman et al. (1990), DOI: 10.1086/261737 |

#### Chronological Dynamics

| Phase                   | Description                                         | Quantitative Measure                          |
|-------------------------|-----------------------------------------------------|-----------------------------------------------|
| Baseline (no ownership) | Random assignment of ownership; trading begins      | WTA/WTP ratio = 2.5×; 20% of predicted volume |
| Ownership established   | Endowed subjects hold; non-endowed reluctant to pay | Median WTA = $7.12; Median WTP = $2.87        |
| Arbitrage attempt       | Rational subjects try to close gap                  | Gap partially closed but persistent           |

#### Quantitative Evidence

1. WTA/WTP ratio = 2.5× across multiple replications (Kahneman et al., 1990)
2. Trading volume = 20% of competitive equilibrium prediction (Kahneman et al., 1990)
3. Endowment premium ≈ 150% of WTP (i.e., WTA = 2.5 × WTP)
4. Replicated in 15+ studies across cultures (Horowitz & McConnell, 2002, Meta-Analysis, DOI: 10.1016/S0095-0696(02)00030-X)

#### Agent Mappings

| Case Agent                            | Simulation Equivalent | §4.N |
|---------------------------------------|-----------------------|------|
| Endowed subject (mug holder)          | EndowedHolder         | §4.1 |
| Non-endowed subject (potential buyer) | NewBuyer              | §4.4 |
| Rational subject (no gap)             | RationalArbitrageur   | §4.3 |
| Non-participating subject             | NoiseTrader           | §4.5 |

#### Calibration Lessons

| Historical Value                         | Simulation Parameter                      | §6 Key |
|------------------------------------------|-------------------------------------------|--------|
| WTA = 2.5 × WTP → 150% endowment premium | `endowment_premium` = 0.15–0.25           | §6     |
| Volume = 20% of equilibrium              | Low `trade_probability` for EndowedHolder | §6     |

---

### §8.2 Case 2: Boston Housing Market (Genesove & Mayer, 2001)

#### Event Profile

| Field      | Detail                                                   |
|------------|----------------------------------------------------------|
| Event Name | Boston Condo Market Post-Peak Adjustment                 |
| Period     | 1989–1992                                                |
| Geography  | Boston, USA                                              |
| Asset Type | Condominiums                                             |
| Resolution | Loss-averse sellers held longer; market illiquid         |
| Sources    | Genesove & Mayer (2001), DOI: 10.1162/003355301753265561 |

#### Chronological Dynamics

| Phase            | Description                           | Quantitative Measure                         |
|------------------|---------------------------------------|----------------------------------------------|
| Boom (1986–1989) | Rapid price appreciation; high volume | Prices +60% from 1986 to 1989                |
| Peak (1989)      | Prices stall; rational sellers exit   | Volume drops 45%                             |
| Bust (1990–1992) | Endowed sellers refuse to accept loss | Prices decline slowly; volume suppressed 60% |

#### Quantitative Evidence

1. Loss-averse sellers listed 25–35% above market-clearing price (Genesove & Mayer, 2001)
2. Time-on-market for loss-averse sellers 3–5× longer than rational sellers
3. Sale probability per month 20% lower for loss-averse sellers
4. Net sale price 3–18% higher for loss-averse sellers who waited — partial compensation for holding costs

#### Agent Mappings

| Case Agent                           | Simulation Equivalent           | §4.N       |
|--------------------------------------|---------------------------------|------------|
| Loss-averse seller (bought at peak)  | EndowedHolder + StatusQuoSeller | §4.1, §4.2 |
| Rational seller (bought before boom) | RationalArbitrageur             | §4.3       |
| Opportunistic buyer                  | NewBuyer                        | §4.4       |
| Uninformed buyer                     | NoiseTrader                     | §4.5       |

#### Calibration Lessons

| Historical Value      | Simulation Parameter                                      | §6 Key |
|-----------------------|-----------------------------------------------------------|--------|
| 25–35% price premium  | `endowment_premium` = 0.25, `status_quo_threshold` = 0.12 | §6     |
| Volume suppressed 60% | Low `sell_reluctance` = 0.30 (only 30% of position sold)  | §6     |

---

### §8.3 Case 3: Japanese Retail Investor Equity Holding (2000–2002)

#### Event Profile

| Field      | Detail                                                            |
|------------|-------------------------------------------------------------------|
| Event Name | Post-bubble equity holding by Japanese retail investors           |
| Period     | 2000–2002                                                         |
| Geography  | Japan (Tokyo Stock Exchange)                                      |
| Asset Type | Technology equities                                               |
| Resolution | Retail investors held loss positions 2× longer than institutional |
| Sources    | Grinblatt & Keloharju (2001), DOI: 10.1111/0022-1082.00353        |

#### Chronological Dynamics

| Phase              | Description                      | Quantitative Measure                                |
|--------------------|----------------------------------|-----------------------------------------------------|
| Bubble (1999–2000) | Rapid run-up; retail buy heavily | Nikkei Technology Index +150%                       |
| Peak (Feb 2000)    | Prices peak; early sellers exit  | Volume drops                                        |
| Bust (2001–2002)   | Retail holds; institutions sell  | Nikkei −65%; retail holding period 2× institutional |

#### Quantitative Evidence

1. Retail investors held losing positions 18 months longer than winners on average
2. Disposition effect ratio (P_gain_sold / P_loss_sold) = 1.7 for retail vs. 1.1 for institutions
3. 68% of retail investors in loss positions held through full drawdown
4. Institutions exited within 3 months of 10% drawdown threshold (Grinblatt & Keloharju, 2001)

#### Agent Mappings

| Case Agent                                 | Simulation Equivalent | §4.N       |
|--------------------------------------------|-----------------------|------------|
| Retail investor (bought at peak, holds)    | EndowedHolder         | §4.1       |
| Institutional investor (exits quickly)     | RationalArbitrageur   | §4.3       |
| Late retail buyer (uninformed)             | NewBuyer, NoiseTrader | §4.4, §4.5 |
| Status-quo retail (neither buys nor sells) | StatusQuoSeller       | §4.2       |

#### Calibration Lessons

| Historical Value                | Simulation Parameter                              | §6 Key |
|---------------------------------|---------------------------------------------------|--------|
| Holding period 2× institutional | `endowment_premium` = 0.15 (sells only at +15%)   | §6     |
| Disposition ratio 1.7           | `sell_reluctance` = 0.30 (reluctant partial sell) | §6     |

---

## §9 Variant Comparison

| Aspect             | Rule                                            | LLM                                              | RuleLLM                                     | Rag                                              |
|--------------------|-------------------------------------------------|--------------------------------------------------|---------------------------------------------|--------------------------------------------------|
| Decision Mechanism | Threshold formulas from §4                      | LLM persona reasoning about ownership attachment | LLM prompted with embedded threshold rules  | Rules + RAG retrieval from endowment literature  |
| Endowment Premium  | Fixed `endowment_premium` parameter             | LLM interprets ownership attachment narratively  | LLM applies threshold from system prompt    | RAG retrieves WTA/WTP research to calibrate      |
| Status Quo Bias    | `status_quo_threshold` numeric comparison       | LLM models inertia via persona description       | Threshold embedded in RuleLLM system prompt | RAG provides Samuelson & Zeckhauser evidence     |
| Determinism        | Fully deterministic given inputs                | Stochastic (LLM temperature)                     | Semi-deterministic (rule anchors LLM)       | Semi-deterministic                               |
| Theory Grounding   | Exact formula from §4                           | Narrative approximation                          | Formula in prompt guides LLM                | Formula + retrieved evidence                     |
| Expected Volume    | Lowest (mechanical thresholds suppress trading) | Moderate (LLM variability in holding decisions)  | Similar to Rule with LLM noise              | Potentially better calibrated to historical data |
