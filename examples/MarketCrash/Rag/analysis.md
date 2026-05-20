# MarketCrash Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate the crash dynamics and whether retrieved knowledge changes the
RuleLLM-like behavior in observable ways.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Maximum Drawdown | `compute_max_drawdown()` | `analysis-bases.md §2.1` | Compare with Rule and RuleLLM |
| Crash Velocity | `compute_crash_velocity()` | `analysis-bases.md §2.2` | Knowledge may alter onset speed |
| Volatility Spike | `compute_volatility_spike()` | `analysis-bases.md §2.3` | Stress-regime validation |
| Forced-Selling Share | `compute_forced_selling_share()` | `analysis-bases.md §2.4` | Deleveraging attribution |
| Liquidity Withdrawal | `compute_liquidity_withdrawal()` | `analysis-bases.md §2.5` | RAG market-maker behavior |
| Panic-Selling Volume | `compute_panic_selling_volume()` | `analysis-bases.md §2.6` | Panic narrative effect |
| Stabilization Ratio | `compute_stabilization_ratio()` | `analysis-bases.md §2.7` | Bottom-fisher knowledge effect |

## §3 Dimension-by-Dimension Analysis

Compare Rag to RuleLLM. A useful Rag effect should appear as changed reasoning,
timing, or quantity while preserving valid order schema and crash mechanism.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval-informed deleveraging | Forced sellers reference crisis/leverage context |
| Retrieval-informed liquidity | Market maker may withdraw earlier or explain caution |
| Knowledge moderation | BottomFisher may be more selective under limits-of-arbitrage context |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RAG mechanism derives from
`../simulation-bases.md §9`.
