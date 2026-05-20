# SunkCostFallacy Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic sunk-cost holding, commitment escalation, rational cutting, and opportunity-cost rules |
| Market | Price/fundamental market with loss-state behavior |
| Agents | SunkCostHolder, CommitmentEscalator, RationalCutter, OpportunityCostTrader, NoiseTrader |
| Runtime Change | Documentation-only rewrite of existing Rule guide; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| SunkCostHolder | `simulation-bases.md §4.1` | Rule class refuses to realize losing positions |
| CommitmentEscalator | `simulation-bases.md §4.2` | Rule class adds exposure after losses |
| RationalCutter | `simulation-bases.md §4.3` | Rule class cuts based on future value |
| OpportunityCostTrader | `simulation-bases.md §4.4` | Rule class reallocates capital by opportunity cost |
| NoiseTrader | `simulation-bases.md §4.5` | Rule class supplies stochastic background liquidity |

## §3 Market Mechanism Implementation

The Rule variant implements the shared market in `players.py`. Orders from
sunk-cost, escalation, rational, opportunity-cost, and noise agents are cleared
by the market player and update price relative to fundamental value.

## §4 Rule Variant-Specific Features

All investor decisions are encoded in Python thresholds and sizing rules. This
variant provides the deterministic baseline for comparing LLM, RuleLLM, and Rag
behavior.

## §5 Architecture Diagram

```text
Market broadcast -> rule investor decide() -> order dict -> Market clearing
```

## §6 Configuration Reference

Primary config: `configs/SunkCostFallacy/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/Rule/run_sunkcostfallacy.py \
  -c configs/SunkCostFallacy/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Sunk-cost and commitment agents should hold or add to losers; rational and
opportunity-cost agents should cut or reallocate.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
