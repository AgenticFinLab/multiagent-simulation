# Variant Document Specifications

## Purpose

This file defines the complete content specifications for the two per-variant documents that every simulation variant must have:

1. **`{Variant}/explain.md`** — 9-section implementation guide (traces design to code)
2. **`{Variant}/analysis.md`** — 7-section analysis guide (traces metrics to functions)

These documents are written **once per variant declared `Yes` in target §10.1** (finance default: Rule, LLM, RuleLLM, Rag; other domains may declare a different scheme). They inherit from the root documents (`simulation-bases.md`, `analysis-bases.md`) and specify how each variant concretely implements the shared design.

---

## Critical Cross-Reference Principle

> `explain.md` and `analysis.md` must NOT duplicate content from `simulation-bases.md` or `analysis-bases.md`.
> Instead, **cite the exact section** using `simulation-bases.md §N.M` notation, then explain only the implementation detail.

**Wrong** (duplicates theory):
> "ConcentratedFund represents a TRS-leveraged fund. TRS allows synthetic exposure without filings..."

**Correct** (traces implementation):
> "ConcentratedFund — theory in simulation-bases.md §4.1. Implementation: `_make_decision()` checks `deviation < self.state.custom_state['leverage_trigger']` (loaded from `extras.leverage_trigger` in players.yml)."

The reader goes to `simulation-bases.md §4.1` for depth. They come here only for the specific code tracing.

---

## Part I: `{Variant}/explain.md` — Implementation Guide

**Location**: `examples/{SimulationName}/{Variant}/explain.md`

**Writing timing**: Write immediately after implementing this variant's `players.py`. Document implementation decisions while fresh.

---

### §1 Variant Overview

```markdown
# {SimulationName} {Variant} — Implementation Explanation

## 1. Overview

| Item                               | Description                                                                                         |
|------------------------------------|-----------------------------------------------------------------------------------------------------|
| Variant                            | [Rule / LLM / RuleLLM / Rag]                                                                        |
| Implements                         | `../simulation-bases.md`                                                                            |
| Decision Logic                     | [Fixed formulas / LLM prompts / Formula-anchored LLM / RAG-augmented LLM]                           |
| Key Difference from Other Variants | [1-2 sentences: what makes this variant unique]                                                     |
| Primary Research Contribution      | [What unique insight running this variant enables]                                                  |
| Files                              | `players.py`, `run_{name}[_suffix].py`, `analysis.py`, `explain.md`, `analysis.md` [, `prompts.py`] |
```

---

### §2 Theory → Implementation Mapping

This section is the core of `explain.md`. For EACH agent type from `simulation-bases.md §4` (finance appendix relabels §4 as "Investor Taxonomy"):

```markdown
### {ClassName}: Theory → Implementation Mapping

> Theory defined in simulation-bases.md §4.{N}. Do NOT re-state theory here.

| Design Element (from simulation-bases.md)   | Implementation in This Variant                                                                        |
|---------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Theoretical basis → sim-bases §4.{N}.3      | Class: `{ClassName}` in `players.py`; docstring cites sim-bases §4.{N}                                |
| Behavioral mechanism → sim-bases §4.{N}.5.2 | Method: `_make_decision()` lines [L1–L2]; [brief description of implementation]                       |
| Mathematical model → sim-bases §4.{N}.5.4   | Trigger: `deviation < self.state.custom_state['threshold']`; Sizing: `quantity = position * fraction` |
| State variables → sim-bases §4.{N}.5.4      | [Variable name in code] → initialized in `_initialize_investor_state()`                               |
| Parameters → sim-bases §6                   | Loaded from `extras.[param_name]` in `players.yml`; default = [value]                                 |
| Activation triggers  → sim-bases §4.{N}.4   | [Which `if/elif` branch corresponds to which scenario]                                                |
```

**For LLM variant — additional row**:
| LLM persona → sim-bases §4.{N}.5.5 (Behavioral Properties) | System prompt: `[PROMPT_CONSTANT_NAME]` in `prompts.py` |

