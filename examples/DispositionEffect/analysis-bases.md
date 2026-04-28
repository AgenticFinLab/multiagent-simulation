# DispositionEffect Analysis Bases

## §1 Objectives

1. **Reproduce Odean PGR/PLR**: Confirm PGR > PLR with ratio ≈ 1.5 matching Odean (1998) empirical benchmark.
2. **Measure disposition coefficient**: Quantify DC = PGR − PLR; DC > 0 confirms disposition effect present.
3. **Isolate loss aversion**: Compare holding periods for winners vs. losers across investor types.
4. **Evaluate performance drag**: Measure return difference between DispositionInvestor and RationalInvestor.
5. **Cross-variant comparison**: Assess whether LLM/Rag agents exhibit stronger or weaker disposition effect than Rule baseline.

## §2 Core Metrics

### §2.1 Proportion of Gains Realized (PGR)

**Definition**: Fraction of potential gain realizations that are actually taken (Odean, 1998).

```python
def proportion_of_gains_realized(trades, price_history, purchase_prices):
    realized_gains = 0
    paper_gains = 0
    for t, trade in enumerate(trades):
        price = price_history[t]
        gain_loss = (price - purchase_prices[t]) / purchase_prices[t] if purchase_prices[t] > 0 else 0
        if gain_loss > 0:
            if trade["action"] == "sell":
                realized_gains += 1
            else:
                paper_gains += 1
    return realized_gains / (realized_gains + paper_gains) if (realized_gains + paper_gains) > 0 else 0.0
```

**Interpretation**: PGR ≈ 0.148 matches Odean (1998); PGR > PLR confirms disposition effect.

**Reference**: Odean (1998) — DOI: https://doi.org/10.1111/0022-1082.00078

---

### §2.2 Proportion of Losses Realized (PLR)

**Definition**: Fraction of potential loss realizations that are actually taken.

```python
def proportion_of_losses_realized(trades, price_history, purchase_prices):
    realized_losses = 0
    paper_losses = 0
    for t, trade in enumerate(trades):
        price = price_history[t]
        gain_loss = (price - purchase_prices[t]) / purchase_prices[t] if purchase_prices[t] > 0 else 0
        if gain_loss < 0:
            if trade["action"] == "sell":
                realized_losses += 1
            else:
                paper_losses += 1
    return realized_losses / (realized_losses + paper_losses) if (realized_losses + paper_losses) > 0 else 0.0
```

**Interpretation**: PLR ≈ 0.098 matches Odean (1998); PLR < PGR confirms reluctance to realize losses.

**Reference**: Odean (1998) — DOI: https://doi.org/10.1111/0022-1082.00078

---

### §2.3 Disposition Coefficient (DC)

**Definition**: Signed measure of disposition strength.

```python
def disposition_coefficient(pgr, plr):
    return pgr - plr
```

**Interpretation**: DC > 0 → disposition effect present; DC ≈ 0.05 (empirical from Odean 1998); DC < 0 → anti-disposition (tax-harvesting behavior).

**Reference**: Shefrin & Statman (1985) — DOI: https://doi.org/10.1111/j.1540-6261.1985.tb05002.x

---

### §2.4 PGR/PLR Ratio

**Definition**: Relative frequency of gain vs. loss realization.

```python
def pgr_plr_ratio(pgr, plr):
    return pgr / plr if plr > 0 else float('inf')
```

**Interpretation**: Ratio ≈ 1.5 (Odean 1998 benchmark); ratio > 1.5 indicates strong disposition; ratio < 1 indicates anti-disposition.

**Reference**: Odean (1998) — DOI: https://doi.org/10.1111/0022-1082.00078

---

### §2.5 Holding Period Asymmetry (HPA)

**Definition**: Ratio of average holding rounds for losers vs. winners sold.

```python
def holding_period_asymmetry(sell_events):
    winner_holds = [e["rounds_held"] for e in sell_events if e["gain_loss_at_sale"] > 0]
    loser_holds = [e["rounds_held"] for e in sell_events if e["gain_loss_at_sale"] < 0]
    avg_winner = sum(winner_holds) / len(winner_holds) if winner_holds else 0
    avg_loser = sum(loser_holds) / len(loser_holds) if loser_holds else 0
    return avg_loser / avg_winner if avg_winner > 0 else 0.0
```

**Interpretation**: HPA > 1 → losers held longer than winners (core disposition behavior); HPA ≈ 1.5–2.0 expected for DispositionInvestor.

**Reference**: Odean (1998) Table III — average holding periods.

---

### §2.6 Performance Drag Index (PDI)

**Definition**: Terminal wealth of DispositionInvestor relative to RationalInvestor, normalized.

```python
def performance_drag_index(disposition_final_wealth, rational_final_wealth):
    return (rational_final_wealth - disposition_final_wealth) / rational_final_wealth
```

