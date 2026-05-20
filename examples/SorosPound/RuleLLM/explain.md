# SorosPound RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Persona reasoning anchored by explicit speculative-attack rules |
| Market | Same price/fundamental market as Rule |
| Agents | RuleLLM macro fund, peg defender, convergence trader, opportunistic trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

RuleLLM maps the same five archetypes from `simulation-bases.md §4` to prompts
with `== PERSONA ==` and `== DECISION RULES ==` sections.

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RuleLLMMacroHedgeFund | `§4.1` | Quantitative attack rules in `prompts.py` |
| RuleLLMPegDefender | `§4.2` | Defense thresholds in `prompts.py` |
| RuleLLMConvergenceTrader | `§4.3` | Peg-stability persona and rule guidance |
| RuleLLMOpportunisticTrader | `§4.4` | Momentum-attack rule guidance |
| RuleLLMNoiseTrader | `§4.5` | Random baseline rule guidance |

## §3 Market Mechanism Implementation

Market clearing remains unchanged. RuleLLM changes only the decision interface:
the LLM receives quantitative rules and returns canonical order JSON.

## §4 Variant-Specific Features

This variant tests whether explicit attack/defense rules reduce drift relative
to persona-only LLM behavior while preserving natural-language reasoning.

## §5 Architecture Diagram

```text
Market state -> persona + rule prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SorosPound/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/SorosPound/RuleLLM/run_sorospound_rulellm.py \
  -c configs/SorosPound/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should stay closer to threshold-driven attack and defense behavior than
LLM while still producing explanatory reasoning.

## §9 References

See `../simulation-bases.md §4`, `../simulation-bases.md §9`, and
`../analysis-bases.md §2`.

