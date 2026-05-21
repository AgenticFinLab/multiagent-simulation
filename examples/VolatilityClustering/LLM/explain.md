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

| Theory Component | Implementation |
|---|---|
| Fundamentalist, `simulation-bases.md §4.1` | `LLMFundamentalist` follows the value-oriented persona and structured order parser. |
| TrendFollower, `simulation-bases.md §4.2` | `LLMTrendFollower` reacts quickly to trends and volatility. |
| NoiseTrader, `simulation-bases.md §4.3` | `LLMNoiseTrader` produces low-information random order flow. |
| SlowAdapter, `simulation-bases.md §4.4` | `LLMSlowAdapter` uses conservative delayed-reaction prompts. |
| VolatilityTrader, `simulation-bases.md §4.5` | `LLMVolatilityTrader` trades based on volatility regime interpretation. |

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
