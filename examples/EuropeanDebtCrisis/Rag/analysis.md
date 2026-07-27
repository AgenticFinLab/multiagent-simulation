# EuropeanDebtCrisis Rag — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                              |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                    |
| Analysis Script                 | `analysis.py` in this directory                                                                                          |
| Output Location                 | `EXPERIMENT/EuropeanDebtCrisis/Rag/analysis/`                                                                             |
| Imports From                    | `examples/EuropeanDebtCrisis/Rule/analysis.py` — reuses `load_simulation_data`, `calculate_metrics`, `validate_european_debt_crisis`, `create_visualizations`, `analyze_europeandebtcrisis`; and `examples/EuropeanDebtCrisis/Rag/players.py` for the `_RAG_FALLBACK` sentinel |
| Variant-Specific Functions      | `analyze_rag_knowledge_effect(rag_contexts)` — per-agent retrieval success/failure counts, character-length statistics, and aggregate retrieval failure rate |
| Variant-Specific Considerations | Rag decisions are LLM-driven but grounded in retrieved European sovereign-debt literature. Every retrieval must be audited against the sentinel `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` (`Rag/players.py`) — rounds that resolve to that sentinel count as retrieval failures and are the primary input to the API-and-RAG-Quality metric (§2.7 of `analysis-bases.md`). |

Measure whether retrieval-augmented, literature-grounded reasoning
sharpens or dampens the self-fulfilling spiral relative to the LLM
baseline. Key questions:

- Does retrieved De Grauwe / Acharya doom-loop content amplify CDI and
  AR beyond the LLM baseline?
- Does retrieved Draghi "whatever it takes" / OMT content raise IER
  and compress SRT relative to LLM?
- Does retrieved LTCM / limits-to-arbitrage literature make HedgedFund
  more cautious at crisis peaks (lower APR floor, lower APR variance)?
- What fraction of decision rounds fall back to the `_RAG_FALLBACK`
  sentinel, and does that fraction correlate with degraded metrics?

---

## 2. Metric Implementation

All seven core metrics inherit their definitions and computation from the
Rule variant (`Rule/analysis.py`). The Rag variant adds one variant-specific
audit function: `analyze_rag_knowledge_effect`, which explicitly compares
each round's recorded `rag_context` against the module-level sentinel:

```python
# examples/EuropeanDebtCrisis/Rag/players.py
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"
```

`analyze_rag_knowledge_effect` treats any round whose `rag_context.strip()`
equals `_RAG_FALLBACK` as a retrieval failure; all other non-empty payloads
are counted as retrieval successes.

### Metric: Crisis Depth Index (CDI)

- **Defined in**: `analysis-bases.md §2 — Crisis Depth Index`
- **Implemented in**: `Rule/analysis.py → crisis_depth_index(price_history, fundamental)`
- **Data source**: `EXPERIMENT/EuropeanDebtCrisis/Rag/records/market/**`
- **Implementation details**: Same as Rule.
- **Variant-specific notes**: Retrieved De Grauwe / Acharya passages may reinforce speculative selling narratives — the upper tail of CDI can exceed the LLM baseline. Runs whose retrieval-failure fraction is high should behave closer to the LLM baseline.
- **Expected range for this variant**: `0.12 – 0.38`.

### Metric: Crisis Duration (CD)

- **Defined in**: `analysis-bases.md §2 — Crisis Duration`
- **Implemented in**: `Rule/analysis.py → crisis_duration(price_history, fundamental, crisis_threshold=-0.10)`
- **Data source**: Same as CDI.
- **Variant-specific notes**: Retrieved doom-loop literature can sustain a fear narrative for longer than a bare LLM prompt; conversely, retrieved Draghi/OMT content can compress CD when ECB knowledge is available. Net effect: similar central CD to LLM with a wider upper tail.
- **Expected range for this variant**: `8 – 35` rounds.

### Metric: Amplification Ratio (AR)

- **Defined in**: `analysis-bases.md §2 — Amplification Ratio`
- **Implemented in**: `Rule/analysis.py → amplification_ratio(creditor_sell_volume, periphery_sell_volume)`
- **Data source**: Rag investor turn payloads. Aggregation uses the canonical `agent_type` field emitted by `_build_order`.
- **Variant-specific notes**: When Acharya-style bank–sovereign nexus text is retrieved for `RagLLMCreditorPanicker`, AR upper bound is higher than LLM. If retrieval fails (`_RAG_FALLBACK`), the agent falls back to persona reasoning and AR reverts toward LLM baseline.
- **Expected range for this variant**: `0.7 – 1.8`.

