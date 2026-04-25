# Financial Multi-Agent Simulation Creation Guide


## How to Use This Guide

This document provides a complete 10-step methodology for creating financial market simulations. Each step references specific template files from the AssetBubble implementation. Follow the steps sequentially, using the referenced files as guides for structure and content.

**Read the MANDATORY FILE STRUCTURE section first** — it defines the required directory layout and documentation files every simulation must have before any implementation begins.

---

## MANDATORY FILE STRUCTURE

Every simulation must conform to the following fixed directory and file layout. All listed files are **required** — no simulation is considered complete without them.

### Complete Required Layout

```
examples/{SimulationName}/
├── __init__.py                    # Package init (empty or minimal)
├── simulation-bases.md            # ROOT: Theoretical & design foundation
├── analysis-bases.md              # ROOT: Analysis methodology foundation
│
├── Rule/
│   ├── __init__.py
│   ├── players.py
│   ├── run_{name}.py
│   ├── analysis.py
│   ├── explain.md                 # How Rule implements simulation-bases.md
│   └── analysis.md                # How Rule implements analysis-bases.md
│
├── LLM/
│   ├── __init__.py
│   ├── players.py
│   ├── prompts.py
│   ├── run_{name}_llm.py
│   ├── analysis.py
│   ├── explain.md                 # How LLM implements simulation-bases.md
│   └── analysis.md                # How LLM implements analysis-bases.md
│
├── RuleLLM/
│   ├── __init__.py
│   ├── players.py
│   ├── prompts.py
│   ├── run_{name}_rulellm.py
│   ├── analysis.py
│   ├── explain.md                 # How RuleLLM implements simulation-bases.md
│   └── analysis.md                # How RuleLLM implements analysis-bases.md
│
└── Rag/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_rag.py
    ├── analysis.py
    ├── explain.md                 # How Rag implements simulation-bases.md
    └── analysis.md                # How Rag implements analysis-bases.md
```

### File Roles at a Glance

| File                    | Scope               | Purpose                                                                                       |
|-------------------------|---------------------|-----------------------------------------------------------------------------------------------|
| `simulation-bases.md`   | Root (all variants) | Single source of truth: phenomenon theory, market design, investor taxonomy, model parameters |
| `analysis-bases.md`     | Root (all variants) | Single source of truth: analysis dimensions, metrics, expected outcomes, evaluation rationale |
| `{Variant}/explain.md`  | Per variant         | How this variant concretely implements the design in `simulation-bases.md`                    |
| `{Variant}/analysis.md` | Per variant         | How this variant concretely executes the analysis defined in `analysis-bases.md`              |
| `{Variant}/players.py`  | Per variant         | All agent class implementations                                                               |
| `{Variant}/prompts.py`  | LLM/RuleLLM/Rag     | System and user prompt constants                                                              |
| `{Variant}/run_*.py`    | Per variant         | Simulation entry point                                                                        |
| `{Variant}/analysis.py` | Per variant         | Analysis script generating plots and reports                                                  |

### Key Design Principle

```
simulation-bases.md          analysis-bases.md
        │                            │
        │ implements                 │ implements
        ▼                            ▼
{Variant}/explain.md        {Variant}/analysis.md
        │                            │
        │ documents                  │ documents
        ▼                            ▼
{Variant}/players.py        {Variant}/analysis.py
```

- `simulation-bases.md` and `analysis-bases.md` are written **once** and shared across all four variants.
- Each variant's `explain.md` and `analysis.md` inherit from the root documents and specify variant-specific implementation details.
- The code (`players.py`, `analysis.py`) always has a corresponding documentation file (`explain.md`, `analysis.md`) that explains it.

### Variant Construction Principles

Each variant has a distinct construction approach, goal, and set of non-negotiable constraints. Use this table as the primary reference when starting to build or review any variant. The table is designed to be extended: add new rows as new variant types are introduced.

| Variant     | What to Build                                                                                                                                                            | How to Build It                                                                                                                                                                                                                                                    | Goal / Research Purpose                                                                                                                                                                    |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Rule**    | `players.py` (all rule-based agents), `run_*.py`, `analysis.py`, `explain.md`, `analysis.md`                                                                             | Implement each investor as deterministic formulas; all thresholds and parameters loaded from config; no LLM calls anywhere                                                                                                                                         | Establish the deterministic baseline; verify that the target phenomenon emerges purely from mathematical rules and agent interactions                                                      |
| **LLM**     | `players.py` (Market rule-based + LLM investors), `prompts.py`, `run_*_llm.py`, `analysis.py`, `explain.md`, `analysis.md`                                               | Market is identical to Rule variant; each investor has a system prompt (persona only — no phenomenon name) and a user prompt template; LLM output parsed as `<analysis>` reasoning + `<decision>` JSON                                                             | Test whether LLM agents, guided only by personality and market data, can reproduce realistic investor psychology and emergent phenomena without explicit quantitative rules                |
| **RuleLLM** | `players.py`, `prompts.py` (PERSONA + DECISION RULES dual-section), `run_*_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md`                                       | Every system prompt has two mandatory sections: **PERSONA** (who the agent is, risk style, emotional traits) and **DECISION RULES** (the exact Rule-variant formulas re-expressed in plain text); LLM may adjust quantities by ±20% but must follow sign and scale | Isolate the effect of language reasoning: with identical quantitative constraints embedded in the prompt, does LLM reasoning alter phenomenon dynamics compared to the pure Rule baseline? |
| **Rag**     | `players.py` (RAG pipeline added to RuleLLM base), `prompts.py` (PERSONA + DECISION RULES + `{rag_context}`), `run_*_rag.py`, `analysis.py`, `explain.md`, `analysis.md` | Extends RuleLLM: at initialization, each agent builds a personal `KnowledgeStore` from documents; at every decision round, the agent queries the store and injects top-k retrieved chunks into the user prompt as `{rag_context}`                                  | Test the effect of external domain knowledge: does access to retrieved financial literature change decision quality and phenomenon intensity compared to RuleLLM?                          |

---

#### Rule

- **Purpose**: Deterministic baseline implementation — every decision is a formula, every parameter is traceable to a config value and a literature source.
- **Required components**:
  - `players.py`: Market class + one class per investor type (all rule-based, no LLM)
  - `run_{name}.py`: simulation entry point
  - `analysis.py`: all metrics from `analysis-bases.md §2` implemented as functions
  - `explain.md`: complete 9-section implementation guide (§2 maps each investor to code, §3 maps price formula to `_clear_market()`)
  - `analysis.md`: complete 7-section analysis guide (§2 maps each metric to `analysis.py` function)
- **Core construction rule**: No hardcoded values. Every numeric threshold, position size, or parameter must be read from `extras` in `players.yml`. Every parameter in `players.yml` must have a source citation comment.
- **Validation criterion**: Run 100 rounds → target phenomenon clearly visible in price chart. Swap parameter values in `players.yml` → behavior changes predictably.

---

#### LLM

- **Purpose**: Replace deterministic agent decision logic with LLM reasoning, keeping the market mechanism identical to Rule, to test behavioral realism of language model investors.
- **Required components**:
  - `players.py`: Market class (copy from Rule), one LLM investor class per type
  - `prompts.py`: one system prompt constant + shared user prompt template per investor type
  - `run_{name}_llm.py`: simulation entry point
  - `analysis.py`: same metrics as Rule variant
  - `explain.md`, `analysis.md`: complete spec docs
- **Core construction rule**: System prompts define **personality only** — they must not name the phenomenon, mention the price formula, or hint at what market event is occurring. The LLM must discover market dynamics from the user prompt data alone. Output format is always `<analysis>...</analysis><decision>...</decision>` with JSON containing `action`, `bid_price`, `quantity`, `reasoning`.
- **Validation criterion**: LLM agents produce varied but coherent reasoning traces. Phenomenon still emerges. Behavior differs visibly from Rule variant in at least one measurable metric (e.g., peak bubble ratio, timing, crash depth).

---

#### RuleLLM

- **Purpose**: Hybrid variant that anchors LLM reasoning to explicit quantitative rules, enabling direct comparison of constrained vs. unconstrained LLM behavior vs. pure rule execution.
- **Required components**:
  - `players.py`: Market (copy from Rule), one hybrid investor class per type
  - `prompts.py`: each system prompt has two mandatory labeled sections (`== PERSONA ==` and `== DECISION RULES ==`)
  - `run_{name}_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md`
- **Core construction rule**: The DECISION RULES section in every prompt must reproduce the exact formulas from the Rule variant, expressed step-by-step in plain text. The LLM is instructed to follow the rule sign (buy/sell/hold) strictly, with at most ±20% quantity adjustment. Rules must match Rule variant — if Rule parameters change, the embedded prompt rules must be updated.
- **Validation criterion**: LLM decisions align directionally with Rule-variant decisions in ≥80% of rounds. The ±20% deviation range produces measurable but bounded difference from the Rule baseline.

---

#### Rag

