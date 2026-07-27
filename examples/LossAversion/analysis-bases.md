# LossAversion Simulation — Analysis Bases

## §1 Analysis Objectives

The LossAversion simulation analysis quantifies the degree to which prospect-theory biases (asymmetric loss sensitivity, break-even gambling, disposition-effect selling) distort price dynamics, redistribute wealth, and impose measurable welfare costs on biased agents relative to rational benchmarks.

Primary objectives:
1. Measure the strength of the disposition effect — asymmetric realisation of gains vs. losses.
2. Quantify the break-even escalation pattern and its price impact.
3. Estimate the wealth penalty imposed on loss-averse agents over the simulation horizon.
4. Decompose volatility into bias-driven vs. fundamental-uncertainty components.
5. Compare cross-variant reduction in bias intensity (Rule → LLM → RuleLLM → Rag).

---

## §2 Core Metrics

### §2.1 Loss Aversion Index (LAI)

**Category**: Behavioural Bias Measurement

**Definition**: Measures the empirical loss-aversion coefficient by comparing the sell-threshold asymmetry between gains and losses in `LossAverseInvestor` trades.

**Formula**:

```
LAI = (median_loss_threshold) / (median_gain_threshold)
```

Where `median_gain_threshold` = median PnL% at which gain-realisations occur, and `median_loss_threshold` = median |PnL%| at which loss-realisations occur.

**Python function**: `loss_aversion_index(trade_history, agent_type='LossAverseInvestor')`

**Inputs**: `trade_history` (list of `{agent_type, action, pnl_pct, round}`), `agent_type` filter

**Interpretation**:

| LAI Value | Interpretation                                           |
|-----------|----------------------------------------------------------|
| 1.0       | No loss aversion — symmetric thresholds                  |
| 1.5–2.0   | Moderate loss aversion                                   |
| 2.0–3.0   | Strong loss aversion (matches Kahneman–Tversky λ = 2.25) |
| > 3.0     | Extreme loss aversion — loser-holding dominates          |

**Academic Basis**: Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185). Empirical λ ≈ 2.25 from laboratory experiments; Odean (1998) finds implicit λ ≈ 1.5–2.0 in brokerage data.

**Normal Range**: 1.8–2.8

**Red Flag Threshold**: LAI < 1.2 (bias not expressed) or LAI > 4.0 (threshold miscalibration)

**Relationships**: Positively correlated with DEI; inversely correlated with WPI (wealth penalty — higher LAI → larger penalty).

**Implementation Notes**: Requires sufficient sell events of both types; filter for `LossAverseInvestor` only. Minimum 20 sell events of each type for reliable estimate.

---

### §2.2 Disposition Effect Index (DEI)

**Category**: Behavioural Bias Measurement

**Definition**: Replicates Odean's (1998) Proportion of Gains Realised (PGR) vs. Proportion of Losses Realised (PLR). Values above 1.0 confirm the disposition effect.

**Formula**:

```
PGR = (Gains Realised) / (Gains Realised + Paper Gains)
PLR = (Losses Realised) / (Losses Realised + Paper Losses)
DEI = PGR / PLR
```

**Python function**: `disposition_effect_index(trade_history, price_history, agent_states)`

**Inputs**: `trade_history`, `price_history`, `agent_states` (current positions and entry prices)

**Interpretation**:

| DEI Value | Interpretation                                    |
|-----------|---------------------------------------------------|
| < 1.0     | Reverse disposition effect (unusual)              |
| 1.0       | No disposition effect                             |
| 1.2–1.8   | Moderate disposition effect                       |
| > 1.8     | Strong disposition effect (Odean benchmark ≈ 1.5) |

