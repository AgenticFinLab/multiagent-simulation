# VolatilityClustering Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | RuleLLM-style volatility-regime decisions with retrieved domain knowledge |
| Market | Same market mechanics as Rule and RuleLLM |
| Knowledge Sources | Shared document corpus and RAG index |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Rag Fundamentalist

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Retrieved valuation context informs stabilizing decisions |
| Effect | May moderate volatility-driven mispricing |

### §2.2 Rag Trend / Volatility Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` and `§4.5` | Retrieved volatility-clustering context informs trend/regime decisions |
| Effect | May alter high-volatility response |

### §2.3 Rag Noise / Slow-Adapter Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` and `§4.4` | Retrieved context is added while preserving stochastic/adaptive roles |
| Effect | Should not break order schema |

## §3 Market Mechanism Implementation

Rag keeps market and order schema aligned with RuleLLM. Retrieval changes only
the prompt context for LLM decisions.

## §4 Variant-Specific Features

Rag adds retrieval quality and embedding/index setup to execution and quality
review.

## §5 Architecture Diagram

```text
Market volatility state -> retrieve context -> LLM decision -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/VolatilityClustering/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/VolatilityClustering/Rag/run_volatilityclustering_rag.py \
  -c configs/VolatilityClustering/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag should preserve volatility clustering while retrieved volatility-model
context may affect regime interpretation.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
