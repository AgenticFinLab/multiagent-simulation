# SorosPound Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | Retrieved domain context plus LLM currency-crisis reasoning |
| Market | Same price/fundamental market as Rule |
| Agents | Rag macro fund, peg defender, convergence trader, opportunistic trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

Rag maps the five `simulation-bases.md §4` archetypes to LLM decisions
augmented by retrieved crisis context.

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RagLLMMacroHedgeFund | `§4.1` | Retrieval may reinforce speculative-attack logic |
| RagLLMPegDefender | `§4.2` | Retrieval may supply defense and reserve context |
| RagLLMConvergenceTrader | `§4.3` | Retrieval may contextualize peg-stability beliefs |
| RagLLMOpportunisticTrader | `§4.4` | Retrieval may emphasize herding and attack timing |
| RagLLMNoiseTrader | `§4.5` | Baseline liquidity remains low-information |

## §3 Market Mechanism Implementation

Rag leaves market clearing unchanged. Retrieved context is inserted into the
LLM decision prompt before canonical order parsing.

## §4 Variant-Specific Features

Rag tests whether historical currency-crisis knowledge changes attack timing,
defense persistence, or convergence confidence.

## §5 Architecture Diagram

```text
Market state -> retrieve context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SorosPound/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/SorosPound/Rag/run_sorospound_rag.py \
  -c configs/SorosPound/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag may strengthen speculative attack or defense reasoning depending on the
retrieved crisis evidence.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

