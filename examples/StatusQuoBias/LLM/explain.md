# StatusQuoBias LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven status quo, default, active, momentum, and noise decisions |
| Market | Same price/fundamental market as Rule |
| Agents | LLM inertial holder, default follower, active rebalancer, momentum trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| LLMInertialHolder | `simulation-bases.md §4.1` | Persona prompt emphasizes resistance to change |
| LLMDefaultFollower | `simulation-bases.md §4.2` | Persona prompt follows default allocation |
| LLMActiveRebalancer | `simulation-bases.md §4.3` | Persona prompt provides rational benchmark |
| LLMMomentumTrader | `simulation-bases.md §4.4` | Persona prompt responds to trend signals |
| LLMNoiseTrader | `simulation-bases.md §4.5` | Persona prompt supplies random baseline liquidity |

## §3 Market Mechanism Implementation

Market mechanics match Rule. LLM changes the decision generator from explicit
rules to persona reasoning and canonical order JSON.

## §4 Variant-Specific Features

LLM tests whether status quo rationalizations and default adherence emerge from
personas without changing market clearing.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/StatusQuoBias/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/StatusQuoBias/LLM/run_statusquobias_llm.py \
  -c configs/StatusQuoBias/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Inertial and default personas should underreact relative to active and momentum
personas.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

