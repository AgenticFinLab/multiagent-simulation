# SouthSeaBubble RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | SouthSeaBubble |
| Decision Mechanism | Explicit rule prompts plus API quantity orders |
| Theory Reference | `examples/SouthSeaBubble/simulation-bases.md` |
| Market Broadcast | `configs/SouthSeaBubble/RuleLLM/topology.yml` |

RuleLLM keeps the same current-market quantity schema and adds explicit
decision-rule prompts for role fidelity.

## §2 Theory -> Implementation Mapping

### §2.1 InsiderAdvantaged (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Insider advantage | `RuleLLMInsiderAdvantaged` receives insider persona plus retained threshold rules. |
| Config link | Portfolio metadata and model config. |
| Output contract | Quantity order plus reasoning and fallback metadata. |

### §2.2 NarrativeBeliever (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Narrative demand | `RuleLLMNarrativeBeliever` receives story-belief persona and momentum rules. |
| Config link | Narrative metadata and model config. |
| Output contract | Quantity order. |

### §2.3 SkepticalAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Fundamental skepticism | `RuleLLMSkepticalAnalyst` receives valuation rules. |
| Config link | Cash-flow metadata and model config. |
| Output contract | Quantity order with quality artifacts. |

### §2.4 Arbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Mispricing correction | `RuleLLMArbitrageur` receives arbitrage threshold rules. |
| Config link | Spread metadata and model config. |
| Output contract | Quantity order with explicit reasoning. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Noise liquidity | `RuleLLMNoiseTrader` receives random-trade rules. |
| Config link | Noise metadata and model config. |
| Output contract | Quantity order and fallback metadata. |

## §3 Market Mechanism

The RuleLLM variant reuses the Rule market; prompt rules guide investor orders
while clearing remains net-demand aggregation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SouthSeaBubble/RuleLLM/players.py` |
| Prompt module | `examples/SouthSeaBubble/RuleLLM/prompts.py` |
| Inference | Project ARK model policy |
| Output parsing | Shared parser plus required-field validation |
| Error handling | Explicit conservative fallback after retries |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SouthSeaBubble/RuleLLM/simulation.yml` | 200-round simulation entry point |
| `configs/SouthSeaBubble/RuleLLM/players.yml` | Class paths, role metadata, and LLM config |
| `configs/SouthSeaBubble/RuleLLM/topology.yml` | Message routing |
| `configs/SouthSeaBubble/RuleLLM/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SouthSeaBubble/RuleLLM/run_southseabubble_rulellm.py -c configs/SouthSeaBubble/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should remain closer to Rule thresholds than LLM while allowing
natural-language reasoning.

## §8 References

See `examples/SouthSeaBubble/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Compare RuleLLM against Rule for rule fidelity and against LLM for reduced
schema drift.
