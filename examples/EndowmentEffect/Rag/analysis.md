# EndowmentEffect Rag — Analysis Guide

## 1. Analysis Objectives

The Rag variant retains the market-level contract of the Rule baseline and adds
retrieval observability. Analysis measures price displacement, persistence,
volume, premium capture, wealth, and turnover, while separately reporting
whether each recorded decision contained retrieved or fallback context.

## 2. Metric → Function Mapping

| Metric from `analysis-bases.md §2` | Function in `Rag/analysis.py` |
|---|---|
| §2.1 Price Deviation (PD) | `price_deviation(price_history, fundamental)` |
| §2.2 Mean Absolute Deviation (MAD) | `mean_absolute_deviation(price_history, fundamental)` |
| §2.3 Deviation Persistence Half-Life (DPHL) | `deviation_half_life(price_history, fundamental)` |
| §2.4 Volume Suppression Ratio (VSR) | `volume_suppression_ratio(actual_volume, rational_volume)` |
| §2.5 Endowment Premium Capture Rate (EPCR) | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)` |
| §2.6 Portfolio Wealth Ratio (PWR) | `portfolio_wealth_ratio(cash_history, position_history, final_price, initial_wealth)` |
| §2.7 Turnover Rate (TR) | `turnover_rate(trades_by_agent, mean_position, total_rounds)` |

`analyze_rag_knowledge_effect(trades)` additionally reports payload coverage,
fallback count, retrieval rate, and fallback rate. `_RAG_FALLBACK` is the exact
sentinel shared by `players.py` and this analysis module.

## 3. Data Inputs and Preparation

`load_simulation_data(config)` reads coordinator price history and player order
payloads from MASim records. Required fields are accessed directly. Empty trade
sets, missing `rag_context` fields, invalid denominators, and insufficient
half-life observations raise errors rather than generating synthetic defaults.

Retrieval coverage is an operational metric: it shows that context reached the
decision payload. It does not prove that the context was relevant or causal.

## 4. Rag-Specific Analysis

Review retrieved context alongside the order's `analysis` and `reasoning`:

- endowed holders should preserve attachment and reservation-price behavior;
- status-quo sellers should preserve inertia when evidence is mixed;
- arbitrageurs should evaluate signed fundamental deviation symmetrically;
- prospective buyers should avoid ownership-history arguments;
- noise traders should remain intermittent rather than inventing a stable rule.

Compare outcomes with both LLM and RuleLLM using the same seed, model settings,
market configuration, and corpus/index version. A high retrieval rate alone is
not evidence that Rag improves empirical fidelity.

## 5. Expected Results and Comparisons

Use `analysis-bases.md §§2 and 6` as calibration targets, not guaranteed
outputs. Report repeated-run dispersion because model sampling and retrieval
ranking are stochastic. Any claim that retrieval changed MAD, DPHL, VSR, EPCR,
PWR, or TR requires a matched non-Rag comparison; retrieval statistics alone
cannot identify that effect.

## 6. Output Artifacts

The analysis writes `summary.json`, `rag_stats.json`, and the shared Rule
visualization set under the analysis directory next to the configured record
path:

- `00_investor_bids.png`
- `01_endowmenteffect_dynamics.png`
- `02_endowmenteffect_analysis.png`
- `03_summary.png`

## 7. Validation Criteria

A valid full run has the configured market rounds, non-empty price and order
records, canonical order fields, a `rag_context` field on every Rag order, and
finite bounded core metrics. A smoke run establishes startup and round
execution only; it does not establish the empirical targets. Run analysis with:

```bash
python -m examples.EndowmentEffect.Rag.analysis \
  -c configs/EndowmentEffect/Rag/simulation.yml
```
