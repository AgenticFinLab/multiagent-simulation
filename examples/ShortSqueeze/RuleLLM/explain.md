# Short Squeeze RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | ShortSqueeze |
| Decision Mechanism | API orders constrained by explicit squeeze rules |
| Theory Reference | `examples/ShortSqueeze/simulation-bases.md` |
| Market Broadcast | `configs/ShortSqueeze/RuleLLM/topology.yml` |

RuleLLM combines persona descriptions with explicit quantitative rules and uses
the liquidity-aware market extension, so each order must include
`provides_liquidity`.

## §2 Theory -> Implementation Mapping

### §2.1 ShortSeller (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Forced covering | `RuleLLMShortSeller` uses short-seller rule prompts and liquidity-aware order fields. |
| API contract | Emits `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |

### §2.2 MomentumBuyer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Positive-feedback demand | `RuleLLMMomentumBuyer` applies momentum buyer rules with bounded LLM judgment. |
| API contract | Explicit rules constrain sign and magnitude. |

### §2.3 RetailCoordinator (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Attention-driven bullish flow | `RuleLLMRetailCoordinator` applies retail trader rules. |
| API contract | Liquidity flag feeds the market depth calculation. |

### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental resistance | `RuleLLMValueInvestor` applies valuation rules. |
| API contract | Structured JSON is parsed into liquidity-aware market orders. |

### §2.5 InstitutionalHolder (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Float scarcity | `RuleLLMInstitutionalHolder` applies holding/profit-taking rules. |
| API contract | Conservative fallback hold is logged and records `provides_liquidity=false`. |

## §3 Market Mechanism

`Market` in `examples/ShortSqueeze/RuleLLM/players.py` consumes
`provides_liquidity` to calculate effective depth and liquidity-sensitive price
impact.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ShortSqueeze/RuleLLM/players.py` |
| Prompt module | `examples/ShortSqueeze/RuleLLM/prompts.py` |
| Inference | ARK API model configured in `players.yml` |
| Output parsing | Shared `parse_llm_response_with_thinking` plus liquidity-field validation |
| Error handling | Bounded retry; explicit conservative fallback hold after stochastic parse failure |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ShortSqueeze/RuleLLM/simulation.yml` | Full simulation entry point |
| `configs/ShortSqueeze/RuleLLM/players.yml` | RuleLLM investor set and liquidity market config |
| `configs/ShortSqueeze/RuleLLM/topology.yml` | Message routing |
| `configs/ShortSqueeze/RuleLLM/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/ShortSqueeze/RuleLLM/run_short_squeeze_rulellm.py -c configs/ShortSqueeze/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should stay closer to Rule than LLM in trade direction while showing
API-level variation and liquidity-depth effects.

## §8 References

See `examples/ShortSqueeze/simulation-bases.md §2` and
`examples/ShortSqueeze/analysis-bases.md §2`.

## §9 Variant Comparison

Compare RuleLLM against LLM for rule anchoring and against Rag for retrieved
knowledge effects.
