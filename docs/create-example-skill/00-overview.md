# Financial Multi-Agent Simulation Creation Guide — Overview

## What This Folder Is

This folder is the **authoritative creation guide** for building financial multi-agent simulations in this project. It supersedes the legacy single-file `docs/create-example-skill.md` and expands each phase into a dedicated, deeply specified file.

Reading through these files in order gives a complete, step-by-step methodology for:
1. Defining a financial phenomenon
2. Grounding it in academic and empirical research
3. Designing a rigorous investor taxonomy
4. Implementing four simulation variants (Rule, LLM, RuleLLM, Rag)
5. Producing standardized analysis tools and documentation

---

## Folder Structure and Reading Order

| File                           | Phase     | Purpose                                                                                                                                     |
|--------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `00-overview.md`               | —         | This file: guide orientation and reading order                                                                                              |
| `01-mandatory-structure.md`    | Pre-work  | Required directory layout, file roles, design principles                                                                                    |
| `02-root-documents-spec.md`    | Spec      | `simulation-bases.md` (9-section) + `analysis-bases.md` (7-section) full specifications — including the **7-part investor design standard** |
| `03-variant-documents-spec.md` | Spec      | `{Variant}/explain.md` (9-section) + `{Variant}/analysis.md` (7-section) full specifications                                                |
| `04-step0-define.md`           | Step 0    | Define your simulation — minimum required input                                                                                             |
| `05-step1-research.md`         | Step 1    | Research and theory foundation methodology                                                                                                  |
| `06-step2-agent-design.md`     | Step 2    | Design agent architecture — market + investor taxonomy                                                                                      |
| `07-step3-config.md`           | Step 3    | Create configuration files (simulation.yml, players.yml, topology.yml, persona.yml)                                                         |
| `08-step4-implement.md`        | Step 4    | Implement code for all four variants                                                                                                        |
| `09-step5-validate.md`         | Step 5    | Validate design against checklists                                                                                                          |
| `10-step6-quality.md`          | Step 6    | Code quality review                                                                                                                         |
| `11-step7-analysis.md`         | Step 7    | Create analysis tools                                                                                                                       |
| `12-step8-documentation.md`    | Step 8    | Write all documentation (root + per-variant)                                                                                                |
| `13-step9-execute.md`          | Step 9    | Execute and debug                                                                                                                           |
| `14-step10-review.md`          | Step 10   | Final review — complete completion checklist                                                                                                |
| `15-reference-assetbubble.md`  | Reference | AssetBubble reference implementation index                                                                                                  |

---

## How to Use This Guide

### For a New Simulation
Read files in order: `01` → `02` → `04` through `14`. Use `15` as a reference whenever you need a concrete example.

### For Reviewing an Existing Simulation
Start with `01-mandatory-structure.md` to check structural completeness, then `02-root-documents-spec.md` and `03-variant-documents-spec.md` to audit documentation quality.

### For Updating bases.md Files
`02-root-documents-spec.md` is the primary reference. Its **§4 Investor Design Standard** defines the 7-part format that every investor entry in every `simulation-bases.md` must follow.

---

## Relationship to Code

```
docs/create-example-skill/      ← This folder: creation methodology
        │
        │ drives
        ▼
examples/{SimulationName}/
├── simulation-bases.md         ← Written per 02-root-documents-spec.md §SIM
├── analysis-bases.md           ← Written per 02-root-documents-spec.md §ANA
└── {Variant}/
    ├── explain.md              ← Written per 03-variant-documents-spec.md §EXPLAIN
    ├── analysis.md             ← Written per 03-variant-documents-spec.md §ANALYSIS
    ├── players.py              ← Implemented per 08-step4-implement.md
    └── analysis.py             ← Implemented per 11-step7-analysis.md
```

---

## Key Design Principles (Summary)

### 1. Root documents are variant-agnostic
`simulation-bases.md` and `analysis-bases.md` describe **what** the simulation models, not **how** any specific variant implements it. They contain:
- Theory, mathematics, academic grounding
- Investor archetypes defined at the economic level
- Market design principles
- No code, no implementation hints, no variant-specific behavior

### 2. Variant documents do the implementation tracing
`{Variant}/explain.md` traces every design element in `simulation-bases.md` to a specific code location. It does NOT re-explain the theory — it cites `simulation-bases.md §N.M` and then specifies the implementation detail (method name, formula in code, config path).

