# Phase 7: Experiment Execution

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 6 with experiment design
> **Output:** `EXPERIMENT/` results, `.md` reports, visualizations

---

## Overview

Execute experiments in the progressive order designed in Phase 6, record results, and write experiment reports.

This phase transforms designed experiments into actual data and insights.

---

## 7.1 Execution Principles

| Principle                 | Description                                                                                      |
|---------------------------|--------------------------------------------------------------------------------------------------|
| **Simple Before Complex** | Run baseline first, confirm infrastructure is correct, then run complex experiments              |
| **Incremental Storage**   | Use storage solution supporting resume — avoid losing existing data on mid-run crash             |
| **Config Copy**           | Each experiment automatically copies config file to output directory — ensures reproducibility   |
| **Batch Runner**          | Write scripts for auto-discovering configs + sequential execution — avoid manual one-by-one runs |
| **State Tracking**        | Support `--status` to view completed/pending, `--force` to force re-run                          |

---

## 7.2 Execution Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Infrastructure Verification                            │
│  - Run uTEST to ensure modules work                             │
│  - Run baseline experiment to confirm setup                     │
│  - Verify GPU, memory, disk space                               │
└─────────────────┬───────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Config Generation                                      │
│  - Run generate_configs.py for each experiment group            │
│  - Verify config files created correctly                        │
│  - Check naming convention compliance                           │
└─────────────────┬───────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Batch Execution                                        │
│  - Start with simplest experiment (Experiment 1)                │
│  - Use run_batch.py with --status to track progress             │
│  - Monitor for errors, record in Progress-record.md             │
└─────────────────┬───────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Result Verification                                    │
│  - Check summary.json for each run                              │
│  - Verify config file copied to output                          │
│  - Run visualization scripts                                    │
└─────────────────┬───────────────────────────────���──────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Documentation Backfill                                 │
│  - Update docs/preExp/{experiment}.md with results              │
│  - Add summary tables and key findings                          │
│  - Record unexpected observations                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7.3 Data Storage Standards

```
EXPERIMENT/{exp_group}/{experiment}/{run_name}/
├── summary.json            # Aggregated statistics
├── *_block_*.json          # Per-sample detailed data
└── *.yml                   # Config file copy
```

### summary.json Format

```json
{
  "total_samples": 100,
  "completed_samples": 100,
  "accuracy": 0.72,
  "f1_score": 0.70,
  "exact_match": 0.68,
  "avg_inference_time": 2.35,
  "total_time": 235.0,
  "config_file": "configs/preExp/region_extraction/region_vlm_guided_num8_llava7b.yml",
  "timestamp": "2024-01-15T10:30:00Z",
  "experiment_name": "region_vlm_guided_num8",
  "model_name": "llava-hf/llava-1.5-7b-hf",
  "dataset": "Visual7W"
}
```

### Per-Sample Data Format

```json
{
  "sample_id": "visual7w_001",
  "question": "What is left of the dog?",
  "image_path": "EXPERIMENT/data/visual7w/images/001.jpg",
  "ground_truth": "tree",
  "prediction": "tree",
  "correct": true,
  "inference_time": 2.1,
  "num_regions": 8,
  "reasoning_steps": [
    {"step": 1, "action": "locate", "target": "dog", "success": true},
    {"step": 2, "action": "relate", "relation": "left", "result": "tree"}
  ]
}
```

---

## 7.4 Batch Runner Implementation

### Batch Runner Features

```python
# examples/preExp/run_batch.py
"""Batch runner with state tracking and resume support."""

import argparse
import json
from pathlib import Path

class BatchRunner:
    def __init__(self, config_dir: str, output_dir: str):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.state_file = self.output_dir / "batch_state.json"
    
    def discover_configs(self) -> list:
        """Auto-discover config files matching naming convention."""
        return sorted(self.config_dir.glob("*.yml"))
    
    def load_state(self) -> dict:
        """Load batch execution state."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"completed": [], "failed": [], "pending": []}
    
    def save_state(self, state: dict):
        """Save batch execution state."""
        self.state_file.write_text(json.dumps(state, indent=2))
    
    def status(self):
        """Print current execution status."""
        configs = self.discover_configs()
        state = self.load_state()
        
        print(f"Total configs: {len(configs)}")
        print(f"Completed: {len(state['completed'])}")
        print(f"Failed: {len(state['failed'])}")
        print(f"Pending: {len(configs) - len(state['completed']) - len(state['failed'])}")
        
        print("\nPending configs:")
        for config in configs:
            if config.name not in state['completed'] and config.name not in state['failed']:
                print(f"  - {config.name}")
    
    def run(self, force: bool = False):
        """Run all pending experiments."""
        configs = self.discover_configs()
        state = self.load_state()
        
        for config in configs:
            if config.name in state['completed'] and not force:
                print(f"Skipping {config.name} (completed)")
                continue
            
            print(f"Running {config.name}...")
            try:
                self._run_single(config)
                state['completed'].append(config.name)
                if config.name in state['failed']:
                    state['failed'].remove(config.name)
            except Exception as e:
                print(f"Failed: {e}")
                if config.name not in state['failed']:
                    state['failed'].append(config.name)
            
            self.save_state(state)
    
    def _run_single(self, config_path: Path):
        """Run single experiment."""
        # Implementation specific to experiment
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", default="configs/preExp/region_extraction")
    parser.add_argument("--output-dir", default="EXPERIMENT/preExp/region_extraction")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--force", action="store_true", help="Force re-run")
    args = parser.parse_args()
    
    runner = BatchRunner(args.config_dir, args.output_dir)
    
    if args.status:
        runner.status()
    else:
        runner.run(force=args.force)
```

