---
name: create-simulation-pipeline
purpose: Top-level pipeline for building a **brand-new** MASim simulation scenario from scratch, starting from a scenario target file `{domain}-{scenario}.md` produced by `define-simulation-scenario-skill.md` (users never hand-author the target file — it is emitted by that upstream skill from minimal user inputs). Produces the full package: root `*-bases.md`, the variants selected in §10.1, configs, code, analysis, review. Orchestrates target-file load, the AGENT_POOL reuse-or-create gate, the Universal Agent Design Handbook, and the per-step `implement-simulation-skill/` files. **Not for upgrading existing scenarios** — use `polish-simulation-pipeline.md` for that.
status: canonical
audience: LLM agents and reviewers building a new simulation scenario from a conforming, skill-produced target file in this repository.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
invocation: Call this file *after* a target file conforming to `masim/skills/define-simulation-scenario-skill.md` exists at `examples/{ScenarioName}/{domain}-{scenario}.md`, **and** the scenario folder does not yet contain a `simulation-bases.md`. If a scenario already has downstream artefacts and you want to bring it up to the latest skill versions, use `masim/skills/polish-simulation-pipeline.md` instead. Do NOT open `implement-simulation-skill/` files directly for a new scenario — they are sub-skills dispatched from Phase 4 of this pipeline. Do NOT begin pipeline execution without a passing target file.
---

# Create-Simulation-Pipeline — End-to-End Scenario Pipeline

## 0. Scope and Authority

This skill is the **single entry point** for building a new multi-agent
simulation scenario in this repository. It is deliberately thin: it owns
**target-file load, the AGENT_POOL reuse gate, and orchestration**,
and it delegates everything else to existing, more specialised skills.

**Scope: this file covers *from-scratch* scenario creation only** — the
target file exists, the scenario folder is empty (or nonexistent), and
we are building all downstream artefacts for the first time. If the
scenario folder already contains `simulation-bases.md` and variant
subdirectories that need to be brought up to the latest skill
specification, this pipeline does **not** apply; use
`masim/skills/polish-simulation-pipeline.md` instead. That polish
pipeline reuses the same skill vocabulary (Universal Handbook,
AGENT_POOL gate, three-PASS validation) but operates as an audit and
patch loop, not a from-scratch build.

