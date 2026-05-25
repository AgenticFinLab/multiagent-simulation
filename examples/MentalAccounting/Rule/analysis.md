# MentalAccounting Rule — Analysis Specification

## §1 Overview

The Rule analysis evaluates whether deterministic mental-accounting agents create account-level realization asymmetry, house-money risk shifts, sunk-cost holding, stabilizing rational trades, and background liquidity. It uses `masim.utils.load_results()` and writes the standard analysis output set under the configured `analysis/` directory.

## §2 Metric Implementation

| Metric | Function / Source | Root Reference |
|---|---|---|
| Account-Level Turnover (ALT) | `calculate_metrics(data)` from investor payloads | `analysis-bases.md §2 Metric: Account-Level Turnover` |
| House-Money Risk Shift (HMRS) | `calculate_metrics(data)` from action and exposure changes | `analysis-bases.md §2 Metric: House-Money Risk Shift` |
| Sunk-Cost Holding Ratio (SCHR) | `calculate_metrics(data)` from losing-position sell behavior | `analysis-bases.md §2 Metric: Sunk-Cost Holding Ratio` |
| Rational Benchmark Deviation (RBD) | `calculate_metrics(data)` from price and fundamental histories | `analysis-bases.md §2 Metric: Rational Benchmark Deviation` |
| Behavioral Price Impact (BPI) | `calculate_metrics(data)` from price response and order flow | `analysis-bases.md §2 Metric: Behavioral Price Impact` |
| Return Volatility (RV) | `calculate_metrics(data)` from price returns | `analysis-bases.md §2 Metric: Return Volatility` |
| Realization Frequency Ratio (RFR) | `calculate_metrics(data)` from gain/loss realization frequency | `analysis-bases.md §2 Metric: Realization Frequency Ratio` |

## §3 Analysis Dimensions

- Agent dimension: compare MentalAccountant, HouseMoneyTrader, RationalPortfolioManager, SunkCostHolder, and NoiseTrader behavior.
- Market dimension: compare price, fundamental value, volume, net demand, and deviation.
- Portfolio dimension: inspect cash, inventory, and realized action paths.
- Contract dimension: verify canonical order fields and non-empty reasoning.

## §4 Phase Analysis

The deterministic run is read as initialization, account-framing activation, behavioral trading, and stabilization phases. ALT, HMRS, SCHR, and RFR are emphasized during agent activation; RBD, BPI, RV, and volume diagnose market consequences.

## §5 Cross-Variant Comparison

The Rule variant is the deterministic baseline for the LLM, RuleLLM, and Rag variants. Cross-variant analysis compares whether API variants preserve the same mental-accounting mechanism while changing reasoning richness and knowledge use.

## §6 Expected Results

### §6.1 Stylised Facts

Rule runs should show positive account-level turnover, higher winner than loser realization, stabilizing rational-manager trades, and nonzero noise liquidity.

### §6.2 Calibration Targets

Targets follow `analysis-bases.md §6.2`: ALT and RFR identify realization behavior, SCHR identifies loss-holding pressure, and RBD/RV/BPI keep market dynamics within plausible ranges.

### §6.3 Cross-Variant Predictions

Rule outputs should be the most mechanically stable; LLM outputs may vary by persona; RuleLLM should retain deterministic rule direction with richer text; Rag should add retrieved-knowledge traces without changing the order schema.

### §6.4 Validation Failure Signs

Zero volume, missing price/fundamental histories, absent canonical order fields, or empty reasoning indicate implementation or configuration failure.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_mentalaccounting_dynamics.png`, `02_mentalaccounting_analysis.png`, and `03_summary.png`.
