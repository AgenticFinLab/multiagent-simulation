# SouthSeaBubble Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic narrative bubble, insider timing, skepticism, and arbitrage rules |
| Market | Price/fundamental market with narrative-driven demand |
| Agents | InsiderAdvantaged, NarrativeBeliever, SkepticalAnalyst, Arbitrageur, NoiseTrader |
| Runtime Change | Documentation-only rewrite of existing Rule guide; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| InsiderAdvantaged | `simulation-bases.md §4.1` | Rule class models privileged timing and early exit |
| NarrativeBeliever | `simulation-bases.md §4.2` | Rule class converts promotional narrative into demand |
| SkepticalAnalyst | `simulation-bases.md §4.3` | Rule class resists overpricing using fundamentals |
| Arbitrageur | `simulation-bases.md §4.4` | Rule class trades against large mispricing |
| NoiseTrader | `simulation-bases.md §4.5` | Rule class supplies stochastic background liquidity |

## §3 Market Mechanism Implementation

The Rule variant implements the shared market in `players.py`. Orders from
narrative, insider, skeptical, and arbitrage agents are cleared by the market
player and update price relative to fundamental value.

## §4 Rule Variant-Specific Features

All investor decisions are encoded in Python thresholds and sizing rules. This
variant provides the deterministic baseline for comparing LLM, RuleLLM, and Rag
behavior.

## §5 Architecture Diagram

```text
Market broadcast -> rule investor decide() -> order dict -> Market clearing
```

## §6 Configuration Reference

Primary config: `configs/SouthSeaBubble/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/SouthSeaBubble/Rule/run_southseabubble.py \
  -c configs/SouthSeaBubble/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Narrative and insider agents should push prices away from fundamentals while
skeptical and arbitrage agents create correction pressure.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
