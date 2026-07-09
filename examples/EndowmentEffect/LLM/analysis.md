# EndowmentEffect LLM — Analysis Guide

## 1. Analysis Objectives

The LLM variant uses the same market-level evaluation contract as the Rule
baseline. Analysis measures price displacement, persistence, volume, premium
capture, portfolio wealth, and turnover while retaining model reasoning for
qualitative persona-adherence review.

## 2. Metric → Function Mapping

| Metric from `analysis-bases.md §2` | Function available from `LLM/analysis.py` |
|---|---|
| §2.1 Price Deviation (PD) | `price_deviation(price_history, fundamental)` |
| §2.2 Mean Absolute Deviation (MAD) | `mean_absolute_deviation(price_history, fundamental)` |
| §2.3 Deviation Persistence Half-Life (DPHL) | `deviation_half_life(price_history, fundamental)` |
| §2.4 Volume Suppression Ratio (VSR) | `volume_suppression_ratio(actual_volume, rational_volume)` |
| §2.5 Endowment Premium Capture Rate (EPCR) | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)` |
| §2.6 Portfolio Wealth Ratio (PWR) | `portfolio_wealth_ratio(cash_history, position_history, final_price, initial_wealth)` |
| §2.7 Turnover Rate (TR) | `turnover_rate(trades_by_agent, mean_position, total_rounds)` |

Shared loading, aggregation, visualization, and validation functions are
imported explicitly from `Rule/analysis.py` and exported through `__all__`.

## 3. Data Inputs and Preparation

`load_simulation_data(config)` reads the coordinator price history and player
order payloads from MASim results. Required payload fields are accessed
directly. The analysis fails if coordinator prices or player orders are absent;
it does not synthesize missing observations.

DPHL uses a log-linear fit over non-zero absolute deviations. A non-decaying
series returns positive infinity. PWR and TR require portfolio histories or
derived per-agent series when called; they reject empty or invalid denominators.

## 4. LLM-Specific Analysis

Core quantitative metrics remain variant-neutral. For the LLM variant, compare
the order `reasoning` and `analysis` fields with the emitting class's persona:

- attachment-driven and inertia-prone investors should give persona-consistent
  reasons when preserving inventory;
- the fundamental investor should reason symmetrically about signed deviation;
- the prospective buyer should avoid ownership-history arguments;
- the intermittently engaged trader should not present a stable threshold rule.

These are interpretive checks, not replacements for the quantitative metrics.

## 5. Expected Results and Comparisons

Calibration targets and red-flag thresholds are defined in
`analysis-bases.md §§2 and 6`. Treat them as validation targets, not guaranteed
outputs. Compare LLM results with the Rule variant using identical round counts,
initial portfolios, market parameters, and agent composition. Because inference
is stochastic, report the model identifier, generation settings, and repeated-run
dispersion when making substantive comparisons.

## 6. Output Artifacts

Running `analysis.py` delegates the main pipeline to `Rule/analysis.py` and
writes `summary.json` plus the standard PNG outputs under the analysis directory
next to the configured record path. The shared outputs are:

- `00_investor_bids.png`
- `01_endowmenteffect_dynamics.png`
- `02_endowmenteffect_analysis.png`
- `03_summary.png`

## 7. Validation Criteria

A valid full experiment has the configured 200 market rounds, non-empty price
and order records, finite bounded core metrics, and the canonical order fields.
A smoke run only establishes startup and round execution; it does not establish
the empirical targets in `analysis-bases.md`. Run analysis with:

```bash
python -m examples.EndowmentEffect.LLM.analysis \
  -c configs/EndowmentEffect/LLM/simulation.yml
```
