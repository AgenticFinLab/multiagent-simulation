# Tulip Mania Rule Variant Explanation

## §1 Overview

The Rule variant is the deterministic baseline for the TulipMania current-market
quantity schema. It preserves the market mechanism and investor formulas
defined in `simulation-bases.md`.

## §2 Theory -> Implementation Mapping

| Investor | Theory Component | Implementation |
|---|---|---|
| `TrendChaser` | `simulation-bases.md §4.1` positive-feedback demand | `TrendChaser._make_decision` buys positive deviation and sells negative deviation. |
| `SocialProofFollower` | `simulation-bases.md §4.2` social-proof demand | `SocialProofFollower._make_decision` uses the same formula interpreted as crowd validation. |
| `IntrinsicValueTrader` | `simulation-bases.md §4.3` intrinsic-value resistance | `IntrinsicValueTrader._make_decision` buys discounts and sells overvaluation. |
| `EarlyExitTrader` | `simulation-bases.md §4.4` strategic early exit | `EarlyExitTrader._make_decision` sells large overvaluation as peak-exit pressure. |
| `NoiseTrader` | `simulation-bases.md §4.5` stochastic liquidity | `NoiseTrader._make_decision` samples occasional random buy/sell orders. |

## §3 Market Mechanism

`Market` in `examples/TulipMania/Rule/players.py` aggregates buy and sell
quantities and updates price through price impact, mean reversion, and Gaussian
noise. It consumes only `action` and `quantity`; no `bid_price` field is used.

## §4 Variant Architecture

The coordinator is `Market`; investors inherit `BaseInvestor`; deterministic
decisions are constructed directly in Python. The output order is a
current-market quantity order sent through `investor_order` messages.

## §5 Config Reference

`configs/TulipMania/Rule/simulation.yml` sets the 200-round experiment entry.
`players.yml` binds player classes and initial portfolios. `topology.yml`
routes market broadcasts to investors and investor orders back to the market.

## §6 Running Instructions

```bash
python examples/TulipMania/Rule/run_tulipmania.py -c configs/TulipMania/Rule/simulation.yml
```

## §7 Expected Behavior

Trend and social-proof demand should lift prices when positive deviation grows.
Intrinsic-value and early-exit traders should generate selling pressure when
prices are materially above the intrinsic anchor. Noise traders add background
volume.

## §8 References

The theoretical basis is listed in `simulation-bases.md §2`; investor-specific
references are mapped in `simulation-bases.md §4`.

## §9 Variant Comparison

This variant is the baseline for comparing stochastic LLM, RuleLLM, and Rag
decision mechanisms under the same market and order schema.
