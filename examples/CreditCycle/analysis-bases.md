# CreditCycle Analysis Bases

## §1 Objectives

The CreditCycle simulation is analyzed to:

1. **Verify boom-bust endogeneity**: Confirm that the credit cycle emerges from agent interactions rather than exogenous shocks.
2. **Measure leverage amplification**: Quantify how ProCyclicalLender and MinskyBorrower magnify price deviations during expansions.
3. **Evaluate counter-cyclical efficacy**: Assess how effectively CounterCyclicalLender and ValueInvestor dampen the cycle.
4. **Track Minsky trajectory**: Observe hedge→speculative→Ponzi→deleveraging sequence via `stable_rounds` accumulation.
5. **Compare variant behavior**: Determine whether LLM-based agents exhibit more realistic boom-bust narratives than rule-based equivalents.

## §2 Core Metrics

### §2.1 Leverage Amplitude Index (LAI)

**Definition**: Peak positive deviation during expansion phase divided by trough negative deviation during contraction.

```python
def leverage_amplitude_index(price_history, fundamental):
    deviations = [(p - fundamental) / fundamental for p in price_history]
    peak = max(deviations)
    trough = min(deviations)
    return abs(peak) / abs(trough) if trough != 0 else float('inf')
```

**Interpretation**: LAI > 1 indicates asymmetric boom-bust; LAI ≈ 1 indicates symmetric cycle.

**Reference**: Geanakoplos (2010) leverage cycle calibration — DOI: https://doi.org/10.1086/648285

---

### §2.2 Minsky Fragility Score (MFS)

**Definition**: Average `stable_rounds` count accumulated by MinskyBorrower before a bust event (δ < −0.05).

```python
def minsky_fragility_score(stable_rounds_history, crisis_events):
    scores = []
    for onset_round in crisis_events:
        pre_crisis = stable_rounds_history[:onset_round]
        scores.append(max(pre_crisis[-10:]) if pre_crisis else 0)
    return sum(scores) / len(scores) if scores else 0
```

**Interpretation**: Higher MFS → more leverage was accumulated before the crisis; maps to Minsky's Ponzi phase depth.

**Reference**: Minsky (1986) financial instability hypothesis; Kindleberger (1978) mania-panic-crash sequence.

---

### §2.3 Credit Contraction Speed (CCS)

**Definition**: Rate of price decline from peak to trough, measured in price units per round.

```python
def credit_contraction_speed(price_history):
    peak_idx = price_history.index(max(price_history))
    trough_idx = price_history.index(min(price_history[peak_idx:]))
    if trough_idx == peak_idx:
        return 0.0
    return (price_history[peak_idx] - price_history[trough_idx]) / (trough_idx - peak_idx)
```

**Interpretation**: Faster contraction → sharper Minsky moment; slower contraction → gradual deleveraging.

**Reference**: Adrian & Shin (2010) — DOI: https://doi.org/10.1016/j.jfi.2008.12.002

---

### §2.4 Counter-Cyclical Offset Ratio (CCOR)

**Definition**: Fraction of bust-phase selling pressure absorbed by CounterCyclicalLender + ValueInvestor.

```python
def counter_cyclical_offset_ratio(agent_volume_by_type, phase="bust"):
    bust_buys_stabilizing = agent_volume_by_type["CounterCyclicalLender"]["buy"] + \
                            agent_volume_by_type["ValueInvestor"]["buy"]
    bust_sells_destabilizing = agent_volume_by_type["ProCyclicalLender"]["sell"] + \
                               agent_volume_by_type["MinskyBorrower"]["sell"]
    return bust_buys_stabilizing / bust_sells_destabilizing if bust_sells_destabilizing > 0 else float('inf')
```

**Interpretation**: CCOR > 0.5 → stabilizers absorb >50% of bust selling; CCOR < 0.3 → cycle runs unchecked.

**Reference**: Basel III CCyB rationale (BIS, 2010).

---

### §2.5 Phase Duration Ratio (PDR)

