# Multi-Agent Simulation Creation Guide — Overview

## What This Folder Is

This folder is the **authoritative step-by-step methodology** for building a
single multi-agent simulation in this project. The methodology is
domain-neutral: it applies to finance, opinion dynamics, epidemics, sociology,
or any other domain whose scenario target file conforms to
`masim/skills/define-simulation-scenario-skill.md`. Each phase of the
methodology is expanded into a dedicated, deeply specified file.

> **Where this folder sits in the larger pipeline.** Every scenario begins
> with a **scenario target file** produced by
> `masim/skills/define-simulation-scenario-skill.md` (an executable skill;
> the user supplies only minimal inputs, and the skill emits the file
> at `examples/{ScenarioName}/{domain}-{scenario}.md`). Users MUST NOT
> hand-author the target file. Post-lock changes go through the define
> skill's §9.3 revise mode, never through direct hand-editing.
>
> The top-level pipelines
> `masim/skills/create-simulation-pipeline.md` (from-scratch) and
> `masim/skills/polish-simulation-pipeline.md` (audit-and-patch) read and
> validate the target file, run the AGENT_POOL reuse gate, dispatch to
> `masim/skills/agent-design-skill.md` for any per-agent design work, and
> then *enter this folder* at Step 0 to build (or audit) the actual scenario
> package. If you are starting a brand-new simulation, invoke
> `create-simulation-pipeline.md`. If you are upgrading an existing one,
> invoke `polish-simulation-pipeline.md`. Do not open this folder directly
> unless you are writing skill content.

Reading through these files in order gives a complete, end-to-end methodology
for:

1. Reading the skill-produced scenario target file `{domain}-{scenario}.md`
   (emitted by `masim/skills/define-simulation-scenario-skill.md`) and
   seeding the pipeline build-log `simulation-build-log.md` (Step 0).
2. Grounding the target file's §4 — §6 anchors in verified academic and
   empirical research (Step 1).
3. Designing the environment and the agent taxonomy from target §7 + §8.
   Each per-agent specification conforms to the **Universal Agent Design
   Handbook** at `masim/skills/agent-design-skill.md`. Domain-specific row
   labels and value palettes (finance, opinion, epidemics, sociology, …) live
   in domain-instantiation appendices attached to `02-root-documents-spec.md`
   (Step 2).
4. Implementing the canonical variants selected by target §10.1. The
   canonical variant set at this version of `implement-simulation-skill`
   is exactly `Rule`, `LLM`, `RuleLLM`, `Rag` (see
   `01-mandatory-structure.md § Canonical Variant Set`); target §10.1
   marks each of these four `Yes` or `No`, and every variant marked `Yes`
   MUST be fully implemented (no silent skipping). Introducing a new
   variant is not permitted ad hoc — it requires the explicit upgrade
   procedure in `01-mandatory-structure.md § Canonical Variant Set`
   (Step 3 — Step 4).
5. Validating, reviewing, analysing, documenting, executing, and final review
   (Step 5 — Step 10, all consolidated in `09-step5-to-10-review.md`).

**Authority boundary.** This guide is the domain-neutral methodology for
*building a multi-agent simulation package* (root docs, variant docs, code,
config). The intrinsic specification of any participant agent (theory, role,
information set, decision logic, action space, parameters, validation) is
governed by `masim/skills/agent-design-skill.md` (the domain-neutral
handbook). Domain-specific instantiation rules — e.g., a Theory Family
palette, real-world counterpart enumeration, Action-Space row-label
substitutions, stylized-fact catalogue, regime palette — live in
domain-instantiation appendices under `02-root-documents-spec.md`. Whenever
this guide and the handbook overlap on agent-intrinsic content, the handbook
prevails. Whenever this guide and a domain appendix disagree on
domain-specific vocabulary, the domain appendix prevails within its own
domain.

---

## Folder Structure and Reading Order

