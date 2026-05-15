# DotComBubble Analysis Bases

## §1 Objectives

1. **Reproduce bubble dynamics**: Confirm that destabilizing agents (NewEconomyEvangelist, IPOFlipper, MomentumFollower) drive price above fundamental, creating measurable overvaluation.
2. **Measure crash severity**: Quantify peak-to-trough decline and compare to NASDAQ historical benchmark (−78%).
3. **Isolate narrative channel**: Compare bubble height with/without NewEconomyEvangelist to isolate narrative economics effect.
4. **Evaluate short seller effectiveness**: Measure how much ShortSeller + SkepticalValueInvestor limit bubble height.
5. **Cross-variant comparison**: Assess whether LLM agents exhibit richer narrative-driven bubble behavior than rule-based equivalents.

## §2 Core Metrics

### §2.1 Bubble Amplitude Index (BAI)

**Definition**: Maximum price deviation from fundamental during bubble phase, normalized by fundamental.

```python
def bubble_amplitude_index(price_history, fundamental):
    deviations = [(p - fundamental) / fundamental for p in price_history]
    return max(deviations)
```

**Interpretation**: BAI > 2.0 → extreme bubble (NASDAQ peaked at ~5× fundamental); BAI < 0.3 → mild overvaluation; BAI matching Abreu & Brunnermeier (2003) calibration ≈ 0.5–1.5.

**Reference**: Shiller (2000) CAPE ratio analysis — DOI: https://doi.org/10.1515/9781400865536

---

### §2.2 Bubble Duration (BD)

**Definition**: Number of rounds price remains above 10% overvaluation (δ > 0.10).

```python
def bubble_duration(price_history, fundamental, bubble_threshold=0.10):
    return sum(1 for p in price_history
               if (p - fundamental) / fundamental > bubble_threshold)
```

**Interpretation**: Longer BD → bubble persists longer; calibration target from Abreu & Brunnermeier (2003) — bubbles persist far beyond rational expectation.

**Reference**: Abreu & Brunnermeier (2003) synchronization risk — DOI: https://doi.org/10.1111/1468-0262.00401

---

### §2.3 Crash Severity (CS)

**Definition**: Maximum peak-to-trough price decline during crash phase.

```python
def crash_severity(price_history):
    peak = max(price_history)
    peak_idx = price_history.index(peak)
    trough = min(price_history[peak_idx:])
    return (peak - trough) / peak
```

**Interpretation**: CS ≈ 0.78 matches NASDAQ dot-com historical crash; CS < 0.30 → mild correction; CS > 0.80 → extreme crash.

**Reference**: Ofek & Richardson (2003) NASDAQ crash analysis — DOI: https://doi.org/10.1111/1540-6261.00530

---

### §2.4 Momentum Amplification Factor (MAF)

**Definition**: Ratio of MomentumFollower buy volume to total buy volume during bubble ascent phase.

```python
def momentum_amplification_factor(agent_volume_by_type, bubble_rounds):
    momentum_buys = sum(agent_volume_by_type["MomentumFollower"]["buy"][t]
                        for t in bubble_rounds)
    total_buys = sum(sum(v["buy"].get(t, 0) for v in agent_volume_by_type.values())
                     for t in bubble_rounds)
    return momentum_buys / total_buys if total_buys > 0 else 0.0
```

**Interpretation**: MAF > 0.4 → momentum followers dominate bubble inflation; MAF < 0.2 → narrative/IPO channels dominant.

**Reference**: Jegadeesh & Titman (1993) momentum returns — DOI: https://doi.org/10.1111/j.1540-6261.1993.tb04702.x

---

### §2.5 Short Squeeze Resistance (SSR)

**Definition**: Fraction of rounds where ShortSeller is net seller despite positive price momentum (resisting squeeze).

```python
def short_squeeze_resistance(short_seller_orders, momentum_sign_history):
    squeeze_rounds = [t for t, m in enumerate(momentum_sign_history) if m > 0]
    sells_in_squeeze = sum(1 for t in squeeze_rounds
                           if short_seller_orders[t]["action"] == "sell")
    return sells_in_squeeze / len(squeeze_rounds) if squeeze_rounds else 0.0
```

**Interpretation**: SSR = 1.0 → ShortSeller never capitulates; SSR < 0.3 → ShortSeller buys to cover under momentum pressure (classic short squeeze).

**Reference**: Abreu & Brunnermeier (2003) arbitrage risk during bubble — DOI: https://doi.org/10.1111/1468-0262.00401

---

### §2.6 Recovery Time (RT)

**Definition**: Rounds from trough to recovery back to within 10% of fundamental.

```python
def recovery_time(price_history, fundamental, recovery_threshold=0.10):
    peak = max(price_history)
    peak_idx = price_history.index(peak)
    trough_idx = peak_idx + price_history[peak_idx:].index(min(price_history[peak_idx:]))
    for t in range(trough_idx, len(price_history)):
        if abs((price_history[t] - fundamental) / fundamental) < recovery_threshold:
            return t - trough_idx
    return len(price_history) - trough_idx  # no recovery
```

**Interpretation**: Shorter RT → faster fundamental restoration; historical dot-com recovery took ~15 years.

**Reference**: Shiller (2000) irrational exuberance cycle length.

---

### §2.7 Wealth Divergence Index (WDI)

