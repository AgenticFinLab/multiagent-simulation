# SorosPound RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | SorosPound |
| Decision Mechanism | Explicit rule prompts plus API reasoning over quantity orders |
| Theory Reference | `examples/SorosPound/simulation-bases.md` |
| Market Broadcast | `configs/SorosPound/RuleLLM/topology.yml` |

RuleLLM keeps the current-market quantity schema and uses prompts that separate
persona from explicit decision rules.

## §2 Theory -> Implementation Mapping

### §2.1 MacroHedgeFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Speculative attack role | `RuleLLMMacroHedgeFund` receives macro persona plus threshold/sizing rules. |
| Config link | Portfolio fields and ARK model config from `configs/SorosPound/RuleLLM/players.yml`. |
| Output contract | Required `action`, `quantity`, `reasoning`, analysis, and fallback metadata. |

### §2.2 PegDefender (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Peg defense role | `RuleLLMPegDefender` receives intervention threshold and direction rules. |
| Config link | Defender portfolio metadata and LLM config. |
| Output contract | Current-market quantity order. |

### §2.3 ConvergenceTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Peg-stability belief role | `RuleLLMConvergenceTrader` receives stochastic convergence-trade rules. |
| Config link | Convergence metadata and LLM config. |
| Output contract | Quantity order with explicit reasoning. |

### §2.4 OpportunisticTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Momentum/herding role | `RuleLLMOpportunisticTrader` receives pressure-following threshold rules. |
| Config link | Attack-join metadata and LLM config. |
| Output contract | Quantity order and parser-quality metadata. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Noise liquidity role | `RuleLLMNoiseTrader` receives random-trade rules. |
| Config link | Noise metadata and LLM config. |
| Output contract | Quantity order with explicit fallback metadata. |

## §3 Market Mechanism

The RuleLLM variant reuses the Rule market. Prompt rules guide stochastic
decisions, but market clearing remains net-demand aggregation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SorosPound/RuleLLM/players.py` |
| Prompt module | `examples/SorosPound/RuleLLM/prompts.py` |
| Inference | Project ARK model policy from `players.yml` |
| Output parsing | Required-field validation after shared LLM parser |
| Error handling | Retryable API/parse failures are retried; final fallback is explicit |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SorosPound/RuleLLM/simulation.yml` | 200-round simulation entry point |
| `configs/SorosPound/RuleLLM/players.yml` | Class paths, role metadata, portfolio state, and model config |
| `configs/SorosPound/RuleLLM/topology.yml` | Market update and investor order routing |
| `configs/SorosPound/RuleLLM/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SorosPound/RuleLLM/run_sorospound_rulellm.py -c configs/SorosPound/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should remain closer to Rule than unconstrained LLM on threshold timing
and role direction while still allowing natural-language reasoning.

## §8 References

See `examples/SorosPound/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Compare RuleLLM with Rule for rule fidelity and with LLM for reduced stochastic
schema drift.
