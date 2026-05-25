# Momentum Effect Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | MomentumEffect |
| Decision Mechanism | Deterministic rule-based momentum trading |
| Theory Reference | `examples/MomentumEffect/simulation-bases.md` |
| Market Broadcast | `configs/MomentumEffect/Rule/topology.yml` |

This is the full six-role deterministic baseline.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | `MomentumTrader` in `examples/MomentumEffect/Rule/players.py` |
| Config | `configs/MomentumEffect/Rule/players.yml:momentum_trader` |

### §2.2 ContrarianTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | `ContrarianTrader` in `examples/MomentumEffect/Rule/players.py` |
| Config | `configs/MomentumEffect/Rule/players.yml:contrarian_trader` |

### §2.3 IndexFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | `IndexFund` in `examples/MomentumEffect/Rule/players.py` |
| Config | `configs/MomentumEffect/Rule/players.yml:index_fund` |

### §2.4 MarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | `MarketMaker` in `examples/MomentumEffect/Rule/players.py` |
| Config | `configs/MomentumEffect/Rule/players.yml:market_maker` |

### §2.5 TechnicalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | `TechnicalTrader` in `examples/MomentumEffect/Rule/players.py` |
| Config | `configs/MomentumEffect/Rule/players.yml:technical_trader` |

### §2.6 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | `FundamentalTrader` in `examples/MomentumEffect/Rule/players.py` |
| Config | `configs/MomentumEffect/Rule/players.yml:fundamental_trader` |

## §3 Market Mechanism

`examples/MomentumEffect/Rule/players.py:Market` updates price from net demand,
weak mean reversion to drifting fundamental value, and noise. It emits
`momentum_5`, returns, volume, net demand, and fundamental value.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Players | `examples/MomentumEffect/Rule/players.py` |
| Prompts | Not applicable |
| Analysis | `examples/MomentumEffect/Rule/analysis.py` |
| Parser | Direct deterministic order construction |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MomentumEffect/Rule/simulation.yml` | 200-round entry point |
| `configs/MomentumEffect/Rule/players.yml` | Six-role baseline parameters |
| `configs/MomentumEffect/Rule/topology.yml` | Market/order message routing |
| `configs/MomentumEffect/Rule/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MomentumEffect/Rule/run_momentum.py -c configs/MomentumEffect/Rule/simulation.yml
```

## §7 Expected Behavior

The Rule baseline should produce observable return continuation when momentum
and technical agents react to recent returns, followed by dampening from
contrarian, passive, market-making, and fundamental roles.

## §8 References

See `examples/MomentumEffect/simulation-bases.md §2`.

## §9 Variant Comparison

Use this variant as the deterministic reference for LLM, RuleLLM, and Rag.
