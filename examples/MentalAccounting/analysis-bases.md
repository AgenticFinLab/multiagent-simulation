# MentalAccounting Analysis Bases

## §1 Analysis Objectives

The analysis measures whether segregated mental accounts produce decisions that
deviate from rational portfolio optimization.

## §2 Metrics

### §2.1 Account-Level Turnover

```python
def compute_account_turnover(orders: list[dict]) -> float
```

Measures trading caused by account-local evaluation.

### §2.2 House-Money Risk Shift

```python
def compute_house_money_shift(agent_states: list[dict]) -> float
```

Compares risk taking after gains versus after losses.

### §2.3 Sunk-Cost Holding Rate

```python
def compute_sunk_cost_holding_rate(positions: list[dict]) -> float
```

Measures losing positions held despite negative expected return.

### §2.4 Rational Benchmark Deviation

```python
def compute_rational_deviation(biased_orders: list[dict], rational_orders: list[dict]) -> float
```

Compares biased agents to RationalPortfolioManager behavior.

### §2.5 Price Impact Of Bias

```python
def compute_bias_price_impact(prices: list[float], benchmark_prices: list[float]) -> float
```

Estimates how much biased order flow moves price away from benchmark.

### §2.6 Trading Concentration

```python
def compute_trading_concentration(orders: list[dict]) -> dict[str, float]
```

Attributes volume by agent type.

### §2.7 Volatility

```python
def compute_return_volatility(prices: list[float]) -> float
```

Measures whether biased turnover increases price volatility.

## §3 Analysis Dimensions

Account segregation, house-money risk, sunk-cost inertia, rational benchmark
gap, and market-level price effects.

## §4 Phase Analysis

Early rounds establish account gains/losses. Middle rounds reveal divergent
account-level decisions. Later rounds show whether bias-driven turnover persists
or mean-reverts.

## §5 Cross-Variant Comparison

Rule is deterministic. LLM may narrate richer account framing. RuleLLM should
preserve explicit behavioral rules. Rag may strengthen behavioral-finance
interpretation if retrieved context is relevant.

## §6 Expected Results

Biased agents should trade differently from RationalPortfolioManager; house
money traders should increase risk after gains; SunkCostHolder should exhibit
sticky losing positions.

## §7 Visualization Plan

Plot price, agent-type volume, risk exposure after gains/losses, losing-position
holding rate, and cross-variant benchmark deviation.
