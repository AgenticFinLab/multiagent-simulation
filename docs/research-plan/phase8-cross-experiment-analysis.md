# Phase 8: Cross-Experiment Analysis

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 7 with experiment results
> **Output:** Comparison tables, unified analysis, `docs/conclusion.md`

---

## Overview

Perform horizontal comparison across all experiment results, verify bridge point consistency, extract final conclusions.

This is the culmination of the research — answering the core hypothesis from Phase 0 with experimental evidence.

---

## 8.1 Comparison Framework

Build unified comparison tables across different experiment groups:

### Comparison Table Structure

| Method/Mode           | Experiment Group   | Key Parameters              | Expected Ranking | Actual Results | Notes                  |
|-----------------------|--------------------|-----------------------------|------------------|----------------|------------------------|
| VLM-guided, 8 regions | Region Extraction  | method=vlm_guided, num=8    | High             | 0.71           | Best extraction method |
| Grid, 8 regions       | Region Extraction  | method=grid, num=8          | Medium           | 0.65           | Baseline extraction    |
| Adaptive graph        | Graph Construction | method=adaptive, thresh=0.5 | High             | 0.73           | Best graph structure   |
| Fully-connected       | Graph Construction | method=full                 | Medium           | 0.70           | Too dense              |
| GraphRegion           | End-to-End         | full pipeline               | Highest          | 0.75           | Our approach           |
| VLM-R³                | End-to-End         | sequential                  | High             | 0.72           | Baseline comparison    |
| CoFFT                 | End-to-End         | multi-step                  | Medium           | 0.68           | Efficiency baseline    |
| ParGo                 | End-to-End         | grid                        | Low              | 0.64           | Grid baseline          |

> **Expected ranking must be written before experiments.** If actual results don't match expectations, this itself is an important finding.

---

## 8.2 Bridge Validation

Bridge validation is key to ensuring results across different experiment groups are comparable:

### Bridge Validation Concept

```
General Pattern:
  A special configuration in Experiment Group A ≈ A special configuration in Experiment Group B
  → If results are consistent: Both groups' frameworks are compatible
  → If results are inconsistent: Investigate differences

Design Principles:
  1. Design at least one bridge point connecting each pair of adjacent experiment groups
  2. Bridge validation should be completed before formal comparison
  3. When bridges are inconsistent, must resolve before drawing cross-group conclusions
```

### VSGR Bridge Points

| Bridge | Experiment A                | Experiment B                   | Expected Equivalence                                       |
|--------|-----------------------------|--------------------------------|------------------------------------------------------------|
| 1      | Region: VLM-guided, num=8   | Graph: adaptive with all edges | Graph construction shouldn't hurt if all regions connected |
| 2      | Graph: adaptive, thresh=1.0 | End-to-End: fully-connected    | High threshold ≈ fully connected                           |
| 3      | End-to-End: no graph edges  | Region: independent regions    | No edges = independent processing                          |

### Bridge Validation Procedure

```python
# scripts/validate_bridges.py
"""Validate bridge points across experiment groups."""

import json
from pathlib import Path

def load_result(exp_group: str, experiment: str, run_name: str) -> dict:
    """Load summary.json for a specific run."""
    result_file = Path(f"EXPERIMENT/{exp_group}/{experiment}/{run_name}/summary.json")
    return json.loads(result_file.read_text())

def validate_bridge_1():
    """Bridge 1: Region extraction vs Graph construction."""
    region_result = load_result("preExp", "region_extraction", "region_vlm_guided_num8_llava7b")
    graph_result = load_result("preExp", "graph_construction", "graph_adaptive_all_edges_llava7b")
    
    diff = abs(region_result["accuracy"] - graph_result["accuracy"])
    
    print("Bridge 1 Validation:")
    print(f"  Region extraction accuracy: {region_result['accuracy']:.3f}")
    print(f"  Graph (all edges) accuracy: {graph_result['accuracy']:.3f}")
    print(f"  Difference: {diff:.3f}")
    
    if diff < 0.02:  # 2% tolerance
        print("  Status: ✓ PASS — Bridge consistent")
        return True
    else:
        print("  Status: ✗ FAIL — Bridge inconsistent, investigate")
        return False

def validate_all_bridges():
    """Validate all bridge points."""
    results = []
    results.append(("Bridge 1", validate_bridge_1()))
    # Add more bridges...
    
    print("\n" + "="*50)
    print("Bridge Validation Summary:")
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("All bridges validated — cross-group comparison is valid")
    else:
        print("Some bridges failed — resolve before cross-group comparison")
    
    return all_passed

if __name__ == "__main__":
    validate_all_bridges()
```

