# ConfirmationBias Rule Variant — Design Specification

## §1 Overview

| Item               | Detail                                                                                                                              |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Confirmation bias: traders seek and overweight evidence confirming their existing beliefs, producing persistent price mispricing    |
| **Variant**        | Rule — fully deterministic algorithmic agents, no LLM calls                                                                         |
| **Rounds**         | 200 (configurable)                                                                                                                  |
| **Market**         | Asset price with net-demand + mean-reversion dynamics                                                                               |
| **Key Feature**    | BeliefAnchor's internal state variable compounds confirming signals; SelectiveScanner's asymmetric response creates persistent bias |
| **Academic Basis** | Nickerson (1998); Lord, Ross & Lepper (1979); Rabin & Schrag (1999)                                                                 |

---

## §2 Theory → Implementation Mapping

| Theoretical Concept                               | Agent / Mechanism                                                      | Code Location                                |
|---------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------|
| Belief anchoring (`simulation-bases.md §4.1`)     | `BeliefAnchor` — internal belief state; overweights confirming signals | `Rule/players.py: BeliefAnchor.decide()`     |
| Biased assimilation (`simulation-bases.md §4.2`)  | `SelectiveScanner` — full buy on confirm, half sell on disconfirm      | `Rule/players.py: SelectiveScanner.decide()` |
| Bayesian rational baseline (`simulation-bases.md §4.3`) | `BalancedAnalyst` — equal weight both signals; mean-reverts            | `Rule/players.py: BalancedAnalyst.decide()`  |
| Contrarian exploitation (`simulation-bases.md §4.4`) | `ContrarianTrader` — fades biased consensus                            | `Rule/players.py: ContrarianTrader.decide()` |
| Noise trader liquidity (`simulation-bases.md §4.5`) | `NoiseTrader` — random Uniform[100, 500]                               | `Rule/players.py: NoiseTrader.decide()`      |
| Price impact + mean reversion (`simulation-bases.md §3.1`) | Market clearing formula                                                | `Rule/players.py: Market.perceive()`         |

### §2.1 BeliefAnchor (`simulation-bases.md §4.1`)

| Theory Component | Implementation |
|---|---|
| Persistent prior belief | `BeliefAnchor` stores and updates `belief` across rounds. |
| Confirmatory updating | Confirming deviation multiplies belief; disconfirming deviation decays it slowly. |

### §2.2 SelectiveScanner (`simulation-bases.md §4.2`)

| Theory Component | Implementation |
|---|---|
| Selective information processing | Buys full size on confirming positive deviation and sells half size on disconfirming negative deviation. |

### §2.3 BalancedAnalyst (`simulation-bases.md §4.3`)

| Theory Component | Implementation |
|---|---|
| Rational evidence weighting | Trades symmetrically around the fundamental value when `|deviation| > 0.05`. |

### §2.4 ContrarianTrader (`simulation-bases.md §4.4`)

| Theory Component | Implementation |
|---|---|
| Bias correction | Fades overvaluation and undervaluation once the deviation exceeds the contrarian threshold. |

### §2.5 NoiseTrader (`simulation-bases.md §4.5`)

| Theory Component | Implementation |
|---|---|
| Noise liquidity | Trades randomly with probability 0.30 and quantity from 100 to 500 shares. |

---

## §3 Market Mechanism

### 3.1 Price Update Formula

```
P(t+1) = P(t) + λ·D(t) + γ·(F − P(t)) + ε(t)
```

| Symbol | Parameter                       | Value               |
|--------|---------------------------------|---------------------|
| λ      | `price_impact`                  | 0.02                |
| D(t)   | net_demand = buy_vol − sell_vol | computed each round |
| γ      | `mean_reversion`                | 0.02                |
| F      | `fundamental_value`             | 100.0               |
| ε(t)   | noise ~ N(0, noise_std)         | noise_std = 0.02    |

### 3.2 Market Broadcast

Each round the Market agent broadcasts to all traders:

```python
{
    "price":       float,   # current asset price
    "fundamental": float,   # intrinsic value (constant = 100.0)
    "deviation":   float,   # (price - fundamental) / fundamental
    "round":       int,
}
```

> Note: `return_pct` is **NOT** broadcast. All agent rules use only `deviation`.

### 3.3 Deviation Definition

```
deviation = (price − fundamental) / fundamental
```

- Positive: price above fundamental → bullish bias dominant
- Negative: price below fundamental → bearish bias or correction

---

## §4 Variant-Specific Features

### 4.1 BeliefAnchor Internal State

The defining feature of ConfirmationBias: `BeliefAnchor` maintains a persistent
`belief` variable that compounds when signals confirm the current direction.

```python
# Confirming signal: belief amplified
if deviation > 0 and belief > 0:
    belief = min(belief * (1 + 0.7 * deviation), 3.0)

# Disconfirming signal: slow decay
else:
    belief = belief * 0.95 + deviation * 0.5

# Trade trigger
if belief > 0.5:  → buy order_size=500
elif belief < -0.5: → sell order_size=500
```

### 4.2 SelectiveScanner Asymmetric Response

```python
scan_threshold = 0.02
# Full buy on confirming bullish signal
if deviation > 0.02 and position >= 0:
    buy order_size=600

# Half sell on disconfirming signal (asymmetric!)
elif deviation < -0.02 and position >= 0:
    sell order_size//2 = 300
```

| Scenario                         | Signal        | Response                |
|----------------------------------|---------------|-------------------------|
| Bullish position + rising price  | Confirming    | Full buy (600 units)    |
| Bullish position + falling price | Disconfirming | Half sell (300 units)   |
| Result                           | —             | Asymmetric accumulation |

