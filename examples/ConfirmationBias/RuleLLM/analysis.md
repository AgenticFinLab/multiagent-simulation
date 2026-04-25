# ConfirmationBias RuleLLM Variant — Analysis Guide

## 1. Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias RuleLLM** variant.
Key question: *Do LLM agents with explicit decision rules achieve ≥80% adherence?
Does rule-guided behavior reproduce the Rule variant's bias dynamics?*

---

## 2. Metric Implementation (`RuleLLM/analysis.py`)

Imports `calculate_metrics`, `load_simulation_data` from `Rule/analysis.py` (DRY pattern).
Adds `analyze_rule_adherence()` — the primary RuleLLM-specific metric.

### `analyze_rule_adherence()` — Key Function

```python
def analyze_rule_adherence(agent_records):
    # For each agent: count rounds where llm_action == rule_action
    # adherence_rate = matching_rounds / total_rounds
    # meets_target = adherence_rate >= 0.80
```

| Metric            | Target     | Interpretation                            |
|-------------------|------------|-------------------------------------------|
| `adherence_rate`  | ≥ 0.80     | LLM follows decision rules ≥80% of rounds |
| `meets_target`    | True/False | Whether prompt engineering is adequate    |
| `matching_rounds` | Count      | Rounds where LLM matched rule             |
| `total_rounds`    | Count      | Total rounds with rule_action data        |

---

## 3. RuleLLM-Specific Output Files

Running `RuleLLM/analysis.py` writes to `EXPERIMENT/ConfirmationBias/RuleLLM/records/analysis/`:

| File                                    | Contents                                                  |
|-----------------------------------------|-----------------------------------------------------------|
| `confirmationbias_rulellm_analysis.png` | 2×2 chart with rule-adherence bar chart                   |
| `summary.json`                          | `{variant: "RuleLLM", ...metrics, rule_adherence: {...}}` |
| `rule_adherence.json`                   | Per-agent adherence statistics                            |

---

## 4. Dimension-by-Dimension Interpretation

### 4.1 Price vs Fundamental

- RuleLLM should produce bias_amplitude_pct between Rule and LLM
- Closer to Rule → rules successfully guide LLM behavior
- Closer to LLM → LLM is overriding rules with "free" reasoning

### 4.2 Deviation Time Series

- `bias_persistence_rounds` should be close to Rule if adherence ≥ 80%
- Rapid oscillation → LLM frequently deviating from rules (low adherence)

### 4.3 Rule Adherence Bar Chart

- **Green bars** (≥ 80%): Prompt engineering adequate for this agent
- **Red bars** (< 80%): Agent's `== DECISION RULES ==` section needs revision
- Key agent to watch: **BeliefAnchor** — rules simplify the internal belief state,
  making this agent hardest to replicate at ≥80%

---

## 5. Variant-Specific Phenomena

### 5.1 BeliefAnchor Simplification Gap

Rule BeliefAnchor: compounding `belief` state → very strong, locked behavior
RuleLLM BeliefAnchor: simplified deviation threshold rule
→ Expect lower adherence for BeliefAnchor vs other agents
→ Lower `bias_amplitude_pct` than Rule

### 5.2 Adherence Improvement Strategies

If an agent's adherence_rate < 80%:
1. Add clearer numerical thresholds in `== DECISION RULES ==`
2. Reduce ambiguity: "If deviation > 0.02, you MUST buy exactly {order_size} units"
3. Reduce temperature to 0.1 for more deterministic outputs
4. Add few-shot examples in the user template

### 5.3 Rule Override Patterns

LLM agents sometimes override rules when market state is extreme.
Positive override: LLM recognizes crisis risk not captured in rule
Negative override: LLM hallucinates rationale for not following rule

---

## 6. Cross-Variant Comparison

| Metric                    | Expected Position          |
|---------------------------|----------------------------|
| `bias_amplitude_pct`      | Rule > RuleLLM > LLM       |
| `bias_persistence_rounds` | Rule > RuleLLM ≈ LLM       |
| `correction_ratio`        | LLM ≈ Rag > RuleLLM ≈ Rule |
| `adherence_rate`          | Target ≥ 80%               |

Compare `rule_adherence.json` per agent to identify which agents
need prompt improvement in the next iteration.
