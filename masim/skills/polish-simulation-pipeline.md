---
name: polish-simulation-pipeline
purpose: Top-level pipeline for **auditing and standardising an existing MASim simulation scenario** (already present under `examples/{ScenarioName}/`) so that every artefact conforms to the current versions of the reusable, domain-neutral skill suite (`define-simulation-scenario-skill.md`, `agent-design-skill.md`, `implement-simulation-skill/`). This pipeline follows the same Step 0 — Step 10 spine as `create-simulation-pipeline.md`, but at every step the action is **audit + patch**, not "produce from scratch". Each step in this pipeline anchors to the corresponding step file's `## Contract (Inputs / Outputs / Polish Hooks)` block; the actual audit work is dispatched to `agent-design-skill.md` and to the individual `implement-simulation-skill/{04..09}-*.md` files. When an audit uncovers a defect, the pipeline patches locally, re-runs the step's Polish Hooks three consecutive times, and commits.
status: canonical
audience: Users and reviewers bringing a pre-existing scenario in `examples/` up to the current skill baseline. The pipeline is domain-neutral — it applies to finance, opinion dynamics, epidemics, sociology, or any other domain whose scenario target file conforms to `define-simulation-scenario-skill.md`.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
invocation: Call this file when a scenario under `examples/{ScenarioName}/` already contains one or more of `simulation-bases.md`, `analysis-bases.md`, or any variant subdirectory declared in the target file `§10.1 Variants to Build`, and the intent is to align these artefacts with the current skill baseline. Do NOT invoke `create-simulation-pipeline.md` on an already-built scenario — it assumes an empty target folder and will refuse to overwrite. Do NOT open the individual `implement-simulation-skill/` step files directly during a polish run except when the step below explicitly dispatches to them; in particular, always read the target step file's `## Contract` block first — that block is the sole contract this pipeline anchors to.
---

# Polish-Simulation-Pipeline — Audit an Existing Scenario Against the Latest Skill Baseline

## 0. Scope and Authority

This skill governs an **audit-and-patch upgrade** of an existing
scenario. It does not add new empirical content, does not change the
scenario's research question, and does not invent new agent
archetypes. It brings every existing artefact into conformance with
the current versions of:

- `masim/skills/define-simulation-scenario-skill.md` — the
  target-file specification and its §11 Validation Checklist. The
  scenario target file is **produced by invoking this skill**; users
  MUST NOT hand-author it. Post-lock changes go through **§9.3 revise
  mode** of the define skill, never through direct hand-editing.
- `masim/skills/agent-design-skill.md` — the Universal Agent Design
  Handbook (canonical section order §3.1 — §3.11 and §6 Validation
  Checklist). This handbook is domain-neutral; the pipeline dispatches
  every per-agent audit to it.
- `masim/skills/implement-simulation-skill/` — per-step methodology
  files, each of which exposes a stable `## Contract (Inputs /
  Outputs / Polish Hooks)` block that this pipeline anchors to. The
  individual step files own the domain-neutral audit logic; this
  pipeline is the orchestrator.

If, during audit, the scenario is found to require materially new
research — e.g., a stylized fact was never sourced, or an agent
archetype has no theory anchor — the polish run **halts and
returns** via `AskUserQuestion`. The user must then either:

- **Re-invoke `define-simulation-scenario-skill.md` in §9.3 revise
  mode** to patch the missing content upstream in the target file, and
  then resume the polish run at the halted step (with three-PASS
  reset), or
- Explicitly scope the deficit out of the polish run and record it in
  the target §0 Meta CHANGELOG as an accepted gap.

A polish run MUST NOT silently invent missing evidence and MUST NOT
fabricate citations, DOIs, parameter values, or theoretical
mechanisms. A polish run MUST NOT hand-edit the target file except
for (a) the single Status transition performed at Step 0 and Closeout,
and (b) appending CHANGELOG lines to §0 Meta. All other target-file
changes go through the define skill's revise mode.

| Concern                                        | Owner                                                                       |
|------------------------------------------------|-----------------------------------------------------------------------------|
| Target-file specification we align to           | `masim/skills/define-simulation-scenario-skill.md` (§11 checklist, §9.3 revise mode) |
| Universal Agent Design Handbook                 | `masim/skills/agent-design-skill.md` (§3 canonical order, §6 checklist)     |
| Per-step audit contract                         | `masim/skills/implement-simulation-skill/{04..09}-*.md` `## Contract`       |
| Root document conformance                       | `implement-simulation-skill/02-root-documents-spec.md`                      |
| Variant document conformance                    | `implement-simulation-skill/03-variant-documents-spec.md`                   |
| Directory / file layout                         | `implement-simulation-skill/01-mandatory-structure.md`                      |
| AGENT_POOL three-stage match protocol           | `implement-simulation-skill/06-step2-agent-design.md §2.2.0`                |
| Three-PASS validation discipline                | This file §3 and `agent-design-skill.md §6`                                 |
| From-scratch pipeline (contrast)                | `masim/skills/create-simulation-pipeline.md`                                |

---

## 1. Design Philosophy

Six commitments shape every step of a polish run. Four are inherited
from `create-simulation-pipeline.md §1` (they apply equally to
upgrades); two are polish-specific.

**Shared with the from-scratch pipeline.**

1. **Same skill files, same order, different action.** A polish run
   walks the exact same sequence as the from-scratch pipeline
   (Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Steps 5 — 10). At
   every step the reference material is the same file — including its
   `## Contract (Inputs / Outputs / Polish Hooks)` block. What
   changes is the verb: instead of *producing* the outputs listed
   under **Outputs**, we *audit* every existing artefact against the
   **Polish Hooks** listed in that block, and dispatch the actual
   audit work into `agent-design-skill.md` (per-agent) or the relevant
   `implement-simulation-skill/{04..09}-*.md` step file.
2. **The `## Contract` block is authoritative.** Every step in this
   pipeline (§4 — §9) anchors explicitly to the corresponding step
   file's `## Contract` block. If a Contract block and any prose
   elsewhere in the same step file disagree, the Contract block wins
   (it is the audit-facing surface; prose is developer-facing
   commentary). Contract-block edits are the only edits this pipeline
   makes to files under `masim/skills/` during a polish run, and they
   are non-destructive additions, not rewrites of adjacent prose.
3. **AGENT_POOL reuse gate is re-run.** Existing agents may currently
   reference stale pool entries (or fail to reference the pool at
   all). The polish run re-executes the three-stage match against the
   current pool at Step 2 and updates §3.11 Provenance to reflect the
   correct `reuse` / `reuse+override` / `fork` / `new` outcome.
4. **Three consecutive PASSes equals approved.** Every checklist —
   `define-simulation-scenario-skill.md §11`, `agent-design-skill.md
   §6`, and each Polish Hook list in the step Contracts — MUST run
   three consecutive times without failure. A single FAIL resets the
   count to zero.

**Polish-specific.**

5. **Preserve intent, upgrade form.** The scenario's research
   question, agent roster, and empirical claims are inherited from
   the existing artefacts. The polish pipeline changes structure,
   wording, anchoring, and validation posture — not substance. Any
   substantive change (new theory anchor, revised research goal, new
   agent archetype, revised parameter range, revised variant list)
   MUST be pushed through `define-simulation-scenario-skill.md` in
   revise mode; the polish pipeline never edits target-file substance
   directly.
