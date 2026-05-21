# MentalAccounting Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Simulation | MentalAccounting |
| Decision Mechanism | Deterministic account-level formulas |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `net_demand`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 MentalAccountant (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Account segregation | `MentalAccountant._make_decision()` computes `position / num_accounts`. |
| Account-local P&L | Uses `entry_price` and current `price` to calculate local P&L. |
| Realization behavior | Sells part of one account after configured gain/loss thresholds. |

### §2.2 HouseMoneyTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Gains increase risk appetite | Uses `gain_risk_multiplier` when P&L is positive. |
| Losses reduce risk appetite | Uses `loss_risk_multiplier` otherwise. |
| Value-direction trading | Buys undervaluation and sells overvaluation when deviation exceeds threshold. |

### §2.3 RationalPortfolioManager (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Whole-portfolio rationality | Ignores mental-account labels and trades on aggregate deviation. |
| Risk-scaled sizing | Uses `risk_aversion`, `quantity_scale`, and `base_size`. |
| Stabilization | Buys below fundamental and sells above fundamental. |

### §2.4 SunkCostHolder (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Sunk-cost inertia | Holds losers instead of realizing losses. |
| Winner realization | Sells configured fraction only after gains exceed 10%. |
| Sticky inventory | Maintains losing positions unless the winner threshold appears. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Noise liquidity | Trades with `trade_probability`. |
| Random direction | Randomly chooses buy or sell. |
| Bounded random size | Uses config `noise_size` and cash/inventory constraints. |

## §3 Market Mechanism

The market implements `P(t+1) = max(0.01, P(t) + lambda * net_demand + gamma * (F - P(t)) + epsilon)`. It records `price`, `fundamental`, and `volume` for analysis.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | `Market` in `Rule/players.py` |
| Investors | Five deterministic investor classes |
| Order Schema | Canonical order with `type`, `from`, `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, `strategy` |
| Failure Policy | Missing or invalid required market/account data raises immediately. |

## §5 Config Reference

Primary config: `configs/MentalAccounting/Rule/simulation.yml`. Investor parameters live in `configs/MentalAccounting/Rule/players.yml`.

## §6 Running Instructions

```bash
python examples/MentalAccounting/Rule/run_mentalaccounting.py \
  -c configs/MentalAccounting/Rule/simulation.yml
```

## §7 Expected Behavior

- Account-level and sunk-cost agents create non-rational order flow.
- RationalPortfolioManager provides stabilizing whole-portfolio trades.
- NoiseTrader adds background liquidity.
- Full runs produce the standard analysis output set.

## §8 References

See `simulation-bases.md §2` for full citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
