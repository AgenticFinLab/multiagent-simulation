# EquityPremium — Analysis Basis

## §1 Analysis Objectives

Quantify the equity premium puzzle dynamics across investor types and variants. Primary goals:
1. Measure the simulated equity premium and compare to historical benchmark (6.18%)
2. Quantify how evaluation frequency and loss aversion affect equity allocation
3. Compare premium levels and volatility across Rule / LLM / RuleLLM / Rag variants

## §2 Core Metrics

### §2.1 Simulated Equity Premium (SEP)

**Definition**: Annualized difference between average stock return and bond return over the simulation.

**Python function**:
```python
def simulated_equity_premium(stock_returns: List[float], bond_return: float, rounds_per_year: int = 12) -> float:
    """Annualized simulated equity premium.

    Args:
        stock_returns: List of per-round stock returns
        bond_return: Risk-free bond return per round (constant)
        rounds_per_year: Number of simulation rounds per year for annualization
    Returns:
        Annualized equity premium as a decimal (e.g., 0.06 = 6%)
    """
```

**Interpretation**:
- High value (> 0.05): Myopic loss aversion is dominating; loss-averse investors require large premium
- Low value (< 0.02): Rational/long-horizon investors are dominating; premium compressed
- Zero: Market is pricing equities at bond return equivalent

**Theoretical grounding**: Mehra & Prescott (1985) — target ~6% annualized premium
**DOI**: `https://doi.org/10.1016/0304-3932(85)90061-3`

---

### §2.2 Equity Allocation Deviation (EAD)

**Definition**: Average absolute difference between each investor's actual stock allocation and a 50% neutral benchmark.

**Python function**:
```python
def equity_allocation_deviation(agent_stock_values: List[float], agent_portfolio_values: List[float], neutral_pct: float = 0.50) -> float:
    """Mean absolute deviation of equity allocation from neutral benchmark.

    Args:
        agent_stock_values: Time series of stock position values for an investor
        agent_portfolio_values: Time series of total portfolio values
        neutral_pct: Neutral equity allocation benchmark (default 50%)
    Returns:
        Mean absolute deviation as decimal (e.g., 0.15 = 15 percentage points from neutral)
    """
```

**Interpretation**:
- High EAD (> 0.20): Investor systematically over- or under-weights equities
- Low EAD (< 0.05): Investor holds near neutral allocation
- Positive direction: Under-allocation (bond preference); Negative: Over-allocation

**Theoretical grounding**: Benartzi & Thaler (1995) — myopic investors show persistent under-allocation
**DOI**: `https://doi.org/10.2307/2118511`

---

### §2.3 Evaluation Frequency Sensitivity (EFS)

**Definition**: Correlation between the evaluation_window parameter and the investor's equity allocation; tests the Benartzi-Thaler horizon hypothesis.

**Python function**:
```python
def evaluation_frequency_sensitivity(window_sizes: List[int], mean_equity_allocations: List[float]) -> float:
    """Correlation between evaluation window and equity allocation.

    Args:
        window_sizes: List of evaluation_window parameter values tested
        mean_equity_allocations: Corresponding mean equity allocations per investor type
    Returns:
        Pearson correlation coefficient (expected positive: longer window → higher allocation)
    """
```

**Interpretation**:
- High positive (> 0.7): Strong horizon effect — confirms Benartzi-Thaler hypothesis
- Near zero: No horizon effect
- Negative: Longer-horizon investors hold less equity (anomalous)

**Theoretical grounding**: Benartzi & Thaler (1995)
**DOI**: `https://doi.org/10.2307/2118511`

---

### §2.4 Stock Return Volatility Ratio (SRVR)

**Definition**: Ratio of simulated stock return standard deviation to bond return standard deviation; measures excess equity volatility.

**Python function**:
```python
def stock_return_volatility_ratio(stock_returns: List[float], bond_return: float) -> float:
    """Ratio of stock return std to bond return equivalent.

    Args:
        stock_returns: List of per-round stock returns
        bond_return: Risk-free bond return per round (constant)
    Returns:
        Volatility ratio (stock_std / bond_return); higher values = more excess volatility
    """
```

**Interpretation**:
- High (> 5): Stocks are much more volatile than bonds; myopic investors experience large loss probability
- Moderate (2–5): Realistic range matching historical equity markets
- Low (< 2): Stocks appear nearly as safe as bonds; premium should collapse

**Theoretical grounding**: Mehra & Prescott (1985) — historical σ(equity) / r_bond ≈ 16
**DOI**: `https://doi.org/10.1016/0304-3932(85)90061-3`

---

### §2.5 Loss Probability Index (LPI)

**Definition**: Fraction of evaluation windows in which the investor experienced a net loss; key driver of myopic loss aversion.

**Python function**:
```python
def loss_probability_index(stock_returns: List[float], evaluation_window: int = 5) -> float:
    """Fraction of evaluation windows with negative return.

    Args:
        stock_returns: List of per-round stock returns
        evaluation_window: Rolling window size for evaluation
    Returns:
        Fraction of windows with negative sum return (0.0–1.0)
    """
```