6. **No `simulation-build-log.md`.** A polish run is a bounded audit,
   not a long-running build. The build-log contract used by
   `create-simulation-pipeline.md` is **skipped**. Audit trail is
   distributed across three places, in priority order:
   - **Target file §0 Meta CHANGELOG** — one line per step that
     produced a patch, summarising what was standardised.
   - **Per-agent §3.11 Design Provenance** — updated in place to
     record that this agent's specification was audited on this date
     against the handbook, and to list any structural changes.
   - **Git commit history** — one commit per completed step (Step 2
     may produce multiple commits, one per audited agent; Step 4 may
     produce one commit per audited variant). The commit history is
     the polish run's primary process log.
   If a legacy `simulation-build-log.md` exists in the scenario folder
   from a previous from-scratch build, it is NOT deleted. Instead, on
   Closeout the pipeline appends a single line to its §D Phase Log:
   `YYYY-MM-DD  Superseded by polish audit; polish trail lives in
   target §0 CHANGELOG + git history.` This preserves the historical
   record without letting the build-log drift into a stale live
   document.

---

## 2. Pipeline Overview

The polish run has one preflight, seven audit steps, and one
closeout. Each step maps 1-to-1 to a file in
`implement-simulation-skill/` (with Step 0 additionally anchoring to
`define-simulation-scenario-skill.md`). The action at every step is
"read Contract, dispatch audit, patch, three-PASS Polish Hooks,
commit".

```text
    ┌────────────────────────────────────────────────────────────┐
    │ Preflight — Inventory & Scope Confirmation                 │
    │   List every file under examples/{ScenarioName}/;          │
    │   confirm repo clean; assert not-a-fresh-scenario;         │
    │   record which built variants exist (from target §10.1).   │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Step 0 — Target File Gate                                  │
    │   File: 04-step0-load-target.md ## Contract → Polish Hooks │
    │   Case A: target file exists → three-PASS §11 only.        │
    │   Case B: target file absent → AskUserQuestion (invoke     │
    │   define skill, or reverse-reconstruct + revise mode);     │
    │   pre-consistency check §4.{N} vs impl vs configs;         │
    │   then §11 three-PASS; lock.                               │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Step 1 — Research Audit                                    │
    │   File: 05-step1-research.md ## Contract → Polish Hooks    │
    │   DOIs resolve; every Theory block six-field complete;     │
    │   every target §4.{k} anchor has a matching Theory block   │
    │   (bidirectional).                                         │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Step 2 — Agent + Environment Design Audit                  │
    │   File: 06-step2-agent-design.md ## Contract → Polish Hooks│
    │   Dispatches per-agent audit into agent-design-skill.md    │
    │   (§3 canonical order, §6 checklist 3-PASS).               │
    │   AGENT_POOL three-stage match rerun (handles reuse/       │
    │   fork/new AND outcome-shrink new→reuse).                  │
    │   Also audits root doc §3 Environment Design, §5 Diversity │
    │   Verification, §7 Communication and Round Structure.      │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Step 3 — Config Audit                                      │
    │   File: 07-step3-config.md ## Contract → Polish Hooks      │
    │   Every YAML parses; # Source: comments trace to target §9 │
    │   / bases §4.{N}.7 / §6; variant folders match target      │
    │   §10.1 exactly (extras and missing both flagged).         │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Step 4 — Implementation Audit                              │
    │   File: 08-step4-implement.md ## Contract → Polish Hooks   │
    │   No-defaults; py_compile clean; import smoke; §4.2.3      │
    │   field-access rule; explain.md §2 / analysis.md §2        │
    │   bidirectional completeness; RuleLLM dual-section prompt  │
    │   invariant; Rag _RAG_FALLBACK defined AND referenced.     │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Steps 5–10 — Scenario-Level Review + Smoke                 │
    │   File: 09-step5-to-10-review.md ## Contract → Polish Hooks│
    │   Three consecutive passes, split by perspective:          │
    │     Pass 1: theory–code (§5.1–§5.4)                        │
    │     Pass 2: code + analysis (§6.1–§6.3, §7.1)              │
    │     Pass 3: docs + final cross-check (§8, §9)              │
    │   Then smoke-run every built variant at 5-round scale.     │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Closeout — Traceability + CHANGELOG + Status               │
    │   Every downstream artefact traces to a target §; write    │
    │   §0 Meta CHANGELOG summary; supersede any legacy build-   │
    │   log; Status: locked → released.                          │
    └────────────────────────────────────────────────────────────┘
```

Each step below declares **entry conditions**, **procedure** (which
Polish Hooks to run and how to patch, plus which downstream skill file
receives the dispatch), **artefacts changed**, and **exit
conditions**. A step MUST NOT start until its entry conditions hold; a
step MUST NOT be marked done until its exit conditions hold and its
Polish Hooks have three consecutive PASS runs.

**Halt recovery path.** Whenever a step halts via `AskUserQuestion`
and the user selects the "re-invoke define skill in revise mode"
option, the polish run is paused. Once the revise-mode invocation
returns and the target file has been updated (with a new §0 Meta
CHANGELOG line recorded by the define skill), the polish run resumes
at the halted step with the three-PASS count reset to zero. No steps
already completed are re-run.

---

## 3. Preflight — Inventory and Scope Confirmation

### 3.1 Entry Conditions

- The scenario folder `examples/{ScenarioName}/` exists and contains
  at least one downstream artefact: any of `simulation-bases.md`,
  `analysis-bases.md`, any variant subdirectory declared in target
  §10.1, or a matching folder under `configs/{ScenarioName}/`. If the
  folder is empty, this pipeline is the wrong tool — invoke
  `create-simulation-pipeline.md` instead.
- Working tree is clean (`git status` shows no unrelated diffs).
- The reader has read this file end-to-end, plus the `## Contract`
  block of every file listed in §14.

### 3.2 Procedure

1. **Inventory.** Enumerate every file under
   `examples/{ScenarioName}/` and every file under
   `configs/{ScenarioName}/`. Classify each against the layout in
   `implement-simulation-skill/01-mandatory-structure.md §1`:

   | Class                        | Meaning                                                                                  |
   |------------------------------|------------------------------------------------------------------------------------------|
   | Present, conforming          | File exists at the expected path with the expected name (structure only; content audited later). |
   | Present, non-conforming      | File exists but has a stale name, wrong header levels, or missing sections.              |
   | Missing (required)           | File is missing but the current spec requires it (e.g., the target file itself).         |
   | Missing (conditional)        | File is missing, but its variant is not marked `Yes` in target §10.1 — no action needed. |
   | Present, deprecated          | File exists under an old name (e.g., `simulation-define.md`) and must be renamed / merged. |

2. **Built-variant list.** Determine the set of variants declared
   `Yes` in target §10.1 Variants to Build. Cross-check that the
   scenario folder contains a subdirectory for each `Yes` variant and
   for no `No` variant. The variant scheme is domain-neutral and MUST
   be read from the target file — do NOT assume a fixed
   `{Rule, LLM, RuleLLM, Rag}` scheme; the target file may declare a
   different set (for example, an epidemics scenario might build
   `Rule` and `LLM` only, or a sociology scenario might add a
   `RagAgent` variant). This built-variant set drives Step 3 (Config
   Audit) and Step 4 (Implementation Audit).
