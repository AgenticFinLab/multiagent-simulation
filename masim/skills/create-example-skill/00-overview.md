# Financial Multi-Agent Simulation Creation Guide — Overview

## What This Folder Is

This folder is the **authoritative step-by-step methodology** for building a
single financial multi-agent simulation in this project. Each phase of the
methodology is expanded into a dedicated, deeply specified file.

> **Where this folder sits in the larger pipeline.** Every scenario begins
> with a **scenario target file** authored by the user (or an upstream LLM
> on the user's behalf): `examples/{ScenarioName}/{domain}-{scenario}.md`.
> The format and validation of that file are owned by
> `masim/skills/create-simulation-target-skill.md`. The top-level pipeline
> `masim/skills/create-simulation-skill.md` ingests the target file, re-runs
> its §11 validation, runs the AGENT_POOL reuse gate, calls
> `masim/skills/agent-design-skill.md` for any new agent that has to be
> designed, and then *enters this folder* at Step 0 to build the actual
> scenario package. If you are starting a brand-new simulation, you should
> be invoked through `create-simulation-skill.md` — not opening this folder
> directly.

Reading through these files in order gives a complete, end-to-end methodology
for:

1. Ingesting the user-authored scenario target file `{domain}-{scenario}.md`
   and seeding the pipeline build-log `simulation-define.md` (Step 0)
2. Grounding the target file's §4 — §6 anchors in verified academic and
   empirical research (Step 1)
3. Designing the market and the investor taxonomy from target §7 + §8. Each
   per-investor specification conforms to the **Universal Agent Design Handbook**
   at `masim/skills/agent-design-skill.md`, with the financial-domain row labels
   and value palettes given inline in `02-root-documents-spec.md §4` and
   `06-step2-agent-design.md §2.2` (Step 2)
4. Implementing the variants chosen in target §10.1 (any subset of
   `Rule, LLM, RuleLLM, Rag`) (Step 3 — Step 4)
5. Validating, reviewing, analysing, documenting, executing, and final review
   (Step 5 — Step 10, all consolidated in `09-step5-to-10-review.md`)

**Authority boundary.** This guide is the methodology for *building a
financial simulation*. The intrinsic specification of any participant agent
(theory, role, information set, decision logic, action space, parameters,
validation) is governed by `masim/skills/agent-design-skill.md` (the
domain-neutral handbook). The financial-domain instantiation rules (Theory
Family palette, real-world counterpart enumeration, Action-Space row-label
substitutions, stylized-fact catalogue, regime palette) are folded inline into
this guide — there is **no separate `agent-design-finance.md` file**. Whenever
this guide and the handbook overlap on agent-intrinsic content, the handbook
prevails.

---

## Folder Structure and Reading Order

| File                           | Phase         | Purpose                                                                                                                                                                                                                                                                       |
|--------------------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `00-overview.md`               | —             | This file: guide orientation and reading order                                                                                                                                                                                                                                |
| `01-mandatory-structure.md`    | Pre-work      | Required directory layout, file roles, design principles                                                                                                                                                                                                                      |
| `02-root-documents-spec.md`    | Spec          | `simulation-bases.md` (9-section) + `analysis-bases.md` (7-section) full specifications. §4 of `simulation-bases.md` defers per-investor format to the **Universal Agent Design Handbook** (`masim/skills/agent-design-skill.md`), with financial-domain row labels inline. |
| `03-variant-documents-spec.md` | Spec          | `{Variant}/explain.md` (9-section) + `{Variant}/analysis.md` (7-section) full specifications                                                                                                                                                                                  |
| `04-step0-define.md`           | Step 0        | Ingest the user-authored scenario target file `{domain}-{scenario}.md` (spec: `masim/skills/create-simulation-target-skill.md`) and seed `simulation-define.md`                                                                                                                                                                                                 |
| `05-step1-research.md`         | Step 1        | Research and theory foundation methodology                                                                                                                                                                                                                                    |
| `06-step2-agent-design.md`     | Step 2        | Design the market and the investor taxonomy. Includes the AGENT_POOL reuse-or-create gate.                                                                                                                                                                                    |
| `07-step3-config.md`           | Step 3        | Create configuration files (simulation.yml, players.yml, topology.yml, persona.yml)                                                                                                                                                                                           |
| `08-step4-implement.md`        | Step 4        | Implement code for the variants selected in target §10.1                                                                                                                                                                                                                                          |
| `09-step5-to-10-review.md`     | Steps 5 — 10  | Validate, code-quality review, analysis tools, documentation, execute, and final review (consolidated)                                                                                                                                                                        |
| `15-reference-assetbubble.md`  | Reference     | AssetBubble reference implementation index                                                                                                                                                                                                                                    |

> *Historical note.* Earlier drafts of this guide split Steps 6 — 10 into separate
> files (`10-step6-quality.md` … `14-step10-review.md`). Those have been merged
> into `09-step5-to-10-review.md`. References to the old filenames in any
> historical document should be redirected to that consolidated file.

---

## How to Use This Guide

### For a New Simulation
Read files in order: `01` → `02` → `03` → `04` through `09`. Use `15` as a
reference whenever you need a concrete example. If you arrived here directly
(not through `create-simulation-skill.md`), the AGENT_POOL reuse gate in
`06-step2-agent-design.md §2.2.0` is the part you most easily overlook — run it.

### For Reviewing an Existing Simulation
Start with `01-mandatory-structure.md` to check structural completeness, then
`02-root-documents-spec.md` and `03-variant-documents-spec.md` to audit
documentation quality.

### For Updating bases.md Files
`02-root-documents-spec.md` is the primary reference. Its **§4 Investor
Taxonomy** specifies how each investor entry conforms to the Universal Agent
Design Handbook (`masim/skills/agent-design-skill.md`) under the embedded-form
header levels, with financial-domain row labels and value palettes specified
inline in §4.

---

## Relationship to Code

```text
masim/skills/create-simulation-target-skill.md
        │      ← Spec for the user-authored scenario target file
        ↓
examples/{ScenarioName}/{domain}-{scenario}.md
        │      ← The actual target file (user-authored, immutable once locked)
        ↓
masim/skills/create-simulation-skill.md
        │      ← Top-level pipeline: ingests the target file, runs
        │        the AGENT_POOL gate, dispatches into this folder.
        ↓
masim/skills/agent-design-skill.md   ← Universal handbook: per-agent
        │                              intrinsic specification standard
        │ governs every investor entry under §4 of
        │ simulation-bases.md (any scenario domain).
        │
        ↓
masim/skills/create-example-skill/   ← This folder: scenario-build methodology
        │                              (financial-domain row labels inline)
        │ drives
        ↓
examples/{SimulationName}/
├── {domain}-{scenario}.md     ← User-authored target (input)
├── simulation-define.md       ← Pipeline build log
├── simulation-bases.md         ← Written per 02-root-documents-spec.md §SIM
│                                   (§4 entries conform to agent-design-skill.md)
├── analysis-bases.md           ← Written per 02-root-documents-spec.md §ANA
└── {Variant}/
    ├── explain.md              ← Written per 03-variant-documents-spec.md §EXPLAIN
    ├── analysis.md             ← Written per 03-variant-documents-spec.md §ANALYSIS
    ├── players.py              ← Implemented per 08-step4-implement.md
    └── analysis.py             ← Implemented per 09-step5-to-10-review.md (Step 7)
```

Per-investor agent profiles that are intended to be **reusable across
scenarios** are additionally stored at:

```text
examples/AGENT_POOL/<domain>/<kebab-name>.md   # one file per agent archetype
```

(see `masim/skills/create-simulation-skill.md` for the reuse-or-create
protocol).

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

### 3. Per-investor specifications conform to the Universal Agent Design Handbook

Every investor entry in `simulation-bases.md §4` MUST conform section-for-
section to `masim/skills/agent-design-skill.md` (the canonical 11-section
format defined in §2 Canonical Section Order of the handbook), with header
levels shifted to embedded form per `02-root-documents-spec.md §4.0` and
Action Space labels instantiated for the market-trading domain per
`02-root-documents-spec.md §4.1`. The handbook requires:

1. Title — sentence-cased role phrase, not a class identifier
2. Summary — 7 fixed rows (Archetype, Theory Family, Behavioral Tendency,
   Time Horizon, Risk Tolerance, Information Asymmetry, Determinism). In the
   embedded form, Behavioral Tendency is renamed "Market Role".
3. Definition and Goals — 3 paragraphs including explicit non-goals
4. Theoretical Foundation — ≥1 sub-block with Citation (DOI), Calibration
   Source, Falsification Conditions, Alternative Theories
5. Design Purpose and Activation Triggers — with Deactivation Conditions and
   Behavioral Adaptation by Condition (embedded form: "Market Contribution by
   Regime")
6. Behavioral Framework — 5 sub-blocks (Decision Information Set, Core
   Behavioral Mechanism, Action Space, Mathematical Model with State-Update
   Rule and Determinism Contract, Behavioral Properties)
7. Parameters — 8-column table (Parameter, Type, Default, Valid Range,
   Sensitivity, Description, Impact, Source) or `_No tunable parameters._`
8. Worked Numerical Examples — ≥3 cases + 1 edge case
9. Behavioral Verification and Calibration — with ≥1 Ablation Hook
10. Academic References
11. Design Provenance and Versioning

**What is NOT in `simulation-bases.md §4`:**

- Rule-Based Behavior (IF/THEN code logic) → goes in `Rule/explain.md §2`
- LLM Persona (prompt text, signal interpretation) → goes in
  `LLM/explain.md §2` and `LLM/prompts.py`
- RuleLLM Hybrid Notes → goes in `RuleLLM/explain.md §2` and
  `RuleLLM/prompts.py`

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

| Pattern                                 | Reference File                                |
|-----------------------------------------|-----------------------------------------------|
| Investor taxonomy (handbook-conformant) | `examples/AssetBubble/simulation-bases.md §4` |
| Price formula + market design           | `examples/AssetBubble/simulation-bases.md §3` |
| Analysis metrics catalogue              | `examples/AssetBubble/analysis-bases.md §2`   |
| Theory → Implementation mapping         | `examples/AssetBubble/Rule/explain.md §2`     |
| LLM prompt design                       | `examples/AssetBubble/LLM/prompts.py`         |
| RuleLLM dual-section prompts            | `examples/AssetBubble/RuleLLM/prompts.py`     |
| RAG pipeline integration                | `examples/AssetBubble/Rag/players.py`         |

See `15-reference-assetbubble.md` for a complete index.
