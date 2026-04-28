# EndowmentEffect — Analysis Methodology Basis

## §1 Objectives

| Objective | Research Question                                                             | Metric(s)                              | Expected Finding                                            |
|-----------|-------------------------------------------------------------------------------|----------------------------------------|-------------------------------------------------------------|
| O1        | Does the endowment effect create persistent overvaluation above fundamental?  | Price Deviation (PD), MAD              | Prices remain 5–15 % above fundamental for extended periods |
| O2        | How much does ownership bias suppress trading volume vs. a rational baseline? | Volume Suppression Ratio (VSR)         | Volume 40–60 % below rational expectation                   |
| O3        | How does the endowment premium magnitude affect price correction speed?       | Deviation Persistence Half-Life (DPHL) | Larger endowment_premium → longer DPHL                      |
| O4        | Do all four variants reproduce the volume-suppression signature?              | Cross-variant VSR                      | All variants show suppression; LLM variant more variable    |
| O5        | How does agent portfolio performance differ across investor types?            | Portfolio Wealth Ratio (PWR) by agent  | RationalArbitrageur outperforms EndowedHolder long-run      |

---

## §2 Core Metrics

### §2.1 Price Deviation from Fundamental (PD)

| Field                    | Content                                                                                        |
|--------------------------|------------------------------------------------------------------------------------------------|
| **Category**             | Price                                                                                          |
| **Definition**           | Signed percentage difference between market price and fundamental value at each round          |
| **Formula**              | `PD(t) = (P(t) − F) / F` where P(t) is round-t price, F is fundamental value                   |
| **Notation**             | P(t): market price; F: fundamental (constant); t: round index                                  |
| **Python function**      | `price_deviation(price_history, fundamental) -> List[float]`                                   |
| **Academic Basis**       | Kahneman, Knetsch & Thaler (1990) `doi:10.1086/261737`; Thaler (1980) `doi:10.1007/BF00055564` |
| **Normal Range**         | PD ∈ [0.03, 0.12] in calibrated runs                                                           |
| **Red Flag Threshold**   | PD > 0.20 (endowment_premium overcalibrated) or PD < 0.01 after round 10                       |
| **Relationships**        | Increases with `endowment_premium`; inversely related to RationalArbitrageur share             |
| **Implementation Notes** | Compute per-round; store as signed fraction; aggregate into MAD separately                     |

```python
def price_deviation(price_history: list[float], fundamental: float) -> list[float]:
    """Per-round signed percentage deviation from fundamental value.

    Args:
        price_history: List of market prices over all rounds.
        fundamental: Fundamental (constant) value of the asset.
    Returns:
        List of fractions, e.g. 0.08 = 8 % above fundamental.
    """
    return [(p - fundamental) / fundamental for p in price_history]
```

**Interpretation table**:

| PD value    | Interpretation                                                 |
|-------------|----------------------------------------------------------------|
| > 0.15      | Strong endowment-driven overvaluation; check endowment_premium |
| 0.05 – 0.15 | Target calibration range; endowment effect active              |
| 0.01 – 0.05 | Mild overvaluation; near-rational pricing                      |
| < 0.01      | Correction complete or effect inactive                         |

---

### §2.2 Mean Absolute Deviation (MAD)

| Field                    | Content                                                                                              |
|--------------------------|------------------------------------------------------------------------------------------------------|
| **Category**             | Price                                                                                                |
| **Definition**           | Time-averaged magnitude of price deviation from fundamental across all rounds                        |
| **Formula**              | `MAD = (1/T) Σ_t                                                                                     |
| **Notation**             | T: total rounds                                                                                      |
| **Python function**      | `mean_absolute_deviation(price_history, fundamental) -> float`                                       |
| **Academic Basis**       | Kahneman et al. (1990) `doi:10.1086/261737`; Smith, Suchanek & Williams (1988) `doi:10.2307/1911361` |
| **Normal Range**         | MAD ∈ [0.03, 0.12]                                                                                   |
| **Red Flag Threshold**   | MAD > 0.18 (overcalibrated) or MAD < 0.01 (effect absent)                                            |
| **Relationships**        | Positively correlated with DPHL; driven by endowment_premium parameter                               |
| **Implementation Notes** | Single scalar per simulation run; primary calibration target                                         |

```python
def mean_absolute_deviation(price_history: list[float], fundamental: float) -> float:
    """Time-averaged absolute price deviation from fundamental.

    Args:
        price_history: List of prices over all rounds.
        fundamental: Fundamental value.
    Returns:
        Scalar MAD as a fraction; target range [0.03, 0.12].
    """
    return sum(abs(p - fundamental) / fundamental for p in price_history) / len(price_history)
