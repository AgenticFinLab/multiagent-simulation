# AvailabilityBias RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Simulation | AvailabilityBias |
| Decision Mechanism | LLM prompts with explicit quantitative decision rules |
| Theory Reference | `simulation-bases.md §2` and investor designs in `simulation-bases.md §4` |
| Market Broadcast | `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMRecentEventOverweighter (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Recency salience overweighting | Prompt has `== DECISION RULES ==` with `0.70 * return_pct + 0.30 * deviation`. |
| Salient event threshold | Prompt instructs buy above `+0.02`, sell below `-0.02`, otherwise hold. |
| Bounded size | Prompt gives `min(300, abs(perceived_signal) * 5000)` and portfolio constraints. |

### §2.2 RuleLLMMediaInfluencedTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Media/social amplification | Prompt computes `0.80 * deviation * 1.50`. |
| Narrative threshold | Prompt trades when amplified signal crosses `+/-0.03`. |
| Bounded size | Prompt gives `min(300, abs(amplified_signal) * 5000)`. |

### §2.3 RuleLLMSystematicAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Objective evidence weighting | Prompt uses deviation thresholds only. |
| Availability resistance | Persona section says the agent resists salient stories and recent moves. |
| Stabilizing threshold | Prompt trades only outside `+/-0.03`. |

### §2.4 RuleLLMValueTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental discipline | Prompt acts only outside `+/-0.05` deviation. |
| Fixed sizing | Prompt uses 300 shares before constraints. |
| Stabilizing role | Buys undervaluation and sells overvaluation. |

### §2.5 RuleLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Noise liquidity | Prompt instructs about 30% trade probability. |
| Random direction | Prompt chooses buy/sell with roughly equal probability. |
| Quantity band | Prompt uses 100-500 shares before constraints. |

## §3 Market Mechanism

The RuleLLM variant reuses the Rule market implementation. Price formation and broadcast schema are unchanged.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Prompt Structure | Each agent has `== PERSONA ==` and `== DECISION RULES ==` sections. |
| Inference | `LangChainAPIInference` using config model settings. |
| Parser | `parse_llm_response_with_thinking`. |
| Retry Logic | Bounded retries for parser or retryable API errors. |
| Failure Policy | Invalid output raises after retries; no silent fallback hold. |

## §5 Config Reference

Primary config: `configs/AvailabilityBias/RuleLLM/simulation.yml`.
Each investor supplies prompt paths and model generation settings under `extras.llm`.

## §6 Running Instructions

```bash
python examples/AvailabilityBias/RuleLLM/run_availabilitybias_rulellm.py \
  -c configs/AvailabilityBias/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- RuleLLM should stay close to Rule while allowing stochastic rationale wording.
- RecentEventOverweighter and MediaInfluencedTrader should show explicit calculation in analysis text.
- SystematicAnalyst should remain isolated from recency/media salience.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