---

## 7.5 Result Visualization

Visualization scripts should be centrally managed:

```
examples/preExp/plotting/
├── plot_accuracy_comparison.py    # Compare accuracy across methods
├── plot_inference_time.py         # Inference time analysis
├── plot_region_coverage.py        # Region extraction quality
└── plot_ablation.py               # Ablation study results
```

### Example: Accuracy Comparison Plot

```python
# examples/preExp/plotting/plot_accuracy_comparison.py
"""Plot accuracy comparison across methods."""

import json
import matplotlib.pyplot as plt
from pathlib import Path

def load_results(exp_group: str, experiment: str):
    """Load all summary.json files for an experiment."""
    results = []
    exp_dir = Path(f"EXPERIMENT/{exp_group}/{experiment}")
    
    for run_dir in exp_dir.iterdir():
        summary_file = run_dir / "summary.json"
        if summary_file.exists():
            results.append(json.loads(summary_file.read_text()))
    
    return results

def plot_region_extraction_accuracy():
    """Plot accuracy for different region extraction methods."""
    results = load_results("preExp", "region_extraction")
    
    # Group by method
    methods = {}
    for r in results:
        method = r["experiment_name"].split("_")[1]  # region_METHOD_numX
        if method not in methods:
            methods[method] = []
        methods[method].append((r["num_regions"], r["accuracy"]))
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for method, data in methods.items():
        data.sort(key=lambda x: x[0])
        nums, accs = zip(*data)
        ax.plot(nums, accs, marker='o', label=method)
    
    ax.set_xlabel("Number of Regions")
    ax.set_ylabel("Accuracy")
    ax.set_title("Region Extraction Method Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.savefig("EXPERIMENT/preExp/plots/region_accuracy.png", dpi=150)
    print("Saved to EXPERIMENT/preExp/plots/region_accuracy.png")

if __name__ == "__main__":
    Path("EXPERIMENT/preExp/plots").mkdir(parents=True, exist_ok=True)
    plot_region_extraction_accuracy()
```

---

## 7.6 Experiment Result Recording

After experiment completion, immediately backfill results to corresponding `.md` documentation:

### Results Backfill Template

```markdown
## Results

### Execution Summary
- **Date:** 2024-01-15
- **Total Runtime:** 4.5 hours
- **Configs Run:** 12
- **Successful:** 12
- **Failed:** 0

### Summary Table

| Method     | Num Regions | Accuracy | Inference Time (s) | Config                |
|------------|-------------|----------|--------------------|-----------------------|
| vlm_guided | 4           | 0.62     | 1.8                | [config](configs/...) |
| vlm_guided | 8           | 0.71     | 2.3                | [config](configs/...) |
| vlm_guided | 16          | 0.73     | 3.1                | [config](configs/...) |
| grid       | 4           | 0.58     | 1.5                | [config](configs/...) |
| grid       | 8           | 0.65     | 1.9                | [config](configs/...) |
| grid       | 16          | 0.66     | 2.4                | [config](configs/...) |

### Key Findings

1. **VLM-guided extraction outperforms grid-based** by 5-8% across all region counts
2. **Diminishing returns beyond 12 regions** — accuracy gain from 8→16 is only 2%
3. **Inference time scales linearly** with region count for both methods

### Unexpected Observations

- Some grid configurations with 16 regions had lower accuracy than 8 regions
  - Hypothesis: Too many regions introduce noise
  - Action: Investigate in follow-up experiment

### Visualizations

![Accuracy Comparison](EXPERIMENT/preExp/plots/region_accuracy.png)

### Raw Data

All results available in:
- `EXPERIMENT/preExp/region_extraction/{run_name}/summary.json`
- `EXPERIMENT/preExp/region_extraction/{run_name}/*_block_*.json`
```

---

## 7.7 Output Verification

| Check Item                                                     | Verification Method                                       |
|----------------------------------------------------------------|-----------------------------------------------------------|
| Baseline experiment runs successfully first?                   | Confirm baseline summary.json exists                      |
| All experiments' summary.json have consistent field structure? | Sample-compare multiple summary.json files                |
| Each experiment output directory has config file copy?         | `ls *.yml` to confirm                                     |
| Incremental storage works correctly? (can resume)              | Interrupt then restart, confirm existing data not lost    |
| Experiment results backfilled to `docs/` docs?                 | Open corresponding .md file, confirm results table exists |
| Visualization scripts produced key charts?                     | Check for saved images or notebooks                       |

---

## 7.8 Common Issues and Solutions

| Issue                            | Cause                                 | Solution                                                            |
|----------------------------------|---------------------------------------|---------------------------------------------------------------------|
| Out of memory                    | Batch size too large or model too big | Reduce batch size, use gradient checkpointing, or use smaller model |
| Experiment crashes mid-run       | GPU error, power issue                | Use incremental storage, resume with `--force` for failed only      |
| Results inconsistent across runs | Different random seeds                | Fix seed in config, verify seed is being used                       |
| Config file not copied           | Missing copy step in runner           | Add explicit config copy to output directory                        |
| Visualization fails              | Missing dependencies                  | Add matplotlib, seaborn to requirements.txt                         |

---

## Next Phase

After Phase 7 completion, proceed to:

**Phase 8: Cross-Experiment Analysis**
- Horizontal comparison across all experiment results
- Verify bridge point consistency
- Extract final conclusions
