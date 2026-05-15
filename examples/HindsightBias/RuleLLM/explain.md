# HindsightBias RuleLLM — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                               |
|--------------------|----------------------------------------------------------------------|
| Variant            | RuleLLM (hybrid: rule-anchored LLM reasoning)                        |
| Simulation         | HindsightBias                                                        |
| Decision Mechanism | LLM reasoning constrained by embedded hindsight bias threshold rules |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                      |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                         |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε`                 |

The RuleLLM variant embeds the deterministic threshold rules from the Rule variant directly into each investor's system prompt. LLM must activate at the same deviation thresholds as Rule (0.02 for biased, 0.05 for rational), but can reason contextually about trade sizing and narrative strength.

## §2 Theory → Implementation Mapping

### §2.1 HindsightOverconfident (simulation-bases.md §4.1)

| Theory Component                  | Implementation                                                                                       |
|-----------------------------------|------------------------------------------------------------------------------------------------------|
| Fischhoff (1975) hindsight effect | Rule embedded: must activate at                                                                      |
| Momentum amplification            | LLM contextualises order size within rule-bounded range (max 800)                                    |
| Inflation parameters              | `hindsight_inflation`, `prediction_overweight` passed as prompt context; LLM modulates within bounds |

### §2.2 OutcomeLearner (simulation-bases.md §4.2)

| Theory Component       | Implementation                                                                           |
|------------------------|------------------------------------------------------------------------------------------|
| Selective attribution  | Rule embedded: threshold 0.02 mandatory; LLM adjusts magnitude by attribution parameters |
| Bull-phase asymmetry   | LLM reasons about success vs. failure attribution within rule bounds                     |
| Hybrid differentiation | Unlike pure Rule (identical to §4.1), RuleLLM §4.2 may show modest differentiation       |

### §2.3 ProcessEvaluator (simulation-bases.md §4.3)

| Theory Component            | Implementation                                               |
|-----------------------------|--------------------------------------------------------------|
| Process rationality         | Rule embedded: must activate at                              |
| Contrarian sizing           | LLM sizes orders within rule-bounded range (max 500)         |
| Rule-constrained correction | Threshold prevents premature activation; LLM adds conviction |

### §2.4 ContrarianSkeptic (simulation-bases.md §4.4)

| Theory Component            | Implementation                                                         |
|-----------------------------|------------------------------------------------------------------------|
| Narrative skepticism        | Rule embedded: threshold 0.05; LLM adds skeptical reasoning for sizing |
| Rule-constrained skepticism | Same threshold as ProcessEvaluator — prevents premature activation     |
| Dual stabilization          | Both §4.3 and §4.4 respect rule threshold; LLM adds contextual sizing  |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component    | Implementation                                          |
|---------------------|---------------------------------------------------------|
| Black (1986) noise  | Rule embedded: `trade_probability` governs activity     |
| Random direction    | LLM with minimal context; rule governs frequency        |
| Threshold initiator | Noise trades preserved; bias agent thresholds respected |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  λ = price_impact      [default: 0.001]
  γ = mean_reversion    [default: 0.05]
  ε ~ N(0, noise_std)   [default: 0.5]
  NetDemand = Σ signed_quantities
```

Rule constraints injected as explicit conditions in the system prompt: "You must not trade unless |deviation| > 0.02" (biased agents) and "You must not trade unless |deviation| > 0.05" (rational agents).

## §4 Variant Architecture

| Component          | Detail                                                       |
|--------------------|--------------------------------------------------------------|
| Base class         | `RuleLLMPlayer`                                              |
| Inference          | LLM API call with embedded rule constraints in system prompt |
| Context            | `market_data` + `agent_extras` + embedded rule text          |
| Output             | `{"action": "buy"/"sell"/"hold", "quantity": int}`           |
| Capacity asymmetry | Preserved in rules: biased max 800; rational max 500         |

## §5 Config Reference

Config file: `configs/HindsightBias/RuleLLM/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `hindsight_inflation`, `prediction_overweight` (HindsightOverconfident)
- `success_attribution`, `failure_discount` (OutcomeLearner)
- `process_weight`, `outcome_weight` (ProcessEvaluator)
- `skepticism_level`, `position_size` (ContrarianSkeptic)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`
- LLM: `model`, `temperature`, `max_tokens`

## §6 Running Instructions

```bash
python -m examples.HindsightBias.RuleLLM.run_hindsight_bias \
    -c configs/HindsightBias/RuleLLM/simulation.yml
```

Or via Streamlit UI: select "HindsightBias" → "RuleLLM" variant.

## §7 Expected Behavior

- **HBI similar to Rule**: Bias agent activation thresholds are rule-anchored — HBI target 0.02–0.08
- **LLM sizing smoothes order flow**: Rule step-function orders replaced by LLM-calibrated sizes → slightly lower VAF
- **NCE similar to Rule**: Rational agent thresholds also rule-anchored → NCE 0.35–0.65
- **Intermediate metrics**: All metrics expected statistically between Rule and LLM baselines
- **Low inter-seed variance**: Rule thresholds prevent LLM stochasticity from dramatically changing dynamics

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — HindsightOverconfident
- Fischhoff & Beyth (1975) `doi:10.1016/0030-5073(75)90002-1` — OutcomeLearner
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — limits to arbitrage

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
