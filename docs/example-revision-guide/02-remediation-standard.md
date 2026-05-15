# Remediation Standard

## Purpose

This file defines the **compliance criteria** for every file type in a simulation. A file is "compliant" only if it satisfies every criterion in the relevant section. These criteria are the authoritative standard — used both for auditing (determining what needs repair) and for validating repairs (confirming the work is complete).

All structural requirements reference `docs/create-example-skill/` as the upstream source of truth.

---

## §1 `simulation-bases.md` — 9-Section Standard

### §1.1 Required Sections (in order)

| Section | Title              | Minimum Content                                                                                                                                                   |
|---------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| §1      | Phenomenon         | 2+ paragraphs: historical event, market mechanism, why it matters; **§1.1 Origin and Source Analysis** (see §1.5 below)                                           |
| §2      | Theory             | DOI-cited references for all key theories; **at least 3 theories**, each with the 5-part sub-structure (Citation, Mechanism, Math, Empirical Evidence, Relevance) |
| §3      | Market Design      | Price formation equation; all parameters defined; market role of each participant                                                                                 |
| §4      | Investor Taxonomy  | One entry per investor type, each using the **7-part standard** (see §1.2)                                                                                        |
| §5      | Agent Diversity    | How the combination of agents produces the phenomenon; destabilizing vs. stabilizing                                                                              |
| §6      | Parameter Table    | Every parameter from §4 with: name, value, source citation, justification                                                                                         |
| §7      | Round Structure    | Execution sequence, timing, initialization                                                                                                                        |
| §8      | Historical Cases   | **≥3 real historical episodes** each with: Event Profile, Chronological Dynamics, Quantitative Evidence (≥4 data points), Agent Mappings, Calibration Lessons     |
| §9      | Variant Comparison | Table comparing Rule / LLM / RuleLLM / Rag on decision mechanism and market effect                                                                                |

### §1.2 The 7-Part Investor Standard (mandatory for every §4 entry)

Every investor in §4 must have all 7 parts:

1. **Summary** — 2-sentence description of role and market effect
2. **Theoretical and Empirical Foundation** — ≥2 sources with DOIs; explain the mechanism
3. **Design Purpose and Activation Scenarios** — when this investor activates; what market condition triggers it
4. **Behavioral Framework** — information set, mechanism narrative, mathematical model (formula), behavioral properties
5. **Decision Process Walkthrough** — step-by-step description with example values
6. **Worked Numerical Example** — fully calculated example: inputs → computation → output
7. **Academic References** — complete bibliography for sources cited in this entry

### §1.3 What Must NOT Appear in §4

The following content belongs in variant documents, not in `simulation-bases.md §4`:

| Forbidden Content                                                | Correct Location                                  |
|------------------------------------------------------------------|---------------------------------------------------|
| Rule-Based Behavior (IF/THEN code logic)                         | `Rule/explain.md §2`                              |
| LLM Persona (prompt text, signal interpretation)                 | `LLM/explain.md §2` and `LLM/prompts.py`          |
| RuleLLM Hybrid Notes                                             | `RuleLLM/explain.md §2` and `RuleLLM/prompts.py`  |
| Implementation-specific thresholds with no theoretical grounding | `{Variant}/players.py` and `{Variant}/explain.md` |

### §1.4 Compliance Checklist

- [ ] File exists at `{Path}/simulation-bases.md`
- [ ] Exactly 9 sections present (§1–§9)
- [ ] **§1 contains §1.1 Origin and Source Analysis** with:
  - [ ] §1.1.1 Intellectual Lineage (≥3 paragraphs tracing historical observation → theory → this simulation)
  - [ ] §1.1.2 Real-World Event Catalogue (≥3 events, each with quantitative magnitude and named agent correspondence)
  - [ ] §1.1.3 Book and Practitioner Literature (≥2 entries)
- [ ] **§2 has ≥3 theories**, each with:
  - [ ] Full citation with DOI
  - [ ] Core Theoretical Mechanism narrative (≥3 paragraphs)
  - [ ] Mathematical Formulation with notation table
  - [ ] Empirical Evidence table with quantitative findings
  - [ ] Relevance section naming specific §4 investor numbers
