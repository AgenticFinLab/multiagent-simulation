# SorosPound LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | SorosPound |
| Decision Mechanism | Persona-conditioned API quantity orders |
| Theory Reference | `examples/SorosPound/simulation-bases.md` |
| Market Broadcast | `configs/SorosPound/LLM/topology.yml` |

The LLM variant preserves the SorosPound current-market quantity schema:
`action`, `quantity`, and `reasoning`. It does not ask for or consume limit
prices.

## §2 Theory -> Implementation Mapping

### §2.1 MacroHedgeFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Speculative attack role | `LLMMacroHedgeFund` uses the macro attacker prompt and current market state. |
| Config link | Portfolio fields, role metadata, and ARK model config from `configs/SorosPound/LLM/players.yml`. |
| Output contract | Required `action`, `quantity`, `reasoning`, optional analysis, and explicit fallback metadata. |

### §2.2 PegDefender (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Peg defense role | `LLMPegDefender` reasons as a reserve-constrained defender. |
| Config link | Defender portfolio and LLM config from `players.yml`. |
| Output contract | Quantity order constrained by cash/inventory after parsing. |

### §2.3 ConvergenceTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Convergence belief role | `LLMConvergenceTrader` reasons from policy-commitment beliefs. |
| Config link | Convergence metadata and LLM config. |
| Output contract | Valid quantity order or explicit conservative fallback. |

### §2.4 OpportunisticTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Attack follower role | `LLMOpportunisticTrader` reasons as a momentum participant. |
| Config link | Attack-join metadata and LLM config. |
| Output contract | Valid quantity order with reasoning. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity role | `LLMNoiseTrader` reasons as low-information noise flow. |
| Config link | Noise metadata and LLM config. |
| Output contract | Valid quantity order; fallback rate must be quality-audited. |

## §3 Market Mechanism

The LLM variant reuses the Rule market. API output only changes investor
decision generation; market clearing remains net-demand aggregation of
current-market quantities.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SorosPound/LLM/players.py` |
| Prompt module | `examples/SorosPound/LLM/prompts.py` |
| Inference | Project ARK model policy from `players.yml` |
| Output parsing | `parse_llm_response_with_thinking` plus required-field validation |
| Error handling | API call errors fail unless retryable; parse fallback is explicit and auditable |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SorosPound/LLM/simulation.yml` | 200-round simulation entry point |
| `configs/SorosPound/LLM/players.yml` | Class paths, role metadata, portfolio state, and model config |
| `configs/SorosPound/LLM/topology.yml` | Market update and investor order routing |
| `configs/SorosPound/LLM/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SorosPound/LLM/run_sorospound_llm.py -c configs/SorosPound/LLM/simulation.yml
```

## §7 Expected Behavior

LLM may alter confidence and quantity sizing, but it must preserve the
SorosPound schema. Any parser fallback must be visible and reviewed before
accepting the sample.

## §8 References

See `examples/SorosPound/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Compare LLM with Rule for attack timing, defense response, herding share, and
parse/fallback quality.
