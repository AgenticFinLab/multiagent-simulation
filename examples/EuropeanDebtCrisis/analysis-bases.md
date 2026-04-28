# EuropeanDebtCrisis — Analysis Basis

## §1 Analysis Objectives

Quantify the self-fulfilling crisis dynamics: crisis severity, duration, ECB intervention effectiveness, and sovereign-bank nexus amplification. Primary goals:
1. Measure crisis depth (price deviation below fundamental) and duration
2. Quantify the sovereign-bank amplification loop contribution from CreditorPanicker
3. Measure ECBIntervenor's effectiveness in halting the self-fulfilling spiral
4. Compare crisis dynamics across Rule / LLM / RuleLLM / Rag variants

## §2 Core Metrics

### §2.1 Crisis Depth Index (CDI)

**Definition**: Maximum negative deviation from fundamental during the simulation.

**Python function**:
```python
def crisis_depth_index(price_history: List[float], fundamental: float) -> float:
    """Maximum negative deviation from fundamental (crisis depth).

    Args:
        price_history: List of bond prices per round
        fundamental: Fundamental bond price (fiscal sustainability level)
    Returns:
        Maximum negative deviation as positive number (e.g., 0.30 = 30% below fundamental)
    """
```

**Interpretation**:
- High CDI (> 0.20): Severe crisis; self-fulfilling spiral occurred
- Moderate CDI (0.10–0.20): Contained crisis; ECB intervention partially effective
- Low CDI (< 0.10): Mild or no crisis; fundamentals dominating

**Theoretical grounding**: De Grauwe (2011) — crisis depth measures severity of self-fulfilling spiral
**DOI**: `https://doi.org/10.2139/ssrn.1930063`

---

### §2.2 Crisis Duration (CD)

**Definition**: Number of rounds for which `deviation < −0.10` (crisis threshold).

**Python function**:
```python
def crisis_duration(price_history: List[float], fundamental: float, crisis_threshold: float = -0.10) -> int:
    """Number of rounds in crisis state (deviation below threshold).

    Args:
        price_history: List of bond prices per round
        fundamental: Fundamental bond price
        crisis_threshold: Deviation threshold defining crisis state (default −0.10)
    Returns:
        Number of rounds spent in crisis state
    """
```

**Interpretation**:
- High CD (> 20 rounds): Persistent crisis; ECB intervention delayed or insufficient
- Moderate CD (5–20 rounds): Temporary crisis; intervention effective
- Zero: No crisis episode

**Theoretical grounding**: De Grauwe & Ji (2012) — crisis duration measures self-fulfilling persistence
**DOI**: `https://doi.org/10.1016/j.jimonfin.2012.11.003`

---

### §2.3 Amplification Ratio (AR)

**Definition**: Ratio of total sell volume from CreditorPanicker to total sell volume from PeripheryBondSeller; measures sovereign-bank nexus amplification.

**Python function**:
```python
def amplification_ratio(creditor_sell_volume: List[float], periphery_sell_volume: List[float]) -> float:
    """Ratio of CreditorPanicker to PeripheryBondSeller sell volume.

    Args:
        creditor_sell_volume: Per-round sell quantities from CreditorPanicker
        periphery_sell_volume: Per-round sell quantities from PeripheryBondSeller
    Returns:
        Total volume ratio (> 1 means creditor amplification exceeded initial shock)
    """
```

**Interpretation**:
- High AR (> 1.0): Creditor panic amplified the initial shock — doom loop active
- AR ≈ 1.0: Creditor and periphery selling roughly equal
- Low AR (< 0.5): Creditor panic minimal; initial shock self-contained

**Theoretical grounding**: Acharya et al. (2014) — AR quantifies sovereign-bank nexus
**DOI**: `https://doi.org/10.1111/jofi.12206`

---

### §2.4 Intervention Effectiveness Ratio (IER)

**Definition**: Fraction of crisis rounds during which ECBIntervenor was actively buying; measures backstop coverage.

**Python function**:
```python
def intervention_effectiveness_ratio(ecb_buy_rounds: List[bool], crisis_rounds: List[bool]) -> float:
    """Fraction of crisis rounds with active ECB intervention.

    Args:
        ecb_buy_rounds: Boolean list — True if ECB bought in that round
        crisis_rounds: Boolean list — True if price was in crisis state that round
    Returns:
        Fraction of crisis rounds covered by ECB buying (0.0–1.0)
    """
```

**Interpretation**:
- High IER (> 0.80): ECB effectively covered crisis; backstop credible
- Moderate IER (0.40–0.80): Partial ECB response; crisis outlasted intervention
- Low IER (< 0.40): ECB intervention ineffective or threshold too negative

**Theoretical grounding**: Draghi (2012) — effective backstop should have IER near 1.0
**DOI**: N/A (ECB speech)

---

### §2.5 Spread Recovery Time (SRT)

**Definition**: Number of rounds for deviation to recover from CDI (crisis bottom) to above −0.05 (near-fundamental).

