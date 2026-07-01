---
name: polish-simulation-pipeline
purpose: Top-level pipeline for **upgrading and standardising an existing MASim simulation scenario** (already present under `examples/{ScenarioName}/`) so that every artefact conforms to the current versions of the skill suite (`define-simulation-scenario-skill.md`, `agent-design-skill.md`, `implement-simulation-skill/`). This pipeline reverse-engineers a scenario target file if one is missing, audits each downstream artefact against the latest skill specifications, applies patches in place, and closes with the same smoke-test rigour as `create-simulation-pipeline.md`. **Not for creating a new scenario from scratch** — use `create-simulation-pipeline.md` for that.
status: canonical
audience: Authors and reviewers bringing a pre-existing scenario in `examples/` up to the current skill baseline.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
invocation: Call this file when a scenario under `examples/{ScenarioName}/` already contains one or more of `simulation-bases.md`, `analysis-bases.md`, `investors/`, or variant subdirectories, and the intent is to align these artefacts with the current skill baseline (not to add new research content). Do NOT invoke `create-simulation-pipeline.md` on an already-built scenario — it assumes an empty target folder and will refuse to overwrite. Do NOT open `implement-simulation-skill/` files directly during a polish run except when the phase below explicitly dispatches to them.
---

# Polish-Simulation-Pipeline — Upgrade Existing Scenario to Latest Skill Baseline

## 0. Scope and Authority

This skill governs **audit-and-patch upgrades** of an existing scenario.
It does not add new empirical content, does not change the scenario's
research question, and does not invent new agent archetypes; it brings
every existing artefact into conformance with the current versions of:

- `masim/skills/define-simulation-scenario-skill.md` (target file spec)
- `masim/skills/agent-design-skill.md` (Universal Agent Design Handbook,
  §3.1 — §3.11 canonical order, §6 Validation Checklist)
- `masim/skills/implement-simulation-skill/` (per-step methodology)

If, during audit, the scenario is found to require materially new
research — e.g., a stylized fact was never sourced, or an agent
archetype has no theory anchor — the polish run **halts and returns**;
the author must either supply the missing content (upstream, into the
scenario target file) or explicitly scope the deficit out of the
polish. A polish run MUST NOT silently invent missing evidence.

| Concern                                       | Owner                                                              |
|-----------------------------------------------|--------------------------------------------------------------------|
| **Target-file spec against which we align**   | **`masim/skills/define-simulation-scenario-skill.md`**             |
| Per-agent handbook against which we align     | `masim/skills/agent-design-skill.md`                               |
| Root / variant layout against which we align  | `masim/skills/implement-simulation-skill/` (files 01 — 09)         |
| Domain-instantiation rules for finance        | `implement-simulation-skill/02-root-documents-spec.md §4.1`        |
| AGENT_POOL three-stage match protocol         | This file §5 and `implement-simulation-skill/06 §2.2.0`            |
| Three-PASS validation discipline              | This file §7 and `agent-design-skill.md §6`                        |
| From-scratch pipeline (contrast)              | `masim/skills/create-simulation-pipeline.md`                       |

---

## 1. Design Philosophy

Five commitments shape every step of a polish run. They are a
deliberate subset of `create-simulation-pipeline.md §1` — items that
apply equally to upgrades — plus one polish-specific commitment:

1. **Preserve intent, upgrade form.** The scenario's research question,
   agent roster, and empirical claims are inherited from the existing
   artefacts. The polish pipeline changes structure, wording,
   anchoring, and validation posture — not substance.
2. **No `simulation-build-log.md`.** A polish run is a bounded audit,
   not a long-running build. The build-log contract used by
   `create-simulation-pipeline.md` is **skipped**. Audit trail is
   distributed across three places, in priority order:
   - **Target file §0 Meta CHANGELOG** (one line per polish run,
     summarising what was standardised).
   - **Per-agent §3.11 Design Provenance** (updated in place to record
     that this agent's specification was audited on this date against
     handbook v?, and to list any structural changes).
   - **Git commit history** (one commit per completed phase, with a
     detailed message body). This is the primary process log.
3. **Handbook as a contract, not a template.** Every existing
   `investors/<role>.md` or `simulation-bases.md §4.{N}` block is
   compared **exactly** against `agent-design-skill.md §3` and §6.
   Structural deviations are corrected; content is preserved.