**For RuleLLM variant — additional rows**:
| Behavioral mechanism → sim-bases §4.{N}.5.2 | `== DECISION RULES ==` section in `[PROMPT_CONSTANT_NAME]` embeds the mechanism narrative as quantitative rules |
| Mathematical model → sim-bases §4.{N}.5.4 | Step-by-step rule text in prompt mirrors the formula from sim-bases §4.{N}.5.4 |

**For Rag variant — additional row**:
| Historical case → sim-bases §8 | Knowledge base content derived from sim-bases §8; docs in `configs/{Sim}/Rag/docs/` |

---

### §3 Environment Mechanism Implementation

```markdown
## 3. Environment Mechanism Implementation

### State Dynamics Implementation

Formula source: simulation-bases.md §3.1

<!-- Finance appendix (§4.1.F) instantiation shown below. Non-finance domains: replace the price
     formula with the state-update law from their §4.1.{X} appendix (opinion: bounded confidence
     update; epidemics: SIR / SEIR update; sociology: adoption threshold rule); replace
     Market._clear_market() with the appropriate coordinator method name. -->

```
P(t+1) = P(t) + λ·D(t) + γ·[F(t)−P(t)] + ε(t)
```

Implemented in: `players.py → Environment.update()` (finance appendix instantiation:
`Market._clear_market()`)

Code translation:
| sim-bases symbol | Python variable     | Config path                | Default |
|------------------|---------------------|----------------------------|---------|
| λ (lambda)       | `price_impact`      | `extras.price_impact`      | [value] |
| γ (gamma)        | `mean_reversion`    | `extras.mean_reversion`    | [value] |
| F (fundamental)  | `self._fundamental` | `extras.fundamental_value` | [value] |
| ε(t)             | `noise`             | `extras.noise_std` (σ)     | [value] |
| D(t)             | `net_demand`        | computed from actions      | —       |

Additional mechanisms: simulation-bases.md §3.2
[For each mechanism: mechanism name → implementing method → config parameter]

Deviations from simulation-bases.md design:
[None — OR — list specific approximations with rationale]
```

---

### §4 Variant-Specific Features

Document what is **unique** to this variant. Cite `simulation-bases.md §9` to justify each choice.

**For Rule variant**:
```markdown
## 4. Rule Variant-Specific Features

**Deterministic formulas** (motivated by sim-bases §9 — "establish deterministic baseline"):
For each agent:
- [ClassName]: Decision encoded as [formula description]; threshold loaded from config;
  no randomness beyond market noise ε(t). See `players.py → {ClassName}._make_decision()`.

**Parameter traceability**: Every threshold traces to §6 parameter table.
Every parameter in §6 has a source citation; see `configs/{Sim}/Rule/players.yml` comments.
```

**For LLM variant**:
```markdown
## 4. LLM Variant-Specific Features

**Personality-only prompts** (motivated by sim-bases §9 — "test LLM behavioral realism"):
- Prompts define investor character WITHOUT naming the phenomenon or stating the price formula.
- System prompts describe [N] distinct investor personalities (see `prompts.py`).
- LLM discovers market dynamics from `{price, fundamental, deviation}` data alone.

**Prompt design choices** (derived from sim-bases §4.{N}.5.5 Behavioral Properties):
| Agent       | Prompt Constant | Persona Element → sim-bases §4.{N}.5.5 |
|-------------|-----------------|----------------------------------------|
| [ClassName] | [CONST_NAME]    | [Key trait → citation in sim-bases]    |

**Output parsing**: `<analysis>...</analysis><decision>{"action":..., "bid_price":..., "quantity":..., "reasoning":...}</decision>`
```

**For RuleLLM variant**:
```markdown
## 4. RuleLLM Variant-Specific Features

**Dual-section prompts** (motivated by sim-bases §9 — "isolate LLM reasoning effect"):
Every system prompt has:
  == PERSONA == : Character, risk style, emotional traits (same as LLM variant)
  == DECISION RULES == : Exact formulas from sim-bases §4.{N}.5.4, expressed in plain text

**Rule embedding fidelity** (derives from sim-bases §4.{N}.5.4):
| Agent       | Rule in sim-bases §4.{N}.5.4 | Embedded as text in == DECISION RULES == |
|-------------|------------------------------|------------------------------------------|
| [ClassName] | [Formula]                    | [How it is phrased in the prompt]        |

**Adherence target**: N/A — the embedded rules serve as deeper investor characterization (knowledge, habits, decision-making framework), not as executable mandates. The LLM uses them as guidance alongside its persona.
```

