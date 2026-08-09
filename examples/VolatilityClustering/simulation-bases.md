# VolatilityClustering Simulation Bases

## §1 Phenomenon Definition

VolatilityClustering models the empirical regularity that large asset-price
changes tend to be followed by large changes, and quiet periods tend to be
followed by quiet periods. The simulation combines GARCH-style volatility
persistence with heterogeneous investors whose orders amplify, dampen, or delay
return shocks.

This is a trading-schema scenario. Rule and LLM variants use a GARCH market with
signed orders. RuleLLM and Rag use a liquidity-aware extension that consumes
`provides_liquidity` and changes price impact through effective depth.

## §2 Theoretical Foundation

### §2.1 Conditional Heteroskedasticity

ARCH and GARCH models represent volatility persistence by making current
variance depend on prior squared returns and prior variance. The market
coordinator implements this mechanism directly through a bounded GARCH(1,1)
update, following ARCH evidence (DOI: 10.2307/1912773) and GARCH modeling
(DOI: 10.1016/0304-4076(86)90063-1).

### §2.2 Heterogeneous Agent Feedback

Heterogeneous agent models show how fundamentalists, trend followers, and noise
traders can produce persistent nonlinear market dynamics. Trend following and
noise shocks help create clustered high-volatility periods; fundamentalists and
slow adapters provide stabilizing pressure (DOI:
10.1016/S0165-1889(98)00011-6).

### §2.3 Trend Following Under Volatility

Trend followers often size positions by market state. In this scenario,
volatility-sensitive trend demand can amplify price moves during turbulent
periods, consistent with time-series momentum evidence (DOI:
10.1016/j.jfineco.2011.11.003).

### §2.4 Slow Adaptation

Slow information processing spreads reactions across multiple rounds, making
the effect of a shock persist after the initial return, following adaptive
expectations and bounded-rationality market models.

### §2.5 Volatility Timing

Volatility traders react to high- and low-volatility regimes rather than price
direction alone, creating direct order-flow feedback from the volatility state.

## §3 Market Mechanism

The Rule and LLM market broadcasts price, previous price, return, volatility,
previous volatility, volume, net demand, and fundamental value. It aggregates
signed quantities and updates price using net-demand impact, mean reversion, and
GARCH-scaled noise:

`P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + sigma(t) * epsilon`

`sigma(t)^2 = omega + alpha * r(t-1)^2 + beta * sigma(t-1)^2`

RuleLLM and Rag retain the same volatility phenomenon but use a
liquidity-sensitive market. Orders marked with `provides_liquidity=true` add to
effective depth; low depth increases price impact. Missing Rag liquidity flags
default to `false`, which is conservative because it cannot inflate market
liquidity.

## §4 Investor Archetypes

### §4.1 Fundamentalist

#### 4.1.1 Summary

| Field              | Content                                                    |
|--------------------|------------------------------------------------------------|
| agent_type         | fundamentalist                                             |
| Class name         | Fundamentalist                                             |
| Domain role        | Stabilising                                                |
| Theory family      | Heterogeneous Agent Feedback (§4.3 of target)              |
| Primary signals    | price, fundamental                                         |
| Population default | 2 instances                                                |
| Variant coverage   | Rule, LLM, RuleLLM, Rag                                   |

#### 4.1.2 Definition and Goals

The fundamentalist trades toward fundamental value at a low frequency, providing a stabilising anchor that damps excessive price deviation and prevents unbounded drift. It represents value/contrarian institutional investors who re-enter markets after dislocations.

#### 4.1.3 Theoretical Foundation

Brock and Hommes (1998, DOI: 10.1016/S0165-1889(98)00011-6) show that fundamentalists create mean-reverting pressure against chartist-driven price excursions. In their heterogeneous beliefs model, the fundamentalist fraction prevents explosive dynamics by pulling prices back toward the rational-expectations equilibrium.

#### 4.1.4 Design Purpose and Activation Triggers

Activation condition: trades only on rounds divisible by `trade_frequency` (default 3). When active, computes a noisy estimate of fundamental value and generates a buy (sell) order proportional to the estimated undervaluation (overvaluation). This infrequent but stabilising flow prevents the trend follower from creating unbounded momentum.

#### 4.1.5 Behavioral Framework

