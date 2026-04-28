# HerdingInformation LLM — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                               |
|--------------------|------------------------------------------------------|
| Variant            | LLM (language model reasoning baseline)              |
| Simulation         | HerdingInformation                                   |
| Decision Mechanism | LLM prompt-based reasoning with cascade context      |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                      |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`         |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε` |

The LLM variant replaces the deterministic threshold formulas of the Rule variant with language model reasoning. Each investor is prompted with cascade theory context and market state; the LLM generates a buy/sell/hold decision and quantity. This introduces reasoning variability: cascades may form later or resolve faster when the LLM contextualises the social signal vs. private information tradeoff.

## §2 Theory → Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component                             | Implementation                                                          |
|----------------------------------------------|-------------------------------------------------------------------------|
| Bikhchandani et al. (1992) cascade formation | LLM prompted with cascade_count, social_weight, cascade_trigger context |
| Social signal weighting                      | LLM calibrates order size based on reasoning about cascade strength     |
| Cascade direction                            | LLM follows deviation direction when reasoning confirms cascade signal  |
| Pre-cascade                                  | LLM may hold even when cascade_count is below trigger (context-aware)   |

### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component                              | Implementation                                                                 |
|-----------------------------------------------|--------------------------------------------------------------------------------|
| Scharfstein & Stein (1990) reputation herding | LLM prompted with reputation_concern, career risk framing                      |
| Lower activation threshold                    | LLM activates at smaller deviations than CascadeFollower due to prompt framing |
| Career concern amplification                  | LLM scales trade size proportionally to deviation magnitude in reasoning       |

### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component        | Implementation                                                                                     |
|-------------------------|----------------------------------------------------------------------------------------------------|
| Rational Bayesian agent | LLM prompted with signal_precision and private information framing                                 |
| Contrarian signal       | LLM may reason against deviation when private signal conflicts with social signal                  |
| Activation threshold    | LLM activation flexible: may act below 0.03 threshold when reasoning strongly indicates mispricing |

### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component                               | Implementation                                                   |
|------------------------------------------------|------------------------------------------------------------------|
| De Bondt & Thaler (1985) deliberate contrarian | LLM prompted with contrarian_threshold framing                   |
| Higher threshold than IndependentThinker       | LLM requires stronger deviation evidence before contrarian trade |
| Cascade resistance                             | LLM explicitly prompted to resist herding pressure               |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                                                               |
|---------------------------------|----------------------------------------------------------------------------------------------|
| Black (1986) uninformed trading | LLM prompted with minimal context; trade_probability governs activity                        |
| Random direction                | LLM has no fundamental basis; decisions approximate random with slight market-following bias |
| Accidental cascade initiator    | LLM noise trades still increment cascade_count when                                          |

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

Market broadcasts `{price, fundamental, deviation, round}`. The `deviation = (P − F) / F` signal drives LLM cascade interpretation: agents are prompted with the current deviation and cascade_count to reason about cascade formation.

## §4 Variant Architecture

| Component     | Detail                                                     |
|---------------|------------------------------------------------------------|
| Base class    | `LLMPlayer`                                                |
| Inference     | LLM API call per agent per round                           |
| Context       | `market_data` + `agent_extras` injected into system prompt |
| Output        | `{"action": "buy"/"sell"/"hold", "quantity": int}`         |
| Cascade state | `cascade_count` passed via prompt context                  |

## §5 Config Reference

Config file: `configs/HerdingInformation/LLM/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `social_weight`, `cascade_trigger` (CascadeFollower — passed as prompt context)
- `reputation_concern` (ReputationHerder)
- `signal_precision` (IndependentThinker)
- `contrarian_threshold` (Contrarian)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`
- LLM: `model`, `temperature`, `max_tokens`

## §6 Running Instructions

```bash
python -m examples.HerdingInformation.LLM.run_herding_information \
    -c configs/HerdingInformation/LLM/simulation.yml
```

Or via Streamlit UI: select "HerdingInformation" → "LLM" variant.

## §7 Expected Behavior

- **Later cascade formation**: LLM reasoning may delay CascadeFollower activation — LLM may interpret pre-cascade market context as insufficient for herding, extending pre-cascade phase
- **Shorter cascade duration**: CPD expected 2–8 rounds (vs. Rule 3–10): IndependentThinker LLM occasionally breaks cascades through explicit reasoning about overvaluation
- **Lower CCI**: LLM agents may contextualize cascade risk and reduce herding participation — CCI target 0.35–0.60 (vs. Rule 0.40–0.70)
- **Variable RHI**: LLM reputation framing may weight career concerns differently each run — RHI variance higher than Rule
- **Lower ICE**: LLM occasionally acts on private reasoning (not pure cascade) — ICE target 0.10–0.30
- **Smaller WDI**: Less systematic bias → smaller wealth gap between rational and cascade agents

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — CascadeFollower
- Scharfstein & Stein (1990) — ReputationHerder
- Avery & Zemsky (1998) JSTOR:116851 — information cascade efficiency

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
