# SunkCostFallacy Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | Retrieved behavioral-finance context plus LLM sunk-cost reasoning |
| Market | Same price/fundamental market as Rule |
| Agents | Rag sunk-cost holder, commitment escalator, rational cutter, opportunity-cost trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RagLLMSunkCostHolder | `simulation-bases.md §4.1` | Retrieval may reinforce sunk-cost evidence |
| RagLLMCommitmentEscalator | `simulation-bases.md §4.2` | Retrieval may contextualize escalation |
| RagLLMRationalCutter | `simulation-bases.md §4.3` | Retrieval may support forward-looking logic |
| RagLLMOpportunityCostTrader | `simulation-bases.md §4.4` | Retrieval may support reallocation reasoning |
| RagLLMNoiseTrader | `simulation-bases.md §4.5` | Baseline liquidity remains low-information |

## §3 Market Mechanism Implementation

Rag leaves market clearing unchanged. Retrieved context is inserted into the
LLM decision prompt before canonical order parsing.

## §4 Variant-Specific Features

Rag tests whether behavioral evidence changes sunk-cost persistence or rational
cutting.

## §5 Architecture Diagram

```text
Market state -> retrieve context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SunkCostFallacy/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/Rag/run_sunkcostfallacy_rag.py \
  -c configs/SunkCostFallacy/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag may make sunk-cost rationalizations more evidence-grounded or strengthen
rational opportunity-cost corrections.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