**State Variables**: `cash`, `position`, `price_history`, `volatility_history`.

**Trigger Function**: `round_num % trade_frequency == 0`.

**Sizing Function**: `quantity = value_sensitivity * deviation * base_position_size`, where `deviation = (estimated_value - price) / price` and `estimated_value = fundamental + N(0, value_noise_std)`.

**Constraint**: `quantity` clamped to `[-20, +20]`; cash constraint `quantity ≤ cash / bid_price` for buys; position constraint `|sell| ≤ position` for sells.

**Output format**: `<decision>{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": str}</decision>`

#### 4.1.6 Parameters

| Parameter          | Symbol    | Default | Source                                                    |
|--------------------|-----------|---------|-----------------------------------------------------------|
| initial_cash       | C0        | 10000.0 | Normalization (scenario default)                          |
| initial_position   | X0        | 0.0     | Normalization (scenario default)                          |
| trade_frequency    | f_trade   | 3       | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6   |
| value_sensitivity  | s_val     | 0.5     | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6   |
| base_position_size | Q_base    | 20.0    | Calibrated for meaningful net demand                      |
| value_noise_std    | sigma_val | 2.0     | Estimation noise                                          |

#### 4.1.7 Population and Heterogeneity

Two instances with identical parameters. Heterogeneity arises from the stochastic value noise (`value_noise_std`), which causes each instance to compute slightly different estimated values each active round.

#### 4.1.8 Worked Numerical Examples

### Case 1 — Buy on undervaluation

Price = 95.0, fundamental = 100.0, noise draw = +1.5 → estimated_value = 101.5. Deviation = (101.5 − 95.0) / 95.0 = 0.0684. Quantity = 0.5 × 0.0684 × 20.0 = +0.684 → buy order of 0.68 units at bid 95.0.

### Case 2 — Sell on overvaluation

Price = 108.0, fundamental = 100.0, noise draw = −0.5 → estimated_value = 99.5. Deviation = (99.5 − 108.0) / 108.0 = −0.0787. Quantity = 0.5 × (−0.0787) × 20.0 = −0.787 → sell order of 0.79 units.

### Case 3 — Hold (non-active round)

Round = 4, trade_frequency = 3. Since 4 % 3 ≠ 0, no trade is generated. Quantity = 0.

### Edge Case — Cash constraint binds

Price = 100.0, cash = 5.0, computed quantity = +10. Max affordable = 5.0 / 100.0 = 0.05. Quantity clamped to 0.05.

#### 4.1.9 Validation and Calibration

Expected behavior: fundamentalist orders correlate negatively with price-fundamental deviation. With `value_sensitivity=0.5` and `base_position_size=20`, peak single-round demand is ~2 units (when deviation ≈ 0.20 × cap), insufficient to single-handedly reverse a trend but sufficient to slow momentum.

#### 4.1.10 Academic References

- Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274. DOI: 10.1016/S0165-1889(98)00011-6
- Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.

#### 4.1.11 Design Provenance and Versioning

Created for the VolatilityClustering scenario under `masim/skills/polish-simulation-pipeline.md`. Profile stored at `masim/agents/defines/finance/fundamentalist.md`.

---

### §4.2 TrendFollower

#### 4.2.1 Summary

| Field              | Content                                                    |
|--------------------|------------------------------------------------------------|
| agent_type         | trend-follower                                             |
| Class name         | TrendFollower                                              |
| Domain role        | Destabilising                                              |
| Theory family      | Time-Series Momentum (§4.4 of target)                      |
| Primary signals    | price, price_history, volatility                           |
| Population default | 3 instances                                                |
| Variant coverage   | Rule, LLM, RuleLLM, Rag                                   |

#### 4.2.2 Definition and Goals

The trend follower chases recent price momentum and scales position size by the ratio of current volatility to a baseline level. It amplifies shocks by trading in the direction of recent price moves with larger size during turbulent regimes, creating the endogenous feedback that extends volatility clusters.

#### 4.2.3 Theoretical Foundation

Moskowitz, Ooi, and Pedersen (2012, DOI: 10.1016/j.jfineco.2011.11.003) demonstrate time-series momentum across asset classes and show that practitioners scale positions by inverse volatility. In this scenario, the trend follower uses a direct volatility multiplier (higher volatility → larger positions) which is the destabilising feedback channel.