3. **Workspace note.** Write the inventory to a throwaway working
   note under the runtime workspace (see the runtime environment for
   the concrete path; conceptually, this is `<workspace>/{ScenarioName}
   -polish-inventory.md`). This file is NEVER committed.
4. **Placeholders.** Fix the following placeholders for the rest of
   the run:
   - `<scenario_path>` = `examples/{ScenarioName}/`
   - `{ScenarioName}` = folder name (PascalCase)
   - `{Domain}` = the value in target §1 `Domain` — used in
     AGENT_POOL paths and to select any domain-instantiation appendix
     (e.g., a finance-instantiation appendix in
     `02-root-documents-spec.md`, or an equivalent appendix for
     opinion / epidemics / sociology). Whether such appendices exist
     depends on the scenario's domain palette in the target file's
     §A Domain Palette Appendix.
   - `{V}` = a member of the built-variant list (variant name is a
     directory name, not a hardcoded token).

### 3.3 Exit Conditions

- Inventory complete; every artefact assigned one of five classes.
- Built-variant list determined and recorded (from target §10.1).
- Domain and any domain-instantiation appendix identified.
- No changes have yet been made to the repository.

---

## 4. Step 0 — Target File Gate

### 4.1 Reference Contract

Anchor:
`masim/skills/implement-simulation-skill/04-step0-load-target.md` →
`## Contract (Inputs / Outputs / Polish Hooks)`. The Contract's
Polish Hooks branch on whether the target file already exists.

### 4.2 Entry Conditions

- Preflight complete.
- Repository clean.

### 4.3 Procedure

**Case A — target file present.**

1. Read `examples/{ScenarioName}/{domain}-{scenario}.md`.
2. Run `masim/skills/define-simulation-scenario-skill.md §11
   Validation Checklist` three consecutive times. Any FAIL resets the
   count to zero.
3. If a FAIL is a **structural** issue (missing sub-section, wrong
   header level, wrong ordering), patch in place and re-run. Header
   ordering, section-title normalisation, and boilerplate scaffolding
   are within polish-pipeline authority.
4. If a FAIL is a **substantive** issue (missing citation, unresolved
   DOI, unsupported numeric range, missing research question, missing
   pass/fail criterion), halt via `AskUserQuestion` with options:
   - **Re-invoke `define-simulation-scenario-skill.md` in §9.3
     revise mode** to patch the missing content upstream. Once the
     define skill returns, resume this step with the §11 three-PASS
     count reset to zero.
   - Scope the deficit out of this polish run and record it in the
     target §0 Meta CHANGELOG as an accepted gap (the scenario stays
     `locked` but marked with the gap).
   - Abort the polish run.
5. After three consecutive PASS runs, ensure the target §1 `Status`
   is `locked` (upgrade `draft → locked` if necessary — this is the
   only edit to the Status field the polish pipeline is authorised
   to make at Step 0).
6. Append one line to §0 Meta CHANGELOG:
   `YYYY-MM-DD  Polish target-file gate: existing (§11 3-PASS).`

**Case B — target file absent.**

**Policy (binding).** When the scenario is missing its target file, the
polish pipeline's DEFAULT and MANDATED path is to invoke
`define-simulation-scenario-skill.md` end-to-end and produce the target
file through that skill. Reverse-reconstruction is a documented
last-resort fallback and MUST NOT be selected unless the user
explicitly rejects the default and asserts that the original scenario
author's minimal inputs (scenario name, domain, phenomenon sketch,
variant preference, anchor event) cannot be re-elicited. This policy
exists because the define skill enforces the same validation surface
the polish pipeline anchors to, guaranteeing internal consistency of
the audit chain; reverse-reconstruction bypasses that surface and can
only ratify what is already in the downstream artefacts.

1. **Pre-consistency check.** Before either option is offered, verify
   internal consistency of the existing artefacts. This is a rapid
   read-only sweep:
   - Every `§4.{N}` block in `simulation-bases.md` has a matching
     agent-implementation module (typically `players.py`, or whatever
     the built variants use as their agent-implementation module).
   - Every agent class in each built variant's implementation module
     has a matching `§4.{N}` block.
   - Every `players.yml` `extras.<agent>` group corresponds to an
     agent in `simulation-bases.md §4.{N}` and to a class in the
     implementation module.
   If any of these three cross-links is broken, halt via
   `AskUserQuestion` — reverse-reconstruction is unsafe on an
   internally inconsistent scenario, and the "invoke the define skill"
   option is also unsafe until the mismatch is resolved. The user
   must resolve the mismatch first (typically by editing the
   downstream artefact that is out of sync with `simulation-bases.md`)
   and then rerun this step.
2. **Halt to `AskUserQuestion`** with two options (max four total per
   the AskUserQuestion hard limit):
   - **Invoke the define skill (MANDATED DEFAULT).** Direct the user to
     invoke `define-simulation-scenario-skill.md`; that skill produces
     the target file end-to-end from minimal inputs (scenario name,
     domain, phenomenon sketch, optional variant preference, optional
     fixed anchor event). Pause the polish run and resume at Step 0
     Case A once the file is present. This option MUST be selected
     unless the user explicitly asserts the fallback condition below.
   - **Reverse-reconstruct (LAST-RESORT FALLBACK — requires explicit
     user override).** Only if the user asserts that the original
     scenario author's minimal inputs cannot be re-elicited: seed the
     target file section-by-section from the mapping table below, then
     re-invoke `define-simulation-scenario-skill.md` in §9.3 revise
     mode to validate and lock the reconstructed target. The polish
     pipeline writes the seed but does NOT lock the file itself;
     locking is always performed by the define skill.

3. **Reverse-reconstruction seed mapping** (used only when the user
   selects the reverse-reconstruct option):

   | Target section              | Source of content in existing scenario                                                    |
   |-----------------------------|-------------------------------------------------------------------------------------------|
   | §1 Meta                     | folder name (PascalCase → phrases); `Status: draft`.                                       |
   | §2 Phenomenon Statement     | `simulation-bases.md §1` narrative + `analysis-bases.md §1` framing.                        |
   | §3 Research Goals           | `analysis-bases.md §1` (hypotheses reverse-mapped to research questions).                  |
   | §4 Theoretical Anchors      | Union of every `§4.{N}.4` (`Theoretical Foundation`) block in `simulation-bases.md`; one target §4.{k} per unique theory. |
   | §5 Stylized Facts           | `simulation-bases.md §1.1.2 / §1.1.3` (empirical regularities) + `analysis-bases.md §6.1`. |
   | §6 Historical / Empirical Anchors | `simulation-bases.md §1` narrative + `simulation-bases.md §8` case studies.           |
   | §7 Agent Roster             | One row per `§4.{N}` block in `simulation-bases.md`.                                        |
   | §8 Environment Specification| `simulation-bases.md §3` Environment Design + any domain-specific §3 subsections.           |
   | §9 Parameter Seeds          | Union of every `Parameters` table across per-agent specs + `configs/{ScenarioName}/*/players.yml` extras + `simulation-bases.md §6`. |
   | §10.1 Variants to Build     | For each built variant subdirectory that exists in the scenario folder: `Yes`; for every variant subdirectory whose name is on any earlier scenario's roster but is absent here: `No`. |
   | §10.2 Pass / Fail Criteria  | `analysis-bases.md §2` metrics + §6.2 calibration targets.                                  |

   Any target section with no upstream source (typically §3 Research
   Goals and §10.2 Pass / Fail Criteria) is left as a placeholder that
   MUST be filled by the user during the subsequent revise-mode
   invocation. NEVER fabricate.

