# Short Squeeze Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | ShortSqueeze |
| Decision Mechanism | Deterministic rule-based trading orders |
| Theory Reference | `examples/ShortSqueeze/simulation-bases.md` |
| Market Broadcast | `configs/ShortSqueeze/Rule/topology.yml` |

The Rule variant is the deterministic benchmark. It uses five configured
archetypes: `ShortSeller`, `MomentumBuyer`, `RetailTrader`, `ValueInvestor`,
and `InstitutionalHolder`.

## §2 Theory -> Implementation Mapping

### §2.1 ShortSeller (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Forced covering | `ShortSeller` in `examples/ShortSqueeze/Rule/players.py` covers part of the short position when loss exceeds `cover_threshold`. |
| Config path | `configs/ShortSqueeze/Rule/players.yml:short_seller.config.extras`. |

### §2.2 MomentumBuyer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Positive-feedback demand | `MomentumBuyer` buys when recent momentum exceeds `momentum_threshold`. |
| Config path | `configs/ShortSqueeze/Rule/players.yml:momentum_buyer.config.extras`. |

### §2.3 RetailTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Attention-driven bullish flow | `RetailTrader` adds noisy demand shifted by `bullish_bias`. |
| Config path | `configs/ShortSqueeze/Rule/players.yml:retail.config.extras`. |

### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental resistance | `ValueInvestor` buys undervaluation and sells overvaluation relative to fundamental value. |
| Config path | `configs/ShortSqueeze/Rule/players.yml:value_investor.config.extras`. |

### §2.5 InstitutionalHolder (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Float scarcity | `InstitutionalHolder` starts with a large long position and generally withholds supply. |
| Config path | `configs/ShortSqueeze/Rule/players.yml:institutional.config.extras`. |

## §3 Market Mechanism

`Market` in `examples/ShortSqueeze/Rule/players.py` aggregates signed orders,
tracks buy-to-cover quantity through `is_short_cover`, applies extra short-cover
price impact, and records price and volume histories.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ShortSqueeze/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Direct deterministic order construction |
| Error handling | Deterministic config/schema errors fail fast |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ShortSqueeze/Rule/simulation.yml` | Full simulation entry point |
| `configs/ShortSqueeze/Rule/players.yml` | Market and five investor definitions |
| `configs/ShortSqueeze/Rule/topology.yml` | Market-to-investor routing |
| `configs/ShortSqueeze/Rule/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/ShortSqueeze/Rule/run_short_squeeze.py -c configs/ShortSqueeze/Rule/simulation.yml
```

## §7 Expected Behavior

The run should show a rally that can force short covering, additional demand
from momentum and retail roles, constrained supply from the institutional
holder, and value resistance near high price premiums.

## §8 References

See `examples/ShortSqueeze/simulation-bases.md §2` and
`examples/ShortSqueeze/analysis-bases.md §2`.

## §9 Variant Comparison

Use Rule as the deterministic benchmark when judging LLM, RuleLLM, and Rag.
