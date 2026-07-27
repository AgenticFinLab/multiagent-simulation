# Evaluation-First Architecture: `masim/evaluation/` as the Single Source

## Purpose & Scope

`masim/evaluation/` is the **唯一且强制性的评估代码来源** — the sole, mandatory source for ALL simulation evaluation logic in the MASim framework. This is not a convenience library; it is an architectural boundary that all implementation must respect.

### What `masim/evaluation/` Contains

The module stores, defines, and exposes **every piece** of reusable evaluation-related content:

- **Metric computation functions** — time-series statistics, behavioral finance measures, microstructure analytics, agent-level accounting, and all registry-compatible `m_*` functions (currently 36 standard metrics)
- **Data extraction & transformation** — the standard data contract, `load_data()`, `aligned_prices_and_fundamentals()`, `payload_buy_sell()`, config extraction helpers
- **Registry infrastructure** — `Metric`, `MetricsRegistry`, `MetricUnavailable` type system enabling declarative metric catalogues
- **Validation logic** — rule-based calibration checks (`validate_asset_bubble()`, etc.) and LLM-based qualitative assessment (`LLMValidator`)
- **Visualization** — all reusable matplotlib charting functions for evaluation output
- **Pipeline orchestration** — `run_standard_analysis()`, `analyze_standard_scenario()`
- **Design patterns & contracts** — function signatures (`fn(data, config) -> dict`), naming conventions (`m_` prefix), error handling (`MetricUnavailable`)

### Why This Architecture Exists

