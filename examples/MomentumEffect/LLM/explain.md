# Momentum Effect LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | MomentumEffect |
| Decision Mechanism | Persona-driven API trading orders |
| Theory Reference | `examples/MomentumEffect/simulation-bases.md` |
| Market Broadcast | `configs/MomentumEffect/LLM/topology.yml` |

This API variant uses five roles: MomentumTrader, ContrarianTrader,
TechnicalTrader, TrendFollower, and FundamentalAnchor.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | `LLMMomentumTrader` in `examples/MomentumEffect/LLM/players.py` |
| Prompt | `LLM_MOMENTUM_TRADER_SYS` |

### §2.2 ContrarianTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | `LLMContrarianTrader` |
| Prompt | `LLM_CONTRARIAN_SYS` |

### §2.3 IndexFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Not configured in this LLM variant |

### §2.4 MarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Not configured in this LLM variant |

### §2.5 TechnicalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | `LLMTechnicalTrader` |
| Prompt | `LLM_TECHNICAL_SYS` |

### §2.6 FundamentalAnchor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | `LLMFundamentalAnchor` |
| Prompt | `LLM_FUNDAMENTAL_SYS` |

### §2.7 TrendFollower

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.7` | `LLMTrendFollower` |
| Prompt | `LLM_TREND_FOLLOWER_SYS` |

## §3 Market Mechanism

The LLM market mirrors the Rule price/fundamental-drift mechanism and does not
consume `provides_liquidity`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Players | `examples/MomentumEffect/LLM/players.py` |
| Prompts | `examples/MomentumEffect/LLM/prompts.py` |
| Parser | `parse_llm_response_with_thinking` |
| Error handling | Retry plus explicit conservative fallback hold |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MomentumEffect/LLM/simulation.yml` | 200-round entry point |
| `configs/MomentumEffect/LLM/players.yml` | API roles and model configuration |
| `configs/MomentumEffect/LLM/topology.yml` | Message routing |
| `configs/MomentumEffect/LLM/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MomentumEffect/LLM/run_momentum_llm.py -c configs/MomentumEffect/LLM/simulation.yml
```

## §7 Expected Behavior

The run should preserve momentum continuation while allowing stochastic
variation in role conviction and order size.

## §8 References

See `examples/MomentumEffect/simulation-bases.md §2`.

## §9 Variant Comparison

Compare against Rule for mechanism shape and against RuleLLM for the effect of
explicit rule text.
