# RepresentativenessBias LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Simulation | RepresentativenessBias |
| Decision Mechanism | Persona-only LLM reasoning with canonical decision JSON |
| Theory Reference | `simulation-bases.md §2` and `§4` |
| Market Broadcast | Same Market implementation as Rule |

## §2 Theory → Implementation Mapping

### §2.1 LLMPatternMatcher (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Prototype matching | `LLM_PATTERN_MATCHER_PROMPT` frames historical patterns as predictive |
| Base-rate neglect | Persona tells the agent to trust pattern recognition over statistical reasoning |
| Runtime path | `LLMInvestor.decide()` parses and validates canonical JSON |

### §2.2 LLMCategoryOvergeneralizer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Category extrapolation | Prompt encourages assigning stocks to dramatic categories from surface features |
| Small sample bias | Prompt treats recent price samples as category-confirming evidence |
| Runtime path | Quantity is constrained by cash and position after parsing |

### §2.3 LLMBayesianUpdater (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Base-rate discipline | Prompt emphasizes priors, evidence weighting, and Bayesian correction |
| Rational benchmark | LLM output is constrained to valid market orders |
| Runtime path | Parse failure after bounded retries raises an error |

### §2.4 LLMContrarianStatistical (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Correction of representativeness mispricing | Prompt identifies pattern-driven price pressure as exploitable |
| Contrarian direction | LLM reasons from deviation and market context |
| Runtime path | Order schema records `bid_price` and `reasoning` |

### §2.5 LLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Uninformed liquidity | Prompt describes random liquidity participation |
| Neutral baseline | Persona is not given representativeness bias |
| Runtime path | Validated JSON prevents silent fallback holds |

## §3 Market Mechanism

The LLM variant imports the Rule `Market`, so price formation and market
broadcasts are identical to the Rule baseline.

## §4 Variant Architecture

```text
Market state -> persona prompt -> LLM -> validated decision JSON -> order -> Market
```

## §5 Config Reference

Primary config: `configs/RepresentativenessBias/LLM/players.yml`.
LLM settings live under `extras.llm.lm_name` and
`extras.llm.generation_config`.

## §6 Running Instructions

```bash
python examples/RepresentativenessBias/LLM/run_representativenessbias_llm.py \
  -c configs/RepresentativenessBias/LLM/simulation.yml
```

## §7 Expected Behavior

LLM pattern and category agents should show representativeness reasoning without
hard-coded formula execution. Bayesian and contrarian personas should introduce
statistical restraint.

## §8 References

See `simulation-bases.md §2` for full citations.

## §9 Variant Comparison

See `simulation-bases.md §9`.
