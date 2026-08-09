---
name: polish-simulation-pipeline
purpose: Top-level pipeline for **auditing and standardising an existing MASim simulation scenario** (already present under `examples/{ScenarioName}/`) so that every artefact conforms to the current versions of the reusable, domain-neutral skill suite (`define-simulation-scenario-skill.md`, `agent-design-skill.md`, `implement-simulation-skill/`). This pipeline follows the same Step 0 — Step 10 spine as `create-simulation-pipeline.md`, but at every step the action is **audit + patch**, not "produce from scratch". Each step in this pipeline anchors to the corresponding step file's `## Contract (Inputs / Outputs / Polish Hooks)` block; the actual audit work is dispatched to `agent-design-skill.md` and to the individual `implement-simulation-skill/{04..09}-*.md` files. When an audit uncovers a defect, the pipeline patches locally and re-runs the step's Polish Hooks three consecutive times.
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
  `tmpl/polish-log.md` as an accepted gap.

A polish run MUST NOT silently invent missing evidence and MUST NOT
fabricate citations, DOIs, parameter values, or theoretical
mechanisms. A polish run MUST NOT hand-edit the target file except
for the single Status transition performed at Step 0 and Closeout.
All other target-file changes go through the define skill's revise mode.

| Concern                                | Owner                                                                                                                                                                                                                                                                                                                  |
|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Target-file specification we align to  | `masim/skills/define-simulation-scenario-skill.md` (§11 checklist, §9.3 revise mode)                                                                                                                                                                                                                                   |
| Universal Agent Design Handbook        | `masim/skills/agent-design-skill.md` (§3 canonical order, §6 checklist)                                                                                                                                                                                                                                                |
| Per-step audit contract                | `masim/skills/implement-simulation-skill/{04..09}-*.md` `## Contract`                                                                                                                                                                                                                                                  |
| Root document conformance              | `implement-simulation-skill/02-root-documents-spec.md`                                                                                                                                                                                                                                                                 |
| Variant document conformance           | `implement-simulation-skill/03-variant-documents-spec.md`                                                                                                                                                                                                                                                              |
| Directory / file layout                | `implement-simulation-skill/01-mandatory-structure.md`                                                                                                                                                                                                                                                                 |
| AGENT_POOL three-stage match protocol  | `implement-simulation-skill/06-step2-agent-design.md §2.2.0`                                                                                                                                                                                                                                                           |
| AGENT_POOL icon generation protocol    | `masim/skills/agent-icon-generation-skill.md`                                                                                                                                                                                                                                                                          |
| Market Coordinator Design Handbook     | `masim/skills/market-design-skill.md` (§2 Market Type taxonomy, §3 canonical section order, §6 Validation Checklist)                                                                                                                                                                                                   |
| Market coordinator icon generation     | `masim/skills/market-icon-generation-skill.md`                                                                                                                                                                                                                                                                         |
| Market coordinator pool match protocol | `masim/agents/defines/market/` — three-stage match analogous to participant-agent gate, driven by `simulation-bases.md §3` coordinator identity                                                                                                                                                                         |
| Agent handbook structural audit        | Manual review against `06-step2-agent-design.md` Hook 5a — walk every AGENT_POOL profile and confirm no `TODO / TBD / FIXME / XXX / PLACEHOLDER / Status: stub / auto-generated placeholder / fill this section / insert here` marker exists outside fenced code blocks; any such marker is a hard FAIL |
| Agent naming / parity / coverage audit | Manual review against Hooks 4, 6, 7 — cross-check every scenario's `players.py` roster, `simulation-bases.md §3` anchor, and per-config roster in `configs/{Scenario}/{Variant}/simulation.yml` for parity |
| Three-PASS validation discipline       | This file §3 and `agent-design-skill.md §6`                                                                                                                                                                                                                                                                            |
| From-scratch pipeline (contrast)       | `masim/skills/create-simulation-pipeline.md`                                                                                                                                                                                                                                                                           |

### 0.1 Anchor Precedence (polish flow)

For any conformance question during a polish run (agent naming, archetype identity, roster completeness, parameter provenance, theory citation), the authoritative source order is fixed. When two sources disagree, the higher-numbered rule loses and MUST be patched through the mechanism named in the winner's row.

| Rank | Authoritative source                                                 | What it authorises                                                                                                                                                       | On disagreement                                                                                                                               |
|------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | `examples/{Scenario}/simulation-bases.md §4.N` block headers         | Theoretical archetype names (kebab-normalized). Persona-only relabellings (e.g. `GreaterFoolSpeculator` for a `MomentumSpeculator` archetype) are NOT alternative names. | Winner. Never override during polish. Substantive changes to §4 archetype names go through the define skill's §9.3 revise mode.               |
| 2    | Target file §7 Agent Roster rows                                     | Deliverable roster — one row per §4.N block, using the same kebab-normalized name.                                                                                       | Loses to rank 1. During polish, §7 rows that disagree with §4 headers are patched via `define-simulation-scenario-skill.md §9.3 revise mode`. |
| 3    | Implementation (`configs/{Scenario}/{V}/players.yml` + `players.py`) | Every top-level identity MUST satisfy `_canonical_archetype(identity)` ∈ { kebab-normalized §4.N header }.                                                               | Loses to ranks 1 and 2. Identity/class renames are the standard fix. See `06-step2-agent-design.md` Hook 6a.                                  |

**Why this hierarchy exists.** In a `create-simulation-pipeline.md` run the target file is drafted first and seeds `simulation-bases.md §4`; the arrow points target → bases. In a `polish-simulation-pipeline.md` run the scenario already has a populated `simulation-bases.md §4` (with theory blocks, citations, formulas, empirical evidence). §4 is where a scenario's archetype identity actually lives; §7 is a derived summary. A polish run therefore inverts the create-flow seed arrow: bases §4 → target §7 → implementation. Steps that ambiguously reference "target §7 seeds §4" language inherited from the create pipeline MUST be read under this rank order in polish mode.

**Halt path when rank-1 and rank-2 conflict.** If a polish audit finds `simulation-bases.md §4.N` header names disagree with target §7 rows, halt via `AskUserQuestion` with two canonical options: (i) patch target §7 via revise mode to match §4 (default — no theory change); (ii) patch §4 via revise mode to match §7 (requires new theory citations and evidence update, since §4.N block bodies must remain internally consistent with their header). Option (ii) is a substantive change and MUST NOT be silently applied by the polish run.

**Halt path when rank-2 and rank-3 conflict.** If implementation identities disagree with target §7 (and by transitivity with §4), the polish run renames identities/classes in-place to match §4. This is the standard Hook 6a fix and does not require revise mode.

---

## 1. Design Philosophy

Seven commitments shape every step of a polish run. Four are inherited
from `create-simulation-pipeline.md §1` (they apply equally to
upgrades); three are polish-specific.

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
   distributed across two places, in priority order:
   - **Local log (`tmpl/polish-log.md`)** — one entry per completed
     step. This local file is the polish run's primary process log.
     It is never committed to version control.
   - **Per-agent §3.11 Design Provenance** — updated in place to
     record that this agent's specification was audited on this date
     against the handbook, and to list any structural changes.

   The target file itself MUST NOT contain any changelog, audit trail,
   or §0 section (see `define-simulation-scenario-skill.md` §3).

   **No git commits.** The polish pipeline MUST NOT execute any `git
   commit` commands. All changes remain local (unstaged). The user
   decides when and how to commit after the run completes.

   If a legacy `simulation-build-log.md` exists in the scenario folder
   from a previous from-scratch build, it is NOT deleted. Instead, on
   Closeout the pipeline appends a single line to its §D Phase Log:
   `YYYY-MM-DD  Superseded by polish audit; polish trail lives in
   tmpl/polish-log.md.` This preserves the historical record without letting
   the build-log drift into a stale live document.

7. **Variant-scoped polish still runs scenario gates.** If the user
   asks to polish a single variant folder such as
   `examples/{Scenario}/LLM/`, the run is still a scenario polish with
   a narrowed downstream surface. It MUST execute Preflight, Step 0,
   Step 1, and Step 2 before any variant-local Step 3 or Step 4 work.
   In particular, Step 2 MUST run the AGENT_POOL match and
   icon-resolution gate for every agent identity used by the selected
   variant. A variant-local request must not be treated as permission
   to skip scenario-level agent/profile/icon assets unless the user
   explicitly says "code-only" or "skip scenario-level assets"; that
   skip is then recorded as an accepted gap, not as a PASS.

