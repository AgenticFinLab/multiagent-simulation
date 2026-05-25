# SouthSeaBubble Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | SouthSeaBubble |
| Decision Mechanism | Deterministic current-market equity quantity orders |
| Theory Reference | `examples/SouthSeaBubble/simulation-bases.md` |
| Market Broadcast | `configs/SouthSeaBubble/Rule/topology.yml` |

SouthSeaBubble uses current-market quantity orders: `action`, `quantity`, and
`agent_type`. The market aggregates net demand and does not consume limit prices.

## §2 Theory -> Implementation Mapping

### §2.1 InsiderAdvantaged (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Insider timing advantage | `InsiderAdvantaged` activates when `abs(deviation) > 0.02`. |
| Quantity rule | `min(800, int(abs(deviation) * 5000))`, constrained by cash/inventory. |
| Config link | Portfolio fields plus insider metadata from `configs/SouthSeaBubble/Rule/players.yml`. |

### §2.2 NarrativeBeliever (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Narrative-driven bubble demand | `NarrativeBeliever` follows the same 2% deviation trigger and 800-unit cap. |
| Quantity rule | Buys positive deviation and sells negative deviation after constraints. |
| Config link | Portfolio fields plus narrative metadata. |

### §2.3 SkepticalAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Fundamental skepticism | `SkepticalAnalyst` activates when `abs(deviation) > 0.05`. |
| Quantity rule | `min(500, int(abs(deviation) * 3000))`, leaning against mispricing. |
| Config link | Portfolio fields plus cash-flow metadata. |

### §2.4 Arbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Mispricing correction | `Arbitrageur` uses the same 5% activation and 500-unit cap as skeptical analysts. |
| Quantity rule | Buys underpricing and sells overpricing subject to constraints. |
| Config link | Portfolio fields plus spread/arbitrage metadata. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | `NoiseTrader` trades randomly in about 30% of rounds. |
| Quantity rule | Random direction and quantity 100-500. |
| Config link | Portfolio fields plus noise metadata. |

## §3 Market Mechanism

The Rule market broadcasts price/fundamental state and clears current-market
quantity orders through net-demand impact, mean reversion, and noise.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SouthSeaBubble/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Deterministic decision construction |
| Error handling | Deterministic config/topology/schema errors fail fast |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SouthSeaBubble/Rule/simulation.yml` | 200-round simulation entry point |
| `configs/SouthSeaBubble/Rule/players.yml` | Market, portfolio, and role parameters |
| `configs/SouthSeaBubble/Rule/topology.yml` | Message routing |
| `configs/SouthSeaBubble/Rule/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SouthSeaBubble/Rule/run_southseabubble.py -c configs/SouthSeaBubble/Rule/simulation.yml
```

## §7 Expected Behavior

Narrative and insider roles should contribute bubble pressure; skeptical and
arbitrage roles should oppose mispricing; noise traders should add stochastic
background flow.

## §8 References

See `examples/SouthSeaBubble/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Rule is the baseline for API variants on bubble magnitude, attribution, crash
timing, and quality metrics.
