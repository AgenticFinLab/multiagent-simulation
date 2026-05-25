# Volatility Clustering RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Decision Mechanism | API-generated orders constrained by explicit volatility rules |
| Scenario Contract | `action`, `bid_price`, `quantity`, `reasoning`, `provides_liquidity` |
| Theory Reference | `examples/VolatilityClustering/simulation-bases.md` |

RuleLLM combines each role's persona with explicit quantitative decision-rule
reminders. It uses the liquidity-aware market extension, so the
`provides_liquidity` field is required.

## §2 Theory -> Implementation Mapping

### §2.1 Fundamentalist (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Fundamental anchoring | `RuleLLMFundamentalist` maps to the fundamentalist rule prompt. |
| API contract | Emits `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |

### §2.2 TrendFollower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Volatility-sensitive trend demand | `RuleLLMTrendFollower` maps to the trend-following rule prompt. |
| API contract | Explicit rules constrain trend direction and volatility-scaled sizing. |

### §2.3 NoiseTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Shock generation | `RuleLLMNoiseTrader` maps to the noise-trader rule prompt. |
| API contract | Liquidity flag is required by the market depth calculation. |

### §2.4 SlowAdapter (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Delayed information processing | `RuleLLMSlowAdapter` maps to the slow-adapter rule prompt. |
| API contract | Explicit rules keep delayed-reaction behavior bounded. |

### §2.5 VolatilityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-regime response | `RuleLLMVolatilityTrader` maps to the volatility-regime rule prompt. |
| API contract | Structured JSON is parsed into liquidity-aware market orders. |

## §3 Market Mechanism

The RuleLLM market uses liquidity-sensitive price impact. Passive liquidity from
orders marked `provides_liquidity=true` adds to baseline depth, while low depth
increases the price impact of net demand.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/VolatilityClustering/RuleLLM/players.py` |
| Prompt module | `examples/VolatilityClustering/RuleLLM/prompts.py` |
| Inference | Project ARK LLM policy from config extras |
| Output parsing | Strict JSON parser requiring liquidity flag |
| Error handling | Explicit conservative hold fallback only after bounded parse retries |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/VolatilityClustering/RuleLLM/simulation.yml` | Full 200-round entry point. |
| `configs/VolatilityClustering/RuleLLM/players.yml` | Liquidity-aware market and five API investors. |
| `configs/VolatilityClustering/RuleLLM/topology.yml` | Market broadcast and investor-order routing. |
| `configs/VolatilityClustering/RuleLLM/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/VolatilityClustering/RuleLLM/run_volatility_clustering_rulellm.py -c configs/VolatilityClustering/RuleLLM/simulation.yml
```

## §7 Expected Behavior

Rule reminders should preserve the volatility mechanism while API reasoning
changes order size and liquidity provision. The sample should be checked for
fallback rate and valid liquidity flags.

## §8 References

See `examples/VolatilityClustering/simulation-bases.md §3` for the
liquidity-aware market and `analysis-bases.md §2.5` for regime-response metrics.

## §9 Variant Comparison

RuleLLM is compared with LLM to measure the effect of explicit rules and with
Rag to isolate the incremental effect of retrieval.