### Metric: Intervention Effectiveness Ratio (IER)

- **Defined in**: `analysis-bases.md §2 — Intervention Effectiveness Ratio`
- **Implemented in**: `Rule/analysis.py → intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds)`
- **Data source**: `RagLLMECBIntervenor` turn payloads.
- **Variant-specific notes**: Retrieved Draghi OMT excerpts model credible commitment with the strongest fidelity of any variant — expect the highest IER ceiling among {Rule, LLM, RuleLLM, Rag}. When the retrieval fallback fires for the ECB agent, IER regresses toward LLM levels.
- **Expected range for this variant**: `0.65 – 0.98`.

### Metric: Spread Recovery Time (SRT)

- **Defined in**: `analysis-bases.md §2 — Spread Recovery Time`
- **Implemented in**: `Rule/analysis.py → spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05)`
- **Data source**: Price + fundamental history.
- **Variant-specific notes**: Grounded ECB narrative shortens SRT relative to LLM; failed retrieval rounds during the recovery phase widen SRT. Occasional non-recovery runs are possible if retrieval systematically fails for the ECB persona.
- **Expected range for this variant**: `4 – 22` rounds (or `-1` sentinel).

### Metric: Arbitrage Profit Rate (APR)

- **Defined in**: `analysis-bases.md §2 — Arbitrage Profit Rate`
- **Implemented in**: `Rule/analysis.py → arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth)`
- **Data source**: `RagLLMHedgedFund` turn payloads.
- **Variant-specific notes**: Retrieved LTCM / limits-to-arbitrage passages induce more cautious HedgedFund behavior at the trough. Expect a lower APR floor than Rule but tighter APR variance than LLM when retrieval succeeds.
- **Expected range for this variant**: `0.02 – 0.18`.

### Metric: API and RAG Quality (AQR)

- **Defined in**: `analysis-bases.md §2 — API And RAG Quality`
- **Implemented in**: `analysis.py → analyze_rag_knowledge_effect(rag_contexts)`
- **Data source**: `player.turns.field("rag_context")` for every non-market player, harvested by `_load_rag_payloads(results)` in `Rag/analysis.py`.
- **Implementation details**:
  ```python
  # Rag/analysis.py
  for context in round_contexts.values():
      total += 1
      text = str(context) if context is not None else ""
      if text.strip() == _RAG_FALLBACK:   # "(No relevant knowledge retrieved this round.)"
          failures += 1
      context_chars_sum += len(text)
  ```
  Per-agent record: `total_rag_rounds`, `retrieval_success_rounds`,
  `retrieval_failure_rounds`, `retrieval_failure_rate`,
  `mean_context_chars`. Aggregate: `mean_retrieval_failure_rate`,
  `max_retrieval_failure_rate`, `total_rag_rounds`,
  `total_failure_rounds`, `overall_failure_rate`, `player_count`.
- **Variant-specific notes**: A healthy Rag run keeps
  `aggregate.overall_failure_rate ≤ 0.20`; higher values imply the
  retrieval index is undersized or the queries are off-topic — economic
  metrics should be treated as LLM-equivalent, not Rag-equivalent, in
  that regime.
- **Expected range for this variant**: `overall_failure_rate ∈ [0.00, 0.20]` under nominal conditions; `mean_context_chars` typically `200 – 1500`.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crisis severity — CDI, CD

- **Function**: `calculate_metrics` (inherited from Rule) + validation.
- **Input data**: price/fundamental series and deviation.
- **Computation**: Identical to Rule.
- **Output**: `fig1_price_fundamental.png`, `fig2_crisis_depth.png`.
- **Variant-specific interpretation**: With successful retrieval, the deviation curve shows sharper kinks around the trough (retrieved "spiral" passages reinforce sell decisions). When retrieval fails often, the curve resembles the LLM baseline. Cross-reference `rag_stats.json` before drawing conclusions.
- **Expected output description**: `fig2` shows moderate jitter; the trough magnitude tracks `rag_stats.aggregate.overall_failure_rate` inversely — the more grounded the run, the deeper the informed trough.

### Dimension 2: Doom loop — AR, sell volume attribution

- **Function**: `plot_fig3_doom_loop` from Rule.
- **Input data**: Per-round periphery / creditor sell volumes bucketed via `agent_type`.
- **Computation**: Identical to Rule.
- **Output**: `fig3_doom_loop.png`.
- **Variant-specific interpretation**: Doom-loop bar heights should be highest when Acharya / bank-sovereign nexus passages are retrieved for `RagLLMCreditorPanicker`. Failed-retrieval rounds soften the amplification.