**Definition**: Ratio of expansion-phase rounds to contraction-phase rounds.

```python
def phase_duration_ratio(price_history, fundamental, threshold=0.02):
    deviations = [(p - fundamental) / fundamental for p in price_history]
    expansion_rounds = sum(1 for d in deviations if d > threshold)
    contraction_rounds = sum(1 for d in deviations if d < -threshold)
    return expansion_rounds / contraction_rounds if contraction_rounds > 0 else float('inf')
```

**Interpretation**: PDR > 2 → prolonged boom with sharp bust (typical Minsky pattern); PDR ≈ 1 → symmetric cycle.

**Reference**: Reinhart & Rogoff (2009) cross-country evidence on credit boom duration.

---

### §2.6 Noise Trader Contamination (NTC)

**Definition**: Correlation between NoiseTrader order volume and price deviation direction (should be near zero for true noise).

```python
import numpy as np

def noise_trader_contamination(noise_orders, deviations):
    directions = [1 if o["action"] == "buy" else -1 for o in noise_orders if o["action"] != "hold"]
    corr = np.corrcoef(directions, deviations[:len(directions)])[0, 1]
    return corr
```

**Interpretation**: |NTC| < 0.1 confirms noise trader randomness; higher values suggest simulation artifact.

**Reference**: Black (1986) noise trading model.

---

### §2.7 Wealth Redistribution Index (WRI)

**Definition**: Difference in terminal wealth between destabilizing agents (ProCyclicalLender + MinskyBorrower) and stabilizing agents (CounterCyclicalLender + ValueInvestor), normalized by initial wealth.

```python
def wealth_redistribution_index(agent_final_states, final_price, initial_wealth=100000):
    destabilizing = sum(
        s["cash"] + s["position"] * final_price
        for k, s in agent_final_states.items()
        if k in ["ProCyclicalLender", "MinskyBorrower"]
    )
    stabilizing = sum(
        s["cash"] + s["position"] * final_price
        for k, s in agent_final_states.items()
        if k in ["CounterCyclicalLender", "ValueInvestor"]
    )
    return (stabilizing - destabilizing) / (2 * initial_wealth)
```

**Interpretation**: WRI > 0 → stabilizers earn more (contrarian advantage); WRI < 0 → destabilizers profit from momentum.

**Reference**: Geanakoplos (2010) Section 4 — leverage cycle wealth dynamics.

## §3 Analysis Dimensions

| Dimension                | Primary Metric | Secondary Metrics      |
|--------------------------|----------------|------------------------|
| Credit cycle amplitude   | LAI (§2.1)     | CCS (§2.3), PDR (§2.5) |
| Minsky fragility         | MFS (§2.2)     | PDR (§2.5)             |
| Contraction dynamics     | CCS (§2.3)     | CCOR (§2.4)            |
| Stabilizer effectiveness | CCOR (§2.4)    | WRI (§2.7)             |
| Cycle shape              | PDR (§2.5)     | LAI (§2.1)             |
| Market quality           | NTC (§2.6)     | —                      |
| Wealth distribution      | WRI (§2.7)     | —                      |

## §4 Phase Analysis

### Expansion Phase (δ > 0.03)
- **Expected**: ProCyclicalLender buys at 2× order_size; MinskyBorrower buys when stable_rounds > 3.
- **Metrics**: LAI numerator builds; NTC should remain near zero; WRI may temporarily favor destabilizers.
- **Warning sign**: If ValueInvestor also buys (δ < +0.10), boom is moderate; if all three buy simultaneously, runaway expansion.

### Stability Plateau (|δ| < 0.02)
- **Expected**: MinskyBorrower accumulates stable_rounds; ProCyclicalLender inactive; all agents near-hold.
- **Metrics**: MFS accumulates; NTC should show cleanest noise signal.
- **Warning sign**: Prolonged plateau (>10 rounds) produces high MFS, predicts sharper eventual bust.

