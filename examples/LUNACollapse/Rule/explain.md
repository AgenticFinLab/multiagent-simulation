# LUNACollapse Rule — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Deterministic threshold rules |
| Key Difference | Establishes the fixed death-spiral baseline |
| Runtime Change | Threshold semantics aligned to configured deviation thresholds; rerun required |

## §2 Theory To Implementation Mapping

| Design Element | Implementation |
|---|---|
| StablecoinHolder (`simulation-bases.md §4.1`) | `StablecoinHolder.decide()` sells 50% when `deviation < -redemption_threshold` |
| Arbitrageur (`simulation-bases.md §4.2`) | `Arbitrageur.decide()` trades when `abs(deviation) > arb_threshold`, capped at 5000 |
| DeFiLender (`simulation-bases.md §4.3`) | `DeFiLender.decide()` sells 60% when `deviation < -liquidation_threshold` |
| AnchorDepositor (`simulation-bases.md §4.4`) | `AnchorDepositor.decide()` sells 40% when `deviation < -yield_threshold` |
| ValueBuyer (`simulation-bases.md §4.5`) | `ValueBuyer.decide()` buys deep discounts using 20% of cash, capped at 1000 |

## §3 Market Mechanism Implementation

`Market` is implemented in `players.py` and follows
`simulation-bases.md §3`: price changes with net demand, mean reversion, and
Gaussian noise, then broadcasts `price`, `fundamental`, `deviation`, and
`round`.

## §4 Variant-Specific Features

Rule uses only deterministic Python logic and direct required-key config access.
It is the baseline for evaluating whether LLM, RuleLLM, and Rag preserve or
alter the stablecoin death-spiral mechanism.

## §5 Architecture Diagram

```text
Market broadcast -> Rule investor threshold decision -> order -> Market clearing
```

## §6 Configuration Reference

Primary config: `configs/LUNACollapse/Rule/players.yml`. Key thresholds are
`redemption_threshold=0.05`, `arb_threshold=0.02`,
`liquidation_threshold=0.15`, `yield_threshold=0.05`, and
`discount_threshold=0.30`.

## §7 Expected Behavior Patterns

Destabilizing redemptions, arbitrage, liquidations, and yield exits should
dominate ValueBuyer demand once confidence breaks.

## §8 Validation Checklist

Verify full rounds, canonical order schema, price/portfolio sanity, and sell
pressure attribution before accepting a sample.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