Jegadeesh and Titman (1993, DOI: 10.1111/j.1540-6261.1993.tb04702.x) provide the original cross-sectional momentum evidence that supports the trend-signal computation.

#### 4.2.4 Design Purpose and Activation Triggers

Activation condition: trend signal `abs((price - MA) / MA) > trend_threshold`. When active, places an order in the trend direction scaled by volatility ratio and trend strength. When the trend signal is below threshold, no order is placed. This conditional activation ensures that trend following only adds demand during moves that are already meaningful.

#### 4.2.5 Behavioral Framework

**State Variables**: `cash`, `position`, `price_history`, `volatility_history`.

**Trigger Function**: `abs(trend) > trend_threshold`, where `trend = (price - MA_lookback) / MA_lookback`.

**Sizing Function**: `quantity = direction * base_position_size * strength * vol_multiplier`, where `strength = min(|trend| / 0.05, 1.0)` and `vol_multiplier = 1.0 + volatility_sensitivity * (vol_ratio - 1.0)`, clamped to `[0.5, 2.0]`.

**Constraint**: Cash/position constraints same as base investor.

**Output format**: `<decision>{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": str}</decision>`

#### 4.2.6 Parameters

| Parameter             | Symbol      | Default | Source                                                              |
|-----------------------|-------------|---------|---------------------------------------------------------------------|
| initial_cash          | C0          | 10000.0 | Normalization                                                       |
| initial_position      | X0          | 0.0     | Normalization                                                       |
| lookback_window       | w_trend     | 3       | Moskowitz, Ooi, and Pedersen (2012), 10.1016/j.jfineco.2011.11.003 |
| trend_threshold       | theta_trend | 0.005   | Moskowitz, Ooi, and Pedersen (2012), 10.1016/j.jfineco.2011.11.003 |
| base_position_size    | Q_base      | 30.0    | Calibrated for stronger amplification vs fundamentalist             |
| volatility_sensitivity| s_vol       | 0.8     | Moskowitz, Ooi, and Pedersen (2012), 10.1016/j.jfineco.2011.11.003 |
| baseline_volatility   | sigma_base  | 1.0     | Calibration reference                                               |

#### 4.2.7 Population and Heterogeneity

Three instances with identical parameters. Population is larger than fundamentalists (3 vs 2) to ensure that trend-following demand dominates stabilising demand during high-volatility episodes, consistent with empirical observations of momentum crowding.

#### 4.2.8 Worked Numerical Examples

### Case 1 — Strong uptrend in high volatility

Price = 105, MA(3) = 100, trend = 0.05 > threshold 0.005. Volatility = 2.0, baseline = 1.0, vol_ratio = 2.0, vol_multiplier = 1.0 + 0.8 × 1.0 = 1.8. Strength = min(0.05/0.05, 1.0) = 1.0. Quantity = +1 × 30 × 1.0 × 1.8 = +54. Clamped by cash constraint.

### Case 2 — Weak trend (hold)

Price = 100.2, MA(3) = 100.0, trend = 0.002 < threshold 0.005. No order generated. Quantity = 0.

### Case 3 — Downtrend with normal volatility

Price = 96, MA(3) = 100, trend = −0.04. Volatility = 1.0, vol_ratio = 1.0, vol_multiplier = 1.0. Strength = min(0.04/0.05, 1.0) = 0.8. Quantity = −1 × 30 × 0.8 × 1.0 = −24. Sell 24 units.

### Edge Case — Vol multiplier clamp

Volatility = 5.0, baseline = 1.0, vol_ratio = 5.0, raw multiplier = 1.0 + 0.8 × 4.0 = 4.2 → clamped to 2.0 (upper bound).

#### 4.2.9 Validation and Calibration

Expected behavior: trend-follower order volume positively correlates with market volatility (stylized fact F3). With 3 instances × Q_base=30, peak single-round aggregate trend demand is ~180 units (3 × 30 × 1.0 × 2.0), which at price_impact=0.05 produces a 9-point price move — enough to trigger further GARCH updating.

#### 4.2.10 Academic References

- Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. DOI: 10.1016/j.jfineco.2011.11.003
- Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. DOI: 10.1111/j.1540-6261.1993.tb04702.x

#### 4.2.11 Design Provenance and Versioning