- **Purpose**: Extends RuleLLM with dynamic external knowledge retrieval, to test whether access to domain-specific financial literature changes agent decision quality and phenomenon dynamics.
- **Required components**:
  - `players.py`: extends RuleLLM agents with `_initialize_rag()`, `_build_prompt()` (with retrieval), `KnowledgeStore` integration
  - `prompts.py`: user prompt template includes `{rag_context}` placeholder; system prompts identical to RuleLLM
  - `run_{name}_rag.py`, `analysis.py`, `explain.md`, `analysis.md`
  - `players.yml`: each agent has a `rag:` block specifying `docs_dir`/`url_csv`/`docs_save_dir`, `rag_persist_dir`, `embed_model`, `top_k`
- **Core construction rule**: Knowledge retrieval is per-agent (each agent has its own `KnowledgeStore`, not shared). On first run, the index is built and persisted; subsequent runs load from disk. The `{rag_context}` field in the user prompt is always populated — if no documents are retrieved, inject `"(No relevant knowledge retrieved this round.)"`.
- **Validation criterion**: RAG index builds successfully on first run and loads from disk on subsequent runs. Retrieved context is visible in agent reasoning traces. At least one measurable metric (e.g., timing of crash, peak deviation) differs from RuleLLM baseline.

---

## ROOT DOCUMENT SPECIFICATIONS

### simulation-bases.md — Theoretical and Design Foundation

This is the **master design document** for the entire simulation. It is written once and serves as the authoritative reference for all four variant implementations.

**Location**: `examples/{SimulationName}/simulation-bases.md`

**Required Sections**:

#### Section 1: Simulation Overview

```
# {SimulationName} — Simulation Design Basis

## 1. Phenomenon Definition

| Item               | Description                                            |
|--------------------|--------------------------------------------------------|
| Phenomenon Name    | [Full name and brief description]                      |
| Category           | [Type: herding / bubble / crash / manipulation / etc.] |
| Core Mechanism     | [1-2 sentences on the key dynamic]                     |
| Real-World Origin  | [Historical event(s) that exemplify this]              |
| Research Relevance | [Why this phenomenon matters academically]             |
```

#### Section 2: Theoretical Foundation

For EACH theory underpinning the simulation:

```
### Theory: [Full Theory Name]

- Citation: [Author, Year, Journal/Book, DOI]
- Core Insight: [2-3 sentence summary]
- Mathematical Formulation: [Equation if applicable]
- Relevance to This Simulation: [How it drives agent behavior or market dynamics]
- Implementation Notes: [How to operationalize in players.py]
```

Minimum 2 theories required. Cite academic sources for every claim.

#### Section 3: Market Design Principles

```
### 3.1 Price Formation Model

Formula:      [Complete equation, e.g. P(t+1) = P(t) + λ·D(t) + γ·[F - P(t)] + ε]
Variable List:
  P(t)         — [Definition]
  D(t)         — [Net demand calculation]
  F            — [Fundamental value definition]
  λ (lambda)   — [Price impact; typical range; chosen value; source]
  γ (gamma)    — [Mean reversion; typical range; chosen value; source]
  ε (epsilon)  — [Noise term; distribution; parameters; rationale]

Economic Rationale: [Why each term is included and how it produces the phenomenon]
Dynamic Properties:
  - When D(t) > 0: [What happens]
  - When P >> F:   [What happens]
  - Noise effect:  [What it represents]

### 3.2 Additional Market Mechanisms

[For each mechanism: name, trigger condition, action taken, economic rationale]
  Examples: circuit breakers, short-selling constraints, margin calls, price floors/ceilings

### 3.3 Information Broadcast Design

Each round, the Market sends to all investors:
  - [Field 1]: [Description and rationale for inclusion]
  - [Field 2]: ...
  - [Derived metrics]: [E.g., bubble_ratio = P/F; price_change_pct; volume]
```

#### Section 4: Investor Taxonomy

For EACH investor type (4–6 types required):

```
### Investor: [ClassName]

| Attribute         | Description                                          |
|-------------------|------------------------------------------------------|
| Role Name         | [Descriptive name]                                   |
| Market Role       | [Stabilizing / Destabilizing / Neutral / Amplifying] |
| Theoretical Basis | [Theory name + citation]                             |
| Time Horizon      | [High-frequency / Day trader / Long-term]            |
| Risk Tolerance    | [Low / Medium / High / Extreme]                      |
| Information Used  | [Which fields from Market broadcast]                 |

Rule-Based Behavior:
  - Buy condition:  [Precise condition with formula if applicable]
  - Sell condition: [Precise condition]
  - Hold condition: [Default]
  - Position sizing: [Formula, constraints, bounds]

LLM Persona:
  - Core Belief:   [One sentence guiding all decisions]
  - Psychological Profile: [2-3 sentences on mindset, biases, tendencies]
  - Decision Framework: [Ordered steps]
  - Signal Interpretation: [How they read rising/falling/stable prices]
  - Position Size Range: [Aggressive / Moderate / Conservative shares]

RuleLLM Hybrid Notes:
  - Embedded quantitative rules to include in prompt
  - When to override rules with judgment

Expected Market Impact: [How this investor affects price dynamics]
```

#### Section 5: Agent Diversity Verification

```
Diversity Check:
  Different time horizons:     [Yes — examples]
  Different information sets:  [Yes — examples]
  Conflicting incentives:      [Yes — examples]
  Mix of stabilizing/destabilizing: [Counts and names]
  Different risk tolerances:   [Yes — range from Low to Extreme]
```

#### Section 6: Parameter Table

| Parameter | Value | Source Citation | Description | Sensitivity                             |
|-----------|-------|-----------------|-------------|-----------------------------------------|
| [name]    | [val] | [Author, Year]  | [Purpose]   | [High/Med/Low — what changes if varied] |

All numeric parameter values must have a source citation. Document sensitivity.

#### Section 7: Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {field1, field2, ...}
  2. Each investor:
     a. perceive() — extract and store market data
     b. decide()   — apply strategy (rule / LLM call)
     c. act()      — send order to Market
  3. Market:
     a. perceive() — collect all orders
     b. decide()   — apply price formula
     c. act()      — broadcast new state
  4. Logging and state persistence
```

#### Section 8: Historical Case Studies

For EACH real-world event referenced:

```
Event: [Name]
Date:  [Period]
Market: [Asset class / exchange]
Trigger: [What started it]
Key Dynamics: [Timeline of key events]
Quantitative Data: [Price peak, trough, % change, duration]
Agents Modeled After: [Which investor type maps to which real participant]
Lesson for Simulation: [What to preserve in the model]
```

#### Section 9: Variant Comparison Preview

| Aspect                   | Rule                 | LLM              | RuleLLM              | Rag               |
|--------------------------|----------------------|------------------|----------------------|-------------------|
| Decision Logic           | Fixed formulas       | Prompt + LLM     | Formula-anchored LLM | RAG-augmented LLM |
| Determinism              | Deterministic        | Stochastic       | Semi-deterministic   | Stochastic        |
| Expected Bubble Strength | [Calibration target] | [Expected range] | [Expected range]     | [Expected range]  |
| Research Question        | [Rule-specific]      | [LLM-specific]   | [Hybrid-specific]    | [RAG-specific]    |

---

### analysis-bases.md — Analysis Methodology Foundation

This is the **master analysis document** for the entire simulation. It defines all analysis dimensions, metrics, and evaluation frameworks used across all four variants.

**Location**: `examples/{SimulationName}/analysis-bases.md`

**Required Sections**:

#### Section 1: Analysis Objectives

```
# {SimulationName} — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question | Metric(s)      | Expected Finding  |
|-----------|-------------------|----------------|-------------------|
| [O1]      | [Question]        | [How measured] | [From literature] |
| [O2]      | ...               | ...            | ...               |
```

Minimum 3 analysis objectives. Each must map to at least one concrete metric.

#### Section 2: Core Metrics Catalogue

For EACH metric:

```
### Metric: [Metric Name]

- Category:    [Price Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific]
- Definition:  [Precise mathematical definition]
- Formula:     [Equation]
- Interpretation:
    - Value = 0:      [What it means]
    - Value > threshold: [What it indicates]
    - Value < threshold: [What it indicates]
- Academic Basis: [Citation or established standard]
- Normal Range:   [Typical values from literature for this phenomenon]
- Red Flag:       [Value that indicates calibration problem]
```

Minimum metrics required:
- Price deviation from fundamental  (primary phenomenon metric)
- Phenomenon intensity measure      (e.g., bubble ratio, crash depth, herding index)
- Volatility metric                  (rolling std of returns or similar)
- Portfolio/wealth metric            (agent performance, Sharpe or cumulative return)
- Volume or activity metric          (trading intensity proxy)
- At least one phenomenon-specific metric unique to this simulation

#### Section 3: Analysis Dimensions

Define the distinct analysis perspectives for this simulation:

```
### Dimension 1: [Name, e.g., Price Dynamics Analysis]

Purpose: [What question this dimension answers]
Metrics Used: [List from Section 2]
Visualization: [What plot type; x-axis; y-axis; overlays]
Expected Pattern: [What the chart should show if simulation works correctly]
Comparison Baseline: [Historical data / theoretical prediction / other variant]

### Dimension 2: [Name, e.g., Investor Behavior Analysis]
...

### Dimension 3: [Name, e.g., Phenomenon Emergence Verification]
...
```

Minimum 3 analysis dimensions. Typical simulations cover:
- Price dynamics (phenomenon emergence)
- Agent/investor behavior and portfolio performance
- Phenomenon intensity and lifecycle (phases: onset → peak → resolution)
- Cross-variant comparison

#### Section 4: Phase Analysis Framework

Define the phases of the phenomenon and how to detect them:

```
Phase Detection Rules:

