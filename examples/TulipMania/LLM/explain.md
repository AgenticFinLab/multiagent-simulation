# Tulip Mania LLM Variant Explanation

## §1 Overview

The LLM variant keeps the Rule market and portfolio accounting but delegates
investor action selection to persona prompts. It uses the same current-market
quantity schema as the Rule baseline.

## §2 Theory -> Implementation Mapping

| Investor | Theory Component | Implementation |
|---|---|---|
| `LLMTrendChaser` | `simulation-bases.md §4.1` | System prompt encodes momentum and greater-fool persona; `LLMInvestor` enforces quantity-order parsing. |
| `LLMSocialProofFollower` | `simulation-bases.md §4.2` | System prompt encodes crowd validation and FOMO; parser keeps the same order schema. |
| `LLMIntrinsicValueTrader` | `simulation-bases.md §4.3` | System prompt encodes fundamental-value discipline. |
| `LLMEarlyExitTrader` | `simulation-bases.md §4.4` | System prompt encodes tactical exit from speculative excess. |
| `LLMNoiseTrader` | `simulation-bases.md §4.5` | System prompt encodes occasional low-conviction noise trading. |

## §3 Market Mechanism

The market is imported from `TulipMania.Rule.players:Market`. It clears
current-market quantities and ignores limit-price fields.

## §4 Variant Architecture

`LLMInvestor` builds a market-state prompt, calls the configured LLM, validates
`action`, `quantity`, and `reasoning`, applies cash/inventory constraints, and
emits an `investor_order` payload with explicit fallback audit fields.

## §5 Config Reference

`configs/TulipMania/LLM/players.yml` binds LLM investor classes, initial
portfolios, and model settings. Topology mirrors the Rule variant.

## §6 Running Instructions

```bash
python examples/TulipMania/LLM/run_tulipmania_llm.py -c configs/TulipMania/LLM/simulation.yml
```

## §7 Expected Behavior

LLM behavior should retain the five investor roles while adding stochastic
reasoning. Any parse fallback must be explicit, conservative, and quality
audited after the run.

## §8 References

See `simulation-bases.md §2` and investor mappings in `simulation-bases.md §4`.

## §9 Variant Comparison

Compare against Rule for timing, magnitude, agent attribution, and fallback
rate.
