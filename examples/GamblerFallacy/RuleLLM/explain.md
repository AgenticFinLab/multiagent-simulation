# GamblerFallacy RuleLLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | LLM reasoning with persona and embedded decision-rule text |
| Key Difference from Other Variants | Makes streak-bias rules explicit in prompts while retaining model reasoning. |
| Primary Research Contribution | Tests whether rule-anchored language reasoning changes streak-bias dynamics relative to Rule. |
| Files | `players.py`, `prompts.py`, `run_gamblerfallacy_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### RuleLLMStreakReversalTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `RuleLLMStreakReversalTrader`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | System prompt includes `== PERSONA ==` and `== DECISION RULES ==`. |
| Mathematical model → sim-bases §4.1.4.3 | Prompt expresses thresholded streak-response guidance. |
| State variables → sim-bases §4.1.4.3 | User template injects market and portfolio state. |
| Parameters → sim-bases §6 | Model and portfolio settings are config supplied. |
| LLM persona → sim-bases §4.1.4.4 | Persona expresses reversal expectation after streaks. |

### RuleLLMHotHandTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `RuleLLMHotHandTrader`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | Prompt embeds hot-hand continuation reasoning. |
| Mathematical model → sim-bases §4.2.4.3 | Prompt guidance is converted by the LLM into canonical decision JSON. |
| State variables → sim-bases §4.2.4.3 | Uses current price, fundamental, deviation, cash, and position. |
| Parameters → sim-bases §6 | Config supplies runtime settings. |
| LLM persona → sim-bases §4.2.4.4 | Persona emphasizes continuation after perceived streaks. |

### RuleLLMIndependentAssessor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `RuleLLMIndependentAssessor`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Prompt embeds independent-assessment logic. |
| Mathematical model → sim-bases §4.3.4.3 | Parsed trades remain bounded by portfolio constraints. |
| State variables → sim-bases §4.3.4.3 | Same market state as Rule and LLM. |
| Parameters → sim-bases §6 | LLM and portfolio settings are config supplied. |
| LLM persona → sim-bases §4.3.4.4 | Persona rejects streak superstition. |

### RuleLLMArbitrageur: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `RuleLLMArbitrageur`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Prompt describes correction of streak-driven mispricing. |
| Mathematical model → sim-bases §4.4.4.3 | LLM action is parsed and capped before order emission. |
| State variables → sim-bases §4.4.4.3 | Uses injected market and portfolio state. |
| Parameters → sim-bases §6 | Config controls model and portfolio. |
| LLM persona → sim-bases §4.4.4.4 | Persona is arbitrage-focused. |

### RuleLLMNoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `RuleLLMNoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Prompt preserves noisy liquidity behavior. |
| Mathematical model → sim-bases §4.5.4.3 | Parsed decision is bounded by portfolio constraints. |
| State variables → sim-bases §4.5.4.3 | Uses market and portfolio fields. |
| Parameters → sim-bases §6 | Config controls model temperature and portfolio. |
| LLM persona → sim-bases §4.5.4.4 | Persona remains non-systematic. |

## §3 Market Mechanism Implementation

RuleLLM imports the Rule `Market`, so market clearing and broadcasts are unchanged. Differences from Rule come from LLM interpretation of embedded rules.

## §4 RuleLLM Variant-Specific Features

- Prompts use mandatory `== PERSONA ==` and `== DECISION RULES ==` sections.
- Decision JSON includes `action`, `bid_price`, `quantity`, and `reasoning`.
- Parsed orders are capped by cash, holdings, and max quantity.
- Parse failures raise runtime errors rather than silent fallback holds.

## §5 Architecture Diagram

```text
Market broadcast -> RuleLLM prompt -> LLM response -> parser -> capped order -> Market
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/GamblerFallacy/RuleLLM/simulation.yml` | Full-run settings |
| `configs/GamblerFallacy/RuleLLM/players.yml` | LLM model, prompt refs, class paths, portfolio values |
| `configs/GamblerFallacy/RuleLLM/topology.yml` | Star topology |
| `configs/GamblerFallacy/RuleLLM/persona.yml` | Shared proxy/storage settings |

## §7 Expected Runtime Outputs

Accepted RuleLLM runs should complete 200 rounds with valid decision JSON and no fallback-hold distortion.

## §8 Validation Checklist

- All prompt constants load.
- Prompt/parser contract checks should report zero issues.
- Runtime prompt and player semantics should remain stable unless a documented mechanism or contract defect is found.

## §9 Cross-Variant Comparison Notes

RuleLLM is compared against Rule to isolate language-reasoning effects under aligned rules and against LLM to measure the stabilizing value of explicit decision-rule guidance.
