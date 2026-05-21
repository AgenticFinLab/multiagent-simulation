# Reversal Effect Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Decision Mechanism | deterministic trading rules |
| Scenario Contract | trading-schema orders |
| Theory Reference | `examples/ReversalEffect/simulation-bases.md` |

The Rule variant is the deterministic baseline for reversal dynamics. It uses
six configured roles: ContrarianInvestor, MomentumInvestor,
OverconfidentTrader, NoiseTrader, ValueInvestor, and IndexTracker.

## §2 Theory -> Implementation Mapping

| Theory Component | Implementation |
|---|---|
| ContrarianInvestor, `simulation-bases.md §4.1` | `ContrarianInvestor` buys after sufficiently negative recent returns and sells after sufficiently positive recent returns. |
| MomentumInvestor, `simulation-bases.md §4.2` | `MomentumInvestor` follows recent return direction and can delay correction. |
| OverconfidentTrader, `simulation-bases.md §4.3` | `OverconfidentTrader` scales directional reaction by overconfidence parameters. |
| NoiseTrader, `simulation-bases.md §4.4` | `NoiseTrader` adds stochastic order flow with bounded inventory behavior. |
| ValueInvestor, `simulation-bases.md §4.5` | `ValueInvestor` trades against price-fundamental deviations. |
| IndexTracker, `simulation-bases.md §4.6` | `IndexTracker` rebalances toward configured target exposure. |

## §3 Market Mechanism

`Market` in `examples/ReversalEffect/Rule/players.py` broadcasts price,
fundamental value, recent return, volume, and net demand. It aggregates signed
orders, applies price impact and mean reversion, and records the series consumed
by the standard analysis helper.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ReversalEffect/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Direct deterministic order construction |
| Error handling | Deterministic config/schema errors fail fast |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ReversalEffect/Rule/simulation.yml` | Full 200-round entry point. |
| `configs/ReversalEffect/Rule/players.yml` | Market and six investor definitions. |
| `configs/ReversalEffect/Rule/topology.yml` | Broadcast and order routing. |
| `configs/ReversalEffect/Rule/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/ReversalEffect/Rule/run_reversal.py -c configs/ReversalEffect/Rule/simulation.yml
```

## §7 Expected Behavior

The path should show price deviation, continuation pressure from momentum or
overconfidence, and later correction pressure from contrarian and value orders.
The baseline should produce complete finite market series and nonzero volume.

## §8 References

See `examples/ReversalEffect/simulation-bases.md §2` for theoretical
references and `analysis-bases.md §2` for metric contracts.

## §9 Variant Comparison

Rule is the deterministic benchmark. LLM tests persona-driven stochastic orders,
RuleLLM adds explicit quantitative rules under liquidity-aware pricing, and Rag
adds retrieved domain context plus retrieval audit artifacts.