---

## 2. Pipeline Overview

The polish run has one preflight, seven audit steps, and one
closeout. Each step maps 1-to-1 to a file in
`implement-simulation-skill/` (with Step 0 additionally anchoring to
`define-simulation-scenario-skill.md`). The action at every step is
"read Contract, dispatch audit, patch, three-PASS Polish Hooks,
log to tmpl/".

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
    │   Hook 5a: Manual structural gate — walk every AGENT_POOL   │
    │   profile line-by-line and confirm §2 section order, §3     │
    │   section-by-section requirements, §3.6.0 I/O Contract      │
    │   presence, and reject any TODO / TBD / FIXME / XXX /       │
    │   PLACEHOLDER / Status: stub / auto-generated-placeholder / │
    │   fill-this-section / insert-here marker outside a fenced   │
    │   code block. No form of TODO or placeholder content is     │
    │   permitted in a conformant profile.                        │
    │   Hook 5b: agent-design-skill.md §6 three-PASS semantic    │
    │   checklist.                                               │
    │   Hook 6: Manual parity gate — cross-check every scenario's │
    │   `players.py` roster against `simulation-bases.md §3`     │
    │   anchor and per-config roster in                          │
    │   `configs/{Scenario}/{Variant}/simulation.yml`.           │
    │   AGENT_POOL three-stage match rerun (handles reuse/       │
    │   fork/new AND outcome-shrink new→reuse).                  │
    │   Also audits root doc §3 Environment Design, §5 Diversity │
    │   Verification, §7 Communication and Round Structure.      │
    │   Market coordinator audit: masim/agents/defines/market/ three-stage │
    │   match, market-design-skill.md §6 three-PASS, icon gate.  │
    └────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────────┐
    │ Step 3 — Config Audit                                      │
    │   File: 07-step3-config.md ## Contract → Polish Hooks      │
    │   Every YAML parses; # Source: comments trace to target §9 │
    │   / bases §4.{N}.7 / §6; variant folders match target      │
    │   §10.1 exactly (extras and missing both flagged);          │
    │   coordinator archetype: field resolves to masim/agents/defines/      │
    │   market/ profile.                                         │
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
    │ Closeout — Traceability + Status                         │
    │   Every downstream artefact traces to a target §;           │
    │   summary in tmpl/polish-log.md; supersede any legacy build-log; │
    │   Status: locked → released.                              │
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
returns and the target file has been updated, the polish run resumes
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
- Working tree is clean (no unrelated local modifications exist).
- The reader has read this file end-to-end, plus the `## Contract`
  block of every file listed in §14.

### 3.2 Procedure

1. **Inventory.** Enumerate every file under
   `examples/{ScenarioName}/` and every file under
   `configs/{ScenarioName}/`. Classify each against the layout in
   `implement-simulation-skill/01-mandatory-structure.md §1`:

   | Class                   | Meaning                                                                                          |
   |-------------------------|--------------------------------------------------------------------------------------------------|
   | Present, conforming     | File exists at the expected path with the expected name (structure only; content audited later). |
   | Present, non-conforming | File exists but has a stale name, wrong header levels, or missing sections.                      |
   | Missing (required)      | File is missing but the current spec requires it (e.g., the target file itself).                 |
   | Missing (conditional)   | File is missing, but its variant is not marked `Yes` in target §10.1 — no action needed.         |
   | Present, deprecated     | File exists under an old name (e.g., `simulation-define.md`) and must be renamed / merged.       |

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
   - Scope the deficit out of this polish run and record it in
     `tmpl/polish-log.md` as an accepted gap (the scenario stays
     `locked` but marked with the gap).
   - Abort the polish run.
5. After three consecutive PASS runs, ensure the target §1 `Status`
   is `locked` (upgrade `draft → locked` if necessary — this is the
   only edit to the Status field the polish pipeline is authorised
   to make at Step 0).
6. Append a summary of the Step 0 outcome to `tmpl/polish-log.md`.

**Case B — target file absent.**

**Policy (binding — default standard, ratified 2026-07-01).** When the
scenario is missing its target file, the polish pipeline's SOLE
DEFAULT path is to invoke `define-simulation-scenario-skill.md`
end-to-end and produce the target file through that skill. This is
recorded as the standing project standard on the grounds of **rigor
(严谨) and completeness (全面)**: the define skill is the only entry
point that enforces the full validation surface (§1 – §11 with the
three-PASS discipline) that the rest of the polish pipeline anchors
to, so any other path would silently weaken the audit chain that
Steps 1 – 10 depend on. The invoking agent MUST take this path by
default and MUST NOT present reverse-reconstruction as an equal
option in the AskUserQuestion prompt.

Reverse-reconstruction is retained ONLY as an explicit-override
fallback. It is available if and only if the user, on their own
initiative and without prompting, names the reverse-reconstruction
path explicitly and asserts that the original scenario author's
minimal inputs (scenario name, domain, phenomenon sketch, variant
preference, anchor event) cannot be re-elicited. Absent that explicit
override, the invoking agent proceeds directly with the define skill.
Reverse-reconstruction bypasses the define skill's validation surface
and can only ratify what is already in the downstream artefacts, so
it is unsafe as a default.

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
2. **Default action — proceed with the define skill.** Once the
   pre-consistency check is green, the invoking agent proceeds
   directly with `define-simulation-scenario-skill.md` end-to-end.
   No AskUserQuestion prompt is issued to choose between paths — the
   default standard fixes the path in advance. Minimal inputs
   (scenario name, domain, phenomenon sketch, optional variant
   preference, optional fixed anchor event) MAY be collected from the
   user by the define skill itself; the invoking agent MAY pre-fill
   any input that can be inferred unambiguously from the existing
   downstream artefacts (e.g., `Domain` from the folder inventory,
   variant preference from the built-variant list) and confirm those
   inferences with the user at the define skill's C-1 checkpoint.
   Once the define skill returns, resume this step at Case A. This
   option MUST be taken unless the reverse-reconstruction override
   (step 2a) has been explicitly invoked by the user.

2a. **Reverse-reconstruct override (LAST-RESORT FALLBACK — user must
   name the path explicitly).** Available only when the user, without
   being prompted, names the reverse-reconstruction path explicitly
   and asserts that the original scenario author's minimal inputs
   cannot be re-elicited. In that case: seed the target file
   section-by-section from the mapping table below, then re-invoke
   `define-simulation-scenario-skill.md` in §9.3 revise mode to
   validate and lock the reconstructed target. The polish pipeline
   writes the seed but does NOT lock the file itself; locking is
   always performed by the define skill.

3. **Reverse-reconstruction seed mapping** (used only when the user
   selects the reverse-reconstruct option):

   | Target section                    | Source of content in existing scenario                                                                                                                                                 |
   |-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
   | §1 Meta                           | folder name (PascalCase → phrases); `Status: draft`.                                                                                                                                   |
   | §2 Phenomenon Statement           | `simulation-bases.md §1` narrative + `analysis-bases.md §1` framing.                                                                                                                   |
   | §3 Research Goals                 | `analysis-bases.md §1` (hypotheses reverse-mapped to research questions).                                                                                                              |
   | §4 Theoretical Anchors            | Union of every `§4.{N}.4` (`Theoretical Foundation`) block in `simulation-bases.md`; one target §4.{k} per unique theory.                                                              |
   | §5 Stylized Facts                 | `simulation-bases.md §1.1.2 / §1.1.3` (empirical regularities) + `analysis-bases.md §6.1`.                                                                                             |
   | §6 Historical / Empirical Anchors | `simulation-bases.md §1` narrative + `simulation-bases.md §8` case studies.                                                                                                            |
   | §7 Agent Roster                   | One row per `§4.{N}` block in `simulation-bases.md`.                                                                                                                                   |
   | §8 Environment Specification      | `simulation-bases.md §3` Environment Design + any domain-specific §3 subsections.                                                                                                      |
   | §9 Parameter Seeds                | Union of every `Parameters` table across per-agent specs + `configs/{ScenarioName}/*/players.yml` extras + `simulation-bases.md §6`.                                                   |
   | §10.1 Variants to Build           | For each built variant subdirectory that exists in the scenario folder: `Yes`; for every variant subdirectory whose name is on any earlier scenario's roster but is absent here: `No`. |
   | §10.2 Pass / Fail Criteria        | `analysis-bases.md §2` metrics + §6.2 calibration targets.                                                                                                                             |

   Any target section with no upstream source (typically §3 Research
   Goals and §10.2 Pass / Fail Criteria) is left as a placeholder that
   MUST be filled by the user during the subsequent revise-mode
   invocation. NEVER fabricate.