### Bust Onset (δ < −0.05)
- **Expected**: ProCyclicalLender and MinskyBorrower both sell; CounterCyclicalLender and ValueInvestor buy.
- **Metrics**: CCS measures bust speed; CCOR measures offset effectiveness.
- **Warning sign**: If CCOR < 0.3, price may overshoot below fundamental significantly.

### Recovery Phase (−0.10 < δ < −0.03)
- **Expected**: ValueInvestor active; CounterCyclicalLender buying; destabilizers reduced or stopped.
- **Metrics**: Recovery speed; WRI begins shifting toward stabilizers.

## §5 Cross-Variant Comparison

| Metric | Rule (Expected)                       | LLM (Expected)                                | RuleLLM (Expected)                                   | Rag (Expected)                                 |
|--------|---------------------------------------|-----------------------------------------------|------------------------------------------------------|------------------------------------------------|
| LAI    | Deterministic, depends on random seed | Variable — LLM may exhibit narrative momentum | Similar to Rule with narrative variation             | RAG context may sharpen Minsky cycle timing    |
| MFS    | Mechanically stable_rounds driven     | LLM may anticipate fragility, reduce buying   | Rule-anchored MinskyBorrower with LLM risk awareness | RAG may retrieve Minsky theory, alter leverage |
| CCS    | Fixed by parameters                   | Variable — LLM panic may accelerate           | Moderate — rule prevents runaway LLM panic           | RAG historical cases may calibrate bust speed  |
| CCOR   | Fixed ≈ 0.4–0.6                       | LLM may vary widely                           | Stable due to rule anchors                           | RAG may improve counter-cyclical timing        |
| WRI    | Near-zero (symmetric design)          | LLM narrative may favor either side           | Rule keeps symmetry                                  | RAG insights may benefit stabilizers           |

## §6 Expected Results

**Rule baseline**:
- 2–3 complete boom-bust cycles per 100-round simulation
- Peak deviation ≈ +8–15% during boom; trough ≈ −10–20% during bust
- CCOR ≈ 0.4–0.6; MFS ≈ 4–8 rounds
- WRI near-zero; CCS ≈ 0.5–1.5 price units/round

**LLM variant**:
- More variable cycle frequency; boom phases may extend via narrative momentum
- MinskyBorrower LLM may recognize fragility and reduce leverage earlier
- CCS may be higher if LLM agents exhibit panic behavior

**RuleLLM variant**:
- Rule anchors prevent extreme LLM deviations; cycle shape more predictable
- LLM commentary adds narrative richness without distorting mechanics

**Rag variant**:
- Retrieved credit cycle / Minsky theory may sharpen agent reasoning
- CounterCyclicalLender may deploy capital more precisely; ValueInvestor may refine discount thresholds

**Calibration targets**:
- LAI should be 1.0–2.0 (booms not dramatically longer than busts)
- PDR should be 1.5–3.0 (booms somewhat longer, busts sharper)
- NTC should be < 0.1 in all variants

## §7 Visualization Catalogue

| Output | Content | Purpose |
|---|---|---|
| `summary.json` | Total rounds, price extrema, deviation metrics, LAI, MFS, CCS, CCOR, PDR, max drawdown, volatility, autocorrelation, agent VWAP, validation result | Machine-readable Level-2 structural quality and scenario-validity summary |
| `00_investor_bids.png` | Investor bid/decision paths when bid fields are recorded | Headline agent behavior plot |
| `01_creditcycle_dynamics.png` | Price, fundamental, deviation, rolling volatility, and phase markers | Visualize boom-bust dynamics and phase timing |
| `02_creditcycle_analysis.png` | Scenario metric dashboard including LAI, MFS, CCS, CCOR, PDR, WRI, and validation score | Connect simulation outputs to §2 metrics |
| `03_summary.png` | Agent VWAP, total buy/sell volume, and terminal behavior summary | Cross-agent comparison for the final run |
| `rag_stats.json` | Rag only: retrieval success/failure counts by agent and aggregate retrieval failure rate | Verify that RAG decisions had inspectable knowledge context |
