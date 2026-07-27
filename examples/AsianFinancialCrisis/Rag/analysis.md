# AsianFinancialCrisis Rag — Analysis Documentation

## §1 Overview

| Item                                | Description                                                                                                                                                         |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                              |
| **Analysis Script**                 | `Rule/analysis.py` (imported — Rag variant uses Rule analysis functions)                                                                                            |
| **Output Location**                 | `EXPERIMENT/AsianFinancialCrisis/Rag/records/analysis/`                                                                                                             |
| **Variant-Specific Considerations** | Knowledge-augmented variant; primary diagnostic is RAG retrieval quality and its effect on decision quality (earlier IMF intervention, more calibrated exit timing) |

---

## §2 Metric Implementation

Rag variant shares all metric functions with `Rule/analysis.py` — no separate analysis.py needed.

| Metric                     | Function              | Root Metric Reference | Rag-Specific Notes                                                                               |
|----------------------------|-----------------------|-----------------------|--------------------------------------------------------------------------------------------------|
| **Price Deviation**        | `def analyze_asian_financial_crisis(...)` | `analysis-bases.md §2.1`                | May show milder crisis if RAG knowledge helps agents avoid panic amplification                   |
| **Maximum Drawdown**       | `def _compute_max_drawdown(prices)` | `analysis-bases.md §2.2`                | Expected 20%–55%; potentially shallower if RAG-informed IMFRescuer intervenes earlier            |
| **Crisis Velocity**        | `def _compute_crisis_velocity(prices)` | `analysis-bases.md §2.3`                | May be slower than LLM if RAG provides context that moderates panic                              |
| **Return Autocorrelation** | `def _compute_rolling_ac1(returns, window=10)` | `analysis-bases.md §2.4`                | Similar to LLM; behavioral stochasticity preserved, knowledge may reduce tail extremes           |
| **Agent-Type Volume**      | `def _load_data(results)` | `analysis-bases.md §2.5`                | Most diagnostic: does RAG-informed IMFRescuer deploy more or earlier than LLM baseline?          |
| **Crisis Onset Round**     | `def _compute_crisis_onset(prices, fundamentals)` | `analysis-bases.md §2.6`                | Variable; historical knowledge may cause earlier or later detection than pure behavioral persona |
| **IMF Rescue Activation**  | `def analyze_asian_financial_crisis(...)` | `analysis-bases.md §2.7`                | RAG historical context may accelerate or moderate IMFRescuer activation timing                   |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Crisis Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price/fundamental from `records/market/*.json`
- Output: `01_asianfinancialcrisis_dynamics.png` and `02_asianfinancialcrisis_analysis.png`

**Variant-Specific Interpretation:**
Rag crisis trajectory should show the most historically calibrated path. If IMFRescuer intervenes earlier (shallower trough) vs. LLM, RAG is improving intervention timing. If trajectory is indistinguishable from LLM, check whether document sources contain relevant crisis materials.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records
- Rag-specific: inspect `reasoning` field for historical citations ("based on the 1997 Thai baht case...")

**Variant-Specific Interpretation:**
Key diagnostic: does `reasoning` field contain historical references? Presence of crisis-specific citations (e.g., Thai baht, Korea IMF package, IMF conditionality) validates that RAG retrieval is providing meaningful context. Absence suggests document sources are insufficient or RAG index not properly built.

---

### Dimension 3: Contagion Signal Analysis
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: return distribution and autocorrelation — same as Rule
- Rag-specific: compare tail distribution vs. LLM; RAG should reduce tail extremes

**Variant-Specific Interpretation:**
If Rag return distribution has thinner tails than LLM, knowledge grounding is reducing panic extremes. Check `rag_context` logs (if available) — empty rag_context every round suggests embedding/retrieval failure.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