```

**Interpretation table**:

| MAD value   | Interpretation                           |
|-------------|------------------------------------------|
| > 0.18      | Overcalibrated; reduce endowment_premium |
| 0.03 – 0.12 | Target calibration range                 |
| 0.01 – 0.03 | Weak effect                              |
| < 0.01      | Effect absent                            |

---

### §2.3 Deviation Persistence Half-Life (DPHL)

| Field                    | Content                                                                                                 |
|--------------------------|---------------------------------------------------------------------------------------------------------|
| **Category**             | Price Dynamics                                                                                          |
| **Definition**           | Number of rounds for price deviation to decay to 50 % of its initial value, fitted by exponential decay |
| **Formula**              | Fit `                                                                                                   |
| **Notation**             | λ: decay rate; DPHL in rounds                                                                           |
| **Python function**      | `deviation_half_life(price_history, fundamental) -> float`                                              |
| **Academic Basis**       | Muth (1961) `doi:10.2307/1905537`; Thaler (1980) `doi:10.1007/BF00055564`                               |
| **Normal Range**         | DPHL ∈ [15, 60] rounds                                                                                  |
| **Red Flag Threshold**   | DPHL > 90 (near-permanent overvaluation) or DPHL < 5 (arbitrage too dominant)                           |
| **Relationships**        | Increases with endowment_premium; decreases with RationalArbitrageur share                              |
| **Implementation Notes** | Use scipy.optimize.curve_fit; report fit R² alongside DPHL                                              |

```python
def deviation_half_life(price_history: list[float], fundamental: float) -> float:
    """Fit exponential decay to |deviation(t)| and return half-life in rounds.

    Args:
        price_history: List of prices.
        fundamental: Fundamental value.
    Returns:
        Half-life in rounds; target range [15, 60].
    """
```

**Interpretation table**:

| DPHL (rounds) | Interpretation                             |
|---------------|--------------------------------------------|
| > 80          | Overcalibrated; endowment_premium too high |
| 15 – 60       | Target range — persistent but correctable  |
| 5 – 15        | Endowment weak; arbitrage dominant         |
| < 5           | Effect near-absent                         |

---

### §2.4 Volume Suppression Ratio (VSR)

| Field                    | Content                                                                                       |
|--------------------------|-----------------------------------------------------------------------------------------------|
| **Category**             | Volume                                                                                        |
| **Definition**           | Ratio of actual trading volume to expected rational-market volume over the simulation         |
| **Formula**              | `VSR = Σ_t V(t) / Σ_t V_rational(t)` where V_rational estimated from NoiseTrader baseline     |
| **Notation**             | V(t): round-t total units traded; V_rational(t): estimated rational-market volume             |
| **Python function**      | `volume_suppression_ratio(actual_volume, rational_volume_estimate) -> float`                  |
| **Academic Basis**       | Plott & Zeiler (2005) `doi:10.1257/aer.95.3.530`; Kahneman et al. (1990) `doi:10.1086/261737` |
| **Normal Range**         | VSR ∈ [0.40, 0.70]                                                                            |
| **Red Flag Threshold**   | VSR > 0.90 (endowment not suppressing volume) or VSR < 0.25 (extreme illiquidity)             |
| **Relationships**        | Inversely related to endowment_premium; lower when EndowedHolder share is high                |
| **Implementation Notes** | Estimate rational baseline from NoiseTrader-only runs; report with 95 % CI                    |

```python
def volume_suppression_ratio(
    actual_volume: list[float], rational_volume_estimate: float
) -> float:
    """Ratio of actual to rational-market expected trading volume.

    Args:
        actual_volume: Per-round total trade volume.
        rational_volume_estimate: Expected volume under full rationality.
    Returns:
        Ratio; target range [0.40, 0.70].
    """
    return sum(actual_volume) / (rational_volume_estimate * len(actual_volume))
```

**Interpretation table**:

