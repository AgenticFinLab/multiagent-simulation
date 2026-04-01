# AssetBubble Rag Analysis Methodology

## Overview

This document describes the evaluation metrics for the **RAG-enhanced asset bubble** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../AssetBubble/analysis.md`**

---

## RAG-Specific Observable Phenomena

### Emergent Behaviors Unique to RAG-Enhanced Agents

| Phenomenon                  | RAG Behavior                                                    | Contrast with Rule-Based               |
|-----------------------------|-----------------------------------------------------------------|----------------------------------------|
| **Knowledge Retrieval**     | Agents retrieve relevant financial concepts from knowledge base | Rule-based has hardcoded rules         |
| **Context-Aware Decisions** | LLM reasoning informed by retrieved domain knowledge            | Rule-based uses fixed formulas         |
| **Adaptive Reasoning**      | Different knowledge retrieved based on market state             | Rule-based is static                   |
| **Grounded Behavior**       | Decisions grounded in documented financial theory               | Rule-based encoded without explanation |

### Expected Differences from Rule-Based

1. **Bubble Formation**: May be more nuanced as agents "understand" bubble dynamics
2. **Peak Deviation**: Potentially lower if retrieved knowledge warns about bubble risks
3. **Crash Dynamics**: May be more orderly if agents recognize warning signs
4. **Cross-Scenario Consistency**: RAG provides consistent theoretical grounding

---

## RAG Configuration

The RAG system uses:
- **Document Source**: Financial literature on asset bubbles, greater fool theory, limits to arbitrage
- **Embedding Model**: HuggingFace BAAI/bge-small-en-v1.5
- **Retrieval Strategy**: Top-k relevant passages per agent per round

---

## Round and Agent Scaling (RAG-Specific)

### Round Scaling

| Total Rounds    | RAG-Specific Observation                                      |
|-----------------|---------------------------------------------------------------|
| **50 rounds**   | RAG may stabilize early if knowledge warns about bubble risks |
| **100 rounds**  | Clear bubble-crash cycle with grounded agent reasoning        |
| **200+ rounds** | Knowledge retrieval may lead to faster recovery after crash   |

### Agent Scaling

| Agent Count     | RAG-Specific Observation                                          |
|-----------------|-------------------------------------------------------------------|
| **3-5 agents**  | High variance in retrieved context; divergent behaviors           |
| **8-10 agents** | Balanced dynamics; shared knowledge base produces coherent market |
| **20+ agents**  | Emergent consensus from shared theoretical grounding              |

---

## Key Metrics (Summary)

| Metric            | Purpose                                |
|-------------------|----------------------------------------|
| Price Deviation   | (P - F) / F deviation from fundamental |
| Bubble Magnitude  | Cumulative deviation                   |
| Positive Feedback | Price increase → more buying           |
| Crash Detection   | Rapid price decline after peak         |

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_price_deviation,
    calculate_bubble_magnitude,
    calculate_returns,
    plot_bubble_crash_analysis,
)

# Same analysis as rule-based version
prices = {...}
deviation = calculate_price_deviation(prices, fundamental=100.0)
bubble = calculate_bubble_magnitude(prices, fundamental=100.0)
```

---

## References

See `../AssetBubble/analysis.md` for complete academic references.
