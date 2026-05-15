# HindsightBias LLM — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                 |
|--------------------|--------------------------------------------------------|
| Variant            | LLM (language model reasoning baseline)                |
| Simulation         | HindsightBias                                          |
| Decision Mechanism | LLM prompt-based reasoning with hindsight bias context |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                        |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`           |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε`   |

The LLM variant replaces deterministic threshold formulas with language model reasoning. Each investor is prompted with hindsight bias theory context and market state. The LLM generates a buy/sell/hold decision and quantity. This introduces reasoning variability: bias agents may occasionally recognize and resist the "obvious" narrative, reducing HBI; rational agents may act with greater contextual conviction.

## §2 Theory → Implementation Mapping

### §2.1 HindsightOverconfident (simulation-bases.md §4.1)

| Theory Component                            | Implementation                                                                   |
|---------------------------------------------|----------------------------------------------------------------------------------|
| Fischhoff (1975) "knew-it-all-along" effect | LLM prompted with hindsight_inflation, prediction_overweight context             |
| Momentum amplification                      | LLM reasons about whether current move "should have been predicted"              |
| Inflation parameters                        | Passed as prompt context; LLM calibrates order size based on narrative certainty |

### §2.2 OutcomeLearner (simulation-bases.md §4.2)

| Theory Component      | Implementation                                                         |
|-----------------------|------------------------------------------------------------------------|
| Selective attribution | LLM prompted with success_attribution, failure_discount framing        |
| Bull-phase dominance  | LLM may reason about attribution asymmetry — stronger buys after gains |
| Reasoning variability | LLM may occasionally discount attribution bias when context is clear   |

### §2.3 ProcessEvaluator (simulation-bases.md §4.3)

| Theory Component             | Implementation                                                                |
|------------------------------|-------------------------------------------------------------------------------|
| Process-oriented rationality | LLM prompted with process vs. outcome evaluation framing                      |
| Contrarian signal            | LLM acts against deviation when process analysis indicates clear mispricing   |
| Activation flexibility       | LLM may act below 0.05 threshold when reasoning strongly indicates mispricing |

### §2.4 ContrarianSkeptic (simulation-bases.md §4.4)

| Theory Component     | Implementation                                                                |
|----------------------|-------------------------------------------------------------------------------|
| Narrative skepticism | LLM explicitly prompted to resist "obvious" hindsight narratives              |
| Contrarian strength  | LLM may apply skepticism at lower deviation when narrative evidence is strong |
| Cascade resistance   | Prompt reinforces narrative skepticism under momentum pressure                |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                               |
|---------------------------------|--------------------------------------------------------------|
| Black (1986) uninformed trading | LLM with minimal context; trade_probability governs activity |
| Random direction                | LLM noise with no fundamental basis                          |
| Threshold initiator             | Noise trades still push prices across bias agent thresholds  |

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

Market broadcasts `{price, fundamental, deviation, round}`. LLM agents are prompted with both the `deviation` signal and their behavioral persona (e.g., "You have a tendency to view past price moves as obviously predictable in retrospect").

## §4 Variant Architecture

| Component          | Detail                                                            |
|--------------------|-------------------------------------------------------------------|
| Base class         | `LLMPlayer`                                                       |
| Inference          | LLM API call per agent per round                                  |
| Context            | `market_data` + `agent_extras` injected into system prompt        |
| Output             | `{"action": "buy"/"sell"/"hold", "quantity": int}`                |
| Capacity asymmetry | Preserved in prompt constraints: biased max 800; rational max 500 |

## §5 Config Reference

Config file: `configs/HindsightBias/LLM/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `hindsight_inflation`, `prediction_overweight` (HindsightOverconfident — prompt context)
- `success_attribution`, `failure_discount` (OutcomeLearner)
- `process_weight`, `outcome_weight` (ProcessEvaluator)
- `skepticism_level`, `position_size` (ContrarianSkeptic)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`
- LLM: `model`, `temperature`, `max_tokens`

## §6 Running Instructions

```bash
python -m examples.HindsightBias.LLM.run_hindsight_bias \
    -c configs/HindsightBias/LLM/simulation.yml
```

Or via Streamlit UI: select "HindsightBias" → "LLM" variant.

## §7 Expected Behavior

- **Lower HBI**: LLM reasoning may partially resist the "obvious" hindsight narrative — HBI target 0.015–0.06 (vs. Rule 0.02–0.08)
- **More variable OBI**: LLM attribution asymmetry varies with prompt framing — OBI variance higher than Rule
- **Higher NCE**: LLM rational agents may recognize and correct mispricings more efficiently — NCE target 0.40–0.70
- **Wider VAF band**: LLM variability produces wider volatility range: 1.2–3.0
- **Lower OWP**: Less systematic bias → smaller wealth penalty for biased agents (0.03–0.20)
- **Multi-seed averaging required**: LLM stochasticity demands ≥5 seeds

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — HindsightOverconfident
- Fischhoff & Beyth (1975) `doi:10.1016/0030-5073(75)90002-1` — OutcomeLearner
- Roese & Vohs (2012) `doi:10.1177/1745691612454303` — rational correction baseline

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
