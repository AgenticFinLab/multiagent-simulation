# Market Crash Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | MarketCrash |
| Decision Mechanism | Deterministic rule-based orders |
| Theory Reference | `examples/MarketCrash/simulation-bases.md` |
| Market Broadcast | `configs/MarketCrash/Rule/topology.yml` |

This variant is the full six-archetype baseline and is the only MarketCrash
variant that includes `PassiveInvestor`.

## §2 Theory -> Implementation Mapping

### §2.1 RiskParityFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Volatility targeting and procyclical selling | `RiskParityFund` in `examples/MarketCrash/Rule/players.py` reads target-volatility parameters from `configs/MarketCrash/Rule/players.yml`. |
| Order schema | Emits signed `quantity`, `bid_price`, `strategy`, and `investor`. |

### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Margin spiral and forced deleveraging | `LeveragedHedgeFund` monitors leverage and liquidation thresholds in `players.py`. |
| Order schema | Emits forced sell orders when configured stress thresholds are crossed. |

### §2.3 MarketMaker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Liquidity supply and withdrawal | `MarketMaker` reduces quote size under high volatility and inventory stress. |
| Order schema | Emits stabilizing or inventory-management orders without API fields. |

### §2.4 PassiveInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Slow rebalancing stabilizer | `PassiveInvestor` trades toward target exposure on configured rebalance rounds. |
| Variant scope | Present only in the Rule baseline. |

### §2.5 PanicSeller (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Behavioral panic selling | `PanicSeller` reacts to drawdown and crash-trigger thresholds. |
| Order schema | Sells a configured fraction of position during panic states. |

### §2.6 BottomFisher (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Contrarian crash absorption | `BottomFisher` buys after discount or crash-return triggers. |
| Order schema | Emits buy orders subject to configured size and cash constraints. |

## §3 Market Mechanism

The Rule coordinator in `examples/MarketCrash/Rule/players.py:Market` updates:
price, volatility, liquidity, volume, net demand, and crash state. It does not
use `provides_liquidity`; instead, it computes liquidity endogenously from its
own state variables.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/MarketCrash/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Direct deterministic order construction |
| Error handling | Deterministic fail-fast only |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MarketCrash/Rule/simulation.yml` | Full simulation entry point |
| `configs/MarketCrash/Rule/players.yml` | Investor set and parameters |
| `configs/MarketCrash/Rule/topology.yml` | Market-to-investor routing |
| `configs/MarketCrash/Rule/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MarketCrash/Rule/run_crash.py -c configs/MarketCrash/Rule/simulation.yml
```

## §7 Expected Behavior

The Rule run should produce a reproducible crash path in which volatility
targeting, leverage, panic selling, and reduced liquidity can jointly amplify
drawdowns, while PassiveInvestor and BottomFisher provide delayed stabilization.

## §8 References

See `examples/MarketCrash/simulation-bases.md §2`.

## §9 Variant Comparison

Use this variant as the mechanism baseline when judging LLM, RuleLLM, and Rag.
