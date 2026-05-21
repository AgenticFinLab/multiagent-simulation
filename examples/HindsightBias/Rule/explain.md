# HindsightBias Rule — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                |
|--------------------|-------------------------------------------------------|
| Variant            | Rule (deterministic baseline)                         |
| Simulation         | HindsightBias                                         |
| Decision Mechanism | Deterministic rule-based deviation threshold formulas |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                       |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`          |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε`  |

The Rule variant is the deterministic baseline for HindsightBias. All five investors apply fixed threshold formulas to the broadcast `deviation` signal. This provides the cleanest signal for measuring hindsight-induced momentum: biased agents amplify deviations above 0.02; rational agents correct deviations above 0.05.

## §2 Theory → Implementation Mapping

### §2.1 HindsightOverconfident (simulation-bases.md §4.1)

| Theory Component                            | Implementation                                                                                                 |
|---------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Fischhoff (1975) "knew-it-all-along" effect | Reads `activation_threshold`, `quantity_scale`, `max_order`, `hindsight_inflation`, and `prediction_overweight` from config; buys positive deviations and sells negative deviations. |
| Momentum amplification                      | Buys when deviation > 0 (trend "obviously" continues); sells when deviation < 0                                |
| Inflation parameters                        | `hindsight_inflation`, `prediction_overweight` modulate quantity (default 1.0 = no inflation)                  |

### §2.2 OutcomeLearner (simulation-bases.md §4.2)

| Theory Component                               | Implementation                                                                                 |
|------------------------------------------------|------------------------------------------------------------------------------------------------|
| Fischhoff & Beyth (1975) selective attribution | Same config-driven threshold as §4.1; `success_attribution` amplifies positive-deviation trades and `failure_discount` scales negative-deviation trades. |
| Bull-phase dominance                           | `success_attribution` > 1.0 amplifies gains-direction trades more than losses-direction trades |
| Identical at default                           | §4.1 and §4.2 produce identical behavior at default extras (all = 1.0)                         |

### §2.3 ProcessEvaluator (simulation-bases.md §4.3)

| Theory Component                                 | Implementation                                                                                     |
|--------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Roese & Vohs (2012) process-oriented rationality | Reads `activation_threshold`, `quantity_scale`, `max_order`, `process_weight`, and `outcome_weight`; trades contrarian only after larger deviations. |
| Contrarian direction                             | Buys when dev < −0.05 (undervalued); sells when dev > 0.05 (overvalued)                            |
| Higher threshold                                 | 0.05 vs. 0.02 — only corrects when mispricing is large enough to clearly signal bias               |

### §2.4 ContrarianSkeptic (simulation-bases.md §4.4)

| Theory Component                         | Implementation                                                                       |
|------------------------------------------|--------------------------------------------------------------------------------------|
| Roese & Vohs (2012) narrative skepticism | Same activation threshold (0.05) as ProcessEvaluator                                 |
| Quantity formula                         | `min(max_order, int(abs(dev) × quantity_scale × skepticism_level))`                  |
| Dual stabilization                       | §4.3 and §4.4 together provide correction capacity to partially offset §4.1 and §4.2 |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                                          |
|---------------------------------|-------------------------------------------------------------------------|
| Black (1986) uninformed trading | `if random() < trade_probability: qty = random.randint(min_order, max_order)` |
| Random direction                | 50/50 buy/sell — no directional bias; provides baseline volatility      |
| Threshold initiator             | Random trades push prices across 0.02 threshold, triggering bias agents |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  λ = price_impact      [default: 0.03]
  γ = mean_reversion    [default: 0.01]
  ε ~ N(0, noise_std)   [default: 0.015]
  NetDemand = Σ signed_quantities
```

Market broadcasts `{price, fundamental, deviation, round}`. The `deviation = (P − F) / F` signal is the primary driver: biased agents activate at |deviation| > 0.02; rational agents activate at |deviation| > 0.05.

## §4 Variant Architecture

| Component          | Detail                                             |
|--------------------|----------------------------------------------------|
| Base class         | `GeneralPlayer`                                    |
| Inference          | None (deterministic formulas)                      |
| Context            | `market_data` from broadcast                       |
| Output             | Canonical order with `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, and `strategy` |
| Capacity asymmetry | Biased: max 800 shares; Rational: max 500 shares   |

## §5 Config Reference

Config file: `configs/HindsightBias/Rule/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `hindsight_inflation`, `prediction_overweight` (HindsightOverconfident)
- `success_attribution`, `failure_discount` (OutcomeLearner)
- `process_weight`, `outcome_weight` (ProcessEvaluator)
- `skepticism_level`, `activation_threshold`, `quantity_scale`, `max_order` (ContrarianSkeptic)
- `trade_probability`, `min_order`, `max_order` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`

## §6 Running Instructions

```bash
python -m examples.HindsightBias.Rule.run_hindsight_bias \
    -c configs/HindsightBias/Rule/simulation.yml
```

Or via Streamlit UI: select "HindsightBias" → "Rule" variant.

## §7 Expected Behavior

- **Momentum phase**: HindsightOverconfident and OutcomeLearner both amplify deviations above 0.02 — combined capacity 1,600 shares overwhelms correction capacity (1,000 shares) in early rounds
- **HBI target**: 0.02–0.08 — sustained mean absolute deviation from fundamental
- **OBI > 1.0**: Bull-phase momentum dominates (at non-default `success_attribution` > 1.0)
- **NCE in 0.35–0.65**: ProcessEvaluator and ContrarianSkeptic partially correct but cannot fully overcome capacity asymmetry
- **VAF in 1.5–3.5**: Bias-active rounds more volatile than quiet rounds
- **Rule produces tightest bands**: Deterministic thresholds → lowest inter-seed variance

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — HindsightOverconfident
- Fischhoff & Beyth (1975) `doi:10.1016/0030-5073(75)90002-1` — OutcomeLearner
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — capacity asymmetry

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