Rag is the "informed" behavioral reference. Key question: does historical knowledge make agents better or worse at crisis navigation? Expected: Rag IMFRescuer intervenes earlier than LLM (historical precedents confirm crisis threshold); Rag ContagionTrader may identify contagion pattern earlier from retrieved signals.

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                                       | How to Observe                                         | Contrast with LLM                        |
|-----------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------|------------------------------------------|
| **Historical Citation in Reasoning**    | Agent reasoning includes specific historical crisis references                    | Search reasoning fields for "1997", "Thai baht", "IMF" | LLM: generic behavioral language only    |
| **Earlier IMF Intervention**            | RagIMFRescuer activates before LLM counterpart due to historical timing knowledge | Compare IMFRescuer first buy round Rag vs. LLM         | LLM: purely persona-driven timing        |
| **Knowledge-Calibrated Exit Threshold** | HotMoneyFunder exit timing informed by historical reversal precedents             | HotMoneyFunder sell round distribution across runs     | LLM: exit purely from persona conviction |
| **RAG Empty Context Rounds**            | Some rounds return "(No relevant knowledge)" — agent defaults to persona          | Count empty RAG context rounds in reasoning logs       | Pure LLM: all rounds are persona-only    |

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                                         |
|----------------|---------------------------------------------------------------------------------------------|
| **50 rounds**  | Full crisis lifecycle; RAG value most apparent at critical decision points (onset, rescue)  |
| **100 rounds** | Recovery phase: RAG agents may show faster recovery alignment with historical recovery data |

### Parameter Sensitivity

| Parameter               | Change      | Expected Effect                                                                  |
|-------------------------|-------------|----------------------------------------------------------------------------------|
| `top_k`                 | 3 → 5       | More retrieved passages; richer context but higher latency                       |
| `chunk_size`            | 512 → 256   | Finer retrieval; may retrieve more specific crisis data points                   |
| Document source quality | thin → rich | Primary driver of Rag advantage; rich crisis literature → better agent decisions |
| `temperature`           | 0.7 → 1.0   | More stochasticity in how RAG context is interpreted                             |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/AsianFinancialCrisis/Rag/records/analysis/`.

| Output File                             | Generated By              | Contents                                         | Interpretation                  |
|-----------------------------------------|---------------------------|--------------------------------------------------|---------------------------------|
| `00_investor_bids.png` | `Rule.analysis._create_visualizations()` | Market price and per-agent bid traces | Primary order-quality check |
| `01_asianfinancialcrisis_dynamics.png` | `Rule.analysis._create_visualizations()` | Price/fundamental and deviation bands | Primary Rag crisis verification |
| `02_asianfinancialcrisis_analysis.png` | `Rule.analysis._create_visualizations()` | Returns and rolling volatility | Crisis velocity and volatility check |
| `03_summary.png` | `Rule.analysis._create_visualizations()` | Agent volume and validation score summary | Compact scenario diagnosis |
| `summary.json` | `analyze_asian_financial_crisis()` | `metrics` and nested `validation` object | Cross-variant comparison input |
| `rag_stats.json` | `analyze_rag_knowledge_effect()` | Retrieval success and retrieval-miss rates | RAG quality audit |

---

## §7 Cross-Variant Comparison Notes

- **Crash emergence speed**: Variable; historical knowledge may accelerate or delay trigger depending on retrieved documents
- **Crash intensity**: Potentially shallower than LLM if IMFRescuer is better calibrated; deeper if knowledge reinforces panic
- **Behavioral realism**: Highest empirical grounding; agents cite historical precedents
- **Document quality dependency**: Rag advantage is entirely contingent on document source relevance and quality

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §5` — Rag variant description in agent diversity table
- `../analysis-bases.md §6` — Expected Rag result ranges (improved timing, variable depth)
- `Rule/analysis.py` — imported metric functions (`calculate_metrics`, `load_simulation_data`)
- `players.py → RagLLMInvestor._build_prompt()` — RAG context injection and query construction
- `players.py → RagLLMInvestor._initialize_rag()` — KnowledgeStore build/load logic