**Definition**: Terminal wealth of destabilizing agents (NewEconomyEvangelist + IPOFlipper + MomentumFollower) vs. stabilizing agents (SkepticalValueInvestor + ShortSeller), normalized.

```python
def wealth_divergence_index(agent_final_states, final_price, initial_wealth=100000):
    destabilizing = ["NewEconomyEvangelist", "IPOFlipper", "MomentumFollower"]
    stabilizing = ["SkepticalValueInvestor", "ShortSeller"]
    dest_wealth = sum(s["cash"] + s["position"] * final_price
                      for k, s in agent_final_states.items() if k in destabilizing)
    stab_wealth = sum(s["cash"] + s["position"] * final_price
                      for k, s in agent_final_states.items() if k in stabilizing)
    return (dest_wealth - stab_wealth) / (3 * initial_wealth)
```

**Interpretation**: WDI > 0 → destabilizing agents profit (bubble not fully deflated); WDI < 0 → stabilizing agents profit (crash severe, short sellers vindicated).

**Reference**: Ofek & Richardson (2003) — long-run returns after lock-up expiration.

---

## §3 Analysis Dimensions

| Dimension          | Primary Metric | Secondary Metrics |
|--------------------|----------------|-------------------|
| Bubble height      | BAI (§2.1)     | BD (§2.2)         |
| Bubble persistence | BD (§2.2)      | MAF (§2.4)        |
| Crash severity     | CS (§2.3)      | RT (§2.6)         |
| Momentum channel   | MAF (§2.4)     | BD (§2.2)         |
| Short seller role  | SSR (§2.5)     | WDI (§2.7)        |
| Recovery dynamics  | RT (§2.6)      | CS (§2.3)         |
| Wealth outcomes    | WDI (§2.7)     | —                 |

## §4 Phase Analysis

### Bubble Inflation Phase (δ > 0.10)

- **Expected**: NewEconomyEvangelist buys regardless of price; MomentumFollower amplifies; IPOFlipper flips at δ > 0.05.
- **Metrics**: BAI builds; BD counts rounds; MAF measures momentum contribution.
- **Warning sign**: MAF > 0.5 → momentum self-reinforcing; crash likely to be sudden.

### Peak Phase (BAI maximum)

- **Expected**: SkepticalValueInvestor begins selling at δ > 0.20; ShortSeller selling at δ > 0.15.
- **Metrics**: SSR measures if short sellers hold positions; WDI direction determined here.

### Crash Phase (rapid δ decline)

- **Expected**: NewEconomyEvangelist finally sells at δ < −0.30; MomentumFollower sells on negative momentum; IPOFlipper sells.
- **Metrics**: CS measured from peak; RT tracking begins at trough.

### Recovery Phase (δ approaching 0)

- **Expected**: SkepticalValueInvestor buys at δ < −0.10; ShortSeller covers at δ < −0.05.
- **Metrics**: RT measured; final WDI computed.

## §5 Cross-Variant Comparison

| Metric | Rule (Expected)              | LLM (Expected)                                 | RuleLLM (Expected) | Rag (Expected)                                  |
|--------|------------------------------|------------------------------------------------|--------------------|-------------------------------------------------|
| BAI    | ≈ 0.5–1.5 (mechanical)       | Higher; LLM narrative conviction drives bubble | Close to Rule      | RAG historical cases may moderate overvaluation |
| BD     | Parameter-driven             | LLM may prolong bubble (narrative persistence) | Close to Rule      | RAG bubble-burst timing may shorten BD          |
| CS     | Parameter-driven (≈ 0.5–0.7) | May be more severe (LLM panic)                 | Close to Rule      | RAG crash history may moderate panic            |
| MAF    | Deterministic                | LLM may show trend-following amplification     | Close to Rule      | RAG momentum literature may calibrate MAF       |
| SSR    | Threshold-based (≈ 0.5)      | LLM short seller may capitulate (squeeze)      | Close to Rule      | RAG synchronization risk knowledge improves SSR |

## §6 Expected Results

**Rule baseline**:
- BAI ≈ 0.5–1.5 (50–150% above fundamental)
- BD ≈ 20–50 rounds
- CS ≈ 0.4–0.7 (40–70% crash)
- MAF ≈ 0.3–0.5
- WDI near-zero or slightly negative (stabilizing agents partially vindicated)

**Calibration targets**:
- BAI: 0.5–1.5 (realistic bubble range)
- CS: 0.5–0.8 (matching dot-com historical range)
- BD: > 15 rounds (bubble must persist meaningfully)

## §7 Visualization Catalogue

| Chart                     | X-axis         | Y-axis             | Purpose                        |
|---------------------------|----------------|--------------------|--------------------------------|
| Price trajectory          | Round          | Price              | Bubble inflation and crash     |
| Deviation trajectory      | Round          | δ(t)               | Phase identification           |
| Agent buy/sell volume     | Round          | Volume by agent    | Attribution analysis           |
| BAI distribution          | Simulation run | BAI value          | Cross-variant comparison       |
| Bubble duration histogram | Simulation run | BD value           | Persistence comparison         |
| Crash severity box plot   | Variant        | CS value           | Cross-variant crash comparison |
| Short seller wealth       | Round          | ShortSeller wealth | Squeeze visualization          |
| WDI by variant            | Variant        | WDI value          | Wealth transfer comparison     |
