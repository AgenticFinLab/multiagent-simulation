# Momentum Follower

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Trend-following agent that buys recent winners and sells recent losers |
| Theory Family         | Momentum / Behavioral Underreaction |
| Behavioral Tendency   | **Amplifying** - reinforces existing price trends by buying into rallies and selling into declines |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a systematic trend follower (CTA, managed futures fund, or momentum strategy) that buys assets with positive recent returns and sells assets with negative recent returns. The real-world counterpart is documented by Jegadeesh and Titman (1993): stocks that have performed well over 3-12 months continue to outperform, and stocks that have performed poorly continue to underperform, due to gradual diffusion of information and behavioral underreaction.

The decision goal is to profit from the continuation of price trends by taking positions in the direction of recent momentum. Non-goals: the agent does not evaluate fundamental value, does not contrarian-trade, and does not provide liquidity.

## Theoretical Foundation

**Cross-sectional momentum and underreaction**:
- Theory / Study: Returns to buying winners and selling losers.
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks with high past returns (3-12 months) earn abnormally high subsequent returns for 3-12 months, attributable to behavioral underreaction to information and gradual price adjustment.
- Mathematical Formulation: `momentum_signal = (price - price_lookback) / price_lookback`. Buy when `momentum_signal > buy_threshold`; sell when `momentum_signal < sell_threshold`.
- Empirical Evidence: Jegadeesh & Titman document 12% annualized excess returns for winner-minus-loser portfolios over 1965-1989. Confirmed in international markets (Rouwenhorst 1998).
- Relevance to This Agent: The agent directly implements the momentum trading rule that generates trend amplification.
- Calibration Source: `lookback_period` 10-60 ticks, `buy_threshold` 0.02-0.10, `sell_threshold` -0.10 to -0.02.
- Falsification Conditions: If the agent buys losers or sells winners, the design is falsified.
- Alternative Theories: Time-series momentum (Moskowitz et al. 2012); rational Bayesian updating without persistence.

**Behavioral underreaction mechanism**:
- Citation: Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143-2184. https://doi.org/10.1111/0022-1082.00184
- Core Insight: Information diffuses gradually among "newswatchers," creating initial underreaction. Momentum traders exploit this but can push prices past fundamentals, creating eventual overreaction.

## Design Purpose and Activation Triggers

Purpose: Amplify price trends by systematically buying winners and selling losers, demonstrating how momentum trading creates positive feedback and potential overshooting.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `price_lookback` available (price N ticks ago)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `momentum_signal > buy_threshold`: buy (trend is up, ride it).
- `momentum_signal < sell_threshold`: sell (trend is down, ride it).
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted for buy signals.
- position exhausted for sell signals.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Strong positive momentum | buys aggressively | trend-following amplifies rally |
| Strong negative momentum | sells aggressively | trend-following amplifies decline |
| Weak/no momentum | holds | below thresholds, no action |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current price |
| `price_lookback` | environment | float | yes | price N periods ago |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is proportional to momentum strength, capped by resources.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current valuation and execution |
| `price_lookback` | Continuous | lookback_period ticks | momentum computation |
| `cash` | State | persistent | buy constraint |
| `position` | State | persistent | sell constraint |

Does NOT use: fundamental value, earnings, macroeconomic indicators, peer signals.

#### Core Behavioral Mechanism

