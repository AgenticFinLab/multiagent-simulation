# LUNACollapse LLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | LLM persona prompts with canonical trading JSON |
| Key Difference | Tests discretionary panic, arbitrage, liquidation, and value reasoning |

## §2 Theory To Implementation Mapping

| Design Element | Implementation |
|---|---|
| StablecoinHolder (`simulation-bases.md §4.1`) | `LLMStablecoinHolder` uses `LLM_STABLECOINHOLDER_PROMPT` |
| Arbitrageur (`simulation-bases.md §4.2`) | `LLMArbitrageur` uses `LLM_ARBITRAGEUR_PROMPT` |
| DeFiLender (`simulation-bases.md §4.3`) | `LLMDeFiLender` uses `LLM_DEFILENDER_PROMPT` |
| AnchorDepositor (`simulation-bases.md §4.4`) | `LLMAnchorDepositor` uses `LLM_ANCHORDEPOSITOR_PROMPT` |
| ValueBuyer (`simulation-bases.md §4.5`) | `LLMValueBuyer` uses `LLM_VALUEBUYER_PROMPT` |

## §3 Market Mechanism Implementation

LLM imports the same `Market` class as Rule. Only investor decision generation
changes: `LLMInvestor.decide()` builds a market-state prompt, calls
`LangChainAPIInference.run()`, and parses `<decision>` JSON.

## §4 Variant-Specific Features

LLM retries malformed output up to three times and then fails loudly with
`RuntimeError`. There is no silent hold fallback in this variant.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market clearing
```

## §6 Configuration Reference

Primary config: `configs/LUNACollapse/LLM/players.yml`. LLM prompts describe
the same economic trigger scale used by the configs while leaving discretionary
reasoning to the model.

## §7 Expected Behavior Patterns

LLM may alter panic timing and order sizes relative to Rule. Outputs should be
reviewed for malformed-output and fallback quality.

## §8 Validation Checklist

Verify full rounds, canonical order schema, LLM parse quality, and price
trajectory sanity.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
