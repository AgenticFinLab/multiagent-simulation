# Volatility Clustering Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Decision Mechanism | deterministic trading rules |
| Scenario Contract | signed trading orders |
| Theory Reference | `examples/VolatilityClustering/simulation-bases.md` |

The Rule variant is the deterministic baseline. It combines a bounded GARCH
market update with Fundamentalist, TrendFollower, NoiseTrader, SlowAdapter, and
VolatilityTrader roles.

## §2 Theory -> Implementation Mapping

### §2.1 Fundamentalist (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Fundamental anchoring | `Fundamentalist` trades toward noisy fundamental value at configured intervals. |
| Order schema | Emits deterministic signed quantity, bid price, strategy, and investor label. |

### §2.2 TrendFollower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Volatility-sensitive trend demand | `TrendFollower` trades with recent price trend and scales size by volatility. |
| Order schema | Emits larger trend-following quantities in high-volatility states. |

### §2.3 NoiseTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Shock generation | `NoiseTrader` generates random order shocks with inventory mean reversion. |
| Order schema | Emits bounded stochastic buy or sell orders around current price. |

### §2.4 SlowAdapter (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Delayed information processing | `SlowAdapter` blends fundamental value with moving average and trades slowly. |
| Order schema | Emits delayed stabilizing orders after price shocks. |

### §2.5 VolatilityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-regime response | `VolatilityTrader` changes exposure when volatility crosses relative thresholds. |
| Order schema | Emits orders based on high- or low-volatility regimes. |

## §3 Market Mechanism

`Market` in `examples/VolatilityClustering/Rule/players.py` updates volatility
with bounded GARCH(1,1), aggregates signed orders, and updates price through
net-demand impact, mean reversion, and volatility-scaled noise.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/VolatilityClustering/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Direct deterministic order construction |
| Error handling | Deterministic config/schema errors fail fast |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/VolatilityClustering/Rule/simulation.yml` | Full 200-round entry point. |
| `configs/VolatilityClustering/Rule/players.yml` | GARCH market and five investor definitions. |
| `configs/VolatilityClustering/Rule/topology.yml` | Market broadcast and investor-order routing. |
| `configs/VolatilityClustering/Rule/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/VolatilityClustering/Rule/run_volatility.py -c configs/VolatilityClustering/Rule/simulation.yml
```

## §7 Expected Behavior

The run should produce finite prices, nonzero volume, persistent volatility
state, and alternating calm/high-volatility phases caused by shocks and
heterogeneous order flow.

## §8 References

See `examples/VolatilityClustering/simulation-bases.md §2` for theory and
`analysis-bases.md §2` for metric contracts.

## §9 Variant Comparison

Rule is the benchmark for GARCH and role-driven clustering. LLM, RuleLLM, and
Rag are compared against it for stochastic interpretation, rule adherence,
liquidity effects, and retrieval effects.
