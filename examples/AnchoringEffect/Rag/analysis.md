# AnchoringEffect Rag — Analysis Documentation

## §1 Overview

| Item                            | Description                                                                                                                                                                          |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                                               |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                                      |
| Output Location                 | `EXPERIMENT/AnchoringEffect/Rag/analysis/`                                                                                                                                           |
| Variant-Specific Considerations | RAG knowledge retrieval effect is the primary research question; analysis must compare to RuleLLM baseline to isolate knowledge contribution; index build/load status must be logged |

---

## §2 Metric Implementation

All 8 metrics are defined in `analysis-bases.md §2`. Below: how each is implemented in the Rag variant.

### Metric: Price Deviation

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_price_deviation()`
- Data source: `EXPERIMENT/AnchoringEffect/Rag/records/market/price/*.json`
- Variant-specific notes: Compare to both Rule and RuleLLM baselines. If Rag MAD < RuleLLM MAD, retrieved knowledge is helping agents correct faster. If Rag MAD > RuleLLM MAD, retrieved knowledge is reinforcing anchoring.
- Expected range for this variant: [2%, 13%] — wider than Rule due to potential knowledge-amplified dynamics

### Metric: Mean Absolute Deviation (MAD)

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_mean_abs_deviation()`
- Data source: market price records + fundamental value from config
- Variant-specific notes: The delta between Rag MAD and RuleLLM MAD is the primary quantification of the RAG knowledge effect. Positive delta = knowledge reinforces anchoring; negative delta = knowledge aids price discovery.
- Expected range for this variant: [2%, 13%]

### Metric: Anchoring Persistence (Half-Life)

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_anchoring_persistence()`
- Data source: deviation time series
- Variant-specific notes: If retrieved documents contain historical examples of anchoring persisting, half-life may increase vs. RuleLLM. If documents contain examples of anchoring being corrected, half-life may decrease.
- Expected range for this variant: [15, 70] rounds

### Metric: Rolling Volatility

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_rolling_volatility()`
- Data source: price return series
- Variant-specific notes: Similar to RuleLLM baseline. Knowledge staleness effects may appear — if retrieved chunks reference outdated market conditions, agents may make inconsistent decisions, increasing volatility.
- Expected range for this variant: [0.4%, 2.5%] per round

### Metric: Return Autocorrelation

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_autocorrelation()`
- Data source: price return series
- Variant-specific notes: Knowledge-reinforced anchoring may produce higher autocorrelation than RuleLLM. Knowledge-aided correction may produce lower autocorrelation and faster mean-reversion.
- Expected range for this variant: lag-1 AC in [0.03, 0.30]

### Metric: Max Drawdown

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_max_drawdown()`
- Data source: cumulative price series
- Variant-specific notes: If retrieved knowledge reinforces sell signals during drawdown (historical crash narratives), Rag may show deeper drawdowns than RuleLLM. This is a testable hypothesis for RAG knowledge design.
- Expected range for this variant: [3%, 24%]

### Metric: Agent-Type Trading Volume

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_agent_volumes()`
- Data source: `EXPERIMENT/AnchoringEffect/Rag/records/{agent_id}/*.json`
- Variant-specific notes: RAG retrieval may increase volume for agents whose knowledge base contains high-activity examples. Compare per-type volume to RuleLLM to isolate knowledge effects.
- Expected range for this variant: similar to RuleLLM ±30%

### Metric: Anchoring Bias Magnitude

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_anchoring_bias_magnitude()`
- Data source: Rag agent records (price, perceived_target from reasoning, bid_price)
- Variant-specific notes: If anchoring-reinforcing documents are retrieved, bias magnitude may be higher than RuleLLM. If correction-supporting documents are retrieved, bias magnitude may be lower. Tracking retrieval query → retrieved document → bias magnitude enables knowledge effect attribution.
- Expected range for this variant: [0.0, 0.6]

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics Analysis

Objective (from analysis-bases.md): Measure how anchoring-induced demand creates and sustains price deviations, with additional focus on knowledge retrieval effects on price discovery speed.

Implementation in analysis.py:
- Function: `analyze_price_dynamics()`
- Input data: market price records; fundamental value from config
- Computation: deviation series, MAD, half-life, rolling volatility; overlay Rule and RuleLLM baselines for comparison
- Output: `price_dynamics.png`, contribution to `summary.json`

Variant-Specific Interpretation:
- Three-way overlay recommended: Rag (solid), RuleLLM (dashed), Rule (dotted)
- Key question: does Rag price path converge to fundamental faster or slower than RuleLLM?
- If no difference from RuleLLM: retrieved knowledge is not affecting price dynamics — check retrieval quality (are relevant chunks being retrieved?)

Expected Output Sample:
```
Three-line price chart. Rag line may show different convergence trajectory.
Key focus: the gap between Rag and RuleLLM deviation curves over time.
```

---

### Dimension 2: RAG Knowledge Effect Analysis (Rag-Specific)

Objective: Quantify the effect of domain knowledge retrieval on agent decisions and market outcomes.

Implementation in analysis.py:
- Function: `analyze_rag_knowledge_effect()`
- Input data: Rag agent records including `rag_context` fields from decision rounds; RuleLLM summary for comparison
- Computation:
  1. Parse retrieved chunk content per round per agent
  2. Classify retrieved chunks as: anchoring-reinforcing / correction-supporting / neutral
  3. Correlate chunk classification with subsequent agent decision (buy/sell/hold)
  4. Compute Rag MAD minus RuleLLM MAD as knowledge effect magnitude
- Output: `rag_knowledge_effect.png`, `rag_retrieval_stats.json`

Variant-Specific Interpretation:
- Positive MAD difference (Rag > RuleLLM): anchoring-reinforcing knowledge dominates retrieval.
- Negative MAD difference (Rag < RuleLLM): correction-supporting knowledge dominates.
- Zero difference: retrieved knowledge does not meaningfully change decisions beyond RuleLLM baseline.
- Knowledge staleness test: check whether retrieved chunks reference recent vs. historical market conditions. Staleness metric = fraction of retrieved chunks with low semantic similarity to current market state.

Expected Output Sample:
```
Bar chart: proportion of anchoring-reinforcing vs. correction-supporting vs. neutral chunks
per agent type. Scatter plot: retrieved chunk relevance score vs. decision change from RuleLLM baseline.
```

---

### Dimension 3: Investor Behavior Analysis

Objective (from analysis-bases.md): Characterize how knowledge retrieval modifies investor decisions compared to RuleLLM.

Implementation in analysis.py:
- Function: `analyze_investor_behavior()`
- Input data: per-agent decision records; rag_context content
- Computation: buy/sell/hold counts; portfolio value; reasoning keyword analysis for RAG influence markers
- Output: `investor_behavior.png`

Variant-Specific Interpretation:
- Look for "knowledge-influenced" rounds: rounds where agent reasoning explicitly references retrieved content.
- Compare per-agent portfolio performance: Rag vs. RuleLLM. If RationalUpdater (Rag) outperforms RationalUpdater (RuleLLM), retrieved rational expectations knowledge is adding decision value.

---

### Dimension 4: Cross-Variant Comparison

Objective (from analysis-bases.md): Position Rag results relative to Rule, LLM, and RuleLLM to isolate the knowledge contribution.

Implementation in analysis.py:
- Function: `generate_comparison_table()`
- Input data: Rag summary.json + Rule/LLM/RuleLLM summary.json (if available)
- Output: `cross_variant_comparison.png`, updated `summary.json`

Variant-Specific Interpretation:
- Primary comparison: Rag vs. RuleLLM (isolates knowledge effect)
- Secondary comparison: Rag vs. Rule (isolates combined LLM + knowledge effect)
- Report: MAD delta, half-life delta, max drawdown delta across these pairs

---

## §4 Variant-Specific Observable Phenomena

Phenomena unique to the Rag variant not present in other variants:

| Phenomenon                      | Description                                                                                                                                  | How to Observe                                                                                                | Contrast with Rule-Based                                                      |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| Knowledge Reinforcement Event   | Retrieved document reinforces anchoring behavior, causing agent to maintain position longer than RuleLLM rules prescribe                     | Round-over-round analysis showing extended hold after retrieval of anchoring-case document                    | Rule has no knowledge retrieval; RuleLLM has no external context              |
| Knowledge Correction Event      | Retrieved rational-expectations document causes agent to break from anchoring and trade toward fundamental faster than RuleLLM               | AnchoredTrader reduces position despite anchoring rule when retrieved document describes anchoring costs      | Impossible in Rule (formula-driven); rare in LLM (no domain knowledge)        |
| Retrieval Failure Round         | No relevant documents retrieved (`(No relevant knowledge retrieved this round.)`) — agent falls back to pure RuleLLM behavior                | `rag_context` field contains fallback string in agent records                                                 | Not applicable to other variants                                              |
| Knowledge Staleness Effect      | Retrieved document content references market conditions irrelevant to current round; agent reasoning shows confusion or irrelevant citations | Agent reasoning contains factual statements that contradict current market state numerical values             | Unique to RAG — stale index problem; not present in other variants            |
| Cross-Agent Knowledge Asymmetry | Different agent types retrieve systematically different quality of context due to different knowledge bases                                  | AnchoredTrader retrieval quality vs. RationalUpdater retrieval quality measured by semantic similarity scores | Each agent has own KnowledgeStore — asymmetry is by design (sim-bases §4 Rag) |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds          | Expected Observable                                                                       | Phenomenon Clarity                                               |
|-----------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| 50 rounds             | RAG index warm-up; knowledge effect may not stabilize                                     | Partial — insufficient for reliable knowledge effect attribution |
| 100 rounds (standard) | Full anchoring lifecycle; RAG retrieval patterns stable after ~10 rounds                  | Good — all 8 metrics + knowledge effect dimension computable     |
| 200 rounds            | Long-run knowledge staleness detectable; potential knowledge reinforcement feedback loops | Excellent — enables longitudinal RAG quality analysis            |

### Agent Count Scaling

| Agent Count            | Expected Observable                                                                        | Market Dynamics                                  |
|------------------------|--------------------------------------------------------------------------------------------|--------------------------------------------------|
| 5 agents (1 per type)  | One knowledge store per type; clear individual-level retrieval analysis                    | Standard — sufficient for RAG effect measurement |
| 10 agents (2 per type) | Intra-type retrieval variance; two agents of same type may retrieve different top-k chunks | Better statistics; higher API and index cost     |

### Parameter Sensitivity

| Parameter                 | Change                                                   | Expected Effect on Analysis                                                                                                          |
|---------------------------|----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `top_k`                   | 1 → 5                                                    | More context = potentially more knowledge influence; also more irrelevant content; MAD change direction depends on knowledge quality |
| `embed_model`             | Weaker model                                             | Lower retrieval relevance; results converge toward RuleLLM baseline (no-retrieval scenario)                                          |
| `docs_dir` content        | Replace anchoring papers with trend-following literature | AnchoredTrader behavior shifts toward MomentumTrader; MAD pattern changes                                                            |
| `rag_persist_dir` deleted | Force index rebuild                                      | First-run behavior; no functional change; only latency impact                                                                        |

---

## §6 Output Files Reference

All outputs written to: `EXPERIMENT/AnchoringEffect/Rag/analysis/`

| Output File                    | Generated By                     | Contents                                                                                  | Interpretation                                     |
|--------------------------------|----------------------------------|-------------------------------------------------------------------------------------------|----------------------------------------------------|
| `price_dynamics.png`           | `analyze_price_dynamics()`       | Price vs. fundamental; Rag, RuleLLM, Rule overlay                                         | Primary evidence for RAG effect on price discovery |
| `rag_knowledge_effect.png`     | `analyze_rag_knowledge_effect()` | Chunk classification distribution; retrieval relevance scores; MAD delta vs. RuleLLM      | Quantifies knowledge retrieval contribution        |
| `rag_retrieval_stats.json`     | `analyze_rag_knowledge_effect()` | Per-round per-agent retrieval metadata; chunk relevance scores; fallback rate             | RAG pipeline quality audit                         |
| `investor_behavior.png`        | `analyze_investor_behavior()`    | Buy/sell/hold counts; portfolio values; knowledge-influenced round markers                | Shows how RAG modifies agent decisions             |
| `cross_variant_comparison.png` | `generate_comparison_table()`    | Side-by-side metric comparison with Rule/LLM/RuleLLM                                      | Positions Rag in variant comparison matrix         |
| `summary.json`                 | `main()`                         | All 8 metrics + RAG-specific metadata (fallback rate, avg retrieval score); variant label | Cross-variant comparison input                     |

---

## §7 Cross-Variant Comparison Notes

This variant's expected position in cross-variant comparison (from `analysis-bases.md §5`):

- **Phenomenon emergence speed**: Similar to RuleLLM — anchoring rules are embedded in prompts and active from round 1. If knowledge base contains strong anchoring-reinforcing examples, phenomenon may intensify slightly faster.
- **Phenomenon intensity**: Uncertain — depends on knowledge base content quality. Expected MAD within ±3 percentage points of RuleLLM. The direction of the difference is itself a research finding.
- **Behavioral realism**: Highest among all variants — combines explicit rules (RuleLLM-level) with domain knowledge context (enables historically-grounded reasoning). Agents may cite specific papers or historical events in their reasoning traces.
- **Decision quality**: If retrieved knowledge improves RationalUpdater performance, Rag may show better portfolio outcomes than RuleLLM for that agent type. AnchoredTrader may show worse performance if anchoring-reinforcing knowledge keeps it in losing positions longer.

See also: `simulation-bases.md §9` — Variant Comparison Preview