**Python function**:
```python
def spread_recovery_time(price_history: List[float], fundamental: float, recovery_threshold: float = -0.05) -> int:
    """Rounds from crisis bottom to near-fundamental recovery.

    Args:
        price_history: List of bond prices per round
        fundamental: Fundamental bond price
        recovery_threshold: Deviation level considered recovered (default −0.05)
    Returns:
        Number of rounds from crisis bottom to recovery; 0 if no crisis; -1 if no recovery
    """
```

**Interpretation**:
- Short SRT (< 5 rounds): Rapid recovery; ECB intervention decisive
- Moderate SRT (5–15 rounds): Gradual recovery; HedgedFund + ECB working together
- Long SRT (> 15 rounds): Persistent spread; multiple stabilization attempts needed

**Theoretical grounding**: De Grauwe & Ji (2012) — recovery speed measures ECB credibility
**DOI**: `https://doi.org/10.1016/j.jimonfin.2012.11.003`

---

### §2.6 Arbitrage Profit Rate (APR)

**Definition**: Terminal portfolio value relative to initial value for HedgedFund; measures profit from spread exploitation.

**Python function**:
```python
def arbitrage_profit_rate(hf_terminal_wealth: float, hf_initial_wealth: float) -> float:
    """HedgedFund terminal profit rate.

    Args:
        hf_terminal_wealth: HedgedFund final portfolio value (cash + position × final_price)
        hf_initial_wealth: HedgedFund initial portfolio value
    Returns:
        Profit rate (e.g., 0.15 = 15% profit; negative = loss)
    """
```

**Interpretation**:
- High APR (> 0.10): HedgedFund profited significantly from spread dislocation; crisis was deep and long
- Low APR (0–0.10): Modest spread exploitation; crisis quickly resolved
- Negative APR: HedgedFund was caught wrong-way during the crisis

**Theoretical grounding**: Shleifer & Vishny (1997) — APR measures arbitrageur ability to exploit crisis
**DOI**: `https://doi.org/10.1111/j.1540-6261.1997.tb03807.x`

---

## §3 Analysis Dimensions

| Dimension          | What to Measure                          | Key Metric |
|--------------------|------------------------------------------|------------|
| Crisis severity    | How far below fundamental did price fall | CDI        |
| Crisis persistence | How long did crisis last                 | CD         |
| Doom loop          | Did creditor panic amplify initial shock | AR         |
| ECB effectiveness  | Did ECB intervention cover crisis rounds | IER        |
| Recovery speed     | How fast did price recover after crisis  | SRT        |
| Arbitrage profit   | Did HedgedFund profit from dislocation   | APR        |

## §4 Phase Analysis

| Phase         | Rounds | Key Events                                            | Metrics to Monitor           |
|---------------|--------|-------------------------------------------------------|------------------------------|
| Pre-crisis    | 1–5    | Mild negative deviation; PeripheryBondSeller inactive | CDI near 0                   |
| Crisis onset  | 6–10   | PeripheryBondSeller triggers; CreditorPanicker begins | CDI rising, AR building      |
| Crisis peak   | 11–20  | Maximum spread; doom loop active; ECB activating      | CDI peak, IER rising         |
| Stabilization | 21–30  | ECB buying offsets panickers; spread stabilizing      | SRT shortening               |
| Recovery      | 31–50  | HedgedFund + ECB driving recovery; spread compressing | CD stabilizing, APR positive |

## §5 Cross-Variant Analysis

| Metric | Rule         | LLM         | RuleLLM      | Rag         |
|--------|--------------|-------------|--------------|-------------|
| CDI    | 0.15–0.35    | 0.10–0.45   | 0.14–0.32    | 0.12–0.38   |
| CD     | 10–30 rounds | 5–40 rounds | 10–28 rounds | 8–35 rounds |
| AR     | 0.8–1.5      | 0.5–2.0     | 0.8–1.4      | 0.7–1.8     |
| IER    | 0.70–0.95    | 0.50–1.00   | 0.72–0.95    | 0.65–0.98   |
| SRT    | 5–20 rounds  | 3–25 rounds | 5–18 rounds  | 4–22 rounds |

## §6 Expected Results

| Agent Type          | Metric      | Expected Value            | Condition                         |
|---------------------|-------------|---------------------------|-----------------------------------|
| PeripheryBondSeller | Sell volume | 600 units/round in crisis | deviation < sell_threshold        |
| CreditorPanicker    | AR          | 0.8–1.5                   | panic_threshold more negative     |
| ECBIntervenor       | IER         | 0.75–0.95                 | intervention_threshold calibrated |
| HedgedFund          | APR         | 0.05–0.20                 | Deep crisis, limits to arbitrage  |
| Market aggregate    | CDI         | 0.15–0.30                 | Rule variant calibration          |

## §7 Visualization Catalogue

1. **Bond price time series**: Line chart with fundamental baseline; shows crisis depth and recovery
2. **Net demand decomposition**: Stacked bar by investor type per round; shows amplification sources
3. **CDI and CD heatmap**: Across parameter sweep (sell_threshold × intervention_threshold)
4. **IER vs. CDI scatter**: ECB effectiveness vs. crisis severity across 4 variants
5. **HedgedFund APR bar chart**: Profit rate by variant
6. **Variant comparison radar**: CDI, CD, AR, IER, SRT, APR across 4 variants