### Dimension 3: Policy response — IER, SRT

- **Function**: `plot_fig4_intervention_timeline`, `plot_fig5_recovery`.
- **Input data**: ECB buy indicator series and crisis flag series.
- **Computation**: Identical to Rule.
- **Output**: `fig4_intervention_timeline.png`, `fig5_recovery.png`.
- **Variant-specific interpretation**: Retrieved Draghi OMT / "whatever it takes" text produces the most credible ECB response of any variant. When the ECB rag context degrades to `_RAG_FALLBACK`, expect delayed intervention and a wider recovery band.

### Dimension 4: Arbitrage channel — APR, action volume

- **Function**: `plot_fig8_hedgedfund_pnl`, aggregate volumes in `calculate_metrics`.
- **Input data**: Reconstructed HedgedFund cash / position from turn payloads.
- **Variant-specific interpretation**: Position trajectory should show a *shallower* accumulation at the trough than Rule when LTCM-style passages are retrieved. Wealth curve should still finish above the initial baseline, but with lower peak-to-terminal ratio.

### Dimension 5: API and RAG quality — AQR

- **Function**: `analyze_rag_knowledge_effect`.
- **Input data**: `player.turns.field("rag_context")` for each player.
- **Output**: `summary.json.rag_stats` and standalone `rag_stats.json`.
- **Variant-specific interpretation**: Sort per-agent `retrieval_failure_rate` descending; agents at the top of that list are effectively running as LLM-only for the corresponding dimension. A high `aggregate.max_retrieval_failure_rate` with low `mean_retrieval_failure_rate` indicates an outlier persona whose retrieval keys need tuning.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                                  | Description                                                                             | How to Observe                                                                | Contrast with LLM variant                                                     |
|---------------------------------------------|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| Literature-anchored fear narrative           | Retrieved De Grauwe / Acharya text reinforces speculative selling                       | Compare `RagLLMPeripheryBondSeller` sell volume vs LLM baseline               | LLM produces persona-only reasoning without external anchors                  |
| Draghi commitment credibility                | Retrieved OMT / "whatever it takes" excerpts drive earlier, larger ECB buys             | `fig4_intervention_timeline.png` green bars at earlier rounds                 | LLM ECB is credible but ungrounded; IER ceiling is lower                      |
| LTCM caution at peaks                        | Retrieved limits-to-arbitrage passages suppress HedgedFund accumulation at trough       | `fig8_hedgedfund_pnl.png` position line flatter around trough                 | LLM HedgedFund may still buy aggressively                                     |
| Retrieval fallback regression                | Rounds resolving to `_RAG_FALLBACK` regress the agent's behavior toward LLM baseline    | `rag_stats.<player>.retrieval_failure_rate`                                    | LLM baseline is the reference behavior in this regime                         |
| Persona-specific retrieval asymmetry         | Some personas retrieve reliably; others (e.g., HedgedFund) may fall back more           | `aggregate.max_retrieval_failure_rate ≫ mean_retrieval_failure_rate`          | LLM has no such asymmetry — all personas share the same knowledge (persona)   |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                     | Phenomenon Clarity | Recommended for  |
|--------------|---------------------------------------------------------|--------------------|------------------|
| 100          | Partial crisis; RAG effect on trough visible            | Low                | Quick testing    |
| 200          | Full lifecycle with clear retrieval-vs-fallback contrast | Medium             | Standard runs    |
| 500          | Multiple crises + long-run knowledge assimilation        | High               | Research quality |

### Agent Count Scaling

| Agent Count    | Expected Observable                                            | Environment Dynamics                                                     |
|----------------|----------------------------------------------------------------|--------------------------------------------------------------------------|
| Minimum viable | Single crisis; retrieval statistics dominated by few agents    | AR extremely variable; `rag_stats` per-agent windows may be thin         |
| Recommended    | Full crisis with attributable per-persona retrieval breakdown  | CDI 0.15–0.30; IER 0.65–0.98; `overall_failure_rate` ≤ 0.20 typical      |

### Parameter Sensitivity (Rag-specific)