| Phase | Name              | Entry Condition    | Exit Condition     | Key Indicators    |
|-------|-------------------|--------------------|--------------------|-------------------|
| 1     | [e.g. Onset]      | [Metric threshold] | [Metric threshold] | [What to observe] |
| 2     | [e.g. Escalation] | ...                | ...                | ...               |
| 3     | [e.g. Peak]       | ...                | ...                | ...               |
| 4     | [e.g. Resolution] | ...                | ...                | ...               |
```

#### Section 5: Cross-Variant Comparison Framework

```
Comparison Protocol:

1. Normalize: [How to make metrics comparable across variants]
2. Statistical test: [What test to use; significance level]
3. Key comparison axes:
   - Phenomenon emergence speed  (Rule vs LLM vs RuleLLM vs Rag)
   - Phenomenon intensity         (Peak metric value across variants)
   - Behavioral realism           (Qualitative assessment criteria)
   - Decision quality             (Portfolio outcomes)
4. Reporting format: [Table structure for comparison results]
```

#### Section 6: Expected Results and Validation

```
Expected Stylized Facts (from literature):
  - [Fact 1]: [Source citation] — How to verify in simulation
  - [Fact 2]: ...
  - [Fact 3]: ...

Calibration Targets:
  - Metric A should be in range [X, Y]: [Source]
  - Metric B should be in range [X, Y]: [Source]

Validation Failure Signs:
  - [Sign 1]: [Diagnosis] → [Corrective action]
  - [Sign 2]: ...
```

#### Section 7: Visualization Catalogue

| Plot Name | Type                         | X-axis  | Y-axis  | Overlays         | Purpose           |
|-----------|------------------------------|---------|---------|------------------|-------------------|
| [Name]    | [Line/Bar/Scatter/Histogram] | [Field] | [Field] | [Optional lines] | [What it reveals] |

Minimum required plots:
- Price vs. Fundamental over time
- Phenomenon intensity metric over time
- Investor/portfolio performance comparison
- Phase detection overlay on price chart
- Cross-variant comparison summary

---

## VARIANT DOCUMENT SPECIFICATIONS

### {Variant}/explain.md — Variant Implementation Guide

This file documents **how the specific variant concretely implements** the theoretical design in `simulation-bases.md`. It is written per variant and must directly trace every design element to its implementation.

> **CROSS-REFERENCE PRINCIPLE**: `explain.md` must NOT duplicate content from `simulation-bases.md`.
> Instead, **cite the exact section** of `simulation-bases.md` that defines each theoretical element,
> then explain only how this variant implements it. This keeps `simulation-bases.md` as the
> single authoritative source, and ensures the implementation stays consistent with the design.
>
> Pattern: `"[Implementation detail] — implements simulation-bases.md §N.M"`

**Required Sections**:

#### Section 1: Variant Overview

```
# {SimulationName} {Variant} — Implementation Explanation

## Overview

| Item                               | Description                                                 |
|------------------------------------|-------------------------------------------------------------|
| Variant                            | [Rule / LLM / RuleLLM / Rag]                                |
| Implements                         | `../simulation-bases.md`                                    |
| Decision Logic                     | [Fixed formulas / LLM prompts / Hybrid / RAG-augmented LLM] |
| Key Difference from Other Variants | [1-2 sentences]                                             |
| Primary Research Contribution      | [What unique insight this variant enables]                  |
```

#### Section 2: How Theoretical Design Is Implemented

For EACH investor type from `simulation-bases.md §4`:

> **Do NOT re-state the theory here.** Instead, write
> `"Theory defined in simulation-bases.md §4 — [ClassName]"` and then
> immediately specify the implementation detail (method name, formula, config path).
> The goal is: reader looks up `simulation-bases.md §4` to understand the theory,
> then comes here to see exactly how that theory is encoded in code.

```
### {ClassName}: Theory → Implementation Mapping
                   (Theory defined in simulation-bases.md §4)

| Theoretical Design Element                             | Implementation                                     |
|--------------------------------------------------------|----------------------------------------------------|
| Theoretical basis → simulation-bases.md §4.{N}         | [Class docstring reference; file line range]       |
| Rule-based behavior (buy/sell/hold) → sim-bases §4.{N} | [Method name; formula in code; parameter source]   |
| LLM persona → simulation-bases.md §4.{N} LLM Persona   | [Prompt constant name; which section of prompt]    |
| Parameter values → simulation-bases.md §6              | [Where loaded from config; default value]          |
| Market impact mechanism → simulation-bases.md §4.{N}   | [How the code produces the expected market impact] |
```

#### Section 3: Market Mechanism Implementation

> **Do NOT re-derive the formula here.** The formula, its variables, and economic rationale
> are fully defined in `simulation-bases.md §3.1`. Here, only document how it is
> **translated into code**: variable names, config paths, and any implementation approximations.

```
### Price Formula Implementation

Formula source: simulation-bases.md §3.1
  P(t+1) = [copy equation from §3.1 — do not re-explain it]

Implemented in: players.py → Market._clear_market()
Code translation:
  [sim-bases variable] → [Python variable name] → [config path in players.yml]
  λ (lambda)           → price_impact           → extras.price_impact
  γ (gamma)            → mean_reversion          → extras.mean_reversion
  F (fundamental)      → self._fundamental       → extras.fundamental_value
  ...

Additional mechanisms: simulation-bases.md §3.2
  [mechanism name] → [implementing method in players.py] → [config parameter]

Deviations from simulation-bases.md design: [None / List any approximations made]
```

#### Section 4: Variant-Specific Features

Document what is **unique** to this variant versus others. For each feature, cite the
`simulation-bases.md §9` (Variant Comparison Preview) entry that motivated this choice:

- **Rule**: Document the specific formulas, thresholds, and algorithmic decision logic
  — cite simulation-bases.md §4 for each investor's rule-based behavior spec
- **LLM**: Document prompt design choices — what personality cues trigger what behaviors;
  expected LLM response patterns; how JSON parsing works
  — cite simulation-bases.md §4 LLM Persona for each investor's prompt design
- **RuleLLM**: Document which rules are embedded in prompts; how rule-judgment balance is handled
  — cite simulation-bases.md §4 RuleLLM Hybrid Notes for each investor
- **Rag**: Document the knowledge base content design; retrieval query strategy; how retrieved
  context modifies decisions — cite simulation-bases.md §8 (Historical Case Studies) as the
  source for knowledge base content choices

#### Section 5: Architecture Diagram

ASCII diagram showing:
- Agent types and their roles
- Message flow between Market and investors
- For LLM variants: LLM API call flow
- For Rag variant: Knowledge retrieval flow

#### Section 6: Configuration Reference

```
Key Configuration Parameters (configs/{SimulationName}/{Variant}/players.yml):

| Parameter | Config Path   | Value   | Design Justification                   |
|-----------|---------------|---------|----------------------------------------|
| [name]    | extras.[name] | [value] | [Why this value implements the design] |
```

#### Section 7: Running Instructions

```
Execution:
  python examples/{SimulationName}/{Variant}/run_{name}[_suffix].py \
      -c configs/{SimulationName}/{Variant}/simulation.yml

Required environment variables:
  [VAR_NAME]: [What it is; where to obtain]

Expected runtime: [Estimate for 200 rounds]
Output location:  EXPERIMENT/{SimulationName}/{Variant}/
```

#### Section 8: Expected Behavior Patterns

```
| Phase        | Rounds  | Expected Agent Behavior | Expected Price Dynamics |
|--------------|---------|-------------------------|-------------------------|
| [Phase name] | [Range] | [Agent decisions]       | [Price movement]        |
```

#### Section 9: References

Do **NOT** repeat full citations already listed in `simulation-bases.md §2`. Instead:
- List only references that are **new to this variant** (not in `simulation-bases.md`)
- For all shared references, write: `"See simulation-bases.md §2 — [Theory Name]"`
- Cross-reference every cited item to the `simulation-bases.md` section where it is
  discussed in depth, e.g.: `"Greater Fool Theory → simulation-bases.md §2, §4 — MomentumSpeculator"`

---

### {Variant}/analysis.md — Variant Analysis Guide

This file documents **how the specific variant concretely executes** the analysis methodology defined in `analysis-bases.md`. It traces analysis objectives to specific implementation details in `analysis.py`.

**Required Sections**:

#### Section 1: Analysis Overview

```
# {SimulationName} {Variant} — Analysis Documentation

## Overview

| Item                            | Description                                       |
|---------------------------------|---------------------------------------------------|
| Implements                      | `../analysis-bases.md`                            |
| Analysis Script                 | `analysis.py` in this directory                   |
| Output Location                 | `EXPERIMENT/{SimulationName}/{Variant}/analysis/` |
| Variant-Specific Considerations | [Key differences from other variants]             |
```

#### Section 2: Metric Implementation

For EACH metric from `analysis-bases.md §2`:

```
### Metric: [Name]

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → [function_name]()`
- Data source: `EXPERIMENT/{Sim}/{Variant}/records/[file_pattern]`
- Variant-specific notes: [Any differences in how this metric behaves for this variant]
  (e.g., "LLM variant shows higher variance due to stochastic LLM decisions")
- Expected range for this variant: [Min, Max based on calibration]
```