4. **Hand off to define skill in revise mode.** Once the seed is
   written, invoke `define-simulation-scenario-skill.md §9.3 revise
   mode` on the seed. The define skill runs its three checkpoints
   (C-1 / C-2 / C-3), performs §11 three-PASS validation, sets
   `Status: locked`, and appends its own §0 Meta CHANGELOG line. The
   polish pipeline does NOT independently run §11 in Case B — that is
   the define skill's authority.
5. Once control returns from the define skill, append one additional
   line to §0 Meta CHANGELOG:
   `YYYY-MM-DD  Polish target-file gate: reverse-reconstructed seed
   handed to define-skill revise mode.`

**Both cases.** No `simulation-build-log.md` is created — the polish
pipeline does not maintain one. If a legacy build-log already exists,
it is preserved for its historical value; the pipeline appends a
supersession line to its §D Phase Log at Closeout (see §10.3).

### 4.4 Artefacts Changed

- `examples/{ScenarioName}/{domain}-{scenario}.md`:
  - §0 Meta CHANGELOG (one line appended, plus any lines the define
    skill adds during revise-mode invocation).
  - §1 Status upgraded to `locked` (Case A) or set to `locked` by the
    define skill (Case B).
  - Structural fixes in place (Case A only). Substantive changes go
    through the define skill in revise mode; the polish pipeline
    itself never edits target-file substance.

### 4.5 Exit Conditions

- Target file exists at the canonical path.
- §11 has three consecutive PASS runs (either performed here in
  Case A or performed by the define skill in Case B).
- Target §1 Status is `locked`.
- §0 Meta CHANGELOG records this Step 0 audit.
- Pre-consistency check (Case B) passed.

Commit at end of step:
`polish({ScenarioName}): step0 target-file gate — <case A|B, existing|reverse-seeded>`.

---

## 5. Step 1 — Research Audit

### 5.1 Reference Contract

Anchor:
`masim/skills/implement-simulation-skill/05-step1-research.md` →
`## Contract (Inputs / Outputs / Polish Hooks)`.

### 5.2 Entry Conditions

- Step 0 exit conditions hold.
- `simulation-bases.md` and `analysis-bases.md` exist under
  `examples/{ScenarioName}/`. If either is missing, halt via
  `AskUserQuestion`: the polish pipeline does not synthesise research
  from scratch — those two files must be produced by the from-scratch
  pipeline before a polish run can proceed past Step 0.

### 5.3 Procedure

Run the three Polish Hooks declared in the Step 1 Contract, in order.
The audit logic itself lives in `05-step1-research.md`; this pipeline
dispatches to it and enforces the three-PASS discipline.

1. **DOI / URL resolution.** For every citation in
   `simulation-bases.md §1` and `§2` and every reference in
   `analysis-bases.md §1`, resolve the DOI or URL against the
   authoritative source (CrossRef for DOIs, publisher site for URLs,
   or a domain-appropriate registry). Any dead reference is a defect.
   Options for repair:
   - Correct the citation (typo, wrong DOI) if a matching resolvable
     citation can be verified.
   - Replace with an equivalent primary source if the original is a
     CrossRef bogus-DOI (see MEMORY: CrossRef returns bogus DOIs for
     arXiv preprints).
   - Halt via `AskUserQuestion` if no equivalent exists — the deficit
     is *substantive* and MUST be pushed through the define skill in
     revise mode, not silently patched.
2. **Six-field completeness per Theory block.** For every Theory
   block under `simulation-bases.md §2`, confirm all six sub-fields
   are present and non-empty:
   Citation, Core Insight, Mathematical Formulation, Empirical
   Evidence, Relevance to This Simulation, Calibration Implication.
   Fill any missing field from material present elsewhere in the
   file (§1 narrative, §4.{N} block, or a resolvable citation). Do
   NOT fabricate. If no upstream material covers a sub-field, halt.
3. **Bidirectional target-anchor coverage.**
   - Forward: every target `§4.{k}` theory anchor MUST have exactly
     one matching Theory block in `simulation-bases.md §2`.
   - Reverse: every Theory block in `simulation-bases.md §2` MUST
     correspond to some target `§4.{k}` anchor. Stray Theory blocks
     without a target anchor are a substantive discrepancy — either
     the target is out of date (push through define skill revise
     mode) or the theory is stray in bases.md (structural removal is
     within polish-pipeline authority).
   - Every target `§5` stylized fact MUST trace to a row in
     `simulation-bases.md §1.1.2` or `§1.1.3`, or to a citation
     footnote. Missing links are defects; add the trace or halt.

Run the three Polish Hooks three consecutive times. Any FAIL resets
the count.

### 5.4 Artefacts Changed

- `examples/{ScenarioName}/simulation-bases.md` — §1 and §2 patched
  in place (structural fills only, never new empirical claims).
- `examples/{ScenarioName}/analysis-bases.md` — §1 patched if a
  hypothesis row lost its target-§3 back-link.

Commit at end of step:
`polish({ScenarioName}): step1 research audit — <one-line summary>`.

### 5.5 Exit Conditions

- All three Step 1 Polish Hooks have three consecutive PASS runs.
- No stray Theory blocks; no missing Theory blocks; no dead DOIs.
- Bidirectional coverage between target §4/§5 and bases.md §2/§1.

---

## 6. Step 2 — Agent + Environment Design Audit

### 6.1 Reference Contract

Anchor:
`masim/skills/implement-simulation-skill/06-step2-agent-design.md` →
`## Contract (Inputs / Outputs / Polish Hooks)`. This step also
directly dispatches to:
- `masim/skills/agent-design-skill.md §3` (canonical section order,
  domain-neutral)
- `masim/skills/agent-design-skill.md §6` (Validation Checklist,
  domain-neutral)

The polish pipeline's role at Step 2 is orchestration and three-PASS
enforcement; the actual per-agent audit logic lives in the handbook.

### 6.2 Entry Conditions

- Step 1 exit conditions hold.
- Every agent surface expected by the current spec exists as `§4.{N}`
  blocks in `simulation-bases.md` (the embedded form is the only
  in-scenario agent surface). Any reused pool profile is referenced
  from the `§4.{N}` block via a relative path to
  `examples/AGENT_POOL/{Domain}/<kebab-name>.md`; the pool file is
  audited alongside the embedded block whenever it is referenced.

### 6.3 Procedure

Step 2 is split into two parts: (A) per-agent audit (dispatched to the
handbook), and (B) environment-and-structure audit (root doc §3, §5,
§7).

**Part A — Per-agent audit.**

For **each** agent, in target §7 roster order, do the following:

1. **Section order and completeness (Handbook §3).** Dispatch to
   `agent-design-skill.md §3` and confirm the canonical order §3.1
   Title → §3.2 Summary → §3.3 Definition and Goals → §3.4
   Theoretical Foundation → §3.5 Design Purpose and Activation
   Triggers → §3.6 Behavioral Framework → §3.7 Parameters → §3.8
   Worked Numerical Examples → §3.9 Behavioral Verification and
   Calibration → §3.10 Academic References → §3.11 Design Provenance
   and Versioning. For embedded-form agents in
   `simulation-bases.md §4.{N}`, the header levels follow
   `02-root-documents-spec.md §4.0` (offset by one). Move
   out-of-order sections; add missing sub-sections using material
   already present in the file. Never fabricate.
2. **Re-run AGENT_POOL three-stage match.** Even if the agent was
   originally reused from the pool, the pool may have been updated
   since, or a new archetype may now cover this agent. Run
   `06-step2-agent-design.md §2.2.0` in full:
   - Stage 1 — filename scan against
     `examples/AGENT_POOL/{Domain}/*.md`.
   - Stage 2 — 7-row Summary fingerprint (≥5/7 match, or ≥3/7 with
     Theory Family match, → escalate to Stage 3).
   - Stage 3 — full-text inspection.
   - Outcome ∈ {reuse, reuse+override, fork, new, **outcome-shrink
     new→reuse**}. The outcome-shrink case fires when an agent that
     was originally created as `new` (or `fork`) is now covered by a
     newer pool archetype — this is a substantive change to the
     agent's provenance and MUST be surfaced to the user. Halt via
     `AskUserQuestion` with three options:
     - **Adopt the pool archetype (reuse).** Rewrite the `§4.{N}`
       block to reference the pool file; keep any scenario-specific
       parameter overrides in the embedded block; log the shrink in
       §3.11 Provenance.
     - **Keep the current fork.** Add a §3.11 Provenance note
       explaining why the pool archetype was rejected.
     - **Push through define skill revise mode.** If the agent's
       identity itself needs to change (e.g., role rename), invoke
       the define skill in revise mode to update target §7.
   - On `new` or `fork`, write the resulting agent spec back into the
     pool as a reusable archetype (this is the only pool write allowed
     at Step 2 during a polish run, and it is only performed after
     three consecutive Handbook §6 PASS runs on the polished agent).
3. **Update §3.11 Design Provenance.** Rewrite this section to record
   the current polish run:

   ```markdown
   ## §3.11 Design Provenance (or ###### §3.11, per embedded-form level)
   - Origin: <fork-from-pool / new / reuse / outcome-shrink new→reuse>
   - Parent (if fork or shrink): `examples/AGENT_POOL/{Domain}/<parent>.md`
   - Polish audit: YYYY-MM-DD against `agent-design-skill.md`.
     Structural changes in this pass:
     - <bullet per structural change; "no structural change" if none>
   - Pool reference: `examples/AGENT_POOL/{Domain}/<file>.md`
     (three-stage match outcome: <reuse / reuse+override / fork / new /
     shrink>)
   ```

4. **Handbook §6 three-PASS.** Dispatch to
   `agent-design-skill.md §6 Validation Checklist` and run three
   consecutive times against the polished agent. Any FAIL resets the
   count. Only after three consecutive PASS runs is the agent
   accepted.

Commit at end of each agent audit:
`polish({ScenarioName}): step2 agent audit — <role-name>`.

**Part B — Environment and structure audit.**

The from-scratch pipeline's Step 2 also produces the environment
design, agent-diversity verification, and communication/round
structure sections of `simulation-bases.md`. A polish run audits these
in place:

1. **`simulation-bases.md §3` Environment Design.** Confirm every
   subsection required by `02-root-documents-spec.md §3` exists and
   maps to target §8 Environment Specification. For scenarios whose
   domain has an instantiation appendix (e.g., a finance-instantiation
   appendix defining an interaction/pricing formula), confirm the
   appendix's required subsections are present. Missing subsections
   are structural defects; missing content that requires new
   substantive claims is halted via `AskUserQuestion` and pushed
   through define skill revise mode.
2. **`simulation-bases.md §5` Agent Diversity Verification.** Confirm
   every dimension listed in target §7 (Time Horizon, Risk Tolerance,
   Information Asymmetry, Determinism, and any domain-specific
   dimensions from the Domain Palette Appendix) is covered by the
   diversity table. Missing rows are added by pulling from the per-
   agent §3.2 Summary rows.
3. **`simulation-bases.md §7` Communication and Round Structure.**
   Confirm the round structure declared here matches target §8's
   temporal/interaction protocol. Structural gaps (missing round
   phases, missing broadcast rules) are patched in place; substantive
   changes to the round protocol go through define skill revise mode.

Run Part B's three checks three consecutive times as a group. Any
FAIL resets the count.

### 6.4 Artefacts Changed

- Every `§4.{N}` block in `simulation-bases.md` (the sole in-scenario
  agent surface).
- `simulation-bases.md §3` Environment Design (structural fills).
- `simulation-bases.md §5` Diversity Verification (missing rows added).
- `simulation-bases.md §7` Communication and Round Structure
  (structural fills).
- Every affected pool file under `examples/AGENT_POOL/{Domain}/` that
  a `§4.{N}` block references (reuse / reuse-with-override / fork /
  outcome-shrink).

### 6.5 Exit Conditions

- Every agent spec follows the canonical §3.1 — §3.11 order.
- Every agent spec has an up-to-date §3.11 Provenance recording this
  polish run.
- Every agent has three consecutive PASS runs of Handbook §6.
- Root doc §3, §5, §7 audits have three consecutive PASS runs.
- The AGENT_POOL now contains a canonical entry for every agent used
  in this scenario (unless outcome was `reuse` or the user selected
  "keep current fork" on an outcome-shrink halt, in which case the
  existing entry stands unchanged).

---

## 7. Step 3 — Config Audit

### 7.1 Reference Contract

Anchor:
`masim/skills/implement-simulation-skill/07-step3-config.md` →
`## Contract (Inputs / Outputs / Polish Hooks)`.

### 7.2 Entry Conditions

- Step 2 exit conditions hold.
- The set of built variants (from Preflight §3.2) is known.

### 7.3 Procedure

For each built variant `{V}`, run the four Polish Hooks declared in
the Step 3 Contract:

1. **YAML parse.** Every YAML file under
   `configs/{ScenarioName}/{V}/` MUST parse cleanly:
   ```
   python -c "import yaml, sys; [yaml.safe_load(open(p)) for p in sys.argv[1:]]" \
     configs/{ScenarioName}/{V}/*.yml
   ```
2. **`# Source:` traceability.** Every `extras.*` key in
   `players.yml` MUST have a `# Source:` comment traceable to one of
   `target §9`, `simulation-bases.md §4.{N}.7`, or
   `simulation-bases.md §6`. Add missing comments; do NOT change
   values.
