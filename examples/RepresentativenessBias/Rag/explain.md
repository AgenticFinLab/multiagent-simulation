# RepresentativenessBias Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | Representativeness decisions augmented with retrieved behavioral-finance context |
| Market | Same market as Rule/LLM/RuleLLM |
| Knowledge Sources | Shared document corpus and RAG index |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Rag Pattern And Category Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` and `§4.2` | Retrieved representativeness/base-rate context is added to prompt |
| Effect | May temper or amplify prototype/category reasoning |

### §2.2 Rag Bayesian And Contrarian Agents

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` and `§4.4` | Retrieved statistical reasoning context informs correction |
| Effect | May strengthen base-rate discipline |

### §2.3 Rag Noise Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Keeps baseline stochastic participation |
| Effect | Should preserve valid order schema |

## §3 Market Mechanism Implementation

Rag preserves the same market and order schema. Retrieval changes the context
available to LLM agents.

## §4 Variant-Specific Features

Rag requires retrieval quality review in addition to execution and parser
quality checks.

## §5 Architecture Diagram

```text
Market state -> retrieve context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/RepresentativenessBias/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/RepresentativenessBias/Rag/run_representativenessbias_rag.py \
  -c configs/RepresentativenessBias/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Retrieved base-rate evidence may reduce representativeness bias, while retrieved
examples may also make salient prototypes more compelling.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
