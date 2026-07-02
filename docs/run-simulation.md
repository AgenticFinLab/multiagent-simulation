# Run Simulation — How to Execute and Analyze Scenarios

## 1. Purpose

Run a simulation scenario from `examples/` end-to-end: execute the simulation,
analyze results, and inspect outputs. Each scenario supports up to four
**variants** that differ in how agents make decisions.

## 2. Prerequisites

- Python environment with `masim` installed (see project README)
- `.env` file at project root with required API keys (needed for LLM/Rag/RuleLLM variants)
- Working directory: project root (`multiagent-simulation/`)

## 3. The Four Variants

| Variant     | Decision Engine                      | API Keys Required | Description                                                                                                 |
|-------------|--------------------------------------|-------------------|-------------------------------------------------------------------------------------------------------------|
| **Rule**    | Hardcoded rules                      | No                | Agents follow deterministic mathematical rules. Fastest, no external dependencies. Baseline for comparison. |
| **LLM**     | Large Language Model                 | Yes               | Agents use LLM (e.g. DeepSeek, Doubao) to make decisions via structured prompts. Stochastic outputs.        |
| **Rag**     | LLM + Retrieval-Augmented Generation | Yes               | Same as LLM but agents retrieve domain knowledge documents before deciding. Tests knowledge grounding.      |
| **RuleLLM** | Hybrid Rule + LLM                    | Yes               | Some agents use rules, others use LLM. Tests interaction between deterministic and stochastic agents.       |

## 4. Running a Simulation

### 4.1 Single Variant

Each variant's runner script contains a `Usage` section in its file header
with the exact command to execute. To run a specific variant:

1. Navigate to `examples/{Scenario}/{Variant}/`
2. Open the `run_*.py` file
3. Copy the command from the `Usage:` docstring at the top of the file
4. Run it from the project root

**Example** — the header of `examples/AnchoringEffect/Rule/run_anchoringeffect.py`:

```python
"""AnchoringEffect Rule-Based Simulation Runner

Usage:
    python examples/AnchoringEffect/Rule/run_anchoringeffect.py \
        -c configs/AnchoringEffect/Rule/simulation.yml
"""
```

Every `run_*.py` across all scenarios and variants follows this same pattern.

### 4.2 What Happens During Execution

1. Config is loaded from `configs/{Scenario}/{Variant}/simulation.yml`
2. Ray cluster initializes and launches player actors
3. Topology connections are established between agents
4. Rounds execute sequentially (level-ordered parallel execution within each round)
5. Results persist to disk automatically after each round
6. Simulation supports **auto-resume** — if interrupted, re-running skips completed rounds

## 5. Running Analysis

After simulation completes, run the corresponding analysis script. Same
pattern as the runner — open `examples/{Scenario}/{Variant}/analysis.py` and
use the `Usage:` command in its file header.

The analysis pipeline:
1. Loads persisted simulation data from the record path
2. Computes all registered metrics (registry-driven)
3. Validates results against calibration targets defined in `analysis-bases.md`
4. Generates multi-panel visualization dashboards (PNG)
5. Emits `summary.json` with all computed metrics

## 6. Where Results Are Saved

All outputs go to `EXPERIMENT/{Scenario}/{Variant}/`:

```
EXPERIMENT/{Scenario}/{Variant}/
├── records/          # Raw simulation data (batched JSON, per-player turns)
├── communication/    # Inter-agent message logs
├── monitoring/       # Agent monitoring data
└── analysis/         # Analysis outputs
    ├── summary.json            # All computed metrics
    ├── 00_investor_orders.png  # Visualization panels
    ├── 01_price_dynamics.png
    ├── 02_volatility_returns.png
    ├── ...
    └── rag_stats.json          # (Rag variant only) retrieval diagnostics
```

## 7. Viewing Results

### 7.1 Summary Metrics

```bash
cat EXPERIMENT/AnchoringEffect/Rule/analysis/summary.json | python -m json.tool
```

### 7.2 Visualization Panels

Open the PNG files in the `analysis/` directory. Each panel focuses on one
aspect (price dynamics, volatility, agent volume, microstructure, etc.).

### 7.3 Streamlit Interface

For interactive exploration, launch the web UI:

```bash
./start_interface.command
```

Opens at `http://127.0.0.1:8501`.

## 8. Configuration Reference

Each variant's configuration lives in `configs/{Scenario}/{Variant}/simulation.yml`:

| Field                        | Purpose                                       |
|------------------------------|-----------------------------------------------|
| `setting.total_rounds`       | Number of simulation rounds                   |
| `setting.record_path`        | Where raw results are persisted               |
| `players`                    | Agent definitions (includes `players.yml`)    |
| `topology`                   | Communication graph (includes `topology.yml`) |
| `communication.storage_path` | Where message logs are saved                  |
| `ray.object_store_memory`    | Ray memory allocation                         |

## 9. Troubleshooting

| Problem                        | Solution                                                     |
|--------------------------------|--------------------------------------------------------------|
| `ModuleNotFoundError: masim`   | Activate the correct conda environment                       |
| LLM variant hangs              | Check `.env` API keys are valid                              |
| Ray out of memory              | Increase `ray.object_store_memory` in config                 |
| Partial run (interrupted)      | Re-run the same command — auto-resume skips completed rounds |
| Analysis fails with empty data | Ensure simulation completed at least a few rounds first      |