3. **Target-§9 authority.** No default value in any config may
   disagree with target §9. If a config diverges (typically because
   the config was calibrated during the original build and target §9
   was later revised, or vice versa), halt via `AskUserQuestion` with
   three options:
   - Update the config to match target §9 (target is authoritative).
   - **Push through define skill revise mode** to update target §9
     itself (halts polish; upstream user fixes target via revise mode;
     polish resumes at Step 0 Case A with three-PASS reset).
   - Record the divergence in target §0 Meta CHANGELOG as an
     intentional override (with rationale) and add a matching
     `# Override:` comment in the config.
4. **Variant-folder presence.** Every variant marked `Yes` in target
   §10.1 MUST have all required YAML files as declared in
   `07-step3-config.md`. The concrete file list is variant-scheme
   dependent (for example, `simulation.yml` + `players.yml` +
   `topology.yml` are always required; a `persona.yml` is required for
   any variant whose implementation includes an LLM component; any
   RAG-flavoured variant additionally requires the RAG-specific
   extras). Every variant marked `No` MUST NOT have a config folder.
   Missing folders → halt (there is code without config, or config
   without code, either way the scenario is inconsistent). Extra
   folders → the user must delete them via a separate commit (this
   pipeline does not delete config folders on its own; deletion is
   discussed with the user via `AskUserQuestion`).

Run the four Polish Hooks three consecutive times per variant. Any
FAIL resets that variant's count.

### 7.4 Artefacts Changed

- `configs/{ScenarioName}/{V}/*.yml` — `# Source:` comments added,
  values realigned only when the user selected option 1 in Hook 3.

Commit at end of step:
`polish({ScenarioName}): step3 config audit — variants {list}`.

### 7.5 Exit Conditions

- All four Step 3 Polish Hooks have three consecutive PASS runs for
  every built variant.
- Every YAML parses.
- Every `# Source:` comment resolves to an upstream anchor.

---

## 8. Step 4 — Implementation Audit

### 8.1 Reference Contract

Anchor:
`masim/skills/implement-simulation-skill/08-step4-implement.md` →
`## Contract (Inputs / Outputs / Polish Hooks)`. Also references:
- `implement-simulation-skill/03-variant-documents-spec.md` for
  `explain.md` and `analysis.md` structure.
- `implement-simulation-skill/00-overview.md § Key Design Principles`
  for the "no-defaults, no-defensive-programming" policy.

Terminology note: "the variant's agent-implementation module" refers
to the Python file that defines the variant's agent classes. Its
canonical filename is `players.py` under
`01-mandatory-structure.md`; the polish pipeline enforces that
convention structurally (via the mandatory-structure spec), but the
audit hooks themselves reference the module by role, not by name.

### 8.2 Entry Conditions

- Step 3 exit conditions hold.

### 8.3 Procedure

For each built variant `{V}`, run the eight Polish Hooks declared in
the Step 4 Contract:

1. **No-defaults rule.** Grep every Python file under
   `examples/{ScenarioName}/{V}/`:
   - `extras.get(` — MUST NOT appear with a second argument. Convert
     `extras.get("k", d)` to `extras["k"]` and add the fail-fast
     comment declared in `00-overview.md § Key Design Principles`.
   - `decision.get("action"` — MUST NOT appear with a fallback.
     Convert to `decision["action"]`; the parser (in the variant's
     `prompts.py`, if it has one) is responsible for raising on
     missing fields, per `08-step4-implement.md §4.2.3`.
   - `if X else fallback` for required fields — same treatment.
   Legitimate exceptions (numerically defensible defaults on optional
   metric-plot arguments, RAG config resolution, `__getstate__` /
   `__setstate__` serialization, truly optional config sections, and
   matplotlib styling) MUST be listed in
   `00-overview.md § Key Design Principles`. If a case is not
   explicitly listed, treat it as a violation.
2. **`py_compile` clean.** Run
   `python -m py_compile examples/{ScenarioName}/{V}/*.py` for every
   built variant. Any SyntaxError is a defect; fix in place.
3. **Import smoke.** After `py_compile` clean, run a scenario-local
   import:
   ```
   python -c "import examples.{ScenarioName}.{V}.players"
   ```
   Any `ImportError` (missing framework symbol, stale relative
   import, mis-cased module name) is a defect that `py_compile` alone
   would miss. Fix in place.
4. **LLM-flavoured variants — decision field access rule (§4.2.3).**
   For every variant whose implementation depends on parsing
   `<decision>` blocks from an LLM (any variant whose config has a
   `persona.yml` or an equivalent LLM-role hook), confirm the parser
   follows `08-step4-implement.md §4.2.3` verbatim: fields extracted
   from the `<decision>` block MUST be accessed by index, not
   `.get(...)`, and a missing field MUST raise. Rewrite offending
   accessors.
5. **Dual-section prompt invariant (RuleLLM-flavoured variants).**
   For every variant whose implementation embeds Rule-variant
   quantitative rules into an LLM system prompt (typically named
   `RuleLLM` or a scenario-specific hybrid), confirm every system
   prompt in the variant's `prompts.py` contains both `== PERSONA ==`
   and `== DECISION RULES ==` labeled sections, per
   `01-mandatory-structure.md §5 RuleLLM Variant`. Missing sections
   are a defect; if only the section labels are missing but the
   content is present, patch structurally. If the rule content itself
   is missing, halt via `AskUserQuestion` — the rules must come from
   the Rule variant's implementation, and the user confirms the port.
6. **`explain.md §2` bidirectional completeness.**
   - Forward: for every `§4.{N}` block in `simulation-bases.md`,
     `explain.md §2` MUST contain a matching Theory → Implementation
     Mapping row.
   - Reverse: every row in `explain.md §2` MUST correspond to some
     `§4.{N}` block. Stray rows are a defect (either the Theory row
     is stale after an agent was removed, or the row references a
     class that no longer exists).
   Missing rows are added by pulling the class name from the
   agent-implementation module and the mechanism cite from
   `simulation-bases.md §4.{N}.4`. Never fabricate mappings.
7. **`analysis.md §2` bidirectional completeness.**
   - Forward: for every metric declared in `analysis-bases.md §2`,
     `analysis.md §2` MUST have an implementation row that names the
     function in the variant's analysis module.
   - Reverse: every row in `analysis.md §2` MUST correspond to some
     metric in `analysis-bases.md §2`.
   Missing rows are added the same way; stray rows are removed.
8. **RAG-flavoured variants — `_RAG_FALLBACK` present AND used.** For
   every variant whose implementation includes a retrieval step
   (typically named `Rag` or a scenario-specific RAG hybrid), confirm:
   - The `_RAG_FALLBACK` constant is present in the variant's
     agent-implementation module and matches the shape declared in
     `08-step4-implement.md §4.4.3`.
   - The constant is actually referenced somewhere in the retrieval
     path (a defined-but-unused fallback is worse than none — it lies
     to the reader).
   This hook is skipped for scenarios whose target §10.1 declares no
   retrieval-flavoured variant.

Run the eight Polish Hooks three consecutive times per variant. Any
FAIL resets that variant's count.

### 8.4 Artefacts Changed

- `examples/{ScenarioName}/{V}/players.py` — `.get(...)` → `[...]`
  conversions, comments added.
- `examples/{ScenarioName}/{V}/analysis.py` — same, plus function
  additions if a metric was missing.
