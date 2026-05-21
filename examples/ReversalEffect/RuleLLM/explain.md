# Reversal Effect RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Decision Mechanism | API-generated orders constrained by explicit rules |
| Scenario Contract | `action`, `bid_price`, `quantity`, `reasoning`, `provides_liquidity` |
| Theory Reference | `examples/ReversalEffect/simulation-bases.md` |

RuleLLM combines persona descriptions with quantitative rule reminders. It uses
the liquidity-aware market extension, so every order must state whether it
provides passive liquidity.

## §2 Theory -> Implementation Mapping

| Theory Component | Implementation |
|---|---|
| ContrarianInvestor, `simulation-bases.md §4.1` | `RuleLLMContrarianInvestor` maps to the contrarian rule prompt. |
| MomentumInvestor, `simulation-bases.md §4.2` | `RuleLLMMomentumChaser` maps to the momentum rule prompt. |
| OverconfidentTrader, `simulation-bases.md §4.3` | `RuleLLMOverconfidentTrader` maps to the overconfident rule prompt. |
| NoiseTrader, `simulation-bases.md §4.4` | `RuleLLMNoiseTrader` maps to the noise-trader rule prompt. |
| ValueInvestor, `simulation-bases.md §4.5` | `RuleLLMValueInvestor` maps to the value-investor rule prompt. |
| IndexTracker, `simulation-bases.md §4.6` | Not instantiated in this API variant. |

## §3 Market Mechanism

The RuleLLM market extends the baseline market with liquidity-sensitive impact.
It reads `provides_liquidity` from each order, adds passive liquidity to base
depth, and increases price impact when effective liquidity is below threshold.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ReversalEffect/RuleLLM/players.py` |
| Prompt module | `examples/ReversalEffect/RuleLLM/prompts.py` |
| Inference | Project ARK LLM policy from config extras |
| Output parsing | Strict JSON parser requiring liquidity flag |
| Error handling | Parse failures retry and then fail fast for deterministic contract errors |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ReversalEffect/RuleLLM/simulation.yml` | Full 200-round entry point. |
| `configs/ReversalEffect/RuleLLM/players.yml` | Liquidity-aware market and five API investor definitions. |
| `configs/ReversalEffect/RuleLLM/topology.yml` | Broadcast and order routing. |
| `configs/ReversalEffect/RuleLLM/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/ReversalEffect/RuleLLM/run_reversal_effect_rulellm.py -c configs/ReversalEffect/RuleLLM/simulation.yml
```

## §7 Expected Behavior

Rule reminders should keep directional behavior close to the baseline while LLM
reasoning changes order size and liquidity provision. The liquidity-aware market
should remain finite and produce nonzero volume.

## §8 References

See `examples/ReversalEffect/simulation-bases.md §3` for the liquidity-aware
market and `analysis-bases.md §2.5` for liquidity-depth metrics.

## §9 Variant Comparison

RuleLLM should be compared with Rule on reversal timing and with LLM on parser
quality and order dispersion. It is the direct runtime base for the Rag variant.