**For Rag variant**:
```markdown
## 4. Rag Variant-Specific Features

**Per-agent knowledge stores** (motivated by sim-bases §9 — "test domain knowledge effect"):
Each agent type has its own `KnowledgeStore` — not shared.

**Knowledge base content** (derived from sim-bases §8 Historical Case Studies):
| Agent       | Knowledge source          | Content type                        | Relevance                                |
|-------------|---------------------------|-------------------------------------|------------------------------------------|
| [ClassName] | sim-bases §8 [Event name] | [e.g., timeline, quantitative data] | [Why relevant to this agent's decisions] |

**Retrieval query strategy**: `_formulate_knowledge_query()` uses [deviation / price / round] to form queries.
**Fallback**: If no documents retrieved → `"(No relevant knowledge retrieved this round.)"` injected into `{rag_context}`.
**Retrieval target**: ≥70% success rate (measured by `analyze_rag_knowledge_effect()`).
```

---

### §5 Architecture Diagram

```markdown
## 5. Architecture Diagram

[ASCII diagram showing actual message flow. Must be accurate to implemented code, not conceptual.]

### Rule / LLM / RuleLLM Topology (Environment coordinator + N agents):

<!-- Finance appendix (§4.1.F) instantiation: rename "Environment Coordinator" → "Market",
     "update() → state-broadcast" → "_clear_market() → P(t+1) formula",
     broadcast payload → "{price, fundamental, ...}", "actions → coordinator.perceive()" →
     "orders → Market.perceive()". Non-finance domains keep the neutral labels. -->

```
         ┌─────────────────────────────────────────────┐
         │       Environment Coordinator (1 instance)  │
         │   update() → state-broadcast per §3.1       │
         │   Broadcasts: {state, anchor, deviation, …} │
         └────────────┬────────────────────────────────┘
                      │ broadcast (round start)
          ┌───────────┼────────────────┐
          ▼           ▼                ▼
    ┌──────────┐ ┌──────────┐  ┌──────────────┐
    │ Agent A  │ │ Agent B  │  │  Agent C     │
    │ perceive │ │ perceive │  │  perceive    │
    │ decide   │ │ decide   │  │  [LLM call]  │
    │ act      │ │ act      │  │  act         │
    └────┬─────┘ └────┬─────┘  └──────┬───────┘
         │            │               │
         └────────────┴───────────────┘
              actions → coordinator.perceive()
```

### Rag variant — additional retrieval flow:

```
Coordinator broadcast → Agent.perceive()
                        │
                        ▼
         Agent._formulate_knowledge_query(deviation, state)
                        │
                        ▼
         KnowledgeStore.query(q, top_k=3) → retrieved_docs
                        │
                        ▼
         Agent._build_prompt(env_data, retrieved_docs)
                        │ {rag_context} injected
                        ▼
         LLM API call → <analysis>...<decision>{...}</decision>
```
```

---

### §6 Configuration Reference

```markdown
## 6. Configuration Reference

Key Configuration Parameters (`configs/{SimulationName}/{Variant}/players.yml`):

| Parameter | Config Path     | Value   | Design Justification                                             |
|-----------|-----------------|---------|------------------------------------------------------------------|
| [param]   | `extras.[name]` | [value] | [Why this value implements simulation-bases.md §4.{N}.5.4 or §6] |
```

**For Rag variant, additional block**:
```markdown
RAG configuration per agent (`players.yml`):
| Parameter       | Path                         | Value        | Purpose                                          |
|-----------------|------------------------------|--------------|--------------------------------------------------|
| docs_dir        | `extras.rag.docs_dir`        | [path]       | Source documents for this agent's KnowledgeStore |
| rag_persist_dir | `extras.rag.rag_persist_dir` | [path]       | Where to save/load vector index                  |
| embed_model     | `extras.rag.embed_model`     | [model name] | Embedding model for indexing                     |
| top_k           | `extras.rag.top_k`           | [int]        | Number of chunks retrieved per query             |
```