| File                           | Phase         | Purpose                                                                                                                                                                                                                                                                       |
|--------------------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `00-overview.md`               | —             | This file: guide orientation and reading order                                                                                                                                                                                                                                |
| `01-mandatory-structure.md`    | Pre-work      | Required directory layout, file roles, design principles                                                                                                                                                                                                                      |
| `02-root-documents-spec.md`    | Spec          | `simulation-bases.md` (9-section) + `analysis-bases.md` (7-section) full specifications. §4 of `simulation-bases.md` defers per-agent format to the **Universal Agent Design Handbook** (`masim/skills/agent-design-skill.md`); domain-specific row labels live in appendices. |
| `03-variant-documents-spec.md` | Spec          | `{Variant}/explain.md` (9-section) + `{Variant}/analysis.md` (7-section) full specifications                                                                                                                                                                                  |
| `04-step0-load-target.md`      | Step 0        | Load the skill-produced scenario target file `{domain}-{scenario}.md` (produced by `masim/skills/define-simulation-scenario-skill.md`) and seed `simulation-build-log.md`                                                                                                     |
| `05-step1-research.md`         | Step 1        | Research and theory foundation methodology                                                                                                                                                                                                                                    |
| `06-step2-agent-design.md`     | Step 2        | Design the environment and the agent taxonomy. Includes the AGENT_POOL reuse-or-create gate.                                                                                                                                                                                  |
| `07-step3-config.md`           | Step 3        | Create configuration files (simulation.yml, players.yml, topology.yml, plus persona.yml for LLM-flavoured variants)                                                                                                                                                          |
| `08-step4-implement.md`        | Step 4        | Implement code for the variants declared in target §10.1                                                                                                                                                                                                                      |
| `09-step5-to-10-review.md`     | Steps 5 — 10  | Validate, code-quality review, analysis tools, documentation, execute, and final review (consolidated)                                                                                                                                                                        |
| `10-evaluation-architecture.md`| Architecture   | Evaluation-first design: all reusable metrics/viz/validation code lives in `masim/evaluation/`; scenario scripts import from there (MANDATORY)                                                                                                                               |
| `15-reference-assetbubble.md`  | Reference     | AssetBubble reference implementation index (finance domain example)                                                                                                                                                                                                           |

> *Historical note.* Earlier drafts of this guide split Steps 6 — 10 into separate
> files (`10-step6-quality.md` … `14-step10-review.md`). Those have been merged
> into `09-step5-to-10-review.md`. References to the old filenames in any
> historical document should be redirected to that consolidated file.

---

## How to Use This Guide

### For a New Simulation
Invoke `masim/skills/create-simulation-pipeline.md`. That pipeline will drive
this folder in order: `01` → `02` → `03` → `04` through `09`. Use `15` as a
concrete finance-domain example whenever you need one; for other domains,
consult the domain-instantiation appendix under `02-root-documents-spec.md`.
If you arrived here directly (not through the pipeline), the AGENT_POOL reuse
gate in `06-step2-agent-design.md §2.2.0` is the part you most easily
overlook — run it.

### For Upgrading an Existing Simulation
Invoke `masim/skills/polish-simulation-pipeline.md`. That pipeline
orchestrates a bounded audit-and-patch across all step files without editing
target-file substance directly.

### For Reviewing an Existing Simulation
Start with `01-mandatory-structure.md` to check structural completeness, then
`02-root-documents-spec.md` and `03-variant-documents-spec.md` to audit
documentation quality.

### For Updating bases.md Files
`02-root-documents-spec.md` is the primary reference. Its **§4 Agent
Taxonomy** specifies how each agent entry conforms to the Universal Agent
Design Handbook (`masim/skills/agent-design-skill.md`) under the embedded-form
header levels. Domain-specific row labels and value palettes are specified in
the corresponding domain-instantiation appendix (finance, opinion, epidemics,
sociology, …).

---

## Relationship to Code