4. **Hand off to define skill in revise mode.** Once the seed is
   written, invoke `define-simulation-scenario-skill.md §9.3 revise
   mode` on the seed. The define skill runs its three checkpoints
   (C-1 / C-2 / C-3), performs §11 three-PASS validation, sets
   `Status: locked`. The polish pipeline does NOT independently run
   §11 in Case B — that is the define skill's authority.
5. Once control returns from the define skill, append a summary of
   the reverse-reconstruction outcome to `tmpl/polish-log.md`.

**Both cases.** No `simulation-build-log.md` is created — the polish
pipeline does not maintain one. If a legacy build-log already exists,
it is preserved for its historical value; the pipeline appends a
supersession line to its §D Phase Log at Closeout (see §10.3).

### 4.4 Artefacts Changed

- `examples/{ScenarioName}/{domain}-{scenario}.md`:
  - §1 Status upgraded to `locked` (Case A) or set to `locked` by the
    define skill (Case B).
  - Structural fixes in place (Case A only). Substantive changes go
    through the define skill in revise mode; the polish pipeline
    itself never edits target-file substance.
  - No changelog or audit trail is written into the target file.

### 4.5 Exit Conditions

- Target file exists at the canonical path.
- §11 has three consecutive PASS runs (either performed here in
  Case A or performed by the define skill in Case B).
- Target §1 Status is `locked`.
- Step 0 outcome is appended to `tmpl/polish-log.md`.
- Pre-consistency check (Case B) passed.

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

Append step summary to `tmpl/polish-log.md`.

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
- `masim/skills/agent-icon-generation-skill.md` (icon generation and
  registration for any AGENT_POOL profile whose icon is missing or broken,
  including new/forked profiles and reused profiles discovered during audit)
- `masim/skills/market-design-skill.md §3` (canonical section order for
  market coordinator profiles, domain-neutral)
- `masim/skills/market-design-skill.md §6` (Validation Checklist for
  market coordinator profiles)
- `masim/skills/market-icon-generation-skill.md` (icon generation and
  registration for any `masim/agents/defines/market/` coordinator profile whose
  icon is missing or broken)

The polish pipeline's role at Step 2 is orchestration and three-PASS
enforcement; the actual per-agent audit logic lives in the handbook
(`agent-design-skill.md` for participant agents,
`market-design-skill.md` for coordinators).

### 6.2 Entry Conditions

- Step 1 exit conditions hold.
- Every agent surface expected by the current spec exists as `§4.{N}`
  blocks in `simulation-bases.md` (the embedded form is the only
  in-scenario agent surface). Any reused pool profile is referenced
  from the `§4.{N}` block via a relative path to
  `masim/agents/defines/{Domain}/<kebab-name>.md`; the pool file is
  audited alongside the embedded block whenever it is referenced.
- For variant-scoped polish requests, build the expected agent identity
  set before Step 2 closes. Sources, in priority order, are the target
  roster, `simulation-bases.md` agent blocks, selected variant config
  files such as `configs/{Scenario}/{Variant}/players.yml`, and the
  selected variant's agent implementation module. For each concrete
  identity, derive the pool stem with `identity.replace("_", "-")`; do
  not derive icon names from the scenario name or from whichever PNG
  files already happen to exist.

### 6.3 Procedure

Step 2 is split into three parts: (A) per-agent audit (dispatched to
`agent-design-skill.md`), (B) environment-and-structure audit (root
doc §3, §5, §7), and (C) market coordinator audit (dispatched to
`market-design-skill.md`).

**Part A — Per-agent audit.**

For **each** agent, in target §7 roster order, do the following:

0. **Icon-completeness preflight.** Cross-check the expected agent
   identity set against `masim/agents/defines/{Domain}/`. For each
   identity, the canonical profile is
   `masim/agents/defines/{Domain}/{identity.replace("_", "-")}.md`
   unless the three-stage match resolves to a different existing pool
   profile. The expected icon is always
   `masim/agents/defines/agent_images/icons/{Domain}-{agent-stem}.png`.
   Missing `.md` profiles, missing `Icon` rows, missing PNGs, stale
   filenames, or missing `agent_images/design.md` rows are Step 2
   failures. Create or repair them through the AGENT_POOL match and
   `agent-icon-generation-skill.md`; do not treat a scenario-level image
   such as `{Domain}-{ScenarioName}.png` as satisfying an agent icon.

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
     `masim/agents/defines/{Domain}/*.md`.
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
     Immediately after the pool file is written, invoke
     `agent-icon-generation-skill.md` to generate and register the
     matching icon. The `new` / `fork` branch is incomplete until the
     icon PNG exists, the pool profile has an `Icon` row, and
     `masim/agents/defines/agent_images/design.md` has the mapping row.
     If image generation is unavailable, halt and return the missing
     icon as a blocking asset task instead of inserting a placeholder.
   - On `reuse` or `reuse+override`, verify the referenced pool profile
     already has a valid `Icon` row, that the linked PNG exists, that
     the PNG filename is `{domain}-{agent-stem}.png`, and that
     `masim/agents/defines/agent_images/design.md` maps the profile to
     that filename. If any of these checks fails, immediately invoke
     `agent-icon-generation-skill.md` as an icon-repair step. The
     reused branch is incomplete until the icon PNG exists, the profile
     has the corrected `Icon` row, and the mapping row records the
     profile-to-icon relationship. If image generation is unavailable,
     halt and return the missing icon as a blocking asset task instead
     of inserting a placeholder.
3. **Update §3.11 Design Provenance.** Rewrite this section to record
   the current polish run:

   ```markdown
   ## §3.11 Design Provenance (or ###### §3.11, per embedded-form level)
   - Origin: <fork-from-pool / new / reuse / outcome-shrink new→reuse>
   - Parent (if fork or shrink): `masim/agents/defines/{Domain}/<parent>.md`
   - Polish audit: YYYY-MM-DD against `agent-design-skill.md`.
     Structural changes in this pass:
     - <bullet per structural change; "no structural change" if none>
   - Pool reference: `masim/agents/defines/{Domain}/<file>.md`
     (three-stage match outcome: <reuse / reuse+override / fork / new /
     shrink>)
   ```

4. **Handbook §6 three-PASS.** Dispatch to
   `agent-design-skill.md §6 Validation Checklist` and run three
   consecutive times against the polished agent. Any FAIL resets the
   count. Only after three consecutive PASS runs is the agent
   accepted.

Append per-agent audit summary to `tmpl/polish-log.md`.

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

**Part C — Market Coordinator Audit.**

Every scenario has at least one coordinator agent (called "Market" in
finance, "OpinionEnvironment" / "InformationEnvironment" in opinion
dynamics, etc.). The coordinator's canonical pool profile lives under
`masim/agents/defines/market/{market-type}-{coordinator-stem}.md`, and
its design specification follows `market-design-skill.md` (the
sibling of `agent-design-skill.md`). A polish run MUST audit the
coordinator with the same rigour applied to participant agents in
Part A. Coordinator audit runs AFTER Part B — it depends on a valid
`simulation-bases.md §3` Environment Design.

0. **Coordinator identity extraction.** Determine the coordinator
   identity and market type from the scenario:
   - Primary source: `simulation-bases.md §3` coordinator class name
     and the mechanism family it declares (e.g., "price-impact",
     "echo-chamber-clustering", "bank-run-diamond-dybvig").
   - Secondary source: `players.yml` `market:` or
     `{variant}_opinion_environment:` / `{variant}_information_environment:`
     block, which MUST contain an `archetype: {stem}` field pointing
     to a pool profile.
   - Derive the expected pool stem: `{market-type}-{coordinator-stem}`
     (all lowercase, kebab-case). The expected pool profile is
     `masim/agents/defines/market/{stem}.md`.

