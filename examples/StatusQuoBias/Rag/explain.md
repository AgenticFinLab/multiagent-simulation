# StatusQuoBias Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | Retrieved behavioral-finance context plus LLM status quo reasoning |
| Market | Same price/fundamental market as Rule |
| Agents | Rag inertial holder, default follower, active rebalancer, momentum trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RagLLMInertialHolder | `simulation-bases.md §4.1` | Retrieval may reinforce inaction/default evidence |
| RagLLMDefaultFollower | `simulation-bases.md §4.2` | Retrieval may contextualize default effects |
| RagLLMActiveRebalancer | `simulation-bases.md §4.3` | Retrieval may support rational rebalancing |
| RagLLMMomentumTrader | `simulation-bases.md §4.4` | Retrieval may contextualize trend following |
| RagLLMNoiseTrader | `simulation-bases.md §4.5` | Baseline liquidity remains low-information |

## §3 Market Mechanism Implementation

Rag leaves market clearing unchanged. Retrieved context is inserted into the
LLM decision prompt before canonical order parsing.

## §4 Variant-Specific Features

Rag tests whether behavioral evidence about defaults and inertia changes LLM
underreaction or active rebalancing.

## §5 Architecture Diagram

```text
Market state -> retrieve context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/StatusQuoBias/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/StatusQuoBias/Rag/run_statusquobias_rag.py \
  -c configs/StatusQuoBias/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag may make status quo rationalizations more evidence-grounded or improve
active rebalancing explanations.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