Created for the VolatilityClustering scenario. Profile stored at `masim/agents/defines/finance/trend-follower.md`.

---

### §4.3 NoiseTrader

#### 4.3.1 Summary

| Field              | Content                                                    |
|--------------------|------------------------------------------------------------|
| agent_type         | noise-trader                                               |
| Class name         | NoiseTrader                                                |
| Domain role        | Shock generator                                            |
| Theory family      | Noise Trader Risk (§4.5 of target)                         |
| Primary signals    | none (stochastic)                                          |
| Population default | 3 instances                                                |
| Variant coverage   | Rule, LLM, RuleLLM, Rag                                   |

#### 4.3.2 Definition and Goals

The noise trader produces stochastic order flow with position mean reversion. It injects variance into the price process independent of fundamental information, providing the exogenous innovation that feeds the GARCH squared-return term. Without noise traders, the GARCH process would lack fresh shocks and volatility would decay monotonically.

#### 4.3.3 Theoretical Foundation

De Long, Shleifer, Summers, and Waldmann (1990, DOI: 10.1086/261703) show that noise traders create unpredictable demand shocks that generate risk for arbitrageurs and prevent prices from converging to fundamentals. Black (1986, DOI: 10.1111/j.1540-6261.1986.tb04513.x) defines noise trading as the counterpart to information-motivated trading.

#### 4.3.4 Design Purpose and Activation Triggers

Always active: every round generates a stochastic order. Position mean-reversion prevents inventory divergence without eliminating shock generation. The noise trader is the only agent that generates demand independent of price signals, making it the exogenous shock source in the system.

#### 4.3.5 Behavioral Framework

**State Variables**: `cash`, `position`, `price_history`, `volatility_history`.

**Trigger Function**: Always (every round).

**Sizing Function**: `quantity = N(0, position_volatility) + mean_reversion_speed × (0 - position)`. The first term injects random demand; the second term pulls position back toward zero.

**Constraint**: Cash/position constraints same as base investor. Quantity clamped to `[-30, +30]`.

**Output format**: `<decision>{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": str}</decision>`

#### 4.3.6 Parameters

| Parameter           | Symbol      | Default | Source                                        |
|---------------------|-------------|---------|-----------------------------------------------|
| initial_cash        | C0          | 10000.0 | Normalization                                 |
| initial_position    | X0          | 0.0     | Normalization                                 |
| position_volatility | sigma_noise | 15.0    | De Long et al. (1990), 10.1086/261703        |
| mean_reversion_speed| rho_noise   | 0.1     | De Long et al. (1990), 10.1086/261703        |

#### 4.3.7 Population and Heterogeneity

Three instances with identical parameters. Heterogeneity arises purely from the random draw each round. The three-instance population triples the aggregate shock injection rate, ensuring the GARCH process receives sufficient innovation even in relatively calm stretches.

#### 4.3.8 Worked Numerical Examples

### Case 1 — Random buy with zero position

Position = 0, random draw = +12.5. Mean-reversion term = 0.1 × (0 − 0) = 0. Quantity = +12.5. Buy 12.5 units at market price.

### Case 2 — Random sell offset by mean reversion

Position = +40, random draw = −5.0. Mean-reversion term = 0.1 × (0 − 40) = −4.0. Quantity = −5.0 + (−4.0) = −9.0. Sell 9 units.

### Case 3 — Mean reversion dominates

Position = +80, random draw = +3.0. Mean-reversion term = 0.1 × (0 − 80) = −8.0. Quantity = +3.0 + (−8.0) = −5.0. Sell 5 units despite positive random draw.

### Edge Case — Clamp at ±50

Position = 0, random draw = +60. Quantity before clamp = +60, after clamp = +50.

#### 4.3.9 Validation and Calibration

Expected behavior: noise-trader orders are uncorrelated with price signals. Aggregate noise injection across 3 instances has standard deviation ≈ 15 × √3 ≈ 26 units per round, producing return shocks of order 0.05 × 26 / price ≈ 1.3% at mean price 100. This is sufficient to trigger GARCH updating but not so large as to overwhelm the system.

#### 4.3.10 Academic References

- De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. DOI: 10.1086/261703
- Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528–543. DOI: 10.1111/j.1540-6261.1986.tb04513.x

