# HerdingInformation Rule — Analysis Guide

## §1 Analysis Objectives

The Rule variant analysis measures the **deterministic baseline** of HerdingInformation cascade dynamics. Because all five investors apply fixed threshold formulas with no stochastic reasoning, the Rule variant provides:

1. The cleanest signal for cascade formation timing and intensity
2. The reference CCI/CPD/RHI values against which LLM/RuleLLM/Rag variants are compared
3. The tightest expected metric bands (lowest variance across seeds)

Analysis objectives:
- Confirm CCI rises into the 0.40–0.70 target range during cascade episodes
- Verify CPD of 3–10 rounds per cascade episode
- Validate RHI in 0.50–1.20 (balanced dual mechanism)
- Confirm ICE in 0.15–0.40 (moderate information destruction)
- Verify VAF in 1.5–3.5 (cascade amplifies volatility)
- Confirm WDI in 0.10–0.30 (rational agents profit from cascade)

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md | Python Function                     | Primary Input                             |
|--------|---------------------------------|-------------------|-------------------------------------|-------------------------------------------|
| CCI    | Cascade Concentration Index     | §2.1              | `cascade_concentration_index()`     | trade_history, price_history, fundamental |
| CPD    | Cascade Persistence Duration    | §2.2              | `cascade_persistence_duration()`    | price_history, fundamental                |
| RHI    | Reputation Herding Index        | §2.3              | `reputation_herding_index()`        | trade_history, price_history, fundamental |
| ICE    | Information Cascade Efficiency  | §2.4              | `information_cascade_efficiency()`  | trade_history, price_history, fundamental |
| VAF    | Volatility Amplification Factor | §2.5              | `volatility_amplification_factor()` | price_history, fundamental                |
| WDI    | Wealth Distribution Index       | §2.6              | `wealth_distribution_index()`       | agent_states, final_price                 |

All functions defined in `Rule/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 Rule-Specific Notes

- **Cascade timing is deterministic**: Given the same random seed, CascadeFollower activates at exactly the same round — cascade_count reaches `cascade_trigger` (default: 3) at a predictable point. This makes Rule the most reproducible variant.
- **No LLM stochasticity**: Metric variance across seeds is driven entirely by the `noise_std` term in the price model and NoiseTrader's random trades. Expected inter-seed variance: ±0.03 for CCI, ±1.2 rounds for CPD.
- **Cascade threshold hierarchy**: ReputationHerder activates at |deviation| > 0.02, CascadeFollower at cascade_count ≥ cascade_trigger. In early rounds, RHI may be high (ReputationHerder active, CascadeFollower not yet activated). After cascade activation, RHI converges to 0.50–1.20.
- **IndependentThinker and Contrarian**: Both trade against deviation. Combined correction capacity ≈ 900 shares < herding capacity ≈ 1,400 shares. Cascades are not immediately broken.
- **No fundamental deviation in HerdEffect comparison**: Unlike HerdEffect which uses momentum, HerdingInformation uses a `deviation` signal (P−F)/F — MAD (Mean Absolute Deviation) is not the appropriate measure here; use CPD and ICE instead.

---

## §4 Expected Ranges

| Metric | Rule Baseline | Notes                                                        |
|--------|---------------|--------------------------------------------------------------|
| CCI    | 0.40–0.70     | Higher end when cascade_trigger = 2 (earlier activation)     |
| CPD    | 3–10 rounds   | Tighter band vs. LLM (no reasoning variability)              |
| RHI    | 0.50–1.20     | Early rounds: RHI > 1.0 (reputation fires first)             |
| ICE    | 0.15–0.40     | Deterministic cascade = consistent information destruction   |
| VAF    | 1.5–3.5       | Rule produces tightest volatility band                       |
| WDI    | 0.10–0.30     | Moderate wealth transfer from cascade followers to rationals |

---

## §5 References

- `analysis-bases.md §2.1` — CCI definition, formula, interpretation
- `analysis-bases.md §2.2` — CPD definition, formula, interpretation
- `analysis-bases.md §2.3` — RHI definition, formula, interpretation
- `analysis-bases.md §2.4` — ICE definition, formula, interpretation
- `analysis-bases.md §2.5` — VAF definition, formula, interpretation
- `analysis-bases.md §2.6` — WDI definition, formula, interpretation
- `simulation-bases.md §4.1–§4.5` — Investor parameter definitions
- Banerjee (1992) `doi:10.2307/2118364` — Cascade formation baseline
- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — Cascade fragility and persistence
