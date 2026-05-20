# FramingEffect RuleLLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | LLM reasoning with persona text plus explicit decision-rule text |
| Key Difference from Other Variants | Preserves Rule-style thresholds in prompt form while still using LLM reasoning. |
| Primary Research Contribution | Isolates the effect of LLM reasoning when the quantitative behavioral frame is supplied. |
| Files | `players.py`, `prompts.py`, `run_framingeffect_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### RuleLLMGainFrameFollower: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `RuleLLMGainFrameFollower`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | `RULELLM_GAIN_FRAME_FOLLOWER_SYS` uses `== PERSONA ==` and `== DECISION RULES ==`. |
| Mathematical model → sim-bases §4.1.4.3 | Prompt states the 2% activation logic and deviation-proportional sizing as decision guidance. |
| State variables → sim-bases §4.1.4.3 | Current market and portfolio fields are injected through `RULELLM_USER_TEMPLATE`. |
| Parameters → sim-bases §6 | LLM settings and portfolio calibration are loaded from `players.yml`. |
| LLM persona → sim-bases §4.1.4.4 | Persona describes gain-frame-sensitive momentum behavior. |

### RuleLLMLossFrameReactor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `RuleLLMLossFrameReactor`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | System prompt embeds loss-frame reaction rules and persona. |
| Mathematical model → sim-bases §4.2.4.3 | Decision rules describe the same thresholded response as the Rule baseline. |
| State variables → sim-bases §4.2.4.3 | Uses price, fundamental, deviation, cash, position, and portfolio value. |
| Parameters → sim-bases §6 | Model and portfolio values come from config. |
| LLM persona → sim-bases §4.2.4.4 | Persona highlights loss sensitivity and urgency. |

### RuleLLMFrameInvariantTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `RuleLLMFrameInvariantTrader`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Prompt embeds frame-invariant value reasoning. |
| Mathematical model → sim-bases §4.3.4.3 | Decision rules describe contrarian trading once deviation is materially large. |
| State variables → sim-bases §4.3.4.3 | Market broadcast and portfolio state are passed into the user prompt. |
| Parameters → sim-bases §6 | Config supplies LLM and portfolio settings. |
| LLM persona → sim-bases §4.3.4.4 | Persona stresses substance over presentation. |

### RuleLLMArbitrageFramer: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `RuleLLMArbitrageFramer`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Prompt describes framing-induced mispricing and arbitrage. |
| Mathematical model → sim-bases §4.4.4.3 | Prompt rules mirror the contrarian correction logic. |
| State variables → sim-bases §4.4.4.3 | Same fields as other RuleLLM investors. |
| Parameters → sim-bases §6 | Runtime values are config supplied. |
| LLM persona → sim-bases §4.4.4.4 | Persona is an arbitrage-focused trader. |

### RuleLLMNoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `RuleLLMNoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Prompt keeps uninformed liquidity-provider behavior. |
| Mathematical model → sim-bases §4.5.4.3 | Parsed action is capped by portfolio constraints and max order size. |
| State variables → sim-bases §4.5.4.3 | Uses injected market and portfolio fields. |
| Parameters → sim-bases §6 | Higher temperature can preserve noisier behavior. |
| LLM persona → sim-bases §4.5.4.4 | Persona avoids systematic framing arbitrage. |

## §3 Market Mechanism Implementation

RuleLLM imports the Rule `Market`; therefore price formation, order collection, and broadcasts remain identical to Rule. Any difference in results comes from prompt-guided LLM order generation.

## §4 RuleLLM Variant-Specific Features

- System prompts must contain `== PERSONA ==` and `== DECISION RULES ==`.
- Decision JSON uses `action`, `bid_price`, `quantity`, and `reasoning`.
- Parsed decisions are bounded by cash, holdings, and maximum quantity before orders are emitted.
- Runtime does not silently substitute fallback holds on parse failure.

## §5 Architecture Diagram

```text
Market broadcast -> RuleLLMInvestor
        |
        v
persona + decision-rules prompt + market state
        |
        v
LLM response -> parser -> capped order -> Market
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/FramingEffect/RuleLLM/simulation.yml` | Full-run settings |
| `configs/FramingEffect/RuleLLM/players.yml` | LLM model, prompt refs, and portfolio settings |
| `configs/FramingEffect/RuleLLM/topology.yml` | Star topology |
| `configs/FramingEffect/RuleLLM/persona.yml` | Shared proxy/storage settings |

## §7 Expected Runtime Outputs

Accepted runs should produce complete 200-round market records, valid order messages, and model reasoning that is consistent with the embedded decision rules.

## §8 Validation Checklist

- Prompt constants load for all five investor classes.
- `== PERSONA ==` and `== DECISION RULES ==` are present.
- API audit reports zero parser-contract mismatches.
- Existing sample can be inherited if only docs and analysis files change.

## §9 Cross-Variant Comparison Notes

RuleLLM is compared against Rule to quantify language-reasoning effects under aligned behavioral rules, and against LLM to measure the stabilizing effect of explicit decision-rule guidance.
