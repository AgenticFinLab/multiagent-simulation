# Market Crash RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | MarketCrash |
| Decision Mechanism | API trading orders constrained by explicit rule text |
| Theory Reference | `examples/MarketCrash/simulation-bases.md` |
| Market Broadcast | `configs/MarketCrash/RuleLLM/topology.yml` |

This is a five-archetype API variant:
`PanicSeller`, `RiskParityFund`, `LeveragedFund`, `MarketMaker`, and
`BottomFisher`. `PassiveInvestor` is omitted by configuration. `BottomFisher`
now uses its own prompt contract rather than the previous incorrect
PassiveInvestor binding.

## §2 Theory -> Implementation Mapping

### §2.1 RiskParityFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Volatility targeting | `RuleLLMRiskParityFund` combines persona text with explicit risk-parity rules. |
| API contract | Emits canonical trading JSON plus `provides_liquidity`. |

### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Margin spiral | `RuleLLMLeveragedFund` represents leveraged deleveraging rules. |
| API contract | Parser requires liquidity flag because the market consumes it. |

### §2.3 MarketMaker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Liquidity supply/withdrawal | `RuleLLMMarketMaker` maps dealer rules into API decisions. |
| API contract | `provides_liquidity=true` identifies passive depth contributions. |

### §2.4 PassiveInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Slow passive stabilization | Not instantiated in this API variant. |
| Variant scope | Documented omission relative to the Rule baseline. |

### §2.5 PanicSeller (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Panic selling | `RuleLLMPanicSeller` follows explicit crash-trigger prompt rules. |
| API contract | Fallback hold is explicit and conservative after bounded retries. |

### §2.6 BottomFisher (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Contrarian absorption | `RuleLLMBottomFisher` binds to `RULELLM_BOTTOM_FISHER_SYS`. |
| API contract | Uses the corrected BottomFisher prompt, not PassiveInvestor. |

## §3 Market Mechanism

The RuleLLM market in `examples/MarketCrash/RuleLLM/players.py:Market` is a
liquidity-sensitive coordinator that explicitly consumes
`order["provides_liquidity"]`. Prompt contracts therefore require
`provides_liquidity` in every API decision payload.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/MarketCrash/RuleLLM/players.py` |
| Prompt module | `examples/MarketCrash/RuleLLM/prompts.py` |
| Inference | ARK API model from `players.yml` |
| Output parsing | `parse_llm_response_with_thinking` |
| Error handling | Explicit retry; conservative logged fallback hold on repeated parse failure |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MarketCrash/RuleLLM/simulation.yml` | Full simulation entry point |
| `configs/MarketCrash/RuleLLM/players.yml` | Hybrid investors and prompt bindings |
| `configs/MarketCrash/RuleLLM/topology.yml` | Message routing |
| `configs/MarketCrash/RuleLLM/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MarketCrash/RuleLLM/run_market_crash_rulellm.py -c configs/MarketCrash/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should stay closer to Rule than pure LLM on directionality of
deleveraging and liquidity withdrawal because its prompts embed explicit
scenario rules. The corrected BottomFisher prompt binding is a runtime change
and requires rerunning successful legacy RuleLLM samples collected under the
wrong binding.

## §8 References

See `examples/MarketCrash/simulation-bases.md §2`.

## §9 Variant Comparison

Use RuleLLM to isolate the effect of adding explicit crash rules to API
decision-making.