### 3. The 7-part investor standard is mandatory
Every investor in `simulation-bases.md §4` must have all 7 parts:
1. Summary
2. Theoretical and Empirical Foundation (≥2 sources with DOIs)
3. Design Purpose and Activation Scenarios
4. Behavioral Framework (information set, mechanism narrative, math model, behavioral properties)
5. Decision Process Walkthrough (step-by-step with example values)
6. Worked Numerical Example (fully calculated)
7. Academic References (complete bibliography)

**What is NOT in simulation-bases.md §4:**
- Rule-Based Behavior (IF/THEN code logic) → goes in `Rule/explain.md §2`
- LLM Persona (prompt text, signal interpretation) → goes in `LLM/explain.md §2` and `LLM/prompts.py`
- RuleLLM Hybrid Notes → goes in `RuleLLM/explain.md §2` and `RuleLLM/prompts.py`

### 4. All parameters must have source citations
Every numeric value in `simulation-bases.md §6` must trace to an empirical study or calibration paper. "Normalization" is acceptable only for scale parameters (e.g., initial_price = 100.0).

### 5. Documentation is written before code
- `simulation-bases.md` and `analysis-bases.md` are written **before** any `players.py`
- Each variant's `explain.md` is written **immediately after** that variant's `players.py` is completed
- This discipline ensures the code reflects the design, not vice versa

### 6. Strict no-default, no-defensive-programming policy
All simulation code (`players.py` and `analysis.py` in every variant) must follow **fail-fast** principles. When required project data is missing, the code must raise an explicit exception — never silently substitute a default value or fall back to a safe action.

**Prohibited patterns** (applies universally to all variants):

| Pattern                                     | Why It Is Dangerous                                        |
|---------------------------------------------|------------------------------------------------------------|
| `dict.get("key", default)` on known dicts   | Silently uses wrong data if key is missing                 |
| `if X else fallback` for required data      | Hides data pipeline failures                               |
| `decision is None → hold` (silent recovery) | Masks LLM parse failures as valid trading decisions        |
| `if rates else 0.0` for computed metrics    | Produces fake zero metrics instead of surfacing empty data |
| `payload.get("field", None)` in analysis    | Silently drops records that should cause investigation     |

**Required replacement**: Direct `dict["key"]` access (raises `KeyError`), `raise ValueError(...)`, or `raise RuntimeError(...)` when data is absent.

**Runtime exception for stochastic API modes**: malformed external LLM output
and transient provider errors are not authoritative project data. After the
prompt/parser/player contract has been fixed at the source, a scenario-local
fallback is allowed only when it is explicit, conservative, counted, and
auditable. The fallback must return every field later read by `players.py` or
written to the order record; auth, quota, missing-key, config, parser-reference,
and framework schema errors still fail loudly.

Post-run quality gates:
- `0` fallback decisions: clean.
- `>0` and `<=1%` of API decisions: acceptable with a quality note if scenario
  metrics remain coherent.
- `>1%`: quality-review required; rerun or repair unless a scenario-specific
  design note justifies acceptance.
- Any fallback caused by deterministic project bugs: invalid output.

**Legitimate exceptions** (these `.get()` patterns are allowed):
- RAG config resolution: `resolved_rag.get("embed_model", ...)` — external library config with genuine optional fields
- `__getstate__`/`__setstate__` serialization infrastructure
- `config.extras.get("optional_feature", {})` — truly optional config sections like `private_knowledge`
- Matplotlib styling defaults (colors, line widths)

---

## Reference: AssetBubble Implementation

AssetBubble is the primary reference implementation. All major patterns are demonstrated there:

| Pattern                         | Reference File                                |
|---------------------------------|-----------------------------------------------|
| Investor taxonomy (full 7-part) | `examples/AssetBubble/simulation-bases.md §4` |
| Price formula + market design   | `examples/AssetBubble/simulation-bases.md §3` |
| Analysis metrics catalogue      | `examples/AssetBubble/analysis-bases.md §2`   |
| Theory → Implementation mapping | `examples/AssetBubble/Rule/explain.md §2`     |
| LLM prompt design               | `examples/AssetBubble/LLM/prompts.py`         |
| RuleLLM dual-section prompts    | `examples/AssetBubble/RuleLLM/prompts.py`     |
| RAG pipeline integration        | `examples/AssetBubble/Rag/players.py`         |

See `15-reference-assetbubble.md` for a complete index.