#### Section 3: Dimension-by-Dimension Analysis

For EACH dimension from `analysis-bases.md §3`:

```
### Dimension [N]: [Name]

Objective (from analysis-bases.md): [Copy objective statement]

Implementation in analysis.py:
  - Function: [function_name]()
  - Input data: [files loaded]
  - Computation: [brief description of steps]
  - Output: [plot file name; report section]

Variant-Specific Interpretation:
  [How to interpret this dimension's results for this specific variant]
  [What patterns are expected that differ from other variants]
  [What constitutes a successful result for this variant]

Expected Output Sample:
  [Text description or ASCII sketch of expected chart/table]
```

#### Section 4: Variant-Specific Observable Phenomena

Document phenomena that are **unique to this variant** and not present in others:

```
| Phenomenon | Description  | How to Observe         | Contrast with Rule-Based |
|------------|--------------|------------------------|--------------------------|
| [Name]     | [What it is] | [Which metric / chart] | [What differs]           |
```

Examples by variant type:
- **Rule**: Exact formula-driven thresholds; deterministic phase transitions
- **LLM**: Reasoning variability; emergent caution after observed crashes; narrative framing effects
- **RuleLLM**: Rule override events; when LLM judgment departs from formula recommendation
- **Rag**: Effect of knowledge retrieval; how historical context modifies decisions vs. no-RAG baseline

#### Section 5: Scaling and Sensitivity Analysis

```
### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity |
|--------------|--------------------|--------------------|[...]

### Agent Count Scaling

| Agent Count | Expected Observable | Market Dynamics |
|-------------|---------------------|-----------------|
[...]

### Parameter Sensitivity

| Parameter | Change | Expected Effect on Analysis |
|-----------|--------|-----------------------------|
[...]
```

#### Section 6: Output Files Reference

```
All outputs written to: EXPERIMENT/{SimulationName}/{Variant}/analysis/

| Output File | Generated By | Contents       | Interpretation   |
|-------------|--------------|----------------|------------------|
| [filename]  | [function()] | [what's in it] | [how to read it] |
```

#### Section 7: Cross-Variant Comparison Notes

For each cross-variant comparison from `analysis-bases.md §5`:

```
This variant's expected position in cross-variant comparison:
- Phenomenon emergence speed:  [Faster / Same / Slower than other variants; reason]
- Phenomenon intensity:        [Higher / Same / Lower; reason]
- Behavioral realism:          [Assessment; what makes this variant more/less realistic]
- Decision quality:            [Portfolio performance expectation vs. other variants]
```

---

## STEP 0: Define Your Simulation

### 0.1 Minimum Required Input

The user only needs to provide:

```
SIMULATION DEFINITION
=====================

Name: [PascalCase, e.g., "FlashCrash", "HerdBehavior", "VolatilitySpike"]

Phenomenon Description:
-----------------------
[1-2 paragraphs describing the financial phenomenon to simulate]
- What happens in this phenomenon?
- What are the key characteristics?
```

### 0.2 AI/Researcher Responsibility

**All remaining information must be researched and developed through comprehensive investigation:**

The AI or researcher should:

1. **Search extensively** for academic papers, empirical studies, and historical data about the phenomenon
2. **Identify real-world examples** (historical events, case studies)
3. **Determine the market context** (type, structure, institutional features)
4. **Formulate research questions** based on gaps in understanding
5. **Build the theoretical foundation** through literature review

**Reference**: See how AssetBubble's `explain.md` develops comprehensive context from a simple starting point. The phenomenon "asset bubbles" expands into detailed theoretical discussion, historical cases, and research questions through thorough investigation.

### 0.3 Research Output Structure

After research, compile findings into:

```
RESEARCHED CONTENT (to be filled through investigation)
======================================================

Scenario Context:
-----------------
[Market type, structure, institutional features - RESEARCHED]

Research Questions:
-------------------
[3-5 specific questions - DEVELOPED from literature gaps]

Real-World Examples:
--------------------
[2-3 historical events with details - FOUND through search]

Theoretical Foundation:
-----------------------
[Core theories, citations, models - EXTRACTED from academic papers]
```

### 0.2 Example: AssetBubble Definition

**Reference**: See `examples/AssetBubble/Rule/explain.md` lines 1-30 for how AssetBubble defines its phenomenon.

Key elements in AssetBubble definition:
- Clear phenomenon name (Asset Bubbles)
- Mechanism description (positive feedback, speculation)
- Theoretical foundation preview (Greater Fool Theory, etc.)
- Key dynamics listed (5-step bubble process)

### 0.3 Validation Checklist

Before proceeding, verify:
- [ ] Name is descriptive and PascalCase
- [ ] Phenomenon is distinct from existing simulations
- [ ] Description is specific enough to guide agent design
- [ ] Research questions are answerable through simulation
- [ ] Real-world examples exist for validation

---

## STEP 1: Research and Theory Foundation

### 1.1 Research Strategy

Conduct systematic research across five dimensions:

**Dimension 1: Core Economic Theory**
Search for academic papers establishing the theoretical foundations of your phenomenon.

Key search terms to use:
```
"[phenomenon] financial theory"
"[phenomenon] economic model"
"[phenomenon] academic papers/books"
"agent-based model [phenomenon]"
```

**Dimension 2: Behavioral Finance**
Identify cognitive biases and psychological factors involved.

Key search terms:
```
"[phenomenon] behavioral finance"
"[phenomenon] cognitive bias"
"[phenomenon] investor psychology"
```

**Dimension 3: Empirical Evidence**
Find stylized facts from real markets.

Key search terms:
```
"[phenomenon] empirical evidence"
"[phenomenon] stylized facts"
"[phenomenon] statistical properties"
```

**Dimension 4: Historical Case Studies**
Document specific historical events.

Key search terms:
```
"[phenomenon] case study"
"[phenomenon] historical analysis"
"famous [phenomenon] events"
```

**Dimension 5: Market Microstructure**
Understand trading mechanisms and institutional details.

Key search terms:
```
"[phenomenon] market microstructure"
"[phenomenon] trading mechanism"
"[phenomenon] high frequency trading"
```

### 1.2 Research Documentation Structure

Create a research notes file with these sections:

**Section 1: Core Theories**

For each theory identified, document:

```
Theory: [Full name]
Citation: [Author, Year, Journal, DOI if available]
Key Insight: [2-3 sentence summary of core mechanism]
Mathematical Model: [Formula if available]
Relevance: [How this applies to your simulation]
Implementation Notes: [How to operationalize in agents]
```

**Reference**: See `examples/AssetBubble/Rule/players.py` lines 1-21 for how AssetBubble documents its theoretical foundation in the module docstring.

**Section 2: Stylized Facts**

Create a table:

| Stylized Fact | Source     | Implementation Approach |
|---------------|------------|-------------------------|
| [Description] | [Citation] | [How to model]          |

**Section 3: Historical Events**

For each event:

```
Event: [Name]
Date: [When it occurred]
Market: [Which market/asset]
Trigger: [What started it]
Timeline:
  - [Time]: [Event]
  - [Time]: [Event]
Price Movement: [Peak, trough, % change]
Key Participants: [Who was involved]
Lessons for Simulation: [What to model]
```

**Section 4: Agent Types from Literature**

Document participant types found in research:

```
Agent Type: [Name from literature]
Frequency: [% of market or prevalence]
Behavior: [What they do]
Strategy: [How they decide]
Impact: [Effect on market]
Theory Basis: [Which theory explains them]
```

**Section 5: Parameter Values**

Compile quantitative estimates:

| Parameter | Typical Range | Source     | Notes     |
|-----------|---------------|------------|-----------|
| [Name]    | [Min-Max]     | [Citation] | [Context] |

### 1.3 Theory Selection Criteria

Select 2-4 theories that:

1. **Explain the core mechanism** - Must directly address what causes the phenomenon
2. **Are implementable** - Can be operationalized as agent rules or prompts
3. **Suggest different agent types** - Each theory maps to a distinct investor class
4. **Have empirical support** - Backed by data or widely accepted in literature

**Reference**: AssetBubble uses four theories (see `examples/AssetBubble/Rule/players.py` lines 7-11):
- Greater Fool Theory → MomentumSpeculator
- Limits to Arbitrage → RationalArbitrageur  
- Noise Trader Risk → NoiseTrader
- Synchronization Risk → timing of bubble bursts

---

## STEP 2: Design Agent Architecture

### 2.1 Market Agent Design

The Market is the coordinator that clears orders and sets prices. Design it first as all investors interact with it.

**Step 2.1.1: Define Price Formation Mechanism**

Specify the mathematical model:

```
PRICE FORMULA SPECIFICATION
===========================

Formula: [Write the complete equation]

Variables:
- P(t): [Definition]
- NetDemand: [How calculated]
- [Other variables]: [Definitions]

Parameters:
- price_impact (λ): [Description, typical value range, your value, source]
- mean_reversion (γ): [Description, typical value range, your value, source]
- [Other parameters]: [Same structure]

Economic Rationale:
[Explain why each term is included and how it contributes to the phenomenon]

Dynamic Properties:
- What happens when NetDemand is positive?
- What happens when price deviates from fundamental?
- How does noise affect dynamics?
```

