# Phase 6: Experiment Design

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 5 with refined hypothesis
> **Output:** Experiment docs, configs, scripts, progressive experiment plan

---

## Overview

Design progressive preliminary experiments (preExp), each experiment verifying one clear sub-hypothesis.

Experiments should form a logical progression from simple to complex, building evidence toward the core hypothesis.

---

## 6.1 Design Principles

| Principle                            | Description                                                                                      |
|--------------------------------------|--------------------------------------------------------------------------------------------------|
| **Progressive Complexity**           | Single-variable experiments first, then multi-variable, finally cross-experiment comparison      |
| **One Core Question per Experiment** | Clearly state "what question does this experiment answer"                                        |
| **Control Variables**                | Same model, same dataset, same evaluation method — only vary experimental variables              |
| **Reproducibility**                  | Config-file driven, fixed random seeds, incremental storage (supports resume)                    |
| **Bridge Validation**                | Design at least one "bridge point" enabling cross-validation between different experiment groups |

---

## 6.2 Progress Recording

Debugging notes, key findings, and engineering issues during research should be recorded in real-time in `docs/Progress-record.md`:

```markdown
## Region Extraction Experiment
- Discovered VLM-guided extraction produces variable region counts
- Solution: Implement adaptive region count with max_regions limit
- Detailed test records: num_regions vs accuracy trade-off

## Graph Construction Experiment
- Found fully-connected graph is too dense for large region counts
- Solution: Use adaptive thresholding based on feature similarity
- Tested thresholds: 0.3 (too sparse), 0.5 (good), 0.7 (too dense)
```

> This document is **informal logging**, doesn't need tidy formatting, but is crucial for later review and paper writing.

---

## 6.3 Script Organization

Experiment script organization evolves with project development:

### Early Stage
```
examples/preExp/
├── region_extraction.py        # Single file does everything
├── graph_construction.py
└── prompts.py                  # Shared prompts
```

### Mature Stage
```
examples/preExp/
├── region_extraction/          # Experiment set: self-contained
│   ├── __init__.py
│   ├── prompts.py
│   ├── extract_vlm_guided.py
│   ├── extract_grid.py
│   └── run_batch.py
├── graph_construction/
│   └── ...
└── end_to_end/
    └── ...
```

**Evolution principle:** When an experiment group has more than 2 scripts, or needs dedicated `prompts.py`, migrate to subdirectory.

---

## 6.4 Batch Config Generation

When experiments have multiple parameter combinations, use Python scripts for batch generation:

### Config Naming Convention

```
{experiment}_{mode}_{param}{value}_{model}.yml

Examples:
  region_vlm_guided_num8_llava7b.yml
  region_grid_num16_llava7b.yml
  graph_adaptive_thresh05_qwen7b.yml
  graph_full_edges_qwen7b.yml
```

### Batch Generation Script

```python
# examples/preExp/generate_configs.py
"""Generate experiment configs following naming convention."""

import os
from pathlib import Path

TEMPLATE = """
data:
  dataset_name: "{dataset}"
  split: "test"
  num_samples: 100

model:
  name: "{model}"

graph_region:
  region_extraction:
    method: "{region_method}"
    num_regions: {num_regions}
  graph_construction:
    method: "{graph_method}"
    edge_threshold: {threshold}

experiment:
  name: "{exp_name}"
"""

def generate_region_configs():
    """Generate region extraction experiment configs."""
    models = ["llava-hf/llava-1.5-7b-hf", "Qwen/Qwen2-VL-7B-Instruct"]
    methods = ["vlm_guided", "grid", "saliency"]
    num_regions = [4, 8, 16]
    
    output_dir = Path("configs/preExp/region_extraction")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for model in models:
        model_short = model.split("/")[-1].replace("-", "_")
        for method in methods:
            for num in num_regions:
                config_name = f"region_{method}_num{num}_{model_short}.yml"
                config_content = TEMPLATE.format(
                    dataset="Visual7W",
                    model=model,
                    region_method=method,
                    num_regions=num,
                    graph_method="adaptive",
                    threshold=0.5,
                    exp_name=f"region_{method}_num{num}"
                )
                (output_dir / config_name).write_text(config_content)
                
if __name__ == "__main__":
    generate_region_configs()
```

