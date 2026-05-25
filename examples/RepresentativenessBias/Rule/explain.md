# RepresentativenessBias Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Simulation | RepresentativenessBias |
| Decision Mechanism | Deterministic prototype, category, Bayesian, contrarian, and noise rules |
| Theory Reference | `simulation-bases.md §2` and `§4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 PatternMatcher (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Prototype matching | `PatternMatcher._make_decision()` trades when `abs(deviation) > 0.02` |
| Base-rate neglect | Trades in the same direction as salient deviation rather than against fundamental |
| Quantity scaling | `min(800, int(abs(deviation) * 5000))` |

### §2.2 CategoryOvergeneralizer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Small-sample category extrapolation | `CategoryOvergeneralizer._make_decision()` uses the same deviation trigger as PatternMatcher |
| Category narrative strength | Config exposes `category_weight` and `sample_bias` for scenario documentation and prompt parity |
| Order cap | Quantity is capped by cash or current position |

### §2.3 BayesianUpdater (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Base-rate disciplined correction | `BayesianUpdater._make_decision()` activates only when `abs(deviation) > 0.05` |
| Undervaluation / overvaluation | Buys negative deviations and sells positive deviations |
| Quantity scaling | `min(500, int(abs(deviation) * 3000))` |

### §2.4 ContrarianStatistical (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Arbitrage against biased beliefs | `ContrarianStatistical._make_decision()` trades against large deviations |
| Capital discipline | Quantity capped at 500 and then by cash or position |
| Correction threshold | Uses the same 5% activation band as the Bayesian benchmark |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Uninformed liquidity | `NoiseTrader._make_decision()` uses `trade_probability` from config |
| Random direction | Buy/sell chosen by random draw |
| Order size | Random integer between 100 and 500, capped by state |

## §3 Market Mechanism

`Market._clear_market()` implements the root price equation:

```text
P_{t+1} = max(0.01, P_t + price_impact * NetDemand_t + mean_reversion * (F - P_t) + noise_t)
```

## §4 Variant Architecture

Rule agents receive market state, compute deterministic actions, emit canonical
orders with `action`, `bid_price`, `quantity`, `agent_type`, and `reasoning`,
and update cash/position during `act()`.

## §5 Config Reference

Primary config: `configs/RepresentativenessBias/Rule/players.yml`.
Key extras include `pattern_sensitivity`, `base_rate_ignore`, `category_weight`,
`sample_bias`, `base_rate_weight`, `evidence_weight`, `contrarian_threshold`,
and `trade_probability`.

## §6 Running Instructions

```bash
python examples/RepresentativenessBias/Rule/run_representativenessbias.py \
  -c configs/RepresentativenessBias/Rule/simulation.yml
```

## §7 Expected Behavior

PatternMatcher and CategoryOvergeneralizer should create early directional
pressure from salient deviations. BayesianUpdater and ContrarianStatistical
should offset deviations after larger mispricing appears.

## §8 References

See `simulation-bases.md §2` for full citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison.