| Parameter                                                | Change     | Expected Effect on This Variant's Analysis                                                    |
|----------------------------------------------------------|------------|-----------------------------------------------------------------------------------------------|
| Retrieval top-k                                          | +50%       | Longer `mean_context_chars`; possibly noisier retrieval; CDI variance may increase            |
| Similarity threshold                                     | Tighter    | Higher `retrieval_failure_rate`; economic metrics regress toward LLM baseline                 |
| Embedding model                                          | Upgrade    | Lower `overall_failure_rate`; sharper doom-loop amplification and Draghi-style intervention   |
| Knowledge-base coverage (Draghi / OMT passages)          | +          | Higher IER ceiling; shorter SRT                                                               |
| Knowledge-base coverage (De Grauwe / Acharya passages)   | +          | Higher AR upper bound; wider CDI upper tail                                                   |
| Temperature (`generation_config`)                        | +50%       | Higher decision variance layered on top of retrieval variance                                 |
| Parse retry limit                                        | 1 → 3      | Fewer parse failures; unchanged retrieval statistics                                          |

---

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/EuropeanDebtCrisis/Rag/analysis/`

| Output File                                                          | Generated By                                       | Contents                                                                              | How to Interpret                                                                                     |
|----------------------------------------------------------------------|----------------------------------------------------|---------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `fig1_price_fundamental.png` … `fig8_hedgedfund_pnl.png`             | `create_visualizations()` (inherited)              | Same eight scenario plots as Rule                                                     | Same interpretation as Rule with Rag-specific amplification/dampening                                |
| `00_investor_bids.png`, `01_..._dynamics.png`, `02_..._analysis.png`, `03_summary.png` | `_write_standard_named_outputs()`         | Standard-contract aliases                                                             | Required by shared 4-plot contract                                                                   |
| `summary.json`                                                        | `analyze_europeandebtcrisis()` + Rag augmentation | Core 7 metrics + `rag_stats` section                                                  | Inspect `rag_stats.aggregate` before drawing metric conclusions                                       |
| `rag_stats.json`                                                      | `main()` in `Rag/analysis.py`                     | Standalone dump of `analyze_rag_knowledge_effect(rag_contexts)` output                | Primary audit artifact for retrieval health                                                          |

The Rag section of `summary.json` has this structure::

    "rag_stats": {
        "<player_id>": {
            "total_rag_rounds": N,
            "retrieval_success_rounds": ...,
            "retrieval_failure_rounds": ...,   # rounds where rag_context == _RAG_FALLBACK
            "retrieval_failure_rate": ...,
            "mean_context_chars": ...
        },
        ...
        "aggregate": {
            "mean_retrieval_failure_rate": ...,
            "max_retrieval_failure_rate": ...,
            "total_rag_rounds": ...,
            "total_failure_rounds": ...,
            "overall_failure_rate": ...,
            "player_count": ...
        }
    }

---

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | This Variant's Expected Position                                       | Reason                                                                                       |
|------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Phenomenon onset speed | Similar to LLM; earlier when Draghi/OMT retrieved for ECB              | Retrieval sharpens the persona's decision timing                                             |
| Phenomenon intensity   | Higher upper-tail CDI/AR than LLM; higher IER ceiling than any variant | Retrieved doom-loop and OMT literature amplify both spiral and stabilization mechanisms      |
| Behavioral realism     | Highest of the four variants                                           | Persona + retrieved evidence + reasoning; ties directly to real 2010–2012 sovereign crisis   |
| Decision quality       | Contract-valid decisions; retrieval health must also pass              | Same parse discipline as LLM plus `_RAG_FALLBACK` audit                                       |

**Cross-variant comparison summary**:

| Comparison       | Interpretation                                                                                                                                     |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Rag vs Rule      | Isolates the joint contribution of persona reasoning **and** retrieved sovereign-debt evidence to the baseline mechanism.                          |
| Rag vs LLM       | Isolates the marginal contribution of retrieved evidence on top of persona-only reasoning.                                                          |
| Rag vs RuleLLM   | Isolates the contribution of retrieved evidence when the decision layer is otherwise constrained to Rule-thresholded triggers.                      |

**Quality checks**:

- Confirm the run completed the configured 200 rounds.
- Confirm `rag_stats.json` is written and `summary.json.rag_stats.aggregate` is populated.
- Confirm every recorded `rag_context` is either substantive text or exactly equals `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` — any other empty/whitespace value indicates a recording bug in `Rag/players.py`.
- Confirm `aggregate.overall_failure_rate ≤ 0.20` before treating economic metrics as Rag-representative; higher failure rates mean the run is effectively LLM-equivalent.
- Confirm order payloads carry canonical `action`, `bid_price`, `quantity`, `reasoning`, and `agent_type` fields.
- Audit parse-failure and retry counts; contract failures must fail fast, not silently become hold.
- Cross-check per-persona `retrieval_failure_rate` — if the ECB persona has a high failure rate, IER must not be interpreted as a Draghi-credibility outcome.
