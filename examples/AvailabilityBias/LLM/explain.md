# AvailabilityBias LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Simulation | AvailabilityBias |
| Decision Mechanism | Persona-only LLM prompts with the shared trading JSON parser |
| Theory Reference | `simulation-bases.md §2` and investor designs in `simulation-bases.md §4` |
| Market Broadcast | `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 LLMRecentEventOverweighter (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Salient recent events dominate attention | `LLM_RECENT_EVENT_OVERWEIGHTER_SYS` describes vivid recent moves as the main decision influence. |
| No explicit formula in LLM mode | Prompt remains persona-only; it receives `return_pct` and `deviation` but no fixed threshold. |
| Bounded trading | `players.py` enforces cash and inventory limits after parsing the decision. |

### §2.2 LLMMediaInfluencedTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Media salience affects judgment | `LLM_MEDIA_INFLUENCED_TRADER_SYS` makes headlines and social narratives the qualitative driver. |
| Narrative amplification | Prompt asks the agent to reason about whether deviation would attract broad media attention. |
| Bounded trading | Parsed action is constrained by cash or position. |

### §2.3 LLMSystematicAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Objective evidence weighting | `LLM_SYSTEMATIC_ANALYST_SYS` emphasizes price, fundamental value, and deviation. |
| Availability resistance | Prompt explicitly resists vivid stories and recent moves. |
| Stabilizing role | Parsed buy/sell decisions are applied against the current market state. |

### §2.4 LLMValueTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental-value discipline | `LLM_VALUE_TRADER_SYS` prioritizes margin of safety and patient contrarian behavior. |
| Narrative resistance | Prompt instructs the trader to ignore short-lived narratives. |
| Bounded trading | Parsed quantity is limited by cash or inventory. |

### §2.5 LLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Uninformed liquidity | `LLM_NOISE_TRADER_SYS` produces weakly motivated buy/sell/hold decisions. |
| No systematic signal | Prompt does not assign formulaic meaning to return or deviation. |
| Bounded trading | Shared parser and portfolio constraints still apply. |

## §3 Market Mechanism

The LLM variant reuses the Rule market implementation. Only investor decision logic changes from deterministic formulas to persona-driven LLM output.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Inference | `LangChainAPIInference` using `lm_name` from config |
| Prompt Contract | `<analysis>...</analysis>` plus `<decision>{...}</decision>` |
| Parser | `parse_llm_response_with_thinking` |
| Retry Logic | Bounded retries for parser or retryable API errors |
| Failure Policy | After retries, invalid parser output raises; it does not create a silent hold fallback. |

## §5 Config Reference

Primary config: `configs/AvailabilityBias/LLM/simulation.yml`.
Each investor config supplies `llm.sys_message`, `llm.user_message`, `lm_name`, and `generation_config`.

## §6 Running Instructions

```bash
python examples/AvailabilityBias/LLM/run_availabilitybias_llm.py \
  -c configs/AvailabilityBias/LLM/simulation.yml
```

## §7 Expected Behavior

- Persona-only agents may express stronger or weaker availability bias than the Rule baseline.
- SystematicAnalyst should not cite recent salience as a reason to overreact.
- All successful runs should have parse-valid decisions and no fallback-hold substitutions.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