- [ ] §4 has one entry per investor class (count must match `Rule/players.py`)
- [ ] Every §4 entry has all 7 parts
- [ ] §6 parameter table is present with source citations
- [ ] **§8 has ≥3 historical cases**, each with:
  - [ ] Event Profile table (6 rows including Resolution and Sources)
  - [ ] Chronological Dynamics table with quantitative measures
  - [ ] ≥4 quantitative evidence data points with full source citations
  - [ ] Agent Mappings table with all simulation agents covered across cases
  - [ ] Calibration Lessons table linking historical values to §6 parameters
- [ ] §4 contains no Rule/LLM/RuleLLM-specific content

### §1.5 §1 Origin and Source Analysis — Detailed Requirements

The `§1.1` subsection is **non-negotiable** in every `simulation-bases.md`. Its three sub-parts serve distinct roles:

| Sub-part                                | Role                                                   | Key Quality Standard                                                          |
|-----------------------------------------|--------------------------------------------------------|-------------------------------------------------------------------------------|
| §1.1.1 Intellectual Lineage             | Traces the academic genealogy of the phenomenon        | Must be a narrative, not a list — show the chain of influence                 |
| §1.1.2 Real-World Event Catalogue       | Provides empirical grounding and RAG knowledge base    | Every row must have a quantitative Magnitude and a named agent Correspondence |
| §1.1.3 Book and Practitioner Literature | Supplements journal literature with accessible sources | At least one practitioner account (report, memoir, case study)                |

**Event Catalogue specific requirements**:
- Minimum 3 events, recommended 5–7
- Events must span multiple decades (pre-2000, 2000–2015, post-2015 recommended)
- Events must span multiple geographies (US + at least one non-US market)
- Each event must name at least 2 simulation agents in the Correspondence column
- Magnitude must be a number with units (%, $, bps, etc.) — qualitative descriptions fail compliance

---

## §2 `analysis-bases.md` — 7-Section Standard

### §2.1 Required Sections (in order)

| Section | Title                    | Minimum Content                                                                                                                     |
|---------|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| §1      | Objectives               | Research questions this analysis answers; what the simulation is designed to measure                                                |
| §2      | Core Metrics             | ≥6 metrics, each with the **full structured metric entry** (see §2.2 below)                                                         |
| §3      | Analysis Dimensions      | Dimensions across which to compare: agents, phases, variants                                                                        |
| §4      | Phase Analysis           | How the phenomenon unfolds in phases; which metrics are relevant in each phase                                                      |
| §5      | Cross-Variant Comparison | How to compare Rule/LLM/RuleLLM/Rag on the core metrics                                                                             |
| §6      | Expected Results         | **Four sub-sections**: §6.1 Stylised Facts, §6.2 Calibration Targets, §6.3 Cross-Variant Predictions, §6.4 Validation Failure Signs |
| §7      | Visualization Catalogue  | Recommended plots with axis labels and interpretation guidance                                                                      |

### §2.2 Core Metrics Format (§2)

Each metric entry must use the **full structured format** — the minimal 4-field template (Definition + Python + Interpretation + DOI) is no longer compliant. Every metric must include all of the following:

```
### Metric: [Metric Name] ([Abbreviation])

#### Category
[Price Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific / Agent Activity / Microstructure]

#### Definition
[Unambiguous plain-language definition — what, over what window, against what reference]

#### Formula
[Equation with notation table; every symbol defined]

**Computation notes**: [edge cases, data source, NaN handling]

**Python function**:
def metric_name(...) -> float:
    """[One-line description].

    Args:
        [arg]: [description with units]
    Returns:
        [description of return value, units, expected range]
    """

#### Interpretation
| Range | Economic Meaning | Simulation Interpretation |

#### Academic Basis
**Primary source**: [Full citation with DOI + 2–3 sentences on how it establishes this metric]
**Supporting studies**: | Study | Context | Finding | Relevance |

#### Normal Range (from literature)
[Specific numeric range from published literature; source citations]

#### Red Flag Threshold
- **Too high** (> [value]): [diagnosis + adjustment]
- **Too low** (< [value]): [diagnosis + adjustment]
- **Zero for all rounds**: [diagnosis + action]

#### Relationship to Other Metrics
[Correlation direction, timing relationship, cross-metric diagnostic logic]

#### Implementation Notes
[Function name, input source, return type, variant-specific notes]
```

