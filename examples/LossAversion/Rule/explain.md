# LossAversion — Rule Variant Explanation

## §1 Overview

| Item               | Description                                                                                     |
|--------------------|-------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Prospect-theory loss aversion — investors sell winners too early and hold losers too long       |
| **Variant**        | Rule-based: all agents use deterministic thresholds derived from Kahneman & Tversky (1979)      |
| **Investor Count** | 5 classes: LossAverseInvestor, BreakEvenTrader, RationalTrader, MomentumTrader, MarketMaker     |
| **Key Feature**    | Loss-aversion coefficient λ = 2.25 encoded directly in sell-threshold asymmetry                 |
| **Academic Value** | Produces disposition effect (PGR > PLR), break-even escalation, and measurable wealth penalties |

---

## §2 Theory → Implementation Mapping

### §2.1 LossAverseInvestor (simulation-bases.md §4.1)

Implements Kahneman & Tversky (1979) Prospect Theory value function asymmetry.

| Theory Element                     | Rule Implementation                                                    |
|------------------------------------|------------------------------------------------------------------------|
| Loss-aversion coefficient λ = 2.25 | `sell_gain_threshold × loss_aversion_lambda ≈ 0.1125` (loss threshold) |
| Concave gain region → sell winners | `if pnl_pct > sell_gain_threshold (0.05): sell 70% of position`        |
| Convex loss region → hold losers   | `elif pnl_pct < −0.1125: sell only 20% of position`                    |
| Reference point = entry price      | `entry_price` updated only on purchases                                |

Activation threshold: `pnl_pct > 0.05` (gain) or `pnl_pct < −0.1125` (loss).
Key formula: `sell_qty_gain = min(position, int(position × 0.7))`, `sell_qty_loss = min(position, int(position × 0.2))`.

### §2.2 BreakEvenTrader (simulation-bases.md §4.2)

Implements CPT break-even effect (Tversky & Kahneman 1992; Barberis & Xiong 2009).

| Theory Element                    | Rule Implementation                 |
|-----------------------------------|-------------------------------------|
| Convex loss domain → risk-seeking | Activates at `pnl_pct < −0.05`      |
| Escalating risk-taking            | `risky_qty = int(                   |
| Cash constraint                   | `min(risky_qty, int(cash / price))` |

Activation threshold: `pnl_pct < −0.05`.
Key formula: `risky_qty = min(int(|pnl_pct| × 2.0 × 5000), int(cash / price))`.

### §2.3 RationalTrader (simulation-bases.md §4.3)

Expected-utility arbitrageur providing rational benchmark.

| Theory Element                  | Rule Implementation                    |
|---------------------------------|----------------------------------------|
| Trade on significant mispricing | `if                                    |
| Proportional sizing             | `qty = min(500, int(                   |
| Direction                       | Buy if underpriced; sell if overpriced |

Activation threshold: `|deviation| > 0.03`.
Key formula: `qty = min(500, int(|deviation| × 0.5 × 3000))`.

### §2.4 MomentumTrader (simulation-bases.md §4.4)

Trend follower that reinforces existing price direction.

| Theory Element               | Rule Implementation                                 |
|------------------------------|-----------------------------------------------------|
| Enter trends above threshold | `if                                                 |
| Follow direction             | Buy when `deviation > 0`; sell when `deviation < 0` |
| Proportional sizing          | `qty = min(500, int(                                |

Activation threshold: `|deviation| > 0.02`.
Key formula: `qty = min(500, int(|deviation| × 3000))`.

### §2.5 MarketMaker (simulation-bases.md §4.5)

Contrarian liquidity provider earning emergent bid-ask spread.

| Theory Element                      | Rule Implementation                             |
|-------------------------------------|-------------------------------------------------|
| Inventory-constrained market making | `if                                             |
| Fixed round size                    | `qty = 300`                                     |
| Contrarian direction                | Sell if `deviation > 0`; buy if `deviation < 0` |

Key formula: `sell_qty = min(300, position)` or `buy_qty = min(300, int(cash/price))`.

---

## §3 Market Mechanism

Price formation (see simulation-bases.md §5):

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Order of operations each round:
1. Market broadcasts `{price, fundamental, deviation}` to all agents.
2. `LossAverseInvestor` computes `pnl_pct` from `entry_price`; checks gain/loss thresholds.
3. `BreakEvenTrader` computes `pnl_pct`; escalates buy if in loss domain.
4. `RationalTrader` and `MomentumTrader` check deviation magnitude.
5. `MarketMaker` provides contrarian order subject to inventory limit.
6. Market aggregates net demand, applies price impact, mean reversion, and noise.

Key dynamic: loss-averse selling of winners limits upward moves; refusal to sell losers limits downward correction → asymmetric price paths.

---

## §4 Variant Architecture