**Reference**: See `examples/AssetBubble/Rule/players.py` lines 41-62 for Market class docstring showing formula documentation.

**Step 2.1.2: Define Additional Market Mechanisms**

List all market features:

```
MARKET MECHANISMS
=================

Circuit Breakers:
- Trigger: [Condition]
- Action: [What happens]
- Duration: [How long]

Short Selling:
- Allowed: [Yes/No]
- Cost: [% of position value]
- Constraints: [Any limits]

Margin Requirements:
- Initial margin: [%]
- Maintenance margin: [%]
- Margin call process: [Description]

Liquidity Provision:
- Market makers: [Yes/No]
- Their behavior: [How they quote]

Other Features:
- [Any other mechanisms]
```

**Step 2.1.3: Define Information Broadcast**

Specify what Market tells investors each round:

```
INFORMATION BROADCAST
=====================

Always Included:
- Current price
- Fundamental value
- Current round number

Calculated Metrics:
- Price deviation from fundamental [%]
- Price change over last N rounds [%]
- Trading volume
- [Other metrics]

Rationale:
[Why each piece of information is included]
```

### 2.2 Investor Taxonomy Design

Design 4-6 distinct investor types. For each type, create a complete specification.

**Step 2.2.1: Investor Type Specification Template**

```
INVESTOR TYPE SPECIFICATION
===========================

Name: [Descriptive name]
Code Name: [PascalCase class name]

Theoretical Basis:
- Primary Theory: [Name from Step 1]
- Citation: [Full reference]
- Key Mechanism: [How theory explains behavior]

Market Role:
- Category: [Stabilizing/Destabilizing/Neutral]
- Typical Fraction: [% of market]
- When Active: [Market conditions]

Behavioral Profile:
- Decision Style: [Rule-based/Discretionary/Hybrid]
- Information Used: [List what they observe]
- Time Horizon: [High-frequency/Day trader/Long-term]
- Risk Tolerance: [Low/Medium/High/Extreme]

RULE-BASED SPECIFICATION
------------------------

Trigger Conditions:
- Buy when: [Specific condition]
- Sell when: [Specific condition]
- Hold when: [Specific condition]

Position Sizing:
- Formula: [How many shares to trade]
- Constraints: [Max position, cash limits, etc.]

Parameters:
| Parameter | Value   | Source     | Description        |
|-----------|---------|------------|--------------------|
| [Name]    | [Value] | [Citation] | [What it controls] |

LLM PERSONA SPECIFICATION
-------------------------

Core Belief: [One sentence that guides all decisions]

Psychological Profile:
[2-3 paragraphs describing mindset, biases, tendencies]

Decision Framework:
1. [Step 1: What to assess first]
2. [Step 2: What to assess next]
3. [Step 3: How to decide]

Signal Interpretation:
- Price rising strongly: [How they interpret]
- Price falling sharply: [How they interpret]
- Price near fundamental: [How they interpret]
- High volatility: [How they interpret]

Position Sizing Approach:
- Aggressive trades: [Range] shares
- Moderate trades: [Range] shares
- Conservative trades: [Range] shares

Risk Management:
[How they manage risk, when they exit]

RULELLM HYBRID SPECIFICATION
----------------------------

Embedded Rules:
[List quantitative formulas to include in prompt]

Rule-Judgment Balance:
[When to follow rules strictly vs use discretion]
```

**Reference**: See `examples/AssetBubble/Rule/players.py` lines 100-200 for MomentumSpeculator class showing rule-based implementation structure.

**Reference**: See `examples/AssetBubble/LLM/prompts.py` lines 15-36 for LLMGreaterFoolSpec system prompt showing persona design.

**Step 2.2.2: Agent Diversity Check**

Ensure your investor set has:

1. **Different time horizons** - Some fast, some slow
2. **Different information processing** - Some technical, some fundamental
3. **Different risk attitudes** - Some conservative, some aggressive
4. **Conflicting strategies** - Some buy when others sell
5. **Different market impacts** - Some small, some large

**Reference**: AssetBubble has 5 investor types (see `configs/AssetBubble/Rule/players.yml`):
- MomentumSpeculator (trend follower, destabilizing)
- Fundamentalist (value-based, stabilizing)
- NoiseTrader (random, creates opportunities)
- RationalArbitrageur (corrects mispricings, weakly stabilizing)
- LeveragedSpeculator (amplifies moves, extreme risk)

### 2.3 Communication Design

**Step 2.3.1: Message Flow Design**

```
ROUND STRUCTURE
===============

Step 1: Market broadcasts state
  └─> All investors receive market_update message

Step 2: Each investor processes information
  └─> Extract relevant data
  └─> Apply strategy (rule or LLM)
  └─> Form decision

Step 3: Investors send orders to Market
  └─> order message with action, quantity, price

Step 4: Market aggregates orders
  └─> Calculate net demand
  └─> Apply price formula
  └─> Update state

Step 5: Record and repeat
  └─> Log transactions
  └─> Increment round
```

**Step 2.3.2: Topology Specification**

```
COMMUNICATION TOPOLOGY
======================

Structure: Star (Market center, all investors connected)

Connections:
- Market → Investors: Broadcast market state
- Investors → Market: Send orders

Message Types:
- market_update: [Fields included]
- order: [Fields included]

Frequency: Every round, synchronous
```

**Reference**: See `configs/AssetBubble/Rule/topology.yml` for topology configuration structure.

---

## STEP 3: Create Configuration Files

### 3.1 Configuration Principles

All parameters must be externalized. No hardcoded values in Python code.

**Principle 1**: Every numeric value has a source citation
**Principle 2**: All file paths are relative and consistent
**Principle 3**: Parameters are grouped logically
**Principle 4**: Documentation comments explain each parameter

### 3.2 File Structure

Create these files for each variant (Rule, LLM, RuleLLM, Rag):

```
configs/{SimulationName}/
├── Rule/
│   ├── simulation.yml    # Simulation settings
│   ├── players.yml       # Agent definitions
│   ├── topology.yml      # Communication structure
│   └── persona.yml       # Persistence settings
├── LLM/
│   └── [same 4 files]
├── RuleLLM/
│   └── [same 4 files]
└── Rag/
    └── [same 4 files]
```

### 3.3 simulation.yml Structure

**Reference**: See `configs/AssetBubble/Rule/simulation.yml` for template.

Key sections to populate:

```
simulation.yml STRUCTURE
========================

Header Comments:
- Simulation name and description
- Phenomenon being studied
- Core theories
- Usage instructions

setting:
  name: [simulation identifier]
  description: [detailed description]
  total_rounds: [200-500 typical]
  record_path: [EXPERIMENT/{Sim}/Rule/records]
  storage_path: [EXPERIMENT/{Sim}/Rule/communication]

environment:
  dotenv_path: [.env file location]
  workspace: [project root]

ray:
  namespace: [unique identifier]
  object_store_memory: [536870912 for LLM sims]
  [other Ray settings]

players: !include players.yml
topology: !include topology.yml

communication:
  storage_path: [message storage location]
  record_messages: [true/false]
```

### 3.4 players.yml Structure

**Reference**: See `configs/AssetBubble/Rule/players.yml` for template.

Key sections to populate:

```
players.yml STRUCTURE
=====================

Header Comments:
- Agent architecture overview
- Theory basis

market:
  name: "Market"
  class: "examples.{Sim}.Rule.players:Market"
  num_instances: 1
  config:
    identity: "market"
    role: coordinator
    extras:
      # All market parameters here
      fundamental_value: [with source comment]
      initial_price: [with source comment]
      price_impact: [with source comment]
      mean_reversion: [with source comment]
      [other parameters]

investor_type_1:
  name: [Display name]
  class: "examples.{Sim}.Rule.players:[ClassName]"
  num_instances: [3-5 typical]
  config:
    identity: [code name]
    role: player
    extras:
      # All investor parameters here
      initial_cash: [value]
      initial_position: [value]
      [strategy parameters with source comments]

# Repeat for each investor type
```

### 3.5 topology.yml Structure

**Reference**: See `configs/AssetBubble/Rule/topology.yml` for template.

```
topology.yml STRUCTURE
======================

graph:
  type: star
  center: market

connections:
  - from: market
    to: [list all investor instances]
    bidirectional: true
  
  - from: [investor group]
    to: [market]
    bidirectional: false

broadcast:
  enabled: true
  from: market
  to: all_players
```

### 3.6 persona.yml Structure

**Reference**: See `configs/AssetBubble/Rule/persona.yml` for template.

```
persona.yml STRUCTURE
=====================

market:
  type: proxy
  checkpoint_dir: [path]
  record_path: [path]
  monitoring:
    record_path: [path]

investor_type_1:
  type: player
  checkpoint_dir: [path]
  record_path: [path]
  monitoring:
    record_path: [path]

# Repeat for each agent
```

---

## STEP 4: Implement Code

### 4.1 Rule Variant Implementation

**Step 4.1.1: Create Directory Structure**

```
examples/{SimulationName}/
├── __init__.py
└── Rule/
    ├── __init__.py
    ├── players.py
    ├── run_{name}.py
    └── analysis.py
```

**Step 4.1.2: Implement Market Agent**