1. **Three-stage masim/agents/defines/market match.** Run a match protocol
   analogous to the participant-agent gate in Part A Hook 2, but
   scoped to `masim/agents/defines/market/`:
   - Stage 1 — filename scan against
     `masim/agents/defines/market/*.md`.
   - Stage 2 — Summary fingerprint comparison (Market Type, Mechanism
     Family, Feedback Direction, State Variables, Broadcast Payload,
     ≥4/6 match → escalate to Stage 3).
   - Stage 3 — full-text inspection of Coordination Framework.
   - Outcome ∈ {reuse, reuse+override, fork, new, outcome-shrink
     new→reuse}. Same halt-and-ask protocol as Part A Hook 2 applies
     when an outcome-shrink is detected.
   - On `new` or `fork`, the resulting coordinator spec is written
     into `masim/agents/defines/market/` AFTER three consecutive PASS
     runs of `market-design-skill.md §6`. Immediately invoke
     `market-icon-generation-skill.md` to generate and register the
     icon at `agent_images/icons/market/{stem}.png`.
   - On `reuse` or `reuse+override`, verify the referenced pool
     profile already has a valid `Icon` row, that the PNG exists at
     `agent_images/icons/market/{stem}.png`, and that
     `agent_images/design.md` maps the profile. If any check fails,
     invoke `market-icon-generation-skill.md` as an icon-repair step.

2. **Section order and completeness (`market-design-skill.md §3`).**
   Dispatch to `market-design-skill.md §3` and confirm the canonical
   order: §3.1 Title → §3.2 Summary → §3.3 Definition and Goals →
   §3.4 Theoretical Foundation → §3.5 Design Purpose and Activation
   Triggers → §3.6 Coordination Framework (I/O Contract, State
   Update Mechanism, Broadcast Space) → §3.7 Environmental
   Parameters → §3.8 Worked Numerical Examples → §3.9 Behavioral
   Verification and Calibration → §3.10 Academic References → §3.11
   Design Provenance. Move out-of-order sections; add missing
   sub-sections using material from `simulation-bases.md §3`. Never
   fabricate.

3. **Consistency: §3 mechanism vs pool profile.** Confirm the
   state-update mechanism (formula, coefficients, feedback direction)
   declared in `simulation-bases.md §3` matches the pool profile's
   §3.6 Coordination Framework. Discrepancies are defects:
   - If the pool profile is authoritative (reuse outcome): patch
     `simulation-bases.md §3` to align.
   - If `simulation-bases.md §3` is authoritative (new/fork outcome):
     patch the pool profile to align.
   - If ambiguous: halt via `AskUserQuestion`.
   Also confirm every Environmental Parameter declared in the pool
   profile's §3.7 has a matching key in
   `configs/{ScenarioName}/{V}/players.yml` `market:` extras (or
   equivalent coordinator block). Missing config keys are defects
   logged for Step 3 to repair.

4. **Update §3.11 Design Provenance.** Rewrite the coordinator
   profile's provenance section to record this polish run:
   ```markdown
   ## §3.11 Design Provenance
   - Origin: <fork-from-pool / new / reuse / outcome-shrink new→reuse>
   - Market Type: <market-type from §2 taxonomy>
   - Parent (if fork or shrink): `masim/agents/defines/market/<parent>.md`
   - Polish audit: YYYY-MM-DD against `market-design-skill.md`.
     Structural changes in this pass:
     - <bullet per structural change; "no structural change" if none>
   ```

5. **`market-design-skill.md §6` three-PASS.** Dispatch to
   `market-design-skill.md §6 Validation Checklist` and run three
   consecutive times against the polished coordinator profile. Any
   FAIL resets the count. Only after three consecutive PASS runs is
   the coordinator accepted.

6. **Icon-completeness gate.** After the coordinator profile passes
   §6 validation, confirm:
   - PNG exists at `agent_images/icons/market/{stem}.png`.
   - Profile has an `Icon` row referencing that path.
   - `agent_images/design.md` has a mapping row for this profile.
   If any check fails and image generation is available, invoke
   `market-icon-generation-skill.md`. If image generation is
   unavailable, halt and return the missing icon as a blocking asset
   task (same protocol as Part A).

Append coordinator audit summary to `tmpl/polish-log.md`.

Run Part C's checks (Hooks 1 through 6) three consecutive times as a
group. Any FAIL resets the count.

### 6.4 Artefacts Changed

- Every `§4.{N}` block in `simulation-bases.md` (the sole in-scenario
  agent surface).
- `simulation-bases.md §3` Environment Design (structural fills).
- `simulation-bases.md §5` Diversity Verification (missing rows added).
- `simulation-bases.md §7` Communication and Round Structure
  (structural fills).
- Every affected pool file under `masim/agents/defines/{Domain}/` that
  a `§4.{N}` block references (reuse / reuse-with-override / fork /
  outcome-shrink).
- Every icon file, profile `Icon` row, and mapping row created or repaired
  by `agent-icon-generation-skill.md` for new/forked pool files and for
  reused pool files whose icon was missing or broken.
- Every affected coordinator pool file under
  `masim/agents/defines/market/` (reuse / reuse+override / fork /
  outcome-shrink) — produced or patched by Part C.
- Every coordinator icon file, profile `Icon` row, and
  `agent_images/design.md` mapping row created or repaired by
  `market-icon-generation-skill.md` for new/forked coordinator profiles
  and for reused coordinator profiles whose icon was missing or broken.
- `simulation-bases.md §3` Environment Design patched to align with
  the authoritative coordinator pool profile (Part C Hook 3).

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
- Every AGENT_POOL entry referenced by this scenario has a valid icon PNG,
  Design Provenance `Icon` row, and `agent_images/design.md` mapping row.
  Missing or broken icons on reused entries have been repaired through
  `agent-icon-generation-skill.md`; unresolved icon gaps are blocking
  asset tasks, never tolerated warnings.
- The scenario's coordinator has a conformant pool profile under
  `masim/agents/defines/market/` with three consecutive PASS runs of
  `market-design-skill.md §6`.
- The coordinator pool profile has an up-to-date §3.11 Provenance
  recording this polish run.
- The coordinator pool profile's §3.6 Coordination Framework is
  consistent with `simulation-bases.md §3` Environment Design.
- The coordinator icon exists at
  `agent_images/icons/market/{stem}.png`, the profile has an `Icon`
  row, and `agent_images/design.md` has the mapping row. Missing or
  broken coordinator icons have been repaired through
  `market-icon-generation-skill.md`.
- Every `players.yml` coordinator block's `archetype:` field resolves
  to the validated pool profile (cross-checked with Step 3 Hook 5).

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

For each built variant `{V}`, run the five Polish Hooks declared in
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
   - Record the divergence in `tmpl/polish-log.md` as an
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
   folders → the user must delete them separately (this
   pipeline does not delete config folders on its own; deletion is
   discussed with the user via `AskUserQuestion`).
5. **Coordinator archetype resolution.** Every `players.yml`
   coordinator block (`market:`, `{variant}_opinion_environment:`,
   `{variant}_information_environment:`, or any other coordinator
   identity declared by the scenario) MUST contain an `archetype:`
   field whose value resolves to an existing pool profile at
   `masim/agents/defines/market/{archetype-value}.md`. Verify:
   - The `archetype:` field is present (missing field is a defect —
     add it using the stem determined at Step 2 Part C Hook 0).
   - The referenced profile exists on disk and has passed
     `market-design-skill.md §6` validation at Step 2.
   - Every Environmental Parameter declared in the pool profile's
     §3.7 has a corresponding key in the coordinator block's `extras`.
     Missing extras keys are defects; add the key with the default
     value from the pool profile's §3.7 table and a `# Source:`
     comment referencing the pool profile.

Run the five Polish Hooks three consecutive times per variant. Any
FAIL resets that variant's count.

### 7.4 Artefacts Changed

- `configs/{ScenarioName}/{V}/*.yml` — `# Source:` comments added,
  values realigned only when the user selected option 1 in Hook 3.
- `configs/{ScenarioName}/{V}/players.yml` — coordinator `archetype:`
  field added if missing (Hook 5); coordinator `extras` keys added
  for Environmental Parameters missing from the pool profile (Hook 5).

Append step summary to `tmpl/polish-log.md`.

### 7.5 Exit Conditions

- All five Step 3 Polish Hooks have three consecutive PASS runs for
  every built variant.
- Every YAML parses.
- Every `# Source:` comment resolves to an upstream anchor.
- Every coordinator block has a valid `archetype:` field pointing to
  an existing `masim/agents/defines/market/` profile, and its `extras` contain
  all Environmental Parameters declared by that profile.

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