Without centralized evaluation code, the project degenerates into:
- **Duplicated logic** with subtle inconsistencies (the same metric computed differently across scenarios)
- **Untraceable bugs** (a fix in one copy never propagates to others)
- **Knowledge loss** (no one can discover what's already implemented)
- **Metric drift** (conceptually identical measures yielding different values)

The evaluation-first architecture eliminates these by enforcing: one implementation, one definition, one authoritative location.

### The Hard Rule (Non-Negotiable)

> **Every reusable evaluation function, helper, constant, and design pattern MUST live in `masim/evaluation/`.**
>
> **Every consumer — scenario `metrics.py`, variant `analysis.py`, notebooks, scripts — MUST import from `masim/evaluation/`. No exceptions.**
>
> **No scenario, variant, or external code may reimplement, copy, or locally redefine any evaluation function that exists here or could reasonably be generalized to exist here.**

Violations are architectural defects. They are corrected immediately upon discovery, not deferred.

### Canonical Detailed Reference

> **`masim/evaluation/README.md`** is the ground-truth document for the module's current state — directory layout, metric counts, data contracts, function signatures, placement decision flowcharts, compliance checklists. Always consult it for up-to-date organizational details. This skills document provides implementation guidance and enforcement rules; the README provides the authoritative specification.

---

## The Rule: Evaluation-First Design

### Core Principle

> When an `analysis.py` script needs a function for loading data, computing a metric, validating results, or generating a visualization, it MUST:
>
> 1. **First check** whether the function already exists in `masim/evaluation/`.
> 2. **If it exists** → import and use it directly.
> 3. **If it does NOT exist but is reusable** → implement it in the appropriate `masim/evaluation/` submodule first, then import it in the analysis script.
> 4. **If it is truly scenario-specific** (not reusable by any other scenario) → implement it locally in the analysis script, but with a comment explaining why it cannot be generalized.

### Where Code Lives

| Category | Location | Examples |
|----------|----------|----------|
| Time-series metrics | `masim/evaluation/finance/timeseries.py` | autocorrelation, rolling volatility, returns, Sharpe, drawdown, VaR, bootstrap CI, Ljung-Box, ADF |
| Behavioral metrics | `masim/evaluation/finance/behavioral.py` | herding CV, directional agreement, cascade measure, agent PnL/wealth/Sharpe, Gini coefficient |
| Volatility metrics | `masim/evaluation/finance/volatility.py` | GARCH signature, volatility persistence, regime detection |
| Microstructure metrics | `masim/evaluation/finance/microstructure.py` | order imbalance, signed volume autocorr, HHI concentration, strategy correlation, information share |
| Visualization | `masim/evaluation/finance/visualization.py` | all reusable plot functions (price dynamics, returns analysis, volatility panels, etc.) |
| Scenario validation | `masim/evaluation/finance/validation.py` | `validate_asset_bubble()`, `validate_short_squeeze()`, etc. |
| LLM-based validation | `masim/evaluation/finance/validation_llm.py` | `LLMValidator`, `validate_with_llm()` |
| Metric registry types | `masim/evaluation/registry.py` | `Metric`, `MetricsRegistry`, `MetricUnavailable` |
| Data loading & helpers | `masim/evaluation/data_loader.py` | `load_data()`, `aligned_prices_and_fundamentals()`, `payload_buy_sell()`, `per_agent_initial_position()` |
| Analysis pipeline orchestration | `masim/evaluation/pipeline.py` | `run_standard_analysis()`, `analyze_standard_scenario()` |

### What Stays in `examples/{Scenario}/{Variant}/analysis.py`

Only truly scenario-specific logic that cannot be reused:

- Scenario-specific validation thresholds and criteria weights (though the validation *framework* is in `masim/evaluation/`)
- Scenario-specific composite scores that combine multiple generic metrics in a unique way
- Scenario-specific plot arrangements (though individual plot *components* are from `masim/evaluation/`)

---

## Module Structure: `masim/evaluation/`

```
masim/evaluation/
├── README.md                      # Full organizational principles & guidelines
├── __init__.py                    # Top-level exports (re-exports domain-agnostic utilities)
├── registry.py                    # Metric, MetricsRegistry, MetricUnavailable
├── data_loader.py                 # batch_to_rounds, load_data, aligned_prices_and_fundamentals, etc.
├── pipeline.py                    # run_standard_analysis, analyze_standard_scenario
│
├── finance/                       # Domain: Financial Market Simulation
│   ├── __init__.py                # STANDARD_METRICS (36) + register_standard_metrics()
│   ├── timeseries.py              # Time-series statistics + 23 registry metrics
│   ├── behavioral.py              # Behavioral finance / agent-level + 8 registry metrics
│   ├── volatility.py              # Volatility modeling (GARCH, regimes)
│   ├── microstructure.py          # Market microstructure + 5 registry metrics
│   ├── visualization.py           # All reusable matplotlib plot functions
│   ├── validation.py              # Rule-based scenario validation
│   └── validation_llm.py          # LLM-based validation with theory prompts
│
└── {future_domain}/               # Future: social, transport, supply_chain, ...
    ├── __init__.py
    └── ...
```

---

## Organizational Principles

### Goals

The `masim/evaluation/` module pursues three goals, in priority order:

1. **Method-category cohesion** — A file owns ONE coherent analytical method family. All functions in that file share the same theoretical grounding and similar input/output signatures. A developer looking for "anything related to time-series statistics" opens one file and finds everything there.
2. **Zero local reimplementation** — If a reusable function exists in evaluation/, no scenario rewrites it locally. If it does not exist yet, it is added to the correct method-category file before being used.
3. **Discoverability by domain context** — A developer writing a finance scenario need only know `masim.evaluation.finance.{method_category}` to find any function. No "catch-all" or "misc" files exist; every function has exactly one correct home.

### The absolute prohibition

**No "umbrella" files.** A single file that aggregates functions from multiple unrelated method categories (e.g., a hypothetical `standard_metrics.py` containing both volatility functions and microstructure functions) violates goal #1 and MUST NOT exist. Each function lives in its method-category file — even if that function is a registry-compatible metric (`fn(data, config) -> dict`). The fact that a function can be registered into a `MetricsRegistry` does not make it a different *kind* of function; it still belongs to the method category that defines its analytical theory.

### Two-level hierarchy: Domain → Method Category

The directory structure follows a **domain-first** organization:

- **Level 0 (top-level)**: Domain-agnostic infrastructure — type systems (`registry.py`), data loading interfaces (`data_loader.py`), pipeline orchestration (`pipeline.py`). These serve ALL domains equally.
- **Level 1 (domain subdirectory)**: One subdirectory per simulation domain (currently only `finance/`). A domain groups all evaluation code that shares domain-specific semantics (e.g., "price", "bid", "portfolio" are finance concepts).
- **Level 2 (files within domain)**: Files organized by **academic theory family / analytical method category**. Each file covers one coherent area of the domain's analytical toolkit. This includes both low-level computation functions (`calculate_returns`) AND registry-compatible metric functions (`m_return_skewness`) — they share the same home because they share the same theory.

### Why domain-first (not method-category-first)

The alternative — organizing as `evaluation/timeseries/finance.py`, `evaluation/behavioral/finance.py` — was considered and rejected because:

1. **Import ergonomics**: A developer writing `analysis.py` for a finance scenario thinks "I need a behavioral metric" → `masim.evaluation.finance.behavioral`. The domain is already known from context; the method category is the lookup key.
2. **Semantic coupling within a domain**: Finance metrics share data structure assumptions (price series, order books, agent portfolios). Mixing finance and transport time-series functions in one file conflates unrelated semantics.
3. **Independent evolution**: A new domain (social dynamics, epidemics) can be added as a self-contained directory without touching existing finance code.
4. **Cross-domain truly-generic utilities** (e.g., autocorrelation, rolling window) belong at the top level or as shared helpers — they are rare in practice because even "generic" statistical operations carry domain-specific parameter semantics.

### Module Responsibility Boundaries

Each file within `finance/` has a precise responsibility boundary:

| Module | Responsibility | Belongs here | Does NOT belong here |
|--------|---------------|-------------|---------------------|
| `timeseries.py` | Pure statistical properties of price/return series. No theoretical stance — just computation. Hosts low-level functions (`calculate_returns`) and 23 registry metrics (`m_return_skewness`, `m_max_drawdown_pct`, `m_value_at_risk_95`, etc.). Categories: price_dynamics (12), information_efficiency (5), statistical_inference (4), tail_risk (2). | autocorrelation, rolling volatility, returns, Sharpe ratio, max drawdown, skewness, kurtosis, variance ratio, VaR, CVaR, bootstrap CI, Ljung-Box, ADF, deviation statistics, half-life fitting, price efficiency ratio, regime transition lag | Anything requiring agent-level data or implying a behavioral theory |
| `behavioral.py` | Metrics grounded in behavioral finance theory (Kahneman, Shiller, Odean, Bikhchandani) AND agent-level accounting/inequality. Hosts herding computation functions plus 8 registry metrics (category: agent_behaviour). | herding CV, directional agreement, cascade measure, investor correlation, agent action frequency, silent agent detection, agent volume, agent net position, agent PnL, agent Sharpe, agent wealth, Gini coefficient | Pure price-level statistics without agent data |
| `volatility.py` | Volatility modeling and clustering (Engle/Bollerslev tradition). Second-moment dynamics. | GARCH signature, volatility persistence, return clustering, regime detection | First-moment metrics (returns, prices), agent-level measures |
| `microstructure.py` | Market microstructure theory (Kyle, Glosten-Milgrom, Amihud). Order-flow, liquidity, price impact. Hosts computation functions plus 5 registry metrics (category: microstructure). | order imbalance, signed volume autocorrelation, HHI volume concentration, strategy correlation matrix, information share by strategy, volume metrics, agent impact, bubble magnitude, net demand, liquidity | Behavioral interpretations of trading patterns |
| `visualization.py` | All reusable matplotlib plot functions for the finance domain. Separated from metrics because it has a distinct dependency (matplotlib) and serves all other modules. | plot_price_dynamics, plot_returns_analysis, plot_multi_panel_summary, create_figure, save_figure | Scenario-specific plot arrangements (those stay in scenario analysis.py) |
| `validation.py` | Rule-based calibration target checking. Each validator takes computed metrics and returns pass/fail against literature-established ranges. | validate_asset_bubble, validate_herd_effect, ValidationResult | Metric computation itself (that belongs in the metric modules) |
| `validation_llm.py` | LLM-based validation using financial theory prompts. Complements rule-based validation with qualitative reasoning. | LLMValidator, validate_with_llm, get_theory_prompt | Rule-based threshold checks |

### Placing a New Function: Decision Flowchart

When implementing a new evaluation function, use this flowchart to determine its home:

```
┌─────────────────────────────────────────────────────┐
│ What DOMAIN does this function serve?               │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Does masim/evaluation/{domain}/ exist?              │
│  • Yes → proceed to method-category placement       │
│  • No  → create the domain subdirectory first       │
│           (with __init__.py re-exporting all)        │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ What THEORY FAMILY does this function belong to?    │
│                                                     │
│  Q1: Does it compute a pure statistical property    │
│      of a time series (no agent data, no theory)?   │
│      → timeseries.py                                │
│                                                     │
│  Q2: Does it measure a behavioral pattern rooted    │
│      in behavioral finance / psychology?            │
│      → behavioral.py                                │
│                                                     │
│  Q3: Does it characterize volatility dynamics       │
│      (2nd-moment structure, clustering, regimes)?   │
│      → volatility.py                                │
│                                                     │
│  Q4: Does it analyze order-flow mechanics,          │
│      liquidity, or price impact at the market       │
│      mechanism level?                               │
│      → microstructure.py                            │
│                                                     │
│  Q5: Does it produce a visualization?               │
│      → visualization.py                             │
│                                                     │
│  Q6: Does it CHECK results against calibration      │
│      targets (not compute metrics)?                 │
│      → validation.py or validation_llm.py           │
│                                                     │
│  Q7: None of the above fit?                         │
│      → Either the function is truly scenario-       │
│        specific (keep local), or a new module is    │
│        needed (create it with a clear theory-family │
│        name and document its boundary here).        │
└─────────────────────────────────────────────────────┘
```

### When to Create a New Module

A new `.py` file in `finance/` is warranted when:

1. There are ≥3 related functions that don't fit any existing module boundary.
2. They share a coherent academic theory family (e.g., information theory, network analysis, agent learning).
3. The existing modules would become semantically diluted by absorbing them.

When creating a new module: add it to this document's Module Structure tree, update the responsibility boundary table, and re-export through `finance/__init__.py`.

### When a Module Grows Too Large

If a single file exceeds ~800 lines or ~20 functions, consider splitting it into a subdirectory:

```
finance/validation/           # replaces finance/validation.py
├── __init__.py               # re-exports everything (preserves import paths)
├── bubble.py                 # validate_asset_bubble, validate_tulip_mania, ...
├── behavioral.py             # validate_disposition_effect, validate_herd_effect, ...
└── crisis.py                 # validate_flash_crash, validate_market_crash, ...
```

The import path `from masim.evaluation.finance.validation import validate_asset_bubble` remains unchanged — the `__init__.py` handles re-export. This ensures zero breaking changes for existing scenarios.

---

## Mandatory Import Patterns

### Pattern 1: Scenario analysis scripts importing metrics

```python
from masim.evaluation.finance.timeseries import (
    calculate_autocorrelation,
    calculate_rolling_volatility,
    calculate_price_deviation,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
)
from masim.evaluation.finance.behavioral import (
    calculate_bid_convergence_cv,
    calculate_directional_agreement,
    calculate_cascade_measure,
)
from masim.evaluation.finance.volatility import (
    calculate_volatility_persistence,
    calculate_garch_signature,
)
from masim.evaluation.finance.visualization import (
    plot_price_dynamics,
    plot_returns_analysis,
    plot_volatility_analysis,
    create_figure,
    save_figure,
)
from masim.evaluation.finance.validation import validate_asset_bubble
```

### Pattern 2: Using the metric registry

```python
from masim.evaluation.registry import Metric, MetricsRegistry, MetricUnavailable

REGISTRY = MetricsRegistry()
REGISTRY.register(Metric(
    name="mad_pct",
    category="price_dynamics",
    fn=compute_mad_pct,
    output_keys=("mad_pct",),
    references=("Shiller 2000",),
    description="Mean absolute deviation from fundamental, as percentage",
))
```

### Pattern 3: Data loading

```python
from masim.evaluation.data_loader import _batch_to_rounds, _load_data
from masim.utils import load_config, load_results
```

### Pattern 4: Cross-variant analysis reuse within a scenario

```python
# Within the same scenario, LLM/analysis.py imports from Rule/analysis.py
# ONLY for scenario-specific orchestration functions (not generic utilities)
from examples.{Scenario}.Rule.analysis import (
    analyze_{scenario},          # scenario-specific orchestration — OK
    _validate_{scenario},        # scenario-specific validation criteria — OK
)

# Generic utilities always come from masim.evaluation
from masim.evaluation.finance.timeseries import calculate_returns
```

---

## Decision Flowchart for Implementers

When you need a function in `analysis.py`:

```
┌─────────────────────────────────────────────────┐
│ I need function F in my analysis script          │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│ Does F already exist in masim/evaluation/?       │
│ (Check: timeseries, behavioral, volatility,     │
│  microstructure, visualization, validation,     │
│  registry, data_loader, pipeline)               │
└──────┬──────────────────────────────┬───────────┘
       │ YES                          │ NO
       ▼                              ▼
┌──────────────┐        ┌─────────────────────────────────┐
│ Import it.   │        │ Is F reusable by other          │
│ Done.        │        │ scenarios / modules?            │
└──────────────┘        └──────┬──────────────────┬───────┘
                               │ YES              │ NO (truly unique)
                               ▼                  ▼
                  ┌─────────────────────┐  ┌──────────────────────┐
                  │ Implement F in the  │  │ Implement F locally   │
                  │ correct submodule   │  │ in analysis.py with   │
                  │ of masim/evaluation │  │ comment: "Scenario-   │
                  │ FIRST. Then import  │  │ specific: cannot      │
                  │ it in analysis.py.  │  │ generalize because…"  │
                  └─────────────────────┘  └──────────────────────┘
```

---

## Compliance Checklist for analysis.py Code Review

```
For each analysis.py file in every built variant:
  □ All reusable imports come from masim.evaluation (not from examples/)
  □ All time-series metrics imported from masim.evaluation.finance.timeseries
  □ All behavioral metrics imported from masim.evaluation.finance.behavioral
  □ All volatility metrics imported from masim.evaluation.finance.volatility
  □ All microstructure metrics imported from masim.evaluation.finance.microstructure
  □ All reusable plot functions imported from masim.evaluation.finance.visualization
  □ Scenario validation function imported from masim.evaluation.finance.validation
  □ MetricsRegistry/Metric/MetricUnavailable (if used) imported from masim.evaluation.registry
  □ _batch_to_rounds / _load_data imported from masim.evaluation.data_loader
  □ Only scenario-specific orchestration logic remains local
  □ Any new reusable function was FIRST added to masim/evaluation/ before being called
  □ No cross-scenario imports (e.g., from examples.{OtherScenario}.Rule.analysis)
```

---

## Adding New Metrics to `masim/evaluation/`

When a scenario requires a metric that does not yet exist in `masim/evaluation/`:

1. **Locate the correct module** using the "Placing a New Function" flowchart above and the Module Responsibility Boundaries table. The theory family determines the file; the domain determines the subdirectory.

2. **Implement the function** in that module, following existing code patterns:
   - Accept generic inputs (numpy arrays, dicts, lists) — not scenario-specific data structures
   - Include a docstring with: purpose, parameters, return value, and academic reference
   - Add the function to the module's `__all__` list
   - Re-export through `masim/evaluation/finance/__init__.py`

3. **Verify** that the function works with representative data (a quick test or assertion).

4. **Then import** the new function in your scenario's `analysis.py`.

### Example: Adding a new metric

Suppose `DispositionEffect` needs a `calculate_disposition_ratio()` metric:

```python
# Step 1: Add to masim/evaluation/finance/behavioral.py

def calculate_disposition_ratio(
    realized_gains: list[float],
    realized_losses: list[float],
    unrealized_gains: list[float],
    unrealized_losses: list[float],
) -> dict:
    """
    Calculate Odean (1998) disposition ratio: PGR / PLR.

    PGR = Proportion of Gains Realized = realized_gains / (realized_gains + unrealized_gains)
    PLR = Proportion of Losses Realized = realized_losses / (realized_losses + unrealized_losses)
    Disposition Ratio = PGR / PLR (> 1.0 indicates disposition effect)

    Reference: Odean, T. (1998). Are investors reluctant to realize their losses?
    Journal of Finance, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00072

    Parameters:
        realized_gains: Count or sum of realized winning positions per period
        realized_losses: Count or sum of realized losing positions per period
        unrealized_gains: Count or sum of paper gains per period
        unrealized_losses: Count or sum of paper losses per period

    Returns:
        dict with keys: pgr, plr, disposition_ratio, has_disposition_effect
    """
    ...
```

```python
# Step 2: In examples/DispositionEffect/Rule/analysis.py
from masim.evaluation.finance.behavioral import calculate_disposition_ratio
```

---

## Three-Level Hierarchy

```
masim/evaluation/  (authoritative for REUSABLE metrics, viz, data loading)
    ▲ imports from
Rule/analysis.py   (authoritative for SCENARIO-SPECIFIC orchestration + validation criteria)
    ▲ imports from
LLM/analysis.py, RuleLLM/analysis.py, Rag/analysis.py  (variant-specific additions only)
```

The key distinction:
- **Generic functions** (calculate_*, plot_*, validate_*) → `masim/evaluation/`
- **Scenario orchestration** (analyze_{scenario}, _validate_{scenario} with scenario-specific criteria) → `Rule/analysis.py`
- **Variant additions** (analyze_action_distribution, analyze_rag_knowledge_effect) → variant's own `analysis.py`

---

## Enforcement Points in the Pipeline

This evaluation-first rule is checked at multiple pipeline stages:

| Stage | Check | Document Reference |
|-------|-------|-------------------|
| Step 4 (Implement) | analysis.py imports follow Pattern 1–4 above | `08-step4-implement.md §4.1.4` |
| Step 7 (Analysis Tools) | All metrics from analysis-bases.md §2 implemented via masim/evaluation | `09-step5-to-10-review.md §7.1` |
| Polish Pass 2 | All reusable code imported from `masim/evaluation/` | `polish-simulation-pipeline.md` |
| Step 10 (Final Review) | Import compliance verified in code checklist | `09-step5-to-10-review.md §10.1` |

---

## Inspiration and Discovery

When implementing a scenario's analysis, you are **encouraged** to explore `masim/evaluation/` thoroughly. The existing functions serve as inspiration — if you see a metric that is conceptually related to what your scenario needs, check whether it can be used directly or adapted:

```python
# Example: You're working on MomentumEffect and need a momentum measure.
# Exploring masim/evaluation/finance/timeseries.py, you discover:
#   - calculate_autocorrelation() — already measures serial correlation!
#   - calculate_rolling_autocorrelation() — rolling version!
# These are exactly what momentum measurement needs. Import them directly.
```

This exploration step is MANDATORY before writing any new metric function. It prevents reinventing the wheel and keeps the evaluation module growing as the project's analytical capability library.

---

## Migration Procedure for Existing Scenarios

When polishing or reviewing an existing scenario whose `analysis.py` still has local implementations of functions that belong in `masim/evaluation/`, apply this procedure:

1. **Search `masim/evaluation/`** for existing functions that match. Use the Module Responsibility Boundaries table and the Placing a New Function flowchart above.

2. **If a matching function exists** → replace the local implementation with an import. If other in-scenario code still references the old local name, use an alias: `from masim.evaluation.finance.timeseries import calculate_max_drawdown as _compute_max_drawdown`.

3. **If no match exists but the function is reusable** → migrate it into the appropriate `masim/evaluation/{domain}/{module}.py` file. Add to `__all__`, re-export through `__init__.py`, then import it back in the scenario.

4. **If truly scenario-specific** → keep local with comment: `# Scenario-specific: {reason why it cannot be generalized}`.

5. **Data loading infrastructure** (`batch_to_rounds`, `load_data`, `market_players`, `market_data_from_payload`, `series`) always comes from `masim.evaluation.data_loader`.

6. **Registry types** (`Metric`, `MetricsRegistry`, `MetricUnavailable`) always come from `masim.evaluation.registry`.

7. **Pipeline orchestration** (`run_standard_analysis`, `analyze_standard_scenario`, `calculate_standard_metrics`, `create_standard_visualizations`) comes from `masim.evaluation.pipeline`.

8. **Verify** after migration: `python3 -c "import examples.{Scenario}.Rule.analysis"` must resolve without ImportError.

This procedure is enforced during `polish-simulation-pipeline.md` Pass 2.

---

## Per-Scenario Metric Modules (`metrics.py`)

### When to use

A scenario-level `metrics.py` is warranted when:

- The scenario defines ≥20 metrics with domain-specific logic
- Metrics require scenario-specific context (agent config, role parsing, special accounting)
- Inlining all metric functions in `analysis.py` would exceed ~500 lines of metric logic

When a scenario meets these criteria, a dedicated `metrics.py` at the scenario root (e.g., `examples/AnchoringEffect/metrics.py`) serves as the metric catalogue shared by all variants. Its presence is documented in `01-mandatory-structure.md §2 Architecturally Valid Optional Files`.

### Architecture rules

1. `metrics.py` lives at the scenario root, shared by all variants via import
2. It imports `Metric`, `MetricsRegistry`, `MetricUnavailable` from `masim.evaluation.registry`
3. Standard metrics are registered via `register_standard_metrics(REGISTRY)` — the scenario does NOT reimplement them
4. Only scenario-specific metrics (requiring hardcoded strategy names, scenario-specific config parsing, or custom phase detection) are defined locally
5. Scenario-specific helpers (config parsing, payload accounting, phase detection) are local and documented with comments explaining why they cannot be generalized

### Standard usage pattern

```python
from masim.evaluation.registry import Metric, MetricsRegistry, MetricUnavailable
from masim.evaluation.finance import register_standard_metrics
from masim.evaluation.data_loader import (
    aligned_prices_and_fundamentals,
    payload_buy_sell,
)
from masim.evaluation.finance.timeseries import _returns

REGISTRY = MetricsRegistry()

# Register all 36 standard metrics (price_dynamics, information_efficiency,
# statistical_inference, tail_risk, agent_behaviour, microstructure)
register_standard_metrics(REGISTRY)

# Then register scenario-specific metrics:
def m_my_scenario_specific_metric(data, config):
    ...

REGISTRY.register(Metric(
    name="my_scenario_specific_metric",
    category="scenario_specific",
    fn=m_my_scenario_specific_metric,
    output_keys=("value",),
))
```

### Relationship to `analysis.py`

```
masim/evaluation/finance/
├── timeseries.py       ← 23 registry metrics (price_dynamics, info_efficiency, stat_inference, tail_risk)
├── behavioral.py       ← 8 registry metrics (agent_behaviour)
├── microstructure.py   ← 5 registry metrics (microstructure)
└── __init__.py         ← register_standard_metrics() aggregates all 36
        ↑ register_standard_metrics()
metrics.py                                     ← scenario-specific metrics + REGISTRY assembly
        ↑ imports REGISTRY
{Variant}/analysis.py                          ← orchestration: load data → compute → validate → visualize
```

Each variant's `analysis.py` imports the `REGISTRY` from `metrics.py` and calls `REGISTRY.compute_all(data, config)`. It never calls evaluation functions directly for metric computation — all metric logic is encapsulated in the registry-registered functions.