4. **AGENT_POOL reuse gate is re-run.** Existing agents may currently
   reference stale pool entries (or fail to reference the pool at
   all). The polish run re-executes the three-stage match against the
   current pool and updates §3.11 Provenance to reflect the correct
   `reuse` / `override` / `fork` / `new` outcome.
5. **Three consecutive PASSes equals approved.** Every validation
   checklist (handbook §6, root-doc spec, variant-doc spec, review
   checklist) MUST run three times in succession. This is unchanged
   from the from-scratch pipeline.

---

## 2. Pipeline Overview

```text
        ┌──────────────────────────────────────────────┐
        │ Phase A — Inventory and Gap List             │
        │   Enumerate existing files; classify each as │
        │   present / missing / non-conforming.        │
        │   Output: workspace gap list (throwaway).    │
        └──────────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────┐
        │ Phase B — Target File Reconstruction         │
        │   If {domain}-{scenario}.md is missing:      │
        │   reverse-engineer it from existing          │
        │   bases.md + investors/ + configs.           │
        │   Then run §11 three-PASS. Status: locked.   │
        └──────────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────┐
        │ Phase C — Root Document Audit                │
        │   simulation-bases.md, analysis-bases.md     │
        │   vs 02-root-documents-spec.md.              │
        │   Fix section names, handbook anchor         │
        │   off-by-one, domain-extension labelling.    │
        └──────────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────┐
        │ Phase D — Per-Agent Handbook Audit           │
        │   For each investors/<role>.md AND each      │
        │   §4.{N} block in simulation-bases.md:       │
        │   check §3.1 — §3.11 canonical order,        │
        │   re-run AGENT_POOL gate, update §3.11.      │
        │   Three-PASS handbook §6 review.             │
        └──────────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────┐
        │ Phase E — Variant Artefact Audit             │
        │   03-variant-documents-spec.md compliance    │
        │   for explain.md / analysis.md.              │
        │   08-step4-implement.md compliance for       │
        │   players.py / analysis.py (no defaults).    │
        │   07-step3-config.md compliance for *.yml.   │
        └──────────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────┐
        │ Phase F — Scenario-Level 3-PASS Review       │
        │   implement-simulation-skill/09 Steps 5 — 9  │
        │   run three times in a row.                  │
        └──────────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────┐
        │ Phase G — Smoke Test and Closeout            │
        │   Run every built variant at smoke-test      │
        │   scale. Update target §0 Meta CHANGELOG.    │
        │   Status: released.                          │
        └──────────────────────────────────────────────┘
```

Each phase declares **entry conditions**, **artefacts changed**, and
**exit conditions**. A phase MUST NOT start until its entry conditions
hold; a phase MUST NOT be marked done until its exit conditions hold.

---

## 3. Phase A — Inventory and Gap List

### 3.1 Entry Conditions

- The scenario folder `examples/{ScenarioName}/` exists and contains at
  least one of: `simulation-bases.md`, `analysis-bases.md`,
  `investors/`, `Rule/`, `LLM/`, `RuleLLM/`, `Rag/`.
- Repository is clean (`git status` shows no unrelated diffs).

### 3.2 Procedure

Enumerate every file in the scenario folder and classify against the
current expected structure declared in
`implement-simulation-skill/01-mandatory-structure.md §1`:

| Class                      | Meaning                                                                  |
|----------------------------|--------------------------------------------------------------------------|
| **Present, conforming**    | File exists and matches current spec (structure only; content audited later). |
| **Present, non-conforming**| File exists but has stale filenames, missing sections, or wrong header levels. |
| **Missing (required)**     | File does not exist but the current spec requires it (e.g., the target file). |
| **Missing (conditional)**  | File does not exist and its variant is not marked `Yes` in target §10.1 — no action. |
| **Present, deprecated**    | File exists under an old name (e.g., `simulation-define.md`) and must be renamed / merged. |

Write the classification to
`/Users/sjia/.qoderwork/workspace/mqz1cq048x69z4wm/{ScenarioName}-polish-gap.md`
(workspace throwaway; NOT under version control). This file drives
Phases B — F and is discarded at the end of the polish run.

### 3.3 Artefacts

- Workspace gap-list file (throwaway).
- No changes yet inside the repository.

### 3.4 Exit Conditions