---

### §7 Running Instructions

```markdown
## 7. Running Instructions

### Execution Command

```bash
python examples/{SimulationName}/{Variant}/run_{name}[_suffix].py \
    -c configs/{SimulationName}/{Variant}/simulation.yml
```

### Required Environment Variables

| Variable   | Purpose                          | Where to Obtain   |
|------------|----------------------------------|-------------------|
| [VAR_NAME] | [What it is — e.g., LLM API key] | [Where to get it] |

### Expected Runtime

| Rounds | Agents | Estimated Time                              |
|--------|--------|---------------------------------------------|
| 200    | [N]    | [estimate for Rule; LLM/Rag will be longer] |

### Output Location

All outputs written to: `EXPERIMENT/{SimulationName}/{Variant}/`

| Subdirectory     | Contents                                        |
|------------------|-------------------------------------------------|
| `records/`       | Per-round environment and agent state logs      |
| `communication/` | Raw message logs                                |
| `analysis/`      | Plots and reports (after running `analysis.py`) |
```

---

### §8 Expected Behavior Patterns

```markdown
## 8. Expected Behavior Patterns

| Phase          | Rounds  | Expected Agent Behavior                             | Expected State Dynamics                                 |
|----------------|---------|-----------------------------------------------------|---------------------------------------------------------|
| [Phase 1 name] | [Range] | [Which agents are active; what decisions they make] | [State movement direction and magnitude]                |
| [Phase 2 name] | [Range] | [Agent behaviors in this phase]                     | [Dynamics]                                              |
| [Phase 3 name] | [Range] | [Agent behaviors]                                   | [Recovery or continuation]                              |

<!-- Finance appendix (§4.1.F) instantiation: relabel "State Dynamics" → "Price Dynamics";
     "State movement" → "Price movement". -->

**Variant-specific deviations from expected behavior**:
[For each non-baseline variant declared in target §10.1: what specific behavioral differences from
the baseline variant are expected, and why (based on sim-bases §9 and this variant's design
choices).]
```

---

### §9 References

```markdown
## 9. References

[Do NOT repeat full citations already listed in simulation-bases.md §2.]
[For shared references, write: "See simulation-bases.md §2 — [Theory Name]"]
[List ONLY references that are new to this variant.]

| Source                                        | New to This Variant | Note              |
|-----------------------------------------------|---------------------|-------------------|
| See simulation-bases.md §2 — [Theory A]       | No                  | Shared foundation |
| [New citation for variant-specific technique] | Yes                 | [What this adds]  |
```

---

## Part II: `{Variant}/analysis.md` — Analysis Guide

**Location**: `examples/{SimulationName}/{Variant}/analysis.md`

**Writing timing**: Write after implementing this variant's `analysis.py`.

---

### §1 Analysis Overview

```markdown
# {SimulationName} {Variant} — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                       |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                            |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                   |
| Output Location                 | `EXPERIMENT/{SimulationName}/{Variant}/analysis/`                                                                                                 |
| Imports From                    | [Rule: "authoritative" / LLM/RuleLLM/Rag: "imports `load_simulation_data`, `calculate_metrics`, `create_visualizations` from `Rule/analysis.py`"] |
| Variant-Specific Functions      | [None / `analyze_rag_knowledge_effect()`]                                                                                                         |
| Variant-Specific Considerations | [Key differences that affect how to interpret results for this variant]                                                                           |
```

---

### §2 Metric Implementation

For EACH metric from `analysis-bases.md §2`:

```markdown
### Metric: [Name]

- **Defined in**: `analysis-bases.md §2 — [Metric Name]`
- **Implemented in**: `analysis.py → calculate_metrics()` (for Rule) or `Rule/analysis.py → calculate_metrics()` (for other variants)
- **Data source**: `EXPERIMENT/{Sim}/{Variant}/records/[file_pattern]`
- **Implementation details**:
  ```python
  # [Brief code sketch showing how the metric is computed]
  ```
- **Variant-specific notes**: [Any differences in how this metric behaves for this variant.
  Examples:
  - "LLM variant shows higher variance due to stochastic LLM decisions"
  - "RuleLLM variant: same core metrics as Rule; embedded rules deepen investor characterization"
  - "Rag variant: retrieval success rate from `analyze_rag_knowledge_effect()` is an additional metric"]
- **Expected range for this variant**: [Min, Max based on calibration — may differ from analysis-bases §6 range]
```

