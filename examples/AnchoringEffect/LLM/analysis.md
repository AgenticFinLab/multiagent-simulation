# AnchoringEffect LLM — Analysis Documentation

## Overview

| Item                            | Description                                                                                                                                                        |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                             |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                    |
| Output Location                 | `EXPERIMENT/AnchoringEffect/LLM/analysis/`                                                                                                                         |
| Variant-Specific Considerations | LLM decisions are stochastic — all metrics exhibit higher run-to-run variance than Rule; reasoning traces provide qualitative evidence unavailable in Rule variant |

---

## 2. Metric Implementation

All 8 metrics are defined in `analysis-bases.md §2`. Below: how each is implemented in the LLM variant.

### Metric: Price Deviation

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_price_deviation()`
- Data source: `EXPERIMENT/AnchoringEffect/LLM/records/market/price/*.json`
- Variant-specific notes: LLM agents are not constrained to apply exact formulas; their bid prices and quantities may diverge from Rule targets, causing deviation paths to differ in shape. Expect more irregular zigzag patterns compared to Rule's smoother curves.
- Expected range for this variant: MAD [3%, 12%] — slightly wider than Rule baseline due to LLM stochasticity

### Metric: Mean Absolute Deviation (MAD)

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_mean_abs_deviation()`
- Data source: market price records + fundamental value from config
- Variant-specific notes: Cross-run standard deviation of MAD is expected to be 1.5–2× higher than Rule variant. Single-run MAD may be within Rule range or significantly outside it.
- Expected range for this variant: [2%, 14%]

### Metric: Anchoring Persistence (Half-Life)

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_anchoring_persistence()`
- Data source: deviation time series from market records
- Variant-specific notes: LLM agents may exhibit variable anchoring strength — some runs show shorter half-lives (LLM breaks from anchor sooner due to narrative reasoning) and others show longer half-lives (LLM reinforces anchor via self-consistent narrative). Expect bimodal distribution across runs.
- Expected range for this variant: [15, 70] rounds — wider interval than Rule [20, 60]

### Metric: Rolling Volatility

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_rolling_volatility()`
- Data source: price return series
- Variant-specific notes: LLM narrative framing creates occasional volatility spikes — periods where multiple LLM agents simultaneously adopt a bearish or bullish narrative, generating correlated order flow. These spikes are absent from the deterministic Rule variant.
- Expected range for this variant: [0.3%, 2.5%] per round

### Metric: Return Autocorrelation

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_autocorrelation()`
- Data source: price return series
- Variant-specific notes: Positive autocorrelation is expected in early rounds (anchored LLM agents create momentum-like persistence), potentially decreasing faster than Rule if LLM agents shift narrative mid-simulation.
- Expected range for this variant: lag-1 AC in [0.05, 0.30]

### Metric: Max Drawdown

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_max_drawdown()`
- Data source: cumulative price series
- Variant-specific notes: LLM agents may exhibit "emergent caution" — after observing price drops in their context window, they suddenly shift to sell or hold, amplifying drawdown events beyond Rule levels.
- Expected range for this variant: [4%, 22%]

### Metric: Agent-Type Trading Volume

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_agent_volumes()`
- Data source: `EXPERIMENT/AnchoringEffect/LLM/records/{agent_id}/*.json`
- Variant-specific notes: Volume distribution across agent types is more variable in LLM. Noise Trader and Momentum Trader may have similar volumes as in Rule, but Anchored/Historical/Rational agents can have substantially different volumes depending on the LLM's narrative interpretation.
- Expected range for this variant: varies by run; overall market volume ±30% of Rule baseline

### Metric: Anchoring Bias Magnitude

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_anchoring_bias_magnitude()`
- Data source: LLM agent records (price, reasoning field from decision JSON)
- Variant-specific notes: This is the primary LLM-specific metric. The qualitative reasoning traces in `<analysis>` tags reveal whether the LLM is actually exhibiting anchoring psychology or rationalizing away from it. In approximately 20–30% of rounds, LLM agents may show "reasoning override" — their stated reasoning departs from anchoring psychology. Anchoring bias magnitude may be lower than Rule in these rounds.
- Expected range for this variant: [0.0, 0.5] (dimensionless, lower than Rule's [0.1, 0.6] due to reasoning escape)

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics Analysis

Objective (from analysis-bases.md): Measure how anchoring-induced demand creates and sustains price deviations from fundamental value across simulation rounds.

Implementation in analysis.py:
- Function: `analyze_price_dynamics()`
- Input data: market price records, fundamental value from config
- Computation: compute deviation series, MAD, half-life, rolling volatility; overlay phases on price chart
- Output: `price_dynamics.png`, contribution to `summary.json`

Variant-Specific Interpretation:
- LLM price paths are stochastic; a single run is not representative. Run at least 3 independent runs to characterize the distribution of outcomes.
- Price paths may show abrupt "narrative shifts" — sudden changes in trend when LLM agents collectively update their framing.
- Compare the LLM price path visually to the Rule baseline to identify regime differences (e.g., does LLM achieve faster or slower mean reversion?).

Expected Output Sample:
```
Price chart showing irregular anchoring-induced mispricing, with wider confidence band
around fundamental than Rule variant. Occasional sharp corrections not seen in Rule.
```

---

### Dimension 2: Investor Behavior Analysis

Objective (from analysis-bases.md): Characterize how each investor type's decisions contribute to anchoring dynamics, including volume patterns and wealth evolution.

Implementation in analysis.py:
- Function: `analyze_investor_behavior()`
- Input data: per-agent decision records (action, quantity, reasoning)
- Computation: aggregate buy/sell/hold counts by agent type; compute portfolio value trajectory; extract reasoning variance metrics
- Output: `investor_behavior.png`, `agent_volumes.json`

Variant-Specific Interpretation:
- LLM agents' reasoning strings can be analyzed for keyword frequency (e.g., "anchor," "historical," "momentum") to verify persona consistency.
- Agents that frequently use "hold" despite market deviation may indicate LLM decision paralysis — a phenomenon unique to this variant.
- Portfolio wealth divergence across agents should be qualitatively similar to Rule but with higher variance.

Expected Output Sample:
```
Bar chart: buy/sell/hold counts by agent type. LLM variants show higher hold-rate variance.
Line chart: portfolio value by agent type — similar ordering to Rule (RationalUpdater best-performing).
```

---

### Dimension 3: Anchoring Phenomenon Verification

Objective (from analysis-bases.md): Confirm that anchoring effect emerges from LLM persona-driven behavior, without explicit quantitative rules.

Implementation in analysis.py:
- Function: `analyze_anchoring_phenomenon()`
- Input data: deviation series, agent decision records
- Computation: test that price deviates from fundamental for ≥20 consecutive rounds; measure half-life; verify anchoring agents' perceived targets differ from true fundamental
- Output: `anchoring_verification.png`

Variant-Specific Interpretation:
- Success criterion: anchoring phenomenon visible (MAD > 3%, half-life > 20 rounds) in ≥70% of independent runs, even without explicit quantitative rules in prompts.
- If phenomenon fails to emerge: check that `== PERSONA ==` prompts correctly instill anchoring psychology without naming the phenomenon.
- Reasoning override events should be documented — they represent the LLM discovering rational behavior despite the persona prompt.

Expected Output Sample:
```
Heatmap or time-series showing rounds with active anchoring signal (deviation > 3%).
Expected: at least 40-60 rounds with deviation > 3% per 100-round simulation.
```

---

### Dimension 4: Cross-Variant Comparison

Objective (from analysis-bases.md): Position LLM results relative to Rule, RuleLLM, and Rag to isolate the effect of language reasoning.

Implementation in analysis.py:
- Function: `generate_comparison_table()`
- Input data: LLM summary.json + Rule/RuleLLM/Rag summary.json (if available)
- Computation: compare MAD, half-life, max drawdown, total volume across variants
- Output: `cross_variant_comparison.png`, updated `summary.json`

Variant-Specific Interpretation:
- LLM vs. Rule: the key comparison. Higher LLM MAD = LLM personas amplify anchoring. Lower = LLM reasoning provides escape from bias.
- LLM vs. RuleLLM: isolates the effect of explicit quantitative rules. If LLM ≈ RuleLLM in most metrics, explicit rules are redundant.
- Expected finding: LLM shows higher metric variance than Rule but similar mean, confirming LLM can reproduce anchoring psychology without explicit formulas.

---

## 4. Variant-Specific Observable Phenomena

Phenomena unique to the LLM variant not present in the deterministic Rule variant:

| Phenomenon                | Description                                                                                             | How to Observe                                                                                                         | Contrast with Rule-Based                                                            |
|---------------------------|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Narrative Shift Event     | LLM agents collectively update their framing mid-simulation, causing abrupt price change                | Sudden deviation reversal on price chart; `<analysis>` text changes from "anchor is firm" to "price has moved too far" | Rule has no such discrete transition; deviation follows smooth formula-driven curve |
| Emergent Caution          | After a price drop, LLM agents spontaneously shift to hold/sell even without fundamental change         | Spikes in hold-rate following negative return rounds                                                                   | Rule agents follow fixed threshold logic regardless of prior experience             |
| Persona Consistency Drift | LLM agent reasoning gradually departs from assigned persona over many rounds                            | Keyword analysis of reasoning strings; declining use of persona-specific language in rounds >60                        | Rule agents never deviate from formula; no equivalent drift                         |
| Reasoning Override        | LLM finds rational solution despite anchoring persona prompt, occasionally trading on true fundamentals | Agent records show bid_price near fundamental_value despite anchoring persona                                          | Never occurs in Rule variant; represents LLM "reasoning escape"                     |
| Narrative Framing Effect  | LLM agents frame the same numeric signal differently based on prior reasoning context                   | Same deviation% triggers buy in one run but hold in another                                                            | Rule always produces identical decision for identical numeric inputs                |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds          | Expected Observable                                               | Phenomenon Clarity                                              |
|-----------------------|-------------------------------------------------------------------|-----------------------------------------------------------------|
| 50 rounds             | Anchoring bias visible but insufficient half-life measurement     | Partial — MAD measurable but persistence analysis unreliable    |
| 100 rounds (standard) | Full anchoring lifecycle observable; reasoning patterns stabilize | Good — all 8 metrics computable; LLM narrative patterns visible |
| 200 rounds            | Multiple anchoring cycles possible; persona drift detectable      | Excellent — enables longitudinal LLM reasoning analysis         |

### Agent Count Scaling

| Agent Count            | Expected Observable                                         | Market Dynamics                                       |
|------------------------|-------------------------------------------------------------|-------------------------------------------------------|
| 5 agents (1 per type)  | Clean individual-agent signals; high idiosyncratic noise    | Low market depth; single LLM reasoning trace per type |
| 10 agents (2 per type) | More stable aggregate behavior; intra-type variance visible | Standard — sufficient for statistic comparison        |
| 20+ agents             | LLM API cost high; narrative convergence effects possible   | Rich but expensive; run only for final validation     |

### Parameter Sensitivity

| Parameter       | Change                    | Expected Effect on Analysis                                                        |
|-----------------|---------------------------|------------------------------------------------------------------------------------|
| LLM temperature | Higher (>1.0)             | More reasoning variability; higher metric variance; more frequent narrative shifts |
| LLM temperature | Lower (<0.3)              | More deterministic LLM; results converge toward RuleLLM baseline                   |
| LLM model       | Stronger model            | More coherent persona maintenance; better anchoring psychology expression          |
| Prompt wording  | Remove psychological cues | LLM reverts to rational-like behavior; MAD drops; phenomenon may disappear         |

---

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/AnchoringEffect/LLM/analysis/`

| Output File                    | Generated By                     | Contents                                                            | Interpretation                                                |
|--------------------------------|----------------------------------|---------------------------------------------------------------------|---------------------------------------------------------------|
| `price_dynamics.png`           | `analyze_price_dynamics()`       | Price vs. fundamental; deviation series; rolling volatility overlay | Primary evidence for anchoring phenomenon emergence           |
| `investor_behavior.png`        | `analyze_investor_behavior()`    | Buy/sell/hold counts by agent type; portfolio value trajectories    | Shows which LLM personas are most/least active                |
| `anchoring_verification.png`   | `analyze_anchoring_phenomenon()` | Anchoring signal heatmap; half-life estimate; MAD time series       | Verifies LLM personas successfully produce anchoring dynamics |
| `cross_variant_comparison.png` | `generate_comparison_table()`    | Side-by-side metric comparison with Rule/RuleLLM/Rag                | Shows LLM position in the variant comparison matrix           |
| `agent_volumes.json`           | `calculate_agent_volumes()`      | Per-agent-type total buy/sell volume by round                       | Supports investor behavior analysis                           |
| `summary.json`                 | `main()`                         | All 8 metrics; variant label; run metadata                          | Used for cross-variant comparison pipeline                    |

---

## 7. Cross-Variant Comparison Notes

This variant's expected position in cross-variant comparison (from `analysis-bases.md §5`):

- **Phenomenon emergence speed**: Similar to Rule baseline; LLM agents adopt anchoring persona immediately, so phenomenon emerges within rounds 1–10 as in Rule. Occasionally faster if LLM strongly anchors.
- **Phenomenon intensity**: Higher variance than Rule; mean MAD approximately equal to Rule. Some runs show stronger anchoring (MAD > 8%) and others show weaker (MAD < 4%) depending on LLM narrative path.
- **Behavioral realism**: Higher than Rule — LLM agents express qualitative reasoning that matches real investor psychology (e.g., "the price was at 105 when I first entered the market; that feels like the right level"). This realism is the primary contribution of this variant.
- **Decision quality**: RationalUpdater (LLM) performance expected to be similar to or slightly below Rule RationalUpdater, as LLM sometimes fails to trade decisively on clear fundamental signals. AnchoredTrader (LLM) may underperform Rule AnchoredTrader if it breaks from anchoring and occasionally acts rationally.

See also: `simulation-bases.md §9` — Variant Comparison Preview
