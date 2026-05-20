# SunkCostFallacy LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven sunk-cost, escalation, rational, opportunity-cost, and noise decisions |
| Market | Same price/fundamental market as Rule |
| Agents | LLM sunk-cost holder, commitment escalator, rational cutter, opportunity-cost trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| LLMSunkCostHolder | `simulation-bases.md §4.1` | Persona prompt resists realizing losses |
| LLMCommitmentEscalator | `simulation-bases.md §4.2` | Persona prompt doubles down on losses |
| LLMRationalCutter | `simulation-bases.md §4.3` | Persona prompt ignores sunk costs |
| LLMOpportunityCostTrader | `simulation-bases.md §4.4` | Persona prompt reallocates by opportunity cost |
| LLMNoiseTrader | `simulation-bases.md §4.5` | Persona prompt supplies random baseline liquidity |

## §3 Market Mechanism Implementation

Market mechanics match Rule. LLM changes the decision generator from explicit
rules to persona reasoning and canonical order JSON.

## §4 Variant-Specific Features

LLM tests whether sunk-cost rationalizations and escalation emerge from
personas without changing market clearing.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SunkCostFallacy/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/LLM/run_sunkcostfallacy_llm.py \
  -c configs/SunkCostFallacy/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Sunk-cost and escalation personas should hold or add to losers; rational and
opportunity-cost personas should exit or reallocate.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

