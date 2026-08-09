# Sentiment trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Noise trader driven by sentiment indicators |
| Theory Family         | Behavioral Finance / Noise Trader Theory |
| Behavioral Tendency   | **Diverging** - amplifies sentiment swings by buying on optimism and selling on pessimism, destabilising fundamental prices |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | none (uses public sentiment) |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail or institutional trader who bases buy/sell decisions on aggregate sentiment indicators rather than fundamental analysis. The real-world counterpart is the noise trader described by De Long, Shleifer, Summers, and Waldmann (1990) and the sentiment-responsive investor documented in Baker and Wurgler (2006). The agent buys when sentiment is bullish, sells when sentiment is bearish, and sizes positions proportionally to sentiment extremity.

The decision goal is to ride sentiment waves for short-term profit by buying into optimism and selling into pessimism. It is not a fundamental analyst and does not compute intrinsic value. Non-goals: it must not trade based on fundamental valuation signals, and it must not hold positions through sentiment reversals.

## Theoretical Foundation

**Noise trader risk (DSSW model)**:
- Theory / Study: Noise trader risk in financial markets.
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703
- Core Insight: Noise traders whose sentiment fluctuates unpredictably create systematic risk that limits arbitrage and allows prices to deviate from fundamentals. Their collective optimism/pessimism moves prices and can persist because rational arbitrageurs face finite horizons.
- Mathematical Formulation: `p_t = f_t + (rho_t / (1 + r))` where `rho_t` is aggregate noise trader misperception (sentiment).
- Empirical Evidence: DSSW show noise traders can earn higher expected returns than rational traders by bearing more risk, and their presence explains excess volatility.
- Relevance to This Agent: The agent operationalises the DSSW noise trader by trading proportionally to a sentiment index.
- Calibration Source: `sentiment_sensitivity` 1.0-3.0, `base_size` 100-500.
- Falsification Conditions: If the agent trades based on fundamental valuation rather than sentiment, the design is falsified.
- Alternative Theories: Rational expectations (no noise); information-based trading (Kyle 1985).

**Investor sentiment and cross-section of stock returns**:
- Theory / Study: Investor sentiment and the cross-section of stock returns.
- Citation: Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645-1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x
- Core Insight: A composite sentiment index predicts cross-sectional stock returns: when sentiment is high, subsequent returns are low (especially for speculative stocks), and vice versa. Sentiment is a systematic pricing factor.
- Mathematical Formulation: `sentiment_index = composite(IPO volume, first-day returns, closed-end fund discount, equity share, dividend premium, turnover)`. Agent trades when `|sentiment_index| > neutral_band`.
- Empirical Evidence: Baker & Wurgler construct a six-component sentiment index that predicts returns out of sample across decades of US data.
- Relevance to This Agent: The agent uses a sentiment index as its sole trading signal.
- Calibration Source: `neutral_band` 0.1-0.3 (no-trade zone around neutral sentiment).
- Falsification Conditions: If the agent ignores sentiment and trades on price/book or earnings, the design is falsified.
- Alternative Theories: Fama-French factor model; rational learning models.

## Design Purpose and Activation Triggers

Purpose: Trade directionally based on aggregate sentiment indicators, amplifying sentiment-driven price movements.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `sentiment` available (normalised sentiment index, -1 to +1)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `sentiment > neutral_band`: buy, sized by `sentiment_sensitivity * base_size * sentiment`.
- `sentiment < -neutral_band`: sell, sized by `sentiment_sensitivity * base_size * |sentiment|`.
- `|sentiment| <= neutral_band`: hold (neutral zone).
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted during bullish sentiment.
- position exhausted during bearish sentiment.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| high sentiment | buys proportionally to sentiment strength | noise trader optimism |
| low sentiment | sells proportionally to sentiment strength | noise trader pessimism |
| neutral sentiment | holds | no directional signal |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `sentiment` | environment | float | yes | normalised sentiment index (-1 to +1) |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `sentiment` | Continuous | 1 tick | sole trading signal |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |

Does NOT use: fundamental valuation, earnings data, balance sheets, peer actions.

#### Core Behavioral Mechanism

