# CurrencyCrisis Analysis Bases

## §1 Objectives

1. **Test self-fulfilling dynamics**: Confirm that currency crises emerge from expectation coordination, not only from fundamental weakness.
2. **Measure attack intensity**: Quantify how fast and deep speculative attacks drive the exchange rate below the peg.
3. **Evaluate defense effectiveness**: Assess how long CentralBankDefender can sustain the peg before reserves are exhausted.
4. **Isolate expectation channel**: Compare crisis depth with/without SelfFulfillingTrader to isolate the coordination channel.
5. **Cross-variant comparison**: Assess whether LLM agents exhibit richer crisis-belief dynamics than rule-based equivalents.

## §2 Core Metrics

### §2.1 Attack Intensity Index (AII)

**Definition**: Maximum negative deviation from peg during crisis phase, normalized by fundamental value.

```python
def attack_intensity_index(price_history, fundamental):
    deviations = [(p - fundamental) / fundamental for p in price_history]
    return abs(min(deviations))
```

**Interpretation**: AII > 0.15 signals severe attack; AII < 0.05 signals repelled attack.

**Reference**: Eichengreen, Rose & Wyplosz (1995) Exchange Market Pressure index — DOI: https://doi.org/10.2307/1344591

---

### §2.2 Peg Survival Duration (PSD)

**Definition**: Number of rounds the exchange rate remains within ±5% of peg (δ > −0.05) before the first breach.

```python
def peg_survival_duration(price_history, fundamental, breach_threshold=-0.05):
    for t, p in enumerate(price_history):
        if (p - fundamental) / fundamental < breach_threshold:
            return t
    return len(price_history)  # peg survived entire simulation
```

**Interpretation**: Longer PSD → more effective defense; PSD = full simulation length → peg held.

**Reference**: Obstfeld (1996) second-generation model — DOI: https://doi.org/10.1016/0014-2921(95)00111-5

---

### §2.3 Defense Exhaustion Rate (DER)

**Definition**: Rate at which CentralBankDefender depletes reserves (cash), measured as fraction of initial_cash consumed per crisis round.

```python
def defense_exhaustion_rate(defender_cash_history, initial_cash, crisis_rounds):
    cash_spent = initial_cash - defender_cash_history[-1]
    return cash_spent / (initial_cash * len(crisis_rounds)) if crisis_rounds else 0.0
```

**Interpretation**: DER > 0.5 per round → reserves exhausted quickly; historical crises often exhibit rapid exhaustion.

**Reference**: Krugman (1979) reserve depletion model — DOI: https://doi.org/10.2307/1991793

---

### §2.4 Self-Fulfilling Amplification Factor (SFAF)

**Definition**: Ratio of SelfFulfillingTrader sell volume to SpeculativeAttacker sell volume during attack phase.

```python
def self_fulfilling_amplification_factor(agent_volume_by_type):
    attacker_sells = agent_volume_by_type["SpeculativeAttacker"]["sell"]
    sft_sells = agent_volume_by_type["SelfFulfillingTrader"]["sell"]
    return sft_sells / attacker_sells if attacker_sells > 0 else 0.0
```

**Interpretation**: SFAF > 1 → expectation channel amplifies beyond initial speculative attack; core Obstfeld mechanism.

**Reference**: Obstfeld (1996) multiple-equilibria currency crisis — DOI: https://doi.org/10.1016/0014-2921(95)00111-5

---

### §2.5 Fundamental Anchor Strength (FAS)

**Definition**: Fraction of attack-phase rounds where FundamentalHedger provides counter-buying at the exact attack price.

```python
def fundamental_anchor_strength(hedger_orders, attack_phase_rounds):
    hedge_buys = sum(1 for o in hedger_orders
                    if o["round"] in attack_phase_rounds and o["action"] == "buy")
    return hedge_buys / len(attack_phase_rounds) if attack_phase_rounds else 0.0
```

**Interpretation**: FAS = 1.0 → FundamentalHedger active every attack round; FAS < 0.5 → anchor weak.

**Reference**: Morris & Shin (1998) global games — stable currency with sound fundamentals — https://www.jstor.org/stable/116850

---

### §2.6 Recovery Speed (RS)

**Definition**: Rounds required for price to recover from trough back to within ±3% of peg.

```python
def recovery_speed(price_history, fundamental, recovery_threshold=0.03):
    trough_idx = price_history.index(min(price_history))
    for t in range(trough_idx, len(price_history)):
        if abs((price_history[t] - fundamental) / fundamental) < recovery_threshold:
            return t - trough_idx
    return len(price_history) - trough_idx  # no recovery
```

**Interpretation**: Shorter RS → quick peg restoration; longer RS → persistent depreciation.

**Reference**: Calvo & Mendoza (2000) emerging market crisis recovery — DOI: https://doi.org/10.1257/aer.90.2.59

---

### §2.7 Wealth Transfer Index (WTI)

**Definition**: Terminal wealth of SpeculativeAttacker + SelfFulfillingTrader minus terminal wealth of CentralBankDefender + FundamentalHedger, normalized by total initial wealth.