#### 4.3.11 Design Provenance and Versioning

Existing profile at `masim/agents/defines/finance/noise-trader.md`. Reused without modification for this scenario.

---

### §4.4 SlowAdapter

#### 4.4.1 Summary

| Field              | Content                                                    |
|--------------------|------------------------------------------------------------|
| agent_type         | slow-adapter                                               |
| Class name         | SlowAdapter                                                |
| Domain role        | Persistence                                                |
| Theory family      | Heterogeneous Agent Feedback (§4.3 of target)              |
| Primary signals    | price, fundamental, moving_average                         |
| Population default | 1 instance                                                 |
| Variant coverage   | Rule, LLM, RuleLLM, Rag                                   |

#### 4.4.2 Definition and Goals

The slow adapter updates its perceived value gradually after market moves, spreading the effect of each shock across multiple rounds. It represents pension funds and insurance mandates with quarterly rebalancing cycles whose delayed response extends volatility clusters beyond what the GARCH mechanism alone produces.

#### 4.4.3 Theoretical Foundation

Brock and Hommes (1998, DOI: 10.1016/S0165-1889(98)00011-6) model adaptive belief formation where agents update expectations slowly. Hommes (2006) extends this to show that heterogeneous updating speeds create persistent price deviations and endogenous volatility fluctuations.

#### 4.4.4 Design Purpose and Activation Triggers

Always active but with delayed effect: updates a moving average of price each round, then trades only when the deviation between its blended perceived value and the current price is material. The slow moving-average update ensures that the agent's demand persists for many rounds after a single shock.

#### 4.4.5 Behavioral Framework

**State Variables**: `cash`, `position`, `price_history`, `volatility_history`, internal `moving_average` (computed from `price_history`).

**Trigger Function**: `abs(perceived_value - price) / price > material_threshold` (implicit in sizing — zero quantity when deviation is near zero).

**Sizing Function**: `perceived_value = update_weight * fundamental + (1 - update_weight) * MA_lookback`. Quantity = `base_position_size * (perceived_value - price) / price`, clamped to `[-10, +10]`.

**Constraint**: Cash/position constraints same as base investor.

**Output format**: `<decision>{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": str}</decision>`

#### 4.4.6 Parameters

| Parameter        | Symbol     | Default | Source                                                    |
|------------------|------------|---------|-----------------------------------------------------------|
| initial_cash     | C0         | 10000.0 | Normalization                                             |
| initial_position | X0         | 0.0     | Normalization                                             |
| lookback_window  | w_slow     | 10      | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6   |
| update_weight    | alpha_slow | 0.1     | Adaptive expectations literature                          |
| base_position_size| Q_base    | 10.0    | Calibrated for weak stabilisation                         |

#### 4.4.7 Population and Heterogeneity

Single instance. The slow adapter's contribution is persistent but small in magnitude per round. One instance is sufficient to extend clustering duration without dominating the system.

#### 4.4.8 Worked Numerical Examples

### Case 1 — Post-shock buying (price below MA)

Price = 92, fundamental = 100, MA(10) = 98. Perceived value = 0.1 × 100 + 0.9 × 98 = 98.2. Deviation = (98.2 − 92) / 92 = 0.067. Quantity = 10 × 0.067 = +0.67. Small buy order.

### Case 2 — Equilibrium (no meaningful trade)

Price = 100, fundamental = 100, MA(10) = 100.2. Perceived value = 0.1 × 100 + 0.9 × 100.2 = 100.18. Deviation = (100.18 − 100) / 100 = 0.0018. Quantity = 10 × 0.0018 = 0.018 ≈ 0.

### Case 3 — Delayed sell after positive shock

Price jumped from 100 to 110 three rounds ago. MA(10) is still catching up at 104. Perceived value = 0.1 × 100 + 0.9 × 104 = 103.6. Deviation = (103.6 − 110) / 110 = −0.058. Quantity = 10 × (−0.058) = −0.58. Small sell order, persisting for many rounds until MA catches up.

### Edge Case — Clamp at ±10

Large deviation creates quantity = +15 → clamped to +10.

#### 4.4.9 Validation and Calibration

Expected behavior: slow-adapter orders lag price shocks by several rounds and persist in the same direction until the moving average converges. This persistence extends clustering duration (stylized fact F2) beyond what the GARCH mechanism alone produces (research goal 5).

