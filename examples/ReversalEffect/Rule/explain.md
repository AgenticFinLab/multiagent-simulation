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

### §2.1 ContrarianInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Contrarian reversal pressure | `ContrarianInvestor` buys after sufficiently negative recent returns and sells after sufficiently positive recent returns. |
| Order schema | Emits deterministic signed quantity, bid price, strategy, and investor label. |

### §2.2 MomentumInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Continuation pressure | `MomentumInvestor` follows recent return direction and can delay correction. |
| Order schema | Emits trend-following signed quantity under configured thresholds. |

### §2.3 OverconfidentTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Signal overweighting | `OverconfidentTrader` scales directional reaction by overconfidence parameters. |
| Order schema | Emits larger directional orders when recent return signals exceed thresholds. |

### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Stochastic background flow | `NoiseTrader` adds random order flow with bounded inventory behavior. |
| Order schema | Emits small stochastic buy or sell quantities around current price. |

### §2.5 ValueInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Fundamental anchoring | `ValueInvestor` trades against price-fundamental deviations. |
| Order schema | Emits value-side signed quantities when mispricing exceeds threshold. |

### §2.6 IndexTracker (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Passive rebalancing | `IndexTracker` rebalances toward configured target exposure. |
| Variant scope | Present only in the deterministic Rule baseline. |

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