### 4.3 Agent Summary Table

| Agent              | Role          | Trigger                   | Quantity          |
|--------------------|---------------|---------------------------|-------------------|
| `BeliefAnchor`     | Destabilizing | `belief > 0.5` / `< -0.5` | 500               |
| `SelectiveScanner` | Destabilizing | `deviation > 0.02` / `< -0.02` | 600 / 300         |
| `BalancedAnalyst`  | Stabilizing   | `|deviation| > 0.05`      | 400               |
| `ContrarianTrader` | Stabilizing   | `|deviation| > 0.05`      | 500               |
| `NoiseTrader`      | Neutral       | p=0.30                    | Uniform[100, 500] |

---

## §5 Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                  Market (Asset)                       │
│  P(t+1) = P(t) + λ·D + γ·(F−P) + ε                  │
│  broadcasts: {price, fundamental, deviation, round}   │
└──────────────────────┬───────────────────────────────┘
                       │  market_update (star topology)
          ┌────────────┼────────────────────┐
          │            │                    │
   ┌──────▼──────┐ ┌───▼─────────────┐ ┌───▼──────────────┐
   │BeliefAnchor │ │SelectiveScanner │ │BalancedAnalyst   │
   │(dest.)      │ │(dest.)          │ │(stab.)           │
   │belief state │ │asymmetric scan  │ │rational Bayesian │
   │c_str=0.7    │ │thr=0.02         │ │thr=0.05          │
   └─────────────┘ └─────────────────┘ └──────────────────┘
          │
   ┌──────▼──────┐ ┌──────────────┐
   │Contrarian   │ │NoiseTrader   │
   │Trader(stab.)│ │(neutral)     │
   │thr=0.05     │ │p=0.30        │
   └─────────────┘ └──────────────┘
          │  all agents send order → Market
```

---

## §6 Configuration Reference

From `configs/ConfirmationBias/Rule/players.yml`:

### Market

| Parameter           | Value | Description          |
|---------------------|-------|----------------------|
| `initial_price`     | 100.0 | Starting asset price |
| `fundamental_value` | 100.0 | Intrinsic value      |
| `price_impact`      | 0.02  | λ in price formula   |
| `mean_reversion`    | 0.02  | γ in price formula   |
| `noise_std`         | 0.02  | ε std deviation      |

### BeliefAnchor

| Parameter               | Value | Description                     |
|-------------------------|-------|---------------------------------|
| `confirmation_strength` | 0.7   | Belief amplification multiplier |
| `order_size`            | 500   | Trade quantity per signal       |
| `initial_belief`        | 1.0   | Starting belief (bullish)       |

### SelectiveScanner

| Parameter        | Value | Description                         |
|------------------|-------|-------------------------------------|
| `scan_threshold` | 0.02  | Minimum deviation to trigger action |
| `order_size`     | 600   | Full buy quantity (sell = 300)      |

### BalancedAnalyst

| Parameter            | Value | Description       |
|----------------------|-------|-------------------|
| `analysis_threshold` | 0.05  | Trigger threshold |
| `order_size`         | 400   | Trade quantity    |

### ContrarianTrader

| Parameter              | Value | Description       |
|------------------------|-------|-------------------|
| `contrarian_threshold` | 0.05  | Trigger threshold |
| `order_size`           | 500   | Trade quantity    |

### NoiseTrader

| Parameter           | Value | Description      |
|---------------------|-------|------------------|
| `trade_probability` | 0.30  | Trade each round |

---

## §7 Running Instructions

```bash
# Run simulation
python examples/ConfirmationBias/Rule/run_confirmationbias_rule.py \
    -c configs/ConfirmationBias/Rule/simulation.yml

# Analyze results
python examples/ConfirmationBias/Rule/analysis.py \
    -c configs/ConfirmationBias/Rule/simulation.yml
```

Output: `EXPERIMENT/ConfirmationBias/Rule/records/`

---

## §8 Expected Behavior

### Phase 1: Bias Establishment (rounds 1–~30)

- Initial belief = 1.0 → BeliefAnchor buys immediately
- Small positive deviations confirm belief → belief compounds
- SelectiveScanner joins buying (deviation > 0.02)
- Price rises above fundamental; deviation reaches 2–5%

### Phase 2: Persistent Mispricing (~round 30–150)

- BeliefAnchor belief saturates at 3.0 (max cap) → consistent 500-unit buys
- SelectiveScanner continues full buys; half sells on dips
- BalancedAnalyst and ContrarianTrader sell at deviation > 5%
- Dynamic equilibrium: biased agents push up; stabilizers dampen
- Deviation persists at 2–8%

### Phase 3: Potential Correction (variable)

- Mean-reversion force γ builds over time
- If noise generates negative deviation: BeliefAnchor belief starts decaying
- If belief drops below 0.5: BeliefAnchor stops buying → price corrects
- correction_ratio measures how much of peak bias is resolved

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Confirmation bias / selective processing → `simulation-bases.md §2.1, §4 — BeliefAnchor`
- Biased assimilation → `simulation-bases.md §2.2, §4 — SelectiveScanner`
- Formal model of confirmatory bias → `simulation-bases.md §2.3, §4 — BeliefAnchor`
- Contrarianism and rational updating → `simulation-bases.md §2.4, §4 — BalancedAnalyst, ContrarianTrader`
- Noise trader theory → `simulation-bases.md §2.5, §4 — NoiseTrader`
- Price formula → `simulation-bases.md §3.1`
- Full parameter table with source citations → `simulation-bases.md §6`
