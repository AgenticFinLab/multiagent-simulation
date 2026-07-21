# EuropeanDebtCrisis LLM — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                              |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                    |
| Analysis Script                 | `analysis.py` in this directory                                                                                          |
| Output Location                 | `EXPERIMENT/EuropeanDebtCrisis/LLM/analysis/`                                                                             |
| Imports From                    | `examples/EuropeanDebtCrisis/Rule/analysis.py` — reuses `load_simulation_data`, `calculate_metrics`, `validate_european_debt_crisis`, `create_visualizations`, `analyze_europeandebtcrisis` |
| Variant-Specific Functions      | `analyze_action_distribution(agent_records)` — per-agent action-type counts, mean reasoning length, decision entropy      |
| Variant-Specific Considerations | LLM decisions are stochastic; crisis onset and intervention timing exhibit substantially higher variance than Rule. Parse failures must fail fast — no silent hold fallback. |

Measure whether LLM persona-driven crisis reasoning produces more or less
severe crises than the Rule baseline. Key questions:

- Do LLM personas generate more realistic self-fulfilling spiral dynamics
  (earlier onset, sharper CDI)?
- Does LLM ECB intervention more authentically model the "whatever it
  takes" credibility effect?
- Does LLM stochasticity amplify or compress crisis variability?
- Are actions well-distributed (buy/sell/hold entropy) or does the LLM
  degenerate into a single action?

---

## 2. Metric Implementation

All seven core metrics inherit their definitions and computation from the
Rule variant (`Rule/analysis.py`). The LLM variant adds one variant-specific
audit function: `analyze_action_distribution`.

### Metric: Crisis Depth Index (CDI)

- **Defined in**: `analysis-bases.md §2 — Crisis Depth Index`
- **Implemented in**: `Rule/analysis.py → crisis_depth_index(price_history, fundamental)`
- **Data source**: `EXPERIMENT/EuropeanDebtCrisis/LLM/records/market/**`
- **Implementation details**: Same as Rule.
- **Variant-specific notes**: LLM may panic at different deviation levels each run — CDI variance is higher; both deeper and shallower outcomes than Rule are possible.
- **Expected range for this variant**: `0.10 – 0.45` (wider than Rule).

### Metric: Crisis Duration (CD)

- **Defined in**: `analysis-bases.md §2 — Crisis Duration`
- **Implemented in**: `Rule/analysis.py → crisis_duration(price_history, fundamental, crisis_threshold=-0.10)`
- **Data source**: Same as CDI.
- **Variant-specific notes**: LLM narrative reasoning may produce prolonged crises when the "fear narrative" persists across rounds, or rapid recoveries when the LLM reinterprets recent stabilization.
- **Expected range for this variant**: `5 – 40` rounds.

### Metric: Amplification Ratio (AR)

- **Defined in**: `analysis-bases.md §2 — Amplification Ratio`
- **Implemented in**: `Rule/analysis.py → amplification_ratio(creditor_sell_volume, periphery_sell_volume)`
- **Data source**: LLM investor turn payloads. Aggregation still uses the canonical `agent_type` field emitted by `_build_order`.
- **Variant-specific notes**: `LLMCreditorPanicker` may amplify more aggressively if the prompt generates a fear narrative; AR upper bound is higher than Rule.
- **Expected range for this variant**: `0.5 – 2.0`.

### Metric: Intervention Effectiveness Ratio (IER)

- **Defined in**: `analysis-bases.md §2 — Intervention Effectiveness Ratio`
- **Implemented in**: `Rule/analysis.py → intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds)`
- **Data source**: `LLMECBIntervenor` turn payloads.
- **Variant-specific notes**: LLM models Draghi commitment; may activate earlier and more aggressively — IER can exceed Rule in some runs and fall short in others.
- **Expected range for this variant**: `0.50 – 1.00`.

### Metric: Spread Recovery Time (SRT)

- **Defined in**: `analysis-bases.md §2 — Spread Recovery Time`
- **Implemented in**: `Rule/analysis.py → spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05)`
- **Data source**: Price + fundamental history.
- **Variant-specific notes**: SRT is more variable than Rule because LLM ECB timing is not deterministic; occasional non-recovery runs are possible.
- **Expected range for this variant**: `3 – 25` rounds (or `-1` sentinel).

### Metric: Arbitrage Profit Rate (APR)

