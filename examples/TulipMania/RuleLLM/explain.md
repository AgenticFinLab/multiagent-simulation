# Tulip Mania RuleLLM Variant Explanation

## §1 Overview

The RuleLLM variant gives the model both persona text and explicit TulipMania
decision rules. It preserves the current-market quantity schema and Rule market
mechanism.

## §2 Theory -> Implementation Mapping

| Investor | Theory Component | Implementation |
|---|---|---|
| `RuleLLMTrendChaser` | `simulation-bases.md §4.1` | Prompt includes positive-feedback persona plus the 0.02 threshold and size formula. |
| `RuleLLMSocialProofFollower` | `simulation-bases.md §4.2` | Prompt includes crowd-following persona plus the same threshold and size formula. |
| `RuleLLMIntrinsicValueTrader` | `simulation-bases.md §4.3` | Prompt includes fundamental-value persona plus the 0.05 contrarian formula. |
| `RuleLLMEarlyExitTrader` | `simulation-bases.md §4.4` | Prompt includes early-exit persona plus the 0.05 exit formula. |
| `RuleLLMNoiseTrader` | `simulation-bases.md §4.5` | Prompt includes random low-conviction trading instructions. |

## §3 Market Mechanism

The market is `TulipMania.Rule.players:Market`, which aggregates quantity orders
and updates current price. It does not consume `bid_price`.

## §4 Variant Architecture

`RuleLLMInvestor` calls the configured LLM, validates `action`, `quantity`, and
`reasoning`, applies portfolio constraints, and emits explicit fallback audit
fields.

## §5 Config Reference

`configs/TulipMania/RuleLLM/players.yml` binds RuleLLM classes and model
settings. `simulation.yml` and `topology.yml` mirror the Rule message flow.

## §6 Running Instructions

```bash
python examples/TulipMania/RuleLLM/run_tulipmania_rulellm.py -c configs/TulipMania/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should be closer to the deterministic formulas than LLM while still
allowing explanatory reasoning. Fallback should be rare and explicitly recorded.

## §8 References

See `simulation-bases.md §2` and the investor formulas in
`simulation-bases.md §4`.

## §9 Variant Comparison

Compare RuleLLM with Rule for formula adherence and with LLM for reduced
behavioral dispersion.
