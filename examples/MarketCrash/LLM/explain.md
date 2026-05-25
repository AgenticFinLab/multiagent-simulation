# Market Crash LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | MarketCrash |
| Decision Mechanism | Persona-driven API trading orders |
| Theory Reference | `examples/MarketCrash/simulation-bases.md` |
| Market Broadcast | `configs/MarketCrash/LLM/topology.yml` |

This is a trading-schema scenario. The configured investor set contains five
archetypes: `PanicSeller`, `RiskParityFund`, `LeveragedFund`, `MarketMaker`,
and `BottomFisher`. `PassiveInvestor` is not configured in this API variant.

## §2 Theory -> Implementation Mapping

### §2.1 RiskParityFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Volatility targeting | `LLMRiskParityFund` uses persona prompts and canonical JSON orders. |
| API contract | Emits `action`, `bid_price`, `quantity`, and `reasoning`. |

### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Margin spiral | `LLMLeveragedFund` represents the leveraged-fund archetype. |
| API contract | Parser validates canonical trading fields. |

### §2.3 MarketMaker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Liquidity-supply behavior | `LLMMarketMaker` expresses dealer/liquidity reasoning through prompts. |
| Variant scope | The LLM market uses internal liquidity state, not `provides_liquidity`. |

### §2.4 PassiveInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Slow passive stabilization | Not instantiated in this API variant. |
| Variant scope | Documented omission relative to the six-role Rule baseline. |

### §2.5 PanicSeller (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Loss-sensitive panic selling | `LLMPanicSeller` uses prompt-driven discretionary selling. |
| API contract | Conservative fallback is explicit and logged after bounded retries. |

### §2.6 BottomFisher (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Contrarian crash absorption | `LLMBottomFisher` represents value/contrarian buying after discounts. |
| API contract | Emits canonical trading JSON parsed by `players.py`. |

## §3 Market Mechanism

The LLM coordinator in `examples/MarketCrash/LLM/players.py:Market` uses its
own internal liquidity state and volatility process. Investor orders do not
carry `provides_liquidity` in this variant.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/MarketCrash/LLM/players.py` |
| Prompt module | `examples/MarketCrash/LLM/prompts.py` |
| Inference | ARK API model from `players.yml` |
| Output parsing | `parse_llm_response_with_thinking` in `players.py` |
| Error handling | Explicit retry; conservative logged fallback hold on repeated parse failure |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MarketCrash/LLM/simulation.yml` | Full simulation entry point |
| `configs/MarketCrash/LLM/players.yml` | LLM investor set, prompts, model config |
| `configs/MarketCrash/LLM/topology.yml` | Message routing |
| `configs/MarketCrash/LLM/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MarketCrash/LLM/run_crash_llm.py -c configs/MarketCrash/LLM/simulation.yml
```

## §7 Expected Behavior

The LLM run should preserve the crash narrative while allowing discretionary
variation in timing and size of panic selling, deleveraging, and contrarian
buying. Because the configured archetype set is smaller than the Rule baseline,
results should not be interpreted as a one-to-one reproduction of all six Rule
roles.

## §8 References

See `examples/MarketCrash/simulation-bases.md §2`.

## §9 Variant Comparison

Compare against Rule for mechanism shape and against RuleLLM for the effect of
removing explicit rule text from prompts.
