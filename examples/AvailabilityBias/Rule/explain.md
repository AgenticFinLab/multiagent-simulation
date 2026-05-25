# AvailabilityBias Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Simulation | AvailabilityBias |
| Decision Mechanism | Deterministic formulas loaded from `configs/AvailabilityBias/Rule/players.yml` |
| Theory Reference | `simulation-bases.md §2` and investor designs in `simulation-bases.md §4` |
| Market Broadcast | `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 RecentEventOverweighter (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Recency salience overweighting | `RecentEventOverweighter.decide()` computes `recency_weight * return_pct + (1 - recency_weight) * deviation`. |
| Salient-event activation | Trades only when `abs(perceived_signal) > salience_threshold`. |
| Bounded order sizing | Uses `quantity_scale` and `max_order` from config, then applies cash or inventory limits. |

### §2.2 MediaInfluencedTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Media/social amplification | `MediaInfluencedTrader.decide()` computes `media_weight * deviation * social_amplification`. |
| Narrative-trigger threshold | Trades only when `abs(amplified_signal) > media_threshold`. |
| Bounded order sizing | Uses config-driven `quantity_scale` and `max_order`. |

### §2.3 SystematicAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Objective information weighting | Uses `deviation` only; ignores `return_pct` and media amplification. |
| Stabilizing counter-trade | Buys undervaluation and sells overvaluation beyond `evidence_threshold`. |
| Bounded order sizing | Uses `quantity_scale` and `max_order` from config. |

### §2.4 ValueTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental value discipline | Trades only when `abs(deviation) > deviation_threshold`. |
| Patient fixed sizing | Uses `position_size` from config. |
| Stabilization role | Buys below fundamental and sells above fundamental. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Uninformed background liquidity | Trades with `trade_probability`. |
| Random direction and size | Draws quantity between config-driven `min_order` and `max_order`. |
| No signal interpretation | Does not use deviation or return signals for direction. |

## §3 Market Mechanism

The market implements `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon`.
`D(t)` is buy quantity minus sell quantity from canonical order payloads. The market records `price`, `fundamental`, and `volume` batch stores for analysis.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | `Market` in `Rule/players.py` |
| Investors | Five deterministic investor classes |
| Output Schema | Canonical order fields: `type`, `from`, `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, `strategy` |
| Failure Policy | Missing required data, invalid price, or invalid action raises immediately. |

## §5 Config Reference

Primary config: `configs/AvailabilityBias/Rule/simulation.yml`.
Investor parameters are in `configs/AvailabilityBias/Rule/players.yml`, including `recency_weight`, `salience_threshold`, `media_threshold`, `quantity_scale`, `max_order`, `position_size`, and `trade_probability`.

## §6 Running Instructions

```bash
python examples/AvailabilityBias/Rule/run_availabilitybias_rule.py \
  -c configs/AvailabilityBias/Rule/simulation.yml
```

## §7 Expected Behavior

- Recency and media agents create measurable but bounded deviation from fundamental value.
- SystematicAnalyst and ValueTrader partially correct overreaction.
- NoiseTrader supplies background liquidity without directional information.
- Full 200-round runs should produce all analysis outputs listed in `analysis-bases.md §7`.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