For each built variant `{V}`, run the twelve Polish Hooks declared in
the Step 4 Contract (Hooks 1–8 remain the original code / prompt /
RAG gates; Hooks 9–12 are the new analysis-depth gates added in the
2026-07-21 revision — see §8.6 for the analysis-depth contract they
implement):

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
9. **Universal-baseline coverage (analysis depth).** For every built
   variant, its `analysis.py` MUST invoke the universal metric
   aggregator declared in §8.6 exactly once per run:
   ```
   from masim.evaluation.universal import write_universal_summary
   write_universal_summary(data, config, output_dir)
   ```
   The resulting `summary.json` MUST contain a `universal_metrics`
   block whose sub-keys mirror the six standard categories
   (`price_dynamics`, `information_efficiency`, `statistical_inference`,
   `tail_risk`, `agent_behaviour`, `microstructure`) and whose entries
   include every metric in `masim.evaluation.finance.STANDARD_METRICS`
   that did not raise `MetricUnavailable`. **Minimum coverage floor:**
   at least 20 of the 36 registered metrics MUST report a numeric
   result (i.e., neither `_unavailable` nor `_error`). Fewer than 20
   is a FAIL unless the target §10.1 explicitly documents a data
   shape that excludes the missing metrics (e.g., pure opinion
   dynamics scenarios that carry no `market_prices`); such
   exemptions MUST be listed in `analysis-bases.md §2.0 Baseline
   Coverage Exemptions` with the exempted metric names and the
   stylized-fact rationale.
10. **Reference completeness.** Every row in `analysis-bases.md §2`
    (scenario-specific metric catalogue) and every row added under
    §8.6's universal-metric appendix MUST cite a primary academic
    source in the form `Author (Year)` with either a DOI, arXiv id,
    or full journal citation (Journal, Volume(Issue): pages) reachable
    in `simulation-bases.md §2 References`. Rows citing a textbook
    MUST include the specific chapter/section number. Rows without a
    verifiable citation are a FAIL; the fix is to add the citation
    (never invent one). Every row in `analysis.md §2` (implementation
    mapping) MUST re-echo the reference so a reader who opens only
    the variant document can trace the metric back to its primary
    source. Halt via `AskUserQuestion` if a metric was implemented
    without a discoverable primary source — the choice is (a) find a
    source, (b) drop the metric.
11. **Output-artefact contract.** After a smoke run of variant `{V}`
    at `--steps 20`, its analysis output directory
    (`examples/{ScenarioName}/{V}/analysis_output/` or the path
    declared in `analysis.md §5`) MUST contain:
    - `summary.json` — top-level keys REQUIRED: `scenario`, `variant`,
      `config_hash`, `n_rounds`, `universal_metrics`,
      `scenario_metrics`, `variant_extras`, `validation`,
      `files_written`, `references`. `universal_metrics` follows the
      Hook 9 schema; `scenario_metrics` mirrors `analysis-bases.md §2`
      row-for-row; `validation` MUST be a dict with at least
      `passed: bool`, `score: float in [0,1]`, and one entry per
      criterion listed in `analysis-bases.md §6`.
    - Minimum eight PNG dashboards: the four universal panels
      (`00_investor_bids.png`, `01_{scenario_lower}_dynamics.png`,
      `02_{scenario_lower}_analysis.png`, `03_summary.png`) plus at
      least four scenario-specific panels named after the metric
      families in `analysis-bases.md §7`. Scenarios whose §7 declares
      fewer than four scenario-specific panels MUST expand §7 first
      via the define skill revise mode.
    - For Rag-flavoured variants: `rag_stats.json` with per-round
      retrieval counts and top-`k` provenance IDs.
    - For LLM-flavoured variants: a `llm_action_distribution` block
      inside `summary.json` produced by
      `masim.evaluation.analyze_action_distribution`, plus a
      `04_llm_actions.png` panel.
    - For RuleLLM variants: both the LLM action distribution AND a
      `rule_llm_divergence` block that reports the mean absolute
      difference between the RuleLLM decision and the corresponding
      Rule variant's rule output on identical inputs. This block MUST
      be computable at smoke-run time; if the Rule variant's outputs
      are not persisted, the smoke run is extended with
      `--persist-rule-shadow`.
    Missing files or missing top-level keys are a FAIL. Extra files
    are allowed but MUST be referenced in `summary.json.files_written`.
12. **Cross-variant summary parity.** After Hooks 9–11 pass for every
    built variant of the scenario, diff each variant's
    `summary.json` schema (keys, not values) against the Rule-variant
    baseline. Every non-baseline variant's `summary.json` MUST have
    the same top-level keys, the same `universal_metrics` category
    keys, and the same `scenario_metrics` row names as the Rule
    variant, plus the variant-specific extras from Hook 11 (Rag →
    `rag_stats`; LLM/RuleLLM → `llm_action_distribution`; RuleLLM
    → `rule_llm_divergence`). Divergent keys are a FAIL; the fix is
    to promote the metric from a variant-local shadow into the
    universal or scenario layer, or to drop it if it was truly
    idiosyncratic. This hook exists so that cross-variant delta
    tables in `analysis.md §4` and paper-level comparisons remain
    apples-to-apples.

Run the twelve Polish Hooks three consecutive times per variant. Any
FAIL resets that variant's count.

### 8.4 Artefacts Changed

- `examples/{ScenarioName}/{V}/players.py` — `.get(...)` → `[...]`
  conversions, comments added.
- `examples/{ScenarioName}/{V}/analysis.py` — same, plus function
  additions if a metric was missing, plus the mandatory
  `write_universal_summary(data, config, output_dir)` call at the
  end of the analysis pipeline (Hook 9).
- `examples/{ScenarioName}/{V}/prompts.py` — parser fixes for §4.2.3
  compliance; dual-section labels restored where missing.
- `examples/{ScenarioName}/{V}/explain.md` — §2 bidirectional
  completeness fills / removals.
- `examples/{ScenarioName}/{V}/analysis.md` — §2 bidirectional
  completeness fills / removals; reference column added to every §2
  row (Hook 10); §5 output artefact list updated to enumerate the
  eight-panel PNG floor and the `summary.json` schema (Hook 11).
- `examples/{ScenarioName}/analysis-bases.md` — reference column
  populated for every §2 row (Hook 10); new §2.0 Baseline Coverage
  Exemptions subsection added when Hook 9 identifies data-shape
  exemptions; §7 expanded to enumerate at least four scenario-specific
  PNG panels when needed.
- `examples/{ScenarioName}/{V}/analysis_output/summary.json` and the
  eight-panel PNG floor — produced by the Hook 11 smoke run and
  checked in per repo convention.

Append per-variant audit summary to `tmpl/polish-log.md`.

### 8.5 Exit Conditions

- All twelve Step 4 Polish Hooks have three consecutive PASS runs for
  every built variant.
- No `.get(key, default)` pattern remains for required data anywhere
  under `examples/{ScenarioName}/`.
- Every built variant compiles cleanly and imports cleanly.
- Every built variant's `explain.md §2` and `analysis.md §2` are
  bidirectionally complete.
- Every built variant's `analysis_output/summary.json` conforms to
  the Hook 11 schema and passes the Hook 12 cross-variant parity
  diff against the Rule-variant baseline.
- Every metric row in `analysis-bases.md §2` and every row in each
  variant's `analysis.md §2` carries a verifiable primary-source
  citation (Hook 10).
- The universal-baseline coverage floor of ≥ 20 numeric metrics
  (out of 36 registered) is met by every variant, or the missing
  metrics are documented in `analysis-bases.md §2.0 Baseline
  Coverage Exemptions` with a stylized-fact rationale.

### 8.6 Universal Metric Contract (analysis depth)

This section is the substantive contract that Hooks 9–12 enforce.
It defines a three-layer metric taxonomy — every scenario's
`analysis-bases.md §2` MUST be structured under these three layers,
in this order — and enumerates the primary academic sources that
back the universal (Layer A) baseline.

**Layer A — Universal baseline (36 metrics, reusable across all
finance-like scenarios).** These metrics are provided by
`masim.evaluation.finance.STANDARD_METRICS` and computed in one
call via `write_universal_summary(...)`. Every scenario MUST invoke
this call. Metrics that raise `MetricUnavailable` for a given data
shape are silently skipped and recorded under
`summary.json.universal_metrics.<category>._unavailable`.

