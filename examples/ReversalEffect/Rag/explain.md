# ReversalEffect Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | RuleLLM-style reversal decisions with retrieved domain knowledge |
| Market | Same market mechanics as Rule and RuleLLM |
| Knowledge Sources | Shared document corpus and RAG index |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Rag Contrarian / Value Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` and `§4.5` | Retrieved overreaction/value context is included in prompt |
| Effect | May change reversal conviction or timing |

### §2.2 Rag Momentum / Overconfidence Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` and `§4.3` | Retrieved behavioral context informs continuation pressure |
| Effect | May extend or moderate overshoot |

### §2.3 Rag Noise Agent

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Retains noisy participation under canonical schema |
| Effect | Adds baseline stochastic pressure |

## §3 Market Mechanism Implementation

Rag keeps the same market and order schema. Retrieval affects only the LLM
context used to generate investor decisions.

## §4 Variant-Specific Features

Rag requires knowledge configuration and should be reviewed for retrieval
quality in addition to execution success.

## §5 Architecture Diagram

```text
Market update -> retrieve context -> LLM decision -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/ReversalEffect/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/ReversalEffect/Rag/run_reversaleffect_rag.py \
  -c configs/ReversalEffect/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag should preserve overshoot/reversal mechanics while retrieved context changes
reasoning or confidence.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