1. Read `price`, `sentiment`, `cash`, and `position`.
2. If `sentiment > neutral_band`:
   - Compute `q = sentiment_sensitivity * base_size * sentiment`.
   - Buy `min(q, cash / price)`.
3. If `sentiment < -neutral_band`:
   - Compute `q = sentiment_sensitivity * base_size * |sentiment|`.
   - Sell `min(q, position)`.
4. Otherwise hold.
5. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `sentiment_sensitivity * base_size * |sentiment|`, capped by resources |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | sell when sentiment turns negative beyond neutral band |

#### Mathematical Model

`q_buy = min(cash / price, sentiment_sensitivity * base_size * sentiment)` if `sentiment > neutral_band`; `q_sell = min(position, sentiment_sensitivity * base_size * |sentiment|)` if `sentiment < -neutral_band`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `sentiment_sensitivity` | responsiveness to sentiment magnitude | 2.0 | De Long et al. (1990) |
| `base_size` | base order size | 300.0 | scenario calibration |
| `neutral_band` | no-trade zone around zero sentiment | 0.20 | Baker & Wurgler (2006) |

#### Behavioral Properties

- Time horizon: short, because sentiment is transient and mean-reverting.
- Risk tolerance: medium, because the agent trades actively but proportionally.
- Information asymmetry: none (uses publicly available sentiment).
- Psychological profile: reactive noise trader who follows crowd sentiment without fundamental analysis.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `sentiment_sensitivity` | float | 2.0 | [1.0, 3.0] | high | multiplier converting sentiment to order size | Higher -> larger sentiment-driven trades | De Long et al. (1990) |
| `base_size` | float | 300.0 | [100, 500] | medium | base order quantity | Higher -> larger absolute trades | scenario calibration |
| `neutral_band` | float | 0.20 | [0.10, 0.30] | medium | sentiment range below which no trade occurs | Wider -> fewer trades, more filtering | Baker & Wurgler (2006) |

## Worked Numerical Examples

### Case 1 - Bullish Sentiment Buy

System state: price 100.0, sentiment +0.70, cash 80000, position 200.
Calculation: `sentiment (0.70) > neutral_band (0.20)` -> buy.
`q = 2.0 * 300 * 0.70 = 420`. `min(420, 80000/100) = 420`.
Decision: buy 420.
State update: position increases to 620; cash decreases by 42000.

### Case 2 - Bearish Sentiment Sell

System state: price 95.0, sentiment -0.60, cash 50000, position 500.
Calculation: `sentiment (-0.60) < -neutral_band (-0.20)` -> sell.
`q = 2.0 * 300 * 0.60 = 360`. `min(360, 500) = 360`.
Decision: sell 360.
State update: position decreases to 140; cash increases.

### Case 3 - Neutral Sentiment Hold

System state: price 100.0, sentiment +0.15, cash 80000, position 300.
Calculation: `|sentiment| = 0.15 < neutral_band (0.20)` -> neutral zone.
Decision: hold.
State update: unchanged.

### Edge Case - Extreme Sentiment but No Cash

System state: price 100.0, sentiment +0.95, cash 0, position 400.
Calculation: `sentiment > neutral_band` but `cash = 0`. `q = min(0, 570) = 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given sentiment above neutral band with cash available, agent must buy.
- Given sentiment below negative neutral band with position available, agent must sell.
- Given sentiment within neutral band, agent must hold.
- Agent must never use fundamental valuation data to override sentiment signal.
- Order size must scale proportionally with sentiment magnitude.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| low-sensitivity | `sentiment_sensitivity = 0.5` | reduced sensitivity dampens sentiment amplification | decrease | excess volatility |
| no-neutral-band | `neutral_band = 0.0` | neutral band prevents noise trading in calm markets | increase | trade frequency |
| contrarian-flip | reverse sentiment sign | contrarian trading stabilises prices | decrease | price deviation from fundamental |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703 | DSSW noise trader model |
| 2 | Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645-1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x | Composite sentiment index |
| 3 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Why arbitrage fails to correct noise traders |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-sentiment-trader.png) |
| Status | draft |
