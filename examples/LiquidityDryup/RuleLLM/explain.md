# LiquidityDryup — RuleLLM Variant Explanation

## §1 Overview

| Item               | Description                                                                                                     |
|--------------------|-----------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Liquidity dry-up with hybrid rule-threshold + LLM narrative reasoning for market maker withdrawal decisions     |
| **Variant**        | RuleLLM: rule-based volatility threshold triggers withdrawal signal; LLM determines withdrawal depth and timing |
| **Investor Count** | 5 hybrid classes; MarketMaker withdrawal is rule-triggered but LLM-calibrated                                   |
| **Key Feature**    | Rule anchor prevents LLM from ignoring withdrawal trigger; LLM adds contextual modulation of withdrawal depth   |
| **Academic Value** | Tests whether rule-anchored LLM produces more consistent liquidity spirals than pure LLM                        |

---

## §2 Theory → Implementation Mapping

### §2.1 RuleLLM MarketMaker (simulation-bases.md §4.1)

| Theory Element     | RuleLLM Implementation                                                              |
|--------------------|-------------------------------------------------------------------------------------|
| Withdrawal trigger | Rule: `                                                                             |
| Withdrawal depth   | LLM determines `provides_liquidity` level and inventory offload fraction            |
| Normal provision   | Rule: LLM provides liquidity in range 0–`base_liquidity` based on market assessment |
| Hard cap           | `max(−25, min(25, quantity))` enforced post-LLM                                     |

### §2.2 RuleLLM LiquiditySeeker (simulation-bases.md §4.2)

| Theory Element       | RuleLLM Implementation                                                       |
|----------------------|------------------------------------------------------------------------------|
| Execution need       | Rule provides baseline; LLM adjusts quantity based on urgency assessment     |
| Liquidity adjustment | LLM may further reduce quantity beyond rule scaling when liquidity is scarce |

### §2.3 RuleLLM ValueTrader (simulation-bases.md §4.3)

| Theory Element      | RuleLLM Implementation                                                              |
|---------------------|-------------------------------------------------------------------------------------|
| Value trigger       | Rule deviation threshold; LLM determines if current conditions warrant crisis entry |
| Liquidity provision | Rule gate + LLM quantity calibration                                                |

### §2.4 RuleLLM MomentumTrader (simulation-bases.md §4.4)

| Theory Element   | RuleLLM Implementation                                        |
|------------------|---------------------------------------------------------------|
| Trend activation | Rule threshold; LLM determines momentum strength and quantity |

### §2.5 RuleLLM NoiseTrader (simulation-bases.md §4.5)

| Theory Element | RuleLLM Implementation                                   |
|----------------|----------------------------------------------------------|
| Random orders  | Rule default; LLM adds minor context-dependent variation |

---

## §3 Market Mechanism

Same rule-based `Market` with liquidity-dependent price impact:

```
P(t+1) = P(t) + (λ × NetDemand × liquidity_factor) + γ × (F − P(t)) + ε(t)
liquidity_factor = 100 / max(total_liquidity, 10)
```

RuleLLM flow per round:
1. Market broadcasts data.
2. Rule layer computes preliminary action and direction.
3. LLM receives `{preliminary_signal, market_data}` and calibrates depth.
4. `provides_liquidity` from LLM contributes to `total_liquidity`.
5. Spiral proceeds via same endogenous amplification mechanism.

---

## §4 Variant Architecture

```
RuleLLM Variant Architecture
─────────────────────────────
Market (rule-based, liquidity-dependent pricing)
  │  broadcast {price, return%, liquidity, fundamental}
  ├─ RuleLLM MarketMaker     │ rule trigger → LLM withdrawal depth
  ├─ RuleLLM LiquiditySeeker │ rule scale → LLM quantity
  ├─ RuleLLM ValueTrader     │ rule deviation gate → LLM entry size
  ├─ RuleLLM MomentumTrader  │ rule trend gate → LLM momentum size
  └─ RuleLLM NoiseTrader     │ rule baseline → LLM minor variation
```

Prompts defined in `examples/LiquidityDryup/RuleLLM/prompts.py`.

---

## §5 Config Reference

| Parameter              | Agent       | Default      | Description                        |
|------------------------|-------------|--------------|------------------------------------|
| `volatility_threshold` | MarketMaker | 0.03         | Rule trigger for withdrawal signal |
| `base_liquidity`       | MarketMaker | 30           | Maximum normal liquidity           |
| `llm.model`            | All LLM     | (configured) | LLM model identifier               |
| `llm.temperature`      | All LLM     | 0.3          | Sampling temperature               |
| `fundamental_value`    | Market      | 100          | Fundamental anchor                 |
| `price_impact`         | Market      | 0.001        | Base λ                             |
| `mean_reversion`       | Market      | 0.05         | γ                                  |

---

## §6 Running Instructions

```bash
# Run RuleLLM variant
python examples/LiquidityDryup/RuleLLM/run_liquidity_dryup_rulellm.py \
    -c configs/LiquidityDryup/RuleLLM/simulation.yml
```

Output written to `records/LiquidityDryup/RuleLLM/`.

---

## §7 Expected Behavior

| Metric      | Expected Range | Rationale                                             |
|-------------|----------------|-------------------------------------------------------|
| LRI minimum | 0.05–0.25      | Rule ensures withdrawal; LLM may reduce depth         |
| MWF maximum | 0.6–1.0        | Rule anchor ensures most MMs withdraw above threshold |
| PAD         | 0.09–0.22      | Intermediate between Rule and LLM                     |
| LPD         | 9–22 rounds    | Rule-anchored cascade; LLM may speed recovery         |
| WDI         | 0.22–0.42      | Intermediate redistribution                           |

RuleLLM should fall between Rule and LLM for all metrics; closer to Rule due to threshold anchoring.

---

## §8 References

- Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Grossman, S. J., & Miller, M. H. (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)

---

## §9 Variant Comparison

| Dimension        | Rule      | LLM        | RuleLLM          | Rag       |
|------------------|-----------|------------|------------------|-----------|
| MM withdrawal    | Formula   | LLM social | Rule + LLM depth | Rule + KB |
| Expected LRI min | 0.05–0.20 | 0.05–0.30  | 0.05–0.25        | 0.10–0.30 |
| Expected LPD     | 10–25     | 8–20       | 9–22             | 6–15      |
| Reproducibility  | High      | Low        | Moderate         | Moderate  |
