# AssetBubble Rag — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                                                                                                     |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                                                                                          |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                                                                                                 |
| **Output Location**                 | `EXPERIMENT/AssetBubble/Rag/analysis/`                                                                                                                                                                                          |
| **Variant-Specific Considerations** | RAG-augmented variant — agents retrieve domain knowledge each round; expect bubble dynamics influenced by quality and relevance of retrieved passages; run multiple trials (≥5) for reliable estimates due to LLM stochasticity |

---

## 1. Metric Implementation

All metrics are defined in `../analysis-bases.md §2`. This variant's `analysis.py` delegates to `examples.AssetBubble.Rule.analysis.analyze_bubble()` via:

```python
from examples.AssetBubble.Rule.analysis import analyze_bubble, _load_data
```

| Metric                      | Function                         | analysis-bases.md Ref | Rag-Specific Notes                                                        |
|-----------------------------|----------------------------------|-----------------------|---------------------------------------------------------------------------|
| **Price Deviation**         | `calculate_price_deviation()`    | `§2.1`                | RAG may moderate extremes if agents retrieve bubble-warning docs          |
| **Bubble Ratio**            | derived in `analyze_bubble()`    | `§2.2`                | Compare to Rule baseline; expect narrower peak if knowledge helps         |
| **Bubble Magnitude**        | `calculate_bubble_magnitude()`   | `§2.3`                | Cumulative area; RAG effect most visible here                             |
| **Rolling Volatility**      | `calculate_rolling_volatility()` | `§2.4`                | window=10; volatility profile shaped by RAG retrieval quality             |
| **Return Autocorrelation**  | `calculate_autocorrelation()`    | `§2.5`                | lag-1 autocorr; RAG may break momentum if agents retrieve contrarian docs |
| **Max Drawdown**            | `calculate_max_drawdown()`       | `§2.6`                | Crash severity; informed agents may exit earlier                          |
| **Trading Volume**          | derived from order aggregation   | `§2.7`                | Volume spike pattern indicates bubble phase transitions                   |
| **Positive Feedback Index** | correlation of Δprice vs Δvolume | `§2.8`                | Measures RAG's moderating effect on herding behavior                      |

---

## 2. Analysis Dimensions

All dimensions are defined in `../analysis-bases.md §3`. Implementation for this variant:

| Dimension                  | analysis-bases.md Ref | Key Observation in Rag Variant                                                |
|----------------------------|-----------------------|-------------------------------------------------------------------------------|
| **Price Dynamics**         | `§3.1`                | Compare price trajectory to Rule/LLM/RuleLLM; RAG may show slower buildup     |
| **Bubble Lifecycle**       | `§3.2`                | Phase detection (latent/growth/peak/crash/recovery) using same thresholds     |
| **Investor Heterogeneity** | `§3.3`                | Each agent type retrieves different knowledge; creates more diverse behavior  |
| **Stability Analysis**     | `§3.4`                | Autocorrelation + volatility profiles per agent type                          |
| **RAG Knowledge Effect**   | `§3.5`                | Unique to Rag: measure whether retrieved passages materially change decisions |

---

## 3. RAG-Specific Observable Phenomena

These phenomena are unique to the Rag variant and require dedicated analysis beyond the standard metrics:

| Phenomenon                       | Description                                                                                    | Measurement                                           |
|----------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| **Knowledge Retrieval Quality**  | Top-k chunks may or may not be relevant to current market state                                | Log retrieval relevance scores per round              |
| **Context-Aware Decision Shift** | Agents citing bubble-warning knowledge should trade more conservatively                        | Compare quantity distributions with/without retrieval |
| **Adaptive Herding Reduction**   | If NoiseTrader retrieves contrarian behavioral finance, herding should weaken                  | Positive feedback index vs RuleLLM baseline           |
| **Arbitrageur Empowerment**      | Arbitrageur retrieving limits-to-arbitrage literature may increase short pressure              | Track arbitrageur quantity and timing                 |
| **Knowledge Persistence Effect** | Indexed knowledge is static; stale docs may lead to miscalibrated decisions late in simulation | Compare early vs late round decision quality          |
| **Index Load vs Build**          | Resumed simulations (loaded index) vs fresh builds may show different retrieval patterns       | Flag and compare across runs                          |

### Expected Differences from Rule Baseline

