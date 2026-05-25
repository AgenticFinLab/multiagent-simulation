# OverconfidenceBias Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Simulation | OverconfidenceBias |
| Decision Mechanism | Deterministic formulas and config thresholds |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 OverconfidentTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Signal overprecision | `_make_decision()` computes `signal = deviation * precision_overestimate`. |
| Excess turnover | Small perceived signals can trigger bounded buy/sell orders. |
| Order discipline | Quantity is capped by `base_size`, cash, and inventory. |

### §2.2 SelfAttributor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Success attribution | Positive deviation with inventory increases buying by `confidence_boost`. |
| Loss response | Negative deviation can trigger exposure trimming. |
| Path dependence | Current position gates favorable-state reinforcement. |

### §2.3 CalibratedTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Rational benchmark | Trades only when `abs(deviation) > trade_threshold`. |
| Signal discipline | Quantity scales with `signal_precision`. |
| Stabilization | Buys undervaluation and sells overvaluation. |

### §2.4 ContrarianInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Overreaction correction | Activates when deviation crosses `contrarian_threshold`. |
| Counter-trend trading | Sells overvaluation and buys undervaluation. |
| Stabilizing pressure | Uses bounded size and portfolio constraints. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | Trades with configured `trade_probability`. |
| Random flow | Randomly selects buy or sell when active. |
| Bounded uncertainty | Uses `noise_size` and portfolio constraints. |

## §3 Market Mechanism

The market implements `P(t+1) = max(0.01, P(t) + lambda * net_demand + gamma * (F - P(t)) + epsilon)`. It records price, fundamental value, and volume histories for standard analysis.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | `Market` in `Rule/players.py` |
| Investors | Five deterministic investor classes |
| Order Schema | Canonical order with `type`, `from`, `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, `strategy` |
| Failure Policy | Required scalar and config errors raise immediately. |

## §5 Config Reference

Primary config: `configs/OverconfidenceBias/Rule/simulation.yml`. Investor parameters live in `configs/OverconfidenceBias/Rule/players.yml`.

## §6 Running Instructions

```bash
python examples/OverconfidenceBias/Rule/run_overconfidencebias.py \
  -c configs/OverconfidenceBias/Rule/simulation.yml
```

## §7 Expected Behavior

- Overconfident and self-attributing agents generate more aggressive flow than calibrated agents.
- Contrarian and calibrated agents provide stabilizing pressure.
- NoiseTrader supplies background liquidity.
- Analysis outputs expose excess turnover, price deviation, and volatility.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
