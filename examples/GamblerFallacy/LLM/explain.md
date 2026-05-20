# GamblerFallacy LLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona-only LLM reasoning over current market and portfolio state |
| Key Difference from Other Variants | Bias expression comes from prompts rather than deterministic rule branches. |
| Primary Research Contribution | Tests whether LLM personas reproduce gambler's-fallacy and hot-hand behavior without executable rules. |
| Files | `players.py`, `prompts.py`, `run_gamblerfallacy_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### LLMStreakReversalTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `LLMStreakReversalTrader`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | System prompt defines a streak-reversal-oriented persona. |
| Mathematical model → sim-bases §4.1.4.3 | User prompt supplies price, fundamental, deviation, cash, position, and portfolio value. |
| State variables → sim-bases §4.1.4.3 | `LLMInvestor.perceive()` stores market and portfolio fields. |
| Parameters → sim-bases §6 | LLM model, temperature, and portfolio settings are loaded from `players.yml`. |
| LLM persona → sim-bases §4.1.4.4 | Prompt expresses belief that streaks are due for reversal. |

### LLMHotHandTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `LLMHotHandTrader`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | Prompt describes continuation belief after recent streaks. |
| Mathematical model → sim-bases §4.2.4.3 | Parsed decision is bounded by portfolio constraints. |
| State variables → sim-bases §4.2.4.3 | Uses the same market fields as Rule. |
| Parameters → sim-bases §6 | Config supplies LLM and portfolio settings. |
| LLM persona → sim-bases §4.2.4.4 | Persona emphasizes hot-hand continuation. |

### LLMIndependentAssessor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `LLMIndependentAssessor`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Prompt instructs independent probability assessment. |
| Mathematical model → sim-bases §4.3.4.3 | Decision JSON expresses buy/sell/hold and quantity under current state. |
| State variables → sim-bases §4.3.4.3 | Reads market broadcast and portfolio values. |
| Parameters → sim-bases §6 | Config provides model and portfolio values. |
| LLM persona → sim-bases §4.3.4.4 | Persona rejects sequential-pattern superstition. |

### LLMArbitrageur: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `LLMArbitrageur`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Prompt describes exploiting streak-driven mispricing. |
| Mathematical model → sim-bases §4.4.4.3 | Model output is parsed and capped before order emission. |
| State variables → sim-bases §4.4.4.3 | Uses current price, fundamental, deviation, cash, and position. |
| Parameters → sim-bases §6 | Config supplies runtime settings. |
| LLM persona → sim-bases §4.4.4.4 | Persona is arbitrage-focused and skeptical of streak bias. |

### LLMNoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `LLMNoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Prompt describes gut-feel liquidity provision. |
| Mathematical model → sim-bases §4.5.4.3 | Valid decision JSON is constrained by portfolio limits. |
| State variables → sim-bases §4.5.4.3 | Same market/portfolio fields as other LLM agents. |
| Parameters → sim-bases §6 | Higher temperature preserves noisier decisions. |
| LLM persona → sim-bases §4.5.4.4 | Persona avoids systematic probability reasoning. |

## §3 Market Mechanism Implementation

LLM imports `Market` from the Rule variant, so price formation and market broadcasts are unchanged. This isolates the effect of prompt-based investor decisions.

## §4 LLM Variant-Specific Features

- Prompts require `<analysis>` and `<decision>` tags.
- Decision JSON includes `action`, `bid_price`, `quantity`, and `reasoning`.
- `LLMInvestor.decide()` parses responses and caps quantities by cash, holdings, and max order size.
- Parse failures raise errors rather than becoming silent fallback holds.

## §5 Architecture Diagram

```text
Market broadcast -> LLMInvestor prompt -> LLM response -> parser -> capped order -> Market
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/GamblerFallacy/LLM/simulation.yml` | Full-run settings |
| `configs/GamblerFallacy/LLM/players.yml` | LLM model, prompt refs, class paths, portfolio values |
| `configs/GamblerFallacy/LLM/topology.yml` | Star topology |
| `configs/GamblerFallacy/LLM/persona.yml` | Shared proxy/storage settings |

## §7 Expected Runtime Outputs

Accepted LLM runs should complete 200 rounds with parseable decisions and no fallback-hold distortion.

## §8 Validation Checklist

- Prompt constants load through `_system_prompt_path`.
- User template contains the full market and portfolio state.
- Prompt/parser contract checks should report zero mismatches.
- Runtime code and prompts should remain stable unless a documented mechanism or contract defect is found.

## §9 Cross-Variant Comparison Notes

LLM is compared against Rule to estimate the effect of unconstrained language reasoning on streak asymmetry, momentum demand, and correction efficiency.
