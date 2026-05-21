# SunkCostFallacy LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona-only LLM prompts with canonical trading JSON |
| Key Difference from Other Variants | Language-model personas produce sunk-cost or rational behavior without direct Python decision formulas. |
| Primary Research Contribution | Tests whether LLM personas rationalize holding losers or escalating commitment. |
| Files | `players.py`, `prompts.py`, `run_sunkcostfallacy_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Agent | Root Section | Implementation |
|---|---|---|
| `LLMSunkCostHolder` | `simulation-bases.md §4.1` | `LLM_SUNK_COST_HOLDER_SYS` frames prior investment as psychologically binding. |
| `LLMCommitmentEscalator` | `simulation-bases.md §4.2` | `LLM_COMMITMENT_ESCALATOR_SYS` encourages averaging down after losses. |
| `LLMRationalCutter` | `simulation-bases.md §4.3` | `LLM_RATIONAL_CUTTER_SYS` emphasizes forward-looking valuation. |
| `LLMOpportunityCostTrader` | `simulation-bases.md §4.4` | `LLM_OPPORTUNITY_COST_TRADER_SYS` emphasizes best alternative use of capital. |
| `LLMNoiseTrader` | `simulation-bases.md §4.5` | `LLM_NOISE_TRADER_SYS` represents low-information liquidity. |

All LLM investors use `LLMInvestor._build_prompt()` to supply current price,
fundamental value, deviation, cash, position, and portfolio value.

## §3 Market Mechanism Implementation

The LLM variant reuses `Market` from `SunkCostFallacy.Rule.players`. Market
clearing is unchanged; only the investor decision generator changes.

## §4 LLM Variant-Specific Features

The system prompt defines persona and behavioral guidance. The user prompt
requires `<analysis>` and `<decision>` sections. `_validate_decision()` rejects
missing or invalid `action`, `bid_price`, `quantity`, or `reasoning` after
bounded retries.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
LLMInvestor._build_prompt(market + portfolio state)
        |
        v
LangChainAPIInference -> parse_llm_response_with_thinking()
        |
        v
_validate_decision() -> canonical order -> Market
```

## §6 Configuration Reference

| Parameter | Config Path | Purpose |
|---|---|---|
| `lm_name` | `*.extras.llm.lm_name` | ARK model used for LLM decisions. |
| `generation_config.temperature` | `*.extras.llm.generation_config.temperature` | Persona-specific stochasticity. |
| `generation_config.max_tokens` | `*.extras.llm.generation_config.max_tokens` | Response-length guard. |
| `initial_cash` / `initial_position` | `*.extras` | Portfolio constraints. |

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/LLM/run_sunkcostfallacy_llm.py \
  -c configs/SunkCostFallacy/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Biased personas should explain holding or averaging down in losing states.
Rational personas should explain valuation or opportunity-cost reasoning.
Invalid output should fail after bounded retries.

## §9 References

Persona design traces to `../simulation-bases.md §4` and variant rationale to
`../simulation-bases.md §9`. Analysis uses `../analysis-bases.md §2`.