- Every file under `examples/{ScenarioName}/` has one of the five
  classifications assigned.
- The gap list records which of the seven downstream phases will need
  work.

---

## 4. Phase B — Target File Reconstruction (Conditional)

### 4.1 Entry Conditions

- Phase A exit conditions hold.
- Gap list marks `{domain}-{scenario}.md` as `Missing (required)`.
- If the target file is already present and conforming, this phase is
  **skipped entirely** and control passes to Phase C.

### 4.2 Procedure

Reverse-engineer the target file from existing artefacts using the
mapping below, then validate against
`define-simulation-scenario-skill.md §11`:

| Target section              | Source of content in existing scenario                             |
|-----------------------------|--------------------------------------------------------------------|
| §1 Scenario Identity        | `simulation-bases.md §1` + folder name (PascalCase → phrases).     |
| §2 Historical Anchor        | `simulation-bases.md §1` (Phenomenon) + `analysis-bases.md §1`.    |
| §3 Research Question        | `analysis-bases.md §1` (hypotheses reverse-mapped to questions).   |
| §4 Theoretical Anchors      | Union of every `Theoretical Foundation` in every `investors/*.md`. |
| §5 Stylized Facts           | `simulation-bases.md §3` (market mechanism assumptions).            |
| §6 Historical Anchors       | `simulation-bases.md §1` narrative + `analysis-bases.md` metric bibliography. |
| §7 Agent Roster             | One row per `investors/<role>.md` (or per `§4.{N}` block).         |
| §8 Signal Palette           | Union of every `Decision Information Set` in every investor spec. |
| §9 Parameter Table          | Union of every `Parameters` table across investor specs + `configs/{Scenario}/*/players.yml` extras. |
| §10.1 Build Matrix          | For each of `{Rule, LLM, RuleLLM, Rag}`: `Yes` if the variant folder exists, `No` otherwise. |
| §10.2 Success Criteria      | `analysis-bases.md §2` metrics.                                   |

Write the reconstructed target file to
`examples/{ScenarioName}/{domain}-{scenario}.md` with `Status: draft`.

Run `define-simulation-scenario-skill.md §11` validation three times
consecutively. First-pass failures are expected: the reverse-engineered
draft usually has gaps that only surface under validation. Repair each
failure by pulling more detail from the source artefacts identified in
the mapping table above; do NOT fabricate. If a failure genuinely
cannot be repaired without new research, halt the polish run and
escalate to the author.

Once three consecutive PASS runs are achieved, edit §1 `Status` from
`draft` to `locked`.

### 4.3 Artefacts

- `examples/{ScenarioName}/{domain}-{scenario}.md` — `Status: locked`.
- §0 Meta CHANGELOG initialised with:
  ```
  YYYY-MM-DD  Reconstructed from existing artefacts during polish run
              against skill baseline vX.Y.
  ```

### 4.4 Exit Conditions

- Target file exists and is locked.
- Every downstream artefact can be traced back to a section of the
  target file (this trace is verified explicitly in Phase G).

---

## 5. Phase C — Root Document Audit

### 5.1 Entry Conditions

- Target file exists and is locked (from Phase B, or already present).

### 5.2 Procedure

Open `simulation-bases.md` and `analysis-bases.md`, and walk each
against `implement-simulation-skill/02-root-documents-spec.md`. The
recurring issues found on legacy scenarios are:

1. **§4.0 mapping table drift.** Confirm every entry matches the
   current spec (notably: Validation row must read `## Behavioral
   Verification and Calibration`, not the older `## Validation and
   Calibration`; Population row must be labelled *(financial-domain
   extension — not in handbook §3 canonical order)* rather than
   claiming handbook §3.8).
2. **Handbook anchor off-by-one.** Legacy scenarios frequently cite
   handbook §3.8 for Worked Examples (correct is §3.8), §3.9 for
   Validation (correct is §3.9 with the new name), §3.10 for
   References (correct is §3.10), §3.11 for Provenance (correct is
   §3.11). Cross-check every `§3.x` reference in every §4.{N} block
   against `agent-design-skill.md §3` current numbering.
3. **§4.3 wrong reference.** `agent-design-skill.md §4` (Evidence
   Provenance) is often cited when `§6` (Validation Checklist) is
   intended. Fix.
