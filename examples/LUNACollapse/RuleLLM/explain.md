# LUNACollapse RuleLLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | LLM prompts with `== PERSONA ==` and `== DECISION RULES ==` |
| Key Difference | Tests language reasoning under explicit death-spiral rules |
| Runtime Change | RuleLLM system prompts were standardized; rerun required |

## §2 Theory To Implementation Mapping

| Design Element | Implementation |
|---|---|
| StablecoinHolder (`simulation-bases.md §4.1`) | `RULELLM_STABLECOINHOLDER_PROMPT` states -5% confidence-break sell rule |
| Arbitrageur (`simulation-bases.md §4.2`) | `RULELLM_ARBITRAGEUR_PROMPT` states ±2% arbitrage trigger and 5000 cap |
| DeFiLender (`simulation-bases.md §4.3`) | `RULELLM_DEFILENDER_PROMPT` states -15% liquidation sell rule |
| AnchorDepositor (`simulation-bases.md §4.4`) | `RULELLM_ANCHORDEPOSITOR_PROMPT` states -5% yield-exit sell rule |
| ValueBuyer (`simulation-bases.md §4.5`) | `RULELLM_VALUEBUYER_PROMPT` states -30% deep-discount buy rule |

## §3 Market Mechanism Implementation

RuleLLM imports the same `Market` class as Rule. Investors call the LLM with
persona and explicit rule prompts, then submit canonical trading orders.

## §4 Variant-Specific Features

RuleLLM keeps the death-spiral rules explicit while allowing natural-language
reasoning. It retries malformed output and fails loudly if no valid decision is
returned after three attempts.

## §5 Architecture Diagram

```text
Market state -> persona + decision rules -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/LUNACollapse/RuleLLM/players.yml`.

## §7 Expected Behavior Patterns

RuleLLM should stay closer to Rule than LLM because thresholds are prompt
anchored, while still varying explanation and possibly quantity.

## §8 Validation Checklist

Full 200-round rerun is required after prompt standardization. Review parse
quality, rule adherence, and price/portfolio sanity.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