| Metric                | Rule Baseline | Rag Expected                             | Hypothesis                                         |
|-----------------------|---------------|------------------------------------------|----------------------------------------------------|
| Peak bubble_ratio     | [1.3, 1.8]×   | [1.1, 1.6]× (potentially lower)          | Informed agents exit earlier                       |
| Max drawdown          | [20%, 60%]    | [15%, 50%] (potentially smaller)         | Agents recognize warning signs from retrieved docs |
| Return autocorr lag-1 | [0.2, 0.6]    | [0.1, 0.4] (potentially weaker momentum) | Contrarian knowledge breaks positive feedback      |
| Bubble magnitude      | High          | Medium-to-high (high variance)           | Effect depends heavily on retrieval quality        |

> Note: These are research hypotheses to be tested. Actual results depend on document sources, embedding quality, and top-k retrieval accuracy.

---

## 4. Scaling and Sensitivity

### Round Scaling

| Total Rounds    | Rag-Specific Observation                                              |
|-----------------|-----------------------------------------------------------------------|
| **50 rounds**   | Agents rely on initial knowledge; RAG effect most pronounced early on |
| **100 rounds**  | Full bubble-crash cycle; RAG effect visible in peak and crash timing  |
| **200+ rounds** | Knowledge staleness effect becomes apparent; late-run divergence      |

### Agent Scaling

| Agent Count     | Rag-Specific Observation                                                     |
|-----------------|------------------------------------------------------------------------------|
| **3–5 agents**  | High variance in retrieved context; agent-level divergence dominates         |
| **8–10 agents** | Balanced dynamics; shared vs personal knowledge base effects visible         |
| **20+ agents**  | Emergent consensus from theoretical grounding; risk of correlated retrievals |

### RAG Configuration Sensitivity

| Parameter           | Effect on Bubble Dynamics                                                     |
|---------------------|-------------------------------------------------------------------------------|
| `top_k` (retrieval) | Higher k = more context but more noise; optimal k depends on document quality |
| `embed_model`       | Better embeddings → more relevant chunks → stronger RAG effect                |
| `persist_dir`       | Loaded index: fast but static; fresh build: slower but current                |
| Document sources    | Theory-heavy docs reduce bubble; narrative docs may amplify                   |

---

## 5. Output Files

All output files are written to `EXPERIMENT/AssetBubble/Rag/analysis/`.

| File                     | Content                                                                  |
|--------------------------|--------------------------------------------------------------------------|
| `01_price_dynamics.png`  | Price vs fundamental time series                                         |
| `02_bubble_analysis.png` | Bubble ratio, rolling volatility, return autocorrelation                 |
| `03_summary.png`         | Multi-panel: all 8 metrics + RAG-specific panels                         |
| `summary.json`           | Structured metrics: all scalar outputs                                   |
| `retrieval_log.json`     | (if enabled) Per-round retrieval queries, top-k chunks, relevance scores |

Output files follow the same naming convention as `Rule/analysis.py`; see `../analysis-bases.md §6`.

---

## 6. Cross-Variant Comparison Notes

This variant should be compared against all three baselines to isolate the RAG effect:

| Comparison Pair | What It Tests                                                         |
|-----------------|-----------------------------------------------------------------------|
| Rag vs Rule     | Full effect of LLM reasoning + RAG knowledge vs deterministic rules   |
| Rag vs LLM      | Effect of adding RAG context to a pure-LLM variant (same personas)    |
| Rag vs RuleLLM  | Marginal effect of external knowledge retrieval beyond embedded rules |

Cross-variant comparison protocol is defined in `../analysis-bases.md §4`.

**Key research question**: Does per-agent personal RAG knowledge reduce bubble severity relative to RuleLLM, and by how much?

**Calibration targets** (from `../analysis-bases.md §5`):
- Peak `bubble_ratio`: [1.3, 1.8]× (if no RAG moderation) or [1.1, 1.6]× (if RAG effective)
- Max drawdown: [20%, 60%]
- Return autocorr lag-1: [0.2, 0.6] in Rule; expect lower in Rag

---

## References

- `../analysis-bases.md` — master analysis specification (metrics, dimensions, validation)
- `../simulation-bases.md §4` — all investor type specifications
- `../simulation-bases.md §3.1` — price dynamics formula
- `Rule/analysis.py` — shared analysis implementation (delegate target)
- `Rag/players.py` — `_initialize_rag()`, `_build_prompt()`, `KnowledgeStore` usage