#### 4.4.10 Academic References

- Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274. DOI: 10.1016/S0165-1889(98)00011-6
- Hommes, C. H. (2006). Heterogeneous agent models in economics and finance. In L. Tesfatsion & K. L. Judd (Eds.), *Handbook of Computational Economics*, Vol. 2, pp. 1109–1186.

#### 4.4.11 Design Provenance and Versioning

Created for the VolatilityClustering scenario. Profile stored at `masim/agents/defines/finance/slow-adapter.md`.

---

### §4.5 VolatilityTrader

#### 4.5.1 Summary

| Field              | Content                                                    |
|--------------------|------------------------------------------------------------|
| agent_type         | volatility-trader                                          |
| Class name         | VolatilityTrader                                           |
| Domain role        | Stabilising                                                |
| Theory family      | Conditional Heteroskedasticity (§4.1, §4.2 of target)      |
| Primary signals    | volatility, vol_moving_average                             |
| Population default | 1 instance                                                 |
| Variant coverage   | Rule, LLM, RuleLLM, Rag                                   |

#### 4.5.2 Definition and Goals

The volatility trader changes exposure based on the volatility regime relative to its own moving average. It sells in high-volatility states and buys in low-volatility states, providing direct feedback from the volatility state to order flow. This represents volatility-targeting mandates and risk-parity strategies that mechanically de-risk when volatility rises.

#### 4.5.3 Theoretical Foundation

Engle (1982, DOI: 10.2307/1912773) and Bollerslev (1986, DOI: 10.1016/0304-4076(86)90063-1) provide the conditional heteroskedasticity framework. Moreira and Muir (2017, DOI: 10.1111/jofi.12575) show that volatility-managed portfolios scale risky exposure inversely to recent volatility — the volatility trader implements this mechanism directly.

#### 4.5.4 Design Purpose and Activation Triggers

Activation condition: `vol_ratio = current_vol / MA_vol(vol_lookback)`. Triggers when `vol_ratio > high_vol_threshold` (sell) or `vol_ratio < low_vol_threshold` (buy). Otherwise holds. This regime-switching behavior provides partial dampening of volatility spikes and re-entry during calm periods.

#### 4.5.5 Behavioral Framework

**State Variables**: `cash`, `position`, `price_history`, `volatility_history`.

**Trigger Function**: `vol_ratio > high_vol_threshold OR vol_ratio < low_vol_threshold`.

**Sizing Function**: When high-vol: `quantity = -base_position_size * (vol_ratio - 1.0)`. When low-vol: `quantity = +base_position_size * (1.0 - vol_ratio)`. Clamped to `[-20, +20]`.

**Constraint**: Cash/position constraints same as base investor.

**Output format**: `<decision>{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": str}</decision>`

#### 4.5.6 Parameters

| Parameter         | Symbol      | Default | Source                                                           |
|-------------------|-------------|---------|------------------------------------------------------------------|
| initial_cash      | C0          | 10000.0 | Normalization                                                    |
| initial_position  | X0          | 0.0     | Normalization                                                    |
| vol_lookback      | w_vol       | 5       | Engle (1982), 10.2307/1912773                                    |
| high_vol_threshold| theta_high  | 1.5     | Moreira and Muir (2017), 10.1111/jofi.12575                     |
| low_vol_threshold | theta_low   | 0.7     | Moreira and Muir (2017), 10.1111/jofi.12575                     |
| base_position_size| Q_base      | 15.0    | Calibrated for partial dampening                                 |

#### 4.5.7 Population and Heterogeneity

Single instance. One volatility trader is sufficient to demonstrate measurable stabilisation pressure during high-vol episodes (stylized fact F5) without fully offsetting the trend-follower amplification.

#### 4.5.8 Worked Numerical Examples

### Case 1 — Sell in high-vol regime

Current volatility = 3.0, MA_vol(5) = 1.8, vol_ratio = 3.0/1.8 = 1.67 > threshold 1.5. Quantity = −15 × (1.67 − 1.5) = −15 × 0.17 = −2.5. Sell 2.5 units.

### Case 2 — Buy in low-vol regime

