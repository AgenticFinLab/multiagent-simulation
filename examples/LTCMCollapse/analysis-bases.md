# LTCMCollapse — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question | Metrics | Expected Finding |
|---|---|---|---|
| O1 | Does leveraged convergence arbitrage create large deviations from fundamental value? | price deviation, maximum drawdown | deviation exceeds normal band after stress amplification |
| O2 | Does deleveraging amplify the initial dislocation? | drawdown, return volatility, action counts | forced selling/cutting increases volatility |
| O3 | Does liquidity withdrawal matter? | deviation persistence, recovery half-life | recovery slows when liquidity providers hold under stress |
| O4 | Does emergency intervention stabilize the market? | recovery half-life, final deviation | intervention shortens recovery and supports price |
| O5 | Do API variants preserve or alter the mechanism? | cross-variant metrics, LLM quality fields | LLM/RuleLLM/Rag differ in timing and action distribution |

## §2 Core Metrics Catalogue

### §2.1 Price Deviation

- **Function**:
  ```python
  def calculate_metrics(data: dict) -> dict:
      ...
  ```
- **Formula**:
  ```
  deviation(t) = (P(t) - F(t)) / F(t)
  ```
- **Data Source**: `load_simulation_data()` reads `custom_state.price` and `custom_state.fundamental` from market records.
- **Interpretation**: Large absolute deviation is the core stress signal for the LTCM mechanism.

### §2.2 Maximum Drawdown

- **Function**:
  ```python
  def calculate_metrics(data: dict) -> dict:
      ...
  ```
- **Formula**:
  ```
  max_drawdown = max_t((peak_price(t) - P(t)) / peak_price(t))
  ```
- **Interpretation**: worst peak-to-trough price decline during the crisis.

### §2.3 Mean Absolute Deviation

- **Function**:
  ```python
  def calculate_metrics(data: dict) -> dict:
      ...
  ```
- **Formula**:
  ```
  mean_abs_deviation = mean(|deviation(t)|)
  ```
- **Interpretation**: Persistence of dislocation.

### §2.4 Volatility

- **Function**:
  ```python
  def calculate_metrics(data: dict) -> dict:
      ...
  ```
- **Formula**:
  ```
  volatility = std(returns) * sqrt(252) * 100
  returns(t) = (P(t) - P(t-1)) / P(t-1)
  ```
- **Interpretation**: Stress intensity and round-to-round instability.

### §2.5 Price Trough

- **Function**:
  ```python
  def calculate_metrics(data: dict) -> dict:
      ...
  ```
- **Formula**:
  ```
  min_price = min(P(t))
  ```
- **Interpretation**: Lowest simulated market price during the crisis.

### §2.6 Final Recovery

- **Function**:
  ```python
  def calculate_metrics(data: dict) -> dict:
      ...
  ```
- **Formula**:
  ```
  final_deviation = (P(T) - F(T)) / F(T)
  ```
- **Interpretation**: Whether the system returns toward fundamental value by the end of 200 rounds.

### §2.7 LLM Output Quality

- **Function**:
  ```python
  def audit_llm_output_quality(sample_path: str) -> dict:
      ...
  ```
- **Fields**: parse failures, fallback counts, action distribution, completed rounds.
- **Interpretation**: API-mode success is not just `exit=0`; malformed output and fallback rate must be reviewed.

## §3 Analysis Dimensions

### §3.1 Price Dislocation

Uses price deviation, min price, and final price to determine whether the scenario generated a material convergence-arbitrage stress event.

### §3.2 Deleveraging Intensity

Uses return volatility and drawdown metrics as observable proxies for forced selling and risk cuts.

### §3.3 Liquidity And Recovery

Uses deviation persistence and final recovery to infer whether liquidity withdrawal delayed stabilization.

### §3.4 Cross-Variant Behavior

Compares Rule, LLM, RuleLLM, and Rag runs using the same price metrics and Level-2 API quality metadata.

## §4 Phase Analysis Framework

| Phase | Entry Condition | Expected Indicators |
|---|---|---|
| Normal | early rounds, small deviation | price near fundamental |
| Stress Build-Up | `abs(deviation)` crosses entry and VaR thresholds | arbitrage and risk-management actions |
| Liquidity Crisis | deviation remains large and liquidity provider withdraws | high volatility, persistent drawdown |
| Intervention/Recovery | central-bank support and mean reversion dominate | final price moves back toward fundamental |

## §5 Cross-Variant Comparison Framework

| Variant | Baseline Role | Comparison Question |
|---|---|---|
| Rule | deterministic baseline | does the mechanism emerge from fixed rules? |
| LLM | behavioral language baseline | do persona-only agents act coherently under stress? |
| RuleLLM | rule-guided LLM | does explicit rule knowledge preserve the baseline mechanism? |
| Rag | historically informed LLM | does external crisis knowledge change action timing or recovery? |

## §6 Expected Results And Validation

| Metric | Expected Direction | Validation Note |
|---|---|---|
| max absolute deviation | higher than normal-market noise | should exceed small random noise band |
| volatility | rises during stress | volatility should not remain flat across 200 rounds |
| final recovery | partial recovery toward fundamental | mean reversion and support should prevent permanent zero |
| LLM fallback rate | low | high fallback invalidates behavioral interpretation |

The Rule analysis implementation writes these metrics to `metrics.json` and writes validation status to `summary.json`. LLM-family quality checks are performed by the experiment resource-pack audit before a sample is accepted.

## §7 Visualization Catalogue

| Plot | Generated By | Purpose |
|---|---|---|
| Price vs Fundamental | `create_visualizations()` | confirm dislocation and recovery |
| Price Deviation | `create_visualizations()` | show stress magnitude |
| Returns | `create_visualizations()` | observe crisis volatility |
| Return Distribution | `create_visualizations()` | inspect tail behavior |
