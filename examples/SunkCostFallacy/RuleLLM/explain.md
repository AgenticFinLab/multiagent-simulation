# SunkCostFallacy RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Persona reasoning anchored by sunk-cost and rational-cutting rules |
| Market | Same price/fundamental market as Rule |
| Agents | RuleLLM sunk-cost holder, commitment escalator, rational cutter, opportunity-cost trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RuleLLMSunkCostHolder | `simulation-bases.md §4.1` | Prompt encodes refusal to realize losses |
| RuleLLMCommitmentEscalator | `simulation-bases.md §4.2` | Prompt encodes doubling down |
| RuleLLMRationalCutter | `simulation-bases.md §4.3` | Prompt encodes forward-looking cuts |
| RuleLLMOpportunityCostTrader | `simulation-bases.md §4.4` | Prompt encodes opportunity-cost reallocation |
| RuleLLMNoiseTrader | `simulation-bases.md §4.5` | Prompt encodes random baseline behavior |

## §3 Market Mechanism Implementation

Market clearing remains unchanged. RuleLLM supplies persona and quantitative
rule instructions to the LLM before canonical order parsing.

## §4 Variant-Specific Features

This variant tests whether explicit rule text constrains LLM sunk-cost
rationalizations toward the Rule baseline.

## §5 Architecture Diagram

```text
Market state -> persona + rule prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SunkCostFallacy/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/RuleLLM/run_sunkcostfallacy_rulellm.py \
  -c configs/SunkCostFallacy/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve sunk-cost holding and escalation while keeping action
schema structured.

## §9 References

See `../simulation-bases.md §4`, `../simulation-bases.md §9`, and
`../analysis-bases.md §2`.