4. **Unconditional "four variants" language.** Every phrase like "all
   four variants" or "run all four Rule/LLM/RuleLLM/Rag" MUST be
   softened to "every built variant (the subset marked Yes in target
   §10.1)".
5. **§4.{N}.7 Population labelling.** Every population block MUST
   carry the financial-domain-extension caveat and MUST NOT claim
   handbook parentage.

Apply patches in place. Commit at end of phase with message:
`polish({ScenarioName}): root-doc audit against 02-root-documents-spec.md`.

### 5.3 Artefacts Changed

- `examples/{ScenarioName}/simulation-bases.md`
- `examples/{ScenarioName}/analysis-bases.md`

### 5.4 Exit Conditions

- Every §4.0 mapping row matches the current spec verbatim.
- Every handbook §3.x citation in every §4.{N} block resolves to the
  current handbook.
- No unconditional "four variants" language remains.

---

## 6. Phase D — Per-Agent Handbook Audit

### 6.1 Entry Conditions

- Phase C exit conditions hold.

### 6.2 Procedure

For every agent specification — both the standalone
`investors/<role>.md` file (if the scenario uses standalone specs) and
the re-levelled `§4.{N}` block in `simulation-bases.md` — do the
following, in order:

1. **Section order and completeness (handbook §3).** Confirm the
   canonical order §3.1 Title → §3.2 Summary → §3.3 Definition and
   Goals → §3.4 Theoretical Foundation → §3.5 Design Purpose → §3.6
   Behavioral Framework → §3.7 Parameters → §3.8 Worked Numerical
   Examples → §3.9 Behavioral Verification and Calibration → §3.10
   Academic References → §3.11 Design Provenance. Move sections that
   are out of order; add sections that are missing (using the source
   material already present elsewhere in the file).
2. **Re-run AGENT_POOL three-stage match.** Even if the agent was
   originally reused from the pool, the pool may have been updated
   since. Run the three-stage match from
   `implement-simulation-skill/06 §2.2.0`:
   - Stage 1: filename scan against
     `examples/AGENT_POOL/<domain>/*.md`.
   - Stage 2: 7-row Summary fingerprint (≥5/7 match, or ≥3+Theory
     Family match, → escalate).
   - Stage 3: full-text inspection.
   - Outcome ∈ {reuse, reuse+override, fork, new}.
3. **Update §3.11 Design Provenance.** Rewrite this section to record
   the current polish run:
   ```markdown
   ## §3.11 Design Provenance
   - Origin: <fork-from-pool / new / reuse>
   - Parent (if fork): `examples/AGENT_POOL/<domain>/<parent>.md`
   - Polish audit: YYYY-MM-DD against `agent-design-skill.md` v<X.Y>.
     Structural changes in this pass:
     - <bullet per structural change>
   - Pool reference: `examples/AGENT_POOL/<domain>/<file>.md`
     (three-stage match outcome: <reuse/override/fork/new>)
   ```
4. **Three-PASS handbook §6 review.** Run
   `agent-design-skill.md §6` Validation Checklist three consecutive
   times against the agent's polished form. Any FAIL resets the count
   to zero. Only after three consecutive PASS runs is the agent
   accepted.

Commit at end of phase with one commit per agent, message:
`polish({ScenarioName}): agent audit — <role-name> against handbook §6`.

### 6.3 Artefacts Changed

- Every `investors/<role>.md` file (if present).
- Every `§4.{N}` block in `simulation-bases.md`.
- Every affected pool file under `examples/AGENT_POOL/<domain>/`.

### 6.4 Exit Conditions

- Every agent spec follows handbook §3.1 — §3.11 canonical order.
- Every agent spec has an up-to-date §3.11 Provenance recording this
  polish run.
- Every agent spec has three consecutive PASS runs of handbook §6.

---

## 7. Phase E — Variant Artefact Audit

### 7.1 Entry Conditions

- Phase D exit conditions hold.

### 7.2 Procedure

For each variant `V` marked `Yes` in target §10.1, walk the four
artefact types:

1. **`{V}/explain.md`** vs
   `implement-simulation-skill/03-variant-documents-spec.md`.
   Confirm section presence, ordering, and variant-specific content.
2. **`{V}/analysis.md`** vs
   `implement-simulation-skill/03-variant-documents-spec.md` §variant.
   Confirm hypothesis rows tie to `analysis-bases.md §1`.