Current volatility = 0.6, MA_vol(5) = 1.2, vol_ratio = 0.6/1.2 = 0.5 < threshold 0.7. Quantity = +15 × (0.7 − 0.5) = +15 × 0.2 = +3.0. Buy 3 units.

### Case 3 — Hold in normal regime

Current volatility = 1.5, MA_vol(5) = 1.3, vol_ratio = 1.15. Since 0.7 < 1.15 < 1.5, no trigger. Quantity = 0.

### Edge Case — Extreme vol ratio

Vol_ratio = 3.0 > threshold 1.5. Raw quantity = −15 × (3.0 − 1.5) = −22.5 → clamped to −15.

#### 4.5.9 Validation and Calibration

Expected behavior: volatility-trader sell volume is positive during at least 30% of high-volatility rounds (stylized fact F5). With peak sell of 15 units, the maximum price impact is 0.05 × 15 = 0.75 points — meaningful but not dominant relative to trend-follower aggregate demand.

#### 4.5.10 Academic References

- Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. DOI: 10.2307/1912773
- Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. DOI: 10.1016/0304-4076(86)90063-1
- Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. DOI: 10.1111/jofi.12575

#### 4.5.11 Design Provenance and Versioning

Created for the VolatilityClustering scenario. Profile stored at `masim/agents/defines/finance/volatility-trader.md`.

## §5 Agent Diversity Verification

The population contains one stabilizing value anchor, one trend amplifier, one
stochastic shock source, one delayed-response investor, and one volatility-regime
trader. This role mix is sufficient to produce clustered volatility through
both exogenous shocks and endogenous order-flow feedback.

All four variants preserve the same five archetypes. RuleLLM and Rag add the
liquidity flag required by their liquidity-aware market. Rag additionally
records retrieved context for post-run audit.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity | Source / Rationale |
|---|---|---|---|---|
| `initial_price` | Starting price | Market | Medium | Normalized starting point for volatility paths |
| `fundamental_value` | Value anchor | Market, Fundamentalist | High | Stabilizing reference value |
| `price_impact` / `base_price_impact` | Net-demand price impact | Market | High | Converts order-flow shocks into returns |
| `mean_reversion` | Pull toward fundamental | Market | Medium | Prevents unbounded drift |
| `garch_omega` | Long-run variance component | Market | High | GARCH baseline variance |
| `garch_alpha` | Return-shock variance loading | Market | High | ARCH shock response |
| `garch_beta` | Volatility persistence | Market | High | GARCH persistence channel |
| `min_volatility` / `max_volatility` | Volatility bounds | Market | Medium | Numerical stability and scenario observability |
| `trend_threshold` | Trend activation | TrendFollower | High | Activates continuation trades only on meaningful trends |
| `volatility_sensitivity` | Volatility-scaled trend size | TrendFollower | High | Links turbulence to order size |
| `position_volatility` | Noise-trader shock size | NoiseTrader | Medium | Generates shocks that feed volatility updates |
| `update_weight` | Slow-adapter fundamental weight | SlowAdapter | High | Controls delayed information processing |
| `high_vol_threshold` / `low_vol_threshold` | Volatility-regime triggers | VolatilityTrader | High | Implements volatility timing behavior |

## §7 Communication And Round Structure

Each round follows market broadcast, investor decision, order aggregation, and
market update. Investors record portfolio state and submit one order. The market
records price, volatility, and volume histories. API variants parse `<analysis>`
and `<decision>` sections; deterministic schema/config errors fail fast, while
explicit stochastic API fallback is allowed only when conservative and
quality-audited.

## §8 Historical Case Studies

### §8.1 Equity Index Stress Periods

Equity markets often show persistent high absolute returns after news shocks,
earnings uncertainty, or macro stress.

### §8.2 Calm-to-Stress Transitions

Markets can remain quiet for extended periods and then move into clustered
stress when trend followers, volatility traders, and noise shocks interact.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Volatility-Clustering Behavior |
|---|---|---|
| Rule | Deterministic GARCH market and formulaic investors | Clean baseline with explicit volatility persistence. |
| LLM | Persona prompts and structured orders | Same volatility state with more variable role interpretation. |
| RuleLLM | Persona plus explicit rules under liquidity-aware pricing | Rule-constrained API orders and liquidity-depth effects. |
| Rag | RuleLLM plus retrieved volatility context | Same market contract plus auditable retrieval context. |