> **Naming convention is crucial:** Batch runners depend on filename regex to identify experiment groups and parameter values.

---

## 6.5 Experiment Group Organization

Each experiment group maintains **one-to-one correspondence** across `docs/`, `examples/`, `configs/`:

```
docs/preExp/                           # Experiment documentation
├── README.md                          # Experiment index (overview table + logic diagram)
├── region_extraction.md               # Per-experiment detailed documentation
├── graph_construction.md
└── end_to_end.md

examples/preExp/                       # Experiment scripts
├── region_extraction/
│   ├── __init__.py
│   ├── README.md                      # Implementation doc
│   ├── prompts.py                     # Prompt templates
│   ├── extract.py                     # Main script
│   └── run_batch.py                   # Batch runner
├── graph_construction/
│   └── ...
└── plotting/                          # Visualization scripts

configs/preExp/                        # Experiment configs
├── region_extraction/
│   └── region_{method}_num{num}_{model}.yml
└── graph_construction/
    └── graph_{method}_thresh{val}_{model}.yml
```

### Implementation README Requirements

Each experiment implementation directory must contain `README.md`:

| Section                          | Content                                             |
|----------------------------------|-----------------------------------------------------|
| **Experiment Objective**         | What core question does this experiment answer?     |
| **Implementation Architecture**  | Call relationships between scripts (ASCII diagram)  |
| **Core Logic Explanation**       | Inference flow, data flow, key steps                |
| **Prompt Design Explanation**    | Design intent for each prompt                       |
| **Config Parameter Explanation** | Which config parameters, meanings and ranges        |
| **Batch Runner Explanation**     | Discovery strategy, execution order, state tracking |
| **Relationship to docs/**        | Points to corresponding design doc                  |

---

## 6.6 VSGR Experiment Design

### Progressive Experiment Logic

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Progressive Experiment Logic                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Experiment 1: Region Extraction (Foundational)                      │
│    ├── Compare extraction methods: VLM-guided vs Grid vs Saliency    │
│    ├── Find optimal region count                                     │
│    └── Establish region quality metrics                              │
│                                                                      │
│  Experiment 2: Graph Construction (Structural)                       │
│    ├── Compare graph methods: Adaptive vs Fully-connected vs KNN     │
│    ├── Find optimal edge threshold                                   │
│    └── Validate graph structure quality                              │
│                                                                      │
│  Experiment 3: End-to-End Reasoning (Integration)                    │
│    ├── Single-pass GraphRegion vs Sequential VLM-R³                  │
│    ├── Compare accuracy on multi-hop visual questions                │
│    └── Measure inference efficiency                                  │
│                                                                      │
│  Experiment 4: Baseline Comparison (Validation)                      │
│    ├── Compare against: VLM-R³, CoFFT, ParGo                         │
│    ├── Ablation studies: no graph, fixed regions, no adaptive stop   │
│    └── Cross-dataset generalization                                  │
│                                                                      │
│  ★ Bridge Validation:                                                │
│    Experiment 2 (adaptive, thresh=1.0) ≈ Experiment 3 (fully-connected)│
│    — Consistent results prove framework compatibility                │
│                                                                      │
│  ★ Ceiling Comparison:                                               │
│    Oracle region selection ≥ VLM-guided ≥ Grid ≥ Random              │
│    — Establish upper bound for region extraction quality             │
└─────────────────────────────────────────────────────────────────────┘
```

### Experiment 1: Region Extraction

**Core Question:** Which region extraction method produces the most useful regions for visual reasoning?

**Variables:**
- Method: vlm_guided, grid, saliency
- Number of regions: 4, 8, 16

**Metrics:**
- Region coverage (IoU with ground truth objects)
- Reasoning accuracy using extracted regions
- Extraction time

**Expected Results:**
- VLM-guided > Grid > Saliency for complex scenes
- Optimal region count: 8-12 (diminishing returns beyond)

### Experiment 2: Graph Construction

**Core Question:** How should regions be connected in the graph for effective reasoning?

**Variables:**
- Method: adaptive, fully_connected, knn
- Edge threshold: 0.3, 0.5, 0.7 (for adaptive)

**Metrics:**
- Graph connectivity (average degree)
- Reasoning accuracy
- Inference time vs graph density

**Expected Results:**
- Adaptive with threshold 0.5 provides best balance
- Fully-connected is too slow for large region counts

### Experiment 3: End-to-End Reasoning

**Core Question:** Does GraphRegion outperform sequential approaches?

**Variables:**
- Method: GraphRegion (ours), VLM-R³ (baseline)
- Dataset: Visual7W, GQA

**Metrics:**
- Accuracy on multi-hop questions
- Inference time (total and per-question)
- Number of VLM forward passes

**Expected Results:**
- Comparable or better accuracy
- 2-3x faster inference
- Single pass vs O(N) passes

### Experiment 4: Baseline Comparison

**Core Question:** How does VSGR compare to all relevant baselines?

**Baselines:**
- VLM-R³: Sequential region reasoning
- CoFFT: Multi-step visual reasoning
- ParGo: Grid-based regions
- Full-image: Standard VLM without regions

**Ablation Studies:**
- No graph edges (independent regions)
- Fixed region count (no adaptive)
- No adaptive stopping (fixed steps)

**Metrics:**
- Comprehensive accuracy comparison
- Efficiency metrics
- Qualitative analysis

---

## 6.7 Experiment Documentation Standards

Each experiment's `.md` documentation must follow **overview-detail** structure:

### Overview Section
- Experiment overview table (name, core question, data, script)
- Cross-experiment group correspondence table
- Batch runner and Prompt locations

### Detail Section (per experiment)
- Experiment principles and design
- How to run (specific commands)
- Result storage path
- Results and analysis

### Documentation Template

```markdown
# Experiment: {Name}

## Overview

| Attribute           | Value                             |
|---------------------|-----------------------------------|
| **Name**            | {experiment_name}                 |
| **Core Question**   | {question}                        |
| **Hypothesis**      | {sub-hypothesis being tested}     |
| **Script Location** | `examples/preExp/{experiment}/`   |
| **Config Location** | `configs/preExp/{experiment}/`    |
| **Output Location** | `EXPERIMENT/preExp/{experiment}/` |

## Design

### Principles
{Core idea and rationale}

### Data Flow
```
[ASCII diagram]
```

### Variables
| Variable | Values   | Description   |
|----------|----------|---------------|
| {var1}   | {values} | {description} |

### Metrics
| Metric    | Description   | Expected         |
|-----------|---------------|------------------|
| {metric1} | {description} | {expected value} |

## How to Run

```bash
# Generate configs
python examples/preExp/{experiment}/generate_configs.py

# Run batch
python examples/preExp/{experiment}/run_batch.py --status
python examples/preExp/{experiment}/run_batch.py

# Visualize
python examples/preExp/plotting/plot_{metric}.py
```

## Results

### Summary Table
| Config    | Metric 1 | Metric 2 | ... |
|-----------|----------|----------|-----|
| {config1} | {value}  | {value}  | ... |

### Key Findings
1. {Finding 1}
2. {Finding 2}

### Analysis
{Detailed analysis of results}
```

---

## 6.8 Output Verification

| Check Item                                                                   | Verification Method                            |
|------------------------------------------------------------------------------|------------------------------------------------|
| Experiment groups arranged by progressive logic?                             | Check logic diagram in `docs/preExp/README.md` |
| Each experiment has `docs/preExp/{experiment}.md`?                           | `ls` to confirm correspondence                 |
| Each experiment implementation has `examples/preExp/{experiment}/README.md`? | `ls` to confirm correspondence                 |
| Config file naming follows convention?                                       | Check if batch runner regex can match          |
| At least one bridge point designed?                                          | Document clearly marks bridge experiment       |
| Clear ceiling/baseline comparison exists?                                    | Document clearly marks baseline experiment     |
| All new code passes Code Quality Gate?                                       | Check item by item                             |

---

## Next Phase

After Phase 6 completion, proceed to:

**Phase 7: Experiment Execution**
- Execute experiments in progressive order
- Record results and write reports
- Backfill results to documentation