**Reference**: Use `examples/AssetBubble/Rule/players.py` lines 41-150 as template.

Structure to implement:

```
Market Agent Implementation
===========================

Module Docstring:
- Phenomenon description
- Theoretical foundation: cite theories WITH simulation-bases.md section numbers
  e.g. "Implements price formation model from simulation-bases.md §3.1"
       "Agent taxonomy defined in simulation-bases.md §4"
- Key dynamics summary (brief — full detail in simulation-bases.md §3.1)
- Note: "See simulation-bases.md for complete theoretical foundation"

Class: Market
-------------

Docstring:
- Purpose
- Price formula: copy the equation from simulation-bases.md §3.1 (one line),
  then write "Full derivation and rationale: simulation-bases.md §3.1"
- Parameter list: for each parameter, write
  "[param_name]: [brief description] — see simulation-bases.md §6 for source and calibration"
- Dynamic properties (1-line each — full economic rationale in simulation-bases.md §3.1)

Methods to implement:

1. perceive()
   - Initialize state on first call
   - Extract orders from observation
   - Call clearing function
   - Update state
   - Log metrics

2. _initialize_market_state()
   - Load parameters from config
   - Set up history buffers
   - Create output directories

3. _extract_orders()
   - Parse inbound messages
   - Validate order format
   - Return list of orders

4. _clear_market()
   - Calculate net demand
   - Apply price impact           # λ term from simulation-bases.md §3.1
   - Apply mean reversion         # γ term from simulation-bases.md §3.1
   - Add noise                    # ε term from simulation-bases.md §3.1
   - Update fundamental
   - Return market result

5. _update_state()
   - Store new price
   - Store new fundamental
   - Update history buffers

6. _log_market_state()
   - Log key metrics
   - Use appropriate log level

7. step()
   - Broadcast market state (fields defined in simulation-bases.md §3.3)
   - Include all relevant metrics
   - Return Action with outbounds
```

**Step 4.1.3: Implement Investor Agents**

**Reference**: Use `examples/AssetBubble/Rule/players.py` lines 150+ for investor templates.

For each investor type:

```
Investor Agent Implementation
=============================

Class Docstring:
- Investor description (1-2 sentences — keep brief)
- Cross-reference: "Theoretical basis: simulation-bases.md §4 — [ClassName] / [Theory Name]"
- Cross-reference: "Strategy specification: simulation-bases.md §4 — Rule-Based Behavior"
- Cross-reference: "Parameters: simulation-bases.md §6"
- Do NOT re-state the full theory or parameter rationale here;
  write "See simulation-bases.md §4 for full investor design specification"

Methods to implement:

1. perceive()
   - Initialize state on first call
   - Extract market info from observation
   - Store in custom_state

2. _initialize_investor_state()
   - Load wealth parameters  (values from simulation-bases.md §6)
   - Load strategy parameters (values from simulation-bases.md §6)
   - Set up history buffers

3. step()
   - Get market info
   - Call decision function
   - Update portfolio state
   - Record wealth
   - Send order message

4. _make_decision()
   - Implement strategy logic (from simulation-bases.md §4 — Rule-Based Behavior)
   - Check all conditions (thresholds from simulation-bases.md §6)
   - Calculate position size (formula from simulation-bases.md §4)
   - Respect constraints
   - Return decision dict
```

**Step 4.1.4: Implement Runner Script**

**Reference**: Use `examples/AssetBubble/Rule/run_bubble.py` as template.

Structure:

```
Runner Script
=============

Docstring:
- Phenomenon description
- Theory basis
- Usage instructions

Implementation:
1. Add project root to sys.path
2. Import run_simulation_with_progress
3. Parse command line arguments
4. Run simulation with progress updates
5. Print completion message
```

**Step 4.1.5: Implement Analysis Script**

**Reference**: Use `examples/AssetBubble/Rule/analysis.py` as template.

Structure:

```
Analysis Script
===============

Functions to implement:

1. load_simulation_data()
   - Read price history
   - Read fundamental history
   - Read volume history
   - Read agent wealth data
   - Return structured data

2. calculate_metrics()
   - Max/min price
   - Max deviation
   - Volatility
   - Average volume
   - [Phenomenon-specific metrics]

3. create_visualizations()
   - Price vs fundamental plot
   - Deviation plot
   - Volume plot
   - Wealth distribution plot
   - [Additional plots]

4. generate_summary_report()
   - Text summary of metrics
   - Interpretation guidance
   - Save to file

5. main()
   - Parse config
   - Load data
   - Calculate metrics
   - Create visualizations
   - Generate report
```

### 4.2 LLM Variant Implementation

**Step 4.2.1: Create Directory Structure**

```
examples/{SimulationName}/
└── LLM/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_llm.py
    └── analysis.py
```

**Step 4.2.2: Implement LLM Investor Agents**

**Reference**: Use `examples/AssetBubble/LLM/players.py` as template.

Structure:

```
LLM Investor Implementation
===========================

Module Docstring:
- Phenomenon
- Design (Market rule-based, Investors LLM)
- LLM provider details
- Usage

Helper Function:
- load_prompt(): Load prompt from module path

Class: Market
-------------
- IDENTICAL to Rule variant
- Copy implementation

Class: LLM{InvestorType}
------------------------

Docstring:
- Personality description
- Psychological profile
- LLM interaction description

Methods:

1. __init__()
   - Initialize LLM client
   - Load prompt paths from config
   - Set generation parameters

2. perceive()
   - Same as Rule variant

3. _initialize_state()
   - Same as Rule variant

4. step()
   - Load system prompt
   - Format user prompt with market data
   - Call LLM API
   - Parse response
   - Validate decision
   - Update state
   - Send order

5. _format_user_prompt()
   - Extract market data
   - Extract portfolio data
   - Fill template variables
   - Return formatted string

6. _validate_decision()
   - Check action validity
   - Enforce quantity limits
   - Respect cash constraints
   - Respect position constraints
   - Return validated decision

7. _update_state()
   - Same as Rule variant
```

**Step 4.2.3: Design LLM Prompts**

**CRITICAL CONSTRAINT**: Prompts must define INVESTOR PERSONALITY ONLY. They must NOT mention the specific phenomenon being simulated.

**Reference**: Use `examples/AssetBubble/LLM/prompts.py` as template.

**CANONICAL OUTPUT FORMAT** (mandatory at end of every system prompt):

```
OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
```

- `<analysis>` tag: chain-of-thought reasoning — market assessment, strategy logic, rationale
- `<decision>` tag: the parseable JSON decision
- **Never use `<think>` tags** — `<think>` is deprecated; `<analysis>` is the canonical tag
- `bid_price` and `quantity` must be numeric literals, not formulas or strings

Structure for each investor type:

```
Prompt Design
=============

System Prompt Structure:

1. Identity Statement
   "You are a [TYPE] in financial markets."

2. Core Belief
   "CORE BELIEF: [One sentence guiding philosophy]"

3. Psychology Description
   "YOUR PSYCHOLOGY: [Mindset, biases, tendencies]"

4. Strategy Framework
   "YOUR STRATEGY:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]"

5. Signal Interpretation
   "HOW YOU INTERPRET MARKET DATA:
    - Price rising: [Interpretation]
    - Price falling: [Interpretation]
    - [Other signals]"

6. Position Sizing
   "POSITION SIZING:
    - Aggressive: [Range] shares
    - Moderate: [Range] shares
    - Conservative: [Range] shares"

7. Risk Profile
   "RISK PROFILE: [Description]"

8. Constraints
   "CONSTRAINTS:
    - Cannot spend more than cash
    - Cannot sell more than owned
    - [Other constraints]"

9. Output Format
   "OUTPUT FORMAT:
    First output your reasoning inside <analysis>...</analysis> tags,
    then output your decision inside <decision>...</decision> tags.
    The decision must be valid JSON:
    {\"action\": \"buy\"|\"sell\"|\"hold\", \"bid_price\": float, \"quantity\": float, \"reasoning\": string}
    IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas."

User Prompt Template:

"Current Market State:
- Price: ${price}
- Fundamental: ${fundamental}
- Deviation: {deviation}
- Recent change: {price_change}

Your Portfolio:
- Cash: ${cash}
- Position: {position} shares
- Value: ${portfolio_value}

[Question prompting decision]"
```

### 4.3 RuleLLM Variant Implementation

**Step 4.3.1: Create Directory Structure**

```
examples/{SimulationName}/
└── RuleLLM/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_rulellm.py
    └── analysis.py
```

**Step 4.3.2: Implement Hybrid Prompts**

**Reference**: Use `examples/AssetBubble/RuleLLM/prompts.py` as template.

Structure:

```
RuleLLM Prompt Design
=====================

System Prompt Structure:

1-7. Same as LLM variant

8. Embedded Rules Section
    "QUANTITATIVE RULES:
     You follow these formulas:
     
     1. [Formula name]:
        [Mathematical expression]
     
     2. [Formula name]:
        [Mathematical expression]
     
     [Additional formulas]"

9. Rule-Judgment Instructions
    "HOW TO USE RULES:
     - Apply formulas to calculate initial values
     - Use judgment to adjust based on context
     - Explain when you follow vs override rules
     - Consider risk management"

10. Output Format
    "OUTPUT FORMAT:
     First output your reasoning inside <analysis>...</analysis> tags,
     then output your decision inside <decision>...</decision> tags.
     The decision must be valid JSON:
     {\"action\": \"buy\"|\"sell\"|\"hold\", \"bid_price\": float, \"quantity\": float, \"reasoning\": string}
     IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas."
    (Identical to LLM variant — always use <analysis> not <think>)
```

