# LossAversion — RuleLLM Variant Explanation

## §1 Overview

| Item               | Description                                                                                                                    |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Prospect-theory loss aversion with hybrid rule-threshold + LLM narrative confirmation                                          |
| **Variant**        | RuleLLM: rule-based thresholds trigger trading signals; LLM provides narrative reasoning and final quantity modulation         |
| **Investor Count** | 5 hybrid classes mirroring Rule investor logic with LLM overlay                                                                |
| **Key Feature**    | Rule thresholds prevent LLM from overriding core loss-aversion logic; LLM moderates quantities within rule boundaries          |
| **Academic Value** | Tests whether anchored LLM reasoning produces more consistent bias expression than pure-LLM while adding narrative flexibility |

---

## §2 Theory → Implementation Mapping

### §2.1 RuleLLM LossAverseInvestor (simulation-bases.md §4.1)

| Theory Element         | RuleLLM Implementation                                                                                  |
|------------------------|---------------------------------------------------------------------------------------------------------|
| Loss-aversion λ = 2.25 | Rule threshold computes gain/loss triggers; LLM confirms and may adjust quantity within bounds          |
| Disposition effect     | Rule enforces `pnl_pct > 0.05` → sell; `pnl_pct < −0.1125` → hold-or-sell-small; LLM narrates rationale |
| Reference point        | `entry_price` maintained by rule logic; provided to LLM in user message                                 |

### §2.2 RuleLLM BreakEvenTrader (simulation-bases.md §4.2)

| Theory Element        | RuleLLM Implementation                                                                |
|-----------------------|---------------------------------------------------------------------------------------|
| Break-even escalation | Rule activates at `pnl_pct < −0.05`; LLM may increase or decrease escalation quantity |
| Risk-seeking logic    | Formula `int(                                                                         |

### §2.3 RuleLLM RationalTrader (simulation-bases.md §4.3)

| Theory Element   | RuleLLM Implementation                                                          |
|------------------|---------------------------------------------------------------------------------|
| Expected utility | Rule threshold `                                                                |
| No bias          | LLM prompt reinforces rational framing; rule anchor prevents pure-noise trading |

### §2.4 RuleLLM MomentumTrader (simulation-bases.md §4.4)

| Theory Element      | RuleLLM Implementation                                     |
|---------------------|------------------------------------------------------------|
| Trend following     | Rule threshold `                                           |
| Proportional sizing | LLM may scale quantity based on narrative trend assessment |

### §2.5 RuleLLM MarketMaker (simulation-bases.md §4.5)

| Theory Element       | RuleLLM Implementation                                           |
|----------------------|------------------------------------------------------------------|
| Liquidity provision  | Rule inventory check; LLM determines optimal contrarian quantity |
| Inventory management | `                                                                |

---

## §3 Market Mechanism

Same rule-based `Market` as Rule and LLM variants. Price formation:

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

RuleLLM agent flow per round:
1. Market broadcasts `{price, fundamental, deviation}`.
2. Rule layer computes preliminary signal: action direction and baseline quantity.
3. LLM receives `{preliminary_signal, price_context, pnl_context}` in user message.
4. LLM confirms, adjusts, or overrides quantity (direction is rule-anchored).
5. Hard constraints enforced post-LLM.
6. Orders aggregated; Market updates price.

---

## §4 Variant Architecture

```
RuleLLM Variant Architecture
─────────────────────────────
Market (rule-based)
  │  broadcast {price, fundamental, deviation}
  ├─ RuleLLM LossAverseInvestor  │ rule threshold → LLM quantity modulation
  ├─ RuleLLM BreakEvenTrader     │ rule activation → LLM escalation level
  ├─ RuleLLM RationalTrader      │ rule deviation gate → LLM trade size
  ├─ RuleLLM MomentumTrader      │ rule trend gate → LLM momentum sizing
  └─ RuleLLM MarketMaker         │ rule inventory gate → LLM quantity
```

Prompts defined in `examples/LossAversion/RuleLLM/prompts.py`.

---

## §5 Config Reference

Configuration file: `configs/LossAversion/RuleLLM/simulation.yml` → `players.yml`

| Parameter              | Agent              | Default      | Description                     |
|------------------------|--------------------|--------------|---------------------------------|
| `loss_aversion_lambda` | LossAverseInvestor | 2.25         | Rule-layer threshold multiplier |
| `sell_gain_threshold`  | LossAverseInvestor | 0.05         | Rule gain trigger               |
| `risk_increase_factor` | BreakEvenTrader    | 2.0          | Rule escalation factor          |
| `risk_aversion`        | RationalTrader     | 0.5          | Rule deviation weight           |
| `entry_threshold`      | MomentumTrader     | 0.02         | Rule trend gate                 |
| `inventory_limit`      | MarketMaker        | 2000         | Rule inventory cap              |
| `llm.model`            | All LLM agents     | (configured) | LLM model identifier            |
| `llm.temperature`      | All LLM agents     | 0.3          | Sampling temperature            |
| `initial_cash`         | All investors      | 100000       | Starting cash                   |
| `initial_position`     | All investors      | 500          | Starting shares                 |

---

## §6 Running Instructions

```bash
# Run RuleLLM variant
python examples/LossAversion/RuleLLM/run_lossaversion_rulellm.py \
    -c configs/LossAversion/RuleLLM/simulation.yml
```

Output files written to `records/LossAversion/RuleLLM/`.

---

## §7 Expected Behavior

| Metric | Expected Range | Rationale                                                                        |
|--------|----------------|----------------------------------------------------------------------------------|
| LAI    | 1.8–2.5        | Rule anchor maintains λ ≈ 2.25; LLM may marginally moderate                      |
| DEI    | 1.3–2.2        | Rule enforces asymmetric thresholds; LLM narrates but rarely overrides direction |
| BER    | 1.3–3.0        | Break-even rule activates; LLM may increase or decrease escalation quantity      |
| VAF    | 1.3–2.2        | Intermediate volatility amplification                                            |
| WPI    | 0.78–0.92      | Moderate wealth penalty — below pure Rule, above pure LLM                        |
| NCE    | 0.10–0.30      | Smaller correction than LLM variant due to rule anchoring                        |

RuleLLM variant should be intermediate between Rule (most biased) and LLM (more flexible) in all metrics.

---

## §8 References

- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Tversky, A., & Kahneman, D. (1992). doi:[10.1007/BF00122574](https://doi.org/10.1007/BF00122574)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)

---

## §9 Variant Comparison

| Dimension              | Rule            | LLM           | RuleLLM           | Rag            |
|------------------------|-----------------|---------------|-------------------|----------------|
| Loss-aversion encoding | Deterministic λ | LLM narrative | Rule + LLM        | Rule + KB      |
| Break-even effect      | Fixed formula   | LLM moderate  | Rule + LLM adjust | RAG may reduce |
| Expected LAI           | 2.0–2.8         | 1.6–2.4       | 1.8–2.5           | 1.4–2.0        |
| Expected NCE           | —               | 0.15–0.40     | 0.10–0.30         | 0.30–0.60      |
| Reproducibility        | High            | Low           | Moderate          | Moderate       |