- `examples/{ScenarioName}/{V}/prompts.py` — parser fixes for §4.2.3
  compliance; dual-section labels restored where missing.
- `examples/{ScenarioName}/{V}/explain.md` — §2 bidirectional
  completeness fills / removals.
- `examples/{ScenarioName}/{V}/analysis.md` — §2 bidirectional
  completeness fills / removals.

Commit at end of step (per variant):
`polish({ScenarioName}): step4 implementation audit — {V}`.

### 8.5 Exit Conditions

- All eight Step 4 Polish Hooks have three consecutive PASS runs for
  every built variant.
- No `.get(key, default)` pattern remains for required data anywhere
  under `examples/{ScenarioName}/`.
- Every built variant compiles cleanly and imports cleanly.
- Every built variant's `explain.md §2` and `analysis.md §2` are
  bidirectionally complete.

---

## 9. Steps 5 — 10 — Scenario-Level Review and Smoke

### 9.1 Reference Contract

Anchor:
`masim/skills/implement-simulation-skill/09-step5-to-10-review.md` →
`## Contract (Inputs / Outputs / Polish Hooks)`.

### 9.2 Entry Conditions

- Step 4 exit conditions hold.
- Every built variant compiles cleanly and imports cleanly.

### 9.3 Procedure

The Step 5 — 10 Contract's Polish Hooks specify **three consecutive
review passes with different perspectives**, followed by a smoke run
of every built variant.

**Three-pass review.**

| Pass | Perspective                            | Anchors in `09-step5-to-10-review.md`                       |
|------|----------------------------------------|-------------------------------------------------------------|
| 1    | Theory–code alignment                   | §5.1 Theory-Code Alignment; §5.2 Prompt Fidelity; §5.3 Configuration Validation; §5.4 Diversity |
| 2    | Code quality + analysis tools           | §6.1 Required Documentation; §6.2 Correctness; §6.3 Style; §7.1 Baseline-variant analysis-module Requirements |
| 3    | Documentation + final cross-check       | §8 Create Documentation; §9 Execute and Debug (dry-run only) |

Any unchecked item in any pass resets the count for that pass. All
three passes MUST reach three consecutive PASSes; failure to reach
three PASSes on any pass is a defect that MUST be repaired before the
smoke run.

**Smoke run.** For each variant `{V}` marked `Yes` in target §10.1,
run:

```
python -m masim.run --config configs/{ScenarioName}/{V}/simulation.yml \
                    --steps 5 --dry-run
```

All variants MUST complete without uncaught exceptions. Also
re-execute `09-step5-to-10-review.md §10.1 Complete Completion
Checklist` as a whole, at the scenario level, three consecutive
times.

### 9.4 Artefacts Changed

- Any file whose review-pass finding forced a small patch
  (analysis-module metric fix, `explain.md` typo, etc.). Substantive
  changes should have been caught earlier — if a Step 5 — 10 review
  surfaces a substantive issue, halt and cycle back to the earliest
  step whose Contract owns that issue.

Commit at end of step:
`polish({ScenarioName}): steps 5-10 scenario-level review + smoke`.

### 9.5 Exit Conditions

- All three review passes have three consecutive PASS runs.
- Smoke run of every built variant completes without exceptions.
- `10.1 Complete Completion Checklist` has three consecutive PASSes
  at the scenario level.

---

## 10. Closeout

### 10.1 Traceability Matrix

Before Status transition, confirm every downstream artefact traces to
a section of the target file. This matrix is the polish-run
equivalent of `create-simulation-pipeline.md §10`, with the
build-log column absent (a polish run has no build log). A polish
run MUST NOT close if any row cannot be resolved.

| Downstream artefact                                                 | Upstream anchor in target file                     |
|---------------------------------------------------------------------|----------------------------------------------------|
| `simulation-bases.md §1` Phenomenon Definition                      | target §2 + §6                                     |
| `simulation-bases.md §2` Theoretical Foundation                     | target §4                                          |
| `simulation-bases.md §3` Environment Design                         | target §5 + §8                                     |
| `simulation-bases.md §4.{N}` Agent blocks                           | target §7 row + target §4 for each theory          |
| `simulation-bases.md §5` Diversity Verification                     | target §7 (roster diversity)                       |
| `simulation-bases.md §6` Parameter Table                            | target §9                                          |
| `simulation-bases.md §7` Communication and Round Structure          | target §8                                          |
| `simulation-bases.md §8` Historical / Empirical Case Studies        | target §6                                          |
| `analysis-bases.md §1` Analysis Objectives                          | target §3                                          |
| `analysis-bases.md §2` Core Metrics Catalogue                       | target §10.2                                       |
| `analysis-bases.md §6` Expected Results                             | target §5 + §6 + §10.2                             |
| `configs/{ScenarioName}/{V}/players.yml` extras                     | target §9 (via `# Source:` comments)               |
| Variant `{V}`'s agent-implementation module classes                 | `simulation-bases.md §4.{N}` (via `explain.md §2`) |
| Variant `{V}`'s analysis module functions                           | `analysis-bases.md §2` (via `analysis.md §2`)      |
| `examples/AGENT_POOL/{Domain}/<file>.md` (touched)                  | target §7 row + agent §3.11 Provenance             |
| Variant subdirectories present                                      | target §10.1                                       |

Any unanchored downstream artefact is a defect and MUST be repaired
before Status transition (or halted via `AskUserQuestion` if it
requires substantive input, in which case the fix is pushed through
define skill revise mode).

### 10.2 Meta CHANGELOG Summary Line

Append a summary line to target §0 Meta CHANGELOG covering the whole
polish run:

```
YYYY-MM-DD  Polish run against skill baseline (define/agent-design/implement).
             - Step 0 (target-file gate): <case A|B, existing|reverse-seeded>
             - Step 1 (research audit):   <one-line summary>
             - Step 2 (agent + env):      <count agents polished, pool writes,
                                            root doc §3/§5/§7 patches>
             - Step 3 (config audit):     <variants polished>
             - Step 4 (impl audit):       <variants polished>
             - Steps 5-10 (review+smoke): <all-green | notes>
```

### 10.3 Legacy Build-Log Supersession

If a `simulation-build-log.md` file exists in the scenario folder from
a previous from-scratch build, append one line to its §D Phase Log:

```
YYYY-MM-DD  Superseded by polish audit; polish trail lives in target
            §0 CHANGELOG + git history. This build-log is retained for
            historical reference only and is not maintained by the
            polish pipeline.
```

Do NOT delete the build-log. Do NOT edit any section of the build-log
other than appending this single line to §D.

### 10.4 Status Transition

Update target §1 `Status` from `locked` to `released`. This is the
only Step-10-time edit to the target file. `simulation-build-log.md`
is NOT written afresh (it does not exist in a polish run's authored
outputs).

### 10.5 Final Commit

Commit:
`polish({ScenarioName}): closeout — status released, changelog updated`.

### 10.6 Exit Conditions and Closeout

- Traceability matrix fully resolved.
- Target §0 Meta CHANGELOG summary line present.
- Target §1 Status: `released`.
- Legacy build-log (if any) has a supersession line in §D.
- Every step (Preflight → Step 0 → Step 1 → Step 2 → Step 3 → Step 4
  → Steps 5 — 10 → Closeout) has at least one corresponding git
  commit whose message clearly identifies the step and scope.

