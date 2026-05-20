# FramingEffect LLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona-only LLM reasoning over the same market broadcast used by Rule |
| Key Difference from Other Variants | Investor direction and size are generated from prompts, not deterministic formulas. |
| Primary Research Contribution | Tests whether LLM personas reproduce framing-sensitive trading without explicit rule code. |
| Files | `players.py`, `prompts.py`, `run_framingeffect_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### LLMGainFrameFollower: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `LLMGainFrameFollower`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | System prompt `LLM_GAIN_FRAME_FOLLOWER_SYS` defines a momentum/gain-frame-sensitive persona. |
| Mathematical model → sim-bases §4.1.4.3 | LLM sees `price`, `fundamental`, `deviation`, cash, and position, then emits a trade JSON. |
| State variables → sim-bases §4.1.4.3 | `LLMInvestor.perceive()` stores current market state and portfolio fields. |
| Parameters → sim-bases §6 | Model name, temperature, and portfolio values come from `configs/FramingEffect/LLM/players.yml`. |
| LLM persona → sim-bases §4.1.4.4 | Prompt emphasizes positive price signals and gain opportunity. |

### LLMLossFrameReactor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `LLMLossFrameReactor`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | System prompt `LLM_LOSS_FRAME_REACTOR_SYS` defines loss-sensitive trading psychology. |
| Mathematical model → sim-bases §4.2.4.3 | The prompt asks for buy/sell/hold and quantity under cash and position constraints. |
| State variables → sim-bases §4.2.4.3 | Uses the same market and portfolio state as Rule. |
| Parameters → sim-bases §6 | LLM settings and initial portfolio are config supplied. |
| LLM persona → sim-bases §4.2.4.4 | Prompt highlights fear of losses and aggressive reaction to negative framing. |

### LLMFrameInvariantTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `LLMFrameInvariantTrader`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Prompt asks the persona to focus on value rather than presentation. |
| Mathematical model → sim-bases §4.3.4.3 | User template supplies deviation and portfolio limits for valuation-based decisions. |
| State variables → sim-bases §4.3.4.3 | Reads current market broadcast fields from inbound messages. |
| Parameters → sim-bases §6 | Model config and portfolio values are loaded from `players.yml`. |
| LLM persona → sim-bases §4.3.4.4 | Prompt describes rational frame-invariant analysis. |

### LLMArbitrageFramer: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `LLMArbitrageFramer`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Prompt frames mispricing as an arbitrage opportunity. |
| Mathematical model → sim-bases §4.4.4.3 | LLM emits trade decision constrained after parsing by cash, holdings, and max quantity. |
| State variables → sim-bases §4.4.4.3 | Uses current price, fundamental, and deviation. |
| Parameters → sim-bases §6 | Config provides LLM and portfolio parameters. |
| LLM persona → sim-bases §4.4.4.4 | Prompt describes a sophisticated arbitrage-focused trader. |

### LLMNoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `LLMNoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Prompt describes random liquidity provision rather than systematic valuation. |
| Mathematical model → sim-bases §4.5.4.3 | Output is still parsed through the shared action schema and capped by portfolio constraints. |
| State variables → sim-bases §4.5.4.3 | Same market state and portfolio state as other LLM investors. |
| Parameters → sim-bases §6 | Config uses higher temperature for noisier behavior. |
| LLM persona → sim-bases §4.5.4.4 | Prompt describes gut-feel trading and limited analytical structure. |

## §3 Market Mechanism Implementation

The LLM variant imports `Market` from `examples.FramingEffect.Rule.players`, so price formation and broadcasts are identical to Rule. This preserves the experiment’s causal comparison: only investor decision generation changes.

## §4 LLM Variant-Specific Features

- Prompts use `<analysis>...</analysis>` and `<decision>{...}</decision>`.
- Required decision JSON fields are `action`, `bid_price`, `quantity`, and `reasoning`.
- `LLMInvestor.decide()` parses model output and caps quantity by cash, position, and the 1000-share maximum.
- Parse failures raise runtime errors; they are not silently converted to hold decisions.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
LLMInvestor._build user prompt + persona system prompt
        |
        v
LangChainAPIInference -> parse_llm_response_with_thinking()
        |
        v
validated order -> Market
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/FramingEffect/LLM/simulation.yml` | Full-run settings and Ray namespace |
| `configs/FramingEffect/LLM/players.yml` | LLM model, temperatures, class paths, and portfolio settings |
| `configs/FramingEffect/LLM/topology.yml` | Market-to-investor and investor-to-market message flow |
| `configs/FramingEffect/LLM/persona.yml` | Shared storage/proxy configuration |

## §7 Expected Runtime Outputs

Each accepted LLM run should include 200 rounds, complete order records, and LLM reasoning traces with valid decision JSON. Quantity caps may reduce model-requested trades but should not change the parsed action semantics.

## §8 Validation Checklist

- Prompt constants load through each class `_system_prompt_path`.
- User template contains current market and portfolio fields.
- API contract audit reports zero prompt/parser issues.
- Existing LLM sample can be inherited if only documentation and analysis files change.

## §9 Cross-Variant Comparison Notes

LLM is compared against Rule to measure how unconstrained language reasoning changes FDI, FAR, VAF, WDI, and qualitative reasoning about equivalent gain/loss frames.