3. **`{V}/players.py` and `{V}/run_*.py`** vs
   `implement-simulation-skill/08-step4-implement.md`. Recurring
   issues:
   - Any `extras.get("key", default)` pattern MUST become
     `extras["key"]` with a preceding comment indicating fail-fast.
   - Any `decision.get("action", "hold")` pattern MUST become
     `decision["action"]` and raise on missing `<decision>` block.
   - The universal "No Defaults" rule (target §9 is authoritative;
     configs echo values verbatim).
4. **`{V}/analysis.py`** vs
   `implement-simulation-skill/08-step4-implement.md` §4.2 — §4.4.
   Confirm `py_compile` passes and the LLM decision field access rule
   (§4.2.3) is respected.
5. **`configs/{ScenarioName}/{V}/*.yml`** vs
   `implement-simulation-skill/07-step3-config.md`. Every extras key
   must have a `# Source:` comment traceable to target §9 or an
   override in `simulation-bases.md §4.{N}.6`.

Commit at end of phase per variant with message:
`polish({ScenarioName}): variant audit — {V}`.

### 7.3 Artefacts Changed

- Every file under `examples/{ScenarioName}/{V}/` for each built `V`.
- Every file under `configs/{ScenarioName}/{V}/` for each built `V`.

### 7.4 Exit Conditions

- Every built variant's `players.py` / `analysis.py` compiles cleanly.
- No `.get(key, default)` pattern remains in any `players.py` or
  `analysis.py`.
- Every YAML config parses cleanly (see
  `implement-simulation-skill/09-step5-to-10-review.md §5.3`).

---

## 8. Phase F — Scenario-Level 3-PASS Review

### 8.1 Entry Conditions

- Phase E exit conditions hold.

### 8.2 Procedure

Run
`implement-simulation-skill/09-step5-to-10-review.md` Steps 5 — 9 as a
single review batch, three times in a row. The three passes emphasise
different aspects (identical to
`create-simulation-pipeline.md §8.2`):

| Pass # | Reviewer perspective                            | Anchors                                |
|--------|-------------------------------------------------|----------------------------------------|
| 1      | Theory-code alignment (Step 5)                  | §5.1, §5.2, §5.3, §5.4                 |
| 2      | Code quality + analysis tools (Steps 6 — 7)     | §6.1, §6.2, §6.3, §7.1                 |
| 3      | Documentation + final cross-check (Steps 8 — 9) | §8, §9                                 |

Any unchecked item in any pass resets the count.

### 8.3 Exit Conditions

- Steps 5 — 9 all-tick, three passes in a row.

---

## 9. Phase G — Smoke Test and Closeout

### 9.1 Procedure

1. For each variant `V` marked `Yes` in target §10.1, run:
   ```
   python -m masim.run --config configs/{ScenarioName}/{V}/simulation.yml \
                       --steps 5 --dry-run
   ```
   All variants MUST complete without uncaught exceptions.
2. Confirm `analysis.py` produces every metric declared in
   `analysis-bases.md §2`.
3. Sanity-check at least one figure per variant.
4. Run the final readiness checklist in
   `09-step5-to-10-review.md §9` against the completed scenario.
5. **Update target §0 Meta CHANGELOG** with a single line summarising
   this polish run:
   ```
   YYYY-MM-DD  Polish run against skill baseline vX.Y:
               - root-doc audit (Phase C): <one-line summary>
               - per-agent audit (Phase D): <count agents polished>
               - variant audit (Phase E): <variants polished>
   ```
6. Update `Status` from `locked` to `released` (target file only —
   no build log exists).

### 9.2 Exit Conditions and Closeout

- All smoke-test runs green.
- Target file `Status: released`.
- Every phase has a corresponding git commit whose message clearly
  identifies the polish scope.

---

## 10. Cross-Phase Traceability Guarantee

Before closing Phase G, verify that every downstream artefact traces
back to a section of the target file. The trace matrix is identical to
`create-simulation-pipeline.md §10` **except** for the log column,
which is absent (a polish run has no build log). Use the target file
directly as the single upstream source:

| Downstream artefact                                     | Upstream anchor in target file       |
|---------------------------------------------------------|--------------------------------------|
| `simulation-bases.md §1` (Phenomenon Definition)        | target §2 + §6                       |
| `simulation-bases.md §2` (Theoretical Foundation)       | target §4                            |
| `simulation-bases.md §3` (market mechanism choices)     | target §5 + §8                       |
| `simulation-bases.md §4.{N}` block                      | target §7 row                        |
| `simulation-bases.md §6` parameter rows                 | target §9                            |
| `examples/AGENT_POOL/<domain>/<file>.md` (touched)      | target §7 row + investor §3.11       |
| `configs/{ScenarioName}/{V}/players.yml` extras         | target §9 + `# Source:` comments     |
| `analysis-bases.md §2` metrics                          | target §5 + §6 + §10.2               |
| Variant folders present                                 | target §10.1                         |

Any unanchored downstream artefact is a defect and MUST be repaired
before Phase G is closed.

---

## 11. Tooling and Interaction Rules

- **AskUserQuestion**: ≤4 options per question. Use only for defect
  clarification — same discipline as
  `create-simulation-pipeline.md §11`.
- **TodoWrite**: maintain a seven-item todo list mirroring Phases A —
  G. Update on phase boundaries; do not micro-track inside a phase.
- **Git discipline**: one commit per completed phase (Phases C — E may
  produce multiple commits, one per audited file). Commit messages
  MUST identify the phase and the artefact scope. This git history is
  the polish run's primary audit trail (no build log is written).
- **Workspace throwaway**: the Phase A gap list lives under
  `/Users/sjia/.qoderwork/workspace/mqz1cq048x69z4wm/` and MUST NOT be
  committed to the repository.

---

## 12. Pipeline Entry Checklist (Pre-Run)

Run this checklist once before invoking Phase A:

- [ ] The scenario `examples/{ScenarioName}/` exists and contains at
      least one downstream artefact (`simulation-bases.md`,
      `investors/`, or a variant folder).
- [ ] Repository is clean (`git status` shows no unrelated diffs).
- [ ] The current versions of the four skill anchors are known:
      `define-simulation-scenario-skill.md`, `agent-design-skill.md`,
      `implement-simulation-skill/02-root-documents-spec.md`,
      `implement-simulation-skill/09-step5-to-10-review.md`.
- [ ] The AGENT_POOL folder for the scenario's domain
      (`examples/AGENT_POOL/<domain>/`) is up to date.
- [ ] You have read this file (`polish-simulation-pipeline.md`)
      end-to-end at least once.

If any item is unchecked, fix it before starting Phase A.

---

## 13. Skill References (Quick Index)

| Topic                                | File                                                                       |
|--------------------------------------|----------------------------------------------------------------------------|
| **Scenario target file spec**        | `masim/skills/define-simulation-scenario-skill.md`                         |
| Universal Agent Design Handbook      | `masim/skills/agent-design-skill.md`                                       |
| From-scratch pipeline (contrast)     | `masim/skills/create-simulation-pipeline.md`                               |
| Methodology overview                 | `masim/skills/implement-simulation-skill/00-overview.md`                   |
| Directory layout                     | `masim/skills/implement-simulation-skill/01-mandatory-structure.md`        |
| Root document specs + §4.1 finance   | `masim/skills/implement-simulation-skill/02-root-documents-spec.md`        |
| Variant document specs               | `masim/skills/implement-simulation-skill/03-variant-documents-spec.md`     |
| Step 0 (Load target)                 | `masim/skills/implement-simulation-skill/04-step0-load-target.md`          |
| Step 1 (Research)                    | `masim/skills/implement-simulation-skill/05-step1-research.md`             |
| Step 2 (Agent design + Pool gate)    | `masim/skills/implement-simulation-skill/06-step2-agent-design.md`         |
| Step 3 (Config)                      | `masim/skills/implement-simulation-skill/07-step3-config.md`               |
| Step 4 (Implement)                   | `masim/skills/implement-simulation-skill/08-step4-implement.md`            |
| Steps 5 — 10 (Validate, review, run) | `masim/skills/implement-simulation-skill/09-step5-to-10-review.md`         |
| AssetBubble reference                | `masim/skills/implement-simulation-skill/15-reference-assetbubble.md`      |
| AGENT_POOL directory                 | `examples/AGENT_POOL/`                                                     |
| Project structure overview           | `docs/structure.md`                                                        |