**Interpretation**:
- High (> 0.40): Frequent losses in myopic window; drives high equity premium demand
- Low (< 0.20): Few losses even myopically; premium should be modest
- 0.50: Random walk; equal chance of gain/loss

**Theoretical grounding**: Benartzi & Thaler (1995) — LPI ≈ 0.49 for annual evaluation of U.S. equities
**DOI**: `https://doi.org/10.2307/2118511`

---

### §2.6 Portfolio Wealth Efficiency (PWE)

**Definition**: Ratio of terminal portfolio value to hypothetical buy-and-hold value; measures welfare cost of behavioral biases.

**Python function**:
```python
def portfolio_wealth_efficiency(agent_terminal_wealth: float, buy_and_hold_terminal_wealth: float) -> float:
    """Ratio of terminal wealth to buy-and-hold benchmark.

    Args:
        agent_terminal_wealth: Final portfolio value (cash + stock × final_price)
        buy_and_hold_terminal_wealth: Terminal value of holding initial stock allocation throughout
    Returns:
        Efficiency ratio (1.0 = matched benchmark; < 1.0 = underperformed due to biased trading)
    """
```

**Interpretation**:
- Above 1.0: Investor out-performed buy-and-hold (rare for myopic agents)
- 0.90–1.0: Modest welfare cost of behavioral bias
- Below 0.90: Significant wealth loss due to myopic loss aversion or noise

**Theoretical grounding**: Benartzi & Thaler (1995) — myopic investors leave significant wealth on table
**DOI**: `https://doi.org/10.2307/2118511`

---

## §3 Analysis Dimensions

| Dimension         | What to Measure                              | Key Metric |
|-------------------|----------------------------------------------|------------|
| Premium level     | Aggregate demanded equity premium            | SEP        |
| Allocation bias   | How far each investor deviates from neutral  | EAD        |
| Horizon effect    | Does longer evaluation window → more equity? | EFS        |
| Volatility effect | Does excess volatility drive the premium?    | SRVR       |
| Loss frequency    | How often do myopic windows show losses?     | LPI        |
| Wealth impact     | Cost of behavioral bias vs. buy-and-hold     | PWE        |

## §4 Phase Analysis

| Phase         | Rounds | Key Events                                                   | Metrics to Monitor |
|---------------|--------|--------------------------------------------------------------|--------------------|
| Warm-up       | 1–5    | Price initialization; investors build history                | SEP stabilizing    |
| Myopic regime | 6–20   | Full myopic evaluation; high loss probability drives premium | LPI, SEP rising    |
| Steady state  | 21–50  | Equilibrium premium established; variant differences visible | EAD, SRVR          |
| Correction    | 51+    | If LongHorizonInvestor dominates, premium compresses         | SEP, PWE           |

## §5 Cross-Variant Analysis

| Metric         | Rule      | LLM       | RuleLLM   | Rag       |
|----------------|-----------|-----------|-----------|-----------|
| SEP            | 0.04–0.07 | 0.03–0.09 | 0.04–0.07 | 0.03–0.08 |
| EAD (MyopicLA) | 0.15–0.30 | 0.10–0.35 | 0.14–0.28 | 0.12–0.30 |
| LPI            | 0.40–0.55 | 0.38–0.58 | 0.40–0.55 | 0.38–0.55 |
| PWE (MyopicLA) | 0.85–0.95 | 0.80–1.00 | 0.85–0.97 | 0.83–0.97 |

## §6 Expected Results

| Agent Type               | Metric | Expected Value                           | Condition                |
|--------------------------|--------|------------------------------------------|--------------------------|
| MyopicLossAverseInvestor | EAD    | 0.15–0.30 (under-weighting)              | High loss_aversion       |
| LongHorizonInvestor      | EAD    | 0.05–0.15 (over-weighting toward target) | target_stock_pct > 0.50  |
| RiskNeutralInvestor      | EAD    | 0.02–0.10 (near neutral)                 | Excess return near 0     |
| ConservativeInvestor     | EAD    | 0.20–0.35 (persistent under-weighting)   | Low target_stock_pct     |
| NoiseTrader              | EAD    | 0.05–0.15 (random around neutral)        | noise_std = 3            |
| Market aggregate         | SEP    | 0.04–0.07                                | Rule variant calibration |

## §7 Visualization Catalogue

1. **Stock price time series**: Line chart with bond return baseline; shows premium accumulation
2. **Equity allocation by investor**: Stacked area chart of stock fraction per investor over time
3. **Equity premium time series**: Rolling SEP vs. Mehra-Prescott benchmark (6.18%)
4. **Loss probability heatmap**: LPI by investor × evaluation window size
5. **Wealth efficiency bar chart**: PWE for each investor type across 4 variants
6. **Variant comparison radar**: SEP, EAD, LPI, SRVR, PWE across 4 variants