Category A.1 — `price_dynamics` (12 metrics).

| Metric name                       | Primary reference                                                                     | What it measures                                             |
|-----------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `price_deviation_ts`              | Shiller (1981) *AER* 71(3):421–436                                                    | Rolling price vs. fundamental deviation series               |
| `mad_pct`                         | Shiller (2000) *Irrational Exuberance* ch. 1                                          | Mean-absolute-deviation of price from fundamental (%)        |
| `half_life_threshold`             | Campbell & Shiller (1988) *RFS* 1(3):195–228                                          | Threshold-crossing time for deviation decay                  |
| `half_life_fitted`                | Cochrane (2001) *Asset Pricing* §20.1                                                 | Log-linear fit of deviation decay half-life                  |
| `rolling_volatility_ts`           | Officer (1973) *JB* 46(3):434–453                                                     | Rolling standard-deviation-of-returns time series            |
| `mean_volatility_pct`             | Schwert (1989) *JF* 44(5):1115–1153                                                   | Period-mean volatility (%)                                   |
| `max_drawdown_pct`                | Magdon-Ismail & Atiya (2004) *Risk* 17(10):99–102                                     | Maximum peak-to-trough decline (%)                           |
| `return_skewness`                 | Chen, Hong & Stein (2001) *JFE* 61(3):345–381                                         | Skewness of the return distribution                          |
| `return_kurtosis`                 | Cont (2001) *Quant. Finance* 1(2):223–236                                             | Excess kurtosis (fat-tail signature)                         |
| `return_autocorr_lag1`            | Fama (1970) *JF* 25(2):383–417                                                        | Lag-1 return autocorrelation (weak-form efficiency)          |
| `return_autocorr_profile`         | Lo & MacKinlay (1988) *RFS* 1(1):41–66                                                | Full 1..K lag autocorrelation profile                        |
| `deviation_decay_slope`           | De Bondt & Thaler (1985) *JF* 40(3):793–805                                           | Slope of log-deviation on lag (mean reversion speed)         |

Category A.2 — `information_efficiency` (5 metrics).

| Metric name                       | Primary reference                                                                     | What it measures                                             |
|-----------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `variance_ratio_lo_mackinlay`     | Lo & MacKinlay (1988) *RFS* 1(1):41–66                                                | Variance-ratio test statistic against the random walk        |
| `under_revision_ratio`            | Barberis, Shleifer & Vishny (1998) *JFE* 49(3):307–343                                | Ratio of under-reactive to over-reactive belief updates      |
| `regime_transition_lag`           | Hamilton (1989) *Econometrica* 57(2):357–384                                          | Latency between regime shift and detected transition         |
| `price_efficiency_ratio`          | Grossman & Stiglitz (1980) *AER* 70(3):393–408                                        | Ratio of informed to noise-driven price variance             |
| `forecast_error_persistence`      | Hong & Stein (1999) *JF* 54(6):2143–2184                                              | Autocorrelation of one-step-ahead forecast errors            |

Category A.3 — `statistical_inference` (4 metrics).

| Metric name                             | Primary reference                                                    | What it measures                                             |
|-----------------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------|
| `mad_block_bootstrap_ci_95`             | Politis & Romano (1994) *JASA* 89(428):1303–1313                     | Block-bootstrap 95 % CI for `mad_pct`                        |
| `half_life_block_bootstrap_ci_95`       | Politis & Romano (1994) *JASA* 89(428):1303–1313                     | Block-bootstrap 95 % CI for `half_life_fitted`               |
| `ljung_box_returns_pvalue`              | Ljung & Box (1978) *Biometrika* 65(2):297–303                        | Portmanteau test for serial correlation in returns           |
| `adf_unit_root_pvalue`                  | Dickey & Fuller (1979) *JASA* 74(366a):427–431                       | Augmented Dickey–Fuller unit-root test p-value               |

Category A.4 — `tail_risk` (2 metrics).

| Metric name                       | Primary reference                                                                     | What it measures                                             |
|-----------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `value_at_risk_95`                | Jorion (2006) *Value at Risk* 3rd ed. §5                                              | Historical VaR at 95 % confidence                            |
| `conditional_var_95`              | Artzner, Delbaen, Eber & Heath (1999) *Math. Finance* 9(3):203–228                    | Expected shortfall (CVaR / ES) at 95 %                       |

Category A.5 — `agent_behaviour` (8 metrics).

| Metric name                       | Primary reference                                                                     | What it measures                                             |
|-----------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `agent_action_frequency`          | Odean (1998) *JF* 53(6):1775–1798                                                     | Per-agent buy / sell / hold frequency                        |
| `silent_agent_count`              | Merton (1987) *JF* 42(3):483–510                                                      | Number of agents that never traded                           |
| `agent_volume_buy_sell`           | Karpoff (1987) *JFQA* 22(1):109–126                                                   | Per-agent gross buy and sell volumes                         |
| `agent_net_position_ts`           | Kyle (1985) *Econometrica* 53(6):1315–1335                                            | Per-agent net position time series                           |
| `agent_pnl_terminal`              | Sharpe (1966) *J. Business* 39(1):119–138                                             | Terminal per-agent profit-and-loss                           |
| `agent_sharpe_terminal`           | Sharpe (1966) *J. Business* 39(1):119–138                                             | Terminal per-agent Sharpe ratio                              |
| `agent_wealth_terminal`           | Levy, Levy & Solomon (2000) *Microscopic Simulation of Financial Markets* ch. 7       | Terminal per-agent wealth                                    |
| `gini_coefficient`                | Gini (1912) *Variabilità e mutabilità*                                                | Gini coefficient of terminal wealth distribution             |

Category A.6 — `microstructure` (5 metrics).

| Metric name                       | Primary reference                                                                     | What it measures                                             |
|-----------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `order_imbalance_ts`              | Chordia, Roll & Subrahmanyam (2002) *JFE* 65(1):111–130                               | Per-round buy-minus-sell order imbalance                     |
| `signed_volume_autocorr`          | Hasbrouck (1991) *JF* 46(1):179–207                                                   | Autocorrelation of signed volume                             |
| `herfindahl_volume_concentration` | Hirschman (1945) *National Power and the Structure of Foreign Trade*                  | Herfindahl–Hirschman index of per-agent volume share         |
| `strategy_correlation_matrix`     | Lakonishok, Shleifer & Vishny (1992) *JFE* 32(1):23–43                                | Cross-strategy correlation matrix of net demand              |
| `information_share_by_strategy`   | Hasbrouck (1995) *JF* 50(4):1175–1199                                                 | Information share attributed to each strategy family         |

**Layer B — Scenario-specific metrics (typically 4–10 per scenario,
authored in `analysis-bases.md §2` and implemented in
`masim/evaluation/finance/scenario_metrics.py` or in the scenario's
own `metrics.py` if truly local).** Layer B rows MUST cite a primary
source and MUST NOT duplicate Layer A. Typical anchors by family:

| Scenario family                            | Signature metrics                                                                    | Canonical references                                                                                                                                                                              |
|--------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Bubble / crash (AssetBubble, TulipMania, SouthSeaBubble, DotComBubble) | `bubble_magnitude`, `crash_amplitude`, `run_up_slope`, `peak_deviation`              | Shiller (2000); Kindleberger & Aliber (2005) *Manias, Panics, and Crashes* 5th ed.; De Long, Shleifer, Summers & Waldmann (1990) *JF* 45(2):379–395                                                |
| Herding / cascade (HerdEffect, ConfirmationBias, EchoChamber)          | `bid_convergence_cv`, `directional_agreement`, `cascade_measure`, `herding_episodes` | Bikhchandani, Hirshleifer & Welch (1992) *JPE* 100(5):992–1026; Christie & Huang (1995) *FAJ* 51(4):31–37; Chang, Cheng & Khorana (2000) *JBF* 24(10):1651–1679                                    |
| Volatility clustering (GARCHVolatility, FlashCrash)                    | `garch_signature`, `volatility_persistence`, `return_clustering`, `regime_switch`    | Bollerslev (1986) *J. Econometrics* 31(3):307–327; Engle (1982) *Econometrica* 50(4):987–1008; Andersen, Bollerslev, Diebold & Labys (2003) *Econometrica* 71(2):579–625                           |
| Momentum / reversal (MomentumEffect, ReversalEffect)                   | `momentum_return`, `reversal_slope`, `winner_loser_spread`                           | Jegadeesh & Titman (1993) *JF* 48(1):65–91; De Bondt & Thaler (1985) *JF* 40(3):793–805                                                                                                            |
| Currency crisis (CurrencyCrisis, AsianFinancialCrisis, CarryTradeUnwind) | `defense_reserves_burn`, `attack_probability`, `peg_break_lag`                       | Krugman (1979) *JMCB* 11(3):311–325; Obstfeld (1996) *EER* 40(3):1037–1047; Brunnermeier, Nagel & Pedersen (2008) *NBER Macro Annual* 23:313–347                                                   |
| Bank / liquidity run (BankRun, SVBBankRun, LiquidityDryup)             | `withdrawal_hazard`, `run_probability`, `panic_onset_round`                          | Diamond & Dybvig (1983) *JPE* 91(3):401–419; Gorton (1988) *OEP* 40(4):751–781                                                                                                                     |
| Anchoring / behavioural bias (AnchoringEffect, AvailabilityBias, DispositionEffect) | `anchor_bias_score`, `availability_bias_score`, `disposition_gain_loss_ratio`        | Northcraft & Neale (1987) *OBHDP* 39(1):84–97; Kahneman, Slovic & Tversky (1982) *Judgment under Uncertainty*; Shefrin & Statman (1985) *JF* 40(3):777–790                                         |
| Credit / Minsky cycle (CreditCycle)                                    | `leverage_cycle_amplitude`, `credit_expansion_slope`, `minsky_moment_round`          | Minsky (1986) *Stabilizing an Unstable Economy* ch. 9; Geanakoplos (2010) *NBER Macro Annual* 24:1–65                                                                                              |
| Equity premium / dividend puzzle (EquityPremium)                       | `equity_premium_pct`, `dividend_yield_gap`                                           | Mehra & Prescott (1985) *J. Monetary Econ.* 15(2):145–161; Campbell & Cochrane (1999) *JPE* 107(2):205–251                                                                                         |
| Opinion / information dynamics (OpinionDynamics, InformationCascade)   | `polarization_index`, `consensus_time`, `information_diffusion_rate`                 | Deffuant, Neau, Amblard & Weisbuch (2000) *ACS* 3:87–98; DeGroot (1974) *JASA* 69(345):118–121; Watts & Dodds (2007) *JCR* 34(4):441–458                                                           |

Layer B rows for scenarios outside the families above MUST still
carry a primary source; consult `docs/analysis-bases-corpus.md` or
halt via `AskUserQuestion` to solicit the source.

**Layer C — Variant-specific extras (surface variance across
Rule / LLM / RuleLLM / Rag).**

| Variant  | Required extra                                                                          | Reference / rationale                                                          |
|----------|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Rule     | (none beyond Layers A + B)                                                              | Rule variant is the schema baseline for Hook 12 parity.                        |
| LLM      | `summary.json.llm_action_distribution` + `04_llm_actions.png`                           | `masim.evaluation.analyze_action_distribution`; Bikhchandani et al. (1992)     |
| RuleLLM  | LLM extras + `summary.json.rule_llm_divergence`                                         | Divergence between LLM decision and shadow Rule decision; Christie–Huang (1995)|
| Rag      | `rag_stats.json` (per-round retrieval count, top-k provenance) + `05_rag_provenance.png`| Lewis, Perez, Piktus et al. (2020) *NeurIPS* 33:9459–9474 (RAG paper)          |

Layers A + B + C together determine the passing metric surface. A
scenario that ships only Layers A + B without the applicable Layer C
extras FAILs Hook 11.

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

| Pass | Perspective                       | Anchors in `09-step5-to-10-review.md`                                                                                                                                                                         |
|------|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | Theory–code alignment             | §5.1 Theory-Code Alignment; §5.2 Prompt Fidelity; §5.3 Configuration Validation; §5.4 Diversity                                                                                                               |
| 2    | Code quality + analysis tools     | §6.1 Required Documentation; §6.2 Correctness; §6.3 Style; §7.1 Baseline-variant analysis-module Requirements; `10-evaluation-architecture.md` import compliance (all reusable code from `masim/evaluation/`) |
| 3    | Documentation + final cross-check | §8 Create Documentation; §9 Execute and Debug (dry-run only)                                                                                                                                                  |

Any unchecked item in any pass resets the count for that pass. All
three passes MUST reach three consecutive PASSes; failure to reach
three PASSes on any pass is a defect that MUST be repaired before the
smoke run.

**Pass 2 — Analysis Migration Rule.**

During Pass 2, for every `analysis.py` in every variant, apply this mandatory migration procedure:

1. **Search `masim/evaluation/`** for existing functions that match what the analysis script needs (metrics, data loading, visualization, validation). Use the module responsibility boundaries and placement flowchart in `10-evaluation-architecture.md`.

2. **If a matching function exists in `masim/evaluation/`** → replace the local implementation with an import. Remove the local function definition (or, if other in-scenario code still calls it, alias it: `from masim.evaluation.finance.timeseries import calculate_max_drawdown as _compute_max_drawdown`).

3. **If no matching function exists but the local function is reusable** (would serve other scenarios) → migrate it into the appropriate `masim/evaluation/{domain}/{module}.py` file first, add it to `__init__.py` re-exports, then import it back into the analysis script.

4. **If the function is truly scenario-specific** (unique logic that no other scenario would use) → keep it local in the analysis script with a comment: `# Scenario-specific: {reason}`.

5. **Data loading** (`_batch_to_rounds`, `_load_data`, `_market_players`, `_market_data_from_payload`) must always come from `masim.evaluation.data_loader`. Remove any local re-implementations of these.

6. **Registry types** (`Metric`, `MetricsRegistry`, `MetricUnavailable`) must always come from `masim.evaluation.registry`.

After migration, verify with `python3 -c "import examples.{Scenario}.Rule.analysis"` that all imports resolve.

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

Append step summary to `tmpl/polish-log.md`.

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

| Downstream artefact                                          | Upstream anchor in target file                     |
|--------------------------------------------------------------|----------------------------------------------------|
| `simulation-bases.md §1` Phenomenon Definition               | target §2 + §6                                     |
| `simulation-bases.md §2` Theoretical Foundation              | target §4                                          |
| `simulation-bases.md §3` Environment Design                  | target §5 + §8                                     |
| `simulation-bases.md §4.{N}` Agent blocks                    | target §7 row + target §4 for each theory          |
| `simulation-bases.md §5` Diversity Verification              | target §7 (roster diversity)                       |
| `simulation-bases.md §6` Parameter Table                     | target §9                                          |
| `simulation-bases.md §7` Communication and Round Structure   | target §8                                          |
| `simulation-bases.md §8` Historical / Empirical Case Studies | target §6                                          |
| `analysis-bases.md §1` Analysis Objectives                   | target §3                                          |
| `analysis-bases.md §2` Core Metrics Catalogue                | target §10.2                                       |
| `analysis-bases.md §6` Expected Results                      | target §5 + §6 + §10.2                             |
| `configs/{ScenarioName}/{V}/players.yml` extras              | target §9 (via `# Source:` comments)               |
| Variant `{V}`'s agent-implementation module classes          | `simulation-bases.md §4.{N}` (via `explain.md §2`) |
| Variant `{V}`'s analysis module functions                    | `analysis-bases.md §2` (via `analysis.md §2`)      |
| `masim/agents/defines/{Domain}/<file>.md` (touched)           | target §7 row + agent §3.11 Provenance             |
| `masim/agents/defines/market/<file>.md` (touched)             | target §8 + coordinator §3.11 Provenance           |
| `configs/{ScenarioName}/{V}/players.yml` coordinator block   | `masim/agents/defines/market/` profile (via `archetype:`)    |
| Variant subdirectories present                               | target §10.1                                       |
| `analysis_output/summary.json.universal_metrics`             | §8.6 Layer A tables (36 rows across 6 categories)  |
| `analysis_output/summary.json.scenario_metrics`              | `analysis-bases.md §2` Layer B rows                |
| `analysis_output/summary.json.variant_extras`                | §8.6 Layer C table                                 |
| `analysis_output/summary.json.validation`                    | `analysis-bases.md §6` Validation Criteria         |
| `analysis_output/summary.json.references`                    | `analysis-bases.md §2` reference column + §8.6 A/B |
| Reference column in `analysis-bases.md §2` rows              | §8.6 Layer A/B primary-source tables               |
| Reference column in variant `analysis.md §2` rows            | `analysis-bases.md §2` reference column            |
| Eight-panel PNG floor in `analysis_output/`                  | `analysis-bases.md §7` visualization plan          |