| VSR value   | Interpretation                               |
|-------------|----------------------------------------------|
| > 0.90      | Volume not suppressed; endowment effect weak |
| 0.40 – 0.70 | Target range — meaningful suppression        |
| 0.25 – 0.40 | Strong suppression                           |
| < 0.25      | Extreme illiquidity; check agent ratios      |

---

### §2.5 Endowment Premium Capture Rate (EPCR)

| Field                    | Content                                                                                                       |
|--------------------------|---------------------------------------------------------------------------------------------------------------|
| **Category**             | Agent Behavior                                                                                                |
| **Definition**           | Fraction of rounds where EndowedHolder's threshold price exceeds current market price (holder withholds sale) |
| **Formula**              | `EPCR = (1/T) Σ_t 𝟙[P(t) < F × (1 + endowment_premium)]`                                                     |
| **Notation**             | 𝟙: indicator function; endowment_premium: min required premium above F                                       |
| **Python function**      | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium) -> float`                      |
| **Academic Basis**       | Thaler (1980) `doi:10.1007/BF00055564`; Novemsky & Kahneman (2005) `doi:10.1509/jmkr.2005.42.2.119`           |
| **Normal Range**         | EPCR ∈ [0.40, 0.75]                                                                                           |
| **Red Flag Threshold**   | EPCR > 0.90 (holder never sells) or EPCR < 0.20 (endowment_premium too low)                                   |
| **Relationships**        | Increases with endowment_premium; decreases with market price trend                                           |
| **Implementation Notes** | Report separately for EndowedHolder and StatusQuoSeller                                                       |

```python
def endowment_premium_capture_rate(
    price_history: list[float],
    fundamental: float,
    endowment_premium: float,
) -> float:
    """Fraction of rounds where price is below EndowedHolder's threshold.

    Args:
        price_history: Per-round market prices.
        fundamental: Fundamental value.
        endowment_premium: Minimum premium required above fundamental to sell.
    Returns:
        Fraction ∈ [0, 1]; target range [0.40, 0.75].
    """
    threshold = fundamental * (1 + endowment_premium)
    return sum(1 for p in price_history if p < threshold) / len(price_history)
```

**Interpretation table**:

| EPCR value  | Interpretation                                                 |
|-------------|----------------------------------------------------------------|
| > 0.90      | Holder almost never sells; check endowment_premium calibration |
| 0.40 – 0.75 | Target range — strong but bounded attachment                   |
| 0.20 – 0.40 | Moderate attachment                                            |
| < 0.20      | Endowment effect weak; threshold rarely binding                |

---

### §2.6 Portfolio Wealth Ratio by Agent Type (PWR)

| Field                    | Content                                                                                                   |
|--------------------------|-----------------------------------------------------------------------------------------------------------|
| **Category**             | Agent Performance                                                                                         |
| **Definition**           | End-of-simulation portfolio value normalized to initial wealth, computed per agent type                   |
| **Formula**              | `PWR = (cash_final + position_final × P_final) / wealth_initial`                                          |
| **Notation**             | wealth_initial = cash_0 + pos_0 × P_0                                                                     |
| **Python function**      | `portfolio_wealth_ratio(cash_history, position_history, final_price, initial_wealth) -> float`            |
| **Academic Basis**       | Thaler (1980) `doi:10.1007/BF00055564`; Shefrin & Statman (1985) `doi:10.1111/j.1540-6261.1985.tb05002.x` |
| **Normal Range**         | RationalArbitrageur PWR ∈ [1.05, 1.20]; EndowedHolder PWR ∈ [0.95, 1.05]                                  |
| **Red Flag Threshold**   | Any agent PWR < 0.80 (strategy collapse)                                                                  |
| **Relationships**        | RationalArbitrageur PWR inversely related to EndowedHolder EPCR                                           |
| **Implementation Notes** | Average across all agents of same type; report mean ± std dev                                             |

```python
def portfolio_wealth_ratio(
    agent_cash_history: list[float],
    agent_position_history: list[float],
    final_price: float,
    initial_wealth: float,
) -> float:
    """Final portfolio value relative to initial wealth.

    Args:
        agent_cash_history: Cash balance over rounds.
        agent_position_history: Share position over rounds.
        final_price: Final market price.
        initial_wealth: Initial cash + position × initial_price.
    Returns:
        Ratio; RationalArbitrageur expected > 1.0, EndowedHolder ≈ 1.0.
    """
    final_value = agent_cash_history[-1] + agent_position_history[-1] * final_price
    return final_value / initial_wealth