The pipeline does **not** collect user input through long
AskUserQuestion sessions. Instead, every piece of user intent is
emitted upstream into the scenario target file
`examples/{ScenarioName}/{domain}-{scenario}.md` by
`masim/skills/define-simulation-scenario-skill.md` (the user supplies
only the minimal inputs listed in that skill's §9.1). The pipeline
reads that file, re-runs its §11 validation, and proceeds only when
the file passes; AskUserQuestion is reserved for *defect
clarifications* raised against the target file (which the user
resolves via a revise-mode re-invocation of the upstream skill), not
for collecting fresh content.

| Concern                                       | Owner                                                       |
|-----------------------------------------------|-------------------------------------------------------------|
| **Upstream scenario target file format**      | **`masim/skills/define-simulation-scenario-skill.md`**      |
| Per-agent intrinsic specification             | `masim/skills/agent-design-skill.md` (Universal Handbook)   |
| Scenario package layout, root + variant specs | `masim/skills/implement-simulation-skill/` (files 01 — 09)  |
| Domain-instantiation rules for finance        | `implement-simulation-skill/02-root-documents-spec.md §4.1` |
| AGENT_POOL three-stage match protocol         | This file §3 and `implement-simulation-skill/06 §2.2.0`     |
| Three-PASS validation discipline              | This file §6 and `agent-design-skill.md §6`                 |

When this file and any of the above overlap, **this file decides the
order and the orchestration**, but the substantive content is governed
by the file in the right-hand column.

> Do not paste the body of the Universal Agent Design Handbook here, do
> not paste `implement-simulation-skill/` files here, and do not paste
> `02-root-documents-spec.md §4.1` here. Reference them by relative
> path and section number.

---

## 1. Design Philosophy

Six commitments shape every step of this pipeline:

1. **Research before code.** No `.py` file is touched before
   `simulation-bases.md` and `analysis-bases.md` are written; no
   `*-bases.md` text is written before the `simulation-build-log.md`
   contract is locked.
2. **Reuse before invent.** Every candidate agent passes the AGENT_POOL
   gate before any new design is started. New designs are written
   *back* to the pool so the next scenario can reuse them.
3. **Handbook as a contract, not a template.** Per-agent specifications
   are authored against the Universal Agent Design Handbook
   (`agent-design-skill.md`). The handbook's section names, header
   levels, and table columns are fixed; only the *content* is
   scenario-specific.
4. **Target file is the contract; AskUserQuestion is for defect
   triage only.** Every piece of user intent — domain, agents,
   theories, parameters, success criteria — is emitted upstream into
   `examples/{ScenarioName}/{domain}-{scenario}.md` by
   `define-simulation-scenario-skill.md` (the user supplies only the
   minimal inputs listed in that skill's §9.1). The pipeline reads
   this file and re-runs its §11 validation. `AskUserQuestion` (≤4
   options per question) is used only to notify the user of a
   discovered defect (e.g., a citation that does not resolve, an
   agent that lacks a theory anchor); repair goes through a re-run
   of `define-simulation-scenario-skill.md` in revise mode (see that
   skill's §9.3). The pipeline never uses AskUserQuestion to invent
   content the target file should have contained, and the pipeline
   never edits the target file itself.
5. **Two files per scenario, distinct roles.** The *target file*
   `{domain}-{scenario}.md` is the upstream, skill-produced statement
   of user intent (immutable once locked; every write is mediated by
   `define-simulation-scenario-skill.md`). The *build-log contract*
   `simulation-build-log.md` is the pipeline's own log: it records the
   AGENT_POOL gate decisions (§A), accumulated research notes (§B
   built atop the target file's §4 — §6 entries), open questions
   raised during execution (§C), and a per-phase build log (§D). The
   pipeline writes to `simulation-build-log.md`; it never writes to the
   target file.
6. **Three consecutive PASSes equals approved.** Every review checklist
   (agent-level handbook §6, scenario-level §6 of this file) MUST be
   run three times in succession; three PASS runs is the only accepted
   approval signal. Anything less than three PASS rounds counts as a
   FAIL, and the offending artefact returns for revision.

---

## 2. Pipeline Overview

```text
            ┌──────────────────────────────────────────────┐
            │ Phase 0 — Target File Load              │
            │   Read examples/{Sim}/{domain}-{scenario}.md │
            │   Re-run §11 validation; raise defects via   │
            │   AskUserQuestion. Seed simulation-build-log.md │
            └──────────────────────────────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────────────────────┐
            │ Phase 1 — Research                           │
            │   implement-simulation-skill/05-step1-research.md  │
            │   Fills §B Research Notes of the contract    │
            └──────────────────────────────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────────────────────┐
            │ Phase 2 — Role Planning                      │
            │   Decide 4–7 archetypes (theory-first)       │
            │   Map each to a tentative real-world class   │
            └──────────────────────────────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────────────────────┐
            │ Phase 3 — AGENT_POOL Gate + Agent Design     │
            │   3-stage match → reuse / fork / new         │
            │   New designs:  agent-design-skill.md §3     │
            │                 + 3-PASS handbook §6 review  │
            │                 + write-back to AGENT_POOL   │
            └──────────────────────────────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────────────────────┐
            │ Phase 4 — Scenario Build                     │
            │   implement-simulation-skill/                      │
            │     02-root-documents-spec.md (bases.md)     │
            │     03-variant-documents-spec.md (explain)   │
            │     07-step3-config.md (yml)                 │
            │     08-step4-implement.md (code)             │
            └──────────────────────────────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────────────────────┐
            │ Phase 5 — Scenario-Level 3-PASS Review       │
            │   implement-simulation-skill/09-step5-to-10-       │
            │     review.md (Steps 5–9) ×3                 │
            └──────────────────────────────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────────────────────┐
            │ Phase 6 — Execution & Final Review           │
            │   run the variants selected in §10.1, do     │
            │   analysis, final review per                 │
            │   09-step5-to-10-review.md Step 10           │
            └──────────────────────────────────────────────┘
```

Each phase has explicit **entry conditions**, **artefacts**, and
**exit conditions** declared below. A phase MUST NOT start until its
entry conditions are satisfied; a phase MUST NOT be marked done until
its exit conditions hold.

---

## 3. Phase 0 — Target File Load

### 3.1 Entry Conditions

- The user has invoked `define-simulation-scenario-skill.md` and that
  skill has produced a target file at
  `examples/{ScenarioName}/{domain}-{scenario}.md` conforming to its
  §11 validation, with `Status: draft`. Users MUST NOT hand-author
  this file; if it lacks a `Produced By` row in §1 Meta, refuse to
  proceed and require a fresh skill invocation.
- This file (`create-simulation-pipeline.md`) is the active skill.

### 3.2 Procedure

1. **Read the target file.** Open
   `examples/{ScenarioName}/{domain}-{scenario}.md` end-to-end. If
   the file does not exist, refuse to proceed and instruct the caller
   to invoke `define-simulation-scenario-skill.md` first to generate
   one.
2. **Re-run the target-file §11 validation.** Run every box in
   `define-simulation-scenario-skill.md §11` against the file. The
   pipeline does **not** trust the upstream skill's local PASS; it
   re-verifies from scratch.
3. **For every FAIL item**, raise an `AskUserQuestion` turn (≤4
   options per question) summarising the defect and offering the
   plausible repair options. Use the `Other` escape hatch for
   free-form corrections. The user then re-invokes
   `define-simulation-scenario-skill.md` in revise mode (its §9.3),
   which re-emits an updated target file; the pipeline re-validates.
   Loop until three consecutive PASS runs are achieved. The pipeline
   MUST NOT edit the target file itself.
4. **Resolve domain palette.** If the chosen domain's palette is
   already documented (e.g., `finance` → `02-root-documents-spec.md
   §4.1`), use it. Otherwise, require the target file's
   `§A Domain Palette Appendix` to be present and complete; if not,
   block and return.
5. **Seed `simulation-build-log.md`.** Create
   `examples/{ScenarioName}/simulation-build-log.md` with the
   following minimal skeleton, populating §0 Meta and §B by reference
   (NOT by duplication) to the target file:

```markdown
# {ScenarioName} — Pipeline Build Log

## §0 Meta

| Field       | Content                                                 |
|-------------|---------------------------------------------------------|
| Name        | {ScenarioName}                                          |
| Target file | examples/{ScenarioName}/{domain}-{scenario}.md          |
| Target spec | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Domain      | {Domain from target §1}                                 |
| Pipeline    | masim/skills/create-simulation-pipeline.md              |
| Status      | draft                                                   |

## §A AGENT_POOL Reuse-or-Create Gate Log
(Empty. Populated by Phase 3.)

## §B Research Notes (extends target §4 — §6)
(Empty. Populated by Phase 1.)

## §C Open Questions and Risks
(Empty. Populated as defects are surfaced.)

## §D Build Log
| Phase | Date | Outcome | Reviewer | Notes |
|-------|------|---------|----------|-------|
```

6. **Upgrade target file status.** Once §11 passes three times in a
   row, the pipeline updates the target file's §1 `Status` from
   `draft` to `locked` (one-line edit only). The target file is now
   immutable until the scenario is `released`.

### 3.3 Artefacts

- `examples/{ScenarioName}/{domain}-{scenario}.md` —
  `Status: locked`.
- `examples/{ScenarioName}/simulation-build-log.md` — `Status: draft`,
  §0 Meta filled, §A / §B / §C / §D stubs created.

### 3.4 Exit Conditions

- Target file §11 has three consecutive PASS runs.
- Target file `Status: locked`.
- `simulation-build-log.md` exists and references the target file by
  path in §0.

### 3.5 Handoff

→ Phase 1 (Research). Downstream phases read intent from the target
file (§1 — §10) and write working notes / build log to
`simulation-build-log.md`. The target file MUST NOT be edited again
until the scenario is released; if a defect is discovered later, the
pipeline halts, the user re-invokes
`define-simulation-scenario-skill.md` in revise mode (its §9.3) to
re-emit the target file, and Phase 0 restarts.

---

## 4. Phase 1 — Research

### 4.1 Entry Conditions

- Phase 0 exit conditions hold (target file locked,
  `simulation-build-log.md` seeded).
- The pipeline agent has access to academic databases and the
  historical record needed to *verify* and *expand on* the target
  file's §4 — §6 entries.

### 4.2 Procedure

Execute `masim/skills/implement-simulation-skill/05-step1-research.md`,
treating the target file's §4 (Theoretical Anchors), §5 (Stylized
Facts), and §6 (Historical / Empirical Anchors) as the seed list.
Research has three jobs, in order:

1. **Verify**. For every entry in target §4, §5, §6, resolve the
   citation (DOI / URL) and confirm the quoted quantitative range
   appears in the source. Any failure → `AskUserQuestion` defect
   raised to the user; the user re-invokes
   `define-simulation-scenario-skill.md` in revise mode; the updated
   target file is re-locked, then research resumes.
2. **Expand**. For every verified entry, add the deeper material
   that `05-step1-research.md` requires (key equations, parameter
   estimates, mechanism diagrams) into `simulation-build-log.md §B`.
   The target file is **not** rewritten — `§B` is the expansion
   layer.
3. **Surface gaps**. If verifying / expanding reveals that the
   target file is materially incomplete (e.g., a stylized fact
   without a primary source), record the gap in
   `simulation-build-log.md §C` and raise it to the user (who then
   authorises a revise-mode re-invocation of
   `define-simulation-scenario-skill.md`). Do not silently invent
   missing content.

### 4.3 Artefacts

- `simulation-build-log.md §B.1 Core Theories` — one expanded block per
  target §4 entry (DOI, key equation, calibration values, mechanism
  detail).
- `§B.2 Empirical Stylized Facts` — one expanded block per target §5
  row (verified range, supporting datasets if any).
- `§B.3 Historical Events` — one expanded block per target §6 entry
  (timeline, participant accounts, primary sources).
- `§B.5 Parameter Estimates` — every target §9 row, expanded with
  any additional cross-references found during research.

### 4.4 Exit Conditions

- Every target §4 / §5 / §6 / §9 entry has a corresponding §B block
  in `simulation-build-log.md`.
- Every defect raised against the target file has been resolved (the
  target file is `locked` again).
- `simulation-build-log.md §C` has been swept; any remaining open
  question is either explicitly deferred (with a `Defer: <reason>`
  tag) or escalated to the user (who resolves it via a revise-mode
  re-invocation of `define-simulation-scenario-skill.md`).

---

## 5. Phase 2 — Role Planning

### 5.1 Entry Conditions

- Phase 1 exit conditions hold.
- The target file's §7 Agent Roster has 4 — 7 rows that passed §11
  cross-section consistency (every agent ties to a §4 theory and a
  §8 signal).

### 5.2 Procedure

For each row in target §7:

1. Re-confirm the chosen primary theory (target §7 column `Theory
   family`) corresponds to a verified §B.1 entry in
   `simulation-build-log.md`.
2. Re-confirm the real-world counterpart (target §7 column) comes
   from the domain enumeration (for finance,
   `02-root-documents-spec.md §4.1.2`).
3. Re-confirm the market / domain role tag (target §7 column) is one
   of `Stabilising`, `Destabilising`, `Context-dependent`.
4. Re-confirm the primary signals (target §7 column) are declared in
   target §8.
5. Re-confirm the intent line begins with `Exists to` and is
   scenario-name-free.

Write the resulting canonical taxonomy table into
`simulation-build-log.md §B.4`. This table is the input to Phase 3's
gate. If any row fails to confirm, raise an `AskUserQuestion`
defect; the user re-invokes `define-simulation-scenario-skill.md` in
revise mode to update target §7; the pipeline re-validates.

The diversity rules of `06-step2-agent-design.md §2.2.1` are
**already encoded** in `define-simulation-scenario-skill.md §7
diversity rules`; the pipeline re-checks them here.

### 5.3 Artefacts

- `simulation-build-log.md §B.4` — taxonomy table that mirrors target
  §7 with one extra column `Pipeline confirmation` (`confirmed` /
  `defect raised`).

### 5.4 Exit Conditions

- Every target §7 row has a `confirmed` entry in §B.4.
- Diversity verification (`06-step2-agent-design.md §2.2.3`) passes.
- §A AGENT_POOL gate log is created (header row only) — ready for
  Phase 3 to fill.

---

## 6. Phase 3 — AGENT_POOL Gate and Agent Design

This is the longest phase and the one this pipeline most carefully
orchestrates. It runs the **three-stage match** for every candidate,
then either reuses or designs, and ends with **three-PASS** validation
plus write-back.

### 6.1 Entry Conditions

- Phase 2 exit conditions hold.
- The domain folder `masim/agents/defines/<domain>/` exists (the
  pipeline creates it in lowercase kebab-case if it does not).

### 6.2 Three-Stage Match Protocol

For each candidate from §B.4, run stages 1 → 2 → 3 in order. The
result of each candidate's run is appended to §A as a single row:

```markdown
| Candidate archetype | Stage reached | Outcome            | Pool file                                                   |
|---------------------|---------------|--------------------|-------------------------------------------------------------|
| trend-follower      | 3             | reuse              | masim/agents/defines/finance/momentum-trader.md              |
| panic-leveraged-LP  | 2             | new                | (to be created)                                             |
| fundamentalist      | 3             | fork (calibration) | masim/agents/defines/finance/fundamental-analyst.md (parent) |
```

**Stage 1 — Filename scan.** List every `*.md` in the domain folder.
Compare each filename's kebab-case role phrase against the candidate's
tentative role. Three filename-similarity buckets:

- *Exact / near-exact match* (≥0.8 token overlap): escalate to Stage 2.
- *Family match* (same theory family hinted by the name, e.g.
  `momentum-trader.md` when the candidate is `trend-follower`):
  escalate to Stage 2.
- *No match*: candidate is filename-novel; still escalate to Stage 2
  if any Stage-2 fingerprint is plausibly compatible (cheap to check).

**Stage 2 — Summary fingerprint check.** For every Stage-1
escalation, read **only** the H1 line and the Summary table (the 7
canonical rows: Archetype, Theory Family, Behavioral Tendency /
Market Role, Time Horizon, Risk Tolerance, Information Asymmetry,
Determinism). Compare each row to the candidate's intent in §B.4.

- ≥5 rows match → escalate to Stage 3.
- ≥3 rows match AND Theory Family matches → escalate to Stage 3.
- Otherwise → candidate is genuinely new; record `Outcome: new` and
  proceed to §6.3 Design.

**Stage 3 — Full-text inspection.** Read the rest of the candidate
file: Definition and Goals, Theoretical Foundation, Decision
Information Set, Core Behavioral Mechanism, Parameters. Decide one
of:

| Outcome                       | Trigger                                                                                       | Action                                                                                                                                               |
|-------------------------------|-----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Reuse as-is**               | Mechanism, signal set, parameters all compatible.                                             | Reference the pool file from `simulation-bases.md §4.{N}`; embed only population/instance count. **No new file** in the pool.                        |
| **Reuse + scenario override** | Mechanism + signals match; only parameter defaults differ.                                    | Reference the pool file; add a "Scenario calibration override" sub-heading under §4.{N}.6 with per-parameter deltas. **No new file** in the pool.    |
| **Fork**                      | Theory family matches; a substantive mechanism (signals, math, activation) genuinely differs. | Treat as new design (§6.3), file a sibling in the pool whose Theoretical Foundation cites the parent and explicitly states the mechanism difference. |
| **Design new**                | None of the above.                                                                            | Treat as new design (§6.3), file a fresh entry in the pool.                                                                                          |

All decisions update §A. The §A table is the single auditable record
of why each agent was reused, forked, or invented.

### 6.3 Design Procedure (for `new` / `fork` outcomes)

For every candidate with outcome `new` or `fork`:

1. **Author against the handbook.** Open
   `masim/skills/agent-design-skill.md` and use **§3 Section-by-Section
   Requirements** (§3.1 — §3.11) as the skeleton. Fill every section per
   the handbook's exact requirements.
2. **Apply financial-domain instantiation.** Use
   `02-root-documents-spec.md §4.1` for:
   - §4.1.1 Theory Family palette
   - §4.1.2 Real-world counterpart enumeration
   - §4.1.3 Stylized-fact catalogue
   - §4.1.4 Regime palette (and the `Market Contribution by Regime`
     relabel)
   - §4.1.5 Action Space row-label substitution table
   - §4.1.6 What stays unchanged
3. **Write standalone form to the pool.** The pool file uses standalone
   header levels (H1 title, H2 sections, H4 behavioral-framework
   sub-blocks). Filename: `<kebab-case-role>.md`. Path:
   `masim/agents/defines/<domain>/<kebab-case-role>.md`.
4. **Embed re-levelled form in `simulation-bases.md §4`.** Shift the
   pool file's header levels down by two so investor title sits at
   `###`, handbook §3.x sections at `####`, handbook §3.6.y
   sub-blocks at `######`, numbered `4.{N}.x`.

### 6.4 Three-PASS Handbook §6 Review

Every newly authored agent (in both the pool file and the re-levelled
`simulation-bases.md §4.{N}` block) MUST pass the **Validation
Checklist** at `agent-design-skill.md §6` **three consecutive times**
before it is accepted.

| Pass # | Reviewer perspective                       | What to look for                                                                                                 |
|--------|--------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| 1      | Structural completeness                    | Section presence and order; required tables / fields; header levels; canonical naming.                           |
| 2      | Cross-section consistency (handbook §5)    | Every §3.7 parameter appears in §3.6.4; every §3.6.1 signal consumed in §3.6.2; every §3.5 trigger has a branch. |
| 3      | Evidence provenance + scenario-portability | Every substantive choice cites Type 1 — 4 evidence; ≤20 % Type 6; no scenario names, fixed rounds, or topology.  |

**The same checklist runs in all three passes.** What differs is the
reviewer's attentional emphasis. Any single unchecked item in any of
the three passes resets the count to zero; the author fixes the
defect and the three-pass cycle restarts from Pass 1.

Three consecutive PASS runs are required before the candidate is
accepted. The §A row is updated to mark the candidate as
*approved*. The pool file is saved; the re-levelled block is
written into `simulation-bases.md §4`.

### 6.5 Exit Conditions

- Every candidate from §B.4 has a row in §A with an `approved`
  outcome.
- Every `new` / `fork` outcome has a corresponding standalone file in
  `masim/agents/defines/<domain>/`.
- `simulation-bases.md §4` contains a re-levelled embedded block (or
  reuse pointer) for every candidate.
- The handbook §6 checklist has been run three times consecutively
  with PASS results for every new/fork agent.

---

## 7. Phase 4 — Scenario Build

### 7.1 Entry Conditions

- Phase 3 exit conditions hold.
- `simulation-bases.md §1, §2, §3, §4` are populated; only §5 — §9
  remain to be written.

### 7.2 Procedure

Dispatch into `implement-simulation-skill/` in the following order:

1. `02-root-documents-spec.md` — finish `simulation-bases.md §5 — §9`
   and write `analysis-bases.md` end-to-end.
2. `03-variant-documents-spec.md` — write `{Variant}/explain.md` and
   `{Variant}/analysis.md` for each chosen variant.
3. `07-step3-config.md` — produce `configs/{Simulation}/{Variant}/
   simulation.yml`, `players.yml`, `topology.yml`, `persona.yml`.
4. `08-step4-implement.md` — implement `players.py`, `run_*.py`,
   `analysis.py` for each variant.

The variant set is sourced **exclusively** from the target file's
§10.1 build matrix. Only variants explicitly marked `Yes` in §10.1 MUST
be built; variants marked `No` MUST NOT have folders created. There is
no implicit default — if §10.1 is absent, Phase 0 will already have
returned the target file as a defect before Phase 4 can run.

### 7.3 Artefacts

- `examples/{SimulationName}/simulation-bases.md` (complete).
- `examples/{SimulationName}/analysis-bases.md` (complete).
- For each built variant `V`:
  - `examples/{SimulationName}/V/players.py`
  - `examples/{SimulationName}/V/run_*.py`
  - `examples/{SimulationName}/V/analysis.py`
  - `examples/{SimulationName}/V/explain.md`
  - `examples/{SimulationName}/V/analysis.md`
  - `configs/{SimulationName}/V/{simulation,players,topology,persona}.yml`

### 7.4 Exit Conditions

- Every artefact above exists.
- `get_problems` returns clean for every modified `.py` file.
- YAML syntax validation succeeds for every `.yml` file (see
  `09-step5-to-10-review.md §5.3`).

---

## 8. Phase 5 — Scenario-Level 3-PASS Review

### 8.1 Entry Conditions

- Phase 4 exit conditions hold.

### 8.2 Procedure

Run `implement-simulation-skill/09-step5-to-10-review.md` Steps 5 — 9 as a
single review batch. Then run the same batch **three times in a row**.
Three consecutive PASS runs are required before Phase 6 may start.

| Pass # | Reviewer perspective                            | Anchors in `09-step5-to-10-review.md`                                     |
|--------|-------------------------------------------------|---------------------------------------------------------------------------|
| 1      | Theory-code alignment (Step 5)                  | §5.1, §5.2, §5.3, §5.4                                                    |
| 2      | Code quality + analysis tools (Steps 6 — 7)     | §6.1, §6.2, §6.3, §7.1; `10-evaluation-architecture.md` import compliance |
| 3      | Documentation + final cross-check (Steps 8 — 9) | §8 documentation hooks, §9 readiness                                      |

As in §6.4, any unchecked item in any pass resets the count. The
three-PASS rule is non-negotiable; partial approvals are not
accepted.

### 8.3 Exit Conditions

- `09-step5-to-10-review.md` Steps 5 — 9 have all checks ticked
  across three consecutive runs.
- The contract file's §C Open Questions has been swept; any
  remaining open question is either answered, deferred with a
  written justification, or escalated to the user.

---

## 9. Phase 6 — Execution and Final Review

### 9.1 Procedure

Execute `09-step5-to-10-review.md` Step 10:

1. Run every built variant end-to-end at the smoke-test scale
   defined in `configs/AssetBubble/Rule/simulation.yml`
   (the reference smoke-test).
2. Confirm `analysis.py` produces all metrics from `analysis-bases.md
   §2`.
3. Inspect at least one figure per variant for sanity.
4. Run the final readiness checklist in `09 §9` against the
   completed scenario.

### 9.2 Exit Conditions and Closeout

- All smoke-test runs complete without uncaught exceptions.
- `simulation-build-log.md §D Build Log` is appended with one row per
  phase recording `Phase`, `Date`, `Outcome`, `Reviewer`, `Notes`.
- Both the target file `{domain}-{scenario}.md` and
  `simulation-build-log.md` have `Status` bumped from `locked` to
  `released` simultaneously.

---

## 10. Cross-Phase Traceability Guarantee

This guarantee is the pipeline's final invariant. Every artefact
produced by any later phase MUST trace back, through
`simulation-build-log.md`, to a section of the **target file**
`{domain}-{scenario}.md`:

| Downstream artefact                                    | Anchor in `simulation-build-log.md` | Original anchor in target file |
|--------------------------------------------------------|-------------------------------------|--------------------------------|
| `simulation-bases.md §1` (Phenomenon Definition)       | §B.3 historical events              | target §2 + §6                 |
| `simulation-bases.md §2` (Theoretical Foundation)      | §B.1 theories                       | target §4                      |
| `simulation-bases.md §3` (market mechanism choices)    | §B.2 stylized facts                 | target §5 + §8                 |
| `simulation-bases.md §4.{N}` block                     | §A row + §B.4 taxonomy entry        | target §7                      |
| `simulation-bases.md §6` parameter rows                | §B.5 estimates                      | target §9                      |
| `masim/agents/defines/<domain>/<file>.md` (new entries) | §A row with outcome ∈ {new, fork}   | target §7 row marked as new    |
| `players.yml` extras with `# Source:` comment          | §B.5 (or override in §4.{N}.6)      | target §9                      |
| Any prompt persona trait in `LLM/prompts.py`           | A handbook §3.4 or §3.6.5 line      | target §4 + §7                 |
| Any analysis metric in `analysis-bases.md §2`          | §B.2 stylized fact / §B.3 event     | target §5 + §6 + §10.2         |
| Variant build choices                                  | — (pipeline records phase)          | target §10.1                   |

Before Phase 6 closes, run a top-down sweep: open
`simulation-build-log.md`, walk each table row, and confirm the
downstream artefact exists and cites the upstream entry. Any
unanchored downstream artefact is a defect and MUST be repaired.

---

## 11. Tooling and Interaction Rules

- **AskUserQuestion**: ≤4 options per question. Use `multiSelect:true`
  only when the answer space is genuinely a set (e.g. Theory Families,
  variants to build). Provide an `Other` option only when free-text is
  meaningful; otherwise omit it.
- **TodoWrite**: maintain a six-item todo list mirroring Phases 0 — 6.
  Update on phase boundaries; do not micro-track inside a phase.
- **Path discipline**: every cross-skill reference uses paths rooted at
  `masim/skills/...` or `examples/...`. The string `masim/format/...`
  is a legacy path and MUST be rewritten on contact.
- **Filename discipline**: pool files use kebab-case role phrases
  (`momentum-trader.md`, not `MomentumTrader.md`). Scenario folders use
  PascalCase (`CarryTradeUnwind/`). YAML config folders mirror the
  scenario folder name exactly.

---

## 12. Pipeline Entry Checklist (Pre-Run)

Run this checklist once before invoking Phase 0:

- [ ] A target file exists at
      `examples/{ScenarioName}/{domain}-{scenario}.md`, produced by
      `masim/skills/define-simulation-scenario-skill.md` (its §1 Meta
      shows a `Produced By` row).
- [ ] `define-simulation-scenario-skill.md §11 Validation` has been
      run inside that skill three consecutive times with a PASS result
      before the file was written to disk.
- [ ] The proposed `{ScenarioName}` is unique under `examples/`.
- [ ] The chosen `{domain}` has (or will be created as) a folder
      under `masim/agents/defines/`. For new domains, the target file
      must include `§A Domain Palette Appendix`.
- [ ] You have access to academic sources sufficient to *verify*
      every citation in target §4, §5, §6, §9.
- [ ] Working tree is clean (no unrelated local modifications).
- [ ] You have read this file end-to-end at least once.

If any item is unchecked, fix it before starting Phase 0.

---

## 13. Skill References (Quick Index)

| Topic                                 | File                                                                   |
|---------------------------------------|------------------------------------------------------------------------|
| **Scenario target file spec**         | `masim/skills/define-simulation-scenario-skill.md`                     |
| Universal Agent Design Handbook       | `masim/skills/agent-design-skill.md`                                   |
| Methodology overview                  | `masim/skills/implement-simulation-skill/00-overview.md`               |
| Directory layout                      | `masim/skills/implement-simulation-skill/01-mandatory-structure.md`    |
| Root document specs + §4.1 finance    | `masim/skills/implement-simulation-skill/02-root-documents-spec.md`    |
| Variant document specs                | `masim/skills/implement-simulation-skill/03-variant-documents-spec.md` |
| Step 0 (Define) and contract template | `masim/skills/implement-simulation-skill/04-step0-load-target.md`      |
| Step 1 (Research)                     | `masim/skills/implement-simulation-skill/05-step1-research.md`         |
| Step 2 (Agent design + Pool gate)     | `masim/skills/implement-simulation-skill/06-step2-agent-design.md`     |
| Step 3 (Config)                       | `masim/skills/implement-simulation-skill/07-step3-config.md`           |
| Step 4 (Implement)                    | `masim/skills/implement-simulation-skill/08-step4-implement.md`        |
| Steps 5 — 10 (Validate, review, run)  | `masim/skills/implement-simulation-skill/09-step5-to-10-review.md`     |
| AssetBubble reference                 | `masim/skills/implement-simulation-skill/15-reference-assetbubble.md`  |
| AGENT_POOL directory                  | `masim/agents/defines/`                                                 |
| Project structure overview            | `docs/structure.md`                                                    |
