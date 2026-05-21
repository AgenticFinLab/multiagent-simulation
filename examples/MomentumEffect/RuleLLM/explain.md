# Momentum Effect RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | MomentumEffect |
| Decision Mechanism | API trading orders constrained by explicit momentum rules |
| Theory Reference | `examples/MomentumEffect/simulation-bases.md` |
| Market Broadcast | `configs/MomentumEffect/RuleLLM/topology.yml` |

This API variant uses five roles and requires `provides_liquidity` in every
decision payload because the market consumes that field.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | `RuleLLMMomentumTrader` |
| Prompt | `RULELLM_MOMENTUM_TRADER_SYS` |

### §2.2 ContrarianTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | `RuleLLMContrarianTrader` |
| Prompt | `RULELLM_CONTRARIAN_TRADER_SYS` |

### §2.3 IndexFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Not configured in this RuleLLM variant |

### §2.4 MarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Not configured in this RuleLLM variant |

### §2.5 TechnicalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | `RuleLLMTechnicalTrader` |
| Prompt | `RULELLM_TECHNICAL_TRADER_SYS` |

### §2.6 FundamentalAnchor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | `RuleLLMFundamentalAnchor` |
| Prompt | `RULELLM_FUNDAMENTAL_ANCHOR_SYS` |

### §2.7 TrendFollower

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.7` | `RuleLLMTrendFollower` |
| Prompt | `RULELLM_TREND_FOLLOWER_SYS` |

## §3 Market Mechanism

`examples/MomentumEffect/RuleLLM/players.py:Market` uses a
liquidity-sensitive price-impact equation and consumes
`order["provides_liquidity"]`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Players | `examples/MomentumEffect/RuleLLM/players.py` |
| Prompts | `examples/MomentumEffect/RuleLLM/prompts.py` |
| Parser | `parse_llm_response_with_thinking` |
| Error handling | Retry plus explicit conservative fallback hold |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MomentumEffect/RuleLLM/simulation.yml` | 200-round entry point |
| `configs/MomentumEffect/RuleLLM/players.yml` | Prompt bindings and API model configuration |
| `configs/MomentumEffect/RuleLLM/topology.yml` | Message routing |
| `configs/MomentumEffect/RuleLLM/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MomentumEffect/RuleLLM/run_momentum_effect_rulellm.py -c configs/MomentumEffect/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should show API variation while preserving directionality from explicit
momentum, contrarian, technical, trend-following, and fundamental rules.

## §8 References

See `examples/MomentumEffect/simulation-bases.md §2`.

## §9 Variant Comparison

Use RuleLLM to isolate the effect of adding explicit strategy rules to API
decisions.
