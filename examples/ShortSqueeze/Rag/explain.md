# ShortSqueeze Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | RuleLLM-style squeeze decisions with retrieved short-squeeze context |
| Market | Same squeeze market as Rule and RuleLLM |
| Knowledge Sources | Shared document corpus and RAG index |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Rag ShortSeller

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Retrieved short-sale constraint context informs covering |
| Effect | May change urgency or explanation |

### §2.2 Rag Retail / Momentum Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` and `§4.3` | Retrieved squeeze precedent informs crowd/momentum reasoning |
| Effect | May amplify or moderate buy pressure |

### §2.3 Rag Value / Institutional Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` and `§4.5` | Retrieved valuation/float context informs resistance and holding |
| Effect | May change stabilization timing |

## §3 Market Mechanism Implementation

Rag preserves the same market and order schema as RuleLLM. Retrieval changes
the context supplied to LLM agents.

## §4 Variant-Specific Features

Rag adds retrieval quality as a post-run concern in addition to execution
success.

## §5 Architecture Diagram

```text
Market squeeze state -> retrieve context -> LLM decision -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/ShortSqueeze/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/ShortSqueeze/Rag/run_shortsqueeze_rag.py \
  -c configs/ShortSqueeze/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Retrieved historical squeeze context may alter covering urgency, retail
coordination, or value resistance while preserving valid decisions.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