```

**Interpretation table**:

| PWR value   | Agent               | Interpretation                      |
|-------------|---------------------|-------------------------------------|
| > 1.15      | RationalArbitrageur | Profits well from endowment premium |
| 1.05 – 1.15 | RationalArbitrageur | Target range                        |
| 0.95 – 1.05 | All types           | Breaks even                         |
| < 0.90      | Any                 | Strategy is net-loss; recalibrate   |

---

### §2.7 Turnover Rate by Agent Type (TR)

| Field                    | Content                                                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------|
| **Category**             | Volume                                                                                                   |
| **Definition**           | Total units traded by an agent type divided by total available position, annualized to simulation length |
| **Formula**              | `TR = total_units_traded / (mean_position × T)`                                                          |
| **Notation**             | mean_position: time-averaged position size                                                               |
| **Python function**      | `turnover_rate(trades_by_agent, mean_position, total_rounds) -> float`                                   |
| **Academic Basis**       | Odean (1999) `doi:10.1111/0022-1082.00091`                                                               |
| **Normal Range**         | NoiseTrader TR ∈ [0.4, 1.2]; EndowedHolder TR ∈ [0.05, 0.25]                                             |
| **Red Flag Threshold**   | EndowedHolder TR > 0.60 (endowment effect not restraining trading)                                       |
| **Relationships**        | Inversely related to EPCR for EndowedHolder                                                              |
| **Implementation Notes** | Compute separately per agent type; ratio of EndowedHolder/RationalArbitrageur TR is key diagnostic       |

```python
def turnover_rate(
    trades_by_agent: list[float], mean_position: float, total_rounds: int
) -> float:
    """Total units traded divided by position capacity, per round.

    Args:
        trades_by_agent: Per-round units traded by this agent type.
        mean_position: Time-averaged position size.
        total_rounds: Total simulation rounds.
    Returns:
        Turnover rate per round; NoiseTrader target [0.4, 1.2].
    """
    return sum(trades_by_agent) / (mean_position * total_rounds)