---

## 11. Halt Protocol

A polish run MUST halt (rather than silently patch or fabricate) when
any of the following occurs:

- A DOI / URL is dead **and** no equivalent primary source is
  verifiable.
- A target section required by the current spec is missing **and**
  no upstream source in the existing artefacts covers it (Step 0
  Case B, mapping table §4.3).
- A config default disagrees with target §9 **and** the user has
  not yet chosen resolution option 1 / 2 / 3 in Step 3 Hook 3.
- An agent's Handbook §6 Validation Checklist has three consecutive
  FAILs (no green PASS achievable within the polish scope).
- An AGENT_POOL outcome-shrink new→reuse is detected (Step 2 Hook 2)
  and the user has not yet chosen adopt / keep-fork / revise-mode.
- A pre-consistency check (Step 0 Case B) fails — some `§4.{N}` block
  has no matching implementation class, or vice versa.
- A dual-section prompt invariant (Step 4 Hook 5) or `_RAG_FALLBACK`
  invariant (Step 4 Hook 8) fails and the fix requires content that
  is not present in existing artefacts.
- A smoke-run variant crashes with an uncaught exception that traces
  back to a substantive gap (missing metric, missing prompt field,
  etc.) rather than a local coding fix.

**On halt.** Use `AskUserQuestion` with at most four options (respect
the hard limit; split into multiple questions if more choices are
needed). One option MUST always be "**Re-invoke
`define-simulation-scenario-skill.md` in §9.3 revise mode**" whenever
the halt is a substantive gap in the target file itself. Never
proceed silently. Never fabricate.

**Recovery path after revise-mode invocation.** The polish run pauses
at the halted step. The user invokes the define skill in revise mode,
which produces the corrected target file (with a new §0 Meta
CHANGELOG line recorded by the define skill). Once the define skill
returns, the polish run resumes at the halted step with the
three-PASS count reset to zero. No steps already completed are
re-run.

---

## 12. Tooling and Interaction Rules

- **AskUserQuestion**: max four options per question. Use only for
  defect clarification, for Step 0 Case B branching, and whenever
  Halt Protocol §11 fires. Same discipline as
  `create-simulation-pipeline.md §11`. Whenever a halt is a
  substantive gap in the target file, one option MUST be
  "re-invoke define skill in revise mode".
- **TodoWrite**: maintain a nine-item todo list mirroring
  Preflight → Step 0 → Step 1 → Step 2 → Step 3 → Step 4 →
  Steps 5 — 10 → Closeout → Traceability Matrix. Update on step
  boundaries; do not micro-track inside a step.
- **Git discipline**: one commit per completed step (Step 2 may
  produce one commit per audited agent; Step 4 may produce one commit
  per audited variant). Commit messages MUST identify the step and
  the artefact scope. This git history is the polish run's primary
  audit trail (no build log is written).
- **Workspace throwaway**: the Preflight inventory lives in the
  runtime workspace directory (see the runtime environment for the
  concrete path) and MUST NOT be committed to the repository.
- **Contract-block edits**: if audit uncovers a gap in one of the
  Contract blocks (a step's Inputs / Outputs / Polish Hooks are
  incomplete or ambiguous), the pipeline MAY non-destructively edit
  the Contract block *of that step file only*. Substantive rewrites
  of adjacent prose are out of scope. Contract-block edits count as
  skill-file changes and are committed under
  `polish(skills): step <N> contract clarification`.
- **Target-file edits**: the polish pipeline MUST NOT hand-edit the
  target file except for (a) appending to §0 Meta CHANGELOG, (b) the
  single Status transitions at Step 0 (`draft → locked`) and Closeout
  (`locked → released`), and (c) Case B seed writes handed off to
  the define skill's revise mode. All other target-file changes go
  through the define skill.

---

## 13. Pipeline Entry Checklist (Pre-Run)

Run this checklist once before invoking Preflight:

- [ ] The scenario `examples/{ScenarioName}/` exists and contains at
      least one downstream artefact (`simulation-bases.md`,
      `analysis-bases.md`, or a variant subdirectory declared in
      target §10.1).
- [ ] Repository is clean (`git status` shows no unrelated diffs).
- [ ] The reader has read the `## Contract` block of every step file
      listed in §14 (this is the audit-facing surface — read it
      first).
- [ ] The AGENT_POOL folder for the scenario's domain
      (`examples/AGENT_POOL/{Domain}/`) exists and is up to date.
- [ ] The reader has read this file (`polish-simulation-pipeline.md`)
      end-to-end at least once.
- [ ] The reader is aware that this pipeline **does not** produce a
      `simulation-build-log.md`; audit trail is CHANGELOG + §3.11
      Provenance + git history.
- [ ] The reader is aware that all substantive target-file changes go
      through `define-simulation-scenario-skill.md §9.3 revise mode`,
      never through direct hand-editing of the target file.

If any item is unchecked, fix it before starting Preflight.

---

## 14. Skill References (Quick Index)

| Topic                                                | File                                                                        |
|------------------------------------------------------|-----------------------------------------------------------------------------|
| Scenario target-file spec (§11 checklist, §9.3 revise mode) | `masim/skills/define-simulation-scenario-skill.md`                     |
| Universal Agent Design Handbook (§3, §6)             | `masim/skills/agent-design-skill.md`                                        |
| From-scratch pipeline (contrast)                     | `masim/skills/create-simulation-pipeline.md`                                |
| Methodology overview                                 | `masim/skills/implement-simulation-skill/00-overview.md`                    |
| Directory layout                                     | `masim/skills/implement-simulation-skill/01-mandatory-structure.md`         |
| Root document specs (bases.md files)                 | `masim/skills/implement-simulation-skill/02-root-documents-spec.md`         |
| Variant document specs                               | `masim/skills/implement-simulation-skill/03-variant-documents-spec.md`      |
| Step 0 (Load target)  — Contract                     | `masim/skills/implement-simulation-skill/04-step0-load-target.md`           |
| Step 1 (Research)     — Contract                     | `masim/skills/implement-simulation-skill/05-step1-research.md`              |
| Step 2 (Agent + env design + Pool gate) — Contract   | `masim/skills/implement-simulation-skill/06-step2-agent-design.md`          |
| Step 3 (Config)       — Contract                     | `masim/skills/implement-simulation-skill/07-step3-config.md`                |
| Step 4 (Implement)    — Contract                     | `masim/skills/implement-simulation-skill/08-step4-implement.md`             |
| Steps 5 — 10 (Validate, review, run) — Contract      | `masim/skills/implement-simulation-skill/09-step5-to-10-review.md`          |
| AssetBubble reference implementation (finance domain)| `masim/skills/implement-simulation-skill/15-reference-assetbubble.md`       |
| AGENT_POOL directory                                 | `examples/AGENT_POOL/`                                                      |
| Project structure overview                           | `docs/structure.md`                                                         |

---

## 15. Status

`Status: canonical`. This file supersedes the legacy Phase A — Phase G
polish structure. Any legacy scenario polished under the old phases
remains valid; new polish runs MUST use the Preflight → Step 0 — 10 →
Closeout structure documented here.