**Academic Basis**: Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072). Shefrin, H., & Statman, M. (1985). doi:[10.1111/j.1540-6261.1985.tb05002.x](https://doi.org/10.1111/j.1540-6261.1985.tb05002.x).

**Normal Range**: 1.2–2.0

**Red Flag Threshold**: DEI < 1.0 (model produces reverse disposition) or DEI > 3.0 (threshold too aggressive)

**Relationships**: Closely tracks LAI; both rise with `loss_aversion_lambda`. Inversely related to NCE in LLM/Rag variants where narratives may correct the bias.

**Implementation Notes**: "Paper gain/loss" = open position with positive/negative unrealised PnL at end of each round. Ensure round-by-round snapshot of open positions.

---

### §2.3 Break-Even Escalation Ratio (BER)

**Category**: Risk-Seeking Behaviour

**Definition**: Quantifies the break-even effect by measuring how much `BreakEvenTrader` increases its buy quantity as losses deepen, normalised by a random baseline.

**Formula**:

```
BER = mean(buy_quantity | pnl_pct < −0.05) / mean(buy_quantity | pnl_pct ∈ [−0.05, 0])
```

**Python function**: `break_even_escalation_ratio(trade_history, agent_type='BreakEvenTrader')`

**Inputs**: `trade_history` filtered for `BreakEvenTrader` buy orders with PnL context

**Interpretation**:

| BER Value | Interpretation                                         |
|-----------|--------------------------------------------------------|
| < 1.0     | No escalation — agent does not increase risk in losses |
| 1.0–1.5   | Mild escalation                                        |
| 1.5–3.0   | Moderate break-even effect                             |
| > 3.0     | Aggressive risk-seeking in loss domain                 |

**Academic Basis**: Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x). Thaler, R. H. (1999). doi:[10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F](https://doi.org/10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F).

**Normal Range**: 1.5–3.5

**Red Flag Threshold**: BER < 1.0 (break-even effect absent) or BER > 6.0 (model instability)

**Relationships**: High BER can lower VAF because break-even purchases are counter-cyclical, while it increases portfolio concentration and wealth risk. In Rag, BER may be lower if retrieval surfaces escalation risk.

**Implementation Notes**: Requires trade records with PnL context. If `BreakEvenTrader` never activates (no loss > 5%), BER is undefined — check `risk_increase_factor` and noise settings.

---

### §2.4 Narrative Correction Efficiency (NCE)

**Category**: LLM / Rag Variant

**Definition**: Measures the degree to which LLM or RAG reasoning reduces the observed LAI compared to the Rule variant baseline. A value of 1.0 means no correction; 0.0 means full correction to rational behaviour.

**Formula**:

```
NCE = 1 − (LAI_variant − 1) / (LAI_rule − 1)
```

Where LAI values are computed from the same simulation length.

**Python function**: `narrative_correction_efficiency(lai_variant, lai_rule_baseline)`

**Inputs**: Pre-computed LAI values for the variant under analysis and the Rule baseline

**Interpretation**:

| NCE Value | Interpretation                                                  |
|-----------|-----------------------------------------------------------------|
| < 0       | LLM amplifies bias beyond Rule baseline                         |
| 0–0.2     | Minimal narrative correction                                    |
| 0.2–0.5   | Moderate correction                                             |
| > 0.5     | Strong correction — LLM/Rag substantially reduces loss aversion |

**Academic Basis**: Kahneman, D. (2011). *Thinking, Fast and Slow*. Insights on narrative debiasing; Logg, J. M., et al. (2019). Algorithm appreciation: People prefer algorithmic to human judgment. *Organizational Behavior and Human Decision Processes*. doi:[10.1016/j.obhdp.2018.12.009](https://doi.org/10.1016/j.obhdp.2018.12.009).

**Normal Range (LLM)**: 0.15–0.40; **Normal Range (Rag)**: 0.30–0.60

**Red Flag Threshold**: NCE < 0 (LLM amplifies bias) or NCE > 0.9 (LLM overwrites rule logic entirely)

**Relationships**: Inversely related to LAI and DEI in the same variant. Positively correlated with KB quality in Rag variant.

**Implementation Notes**: Requires Rule baseline LAI from an identical simulation run. Only meaningful for LLM, RuleLLM, Rag variants.

---

### §2.5 Volatility Amplification Factor (VAF)

**Category**: Market Impact

**Definition**: Ratio of realised price volatility in the biased simulation to the counterfactual volatility with only rational agents and market makers, normalised to the same fundamental noise level.

**Formula**:

```
VAF = std(price_returns_biased) / std(price_returns_rational_only)
```

**Python function**: `volatility_amplification_factor(price_history, fundamental, rational_benchmark_std)`

**Inputs**: `price_history`, `fundamental` value, `rational_benchmark_std` (from Rule-only-rational run)

**Interpretation**:

| VAF Value | Interpretation                                                 |
|-----------|----------------------------------------------------------------|
| < 1.0     | Net moderation — loss holding and break-even buying are counter-cyclical |
| 1.0       | No net volatility impact                                       |
| 1.0–1.5   | Mild amplification                                             |
| 1.5–2.5   | Moderate amplification (typical for loss-aversion simulations) |
| > 2.5     | Severe amplification                                           |

**Academic Basis**: Barber, B. M., & Odean, T. (2000). Trading Is Hazardous to Your Wealth. *Journal of Finance*, 55(2), 773–806. doi:[10.1111/0022-1082.00226](https://doi.org/10.1111/0022-1082.00226).

**Normal Range**: 0.1–2.5; the direction depends on whether counter-cyclical break-even demand or momentum demand dominates.

**Red Flag Threshold**: VAF ≤ 0.1 (metric degeneracy) or VAF ≥ 4.0 (simulation instability)

**Relationships**: Break-even buying and loss holding can lower VAF, while momentum demand can raise it. The observed direction is an empirical result of the population mix.

**Implementation Notes**: Rational benchmark requires a separate simulation run with only `RationalTrader` + `MarketMaker`. Alternatively use the Rule variant's last 10% of rounds when bias is exhausted as a proxy.

---

### §2.6 Wealth Penalty Index (WPI)

**Category**: Welfare / Performance

**Definition**: Measures the terminal wealth of `LossAverseInvestor` and `BreakEvenTrader` relative to `RationalTrader`, expressed as a fraction of rational wealth. Lower WPI = larger bias penalty.

**Formula**:

```
WPI = mean(terminal_wealth_biased / initial_wealth_biased)
      / mean(terminal_wealth_rational / initial_wealth_rational)
```

Where `terminal_wealth = cash + position × final_price`. Initial-wealth normalization is mandatory because archetypes have different starting endowments.

**Python function**: `wealth_penalty_index(agent_states, final_price, biased_types, rational_type)`

**Inputs**: `agent_states` (final cash and positions), `final_price`, lists of biased and rational agent class names

**Interpretation**:

| WPI Value | Interpretation                                     |
|-----------|----------------------------------------------------|
| > 0.95    | Minimal wealth penalty                             |
| 0.85–0.95 | Moderate penalty (typical empirical range)         |
| 0.70–0.85 | Significant penalty                                |
| < 0.70    | Severe penalty — bias substantially destroys value |

**Academic Basis**: Barber, B. M., & Odean, T. (2000). doi:[10.1111/0022-1082.00226](https://doi.org/10.1111/0022-1082.00226). Documents 3.7% annual return disadvantage for active retail traders; Odean (1998) finds disposition traders earn 3.3% less.

**Normal Range**: 0.75–0.95

**Red Flag Threshold**: WPI > 1.05 (biased agents outperform — check rational agent parameters) or WPI < 0.60 (extreme penalty — check `loss_aversion_lambda`)

**Relationships**: Inversely related to LAI and DEI; positively related to simulation length (longer runs → larger cumulative penalty).

**Implementation Notes**: Compute at end of simulation only. If multiple `LossAverseInvestor` instances, average their terminal wealth. Compare all variants; Rag variant should have highest WPI (lowest penalty).

---

### §2.7 Sell Rate Ratio (SRR)

**Category**: Trading Behaviour

**Definition**: Compares the sell frequency of `LossAverseInvestor` in gain rounds vs. loss rounds, providing a direct measure of the asymmetric realisation rate.

**Formula**:

```
SRR = (sell_count_gain_rounds / total_gain_rounds) / (sell_count_loss_rounds / total_loss_rounds)
```

**Python function**: `sell_rate_ratio(trade_history, price_history, agent_type='LossAverseInvestor')`

**Inputs**: `trade_history`, `price_history`

**Interpretation**:

| SRR Value | Interpretation                            |
|-----------|-------------------------------------------|
| 1.0       | Symmetric selling — no disposition effect |
| 1.2–1.8   | Mild disposition effect                   |
| > 2.0     | Strong disposition effect (Odean: ~1.5×)  |

**Academic Basis**: Odean (1998) documents PGR/PLR ≈ 1.5 in retail brokerage data. doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072).

**Normal Range**: 1.3–2.5

**Red Flag Threshold**: SRR < 1.0 or SRR > 4.0

**Relationships**: Direct operationalisation of DEI using frequency rather than proportion. Highly correlated with DEI.

**Implementation Notes**: "Gain round" = round where current_price > entry_price for that agent instance.

---

## §3 Metric Relationships

```
LAI → DEI → WPI (bias magnitude → realisation asymmetry → wealth cost)
BER → VAF (break-even buying → volatility amplification)
NCE ← (LAI_rule − LAI_variant) (correction = reduction in loss-aversion coefficient)
SRR ↔ DEI (frequency vs. proportion operationalisation of same effect)
```

---

## §4 Data Collection Requirements

| Metric | Required Data                                  | Collection Frequency |
|--------|------------------------------------------------|----------------------|
| LAI    | Trade records with entry price and sell PnL%   | Every sell event     |
| DEI    | Trade records + open position snapshots        | Every round          |
| BER    | BreakEvenTrader trade records with PnL context | Every buy event      |
| NCE    | Pre-computed LAI from Rule variant             | Post-simulation      |
| VAF    | Full price history + rational benchmark        | Post-simulation      |
| WPI    | Final agent states + final price               | Post-simulation      |
| SRR    | Trade records with round-level PnL context     | Every sell event     |

---

## §5 Cross-Scenario Predictions

| Variant | LAI     | DEI     | BER     | VAF     | WPI       | NCE       |
|---------|---------|---------|---------|---------|-----------|-----------|
| Rule    | 2.0–2.8 | 1.5–3.5 | > 1.0   | 0.1–2.5 | 0.75–0.95 | —         |
| LLM     | 1.6–2.4 | 1.2–2.0 | 1.2–2.5 | 1.2–2.0 | 0.80–0.93 | 0.15–0.40 |
| RuleLLM | 1.8–2.5 | 1.3–2.2 | 1.3–3.0 | 1.3–2.2 | 0.78–0.92 | 0.10–0.30 |
| Rag     | 1.4–2.0 | 1.0–1.8 | 1.0–2.0 | 1.2–1.8 | 0.85–0.95 | 0.30–0.60 |

---

## §6 Validation Framework

### §6.1 Stylised Facts

1. LossAverseInvestor realises gains ~70% of position vs. ~20% of position for losses (3.5× ratio).
2. BreakEvenTrader buy orders increase monotonically with loss depth.
3. `RationalTrader` and `MarketMaker` accumulate higher terminal wealth than biased agents.
4. Price exhibits asymmetric return distribution: positive skewness (winner-selling caps gains) or negative excess kurtosis.
5. Disposition-effect agents generate momentum at short horizons (loser-holding provides floor; winner-selling provides ceiling).

### §6.2 Calibration Targets

| Parameter             | Empirical Target            | Source                             |
|-----------------------|-----------------------------|------------------------------------|
| Loss-aversion lambda  | 2.25                        | Kahneman & Tversky (1979)          |
| PGR/PLR ratio (DEI)   | ~1.5                        | Odean (1998)                       |
| WPI deficit           | –5% to –15% over 100 rounds | Barber & Odean (2000) extrapolated |
| Break-even escalation | 2× normal buy quantity      | Barberis & Xiong (2009)            |

### §6.3 Cross-Variant Predictions

- Rule variant: highest LAI, lowest WPI, highest VAF.
- LLM variant: moderate reduction in LAI; LLM may contextually resist selling winners.
- RuleLLM: rule-anchored LAI with marginal LLM moderation.
- Rag variant: largest LAI reduction; knowledge base retrieves Prospect Theory papers, enabling agents to recognise their own bias.

### §6.4 Validation Failure Signs

| Symptom   | Likely Cause                                                | Fix                                                 |
|-----------|-------------------------------------------------------------|-----------------------------------------------------|
| LAI ≈ 1.0 | `loss_aversion_lambda` too low or sell thresholds symmetric | Increase `loss_aversion_lambda` to 2.25             |
| WPI > 1.0 | Biased agents outperform rational                           | Check `risk_aversion` — may be too conservative     |
| BER < 1.0 | BreakEvenTrader never activates                             | Ensure `noise_std` causes sufficient –5% PnL events |
| NCE > 0.9 | LLM ignores system prompt role                              | Strengthen loss-aversion framing in system prompt   |
| VAF ≤ 0.1 | Degenerate activity/inactivity volatility comparison          | Inspect stimulus exclusion and active-round counts  |

---

## §7 Visualization Recommendations

1. **LAI over time**: Plot rolling LAI per 20-round window to detect regime changes (e.g., break-even effect dominates early, fades late).
2. **PGR vs. PLR bar chart**: Compare gain/loss realisation rates per variant side-by-side.
3. **Wealth trajectory**: Line chart of cumulative wealth for each agent class across all 100 rounds.
4. **Price deviation heatmap**: Heatmap of `deviation × round` coloured by dominant agent action.
5. **BER scatter plot**: `buy_quantity` vs. `pnl_pct` for BreakEvenTrader; regression slope = escalation rate.
6. **Cross-variant metric radar chart**: LAI, DEI, BER, VAF, WPI, NCE for all 4 variants.