```

**Interpretation table**:

| Agent type          | Target TR   | Deviation signal                     |
|---------------------|-------------|--------------------------------------|
| EndowedHolder       | 0.05 – 0.25 | TR > 0.50: endowment effect inactive |
| StatusQuoSeller     | 0.10 – 0.35 | TR > 0.60: status-quo bias inactive  |
| RationalArbitrageur | 0.30 – 0.80 | TR < 0.10: arbitrage suppressed      |
| NewBuyer            | 0.20 – 0.60 | TR > 1.0: overbidding noise          |
| NoiseTrader         | 0.40 – 1.20 | TR < 0.20: noise too quiet           |

---

## §3 Analysis Dimensions

| Dimension                 | Metrics                                 | Analytical Question                                      |
|---------------------------|-----------------------------------------|----------------------------------------------------------|
| D1 Price dynamics         | PD, MAD, DPHL                           | How persistent and large is the overvaluation?           |
| D2 Volume analysis        | VSR, TR by agent                        | How severely does ownership bias suppress trading?       |
| D3 Agent performance      | PWR, EPCR by agent                      | Which investor types profit or suffer from the bias?     |
| D4 Threshold sensitivity  | EPCR vs. endowment_premium              | How does the calibration parameter drive outcomes?       |
| D5 Cross-variant fidelity | All metrics across Rule/LLM/RuleLLM/Rag | Do all variants reproduce the same behavioral signature? |

---

## §4 Phase Analysis

| Phase          | Rounds  | Key Metrics | Expected Pattern                                                            |
|----------------|---------|-------------|-----------------------------------------------------------------------------|
| Initialization | 1 – 5   | PD          | Price sets at ~5 % above fundamental; EndowedHolder holds                   |
| Resistance     | 6 – 40  | MAD, VSR    | EndowedHolder/StatusQuoSeller suppress selling; MAD ≈ 0.05–0.10; VSR ≈ 0.45 |
| Correction     | 41 – 80 | DPHL, EPCR  | RationalArbitrageur gradually erodes premium; DPHL ≈ 20–60 rounds           |
| Convergence    | 80+     | PD, PWR     | Price → fundamental ± noise; PWR divergence by agent type stabilizes        |

---

## §5 Cross-Variant Comparison

| Metric               | Rule        | LLM         | RuleLLM     | Rag         |
|----------------------|-------------|-------------|-------------|-------------|
| MAD                  | 0.05 – 0.10 | 0.04 – 0.12 | 0.05 – 0.10 | 0.04 – 0.09 |
| DPHL (rounds)        | 20 – 50     | 15 – 60     | 20 – 50     | 15 – 45     |
| VSR                  | 0.40 – 0.60 | 0.45 – 0.65 | 0.42 – 0.62 | 0.44 – 0.64 |
| EPCR (EndowedHolder) | 0.55 – 0.75 | 0.50 – 0.80 | 0.55 – 0.75 | 0.50 – 0.72 |

---

## §6 Expected Results

### §6.1 Stylised Facts

1. EndowedHolder and StatusQuoSeller consistently demand a premium above fundamental value before selling — EPCR > 0.50.
2. Market prices remain above fundamental for multiple rounds after initialization, producing positive MAD throughout the resistance phase.
3. RationalArbitrageur accumulates positive returns (PWR > 1.0) by supplying liquidity at inflated prices.
4. Total trading volume falls 30–60 % below a fully rational baseline (VSR ∈ [0.40, 0.70]).
5. Price correction is gradual, not discontinuous — DPHL ≥ 15 rounds in calibrated runs.

### §6.2 Calibration Targets

| Parameter               | Target Range   | Tolerance |
|-------------------------|----------------|-----------|
| MAD                     | 0.03 – 0.12    | ±0.02     |
| DPHL                    | 15 – 60 rounds | ±5 rounds |
| VSR                     | 0.40 – 0.70    | ±0.05     |
| EPCR (EndowedHolder)    | 0.40 – 0.75    | ±0.05     |
| RationalArbitrageur PWR | 1.05 – 1.20    | ±0.05     |

### §6.3 Cross-Variant Predictions

| Variant | Signature                                                    | Predicted Deviation  |
|---------|--------------------------------------------------------------|----------------------|
| Rule    | Deterministic endowment_premium → tight MAD band             | Lowest variance      |
| LLM     | Narrative reasoning → wider MAD spread; higher DPHL variance | Most variable        |
| RuleLLM | Rule backbone + LLM nuance → intermediate variance           | Moderate             |
| Rag     | Document-grounded decisions → MAD slightly lower than Rule   | Closest to empirical |

### §6.4 Validation Failure Signs

| Sign                      | Likely Cause                                               | Remediation                                  |
|---------------------------|------------------------------------------------------------|----------------------------------------------|
| MAD < 0.01 after round 10 | endowment_premium too low or EndowedHolder share too small | Increase endowment_premium (0.05 → 0.10)     |
| VSR > 0.90                | EndowedHolder share too small; effect swamped by noise     | Increase EndowedHolder/StatusQuoSeller share |
| DPHL < 5                  | RationalArbitrageur share too large; arbitrage too rapid   | Reduce RationalArbitrageur share             |
| EPCR < 0.20               | endowment_premium set below typical P(t) − F spread        | Raise endowment_premium                      |
| Any PWR < 0.80            | Agent logic error; check decision function                 | Debug players.py                             |

---

## §7 Visualization Catalogue

| #  | Chart Type | Axes / Groups                              | Metric Sourced | Purpose                                            |
|----|------------|--------------------------------------------|----------------|----------------------------------------------------|
| V1 | Line chart | x: round, y: price + fundamental line      | PD             | Endowment overvaluation trajectory                 |
| V2 | Line chart | x: round, y: PD %                          | PD             | Mark endowment_premium and moderate_premium levels |
| V3 | Bar chart  | x: agent type, y: total volume             | VSR, TR        | Turnover by investor class                         |
| V4 | Line chart | x: round, y: PWR by agent                  | PWR            | Divergence over simulation horizon                 |
| V5 | Histogram  | x: per-round volume, y: count              | VSR            | Actual vs. rational-baseline distribution          |
| V6 | Scatter    | x: endowment_premium, y: MAD               | MAD            | Parameter sensitivity sweep                        |
| V7 | Heatmap    | x: round, y: agent type, fill: trade count | TR             | Trade activity density map                         |
