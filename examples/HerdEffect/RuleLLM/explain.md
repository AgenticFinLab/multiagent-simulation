# HerdEffect RuleLLM — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                                         |
|--------------------|--------------------------------------------------------------------------------|
| Variant            | RuleLLM                                                                        |
| Simulation         | HerdEffect                                                                     |
| Decision Mechanism | Rule `calculate_bid()` + LLM narrative reasoning overlay                       |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                |
| Market Broadcast   | `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `round` |
| Price Model        | Same order-book clearing as Rule — Market agent unchanged                      |

The RuleLLM variant uses the deterministic `calculate_bid()` formulas as the primary decision engine, with an LLM narrative layer that provides explanatory context and optional override capacity. Rule formulas dominate; LLM adds nuance without replacing the mathematical backbone.

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMMomentumInvestor (simulation-bases.md §4.1)

| Theory Component                 | Implementation                                                                  |
|----------------------------------|---------------------------------------------------------------------------------|
| Shiller (1984) positive feedback | Rule formula: `bid_price = price × (1 + lambda_price × ret)` (primary)          |
| LLM narrative layer              | LLM explains momentum reasoning; may suggest small adjustments to quantity      |
| Behavioral authenticity          | Rule backbone ensures consistent positive feedback; LLM adds graduated language |

### §2.2 RuleLLMContrarianInvestor (simulation-bases.md §4.2)

| Theory Component                        | Implementation                                                       |
|-----------------------------------------|----------------------------------------------------------------------|
| De Bondt & Thaler (1985) mean reversion | Rule formula: `bid_price = fundamental + N(0, noise_std)` (primary)  |
| Fundamental source                      | Reads from own `extras` (not broadcast) — same as Rule               |
| LLM narrative                           | LLM articulates value reasoning; contrarian signal from Rule formula |

### §2.3 RuleLLMRiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component               | Implementation                                                                            |
|--------------------------------|-------------------------------------------------------------------------------------------|
| Markowitz (1952) mean-variance | Rule variance calculation: `k / variance × cash / P` (primary)                            |
| LLM overlay                    | LLM describes risk context; may reinforce early exit when volatility narrative is salient |

### §2.4 RuleLLMNoiseTrader (simulation-bases.md §4.4)

| Theory Component                    | Implementation                            |
|-------------------------------------|-------------------------------------------|
| De Long et al. (1990) noise trading | Rule random bid/quantity (primary)        |
| LLM narrative                       | Adds qualitative context to random trades |

### §2.5 RuleLLMAggressiveInvestor (simulation-bases.md §4.5)

| Theory Component                  | Implementation                                                     |
|-----------------------------------|--------------------------------------------------------------------|
| Leveraged momentum + acceleration | Rule formula: `kappa × ret + accel_bonus × acceleration` (primary) |
| LLM narrative                     | Articulates aggressive conviction; bounded by Rule's ±80 cap       |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + α × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Identical to Rule variant. RuleLLM formulas produce the same mathematical bid structure — LLM narrative does not alter the clearing mechanism.

## §4 Variant Architecture

| Component      | Detail                                                         |
|----------------|----------------------------------------------------------------|
| Base class     | `BaseInvestor` (RuleLLM subclass)                              |
| Primary engine | `calculate_bid()` rule formulas                                |
| LLM role       | Narrative and minor override layer                             |
| Inference      | `LangChainAPIInference` (called after rule calculation)        |
| Output         | Same `{bid_price, quantity, strategy, cash, position}` as Rule |

## §5 Config Reference

Config file: `configs/HerdEffect/RuleLLM/simulation.yml`

Key extras:
- All Rule parameters (lambda_price, beta, kappa, accel_bonus, etc.)
- `lm_name`: LLM model identifier
- `system_prompt`: persona for LLM narrative layer
- Market config unchanged from Rule variant

## §6 Running Instructions

```bash
python -m examples.HerdEffect.RuleLLM.run_herd_effect \
    -c configs/HerdEffect/RuleLLM/simulation.yml
```

Or via Streamlit UI: select "HerdEffect" → "RuleLLM" variant.

## §7 Expected Behavior

- **Near-Rule dynamics**: Rule formulas dominate; EMI, MDD, HVR close to Rule baseline
- **Moderate LLM influence**: Small deviations from Rule when LLM narrative overrides at margin
- **Consistent early exit**: RiskAverseInvestor rule formula unchanged → REI similar to Rule
- **Explainability**: LLM narrative provides human-readable explanation of each agent's decision
- **Lower variance than LLM**: More reproducible than pure LLM due to formula backbone

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Shiller (1984) `doi:10.2307/2534436` — RuleLLMMomentumInvestor
- De Bondt & Thaler (1985) `doi:10.1111/j.1540-6261.1985.tb05004.x` — RuleLLMContrarianInvestor
- Markowitz (1952) `doi:10.1111/j.1540-6261.1952.tb01525.x` — RuleLLMRiskAverseInvestor

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