---

## 8.3 Conclusion Extraction

Final conclusions must **directly answer the core hypothesis from Phase 0**:

### Conclusion Document Structure

```markdown
# Research Conclusion: VSGR

## Phase 0 Hypothesis (Recap)

Visual reasoning with region relationship graphs via multi-agent reinforcement
learning outperforms sequential one-step-one-region approaches while maintaining
full image context and reducing inference iterations.

## Verification Results

### Sub-hypothesis 1: Accuracy Comparison
**Claim:** GraphRegion achieves higher accuracy than VLM-R³ on cross-region reasoning

| Method             | Accuracy | Relative Improvement |
|--------------------|----------|----------------------|
| GraphRegion (ours) | 0.75     | —                    |
| VLM-R³             | 0.72     | +4.2%                |
| CoFFT              | 0.68     | +10.3%               |
| ParGo              | 0.64     | +17.2%               |

**Conclusion:** ✓ Supported — GraphRegion achieves highest accuracy

### Sub-hypothesis 2: Efficiency Comparison
**Claim:** GraphRegion is more efficient than multi-iteration methods

| Method      | Avg Time (s) | Speedup vs VLM-R³ |
|-------------|--------------|-------------------|
| GraphRegion | 2.5          | 2.4x faster       |
| VLM-R³      | 6.0          | —                 |
| CoFFT       | 8.5          | 0.7x (slower)     |
| ParGo       | 1.8          | 3.3x faster       |

**Conclusion:** ✓ Supported — GraphRegion is 2.4x faster than VLM-R³

### Sub-hypothesis 3: Region Quality
**Claim:** Adaptive regions outperform uniform grid

| Method     | Accuracy | Coverage |
|------------|----------|----------|
| VLM-guided | 0.71     | 0.82     |
| Grid       | 0.65     | 0.68     |
| Saliency   | 0.63     | 0.71     |

**Conclusion:** ✓ Supported — VLM-guided extraction is best

## Bridge Validation Results

| Bridge             | Status | Notes                  |
|--------------------|--------|------------------------|
| Region → Graph     | ✓ Pass | Consistent within 1.5% |
| Graph → End-to-End | ✓ Pass | Consistent within 2%   |

All bridges validated — cross-group comparison is valid.

## Overall Conclusion

**The core hypothesis is SUPPORTED by experimental evidence:**

1. GraphRegion achieves **4.2% higher accuracy** than the best baseline (VLM-R³)
2. GraphRegion is **2.4x faster** than sequential approaches
3. Adaptive region extraction **outperforms uniform grid** by 9.2%

### Key Insights

1. **Graph structure enables cross-region reasoning** that sequential approaches miss
2. **Single-pass inference** is significantly more efficient than multi-iteration
3. **VLM-guided region extraction** focuses on relevant image areas

### Limitations and Future Work

1. Experiments limited to Visual7W and GQA datasets — broader evaluation needed
2. Region extraction depends on VLM quality — errors propagate
3. Graph construction hyperparameters (threshold) require tuning

## Comparison to Baselines

| Aspect                 | VSGR     | VLM-R³  | CoFFT | ParGo |
|------------------------|----------|---------|-------|-------|
| Accuracy               | **0.75** | 0.72    | 0.68  | 0.64  |
| Speed                  | **2.5s** | 6.0s    | 8.5s  | 1.8s  |
| Cross-region reasoning | **Yes**  | Limited | No    | No    |
| Adaptive regions       | **Yes**  | Yes     | No    | No    |
| Training required      | **No**   | No      | No    | No    |
```

---

## 8.4 Discrepancy Analysis

When actual results don't match expected rankings, document the analysis:

