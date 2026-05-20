# SouthSeaBubble Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | Retrieved bubble context plus LLM narrative/correction reasoning |
| Market | Same price/fundamental market as Rule |
| Agents | Rag insider, narrative believer, skeptical analyst, arbitrageur, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RagLLMInsiderAdvantaged | `simulation-bases.md §4.1` | Retrieval may contextualize insider timing |
| RagLLMNarrativeBeliever | `simulation-bases.md §4.2` | Retrieval may reinforce promotional narratives |
| RagLLMSkepticalAnalyst | `simulation-bases.md §4.3` | Retrieval may supply fundamental skepticism |
| RagLLMArbitrageur | `simulation-bases.md §4.4` | Retrieval may strengthen correction logic |
| RagLLMNoiseTrader | `simulation-bases.md §4.5` | Baseline liquidity remains low-information |

## §3 Market Mechanism Implementation

Rag leaves market clearing unchanged. Retrieved context is inserted into the
LLM decision prompt before canonical order parsing.

## §4 Variant-Specific Features

Rag tests whether historical bubble knowledge alters narrative demand,
skeptical resistance, or correction timing.

## §5 Architecture Diagram

```text
Market state -> retrieve context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SouthSeaBubble/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/SouthSeaBubble/Rag/run_southseabubble_rag.py \
  -c configs/SouthSeaBubble/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag may ground bubble reasoning in historical analogies and change the balance
between narrative and skeptical agents.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

