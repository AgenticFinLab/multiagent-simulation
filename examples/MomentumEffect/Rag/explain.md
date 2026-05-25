# Momentum Effect Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | MomentumEffect |
| Decision Mechanism | Rule-guided API trading with retrieved domain context |
| Theory Reference | `examples/MomentumEffect/simulation-bases.md` |
| Market Broadcast | `configs/MomentumEffect/Rag/topology.yml` |

This variant keeps the RuleLLM five-role set and records per-round
`rag_context` for retrieval-quality audit.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | `RagLLMMomentumTrader` |
| Prompt | `RAGLLM_MOMENTUM_TRADER_SYS` |

### §2.2 ContrarianTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | `RagLLMContrarianTrader` |
| Prompt | `RAGLLM_CONTRARIAN_TRADER_SYS` |

### §2.3 IndexFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Not configured in this Rag variant |

### §2.4 MarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Not configured in this Rag variant |

### §2.5 TechnicalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | `RagLLMTechnicalTrader` |
| Prompt | `RAGLLM_TECHNICAL_TRADER_SYS` |

### §2.6 FundamentalAnchor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | `RagLLMFundamentalAnchor` |
| Prompt | `RAGLLM_FUNDAMENTAL_ANCHOR_SYS` |

### §2.7 TrendFollower

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.7` | `RagLLMTrendFollower` |
| Prompt | `RAGLLM_TREND_FOLLOWER_SYS` |

## §3 Market Mechanism

The Rag market matches the RuleLLM liquidity-sensitive coordinator and consumes
`provides_liquidity`. Players retrieve context, inject it into prompts, and
record the resolved `rag_context`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Players | `examples/MomentumEffect/Rag/players.py` |
| Prompts | `examples/MomentumEffect/Rag/prompts.py` |
| Retrieval | Unified `masim.knowledge` stack |
| Analysis | Standard output contract plus `rag_stats.json` |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MomentumEffect/Rag/simulation.yml` | 200-round entry point |
| `configs/MomentumEffect/Rag/players.yml` | RAG, prompt, and API model configuration |
| `configs/MomentumEffect/Rag/topology.yml` | Message routing |
| `configs/MomentumEffect/Rag/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MomentumEffect/Rag/run_momentum_effect_ragllm.py -c configs/MomentumEffect/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve RuleLLM strategy direction while allowing retrieved
momentum literature to affect reasoning and conviction. Successful samples must
be audited for retrieval coverage.

## §8 References

See `examples/MomentumEffect/simulation-bases.md §2`.

## §9 Variant Comparison

Use Rag to test whether retrieved knowledge changes trend-following intensity
or stabilization timing relative to RuleLLM.