```markdown
## Discrepancy Analysis

### Expected vs Actual: Graph Construction

**Expected:** Adaptive graph > Fully-connected > KNN
**Actual:** Adaptive (0.73) > Fully-connected (0.70) > KNN (0.68)

**Analysis:**
- Result matches expected ranking
- However, margin between adaptive and fully-connected is smaller than expected
- Investigation: Fully-connected may work better for small region counts

### Expected vs Actual: Region Count

**Expected:** Accuracy increases monotonically with region count
**Actual:** Peak at 8-12 regions, decrease at 16 regions

**Analysis:**
- Contradicts initial expectation
- Hypothesis: Too many regions introduce noise and dilute attention
- Follow-up: Test adaptive region count based on image complexity
```

---

## 8.5 Final Deliverables

### 1. Conclusion Document
`docs/conclusion.md` — Complete research conclusion with:
- Hypothesis restatement
- Verification results for each sub-hypothesis
- Bridge validation results
- Overall conclusion with supporting data
- Limitations and future work

### 2. Comparison Tables
`docs/comparison-tables.md` — All cross-experiment comparisons:
- Method comparison table
- Ablation study results
- Efficiency comparison
- Dataset-specific results

### 3. Visualization Summary
`EXPERIMENT/final-plots/` — Key visualizations:
- Accuracy comparison across all methods
- Efficiency comparison
- Ablation analysis
- Example predictions (qualitative)

### 4. Reproducibility Package
```
REPRODUCE/
├── README.md                    # How to reproduce all experiments
├── requirements.txt             # Exact dependency versions
├── environment.yml              # Conda environment (optional)
├── configs/                     # All configs used
└── scripts/
    ├── run_all_experiments.sh   # One-command reproduction
    └── verify_results.py        # Check results match reported
```

---

## 8.6 Output Verification

| Check Item                                                | Verification Method                                     |
|-----------------------------------------------------------|---------------------------------------------------------|
| Cross-experiment group comparison table established?      | Table includes key modes from all experiment groups     |
| Expected ranking written before experiments?              | Check document version history                          |
| Bridge validation results consistent?                     | Compare key metrics in bridge experiments' summary.json |
| If bridges inconsistent, issue investigated and resolved? | Document has investigation record                       |
| Final conclusion directly answers Phase 0 hypothesis?     | Conclusion format is "Supports/Does not support + data" |
| Conclusion document (`docs/conclusion.md`) written?       | Open to confirm content is complete                     |
| All discrepancies between expected and actual analyzed?   | Document has explicit discrepancy discussion            |

---

## 8.7 Phase 8 Completion Marker

**Phase 8 is complete when you can clearly explain in one paragraph + one table:**

> "Our hypothesis was that graph-based visual reasoning would outperform sequential approaches. We tested this through 4 progressive experiments comparing region extraction, graph construction, and end-to-end reasoning against 3 baselines. Results show GraphRegion achieves 4.2% higher accuracy and 2.4x faster inference than the best baseline (VLM-R³), supporting our hypothesis."

| Method             | Accuracy | Speed | Supports Hypothesis?                |
|--------------------|----------|-------|-------------------------------------|
| GraphRegion (ours) | 0.75     | 2.5s  | —                                   |
| VLM-R³             | 0.72     | 6.0s  | ✓ Better accuracy + speed           |
| CoFFT              | 0.68     | 8.5s  | ✓ Better accuracy + speed           |
| ParGo              | 0.64     | 1.8s  | ✓ Better accuracy (trade-off speed) |

---

## Research Completion

Upon completing Phase 8, the research cycle is complete. The deliverables include:

1. **Codebase:** Fully functional `{package}/` with modules, tests, and documentation
2. **Experiments:** Complete `EXPERIMENT/` directory with reproducible results
3. **Documentation:** Comprehensive docs covering all phases
4. **Conclusions:** Clear answer to the original hypothesis

### Optional Next Steps

- **Paper Writing:** Convert conclusion to academic paper format
- **Extended Experiments:** Test on additional datasets or with variations
- **Code Release:** Clean and release code for community use
- **Follow-up Research:** Identify new hypotheses based on findings
