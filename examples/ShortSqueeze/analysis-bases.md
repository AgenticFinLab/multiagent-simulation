# ShortSqueeze Analysis Bases

## §1 Analysis Objectives

The analysis verifies forced covering, momentum/retail amplification, float
scarcity, and overvaluation reversal pressure.

## §2 Metrics

### §2.1 Squeeze Magnitude

```python
def compute_squeeze_magnitude(prices: list[float], fundamental: float) -> float
```

Measures peak price premium to fundamental.

### §2.2 Covering Volume

```python
def compute_covering_volume(orders: list[dict]) -> float
```

Measures ShortSeller buy-to-cover volume.

### §2.3 Retail Demand Share

```python
def compute_retail_demand_share(orders: list[dict]) -> float
```

Attributes buy volume to retail traders.

### §2.4 Momentum Amplification

```python
def compute_momentum_amplification(orders: list[dict], returns: list[float]) -> float
```

Links positive returns to future momentum buys.

### §2.5 Float Constraint Proxy

```python
def compute_float_constraint(institutional_holdings: list[float]) -> float
```

Measures supply withheld by institutional holders.

### §2.6 Squeeze Onset

```python
def compute_squeeze_onset(prices: list[float], threshold: float) -> int
```

Finds first round where price premium breaches threshold.

### §2.7 Value Resistance

```python
def compute_value_resistance(orders: list[dict]) -> float
```

Measures value-investor sell pressure at overvaluation.

## §3 Analysis Dimensions

Price spike, covering pressure, retail/momentum demand, float scarcity, and
value resistance.

## §4 Phase Analysis

Short buildup, initial rally, forced covering, retail/momentum amplification,
peak squeeze, and stabilization/reversal.

## §5 Cross-Variant Comparison

Rule is mechanical. LLM may produce more narrative buying or hesitation.
RuleLLM follows explicit squeeze rules. Rag may cite GameStop/VW-like context.

## §6 Expected Results

Short covering and retail/momentum demand should increase as price rises;
institutional holding should constrain supply; value resistance appears near
extreme premiums.

## §7 Visualization Plan

Plot price premium, short interest/covering volume, retail demand, institutional
float proxy, and cross-variant squeeze magnitude.
