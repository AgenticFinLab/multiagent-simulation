# MomentumEffect Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | RuleLLM-style momentum decisions with retrieved domain knowledge |
| Market | Same market mechanics as Rule and RuleLLM |
| Knowledge Sources | Shared document corpus and RAG index |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Rag Momentum / Trend Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` and `§4.5` | Retrieved momentum/technical context is included in prompt |
| Effect | May alter trend conviction or explanation |

### §2.2 Rag Contrarian Agent

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Retrieved overreaction/reversal context informs contrarian reasoning |
| Effect | May strengthen reversal timing |

### §2.3 Rag Fundamental Anchor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Retrieved valuation context informs anchor decisions |
| Effect | May moderate momentum overshoot |

## §3 Market Mechanism Implementation

Rag keeps the same market and order schema. Retrieval changes only the context
supplied to LLM agents.

## §4 Variant-Specific Features

Rag requires knowledge setup, embedding/index configuration, and per-agent
private knowledge configuration.

## §5 Architecture Diagram

```text
Market update -> retrieve context -> LLM prompt -> decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/MomentumEffect/Rag/players.yml`, including top-level
`knowledge` and per-agent `private_knowledge.rag`.

## §7 Running Instructions

```bash
python examples/MomentumEffect/Rag/run_momentumeffect_rag.py \
  -c configs/MomentumEffect/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag should preserve momentum/reversal mechanics while retrieved evidence may
alter conviction, timing, or explanation.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
