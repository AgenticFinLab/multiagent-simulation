# SouthSeaBubble RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Persona reasoning anchored by bubble/correction rules |
| Market | Same price/fundamental market as Rule |
| Agents | RuleLLM insider, narrative believer, skeptical analyst, arbitrageur, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RuleLLMInsiderAdvantaged | `simulation-bases.md §4.1` | Prompt encodes timing and privileged-information behavior |
| RuleLLMNarrativeBeliever | `simulation-bases.md §4.2` | Prompt encodes narrative/momentum behavior |
| RuleLLMSkepticalAnalyst | `simulation-bases.md §4.3` | Prompt encodes fundamental resistance |
| RuleLLMArbitrageur | `simulation-bases.md §4.4` | Prompt encodes mispricing correction |
| RuleLLMNoiseTrader | `simulation-bases.md §4.5` | Prompt encodes random baseline behavior |

## §3 Market Mechanism Implementation

Market clearing remains unchanged. RuleLLM supplies persona and quantitative
rule instructions to the LLM before canonical order parsing.

## §4 Variant-Specific Features

This variant tests whether explicit bubble and correction rules constrain LLM
narratives toward the Rule baseline.

## §5 Architecture Diagram

```text
Market state -> persona + rule prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SouthSeaBubble/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/SouthSeaBubble/RuleLLM/run_southseabubble_rulellm.py \
  -c configs/SouthSeaBubble/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve narrative demand and correction pressure while reducing
unstructured prompt drift.

## §9 References

See `../simulation-bases.md §4`, `../simulation-bases.md §9`, and
`../analysis-bases.md §2`.