**Step 4.3.3: Implement Players**

- Market: IDENTICAL to Rule variant
- Investors: Same structure as LLM variant
- Only difference is prompt content

### 4.4 RAG Variant Implementation

**Step 4.4.1: Create Directory Structure**

```
examples/{SimulationName}/
└── Rag/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_rag.py
    └── analysis.py
```

**Step 4.4.2: Design Knowledge Base**

```
Knowledge Base Design
=====================

Content to Include:
- Historical case studies
- Academic research findings
- Similar market events
- Strategy performance data

Indexing Strategy:
- Vector store per agent type
- Metadata filters
- Top-k retrieval (k=3 typical)

Query Formulation:
- Based on current market state
- Price deviation magnitude
- Volatility level
- Trend direction
```

**Step 4.4.3: Implement RAG Investors**

**Reference**: Use `examples/AssetBubble/Rag/players.py` as template.

Additional methods needed:

```
RAG Investor Additional Methods
===============================

1. _init_knowledge_store()
   - Initialize vector store
   - Set persist directory
   - Load existing index if available

2. _formulate_knowledge_query()
   - Extract key market features
   - Create search query
   - Return query string

3. _format_retrieved_docs()
   - Take retrieved documents
   - Format for prompt inclusion
   - Return context string

Modified step() method:
- Formulate query
- Retrieve documents
- Format context
- Augment system prompt
- Generate decision
```

---

## STEP 5: Validate Design

### 5.1 Design Validation Checklist

**Theory Alignment**
- [ ] Every agent behavior is justified by specific financial theory
- [ ] Every parameter value is backed by empirical research
- [ ] Market mechanism captures key phenomenon dynamics
- [ ] All theories are properly cited

**Agent Diversity**
- [ ] Multiple distinct strategies represented
- [ ] Agents have conflicting incentives
- [ ] Different time horizons present
- [ ] Different risk tolerances present
- [ ] Mix of stabilizing and destabilizing agents

**Phenomenon Specificity**
- [ ] Simulation captures unique aspects of target phenomenon
- [ ] Not generic - has distinctive features
- [ ] Can generate stylized facts from literature
- [ ] Parameters calibrated for phenomenon emergence

**Comparability**
- [ ] Rule and LLM variants use same market mechanism
- [ ] Agent types are roughly equivalent across variants
- [ ] Parameters are calibrated for fair comparison
- [ ] Output metrics are comparable

### 5.2 Prompt Validation Checklist

**LLM Prompts**
- [ ] Define personality only, not phenomenon
- [ ] Core belief is clear and consistent
- [ ] Decision framework is specific
- [ ] Output format is unambiguous
- [ ] Constraints are explicit

**RuleLLM Prompts**
- [ ] Include all quantitative rules
- [ ] Explain rule-judgment balance
- [ ] Rules match Rule variant exactly
- [ ] Examples show rule application

### 5.3 Configuration Validation Checklist

- [ ] All paths are correct and consistent
- [ ] All parameters have source comments
- [ ] No hardcoded values in code
- [ ] YAML syntax is valid
- [ ] All required fields present

---

## STEP 6: Code Quality Check

### 6.1 Code Review Checklist

**Documentation**
- [ ] Module docstrings present with phenomenon and theory
- [ ] Class docstrings present with parameter descriptions
- [ ] Method docstrings present with inputs/outputs
- [ ] Complex formulas have inline comments
- [ ] Variable names are descriptive

**Correctness**
- [ ] Price calculations are numerically stable
- [ ] Division by zero prevented
- [ ] Negative prices prevented
- [ ] Edge cases handled
- [ ] State updates are atomic

**Structure**
- [ ] Methods follow perceive/decide/act pattern
- [ ] Helper functions for complex logic
- [ ] Consistent error handling
- [ ] Appropriate logging

**Performance**
- [ ] No unnecessary computations in loops
- [ ] History buffers have size limits
- [ ] Efficient data structures

### 6.2 Reference File Check

Verify your implementation matches reference structure:

**Market Agent**: Compare to `examples/AssetBubble/Rule/players.py` Market class
**Investor Agents**: Compare to `examples/AssetBubble/Rule/players.py` investor classes
**LLM Investors**: Compare to `examples/AssetBubble/LLM/players.py`
**Prompts**: Compare to `examples/AssetBubble/LLM/prompts.py`
**Runner**: Compare to `examples/AssetBubble/Rule/run_bubble.py`
**Analysis**: Compare to `examples/AssetBubble/Rule/analysis.py`

---

## STEP 7: Create Analysis Tools

### 7.1 Analysis Script Requirements

**Reference**: Use `examples/AssetBubble/Rule/analysis.py` as template.

Functions to implement:

```
Analysis Script Components
==========================

1. Data Loading
   - Load price history from EXPERIMENT/.../market/price
   - Load fundamental history
   - Load volume history
   - Load wealth history for each agent
   - Handle missing data gracefully

2. Metric Calculation
   - Price statistics (max, min, final)
   - Deviation statistics (max, min, mean)
   - Volatility (std of returns)
   - Volume statistics
   - Wealth distribution metrics
   - [Phenomenon-specific metrics]

3. Visualization
   - Price vs fundamental over time
   - Price deviation percentage
   - Trading volume by round
   - Wealth distribution histogram
   - Agent-type performance comparison
   - [Phenomenon-specific plots]

4. Report Generation
   - Text summary of all metrics
   - Interpretation guidance
   - Comparison to expected ranges
   - Save to EXPERIMENT/.../analysis/
```

### 7.2 Testing Strategy

**Unit Tests**
- Test Market price calculation
- Test each investor decision logic
- Test edge cases
- Test data loading

**Integration Tests**
- Run short simulation (10 rounds)
- Verify all agents participate
- Verify data is recorded
- Verify analysis runs

**Validation Tests**
- Check phenomenon emerges
- Verify metrics in reasonable ranges
- Compare to historical data

---

## STEP 8: Create Documentation

> **All documentation follows the MANDATORY FILE STRUCTURE defined at the top of this guide.**
> Write `simulation-bases.md` and `analysis-bases.md` once at the root level,
> then write `explain.md` and `analysis.md` per variant.

### 8.1 Root Documents (Written Once)

#### 8.1.1 simulation-bases.md

**Location**: `examples/{SimulationName}/simulation-bases.md`

Follow the specification in **ROOT DOCUMENT SPECIFICATIONS → simulation-bases.md** above.

Key writing guidance:
- Write this **before** any code. The design in this document drives all implementations.
- Every investor type defined here must have a corresponding class in all four `players.py` files.
- Every parameter value must have a source citation.
- Sections 3 (Market Design) and 4 (Investor Taxonomy) are the most critical — spend the most time here.
- Section 9 (Variant Comparison Preview) should be revisited and updated after all variants are implemented.

**Reference**: See `examples/AssetBubble/LLM/explain.md` for the style of theory-to-implementation mapping.

#### 8.1.2 analysis-bases.md

**Location**: `examples/{SimulationName}/analysis-bases.md`

Follow the specification in **ROOT DOCUMENT SPECIFICATIONS → analysis-bases.md** above.

Key writing guidance:
- Write this alongside `simulation-bases.md`, before implementing `analysis.py`.
- Every metric in Section 2 must be implemented in every variant's `analysis.py`.
- Section 6 (Expected Results) should cite specific values from literature — these serve as calibration targets.
- At minimum include: price deviation, phenomenon intensity, volatility, portfolio metrics, volume, and one phenomenon-specific metric.

**Reference**: See `examples/AssetBubble/LLM/analysis.md` for style reference.

### 8.2 Per-Variant Documents (Written Four Times)

#### 8.2.1 {Variant}/explain.md

**Location**: `examples/{SimulationName}/{Variant}/explain.md` (Rule, LLM, RuleLLM, Rag)

Follow the specification in **VARIANT DOCUMENT SPECIFICATIONS → {Variant}/explain.md** above.

Key writing guidance:
- Write this **immediately after implementing** the variant's `players.py` — it documents implementation decisions while they are fresh.
- **NEVER duplicate `simulation-bases.md` content.** Every piece of theory, parameter rationale, and economic reasoning belongs in `simulation-bases.md`. This file only records *how the code maps to that design*.
- **Always cite exact sections**: use the form `"simulation-bases.md §N.M"` whenever pointing to a theory, parameter, investor spec, or historical event. The reader will go to `simulation-bases.md` for depth; they come here only for implementation tracing.
- Section 2 (Theory → Implementation Mapping) is the most important: every theoretical design element must trace to a specific code location using `simulation-bases.md §` references.
- Section 3 (Market Mechanism): copy the formula equation from `simulation-bases.md §3.1`, then map each symbol to its Python variable and config path. Do not re-explain the formula.
- Section 4 (Variant-Specific Features): cite `simulation-bases.md §9` to justify why this variant's choices differ from others.
- The Architecture Diagram must accurately reflect actual message flow, not just conceptual design.
- For LLM variants: cite `simulation-bases.md §4 LLM Persona` for each investor's prompt source.
- For Rag variant: cite `simulation-bases.md §8` as the source of knowledge base content.

