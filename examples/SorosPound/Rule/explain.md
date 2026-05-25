# SorosPound Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | SorosPound |
| Decision Mechanism | Deterministic current-market currency quantity orders |
| Theory Reference | `examples/SorosPound/simulation-bases.md` |
| Market Broadcast | `configs/SorosPound/Rule/topology.yml` |

SorosPound uses a current-market quantity schema: `action`, `quantity`, and
`agent_type`. The market does not consume `bid_price`; it aggregates net demand
and updates a sterling proxy.

## §2 Theory -> Implementation Mapping

### §2.1 MacroHedgeFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Speculative attack role | `MacroHedgeFund` activates when `abs(deviation) > 0.02`. |
| Quantity rule | `min(800, int(abs(deviation) * 5000))`, constrained by cash or inventory. |
| Config link | Uses portfolio fields plus macro metadata in `configs/SorosPound/Rule/players.yml`. |

### §2.2 PegDefender (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Stabilizing intervention | `PegDefender` activates when `abs(deviation) > 0.05`. |
| Quantity rule | `min(500, int(abs(deviation) * 3000))`, leaning against deviation. |
| Config link | Uses portfolio fields plus reserve/defense metadata. |

### §2.3 ConvergenceTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Peg-stability belief trade | `ConvergenceTrader` supplies intermittent mixed flow. |
| Quantity rule | Trades in 30% of rounds with random direction and quantity 100-500. |
| Config link | Uses portfolio fields plus convergence metadata. |

### §2.4 OpportunisticTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Attack follower / herding role | `OpportunisticTrader` follows visible pressure after `abs(deviation) > 0.02`. |
| Quantity rule | Same retained scale as macro attacker: `min(800, int(abs(deviation) * 5000))`. |
| Config link | Uses portfolio fields plus attack-join metadata. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | `NoiseTrader` adds random low-information flow. |
| Quantity rule | Trades in 30% of rounds with random direction and quantity 100-500. |
| Config link | Uses portfolio fields plus noise metadata. |

## §3 Market Mechanism

`Market` in `examples/SorosPound/Rule/players.py` broadcasts current price,
fundamental value, deviation, volume, and net demand. It then clears
current-market quantities from investors and updates price using `price_impact`,
`mean_reversion`, and `noise_std`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SorosPound/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Direct deterministic decision construction |
| Error handling | Config, topology, and schema errors fail fast |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SorosPound/Rule/simulation.yml` | 200-round simulation entry point |
| `configs/SorosPound/Rule/players.yml` | Market, portfolio, and role parameters |
| `configs/SorosPound/Rule/topology.yml` | Market update and investor order routing |
| `configs/SorosPound/Rule/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SorosPound/Rule/run_sorospound.py -c configs/SorosPound/Rule/simulation.yml
```

## §7 Expected Behavior

- Attack pressure should become visible when deviation crosses the retained
  thresholds.
- Peg defense should lean against larger deviations.
- Convergence and noise traders should create background flow.
- A full accepted sample must complete 200 rounds and pass Level-2 structural
  quality review.

## §8 References

See `examples/SorosPound/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Rule is the baseline for comparing API variants on attack pressure, defense
effectiveness, herding share, and break timing.