Any unanchored downstream artefact is a defect and MUST be repaired
before Status transition (or halted via `AskUserQuestion` if it
requires substantive input, in which case the fix is pushed through
define skill revise mode).

### 10.2 Run Summary (local log)

At closeout, append a full-run summary block to `tmpl/polish-log.md`:

```
polish({ScenarioName}): closeout — status released

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
YYYY-MM-DD  Superseded by polish audit; polish trail lives in
            tmpl/polish-log.md. This build-log is retained for
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

### 10.5 Exit Conditions and Closeout

- Traceability matrix fully resolved.
- Target §1 Status: `released`.
- Legacy build-log (if any) has a supersession line in §D.
- Every step (Preflight → Step 0 → Step 1 → Step 2 → Step 3 → Step 4
  → Steps 5 — 10 → Closeout) has a corresponding entry in
  `tmpl/polish-log.md`.

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
- A coordinator's `market-design-skill.md §6` Validation Checklist
  has three consecutive FAILs (no green PASS achievable within the
  polish scope) — same halt protocol as participant agents.
- An masim/agents/defines/market/ outcome-shrink new→reuse is detected (Step 2
  Part C Hook 1) and the user has not yet chosen adopt / keep-fork /
  revise-mode.
- The coordinator pool profile's §3.6 Coordination Framework
  contradicts `simulation-bases.md §3` and no authoritative source is
  determinable (Step 2 Part C Hook 3 ambiguous case).
- A pre-consistency check (Step 0 Case B) fails — some `§4.{N}` block
  has no matching implementation class, or vice versa.
- A dual-section prompt invariant (Step 4 Hook 5) or `_RAG_FALLBACK`
  invariant (Step 4 Hook 8) fails and the fix requires content that
  is not present in existing artefacts.
- Universal-baseline coverage (Step 4 Hook 9) reports fewer than 20
  numeric metrics and no defensible data-shape exemption can be
  formulated. The halt options are: (i) implement the missing data
  fields in the coordinator (loops back to Step 2), (ii) accept a
  documented exemption in `analysis-bases.md §2.0`, or (iii) drop
  the failing variant.
- A metric row lacks a discoverable primary source (Step 4 Hook 10).
  The halt options are: (i) supply a citation, (ii) drop the row —
  never invent a citation.
- Cross-variant `summary.json` parity (Step 4 Hook 12) fails and the
  divergent key is genuinely idiosyncratic. The halt options are:
  (i) promote the metric into the universal or scenario layer,
  (ii) drop the metric from the variant that carries it. Silent
  drift is forbidden.
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
which produces the corrected target file. Once the define skill
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
- **Local-log discipline**: append one entry to `tmpl/polish-log.md`
  per completed step. The log file is created at Preflight if absent.
  This local file is the polish run's primary audit trail (no build
  log is written; no git commits are made by the pipeline).
- **No git commits**: the polish pipeline MUST NOT execute `git add`,
  `git commit`, or any version-control command. All file changes
  remain local and unstaged. The user decides post-run when to commit.
- **Workspace throwaway**: the Preflight inventory lives in the
  runtime workspace directory (see the runtime environment for the
  concrete path) and MUST NOT be committed to the repository.
- **Contract-block edits**: if audit uncovers a gap in one of the
  Contract blocks (a step’s Inputs / Outputs / Polish Hooks are
  incomplete or ambiguous), the pipeline MAY non-destructively edit
  the Contract block *of that step file only*. Substantive rewrites
  of adjacent prose are out of scope.
- **Target-file edits**: the polish pipeline MUST NOT hand-edit the
  target file except for (a) the single Status transitions at Step 0
  (`draft → locked`) and Closeout (`locked → released`), and
  (b) Case B seed writes handed off to the define skill's revise mode.
  All other target-file changes go through the define skill. No
  changelog, audit trail, or §0 section may be written into the
  target file.
- **Non-spec content removal**: any field, row, section, or block
  found in a downstream artefact that is NOT defined in the governing
  skill spec MUST be deleted during the polish audit. Examples:
  `Change log` rows in agent §3.11 tables (removed from
  `agent-design-skill.md` spec), `CHANGELOG` tables, `§0` sections,
  `Produced By` / `Created` / `Status` rows in scenario §1 Meta.
  The pipeline does not preserve legacy content that violates the
  current spec — delete it outright.

---

## 13. Pipeline Entry Checklist (Pre-Run)

Run this checklist once before invoking Preflight:

- [ ] The scenario `examples/{ScenarioName}/` exists and contains at
      least one downstream artefact (`simulation-bases.md`,
      `analysis-bases.md`, or a variant subdirectory declared in
      target §10.1).
- [ ] Working tree is clean (no unrelated local modifications).
- [ ] The reader has read the `## Contract` block of every step file
      listed in §14 (this is the audit-facing surface — read it
      first).
- [ ] The AGENT_POOL folder for the scenario's domain
      (`masim/agents/defines/{Domain}/`) exists and is up to date.
- [ ] The reader has read this file (`polish-simulation-pipeline.md`)
      end-to-end at least once.
- [ ] The reader is aware that this pipeline **does not** produce a
      `simulation-build-log.md`; audit trail is §3.11 Provenance +
      `tmpl/polish-log.md` (no content is written into the target file
      itself).
- [ ] The reader is aware that all substantive target-file changes go
      through `define-simulation-scenario-skill.md §9.3 revise mode`,
      never through direct hand-editing of the target file.

If any item is unchecked, fix it before starting Preflight.

---

## 14. Skill References (Quick Index)

| Topic                                                       | File                                                                   |
|-------------------------------------------------------------|------------------------------------------------------------------------|
| Scenario target-file spec (§11 checklist, §9.3 revise mode) | `masim/skills/define-simulation-scenario-skill.md`                     |
| Universal Agent Design Handbook (§3, §6)                    | `masim/skills/agent-design-skill.md`                                   |
| Market Coordinator Design Handbook (§3, §6)                 | `masim/skills/market-design-skill.md`                                  |
| Market coordinator icon generation                          | `masim/skills/market-icon-generation-skill.md`                         |
| From-scratch pipeline (contrast)                            | `masim/skills/create-simulation-pipeline.md`                           |
| Methodology overview                                        | `masim/skills/implement-simulation-skill/00-overview.md`               |
| Directory layout                                            | `masim/skills/implement-simulation-skill/01-mandatory-structure.md`    |
| Root document specs (bases.md files)                        | `masim/skills/implement-simulation-skill/02-root-documents-spec.md`    |
| Variant document specs                                      | `masim/skills/implement-simulation-skill/03-variant-documents-spec.md` |
| Step 0 (Load target)  — Contract                            | `masim/skills/implement-simulation-skill/04-step0-load-target.md`      |
| Step 1 (Research)     — Contract                            | `masim/skills/implement-simulation-skill/05-step1-research.md`         |
| Step 2 (Agent + env design + Pool gate) — Contract          | `masim/skills/implement-simulation-skill/06-step2-agent-design.md`     |
| Step 3 (Config)       — Contract                            | `masim/skills/implement-simulation-skill/07-step3-config.md`           |
| Step 4 (Implement)    — Contract                            | `masim/skills/implement-simulation-skill/08-step4-implement.md`        |
| Steps 5 — 10 (Validate, review, run) — Contract             | `masim/skills/implement-simulation-skill/09-step5-to-10-review.md`     |
| AssetBubble reference implementation (finance domain)       | `masim/skills/implement-simulation-skill/15-reference-assetbubble.md`  |
| AGENT_POOL directory                                        | `masim/agents/defines/`                                                 |
| AGENT_POOL market coordinator pool                          | `masim/agents/defines/market/`                                          |
| Project structure overview                                  | `docs/structure.md`                                                    |

---

## 15. Status

`Status: canonical`. This file supersedes the legacy Phase A — Phase G
polish structure. Any legacy scenario polished under the old phases
remains valid; new polish runs MUST use the Preflight → Step 0 — 10 →
Closeout structure documented here.