- **Defined in**: `analysis-bases.md §2 — Arbitrage Profit Rate`
- **Implemented in**: `Rule/analysis.py → arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth)`
- **Data source**: `LLMHedgedFund` turn payloads.
- **Variant-specific notes**: LLM models limits-to-arbitrage caution; APR floor is lower than Rule because the LLM may withdraw at extreme crisis intensity.
- **Expected range for this variant**: `0.00 – 0.25`.

### Metric: LLM Action Distribution (LLM-specific)

- **Defined in**: this document (§2 above) and referenced by `analysis-bases.md §5 — API quality`.
- **Implemented in**: `analysis.py → analyze_action_distribution(agent_records)`
- **Data source**: LLM investor turn payloads keyed by `player_id`.
- **Implementation details**:
  ```python
  def analyze_action_distribution(agent_records):
      # For every agent count buy/sell/hold occurrences,
      # mean/median reasoning length, empty-reasoning rate,
      # and Shannon entropy (bits) of the action distribution.
      # Returns {player_id: {...}, "_aggregate": {...}}.
  ```
- **Variant-specific notes**: A degenerate LLM (always-hold or always-sell) will show entropy near 0 for the affected agent; healthy behavior yields entropy > 0.8 bits.
- **Expected range for this variant**: `decision_entropy_bits ∈ [0.8, log2(3) ≈ 1.585]` per agent under nominal conditions.

### Metric: API and RAG Quality (AQR)

- **Defined in**: `analysis-bases.md §2 — API And RAG Quality`
- **Implemented in**: RAG portion in `Rag/analysis.py`; API-side (parse failure rate) is captured by `analyze_action_distribution` via the `empty_reasoning_rate` field.
- **Variant-specific notes**: The LLM variant has no RAG contexts. `analyze_action_distribution` covers the API-quality subset by reporting fractions of accepted decisions and reasoning-length statistics.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crisis severity — CDI, CD

- **Function**: `calculate_metrics` (inherited from Rule) + validation.
- **Input data**: price/fundamental series and deviation.
- **Computation**: Identical to Rule.
- **Output**: `fig1_price_fundamental.png`, `fig2_crisis_depth.png`.
- **Variant-specific interpretation**: The trough position may not coincide with any single `deviation` threshold because the LLM decides continuously; expect a rougher deviation curve than Rule.
- **Expected output description**: `fig2` shows more jitter in the deviation line; the trough may occur at a shallower or deeper level than Rule.

### Dimension 2: Doom loop — AR, sell volume attribution

- **Function**: `plot_fig3_doom_loop` from Rule.
- **Input data**: Per-round periphery / creditor sell volumes canonically bucketed via `agent_type`.
- **Computation**: Identical to Rule.
- **Output**: `fig3_doom_loop.png`.
- **Variant-specific interpretation**: Look for asymmetric amplification — the LLM Creditor persona may accelerate faster than Rule (fear narrative) or stall (LLM re-reads and hedges).

### Dimension 3: Policy response — IER, SRT

- **Function**: `plot_fig4_intervention_timeline`, `plot_fig5_recovery`.
- **Input data**: ECB buy indicator series and crisis flag series.
- **Computation**: Identical to Rule.
- **Output**: `fig4_intervention_timeline.png`, `fig5_recovery.png`.
- **Variant-specific interpretation**: LLM ECB might fire outside the crisis window (proactively or defensively) — panel A green bars can appear before the red band opens.

### Dimension 4: Arbitrage channel — APR, action volume

- **Function**: `plot_fig8_hedgedfund_pnl`.
- **Variant-specific interpretation**: LLM `HedgedFund` may withdraw during the deepest crisis (funding-stress narrative); expect a flatter position line during the trough and lower terminal wealth than Rule.

### Dimension 5: API quality (LLM-specific)

