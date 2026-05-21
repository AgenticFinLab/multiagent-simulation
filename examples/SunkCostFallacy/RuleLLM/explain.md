# SunkCostFallacy RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona plus explicit sunk-cost, escalation, rational-cutting, and opportunity-cost rules |
| Key Difference from Other Variants | LLM reasoning is anchored by rule text while still producing natural-language analysis. |
| Primary Research Contribution | Tests whether explicit behavioral rules constrain LLM sunk-cost decisions. |
| Files | `players.py`, `prompts.py`, `run_sunkcostfallacy_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Agent | Root Section | Implementation |
|---|---|---|
| `RuleLLMSunkCostHolder` | `simulation-bases.md §4.1` | Prompt separates persona from rules that avoid selling losing positions. |
| `RuleLLMCommitmentEscalator` | `simulation-bases.md §4.2` | Prompt encodes averaging-down and commitment reinforcement. |
| `RuleLLMRationalCutter` | `simulation-bases.md §4.3` | Prompt encodes forward-looking valuation actions. |
| `RuleLLMOpportunityCostTrader` | `simulation-bases.md §4.4` | Prompt encodes opportunity-cost reallocation. |
| `RuleLLMNoiseTrader` | `simulation-bases.md §4.5` | Prompt encodes small random liquidity behavior. |

## §3 Market Mechanism Implementation

The RuleLLM variant reuses the Rule market. Formula, order aggregation, and
market broadcasts match `simulation-bases.md §3.1`.

## §4 RuleLLM Variant-Specific Features

System prompts contain `== PERSONA ==` and `== DECISION RULES ==` sections.
The decision rules are guidance for the LLM, not executable code. The returned
decision must satisfy the same canonical parser contract as LLM and Rag.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
RuleLLMInvestor._build_prompt(market + portfolio state)
        |
        v
System prompt: persona + decision rules
        |
        v
LLM response -> parser -> _validate_decision() -> order -> Market
```

## §6 Configuration Reference

| Parameter | Config Path | Purpose |
|---|---|---|
| `lm_name` | `*.extras.llm.lm_name` | ARK model for RuleLLM decisions. |
| `generation_config.temperature` | `*.extras.llm.generation_config.temperature` | Role-specific stochasticity. |
| Strategy parameters | `*.extras` | Preserve traceability to `simulation-bases.md §6`. |

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/RuleLLM/run_sunkcostfallacy_rulellm.py \
  -c configs/SunkCostFallacy/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should remain closer to Rule than LLM in action direction while still
producing auditable natural-language reasoning.

## §9 References

Prompt design traces to `../simulation-bases.md §4` and `../simulation-bases.md §9`.
Metrics trace to `../analysis-bases.md §2`.
