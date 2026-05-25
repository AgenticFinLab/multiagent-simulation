# Volatility Clustering LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Decision Mechanism | API-generated trading orders |
| Scenario Contract | `action`, `bid_price`, `quantity`, `reasoning` |
| Theory Reference | `examples/VolatilityClustering/simulation-bases.md` |

The LLM variant keeps the bounded GARCH market and five role families but
replaces deterministic investor formulas with persona prompts and canonical JSON
orders.

## §2 Theory -> Implementation Mapping

### §2.1 Fundamentalist (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Fundamental anchoring | `LLMFundamentalist` follows the value-oriented persona and structured order parser. |
| API contract | Emits `action`, `bid_price`, `quantity`, and `reasoning`. |

### §2.2 TrendFollower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Volatility-sensitive trend demand | `LLMTrendFollower` reacts quickly to trends and volatility. |
| API contract | Parser converts canonical JSON into signed market orders. |

### §2.3 NoiseTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Shock generation | `LLMNoiseTrader` produces low-information random order flow. |
| API contract | Bounded retries handle stochastic parse errors; deterministic schema errors fail fast. |

### §2.4 SlowAdapter (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Delayed information processing | `LLMSlowAdapter` uses conservative delayed-reaction prompts. |
| API contract | Reasoning text is recorded for post-run quality review. |

### §2.5 VolatilityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-regime response | `LLMVolatilityTrader` trades based on volatility regime interpretation. |
| API contract | Emits canonical trading JSON rather than a special volatility schema. |

## §3 Market Mechanism

The market mechanism matches the Rule GARCH coordinator. The difference is that
agent orders are produced by the project ARK LLM client and parsed from
`<analysis>` and `<decision>` sections.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/VolatilityClustering/LLM/players.py` |
| Prompt module | `examples/VolatilityClustering/LLM/prompts.py` |
| Inference | Project ARK LLM policy from config extras |
| Output parsing | Canonical LLM parser requiring action, bid_price, quantity, and reasoning |
| Error handling | Parse failures retry and then fail fast for deterministic contract errors |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/VolatilityClustering/LLM/simulation.yml` | Full 200-round entry point. |
| `configs/VolatilityClustering/LLM/players.yml` | GARCH market and five API investor definitions. |
| `configs/VolatilityClustering/LLM/topology.yml` | Market broadcast and investor-order routing. |
| `configs/VolatilityClustering/LLM/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/VolatilityClustering/LLM/run_volatility_llm.py -c configs/VolatilityClustering/LLM/simulation.yml
```

## §7 Expected Behavior

The LLM path should preserve volatility clustering while allowing role-level
variation in order timing and size. The sample should be reviewed for parse
failures and fallback events.

## §8 References

See `examples/VolatilityClustering/simulation-bases.md §2` for volatility
theory and `analysis-bases.md §2.7` for API quality.

## §9 Variant Comparison

LLM is compared with Rule to measure stochastic prompt interpretation. It does
not use liquidity-depth fields or RAG retrieval.