---

### §3 Dimension-by-Dimension Analysis

For EACH dimension from `analysis-bases.md §3`:

```markdown
### Dimension [N]: [Name]

**Objective** (from analysis-bases.md §3.{N}): [Copy the purpose statement]

**Implementation in `analysis.py`**:
- Function: `[function_name]()`
- Input data: [Which files are loaded; data format]
- Computation: [Brief description of how the dimension is computed]
- Output: [Plot filename(s); report section identifier]

**Variant-Specific Interpretation**:
[How to read this dimension's results for THIS specific variant.
What patterns are expected that differ from other variants.
What constitutes a "successful" result for this variant.]

**Expected Output Description**:
[Text description of what the chart or table should look like when the simulation works correctly.
Be specific enough that a reader can tell if a result is correct or anomalous.]
```

---

### §4 Variant-Specific Observable Phenomena

Document phenomena that are **unique to this variant** and not visible in others:

```markdown
## 4. Variant-Specific Observable Phenomena

| Phenomenon | Description                             | How to Observe                   | Contrast with Baseline Variant |
|------------|-----------------------------------------|----------------------------------|--------------------------------|
| [Name]     | [What it is — specific to this variant] | [Which metric or chart shows it] | [What differs from baseline]   |
```

**By variant type**:
- **Rule**: Exact formula-driven thresholds; deterministic phase transitions; no randomness beyond ε(t)
- **LLM**: Reasoning variability across runs; emergent caution after observed price drops; narrative framing effects; inconsistent threshold adherence
- **RuleLLM**: Embedded rules as deeper investor characterization; comparison of LLM reasoning quality with and without explicit quantitative guidance
- **Rag**: Effect of knowledge retrieval on decisions; `analyze_rag_knowledge_effect()` output; comparison of decisions with vs. without retrieved context

---

### §5 Scaling and Sensitivity Analysis

```markdown
## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for  |
|--------------|---------------------|--------------------|------------------|
| 100          | [What can be seen]  | Low                | Quick testing    |
| 200          | [What can be seen]  | Medium             | Standard runs    |
| 500          | [What can be seen]  | High               | Research quality |

### Agent Count Scaling

| Agent Count      | Expected Observable | Environment Dynamics |
|------------------|---------------------|----------------------|
| [Minimum viable] | [What works]        | [Dynamics]           |
| [Recommended]    | [Full phenomenon]   | [Dynamics]           |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|-----------|--------|--------------------------------------------|
| [param]   | +50%   | [Effect]                                   |
| [param]   | −50%   | [Effect]                                   |
```

---

### §6 Output Files Reference

```markdown
## 6. Output Files Reference

All outputs written to: `EXPERIMENT/{SimulationName}/{Variant}/analysis/`

| Output File    | Generated By      | Contents         | How to Interpret                               |
|----------------|-------------------|------------------|------------------------------------------------|
| [filename.png] | [function_name()] | [What's in it]   | [How to read it; what good vs. bad looks like] |
| [report.txt]   | [function_name()] | [Metric summary] | [Key numbers to look at first]                 |
```

---

### §7 Cross-Variant Comparison Notes

```markdown
## 7. Cross-Variant Comparison Notes

This variant's expected position in cross-variant comparison (from analysis-bases.md §5):

| Comparison Axis        | This Variant's Expected Position                    | Reason                                                |
|------------------------|-----------------------------------------------------|-------------------------------------------------------|
| Phenomenon onset speed | [Faster / Same / Slower than baseline variant]      | [Mechanism explanation]                               |
| Phenomenon intensity   | [Higher / Same / Lower than baseline variant]       | [Mechanism explanation]                               |
| Behavioral realism     | [Assessment]                                        | [Why more or less realistic than other variants]      |
| Decision quality       | [Outcome distribution vs. baseline]                 | [Which agent types benefit from this variant's logic] |
```