```python
def wealth_transfer_index(agent_final_states, final_price, initial_wealth=100000):
    attackers = sum(
        s["cash"] + s["position"] * final_price
        for k, s in agent_final_states.items()
        if k in ["SpeculativeAttacker", "SelfFulfillingTrader"]
    )
    defenders = sum(
        s["cash"] + s["position"] * final_price
        for k, s in agent_final_states.items()
        if k in ["CentralBankDefender", "FundamentalHedger"]
    )
    return (attackers - defenders) / (2 * initial_wealth)
```

**Interpretation**: WTI > 0 → speculators profit (attack succeeded); WTI < 0 → defenders profit (attack repelled).

**Reference**: Eichengreen et al. (1995) — crisis profitability for currency speculators.

## §3 Analysis Dimensions

| Dimension           | Primary Metric | Secondary Metrics |
|---------------------|----------------|-------------------|
| Attack depth        | AII (§2.1)     | SFAF (§2.4)       |
| Defense duration    | PSD (§2.2)     | DER (§2.3)        |
| Reserve capacity    | DER (§2.3)     | WTI (§2.7)        |
| Expectation channel | SFAF (§2.4)    | AII (§2.1)        |
| Fundamental anchor  | FAS (§2.5)     | RS (§2.6)         |
| Recovery dynamics   | RS (§2.6)      | PSD (§2.2)        |
| Wealth outcomes     | WTI (§2.7)     | —                 |

## §4 Phase Analysis

### Pre-Attack Phase (|δ| < 0.03)
- **Expected**: All agents relatively inactive; noise trader provides baseline liquidity.
- **Metrics**: FAS = 0 (threshold not triggered); SFAF not yet meaningful.

### Attack Phase (−0.10 < δ < −0.03)
- **Expected**: SpeculativeAttacker sells; SelfFulfillingTrader follows with momentum; CentralBankDefender buys.
- **Metrics**: AII builds; DER accelerates; FAS tracks FundamentalHedger activation.
- **Warning sign**: If SFAF > 2, self-fulfilling channel dominates; peg at high risk.

### Crisis Phase (δ < −0.10)
- **Expected**: Emergency defense at 1,000 units; SpeculativeAttacker scales attack.
- **Metrics**: PSD recorded; AII peaks; DER at maximum.
- **Warning sign**: DER > 0.8 per round → reserves nearly exhausted → peg collapse imminent.

### Recovery or Collapse (δ > −0.05 or persistent δ < −0.15)
- **Recovery**: RS measured; WTI swings toward defenders.
- **Collapse**: WTI positive (speculators profited); peg permanently abandoned.

## §5 Cross-Variant Comparison

| Metric | Rule (Expected)              | LLM (Expected)                         | RuleLLM (Expected)                   | Rag (Expected)                             |
|--------|------------------------------|----------------------------------------|--------------------------------------|--------------------------------------------|
| AII    | Deterministic; ≈ 0.12–0.25   | Variable; LLM panic may worsen         | Close to Rule; rule-anchored defense | RAG historical cases may moderate          |
| PSD    | Fixed by parameters          | LLM defense may be adaptive            | Rule-anchored PSD                    | RAG informs defense timing                 |
| SFAF   | Mechanical momentum-based    | LLM may coordinate beliefs more        | Rule-triggered SFAF                  | RAG may reduce SFAF (historical awareness) |
| FAS    | Fixed threshold activation   | LLM may vary fundamental commitment    | Rule-anchored FAS                    | RAG PPP/fundamental knowledge improves FAS |
| WTI    | Near-zero (symmetric design) | LLM variable; attacker LLMs may profit | Close to zero (rule symmetry)        | RAG may favor defenders                    |

## §6 Expected Results

**Rule baseline**:
- AII ≈ 0.12–0.20 (crisis reaches −12% to −20% below peg)
- PSD ≈ 15–30 rounds
- SFAF ≈ 0.6–0.9 (SelfFulfillingTrader adds but doesn't dominate)
- FAS ≈ 0.5–0.8 (FundamentalHedger active during most attack rounds)
- WTI near-zero; RS ≈ 10–25 rounds

**LLM variant**:
- Higher AII variance; panic-LLM agents may deepen crisis
- SelfFulfillingTrader LLM may exhibit richer coordination behavior
- Central bank LLM defense may be more adaptive

**Calibration targets**:
- AII: 0.10–0.25 (realistic currency crash range)
- DER: < 0.3 per round (reserves last at least 3–4 rounds of crisis)
- SFAF: 0.5–1.5 (amplification without total domination)

## §7 Visualization Catalogue

| Chart                     | X-axis              | Y-axis                   | Purpose                            |
|---------------------------|---------------------|--------------------------|------------------------------------|
| Exchange rate trajectory  | Round               | Price                    | Visualize peg defense and collapse |
| Deviation heatmap         | Round               | δ(t)                     | Crisis phase identification        |
| Attack vs. defense volume | Round               | Buy/sell volume by agent | Attribution during crisis          |
| AII distribution          | Simulation run      | AII value                | Cross-variant comparison           |
| Reserve depletion curve   | Round (crisis only) | Defender cash            | DER dynamics                       |
| SFAF by attack event      | Attack ID           | SFAF value               | Self-fulfilling amplification      |
| Recovery path             | Round (post-trough) | Price                    | RS measurement                     |
| WTI box plot              | Variant             | WTI distribution         | Wealth transfer across variants    |