**Mandatory metric types** (must appear in every simulation's `analysis-bases.md`):

| # | Metric Type                      | Rationale                                                             |
|---|----------------------------------|-----------------------------------------------------------------------|
| 1 | Price deviation from fundamental | Primary phenomenon detection metric                                   |
| 2 | Phenomenon intensity measure     | Phenomenon-specific (e.g., bubble ratio, crash depth, bias magnitude) |
| 3 | Volatility metric                | Rolling std of returns or similar; required for risk assessment       |
| 4 | Portfolio / wealth metric        | Tracks agent performance; enables cross-variant comparison            |
| 5 | Volume or activity metric        | Trading intensity proxy; detects silent periods                       |
| 6 | ≥1 phenomenon-specific metric    | Unique to this simulation — not present in generic bubble/crash sims  |

### §2.3 §6 Expected Results Format

The §6 section must contain all four sub-sections:

- **§6.1 Stylised Facts**: table of ≥4 measurable stylised facts with quantitative targets, DOI sources, verification method, and failure indicator
- **§6.2 Calibration Targets**: table of target ranges per metric with lower/upper bound sources; plus the 5-step calibration protocol
- **§6.3 Cross-Variant Predictions**: table comparing Rule / LLM / RuleLLM / Rag expected metric directions with theoretical basis column
- **§6.4 Validation Failure Signs**: table of observable symptoms with diagnosis, root cause, and specific corrective action

### §2.4 Compliance Checklist

- [ ] File exists at `{Path}/analysis-bases.md`
- [ ] Exactly 7 sections present (§1–§7)
- [ ] **§2 has ≥6 metrics**, each with:
  - [ ] Category field
  - [ ] Formula with notation table (every symbol defined)
  - [ ] Interpretation table with ≥3 range rows
  - [ ] Academic Basis: primary source with DOI + supporting studies table (≥2 studies)
  - [ ] Normal Range from literature (numeric, with citations)
  - [ ] Red Flag Threshold (3 scenarios: too high, too low, zero)
  - [ ] Relationship to Other Metrics
  - [ ] Python function with typed Args and Returns docstring
- [ ] **§6 has all four sub-sections** (§6.1, §6.2, §6.3, §6.4)
- [ ] §6.1 has ≥4 stylised facts with quantitative targets and DOI citations
- [ ] §6.2 has calibration targets with source citations for both bounds; includes 5-step protocol
- [ ] §6.3 has cross-variant prediction table covering all 4 variants
- [ ] §6.4 has ≥3 validation failure signs with specific corrective actions
- [ ] §7 visualization catalogue has ≥5 plot descriptions (one per mandatory plot type)

---

## §3 `{Variant}/explain.md` — 9-Section Standard

### §3.1 Required Sections (in order)

| Section | Title                           | Minimum Content                                                                                    |
|---------|---------------------------------|----------------------------------------------------------------------------------------------------|
| §1      | Overview                        | Variant summary table: Variant, Simulation, Decision Mechanism, Theory Reference, Market Broadcast |
| §2      | Theory → Implementation Mapping | One `§2.N` subsection per investor with a 2-column mapping table                                   |
| §3      | Market Mechanism                | Price formula; how it is encoded in this variant                                                   |
| §4      | Variant Architecture            | Component table: base class, inference (if LLM), context, output parsing, retry logic              |
| §5      | Config Reference                | Config file path; key extras listed                                                                |
| §6      | Running Instructions            | `python -m ...` command                                                                            |
| §7      | Expected Behavior               | Bullet list of anticipated metric values and qualitative outcomes                                  |
| §8      | References                      | `See simulation-bases.md §2 for full DOI citations.`                                               |
| §9      | Variant Comparison              | `See simulation-bases.md §9 for Rule / LLM / RuleLLM / Rag comparison table.`                      |

Note: §9 may be omitted for Rule variant (it is the baseline); §4 LLM Architecture section applies only to LLM/RuleLLM/Rag variants.

### §3.2 Theory → Implementation Mapping Table (§2)

Each investor subsection must use this format:

```markdown
### §2.N InvestorClassName (simulation-bases.md §4.N)

| Theory Component                       | Implementation                            |
|----------------------------------------|-------------------------------------------|
| [Theory from simulation-bases.md §4.N] | [Code: class, method, threshold, formula] |
| [Second theory component]              | [Second implementation detail]            |
```

**Rules**:
- The subsection heading must cite `simulation-bases.md §4.N` — the exact section number
- The `Theory Component` column cites the mechanism from `simulation-bases.md`, never re-explains it
- The `Implementation` column gives the concrete code detail: class name, method name, threshold value, formula
- For Rule variant: `Implementation` describes the IF/THEN rule
- For LLM variant: `Implementation` describes the system prompt instruction
- For RuleLLM variant: `Implementation` describes the embedded rule in the prompt
- For Rag variant: `Implementation` describes the RAG query and how retrieved context affects the decision

### §3.3 What Must NOT Appear in explain.md

| Forbidden Content                                    | Reason                                                      |
|------------------------------------------------------|-------------------------------------------------------------|
| Re-explanation of the theory                         | Already in `simulation-bases.md §2` — cite it, don't repeat |
| Agent parameter lists with no implementation mapping | This is `simulation-bases.md §6` content — not here         |
| Shell commands for running all four variants         | Only the current variant's run command belongs              |
| Generic "Agent Descriptions" sections                | Replaced by Theory→Implementation mapping tables            |

### §3.4 Compliance Checklist

- [ ] File exists at `{Path}/{Variant}/explain.md`
- [ ] §1 has the overview table with all 5 rows
- [ ] §2 has one subsection per investor class (count matches `players.py`)
- [ ] Every §2 subsection has a 2-column mapping table
- [ ] Every §2 subsection cites `simulation-bases.md §4.N`
- [ ] §3 has the price formula
- [ ] §7 has expected metric values (not just "varies by scenario")
- [ ] §8 references `simulation-bases.md §2` for citations

---

## §4 `{Variant}/analysis.md` — 5-Section Standard

### §4.1 Required Sections (in order)

| Section | Title                     | Minimum Content                                                                                                |
|---------|---------------------------|----------------------------------------------------------------------------------------------------------------|
| §1      | Analysis Objectives       | What this variant analysis aims to measure or compare                                                          |
| §2      | Metric → Function Mapping | Table of all 7 metrics with function name and `analysis-bases.md §2.X` reference                               |
| §3      | Variant-Specific Notes    | Bullet list of how this variant's mechanism affects each metric                                                |
| §4      | Expected Ranges           | Table: Metric                                                                                                  |
| §5      | References                | `See analysis-bases.md §2 for full metric derivations and simulation-bases.md §4 for agent parameter sources.` |

### §4.2 Metric → Function Mapping Table (§2)

```markdown
| Metric                    | Function                    | analysis-bases.md ref |
|---------------------------|-----------------------------|-----------------------|
| MetricName (Abbreviation) | `function_name(arg1, arg2)` | §2.N                  |
```

All 7 metrics from `analysis-bases.md §2` must appear. The function signature must match exactly what is in `analysis-bases.md §2.N`.

### §4.3 Expected Ranges Table (§4)

```markdown
| Metric | Expected Range | Interpretation                    |
|--------|----------------|-----------------------------------|
| BAI    | 0.5 – 1.5      | 50–150% above fundamental at peak |
```

Must cover all 7 metrics. Never use "Varies by scenario" — provide specific numeric ranges.

### §4.4 Compliance Checklist

- [ ] File exists at `{Path}/{Variant}/analysis.md`
- [ ] §1 states concrete analysis objectives
- [ ] §2 table has all 7 metrics from `analysis-bases.md`
- [ ] §2 table includes `analysis-bases.md §2.X` references for every metric
- [ ] §3 has variant-specific notes (not just generic bullet points)
- [ ] §4 expected ranges are numeric, not "varies by scenario"
- [ ] §5 references both `analysis-bases.md §2` and `simulation-bases.md §4`

---

## §5 `players.py` Docstrings — Citation Standard

### §5.1 Rule Variant — Multi-line Docstring

Every investor class in `Rule/players.py` must have a multi-line docstring in this exact format:

```python
class ClassName(GeneralPlayer):
    """Brief one-line description of the investor.

    Theory: simulation-bases.md §4.N — ClassName
    Theoretical basis: Author (Year) theory name; description of mechanism.
    See simulation-bases.md §4.N for mathematical model.
    """
```

Requirements:
- Line 1: one-line description (ends with `.`)
- Line 2: blank
- Line 3: `Theory: simulation-bases.md §4.N — ClassName` (exact format)
- Line 4: `Theoretical basis: Author (Year) theory name; mechanism description.`
- Line 5: `See simulation-bases.md §4.N for mathematical model.`
- Line 6: closing `"""`

### §5.2 LLM / RuleLLM / Rag Variants — One-liner Docstring

```python
class LLMClassName(LLMInvestor):
    """LLM-driven class description — brief mechanism. Theory: simulation-bases.md §4.N."""
```

Requirements:
- Single line enclosed in `"""`
- Must contain `Theory: simulation-bases.md §4.N` (exact phrase, with correct N)
- Description must include the class's behavioral mechanism

### §5.3 Module Docstring (all variants)

```python
"""<Scenario> <Variant> — <description of this variant>.

Theoretical Foundation:
    - Author (Year): Key insight relevant to this simulation.
    - Author2 (Year): Second key insight.
"""
```

Must be the **first statement** in the file, before all imports.

### §5.4 Compliance Checklist

- [ ] Module docstring is the first statement (before all imports)
- [ ] Every investor class has a docstring (not just `pass`)
- [ ] Rule investor docstrings use multi-line format with `Theory: simulation-bases.md §4.N`
- [ ] LLM/RuleLLM/Rag investor docstrings use one-liner format with `Theory: simulation-bases.md §4.N`
- [ ] Section numbers `§4.N` match the actual section numbers in `simulation-bases.md`
- [ ] Author/year in Rule docstrings match the theoretical basis in `simulation-bases.md §4.N`

---

## §6 Summary: Non-Negotiable Requirements

The following failures always require repair, regardless of task type:

| Failure                                                                    | Impact                                                         | Fix Required                                                               |
|----------------------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------|
| `simulation-bases.md §4` contains rule/LLM content                         | Corrupts the variant-agnostic design principle                 | Remove and relocate to variant explain.md                                  |
| `{Variant}/explain.md` has no `§2` Theory→Implementation tables            | explain.md is useless without theory-code tracing              | Rewrite §2 entirely                                                        |
| `{Variant}/analysis.md` uses "Varies by scenario"                          | Analysis guide provides no analytical value                    | Replace all entries with numeric ranges                                    |
| `players.py` investor classes have no docstrings                           | Code has no theory traceability                                | Add docstrings per §5                                                      |
| `players.py` docstrings lack `Theory: simulation-bases.md §4.N`            | Citations are missing                                          | Patch docstrings per §5                                                    |
| `analysis.md` lacks `analysis-bases.md §2.X` references                    | Metrics are disconnected from analysis framework               | Add references per §4.2                                                    |
| `players.py` or `analysis.py` uses `.get(key, default)` on simulation data | Silent failures mask missing data — breaks fail-fast principle | Replace with `dict["key"]` per `04-code-repair.md §12`                     |
| `players.py` uses `if X else fallback` for required data                   | Hides data pipeline failures                                   | Replace with `if not X: raise ValueError(...)` per `04-code-repair.md §12` |
