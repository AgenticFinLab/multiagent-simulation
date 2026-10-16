# `masim/evaluation/` — The Sole Authoritative Source for All Simulation Evaluation

## What This Module Is

`masim/evaluation/` is the **唯一且完整的评估代码仓库** (single, complete evaluation code repository) for the entire MASim framework. It stores, defines, and exposes **all** reusable content related to simulation evaluation, including but not limited to:

- **Metric functions** — every statistical, behavioral, microstructural, and domain-specific metric computation
- **Data extraction & transformation** — the standard data contract, loading pipelines, and helper functions that convert raw simulation outputs into analysis-ready structures
- **Validation logic** — both rule-based calibration checks and LLM-based qualitative assessment
- **Visualization** — all reusable charting functions for evaluation output
- **Registry infrastructure** — the type system (`Metric`, `MetricsRegistry`, `MetricUnavailable`) that enables declarative metric catalogues
- **Design patterns & contracts** — the function signatures, naming conventions, and architectural patterns that all evaluation code follows

## Why It Exists

Without a centralized evaluation module, metric implementations scatter across dozens of scenario directories, leading to:
- Duplicated logic with subtle inconsistencies (different volatility calculations giving different answers)
- Untraceable bugs (a fix in one scenario never propagates to copies elsewhere)
- Knowledge loss (new developers cannot discover what's already implemented)
- Metric definition drift (the same conceptual metric computed differently across scenarios)

This module eliminates these problems by being the **single point of truth**: one implementation, one definition, one place to look.

## The Hard Rule

> **Every piece of reusable evaluation logic — functions, helpers, constants, data contracts, design patterns — MUST live in `masim/evaluation/`.**
>
> **Every consumer — scenario `metrics.py`, variant `analysis.py`, notebooks, scripts — MUST import from `masim/evaluation/`.**
>
> **No scenario, variant, or external script is permitted to reimplement, copy, or locally define any evaluation function that already exists here or could reasonably be generalized to exist here.**

This is an absolute architectural constraint. It is enforced at code review, during implementation, and by the skills pipeline. Violations are treated as architectural defects requiring immediate correction.

### What This Means in Practice

1. **Before writing any evaluation-related function**, search this module first. If it exists — import it. If it doesn't exist but is reusable — implement it here first, then import.
2. **If you find evaluation code living outside this module** (in a scenario, in a notebook, in a utility script), it is either (a) truly scenario-specific and should be documented as such with a comment, or (b) a violation that must be migrated here.
3. **The module's scope grows monotonically** — new metrics, new helpers, new patterns are added here as the project evolves. Nothing is removed without deprecation.
4. **Scenario-level code (`metrics.py`, `analysis.py`) exists only for**: (a) assembling a scenario-specific registry by calling `register_standard_metrics()` then adding scenario-unique metrics, and (b) orchestrating the analysis pipeline (load → compute → validate → visualize). It does NOT define reusable computation.

---

## Directory Layout

```
masim/evaluation/
├── README.md              ← This file
├── __init__.py            ← Top-level re-exports (domain-agnostic utilities)
├── registry.py            ← Metric, MetricsRegistry, MetricUnavailable
├── data_loader.py         ← Standard data extraction from MASim results
├── pipeline.py            ← High-level analysis orchestration
│
└── finance/               ← Domain: Financial Market Simulation
    ├── __init__.py        ← Aggregation: STANDARD_METRICS, register_standard_metrics()
    ├── timeseries.py      ← Pure time-series statistical tools + 23 registry metrics
    ├── behavioral.py      ← Behavioral finance / agent-level metrics + 8 registry metrics
    ├── microstructure.py  ← Market microstructure (order-flow, liquidity) + 5 registry metrics
    ├── volatility.py      ← Volatility modeling (GARCH, regime detection)
    ├── visualization.py   ← All reusable matplotlib plot functions
    ├── validation.py      ← Rule-based scenario validation (calibration targets)
    └── validation_llm.py  ← LLM-based validation with financial theory prompts
```

Future domains (social dynamics, supply chain, epidemics, etc.) will follow the same pattern as `finance/` — one subdirectory per domain, files organized by method category within.

---

## Organizational Principles

### Three Goals (Priority Order)

1. **Method-category cohesion** — Each `.py` file owns ONE coherent analytical method family. All functions within share the same theoretical grounding. A developer seeking "anything about time-series statistics" opens `timeseries.py` and finds everything.

2. **Zero local reimplementation** — If a reusable function exists here, no scenario rewrites it locally. If it does not exist yet, it is added to the correct method-category file *before* being used.

3. **Discoverability by domain context** — A developer writing a finance scenario needs only `masim.evaluation.finance.{method_category}` to find any function. No "catch-all" or "misc" files; every function has exactly one correct home.

### Absolute Prohibition: No Umbrella Files

A single file aggregating functions from multiple unrelated method categories (e.g., a hypothetical `standard_metrics.py` combining volatility functions with microstructure functions) violates Goal #1 and **must not exist**. Each function lives in its method-category file — including registry-compatible metrics. The fact that a function can be registered into a `MetricsRegistry` does not exempt it from method-category placement.

### Two-Level Hierarchy: Domain → Method Category

| Level | Role | Example |
|-------|------|---------|
| **0** (top-level) | Domain-agnostic infrastructure | `registry.py`, `data_loader.py`, `pipeline.py` |
| **1** (domain subdirectory) | Groups code sharing domain-specific semantics | `finance/` (prices, bids, portfolios) |
| **2** (files within domain) | One file per academic theory family / analytical method | `timeseries.py`, `behavioral.py`, etc. |

---

## Top-Level Modules (Domain-Agnostic)

### `registry.py` — Type System

Provides three types consumed by all domains and scenarios:

| Type | Role |
|------|------|
| `Metric` | Dataclass defining a named metric: `name`, `category`, `fn`, `output_keys`, `references`, `description` |
| `MetricsRegistry` | Collection of Metric instances; provides `register()`, `compute_all(data, config)`, `__len__()` |
| `MetricUnavailable` | Exception raised inside `fn(data, config)` when required input data is absent |

The registry's `compute_all()` catches `MetricUnavailable` per-metric and records the skip, so a partial dataset gracefully produces partial results rather than crashing.

### `data_loader.py` — Standard Data Extraction

Understands MASim's internal storage (batch stores, turn payloads, player roles) and normalizes them into clean Python dicts for metric consumption.

Public functions (canonical names):

| Function | Purpose |
|----------|---------|
| `batch_to_rounds(values)` | List → `{round: value}` dict (1-based) |
| `load_data(results, config)` | Full extraction → standard data contract dict |
| `market_players(results)` | Finds coordinator/environment players |
| `market_data_from_payload(payload)` | Extracts market data from a turn payload |
| `series(player, store)` | Shorthand: `batch_to_rounds(player.batch(store).all())` |
| `aligned_prices_and_fundamentals(data)` | Returns `(rounds, prices, fundamentals)` aligned on round intersection |
| `payload_buy_sell(payload)` | Returns `(buy_qty, sell_qty)` from action/quantity fields |
| `per_agent_initial_position(config)` | Extracts initial share positions from config (handles num_instances) |
| `per_agent_initial_cash(config)` | Extracts initial cash from config (handles num_instances) |

All public functions also have underscore-prefixed aliases (`_batch_to_rounds`, etc.) for backward compatibility.

#### Standard Data Contract

The canonical `data` dict produced by `load_data()` and consumed by all metric functions:

```python
data = {
    "market_prices":       {round: float},          # Market clearing prices
    "fundamentals":        {round: float},          # True fundamental values
    "investor_quantities": {player_id: {round: float}},  # Holdings per agent
    "investor_bids":       {player_id: {round: float}},  # Bids per agent
    "investor_payloads":   {player_id: {round: dict}},   # Full turn payloads
}
```

### `pipeline.py` — Orchestration

High-level functions that run the standard analysis pipeline end-to-end: `run_standard_analysis()`, `analyze_standard_scenario()`. Used primarily by scenarios that don't need custom orchestration.

---

## Finance Domain (`finance/`)

### Current Metric Counts (36 Standard Registry Metrics)

| Module | Category | Count |
|--------|----------|-------|
| `timeseries.py` | price_dynamics | 12 |
| `timeseries.py` | information_efficiency | 5 |
| `timeseries.py` | statistical_inference | 4 |
| `timeseries.py` | tail_risk | 2 |
| `behavioral.py` | agent_behaviour | 8 |
| `microstructure.py` | microstructure | 5 |
| **Total** | | **36** |

All 36 are aggregated in `finance/__init__.py` as `STANDARD_METRICS` and registered via `register_standard_metrics(registry)`.

### Module Responsibility Boundaries

#### `timeseries.py` — Pure Time-Series Statistics (23 registry metrics)

**Theory family**: Statistical properties of price/return series. No behavioral stance — just computation.

**Belongs here**: autocorrelation, rolling volatility, returns, Sharpe ratio, max drawdown, skewness, kurtosis, variance ratio (Lo-MacKinlay), VaR, CVaR, bootstrap confidence intervals, Ljung-Box test, ADF unit root test, deviation statistics, half-life fitting, price efficiency ratio, regime transition lag.

**Does NOT belong**: Anything requiring agent-level data or implying behavioral theory.

**Internal structure**:
- Part I: Computation Primitives (`calculate_returns`, `calculate_autocorrelation`, etc.)
- Part II: Internal Helpers (`_returns`, `_log_returns`, `_half_life_threshold_impl`, `_block_bootstrap_indices`, etc.)
- Part III: Registry-Compatible Metric Functions (`m_price_deviation_ts` through `m_conditional_var_95`)
- Part IV: `TIMESERIES_METRICS` list (23 Metric objects)

#### `behavioral.py` — Behavioral Finance / Agent-Level (8 registry metrics)

**Theory family**: Behavioral finance (Kahneman, Shiller, Odean, Bikhchandani). Measures agent-level or collective behavioral patterns, wealth accounting, and inequality.

**Belongs here**: herding CV, directional agreement, cascade measure, agent action frequency, agent volume, agent net position, agent PnL, agent Sharpe ratio, agent wealth, Gini coefficient, silent agent detection.

**Does NOT belong**: Pure price-level statistics without behavioral interpretation.

**Internal structure**:
- Part I: Computation Primitives (`calculate_bid_convergence_cv`, `calculate_directional_agreement`, `calculate_cascade_measure`, etc.)
- Part II: Registry-Compatible Metric Functions (`m_agent_action_frequency` through `m_gini_coefficient`)
- Part III: `BEHAVIORAL_METRICS` list (8 Metric objects)

#### `microstructure.py` — Market Microstructure (5 registry metrics)

**Theory family**: Kyle (1985), Glosten-Milgrom (1985), Amihud (2002). Order-flow mechanics, liquidity, price impact.

**Belongs here**: order imbalance, signed volume autocorrelation, HHI volume concentration, strategy correlation matrix, information share by strategy, volume-price relationships, bid-ask spread, Amihud illiquidity, net demand flow.

**Does NOT belong**: Behavioral interpretations of trading patterns, bubble detection (valuation concept).

#### `volatility.py` — Volatility Modeling

**Theory family**: Engle (1982) / Bollerslev (1986). Second-moment dynamics, clustering, regimes.

**Belongs here**: GARCH signature, volatility persistence, return clustering, regime detection.

**Does NOT belong**: First-moment metrics (returns, prices), agent-level measures.

#### `visualization.py` — Reusable Plot Functions

All matplotlib-based charting functions for the finance domain. Separated from metrics because it has a distinct dependency (matplotlib) and serves all other modules.

**Belongs here**: `plot_price_dynamics`, `plot_returns_analysis`, `plot_multi_panel_summary`, `create_figure`, `save_figure`.

**Does NOT belong**: Scenario-specific plot arrangements (those stay in scenario `analysis.py`).

#### `validation.py` — Rule-Based Calibration Checks

Each validator takes computed metrics and returns pass/fail against literature-established ranges. Returns `ValidationResult` objects.

**Belongs here**: `validate_asset_bubble`, `validate_herd_effect`, `validate_flash_crash`, etc.

**Does NOT belong**: Metric computation itself (that belongs in metric modules).

#### `validation_llm.py` — LLM-Based Validation

Complements rule-based validation with qualitative reasoning using financial theory prompts.

**Belongs here**: `LLMValidator`, `validate_with_llm`, `get_theory_prompt`.

---

## Registry-Compatible Metric Functions

### Signature Contract

Every `m_*` function follows this signature:

```python
def m_metric_name(data: dict, config: dict) -> dict:
    """Docstring with description and academic reference."""
    # Guard clause: raise if required data missing
    prices = data.get("market_prices")
    if not prices:
        raise MetricUnavailable("market_prices not available")
    # Computation
    result = ...
    # Return dict with keys matching Metric.output_keys
    return {"key1": value1, "key2": value2}
```

Key rules:
- `data` follows the standard data contract (see above)
- `config` is the scenario configuration dict
- Returns a `dict` whose keys match the `output_keys` declared in the corresponding `Metric` definition
- Raises `MetricUnavailable` (never returns None/empty) when required input is absent
- Uses only numpy and standard library (no scenario-specific imports)

### Metric Definition

```python
Metric(
    name="return_skewness",           # Unique identifier (no m_ prefix)
    category="price_dynamics",        # Category for grouping
    fn=m_return_skewness,             # The function reference
    output_keys=("skewness",),        # Keys in the returned dict
    references=("Cont (2001)",),      # Academic references
    description="Skewness of log returns; negative indicates crash risk.",
)
```

---

## Standard Import Patterns

### Pattern 1: Scenario `metrics.py` using the registry system

```python
from masim.evaluation.registry import Metric, MetricsRegistry, MetricUnavailable
from masim.evaluation.finance import register_standard_metrics
from masim.evaluation.data_loader import (
    aligned_prices_and_fundamentals,
    payload_buy_sell,
)
from masim.evaluation.finance.timeseries import _returns

REGISTRY = MetricsRegistry()

# Register all 36 standard metrics
register_standard_metrics(REGISTRY)

# Scenario-specific metrics below
def m_my_specific_metric(data, config):
    ...

REGISTRY.register(Metric(
    name="my_specific_metric",
    category="scenario_specific",
    fn=m_my_specific_metric,
    output_keys=("value",),
))
```

### Pattern 2: Direct function imports in `analysis.py`

```python
from masim.evaluation.finance.timeseries import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_sharpe_ratio,
)
from masim.evaluation.finance.behavioral import (
    calculate_bid_convergence_cv,
    calculate_directional_agreement,
)
from masim.evaluation.finance.visualization import (
    plot_price_dynamics,
    create_figure,
    save_figure,
)
```

### Pattern 3: Data loading

```python
from masim.evaluation.data_loader import load_data, batch_to_rounds, series
```

---

## Adding New Functions: Decision Flowchart

```
┌─────────────────────────────────────────────┐
│ I need function F.                          │
│ Is it reusable by other scenarios?          │
└─────────────┬─────────────────┬─────────────┘
              │ YES             │ NO
              ▼                 ▼
┌─────────────────────────┐  ┌────────────────────────────────────┐
│ Does it already exist   │  │ Keep local with comment:           │
│ in masim/evaluation/?   │  │ # Scenario-specific: {reason}      │
│                         │  └────────────────────────────────────┘
│ YES → import it. Done.  │
│ NO  → implement it in   │
│       the correct module │
│       FIRST, then import.│
└─────────────────────────┘
```

### Choosing the Correct Module

1. Does it compute a pure statistical property of a time series (no agent data, no behavioral theory)?
   → `timeseries.py`

2. Does it measure an agent-level or collective behavioral pattern, wealth, or inequality?
   → `behavioral.py`

3. Does it characterize volatility dynamics (second-moment structure, clustering, regimes)?
   → `volatility.py`

4. Does it analyze order-flow mechanics, liquidity, or price impact at the market mechanism level?
   → `microstructure.py`

5. Does it produce a visualization?
   → `visualization.py`

6. Does it CHECK results against calibration targets (not compute metrics)?
   → `validation.py` or `validation_llm.py`

7. Is it domain-agnostic data extraction/transformation?
   → `data_loader.py`

8. None of the above fit?
   → Either truly scenario-specific (keep local), or create a new module if ≥3 related functions are needed.

---

## Scenario-Level `metrics.py`

A scenario may have its own `metrics.py` at the scenario root (e.g., `examples/AnchoringEffect/metrics.py`) when:
- It defines domain-specific metrics requiring hardcoded strategy names, scenario-specific config parsing, or custom phase detection logic
- Inlining all metric logic in `analysis.py` would exceed ~500 lines

### Rules for scenario `metrics.py`

1. Lives at the scenario root, shared by all variants
2. Imports `Metric`, `MetricsRegistry`, `MetricUnavailable` from `masim.evaluation.registry`
3. Calls `register_standard_metrics(REGISTRY)` — never reimplements standard metrics
4. Only defines metrics that truly cannot be generalized (requires scenario-specific config parsing, hardcoded strategy names, custom phase detection)
5. Each local helper has a comment explaining why it cannot be promoted to `evaluation/`
6. Uses helpers from `masim.evaluation.data_loader` for data extraction whenever possible

### Architecture Diagram

```
masim/evaluation/finance/
├── timeseries.py        ← 23 registry metrics
├── behavioral.py        ← 8 registry metrics
├── microstructure.py    ← 5 registry metrics
└── __init__.py          ← STANDARD_METRICS (36) + register_standard_metrics()
        ↑ register_standard_metrics()
examples/{Scenario}/metrics.py  ← scenario-specific metrics + REGISTRY assembly
        ↑ imports REGISTRY
examples/{Scenario}/{Variant}/analysis.py  ← orchestration: load → compute → validate → visualize
```

---

## When to Create a New Module

A new `.py` file within `finance/` is warranted when:

1. There are ≥3 related functions that don't fit any existing module boundary
2. They share a coherent academic theory family (e.g., information theory, network analysis, agent learning)
3. The existing modules would become semantically diluted by absorbing them

When creating: add to the directory layout above, define its responsibility boundary, and ensure `finance/__init__.py` re-exports its public names.

## When a Module Grows Too Large

If a file exceeds ~800 lines or ~20 functions, split into a subdirectory:

```
finance/timeseries/        # replaces finance/timeseries.py
├── __init__.py            # re-exports everything (preserves import paths)
├── returns.py             # return series computations
├── deviation.py           # price deviation and half-life
└── inference.py           # statistical tests (ADF, Ljung-Box, bootstrap)
```

The `__init__.py` re-export ensures that `from masim.evaluation.finance.timeseries import m_return_skewness` still works — zero breaking changes for existing code.

---

## Migration Procedure (For Existing Scenarios)

When polishing a scenario whose code still contains local reimplementations:

1. **Search** `masim/evaluation/` for matching functions
2. **If match exists** → replace local code with import
3. **If no match but reusable** → promote to the correct method-category file, add to `__all__`, re-export through `finance/__init__.py`, then import
4. **If truly scenario-specific** → keep local with comment explaining why
5. **Verify** after migration: `python3 -c "import examples.{Scenario}.Rule.analysis"` must succeed

---

## Compliance Checklist

For each `analysis.py` or `metrics.py` file:

- [ ] All reusable imports come from `masim.evaluation` (not from `examples/`)
- [ ] Time-series metrics from `masim.evaluation.finance.timeseries`
- [ ] Behavioral metrics from `masim.evaluation.finance.behavioral`
- [ ] Microstructure metrics from `masim.evaluation.finance.microstructure`
- [ ] Visualization from `masim.evaluation.finance.visualization`
- [ ] Validation from `masim.evaluation.finance.validation`
- [ ] Registry types from `masim.evaluation.registry`
- [ ] Data loaders from `masim.evaluation.data_loader`
- [ ] Standard metrics registered via `register_standard_metrics()`, not reimplemented
- [ ] Only scenario-specific logic remains local (with comments justifying why)
- [ ] No cross-scenario imports (`from examples.{OtherScenario}...`)
