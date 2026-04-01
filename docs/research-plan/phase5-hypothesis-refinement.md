# Phase 5: Hypothesis Refinement

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase with Iteration
> **Prerequisite:** Completed Phase 3-4 with literature survey and source analysis
> **Output:** Updated hypothesis, code architecture, config templates

---

## Overview

Based on Phase 3 (literature) and Phase 4 (source code) analysis, **trace back and update**:
1. Precise formulation of research hypothesis
2. Code architecture adaptation (add new modules, update base classes)
3. Config template refinement

> **Key insight: Phase 5 is not a one-time task, but continuous iteration.** Each time you analyze a new paper, discover a new engineering issue, or complete an experiment with new findings, it may trigger trace-back updates. Phases 3-4-5 form a feedback loop.

---

## 5.1 Update Dimensions

```
Literature/Source Code Analysis Results
  ├─► Hypothesis Update: More precise falsifiable hypothesis
  ├─► Code Update: Add/modify modules to support verification experiments
  │   ├── {package}/{core_module}/  — Core research capability implementation
  │   ├── {package}/utils/          — Domain utility functions
  │   └── {package}/evaluate/       — Evaluation framework
  └─► Config Update: TEMPLATE adds new config blocks
```

> **Each trace-back should update all three dimensions simultaneously** — Only updating hypothesis without code = wishful thinking; Only updating code without config = experiments won't run; Only updating code without hypothesis = losing research direction.

---

## 5.2 Hypothesis Refinement Example

### Initial Hypothesis (Phase 0)

```
Visual reasoning with region relationship graphs via multi-agent reinforcement
learning outperforms sequential one-step-one-region approaches while maintaining
full image context.
```

### Refined Hypothesis (After Phase 3-4)

```
Visual reasoning with adaptive region relationship graphs (GraphRegion) achieves:
1. Higher accuracy than sequential region approaches (VLM-R³) on cross-region
   reasoning tasks (+5-10% on multi-hop visual questions)
2. Lower inference latency than multi-iteration methods (CoFFT) through
   single-pass parallel processing (2-3x speedup)
3. Better region coverage than uniform grid methods (ParGo) through
   VLM-guided adaptive extraction

while maintaining full image context and requiring no task-specific training.
```

### What Changed?

| Aspect             | Initial               | Refined                                |
|--------------------|-----------------------|----------------------------------------|
| Specificity        | General "outperforms" | Specific metrics (+5-10%, 2-3x)        |
| Comparison targets | Vague                 | Named baselines (VLM-R³, CoFFT, ParGo) |
| Claims             | Single claim          | Three distinct claims with mechanisms  |
| Falsifiability     | Hard to disprove      | Clear thresholds for failure           |

---

## 5.3 Code Updates Based on Analysis

### Example: Trace-back Update Table

| Analysis Finding                                           | Trace-back Update                                                                     |
|------------------------------------------------------------|---------------------------------------------------------------------------------------|
| VLM-R³ loads full model each step, no KV sharing           | Add `vsgr/models/base.py` with efficient VLM wrapper supporting single-pass inference |
| CoFFT uses fixed iteration count                           | Add adaptive stopping to `gr_reason/graphregion_model.py`                             |
| ParGo uniform grid misses small objects                    | Implement VLM-guided region extraction in `gr_reason/region_extractor.py`             |
| No existing implementation of graph-based visual reasoning | Create `gr_reason/graph_constructor.py` and `gr_reason/multi_agent_reasoning.py`      |
| Need to compare against multiple baselines                 | Add `evaluate/baseline_comparison.py` with unified evaluation interface               |

### Module Updates Checklist

After identifying findings, update code:

```markdown
## Code Updates from Phase 3-4 Findings

### New Modules Added
- [ ] `vsgr/gr_reason/region_extractor.py` — VLM-guided adaptive extraction
- [ ] `vsgr/gr_reason/graph_constructor.py` — Build region relationship graphs
- [ ] `vsgr/gr_reason/multi_agent_reasoning.py` — Multi-agent RL reasoning
- [ ] `vsgr/evaluate/baseline_comparison.py` — Unified baseline evaluation

### Existing Modules Modified
- [ ] `vsgr/models/base.py` — Add efficient single-pass inference support
- [ ] `vsgr/gr_reason/base.py` — Add adaptive stopping dataclass
- [ ] `vsgr/utils/config_loader.py` — Add new config sections

### New uTESTs Added
- [ ] `examples/uTEST/test_region_extraction.py`
- [ ] `examples/uTEST/test_graph_construction.py`
- [ ] `examples/uTEST/test_multi_agent_reasoning.py`
```

---

## 5.4 Config Template Updates

Add new config blocks based on findings:

