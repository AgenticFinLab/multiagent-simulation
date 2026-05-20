# TulipMania Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic trend chasing, social proof, valuation resistance, early exit, and noise rules |
| Market | Price/fundamental market with mania and correction dynamics |
| Agents | TrendChaser, SocialProofFollower, IntrinsicValueTrader, EarlyExitTrader, NoiseTrader |
| Runtime Change | Documentation-only rewrite of existing Rule guide; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| TrendChaser | `simulation-bases.md §4.1` | Rule class buys rising prices |
| SocialProofFollower | `simulation-bases.md §4.2` | Rule class follows crowd participation |
| IntrinsicValueTrader | `simulation-bases.md §4.3` | Rule class sells extreme overvaluation |
| EarlyExitTrader | `simulation-bases.md §4.4` | Rule class exits before collapse |
| NoiseTrader | `simulation-bases.md §4.5` | Rule class supplies stochastic background liquidity |

## §3 Market Mechanism Implementation

The Rule variant implements the shared market in `players.py`. Orders from
trend, social-proof, value, early-exit, and noise agents are cleared by the
market player and update price relative to intrinsic/fundamental value.

## §4 Rule Variant-Specific Features

All investor decisions are encoded in Python thresholds and sizing rules. This
variant provides the deterministic baseline for comparing LLM, RuleLLM, and Rag
behavior.

## §5 Architecture Diagram

```text
Market broadcast -> rule investor decide() -> order dict -> Market clearing
```

## §6 Configuration Reference

Primary config: `configs/TulipMania/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/TulipMania/Rule/run_tulipmania.py \
  -c configs/TulipMania/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Trend and social-proof agents should amplify mania; intrinsic-value and
early-exit agents should provide correction pressure.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
