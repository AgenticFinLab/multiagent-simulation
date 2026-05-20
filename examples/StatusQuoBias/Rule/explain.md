# StatusQuoBias Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic inertia, default-following, rebalancing, momentum, and noise rules |
| Market | Price/fundamental market with signal underreaction |
| Agents | InertialHolder, DefaultFollower, ActiveRebalancer, MomentumTrader, NoiseTrader |
| Runtime Change | Documentation-only rewrite of existing Rule guide; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| InertialHolder | `simulation-bases.md §4.1` | Rule class holds unless evidence is strong |
| DefaultFollower | `simulation-bases.md §4.2` | Rule class stays near default allocation |
| ActiveRebalancer | `simulation-bases.md §4.3` | Rule class responds directly to signals |
| MomentumTrader | `simulation-bases.md §4.4` | Rule class follows trend signals |
| NoiseTrader | `simulation-bases.md §4.5` | Rule class supplies stochastic background liquidity |

## §3 Market Mechanism Implementation

The Rule variant implements the shared market in `players.py`. Orders from
inertial, default, active, momentum, and noise agents are cleared by the market
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

Primary config: `configs/StatusQuoBias/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/StatusQuoBias/Rule/run_statusquobias.py \
  -c configs/StatusQuoBias/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Inertial and default agents should underreact to signals; active and momentum
agents should create faster adjustment.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
