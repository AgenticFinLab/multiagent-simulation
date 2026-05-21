# SouthSeaBubble LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | SouthSeaBubble |
| Decision Mechanism | Persona-conditioned API quantity orders |
| Theory Reference | `examples/SouthSeaBubble/simulation-bases.md` |
| Market Broadcast | `configs/SouthSeaBubble/LLM/topology.yml` |

The LLM variant preserves the current-market quantity schema: `action`,
`quantity`, and `reasoning`; no limit price is requested or consumed.

## §2 Theory -> Implementation Mapping

### §2.1 InsiderAdvantaged (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Insider advantage | `LLMInsiderAdvantaged` uses insider persona and current market state. |
| Config link | Portfolio metadata and ARK model config from `configs/SouthSeaBubble/LLM/players.yml`. |
| Output contract | Required `action`, `quantity`, `reasoning`, optional analysis, and fallback metadata. |

### §2.2 NarrativeBeliever (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Narrative demand | `LLMNarrativeBeliever` reasons from promotional-story conviction. |
| Config link | Narrative metadata and model config. |
| Output contract | Current-market quantity order. |

### §2.3 SkepticalAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Fundamental skepticism | `LLMSkepticalAnalyst` reasons from valuation and cash-flow doubts. |
| Config link | Cash-flow metadata and model config. |
| Output contract | Quantity order with explicit fallback fields. |

### §2.4 Arbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Mispricing correction | `LLMArbitrageur` reasons about narrative price versus fundamental value. |
| Config link | Spread metadata and model config. |
| Output contract | Quantity order with parser quality artifacts. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | `LLMNoiseTrader` supplies low-information orders. |
| Config link | Noise metadata and model config. |
| Output contract | Valid quantity order or explicit conservative fallback. |

## §3 Market Mechanism

The LLM variant reuses the Rule market; API output changes only investor
decision generation, not market clearing.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SouthSeaBubble/LLM/players.py` |
| Prompt module | `examples/SouthSeaBubble/LLM/prompts.py` |
| Inference | Project ARK model policy |
| Output parsing | Shared parser plus required-field validation |
| Error handling | Retryable API/parse failures are retried; final fallback is explicit |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SouthSeaBubble/LLM/simulation.yml` | 200-round simulation entry point |
| `configs/SouthSeaBubble/LLM/players.yml` | Class paths, role metadata, and LLM config |
| `configs/SouthSeaBubble/LLM/topology.yml` | Message routing |
| `configs/SouthSeaBubble/LLM/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SouthSeaBubble/LLM/run_southseabubble_llm.py -c configs/SouthSeaBubble/LLM/simulation.yml
```

## §7 Expected Behavior

LLM may amplify or dampen narrative conviction, but must preserve valid
quantity-order payloads and visible fallback metadata.

## §8 References

See `examples/SouthSeaBubble/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Compare LLM against Rule on bubble magnitude, role attribution, and API quality.