```yaml
# configs/TEMPLATE/vsgr_experiment.yml

# BLOCK 4: Graph Region Configuration (UPDATED)
graph_region:
  # NEW: Region extraction strategies
  region_extraction:
    method: "vlm_guided"  # Options: vlm_guided, grid, saliency
    num_regions: 8
    min_region_size: 0.05
    adaptive: true        # NEW: Enable adaptive region count
    max_regions: 16       # NEW: Upper bound for adaptive
  
  # NEW: Graph construction strategies
  graph_construction:
    method: "adaptive"    # Options: adaptive, fully_connected, knn
    edge_threshold: 0.5
    relation_types: ["spatial", "semantic"]
    self_loops: false     # NEW: Whether to include self-connections
  
  # NEW: Multi-agent reasoning configuration
  reasoning:
    method: "multi_agent_rl"
    num_agents: 3
    max_steps: 10
    adaptive_stopping: true    # NEW: From CoFFT analysis
    confidence_threshold: 0.8  # NEW: Stopping criterion
    
    # NEW: Agent configuration
    agent_config:
      verifier:
        role: "verify_region_relevance"
        can_terminate: false
      navigator:
        role: "navigate_relationships"
        can_terminate: false
      reasoner:
        role: "synthesize_answer"
        can_terminate: true     # NEW: Only reasoner can terminate

# BLOCK 8: Experiment-specific (NEW options)
experiment:
  name: "adaptive_graph_region"
  description: "GraphRegion with adaptive stopping"
  
  # NEW: Baseline comparison settings
  baselines:
    - name: "vlm_r3"
      enabled: true
    - name: "cofft"
      enabled: true
    - name: "pargo"
      enabled: true
  
  # NEW: Ablation studies
  ablations:
    - "no_graph_edges"
    - "fixed_regions"
    - "no_adaptive_stopping"
```

---

## 5.5 Positioning Against Baselines

After refinement, clearly articulate how your approach differs from baselines:

```markdown
## VSGR Positioning

### vs VLM-R³ (Sequential Region Reasoning)
| Aspect                 | VLM-R³                    | VSGR                         |
|------------------------|---------------------------|------------------------------|
| Region processing      | Sequential, one at a time | Parallel, graph-structured   |
| Inference passes       | O(N) for N regions        | O(1) single pass             |
| Cross-region reasoning | Implicit through state    | Explicit through graph edges |
| Context maintenance    | Accumulated state         | Full graph structure         |

### vs CoFFT (Multi-Step Visual Reasoning)
| Aspect             | CoFFT            | VSGR                     |
|--------------------|------------------|--------------------------|
| Iteration count    | Fixed            | Adaptive                 |
| Stopping criterion | Max steps        | Confidence threshold     |
| Visual attention   | Sequential focus | Parallel graph attention |

### vs ParGo (Grid-Based Regions)
| Aspect                | ParGo          | VSGR                 |
|-----------------------|----------------|----------------------|
| Region layout         | Uniform grid   | Adaptive to content  |
| Region selection      | All grid cells | VLM-guided selection |
| Relationship modeling | Grid neighbors | Learned graph edges  |
```

---

## 5.6 Output Verification

| Check Item                                                        | Verification Method                               |
|-------------------------------------------------------------------|---------------------------------------------------|
| Phase 0 hypothesis document updated to more precise version?      | Compare before/after, confirm substantive changes |
| Which modules/classes/functions added based on analysis findings? | `git diff` or compare directory structure         |
| Does new code pass Code Quality Gate (Phase 2.9)?                 | Check item by item                                |
| Do new modules have corresponding `docs/{module}.md`?             | Check one-to-one correspondence                   |
| Has `configs/TEMPLATE/` added new config blocks?                  | Open YAML to confirm new fields                   |
| Is "Analysis Finding → Trace-back Update" table recorded?         | Table has ≥2 rows of correspondence               |
| Do new uTESTs cover new functionality?                            | `ls examples/uTEST/` to confirm new tests added   |

---

## 5.7 Iteration Trigger Conditions

Revisit Phase 5 when:

| Trigger                                  | Action                                    |
|------------------------------------------|-------------------------------------------|
| New paper analyzed in Phase 3            | Check if hypothesis needs refinement      |
| New source code analyzed in Phase 4      | Check if code architecture needs updates  |
| uTEST reveals unexpected behavior        | Update hypothesis to account for findings |
| Experiment results contradict hypothesis | Refine hypothesis or check implementation |
| Code review suggests better approach     | Update architecture and config            |

---

## Next Phase

After Phase 5 completion, proceed to:

**Phase 6: Experiment Design**
- Design progressive preliminary experiments
- Each experiment verifies one clear sub-hypothesis
- Establish bridge points for cross-experiment validation