**Interpretation**: PDI > 0 → DispositionInvestor underperforms; PDI ≈ 0.03–0.06 (3–6% drag) expected from empirical evidence.

**Reference**: Odean (1998) — annual return drag of 3.2% for individual investors with disposition bias.

---

### §2.7 Tax Reversal Index (TRI)

**Definition**: PLR of TaxAwareInvestor relative to DispositionInvestor PLR — measures anti-disposition strength.

```python
def tax_reversal_index(tax_plr, disposition_plr):
    return tax_plr / disposition_plr if disposition_plr > 0 else 0.0
```

**Interpretation**: TRI > 1 → TaxAwareInvestor realizes losses more readily; TRI ≈ 2–3 expected (deliberate tax harvesting vs. reluctant realization).

**Reference**: Constantinides (1983) tax-loss harvesting — DOI: https://doi.org/10.1086/261210

---

## §3 Analysis Dimensions

| Dimension            | Primary Metric | Secondary Metrics    |
|----------------------|----------------|----------------------|
| Disposition strength | DC (§2.3)      | PGR/PLR ratio (§2.4) |
| Gain realization     | PGR (§2.1)     | HPA (§2.5)           |
| Loss realization     | PLR (§2.2)     | HPA (§2.5)           |
| Holding behavior     | HPA (§2.5)     | DC (§2.3)            |
| Performance impact   | PDI (§2.6)     | PGR/PLR (§2.4)       |
| Tax strategy         | TRI (§2.7)     | PLR (§2.2)           |

## §4 Phase Analysis

### Gain Phase (gain_loss > gain_threshold)

- **DispositionInvestor**: Sells 50% of position immediately → PGR increases
- **RationalInvestor**: May hold if target allocation not exceeded
- **TaxAwareInvestor**: Holds (defers capital gains)
- **InstitutionalInvestor**: Sells symmetrically at wider threshold (8%)

### Loss Phase (gain_loss < loss_threshold)

- **DispositionInvestor**: Holds 85% of position — reluctant realization → PLR low
- **RationalInvestor**: Rebalances toward target allocation
- **TaxAwareInvestor**: Sells for tax loss harvesting → PLR elevated
- **InstitutionalInvestor**: Cuts loss symmetrically at −8%

### Near Reference Point (|gain_loss| < 1%)

- **DispositionInvestor**: Adds to position at perceived "fair value"
- Other investors: No special behavior at reference point

## §5 Cross-Variant Comparison

| Metric | Rule (Expected)            | LLM (Expected)                                  | RuleLLM (Expected)       | Rag (Expected)                         |
|--------|----------------------------|-------------------------------------------------|--------------------------|----------------------------------------|
| PGR    | ≈ 0.148 (Odean calibrated) | Variable; may be higher (emotional eagerness)   | Close to Rule            | RAG may moderate eagerness             |
| PLR    | ≈ 0.098 (Odean calibrated) | Variable; may be lower (stronger loss aversion) | Close to Rule            | RAG prospect theory may reinforce bias |
| DC     | ≈ 0.05                     | Potentially wider range                         | Narrow range around Rule | Moderate                               |
| HPA    | ≈ 1.5–2.0                  | May exceed 2.0 (LLM "can't bear to sell")       | Similar to Rule          | Moderated by historical evidence       |
| PDI    | ≈ 0.03–0.05                | Higher variance                                 | Similar to Rule          | May be lower (informed decisions)      |

## §6 Expected Results

**Rule baseline**:
- PGR ≈ 0.10–0.20 (calibrated to Odean 1998)
- PLR ≈ 0.06–0.12
- PGR/PLR ratio ≈ 1.4–1.7
- DC ≈ 0.03–0.07
- HPA ≈ 1.5–2.5 for DispositionInvestor

**Calibration targets** (from Odean 1998):
- PGR/PLR: 1.4–1.7
- PDI: 0.03–0.06 (3–6% performance drag)
- TRI: 2.0–4.0 (TaxAwareInvestor PLR >> DispositionInvestor PLR)

## §7 Visualization Catalogue

| Chart                                      | X-axis              | Y-axis          | Purpose                           |
|--------------------------------------------|---------------------|-----------------|-----------------------------------|
| Price trajectory with reference zones      | Round               | Price           | Gain/loss state visualization     |
| PGR vs. PLR over time                      | Round               | Proportion      | Disposition strength evolution    |
| Investor type wealth comparison            | Investor type       | Terminal wealth | Performance drag measurement      |
| Gain/loss at sale histogram                | gain_loss % at sale | Count           | Sell distribution asymmetry       |
| Holding period box plot                    | Investor type       | Rounds held     | HPA visualization                 |
| PGR/PLR ratio by variant                   | Variant             | PGR/PLR ratio   | Cross-variant comparison          |
| DC distribution                            | Simulation run      | DC value        | Disposition coefficient stability |
| Tax reversal: TaxAware vs. Disposition PLR | Variant             | PLR             | Anti-disposition effect           |