**Reference**: `examples/AssetBubble/LLM/explain.md` demonstrates the complete structure.

#### 8.2.2 {Variant}/analysis.md

**Location**: `examples/{SimulationName}/{Variant}/analysis.md` (Rule, LLM, RuleLLM, Rag)

Follow the specification in **VARIANT DOCUMENT SPECIFICATIONS → {Variant}/analysis.md** above.

Key writing guidance:
- Write this **after implementing** the variant's `analysis.py` — document what the script actually does.
- For every analysis dimension, specify the exact function in `analysis.py` that implements it.
- Section 4 (Variant-Specific Observable Phenomena) is critical: what unique behaviors can only be observed in this variant?
- LLM variant `analysis.md` must document reasoning variability and how to analyze LLM decision quality.
- Rag variant `analysis.md` must document how retrieval quality affects outcomes.

**Reference**: `examples/AssetBubble/LLM/analysis.md` demonstrates the structure.

### 8.3 Documentation Completion Order

```
Recommended writing order:

1. simulation-bases.md          ← Design first (before any code)
2. analysis-bases.md            ← Plan analysis alongside design
3. Rule/players.py              ← Implement first variant
4. Rule/explain.md              ← Document immediately after
5. Rule/analysis.py             ← Implement analysis
6. Rule/analysis.md             ← Document immediately after
7. (Repeat steps 3-6 for LLM, RuleLLM, Rag)
8. Update simulation-bases.md   ← Revise Section 9 with real variant comparison
   Section 9 Variant Preview
```

---

## STEP 9: Execute and Debug

### 9.1 Execution Steps

```
Execution Workflow
==================

Step 1: Run Rule variant
  $ python examples/{Sim}/Rule/run_{name}.py \\
      -c configs/{Sim}/Rule/simulation.yml

Step 2: Check outputs
  $ ls EXPERIMENT/{Sim}/Rule/records/
  Verify files created

Step 3: Run analysis
  $ python examples/{Sim}/Rule/analysis.py \\
      -c configs/{Sim}/Rule/simulation.yml

Step 4: View results
  $ open EXPERIMENT/{Sim}/Rule/analysis/analysis_summary.png

Step 5: Run LLM variant (if API key available)
  $ python examples/{Sim}/LLM/run_{name}_llm.py \\
      -c configs/{Sim}/LLM/simulation.yml

Step 6: Compare variants
  Run analysis on both
  Compare metrics
```

### 9.2 Common Issues and Solutions

| Issue                  | Diagnosis            | Solution                       |
|------------------------|----------------------|--------------------------------|
| Simulation won't start | Check YAML syntax    | Validate YAML online           |
| Import errors          | Check sys.path       | Verify project structure       |
| No trading             | Check thresholds     | Relax conditions               |
| Price goes negative    | Check floor          | Add max(price, 0.01)           |
| LLM invalid JSON       | Check prompt clarity | Strengthen format instructions |
| Too slow               | Check agent count    | Reduce num_instances           |
| No phenomenon          | Check parameters     | Calibrate to literature        |

### 9.3 Debugging Strategy

```
Debugging Workflow
==================

1. Test Market alone
   - Create minimal simulation
   - Only Market agent
   - Verify price dynamics

2. Add one investor type
   - Test in isolation
   - Verify decisions
   - Check state updates

3. Add remaining investors
   - One at a time
   - Verify interactions

4. Full simulation
   - Short run (10 rounds)
   - Check all outputs
   - Verify phenomenon emerges

5. Production run
   - Full rounds
   - All variants
   - Complete analysis
```

---

## STEP 10: Final Review

### 10.1 Completeness Checklist

**Root Documentation**
- [ ] `simulation-bases.md` exists at `examples/{SimulationName}/simulation-bases.md`
- [ ] `simulation-bases.md` contains all 9 required sections
- [ ] Every investor type in Section 4 has a corresponding class in all four `players.py` files
- [ ] Every parameter in Section 6 has a source citation
- [ ] Section 9 (Variant Comparison Preview) updated after all variants complete
- [ ] `analysis-bases.md` exists at `examples/{SimulationName}/analysis-bases.md`
- [ ] `analysis-bases.md` contains all 7 required sections
- [ ] At least 6 metrics defined in Section 2 (including all minimum required metrics)
- [ ] At least 3 analysis dimensions defined in Section 3
- [ ] Section 6 (Expected Results) has calibration targets with source citations

**Code**
- [ ] Rule/ players.py implements all agents
- [ ] Rule/ run script works
- [ ] Rule/ analysis.py generates plots
- [ ] LLM/ prompts.py has all personalities
- [ ] LLM/ prompts.py uses `<analysis>` tag (not `<think>`) in output format
- [ ] LLM/ prompts.py decision JSON includes `bid_price`, `quantity`, `reasoning` fields
- [ ] LLM/ players.py handles responses
- [ ] RuleLLM/ hybrid prompts complete
- [ ] RuleLLM/ prompts.py uses `<analysis>` tag in output format
- [ ] Rag/ knowledge retrieval implemented
- [ ] Rag/ prompts.py uses `<analysis>` tag in output format
- [ ] All __init__.py files present

**Per-Variant Documentation (verify for Rule, LLM, RuleLLM, Rag)**
- [ ] `{Variant}/explain.md` exists
- [ ] `explain.md` Section 2: every investor type mapped to code location
- [ ] `explain.md` Section 3: price formula implementation documented
- [ ] `explain.md` Section 4: variant-specific features documented
- [ ] `explain.md` Section 5: Architecture Diagram present and accurate
- [ ] `explain.md` Section 7: Running Instructions complete
- [ ] `{Variant}/analysis.md` exists
- [ ] `analysis.md` Section 2: every metric from `analysis-bases.md` mapped to `analysis.py` function
- [ ] `analysis.md` Section 3: all analysis dimensions implemented
- [ ] `analysis.md` Section 4: variant-specific observable phenomena documented
- [ ] `analysis.md` Section 6: all output files listed

**Configuration**
- [ ] All simulation.yml files valid
- [ ] All players.yml files valid
- [ ] All topology.yml files valid
- [ ] All persona.yml files valid
- [ ] Paths correct in all files
- [ ] Parameters documented

**Integration**
- [ ] SCENARIO_PATH_MAP updated
- [ ] WebUI discovers simulation
- [ ] Paths use nested structure
- [ ] All imports resolve

### 10.2 Quality Standards

**Theory Quality**
- Every claim backed by citation
- Parameters from empirical research
- Mechanisms justified by theory

**Code Quality**
- Follows project conventions
- Well-documented
- Handles errors gracefully
- Efficient implementation

**Documentation Quality**
- Clear and comprehensive
- Properly formatted
- Examples included
- Accessible to newcomers

**Reproducibility**
- All parameters externalized
- Random seeds documented
- Environment specified
- Results verifiable

---

## Reference: AssetBubble Implementation

Use AssetBubble as the primary reference for all implementation details:

### Key Reference Files

| Component         | Reference File                                      |
|-------------------|-----------------------------------------------------|
| Market Agent      | `examples/AssetBubble/Rule/players.py` lines 41-150 |
| Investor Agents   | `examples/AssetBubble/Rule/players.py` lines 150+   |
| LLM Investors     | `examples/AssetBubble/LLM/players.py`               |
| LLM Prompts       | `examples/AssetBubble/LLM/prompts.py`               |
| RuleLLM Prompts   | `examples/AssetBubble/RuleLLM/prompts.py`           |
| RAG Investors     | `examples/AssetBubble/Rag/players.py`               |
| Runner Script     | `examples/AssetBubble/Rule/run_bubble.py`           |
| Analysis Script   | `examples/AssetBubble/Rule/analysis.py`             |
| Simulation Config | `configs/AssetBubble/Rule/simulation.yml`           |
| Players Config    | `configs/AssetBubble/Rule/players.yml`              |
| Topology Config   | `configs/AssetBubble/Rule/topology.yml`             |
| Persona Config    | `configs/AssetBubble/Rule/persona.yml`              |
| Documentation     | `examples/AssetBubble/Rule/explain.md`              |
| Analysis Guide    | `examples/AssetBubble/Rule/analysis.md`             |

### AssetBubble Key Patterns

**Price Formula Pattern**:
```
P(t+1) = P(t) + λ×NetDemand + γ×[F-P(t)] + ε
```

**Agent Decision Pattern**:
1. Perceive: Extract market info
2. Decide: Apply strategy (rule or LLM)
3. Act: Send order, update state

**Prompt Structure Pattern**:
1. Identity
2. Core Belief
3. Psychology
4. Strategy
5. Constraints
6. Output Format

**Configuration Pattern**:
- All parameters in extras
- Source comments on each
- Consistent path structure

---

## Conclusion

This guide provides a complete methodology for creating financial market simulations. By following the 10 steps and referencing the AssetBubble implementation, you can create rigorous, theory-grounded simulations.

Remember:
1. Ground everything in academic research
2. Document all parameters and their sources
3. Test incrementally
4. Validate against stylized facts
5. Document thoroughly for reproducibility

For questions, refer to the AssetBubble reference files and the troubleshooting section.
