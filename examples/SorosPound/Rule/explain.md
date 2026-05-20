# SorosPound Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic speculative-attack and peg-defense rules |
| Market | Price/fundamental market with peg-pressure dynamics |
| Agents | MacroHedgeFund, PegDefender, ConvergenceTrader, OpportunisticTrader, NoiseTrader |
| Runtime Change | Documentation-only rewrite of existing Rule guide; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| MacroHedgeFund | `simulation-bases.md §4.1` | Rule class builds directional pressure against an unsustainable peg |
| PegDefender | `simulation-bases.md §4.2` | Rule class offsets pressure with stabilizing intervention |
| ConvergenceTrader | `simulation-bases.md §4.3` | Rule class represents capital betting the peg holds |
| OpportunisticTrader | `simulation-bases.md §4.4` | Rule class joins visible speculative pressure |
| NoiseTrader | `simulation-bases.md §4.5` | Rule class supplies stochastic background liquidity |

## §3 Market Mechanism Implementation

The Rule variant implements the shared market in `players.py`. Orders from
investors are cleared by the market player and update price relative to
fundamental/peg pressure. The implementation corresponds to
`simulation-bases.md §3`.

## §4 Rule Variant-Specific Features

All investor decisions are encoded in Python thresholds and sizing rules. This
variant provides the deterministic baseline for comparing LLM, RuleLLM, and Rag
behavior.

## §5 Architecture Diagram

```text
Market broadcast -> rule investor decide() -> order dict -> Market clearing
```

## §6 Configuration Reference

Primary config: `configs/SorosPound/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/SorosPound/Rule/run_sorospound.py \
  -c configs/SorosPound/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Macro and opportunistic agents should increase attack pressure; PegDefender and
ConvergenceTrader should resist until credibility weakens.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
