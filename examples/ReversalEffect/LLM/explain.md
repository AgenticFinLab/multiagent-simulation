# Reversal Effect LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Decision Mechanism | API-generated trading orders |
| Scenario Contract | `action`, `bid_price`, `quantity`, `reasoning` |
| Theory Reference | `examples/ReversalEffect/simulation-bases.md` |

The LLM variant keeps the same mean-reverting market structure as the Rule
baseline but replaces deterministic investor formulas with persona prompts and
structured JSON decisions.

## §2 Theory -> Implementation Mapping

### §2.1 ContrarianInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Contrarian reversal pressure | `LLMContrarianInvestor` uses the mean-reversion persona and a structured order parser. |
| API contract | Emits `action`, `bid_price`, `quantity`, and `reasoning`. |

### §2.2 MomentumInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Continuation pressure | `LLMMomentumChaser` follows recent short-term direction. |
| API contract | Parser converts canonical JSON into signed market orders. |

### §2.3 OverconfidentTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Signal overweighting | `LLMOverconfidentTrader` extrapolates recent returns. |
| API contract | Bounded retries handle stochastic parse errors; deterministic schema errors fail fast. |

### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Stochastic background flow | `LLMNoiseTrader` represents low-conviction retail order flow. |
| API contract | Emits canonical trading JSON rather than special-schema actions. |

### §2.5 ValueInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Fundamental anchoring | `LLMValueInvestor` compares price to fundamental value. |
| API contract | Reasoning text is recorded for post-run quality review. |

### §2.6 IndexTracker (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Passive rebalancing | Not instantiated in the API variants. |
| Variant scope | The passive role is retained only in Rule. |

## §3 Market Mechanism

The LLM market broadcasts price, previous price, return, cumulative return,
performance label, and fundamental value. Parsed LLM orders update portfolio
state before the market aggregates demand and applies mean reversion and noise.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ReversalEffect/LLM/players.py` |
| Prompt module | `examples/ReversalEffect/LLM/prompts.py` |
| Inference | Project ARK LLM policy from config extras |
| Output parsing | `<analysis>` plus `<decision>` JSON |
| Error handling | Explicit conservative API fallback only after parse/runtime retries |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ReversalEffect/LLM/simulation.yml` | Full 200-round entry point. |
| `configs/ReversalEffect/LLM/players.yml` | Market and five API investor definitions. |
| `configs/ReversalEffect/LLM/topology.yml` | Broadcast and order routing. |
| `configs/ReversalEffect/LLM/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/ReversalEffect/LLM/run_reversal_llm.py -c configs/ReversalEffect/LLM/simulation.yml
```

## §7 Expected Behavior

The run should preserve reversal pressure while allowing variation in timing and
order size. Any fallback decisions must be visible in logs or post-run quality
audit and must not mask deterministic schema bugs.

## §8 References

See `examples/ReversalEffect/simulation-bases.md §2` for theory and
`analysis-bases.md §2.7` for API quality checks.

## §9 Variant Comparison

LLM differs from Rule by replacing formulas with persona prompts. It does not
use liquidity-depth fields or RAG retrieval, so it should be compared primarily
on reversal timing, order dispersion, and API quality.
