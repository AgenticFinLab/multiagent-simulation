# HerdingInformation RuleLLM — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                        |
|--------------------|---------------------------------------------------------------|
| Variant            | RuleLLM (hybrid: rule-anchored LLM reasoning)                 |
| Simulation         | HerdingInformation                                            |
| Decision Mechanism | LLM reasoning constrained by embedded cascade threshold rules |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                               |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                  |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε`          |

The RuleLLM variant embeds the deterministic cascade threshold rules from the Rule variant directly into each investor's system prompt. The LLM must respect these rules but can reason contextually about trade sizing and market conditions. This hybrid approach combines rule-based cascade trigger consistency with LLM-based contextual nuance.

## §2 Theory → Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component                             | Implementation                                                              |
|----------------------------------------------|-----------------------------------------------------------------------------|
| Bikhchandani et al. (1992) cascade formation | Rule embedded in prompt: activate only when cascade_count ≥ cascade_trigger |
| Social signal weighting                      | LLM contextualises order size within rule-bounded quantity range            |
| Cascade direction                            | LLM must follow deviation direction per embedded rule                       |
| Pre-cascade discipline                       | Prompt strictly prevents cascade before threshold — tighter than pure LLM   |

### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component                              | Implementation                                           |
|-----------------------------------------------|----------------------------------------------------------|
| Scharfstein & Stein (1990) reputation herding | Rule embedded: activate at                               |
| Lower activation threshold                    | Threshold rule preserved: fires before CascadeFollower   |
| Career concern amplification                  | LLM reasons about reputation_concern in sizing decisions |

### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component        | Implementation                                                                      |
|-------------------------|-------------------------------------------------------------------------------------|
| Rational Bayesian agent | Rule embedded: activate at                                                          |
| Contrarian signal       | LLM may strengthen contrarian position when fundamental clearly supports correction |
| Activation threshold    | Rule-enforced 0.03 minimum — prevents premature activation                          |

### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component                               | Implementation                                                      |
|------------------------------------------------|---------------------------------------------------------------------|
| De Bondt & Thaler (1985) deliberate contrarian | Rule embedded: activate at                                          |
| Higher threshold than IndependentThinker       | Threshold rule anchors activation; LLM adds conviction-based sizing |
| Cascade resistance                             | Prompt reinforces contrarian discipline under herding pressure      |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                                      |
|---------------------------------|---------------------------------------------------------------------|
| Black (1986) uninformed trading | Rule embedded: trade_probability governs activity                   |
| Random direction                | LLM noise with minimal context — rule governs frequency             |
| Accidental cascade initiator    | Noise trades preserved; cascade_count increments as in Rule variant |

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

Market broadcasts `{price, fundamental, deviation, round}`. Rule constraints are injected as explicit conditions in the system prompt: "You must not execute a cascade trade unless cascade_count >= cascade_trigger."

## §4 Variant Architecture

| Component     | Detail                                                             |
|---------------|--------------------------------------------------------------------|
| Base class    | `RuleLLMPlayer`                                                    |
| Inference     | LLM API call with embedded rule constraints in system prompt       |
| Context       | `market_data` + `agent_extras` + embedded rule text                |
| Output        | `{"action": "buy"/"sell"/"hold", "quantity": int}`                 |
| Cascade state | `cascade_count` passed via prompt context; rule enforces threshold |

## §5 Config Reference

Config file: `configs/HerdingInformation/RuleLLM/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `social_weight`, `cascade_trigger` (CascadeFollower)
- `reputation_concern` (ReputationHerder)
- `signal_precision` (IndependentThinker)
- `contrarian_threshold` (Contrarian)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`
- LLM: `model`, `temperature`, `max_tokens`

## §6 Running Instructions

```bash
python -m examples.HerdingInformation.RuleLLM.run_herding_information \
    -c configs/HerdingInformation/RuleLLM/simulation.yml
```

Or via Streamlit UI: select "HerdingInformation" → "RuleLLM" variant.

## §7 Expected Behavior

- **Rule-consistent cascade timing**: CascadeFollower activates at the same cascade_count threshold as Rule — cascade onset timing is rule-anchored (vs. LLM's free-form reasoning)
- **Contextual sizing**: LLM sizes orders within rule-bounded range — produces smoother order flow than Rule's abrupt step function
- **CCI similar to Rule**: Cascade formation timing anchored by rules → CCI target 0.45–0.65 (close to Rule 0.40–0.70)
- **CPD similar to Rule**: Rule-enforced thresholds maintain cascade persistence within 3–9 rounds
- **RHI similar to Rule**: Reputation threshold also rule-anchored — RHI variance lower than pure LLM
- **Intermediate between Rule and LLM**: All metrics expected between Rule and LLM baselines

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — CascadeFollower
- Scharfstein & Stein (1990) — ReputationHerder
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — limits to arbitrage

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
