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

Implemented by `RiskParityFund` in
`examples/MarketCrash/Rule/players.py` with parameters from
`configs/MarketCrash/Rule/players.yml`.

### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

Implemented by `LeveragedHedgeFund` in
`examples/MarketCrash/Rule/players.py`.

### §2.3 MarketMaker (simulation-bases.md §4.3)

Implemented by `MarketMaker` in `examples/MarketCrash/Rule/players.py`.

### §2.4 PassiveInvestor (simulation-bases.md §4.4)

Implemented by `PassiveInvestor` in
`examples/MarketCrash/Rule/players.py`. This archetype is present only in the
Rule baseline.

### §2.5 PanicSeller (simulation-bases.md §4.5)

Implemented by `PanicSeller` in `examples/MarketCrash/Rule/players.py`.

### §2.6 BottomFisher (simulation-bases.md §4.6)

Implemented by `BottomFisher` in `examples/MarketCrash/Rule/players.py`.

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
