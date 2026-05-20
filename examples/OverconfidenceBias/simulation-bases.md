# OverconfidenceBias Simulation Bases

## §1 Phenomenon Definition

OverconfidenceBias models traders who overestimate signal precision, attribute
success to skill, trade too frequently, and generate excess volume relative to a
calibrated benchmark.

## §2 Theoretical Foundation

### §2.1 Overprecision

Investors may believe their private signals are more accurate than they are,
creating excessive confidence in forecasts.

### §2.2 Self-Attribution

Success increases perceived skill more than failure reduces it, producing
confidence drift after lucky gains.

### §2.3 Excess Trading

Behavioral finance evidence links overconfidence to excessive trading volume
and lower realized performance.

## §3 Market Mechanism

The market converts net demand into price changes with mean reversion and noise.
Overconfident traders affect price through excessive and directional order flow.

## §4 Investor Archetypes

### §4.1 OverconfidentTrader

**Summary**: Overestimates signal precision and trades too aggressively.
**Theoretical and Empirical Basis**: Overprecision models.
**Design Purpose**: Generate excess trading from inflated confidence.
**Behavioral Framework**: Uses `precision_overestimate`.
**Decision Process**: Converts perceived signal strength into larger orders.
**Worked Numerical Example**: A weak signal becomes tradable when multiplied by
overestimated precision.
**Academic References**: Odean (1998); Barber and Odean (2001).

### §4.2 SelfAttributor

**Summary**: Raises confidence after success and discounts failure.
**Theoretical and Empirical Basis**: Self-attribution bias.
**Design Purpose**: Create path-dependent confidence.
**Behavioral Framework**: Uses `confidence_boost`.
**Decision Process**: After profitable trades, increases future aggressiveness.
**Worked Numerical Example**: A gain raises confidence, increasing next-round
quantity.
**Academic References**: Daniel, Hirshleifer, and Subrahmanyam (1998).

### §4.3 CalibratedTrader

**Summary**: Trades only when signal quality justifies it.
**Theoretical and Empirical Basis**: Bayesian/calibrated decision making.
**Design Purpose**: Provide rational benchmark.
**Behavioral Framework**: Uses `signal_precision` and `trade_threshold`.
**Decision Process**: Trades only when expected signal value exceeds threshold.
**Worked Numerical Example**: A signal below threshold results in hold.
**Academic References**: Standard rational expectations benchmark.

### §4.4 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader literature.
**Design Purpose**: Add background liquidity.
**Behavioral Framework**: Uses `trade_probability`.
**Decision Process**: Random buy/sell/hold independent of signal.
**Worked Numerical Example**: A random draw below probability triggers a small
order.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population contrasts overconfident traders, path-dependent self-attributors,
calibrated rational traders, and random noise traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `precision_overestimate` | Inflation of perceived signal quality | OverconfidentTrader | High |
| `confidence_boost` | Confidence increase after success | SelfAttributor | High |
| `signal_precision` | True signal reliability | CalibratedTrader | Medium |
| `trade_threshold` | Rational trading threshold | CalibratedTrader | Medium |
| `trade_probability` | Random trading frequency | NoiseTrader | Low |

## §7 Communication And Round Structure

Market broadcasts state; agents update confidence or signal interpretation;
orders are aggregated; price updates from net demand.

## §8 Historical Case Studies

### §8.1 Retail Day Trading

Empirical studies show frequent retail traders often underperform, consistent
with overconfidence and excessive trading.

### §8.2 Post-Success Risk Escalation

Traders frequently increase risk after lucky gains, mapping to the
SelfAttributor archetype.

## §9 Variant Comparison Preview

Rule fixes confidence formulas. LLM may vary confidence expression. RuleLLM
anchors persona decisions to explicit rules. Rag may cite behavioral finance
evidence and alter reasoning strength.