```text
masim/skills/define-simulation-scenario-skill.md
        │      ← Executable skill: produces the target file from
        │        minimal user inputs (see its §9)
        ↓
examples/{ScenarioName}/{domain}-{scenario}.md
        │      ← The actual target file (skill-produced, immutable once locked)
        ↓
masim/skills/create-simulation-pipeline.md   OR   polish-simulation-pipeline.md
        │      ← Top-level pipeline: reads and validates the target file, runs
        │        the AGENT_POOL gate, dispatches into this folder.
        ↓
masim/skills/agent-design-skill.md   ← Universal handbook: per-agent
        │                              intrinsic specification standard
        │ governs every agent entry under §4 of simulation-bases.md
        │ (any scenario domain).
        │
        ↓
masim/skills/implement-simulation-skill/   ← This folder: scenario-build methodology
        │                              (domain-neutral; domain appendices
        │                               attached to 02-root-documents-spec.md)
        │ drives
        ↓
examples/{ScenarioName}/
├── {domain}-{scenario}.md     ← Skill-produced target (input)
├── simulation-build-log.md    ← Pipeline build log
├── simulation-bases.md        ← Written per 02-root-documents-spec.md §SIM
│                                (§4 entries conform to agent-design-skill.md)
├── analysis-bases.md          ← Written per 02-root-documents-spec.md §ANA
└── {Variant}/
    ├── explain.md             ← Written per 03-variant-documents-spec.md §EXPLAIN
    ├── analysis.md            ← Written per 03-variant-documents-spec.md §ANALYSIS
    ├── players.py             ← Implemented per 08-step4-implement.md
    │                            (canonical agent-implementation module name)
    └── analysis.py            ← Implemented per 09-step5-to-10-review.md (Step 7)
```

Per-agent profiles that are intended to be **reusable across scenarios** are
additionally stored at:

```text
masim/agents/defines/<domain>/<kebab-name>.md   # one file per agent archetype
```

(see `masim/skills/create-simulation-pipeline.md` for the reuse-or-create
protocol).

---

## Key Design Principles (Summary)

### 1. Root documents are variant-agnostic
`simulation-bases.md` and `analysis-bases.md` describe **what** the simulation
models, not **how** any specific variant implements it. They contain:
- Theory, mathematics, academic grounding
- Agent archetypes defined at the theoretical / behavioral level
- Environment design principles
- No code, no implementation hints, no variant-specific behavior

### 2. Variant documents do the implementation tracing
`{Variant}/explain.md` traces every design element in `simulation-bases.md`
to a specific code location. It does NOT re-explain the theory — it cites
`simulation-bases.md §N.M` and then specifies the implementation detail
(method name, formula in code, config path).

### 3. Per-agent specifications conform to the Universal Agent Design Handbook

Every agent entry in `simulation-bases.md §4` MUST conform section-for-section
to `masim/skills/agent-design-skill.md` (the canonical 11-section format
defined in §2 Canonical Section Order of the handbook), with header levels
shifted to embedded form per `02-root-documents-spec.md §4.0` and domain-
specific row labels instantiated per the corresponding domain-instantiation
appendix under `02-root-documents-spec.md`. The handbook requires:

1. Title — sentence-cased role phrase, not a class identifier
2. Summary — 7 fixed rows (Archetype, Theory Family, Behavioral Tendency,
   Time Horizon, Risk Tolerance, Information Asymmetry, Determinism). In the
   embedded form, "Behavioral Tendency" MAY be renamed by the domain
   appendix (e.g., finance renames it "Market Role"; opinion dynamics may
   rename it "Opinion Role").
3. Definition and Goals — 3 paragraphs including explicit non-goals
4. Theoretical Foundation — ≥1 sub-block with Citation (DOI), Calibration
   Source, Falsification Conditions, Alternative Theories
5. Design Purpose and Activation Triggers — with Deactivation Conditions and
   Behavioral Adaptation by Condition (embedded form: name is domain-
   configurable — finance uses "Market Contribution by Regime"; other
   domains use their equivalent)
6. Behavioral Framework — 5 sub-blocks (Decision Information Set, Core
   Behavioral Mechanism, Action Space, Mathematical Model with State-Update
   Rule and Determinism Contract, Behavioral Properties). The Action Space
   row labels are domain-specific and instantiated by the domain appendix.
7. Parameters — 8-column table (Parameter, Type, Default, Valid Range,
   Sensitivity, Description, Impact, Source) or `_No tunable parameters._`
8. Worked Numerical Examples — ≥3 cases + 1 edge case
9. Behavioral Verification and Calibration — with ≥1 Ablation Hook
10. Academic References
11. Design Provenance and Versioning

**What is NOT in `simulation-bases.md §4`:**

- Rule-based behavioural code (IF/THEN logic) → goes in `Rule/explain.md §2`
- LLM Persona (prompt text, signal interpretation) → goes in
  `LLM/explain.md §2` and `LLM/prompts.py`