1. Compute `momentum_signal = (price - price_lookback) / price_lookback`.
2. If `momentum_signal > buy_threshold`: compute `q_buy = min(cash / price, base_size * (momentum_signal / buy_threshold))`.
3. If `momentum_signal < sell_threshold`: compute `q_sell = min(position, base_size * abs(momentum_signal / sell_threshold))`.
4. If neither threshold crossed: hold.
5. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * (signal_strength / threshold)`, capped by constraints |
| Action lifetime | one decision call |
| Revision policy | recompute each tick based on latest momentum |
| State constraint | position >= 0, cash >= 0 |
| Resource cap | buy limited by cash/price, sell limited by position |
| Exit rule | sell when momentum reverses below sell_threshold |

#### Mathematical Model

`m = (price - price_lookback) / price_lookback`

`q_buy = min(cash / price, base_size * m / buy_threshold)` if `m > buy_threshold`

`q_sell = min(position, base_size * |m| / |sell_threshold|)` if `m < sell_threshold`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `lookback_period` | ticks for momentum calculation | 20 | Jegadeesh & Titman (1993) |
| `buy_threshold` | minimum positive momentum to buy | 0.05 | calibration |
| `sell_threshold` | minimum negative momentum to sell | -0.05 | calibration |
| `base_size` | base order size at threshold | 500.0 | scenario normalization |
| `momentum_scale` | signal-to-size multiplier | 1.0 | calibration |

#### Behavioral Properties

- Time horizon: medium, because momentum persists over 3-12 months equivalent.
- Risk tolerance: medium, because sizing is proportional but not leveraged.
- Information asymmetry: none, uses only public price history.
- Psychological profile: trend-following, disciplined, reactive to price patterns.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `lookback_period` | int | 20 | [10, 60] | high | number of ticks for momentum calculation | Shorter -> faster reaction, noisier | Jegadeesh & Titman (1993) |
| `buy_threshold` | float | 0.05 | [0.02, 0.10] | medium | minimum positive momentum to trigger buy | Lower -> more frequent buying | calibration |
| `sell_threshold` | float | -0.05 | [-0.10, -0.02] | medium | minimum negative momentum to trigger sell | Higher (less neg) -> more frequent selling | calibration |
| `base_size` | float | 500.0 | [200, 1000] | medium | base order size at threshold | Higher -> larger market impact | scenario normalization |

## Worked Numerical Examples

### Case 1 - Buy (Positive Momentum)
System state: price 110, price_lookback 100, cash 100000.
Calculation: `m = (110-100)/100 = 0.10`. `m > 0.05`. `q = min(100000/110, 500 * 0.10/0.05) = min(909, 1000) = 909`.
Decision: buy 909.
State update: position increases, cash decreases.

### Case 2 - Sell (Negative Momentum)
System state: price 85, price_lookback 100, position 2000.
Calculation: `m = (85-100)/100 = -0.15`. `m < -0.05`. `q = min(2000, 500 * 0.15/0.05) = min(2000, 1500) = 1500`.
Decision: sell 1500.
State update: position decreases by 1500.

### Case 3 - Hold (Flat Market)
System state: price 101, price_lookback 100.
Calculation: `m = 0.01`. `|m| < 0.05`.
Decision: hold.
State update: unchanged.

### Edge Case - Strong Momentum But No Cash
System state: price 120, price_lookback 100, cash 500.
Calculation: `m = 0.20`. `q = min(500/120, 500 * 0.20/0.05) = min(4.17, 2000) = 4`.
Decision: buy 4 (limited by cash).
State update: small purchase.

## Behavioral Verification and Calibration

- Given momentum above buy_threshold and available cash, agent must buy.
- Given momentum below sell_threshold and available position, agent must sell.
- Given momentum between thresholds, agent must hold.
- Agent must never buy when momentum is negative or sell when momentum is positive.
- Given missing price_lookback, agent must hold.
- Order size must scale with momentum strength (not fixed).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-momentum | `buy_threshold = 999` | momentum trading amplifies trends | decrease | price autocorrelation |
| short-lookback | `lookback_period = 5` | shorter window creates more noise trading | increase | price volatility |
| large-base | `base_size = 2000` | larger orders create more price impact | increase | momentum persistence |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Core momentum anomaly |
| 2 | Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction. *Journal of Finance*, 54(6), 2143-2184. https://doi.org/10.1111/0022-1082.00184 | Behavioral mechanism for momentum |
| 3 | Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228-250. https://doi.org/10.1016/j.jfineco.2011.11.003 | Time-series momentum across asset classes |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-momentum-follower.png) |
| Status | draft |