- **Function**: `analyze_action_distribution`.
- **Input data**: LLM investor payloads.
- **Output**: `summary.json.llm_action_distribution`.
- **Variant-specific interpretation**: An agent with `decision_entropy_bits < 0.5` or `empty_reasoning_rate > 0.05` is behaving pathologically — inspect prompts and parse logs. Aggregate `hold` fraction > 0.8 suggests the LLM is under-participating.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                          | Description                                                                       | How to Observe                                     | Contrast with Rule                                           |
|-------------------------------------|-----------------------------------------------------------------------------------|----------------------------------------------------|--------------------------------------------------------------|
| Narrative-driven onset shift        | LLM persona may over-react or under-react to a given deviation                    | Compare CDI across seeds                            | Rule CDI variance ≈ 0; LLM variance is meaningful            |
| Reasoning length correlated with action | Sell/buy decisions often carry longer reasoning than holds                     | `mean_reasoning_length` field                       | Rule has no reasoning text                                   |
| Emergent caution after drops        | LLM may switch to hold after observing a large drop                               | Action distribution near trough                     | Rule keeps selling until threshold flips                     |
| Inconsistent threshold adherence    | LLM may buy above `entry_threshold` when narrative is bullish                     | HedgedFund action stream                            | Rule strictly obeys `entry_threshold`                        |
| Degenerate agents                   | Some LLM agents collapse to always-hold if prompts under-specify sell triggers    | `decision_entropy_bits ≈ 0`                         | Rule agents always emit correct actions                      |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                              | Phenomenon Clarity | Recommended for  |
|--------------|--------------------------------------------------|--------------------|------------------|
| 100          | Onset + partial recovery; crisis may be shallow  | Low                | Quick testing    |
| 200          | Full crisis lifecycle with occasional relapses   | Medium             | Standard runs    |
| 500          | Multiple crises + LLM adaptation visible         | High               | Research quality |

### Agent Count Scaling

| Agent Count    | Expected Observable                            | Environment Dynamics                         |
|----------------|------------------------------------------------|----------------------------------------------|
| Minimum viable | Single crisis; noisy metrics                   | AR extremely variable                        |
| Recommended    | Full crisis with clear amplification/backstop  | CDI 0.15–0.30 typical; IER 0.55–0.95 typical |

### Parameter Sensitivity (LLM-specific)

| Parameter                                | Change    | Expected Effect on This Variant's Analysis                                       |
|------------------------------------------|-----------|----------------------------------------------------------------------------------|
| Temperature (`generation_config`)        | +50%      | Higher CDI variance; higher `decision_entropy_bits`                              |
| System prompt "fear narrative" intensity | Increase  | Deeper CDI; higher AR                                                            |
| Max reasoning tokens                     | Decrease  | Shorter reasoning; may increase hold fraction                                    |
| Parse retry limit                        | 1 → 3     | Fewer parse failures; unchanged economic metrics                                 |
| Persona for `LLMECBIntervenor`           | Draghi-heavy | Higher IER, shorter SRT                                                        |

---

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/EuropeanDebtCrisis/LLM/analysis/`

| Output File                              | Generated By                     | Contents                                                     | How to Interpret                                                          |
|------------------------------------------|----------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------------|
| `fig1_price_fundamental.png` … `fig8_hedgedfund_pnl.png` | `create_visualizations()` (inherited) | Same eight scenario plots as Rule                          | Same interpretation as Rule with LLM-specific variance                    |
| `00_investor_bids.png`, `01_..._dynamics.png`, `02_..._analysis.png`, `03_summary.png` | `_write_standard_named_outputs()` | Standard-contract aliases                                    | Downstream tooling                                                        |
| `summary.json`                           | `analyze_europeandebtcrisis()` + LLM section | Core 7 metrics + `llm_action_distribution`               | Inspect `llm_action_distribution._aggregate.decision_entropy_bits`        |

The LLM section of `summary.json` has this structure::

    "llm_action_distribution": {
        "<player_id>": {
            "agent_type": "...",
            "total_decisions": N,
            "action_counts": {"buy": ..., "sell": ..., "hold": ...},
            "action_fractions": {...},
            "mean_reasoning_length": ...,
            "median_reasoning_length": ...,
            "empty_reasoning_rate": ...,
            "decision_entropy_bits": ...
        },
        ...
        "_aggregate": {...}
    }

---

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | This Variant's Expected Position                    | Reason                                                       |
|------------------------|-----------------------------------------------------|--------------------------------------------------------------|
| Phenomenon onset speed | Faster or slower than Rule depending on prompt tone | LLM discretionary trigger                                    |
| Phenomenon intensity   | Wider CDI band (higher variance)                    | Discretionary crisis interpretation                          |
| Behavioral realism     | Highest of the four variants                        | Persona-driven; can rationalize positions                    |
| Decision quality       | Contract-valid decisions after retries; parse failures must fail fast | 3-retry loop in `LLM/players.py`                    |

**Quality checks**:

- Confirm the run completed the configured 200 rounds.
- Audit parse-failure and retry counts; contract failures must fail fast, not silently become hold.
- Confirm accepted decisions carry canonical `action`, `bid_price`, `quantity`, and non-empty `reasoning`.
- Inspect `decision_entropy_bits` per agent for pathological collapses.
- Compare `llm_action_distribution._aggregate.action_fractions` with Rule expectations to detect over-holding.