- RuleLLM Hybrid Notes → goes in `RuleLLM/explain.md §2` and
  `RuleLLM/prompts.py`
- RAG retrieval integration notes → goes in `Rag/explain.md §2` and
  `Rag/players.py`

### 4. All parameters must have source citations
Every numeric value in `simulation-bases.md §6` must trace to an empirical
study or calibration paper. "Normalization" is acceptable only for scale
parameters (e.g., `initial_price = 100.0` in a finance scenario, or
`initial_infected_fraction = 0.01` in an epidemics scenario).

### 5. Documentation is written before code
- `simulation-bases.md` and `analysis-bases.md` are written **before** any
  agent-implementation module (`players.py`).
- Each variant's `explain.md` is written **immediately after** that variant's
  `players.py` is completed.
- This discipline ensures the code reflects the design, not vice versa.

### 6. Strict no-default, no-defensive-programming policy
All simulation code (`players.py` and `analysis.py` in every variant) must
follow **fail-fast** principles. When required project data is missing, the
code must raise an explicit exception — never silently substitute a default
value or fall back to a safe action.

**Prohibited patterns** (applies universally to all variants and domains):

| Pattern                                     | Why It Is Dangerous                                        |
|---------------------------------------------|------------------------------------------------------------|
| `dict.get("key", default)` on known dicts   | Silently uses wrong data if key is missing                 |
| `if X else fallback` for required data      | Hides data pipeline failures                               |
| `decision is None → default action` (silent recovery) | Masks LLM parse failures as valid decisions      |
| `if rates else 0.0` for computed metrics    | Produces fake zero metrics instead of surfacing empty data |
| `payload.get("field", None)` in analysis    | Silently drops records that should cause investigation     |

**Required replacement**: Direct `dict["key"]` access (raises `KeyError`),
`raise ValueError(...)`, or `raise RuntimeError(...)` when data is absent.

**Runtime exception for stochastic API modes**: malformed external LLM output
and transient provider errors are not authoritative project data. After the
prompt/parser/player contract has been fixed at the source, a scenario-local
fallback is allowed only when it is explicit, conservative, counted, and
auditable. The fallback must return every field later read by `players.py` or
written to the action record; auth, quota, missing-key, config,
parser-reference, and framework schema errors still fail loudly.

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

### 7. Evaluation-first architecture for analysis code

All reusable evaluation, metrics, visualization, and validation code lives in
`masim/evaluation/` — the project's shared analytical capability library.
Scenario-specific `analysis.py` scripts import from there; they do not define
their own generic functions locally.

**The decision rule:**
1. Need a function? → Check `masim/evaluation/` first.
2. Found it? → Import it.
3. Not found but reusable? → Implement in `masim/evaluation/` FIRST, then import.
4. Truly scenario-specific? → Implement locally with a comment explaining why.

**Full specification:** `masim/skills/implement-simulation-skill/10-evaluation-architecture.md`

This grows the project's shared library with every new scenario and prevents
the anti-pattern of N scenarios each re-implementing the same metric function.

---

## Reference: AssetBubble Implementation (Finance Domain Example)

AssetBubble is a finance-domain reference implementation. All major patterns
are demonstrated there; other-domain scenarios follow the same structural
patterns with their own domain-instantiation appendix vocabulary.

| Pattern                                              | Reference File                                |
|------------------------------------------------------|-----------------------------------------------|
| Agent taxonomy (handbook-conformant, finance domain) | `examples/AssetBubble/simulation-bases.md §4` |
| Interaction / price formula + environment design      | `examples/AssetBubble/simulation-bases.md §3` |
| Analysis metrics catalogue                            | `examples/AssetBubble/analysis-bases.md §2`   |
| Theory → Implementation mapping                       | `examples/AssetBubble/Rule/explain.md §2`     |
| LLM prompt design                                     | `examples/AssetBubble/LLM/prompts.py`         |
| RuleLLM dual-section prompts                          | `examples/AssetBubble/RuleLLM/prompts.py`     |
| RAG pipeline integration                              | `examples/AssetBubble/Rag/players.py`         |

See `15-reference-assetbubble.md` for a complete index.