```
Rule Variant Architecture
─────────────────────────
Market (rule-based)
  │  broadcast {price, fundamental, deviation}
  ├─ LossAverseInvestor   │ λ=2.25 threshold logic
  ├─ BreakEvenTrader      │ break-even escalation
  ├─ RationalTrader       │ expected-utility arbitrage
  ├─ MomentumTrader       │ trend following
  └─ MarketMaker          │ contrarian liquidity
```

All agents are purely deterministic. No LLM calls. No external data sources.

---

## §5 Config Reference

Configuration file: `configs/LossAversion/Rule/simulation.yml` → `players.yml`

| Parameter              | Agent              | Default | Description                          |
|------------------------|--------------------|---------|--------------------------------------|
| `loss_aversion_lambda` | LossAverseInvestor | 2.25    | Loss multiplier                      |
| `sell_gain_threshold`  | LossAverseInvestor | 0.05    | Gain trigger for winner sale         |
| `risk_increase_factor` | BreakEvenTrader    | 2.0     | Escalation multiplier in loss domain |
| `risk_aversion`        | RationalTrader     | 0.5     | EU risk weight                       |
| `entry_threshold`      | MomentumTrader     | 0.03    | Minimum trend to follow              |
| `inventory_limit`      | MarketMaker        | 2000    | Max absolute inventory               |
| `initial_cash`         | All investors      | 100000  | Starting cash                        |
| `initial_position`     | All investors      | 500     | Starting shares                      |
| `initial_price`        | All                | 100.0   | Entry price reference                |
| `price_impact`         | Market             | 0.0002  | λ coefficient                        |
| `mean_reversion`       | Market             | 0.05    | γ coefficient                        |
| `noise_std`            | Market             | 0.3     | ε standard deviation                 |

---

## §6 Running Instructions

```bash
# Run Rule variant
python examples/LossAversion/Rule/run_lossaversion.py \
    -c configs/LossAversion/Rule/simulation.yml

# Run with custom lambda
python examples/LossAversion/Rule/run_lossaversion.py \
    -c configs/LossAversion/Rule/simulation.yml \
    --extras loss_aversion_lambda=3.0
```

Output files written to `records/LossAversion/Rule/`:
- `price/` — price history per round
- `trades/` — order records per agent per round
- `wealth/` — terminal wealth summary

---

## §7 Expected Behavior

| Metric                         | Expected Range | Rationale                                                |
|--------------------------------|----------------|----------------------------------------------------------|
| LAI (Loss Aversion Index)      | 2.0–2.8        | Directly set by `loss_aversion_lambda = 2.25`            |
| DEI (Disposition Effect Index) | 1.5–2.5        | 70%/20% sell ratio → PGR ≫ PLR                           |
| BER (Break-Even Escalation)    | 1.5–3.5        | Escalating buys at pnl < –5%                             |
| VAF (Volatility Impact Ratio)  | 0.1–2.5        | Values below one show counter-cyclical moderation; values above one show amplification |
| WPI (Wealth Penalty Index)     | 0.75–0.90      | Biased agents underperform rational by 10–25%            |
| SRR (Sell Rate Ratio)          | 1.5–2.5        | Sell rate 1.5–2.5× higher in gain rounds                 |

The Rule variant produces the strongest and most mechanically consistent expression of all metrics — it is the baseline against which LLM, RuleLLM, and Rag variants are compared.

---

## §8 References

- Kahneman, D., & Tversky, A. (1979). Prospect Theory. *Econometrica*, 47(2), 263–291. doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Tversky, A., & Kahneman, D. (1992). Cumulative Prospect Theory. *Journal of Risk and Uncertainty*, 5(4), 297–323. doi:[10.1007/BF00122574](https://doi.org/10.1007/BF00122574)
- Shefrin, H., & Statman, M. (1985). The Disposition to Sell Winners Too Early and Ride Losers Too Long. *Journal of Finance*, 40(3), 777–790. doi:[10.1111/j.1540-6261.1985.tb05002.x](https://doi.org/10.1111/j.1540-6261.1985.tb05002.x)
- Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775–1798. doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). What Drives the Disposition Effect? *Journal of Finance*, 64(2), 751–784. doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)

---

## §9 Variant Comparison

| Dimension              | Rule                   | LLM                 | RuleLLM                 | Rag              |
|------------------------|------------------------|---------------------|-------------------------|------------------|
| Loss-aversion encoding | Deterministic λ = 2.25 | LLM narrative       | Rule + LLM confirmation | Rule + KB papers |
| Break-even effect      | Fixed formula          | LLM may moderate    | Rule-triggered          | RAG may reduce   |
| Expected LAI           | 2.0–2.8                | 1.6–2.4             | 1.8–2.5                 | 1.4–2.0          |
| Expected WPI           | 0.75–0.90              | 0.80–0.93           | 0.78–0.92               | 0.85–0.95        |
| Stochasticity          | Minimal (noise only)   | High (LLM variance) | Moderate                | Moderate         |
